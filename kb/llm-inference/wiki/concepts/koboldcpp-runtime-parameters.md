---
type: Concept
title: KoboldCpp 参数模型
description: KoboldCpp 是基于 llama.cpp/ggml 生态的本地推理应用和服务端，常用于桌面、本地写作、角色扮演、轻量 API 服务和
  GGUF 模型运行。它把模型加载、Web UI、Kobold API / OpenAI-compatible 风格接口、GPU offload、上下文和采样参数封装成一个本地程序。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# KoboldCpp 参数模型

KoboldCpp 是基于 llama.cpp/ggml 生态的本地推理应用和服务端，常用于桌面、本地写作、角色扮演、轻量 API 服务和 GGUF 模型运行。它把模型加载、Web UI、Kobold API / OpenAI-compatible 风格接口、GPU offload、上下文和采样参数封装成一个本地程序。

## 参数面

| 参数面 | 常见参数 / 概念 | 作用 |
|---|---|---|
| 模型加载 | GGUF model、adapter、mmproj、model path | 决定加载哪类权重和多模态 projector |
| CPU | threads、blas threads、batch | 控制 CPU 计算、prompt 处理和线程竞争 |
| GPU offload | GPU layers、tensor split、main GPU、backend acceleration | 把部分层或计算放到 GPU |
| 上下文 / KV | context size、rope scaling、KV cache type、flash attention | 控制长上下文、KV 显存和 attention 性能 |
| UI / Server | `--host`、`--port`、`--launch`、`--password`、API mode、remote access | 暴露 Web UI 和 API |
| Sampling | temperature、top-p、top-k、min-p、repeat penalty、Mirostat、stop | 控制输出风格和复现 |

具体参数名随 KoboldCpp 版本和图形界面/命令行入口变化；生产或脚本化使用前应以当前发行版 help 和官方 README 为准。

## 与 llama.cpp 的关系

KoboldCpp 的底层推理思路与 llama.cpp 接近：

- GGUF 权重量化减少内存/显存带宽。
- `context size` 增大会放大 KV cache。
- GPU layers/offload 决定权重计算放在 CPU 还是 GPU。
- Flash attention、KV cache 量化、BLAS/CUDA/Metal/Vulkan 后端影响速度。

KoboldCpp 的额外价值是把这些能力做成本地应用和 API server，适合非工程用户或轻量本地服务。

## 常用参数

| 参数族 | 常见参数 |
|---|---|
| 模型 / server | `--model`、`--port`、`--host`、`--launch`、`--config`、`--password` |
| 上下文 / batch | `--contextsize`、`--batchsize`、`--blasbatchsize` |
| 线程 | `--threads`、`--blasthreads` |
| GPU backend | `--usecuda` / `--usecublas`、`--usehipblas`、`--usevulkan`、`--usecpu` |
| GPU 放置 | `--gpulayers`、`--tensor_split`、`--maingpu`、`--autofit` |
| Attention / KV | MMQ 开关、Flash Attention、`--quantkv` |
| API / streaming | Kobold API、OpenAI `/v1/completions`、`/v1/chat/completions`、SSE streaming |
| 管理 / 路由 | `--admin`、`--admindir`、`--routermode`、`--adminunloadtimeout` |

Router mode 的“热切换”通常不是零成本：它会按请求里的 model 字段卸载当前模型、加载目标模型再处理请求。适合低频本地多模型，不适合严格低延迟服务。

## 调参路径

| 症状 | 优先检查 |
|---|---|
| 加载失败 | 模型格式、GGUF 版本、可用 RAM/VRAM、GPU backend |
| 首 token 慢 | prompt 长度、batch、BLAS/GPU offload、模型是否冷加载 |
| decode 慢 | GPU layers、量化类型、线程数、KV cache dtype、context size |
| 长上下文 OOM | context size、KV cache quant、并发和多模态 token |
| API 行为不一致 | prompt template、stop/eos、streaming、sampling 默认值 |

## 常见误区

- 把 Web UI 体验当成 API 服务容量：UI 单用户流畅不代表多客户端稳定。
- 盲目拉满 GPU layers：小显存上可能让 KV cache 无处可放。
- 线程越多越好：CPU 路径可能被缓存/NUMA/内存带宽限制。
- 忽略 remote access 安全：本地工具一旦监听外部地址，就要考虑鉴权和网络边界。
- 把 Kobold API、OpenAI-compatible API 和原生 llama.cpp server 语义混为一谈。

## 相关页面

- [llama.cpp 参数模型](llama-cpp-runtime-parameters.md)
- [llamafile 参数模型](llamafile-runtime-parameters.md)
- [CPU、边缘与 NPU 推理](cpu-edge-npu-inference.md)
- [OpenAI-compatible API 语义与兼容边界](openai-compatible-api-semantics.md)

## 关键来源

- KoboldCpp GitHub: https://github.com/LostRuins/koboldcpp
- KoboldCpp README: https://github.com/LostRuins/koboldcpp/blob/concedo/README.md
- KoboldCpp wiki: https://github.com/LostRuins/koboldcpp/wiki
