---
type: Concept
title: Tokenization、Validation 与预处理性能
description: LLM 服务里的 CPU 侧预处理常被低估。请求进入 GPU 前通常要经历 JSON 解析、鉴权、schema validation、chat
  template 渲染、tool schema 拼接、tokenization、长度检查、媒体预处理和 admission control。GPU 很空但 TTFT
  高，很多时候瓶颈就在这里。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Tokenization、Validation 与预处理性能

LLM 服务里的 CPU 侧预处理常被低估。请求进入 GPU 前通常要经历 JSON 解析、鉴权、schema validation、chat template 渲染、tool schema 拼接、tokenization、长度检查、媒体预处理和 admission control。GPU 很空但 TTFT 高，很多时候瓶颈就在这里。

## 预处理流水线

```text
HTTP request
  -> JSON / schema validation
  -> auth / rate limit
  -> chat template render
  -> tokenizer
  -> length / truncation / stop validation
  -> scheduler admission
  -> prefill
```

对多模态请求，还会多出图片下载、解码、resize、vision processor、音频切片或视频采样。

## 参数族

| 参数/字段 | 所在框架 | 原理与影响 |
|---|---|---|
| `apply_chat_template` | Transformers | 把 messages 渲染成模型训练格式 |
| `add_generation_prompt` | Transformers | 在 prompt 末尾添加 assistant generation 起始标记 |
| `continue_final_message` | Transformers | 让模型继续最后一条 assistant 消息，而不是开始新消息 |
| `--tokenizer-mode` | vLLM | 选择 tokenizer 加载/执行模式；影响兼容性和速度 |
| `--renderer-num-workers` | vLLM | 并行处理 chat template、tokenization、多模态 preprocessing |
| `--skip-tokenizer-init` | vLLM | 跳过 tokenizer 初始化，适合外部传 token ids 的特殊路径 |
| `--enable-prompt-embeds` | vLLM | 允许传 prompt embeddings；只适合可信输入和严格 shape 校验 |
| `--chat-template` | vLLM / llama.cpp / Transformers | 控制 messages 到 prompt 的渲染方式 |
| `--trust-remote-code` | 多框架 | 允许加载自定义 tokenizer/model code；性能和安全边界 |
| `--validation-workers` | TGI | 请求 validation/tokenization worker 数 |
| `--max-concurrent-requests` | TGI / TEI 等 | 服务端背压，避免 validation 队列无限增长 |
| `--max-input-tokens` | TGI | validation 阶段拒绝过长输入 |
| `--max-batch-prefill-tokens` | TGI | prefill token budget，也间接影响 validation 后进入调度的压力 |
| `--tokenization-workers` | TEI | embedding/rerank tokenization worker 数 |
| `--max-client-batch-size` | TEI | 单请求输入条数上限，防止大请求卡住服务 |
| Fast tokenizer / Rust tokenizer | Hugging Face Tokenizers | 减少 CPU tokenization 开销 |
| `TOKENIZERS_PARALLELISM` | Hugging Face ecosystem | 控制 tokenizer 并行行为，避免 fork/线程争用问题 |

## Chat template 是性能参数

Chat template 不只是质量参数，也会影响成本：

- 工具 schema 很长时，template 会显著增加 prompt tokens。
- 多轮 history 未压缩时，tokenization 时间和 prefill 时间一起变长。
- 模板重复添加 BOS/EOS 会损害模型表现，也会浪费 token。
- 不同服务端如果各自渲染模板，token count 可能不一致。

生产中建议记录渲染后 prompt token 数、template version 和 tokenizer revision。

`add_generation_prompt` 和 `continue_final_message` 是互斥心智模型：前者告诉模型“开始生成新 assistant 消息”，后者告诉模型“继续最后一条消息”。Reasoning prefill、JSON 续写和 tool call 场景如果选错，会表现为模型提前闭合 thinking block、重复角色标记或格式漂移。

## Validation worker 与 GPU 利用

