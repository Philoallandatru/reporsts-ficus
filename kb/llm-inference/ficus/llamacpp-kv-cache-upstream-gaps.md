---
type: Reference
title: llama.cpp 的 KV 缓存上游最小缺口
description: 外部 KV 缓存要落地，llama.cpp 缺哪几个原语，以及哪些改动上游不会要。
summary: 上游内部已按 cell range 写状态，只是没对外暴露按区间导出导入，这是最有价值的贡献切口
tags:
- llm
- kv-cache
- llama.cpp
- open-source
sources:
- session: 2026-11-18 KV Cache 生态研究与文档重构
- C:/Users/Administrator/Documents/Code/my-code/lm-llama/research/kv-cache-ecosystem/06-integration-and-gaps.md
- C:/Users/Administrator/Documents/Code/my-code/lm-llama/research/kv-cache-ecosystem/07-llamacpp-implications.md
createdAt: '2026-11-18'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# llama.cpp 的 KV 缓存上游最小缺口

**llama.cpp 内部本来就按 cell range 写状态，只是没有对外暴露「按逻辑行区间导出/导入」——这是外部 KV 缓存落地时最有价值、也最可能被上游接受的贡献切口。**

## 背景 / 为什么

想在 llama.cpp 上做 L0 显存 → L1 RAM → L2 SSD 的分层缓存，第一步往往是照着别人的实现改引擎。问题是：哪些改动上游会当 bug 修掉，哪些是真缺口值得提 PR。

这份结论的价值在于**缺口清单不是猜的**，而是被两个互相独立的项目方向同时确认过——KVMem 和 LMCache 分别从不同角度得出了同一个结论。

## 核心内容

### 缺口被两个独立方向确认

- **KVMem 侧**：它的 llama.cpp 补丁触及 50 个文件、约 2,768 行，但**只有 2 处进了 public `llama.h`**——`llama_batch` 新增 `logical_pos` 字段（这改的是 public struct 布局，**破坏 C ABI**）与 `llama_batch_ext_set_logical_pos()`。其余全在 `src/` 内部头：`get_v_storage`、`seq_rm_logical`、`llama-kvmem-factory.h` 等。上游完全没有 KV 张量句柄、cell 枚举、区间导出、逻辑行寻址。
- **LMCache 侧**：blob 路线的头号阻塞点是「公开 state API 只接受 `seq_id`，不接受位置区间」——而 `llama_memory_i::state_write` **内部本来就是按 cell range 写的**（`llama.cpp/src/llama-kv-cache.cpp:2392-2422`）。

即：**上游有按区间写状态的内部机制，只是没对外暴露。**

### 收敛出的最小 API 集合

按「对外部 KV 缓存的必要性」排序，供后续 PR 拆分：

| # | 能力 | 形态 | 备注 |
|---|---|---|---|
| 1 | 按**逻辑行区间**导出/导入 KV | `llama_memory_seq_get_data_range(mem, seq_id, p0, p1, dst)` 一类的 public 函数 | `state_write` 内部已按 cell range 写；最高价值的一项 |
| 2 | 逻辑行游标 | `llama_batch.logical_pos` + `llama_batch_ext_set_logical_pos()` | KVMem 补丁里已有；字段进 public struct 会破坏 ABI，可能需改为扩展函数或 ext 结构体 |
| 3 | 按逻辑行删除 cell | public 版 `seq_rm_logical` | M-RoPE 下按模型位置删会误删邻居 |
| 4 | KV 布局元数据 | 层数、每层 K/V 类型与行字节、head 数、page 粒度 | 让外部缓存不必解析 `state_write` 的非稳定二进制布局 |
| 5 | recurrent 状态句柄 | **已有**（`llama_memory_hybrid::state_write` 一并写 attn 与 recurrent） | 不必新增 |

第 5 条值得注意：**混合模型的 recurrent 状态不需要新增接口**，`state_write` 已经一并处理。这让「opaque state blob」路线在 hybrid 模型上天然可行。

### 哪些改动上游不会要

KVMem 里被标注为「非侵入不可」的 5 项语义改动，说明了哪些需求上游会视为 bug 来源，不宜直接上游化：

1. `llama_kv_cell_ext` 增 `logical_pos`；
2. **非 SWA 缓存放弃连续性不变量**（上游明确注释过这个不变量的理由）；
3. 注意力 mask 的 copy-and-patch 快捷路径需加「有洞检测」；
4. CUDA graph 槽从 2 张扩到 9 张并需新增 `ggml_backend_sched_restore_graph_srcs()`；
5. GDN 的 `K==0` 语义（把「必须写 state」放宽成「可以不写」）。

