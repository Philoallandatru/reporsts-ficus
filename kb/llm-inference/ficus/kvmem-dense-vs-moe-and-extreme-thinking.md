---
type: Concept
title: KVMem 在 27B Dense 与 MoE 下的上下文、并发与极限思考实测
description: 基于自编译 llama-kvmem-server.exe 的 27B Dense vs 35B-A3B MoE 多上下文/并发对比、Nsight
  MemOps 剖析、256K 极限压力与思考强度测试，以及主机内存变慢与稀疏召回原理。
tags:
- llm
- kv-cache
- kvmem
- llamacpp
- reasoning
- moe
sources:
- C:/Users/Administrator/Documents/Code/my-code/lm-llama/kvmem/README.zh-CN.md
createdAt: '2026-11-22'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# KVMem 在 27B Dense 与 MoE 下的上下文、并发与极限思考实测

## 一、 27B Dense vs 35B-A3B MoE：上下文与并发矩阵（RTX 5080 16 GiB）

本地编译 `llama-kvmem-server.exe`（`cd959bae99ff` + 6 个补丁，CUDA `sm_120a`），对比 **`Qwen3.8-27B-UD-IQ3_XXS`（Dense）** 与 **`Qwen3.6-35B-A3B-UD-IQ2_XXS`（MoE）**：

| 模型与配置 | 上下文 / 并发 | TTFT | 聚合输出 tok/s | 峰值显存 | GPU 利用率 |
|---|---|---:|---:|---:|---:|
| 27B Dense · `--no-kvmem` | 2,354 / `np=1` | 1.49s | 33.87 | 11,701 MiB | 75.3% |
| 27B Dense · `--kvmem (B=1024)` | 2,354 / `np=1` | 2.48s | 25.84 | 11,859 MiB | 73.7% |
| 27B Dense · `--no-kvmem` | 14,030 / `np=1` | 7.12s | 13.42 | 11,981 MiB | 84.4% |
| 27B Dense · `--kvmem (B=4096)` | 14,030 / `np=1` | 8.43s | 11.69 | 11,989 MiB | 77.6% |
| 27B Dense · `--no-kvmem` | 26,854 / `np=1` | 14.22s | 7.63 | 12,481 MiB | 92.3% |
| 27B Dense · `--kvmem (B=4096)` | 26,854 / `np=1` | 15.06s | 7.25 | **11,929 MiB (-552M)** | 84.7% |
| 27B Dense · 原生 `llama-server` | 4×2,354 / `np=4` | 4.28s | 49.27 | 12,005 MiB | 85.9% |
| 27B Dense · `--kvmem (B=1024/lane)` | 4×2,354 / `np=4` | 6.48s | 34.41 | 15,897 MiB | 84.0% |
| 35B-A3B MoE · `--no-kvmem` | 2,354 / `np=1` | 0.90s | **73.39** | 12,157 MiB | 68.8% |
| 35B-A3B MoE · `--no-kvmem` | 14,030 / `np=1` | 2.79s | **34.40** | 12,253 MiB | 63.6% |
| 35B-A3B MoE · `--kvmem (B=4096)` | 14,030 / `np=1` | 2.95s | 31.23 | 12,199 MiB | 71.4% |
| 35B-A3B MoE · `--no-kvmem` | 26,854 / `np=1` | 5.36s | 20.13 | 12,471 MiB | 78.2% |
| 35B-A3B MoE · `--kvmem (B=4096)` | 26,854 / `np=1` | 5.26s | 19.60 | **12,199 MiB (-272M)** | 75.6% |
| 35B-A3B MoE · 原生 `llama-server` | 4×2,354 / `np=4` | 1.56s | **127.55** | 12,029 MiB | 61.7% |
| 35B-A3B MoE · `--kvmem (B=1024/lane)` | 4×2,354 / `np=4` | 2.22s | **124.91** | 14,477 MiB | 87.2% |

### Nsight Systems 12K 显微对比（KVMem 开启时）
- **显存搬运量差 5.8×~184×**：27B Dense 产生 **2,074.3 MB D2H**（KV 换出 + Mean-K 统计）、**1,418.1 MB H2D**（KV 召回）、**1,271.6 MB D2D**（槽位整理）；而 35B-A3B MoE 仅产生 **358.2 MB D2H**、**566.0 MB H2D**、**6.9 MB D2D**。
- **算力与同步耗时**：27B Dense 的全参数 `mul_mat_q` 累计 **`3.72s`**、`cudaStreamSynchronize` **`5.36s`（3,051 次）**；MoE 仅激活 3B 参数，`mul_mat_q` 仅 **`1.48s`**（快 2.5×），`cudaStreamSynchronize` 仅 **`1.74s`（2,032 次）**。

