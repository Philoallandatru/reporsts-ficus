---
type: Concept
title: Speculative decoding
description: Speculative decoding 用较便宜的方法先猜多个 token，再由主模型一次验证。它试图减少主模型自回归 decode 的步数，而不改变目标模型的输出分布或尽量保持一致。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Speculative decoding

Speculative decoding 用较便宜的方法先猜多个 token，再由主模型一次验证。它试图减少主模型自回归 decode 的步数，而不改变目标模型的输出分布或尽量保持一致。

## 基本流程

```text
prompt
  -> draft model 猜 K 个 token
  -> target model 并行验证这些 token
  -> 接受前缀中通过验证的 token
  -> 拒绝处由 target model 修正
  -> 继续下一轮
```

收益来自“target model 一次 forward 验证多个候选 token”。如果 draft 猜得准，就能少跑很多 target decode step；如果猜得差，额外 draft 计算会抵消收益。

## 常见变体

| 变体 | 思路 | 适用场景 |
|---|---|---|
| Draft-target | 小模型作为 draft，大模型验证 | 有同族小模型，接受率高 |
| Medusa | 在模型上加多个预测 head | 有专门 Medusa head 的模型 |
| EAGLE | 用特征/隐藏状态辅助预测未来 token | 高性能 serving 框架支持时 |
| N-gram speculation | 从上下文中匹配重复 n-gram | 代码、模板、重复文本 |
| Lookahead | 在解码路径中前瞻候选 | 特定框架实现 |

Draft-target speculative sampling 的理论目标是保持 target model 分布：draft 只是提出候选，最终接受/拒绝由 target model 概率校正。Medusa 和 EAGLE 则把“草稿生成器”做进或贴近主模型，减少额外小模型带来的部署复杂度。

## 关键参数

| 参数族 | 含义 |
|---|---|
| draft model | 草稿模型路径、dtype、并行配置 |
| draft token 数 | 每轮预测多少候选 token |
| acceptance / verification | 验证策略和采样一致性 |
| draft KV cache | 草稿模型也需要自己的 cache 预算 |
| fallback | 猜错时回退到 target model 的策略 |

## 什么时候有用

更可能有效：

- 代码补全、模板输出、重复上下文。
- draft model 与 target model 同族且质量接近。
- 单请求/小 batch decode latency 是瓶颈。
- target model 很大，draft model 很便宜。

不一定有效：

- 高温度创作，token 分布很散。
- draft 模型太弱，接受率低。
- batch 已经很大，GPU 被 target model 吃满。
- draft 和 target 的 tokenizer/template 不一致。

## 调参建议

- 从小的 draft token 数开始，例如 2-4，再看接受率和 TPOT。
- 只看 tokens/s 不够，还要看 TTFT、TPOT、GPU 利用率和质量。
- 对结构化输出要验证 grammar/guided decoding 与 speculation 是否兼容。
- 多 GPU 场景下，draft model 的放置也会影响通信和显存。

## 关键来源

- vLLM Speculative Decoding: https://docs.vllm.ai/en/stable/features/spec_decode/
- SGLang speculative decoding: https://docs.sglang.io/docs/advanced_features/speculative_decoding
- TensorRT-LLM Speculative Decoding: https://nvidia.github.io/TensorRT-LLM/advanced/speculative-decoding.html
- TGI Speculation: https://huggingface.co/docs/text-generation-inference/conceptual/speculation
- Speculative Sampling paper: https://arxiv.org/abs/2302.01318
- Medusa paper: https://arxiv.org/abs/2401.10774
- EAGLE repo and papers: https://github.com/SafeAILab/EAGLE
