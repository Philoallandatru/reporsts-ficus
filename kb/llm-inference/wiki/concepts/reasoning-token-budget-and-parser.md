---
type: Concept
title: Reasoning / Thinking Token 预算与 Parser
description: Reasoning model 的推理成本不只来自最终回答 token，还来自模型内部或显式输出的 reasoning / thinking
  token。不同 provider 和自托管框架对 reasoning 的暴露方式不同：有的把 reasoning 当作隐藏 token 计入输出预算，有的把
  `<think>...</think>` 一类内容作...
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Reasoning / Thinking Token 预算与 Parser

Reasoning model 的推理成本不只来自最终回答 token，还来自模型内部或显式输出的 reasoning / thinking token。不同 provider 和自托管框架对 reasoning 的暴露方式不同：有的把 reasoning 当作隐藏 token 计入输出预算，有的把 `<think>...</think>` 一类内容作为可解析文本返回，有的提供单独的 `reasoning_content` 字段。

## 两种模式

| 模式 | 代表 | 特点 |
|---|---|---|
| 隐藏 reasoning token | OpenAI reasoning models 等 | reasoning 消耗输出预算和延迟，但不一定逐字返回给客户端 |
| 可见 thinking 文本 | DeepSeek-R1、Qwen3 thinking、部分本地模型 | 模型输出包含 reasoning 段，需要 server/parser 分离 |

部署时最容易误判的是：`max_tokens` / `max_output_tokens` 看起来留够了最终答案，但 reasoning token 先吃掉预算，导致最终答案短、被截断或延迟明显上升。

## 参数族

| 参数/字段 | 原理与影响 |
|---|---|
| `reasoning.effort` / reasoning effort | 控制模型花在 reasoning 上的强度；通常越高越慢、越贵、可能更稳 |
| `reasoning.summary` | 控制是否返回 reasoning 摘要；不是逐字暴露完整隐藏推理 |
| `usage.output_tokens_details.reasoning_tokens` | 观测 hidden/reasoning token 消耗的关键 usage 字段 |
| `max_output_tokens` / `max_completion_tokens` | 输出总预算；reasoning token 和最终答案常共享这个预算 |
| Anthropic `thinking.type` / `thinking.budget_tokens` | 开启 extended thinking 并分配明确 token 预算 |
| Anthropic `output_config.effort` | adaptive thinking 模式下按 effort 控制 thinking 强度 |
| Anthropic `usage.output_tokens_details.thinking_tokens` | 观测 thinking token 消耗 |
| `include` / summary 字段 | 控制是否返回 reasoning 摘要或额外 reasoning 信息 |
| vLLM `--enable-reasoning` | 开启 reasoning output 解析 |
| vLLM `--reasoning-parser` | 选择 DeepSeek/Qwen 等模型族对应 parser |
| vLLM `--reasoning-config` | 给 reasoning parser 传模型族相关配置 |
| vLLM `thinking_token_budget` | 在支持的模型/模板中限制 thinking token，并触发 reasoning end |
| vLLM `--default-chat-template-kwargs` | 给 chat template 传 `enable_thinking` 等默认参数 |
| SGLang separate reasoning | 把 reasoning content 和 final answer 分离 |
| llama.cpp `--reasoning-format` | server 侧把模型 thinking/reasoning 格式映射到 API 返回 |
| llama.cpp `--reasoning` / `--reasoning-effort` / `--reasoning-budget` | Jinja template 控制 thinking 开关、强度和预算 |
| llama.cpp `--reasoning-preserve` | 是否把历史 reasoning 保留进后续上下文 |
| `stop` / template | 控制 `<think>`、答案边界和截断风险 |

## OpenAI reasoning

OpenAI reasoning 文档把 reasoning 视为模型在回答前的内部推理过程。对部署和成本估算，关键点是：

