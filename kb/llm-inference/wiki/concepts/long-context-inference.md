---
type: Concept
title: 长上下文推理
description: 长上下文推理不是简单把 `max_model_len` 拉大。它会同时放大 KV cache、prefill 时间、attention kernel
  压力、调度尾延迟和多 GPU 通信。正确做法是同时处理位置编码、KV cache、调度、attention backend 和 admission control。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 长上下文推理

长上下文推理不是简单把 `max_model_len` 拉大。它会同时放大 KV cache、prefill 时间、attention kernel 压力、调度尾延迟和多 GPU 通信。正确做法是同时处理位置编码、KV cache、调度、attention backend 和 admission control。

## 长上下文的成本

| 成本 | 为什么上升 |
|---|---|
| KV cache | 与上下文 token 数线性相关 |
| Prefill 时间 | prompt 越长，一次 prefill 计算越重 |
| Attention 带宽 | decode 每步要读更多历史 KV |
| 调度尾延迟 | 长 prompt 会占用 prefill 资源 |
| 多 GPU 通信 | context parallel / disaggregation 需要跨卡传输 |

## RoPE scaling 与 YaRN

RoPE 模型的位置编码有训练时上下文范围。RoPE scaling、YaRN 等方法试图把位置频率映射扩展到更长上下文。它们能让模型“跑”更长输入，但不是无损扩容：长距离检索、顺序敏感任务和格式稳定性仍需实测。

Hugging Face Transformers 把 RoPE 类型整理为 `default`、`linear`、`dynamic`、`yarn`、`longrope`、`llama3` 等，并通过 `rope_parameters` 配置。vLLM 新版 context extension 更推荐通过 `--hf-overrides '{"rope_parameters": ...}'` 传入模型配置，而不是只依赖旧式 `--rope-scaling` 参数。

Qwen 文档提醒过一个很实用的坑：静态 YaRN 可能影响短文本性能，只有确实需要长上下文时才应启用，并按目标上下文长度设置 factor。

## Sliding window attention

Sliding window attention 让模型只关注最近窗口内的 token，降低远距离 KV 读取压力。它适合模型原生支持 SWA 的架构，但对需要全局证据的 RAG、长文档问答并不总是合适。

## Chunked context / chunked prefill

长 prompt 的 prefill 峰值高，容易拖慢其他 decode 请求。Chunked prefill 把长 prompt 切块调度，降低峰值和排队影响。

TensorRT-LLM 还区分 chunked context 和 chunked attention：前者是调度层把输入分块并与 decode 混合；后者是在 attention layer 内限制 token 只关注同 chunk 历史，会改变注意力可见范围。

## KV eviction 与 cache reuse

长上下文服务需要决定“哪些 KV 值保留，哪些丢弃或迁移”：

- Prefix cache：保留高复用的公共前缀。
- KV eviction：在 cache 满时驱逐低价值 block。
- KV offload：把暂时不用的 cache 移到 CPU/其他存储层。
- Context shift/sliding window：丢弃旧 token，仅保留窗口。

TensorRT-LLM 的 KV cache system 使用 block pool，并支持 prioritized LRU；启用 host offload 后，GPU block 在驱逐前可复制到 CPU host memory，后续命中再搬回 GPU。vLLM 的 `--watermark` 则是 admission headroom：保留一部分 KV block，避免接近满载时频繁 eviction/preemption。

## Context parallel

Context parallel 把长序列维度分到多 GPU，缓解单卡 KV/attention 压力。它适合非常长的上下文，但代价是跨卡 attention/KV 通信。NVLink/NVSwitch 环境比普通 PCIe 更适合。

## 关联参数

| 框架 | 参数 | 说明 |
|---|---|---|
| vLLM | `--hf-overrides '{"rope_parameters": ...}'` | 通过 HF config 覆盖 RoPE / YaRN 等上下文扩展设置 |
| vLLM | `--max-model-len` | 服务最大上下文窗口 |
| vLLM | `--enable-chunked-prefill` | 允许 prefill request 被切块调度 |
| vLLM | `--scheduler-reserve-full-isl` | admission 时按完整输入长度预留 KV，避免 chunked prefill 过量接入 |
| vLLM | `--disable-hybrid-kv-cache-manager` | full attention 与 sliding window 混合模型的 KV cache 管理相关 |
| SGLang | `--context-length` | 最大上下文长度 |
| SGLang | `--json-model-override-args '{"rope_scaling": ...}'` | 部分模型部署时注入 YaRN / RoPE scaling |
| SGLang | `--chunked-prefill-size`、`--enable-dynamic-chunking` | prefill 分块大小和动态分块 |
| TensorRT-LLM | `enable_chunked_prefill` | 开启 chunked context |
| TensorRT-LLM | `kv_cache_config.max_attention_window` | 每层 attention window size |

## 调参建议

- 先估 KV cache，再调上下文长度。
- 长 prompt OOM：优先 chunked prefill / microbatch / KV dtype，而不是只换更大 GPU。
- 长上下文质量差：检查 RoPE scaling 是否与模型推荐一致。
- RAG 场景：优先 prefix cache 和 prompt 压缩，不要盲目扩大窗口。
- 超长上下文生产：同时评估 context parallel、KV offload、disaggregated prefill。

## 关键来源

- RoPE paper: https://arxiv.org/abs/2104.09864
- YaRN paper: https://arxiv.org/abs/2309.00071
- Hugging Face RoPE utilities: https://huggingface.co/docs/transformers/en/internal/rope_utils
- vLLM Context Extension: https://docs.vllm.ai/en/latest/features/context_extension/
- Qwen SGLang deployment docs: https://qwen.readthedocs.io/en/latest/deployment/sglang.html
- vLLM Optimization: https://docs.vllm.ai/en/stable/configuration/optimization/
- TensorRT-LLM Long Sequence: https://nvidia.github.io/TensorRT-LLM/features/long-sequence.html
- TensorRT-LLM KV Cache System: https://nvidia.github.io/TensorRT-LLM/features/kvcache.html
- TensorRT-LLM KV Cache Reuse: https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html
- SGLang Hyperparameter Tuning: https://docs.sglang.io/docs/advanced_features/hyperparameter_tuning
