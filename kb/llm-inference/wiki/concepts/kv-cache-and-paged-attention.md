---
type: Concept
title: KV cache 与 PagedAttention
description: KV cache 是 LLM 推理的“历史状态内存”。没有 KV cache，模型每生成一个新 token 都要重新计算所有历史 token
  的 key/value；有了 KV cache，decode 阶段只需要为新 token 计算 K/V，并在 attention 中读取历史 K/V。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# KV cache 与 PagedAttention

KV cache 是 LLM 推理的“历史状态内存”。没有 KV cache，模型每生成一个新 token 都要重新计算所有历史 token 的 key/value；有了 KV cache，decode 阶段只需要为新 token 计算 K/V，并在 attention 中读取历史 K/V。

## KV cache 为什么大

对 decoder-only Transformer，单个请求的 KV cache 近似为：

```text
KV bytes =
  layers
  * tokens_in_context
  * kv_heads
  * head_dim
  * 2         # K and V
  * bytes_per_element
```

服务端并发时还要乘以活跃 sequence 数。使用 MQA/GQA 的模型，`kv_heads` 小于 query heads，因此 KV cache 会明显小于 full multi-head attention。

## 它控制哪些参数

| 参数族 | 典型名字 | 影响 |
|---|---|---|
| 上下文长度 | `ctx-size`、`max-model-len`、`session-len`、`num_ctx`、`max_seq_len` | 线性增加单请求 KV cache |
| 并发序列 | `parallel`、`max-running-requests`、`max-num-seqs`、`max_batch_size` | 线性增加总 KV cache |
| KV dtype | `cache-type-k/v`、`kv-cache-dtype`、`kv_cache_dtype` | f16/bf16 到 fp8/int8/q4 可明显省内存 |
| 内存占比 | `gpu-memory-utilization`、`mem-fraction-static`、`cache-max-entry-count`、`kv_cache_free_gpu_memory_fraction` | 控制多少显存能给 KV cache |
| block 粒度 | `block-size`、`cache_block_seq_len`、`num_kv_blocks` | 影响碎片、管理开销和调度灵活度 |

## PagedAttention 的核心思想

PagedAttention 把 KV cache 分成固定大小 block，类似操作系统分页：逻辑 token 序列不必连续放在物理显存里。这样可以：

- 减少因为不同请求长度不同造成的显存碎片。
- 让 scheduler 更容易插入新请求。
- 支持 prefix cache、block reuse、copy-on-write 等复用策略。
- 让长上下文和高并发服务更接近“按 token 预算”管理，而不是按最大长度整块预留。

PagedAttention 论文还强调了一个容易被忽略的问题：传统系统常为请求最大长度预留连续 KV 空间，真实请求长度又高度不均匀，于是显存浪费来自预留、碎片和复制。Block 化以后，调度器可以把 token 序列映射到非连续物理块，并在并行采样或共享前缀中复用块。

## Prefix cache / KV reuse

Prefix cache 复用多个请求的公共前缀，例如 system prompt、工具说明、few-shot 示例、RAG 模板。它省的是 prefill 计算和部分 KV 存储分配，不改变后续生成 token 仍需 KV cache 的事实。

实现上通常要解决“如何判断两个前缀相同”。vLLM 使用 block-level hashing，把前缀 token 与当前 block token 组合成 cache key；SGLang 的 RadixAttention 用 radix tree 管理公共前缀。前者接近 hash table，后者接近前缀树，但目标都是让共享 prompt 不反复 prefill。

典型适用场景：

- RAG 系统每个请求都有相同 instruction 和格式要求。
- Agent 系统反复发送同一套工具 schema。
- 多轮对话保留长系统提示。
- 批量任务共享模板，只替换少量用户字段。

## 调参判断

| 症状 | 常见原因 | 优先动作 |
|---|---|---|
| 模型能加载，长 prompt OOM | KV cache 或 prefill activation 过大 | 降上下文、降 KV dtype、降低 prefill batch |
| 并发高后 OOM | 活跃 sequence 的 KV 总量过大 | 降并发、降 KV dtype、扩大 KV pool |
| 显存有余但吞吐低 | KV pool 或 batch token budget 太小 | 提高 memory fraction / token budget |
| RAG 首 token 慢 | 重复 prefill 太多 | 开 prefix cache / RadixAttention |

## 注意事项

- KV cache 低精度不是纯内存优化，也可能影响输出质量。
- `gpu-memory-utilization` 这类参数通常是单实例预算，不会自动感知同卡其他进程。
- 上下文长度、并发和 beam width 会互相乘，不能分开估算。
- Prefix cache 对随机、完全不同 prompt 的收益很低。

## 关键来源

- vLLM PagedAttention: https://docs.vllm.ai/en/stable/design/paged_attention/
- vLLM Automatic Prefix Caching: https://docs.vllm.ai/en/stable/features/automatic_prefix_caching/
- PagedAttention paper: https://arxiv.org/abs/2309.06180
- vLLM APC RFC: https://github.com/vllm-project/vllm/issues/2614
- TensorRT-LLM KV Cache System: https://nvidia.github.io/TensorRT-LLM/features/kvcache.html
- TensorRT-LLM Paged Attention / IFB / Scheduler: https://nvidia.github.io/TensorRT-LLM/features/paged-attention-ifb-scheduler.html
- TGI PagedAttention: https://huggingface.co/docs/text-generation-inference/conceptual/paged_attention
