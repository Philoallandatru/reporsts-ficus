---
type: Concept
title: llama.cpp 131K TPS 扫描结果
description: 日期：2026-09-01 02:15:06
tags:
- llm
- llamacpp
- kv-cache
sources:
- c:/Users/Administrator/Documents/Code/my-code/lm-llama/research/llamacpp_131k_tps_sweep_summary.md
createdAt: '2026-11-23'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# llama.cpp 131K TPS 扫描结果

日期：2026-09-01 02:15:06

## 概要

| 变体 | 运行次数 | decode TPS 中位数 | decode TPS 均值 | prompt TPS 中位数 |
|---|---:|---:|---:|---:|
| `baseline_b2048_ub512` | 2 | 58.03 | 58.03 | 850.8 |
| `batch512_ub256` | 2 | 57.94 | 57.94 | 859.0 |
| `ngram_batch512` | 2 | 53.51 | 53.51 | 842.3 |
| `ot56_63_batch512` | 2 | 24.14 | 24.14 | 635.3 |
| `ot48_63_batch512` | 2 | 15.93 | 15.93 | 510.1 |
| `mtp_batch512` | 2 | 6.94 | 6.94 | 2.3 |

原始 JSON：`C:\Users\Administrator\Documents\Code\my-code\lm-llama\research\llamacpp_131k_tps_sweep_results.json`
日志：`C:\Users\Administrator\Documents\Code\my-code\lm-llama\research\llamacpp-131k-tps-logs`