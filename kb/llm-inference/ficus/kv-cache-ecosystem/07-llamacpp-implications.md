---
type: Guide
title: 对 llama.cpp 三级缓存的落地建议
description: 能抄什么、不能抄什么，本工作区原型的改造顺序
summary: 能抄什么、不能抄什么，本工作区原型的改造顺序
tags:
- llm
- kv-cache
- llama.cpp
- implementation
sources:
- session: 2026-11-18 KV Cache 生态研究与文档重构
- C:/Users/Administrator/Documents/Code/my-code/lm-llama/research/kv-cache-ecosystem/07-llamacpp-implications.md
createdAt: '2026-11-18'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 对 llama.cpp 三级缓存的落地建议

> 能抄什么、不能抄什么，以及本工作区原型该按什么顺序改。

## 速览

```text
  可直接借鉴  逻辑/物理位置分离 · 换出原子性 · 租约与延迟读源分层
              元数据与内容分离 · 淘汰三段分离 · 三态查询结果 · 后端插件形状
  需要改造    KVMem 召回评分 · host 存储与 SpillFile · Mooncake SSD 双向流水线
  不适用      KVMem 50 文件补丁 · LMCache 对 vLLM 的耦合 · Mooncake 集群假设

  本工作区原型：整序列 opaque blob，完全落在 llama.cpp 既有 public API 内
  落 L2 前必须按序解决：粒度 -> 键的身份 -> 索引持久化
```

## 1. 对本工作区（llama.cpp 三级缓存）的结论

本工作区研究 L0 显存 → L1 RAM → L2 SSD 的 KV/prompt 缓存。这里把“完整 Prefix State Blob 的停放/恢复”与“活动推理中的原生页换入”分开：前者可优先研究现有 state API，后者需要更细的布局、位置、写入及调度接口。KVMem 基础 llama 补丁触及 50 文件只能说明改动范围，不能单凭文件数断言其性能或可维护性优劣。Strata 的新增对齐见 四维对齐系列（02–05）；下面的建议不代表实施或性能验收。

### 5.1 可以直接借鉴（按价值排序）

1. **把逻辑记录、有效版本与驻留位置分开管理**
   KVMem 的 `HostKvStorage`/`HostKvRecord` 统一记账 RAM/SSD 的逻辑记录（`kvmem/kvmem/include/kvmem/host_kv_storage.hpp:60`）；Strata mode 1 则保留权威 host 和 VRAM write-through 副本。共同价值是明确所有权和完成边界，不是宣称只有一份物理数据或自动消除一致性问题。

2. **原始位置 vs 物理槽分离 → 纯 memcpy 搬运**
   `kvmem/docs/memory-backend-contract.md:77-91` 定义的三种坐标，加上 `layout_gpu_slots_by_orig_pos`（`llama-memory-kvmem.cpp:2332`）。搬运保持 KV 的原始 RoPE 位置，回灌是 packed 格式 memcpy，**不需要 re-RoPE、不需要反量化重算**。这是三者里对 llama.cpp 最值钱的一条。

3. **逻辑删除 vs 物理释放分离**
   `seq_rm_logical`（按逻辑位置删 cell）与 slot 释放分离。对应你的语义：「这段历史逻辑上还在 L2，只是这一轮不在 L0」。

4. **换出原子性**
   先预留目标配额 → 写成功才发布 SSD 副本并释放 H → 任何失败保留原 RAM 副本（`kvmem/docs/active-kv-tiering.md:39-40`，`host_kv_storage.cpp:127-140`）。SSD 写失败绝不能丢唯一有效副本——这是最容易写错的地方。

5. **读租约 vs 延迟读源分离**
   `HostKvLease`（钉住 RAM + 磁盘配额）与 `HostKvSource`（只钉内容版本，不钉 RAM 层）的区别（`host_kv_storage.hpp:16-56`）：冷数据读取不能把整条记录拉回 RAM；排队中的冷请求不应吃光别的传输需要的 RAM。

6. **元数据与内容分离 + 扁平不透明键**
   Mooncake 的 `ObjectMetadata` / `Replica` 分离，以及 Store 层只认不透明字符串键。llama.cpp 现在的 slot prompt cache 把「这个 slot 里是什么」和「数据在哪」揉在一起，这是最值得先拆的一层。

