---
type: Concept
title: Hugging Face TEI 参数模型
description: Hugging Face Text Embeddings Inference (TEI) 是面向 embedding、rerank 和 sequence-classification
  类 encoder 推理的专用服务。它和 TGI 的定位不同：TGI 主要服务生成式文本模型，TEI 主要服务“输入文本到向量/分数”的模型，没有逐 token
  deco...
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Hugging Face TEI 参数模型

Hugging Face Text Embeddings Inference (TEI) 是面向 embedding、rerank 和 sequence-classification 类 encoder 推理的专用服务。它和 TGI 的定位不同：TGI 主要服务生成式文本模型，TEI 主要服务“输入文本到向量/分数”的模型，没有逐 token decode 循环，也没有采样参数。

## 参数分组

| 参数族 | 代表参数 | 原理与影响 |
|---|---|---|
| 模型来源 | `--model-id`、`--revision` | 控制 Hugging Face Hub / 本地模型与版本；生产应固定 revision |
| 服务模型名 | `--served-model-name` | API 对外暴露的模型名；可与真实模型 id 分离 |
| 加载安全 | `--trust-remote-code` | 是否执行模型仓库自定义代码；安全边界参数 |
| 私有模型 | `--hf-token` | 拉取 gated/private 模型；不要使用旧参数名或把 token 写入日志 |
| 精度 | `--dtype` | 控制权重/计算精度；影响显存、吞吐和硬件兼容 |
| Pooling | `--pooling` | 把 token-level hidden states 聚合成句向量；必须匹配模型训练方式 |
| Prompt 前缀 | `--default-prompt-name`、`--default-prompt` | 给 query/passages 自动加前缀；影响检索质量 |
| 批处理 | `--max-batch-tokens`、`--max-batch-requests` | 控制服务端 batch 的 token 和请求上限 |
| 客户端批量 | `--max-client-batch-size` | 限制单次 API 请求里包含多少输入 |
| 并发与背压 | `--max-concurrent-requests` | 控制同时进入服务的请求数，防止排队和内存膨胀 |
| Tokenization | `--tokenization-workers` | tokenization 是 embedding 服务常见 CPU 瓶颈 |
| 截断 | `--auto-truncate` | 输入超过模型长度时是否自动截断；质量风险要显式评估 |
| 网络/API | `--hostname`、`--port`、`--payload-limit`、`--api-key`、`--cors-allow-origin` | 控制监听地址、请求体上限、鉴权和跨域 |
| 观测 | `--prometheus-port`、`--otlp-endpoint`、`--disable-spans`、`--json-output` | 控制 metrics、tracing 和日志格式 |

TEI 的性能主旋钮通常不是“并发越大越好”，而是 `max-batch-tokens`、tokenization worker、输入长度和 pooling/输出带宽之间的平衡。`--max-client-batch-size` 限制的是客户端单请求里能塞多少条输入，不等于服务端最终形成的 engine batch。

## Embedding 与 Rerank 的差别

| 任务 | 输入形状 | 输出 | 主要成本 |
|---|---|---|---|
| Embedding | 多条文本 | dense/sparse 向量 | encoder 前向、pooling、向量输出 |
| Rerank | query-document pairs | 分数 | pair 数量乘以 pair token 长度 |
| Classification | 文本或 pair | label/logit/score | encoder + head 计算 |

Rerank 的成本常被候选文档数放大。RAG 系统里“召回 top 100 再全量 rerank”可能让 reranker 成为主要延迟来源。

## Pooling 与 Prompt 为什么是质量参数

Embedding 模型不是只要维度对就能用。质量常取决于：

- `mean`、`cls`、`last-token` 等 pooling 是否匹配训练配置。
- query/passages 是否需要不同 prompt 前缀。
- 输出向量是否需要 normalize。
- 模型 revision、tokenizer 和 prompt 名是否固定。

如果漏掉 query prompt，召回质量可能明显下降，但监控上只会看到“服务正常返回向量”。所以 TEI 的参数页应把 pooling/prompt 当作质量关键项，而不是只当格式字段。

`--pooling` 会覆盖 Sentence Transformers 模型中的 `1_Pooling/config.json`。`--default-prompt-name` 和 `--default-prompt` 是互斥方向：前者引用模型配置里的 prompt，后者直接指定默认 prompt 文本。

## 调参判断

| 症状 | 可能原因 | 优先动作 |
|---|---|---|
| GPU 很空但延迟高 | tokenization worker 或请求批量太小 | 增加 `--tokenization-workers`、`--max-batch-tokens`，合并小请求 |
| OOM 或延迟尖刺 | batch token 上限太高，长输入太多 | 降低 `--max-batch-tokens`，限制输入长度 |
| 向量质量差 | pooling、prompt、normalize 或 revision 错配 | 对齐模型卡说明，固定 prompt/pooling/revision |
| Rerank 很慢 | pair 数量过多或文档过长 | 限制候选数、pair 最大长度，先粗排再精排 |
| 客户端一次请求过大 | `max-client-batch-size` 太宽 | 限制客户端批量，服务端做均匀 batching |
| 输入过长导致质量不可解释 | `--auto-truncate` 静默截断 | 重要业务关闭自动截断，让超长输入显式失败 |
| 私有模型拉取失败 | token 参数或镜像环境不匹配 | 使用当前 `--hf-token`，并确认容器环境变量传入方式 |

## 与其他页面的关系

- [Embedding、Reranker 与 Encoder 推理](embedding-and-reranker-inference.md)：任务层原理。
- [推理负载建模与压测数据集](workload-modeling-and-load-testing.md)：embedding/rerank 要按 samples/s、pairs/s 建模。
- [推理成本与效率模型](inference-cost-and-efficiency.md)：向量输出、pair 数量和 batch 影响成本。
- [OpenAI-compatible API 语义与兼容边界](openai-compatible-api-semantics.md)：embedding/rerank endpoint 的兼容边界。

## 关键来源

- Hugging Face TEI documentation: https://huggingface.co/docs/text-embeddings-inference/en/index
- Hugging Face TEI CLI arguments: https://huggingface.co/docs/text-embeddings-inference/en/cli_arguments
- TEI reranker README: https://github.com/huggingface/text-embeddings-inference#using-re-rankers-models
- TEI repository: https://github.com/huggingface/text-embeddings-inference
- TEI supported models and hardware: https://huggingface.co/docs/text-embeddings-inference/en/supported_models
- TEI router source: https://github.com/huggingface/text-embeddings-inference/blob/main/router/src/main.rs
- TEI dtype source: https://github.com/huggingface/text-embeddings-inference/blob/main/backends/src/dtype.rs
