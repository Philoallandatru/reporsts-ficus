---
type: Concept
title: 模型生命周期、热切换与保活
description: 在线推理不只是在进程启动时加载一个模型。真实系统会遇到多模型路由、模型按需加载、空闲卸载、LoRA 切换、灰度发布、版本回滚和本地模型热切换。这一层决定冷启动、显存碎片、alias
  一致性和用户请求是否会打到正确模型。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 模型生命周期、热切换与保活

在线推理不只是在进程启动时加载一个模型。真实系统会遇到多模型路由、模型按需加载、空闲卸载、LoRA 切换、灰度发布、版本回滚和本地模型热切换。这一层决定冷启动、显存碎片、alias 一致性和用户请求是否会打到正确模型。

## 生命周期状态

| 状态 | 含义 | 风险 |
|---|---|---|
| Not present | 权重不在本机或缓存中 | 下载慢、鉴权失败、revision 漂移 |
| Cached | artifact 已在磁盘/NVMe/HF cache | 仍需加载 tokenizer、权重、engine |
| Loaded | 权重在 RAM/VRAM，engine 已初始化 | 占用资源，可能阻止其他模型加载 |
| Warm | CUDA graph、KV/prefix cache、JIT/compile 已热 | 最低延迟但成本最高 |
| Draining | 不接新请求，等待旧请求结束 | 长 streaming 会阻塞卸载 |
| Unloaded | 释放 RAM/VRAM，只保留磁盘缓存 | 下次请求冷启动 |

## 常见控制

| 系统 | 控制方式 | 语义 |
|---|---|---|
| Ollama | `keep_alive`、load/unload API、`OLLAMA_KEEP_ALIVE`、`OLLAMA_MAX_LOADED_MODELS`、`OLLAMA_NUM_PARALLEL`、`OLLAMA_MAX_QUEUE` | 控制模型空闲后保留多久、并发与排队 |
| LocalAI | models directory、models config、preload、`--load-to-memory`、watchdog/LRU | 多模型配置、启动时加载和后端驱逐 |
| TabbyAPI | model load/unload/list 管理接口 | 本地 GPU 模型切换和默认模型管理 |
| KoboldCpp | `--admin`、`--admindir`、`--routermode`、`--adminunloadtimeout` | 本地配置切换和按 model 字段重载 |
| llama-swap | OpenAI-compatible 前置路由、TTL、alias/profile、unload API、metrics | 用轻量 router 做本地多模型切换 |
| vLLM / SGLang | 多服务副本、LoRA runtime loading、model alias | 高吞吐场景通常用多进程/多副本隔离 |

## 热切换的代价

热切换听起来像只是改一个 `model` 字段，但实际可能包括：

- 停止接收旧模型新请求。
- 等待旧请求 streaming 完成或取消。
- 释放 KV cache、权重、CUDA graph、adapter。
- 加载新权重、tokenizer、chat template、generation config。
- 捕获 CUDA graph、warmup、恢复 readiness。

如果没有显式状态机，模型切换很容易变成“某些请求打到旧模型，某些请求打到新模型，日志里都叫同一个 alias”。

## 调参建议

1. 为每个 model alias 记录真实 model id、revision、quantization、template、default sampling。
2. 交互模型设置较长 keepalive；低频模型按需加载但给用户明确冷启动预期。
3. 大模型切换前先 drain，不要强杀还在 streaming 的请求。
4. 多模型共享同 GPU 时，保留显存 headroom，避免反复加载造成碎片和 OOM。
5. LoRA/adapters 也属于模型状态，必须记录启用的 adapter、rank、revision。
6. 对本地 router，区分“路由切换”与“底层 engine 已经 warm”。
7. 对 Ollama 这类有 `keep_alive` 的系统，记录 load duration 和空闲卸载策略，避免把冷启动误判为模型慢。

## 常见误区

- 只缓存权重文件：磁盘缓存不等于模型已 warm。
- 一个 alias 指多个 revision：质量和复现都会漂。
- 低频模型 keepalive 太长：省了冷启动，但浪费显存和电费。
- 卸载时不处理长连接：streaming 请求可能拖住旧模型几分钟。
- 让 router 自动重试到另一个模型：这会改变回答质量和计费语义。

## 相关页面

- [模型 Artifact 分发、缓存与冷启动](model-artifact-distribution-and-cold-start.md)
- [LLM 网关与路由层参数](llm-gateway-routing-parameters.md)
- [Streaming、Backpressure、Timeout 与取消](streaming-backpressure-timeouts-cancellation.md)
- [OpenAI-compatible API 语义与兼容边界](openai-compatible-api-semantics.md)

## 关键来源

- Ollama API: https://docs.ollama.com/api
- Ollama FAQ: https://docs.ollama.com/faq
- LocalAI model configuration: https://localai.io/docs/advanced/model-configuration/
- TabbyAPI GitHub: https://github.com/theroyallab/tabbyAPI
- llama-swap GitHub: https://github.com/mostlygeek/llama-swap
- llama-swap config example: https://github.com/mostlygeek/llama-swap/blob/main/config.example.yaml