7. **淘汰三段分离**
   Index 定访问顺序 / Policy 定谁有资格淘汰 / Reclaimer 执行释放（`mooncake-store/include/eviction/evictor.h:16-35`）。你现在「L1 满了就按 LRU 挑一个丢到 L2」是单点逻辑，拆成三段后三部分可分别调优与测试。

8. **租约 + 软/硬 pin 三档**
   Mooncake 的 `lease.h` + 软硬 pin（`object_metadata.h:167, 345-471`）。agent 场景里「刚算完的中间结果别急着丢，但也不能永久占位」正好对应 soft pin。

9. **连续区间合并与批量传输**
   Mooncake 的 `group_concurrent_contiguous`（`mooncake_connector_v1.py:647`）合并相邻块；Strata 的 prefill/ring 路径可连续 DMA，但 decode miss kernel 是逐页搬运，不能混称同一种批量机制。对 syscall、带宽或 TTFT 的实际收益要用相同工作负载测量。

10. **三态元数据查询结果**
    `GetResult{kFound, kNotFound, kUnavailable}`（`transfer_metadata.h:44-54`）：区分「文件确实不存在」与「读取时 I/O 出错」。否则一次 IO 抖动就会导致误删缓存条目。

11. **配额语义分层声明**
    KVMem 明确写「H 不是进程 RSS 限制」（`active-kv-tiering.md:25`）。这个措辞纪律与本工作区 `CLAUDE.md` 的「写结论时的约定」是一致的，建议照抄。

12. **`MemoryFormat` 显式枚举 + `MemoryObj` 抽象**
    LMCache 把「层数据长什么样」从引擎里解耦出来（`v1/memory_management.py:77`），llama.cpp 侧同样需要这层——尤其是 `KV_MLA_FMT` 那种 K/V 不分离的变体，以及你持有的 Qwen hybrid 的 recurrent 状态。

13. **backend 插件接口形状**
    LMCache 的 `StorageBackendInterface`（`abstract_backend.py:27`）证明了「存储后端可插拔」这条路可行，但它是 Python/torch 风格的接口，llama.cpp 是 C++，**只能借鉴接口形状**（contains / batched put / blocking+non-blocking get / pin 语义 / 每键独立完成回调）。

14. **URL schema 的后端发现**
    `ConnectorManager`（`connector/__init__.py:214`）用 schema 前缀自动发现 connector。llama.cpp 的 L2 插件若要支持多种后端，这是比「配置里写枚举」更干净的扩展点。

15. **`AddressManager` 的对齐与空闲块合并**
    `v1/memory_management.py:1286`：4096 对齐的虚拟地址空间 + 空闲块合并。你的 L1/L2 分配器可以直接参考这个形状。

16. **健康检查失败要显式降级而不是静默**
    LMCache 的做法是健康检查不通过时 store/retrieve/lookup 全部退化为 no-op 只打 warning（`cache_engine.py:416, 808, 1166`）。**这个做法本身有坑**（排障时容易误判为「缓存没命中」），但反面提醒很清楚：三级缓存的降级路径必须可观测。

### 5.2 需要改造后才能用

- **KVMem 的召回评分整套**（mean-K / page-softmax / GQA max / LRFU / 图传播）：只有在你的 L0 目标确实是「丢掉不相关的历史」时才需要。注意它的收益是「GPU 装得下」，代价是精度不再有保证（`kvmem/docs/modification-plan.md:342` 记录的 needle 召不回）。
- **KVMem 的 host 存储与 SpillFile 实现**：`kvmem/src/host/host_kv_storage.cpp`（22 KB）+ `spill_io.cpp`（20 KB）是纯 C++17、无引擎依赖，可作为 L1/L2 的实现参考（注意许可证）。
- **Host store 淘汰**：KVMem 公共 host store 用 FIFO/LRU（`host_kv_storage.cpp:113`），而它自己在遗留 CPU tier 里承认 heat-aware 更好（`pinned_kv_tier.hpp:250-258`）。agent 长尾访问用 LRU 会抖，L2 建议用热度。
- **多会话切换**：KVMem 的全量 drain + rebuild 成本太高。值得借鉴的是「bundle 整体转移所有权」和「recurrent 半边不跟着切」这两个约束。
- **Mooncake 的 SSD offload/promotion 双向流水线**：它的语义是「客户端本地盘 + Store 统一记账」，不是纯本地文件管理。单机构建等价物要自己实现容量上报、promotion 链、失败围栏。
- **LMCache 的 MP 模式**：token 查键可在服务端完成，但实际 KV 仍需通过引擎侧导出/恢复或注册的 IPC 布局搬运；具体适配量尚未评估，不能由服务进程分离推断成“不需要 KV 布局”。

