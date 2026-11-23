---
type: Concept
title: LocalAI 参数模型
description: LocalAI 是本地/自托管的 OpenAI-compatible API server。它把多个后端封装在统一 API 后面，可以服务文本生成、embedding、音频、图像等任务。和
  vLLM 这类单一高吞吐 LLM engine 不同，LocalAI 的关键在于“模型配置 + backend 选择 + OpenAI-compatible API...
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# LocalAI 参数模型

LocalAI 是本地/自托管的 OpenAI-compatible API server。它把多个后端封装在统一 API 后面，可以服务文本生成、embedding、音频、图像等任务。和 vLLM 这类单一高吞吐 LLM engine 不同，LocalAI 的关键在于“模型配置 + backend 选择 + OpenAI-compatible API 兼容层”。

## 参数面

| 参数面 | 常见字段 / 配置 | 作用 |
|---|---|---|
| 模型配置 | `name`、`backend`、`parameters`、`context_size`、`threads`、`f16`、`mmap`、`gpu_layers` | 定义一个模型服务入口如何加载和运行 |
| 请求参数 | OpenAI-compatible `messages`、`prompt`、`temperature`、`top_p`、`top_k`、`max_tokens`、`stream`、penalty、`logit_bias` | 兼容常见客户端和 SDK |
| Backend | llama.cpp、transformers、diffusers、whisper 等后端 | 决定真实推理引擎和支持的参数集合 |
| 模板 / 结构化输出 | `template.chat`、`template.chat_message`、`template.completion`、`template.use_tokenizer_template`、grammar / JSON schema | 控制 chat 格式和语法约束 |
| Embedding / rerank | `pooling_type`、`embd_normalize`、embedding model 配置、tokenizer、pooling 路径 | 用同一 API server 提供向量能力 |
| 运行环境 | 模型目录、预加载、并发、日志、API key、CORS | 控制服务生命周期和访问边界 |

LocalAI 的模型配置通常放在模型目录中的 YAML 文件里。请求里的 OpenAI-compatible 字段会被 LocalAI 翻译到具体 backend；如果 backend 不支持某个字段，该字段可能被忽略或语义不同。

## Backend 不是细节

LocalAI 的 `backend` 决定很多参数是否生效：

- llama.cpp backend 更关注 GGUF、`context_size`、线程、GPU layers、grammar。
- Transformers 类 backend 更关注 HF 模型、dtype、device、tokenizer 和 generation config。
- Audio/image 后端的参数面和 LLM 生成完全不同。

因此 LocalAI 的调参流程应先确认 backend，再套具体框架页的知识。不要把 vLLM 的 batch/KV 参数直接套到 LocalAI 的 llama.cpp backend 上。

## 高风险字段

| 字段 | 含义 | 风险 |
|---|---|---|
| `context_size` | 上下文窗口；`-1` 可尝试从 GGUF metadata 使用模型训练上下文 | 可能绕过显存保护，直接 OOM |
| `threads` | 覆盖服务级 CPU thread 设置 | 过高会抢占 tokenizer、HTTP 和其他模型线程 |
| `batch` | 控制处理 batch | 太大提高峰值内存，太小吞吐差 |
| `gpu_layers` / `tensor_split` / `main_gpu` | 控制 llama.cpp 类 backend 的 GPU offload | 错配设备会慢或 OOM |
| `cache_type_k` / `cache_type_v` | KV cache dtype/量化 | 省内存但可能影响质量或兼容性 |
| `template.*` | chat/completion 模板 | 模板错会让角色、tool、system prompt 失效 |
| `known_usecases` | 声明模型用途，如 embeddings | 配错会让模型暴露错误 endpoint |

## 常见调参路径

| 症状 | 优先检查 |
|---|---|
| 输出慢 | backend 是否走目标硬件、`threads`、GPU offload、上下文长度、模型量化 |
| 首 token 慢 | 模型是否预加载、权重是否每次冷加载、prompt/context 是否过长 |
| OOM | `context_size`、batch、GPU layers、模型量化、backend dtype |
| OpenAI 客户端行为不一致 | chat template、stop/eos、stream chunk、usage、tool/JSON 字段兼容性 |
| JSON 不稳定 | grammar/schema 是否真的启用，backend 是否支持对应约束 |

## 与高吞吐 serving 的差别

LocalAI 适合本地开发、边缘部署、多能力统一 API 和轻量自托管。它不一定提供 vLLM/SGLang/TGI 那种以 continuous batching、PagedAttention 和 engine-level queue 为核心的高吞吐调度模型。

如果目标是单机/多机高并发聊天服务，应把 LocalAI 放在“兼容层/聚合层”的位置评估；如果瓶颈在底层 LLM decode，则应回到具体 backend 的参数。

## 常见误区

- 只看 OpenAI-compatible API 成功：API 兼容不代表 tokenizer、template、采样默认值一致。
- 混淆模型名和 backend：同一个 `name` 可以指向完全不同的后端和模型 artifact。
- 盲目增大上下文：`context_size` 同时增加 KV cache 和延迟压力。
- 忽略模型目录和预加载：冷启动会被误判成推理慢。

## 相关页面

- [llama.cpp 参数模型](llama-cpp-runtime-parameters.md)
- [OpenAI-compatible API 语义与兼容边界](openai-compatible-api-semantics.md)
- [模型 Artifact 分发、缓存与冷启动](model-artifact-distribution-and-cold-start.md)
- [Logits Processor、惩罚项与长度控制](logits-processors-penalties-and-length-control.md)

## 关键来源

- LocalAI documentation: https://localai.io/
- LocalAI quickstart: https://localai.io/docs/basics/getting_started/
- LocalAI text generation: https://localai.io/docs/features/text-generation/
- LocalAI model configuration: https://localai.io/docs/advanced/model-configuration/
- LocalAI model compatibility: https://localai.io/docs/model-compatibility/
- LocalAI advanced usage: https://localai.io/docs/advanced/
- LocalAI GitHub: https://github.com/mudler/LocalAI