### 注意力质量：无法非侵入获得，但 Mean-K 可以退化

- **页级 attention mass 做不到零侵入**：FA 内核不物化注意力概率矩阵，Q 也不在外部缓存里；用 `cb_eval` 观察图节点不可行（scheduler 会 split 并在每次询问时同步）。KVMem 现在的做法（把 post-RoPE Q/K/mask 挂成图输出、在独立 backend 上重算注意力、只对首/中/末 3 层采样）是当前 FA 架构下唯一能拿到页级质量分布的办法。
- **Mean-K 这条线可以退化**：导出的 packed K 已经是 post-RoPE + 已量化的，用它的均值做块级打分是可接受的近似；精确复现 pre-RoPE F32 Mean-K 则不成立。**这是最有希望的非侵入化收益点**——把整套 pre-RoPE 捕获删掉，改为 stage-out 时顺手对已读出的 packed K 做一次归约。

```text
外部 KV 缓存落地路径（宿主：llama.cpp）

  引擎侧需要暴露的原语
  +----------------------------------------------------+
  | | ① 按逻辑行区间导出/导入 KV   ← 最高价值        | |
  | | ② 逻辑行游标 logical_pos                       | |
  | | ③ 按逻辑行删除 cell                            | |
  | | ④ KV 布局元数据                                | |
  | | ⑤ recurrent 状态句柄            ← 已有，不新增 | |
  +----------------------------------------------------+
                     |
                     v
  上层可选两条路线
+-----------------------+   +------------------------+
| A. 原生块搬运         |   | B. 不透明 state blob   |
| 需要 V getter +       |   | 只用 llama_state_seq_* |
| 张量句柄 + 布局元数据 |   | _ext，天然含 recurrent |
| → 更底层、更通用      |   | → 改动面小、适合先做   |
+-----------------------+   +------------------------+

  注意：路线 B 成立，所以「必须先补 V getter」是错的
```

### 三种集成形态

- **KVMem = 打补丁进引擎**（最侵入）：50 个文件，包括 `llama-kv-cache`、`llama-graph`、`llama-context`、`llama-memory-{recurrent,hybrid}`、模型实现、ggml 层 CUDA 内核。llama.cpp 侧只留一个薄 hook（`llama_memory_kvmem_maybe_create`），但**接口薄 ≠ 补丁薄**。
- **Mooncake = in-process 插件**：vLLM 侧 `MooncakeConnector` 实现 `KVConnectorBase_V1`，按角色拆成 Scheduler 与 Worker 两半，PD 场景元数据走 ZMQ side channel。
- **LMCache = 引擎适配器 / 独立服务**：classic 是引擎内进程库；MP 是独立守护进程，引擎侧拆成 scheduler 侧（token 级查找调度、块表/锁管理）和 worker 侧（GPU 指针注册、实际字节搬运）。**必须拆**是因为 scheduler 进程没有 GPU KV buffer。

## 关键要点

- 最高价值的上游贡献是暴露「按逻辑行区间导出/导入 KV」，因为内部机制已存在，工作量主要是接口设计与测试。
- 逻辑行游标进 public struct 会破坏 C ABI，改成扩展函数或 ext 结构体更可能被接受。
- 混合模型的 recurrent 状态已有接口支持，**不要为此新增 API**。
- opaque state blob 路线（只用 `llama_state_seq_*_ext`）在 hybrid 模型上天然可行，是最小改动路径；不必为了「块级共享」重写整套原型。
- 但 blob 路线无法共享公共前缀，两个会话共享长前缀会存两份——落 L2 前仍需按序解决粒度、键身份、索引持久化三件事。
- 注意力质量统计（页级 attention mass）建议整体推迟：它是「检索质量」问题，不是「外部缓存」问题；先做块粒度搬运 + LRU，收益链条短得多。
- 页面级 attention mass 与「零侵入」在 FA 架构下互斥，不要把质量评估混进第一个 PR。

## 相关

- [[kv-cache-tiering-principles]] — 分层的五条原理与恢复条件
- [[kv-cache-ecosystem-framework-comparison]] — 四家框架的层次分工与集成形态
- [[kv-cache-vllm-sglang-learning]] — KV Cache 复用与 TTFT 指标基础