### 5.3 不适用（不要抄）

- **KVMem 的 50 文件 llama.cpp 补丁**：你的路线是外部调度，不要退回到引擎内深度侵入。
- **LMCache 对 vLLM 的耦合**：`GPUConnectorInterface` 的实现直接读 vLLM 的 `kv_caches` dict 与 `block_table`/`slot_mapping`（`v1/gpu_connector/gpu_connectors.py:45, 148, 432`）；`KernelGroupInfo` / `PageBufferShapeDesc` 全部围绕 vLLM paged block 描述（`v1/kv_layer_groups.py:157`）；`get_num_new_matched_tokens` / `update_state_after_alloc` 是 vLLM 调度器钩子。**这些在 llama.cpp 里没有等价物。**
  更根本的是：**LMCache 没有 llama.cpp 集成**，而且**不存在「v0 的 llama.cpp 集成路径」**（v0 已于 2025-12 至 2026-04 间三轮删除，且从未有过 llama.cpp 适配器）。
- **把 LMCache 作为 llama.cpp 的进程内依赖**：需要处理 Python/PyTorch 与 C++/ggml 边界、GPU 数据布局和引擎生命周期。可先参考后端协议与分层职责，但不能声称对齐 chunk key 就能互读原生 KV；完整 state blob 与 LMCache tensor chunk 仍是不同格式，需独立适配并验证。
- **Mooncake 的 PD 解耦 / RDMA / GPUDirect / etcd / HA / Master 全局放置 / Conductor 全局索引**：全是集群假设。Mooncake 本身是 **Linux-only**（`transfer_engine.h:299-310` 明说 `completionFd()` 在非 Linux 返回 -1），你的 Windows + RTX 5080 环境只能读设计不能跑。
- **KVMem 的 recurrent 状态策略的 replay 模式**：它的 GDN replay 限定在 `LLAMA_ARCH_QWEN35` + `ssm_d_state==128` + `ssm_d_conv==4` + `n_rs_seq∈[1,5]` 的窄几何内（`llama-memory-kvmem-hybrid.cpp:14-40`），不满足就直接抛异常。它的「recurrent 状态走独立字节快照通道」这个**前提**对你持有的 Qwen hybrid 成立，但意味着**你的 L1/L2 只覆盖 attention KV，GDN 状态必须另立一项**。

### 5.4 现成可借的组合路径

一个已验证的事实：**Mooncake Store 已经作为 L2 后端接进 LMCache**（`mooncake/docs/source/deployment/integrations/lmcache/vllmv1-lmcache-mp-integration.md:9-11, 74-78`），角色划分是「LMCache 管 L1/L2 策略与淘汰，Mooncake Store 只当远端对象池」，配置形如：

```bash
--l2-adapter '{"type": "mooncake_store", "local_hostname": "...", "metadata_server": "P2PHANDSHAKE", "protocol": "rdma"}'
```

这证明社区认可的分层是「策略层 + 存储层」分离，而不是一个大一统的缓存。对你的意义：**如果将来要跨进程/跨实例共享，LMCache 的策略层 + 某个存储后端是可行组合**——但这条路在 Windows 单机上跑不通（要求 Linux + 从源码构建 LMCache 以启用 `lmcache.lmcache_mooncake` 原生扩展），而且仍然需要先解决「LMCache 没有 llama.cpp connector」这个根问题。

### 5.5 llama.cpp 接入路线：先定义交换对象，再选择接口

| 路线 | 交换对象与接口 | 尚需解决的边界 |
|---|---|---|
| **完整 Prefix State Blob** | 用现有 sequence state API 保存/恢复引擎状态，在本地 RAM/SSD 管理带兼容性元数据的对象 | 模型与引擎版本、token 前缀、recurrent checkpoint、失败后的目标状态；不能当作 LMCache tensor chunk 交给现有 GPU connector |
| **原生页/块搬运** | 参考 KVMem 的 native payload 与 Strata 的逻辑页/物理槽分离，显式导出所需数值面 | ggml K/V stride、量化 scale、位置/掩码、引用归属、模型原生必须可见的集合；普通 cell 元数据不等于 vLLM PagedAttention 页协议 |
| **LMCache 引擎适配** | 独立实现布局、生命周期及完成通知；根据 classic GPU connector 或 MP engine-driven/IPC 接口选通路 | 发 token 只解决查键；实际 KV 的源/目标布局及 recurrent 状态仍需适配，不能因为使用 MP 就省去 |

