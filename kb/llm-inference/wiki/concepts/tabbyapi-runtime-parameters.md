---
type: Concept
title: TabbyAPI 参数模型
description: TabbyAPI 是面向本地 GPU 推理的 API server，围绕 ExLlama 系列运行时提供 OpenAI-compatible
  API、模型加载/卸载、采样、LoRA、draft/speculative 相关能力和管理接口。它适合低比特本地部署，尤其是单机多模型、EXL2/ExLlama
  生态和希望用 OpenAI 客户端接入本地模型的场景。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# TabbyAPI 参数模型

TabbyAPI 是面向本地 GPU 推理的 API server，围绕 ExLlama 系列运行时提供 OpenAI-compatible API、模型加载/卸载、采样、LoRA、draft/speculative 相关能力和管理接口。它适合低比特本地部署，尤其是单机多模型、EXL2/ExLlama 生态和希望用 OpenAI 客户端接入本地模型的场景。

## 版本注意

TabbyAPI 生态与 ExLlama 版本耦合较强。当前主线已转向 ExLlamaV3；历史 EXL2/ExLlamaV2 能力通常在旧分支或旧配置中出现。部署时要先确认自己运行的是主线版本、EXL2 checkpoint 分支，还是某个打包发行版。

## 参数面

| 参数面 | 常见配置 | 作用 |
|---|---|---|
| Server | `network.host`、`network.port`、`disable_auth`、`api_servers`、`sse_ping_interval`、logging、metrics | 暴露 OpenAI-compatible / Kobold API 和管理接口 |
| 模型目录 | `model_dir`、`model_name`、`inline_model_loading`、`use_dummy_models`、`use_as_default`、`backend` | 管理本地权重、默认模型和加载策略 |
| 显存 / cache | `max_seq_len`、`cache_size`、`cache_mode`、tensor parallel、GPU split/autosplit | 控制上下文、KV cache、跨 GPU 放置 |
| 量化格式 | ExLlama/EXL2/ExLlamaV3 支持格式 | 决定权重压缩、kernel 和质量 |
| LoRA / adapter | LoRA 加载、选择、限制 | 同一 base model 上服务多个任务 |
| Draft / speculation | draft model、n-gram 或 runtime 支持的 speculative 路径 | 降低 decode token 延迟 |
| API 兼容 | `/v1/chat/completions`、`/v1/completions`、streaming、sampling params | 兼容 OpenAI 客户端 |

## 关键配置

| 配置 | 含义 | 风险 |
|---|---|---|
| `disable_auth` | 关闭鉴权 | 只适合纯 localhost；外部监听必须使用 key 或网络隔离 |
| `api_servers: ["OAI"]` | 选择暴露的 API surface | 客户端兼容性和安全边界随 API surface 变化 |
| `cache_size` | KV cache token 容量，通常需按块对齐 | 太大会 OOM，太小会限制上下文 |
| `cache_mode` | FP16/Q8/Q6/Q4 或 K/V bit pair | 低 bit 省显存，但长上下文质量和兼容性要回归 |
| `tensor_parallel_backend` | native 或 NCCL | PCIe/NVLink 拓扑不同，最佳后端不同 |
| `gpu_split_auto` / `gpu_split` | 自动或手动拆分显存 | 自动能加载成功，不代表 p99 最好 |
| `draft_model.draft_mode` | `model`、`mtp`、`ngram` 或 disabled | draft 模型会额外占 VRAM，且必须匹配 tokenizer/模板 |
| `use_dummy_models` | 在 `/v1/models` 暴露占位模型 | 方便客户端发现，但 alias 与真实模型可能不一致 |

## 调参重点

| 目标 | 优先检查 |
|---|---|
| 避免 OOM | `max_seq_len`、cache mode、GPU split/autosplit、并发请求 |
| 提高 decode | cache dtype/mode、batch、draft/speculative、GPU kernel 版本 |
| 多 GPU | tensor split/autosplit 是否匹配实际显存和 PCIe/NVLink |
| 多模型 | 模型加载/卸载 API、默认模型、冷启动、显存碎片 |
| API 稳定 | OpenAI-compatible 字段、stream chunk、stop/eos、usage、tool/JSON 支持 |

TabbyAPI 的性能边界通常来自低比特 kernel、KV cache 和单机 GPU 显存。它适合“本地高质量低比特模型服务”，但不等同于 vLLM/SGLang/TGI 那种面向大规模 continuous batching 的生产 engine。

## 模型生命周期

TabbyAPI 的管理接口让模型加载、卸载和切换成为运行时行为。这带来便利，也带来风险：

- 模型切换会引入冷启动和显存重新分配。
- 长上下文请求结束前，KV cache 仍然占用显存。
- 多模型共享同一 GPU 时，alias 和默认模型必须固定，否则输出回归难定位。
- LoRA/adapters 的加载状态要纳入观测和审计。

## 常见误区

- 只看 OpenAI-compatible API：兼容接口不代表 sampling 默认值、template、stop/eos 和 usage 语义一致。
- `max_seq_len` 设太大：低比特权重省显存，但 KV cache 仍可能吃满 VRAM。
- autosplit 之后不测 p99：自动放置能让模型加载成功，但跨卡通信和不均衡会影响尾延迟。
- 忽略版本分支：ExLlamaV2/EXL2 与 ExLlamaV3 的配置和兼容性可能不同。

## 相关页面

- [ExLlamaV2 参数模型](exllamav2-runtime-parameters.md)
- [OpenAI-compatible API 语义与兼容边界](openai-compatible-api-semantics.md)
- [推理量化](inference-quantization.md)
- [模型生命周期、热切换与保活](model-lifecycle-hot-swap-and-keepalive.md)

## 关键来源

- TabbyAPI GitHub: https://github.com/theroyallab/tabbyAPI
- TabbyAPI documentation: https://theroyallab.github.io/tabbyAPI
- TabbyAPI config sample: https://github.com/theroyallab/tabbyAPI/blob/main/config_sample.yml
- TabbyAPI API tokens sample: https://github.com/theroyallab/tabbyAPI/blob/main/api_tokens_sample.yml
- TabbyAPI getting started: https://github.com/theroyallab/tabbyAPI/blob/main/docs/01.-Getting-Started.md
- TabbyAPI tool calling: https://github.com/theroyallab/tabbyAPI/blob/main/docs/10.-Tool-Calling.md
