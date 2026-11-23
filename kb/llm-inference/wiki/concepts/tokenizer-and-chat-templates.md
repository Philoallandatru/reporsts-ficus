---
type: Concept
title: Tokenizer、chat template 与 token 预算
description: Tokenizer 和 chat template 是推理系统里最容易被低估的部分。同一个权重，如果 tokenizer 或模板错配，模型可能表现为“不听指令”“工具调用格式错”“输出乱码”或
  token 预算突然膨胀。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Tokenizer、chat template 与 token 预算

Tokenizer 和 chat template 是推理系统里最容易被低估的部分。同一个权重，如果 tokenizer 或模板错配，模型可能表现为“不听指令”“工具调用格式错”“输出乱码”或 token 预算突然膨胀。

## Tokenizer 决定什么

- 文本如何切成 token。
- special tokens 的 ID 和含义。
- BOS/EOS/PAD 等边界。
- 工具消息、角色消息如何编码。
- 估算上下文长度和计费 token。

## Chat template 决定什么

Chat template 把结构化 messages 转成模型训练时见过的字符串格式。例如：

```text
system + user + assistant + tool
  -> template render
  -> tokenizer
  -> model input ids
```

模板错配会导致模型看不到正确的 role 边界，或把 tool schema 当普通文本处理。

## 常见错配

| 错配 | 表现 |
|---|---|
| tokenizer 版本不同 | token 数变化、special token ID 错 |
| chat template 不匹配 | 指令跟随变差、角色混乱 |
| 工具消息格式错 | function calling 失败 |
| 多模态占位符错 | image/audio token 无法对齐 |
| stop token 错 | 提前截断或不停生成 |

Hugging Face 文档特别提醒：chat template 通常已经包含必要 special tokens，如果后续 tokenize 时又自动添加 `<bos>/<eos>`，会重复 special tokens 并损害性能。更稳的方式是让模板渲染和 tokenize 在同一路径完成。

## Token 预算

上下文预算要包含：

- system prompt。
- developer/tool instructions。
- user messages。
- history。
- retrieved documents。
- tool schemas。
- multimodal media tokens。
- output reserve。

如果只按用户文本估算，很容易在 RAG、agent、多模态场景超预算。

## 调参建议

- 模型、tokenizer、chat template 一起 pin revision。
- 服务端 admission control 使用 tokenizer 后的真实 token 数。
- 工具调用和结构化输出要用模型官方模板验证。
- 多模态模型要检查 image placeholder / media token 是否由 template 插入。
- 对外提供 API 时，记录渲染后的 prompt token 数，方便定位问题。

## 关键来源

- Hugging Face Chat Templates: https://huggingface.co/docs/transformers/en/chat_templating
- Hugging Face Writing Chat Templates: https://huggingface.co/docs/transformers/en/chat_templating_writing
- vLLM Tool Calling: https://docs.vllm.ai/en/v0.25.1/features/tool_calling/
- SGLang Custom Chat Template: https://docs.sglang.io/docs/references/custom_chat_template.md
- llama.cpp Function Calling: https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md
- Ollama Modelfile: https://docs.ollama.com/modelfile
