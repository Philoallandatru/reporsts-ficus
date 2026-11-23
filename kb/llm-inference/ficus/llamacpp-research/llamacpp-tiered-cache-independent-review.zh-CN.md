---
type: Concept
title: llama.cpp 三级缓存方案：独立第二意见审查
description: 日期：2026-09-27。审查对象是本目录中主要由另一个模型完成的方案、源码审计与实测（下文统称“原研究”）。本轮只读：没有修改任何已有文件，没有启动
  llama-server、GPU 基准或长时间进程。所有结论都重新追到本地源码、本地实
tags:
- llm
- llamacpp
- kv-cache
sources:
- c:/Users/Administrator/Documents/Code/my-code/lm-llama/research/llamacpp-tiered-cache-independent-review.zh-CN.md
createdAt: '2026-11-23'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# llama.cpp 三级缓存方案：独立第二意见审查

日期：2026-09-27。审查对象是本目录中主要由另一个模型完成的方案、源码审计与实测（下文统称“原研究”）。本轮只读：没有修改任何已有文件，没有启动 llama-server、GPU 基准或长时间进程。所有结论都重新追到本地源码、本地实测原始数据或一手网页。标注约定：**[核实]** 表示已对照一手来源确认；**[推断]** 表示基于已核实事实的推导或判断；**[未核实]** 表示没有独立复核。

## 结论摘要

1. **可行性：有条件可行，但在本机当前负载上还不值得做 L2。** 技术上，固定合法边界的 Prefix State Blob 可以从 SSD 恢复并且结果正确，单次命中的代价远低于重算。经济上，只有当“暂停后会回访”的会话状态真正超过 L0+L1 预算时，SSD 才有增量价值。现有真实 Agent 轨迹离这个条件还差得远。
2. **盈亏平衡不受带宽约束。** 按本机实测参数，SSD 恢复路径的有效吞吐约 2.2 GB/s，重算约 0.53 ms/token。前缀超过约 135 tokens 时恢复就比重算快；4K 前缀只需约 110 MB/s 的读带宽即可打平。真正约束 L2 的是三件事：写入的对象被回访的比例（需超过 5–11%）、合法恢复边界，以及基线是否已调优。
3. **在现有 Pi 轨迹上，缓存收益的上限只有约 1–3% 墙钟时间。** 原生双槽位回放中，剩余 13,457 个 prefill tokens 里约 12,100 个是每轮新增、不可缓存的内容；decode 占了大部分 GPU 时间。因此这条轨迹无论怎么加层都证明不了 L2，必须构造新负载。
4. **块级前缀共享对这个模型“不是做不到，而是小块不划算”。** attention KV 可以按位置截断，recurrent 状态只能在快照边界恢复。vLLM+LMCache 已经对同族 Qwen3.6-27B 用 784-token 块、每块附一份 recurrent 页的方式实现了块级复用。但在 llama.cpp 的 q4_0 配置下，每个 256-token 块要附带 33 倍于其 KV 的 recurrent 状态；块要到约 8K tokens，两者才相当。
5. **与 LMCache 的关系：先引擎内自研，接口按“边界键控的不透明对象”设计。** 原研究漏掉了一件事：LMCache 已经支持 Mamba/GDN hybrid（Qwen3.5/3.6 系列）。真正的阻碍不在 LMCache，而在 llama.cpp 没有 token 区间 KV 导出，也没有块边界 recurrent 快照。
6. **与原研究的主要分歧有四点**：
   - slot 文件恢复失败的根因可以精确定位：保存位置含生成 token，恢复时又丢了检查点。这不能证明 slot 文件路径不可用。
   - 原生 RAM 组的增量小，主要原因是 `f_keep ≥ 0.5` 时根本不查 RAM 缓存，再加上 2048 检查点粒度，不只是“槽位受限”。
   - “一次复用即回本”的比较对象是冷算，而且 SSD 读的是刚写入、反复读取的热文件。
   - try-out 原型的预算记账漏算了检查点，键没有校验，淘汰策略近似随机。
7. **最大技术风险是静默错误**：recurrent 快照与 KV/token 边界错位后，模型给出流畅但错误的输出。SGLang 在 2026-09 仍有同类未关闭缺陷（issue #39830），b9209 的 slot 恢复也保留了过期检查点。其次是引擎线程同步导出造成的全局停顿，以及与上游 `--cache-disk` 方向分叉。

---

# 第一部分：可行性

## 0. 核对范围与版本

本轮涉及三个 llama.cpp 版本，结论不能混用。

| 版本 | 用途 | 说明 |
|---|---|---|
| b9209 / `0caf2a1d4` | 全部历史实测所用运行时 | 用 `git show 0caf2a1d4:<path>` 读取，下文记作 `b9209:路径:行` |
| `f5e85d43a`（2026-08-28） | `llama.cpp/` 只读参考 clone | 下文不加前缀的 `llama.cpp/...` 行号均指此版本 |
| `56b9eb280`（2026-09-12） | `try-out/llama.cpp/` 的基线 | **[核实]** 它比参考 clone 新 264 个提交，也不是 b9209；原研究文档没有提到这一点 |

b9209 是另外两个版本的祖先。由此得出一条约束 **[推断]**：以后正式对比时，原生组也要用 `56b9eb280`（关闭新功能）构建，不能拿 b9209 二进制当原生基线。

## 1. llama.cpp 现有缓存与状态机制（逐项核实）

