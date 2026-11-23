---
type: Concept
title: llama.cpp 多级缓存：源码能力与实现边界审计
description: 审计日期：2026-09-11。仅阅读源码与官方资料，没有修改 llama.cpp，也没有运行推理或性能测试。硬件与工作负载实测由主报告另行核实。
tags:
- llm
- llamacpp
- kv-cache
sources:
- c:/Users/Administrator/Documents/Code/my-code/lm-llama/research/llamacpp-tiered-cache-source-audit.md
createdAt: '2026-11-23'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# llama.cpp 多级缓存：源码能力与实现边界审计

审计日期：2026-09-11。仅阅读源码与官方资料，没有修改 llama.cpp，也没有运行推理或性能测试。硬件与工作负载实测由主报告另行核实。

本地源码 HEAD 是 `f5e85d43a048f3d5adefb4c5e29867d8077fba62`；主任务发现的已运行二进制是 b9209，对应 `0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e`。两个提交均在本地 Git 对象库中，本报告用 `git show` 审计旧版，用工作树阅读 HEAD。下面的“现有能力”不能跨版本混用。

## 1. 可以直接使用什么

| 能力 | b9209 / `0caf2a1d4` | 源码 HEAD / `f5e85d43a` |
| --- | --- | --- |
| RAM prompt cache | `--cache-ram N`，单位 MiB；默认 8192，0 关闭，-1 无字节限额，但仍有动态 token 约束 | 同样存在 |
| 缓存对象 | 整个序列的 target state、可选 draft state、token 序列、历史 partial checkpoints | 同样以整个 prompt state 为对象，结构有所重组 |
| 字节限额 | 先分配新对象，再淘汰；即使超额也保留至少 1 个对象 | 分配前拒绝单个超额对象、先淘汰腾空间；允许淘汰全部对象 |
| idle slot | 必须同时启用 RAM cache 与 `--kv-unified`；新任务启动后保存并清空其他 idle slots | RAM cache 是前提；无 unified 也保存，有 unified 才清空 |
| checkpoint 上限 | `--ctx-checkpoints N`，默认 32，按 slot 限制个数 | 同样存在 |
| checkpoint 位置控制 | `--checkpoint-every-n-tokens N`，默认 8192；周期性 mid-prompt checkpoint，另有接近 prompt 尾部的检查点 | `--checkpoint-min-step N`，默认 8192；增加用户消息边界策略、旧 checkpoint 间距清理 |
| 磁盘 | 显式 slot save / restore，保存当前 target 序列与 tokens | 同类接口；不能等同于自动、完整的 RAM prompt-cache 落盘 |
| 外部块缓存与迁移 | 本次检查路径没有通用 token-range block export/import、跨进程共享前缀索引或自动 NVMe 后端 | 同样不能通过上述开关直接获得 |