**撤回上一版的“约 200 行、对齐 key 后直接写 `.pt` 目录即可共享”建议。** classic LocalDisk 的命中依赖进程内 `DiskCacheMetadata`，文件之外还需要形状、dtype、format、位置等元数据。直接投放同名裸文件并不完成注册、恢复或淘汰协议（`local_disk_backend.py:118`、`:210`、`:306`、`:425`）。

本次确认：llama.cpp 的普通 KV 层分配独立的 K/V 三维张量（`try-out/llama.cpp/src/llama-kv-cache.cpp:233`），cell 表记录位置和 sequence 归属；**逻辑 cell 可以非连续，底层张量的存储布局是另一个问题**，不能由 cell 元数据直接推导为 vLLM 页布局。Qwen hybrid 还需一起恢复 recurrent/checkpoint 状态。GGUF 的 Q4/Q8 KV 编码也不等于 LMCache 的 `torch.dtype` 名字。

Strata session fingerprint、KVMem native payload identity、LMCache layout/group 元数据共同说明：**相同 token hash 只回答候选对象是谁，布局与执行状态兼容才回答能否安全恢复。** 本轮不承诺跨引擎 KV 互读，也不估未经实现与测试的行数成本。

### 5.6 本工作区原型在四方架构中的位置

**当前实现**（`try-out/llama.cpp/tools/server/server-tier-store.{h,cpp}`、`server-context.cpp` 未提交改动，本轮只读核实）：

| 项 | 现状 | 出处 |
|---|---|---|
| 交换对象 | **整序列 opaque state blob**：`llama_state_seq_get_size_ext` / `get_data_ext` 取主模型与 draft 的整条序列状态，装进 `server_tier_snapshot{server_prompt prompt; server_prompt_data data;}`；`tier_restore()` 对称写回 | `server-context.cpp:344-385` |
| 键 | FNV-1a 64 over token ids，**只含 token 序列** | `server-tier-store.h:9-16` |
| 容器 | 进程内 `std::map<uint64_t, server_tier_snapshot>`；`LLAMA_TIER_CACHE_MIB` 设上限；**L2 SSD 仍是注释占位** | `server-tier-store.h:32-45` |
| 淘汰 | 超预算时删**键最小**的条目（hash 顺序，不是 recency） | `server-tier-store.cpp:15-18` |
| 入口 | `POST /tier/:id_slot`；save/load 任务分支 | `server-context.cpp:4936`、`:2732`、`:2770` |

**关键架构事实**：这套快照机制**完全落在 llama.cpp 既有 public API 内**（`include/llama.h` 的 `llama_state_seq_*_ext`），**没有改动 llama.cpp 核心**。这与 KVMem 改 50 个文件形成对照，也与 Strata 的 session 文件同构——**「引擎外的整会话停放」这条路，第一步不需要上游改动。**

**与四家的架构差异定位**

| 维度 | 本工作区原型 | Strata 会话文件 | LMCache / Mooncake / KVMem |
|---|---|---|---|
| 交换对象 | 整序列 opaque blob | 整会话（attention KV + GDN + PLE + indexer） | 块级 KV（chunk / page / slot） |
| 键 | token hash（FNV-1a） | token 前缀 + 图片 `(start,hash)` | 前缀哈希链 + 模型/配置元数据 |
| 兼容性校验 | 仅恢复时比对 blob 长度 | config fingerprint + 模型采样指纹 | key 内嵌 model/rank/dtype；KVMem 另有 `BackendIdentity` |
| 粒度收益 | 整前缀命中才省 prefill | 同 | 公共前缀可共享、可按块下放 |
| 淘汰 | 键最小先出 | LRU + root/tail/pin + guard | LRU/LFU/lease-age + pin |
| L2 SSD | 未实现 | 会话文件（整会话事务） | 块级下沉 |
| hybrid recurrent | **天然包含**（在 state blob 内） | checkpoint + 完整快照 | 需单独用 group 表达 |

**三个判断**