---

## 二、 256K 极限上下文（193K 输入）+ 思考强度实测

在 `Qwen3.8-27B` 上开启 `-c 262144`（输入 `193,113` tokens），植入 6 条带版本覆盖修订（`AUDIT-REVISION`）与 `STANDBY` 剔除的冲突日志，设置极限预算 `B=2048, R=512`（**99% 历史 KV 换出显存**），进行 Turn 1（最新值精算，正解 `$126.28`）+ Turn 2（回溯早期初始值重算，正解 `$165.16` / 差额 `+$38.88`）双轮测试：

| 模式 / 思考强度 | 轮次 | 输出 tokens / 思考字符 | TTFT / 总耗时 | 峰值显存 | 任务完成度 | 现象解析 |
|---|---|---|---|---:|---:|---|
| `--no-kvmem` | T1 | — | **14.65 tok/s 预填充** | 爆显存溢出 | 不可用 | 溢出 16 GiB 走共享内存，跑完 193K 预填充需 ~3.6 小时 |
| `KVMem` + `none` | T1 | 1,051 / 0 | 96.34s / 114.95s | 11,454 MiB | **2/4** | 漏召回第 450 行 `Beta-3=350kW`，错幻觉为 `400kW` |
| `KVMem` + `none` | T2 | 869 / 0 | 2.44s / 17.96s | 11,466 MiB | **2/3** | 延续 T1 错误，`net_165_16` 算错 |
| `KVMem` + `medium` | T1 | 1,460 / 2,026 | 96.51s / 121.09s | 11,454 MiB | **2/4** | 仍未发现 `Beta-3` 召回缺失，同样错用 `400kW` |
| `KVMem` + `medium` | T2 | 1,671 / 1,758 | 3.70s / 31.89s | 11,456 MiB | **2/3** | 同上 |
| `KVMem` + `xhigh` | T1 | **16,384** / **53,667** | 94.90s / 373.50s | 11,212 MiB | **0/4 (`length`)** | 反复自检导致思考链打满 16K 输出上限（`R=512` 回绕 32 次） |
| `KVMem` + `xhigh` | T2 | 2,965 / **5,901** | 3.38s / 53.48s | 11,270 MiB | **3/3 (100%)** | **唯一满分！** 通过 5.9K 字符深度推演成功纠偏并找回 `Beta-3=350kW` |

*(注：在 128K / 105K 输入 + `B=4096, R=1024` 较宽松压力下，`--kvmem` 不仅全拿 3/3 满分，且因工作集从 105K 缩到 4K，Prefill 从 `88.76s` 提速至 `54.60s`、Decode 从 `37.7` 提速至 `57.88 tok/s`，并省下 `3,790 MiB` 显存。)*

---

## 三、 原理解析：为什么放内存会慢，以及为什么不用读完整 193K？

1. **为什么存进主机内存会变慢？**
   - RTX 5080 显存内部带宽约 **960 GB/s**（主厨手边操作台），而经 PCIe 到主机内存的带宽仅 **32.6 GB/s**（差约 **30 倍**），外加打包换出（D2H）、`Mean-K` 记账与 `cudaStreamSynchronize` 同步等待（占 CUDA API 耗时 67.7%）。
   - 因此在显存原本装得下的中短上下文（2K/12K），开 KVMem 会慢 13%~24%；但在 105K/193K 超长上下文下，它靠只保留热点块反而比原生全量扫描更快、且避免爆显存。
2. **为什么不需要读完整的 193K？**
   - **切块摘要（`pre-RoPE Mean-K`）**：按 32 tokens 一块切分 193K（约 6,000 块），在加 RoPE 位置旋转前算出平均 Key 向量作为“目录索引卡”。
   - **翻牌子打分（`page-softmax` + 1-hop `Graph Recall`）**：用当前问题的 Query 向量和 6,000 张摘要卡点积打分，并拉高邻近关联块权重。
   - **头 + 尾 + 精华（`Sink + Recent + Selected = B`）**：显存只留开头锚点（Sink）、最新后缀（Recent + 生成工作区 `R`）与高分历史块，其余全放内存。
   - **原位恢复零重算（`No re-RoPE`）**：召回的 KV 块保留原始位置编号 `orig_pos` 直接拷入显存，无需反量化或重跑模型前向计算。

## 相关链接
- [[kv-cache-tiering-principles|KV Cache 分层的五条原理]]
- [[strata-vs-llamacpp-profiling-and-scenarios|Strata 与 llama.cpp 多场景实测、Nsight Profiling 与模块学习路线]]
- [[qwen38-gdn-qsa-hybrid-architecture|千问 3.8 的 GDN 与 QSA 混合注意力原理解析]]
