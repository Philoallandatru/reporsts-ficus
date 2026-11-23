---
type: Concept
title: TensorRT-LLM Serving 参数模型
description: TensorRT-LLM 面向 NVIDIA GPU 上的高性能推理，`trtllm-serve` 提供 OpenAI-compatible
  server。当前文档显示服务端支持 `/v1/models`、`/v1/completions`、`/v1/chat/completions`，并有 `/health`、`/metrics`、`/version...
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# TensorRT-LLM Serving 参数模型

TensorRT-LLM 面向 NVIDIA GPU 上的高性能推理，`trtllm-serve` 提供 OpenAI-compatible server。当前文档显示服务端支持 `/v1/models`、`/v1/completions`、`/v1/chat/completions`，并有 `/health`、`/metrics`、`/version` 等观测接口。

## 参数分组

| 类别 | 常用参数 | 原理与影响 |
|---|---|---|
| 启动 | `trtllm-serve serve MODEL`、`--config`、`--backend`、`--generation-config`、`--tokenizer` | 支持 Hugging Face checkpoint 或 TensorRT engine；YAML 可配置 LLM API 参数，CLI 优先级更高 |
| 服务 | `--host`、`--port`、`--log_level`、`--num_serve_frontends`、`--num_postprocess_workers` | 控制 OpenAI-compatible API 与前后处理并发 |
| batch | `--max_batch_size`、`--max_num_tokens`、`--max_beam_width`、`--max_seq_len` | batch size 是请求数上限，num tokens 是去 padding 后 batched token 上限 |
| KV cache | `--free_gpu_memory_fraction` / `--kv_cache_free_gpu_memory_fraction`、`--kv_cache_dtype`、YAML 中 `kv_cache_config` | 模型权重和 buffer 后剩余显存中，为 KV cache 保留的比例 |
| 并行 | `--tensor_parallel_size` / `--tp_size`、`--pipeline_parallel_size` / `--pp_size`、`--context_parallel_size` / `--cp_size`、`--expert_parallel_size` / `--ep_size`、`--gpus_per_node` | TP/PP/CP/EP 分别切矩阵、层、上下文和 MoE experts |
| 多模态 | `mm_embedding_serve`、多模态配置 YAML、`chat_template` 限制 | 部分多模态配置不兼容 KV cache reuse，需要显式关闭 block reuse |
| embeddings | `trtllm-serve embeddings`、`--max_batch_size`、`--max_num_tokens`、`--max_queue_delay`、`--max_queue_size` | encoder-only serving 使用动态 batching，无 KV cache / sampler / scheduler |
| 观测 | `/metrics`、`enable_iter_perf_stats` | metrics 可输出 GPU memory、KV cache 和 in-flight batching 信息 |

## 关键参数原理

### `--max_batch_size`

限制 engine 可调度请求数。值越大，吞吐潜力越高，但每个请求都可能携带 KV cache、beam 或输出状态。对短请求吞吐有效，对长上下文服务则常被 token budget 限制。

### `--max_num_tokens`

限制每批去 padding 后的 token 总数。它比单纯 request batch size 更贴近真实显存和计算量。长 prompt 场景优先看该值。

### `--max_seq_len`

限制单请求 prompt + output 的总长度。如果不设置，通常从模型配置推导。生产环境应显式设定，避免客户端把上下文窗口吃满导致吞吐不可控。

### `--kv_cache_free_gpu_memory_fraction`

TensorRT-LLM 的语义是：模型权重和 buffer 分配后，剩余 GPU 显存中为 KV cache 保留的比例。值越高，可容纳更多 token 和并发；值过高会压缩 activation、通信和临时 workspace 空间。

### `--tp_size` / `--pp_size` / `--cp_size` / `--ep_size`

Tensor parallel 解决单层权重/计算太大；pipeline parallel 解决模型层太多/总权重太大；context parallel 切分长上下文注意力/KV 相关压力；expert parallel 针对 MoE。通信拓扑决定收益，NVLink/NVL72 与普通 PCIe 的最佳点会不同。

## 调参建议

- NVIDIA 生产服务：先用官方 recipe 或 model-specific guide，再微调 `max_batch_size`、`max_num_tokens`、KV cache fraction。
- 长上下文：优先约束 `max_seq_len` 和 `max_num_tokens`，再调整 KV cache fraction。
- 多模态：检查模型限制；部分多模态需要关闭 `kv_cache_config.enable_block_reuse`。
- 观测：开启 metrics，重点看 GPU memory、KV cache、in-flight batching，而不是只看 tokens/s。

## 关键来源

- TensorRT-LLM `trtllm-serve`: https://nvidia.github.io/TensorRT-LLM/commands/trtllm-serve/trtllm-serve.html
- TensorRT-LLM KV Cache System: https://nvidia.github.io/TensorRT-LLM/features/kvcache.html
- TensorRT-LLM Paged Attention / IFB / Scheduler: https://nvidia.github.io/TensorRT-LLM/features/paged-attention-ifb-scheduler.html