| 机制 | 行为 | 位置 |
|---|---|---|
| slot 选择 | 先按 LCP 相似度选空闲 slot（阈值 `slot_prompt_similarity`，默认 0.1）。只有 `f_keep < 0.5`（即将丢掉该 slot 大半上下文）时才触发 RAM 缓存保存与加载；否则直接用该 slot，完全不查 RAM 缓存。选不中时按 LRU 选，并总是触发缓存更新 | `llama.cpp/tools/server/server-context.cpp:1549-1621`，其中 `1595`；b9209 同逻辑见 `b9209:tools/server/server-context.cpp:1147-1156`；默认值 `llama.cpp/common/common.h:694`；参数 `-sps` 见 `llama.cpp/common/arg.cpp:3804-3809` |
| RAM 缓存触发点 | 在选 slot 时于引擎线程同步执行：先 `prompt_save` 当前 slot，再 `prompt_load` 最佳条目，最后 `update` | `server-context.cpp:1625-1643`；上游在此留有 TODO：“move slot to level 2 cache instead of removing?”（`server-context.cpp:1650-1655`） |
| `cache_prompt` | 求当前 slot tokens 与新 prompt 的最长公共前缀，得到 `n_past` | `server-context.cpp:3190-3192` |
| `--cache-reuse N` | 在 `n_past` 之后查找长度 ≥N 的相同块，用 `seq_rm` 加 `seq_add` 平移 KV。启动时只有多模态或 `llama_memory_can_shift()==false` 时才关闭 | `server-context.cpp:3200-3257`、`1179-1195`；参数 `common/arg.cpp:3591-3597` |
| hybrid 下的 `can_shift` | hybrid 直接返回 attention 部分的值，recurrent 本身也返回 true，因此 hybrid 模型不会在启动时关闭 `--cache-reuse` | `src/llama-memory-hybrid.cpp:133-136`、`src/llama-memory-recurrent.cpp:716-719` |
| RAM prompt cache 对象 | 一个条目包含完整 target/draft 序列状态、token 序列和该 slot 的全部检查点。`size()` = 状态字节加所有检查点字节 | `tools/server/server-task.h:566-633` |
| RAM 准入与淘汰（上游 HEAD） | 新 prompt 已被某条目完全包含时不存；单条超过限额时拒绝；先移除被新 prompt 包含的旧条目；按插入顺序从表头淘汰直到放得下；`update()` 再施加字节与动态 token 两种约束 | `server-task.cpp:1711-1791`、`1870-1895` |
| RAM 淘汰（b9209） | 两个淘汰循环都要求 `states.size() > 1`，即至少保留 1 条，因此正值限额不是硬上限 | `b9209:tools/server/server-task.cpp:2130`、`2148` |
| RAM 命中语义 | 候选需满足 `f_keep ≥ 0.25`，且 keep 与 sim 两项同时优于当前值。命中后把状态装入 slot、释放主机字节，并从列表删除该条目。语义是交换，不是共享只读副本 | `server-task.cpp:1793-1868`（`1813`、`1839`、`1864`） |
| 序列状态 API | `llama_state_seq_{get,set}_data[_ext]` 以及 `save/load_file`，参数只有 seq_id、缓冲区和 flags，没有 token 区间 | `include/llama.h:869-937` |
| flags | `PARTIAL_ONLY=1`（只处理 SWA/recurrent 这类“部分状态”）；`ON_DEVICE=2`（保留在设备上；同一 seq 再取会使之前取得的状态失效） | `include/llama.h:906-916` |
| 同步 | `get_data_ext`、`set_data_ext`、`save_file`、`load_file` 入口都先 `ctx->synchronize()` | `src/llama-context.cpp:4166-4196` |
| hybrid 序列化 | 不带 `PARTIAL_ONLY` 时写 attention 加 recurrent，带上时只写 recurrent | `src/llama-memory-hybrid.cpp:190-202` |
| KV 序列化粒度 | 遍历属于该 seq 的全部 cell 并按区间写出，每 cell 附 pos、seq_id 等元数据；没有任意 token 区间导出 | `src/llama-kv-cache.cpp:2094-2160`、`2244-2276` |
| 检查点创建（HEAD） | 仅在 memory 不支持部分删除、只能有界回退或使用 SWA 时创建。在用户消息起点，以及距 prompt 末尾 `4+n_ubatch` 和 `4` tokens 处切分 batch 并创建；间距受 `--checkpoint-min-step` 约束；内容为 `PARTIAL_ONLY` 的 recurrent 状态 | `server-context.cpp:3433-3446`、`3522-3548`、`3590-3608`、`2296-2344`（`2336`） |
| 检查点创建（b9209） | 使用 `--checkpoint-every-n-tokens` 做周期性检查点 | `b9209:tools/server/server-context.cpp:2865-2876` |
| 检查点恢复 | 当 `pos_min ≥ pos_min_thold` 时，从新到旧找满足 `pos_min < thold` 的检查点并装入，把 `n_past` 截到检查点位置；找不到就从 0 重算。随后删除所有 `pos_max > pos_next` 的检查点 | `server-context.cpp:3263-3374` |
| 至少重算 1 token | 全部命中时 `n_past--`，以便取得 logits | `server-context.cpp:3376-3381`（`TAG_PROMPT_LOGITS`） |
| `kv_unified` 与 idle slots | HEAD：`--cache-idle-slots` 只需要 RAM 缓存；有 unified KV 时保存后清空 idle slot，无 unified 时只发布副本。b9209：必须同时有 `--kv-unified` 和 `--cache-ram` | `server-context.cpp:1420-1432`、`2409-2423`；`b9209:tools/server/server-context.cpp:1028-1038`；`include/llama.h:406` |
| slot 文件保存与恢复 | 保存：`llama_state_seq_save_file`，即 tokens 加 flags=0 的完整状态，不含检查点列表。HEAD 恢复时 `slot->prompt.clear()`，检查点一并清空；**b9209 恢复时只替换 tokens，旧检查点列表保留** | `server-context.cpp:2518-2620`（`2612`）；`b9209:tools/server/server-context.cpp:2055-2087` |

### 1.1 为什么 hybrid 模型不能按任意 token 位置截断恢复 [核实]

1. recurrent 状态只代表“处理到最后一个位置为止”的结果。`seq_rm(p0, p1)` 截掉尾部时，只有回退量不超过 `n_rs_seq`（为 MTP/投机解码保留的逐 token 快照数）才会成功，否则返回 false。源码注释直接说明：这类模型“can't have a state partially erased at the end”（`src/llama-memory-recurrent.cpp:161-216`，特别是 `182-203`）。
2. hybrid 的 `seq_rm` 先删 recurrent 部分，失败就整体失败（`src/llama-memory-hybrid.cpp:143-149`）。`seq_pos_min` 取两部分中的较大值（`172-175`），所以只要 recurrent 停在末尾，`pos_min` 就接近序列末尾。
3. 因此 server 发现新 prompt 在 slot 末尾之前就分叉时，`pos_min ≥ pos_min_thold` 成立，只能找一个早于分叉点的检查点，把实际复用长度截到该点，然后重算其后的 tokens（`server-context.cpp:3325-3362`）。**逻辑 LCP 与实际复用长度之间的差，由检查点的分布决定。**

本地日志把这一点量化了：

- `research/llamacpp-cache-logs/cache_ram_slot_save.log:75-78`：`n_past = 972`，但可用检查点在 475，实际只复用 475 tokens。
- `research/pi-cache-bench/runs/20260914-091733-replay-ram-c2-r1/server.log:67-71` 及其后多处：两个会话共享 2179 tokens 的系统前缀，切换会话后都只能恢复到 2048 处的周期检查点。

### 1.2 对这个模型，块级（chunk 级）前缀共享是否根本做不到？

**结论：前缀型块共享可以做到，但单块很小时代价高到不划算；非前缀块复用（CacheBlend 类）对 recurrent 状态在原理上不成立，除非接受近似。** 分三层说明：

