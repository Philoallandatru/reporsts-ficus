---
type: Concept
title: vLLM Engine Args 参数模型
description: vLLM 的核心抽象是一个高吞吐 LLM engine：PagedAttention 管理 KV cache，调度器做 continuous
  batching，OpenAI-compatible server 暴露服务。调参时最重要的是 token 预算、KV cache 预算和并行策略。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# vLLM Engine Args 参数模型

vLLM 的核心抽象是一个高吞吐 LLM engine：PagedAttention 管理 KV cache，调度器做 continuous batching，OpenAI-compatible server 暴露服务。调参时最重要的是 token 预算、KV cache 预算和并行策略。

## 参数分组

| 类别 | 常用参数 | 原理与影响 |
|---|---|---|
| 模型加载 | `model`、`--tokenizer`、`--revision`、`--trust-remote-code`、`--dtype`、`--quantization`、`--load-format` | 决定权重来源、模型代码、权重 dtype、量化 kernel |
| 上下文 | `--max-model-len` | prompt + output 的总上下文窗口；可用 `k/m/g/K/M/G` 可读格式，`auto` 会尝试选择可装入显存的最大长度 |
| KV cache | `--block-size`、`--gpu-memory-utilization`、`--kv-cache-memory-bytes`、`--kv-cache-dtype`、`--num-gpu-blocks-override` | PagedAttention 以 block 管理 cache；显存利用率默认是每实例预算，不是全机全局协调 |
| 调度容量 | `--max-num-batched-tokens`、`--max-num-seqs`、scheduler config 字段 | 限制单轮调度 token 数和序列数，是吞吐/延迟核心旋钮 |
| prefix cache | `--enable-prefix-caching`、`--prefix-caching-hash-algo`、`--prefix-match-unit` | 相同前缀的 KV block 可复用；hash 算法涉及性能与多租户碰撞风险 |
| offload | `--cpu-offload-gb`、`--kv-offloading-size`、`--kv-offloading-backend`、`--offload-*` | 用 CPU 内存换 GPU 容量，代价是 PCIe/NVLink 传输延迟 |
| 并行 | `--tensor-parallel-size` / `-tp`、`--pipeline-parallel-size` / `-pp`、`--data-parallel-size` / `-dp`、`--decode-context-parallel-size` / `-dcp`、`--prefill-context-parallel-size` / `-pcp` | TP/PP/DP/DCP/PCP 分别切权重、层、副本、decode KV、prefill 序列 |
| LoRA | `--enable-lora`、`--max-loras`、`--max-lora-rank`、`--fully-sharded-loras` | 多 adapter 服务时限制同时活跃 LoRA 数和 rank；高 TP/长序列时 fully sharded 可能更快 |
| 推测解码 | speculative decoding 相关参数 | 用 draft model 或 n-gram 降低主模型 decode 次数 |
| 服务 | `--host`、`--port`、OpenAI-compatible API 参数、metrics/logging 参数 | 控制 API 边界、观测与集成 |

## 关键参数原理

### `--gpu-memory-utilization`

该参数指定当前 vLLM 实例可用于 model executor 的 GPU 显存比例，默认值来自官方文档。它不是集群级资源管理器；同一张 GPU 上跑多个 vLLM 实例时，需要人为给每个实例拆预算。

### `--kv-cache-memory-bytes`

如果设置，它比 `--gpu-memory-utilization` 更直接：明确指定每张 GPU 用多少字节做 KV cache。适合生产环境固定容量，减少 profiler 推导带来的漂移。

### `--block-size`

PagedAttention 把 KV cache 切成固定 token block，类似虚拟内存分页。小 block 碎片少、调度灵活；大 block metadata 更少、可能更利于吞吐。实际最优值依赖模型、上下文长度和硬件 kernel。

### `--max-model-len`

它是单请求 prompt + output 的总上限。调大后，不代表每个请求一定用满，但 engine 需要能为最坏情况留出 KV cache 预算。长上下文服务中，它经常是吞吐下降的根因。

### `--max-num-batched-tokens` / `--max-num-seqs`

这两个参数控制调度器一次能处理多少 token 和多少 sequence。token budget 影响长 prompt/prefill 和 decode 混批，sequence budget 影响短请求并发。吞吐低但显存有余量时可以逐步提高；TTFT 或尾延迟变差时回退。

### `--enable-prefix-caching`

Prefix caching 让系统缓存共同前缀的 KV block。RAG、多轮对话系统 prompt、agent 工具说明、few-shot 模板都能受益。多租户场景要注意 hash 碰撞和隐私隔离，官方文档也对非加密 hash 给出风险提醒。

### 并行参数

- `--tensor-parallel-size`：把大矩阵切到多卡，降低单卡权重压力。
- `--pipeline-parallel-size`：按层切分，适合更大模型，但有流水线调度成本。
- `--data-parallel-size`：多副本提升总吞吐，常和负载均衡一起用。
- `--decode-context-parallel-size`：针对 decode 阶段 KV cache/attention 的并行，特别适合长上下文或 MLA 相关模型。

## 调参建议

- 单机高吞吐：优先调 `--gpu-memory-utilization`、`--max-model-len`、batch token 预算和 prefix caching。
- 多租户：避免激进的 `xxhash` prefix hash，除非能接受碰撞风险；设置明确的请求上限。
- 显存不足：降低 `--max-model-len`，启用权重量化或 KV cache 低精度，再考虑 CPU offload。
- 长上下文：同时关注 `--max-model-len`、KV cache dtype、DCP/PCP、prefix cache；不要只拉高 context。

## 关键来源

- vLLM Engine Arguments: https://docs.vllm.ai/en/stable/configuration/engine_args/
- vLLM PagedAttention: https://docs.vllm.ai/en/stable/design/paged_attention/
- vLLM Automatic Prefix Caching: https://docs.vllm.ai/en/stable/features/automatic_prefix_caching/
- vLLM Speculative Decoding: https://docs.vllm.ai/en/stable/features/spec_decode/
