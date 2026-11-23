---
type: Concept
title: Transformers.js 参数模型
description: Transformers.js 是 Hugging Face 面向浏览器和 JavaScript 运行时的模型推理库。它提供类似 Python
  `transformers.pipeline()` 的 API，底层使用 ONNX Runtime 执行模型，可以在浏览器 WASM、WebGPU、Node.js
  等环境中运行。它适合端侧 NLP、视觉、音频和...
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Transformers.js 参数模型

Transformers.js 是 Hugging Face 面向浏览器和 JavaScript 运行时的模型推理库。它提供类似 Python `transformers.pipeline()` 的 API，底层使用 ONNX Runtime 执行模型，可以在浏览器 WASM、WebGPU、Node.js 等环境中运行。它适合端侧 NLP、视觉、音频和轻量生成任务，不是面向多用户 GPU serving 的调度系统。

## 参数面

| 参数面 | 常见字段 / API | 作用 |
|---|---|---|
| Pipeline | `pipeline(task, model, options)`、task id、model id/path | 选择任务、模型和加载选项 |
| 设备 | `device: "wasm"`、`device: "webgpu"`、默认 CPU/WASM | 控制使用 WASM CPU 还是 WebGPU |
| dtype / 量化 | `dtype: "fp32"`、`"fp16"`、`"q8"`、`"q4"` | 降低模型下载体积和内存/带宽 |
| 模型来源 | Hub model id、本地路径、compatible ONNX model | 决定下载哪个 ONNX artifact |
| 缓存 / 环境 | `env`、cache、local model、private/gated model token | 控制模型文件获取和离线/私有模型访问 |
| 加载反馈 | `progress_callback` / loading metadata | 展示模型文件下载和缓存状态 |
| 生成参数 | `max_new_tokens`、`temperature`、`top_p`、`do_sample`、`streamer` | 控制文本生成长度、随机性和 streaming |
| 后端 | ONNX Runtime Web、WASM、WebGPU | 决定真实算子执行路径和兼容性 |

## 原理

Transformers.js 把 PyTorch/TensorFlow/JAX 模型转换成 ONNX 后在 JavaScript 环境中执行。pipeline 负责预处理、模型推理和后处理；ONNX Runtime 负责算子执行。浏览器里默认通常走 WASM CPU，设置 `device: "webgpu"` 后可用 WebGPU 加速。

参数要分三层理解：

- Hugging Face 层：task、model id、revision、tokenizer、processor。
- Transformers.js 层：pipeline、dtype、device、progress callback、streamer。
- ONNX Runtime 层：WASM/WebGPU 能力、浏览器支持、算子覆盖。

## 关键参数

### `task` 和 `model`

`task` 决定 pipeline 类型，例如 text-generation、feature-extraction、automatic-speech-recognition、image-classification 等。`model` 决定具体 Hub repo 或本地模型。不是所有 Python Transformers 模型都能直接跑；需要 Transformers.js / ONNX 兼容 artifact。

### `device`

`device: "webgpu"` 使用 WebGPU。它能显著改善部分模型速度，但 WebGPU 仍受浏览器版本、GPU driver、操作系统和算子支持影响。WASM 更稳，但大模型和生成任务会慢。

### `dtype`

`dtype` 控制加载哪个精度/量化版本。文档列出的典型值包括 WebGPU 默认 `fp32`、WASM 默认 `q8`，以及 `fp16`、`q4` 等。低精度能减少下载体积和内存，但质量、速度和支持矩阵要看模型。

### 生成与 streaming

文本生成仍受 `max_new_tokens`、采样参数和 streamer 控制。浏览器端生成要特别限制最大输出长度，避免长时间占用用户设备和主线程资源。

## 常见误调风险

| 风险 | 表现 | 处理 |
|---|---|---|
| Python 模型直接照搬 | 模型无法加载或缺 ONNX 文件 | 使用带 transformers.js 标签或明确 ONNX artifact 的模型 |
| WebGPU 假定可用 | 部分浏览器/设备失败 | feature detection + WASM fallback |
| dtype 过低 | 分类边界、生成质量、ASR 质量下降 | 对目标任务做 q4/q8/fp16 对比 |
| 模型文件太大 | 首次加载慢，移动端失败 | 选小模型、量化模型、分阶段加载 |
| 缓存策略不清 | 私有模型 token 泄漏或离线不可用 | 区分 public/private、本地 cache 和 token 配置 |
| 生成长度失控 | UI 卡顿、电量消耗大 | 限制 `max_new_tokens` 和并发请求 |

## 适用边界

| 场景 | 建议 |
|---|---|
| 端侧 embedding / classification | 很适合，优先小模型 + q8/q4 |
| 浏览器 ASR / vision demo | 适合，WebGPU 可显著改善体验 |
| 大型 chat LLM | 谨慎，通常 WebLLM/MLC 或服务端 engine 更合适 |
| 企业内网离线 Web 应用 | 可行，但要固定模型文件和缓存策略 |
| 高并发在线服务 | 不适合，浏览器推理不能替代服务端调度 |

## 相关页面

- [CPU、边缘与 NPU 推理](cpu-edge-npu-inference.md)
- [ONNX Runtime Web 参数模型](onnxruntime-web-parameters.md)
- [WebLLM 参数模型](webllm-runtime-parameters.md)
- [Embedding、Reranker 与 Encoder 推理](embedding-and-reranker-inference.md)
- [模型转换、量化与校准流水线](model-conversion-quantization-pipeline.md)

## 关键来源

- Transformers.js docs: https://huggingface.co/docs/transformers.js/index
- Transformers.js pipeline API: https://huggingface.co/docs/transformers.js/api/pipelines
- Transformers.js WebGPU guide: https://huggingface.co/docs/transformers.js/guides/webgpu
- Transformers.js dtype guide: https://huggingface.co/docs/transformers.js/guides/dtypes
- Transformers.js GitHub: https://github.com/huggingface/transformers.js
