---
type: Concept
title: Strata 与 llama.cpp 多场景实测、Nsight Profiling 与模块学习路线
description: 基于 RTX 5080 的 Strata 与 llama.cpp 全链路数据流对比、Nsight Systems 显微级 CUDA API/Kernel
  差异分析，以及各项目源码测试与学习路线。
tags:
- llm
- inference
- strata
- llamacpp
- profiling
- nsight
sources:
- C:/Users/Administrator/Documents/Code/tasks/strata-lab/strata-profiling-20261109/report.md
- C:/Users/Administrator/Documents/Code/tasks/strata-lab/strata-profiling-20261109/source-paths.md
- C:/Users/Administrator/Documents/Code/my-code/lm-llama/research/strata-vs-llamacpp-source-analysis-20261112.zh-CN.md
createdAt: '2026-11-22'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# Strata 与 llama.cpp 多场景实测、Nsight Profiling 与模块学习路线

## 一、 全链路数据流动与多场景实测（RTX 5080 · Qwen3.8-Flash-Next IQ2_XS）

在 `NVIDIA GeForce RTX 5080 (16 GiB)` 上使用 `Qwen3.8-Flash-Next-GSQ-RCO-IQ2_XS`（176.94B 总参数 / A3B 激活）实测三类场景：

| 场景 | llama.cpp (`mmap` + 6.7G MoE Cache + MTP) | Strata (RAM Arena 或 14G 有界内存 + MTP) | 核心差异原因 |
|---|---|---|---|
| **r1 短对话** (44~50 in → 768 out) | 31.98 / 33.43 tok/s (TTFT 2.89s/1.50s) | **105.61 / 107.02 tok/s** (`RAM Arena`, TTFT 0.55s) | Strata 34.5G 连续 RAM Arena + 6193 热槽（85%~87% 命中）+ 15 核并行算 miss，GPU 利用率 97.8%；llama 每层同步搬运累计 238.1 GiB H2D，GPU 37.2%。 |
| **r2 台账分析** (14G 有界内存) | 短 36.16 / 长 9.86 tok/s | 短 **36.58** / 长 **16.69 tok/s** (`14G Budget + SSD`) | 当 RAM 收紧到 14G 时，Strata Decode 受限于 SSD 随机读，短请求回落至与 llama 持平；长输入 Prefill 仍靠 Stager 流水线快 69%。 |
| **long-28k 超长输入** (9,801 in → 128 out) | 1.20 tok/s (TTFT **100.74s**) | **6.34 tok/s** (`14G Budget`, TTFT **17.10s**) | llama 在大微批（`ubatch > 8`）下 MoE 缓存命中率跌至 11.4% 并反复同步搬运；Strata 按层分组走 fused INT8 路径，快 **5.28×**。 |

### 数据流动对比（Disk → Page Cache / RAM → PCIe → VRAM）
1. **`llama.cpp`（`mmap` 惰性缺页）**：启动仅读 2.67 GiB 常驻权重（RSS 7.30 GiB），其余专家与 26.82 GiB PLE 建虚拟映射。推理时随缺页中断把 RSS 从 `7.30 → 38.47 GiB` 逐步拉入内存；Decode 期 19.86% 未命中专家经 PCIe 同步 H2D 上传（5 条请求累计 238.1 GiB）。
2. **`Strata`（连续 RAM Arena + Profile 预填热槽）**：启动时打包 24,576 个专家入 34.51 GiB 连续 Arena（或按有界预算从 SSD 分层读取），按 `expert-profile.bin` 静态锁定 6,193 个显存热槽（8.30 GiB），仅 2.6%~4.4% 路由专家走 PCIe，其余由 15 个 CPU Pool Worker 并行计算。

---

## 二、 Nsight Systems 显微级 Profiling 差异（2026-11-09 历史抓包分析）

