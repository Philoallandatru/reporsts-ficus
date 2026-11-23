---
type: Concept
title: OpenAI-compatible API 语义与兼容边界
description: “OpenAI-compatible”通常表示请求路径、JSON 字段和 SDK 调用方式尽量接近 OpenAI API；它不表示不同后端在
  tokenization、chat template、tool call、streaming chunk、错误码和默认采样上完全一致。把它当成协议适配层，而不是模型语义等价层。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# OpenAI-compatible API 语义与兼容边界

“OpenAI-compatible”通常表示请求路径、JSON 字段和 SDK 调用方式尽量接近 OpenAI API；它不表示不同后端在 tokenization、chat template、tool call、streaming chunk、错误码和默认采样上完全一致。把它当成协议适配层，而不是模型语义等价层。

## 常见端点

| 端点/能力 | 常见支持者 | 需要确认的差异 |
|---|---|---|
| `/v1/chat/completions` | vLLM、SGLang、TGI Messages API、llama.cpp server、NIM、MLC、FastChat、Sonar/Aphrodite | chat template、system/tool message 格式、streaming delta |
| `/v1/responses` | OpenAI、vLLM、llama.cpp、NIM 等部分兼容 server | Responses 的 typed output items、stateful 行为和事件流不等同于 Chat Completions |
| `/v1/completions` | vLLM、llama.cpp、FastChat、部分兼容 server | 是否是 legacy text completion；是否自动加模板 |
| `/v1/embeddings` | vLLM pooling、TGI/TEI、NIM、MLC、FastChat | pooling、normalize、维度截断、embedding dtype |
| `/v1/rerank` / `/rerank` | vLLM、TEI、OpenVINO Model Server、Sonar/Aphrodite 等 | 不是 OpenAI 官方标准端点，常是 Cohere/Jina 风格或框架扩展 |
| `/v1/models` | 多数兼容 server | 返回的 `id` 可能是 served model alias，而非真实权重 revision |
| tool/function calling | OpenAI、vLLM、SGLang、Sonar/Aphrodite、llama.cpp 等 | parser、template、JSON schema 支持范围差异最大 |
| multimodal input | OpenAI、vLLM、SGLang、llama.cpp、NIM、Sonar/Aphrodite 等 | image/video/audio token 预算、URL 安全策略、processor 参数 |

API 兼容层的价值是让应用、SDK、网关和压测工具复用同一请求形状。它真正接到后端后，仍然要映射到各 engine 的 tokenizer、scheduler、KV cache、sampling params 和模型能力。

OpenAI 自身也有“接口世代”差异：Chat Completions 以 `messages` 和 `choices[]` 为中心；Responses API 以 typed input/output items、工具调用事件和更细的流式事件为中心。一个服务支持 Chat Completions，不应自动推断它支持完整 Responses API。

## 请求字段的三层含义

| 层 | 示例字段 | 原理 |
|---|---|---|
| 协议字段 | `model`、`messages`、`stream`、`tools`、`response_format` | 决定 HTTP 请求形状和客户端解析方式 |
| 生成字段 | `temperature`、`top_p`、`max_tokens`、`stop`、`presence_penalty` | 最终映射到后端 sampler；不是所有后端都支持完全相同的 sampler |
| 后端扩展 | vLLM `extra_body`、SGLang/Sonar 自定义字段、llama.cpp server 扩展字段 | 暴露 engine 独有能力，如 guided decoding、top-k、min-p、cache/token 细节 |

生产中建议把“兼容字段”和“后端扩展字段”分开管理。前者用于跨后端可移植，后者用于明确绑定某个 engine 的性能或格式能力。

## Streaming

OpenAI 风格 streaming 通常使用 Server-Sent Events，客户端逐块收到 delta。兼容 server 常见差异包括：

- chunk 中是否稳定返回 `role`、`content`、`tool_calls`。
- 最后一块是否返回 usage。
- 是否使用 `[DONE]` 结束。
- tool call 的 arguments 是完整 JSON 还是分片字符串。
- 错误在 HTTP 层返回，还是在流中途以错误事件返回。

