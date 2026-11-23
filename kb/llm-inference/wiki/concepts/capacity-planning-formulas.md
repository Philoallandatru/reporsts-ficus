---
type: Concept
title: 推理容量规划公式
description: 容量规划的目的不是精确预测每个 kernel，而是在部署前判断“能不能装下、能承载多少并发、瓶颈更可能在算力还是内存/网络”。下面的公式适合作为粗估和压测前
  sanity check。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 推理容量规划公式

容量规划的目的不是精确预测每个 kernel，而是在部署前判断“能不能装下、能承载多少并发、瓶颈更可能在算力还是内存/网络”。下面的公式适合作为粗估和压测前 sanity check。

## 1. 权重显存

```text
weight_bytes ~= parameter_count * bytes_per_weight / tensor_parallel_size
```

常见 `bytes_per_weight`：

| 精度 | 粗略字节/参数 |
|---|---:|
| fp32 | 4 |
| fp16 / bf16 | 2 |
| int8 / fp8 | 1 |
| int4 / nf4 | 0.5，加少量 scale/zero-point 开销 |

实际部署还要加 embedding、lm head、量化 scale、runtime workspace、CUDA graph capture、allocator reserve。vLLM 的 `--gpu-memory-utilization`、TensorRT-LLM 的 KV cache fraction、SGLang 的 `--mem-fraction-static` 都不是单纯的权重预算，而是整个 engine 的显存分配策略。

## 2. 单请求 KV cache

```text
kv_bytes_per_request =
  layers
  * tokens_in_context
  * kv_heads
  * head_dim
  * 2
  * bytes_per_kv_element
```

其中 `2` 是 K 和 V。GQA/MQA 模型的 `kv_heads` 小于 attention heads，所以 KV cache 明显更省。beam search、并行采样、多候选输出会让活跃序列数增加，不能只按“用户请求数”估算。

## 3. 最大活跃 token 容量

```text
available_kv_bytes =
  gpu_memory_budget
  - weight_bytes
  - runtime_overhead
  - activation_peak_reserve

max_live_tokens ~= available_kv_bytes
  / (layers * kv_heads * head_dim * 2 * bytes_per_kv_element)
```

这个 `max_live_tokens` 是所有活跃请求的 prompt + generated tokens 总和，不是单请求上下文长度。真正并发上限还要看请求长度分布：

```text
max_concurrency ~= max_live_tokens / avg_live_tokens_per_request
```

如果服务把 `max_model_len` 配得很大，但真实请求平均很短，PagedAttention 可以减少碎片；如果大量请求真的接近上限，吞吐会线性下降。

## 4. Prefill 计算量

粗略看，prefill 对 prompt token 做一次全上下文前向：

```text
prefill_work ~= prompt_tokens * model_flops_per_token
```

长 prompt 的 TTFT 主要由 prefill、排队、tokenization 和 prefix cache 命中决定。Chunked prefill 把超长 prompt 拆成多块，让 decode 请求穿插执行，通常改善尾延迟和 OOM 风险，但可能增加调度开销。

## 5. Decode 吞吐

Decode 每步为每个活跃 sequence 生成一个 token：

```text
decode_tokens_per_second ~= active_sequences / TPOT
```

小 batch decode 容易 GPU 利用率低；大 batch decode 吞吐高但单请求 TPOT 可能变差。对内存带宽敏感的模型，权重读取、KV cache 读取和跨卡通信比峰值 FLOPS 更关键。

## 6. KV transfer 带宽

Prefill/decode 分离或远端 KV cache 需要估算传输时间：

```text
kv_transfer_seconds ~= kv_bytes_to_move / effective_link_bandwidth
```

如果 `kv_transfer_seconds` 接近或超过本地 prefill 节省的时间，分离式架构不会带来收益。跨节点部署要用实测有效带宽，不要直接拿网卡标称值。

## 7. 输出向量存储

Embedding 离线任务要算输出体积：

```text
embedding_output_bytes =
  row_count * embedding_dim * bytes_per_value
```

例如 1,000,000 条、768 维、float32 输出约 3 GB。使用 fp16/int8/binary、`truncate_dim` 或分区写入可以降低存储和网络压力。

## 参数到公式的映射

| 公式项 | 典型参数 |
|---|---|
| `parameter_count` / `bytes_per_weight` | `--dtype`、`--quantization`、GGUF quant、AWQ/GPTQ/FP8 |
| `tokens_in_context` | `--ctx-size`、`--max-model-len`、`--session-len`、`num_ctx` |
| `bytes_per_kv_element` | `--cache-type-k/v`、`--kv-cache-dtype`、`kv_cache_dtype` |
| `available_kv_bytes` | `--gpu-memory-utilization`、`--kv-cache-memory-bytes`、`--mem-fraction-static`、`--cache-max-entry-count` |
| `active_sequences` | `--parallel`、`--max-num-seqs`、`--max-running-requests`、`--max-concurrent-requests` |
| `prefill batch` | `--max-num-batched-tokens`、`--chunked-prefill-size`、`--max-batch-prefill-tokens` |
| `decode batch` | continuous batching / in-flight batching scheduler 参数 |
| `kv transfer` | NIXL/LMCache/Mooncake connector、KV role、transfer backend |

## 实战流程

1. 算权重是否能装下。
2. 算单请求最大 KV cache。
3. 用真实请求分布估算平均 live tokens。
4. 估算并发上限，再留 15% 到 30% 的 runtime/headroom。
5. 压测验证 TTFT、TPOT、p99、OOM 和 cache hit rate。
6. 如果加入 offload 或 disaggregation，单独测 PCIe/NVLink/网络带宽。

## 关键来源

- vLLM Engine Arguments: https://docs.vllm.ai/en/stable/configuration/engine_args/
- vLLM PagedAttention: https://docs.vllm.ai/en/stable/design/paged_attention/
- TensorRT-LLM KV Cache System: https://nvidia.github.io/TensorRT-LLM/features/kvcache.html
- SGLang Hyperparameter Tuning: https://docs.sglang.io/docs/advanced_features/hyperparameter_tuning
- Hugging Face TEI CLI arguments: https://huggingface.co/docs/text-embeddings-inference/en/cli_arguments
- NVIDIA NIM LLM benchmarking metrics: https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html
- PagedAttention paper: https://arxiv.org/abs/2309.06180
