---
type: Concept
title: ONNX Runtime Web 参数模型
description: ONNX Runtime Web 是在浏览器和 Web 前端运行 ONNX 模型的 JavaScript runtime。它提供 `onnxruntime-web`
  包、`InferenceSession`、Tensor API、WASM/WebGPU/WebNN execution providers、session options
  和环境 flag...
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# ONNX Runtime Web 参数模型

ONNX Runtime Web 是在浏览器和 Web 前端运行 ONNX 模型的 JavaScript runtime。它提供 `onnxruntime-web` 包、`InferenceSession`、Tensor API、WASM/WebGPU/WebNN execution providers、session options 和环境 flags。很多上层库，包括 Transformers.js，会把模型执行交给 ONNX Runtime Web。

## 参数面

| 参数面 | 常见字段 / API | 作用 |
|---|---|---|
| Session 创建 | `ort.InferenceSession.create(modelPath, options)` | 加载 ONNX/ORT 模型并配置执行 |
| Execution Provider | `executionProviders: ["wasm"]`、`["webgpu"]`、`["webnn"]` | 选择 CPU/WASM、GPU/WebGPU 或 WebNN 后端 |
| SessionOptions | `graphOptimizationLevel`、`freeDimensionOverrides`、`preferredOutputLocation` | 控制图优化、动态 shape 和输出位置 |
| WASM flags | `ort.env.wasm.numThreads`、SIMD、proxy、wasm path | 控制 CPU 执行、线程和资源加载 |
| WebGPU flags | `ort.env.webgpu.*`、Graph Capture、GPU tensor | 控制 WebGPU 设备、graph capture 和 GPU 数据驻留 |
| WebNN options | `deviceType`、`powerPreference`、`context` | 选择 WebNN CPU/GPU/NPU 和电源偏好 |
| Tensor / IO | `new ort.Tensor(...)`、`Tensor.fromGpuBuffer()`、`Tensor.fromMLTensor()`、feeds/fetches | 管理输入输出数据和是否留在设备内存 |
| 模型优化 | ONNX -> ORT format、graph optimization、quantization、custom build | 降低初始化时间、包体积和运行时内存 |

## 原理

ONNX Runtime Web 的核心是把 ONNX graph 放进浏览器执行。WASM EP 覆盖最稳，WebGPU/WebNN 更快但算子支持和浏览器支持有限。对于 transformer 类模型，反复调用 session 时，如果每步都把 tensor 在 CPU 和 GPU 之间复制，开销会吃掉加速收益；IO binding / GPU tensor 的价值就在这里。

## Execution Provider 选择

| EP | 适合 | 风险 |
|---|---|---|
| WASM | 最广浏览器覆盖、小模型、稳定 fallback | 大模型和生成任务慢，线程受浏览器隔离策略影响 |
| WebGPU | 计算密集模型、视觉/语音/Transformer 加速 | 浏览器/OS/GPU 支持不一，部分算子可能不支持 |
| WebNN | 希望使用本机 CPU/GPU/NPU 抽象 | 仍在发展，常需要浏览器 flag，算子覆盖要核对 |
| WebGL | 旧兼容路径 | 文档中 WebGL 已偏维护模式，优先 WebGPU |

## 关键参数

### `executionProviders`

这是最重要的运行时参数。它决定模型优先在哪个 EP 上执行。模型能跑不代表算子都在目标 EP 上；如果关键算子 fallback 到 WASM，性能可能和预期完全不同。

### `graphOptimizationLevel`

图优化可以折叠常量、融合算子、减少运行时开销。浏览器端模型更关注初始化时间和包体积；部署前应预先优化或转换成 ORT format，而不是把所有优化都留给用户设备。

### `freeDimensionOverrides`

动态 shape 模型在浏览器中容易导致分配和编译开销。对输入分辨率、sequence length、batch 等 free dimension 做覆盖，可以让 runtime 更容易优化，也能避免意外的大 shape。

### WASM 线程和 SIMD

WASM EP 的性能受 `numThreads`、SIMD 和浏览器跨域隔离限制影响。线程越多不一定越快；移动设备和低功耗笔记本上，线程过多会带来热降频和 UI 卡顿。

### WebGPU IO binding

WebGPU EP 支持把数据保留在 GPU buffer 中。对多步 transformer 或后续 GPU 后处理很有用；但 GPU tensor 生命周期需要手动管理，忘记 dispose 或销毁 buffer 会造成内存泄漏或运行失败。

## 常见误调风险

| 风险 | 表现 | 处理 |
|---|---|---|
| 只指定 WebGPU，不验证算子覆盖 | 性能没有提升或运行失败 | 用 profiling / 日志确认 EP assignment |
| 大模型直接放浏览器 | 下载慢、内存爆、页面崩溃 | 预优化、量化、切小模型或改服务端 |
| 动态 shape 不受控 | 每种输入尺寸都重新分配或编译 | 用 `freeDimensionOverrides` 固定关键维度 |
| GPU tensor 未释放 | 多次推理后显存/内存增长 | 明确 `dispose()` / buffer 生命周期 |
| WASM 多线程未生效 | CPU 利用率低 | 检查 cross-origin isolation、浏览器限制和 `numThreads` |
| WebNN 过早依赖 | 用户设备支持不足 | 做 feature detection 和 EP fallback |

## 调参路径

1. 先用 WASM 跑通，确认 ONNX 输入输出、pre/post processing 正确。
2. 切 WebGPU 或 WebNN，检查支持矩阵和是否有 fallback。
3. 对固定输入尺寸使用 graph optimization、ORT format、`freeDimensionOverrides`。
4. 对多步模型减少 CPU/GPU copy，评估 IO binding。
5. 在目标浏览器矩阵上测首次加载、热推理、内存峰值和电量/热表现。

## 相关页面

- [Transformers.js 参数模型](transformers-js-runtime-parameters.md)
- [CPU、边缘与 NPU 推理](cpu-edge-npu-inference.md)
- [模型转换、量化与校准流水线](model-conversion-quantization-pipeline.md)
- [ONNX Runtime GenAI 参数模型](onnxruntime-genai-parameters.md)
- [图编译与 Engine 构建优化](graph-compilation-and-engine-build.md)

## 关键来源

- ONNX Runtime Web tutorial: https://onnxruntime.ai/docs/tutorials/web/
- ONNX Runtime Web getting started: https://onnxruntime.ai/docs/get-started/with-javascript/web.html
- ONNX Runtime Web WebGPU EP: https://onnxruntime.ai/docs/tutorials/web/ep-webgpu.html
- ONNX Runtime Web WebNN EP: https://onnxruntime.ai/docs/tutorials/web/ep-webnn.html
- ONNX Runtime quantization: https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html
- ONNX Runtime GitHub: https://github.com/microsoft/onnxruntime
