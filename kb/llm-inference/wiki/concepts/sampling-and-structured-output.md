---
type: Concept
title: 采样与结构化输出
description: 采样参数决定模型如何从 logits 选出下一个 token；结构化输出机制则在采样之外加入语法约束，让模型只能生成合法 JSON、正则/grammar
  或 schema 允许的 token。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 采样与结构化输出

采样参数决定模型如何从 logits 选出下一个 token；结构化输出机制则在采样之外加入语法约束，让模型只能生成合法 JSON、正则/grammar 或 schema 允许的 token。

## 采样参数的作用

| 参数 | 原理 | 常见影响 |
|---|---|---|
| `temperature` | 缩放 logits；低温更尖锐，高温更平 | 低温稳定，高温多样 |
| `top_k` | 只保留概率最高的 K 个 token | 限制离谱 token |
| `top_p` | 保留累计概率达到 p 的候选集合 | 动态候选大小 |
| `min_p` | 保留相对最高概率不低于阈值的 token | 比 top_p 更依赖当前最高概率 |
| `typical_p` | 保留信息量接近典型集合的 token | 减少过于异常的 token |
| repetition penalty | 惩罚近期出现 token | 抑制复读，也可能伤害术语/代码 |
| presence/frequency penalty | 按是否出现/出现频率惩罚 | 鼓励话题扩展 |
| `seed` | 固定随机数 | 便于复现，但 GPU kernel 仍可能有非确定性 |
| `stop` | 命中停止序列后截断 | 控制边界，不保证内部格式正确 |

## Greedy、sampling、beam

| 解码方式 | 说明 | 适用 |
|---|---|---|
| Greedy | 每步选最高概率 token | 稳定抽取、代码、低创造性任务 |
| Sampling | 按概率随机选 token | 创作、对话、多样候选 |
| Beam search | 保留多个候选序列 | 翻译、短答案、确定性生成；LLM 聊天不一定更好 |

## 为什么 stop 不等于结构化输出

`stop` 只能告诉服务端“遇到某个字符串就停”。它不能保证：

- JSON 括号闭合。
- 字段类型正确。
- 枚举值合法。
- 数组长度符合要求。
- 模型不会在 stop 前输出解释性文字。

因此生产 JSON/工具调用应优先使用 grammar、JSON schema、guided decoding 或框架的 structured outputs。

## 结构化输出的原理

结构化输出通常在每一步 decode 时根据 grammar/schema 计算“下一步允许哪些 token”，把不合法 token 的概率屏蔽掉。它比 prompt 约束更强，因为非法 token 从采样集合中直接消失。

常见约束形式：

- JSON Schema：适合 API 返回、工具调用、数据抽取。
- Grammar / GBNF：适合 DSL、代码片段、协议格式。
- Regex / choice：适合短字段、枚举、分类。
- Guided decoding backend：框架内部把 schema/grammar 编译成 token 级约束。

代价：

- 解码开销增加。
- 复杂 schema 可能降低吞吐。
- 某些采样/beam/speculative decoding 组合可能不兼容。
- tokenizer 边界会让 schema 约束实现更复杂。

## 调参建议

- 稳定 JSON：低温度 + JSON schema/guided decoding。
- 多样创作：提高 temperature，放宽 top_p，谨慎用 repetition penalty。
- 代码生成：低温度，适中 top_p，必要时 grammar 限制语言片段。
- 长答案复读：先调 repetition penalty，再检查 prompt 是否要求重复。
- 可复现实验：固定 seed、采样参数、模型版本、tokenizer 和服务框架。

## 关键来源

- vLLM Structured Outputs: https://docs.vllm.ai/en/stable/features/structured_outputs.html
- SGLang Structured Outputs: https://docs.sglang.io/docs/advanced_features/structured_outputs
- llama.cpp server README: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- llama.cpp grammars: https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md
- Ollama Modelfile parameters: https://docs.ollama.com/modelfile
- OpenVINO GenAI inference docs: https://docs.openvino.ai/2025/openvino-workflow-generative/inference-with-genai.html
