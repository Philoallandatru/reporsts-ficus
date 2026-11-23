---
type: Concept
title: Logits Processor、惩罚项与长度控制
description: 采样页解释“如何从概率分布里选 token”，这一页聚焦选 token 之前发生的事：logits processor / logits
  warper 会修改候选 token 的分数，长度参数会决定生成何时停止。这些参数经常被误当成“风格旋钮”，但它们实际改变的是每一步 decode 的候选集合和概率形状。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Logits Processor、惩罚项与长度控制

采样页解释“如何从概率分布里选 token”，这一页聚焦选 token 之前发生的事：logits processor / logits warper 会修改候选 token 的分数，长度参数会决定生成何时停止。这些参数经常被误当成“风格旋钮”，但它们实际改变的是每一步 decode 的候选集合和概率形状。

## Decode 单步流水线

典型顺序可以抽象成：

```text
model logits
  -> logits processors: bad words, no-repeat ngram, repetition penalty, logit bias
  -> logits warpers: temperature, top_k, top_p, min_p
  -> token selection: greedy / sampling / beam
  -> stop/eos/length check
```

不同框架的顺序和命名不完全一样。迁移服务时，不能只对齐 `temperature` 和 `top_p`，也要对齐 penalty、stop、eos、chat template 和默认 sampler 顺序。

## 参数族

| 参数族 | 作用位置 | 原理 | 常见风险 |
|---|---|---|---|
| `temperature` | logits warper | 缩放 logits，改变分布尖锐度 | 高温幻觉增加；低温不等于完全确定 |
| `top_k` / `top_p` / `min_p` | logits warper | 裁剪候选 token 集合 | 过窄会模板化，过宽会不稳定 |
| repetition penalty | logits processor | 对已出现 token 重新缩放分数 | 过强会破坏术语、代码、JSON key |
| presence / frequency penalty | logits processor | 按是否出现或出现频次降低 token 倾向 | 容易让模型绕开应重复的实体名 |
| `no_repeat_ngram_size` | logits processor | 禁止重复 n-gram | 对摘要有效，对代码/表格可能误伤 |
| `bad_words_ids` / suppress tokens | logits processor | 屏蔽指定 token | tokenizer 切分不当会漏掉或误屏蔽 |
| `logit_bias` | logits processor | 对指定 token 加减偏置 | token ID 依赖 tokenizer，跨模型不可直接复用 |
| watermark | logits processor | 有意偏置一部分 token 以便检测 | 会改变分布，可能影响质量和兼容性 |
| `max_tokens` / `max_new_tokens` | 停止条件 | 限制输出 token 数 | 与 reasoning token、tool schema、JSON 闭合互相竞争 |
| `min_tokens` / `min_new_tokens` | 停止条件 | 在达到最小长度前抑制 EOS | 可能强迫模型继续输出废话 |
| stop sequences | 停止条件 | 命中特定字符串后截断 | 不保证结构合法，且字符串边界受 tokenizer 影响 |

## Penalty 的直觉

Penalty 会把“模型本来想说什么”改成“系统允许它更想说什么”。它适合轻度控制复读，但不是事实性或格式控制工具。

- repetition penalty 更像“已经出现过的 token 不要再这么容易出现”。
- presence penalty 更像“出现过一次就降低继续出现的倾向”。
- frequency penalty 更像“出现越多，惩罚越强”。
- `no_repeat_ngram_size` 是硬约束，命中后对应候选直接不可选。
- Transformers 的 repetition penalty 中，`1.0` 表示不惩罚，`>1.0` 惩罚重复，`0` 到 `1.0` 反而会奖励重复；decoder-only 模型默认会把 prompt token 也算进“已经出现过”的范围。

如果输出是 JSON、代码、SQL、正则或固定协议，惩罚项太强会伤害重复字段名、括号、缩进和关键字。此时应优先用 grammar/schema，而不是靠 penalty 逼格式。

## 长度控制的隐藏成本

长度参数同时影响质量、延迟、KV cache 和计费：

- `max_tokens` 越大，最坏情况下连接、KV cache 和 decode slot 占用越久。
- `min_tokens` 可能阻止模型及时输出 EOS，使短答任务变慢。
- beam search、多候选和 `best_of` 会复制候选序列，显存不能只按用户请求数估算。
- reasoning/thinking 模型中，内部 reasoning token 和最终答案可能共享同一输出预算。

## 框架映射

| 框架 | 相关字段 |
|---|---|
| Hugging Face Transformers | `GenerationConfig`、`LogitsProcessorList`、`repetition_penalty`、`no_repeat_ngram_size`、`bad_words_ids`、`min_new_tokens`、`max_new_tokens`、`WatermarkLogitsProcessor` |
| vLLM | `SamplingParams` 中的 `temperature`、`top_p`、`top_k`、`min_p`、`presence_penalty`、`frequency_penalty`、`repetition_penalty`、`length_penalty`、`logit_bias`、`max_tokens`、`min_tokens`、`stop` |
| llama.cpp | `--samplers`、`--temperature`、`--top-k`、`--top-p`、`--min-p`、`--typical-p`、`--repeat-penalty`、`--repeat-last-n`、`--presence-penalty`、`--frequency-penalty`、DRY/XTC/Mirostat、`--grammar`、`--json-schema` |
| OpenAI-compatible APIs | `temperature`、`top_p`、`frequency_penalty`、`presence_penalty`、`logit_bias`、`max_tokens` / `max_completion_tokens`、`stop` | 
| OpenVINO GenAI | `GenerationConfig` 中的 beam、sampling、length、stop 相关字段 |
| ONNX Runtime GenAI | `SearchOptions` / generator params 中的 sampling、beam 和 length 字段 |

## 调参建议

1. 先固定 tokenizer、chat template、stop/eos，再调 penalty。
2. 复读问题先小幅调 repetition penalty；如果是 prompt 要求重复，就改 prompt。
3. JSON/tool 输出优先用 schema/grammar；penalty 只做轻微辅助。
4. 长答案质量差时，不要只加 `max_tokens`，先看是否过早 stop 或 context 被挤爆。
5. 对成本敏感服务，把 `max_tokens` 当 admission control 的一部分。
6. 只调 `temperature` 或 `top_p` 之一作为主旋钮；两者同时大幅变化会让问题难以归因。

## 关键来源

- Hugging Face Transformers generation: https://huggingface.co/docs/transformers/en/main_classes/text_generation
- Hugging Face generation utilities: https://huggingface.co/docs/transformers/en/internal/generation_utils
- vLLM SamplingParams API: https://docs.vllm.ai/en/stable/api/vllm/sampling_params.html
- llama.cpp server README: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- OpenAI Completions API reference: https://developers.openai.com/api/reference/resources/completions/methods/create/
- OpenVINO GenAI inference docs: https://docs.openvino.ai/2025/openvino-workflow-generative/inference-with-genai.html
