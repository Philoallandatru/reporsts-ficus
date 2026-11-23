---
type: Concept
title: 跨框架参数对照表
description: 不同推理框架的参数名经常不一样，但背后控制的是同几类资源：权重显存、KV cache、prefill 计算、decode 调度、请求队列、输出约束和服务边界。这个表不是完整参数字典，而是部署时最常见的“同类旋钮”映射。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 跨框架参数对照表

不同推理框架的参数名经常不一样，但背后控制的是同几类资源：权重显存、KV cache、prefill 计算、decode 调度、请求队列、输出约束和服务边界。这个表不是完整参数字典，而是部署时最常见的“同类旋钮”映射。

## 快速对照

| 调参目标 | vLLM | SGLang | TGI | TensorRT-LLM | llama.cpp / llama-cpp-python | Ollama / LocalAI / Xinference |
|---|---|---|---|---|---|---|
| 模型路径 / 名称 | `--model` | `--model-path` | `--model-id` | `MODEL` / `model` | `--model` / `model_path` | `model` / `model_name` / `name` |
| 上下文长度 | `--max-model-len` | `--context-length` / model config | `--max-total-tokens`、`--max-input-tokens` | max sequence / `max_seq_len` / config | `--ctx-size` / `n_ctx` | `num_ctx` / `context_size` / backend 参数 |
| KV cache 显存比例 | `--gpu-memory-utilization`、KV cache config | `--mem-fraction-static` | `--max-batch-total-tokens` 间接限制 | KV cache fraction / free GPU memory fraction | `--ctx-size`、`--parallel`、cache dtype | backend 参数或模型 options |
| KV cache dtype | `--kv-cache-dtype` | `--kv-cache-dtype` | `--kv-cache-dtype` | KV cache quant / dtype | `--cache-type-k/v`、`type_k/type_v`、`cache_type` | llama.cpp backend 字段、TabbyAPI `cache_mode` |
| Batch token 预算 | `--max-num-batched-tokens` | `--chunked-prefill-size`、batch 相关参数 | `--max-batch-total-tokens`、`--max-batch-prefill-tokens` | max batch / scheduler config | `--batch-size` / `n_batch`、`--ubatch-size` / `n_ubatch` | backend 参数、`XINFERENCE_BATCH_SIZE` |
| 并发请求 / slot | `--max-num-seqs` | `--max-running-requests` | `--max-concurrent-requests` | max batch size / scheduler limits | `--parallel` | `replica`、`request_limits`、`keep_alive`、server queue |
| GPU 并行 | `--tensor-parallel-size`、`--pipeline-parallel-size` | `--tp-size`、`--pp-size`、EP | TP/`--num-shard` / sharding | TP/PP/CP/EP | `--gpu-layers`、`--tensor-split`、`split_mode` | `n_gpu`、`gpu_idx`、backend TP |
| Prefix / prompt cache | automatic prefix caching | RadixAttention / prefix cache / HiCache | prefix caching 支持随版本变化 | KV cache reuse | `--cache-prompt`、server cache | prompt cache / response cache / backend cache |
| Speculative decoding | spec decode config | speculative / draft 参数 | speculation / Medusa / n-gram | Medusa、EAGLE、NGram、Lookahead | draft model 参数 | backend-specific |
| LoRA / adapter | LoRA serving 参数 | LoRA serving 参数 | adapter / LoRA 支持 | LoRA support | `--lora` / adapter loading | `ADAPTER`、model YAML、API load |
| 结构化输出 | guided decoding / structured outputs | constrained decoding | grammar / JSON schema 支持 | guided / parser 生态 | `--grammar`、`--json-schema` | format / grammar / backend support |
| Streaming / timeout | OpenAI stream、server timeout | stream、scheduler timeout | SSE stream、waiting tokens | OpenAI-compatible stream | SSE/server stream | API stream、keepalive、proxy timeout |
| 观测 | `/metrics`、Prometheus | metrics | Prometheus metrics | `/metrics`、telemetry | `--metrics` | metrics/API/logs |

## 读表方式

同一行参数解决同一类问题，但语义不一定等价：

- vLLM 的 `--gpu-memory-utilization` 是 engine 显存预算；llama.cpp 的 `--gpu-layers` 是权重 offload 数。
- TGI 的 `--max-total-tokens` 同时约束单请求输入和输出；llama.cpp 的 `--ctx-size` 是 slot 的上下文窗口。
- `replica` 是多进程/多实例复制；`tensor_parallel` 是一个模型跨多卡切分；两者都会用多 GPU，但目标完全不同。
- OpenAI-compatible 的 `stream=true` 只说明 HTTP 输出形式，不说明服务端是否支持 cancel、drain、backpressure 或部分重试。