- reasoning effort 影响模型推理深度、延迟和 token 消耗。
- 输出预算需要给 reasoning 留空间，不能只按最终答案长度设置。
- Responses API 的事件和输出结构不同于旧 Chat Completions，需要客户端单独适配。
- 如果只看最终 visible text，容易低估实际 token 成本。

## Anthropic extended thinking

Anthropic extended thinking 使用 `thinking` 配置和 `budget_tokens` 来显式分配思考预算，也提供 adaptive thinking 的 effort 形态。它适合需要更强推理、数学、代码、规划或复杂分析的请求，但会增加延迟和成本。`budget_tokens` 与整体 `max_tokens` 的关系要一起设计，否则最终答案空间可能不够；过低的 thinking budget 会被拒绝，过高的预算也会增加长连接和超时风险。

## 自托管 parser

本地 reasoning 模型常把 thinking 作为普通文本生成，例如先输出 `<think>...</think>`，再输出最终答案。API server 需要做三件事：

1. 识别 reasoning 起止标记。
2. 把 reasoning content 放入兼容 API 的单独字段或事件。
3. 保证 streaming 中 reasoning delta 和 answer delta 不被客户端误解。

vLLM、SGLang 和 llama.cpp 都有围绕 reasoning parser / reasoning format 的服务端能力，但支持的 parser 名、模型族和返回字段会随版本变化。生产迁移时要把 parser、chat template、模型 revision 和客户端解析逻辑作为一个版本单元发布。

## 成本与延迟

| 现象 | 原因 | 调参方向 |
|---|---|---|
| 最终答案被截断 | reasoning 先消耗输出预算 | 增大总输出预算或降低 reasoning effort/budget |
| TTFT 或端到端延迟上升 | 模型先进行长 reasoning | 降低 effort，按任务分流 reasoning 模型 |
| streaming 前段只有思考内容 | reasoning 被显式流出 | 客户端 UI 区分 thinking 与 final |
| tool call 失败 | reasoning 文本混进 tool JSON | 使用正确 parser 和结构化输出策略 |
| 成本异常 | 只统计最终答案 token | 记录 reasoning/hidden/output usage |
| 多轮上下文变长 | 历史 reasoning 被保留 | 检查 reasoning preserve / history 策略 |
| prompt cache 命中变化 | thinking 配置改变了请求语义 | 把 reasoning profile 纳入 cache key |

## 调参建议

- 为不同任务设 reasoning profile：简单问答低 effort，复杂规划/代码/数学高 effort。
- `max_output_tokens` 要包含 reasoning 和最终答案，不要只按最终回答估算。
- 对自托管模型，固定 reasoning parser、chat template、stop tokens 和模型 revision。
- 对 tool calling / JSON 输出，先确认 reasoning 不会污染最终结构化字段。
- 观测里单独记录 reasoning token、answer token、TTFT、E2E latency 和截断率。

## 与其他页面的关系

- [采样与结构化输出](sampling-and-structured-output.md)：reasoning 与 JSON/tool 输出经常互相影响。
- [OpenAI-compatible API 语义与兼容边界](openai-compatible-api-semantics.md)：不同 server 对 reasoning 字段兼容性不同。
- [Tool/function calling 推理路径](tool-calling-inference.md)：reasoning parser 错配会破坏 tool call。
- [推理成本与效率模型](inference-cost-and-efficiency.md)：hidden/reasoning tokens 必须进成本模型。

## 关键来源

- OpenAI reasoning guide: https://developers.openai.com/api/docs/guides/reasoning
- Anthropic extended thinking: https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking
- Anthropic Messages API: https://docs.anthropic.com/en/api/messages
- vLLM reasoning outputs: https://docs.vllm.ai/en/stable/features/reasoning_outputs.html
- vLLM serve CLI: https://docs.vllm.ai/en/stable/cli/serve/
- SGLang separate reasoning: https://sgl-project.github.io/advanced_features/separate_reasoning.html
- llama.cpp server README: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
