---
type: Concept
title: Hugging Face TGI Launcher 参数模型
description: Text Generation Inference (TGI) 的参数核心在 router：限制请求大小、控制 batch token 预算、配置
  sharding/quantization/KV cache dtype，并暴露 Hugging Face 生态友好的 OpenAI/HTTP 服务。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Hugging Face TGI Launcher 参数模型

Text Generation Inference (TGI) 的参数核心在 router：限制请求大小、控制 batch token 预算、配置 sharding/quantization/KV cache dtype，并暴露 Hugging Face 生态友好的 OpenAI/HTTP 服务。

## 参数分组

| 类别 | 常用参数 | 原理与影响 |
|---|---|---|
| 模型加载 | `--model-id`、`--revision`、`--trust-remote-code`、`--tokenizer-config-path`、cache path 参数 | 控制模型和 tokenizer 来源；私有/自定义模型需固定 revision |
| sharding | `--sharded`、`--num-shard`、`--master-addr`、`--master-port`、`--shard-uds-path` | 多 GPU 分片模型，router 与 shard 进程通信 |
| 量化 | `--quantize`、`--dtype`、`--kv-cache-dtype` | 支持 AWQ/GPTQ/Marlin/bitsandbytes/FP8 等；`dtype` 与 `quantize` 不能同时随意叠加 |
| 请求限制 | `--max-concurrent-requests`、`--max-input-tokens`、`--max-total-tokens`、`--max-best-of`、`--max-stop-sequences`、`--payload-limit` | 服务端硬限制，防止单请求或恶意请求耗尽资源 |
| batch 调度 | `--max-batch-prefill-tokens`、`--max-batch-total-tokens`、`--max-waiting-tokens`、`--waiting-served-ratio`、`--max-batch-size` | 控制 prefill/decode 混批、等待队列与 batch token 预算 |
| CUDA/内存 | `--cuda-memory-fraction`、`--cuda-graphs`、`--disable-custom-kernels` | 显存上限、CUDA graph batch size 和 kernel 选择 |
| RoPE | `--rope-scaling`、`--rope-factor` | 位置编码扩展，仅适用于 RoPE 模型 |
| 推测解码 | `--speculate` | Medusa 模型自动使用头；否则使用 n-gram speculation |
| LoRA | `--lora-adapters` | 启动时加载可用 adapter |
| 结构化输出 | grammar / guided generation 相关参数与请求字段 | 用语法约束减少 JSON/格式漂移 |
| 服务/观测 | `--hostname`、`--port`、`--prometheus-port`、`--api-key`、`--cors-allow-origin`、OTLP 参数 | API、安全、metrics 和 tracing |

## 关键参数原理

### `--max-total-tokens`

TGI 官方文档把它称作最重要的内存预算之一。它限制单请求输入 + 生成的总 token 数。值越大，单请求可占 KV cache 越多，batching 效率会下降；值过小则会拒绝长输入或长输出任务。

### `--max-batch-total-tokens`

这是硬件利用率核心参数，表示一个 batch 内所有请求的潜在 token 总量。在非 padding / flash attention 场景，它比 `batch_size * max_total_tokens` 更精细。生产调优常把它设为显存能承受的最大值，然后用延迟 SLO 回退。

### `--waiting-served-ratio` 与 `--max-waiting-tokens`

这两个参数控制“等待请求什么时候插入正在 decode 的 batch”。插入太积极，会频繁打断 decode 做 prefill，正在生成的请求延迟变差；插入太保守，新请求排队时间变长。

### `--kv-cache-dtype`

KV cache 可显式设为 FP8 类型，适合长上下文或高并发。没有设置时通常跟随模型 dtype。低精度 cache 要用真实任务检查质量。

### `--cuda-memory-fraction`

限制 TGI 可见 CUDA 显存比例。多服务共卡时有用，但它不是智能调度器；还要给 NCCL、driver、监控和其他进程留余量。

## 调参建议

- 面向 API 服务：先设置 `--max-concurrent-requests`、`--max-input-tokens`、`--max-total-tokens`，明确拒绝策略。
- 追吞吐：逐步提高 `--max-batch-total-tokens`，观察 TTFT、TPOT 和 OOM。
- 长 prompt：调 `--max-batch-prefill-tokens`，避免 prefill 把显存峰值拉爆。
- 多 GPU：用 `--sharded true` 和 `--num-shard`；确保 interconnect 足够，否则 TP 通信会吃掉收益。

## 关键来源

- TGI launcher arguments: https://huggingface.co/docs/text-generation-inference/reference/launcher
- TGI PagedAttention: https://huggingface.co/docs/text-generation-inference/conceptual/paged_attention
- TGI Tensor Parallelism: https://huggingface.co/docs/text-generation-inference/conceptual/tensor_parallelism
- TGI Speculation: https://huggingface.co/docs/text-generation-inference/conceptual/speculation
