---
type: Reference
title: 集成形态与上游最小缺口
description: 三种集成形态、llama.cpp 缺哪几个原语
summary: 三种集成形态、llama.cpp 缺哪几个原语
tags:
- llm
- kv-cache
- llama.cpp
- open-source
sources:
- session: 2026-11-18 KV Cache 生态研究与文档重构
- C:/Users/Administrator/Documents/Code/my-code/lm-llama/research/kv-cache-ecosystem/06-integration-and-gaps.md
createdAt: '2026-11-18'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 集成形态与上游最小缺口

> 做开源贡献的落点：llama.cpp 缺哪几个原语，以及哪些改动上游不会要。

## 速览

```text
  集成形态
    KVMem    打补丁进引擎（50 个文件，最侵入）
    Mooncake in-process 插件（KVConnector）
    LMCache  引擎适配器 / 独立服务（classic / MP）

  上游最小缺口（按对外部缓存的必要性排序）
    1 按逻辑行区间导出/导入 KV   <- 最高价值（内部已按 cell range 写）
    2 逻辑行游标 logical_pos
    3 按逻辑行删除 cell
    4 KV 布局元数据
    5 recurrent 状态句柄（已有，不新增）
```

## 1. 与推理引擎的集成方式

这是三者差异最大、也最影响可维护性的一维。

**KVMem = 打补丁进引擎**（最侵入）
`kvmem/backends/patches/llamacpp-kvmem.patch`（125 KB）触及 **50 个 llama.cpp 文件**（按 patch 内 `diff --git` 计数），包括 `src/llama-kv-cache.{h,cpp}`、`src/llama-graph.{h,cpp}`、`src/llama-context.{h,cpp}`、`src/llama-memory-{recurrent,hybrid}.{h,cpp}`、`src/models/qwen3.cpp`、`src/models/qwen35.cpp`、以及 ggml 层的 `ggml-cuda/gated_delta_net.cu`、`getrows.cu`、`norm.cu`、`ggml-backend.cpp` 等。

llama.cpp 侧只看到一个薄 hook（补丁新增 `src/llama-kvmem-factory.h`）：

```cpp
// Thin hook used by llama_model::create_memory when LLAMA_KVMEM is enabled.
// Implementation lives out-of-tree in src/adapter/.
llama_memory_i * llama_memory_kvmem_maybe_create(const llama_model &, const llama_memory_params &, const llama_cparams &);
```

但「接口薄 ≠ 补丁薄」。**llama.cpp 需要暴露 4 样东西**：

1. 独立于 M-RoPE 的逻辑行游标：`llama_ubatch::logical_pos` + `llama_batch_ext_set_logical_pos()`；
2. 按逻辑行删除 cache cell：`llama_kv_cache::seq_rm_logical(seq_id, p0, p1)`；
3. KV storage 张量的直接访问句柄（`get_k_storage` / 新增 `get_v_storage`）；
   > **本地接口边界**：`get_k_storage(int32_t il)` 存在，`get_v_storage`、`seq_rm_logical`、`logical_pos` 未在当前 try-out 树找到。这是直接操作原生块/张量的接口缺口，**不是完整 state 保存的缺口**：已有 `llama_state_seq_get_data/set_data` 和 `save_file/load_file`（`try-out/llama.cpp/include/llama.h:874`）可经引擎内部序列化数值状态。是否增加 V getter，取决于选择原生块搬运还是不透明 state blob 路线，不能写成所有分层方案的先决条件。
4. 注意力图构建处的捕获钩子（改 `llama-graph.cpp`）。

**Mooncake = in-process 插件**（引擎提供 KVConnector 抽象，Mooncake 实现）
vLLM 侧 `MooncakeConnector` 实现 `KVConnectorBase_V1`，按角色拆成 `MooncakeConnectorScheduler` 与 `MooncakeConnectorWorker`（`mooncake-wheel/mooncake/mooncake_connector_v1.py:121-394`）。PD 场景的元数据走 ZMQ side channel。

**LMCache = 引擎适配器 / 独立服务**
classic 是引擎内进程库（vLLM / SGLang / TensorRT-LLM / ATOM 四个适配器）；MP 是独立守护进程（`docs/source/mp/index.rst:44-58` 把 `lmcache server` 标为 **Recommended**，`python3 -m lmcache.v1.multiprocess.server` 标为 Legacy）。MP 模式下引擎侧拆成两个角色：

| | `LMCacheMPSchedulerAdapter`（`integration/vllm/vllm_multi_process_adapter.py:591`） | `LMCacheMPWorkerAdapter`（`:1100`） |
|---|---|---|
| 运行位置 | vLLM **scheduler 进程** | vLLM **TP worker 进程** |
| 职责 | token 级查找调度、块表/锁管理 | GPU 指针注册、实际字节搬运 |

**为什么必须拆**：scheduler 进程没有 GPU KV buffer，只能做 token→key 的查找与元数据管理；worker 进程持有 KV tensor 的 device 指针，负责搬运。

> **对 llama.cpp 最关键的事实（本次核实）**：**LMCache 没有任何 llama.cpp 集成**。全仓库检索 `llama.cpp|llamacpp|llama_cpp|gguf`，唯一命中是 `LMCache/examples/online_session/README.md:4` 的一句举例说明——那里是把 llama.cpp 当作「说 OpenAI `/v1` API 的 server」做 TTFT 基准，**不是集成**。（`docs/source/recipes/llama.rst` 是 Llama 模型家族的 recipe，与 llama.cpp 无关；`git log -S'llama.cpp'` 只有两条提交，都与那个 example 有关。）它也没有 `lmcache/integration/llama*` 目录。

