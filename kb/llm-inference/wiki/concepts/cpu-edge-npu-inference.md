---
type: Concept
title: CPU、边缘与 NPU 推理
description: 不是所有 LLM 推理都发生在数据中心 GPU 上。CPU、Apple silicon、Intel GPU/NPU、Qualcomm NPU、WebGPU
  和本地端侧场景有不同的约束：内存带宽、启动时间、模型大小、功耗、离线可用性、隐私和平台 SDK。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# CPU、边缘与 NPU 推理

不是所有 LLM 推理都发生在数据中心 GPU 上。CPU、Apple silicon、Intel GPU/NPU、Qualcomm NPU、WebGPU 和本地端侧场景有不同的约束：内存带宽、启动时间、模型大小、功耗、离线可用性、隐私和平台 SDK。

## 典型路径

| 路径 | 代表 | 适合场景 |
|---|---|---|
| CPU / BLAS | llama.cpp、CTranslate2、ONNX Runtime CPU EP | 无 GPU、批量小、部署简单 |
| Apple silicon | MLX LM、llama.cpp Metal、MLC Metal | Mac/iOS 本地应用、统一内存 |
| Intel CPU/GPU/NPU | OpenVINO GenAI、ONNX Runtime OpenVINO EP | 企业 CPU/GPU/NPU、边缘设备 |
| Qualcomm / Android NPU | ONNX Runtime QNN EP、厂商 SDK | 移动端、低功耗离线推理 |
| WebGPU / Browser | WebLLM、Transformers.js、ONNX Runtime Web、MLC LLM WebGPU | 浏览器内推理、隐私演示、离线 PWA |

## CPU 推理关注点

CPU 推理通常受内存带宽和矩阵乘法库影响：

- 权重量化比 GPU 上更关键，因为它减少内存读取。
- 线程数不是越大越好，过高会造成 NUMA/缓存竞争。
- batch 小时延迟可控，batch 大时吞吐提升有限。
- AVX2/AVX512/AMX 等指令集差异很大。

典型参数：

| 参数族 | 典型名字 |
|---|---|
| 线程 | `--threads`、`intra_threads`、`inter_threads` |
| batch | `--batch-size`、`max_batch_size` |
| 量化 | GGUF quant、CTranslate2 `compute_type`、ONNX int8/int4 |
| 内存 | mmap/mlock、NUMA、KV cache dtype |

## NPU / 专用加速器

NPU 路径通常需要模型转换、静态 shape 或算子覆盖检查。ONNX Runtime 的 QNN Execution Provider 面向 Qualcomm AI Engine Direct SDK，OpenVINO 面向 Intel 设备，二者都强调“哪些子图能跑在目标 EP/设备上”。

OpenVINO 的 NPU 路径适合低功耗 AI PC/边缘设备；ONNX Runtime 的 OpenVINO EP 和 QNN EP 则分别面向 Intel backend 和 Qualcomm backend。两类路线都要确认 provider assignment：模型能运行不代表关键算子已经下沉到 NPU。

调参重点：

- 模型是否可转换到目标 IR/ONNX 格式。
- 算子是否被 EP 支持，有没有 fallback 到 CPU。
- 量化格式和校准是否符合 NPU 要求。
- 上下文长度和 KV cache 是否在设备内存范围内。
- 首次编译/加载是否需要缓存。

## 端侧部署取舍

| 目标 | 常见选择 |
|---|---|
| 最小内存 | 更小模型、4-bit 权重量化、短上下文 |
| 最低功耗 | NPU/专用 EP，降低输出长度和并发 |
| 离线隐私 | 本地模型、禁用远端 telemetry、固定模型版本 |
| 最快首 token | 预加载模型、prompt cache、减少 system prompt |
| 跨平台 | ONNX Runtime、MLC LLM、llama.cpp |

## 浏览器 / WebGPU

浏览器推理的瓶颈和服务端不同：

- 模型下载体积和缓存命中会支配首次体验。
- WebGPU 可用性依赖浏览器、操作系统和 GPU driver。
- WASM 覆盖更广，但大模型生成速度通常有限。
- IndexedDB、Cache API、Service Worker 会影响模型生命周期。
- 长上下文会占用浏览器进程内 GPU/系统内存，容易触发页面回收。

WebLLM 更像“浏览器内 LLM engine”；Transformers.js 更像“浏览器/Node 的 HF pipeline”；ONNX Runtime Web 是底层 ONNX 执行引擎。调参时先判断自己在哪一层。

## 常见误区

- 把 GPU serving 参数直接套到 CPU/NPU。CPU 的线程和内存带宽更关键。
- 只验证模型能运行，不检查 EP fallback。跑起来不代表跑在 NPU/GPU 上。
- 移动端拉太长上下文，KV cache 把内存吃光。
- 没有固定模型转换版本，导致性能回归难以复现。
- 只在开发机 Chrome 上验证 WebGPU，不做浏览器/设备矩阵。
- 把模型缓存命中误认为模型已经 warm；页面生命周期变化仍可能重新初始化。

## 与其他页面的关系

- [OpenVINO GenAI 参数模型](openvino-genai-parameters.md)：Intel 设备路径。
- [ONNX Runtime GenAI 参数模型](onnxruntime-genai-parameters.md)：ONNX 与多 EP 路径。
- [ONNX Runtime Web 参数模型](onnxruntime-web-parameters.md)：浏览器 WASM/WebGPU/WebNN 路径。
- [MLC LLM 参数模型](mlc-llm-runtime-parameters.md)：跨平台编译部署。
- [WebLLM 参数模型](webllm-runtime-parameters.md)：浏览器内 LLM / MLC WebGPU 路径。
- [Transformers.js 参数模型](transformers-js-runtime-parameters.md)：浏览器/Node 的 HF pipeline 路径。
- [llama.cpp 参数模型](llama-cpp-runtime-parameters.md)：CPU/GPU/Metal/Vulkan 本地推理。

## 关键来源

- ONNX Runtime Execution Providers: https://onnxruntime.ai/docs/execution-providers/
- ONNX Runtime QNN Execution Provider: https://onnxruntime.ai/docs/execution-providers/QNN-ExecutionProvider.html
- ONNX Runtime OpenVINO Execution Provider: https://onnxruntime.ai/docs/execution-providers/OpenVINO-ExecutionProvider.html
- ONNX Runtime graph optimizations: https://onnxruntime.ai/docs/performance/model-optimizations/graph-optimizations.html
- OpenVINO model preparation: https://docs.openvino.ai/2025/openvino-workflow/model-preparation.html
- OpenVINO NPU device: https://docs.openvino.ai/2025/openvino-workflow/running-inference/inference-devices-and-modes/npu-device.html
- OpenVINO optimize inference: https://docs.openvino.ai/2025/openvino-workflow/running-inference/optimize-inference.html
- llama.cpp build documentation: https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md
- Apple MLX documentation: https://ml-explore.github.io/mlx/build/html/index.html
- MLC LLM introduction: https://llm.mlc.ai/docs/get_started/introduction
- WebLLM documentation: https://webllm.mlc.ai/docs/
- Transformers.js docs: https://huggingface.co/docs/transformers.js/index
- ONNX Runtime Web tutorial: https://onnxruntime.ai/docs/tutorials/web/