1. **原型当前处在「会话级停放」这一档，不是「块级分层」。** 这条路线能拿到 TTFT 收益（跳过整段前缀 prefill），但拿不到容量收益——不同会话的公共前缀仍各存一份，长会话之间的重复历史不会因为下沉 L2 而减少。
2. **键只有 token hash，是落 L2 之前必须先补的一处。** 进程内实现时风险有限（模型不会中途更换），但一旦要落到 SSD 跨重启，同一前缀在不同模型、不同 KV dtype 或不同引擎版本下会撞 key，恢复是整块 blob 写入——这属于静默错误。Strata 用 config + 模型采样指纹、Mooncake 用 key 内嵌模型名、LMCache 用 key 内嵌 dtype，都是为了堵这个洞。
3. **淘汰按 hash 顺序而不是 recency。** 在 agent 场景会表现为「刚用过的高价值前缀被随机踢掉」，而且会直接污染命中率测量。改动只有几行，但它决定 L1 的实测数字是否有意义。

---

## 2. 对本工作区原型的直接结论

结合 §1.6 的原型现状与本节结论：

1. **当前原型的路线是对的**：opaque blob 路线不需要改 llama.cpp 核心，且对 Qwen hybrid 天然正确（recurrent 已在 blob 内）。**不要为了「块级」而重写整个方案**——先确认整会话停放能带来多少 TTFT 收益。
2. **但落 L2 之前必须先解决三件事**，顺序不能颠倒：
   - **粒度**：整序列 blob 无法部分命中，长 prompt 下 blob 巨大。**能否只导出前 N token 的 state 是路线 B 的头号阻塞点**——需要查清能否用位置区间 API，或用 `llama_memory_seq_rm` + 临时 seq 组合出「前缀切片」。
   - **键的身份**：键只有 token hash，跨重启落盘后会撞（§1.6 判断 2）。
   - **索引持久化**：LMCache 的 LocalDisk 已经踩过这个坑——`self.dict` 是进程内映射，重启后文件还在但索引没了，**看起来全 miss，而且这些文件再也不会被淘汰，等于永久泄漏**（`LMCache/lmcache/v1/storage_backend/local_disk_backend.py:119`、`:210`、`:274`）。你的 `server_tier_store` 是同样的进程内 `std::map`，加 L2 时必须一并解决索引落盘。
3. **淘汰按 hash 顺序**（`server-tier-store.cpp:15-18`）在加 L2 之前就该改成 recency——否则 L1/L2 的命中率测量没有意义。

---

## 3. 四个最容易踩的坑（跨项目）

1. **别把 LRFU 当淘汰策略**。KVMem 里 LRFU 是召回评分的衰减历史，Host store 的下沉走的是 FIFO/LRU。两套机制在不同文件里，混起来会做出错误的设计决策。
2. **负分不能置零**。KVMem 的 LRFU 明确保留未过阈值的负分为 `min(score,0)`（`lrfu.hpp:72-77`）——置零会「相对于命中但分数没那么负的块，反而奖励了它，在没有历史时反转相关性」。
3. **租约必须 honor now+ttl**。Mooncake 的 `lease.h:16-30` 记录了这个坑：服务端保留旧 deadline 而客户端已按新 TTL 计算，会出现「客户端还在读，服务端已淘汰」。单机场景同样成立。
4. **chunk 粒度 ≠ 引擎页粒度**。LMCache 的 256 与 vLLM 的 16 不对齐时，中间会出现重叠覆盖重算（`cache_engine.py:944-956`），而且**整 prompt 全命中时必须重算最后一个 token**（`vllm_v1_adapter.py:1450-1452`）。llama.cpp 的三级缓存如果自己定 chunk 粒度，一开始就要和 slot 容量对齐。
5. **整会话 blob 与块级 KV 是两种能力，不能混谈收益**。opaque state blob（llama.cpp `llama_state_seq_*_ext`、Strata session 文件）能跳过整段前缀的 prefill，但**每个会话的公共前缀仍各存一份**，下沉 L2 也不会减少重复；块级 KV（chunk/page/slot）才能让公共前缀被共享、被部分下放。谈「三级缓存省了多少」时必须先说清是哪一种，否则容量收益会被高估。
6. **键必须带身份，否则跨重启就是静默错误**。只有 token 序列的哈希在进程内勉强够用，一旦落盘就要加模型/引擎版本/KV dtype/RoPE 配置：Strata 用 config + 模型采样指纹，Mooncake 与 LMCache 把模型名/rank/dtype 编进 key，KVMem 用 `BackendIdentity{backend,revision,model,state_schema}`。哈希相同不等于状态可恢复。

---