## 2. Strata 的「权威副本 + 窗口 + 驻留映射」三层模型

设计边界写在头注释里（`strata/include/strata/kernels/kv_stream.hpp:1-20`）：权威 K/V 在 **pinned、device-mapped 的主机内存**，布局与全驻留池完全一致；VRAM 只放 `n_slots` 个页；page table 退化成 **residency map**（`page_table[block]` = 槽位或 -1）。

最关键的是**写者不变式**（`strata/src/prefill/kernels.cu:2545-2573`）：append **总是**写权威副本，**只在该块常驻时**才写 VRAM 槽。于是槽位永不变陈旧，「被拒绝的草稿」「会话恢复」都不需要失效逻辑。淘汰用 **CLOCK 二次机会**（`kv_stream.cu:116-154`），一次 resolve 解决全部 miss。

**但这套模型有一个与你的目标相反的前提**：host pool 是按**完整上下文**分配的（`strata/src/core/layer.cpp:919-933`，`pages` 来自 `max_cells`）。**RAM 是终点，不是窗口。** 所以 Strata 天生只有两级（VRAM + RAM），拿不到 L2；要加 L2 得允许 host pool 自身溢出到文件，那是新写一整套（页索引 + 部分读 + 槽填充 + 失效协议 + CUDA graph 地址一致性），不是移植。

还有两处前提在 llama.cpp 不成立：**页大小**（Strata 4 cell ≈ 4,224 B，llama.cpp 的页大几个数量级）；**窗口下限**（Strata 4096 cells 够用是因为 QSA 稀疏选择一次只读 `idx_top_k + idx_block - 1` 个 cell，llama.cpp 是稠密注意力，窗口化会直接改变数值结果）。

## 3. llama.cpp 的上游缺口：被两个独立方向确认

KVMem 和 LMCache 两条路径各自独立地得出同一个结论：

- **KVMem 侧**：125 KB 补丁触及 50 个文件，但**只有 2 处进了 public `llama.h`**——`llama_batch` 新增 `logical_pos` 字段（注意：这改的是 public struct 布局，**破坏 C ABI**）与 `llama_batch_ext_set_logical_pos()`。其余全在 `src/` 内部头：`get_v_storage`、`seq_rm_logical`、`llama-kvmem-factory.h` 等。上游完全没有 KV 张量句柄、cell 枚举、区间导出、逻辑行寻址。
- **LMCache 侧**：blob 路线的**头号阻塞点**是「公开 state API 只接受 `seq_id`，不接受位置区间」——而 `llama_memory_i::state_write` **内部本来就是按 cell range 写的**（`llama.cpp/src/llama-kv-cache.cpp:2392-2422`）。

**即：上游有按区间写状态的内部机制，只是没对外暴露。** 这是最有价值的贡献切口，也是本轮最实在的结论。

**KVMem 里「非侵入不可」的 5 项语义改动**（说明哪些需求上游会视为 bug 来源，不宜直接上游化）：`llama_kv_cell_ext` 增 `logical_pos`；**非 SWA 缓存放弃连续性不变量**（上游明确注释过这个不变量的理由）；注意力 mask 的 copy-and-patch 快捷路径需加「有洞检测」；CUDA graph 槽从 2 张扩到 9 张并需新增 `ggml_backend_sched_restore_graph_srcs()`；GDN 的 `K==0` 语义（把「必须写 state」放宽成「可以不写」）。

## 4. 注意力质量无法非侵入获得，但 Mean-K 可以退化

- **页级 attention mass 做不到零侵入**：FA 内核不物化注意力概率矩阵，Q 也不在外部缓存里；用 `cb_eval` 观察图节点也不可行（scheduler 会 split 并在每次询问时同步）。KVMem 现在的做法（把 post-RoPE Q/K/mask 挂成图输出、在独立 backend 上重算注意力、只对首/中/末 3 层采样）是当前 FA 架构下唯一能拿到页级质量分布的办法。
- **Mean-K 这条线可以退化**：导出的 packed K 已经是 **post-RoPE + 已量化** 的，用它的均值做块级打分是可接受的近似；精确复现 pre-RoPE F32 Mean-K（LRFU 的打分信号）则不成立。**这是最有希望的非侵入化收益点**：把整套 pre-RoPE 捕获删掉，改为 stage-out 时顺手对已读出的 packed K 做一次归约。

## 5. 收敛出的最小上游 API 集合

按「对外部 KV 缓存的必要性」排序，供后续 PR 拆分：

| # | 能力 | 形态 | 备注 |
|---|---|---|---|
| 1 | 按**逻辑行区间**导出/导入 KV | `llama_memory_seq_get_data_range(mem, seq_id, p0, p1, dst)` 一类的 public 函数 | `state_write` 内部已按 cell range 写；这是最高价值的一项 |
| 2 | 逻辑行游标 | `llama_batch.logical_pos` + `llama_batch_ext_set_logical_pos()` | KVMem 补丁里已有，可独立上游；但字段进 public struct 会破坏 ABI，可能需改为扩展函数或 ext 结构体 |
| 3 | 按逻辑行删除 cell | public 版 `seq_rm_logical` | M-RoPE 下按模型位置删会误删邻居 |
| 4 | KV 布局元数据 | 层数、每层 K/V 类型与行字节、head 数、page 粒度 | 让外部缓存不必解析 `state_write` 的非稳定二进制布局 |
| 5 | recurrent 状态句柄 | **已有**（`llama_memory_hybrid::state_write` 一并写 attn 与 recurrent） | 不必新增 |

**注意力质量统计（§5 那条线）建议整体推迟**——它是「检索质量」问题，不是「外部缓存」问题；先做块粒度搬运 + LRU，收益链条短得多。
