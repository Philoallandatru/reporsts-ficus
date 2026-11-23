---
type: Concept
title: SGLang Server Arguments 参数模型
description: SGLang 同时面向结构化 LLM 程序和高性能 serving。它的关键特征包括 RadixAttention/prefix cache、chunked
  prefill、并行部署、LoRA、structured output、speculative decoding 和 prefill/decode disaggregation。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# SGLang Server Arguments 参数模型

SGLang 同时面向结构化 LLM 程序和高性能 serving。它的关键特征包括 RadixAttention/prefix cache、chunked prefill、并行部署、LoRA、structured output、speculative decoding 和 prefill/decode disaggregation。

## 参数分组

| 类别 | 常用参数 | 原理与影响 |
|---|---|---|
| 模型与 tokenizer | `--model-path` / `--model`、`--tokenizer-path`、`--tokenizer-mode`、`--load-format`、`--trust-remote-code`、`--context-length`、`--model-impl` | 决定权重、tokenizer、模型实现和最大上下文 |
| HTTP/gRPC 服务 | `--host`、`--port`、`--grpc-mode`、`--ssl-*`、`--enable-http2`、`--allowed-media-domains` | 控制服务协议、安全和多模态远程媒体边界 |
| 量化与 dtype | `--dtype`、`--quantization`、`--kv-cache-dtype`、`--quantization-param-path` | 权重和 KV cache 低精度；FP8 KV cache 通常需要 scaling factors |
| 内存与调度 | `--mem-fraction-static`、`--max-running-requests`、`--max-queued-requests`、`--max-total-tokens`、`--chunked-prefill-size`、`--max-prefill-tokens`、`--prefill-max-requests`、`--schedule-policy` | static memory 主要给模型权重 + KV cache；chunked prefill 降低长 prompt 峰值；`lpm` 倾向最长前缀匹配 |
| prefix cache | `--disable-radix-cache`、`--radix-eviction-policy`、schedule policy | RadixAttention 用 radix tree 复用公共前缀 KV |
| runtime 优化 | `--enable-torch-compile`、`--cuda-graph-max-bs-decode`、attention backend 参数 | CUDA graph 可降低 launch overhead，但会预留额外内存 |
| 并行 | `--tp` / `--tensor-parallel-size`、`--dp`、`--nnodes`、`--node-rank`、`--dcp-size` | TP/DP/多节点/DCP 控制模型和请求在多卡间分布 |
| LoRA | LoRA serving 参数 | 控制 adapter 数量、rank、加载方式 |
| speculative decoding | speculative、n-gram、EAGLE/MTP 相关参数 | 用草稿 token 降低主模型 decode 计算 |
| disaggregation | `--disaggregation-mode` 及传输 backend 参数 | 把 prefill 和 decode 放在不同实例/资源池，适合长 prompt 或高并发生产系统 |

## 关键参数原理

### `--mem-fraction-static`

SGLang 官方调优文档把总显存拆成模型权重、KV cache pool、CUDA graph buffers 和 activations。`--mem-fraction-static` 控制模型权重 + KV cache pool 占 GPU 显存的比例。值越高，KV cache 越大、并发能力越强；值过高会挤掉 activation 和 CUDA graph 空间，造成运行期 OOM。

### `--chunked-prefill-size`

长 prompt prefill 是一次性计算密集阶段，activation 峰值明显。把 prefill 切块可以降低峰值显存，代价是更多调度步骤和更慢的 prefill。官方建议遇到 prefill OOM 时可降到 4096 或 2048 级别试探。

### RadixAttention 与 `--schedule-policy`

RadixAttention 把公共 prompt 前缀组织成 radix tree，多个请求共享已经计算过的 KV。`schedule-policy=lpm` 会偏向最长前缀匹配，更适合大量共享 system prompt、工具说明或 RAG 模板的场景；`fcfs` 更直观，适合公平性优先。

### `--max-running-requests`

它限制同时处于运行态的请求数。decode OOM 通常来自并发请求持有的 KV cache 和 decode batch 过大；降低该值会牺牲峰值吞吐，但能稳定尾延迟和显存。

### `--kv-cache-dtype`

`auto` 会使用模型 dtype；显式 FP8/FP4 KV cache 可以换取更多上下文和并发。风险是需要正确 scaling factors，否则某些模型可能出现精度退化。

### `--cuda-graph-max-bs-decode`

CUDA graph 对固定 batch size 的 decode 很有效，但每个捕获 batch size 都会占内存。增加上限可能提升大 batch decode throughput，同时需要降低 `--mem-fraction-static` 预留更多动态空间。

## 调参建议

- OOM during prefill：先降 `--chunked-prefill-size`，再降 `--max-prefill-tokens`。
- OOM during decoding：先降 `--max-running-requests`，再降 `--mem-fraction-static` 或 KV cache dtype。
- GPU 利用率低但显存充足：逐步提高 `--mem-fraction-static`，扩大 KV cache pool 和并发。
- 长上下文生产：评估 disaggregated prefill/decode，把 prefill-heavy 请求和 decode-heavy 请求拆开扩容。

## 关键来源

- SGLang Server Arguments: https://docs.sglang.io/docs/advanced_features/server_arguments
- SGLang Hyperparameter Tuning: https://docs.sglang.io/docs/advanced_features/hyperparameter_tuning
- SGLang speculative decoding: https://docs.sglang.io/docs/advanced_features/speculative_decoding
