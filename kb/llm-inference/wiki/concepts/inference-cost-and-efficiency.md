---
type: Concept
title: 推理成本与效率模型
description: 推理成本不是单纯的“每秒 tokens 越多越便宜”。真实成本由硬件时间、可用吞吐、SLO 成功率、输入/输出长度、缓存命中、批处理效率和失败重试共同决定。一个系统总
  tokens/s 很高，但如果大量请求超过 TTFT/p99 SLO，业务可用容量仍然很低。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 推理成本与效率模型

推理成本不是单纯的“每秒 tokens 越多越便宜”。真实成本由硬件时间、可用吞吐、SLO 成功率、输入/输出长度、缓存命中、批处理效率和失败重试共同决定。一个系统总 tokens/s 很高，但如果大量请求超过 TTFT/p99 SLO，业务可用容量仍然很低。

## 基本公式

| 指标 | 近似公式 | 用途 |
|---|---|---|
| 每小时实例成本 | 云实例单价 + 存储 + 网络 + 管理开销 | 预算上限 |
| tokens/s | 单位时间输出或输入+输出 token 数 | 粗吞吐 |
| cost / 1M tokens | 每小时成本 / 每小时 token 数 * 1,000,000 | 框架/硬件横向比较 |
| cost / good token | 每小时成本 / 满足 SLO 的 token 数 | 生产容量比较 |
| cost / request | 实例占用时间成本 + provider token 成本 + 重试成本 | 业务估价 |
| cache-adjusted cost | 未命中成本 * 未命中率 + 命中成本 * 命中率 | 评估 prompt/prefix/semantic cache |

在自托管 GPU 中，输入 token 和输出 token 的成本结构不同：长输入主要消耗 prefill 计算和 KV cache，长输出主要消耗 decode 步数和持续占用时间。云 API 计价常把 input/output/reasoning/cache token 分开；自托管则要自己用 benchmark 和 metrics 建模。

## 输入与输出长度

| 负载形态 | 成本驱动 | 优先优化 |
|---|---|---|
| 短输入短输出 | 请求调度、tokenizer、网络、batch overhead | continuous batching、低开销网关 |
| 长输入短输出 | prefill、TTFT、KV cache、prefix cache | prompt 压缩、prefix cache、chunked prefill、disaggregation |
| 短输入长输出 | decode tokens/s、KV cache 占用时间 | decode batch、speculative decoding、量化 |
| 长输入长输出 | prefill + decode + KV cache 全部高 | 限长、分池、容量规划、缓存 |
| Agent/tool 多轮 | 重复系统 prompt、tool schema、历史消息增长 | prompt cache、history compaction、schema 稳定化 |

成本估算必须用真实长度分布。只用平均长度会低估长尾，因为少数超长 prompt 会显著影响 KV cache、TTFT 和排队。

## Goodput 比 Throughput 更重要

Throughput 统计系统做了多少工作；goodput 统计系统在 SLO 内完成了多少有用工作。LLM 服务常见 SLO 包括：

- TTFT p95/p99。
- TPOT 或 inter-token latency。
- 端到端请求延迟。
- 成功率和格式正确率。
- 每租户公平性。

调大 batch token budget 往往提高 tokens/s，但如果 TTFT 和 p99 超标，cost / good token 可能变差。

## 成本杠杆

| 杠杆 | 降成本原理 | 风险 |
|---|---|---|
| 权重量化 | 降低权重显存，使用更小 GPU 或更多副本 | 质量下降、kernel 不匹配、吞吐反降 |
| KV cache 量化 | 降低长上下文和并发显存 | 长上下文质量和数值稳定性风险 |
| Prefix/prompt cache | 复用重复 prefill | template/revision 变化会破坏命中 |
| Response/semantic cache | 直接复用答案或近似答案 | 权限、时效性、质量和安全边界 |
| Continuous batching | 提高 GPU 利用率 | 过大 batch 增加尾延迟 |
| Speculative decoding | 用 draft/heads 减少目标模型 decode 步数 | 接受率低时浪费算力 |
| 多副本/data parallel | 横向扩吞吐、降低排队 | 权重加载和空闲副本成本 |
| 分离式 prefill/decode | 让不同硬件池处理不同阶段 | KV transfer 成本和系统复杂度 |
| 离线 batch | 用较松 SLO 换更高利用率 | 不适合交互式业务 |

## 利用率陷阱

GPU utilization 高不一定成本好：

- 如果大量时间花在无效重试，利用率高但 goodput 低。
- 如果 MoE all-to-all 或 offload 等待占比高，GPU 可能忙但 tokens/s 不好。
- 如果 batch 太大导致 p99 超标，总 tokens/s 提升反而减少可用容量。
- 如果 scale-to-zero 冷启动频繁，steady-state benchmark 会低估实际成本。

## 一个实用估算流程

1. 收集真实请求分布：input tokens、output tokens、并发、到达率、工具调用轮数、prefix sharing。
2. 单实例压测：记录 TTFT、TPOT、tokens/s、goodput、GPU memory、KV usage。
3. 把 benchmark 分成 prefill-heavy、decode-heavy 和 mixed 三组，不要只取总平均。
4. 计算在目标 SLO 下每实例可承载 QPS 和 token/s。
5. 加入副本冗余、冷启动、失败重试、网关和缓存命中率。
6. 用云实例公开价格或内部折旧价格换算 cost / request 与 cost / good token。

## 与其他页面的关系

- [推理性能指标与基准测试](inference-benchmarking-metrics.md)：指标口径。
- [推理负载建模与压测数据集](workload-modeling-and-load-testing.md)：如何构造真实负载。
- [推理缓存层：Response、Semantic、Prompt 与 KV](inference-caching-layers.md)：缓存如何改变成本曲线。
- [推理容量规划公式](capacity-planning-formulas.md)：显存、KV 和并发估算。
- [Autoscaling 与 Admission Control](autoscaling-and-admission-control.md)：把成本模型落到扩缩容。

## 关键来源

- NVIDIA NIM LLM benchmarking metrics: https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html
- NVIDIA NIM benchmarking overview: https://docs.nvidia.com/nim/benchmarking/llm/latest/overview.html
- NVIDIA AIPerf metrics reference: https://docs.nvidia.com/aiperf/reference/ai-perf-metrics-reference
- NVIDIA AIPerf repository: https://github.com/ai-dynamo/aiperf
- vLLM serving benchmark: https://docs.vllm.ai/en/stable/cli/bench/serve/
- vLLM benchmark CLI: https://docs.vllm.ai/en/stable/benchmarking/cli/
- Triton GenAI-Perf: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html
- Google Cloud Compute pricing: https://cloud.google.com/products/compute/pricing
- Google Cloud GPU documentation: https://docs.cloud.google.com/compute/docs/gpus
