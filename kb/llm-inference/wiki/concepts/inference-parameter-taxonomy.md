---
type: Concept
title: 推理参数分类总览
description: LLM 推理框架的参数虽然名字不同，本质上都在控制同一组资源：模型权重放在哪里，KV cache 能装多少 token，请求如何进入 batch，decode
  每步如何采样，以及服务如何暴露给客户端。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 推理参数分类总览

LLM 推理框架的参数虽然名字不同，本质上都在控制同一组资源：模型权重放在哪里，KV cache 能装多少 token，请求如何进入 batch，decode 每步如何采样，以及服务如何暴露给客户端。

## 1. 模型加载参数

常见名字：`model`、`model-path`、`model-id`、`revision`、`tokenizer`、`trust-remote-code`、`load-format`、`model-format`、`backend`、`dtype`。

原理：模型加载阶段决定权重文件格式、tokenizer、模型代码来源和权重数据类型。`revision` 锁定 Hugging Face commit/branch/tag，能减少“今天能跑、明天拉到新代码就变了”的风险。`trust-remote-code` 会执行模型仓库中的自定义 Python 代码，适合需要自定义 architecture 的模型，但生产环境应配合固定 revision。

调参影响：

- `dtype=bf16/fp16/fp32` 影响显存、吞吐和数值范围。
- `load-format=gguf/safetensors/gptq/awq/...` 决定能否使用框架特定 kernel。
- `tokenizer` 与 `chat_template` 错配会导致输出格式异常，比性能问题更隐蔽。

## 2. 上下文与 KV cache 参数

常见名字：`ctx-size`、`max-model-len`、`session-len`、`num_ctx`、`max-total-tokens`、`block-size`、`cache-type-k`、`cache-type-v`、`kv-cache-dtype`、`gpu-memory-utilization`、`mem-fraction-static`、`cache-max-entry-count`、`kv_cache_free_gpu_memory_fraction`。

原理：Transformer decode 时每生成一个 token，都要复用之前 token 的 key/value。KV cache 的大小近似正比于：

```text
layers * context_tokens * kv_heads * head_dim * 2(K,V) * dtype_bytes * concurrent_sequences
```

因此上下文长度和并发数不是免费参数。把上下文从 8K 拉到 64K，KV cache 可能线性增大 8 倍；把并发 slot 从 1 拉到 8，也会继续乘上去。

调参影响：

- 提高上下文长度：能支持长 prompt，但显存下降、可并发请求数下降。
- 降低 KV cache dtype：节省显存，提高可并发 token 数，但可能带来精度损失。
- 提高 KV cache 内存占比：吞吐上升，OOM 风险也上升，因为 activation、CUDA graph 和通信 buffer 的空间被压缩。

延伸阅读：[KV cache 与 PagedAttention](kv-cache-and-paged-attention.md)。

## 3. Batch、调度与并发参数

常见名字：`max-running-requests`、`max-concurrent-requests`、`max-batch-size`、`max-num-batched-tokens`、`max-batch-total-tokens`、`max-batch-prefill-tokens`、`waiting-served-ratio`、`max-waiting-tokens`、`parallel`、`cont-batching`、`chunked-prefill-size`。

原理：LLM 服务端通常把请求拆成 prefill 和 decode。Prefill 处理整段 prompt，计算密集；decode 每步生成一个 token，容易受内存带宽、调度和小 batch 开销影响。Continuous batching / in-flight batching 的目标是让新请求能插入正在运行的 decode 循环，而不是等整批请求全部结束。

调参影响：

- `max-batch-*` 过低：吞吐受限，GPU 吃不满。
- `max-batch-*` 过高：首 token 延迟和尾延迟变差，且更容易 OOM。
- `chunked-prefill-size` 变小：长 prompt 更不容易 OOM，但 prefill 更慢。
- `max-running-requests` 变小：decode OOM 风险下降，但峰值吞吐下降。

延伸阅读：[Continuous batching 与推理调度](continuous-batching-and-scheduling.md)。

## 4. 并行与设备参数