1. **Prefill（1,560-token 英文，无 MTP）**：总墙钟 `4.840s`（llama.cpp）vs `1.249s`（Strata）。计算 Kernel 并集仅差 82ms（`0.655s` vs `0.573s`），差距主要来自 **H2D/D2D 搬运与同步空等**（llama H2D `46.73 GiB / 81,775 次`，未重叠同步等待 `1.360s`；Strata H2D `26.85 GiB / 19,978 次`，未重叠同步仅 `0.006s`）。
2. **Decode（256-token 中文，无 MTP）**：总墙钟 `4.955s` vs `2.961s`。
   - **`llama.cpp`（Host 驱动逐层同步）**：每层算完路由后 D2H 传回 40 B 专家 ID（`12,214` 次），调用 **`cudaStreamSynchronize`（`36,377` 次 / `2.745s`）**、`cudaGraphLaunch`（`12,351` 次）、`cudaMemcpyAsync`（`63,172` 次），导致 GPU 无活动空窗高达 **`2.047s`（41.3%）**，SMs Active 均值 `37.8%`。
   - **`Strata`（Device 大图 + 映射内存 Doorbell）**：将循环打包进少数大 CUDA Graph（仅 **`250` 次启动**），用零拷贝映射内存 + GPU 端 **`wait_flag_ge_kernel`（421.3ms）** 轮询与 **`fetch_blobs_kernel`** 替代主机同步和显式拷贝，`cudaStreamSynchronize` 降至 **`688` 次（`0.142s`）**，ETW 测得 CPU 进程并发 **`15.39` 核当量**，SMs Active 达 `57.0%`。
3. **开启 MTP 后的变化与插桩扰动**：
   - MTP 将验证窗口变为 `batch=4`，两引擎 Kernel 节点数均减半；但 `llama.cpp` 因 4 token 同时激活更多不同专家，H2D 暴涨至 `25.17 GiB（+67%）`，且变长接受窗口触发 **`399` 次 `cudaGraphInstantiate`（325.5ms）**，SMs Active 跌至 `21.4%`。
   - 节点级 Nsight 插桩对 Strata 大图注入额外开销（无插桩 `107.5` → 节点级 `79.7 tok/s`），使面板上的相对差距显得比真实跑分略小。

---

## 三、 各项目源码测试集重点与模块学习路线

### 各项目 `tests/` 测试重点
- **`llama.cpp/tests`**：`test-expert-store.cpp`（文件/RAM 专家缓存与异步释放安全）、`test-backend-ops.cpp`、`test-alloc.cpp`、`test-llama-context.cpp`、`test-speculative-rejection-sampling.cpp`。
- **`strata/tests`**：`core/`（`expert_cache_segmented_test.cpp`、`file_expert_source_test.cpp`、`vmm_test.cpp`、`memory_guard_test.cpp`）、`cuda/`（`prefill_fused_moe_test.cpp`、`hc_q8_stream_test.cu`）、`gdn/`（`qsa_two_pass_test.cpp`、`routed_stream_test.cpp`）、`prefill/`（`prefill_plan_test.cpp`、`stage_reserve_test.cpp`）。
- **`kvmem/tests`**：`cache-admission-http.py`、`query-policy-regression.py`、`gdn-replay-test.cpp`、`checkpoint-tail-test.cpp`、`http-host-memory-test.cpp`。
- **`LMCache/tests`**：`v1/`（Chunk 索引与存储后端）、`disagg/`（P/D 分离传输）、`test_serde.py`。

### 学习路线建议
按**“Load → Prefill → Decode 数据流 + 单元测试切入”**，避免直接通读上万行大文件：
1. **建立地图**：先读 `lm-llama/research/strata-vs-llamacpp-source-analysis-20261112.zh-CN.md` 第 2、4、5 节与 `kvmem/README.zh-CN.md`。
2. **按单测切入核心模块**：`llama.cpp` 配合 `llamacpp-file-expert-7-day-plan.zh-CN.md` + `test-expert-store.cpp`；`Strata` 拆成 `core/`（专家放置）、`gdn/`（3:1 混合注意力）、`prefill/`（Stager 流水线）三块阅读；`kvmem` 从 `gdn-replay-test.cpp` 与 `llamacpp-kvmem.patch` 切入。
3. **日志与源码对齐**：修改单个单测参数验证断言，并与实机日志里的 `expert cache slots`、`RS buffer`、`KV buffer` 一一对应。

## 相关链接
- [[kv-cache-tiering-principles|KV Cache 分层的五条原理]]
- [[kvmem-dense-vs-moe-and-extreme-thinking|KVMem 在 27B Dense 与 MoE 下的上下文、并发与极限思考实测]]
- [[qwen38-gdn-qsa-hybrid-architecture|千问 3.8 的 GDN 与 QSA 混合注意力原理解析]]