来源：[b9209 参数默认值](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/common/common.h#L593-L596)、[旧版参数定义](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/common/arg.cpp#L1328-L1365)、[旧版 idle 条件](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/tools/server/server-context.cpp#L1028-L1038)、[HEAD 参数](https://github.com/ggml-org/llama.cpp/blob/f5e85d43a048f3d5adefb4c5e29867d8077fba62/common/arg.cpp#L1695-L1735)、[HEAD idle 行为](https://github.com/ggml-org/llama.cpp/blob/f5e85d43a048f3d5adefb4c5e29867d8077fba62/tools/server/server-context.cpp#L2409-L2423)。

## 2. RAM cache 的容量和替换语义

b9209 的 `alloc()` 先检查包含关系：若新 prompt 已完全包含在缓存对象的 token 前缀中，就不再存；若现有对象完全包含在新 prompt 中，就移除旧对象。随后分配整块 target / draft 的字节向量，克隆 tokens 与 checkpoints。它没有共享前缀的块级去重。即使不同对话共享长 system prompt，只要分别存成对象，相关序列状态仍然分别占空间。[旧版 alloc](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/tools/server/server-task.cpp#L1997-L2049)

查找不是单纯“最长前缀最大者胜出”。对对象 i，计算 `keep_i=LCP_i/cached_tokens_i` 和 `sim_i=LCP_i/request_tokens`；`keep_i<0.25` 被跳过，候选必须同时严格改善当前最优的 keep 与 sim。命中后恢复整个对象，释放 target/draft 主机字节，移走 tokens/checkpoints，并从 RAM cache 列表删除该对象。这更接近在 slot 和主机缓存间交换状态，不是永久保留一份命中副本的只读共享库。[旧版 load](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/tools/server/server-task.cpp#L2052-L2124)

替换是从列表头部删除最早保存的对象；slot 的选择另有 LCP 优先、否则 LRU 的逻辑。不要把整个系统概括成严格的 token-block LRU。原生查找也没有比较恢复时长与重新 prefill 的时长。[旧版更新规则](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/tools/server/server-task.cpp#L2127-L2165)、[slot 选择与同步更新](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/tools/server/server-context.cpp#L1123-L1208)

旧版 `update()` 的准确顺序如下，其中 B 是缓存对象累计字节，T 是累计 tokens，L 是 `cache_ram` 字节限额，C 是构造时传入的 context token 数。

```text
if L > 0:
    while entry_count > 1 AND B > L:
        evict oldest
s = max(1, B / max(1, T))
C_effective = L > 0 ? max(C, L / s) : C
if C > 0:
    while entry_count > 1 AND T > C_effective:
        evict oldest
```

因此，日志中的 `8192 tokens` 不是有限 RAM cache 的固定总 token 上限；`18947 est` 才是该次更新的动态估计。对于正数 L，字节淘汰后若 B≤L，数学上 L/(B/T)≥T，故 token 阶段通常不再约束当前集合，除去浮点舍入等边界。但 `--cache-ram -1` 会退回 C 这个 token 上限，并非真正无约束无限缓存。HEAD 保留相同公式，只是两个循环不再强制保留 1 项。[旧版公式](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/tools/server/server-task.cpp#L2127-L2161)、[HEAD 公式](https://github.com/ggml-org/llama.cpp/blob/f5e85d43a048f3d5adefb4c5e29867d8077fba62/tools/server/server-task.cpp#L1870-L1895)

HEAD 的新准入把 full target、full draft 和所有 checkpoint 字节一起比较限额，过大的对象直接跳过，并在分配向量前逐项腾空间。但 `size()` 仍是序列化 data/checkpoint 的逻辑字节合计，不包括所有容器开销、live slot checkpoints、GPU 分配、权重映射、I/O staging 或操作系统文件缓存。不能把 `--cache-ram 8192` 当成整个进程的 RAM 上限。[HEAD alloc](https://github.com/ggml-org/llama.cpp/blob/f5e85d43a048f3d5adefb4c5e29867d8077fba62/tools/server/server-task.cpp#L1711-L1793)、[HEAD size](https://github.com/ggml-org/llama.cpp/blob/f5e85d43a048f3d5adefb4c5e29867d8077fba62/tools/server/server-task.h#L598-L633)

## 3. Qwen3.5 hybrid 状态为什么改变缓存粒度

对 hybrid memory，完整状态包含 attention cache 和 recurrent state；设置 `LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY` 时跳过 attention 部分，只读写 recurrent 部分。这里的 partial 指“某种状态组件”，不是“任选一段 tokens”。该公开接口只有 seq_id、buffer、size、flags，没有任意 token 起止范围参数。[b9209 hybrid state](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/src/llama-memory-hybrid.cpp#L181-L193)、[公开 API](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/include/llama.h#L869-L899)

recurrent state 不能像普通 attention KV 一样随意删除任意尾部；b9209 提供的 per-token rollback 受 `n_rs_seq` 限制，超出界限会返回 false。因此可复用前缀长度不应直接等于最长相同 token 前缀，而应由可恢复 checkpoint 和后续重算位置共同决定。[recurrent rollback](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/src/llama-memory-recurrent.cpp#L150-L189)

server 的历史 context checkpoints 用 `PARTIAL_ONLY`，放在普通 `std::vector<uint8_t>` 中，并保存 `n_tokens / pos_min / pos_max`。它们是主机内存对象；b9209 中另有用于 speculative decoding 的 `PARTIAL_ONLY|ON_DEVICE` checkpoint，不能把两者混为一谈。向 RAM cache 保存 prompt 时还会复制历史 checkpoint 列表，所以 live slot 与刚保存对象可在一段时间内同时持有这些数据。[checkpoint 结构](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/common/common.h#L1052-L1093)、[checkpoint 分配](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/common/common.cpp#L2058-L2073)、[历史 checkpoint 创建](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/tools/server/server-context.cpp#L1864-L1885)、[speculative checkpoint](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/tools/server/server-context.cpp#L2354-L2383)

当相同前缀不足以直接沿用当前 recurrent 状态，server 反向找可用 checkpoint，恢复后重新设置 n_past；找不到就强制从头重新处理 prompt。即使全部 token 匹配，也至少处理 1 个 token 以取得 logits。命中 tokens 统计与真正免除的 prefill 工作应分开记录。[恢复与回退](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/tools/server/server-context.cpp#L2638-L2699)

设计含义（推导）：第一版应缓存“可恢复的前缀状态包”，容量模型使用 `full_state_bytes + sum(checkpoint_bytes)`，并另外预留 live slot checkpoints。若 recurrent 检查点本身很大，把所有 prompt 按 256 tokens 固定切块再每块保存一次完整 recurrent 状态，可能显著放大容量和保存时间。后续真正的 block cache 必须把可分享 attention 块与 recurrent 边界快照分开建模。

HEAD 的 checkpoint 策略已变化：旧任务里间距过近的 checkpoint 会被移除，当前任务的例外仍可保留；还记录 speculative state。代码保留一个针对 SWA 覆盖范围的 TODO，因此不能仅凭 metadata 假设任意模型的区间语义已完备。这个 TODO 不直接证明当前 Qwen3.5 测试存在错误。[HEAD checkpoint 创建](https://github.com/ggml-org/llama.cpp/blob/f5e85d43a048f3d5adefb4c5e29867d8077fba62/tools/server/server-context.cpp#L2298-L2344)

## 4. 磁盘 slot 文件为什么不是完整 L2 缓存协议

b9209 的 slot save 调用 `llama_state_seq_save_file(ctx_tgt, ...)`；文件包含 magic、版本、tokens、当前序列状态，状态保存的 flags 为 0。server 的历史 checkpoint 列表、draft context 与缓存替换 metadata 没有作为该文件的一部分写入。restore 对活跃 slot 会延后；恢复成功后 server 重建 token 列表。这可以实现“保存当前位置并续写”，不能自动保证“任意较早分叉点命中”与 RAM prompt cache 等价。[slot save/restore](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/tools/server/server-context.cpp#L2040-L2100)、[seq 文件读写](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/src/llama-context.cpp#L2917-L2977)

建议新增的持久化包（设计，不是现有开关）：

- manifest：模型文件/模型内容标识、tokenizer 与模板标识、token 前缀哈希、位置/长度、缓存 K/V 类型、RoPE 参数、adapter 标识、状态格式版本、llama.cpp 提交与目标后端布局兼容性标识。
- blob：target full state、需要时的 draft full state、每个有效 partial checkpoint，以及其 n_tokens / pos_min / pos_max；新版本还需考虑对应 speculative state。
- 每包校验、原子写入完成标记、失败时回退重算；同一模型形状不意味着状态内容可以跨模型加载。
- 外部服务只管理不可变主机字节对象与索引；GPU 指针及 `ON_DEVICE` 句柄不得落盘或跨进程复用。

HEAD API 明确写明：对同一 seq_id 再次取得 `ON_DEVICE` 状态会使该 seq_id 此前取得的这种状态失效。它适合受控的临时回滚，不能直接用作保存许多历史版本的通用 GPU 缓存容器。[HEAD ON_DEVICE 契约](https://github.com/ggml-org/llama.cpp/blob/f5e85d43a048f3d5adefb4c5e29867d8077fba62/include/llama.h#L911-L930)

## 5. 异步传输：可以规划，但当前 API 不能提供保证

两版 `llama_state_seq_get_data_ext / set_data_ext / save_file / load_file` 在入口都同步整个 llama_context。b9209 的 host serializer 析构时逐 tensor get/set；CUDA tensor get/set 尽管调用 `cudaMemcpyAsync`，紧接着就调用 `cudaStreamSynchronize`。因此把 seq-save 调到另一个线程，并不自动产生与当前 context 的 decode 并行；反而需要处理上下文的并发修改与生存期问题。[旧版入口同步](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/src/llama-context.cpp#L3861-L3891)、[HEAD 入口同步](https://github.com/ggml-org/llama.cpp/blob/f5e85d43a048f3d5adefb4c5e29867d8077fba62/src/llama-context.cpp#L4166-L4192)、[host get/set](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/src/llama-context.cpp#L2378-L2439)、[CUDA 同步](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/ggml/src/ggml-cuda/ggml-cuda.cu#L682-L695)

可分两阶段实现（建议）：先在 engine 可控安全点导出完整、稳定的主机 blob，后续压缩、NVMe 写入和读取预热可在后台工作；只有确认 GPU 传输是瓶颈后，才改后端接口，使用有容量上限的 pinned staging pool、分设备复制流、完成事件和不可变 snapshot/生命周期约束，以批量传输代替逐 tensor 同步。H2D 恢复是否能按层预取，也需要执行器在使用相应层前等待正确事件，不能只靠文件 I/O 层解决。

NVIDIA 官方指南说明：主机和设备间复制与 kernel 执行重叠，需要设备支持相应能力、pinned host memory，以及合适的不同 streams；pinned memory 不应无上限使用。因此主缓存可用普通 RAM，而把 pinned RAM 作为小规模复用的传输暂存池。异步并不免除 PCIe 流量，也不保证 TTFT 或并发 decode 的尾延迟不受影响。[CUDA pinned 与重叠条件](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html#pinned-memory)

## 6. 多 GPU 缓存的边界

llama.cpp 的 `layer` 模式按层分散权重与 KV；`row` 模式按行分散权重，而 main GPU 承担中间结果与 KV；`tensor` 模式同时分散权重与 KV，在 b9209 参数里标为 experimental。因此两张卡不能简单当成一个可随意放置 KV 的连续 VRAM 池。缓存条目成本应记录每张卡的分片字节、恢复路径和排队时延；使用另一张卡存冷 KV 还要计算它本来承担的权重/计算与传输机会成本。[split 参数语义](https://github.com/ggml-org/llama.cpp/blob/0caf2a1d48d2b678f2ea2fdfcb07ee35816f9f5e/common/arg.cpp#L2369-L2423)

不能从型号或“存在两个 GPU”推断能高速 P2P。NVIDIA 将实际可用性定义为对设备对调用 `cudaDeviceCanAccessPeer()` 的结果，并受拓扑影响；开启可用的 P2P 后才可避免主机 staging。即便 API 支持，也应测双向带宽与运行时争用。[CUDA 多 GPU/P2P](https://docs.nvidia.com/cuda/cuda-programming-guide/03-advanced/multi-gpu-systems.html#peer-to-peer-memory-access)

设计含义（推导）：先把 GPU 层定义成模型正在使用的 active state 与少量预计立即复用的 warm slots；RAM 层承担会话间的主要复用；NVMe 只接纳预期收益覆盖落盘、恢复和占用成本的冷对象。不要默认把第二块显卡降格成专用缓存盘，也不要在每一个 decode token 上从 RAM/NVMe 按需取回全量历史 KV。

## 7. 衡量真实收益的最小观测字段

下列是建议新增/整合的观测字段，不是声称当前 server 全部提供：请求级 TTFT（含队列）、完成时延、生成吞吐、实际省下的 prefill tokens/time、按层命中、被选 checkpoint 的真实恢复位置、D2H/H2D 字节与耗时、checkpoint 创建耗时、NVMe 读写耗时、缓存准入/淘汰、各卡 VRAM 高水位、主机私有内存与系统文件缓存、并发 decode 的 p95/p99 token 间隔。

以“预期未来复用次数 × 可避免 prefill 时间 − 导出/恢复/落盘/争用成本”做准入，并用每字节净收益辅助替换，是对原生实现的增量设计。用在线测得的恢复成本比较重新 prefill 的成本，选择更快的一条路径；对 hybrid，应按可恢复 checkpoint 后实际需要重算的 suffix 估算，不能只用 token LCP 计数。
