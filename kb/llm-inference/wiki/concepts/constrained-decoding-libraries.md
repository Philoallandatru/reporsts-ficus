---
type: Concept
title: 结构化解码库生态
description: 结构化解码的目标是让模型输出满足格式约束，例如 JSON schema、regex、CFG、choice list、tool call schema。它和
  prompt engineering 不同：prompt 是“请求模型遵守”，结构化解码是在 token 选择阶段把不合法 token 排除。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 结构化解码库生态

结构化解码的目标是让模型输出满足格式约束，例如 JSON schema、regex、CFG、choice list、tool call schema。它和 prompt engineering 不同：prompt 是“请求模型遵守”，结构化解码是在 token 选择阶段把不合法 token 排除。

## 两类实现

| 类型 | 代表 | 工作方式 |
|---|---|---|
| Engine 内置 | vLLM guided decoding、SGLang structured outputs、llama.cpp GBNF | serving engine 在采样阶段约束 token |
| 外部库 | Outlines、Guidance、LM Format Enforcer、XGrammar | 构建 regex/CFG/schema 状态机或 logits processor，接入不同模型后端 |

内置方案通常更容易获得高吞吐和 streaming 集成；外部库更适合应用侧复杂控制、实验和跨后端一致性。

## 常见约束形式

| 约束 | 适合场景 | 风险 |
|---|---|---|
| JSON mode | 只要求合法 JSON | 字段可能缺失或类型错 |
| JSON Schema | API 参数、工具调用、抽取 | schema 过复杂会变慢 |
| Regex | id、日期、短格式 | tokenizer 与字符边界可能不直观 |
| CFG / grammar | DSL、SQL 子集、嵌套结构 | grammar 编写和调试成本高 |
| Choice / enum | 分类、路由、短答案 | 候选太多时开销上升 |

## 库对照

| 库 | 重点能力 | 典型接入 |
|---|---|---|
| Outlines | regex、JSON schema、choice、typed generation | Transformers、vLLM、llama.cpp 等后端 |
| Guidance | 模板式控制流、select、regex、JSON、tool-like generation | Python 应用内控制生成流程 |
| LM Format Enforcer | JSON schema / regex prefix filtering | Transformers、vLLM、llama.cpp、LangChain 等集成 |
| XGrammar | 高性能结构化生成、grammar compiler、token mask | MLC、vLLM、SGLang、TensorRT-LLM 等生态 |
| llama.cpp GBNF | 本地 grammar / JSON schema 到 grammar | `llama-server` / llama.cpp |
| vLLM structured outputs | `structured_outputs`、choice、regex、JSON、grammar、structural tag | OpenAI-compatible serving；新版后端以 xgrammar/guidance 为主 |
| SGLang structured outputs | constrained decoding、regex、JSON、EBNF、grammar backend | SGLang runtime；官方建议 XGrammar 作为主要 backend |

## 性能原理

结构化解码每一步都要根据当前前缀判断哪些 token 合法：

```text
next_token_candidates = vocabulary - invalid_tokens(prefix, grammar_state)
```

开销来自：

- grammar/schema 编译。
- 每步 token mask 计算。
- tokenizer 的字节/字符/token 边界。
- batch 内不同请求的不同 grammar 状态。
- streaming 时的增量校验。

简单 enum/regex 通常很轻；深层 JSON schema、复杂 CFG、多请求不同 schema 会影响吞吐。

vLLM 旧的 `guided_*` 字段正在迁移到 `structured_outputs` 形式；维护知识库时应优先记录新版请求形状，历史字段只作为兼容说明。SGLang 的 grammar backend 可选 XGrammar、Outlines、llguidance 等，生产默认选择要按版本文档确认。

## 调参判断

| 症状 | 可能原因 | 处理 |
|---|---|---|
| 输出仍不合法 | 只是 prompt 约束，没有启用 guided decoding | 使用 JSON schema / grammar / regex 约束 |
| 生成很慢 | schema 太复杂、batch 内 grammar 状态分散 | 简化 schema、按 schema 分桶、缓存 grammar compiler |
| 模型拒绝输出某字段 | schema 与 prompt 冲突，或字段描述不清 | 对齐 prompt 和 schema；减少可选字段歧义 |
| stop 提前触发 | stop/eos 与 grammar 边界冲突 | 检查 stop strings、EOS token、JSON 结尾 |
| 不同后端结果差异 | tokenizer 或 guided backend 不同 | 固定 tokenizer，做小样本一致性测试 |

## 与 tool calling 的关系

Tool/function calling 通常也是结构化输出，只是 schema 表示的是函数名和参数。区别在于：

- tool calling 还需要 parser 把模型输出转成工具调用对象。
- JSON schema guided decoding 只能保证形状，不能保证工具语义正确。
- 多工具场景要约束工具名，也要让 prompt/template 正确呈现工具列表。

## 关键来源

- vLLM Structured Outputs: https://docs.vllm.ai/en/stable/features/structured_outputs.html
- SGLang Structured Outputs: https://docs.sglang.io/docs/advanced_features/structured_outputs
- llama.cpp grammars: https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md
- Outlines documentation: https://dottxt-ai.github.io/outlines/latest/
- Outlines GitHub: https://github.com/dottxt-ai/outlines
- Guidance GitHub: https://github.com/guidance-ai/guidance
- LM Format Enforcer GitHub: https://github.com/noamgat/lm-format-enforcer
- XGrammar documentation: https://xgrammar.mlc.ai/docs/
- XGrammar GitHub: https://github.com/mlc-ai/xgrammar
- vLLM latest Structured Outputs: https://docs.vllm.ai/en/latest/features/structured_outputs/
- OpenAI Structured Outputs: https://developers.openai.com/api/docs/guides/structured-outputs