- **(a) 同一前缀、不同延伸长度之间共享 attention KV 块。** 原理上可行 **[核实]**。attention KV 按位置存储，可以截断（`llama-kv-cache` 支持部分 `seq_rm`）。恢复到边界 k 需要两样东西：`[0,k)` 的 KV，加上**恰好在 k 处**的 recurrent 快照。业界已有实现：
  - LMCache 的 MP connector 与 vLLM `--mamba-cache-mode align` 配合，把 recurrent 状态当作每个块的“不透明页”存取，块大小取 vLLM 统一块大小 N，Qwen3.6-27B 的 N 为 784（`LMCache/docs/source/mp/hybrid_models.rst:133-230`；`LMCache/lmcache/integration/vllm/kv_cache_groups.py:59-71`；`LMCache/lmcache/integration/vllm/lmcache_mp_connector.py:148-176`）。
  - SGLang 的 MambaRadixCache 只在“有 Mamba 状态的节点”上命中，并用两条 LRU 分别淘汰 KV 与 Mamba 状态（[PyTorch/SGLang 博客](https://pytorch.org/blog/hybrid-models-meet-sglang-more-than-full-attention/)）。
- **(b) 在 llama.cpp 中实现 (a) 的缺口。** 其一，没有 token 区间 KV 导出/导入 API（`include/llama.h:869-937`、`src/llama-kv-cache.cpp:2094-2160`）。其二，prefill 期间需要在每个块边界切 batch 并导出一次 150 MiB 的 recurrent 快照；现有检查点机制正是这样做的，只是频率受 `checkpoint-min-step` 限制，且每次都是同步 D2H。
- **(c) 经济性 [推断，基于实测字节]。** 每个边界快照 b ≈ 156.9 MB，每 token KV 为 a = 18,452 B。块大小为 c 时，recurrent 与 KV 的字节比为 `b/(c·a)`：c=256 时 33.2 倍，c=784 时 10.8 倍，c=2048 时 4.2 倍，c=8192 时 1.04 倍。也就是说，只有“少量高价值边界”（系统提示末尾、消息边界）上的快照才划算。原研究的另一个判断成立：对 8K、带 4 个检查点、共约 892 MiB 的条目，即使 KV 完美去重，最多也只省约 16%（`llamacpp-tiered-cache-design.md` §7）。
- **(d) 非前缀复用、任意 token 粒度复用。** recurrent 状态依赖全部前文，不存在“脱离前文的块状态”。近期的 Tail-Replay 用“缓存 attention 数据，再重放一小段后缀来重建线性层状态”实现 token 级复用，但它是有损近似，报告质量保持 92.8–99.9%（[arXiv:2608.30310](https://arxiv.org/abs/2608.30310)），不满足本项目“logits 一致”的正确性标准。

## 2. 分层的经济学：盈亏平衡模型

### 2.1 实测参数（全部来自本机）

数据源：`research/prefix-state-bench/runs/20260913-122835-full/summary.json`、`results.jsonl` 的 snapshot 事件，以及 `report.md`。模型为 Qwen3.8-27B IQ3_XXS，K/V 为 q4_0，batch/ubatch = 2048/512，运行时 b9209；每条路径 30 个样本，报告 p50 与分量均值。

| 参数 | 值 | 推导 |
|---|---:|---|
| 状态字节 S(4K/8K/16K) | 232,474,156 / 308,053,548 / 459,212,332 B | results.jsonl `state_bytes` |
| 每 token 边际字节 a | **18,452 B** | 相邻两点之差 ÷ 4096。其中 18,432 B 是 q4_0 KV，约 20 B 是每 cell 元数据（`llama-kv-cache.cpp:2244-2276`） |
| 固定部分 b | **156.9 MB（149.63 MiB）** | 截距；与日志中每个检查点 149.626 MiB 吻合 |
| 重算速率 R_p | **≈1,885 tok/s（0.530 ms/token）** | 冷算 p50 的斜率：(8718.1−2200.1)/(16384−4096) |
| SSD 读（无缓冲） | 4.5–4.8 GB/s | S/read_ms，例如 232.5 MB / 51.0 ms；包含打开与关闭 |
| 校验（XXH3） | ≈11.7 GB/s | S/verify_ms |
| H2D 安装 | ≈7.7–7.9 GB/s | S/install_ms |
| D2H 导出 | 6.8–8.5 GB/s | S/export_ms（34.3 / 36.4 / 59.0 ms） |
| 写入并 flush | **≈1.06–1.11 GB/s** | S/(write+flush)：218 / 292 / 415 ms |
| RAM 首次保存（分配、导出、校验） | 118.8 / 130.7 / 187.0 ms | snapshot `ram_save_total_ms`；其中分配（首次触页）占 65–94 ms |
| 后缀 128 tokens 的 prefill | 87–99 ms | 各路径相同，在比较中抵消 |

按字节线性拟合，恢复开销（不含后缀）为：SSD 路径约 **0.450 ms/MB（等效 2.22 GB/s）**，RAM 路径约 **0.223 ms/MB（等效 4.49 GB/s）**，截距都接近 0。

`llamacpp-tiered-cache-hardware.json` 只有设备清单和空闲时的 PCIe 链路状态（5080 当前 Gen1 x16，最大 Gen5 x16），**没有任何 SSD 或 PCIe 带宽实测**。上表带宽都是从基准分量反推出来的，含 API 与文件系统开销。

### 2.2 公式

令 N 为可合法恢复的前缀长度（token），`S(N) = a·N + b`：

```text
T_re(N)   = N / R_p                                   # 重算前缀
T_L(N)    = S(N) · (1/B_read,L + 1/B_verify + 1/B_H2D) # 从层 L 恢复
            = S(N) / B_eff,L
恢复优于重算  ⇔  T_L(N) < T_re(N)
          ⇔  N > N* = b / (B_eff,L / R_p − a)
渐近加速比（N→∞）= B_eff,L / (a · R_p)
单次命中收益 Δ_L(N) = T_re(N − k_alt) − T_L(N)
      （k_alt：不用该层时原生仍能复用的长度，例如共享系统提示对应的检查点）
写入回本（单个对象，按命中概率 p 摊销）：p · Δ_L2 > C_write = S(N)/B_write
          ⇔  p > p* = C_write / Δ_L2
```

### 2.3 代入数字

| N | S(N) | T_re | T_SSD | T_RAM | 重算/SSD | 打平所需最低读带宽 |
|---:|---:|---:|---:|---:|---:|---:|
| 512 | 158.6 MiB | 272 ms | 74 ms | 37 ms | 3.7× | 705 MB/s |
| 1K | 167.6 MiB | 543 ms | 78 ms | 39 ms | 7.0× | 348 MB/s |
| 2K | 185.7 MiB | 1,086 ms | 86 ms | 43 ms | 12.6× | 186 MB/s |
| 4K | 221.7 MiB | 2,173 ms | 103 ms | 52 ms | 21.0× | 110 MB/s |
| 8K | 293.8 MiB | 4,345 ms | 137 ms | 69 ms | 31.8× | 72 MB/s |
| 16K | 437.9 MiB | 8,691 ms | 204 ms | 102 ms | 42.6× | 53 MB/s |
| 32K\* | 726.3 MiB | 17,381 ms | 338 ms | 170 ms | 51.4× | 44 MB/s |

\* 32K 超出实测范围，是按线性外推的 **[推断]**。attention 成本随长度增长，实际重算会更慢，加速比只会更大。短前缀的实际 prefill 速率低于 1,885 tok/s（例如日志中 517 tokens 为 1,401 tok/s），所以短前缀一端的估计偏保守。

- **N\*（SSD）≈ 135 tokens，N\*（RAM）≈ 66 tokens；渐近加速比：SSD 约 64 倍，RAM 约 129 倍。** 实测 16K 含后缀的端到端加速为 29.5 倍，与模型一致（后缀约 98 ms 摊薄了比值）。
- 以“最低读带宽”一栏看，4K 前缀只要约 110 MB/s 就能打平。**SSD 带宽不是约束 [推断]。** 原因是这个 27B 模型在本卡上重算很贵（约 1.9k tok/s），而状态很小：只有 16 层 full attention，q4_0 KV 每 token 18 KiB。这个结论不能外推到每 token KV 大 1–2 个数量级的纯 Transformer。
- **写入回本**（用实测配对收益中位数）：p\* = 218/2008 = **10.9%**（4K）、292/4079 = **7.2%**（8K）、415/8415 = **4.9%**（16K）。换句话说，写进 SSD 的对象只要有 5–11% 以后被读回，写盘的磁盘时间就能回本。如果写盘在后台进行、不与读竞争，占用 GPU 或引擎线程的只有同步导出（119–187 ms，其中触页分配 65–94 ms 可以用缓冲池消除）。按这部分计算，p\* 只有 2–6%。“需要复用几次才回本”的准确说法是：**只要被复用一次就回本；真正的门槛是命中概率 p\***。
- **容量**：固定边界对象为 222–438 MiB（4K–16K）。原生条目带 C 个检查点，为 `N·18 KiB + (C+1)·149.6 MiB`；8K 带 4 个检查点约 892 MiB。16 GiB 的 L1 约放得下 55 个 8K 固定边界对象，或 18 个带 4 个检查点的原生条目 **[推断]**。本机空闲 RAM 采样值为 27–40 GiB（`llamacpp-tiered-cache-hardware.json`、bench 报告“系统可用内存最低 27.09 GiB”），因此 L1 本身就能容纳几十个会话。
- **SSD 寿命**（公式，缺少 TBW 数据，未代入）：日写入量 = 每日新准入 L2 对象数 × S(N)。准入策略必须把 p\* 作为下限，否则写放大直接转化为磨损。

### 2.4 上限检查：现有真实轨迹里有多少可省的时间？

对 `research/pi-cache-bench/runs/20260914-093413-replay-slot-c2-r1-slots2/requests.jsonl`（原生双槽位，58.45 s）逐请求统计：prefill 共 13,457 tokens（13.8 s），decode 共 74.4 s（两个 slot 并发，与 prefill 部分重叠）。

每轮“相对上一轮 prompt 加生成内容的新增 token”合计约 **12,145**（首轮全量计入）**[推断，按 usage 近似，未重新分词]**。所以理想缓存最多还能再省约 1.3K tokens（约 0.7 s）。即使把两个会话共享的 2179-token 系统前缀也算进去，也不到约 3.5K tokens（约 1.8 s），相当于整批墙钟的 **1–3%**。

**这条轨迹在原理上无法显示 L2 的收益**，原方案“E 相对 C 的 p95 TTFT 降低 20%”的门槛在它上面不可能达到。benchmark 必须换负载（见第二部分）。

## 3. 与 LMCache 的关系

### 3.1 LMCache 的契约（对照 `LMCache/` a0e4a4c2 源码）[核实]

- **GPU 连接器**：`to_gpu/from_gpu/batched_*` 以 `MemoryObj` 和 `[start, end)` token 区间为单位，读写引擎注册的 KV 张量（`lmcache/v1/gpu_connector/gpu_connectors.py:45-110`）。它要求引擎暴露按 token 可寻址的张量布局。
- **chunk 与 hash**：`ChunkedTokenDatabase` 默认 `chunk_size=256`，用链式前缀哈希，每块的哈希包含父哈希（`lmcache/v1/token_database.py:298-420`，默认值在 `329`）。
- **对象与 L2**：`ObjectKey = (chunk_hash, model_name, kv_rank, object_group_id, cache_salt)`（`lmcache/v1/distributed/api.py:82-130`）。L2 适配器是一组异步接口：store、lookup_and_lock、load（`lmcache/v1/distributed/l2_adapters/base.py:80`、`206-330`），已有 fs、nixl、s3、mooncake、valkey 等十余种实现（同目录）。`MemoryFormat` 含 `BINARY` 与 `BINARY_BUFFER`（`lmcache/v1/memory_management.py:77-97`），存储层本身不强制对象必须是 KV 张量。
- **hybrid 支持**：LMCache 通过 `--separate-object-groups` 把 recurrent 层分成单独的对象组，把 conv 加 SSM 状态“reinterprets … as an opaque page”，每块一页，恢复时只取最后匹配块的页。前提是引擎在每个块边界都产出 recurrent 快照（vLLM `align` 模式）。文档还注明缓存与冷算结果“not bit-exact”（`LMCache/docs/source/mp/hybrid_models.rst:133-250`）。

### 3.2 能否用于 llama.cpp 的 hybrid 状态

| 层次 | 能否直接复用 | 原因 |
|---|---|---|
| L2 存储、异步任务、配额、可观测性 | **能**（需要适配） | 可以把 Prefix State Blob 当作一个 `BINARY` 对象，用“边界哈希”作 `chunk_hash`。代价是要跑一个 Python 服务或进程，并经 ZMQ 多一跳；按 256-token 设计的 L1 分配与淘汰也要重新检查 **[推断]** |
| chunk 前缀查找（lookup） | **不能直接用** | LMCache 找的是“连续命中的最长块链”。llama.cpp 的合法恢复点是稀疏的检查点边界，一个 blob 大小可变（150 MiB 起），不是等长块 |
| GPU 连接器（KV 张量协议） | **不能** | llama.cpp 没有 token 区间 KV 导出，也没有块边界 recurrent 快照（§1.2(b)）。要做就得修改 libllama：暴露按层、按 cell 区间的张量视图，并在块边界切分 prefill、导出 recurrent |
| hybrid 语义 | 思路可借鉴 | LMCache/vLLM 的“每块一页 recurrent”是现成设计。在 llama.cpp q4_0 下块必须大（§1.2(c)），否则存储放大 10–33 倍 |

### 3.3 两条路线的比较 [推断]

| 维度 | A：引擎内自研分层（`server_prompt_cache` 加 SSD 后端） | B：接入 LMCache |
|---|---|---|
| 首个可验证结果 | 快：改动集中在 `tools/server`，对象就是现有 `server_prompt_cache_state` | 慢：B1（只借 L2 存储）要写 C++↔Python 的 IPC；B2（KV 张量协议）要改 libllama |
| hybrid 正确性 | 复用原生检查点语义，恢复路径与 RAM 缓存相同，便于做对照 | B2 要新造边界快照；LMCache 自己也声明 hybrid 结果不是逐位一致 |
| 容量效率 | 一个对象一份完整状态，公共前缀不去重（对此模型最多损失约 16%，§1.2(c)） | B2 可以去重 attention 块，但 recurrent 页占大头 |
| 多实例或跨节点共享 | 不支持 | 这是 LMCache 的核心价值（P2P、Mooncake、S3 等） |
| 与上游的关系 | 上游正走这个方向：PR [#28092](https://github.com/ggml-org/llama.cpp/pull/28092)（`--cache-disk`，含 hybrid/SWA 检查点持久化，未合并）、PR [#24028](https://github.com/ggml-org/llama.cpp/pull/24028)（slot 检查点 sidecar，未合并）、issue [#20697](https://github.com/ggml-org/llama.cpp/issues/20697)。#28092 的作者在讨论中转述，维护者 ngxson 本地有一个“基于定长 token 块链式哈希”的实现（二手转述，未见原话）| 独立于上游节奏 |
| 适用本机的判断 | **推荐作为第一步** | 仅当出现多实例或跨机共享需求时再考虑 B1；B2 投入最大、收益最不确定 |

建议 **[推断]**：走路线 A，但把对象协议设计成 `(兼容域指纹, 边界 token 哈希链, 边界位置 k) → 不透明 blob + 检查点列表`。这样日后既能挂到 LMCache L2 适配器，也能与上游可能的“块哈希”方案对齐。同时密切跟踪 #28092 和 ngxson 的方案，避免维护一个注定被上游替换的分叉。

## 4. 业界先例（一手来源）

| 系统 | 做法 | 对本项目的启示 |
|---|---|---|
| vLLM APC | 按块哈希做前缀复用；只减少 prefill，不减少 decode；新请求没有共享前缀时无收益（[官方文档](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html)） | 与本机 Pi 轨迹中 decode 占主导一致 |
| vLLM KV offloading 与 connector | `OffloadingConnector` 把已完成的 KV 块异步 DMA 到 pinned CPU 内存，可叠加文件系统等二级层；另有 LMCacheConnectorV1、NixlConnector、MooncakeConnector 等（[Offloading 使用指南](https://docs.vllm.ai/en/latest/features/kv_offloading_usage/)、[disagg/connector 文档](https://docs.vllm.ai/en/latest/features/disagg_prefill.html)、[vLLM 博客](https://blog.vllm.ai/2026/01/08/kv-offloading-connector.html)） | 依赖“按块可寻址的分页 KV”加异步 DMA，llama.cpp 两者都没有 |
| SGLang RadixAttention | radix 树管理 KV 复用、LRU 淘汰、缓存感知调度（[arXiv:2312.07104](https://arxiv.org/abs/2312.07104)） | 前缀索引的标准形态 |
| SGLang HiCache | L1 GPU、L2 主机 DRAM、L3 存储后端；HiRadixTree；写策略 write_through / write_through_selective / write_back；预取终止策略 best_effort / wait_complete / timeout（[设计文档](https://docs.sglang.io/advanced_features/hicache_design.html)） | “选择性写入”对应本文的 p\* 准入。hybrid 接入 HiCache 仍在进行中，存在静默错误缺陷 [#39830](https://github.com/sgl-project/sglang/issues/39830)（2026-09-16 提交，未关闭：宿主层命中 0/20 正确，疑似 Mamba 检查点与 KV 位置错位） |
| SGLang MambaRadixCache | 只在带 Mamba 状态的节点命中；KV 与 Mamba 状态分别用 LRU 淘汰；指出 SSM 状态“比单 token 的 KV 大几个数量级”（[PyTorch 博客](https://pytorch.org/blog/hybrid-models-meet-sglang-more-than-full-attention/)） | 与本模型一次 150 MiB 对 18 KiB/token 的情况完全一致 |
| LMCache | 引擎外 KV 层，支持 offload 与 P/D 分离，论文报告与 vLLM 结合“最高 15 倍吞吐”（[arXiv:2510.09665](https://arxiv.org/abs/2510.09665)）；hybrid 支持见 §3.1 | 其 AMD 文章说低负载、工作集放得进 HBM 时原生前缀缓存胜出，与本文的对照组设计一致（原研究已引） |
| Mooncake | 以 KVCache 为中心的 P/D 分离架构，用 CPU、DRAM、SSD 组成 KV 池，过载时基于预测提前拒绝请求（[arXiv:2407.00079](https://arxiv.org/abs/2407.00079)；FAST'25，[USENIX 页面](https://www.usenix.org/conference/fast25/presentation/qin)） | 集群级方案，与单机单卡关系不大 |
| CachedAttention / AttentionStore | HBM、DRAM、SSD 三层保存多轮对话 KV；逐层预加载与异步保存；利用调度器提示预取和淘汰；位置编码解耦；TTFT 最多降低 87%（[arXiv:2403.19708](https://arxiv.org/abs/2403.19708)，USENIX ATC'24） | 与本方案最接近：多轮会话 + SSD。它的“调度器感知预取”依赖已知的会话队列，本项目可以用 Agent 工具间隙作为提前量 |
| llama.cpp 上游 | host 内存 prompt cache（[PR #16391](https://github.com/ggml-org/llama.cpp/pull/16391)，2025-10 合并，仅 RAM）；SWA 检查点与 `_ext` 状态 API（[PR #15293](https://github.com/ggml-org/llama.cpp/pull/15293)，2025-08 合并）；磁盘层 #28092、#24028、#20697 见 §3.3 | #24028 正好对应本文 §5 E3 定位的“slot 文件丢检查点”问题；审查者还指出 `data_spec` 未被序列化 |
| 线性注意力前缀缓存研究 | Tail-Replay 通过重放后缀重建线性层状态，实现近似的 token 级复用（[arXiv:2608.30310](https://arxiv.org/abs/2608.30310)） | 有损，不满足本项目的正确性标准 |

## 5. 对原研究的核实

### 5.1 站得住的关键结论 [核实]

1. **状态尺寸模型**：18 KiB/token 的 KV 加每个边界 149.626 MiB 的 recurrent 状态。bench 实测的斜率 18,452 B/token 与截距 156.9 MB 独立印证了这一点（`llamacpp-tiered-cache-evaluation-and-implementation.md` §7；`llamacpp-tiered-cache-design.md` §3）。
2. **固定合法边界的恢复正确且更快**：logits 最大差 0.0，128 个 greedy token 一致；SSD 路径 p50 为 187.6 / 219.2 / 295.6 ms，重算为 2200.1 / 4296.2 / 8718.1 ms（`prefix-state-bench/runs/20260913-122835-full/report.md`、`summary.json`）。
3. **`llama_state_seq_*` 入口同步**：放进后台线程也得不到计算重叠（`src/llama-context.cpp:4166-4196`）。
4. **`PARTIAL_ONLY` 是“状态组件”而不是“token 区间”；`ON_DEVICE` 会使之前的状态失效**（`include/llama.h:906-916`、`src/llama-memory-hybrid.cpp:190-202`）。
5. **RAM 缓存语义**：命中即交换（条目被移出）、没有块去重、HEAD 在分配前拒绝超额对象、b9209 至少保留 1 条（§1 表）。
6. **Pi 回放数值**：双客户端下整批时间 111.20 / 87.52 / 80.84 s，RAM 组比 slot 组少 7.6%，prefill 时间少 29.6%；原生双槽位 58.45 s；RAM 峰值 1506 MiB（`pi-cache-bench/results/report.md`、`slot-calibration.json`）。
7. **方法论约束**：对照必须是调优后的原生配置；SSD 的容量收益必须在工作集自然越过 RAM 时证明；不能把页缓存命中当成设备读；p95 与 p99 需要足够样本（原研究第 2–4 节）。本文完全认同这些约束。
8. **“KV 块完美去重最多省约 16%”** 的算术正确（144/892）。

### 5.2 错误、证据不足或措辞过度之处

| 编号 | 原研究说法 | 问题 | 证据 |
|---|---|---|---|
| E1 | “三种长度均在一次后续复用后回本”（主方案 §9、bench 报告） | 算术没错，但**比较对象是冷算**，不是原生仍能复用的部分（k_alt），也不是 RAM 层。每个长度只有 1 个保存样本。SSD 读是对刚写入的同一文件读 30 次，控制器或 SLC 缓存很可能是热的，“无缓冲”只绕过了 OS 缓存。“单次回访即回本”应改写为“命中概率 p > p\*（5–11%）即回本”，并补上冷设备读 | `results.jsonl` 的 snapshot 事件每个前缀只出现 1 次；`prefix-state-bench/README.md` 的“What is measured”一节 |
| E2 | 手动 slot save/restore 后 `cached_tokens=0`，归因于“很可能与 SWA/hybrid/recurrent 处理有关”，并由此认为“只把原生 `.bin` 塞入多级缓存还不够” | 根因可以精确定位 **[核实]**：保存时 slot 含生成 token（993 个 tokens，而新 prompt 只有 990 个），新请求在 990 处分叉，需要回退 recurrent；恢复后检查点列表为空，只能从 0 重算。换成严格延伸已保存 tokens 的请求就能命中（`n_past == slot tokens` 时不走检查点分支）。结论方向（需要检查点或 prompt 末尾边界）是对的，但这次实验不能证明 slot 文件路径不可用 | `research/llamacpp-cache-logs/cache_ram_slot_save.log` 末段（task 175：`n_past = 990, slot.prompt.tokens.size() = 993` 后紧接 `forcing full prompt re-processing`）；`b9209:tools/server/server-context.cpp:2586-2588`、`2689` |
| E3 | 双客户端单槽位下 RAM 增量“只适用于槽位受限场景” | 遗漏了主要机制 **[核实]**。两个会话共享 2179 tokens 的系统前缀，`f_keep ≈ 0.7 ≥ 0.5`，于是 slot 被“按 LCP 选中”后**根本不查 RAM 缓存**，每轮只有 5 次 “found better prompt”。复用又被截到 2048 周期检查点。因此 `ram` 组不是“调优后的 RAM 层”，`-sps` 等调优没有试过，“RAM 层价值”被低估 | `b9209:tools/server/server-context.cpp:1147-1156`；`pi-cache-bench/runs/20260914-091733-replay-ram-c2-r1/server.log:67-190`；`results/report.md` 的“每轮 RAM 找到更好前缀事件数 5, 5” |
| E4 | 下一阶段验收目标“E 相对 C 的 p95 TTFT 降低至少 20%”（主方案 §4.3、设计 §11） | 没有配套的“可省时间上限”分析。在现有 Pi 轨迹上，上限只有 1–3%，该门槛不可达。这不是负载的错，而是说明这条轨迹不适合检验 L2 | §2.4 |
| E5 | “检查点策略就是缓存容量策略”（设计 §3） | 方向对，但需要补充：对 Agent 对话，全状态末尾的那份 recurrent 状态常常用不上。1343 会话第 2 轮的复用点是 prompt−4 处的检查点（cache 2992 对 prompt 2996）；而 1359 第 2 轮复用到了生成段（cache 2959 > prompt 2881）。两种情况都有，应先测出“末尾状态被直接延续”的比例，再决定 L2 对象是保存末尾状态、prompt 末尾检查点，还是两者都保存 | `pi-cache-bench/runs/20260914-093413-replay-slot-c2-r1-slots2/requests.jsonl` |
| E6 | LMCache 集成缺口的论述（`lmcache-llamacpp-kv-cache.md`、主方案 §8） | **遗漏了 LMCache 已支持 Mamba/GDN hybrid**，包括 Qwen3.5/3.6 系列，Qwen3.6-27B 块大小为 784。缺口在 llama.cpp 侧（区间导出、边界快照），不在 LMCache 能否保存 recurrent 状态 | `LMCache/docs/source/mp/hybrid_models.rst:133-250`；`LMCache/lmcache/integration/vllm/kv_cache_groups.py:59-71` |
| E7 | `--cache-reuse` 在“memory 实现支持 shifting 时”生效（`lmcache-llamacpp-kv-cache.md`） | 对 hybrid 有误导。hybrid 的 `get_can_shift` 返回 attention 部分的值，所以启动时不会关闭；但 KV 平移不会重建 recurrent 状态。历史实验中 reuse256 与普通 RAM 缓存几乎相同，与“对此模型无实效”一致 **[推断]**。建议对此模型保持关闭，或加入正确性探针后再评估 | `src/llama-memory-hybrid.cpp:133-136`；`server-context.cpp:1185-1195`、`3200-3257`；`llamacpp-cache-benchmark-results.md` |
| E8 | “原 working_set_pressure 的 RAM 条目约 2.28 GiB” | 单位笔误：日志是 2280.400 **MiB**（约 2.23 GiB）。不影响“低于 4 GiB”的结论 | `research/llamacpp-realistic-cache-logs/cache_ram_4096.log`（“cache state: 4 prompts, 2280.400 MiB”） |
| E9 | 主方案开头“尚未修改推理引擎”；CLAUDE.md 把 try-out 描述为“三级缓存原型” | 原型只有 L1，SSD 为占位；只能通过 `/tier` 手动触发，不在请求路径上自动查找；`run_tier_cache_eval.py` 没有留下任何结果文件。“三级缓存原型”的说法过度 | `try-out/llama.cpp/tools/server/server-tier-store.h:32-34`（注释 “L2 (SSD) is left as a placeholder”）；`research/` 下没有 tier 评测结果 |
| E10 | 原型的预算与键 | ① `size()` 只算 `data` 加 tokens，**不算快照里克隆的检查点**（每个 149.6 MiB，最多 8 个），实际占用可达记账值的数倍；② 淘汰策略是 `std::map` 中“最小哈希键”，近似随机，还可能淘汰刚插入的对象；③ 64 位 FNV 键在恢复时**不校验 tokens 和兼容指纹**，碰撞会静默装入错误状态；④ 恢复失败时没有清理 slot，可能留下半装状态；⑤ 与原生 `prompt_cache` 并存，违背主方案 §6“接替原生 RAM、避免双份缓存”的要求 | `try-out/llama.cpp/tools/server/server-tier-store.h:8-16`、`27-29`；`server-tier-store.cpp:7-22`；`try-out/llama.cpp/tools/server/server-context.cpp:344-385`、`1414-1420` |
| E11 | 三个版本的关系 | 文档只说“正式对比须同一提交”，没有指出 try-out 基线 `56b9eb280` 与 b9209、与参考 clone 都不同。`run_tier_cache_eval.py` 的三组都用 try-out 构建，内部一致；但不能与 b9209 的历史数字直接比较 | §0 |
| E12 | b9209 slot 恢复的正确性 | 原研究没有指出：b9209 恢复 slot 文件时**不清空旧检查点列表**。如果新请求触发检查点搜索，可能装入属于先前内容的 recurrent 快照，造成静默错误。HEAD 已改为 `prompt.clear()`。这正是 hybrid 分层的核心风险类型 | `b9209:tools/server/server-context.cpp:2076-2087`；`llama.cpp/tools/server/server-context.cpp:2612` |

## 6. 判断：有条件可行

**技术可行性：可行 [核实]。** 固定合法边界的完整状态可以从 SSD 正确恢复，单次命中收益为 2.0–8.4 s 量级，成本在 0.1–0.2 s。

**是否值得：有条件。** 需要**同时**满足以下条件（前两条是负载条件，后两条是工程条件）：

1. **负载条件**：存在大量“暂停后会回访”的会话，其状态总量 W 超过 L0（多 slot）加 L1（RAM 预算）的有效容量。回访距离（按字节计）要大于 L1 预算、小于 L1+L2 预算。本机空闲 RAM 有 27–40 GiB，单个 8K 会话固定边界状态约 0.3 GiB，**要几十个活跃回访会话才会越过 RAM**。当前两个 Agent 的使用方式远未达到。
2. 写入 L2 的对象中，后来被读回的比例超过 p\*（4K 约 11%，16K 约 5%），前缀至少约 1–2K tokens。
3. **工程条件**：在请求路径上自动查找合法边界，统一预算（含检查点、staging 和页缓存），磁盘 I/O 在后台进行，失败时安全回落到重算。
4. **对照条件**：必须赢过调优后的原生配置（多 slot、`-sps`、合适的 `--cache-ram`）。对这个模型，L0 本身就很便宜：每个 slot 约 150 MiB 的 recurrent 状态加每 token 18 KiB，多开 slot 是最便宜的“一层”。

**本机最现实的 L2 价值 [推断]**：一是**进程重启或切换模型后的热启动**，这是 RAM 天然做不到的；二是**多项目、多会话的长间隔回访**；三是 RAM 被其他程序挤占时，把 L1 缩小后用 SSD 兜底。

**最大技术风险（按严重度）**：

1. **静默正确性错误**：recurrent 快照与 token 或 KV 边界错位。旁证有 SGLang #39830（宿主层命中 0/20 正确）、本文 E12（b9209 过期检查点）、E10③（原型键不校验）。这类错误不报错，只有 logits 或 greedy 对照测试能抓到。
2. **引擎线程同步停顿**：`prompt_save/load` 在选 slot 时同步执行（`server-context.cpp:1625-1643`），导出期间所有 slot 都停摆。以 8K 为例，约 131 ms 的导出（其中约 71 ms 是分配触页）会加到其他并发请求的 TTFT 和 ITL 上。
3. **上游分叉**：`--cache-disk`（#28092）和块哈希方案正在上游推进，自研对象格式有被替换的风险。
4. **容量论据可能不成立**：本机 RAM 充裕，多开 slot 也便宜，L2 可能长期只在重启场景有用。

---

# 第二部分：benchmark 设计（可证伪）

## 7. 预先登记的假设

每条假设都带有“什么结果算证伪”：

- **H1（机制）**：从 L2 恢复合法边界后，输出与冷算逐位一致，并且实际跳过的 prefill tokens 等于 k − k_alt。任何不一致即判失败。
- **H2（成本模型）**：单次 L2 命中节省的时间符合 §2.2 公式（`Δ = T_re(k − k_alt) − S/2.22 GB/s`）。实测值偏离预测超过 ±30% 即认为模型被证伪，需要先修正模型再解释收益。
- **H3（容量拐点）**：同一调度器下，W/B1 ≤ 0.5 时 S（RAM+SSD）与 R（RAM-only）差异落在噪声内；W/B1 ≥ 1.5 时 R 的命中率明显下降，S 的 L2 命中率大于 0，p95 TTFT 优势随 W/B1 增大而增大。如果 W/B1 ≥ 1.5 时 S 相对 R 的改善低于门槛，说明 L2 在本机不值得。
- **H4（相对原生）**：在 H3 的获胜区间内，S 仍优于调优后的原生配置 N。如果 N 通过多 slot 就吃掉了大部分收益，结论为“先调原生，不上 L2”。
- **H5（无害性）**：在负对照场景（工作集放得进 RAM、短前缀、无回访）中，S 相对 R 与 N 的退化不超过门槛。

## 8. 场景参数

### 8.1 SSD 应当胜出的场景

| 参数 | 取值 | 依据 |
|---|---|---|
| 工作集与 RAM 预算之比 W/B1 | 0.5、1、1.5、2、4 | W 按实际导出字节（含检查点）的并集计算；0.5 作为内部对照 |
| RAM 预算 B1 | MVP 取 4 GiB；完整版取 4 GiB 与 16 GiB | 4 GiB 便于快速制造压力；16 GiB 贴近本机真实可用内存。**缩小 B1 得到的结论只按 W/B1 的比例外推，并需在 16 GiB 下复核一次** |
| L2 预算 | 64 GiB，保证 ≥ W | G:（BIWIN X570）；目录每次运行新建 |
| 会话数 M | 由 W/B1 与每会话字节反推。例如 B1=4 GiB、8K 固定边界对象 294 MiB 时，M = 7、14、21、28、56；若用原生条目（带 2 个检查点约 593 MiB），M = 4、7、11、14、28 | §2.3 |
| 前缀长度 L | 主场景 8K 与 16K 各半；扫描 2K、4K、8K、16K、24K | 需大于 N\* 两个数量级；上限受 `-c` 约束 |
| 每轮新增 tokens Δ | 从 Pi 实测分布重采样，范围 32–1,723，中位数约 350 | `requests.jsonl` |
| 回访顺序 | ① 循环扫描（对 LRU 最不利，最能暴露拐点）；② Zipf(α=0.8) 热度；③ 按真实 Pi 会话节奏交错 | 设计文档 §2 与主方案 §4.2 |
| 回访距离与暂停时长 | 字节回访距离 D 分布在 B1 到 3·B1；暂停时长为录制的工具间隙 ×{1, 10}（后者模拟人工暂停） | 用“回访前插入了多少其他会话状态字节”来控制，而不是用秒数 |
| 共享前缀比例 | 0%、50%、90%（所有会话共享的系统提示长度占前缀的比例） | Pi 实测为 2179/≈6000，约 35% |
| 并发 | 活跃客户端 1、2；服务 slot 数随组别变化 | 与 Pi 实验一致 |
| 输出 | 固定 64 tokens，使用 `ignore_eos` | 去掉 decode 长度差异；另设长输出对照 |

### 8.2 预期**不会**胜出的对照场景

| 编号 | 场景 | 预期 |
|---|---|---|
| C1 | W/B1 = 0.5（全部放得进 RAM） | S ≈ R；S 多出的写盘不应拖慢 TTFT |
| C2 | 短前缀 L ≤ 1K，每次回访有大量新增 | 收益很小；检验同步导出开销 |
| C3 | 无回访（每个前缀只用一次） | 只有写入成本；检验准入能否把写放大压下来 |
| C4 | 边界失配（历史重渲染使 LCP 小于快照边界，例如重排工具参数 JSON） | S ≈ R ≈ N；这类 miss 不是容量问题，加 SSD 没用 |
| C5 | 长输出（1,024 tokens），其余同主场景 | TTFT 仍有改善，但整批墙钟改善低于主场景的 1/3 |
| C6 | L0 足够：M ≤ 调优原生的 slot 数 | N ≥ S |
| C7 | 重启场景（反向：这是 S 必胜的场景） | 用来验证持久化链路，但**不计入容量收益结论** |

## 9. 负载构造

两者结合：**语义内容来自真实录制，访问形状用 Trace-Shaped 生成器控制**。

1. **扩大真实录制**：用现有 `pi-cache-bench/bench.py live`，在 SWE-bench Lite 中不同仓库的 16–32 个任务上录制，每个任务一个 Pi 会话，保留请求体与工具间隙。现有两个 marshmallow 会话的上下文从 3K 增长到 8.7K，单会话状态低于 1 GiB，两个会话合计的 RAM 峰值只有 1.47 GiB，**不可能越过 4 GiB**。至少需要约 14 个 8K 级会话，才能让原生条目达到 W/B1 = 2。
2. **Trace-Shaped 编排**：生成器从录制会话中取请求序列，按 §8 的顺序、回访距离和共享比例交错。回放照旧只发录制的请求体、不执行工具，与现有回放语义一致。**先离线计算每个会话每轮的状态字节**（用日志中的 “total state size” 与检查点数量，或按 `S = a·N + (C+1)·b` 估算），据此选 M，使 W/B1 达到目标值；运行后再用实测 RAM 条目峰值、L2 写入字节和淘汰事件验证 W 确实越过了 B1。
3. **MVP 的纯合成补充**：MVP 用本地语料（与 prefix-state-bench 相同的源码和文档）生成 M 个首 token 起就不同的前缀，按 token ID 直接续算，避开 chat 模板的影响，专门检验 H1–H3。
4. **防止“人为清空 RAM”**：禁止在运行中手动驱逐或清空。L2 命中必须来自 B1 的自然淘汰，事件日志逐条记录“L1 淘汰 → L2 命中”的对应关系。

## 10. 对照组

所有组使用**同一提交**（`56b9eb280` 加原型；原生组用同一构建并关闭新功能）、同一模型、`-c`、batch、K/V 类型、采样、轨迹和总主机内存预算。

| 组 | 配置 | 作用 |
|---|---|---|
| A | `--no-cache-prompt --cache-ram 0 --ctx-checkpoints 0` | 下界；只作机制参照 |
| N | **调优后的原生配置**。在独立的调优轨迹（不同随机种子）上网格搜索：`-np` ∈ {1,2,4}（按显存可行性裁剪）、`-sps` ∈ {0.1, 0.5, 0.95}、`--cache-ram` = B1、`--ctx-checkpoints` ∈ {4,8}、`--checkpoint-min-step` ∈ {2048, 8192}，按 p95 TTFT 选最优。**先冻结配置，再跑正式轨迹** | 工程方案必须面对的基线 |
| R | 自定义调度器，只开 RAM，预算 B1（记账含检查点和 staging），字节 LRU，不预取 | 与 S 只差 SSD 一项 |
| S | 与 R 完全相同，另开 SSD（64 GiB）；准入先用“RAM 淘汰即写入”，第二轮改用 p\* 准入 | S−R 隔离 SSD 的贡献；S−N 衡量整个方案 |
| I（可选） | R 的 RAM 预算设为无限（例如 48 GiB），用于估计容量收益上限 | 衡量 S 离“理想大内存”还差多少 |

## 11. 指标与预先登记的通过/失败门槛

### 11.1 指标

- **延迟**：客户端 TTFT，定义沿用 `pi-cache-bench/README.md`（从请求发出到首个非空内容增量）；报告 p50、p95，按会话聚类的 bootstrap 95% 置信区间。
- **吞吐**：整批墙钟时间；SLO 内完成的请求数/秒（SLO 例如 p95 TTFT ≤ 2 s）。
- **工作量**：每请求实际 prefill tokens（`timings.prompt_n`）与 `prompt_ms`；恢复位置 k、LCP 与 `LCP − k`（边界损失）。
- **命中**：按层统计的 L0、L1、L2 命中与 miss；miss 原因分为容量、边界、不兼容、首次访问。
- **I/O**：应用层 L2 读写字节，另用 Windows PhysicalDisk 计数器核对设备读字节，以区分设备读与页缓存。**写放大 WA = L2 写入字节 / L2 读回字节**，同时报告从未被读回的 L2 对象占比。
- **资源**：进程私有提交与 RSS 峰值、系统可用内存、整卡与本进程显存；引擎线程同步停顿（每次导出和安装的毫秒数）。
- **干扰**：并发 decode 请求的 ITL（token 间隔）p95。

### 11.2 门槛（运行前冻结，失败不以速度抵消）

| 编号 | 条件 | 通过标准 |
|---|---|---|
| G0 正确性 | 全部组别，含所有 L1/L2 命中请求 | token 续算探针：logits 差 ≤ 冷算重复的噪声（bench 实测为 0.0），128 个 greedy token 完全一致；server 路径：对每个 L2 命中请求按相同 token 冷算，前 32 个 greedy token 一致，且 top-10 logprob 差 ≤ 1e-3。**任何一例失败，整体判失败**。损坏、截断、版本不符的对象必须 100% 回落到重算 |
| G1 机制 | W/B1 ≥ 1.5 | S 的 L2 命中数 > 0 且全部来自自然淘汰；S 的实际 prefill tokens 比 R 少 ≥ 30% |
| G2 模型 | 所有 L2 命中 | 实测单次节省与 §2.2 预测之比落在 [0.7, 1.3] |
| G3 主收益（相对 R） | W/B1 = 2 与 4，主场景 | p95 TTFT 降低 ≥ 25%，且整批墙钟降低 ≥ 10%，两者的 95% 置信区间都不跨 0，并超过 A/A 噪声的 2 倍 |
| G4 主收益（相对 N） | 同上 | p95 TTFT 降低 ≥ 20%，或 SLO 内吞吐提高 ≥ 10% |
| G5 无害 | C1、C2、C3 | S 相对 R 与 N：p50 和 p95 TTFT 退化 ≤ 5%，墙钟退化 ≤ 3%，并发 decode 的 ITL p95 退化 ≤ 5% |
| G6 资源 | 所有运行 | 主机私有提交峰值 ≤ 预算 × 1.1；在 p\* 准入下 WA ≤ 1/p\*（4K 约 9，16K 约 20），否则说明准入失效 |

**判读规则**：G0 失败则方案不可用。G1、G2 通过但 G3 在 W/B1 = 2 和 4 下都失败，结论为“**L2 在本机不值得**”。G3 通过但 G4 失败，结论为“**先调原生**”。

## 12. 正确性与噪声控制

- **正确性**分三层：
  1. 在 `prefix-state-bench` 中按 token 续算做全词表 logits 比对；
  2. 在 server 路径上，对每个 L2 命中做冷算对照；
  3. 定向测试 hybrid 风险：
     - 恢复后发送在边界之前分叉的请求（验证能回落到正确的检查点或重算）；
     - 恢复后立刻发送完全相同的 prompt（`TAG_PROMPT_LOGITS` 路径）；
     - 先恢复会话 X，再发送会话 Y（检查是否残留过期检查点）；
     - 构造同一 64 位键但 tokens 不同的对象（键冲突）；
     - 文件损坏或截断、并发读与淘汰、取消请求、磁盘写满。
- **GPU 非独占**：每次运行前后用 `nvidia-smi --query-compute-apps` 与利用率采样记录其他进程。其他进程占用 > 10% 或显存变化 > 500 MiB 的运行标为无效并重跑，但保留日志。不修改时钟或系统设置。
- **A/A 噪声基线**：每个场景把同一组跑两遍，得到噪声分布；门槛要超过 A/A 差异的 2 倍。
- **预热与冷启动**：模型加载不计时；每次启动先发 1 个不计入的预热请求，其前缀不属于评测集。同时报告“从空缓存开始”的完整回放和稳定期两段。
- **页缓存**：L2 默认使用 `FILE_FLAG_NO_BUFFERING`；每次运行新建 L2 目录。另设一组普通缓冲读，结果单列为“文件缓存收益”。用 PhysicalDisk 读字节核对设备确实被读取。
- **顺序效应**：组别按 ABBA 或拉丁方交错；每个格子至少重复 3 次（MVP）或 5 次（完整版），其中一半逆序执行。一次完整回放算一个样本，同一会话内的请求不当作独立样本。
- **生成差异**：固定 `ignore_eos` 和 `n_predict`，温度 0，关闭 reasoning；回放不把新生成的回答写回历史（与现有回放一致）。

## 13. 落地

### 13.1 MVP（不改 server，约半天 GPU 时间）

1. **离线预测**：新增一个轻量模拟器（Python）。输入 trace 与每对象字节，模拟 R 和 S 的字节 LRU，输出预测命中数和按 §2.2 预测的节省时间，写入预注册文件。它先回答“哪些 W/B1 值得跑”。
2. **扩展 `research/prefix-state-bench`**：新增 trace 模式。单进程加载模型；M 个首 token 起就不同的真实语料前缀；实现 RAM 字节 LRU（B1 = 4 GiB，真实分配）与 SSD 目录（无缓冲读）；按循环或 Zipf 顺序访问，每次访问执行“查找 → 恢复或重算 → 128-token 后缀 → 按策略保存”。策略分为无缓存、RAM-only、RAM+SSD、无限 RAM。
   - 前缀取 8K，W/B1 ∈ {0.5, 1, 2, 4}（M = 7、14、28、56），每个格子访问 5 轮，重复 3 次，ABBA 顺序。
   - 指标用引擎首 token 时间（明确不叫客户端 TTFT）、命中与字节计数、设备读字节。
   - 覆盖 H1–H3 与 G0–G2 的机制部分。
3. **复用的脚本**：`prefix-state-bench/main.cpp`、`run.py`、`summarize.py`、`monitor.py`。**需要新增**：trace 生成器、LRU 模拟器、在 `monitor.py` 中增加 PhysicalDisk 计数采样。

### 13.2 完整版（需要先完成 server 集成）

1. **前置实现**：把原型改成请求路径上自动查找合法边界；以 `server_prompt_cache` 为唯一 L1（修正 E10 的五个问题）；增加 SSD 后端（后台写入、原子发布、校验、失败回落）；提供按层命中、恢复位置 k、I/O 字节等观测字段。
2. **负载**：按 §9 录制 16–32 个 Pi 会话，由编排器生成 W/B1 ∈ {0.5, 1, 1.5, 2, 4} 的轨迹，另加 C1–C7。
3. **组别**：A、N（先冻结调优结果）、R、S、I；B1 = 4 GiB 全量跑，B1 = 16 GiB 只复核 W/B1 = 2。
4. **脚本**：
   - 复用：`pi-cache-bench/bench.py`（`live`、`replay`）、`analyze.py`、`report.py`、`matrix.py`；
   - 扩展：`matrix.py` 支持 ABBA 顺序与新组别，`analyze.py` 增加按层命中与 WA 统计；
   - 新增：会话编排器（交错与回访距离控制）、server 正确性探针（冷算对照与定向故障注入）、预注册门槛的判定脚本；
   - 废弃或重写：`run_tier_cache_eval.py`，它只覆盖手动 `/tier` 接口，且没有结果。
5. **时间估计 [推断]**：每次回放 5–15 分钟；5 组 × 5 个 W/B1 × 5 次重复 ≈ 125 次，约 10–30 小时 GPU 时间，需要分多天在 GPU 空闲时段运行。

---

## 参考来源

### 本地源码

- `llama.cpp/`（f5e85d43a）：`tools/server/server-context.cpp`、`tools/server/server-task.{h,cpp}`、`include/llama.h`、`src/llama-context.cpp`、`src/llama-memory-recurrent.cpp`、`src/llama-memory-hybrid.cpp`、`src/llama-kv-cache.cpp`、`common/common.{h,cpp}`、`common/arg.cpp`、`tools/server/README.md`；行号见正文。
- b9209（`git show 0caf2a1d4:...`）：`tools/server/server-context.cpp`（1028-1038、1147-1156、2055-2087、2586-2588、2689、2865-2876）、`tools/server/server-task.cpp`（2130、2148）。
- `try-out/llama.cpp/`（`56b9eb280` 加未提交改动）：`tools/server/server-tier-store.{h,cpp}`、`tools/server/server-context.cpp`（344-385、1414-1420、2719-2790、4936+）。
- `LMCache/`（a0e4a4c2）：`lmcache/v1/gpu_connector/gpu_connectors.py`、`lmcache/v1/token_database.py`、`lmcache/v1/memory_management.py`、`lmcache/v1/distributed/api.py`、`lmcache/v1/distributed/l2_adapters/base.py`、`lmcache/integration/vllm/kv_cache_groups.py`、`lmcache/integration/vllm/lmcache_mp_connector.py`、`docs/source/mp/hybrid_models.rst`。

### 本地实测与文档

- `research/prefix-state-bench/runs/20260913-122835-full/{report.md,summary.json,results.jsonl,config.json}`
- `research/pi-cache-bench/results/{report.md,slot-calibration.json}`；`research/pi-cache-bench/runs/20260914-093413-replay-slot-c2-r1-slots2/requests.jsonl`；`research/pi-cache-bench/runs/20260914-091733-replay-ram-c2-r1/{requests.jsonl,server.log}`；`research/pi-cache-bench/runs/20260914-091319-replay-no_cache-c2-r1/requests.jsonl`
- `research/llamacpp-cache-logs/cache_ram_slot_save.log`；`research/llamacpp-realistic-cache-logs/cache_ram_4096.log`
- `research/llamacpp-cache-benchmark-results.md`、`research/llamacpp_realistic_cache_smoke_summary.md`、`research/llamacpp-tiered-cache-hardware.json`
- 被审查文档：`research/llamacpp-tiered-cache-evaluation-and-implementation.md`、`research/llamacpp-tiered-cache-design.md`、`research/llamacpp-tiered-cache-source-audit.md`、`research/lmcache-llamacpp-kv-cache.md`

### 网页（一手）

- vLLM Automatic Prefix Caching：https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html
- vLLM KV Offloading Usage Guide：https://docs.vllm.ai/en/latest/features/kv_offloading_usage/
- vLLM Disaggregated Prefill / KV connectors：https://docs.vllm.ai/en/latest/features/disagg_prefill.html
- vLLM 博客，KV Offloading Connector：https://blog.vllm.ai/2026/01/08/kv-offloading-connector.html
- SGLang（RadixAttention）论文：https://arxiv.org/abs/2312.07104
- SGLang HiCache 设计：https://docs.sglang.io/advanced_features/hicache_design.html
- SGLang hybrid 模型（MambaRadixCache）：https://pytorch.org/blog/hybrid-models-meet-sglang-more-than-full-attention/
- SGLang issue #39830（hybrid 宿主层命中错误）：https://github.com/sgl-project/sglang/issues/39830
- LMCache 论文：https://arxiv.org/abs/2510.09665
- LMCache hybrid 文档（在线版）：https://docs.lmcache.ai/mp/hybrid_models.html
- Mooncake：https://arxiv.org/abs/2407.00079 ；FAST'25：https://www.usenix.org/conference/fast25/presentation/qin
- CachedAttention（ATC'24）：https://arxiv.org/abs/2403.19708
- Tail-Replay：https://arxiv.org/abs/2608.30310
- llama.cpp PR #16391（host 内存 prompt cache）：https://github.com/ggml-org/llama.cpp/pull/16391
- llama.cpp PR #15293（SWA 检查点与 `_ext` API）：https://github.com/ggml-org/llama.cpp/pull/15293
- llama.cpp PR #28092（`--cache-disk`，未合并）：https://github.com/ggml-org/llama.cpp/pull/28092
- llama.cpp PR #24028（slot 检查点 sidecar，未合并）：https://github.com/ggml-org/llama.cpp/pull/24028
- llama.cpp issue #20697（磁盘检查点卸载请求）：https://github.com/ggml-org/llama.cpp/issues/20697
