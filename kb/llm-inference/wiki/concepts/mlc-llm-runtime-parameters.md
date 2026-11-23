---
type: Concept
title: MLC LLM 参数模型
description: MLC LLM 是基于 TVM 的通用 LLM 部署引擎。它把模型转换、量化、编译和运行时 API 串起来，目标是让同一类 LLM 能在
  CUDA、Vulkan、Metal、WebGPU、iOS、Android 等不同平台上以本地方式运行。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# MLC LLM 参数模型

MLC LLM 是基于 TVM 的通用 LLM 部署引擎。它把模型转换、量化、编译和运行时 API 串起来，目标是让同一类 LLM 能在 CUDA、Vulkan、Metal、WebGPU、iOS、Android 等不同平台上以本地方式运行。

## 工作流

| 阶段 | 命令 / API | 作用 |
|---|---|---|
| 转换权重 | `mlc_llm convert_weight` | 把 Hugging Face 权重转换/量化为 MLC 格式 |
| 生成配置 | `mlc_llm gen_config` | 生成 `mlc-chat-config.json`，包含模型、模板、上下文和编译元数据 |
| 编译模型库 | `mlc_llm compile` | 为目标平台生成优化后的模型库 |
| 本地聊天 | `mlc_llm chat` | 交互式 CLI 推理 |
| REST 服务 | `mlc_llm serve` | OpenAI-compatible HTTP API |
| Python 集成 | `MLCEngine` / `AsyncMLCEngine` | 应用内同步/异步调用 |
| 打包 | `mlc_llm package` | iOS/Android/Web 等场景打包模型库和权重 |

MLC 的特点是“编译前参数”和“运行时参数”都很重要。量化、目标平台、tensor parallel、context window 会进入编译/配置产物；服务端的 host/port/CORS/stream 和采样参数则是运行时控制。

## 关键参数

| 类别 | 参数 | 原理与影响 |
|---|---|---|
| 模型来源 | `MODEL`、`HF://...`、本地 MLC 模型目录 | 指向已转换或可 JIT 编译的模型 |
| 模型库 | `--model-lib` | 显式指定编译后的动态库；省去 JIT 或避免加载错误版本 |
| 设备 | `--device` | 选择 cuda、vulkan、metal、webgpu 等后端 |
| 量化 | `--quantization q4f16_1` 等 | 控制权重/激活精度和内存占用 |
| 多 GPU | `--overrides "tensor_parallel_shards=N"` | 多卡 tensor parallel，降低单卡权重压力 |
| 上下文 | `context_window_size`、`sliding_window_size`、`prefill_chunk_size` | 影响 KV cache、长上下文和 prefill 峰值 |
| 服务 | `--host`、`--port`、CORS 参数 | 控制 REST server 暴露边界 |
| tracing | `--enable-tracing` | 诊断运行时性能 |
| speculative | `--speculative-mode` | 推测解码相关模式 |
| 多模型 | `--additional-models` | 同一服务暴露额外模型 |

## 量化命名

MLC 用短代码表示量化模式，例如：

- `q0f16`：不做权重量化，float16。
- `q0f32`：float32。
- `q3f16_1` / `q4f16_1` / `q4f32_1`：weight-only 量化变体。
- `q4f16_awq`：AWQ 相关模式。
- `e4m3_e4m3_f16` / `e5m2_e5m2_f16`：FP8 权重+激活量化模式。

量化不是只影响模型大小：它还决定编译出的 kernel、目标平台是否支持、以及输出质量。移动端/WebGPU 场景通常需要更激进的量化和更短上下文。

## REST / OpenAI-compatible API

`mlc_llm serve MODEL [--model-lib ...]` 启动 REST server，支持 OpenAI-compatible chat/completions 风格请求。请求级参数包括 `messages`、`stream`、`max_tokens`、`temperature`、`top_p`、`stop`、`frequency_penalty`、`presence_penalty` 等。

和 vLLM/TGI 相比，MLC 的价值更多在跨平台和本地编译部署；高并发云端服务仍需实测它的 batching、异步 engine 和 GPU 利用率。

## Python API

`MLCEngine` 对齐 OpenAI Python 客户端风格，适合应用内同步调用。文档特别提示，同步 `MLCEngine` 不会 batch concurrent requests；需要请求批处理时使用 `AsyncMLCEngine`。

## 调参判断

| 症状 | 优先检查 |
|---|---|
| 启动找不到模型库 | `--model-lib` 是否匹配模型、设备和量化配置 |
| 显存不足 | 更低量化、降低 context window、减少 tensor parallel 之外的副本 |
| 首次运行慢 | 是否 JIT compile；生产应预编译模型库 |
| 多 GPU 不生效 | `tensor_parallel_shards` 是否写入 config/overrides，模型库是否按对应并行度编译 |
| Web/mobile 太慢 | 量化模式、context window、设备 backend 和浏览器/WebGPU 支持 |

## 与其他框架的关系

- 与 [llama.cpp](llama-cpp-runtime-parameters.md) 一样，MLC LLM 很适合本地/端侧部署，但它走 TVM 编译路线。
- 与 [ONNX Runtime GenAI](onnxruntime-genai-parameters.md) 一样，MLC 强调跨硬件部署；差别在于 MLC 以 TVM 编译和 MLC 模型格式为中心。
- 与 [vLLM](vllm-engine-parameters.md) 相比，MLC 不是最常见的数据中心高吞吐 serving baseline。

## 关键来源

- MLC LLM introduction: https://llm.mlc.ai/docs/get_started/introduction
- MLC LLM quick start: https://llm.mlc.ai/docs/get_started/quick_start
- MLC LLM REST API: https://llm.mlc.ai/docs/deploy/rest.html
- MLC LLM CLI: https://llm.mlc.ai/docs/deploy/cli.html
- MLC LLM Python API: https://llm.mlc.ai/docs/deploy/python_engine.html
- MLC LLM compile models: https://llm.mlc.ai/docs/compilation/compile_models.html
- MLC LLM configure quantization: https://llm.mlc.ai/docs/compilation/configure_quantization.html
- MLC LLM convert weights: https://llm.mlc.ai/docs/compilation/convert_weights.html
- MLC chat config: https://llm.mlc.ai/docs/deploy/mlc_chat_config.html
