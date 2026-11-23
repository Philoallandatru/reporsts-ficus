---
type: Concept
title: 推理安全与多租户边界
description: 推理服务的安全边界不只在模型输出。模型加载、远程媒体、CORS、API key、LoRA adapter、tool calling、remote
  code、队列和 token 限制都可能成为多租户风险。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 推理安全与多租户边界

推理服务的安全边界不只在模型输出。模型加载、远程媒体、CORS、API key、LoRA adapter、tool calling、remote code、队列和 token 限制都可能成为多租户风险。

## 主要风险面

| 风险 | 场景 | 控制 |
|---|---|---|
| 远程代码执行 | `trust_remote_code`、pickle `.bin` | 固定 revision、审计、隔离构建 |
| 任意 URL fetch | 多模态图片/视频 URL | `allowed-media-domains`、下载大小限制 |
| 资源耗尽 | 超长 prompt、超大 output、太多并发 | token limits、queue limits、rate limits |
| Adapter 注入 | 用户动态加载 LoRA | adapter allowlist、大小/rank 限制 |
| Tool 滥用 | 模型调用高权限工具 | 权限分级、参数校验、人工确认 |
| 跨租户泄漏 | prefix/KV cache、多 LoRA、多用户日志 | 租户隔离、cache key 隔离、日志脱敏 |
| 浏览器滥用 | 开放 CORS/API key 泄漏 | CORS allowlist、鉴权、网关 |

## 多租户缓存隔离

Prefix cache 和 KV cache reuse 会提升吞吐，但多租户场景要考虑：

- cache key 是否包含租户边界。
- 是否允许跨租户共享公共系统 prompt。
- 日志是否记录完整 prompt。
- LoRA adapter 是否能被其他租户命中。

高安全场景宁可牺牲部分 cache 命中率，也要显式隔离租户。

## 请求限制

生产入口至少限制：

- 最大输入 token。
- 最大输出 token。
- 最大总 token。
- 最大媒体数量和大小。
- 最大工具 schema 大小。
- 最大并发和排队请求。
- 每 API key / tenant rate limit。

TGI 源码注释把 `max_total_tokens` 描述为请求的 memory budget：prompt token 与 generated token 共享该预算。vLLM 的 `--allowed-local-media-path` 属于高风险能力，只应在可信环境启用；多模态 URL 则应配合 `allowed-media-domains`、payload limit、内容类型校验和超时。

## 供应链控制

- 优先 safetensors，避免未审计 pickle 权重。
- 固定 model/tokenizer/template/adapter revision。
- 禁止运行时从用户传入仓库动态 `trust_remote_code`。
- 模型镜像构建时完成下载、校验和 warmup。

## 调参建议

- 面向公网的推理服务不要裸开框架 server；放在 API gateway 后面。
- 多模态 URL fetch 默认关闭或 allowlist。
- Tool calling 的执行权限按工具拆分，不给模型一个“万能工具”。
- 结构化输出只能保证格式，不保证安全。
- 监控 rejected requests、queue overflow、OOM、media fetch failures 和 tool errors。

## 关键来源

- vLLM Engine Arguments: https://docs.vllm.ai/en/stable/configuration/engine_args/
- vLLM Multimodal Inputs: https://docs.vllm.ai/en/stable/features/multimodal_inputs/
- vLLM Serve CLI: https://docs.vllm.ai/en/stable/cli/serve/
- SGLang Server Arguments: https://docs.sglang.io/docs/advanced_features/server_arguments
- TGI launcher arguments: https://huggingface.co/docs/text-generation-inference/reference/launcher
- TGI safety: https://huggingface.co/docs/text-generation-inference/en/basic_tutorials/safety
- llama.cpp server README: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- Hugging Face safetensors: https://huggingface.co/docs/safetensors/en/index
- OpenAI Function Calling: https://developers.openai.com/api/docs/guides/function-calling
