---
type: Concept
title: 真实场景 llama.cpp 缓存冒烟测试结果
description: 日期：2026-09-01 01:09:45
tags:
- llm
- llamacpp
- kv-cache
sources:
- c:/Users/Administrator/Documents/Code/my-code/lm-llama/research/llamacpp_realistic_cache_smoke_summary.md
createdAt: '2026-11-23'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 真实场景 llama.cpp 缓存冒烟测试结果

日期：2026-09-01 01:09:45

## 运行配置

- 模型：`C:\Users\Administrator\Documents\models\Qwen3.8-27B-UD-IQ3_XXS.gguf`
- 服务：`C:\Users\Administrator\Documents\models\llama\llama-server.exe`
- GPU：`CUDA_VISIBLE_DEVICES=0`
- 上下文：`8192`
- 变体：`baseline_no_cache, cache_ram_4096`

## 概要

- 缓存命中用例：非 control 用例中 `8` / `13`
- prompt 加速中位数：`2.91x`
- prompt 加速最大值：`7.09x`
- 基线 decode TPS 中位数：`57.68`
- 缓存版 decode TPS 中位数：`57.74`

## 对比明细

| 场景 | 步骤 | 名称 | 缓存 token | 缓存比例 | prompt 加速 | wall 加速 | decode TPS |
|---|---:|---|---:|---:|---:|---:|---:|
| `real_coding_same_prefix` | 1 | `mechanism_summary` | 0 | 0.00% | 0.95x | 0.96x | 50.74 |
| `real_coding_same_prefix` | 2 | `risk_list` | 4088 | 88.85% | 6.78x | 3.91x | 54.40 |
| `real_coding_same_prefix` | 3 | `test_plan` | 4088 | 88.79% | 6.83x | 3.85x | 54.54 |
| `swe_trajectory_shape` | 1 | `agent_start` | 4088 | 88.01% | 5.97x | 3.73x | 57.80 |
| `swe_trajectory_shape` | 2 | `tool_result_1` | 4088 | 87.07% | 5.36x | 3.51x | 57.39 |
| `swe_trajectory_shape` | 3 | `tool_result_2` | 4179 | 88.13% | 6.16x | 3.79x | 57.68 |
| `swe_trajectory_shape` | 4 | `revisit` | 4179 | 89.95% | 7.09x | 4.09x | 57.02 |
| `working_set_pressure` | 1 | `warm_A_llama_server` | 0 | 0.00% | 0.91x | 0.77x | 58.67 |
| `working_set_pressure` | 2 | `warm_B_llama_args` | 0 | 0.00% | 0.92x | 0.87x | 58.48 |
| `working_set_pressure` | 3 | `warm_C_lmcache_mp` | 0 | 0.00% | 0.92x | 0.85x | 58.25 |
| `working_set_pressure` | 4 | `warm_D_lmcache_storage` | 0 | 0.00% | 0.83x | 0.79x | 58.73 |
| `working_set_pressure` | 5 | `revisit_A_llama_server` | 1236 | 70.39% | 2.37x | 1.45x | 58.68 |
| `working_set_pressure` | 6 | `revisit_B_llama_args` | 1656 | 76.10% | 2.91x | 1.73x | 58.49 |
| `negative_control` | 1 | `cache_prompt_false` | 0 | 0.00% | 0.94x | 0.90x | 54.37 |

## 解读

本次冒烟测试使用真实本地源码/文档作为 prompt 语义内容，使用类 SWE-agent/OpenHands 的请求推进作为 trace 形状。
decode TPS 由 `predicted_n / predicted_ms` 推导；本次每个请求只生成 16 个 token，所以 TPS 更适合作为健全性检查，而不是稳定的吞吐基准。

原始 JSON：`C:\Users\Administrator\Documents\Code\my-code\lm-llama\research\llamacpp_realistic_cache_smoke_results.json`
日志：`C:\Users\Administrator\Documents\Code\my-code\lm-llama\research\llamacpp-realistic-cache-logs`