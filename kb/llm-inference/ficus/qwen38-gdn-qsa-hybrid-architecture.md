---
type: Concept
title: 千问 3.8 的 GDN 与 QSA 混合注意力原理解析
description: 解析 Qwen3.8 3:1 混合架构中 GDN 线性注意力与 QSA 注意力的分工，以及为什么 120B+ MoE 在本地平台上能开比
  27B Dense 更大的上下文且保持较高速度。
tags:
- llm
- attention
- gdn
- qsa
- moe
- qwen3.8
createdAt: '2026-11-22'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 千问 3.8 的 GDN 与 QSA 混合注意力原理解析

在千问 3.8 系列（如 `Qwen3.8-Flash-Next` 48 层、`Qwen3.8-27B`）中，采用了 **3:1 混合注意力架构**：每 4 层为一组，由 **3 层 GDN + 1 层 QSA** 组成。

## 一、 GDN vs QSA 核心对比

| 维度 | GDN (Gated DeltaNet) | QSA (Qwen Sparse / Full Attention) |
|---|---|---|
| **本质** | 带门控遗忘与 Delta 增量更新的**线性注意力 / 循环状态层** | 保留下来的 **Softmax 注意力层**（在 48 层中占 12 层，即 1/4） |
| **类比** | **固定大小的滚动黑板** | **按词建档的精确档案柜** |
| **存储对象** | 不存历史 K/V，只维护固定大小的 `RS buffer`（`R/S/P` 张量，实测 48 层模型固定占用 **450.28 MiB**） | 唯一真正产生并存储 **KV Cache** 的层（实测 `32K` 上下文、`q8_0` 仅占 **408.00 MiB**，约 12.75 KB/token） |
| **复杂度与长处** | 显存与 Decode 访存均为 **$O(1)$**，不随上下文增长，推进语义脉络极快 | 保留历史 token 原始 K/V，负责**跨十万字的点对点精确检索**（如审计数字、序列号） |
| **短板** | 信息有损压缩在固定矩阵内，精确回忆孤立细节容易模糊 | KV 随上下文线性增长，但因仅占 1/4 层，总 KV 体积已比传统全注意力砍掉 **75%** |
| **引擎层体现** | `llama.cpp` 中为 `llama_memory_recurrent` / `gdn_single` 算子 | `llama.cpp` 中为 `llama_kv_cache`；Strata 中含 `qsa_two_pass` 实现 |

---

## 二、 为什么 120B+ MoE 能开比 27B Dense 更大的上下文且速度不慢？

1. **KV 体积不看“总参数量”，且冷专家可移出显存**：
   - 120B+/176B 的绝大部分参数是静态的 **MoE 专家（FFN 权重）**，专家权重不随上下文膨胀，也不产生 KV 缓存。
   - 在 Strata / llama.cpp 平台上，冷专家可放入主机 RAM（几十 GiB）甚至 SSD，显存留给热专家与少量 KV；而 27B Dense 必须把全部权重死锁在 16 GiB 显存内，直接挤压 KV 空间。
2. **激活参数差 9 倍（A3B vs 27B Dense）**：
   - 27B Dense 每生成 1 个 token 需把全部 27B 参数从显存扫一遍（`nsys` 实测 `mul_mat_q` 耗时 **`3.72s`**）；
   - MoE 每次只激活 ~3B 参数（`mul_mat_q` 仅 **`1.48s`**，快 2.5×）。在 28K 上下文实测中，35B-A3B MoE 仍跑出 **`20.13 tok/s`**，而 27B Dense 已降至 **`7.63 tok/s`**。
3. **3/4 线性层 $O(1)$ 不受大上下文拖累 + 热专家锁槽**：
   - 上下文拉到 100K+ 时，75% 的 GDN 层读写量恒定不变；配合 Strata 将 **85%~87% 热专家锁定在显存**、冷专家由 CPU 15 核并发计算，热专家与小体积 KV 互不抢占，因此既能撑起大上下文又能维持较高吞吐。

## 相关链接
- [[strata-vs-llamacpp-profiling-and-scenarios|Strata 与 llama.cpp 多场景实测、Nsight Profiling 与模块学习路线]]
- [[kvmem-dense-vs-moe-and-extreme-thinking|KVMem 在 27B Dense 与 MoE 下的上下文、并发与极限思考实测]]