Validation worker 太少时，GPU 可能在等 CPU；worker 太多时，CPU 抢占、内存占用和排队都会上升。正确做法是把 metrics 分层：

| 指标 | 判断 |
|---|---|
| HTTP queue 高、GPU 低 | 网关/API/validation 可能瓶颈 |
| tokenization CPU 满 | 增加 worker 或使用 fast tokenizer |
| validation rejection 高 | 输入长度、schema 或 tool 格式问题 |
| TTFT 高但 engine queue 低 | 预处理/模板/媒体处理慢 |
| prompt tokens 突然变多 | 模板、history、tool schema 或 tokenizer revision 变化 |

## 常见误调

| 误调 | 后果 | 修正 |
|---|---|---|
| 只看 GPU utilization | 忽略 CPU validation 和 tokenization | 分开记录 preprocessing time 和 engine time |
| tokenizer/template 版本不固定 | 输出质量和 token 数漂移 | pin tokenizer、template、model revision |
| 客户端先 tokenize、服务端再 tokenize | token 数和 special token 可能不一致 | 统一服务端 tokenization 或严格校验 token ids |
| `max-client-batch-size` 过大 | 单个 embedding 请求占满 validation | 限制客户端批量，服务端统一 batching |
| 过度开启 remote code | 安全风险和不可复现 | 只对审计过的模型启用 |
| 多模态 URL 不限域 | 预处理慢且有安全风险 | 配置 allowed media domains 和大小限制 |
| renderer/validation worker 太少 | GPU 空等预处理 | 按 CPU 核数、请求形态和模板复杂度调 worker |
| renderer/validation worker 太多 | CPU 抢占、内存涨、上下文切换多 | 同时看 CPU saturation 和 queue time |
| prompt embeds 对外开放 | 非法 shape 或恶意输入可能打崩 engine | 只给可信内部调用开放，并严格校验 |

## 调参建议

- 压测时记录 preprocessing latency、tokenization latency、engine queue、TTFT 和 TPOT。
- 对 agent/tool 流量，单独计算 tool schema token 和模板渲染耗时。
- 对 embedding/rerank，优先看 tokenization worker、batch tokens、pair 数，而不是采样参数。
- 对多租户服务，validation 阶段就拒绝超长输入和超大媒体，避免进入 GPU 队列。
- 发生质量漂移时，先对比渲染后的 prompt，而不是只看原始 messages。

## 与其他页面的关系

- [Tokenizer、chat template 与 token 预算](tokenizer-and-chat-templates.md)：模板和 tokenizer 的语义正确性。
- [OpenAI-compatible API 语义与兼容边界](openai-compatible-api-semantics.md)：兼容 API 不保证同样的模板/tokenizer。
- [Autoscaling 与 Admission Control](autoscaling-and-admission-control.md)：validation 背压是 admission 的一部分。
- [Hugging Face TEI 参数模型](huggingface-tei-parameters.md)：embedding/rerank 预处理尤其关键。
- [多模态推理与媒体 token 预算](multimodal-inference.md)：媒体预处理和 token 预算。

## 关键来源

- Hugging Face Tokenizers: https://huggingface.co/docs/tokenizers/index
- Hugging Face Chat Templates: https://huggingface.co/docs/transformers/en/chat_templating
- Hugging Face Fast Tokenizers: https://huggingface.co/docs/transformers/en/fast_tokenizers
- Hugging Face Writing Chat Templates: https://huggingface.co/docs/transformers/en/chat_templating_writing
- vLLM Engine Args: https://docs.vllm.ai/en/stable/configuration/engine_args/
- vLLM latest Engine Args: https://docs.vllm.ai/en/latest/configuration/engine_args.html
- vLLM serve CLI: https://docs.vllm.ai/en/stable/cli/serve/
- Hugging Face TGI launcher: https://huggingface.co/docs/text-generation-inference/reference/launcher
- Hugging Face TEI CLI arguments: https://huggingface.co/docs/text-embeddings-inference/en/cli_arguments
