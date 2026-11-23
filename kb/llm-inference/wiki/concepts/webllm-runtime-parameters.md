---
type: Concept
title: WebLLM 参数模型
description: WebLLM 是 MLC 生态的浏览器内 LLM 推理引擎。它把模型编译、下载缓存、WebGPU 执行、OpenAI-compatible
  chat completions、streaming、JSON mode、logit 控制和 worker/service worker 集成到 Web 应用里。它的核心约束不是多租户
  GPU serving，而是...
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# WebLLM 参数模型

WebLLM 是 MLC 生态的浏览器内 LLM 推理引擎。它把模型编译、下载缓存、WebGPU 执行、OpenAI-compatible chat completions、streaming、JSON mode、logit 控制和 worker/service worker 集成到 Web 应用里。它的核心约束不是多租户 GPU serving，而是浏览器 WebGPU 能力、模型下载体积、IndexedDB/Cache 存储、页面生命周期和端侧内存。

## 参数面

| 参数面 | 常见字段 / API | 作用 |
|---|---|---|
| Engine 创建 | `CreateMLCEngine(model_id, engineConfig)`、`CreateWebWorkerMLCEngine`、`MLCEngine.reload()` | 创建 engine、加载模型、切换模型或覆盖 chat config |
| App 配置 | `appConfig`、`prebuiltAppConfig`、`model_list`、`cacheBackend` | 配置可用模型、模型库、缓存后端和应用级下载策略 |
| 模型条目 | `model_id`、`model_lib`、`model` / wasm URL、`model_url`、`low_resource_required` | 决定下载哪个 MLC artifact、加载哪个 WebGPU/wasm 模型库 |
| 加载进度 | `initProgressCallback` | 暴露模型下载、初始化和 reload 进度，避免页面“假死” |
| 浏览器缓存 | Cache API、IndexedDB、cross-origin storage fallback | 缓存权重和模型库，降低二次加载时间 |
| Chat config | `context_window_size`、`sliding_window_size`、`attention_sink_size`、penalty、`temperature`、`top_p` | 控制 KV cache、长上下文策略和默认采样 |
| 请求参数 | `messages`、`stream`、`max_tokens`、`temperature`、`top_p`、`stop`、penalty | OpenAI-compatible chat completion 请求字段 |
| 扩展 | `logitProcessorRegistry`、JSON mode、function calling 相关能力 | 自定义 logits 处理和结构化输出 |
| Worker | Web Worker / Service Worker engine | 避免主线程阻塞，并管理模型生命周期 |

## 原理

WebLLM 预先把模型编译成 WebGPU 可运行的 artifact，并在浏览器里下载权重和 wasm/model library。生成时，prefill 和 decode 都发生在用户设备上；KV cache 占用浏览器进程可用的 GPU/系统内存，模型文件占用浏览器缓存或 IndexedDB。

这意味着 WebLLM 的调参优先级和 vLLM/SGLang 不同：

- 首次体验常被下载体积、缓存命中和初始化进度决定。
- 长上下文主要受 `context_window_size`、滑动窗口和设备内存限制。
- UI 卡顿通常来自主线程工作，应使用 Web Worker 或 Service Worker。
- 浏览器和 GPU driver 差异会影响可用性；同一模型在不同用户设备上表现不同。

## 关键参数

### `appConfig.model_list`

模型列表决定用户能加载哪些模型，以及每个模型对应的权重和模型库。生产应用应固定模型条目和版本，不要让前端 silently 指向不同 artifact。

### `cacheBackend`

WebLLM 支持多种缓存后端。默认浏览器缓存适合普通 Web 应用；IndexedDB 更适合明确管理大文件；cross-origin storage 属于实验路径，需要浏览器/扩展支持。缓存命中只降低下载和加载成本，不会让模型计算更快。

### `context_window_size`

这是浏览器端最容易 OOM 的参数。更大的上下文意味着更多 KV cache；在 WebGPU 设备内存小、浏览器限制严格或页面同时有其他 WebGL/WebGPU 内容时，要保守设置。

### 请求级采样

`temperature`、`top_p`、`max_tokens`、`stop` 等请求参数与 OpenAI API 类似。如果请求中省略，WebLLM 可回落到 reload 时的 baseline config。生产要显式记录默认值，避免模型切换后输出风格漂移。

## 常见误调风险

| 风险 | 表现 | 处理 |
|---|---|---|
| 模型太大 | 首次下载慢、初始化失败、页面被浏览器杀掉 | 使用更小模型、更低量化、更短上下文 |
| WebGPU 不可用 | 用户设备直接无法运行 | 做 feature detection，并准备云端或 WASM fallback |
| 主线程运行 engine | UI 卡顿、输入延迟、页面无响应 | 使用 Worker / Service Worker |
| cache 版本不清 | 用户一直加载旧模型 | 模型 URL / model id 加版本，提供 cache 清理路径 |
| 上下文窗口过大 | WebGPU allocation 失败或 decode 变慢 | 降 `context_window_size`，使用 sliding window |
| OpenAI-compatible 误判 | streaming chunk、tool/JSON、usage 与服务端不完全一致 | 用目标客户端逐项回归 |

## 适用边界

| 场景 | 是否适合 |
|---|---|
| 隐私演示、本地聊天、离线 PWA | 适合 |
| 教育 demo、低并发个人工具 | 适合 |
| 大模型高并发在线服务 | 不适合，应该用服务端 engine |
| 严格可控硬件环境 | 需要设备矩阵测试 |
| 移动浏览器长上下文 | 风险高，优先小模型和短上下文 |

## 相关页面

- [CPU、边缘与 NPU 推理](cpu-edge-npu-inference.md)
- [MLC LLM 参数模型](mlc-llm-runtime-parameters.md)
- [Transformers.js 参数模型](transformers-js-runtime-parameters.md)
- [ONNX Runtime Web 参数模型](onnxruntime-web-parameters.md)
- [模型生命周期、热切换与保活](model-lifecycle-hot-swap-and-keepalive.md)

## 关键来源

- WebLLM documentation: https://webllm.mlc.ai/docs/
- WebLLM getting started: https://webllm.mlc.ai/docs/user/get_started.html
- WebLLM API reference: https://webllm.mlc.ai/docs/user/api_reference.html
- WebLLM GitHub: https://github.com/mlc-ai/web-llm