## 参数同义词

| 概念 | 常见名称 | 实际控制 |
|---|---|---|
| 上下文窗口 | `max_model_len`、`ctx-size`、`n_ctx`、`num_ctx`、`session_len`、`max_total_tokens` | 单请求或单会话能看多少 token，以及 KV cache 上限 |
| 最大新 token | `max_tokens`、`max_new_tokens`、`num_predict`、`max_completion_tokens` | decode 阶段最多生成多少 token |
| Prompt batch | `batch_size`、`n_batch`、`max_num_batched_tokens`、`max_batch_prefill_tokens` | prefill 一次处理多少 token |
| 并发序列 | `max_num_seqs`、`max_running_requests`、`parallel`、`replica`、`max_concurrent_requests` | 同时存在多少活跃请求或模型副本 |
| 显存占比 | `gpu_memory_utilization`、`mem_fraction_static`、`cache_max_entry_count`、KV cache fraction | engine 为 KV/cache/workspace 保留多少显存 |
| GPU offload | `gpu_layers`、`n_gpu_layers`、`ngl`、`device_map`、`tensor_split` | 哪些权重或 tensor 在 GPU 上执行 |
| 副本 | `replica`、`num_replicas`、`deployment replicas`、`min/max replicas` | 同一模型实例复制多少份，用于并发、可用性和扩缩容 |
| 量化 | `quantization`、`quantize`、`dtype`、`compute_type`、`cache_type` | 权重、激活或 KV cache 的数值格式 |
| 模板 | `chat_template`、`chat_format`、`template`、`tokenizer_mode` | messages 到 token 序列的渲染方式 |
| 随机性 | `temperature`、`top_p`、`top_k`、`min_p`、`seed` | 采样分布和复现性 |

## 常见迁移陷阱

| 从 | 到 | 容易错的点 |
|---|---|---|
| llama.cpp | vLLM | `--ctx-size` 不能机械换成 `--max-model-len`；还要看 `--max-num-seqs` 和 KV cache budget |
| vLLM | SGLang | 两者都有高吞吐调度，但 prefix cache、chunked prefill、结构化输出的实现和默认值不同 |
| TGI | vLLM | TGI router 的请求限制参数不等同于 vLLM engine 的 batch token 和 sequence 上限 |
| Ollama | llama.cpp | Ollama 的 `num_ctx` / Modelfile 是包装层；底层 GGUF 能力、KV dtype、GPU offload 仍要另查 |
| Xinference | backend engine | Xinference 的 `replica` / `n_gpu` 是平台放置参数；vLLM/SGLang TP 仍在 backend 层 |
| OpenAI API | 自托管兼容 API | endpoint 名一样，不代表 tool calling、usage、error、stream chunk 完全一样 |

## 排查顺序

1. 先判断你在调哪一层：API 网关、平台包装层、engine、kernel，还是请求采样。
2. 找到问题对应资源：显存、CPU、队列、网络、磁盘冷启动、模板/输出语义。
3. 用本页把“同类参数”定位到具体框架页，再查官方参数名。
4. 每次只改一类预算，例如先改上下文/KV，再改 batch，再改并发。
5. 把最终运行参数落到配置文件或启动日志，避免环境变量和 CLI 覆盖导致不可复现。

## 相关页面

- [推理参数分类总览](inference-parameter-taxonomy.md)
- [推理调参决策手册](inference-tuning-playbook.md)
- [KV cache 与 PagedAttention](kv-cache-and-paged-attention.md)
- [Continuous batching 与推理调度](continuous-batching-and-scheduling.md)
- [OpenAI-compatible API 语义与兼容边界](openai-compatible-api-semantics.md)
- [模型生命周期、热切换与保活](model-lifecycle-hot-swap-and-keepalive.md)

## 关键来源

- vLLM Engine Args: https://docs.vllm.ai/en/stable/configuration/engine_args/
- SGLang server arguments: https://docs.sglang.io/docs/advanced_features/server_arguments
- Hugging Face TGI launcher: https://huggingface.co/docs/text-generation-inference/reference/launcher
- TensorRT-LLM `trtllm-serve`: https://nvidia.github.io/TensorRT-LLM/commands/trtllm-serve/trtllm-serve.html
- llama.cpp server README: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- llama-cpp-python server docs: https://llama-cpp-python.readthedocs.io/en/latest/server/
- llama-cpp-python API reference: https://llama-cpp-python.readthedocs.io/en/latest/api-reference/
- Ollama Modelfile: https://docs.ollama.com/modelfile
- LocalAI model configuration: https://localai.io/docs/advanced/model-configuration/
- Xinference model launching: https://inference.readthedocs.io/en/latest/user_guide/launch.html
