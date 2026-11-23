---
type: Concept
title: Dense 稠密模型 vs MoE 专家模型 & 思考强度与投机解码入门
description: 新手入门指南：搞懂为什么 35B/120B 的 MoE 模型反而比 27B Dense 跑得快、MoE 缓存命中率怎么影响速度，以及 Thinking
  思考强度和 MTP 投机解码的原理。
tags:
- llm
- beginner
- moe
- reasoning
- speculative-decoding
createdAt: '2026-11-22'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# Dense 稠密模型 vs MoE 专家模型 & 思考强度与投机解码入门

## 一、 Dense（稠密模型）vs MoE（混合专家模型）

| 对比维度 | Dense 模型（如 `Qwen3.8-27B`） | MoE 模型（如 `Qwen3.6-35B-A3B`、`Qwen3.8-120B+`） |
|---|---|---|
| **总参数 vs 激活参数** | **全员上岗**：总参数 27B，每生成一个字都要把 27B 全部算一遍 | **专人专办**：总参数很大（35B~176B），但每个字只挑几个专家（如 `A3B` 只激活 **3B**） |
| **类比** | 每次开会都要公司 270 名员工全员发言 | 公司有 1,700 名专家，但每次只叫最懂行那 30 个人开会 |
| **速度表现** | 每步计算和显存读取量是 MoE 的 **9 倍**，上下文一长更容易变慢 | 每次只算 3B，本机实测 28K 下仍跑 **20.1 tok/s**（27B 仅 **7.6 tok/s**） |
| **主要瓶颈** | 权重和 KV 抢 16 GB 显存，算力与显存带宽双吃紧 | 专家总体积太大（几十到上百 GB），放不进显存，瓶颈在于**怎么少搬运冷专家** |

### 为什么 MoE 的“热专家缓存（MoE Cache）”这么重要？
虽然每次只挑 10 个专家，但如果这 10 个专家每次都要临时从主机内存通过窄窄的 PCIe 传进显卡，速度照样会卡死（实测 `llama.cpp` 5 条短请求就传了 238 GB）。
因此引擎会在显存里留一块空间专门缓存**最常被点名的“热专家”**：
- **命中率 80% vs 87%**：别小看这 7% 的差距——把常用专家锁在显存不淘汰，再让多核 CPU 并行分担剩下的冷专家（Strata 的做法），能让 GPU 利用率从 37% 直接飙到 98%。

---

## 二、 思考强度（Thinking / Reasoning Effort）

像千问 3.8 这类推理模型支持在正式回答前先在 `<think>...</think>` 标签里打草稿，通常分为 `none`（不思考）、`medium`（中等）、`xhigh`（深度思考）。

- **优点**：面对复杂逻辑、跨十万字的多跳核对时，长思考能帮模型自我纠错（例如在我们的 193K 极限测试中，只有 `xhigh` 成功把漏掉的 `Beta-3 = 350kW` 救了回来，拿到满分）。
- **新手踩坑点（双重消耗）**：
  1. **思考字数也算输出 Token**：如果 `xhigh` 遇到模糊信息反复自我怀疑，可能一口气思考 16,000 个 token 耗尽输出上限，导致根本来不及写出最终答案（`finish_reason: length`）。
  2. **会挤占 KV 工作空间**：思考链越长，KVMem 的生成工作区（`Gen Reserve`）回绕次数就越多。工程上建议配合 `--reasoning-budget` 给思考设上限。

---

## 三、 投机解码（Speculative Decoding / MTP）

大模型之所以慢，是因为 Decode 阶段每次只能吐 1 个字、每吐 1 个字都要把权重读一遍。
**MTP（Multi-Token Prediction，多词预测）** 的思路是**“小草稿员先猜 3~4 个字，大老板一次批量批改”**：
- 如果小草稿员猜对了 3 个字，大老板只需花**几乎相当于算 1 个字的时间**，一次性通过 3~4 个字，速度直接翻倍。
- **在 MoE 上的副作用**：原本算 1 个字只需激活 10 个专家；开 MTP 一次验证 4 个字时，**4 个不同的字可能各自点名不同的专家**，导致单步激活的专家总数翻倍、显存专家缓存更容易 miss（我们在 `nsys` 里实测开 MTP 后 `llama.cpp` 的 H2D 搬运量反而增加了 67%）。

## 相关链接
- [[llm-inference-basics-and-kv-cache|大模型推理入门：Prefill、Decode、TTFT 与 KV Cache]]
- [[qwen38-gdn-qsa-hybrid-architecture|千问 3.8 的 GDN 与 QSA 混合注意力原理解析]]
- [[kvmem-dense-vs-moe-and-extreme-thinking|KVMem 在 27B Dense 与 MoE 下的上下文、并发与极限思考实测]]