这会影响 SDK、网关、日志采集和前端显示。上线前要用目标 SDK 做真实流式回放，而不是只用一次非流式请求验证。

## Tool calling

Tool calling 的兼容风险比普通文本更高，因为模型必须同时满足三件事：

1. prompt/chat template 要把工具 schema 放到模型期望的位置。
2. sampler 或 parser 要把模型输出解析成 API 返回结构。
3. 客户端要能处理 streaming tool call delta、并发 tool calls 和失败重试。

同一个 `tools` JSON schema，在不同模型和不同后端上可能走完全不同的 parser。vLLM、SGLang、llama.cpp 和 Sonar/Aphrodite 都有各自的 tool parser / guided decoding 参数；迁移时要把 parser 名、chat template 和模型族一起迁移。

## “兼容”不保证一致的地方

| 现象 | 原因 | 处理方式 |
|---|---|---|
| 同 prompt 输出不同 | tokenizer、template、默认采样、量化路径不同 | 固定 template、sampling、revision，并保存完整请求 |
| stop 不生效 | stop 字符串被 tokenization 分裂或模板插入特殊 token | 用 token 级测试确认；必要时改模板或 stop 集合 |
| usage 不一致 | prompt token 计算、special tokens、多模态 token 预算不同 | 以服务端 tokenizer 为准，记录 engine 的 token 统计 |
| tool call JSON 漂移 | parser 和模型训练格式不匹配 | 选后端支持的 parser，并考虑 guided decoding |
| 网关路由后质量波动 | 一个 alias 后接多个真实模型/模板 | `model` alias 要绑定明确 revision/template/sampling profile |

## 调参建议

- 迁移后端时，先做“语义一致性测试”：固定 20-50 条代表性请求，对比 token count、finish reason、stop、tool call 和 JSON 格式。
- OpenAI-compatible 字段够用时，避免使用后端扩展；需要性能或结构化能力时，再显式引入扩展字段。
- 对需要 tool calling 的服务，把 parser、chat template、模型 revision 当作同一个版本单元发布。
- 对 streaming 客户端，单独测试中途断开、超时、tool delta、usage chunk 和错误事件。
- 对 rerank/score，明确标注它是 OpenAI-style 扩展、Cohere/Jina 兼容，还是框架自定义接口。
- 对多后端网关，记录真实 backend、served model name、model revision 和 sampling profile，避免只记录 `model` alias。

## 与其他页面的关系

- [Tokenizer、chat template 与 token 预算](tokenizer-and-chat-templates.md)：解释兼容 API 为什么仍会输出不一致。
- [Tool/function calling 推理路径](tool-calling-inference.md)：展开 parser、schema 和 guided decoding。
- [LLM 网关与路由层参数](llm-gateway-routing-parameters.md)：解释 API 兼容层在多后端路由中的位置。
- [采样与结构化输出](sampling-and-structured-output.md)：解释请求字段如何落到 sampler 和 grammar。

## 关键来源

- OpenAI streaming responses: https://developers.openai.com/api/docs/guides/streaming-responses
- OpenAI API overview: https://developers.openai.com/api/reference/overview/
- OpenAI Responses migration guide: https://developers.openai.com/api/docs/guides/migrate-to-responses
- OpenAI function calling: https://developers.openai.com/api/docs/guides/function-calling
- vLLM OpenAI-compatible server: https://docs.vllm.ai/en/stable/serving/openai_compatible_server/
- vLLM online serving endpoints: https://docs.vllm.ai/en/stable/serving/online_serving/
- llama.cpp server README: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- SGLang documentation: https://docs.sglang.io/
- TGI Messages API: https://huggingface.co/docs/text-generation-inference/en/messages_api
- NVIDIA NIM API reference: https://docs.nvidia.com/nim/large-language-models/latest/api-reference.html
- MLC LLM REST API: https://llm.mlc.ai/docs/deploy/rest.html
- FastChat OpenAI API: https://github.com/lm-sys/FastChat/blob/main/docs/openai_api.md?plain=1
- Sonar OpenAI-compatible API: https://sonar.dphn.ai/serving/openai/
