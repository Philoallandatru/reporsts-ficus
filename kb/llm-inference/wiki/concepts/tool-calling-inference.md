---
type: Concept
title: Tool/function calling 推理路径
description: Tool/function calling 不是单纯 prompt 工程。服务端要把工具 schema 注入模型上下文，模型生成结构化 tool
  call，框架或应用解析并执行工具，再把 tool result 作为消息返回模型。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Tool/function calling 推理路径

Tool/function calling 不是单纯 prompt 工程。服务端要把工具 schema 注入模型上下文，模型生成结构化 tool call，框架或应用解析并执行工具，再把 tool result 作为消息返回模型。

## 基本流程

```text
user request
  -> render tool schemas into chat template
  -> model generates tool call
  -> parser validates name/arguments
  -> application executes tool
  -> tool result appended to messages
  -> model generates final answer
```

## 服务端组件

| 组件 | 作用 |
|---|---|
| Tool schema | 定义函数名、参数 JSON schema、描述 |
| Chat template | 把 tool schema 和 tool messages 渲染成模型格式 |
| Guided decoding | 可选，用 schema/grammar 限制参数格式 |
| Tool parser | 从模型输出提取 tool call |
| Execution sandbox | 执行工具并限制权限 |

## 与结构化输出的关系

结构化输出保证“输出形状合法”，tool calling 还要保证“工具名存在、参数语义安全、执行权限正确”。JSON schema 能减少解析错误，但不能替代工具执行的权限控制。

llama.cpp 的 function calling 文档区分 native handler 和 generic handler：native handler 更贴近模型原生工具格式，generic handler 覆盖面更广但可能消耗更多 token。vLLM 的 tool calling 也依赖 parser/template 组合；某些 `auto` 模式只有工具声明 `strict: true` 时才会对参数做结构化约束。

## 性能影响

- 工具 schema 会占用上下文 token，工具越多 prompt 越长。
- 多轮 tool call 会增加 round trip 和历史 KV cache。
- parser/guided decoding 可能降低吞吐，但提升格式稳定性。
- tool result 太长会挤占后续上下文。

## 调参建议

- 工具 schema 保持短而明确，避免把完整文档塞进工具描述。
- 用 guided decoding / structured outputs 约束参数格式。
- 对工具参数做二次校验，不信任模型输出。
- 为 tool result 设置长度上限和摘要策略。
- 工具调用模型必须匹配对应 chat template。

## 关键来源

- OpenAI Function Calling: https://developers.openai.com/api/docs/guides/function-calling
- OpenAI Structured Outputs: https://developers.openai.com/api/docs/guides/structured-outputs
- vLLM Tool Calling: https://docs.vllm.ai/en/v0.25.1/features/tool_calling/
- SGLang Tool Parser: https://docs.sglang.io/docs/advanced_features/tool_parser.md
- SGLang Structured Outputs: https://docs.sglang.io/docs/advanced_features/structured_outputs
- llama.cpp Function Calling: https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md
- Ollama Structured Outputs: https://docs.ollama.com/capabilities/structured-outputs
