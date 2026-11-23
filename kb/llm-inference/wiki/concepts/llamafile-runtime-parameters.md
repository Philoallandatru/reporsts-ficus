---
type: Concept
title: llamafile 参数模型
description: llamafile 把模型、运行时和本地服务能力打包成一个可执行文件，目标是让用户下载后直接运行本地 LLM。它基于 llama.cpp/ggml
  生态，适合离线、本地开发、演示、轻量服务和跨平台分发。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# llamafile 参数模型

llamafile 把模型、运行时和本地服务能力打包成一个可执行文件，目标是让用户下载后直接运行本地 LLM。它基于 llama.cpp/ggml 生态，适合离线、本地开发、演示、轻量服务和跨平台分发。

## 参数面

| 参数面 | 常见参数 / 概念 | 作用 |
|---|---|---|
| 启动方式 | 直接运行 `.llamafile`、server mode、browser UI | 控制本地交互或 HTTP 服务 |
| 模型与上下文 | bundled model、external model、context size | 决定可处理 prompt 长度和 KV cache 占用 |
| CPU/GPU | threads、GPU offload、backend acceleration | 控制算力落在 CPU、Metal、CUDA、Vulkan 等路径 |
| Batch / prompt | batch、prompt、system prompt、chat template | 影响 TTFT、吞吐和角色格式 |
| Sampling | temperature、top-k、top-p、repeat penalty、seed、stop | 控制输出风格和复现性 |
| Server | host、port、API endpoint、web UI、CORS/访问边界 | 暴露本地服务给浏览器或客户端 |

很多参数语义继承自 llama.cpp，因此推理原理应和 [llama.cpp 参数模型](llama-cpp-runtime-parameters.md) 一起看。

## 常用参数

| 参数族 | 常见参数 |
|---|---|
| 模式 | `--cli`、`--chat`、`--server` |
| CPU / batch | `-t` / `--threads`、`-tb` / `--threads-batch`、`-c` / `--ctx-size`、`-b` / `--batch-size`、`-ub` / `--ubatch-size` |
| GPU offload | `--gpu auto|nvidia|amd|apple|vulkan|disable`、`-ngl` / `--gpu-layers` / `--n-gpu-layers`、`--device`、`--list-devices`、`--split-mode`、`--tensor-split`、`--main-gpu` |
| MoE offload | `--cpu-moe`、`--n-cpu-moe` |
| KV / memory | `--kv-offload` / `--no-kv-offload`、`--cache-type-k`、`--cache-type-v`、`--mlock`、`--mmap` / `--no-mmap`、`--numa` |
| Sampling | `--temp`、`--top-k`、`--top-p`、`--min-p`、`--repeat-penalty`、`--presence-penalty`、`--frequency-penalty`、`--mirostat`、`--seed`、`--grammar`、`--json-schema` |
| Server | `--host`、`--port`、`--api-key`、`--api-prefix`、`--webui` / `--no-webui`、`--parallel`、`--cont-batching`、`--threads-http`、`--metrics`、`--slots`、`--tools`、`--confine-reads` |

## 适用场景

| 场景 | 为什么适合 |
|---|---|
| 离线 demo | 单文件分发，不依赖云端服务 |
| 本地开发 | 快速启动 OpenAI-like 本地 endpoint 或浏览器 UI |
| 教学 / 可复现包 | 模型和运行时绑定，减少安装差异 |
| 轻量边缘 | 小模型 + 量化 + 本地 CPU/GPU 后端 |

如果目标是高并发生产 serving，llamafile 的价值通常在“简单分发和本地可运行”，不是替代 vLLM/SGLang/TGI 的 GPU 调度器。

## 性能路径

llamafile 常见瓶颈与 llama.cpp 类似：

- CPU 路径主要受内存带宽、线程数和量化格式影响。
- GPU offload 能提高吞吐，但上下文/KV cache 仍要占内存或显存。
- 过大的 context 会显著增加 KV cache，并拖慢长 prompt。
- 单文件首次运行和模型加载时间要和 steady-state decode 分开看。
- 可执行文件和权重通常通过 `mmap()` 映射，首次 page fault 与 OS page cache warmup 会影响冷启动观测。
- 如果 GPU backend 不能构建或加载，可能回退 CPU；生产验证时应显式选择目标 GPU backend，避免静默慢路径。

## 安全边界

llamafile 的便利性来自“本地即可运行”，但 server 模式仍然是一个 HTTP 服务：

- `--host 0.0.0.0` 会暴露到外部接口，需要 API key、网络边界和反向代理。
- GPU mode 可能需要访问 GPU driver 设备，沙箱能力和纯 CPU/server 模式不同。
- `--tools all`、MCP proxy 或 server-side tools 可能访问本地文件或网络，不应在不可信环境开启。
- `--confine-reads` 可以收紧读路径，但不能替代整体部署隔离。

## 常见误区

- 以为单文件就没有供应链问题：模型 artifact、运行时版本和下载来源仍要固定。
- 本地浏览器 UI 能用就开放到公网：生产访问需要代理、认证和网络边界。
- 盲目增加线程：CPU 线程过多会造成缓存/NUMA 竞争。
- 忽略 chat template：同一模型在不同 prompt 格式下行为差异很大。
- 把本地单用户体验当成多用户服务容量。

## 相关页面

- [llama.cpp 参数模型](llama-cpp-runtime-parameters.md)
- [CPU、边缘与 NPU 推理](cpu-edge-npu-inference.md)
- [OpenAI-compatible API 语义与兼容边界](openai-compatible-api-semantics.md)
- [模型 Artifact 分发、缓存与冷启动](model-artifact-distribution-and-cold-start.md)
- [Reproducibility、Seed 与推理确定性](reproducibility-seeds-and-determinism.md)

## 关键来源

- llamafile documentation: https://docs.mozilla.ai/llamafile
- llamafile quickstart: https://docs.mozilla.ai/llamafile/getting-started/quickstart
- Running llamafile: https://docs.mozilla.ai/llamafile/using-llamafile/running_llamafile
- llamafile CLI arguments: https://docs.mozilla.ai/llamafile/reference/cli_arguments
- llamafile security: https://docs.mozilla.ai/llamafile/reference/security
- llamafile technical details: https://docs.mozilla.ai/llamafile/reference/technical_details
- llamafile troubleshooting: https://docs.mozilla.ai/llamafile/reference/troubleshooting
- llamafile GitHub: https://github.com/mozilla-ai/llamafile
