---
type: Concept
title: 离线推理与批量推理
description: 离线推理不是“没有服务端”的同义词，而是以数据集为中心的推理模式：输入通常来自文件、表、队列或对象存储，输出写回数据集或结果文件。它不追求单个用户请求的最低
  TTFT，而是追求单位时间内处理更多样本、失败后可续跑、结果可审计。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 离线推理与批量推理

离线推理不是“没有服务端”的同义词，而是以数据集为中心的推理模式：输入通常来自文件、表、队列或对象存储，输出写回数据集或结果文件。它不追求单个用户请求的最低 TTFT，而是追求单位时间内处理更多样本、失败后可续跑、结果可审计。

## 与在线服务的差异

| 维度 | 在线 serving | 离线 / batch inference |
|---|---|---|
| 目标 | 低延迟、流式返回、SLO | 高吞吐、低成本、可恢复 |
| 输入 | 单请求或小批请求 | 大数据集、JSONL、表格、对象存储 |
| 调度 | admission control、continuous batching | 数据分片、worker 并行、engine batch |
| 指标 | TTFT、TPOT、p99、错误率 | samples/s、tokens/s、cost/sample、重试率 |
| 失败处理 | 请求失败或降级 | checkpoint、跳过已完成样本、幂等输出 |

在线服务常用 `max-concurrent-requests` 控制排队，离线推理更常用 `batch_size`、`concurrency`、`max_tasks_in_flight` 这类数据流水线参数控制吞吐和恢复粒度。

## 核心原理

### 两层 batch

离线 LLM 推理通常有两层 batch：

1. 数据层 batch：一次从数据集中取多少条样本，影响 I/O、预处理、后处理和失败重试粒度。
2. Engine 层 batch：推理框架实际把多少 token/sequence 放进一次调度，影响 GPU 利用率、KV cache 和尾延迟。

Ray Data LLM 的 `vLLMEngineProcessorConfig` 同时暴露 `batch_size`、`concurrency`、`max_concurrent_batches`、`max_pending_requests` 和 `engine_kwargs`。`batch_size` 太小会让 GPU 等数据，太大会让单批失败重跑成本变高；`engine_kwargs` 里的 `max_model_len`、`max_num_batched_tokens`、`enable_chunked_prefill` 仍然决定显存和 token 调度。

Ray Serve LLM 更偏在线 serving：它提供 OpenAI-compatible endpoint、autoscaling、load balancing 和 back-pressure，适合把 vLLM/SGLang 作为线上 deployment 管理；如果目标是大数据集离线处理，优先看 Ray Data LLM。

### OpenAI Batch 文件格式

OpenAI Batch API 和 vLLM 的 OpenAI Batch 文件格式都把每个任务做成一行请求记录，常见字段包括 `custom_id`、`method`、`url`、`body`。`custom_id` 是离线任务的关键：它让输出可以和原始样本稳定 join，失败重跑时也更容易去重。

### 吞吐优先不等于无限并发

离线推理可以牺牲 TTFT，但不能无限增大并发。极限通常来自：

- KV cache：长 prompt 或大输出导致每个样本占用更多上下文状态。
- prefill 峰值：超长输入在同一批进入会造成 activation 或 attention 临时内存峰值。
- 输出长度分布：少数长输出拖住整批后处理。
- 数据流水线：tokenization、chat template、对象存储读写可能成为瓶颈。

## 常见参数映射

| 框架 / 工具 | 参数 | 作用 |
|---|---|---|
| vLLM offline | `LLM(...)` engine args、`SamplingParams` | 离线加载模型并对 prompt 批量生成；仍受 `max_model_len`、`gpu_memory_utilization`、`max_num_batched_tokens` 等影响 |
| vLLM OpenAI Batch | OpenAI Batch JSONL 字段 | 复用 OpenAI-compatible 请求格式做离线批量处理 |
| vLLM benchmark | `benchmark throughput`、`benchmark serve` | 分别测离线 engine 吞吐和在线服务负载；不要用在线压测替代离线吞吐测量 |
| Ray Data LLM | `batch_size`、`concurrency`、`max_concurrent_batches`、`max_pending_requests`、`task_type` | 控制数据集分片、engine replica、并发批次和任务类型 |
| Ray Data LLM | `engine_kwargs` | 透传 vLLM/SGLang engine 参数，例如 `max_model_len`、`max_num_batched_tokens` |
| Ray Serve LLM | deployment replicas、autoscaling config、`engine_kwargs` | 在线部署和弹性伸缩，不是离线数据集处理的主路径 |
| OpenAI Batch API | input file、endpoint、completion window、metadata | 由平台异步处理大量请求，适合非实时任务 |

## 调参路径

### GPU 利用率低

优先增大数据层 `batch_size`，再增加 `concurrency` 或 engine replica。如果 GPU 仍然空转，检查 tokenization、数据读取和后处理是否在 CPU 或存储侧排队。

### 批量任务频繁 OOM

先降低 `max_model_len` 和每批 token 预算，再检查输入长度分布。离线场景应把超长样本单独分桶处理，而不是让少数长样本拖累所有批次。

### 结果难以回溯

使用稳定 `custom_id`，保留模型名、revision、采样参数、chat template 版本和输入哈希。离线批量任务的主要风险不是单次失败，而是几百万条输出后来无法解释。

### 重跑成本太高

缩小数据层 batch，开启 checkpoint 或分区级输出。批越大吞吐可能越好，但失败时重算窗口也越大。

## 与其他机制的关系

- [推理性能指标与基准测试](inference-benchmarking-metrics.md)：离线 benchmark 更看吞吐，线上 benchmark 更看尾延迟。
- [Tokenizer、chat template 与 token 预算](tokenizer-and-chat-templates.md)：批量任务必须固定模板，否则结果不可比。
- [LoRA 与 adapter serving](lora-and-adapter-serving.md)：多 adapter 离线任务要按 adapter 分桶，减少切换。
- [容量规划公式](capacity-planning-formulas.md)：用公式预估最大批量和并发上限。

## 关键来源

- vLLM Offline Inference: https://docs.vllm.ai/en/stable/examples/basic/offline_inference/
- vLLM Offline Inference with the OpenAI Batch file format: https://docs.vllm.ai/en/stable/examples/features/openai_batch/
- vLLM Benchmark CLI: https://docs.vllm.ai/en/stable/benchmarking/cli/
- vLLM bench throughput: https://docs.vllm.ai/en/stable/cli/bench/throughput/
- OpenAI Batch API: https://developers.openai.com/api/docs/guides/batch
- Ray Data Batch Inference: https://docs.ray.io/en/latest/data/batch_inference.html
- Ray Data Working with LLMs: https://docs.ray.io/en/latest/data/working-with-llms.html
- Ray `vLLMEngineProcessorConfig`: https://docs.ray.io/en/latest/data/api/doc/ray.data.llm.vLLMEngineProcessorConfig.html
- Ray Serve LLM: https://docs.ray.io/en/latest/serve/llm/index.html