常见名字：`tensor-parallel-size` / `tp`、`pipeline-parallel-size` / `pp`、`data-parallel-size` / `dp`、`expert-parallel-size` / `ep`、`gpu-layers`、`split-mode`、`tensor-split`、`device`、`main-gpu`、`num-shard`。

原理：

- Tensor parallel 把单层矩阵切到多 GPU，适合单卡装不下或单层计算很重的模型。
- Pipeline parallel 按层切分，容易有流水线气泡，适合超大模型。
- Data parallel 复制模型，适合提升总吞吐，通常需要外部或内部路由。
- Expert parallel 针对 MoE，把专家分散到多个设备。
- llama.cpp 的 `gpu-layers` 是本地推理特色：把前 N 层或全部层 offload 到 GPU。

## 5. 量化参数

常见名字：`quantization`、`quantize`、`model-format`、`dtype`、`kv-cache-dtype`、`cache-type-k/v`、`quant_policy`。

原理：权重量化压缩模型权重，KV cache 量化压缩历史状态。权重量化影响每次 matmul；KV cache 量化主要影响长上下文和高并发场景。

调参影响：

- 权重量化通常直接降低显存，使更大模型能装入单机。
- 4-bit 权重量化不一定比 fp16 更快，取决于 kernel 是否成熟、是否需要反量化。
- KV cache fp8/int8/q4 能扩大上下文或并发，但输出质量和稳定性需要用真实任务回归验证。

延伸阅读：[推理量化：权重、激活与 KV cache](inference-quantization.md)。

## 6. 采样参数

常见名字：`temperature`、`top_k`、`top_p`、`min_p`、`typical_p`、`repeat_penalty`、`presence_penalty`、`frequency_penalty`、`seed`、`stop`、`max_tokens`、`num_predict`、`grammar`、`json_schema`。

原理：模型每步输出 logits，采样参数决定如何把 logits 变成下一个 token。`temperature` 改变概率分布尖锐程度；`top_k` 限制候选 token 数；`top_p` 选择累计概率达到阈值的候选集合；`min_p` 用相对最高概率过滤低概率 token；重复惩罚会降低最近出现 token 的概率。

调参影响：

- 低温度 + 小候选集合：更稳定，适合代码、摘要、抽取。
- 高温度 + 大候选集合：更多样，适合创作，但幻觉和格式漂移增加。
- 结构化输出优先用 grammar / JSON schema，而不是只靠 prompt。

延伸阅读：[采样与结构化输出](sampling-and-structured-output.md)。

## 7. 推测解码参数

常见名字：`speculate`、`draft_model`、`num_assistant_tokens`、`draft_num_predict`、`speculative-*`。

原理：小 draft model 先猜多个 token，大 model 一次验证。猜对越多，主模型 forward 次数越少；猜错越多，收益越低。n-gram speculation 不需要额外模型，但只对重复性强的任务明显。

调参影响：

- draft 模型太弱：接受率低，收益小。
- draft token 数太大：验证浪费增加。
- 对代码补全、模板化输出、重复上下文，收益通常更明显。

延伸阅读：[Speculative decoding](speculative-decoding.md)。

## 8. 服务/API 参数

常见名字：`host`、`port`、`api-key`、`cors`、`metrics`、`prometheus-port`、`max-queued-requests`、`payload-limit`、`ssl-*`、`allowed-media-domains`。

原理：这些参数不改变模型数学，但决定安全边界、可观测性、背压和客户端兼容性。生产环境中，拒绝过载请求通常比无限排队更健康。

## 关键来源

- llama.cpp server README: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- vLLM Engine Arguments: https://docs.vllm.ai/en/stable/configuration/engine_args/
- SGLang Server Arguments: https://docs.sglang.io/docs/advanced_features/server_arguments
- TGI launcher arguments: https://huggingface.co/docs/text-generation-inference/reference/launcher
- TensorRT-LLM `trtllm-serve`: https://nvidia.github.io/TensorRT-LLM/commands/trtllm-serve/trtllm-serve.html
