---
type: Concept
title: Embedding、Reranker 与 Encoder 推理
description: Embedding 和 reranker 推理的瓶颈与生成式 LLM 不一样。它们通常没有自回归 decode 循环，也没有随着输出 token
  线性增长的 KV cache；主要成本来自 encoder 前向、输入 tokenization、pooling、向量归一化和向量输出带宽。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Embedding、Reranker 与 Encoder 推理

Embedding 和 reranker 推理的瓶颈与生成式 LLM 不一样。它们通常没有自回归 decode 循环，也没有随着输出 token 线性增长的 KV cache；主要成本来自 encoder 前向、输入 tokenization、pooling、向量归一化和向量输出带宽。

## 三类任务

| 任务 | 输出 | 典型用途 | 主要瓶颈 |
|---|---|---|---|
| Embedding | 每条文本一个 dense/sparse 向量 | 召回、聚类、去重、RAG 索引 | batch token 数、pooling、输出向量写入 |
| Rerank / score | query-doc pair 的相关性分数 | RAG 二阶段排序、搜索重排 | pair 数量、cross-encoder 长度、CPU/GPU batch |
| Classification / reward | label 或 scalar reward | 内容分类、偏好模型、guardrail | 输入分布、head 计算、校准 |

Embedding 适合大 batch，因为每条输入之间独立；reranker 常被 pair 数量放大，例如 1 个 query 召回 100 个文档就产生 100 个 pair。

## Pooling 为什么重要

Encoder 输出通常是 token-level hidden states，embedding 服务需要把它压成句向量。常见 pooling：

- `mean`：对有效 token hidden states 求平均，通用且稳定。
- `cls`：取 CLS token，依赖模型训练方式。
- `last-token`：取最后 token，常见于部分 decoder-style embedding model。
- sparse / SPLADE：输出稀疏词项权重，适合 lexical + neural hybrid retrieval。

如果 pooling 与模型训练配置不一致，向量维度可能对，召回质量却明显下降。TEI 支持显式 `--pooling`，也可以从 Sentence Transformers 的 `1_Pooling/config.json` 读取配置。

vLLM 的 pooling 支持适合统一接口和复用同一套 serving 基础设施，但 embedding/rerank 的性能仍要按模型、batch 和硬件实测；不要默认假设它一定快过 TEI、Sentence Transformers 或 OpenVINO 这类专用路径。

## Reranker 的形状成本

Embedding 通常编码 query 和 document 后做向量相似度；reranker/cross-encoder 会把 query 和 document 拼成一段输入再前向。这样质量通常更好，但成本近似随 `query_count * docs_per_query * pair_tokens` 增长。

因此 rerank 服务要重点控制：

- 单 query 最大候选数。
- query 和 document 的最大 token 长度。
- pair 的 batch token 上限。
- 是否启用 truncation，以及截断策略是否保留关键字段。

## 常见参数映射

| 框架 / 工具 | 参数 | 原理与影响 |
|---|---|---|
| vLLM pooling | `task="embed"`、`task="score"`、pooling params | 用同一 engine 运行 embedding、score、reward、classification 等 pooling task |
| Ray Data LLM | `task_type="embed"` / `"score"` | 把 batch 数据集任务路由到对应 vLLM task |
| Hugging Face TEI | `--model-id`、`--revision`、`--dtype` | 控制模型来源、版本和权重精度 |
| Hugging Face TEI | `--pooling`、`--default-prompt-name`、`--default-prompt` | 控制句向量生成方式和 query/passage prompt 前缀 |
| Hugging Face TEI | `--max-batch-tokens`、`--max-batch-requests`、`--max-client-batch-size`、`--max-concurrent-requests` | 控制 token batch、请求 batch、客户端批量和服务背压 |
| Hugging Face TEI | reranker / sequence-classification model | 可服务 cross-encoder reranker，例如 BGE reranker 类模型 |
| Sentence Transformers | `encode(..., batch_size, precision, normalize_embeddings, truncate_dim, device, chunk_size)` | 控制离线 embedding 的批量、量化输出、归一化、维度截断和设备 |
| Sentence Transformers | `backend="torch" / "onnx" / "openvino"`、`model_kwargs` | 控制推理后端、dtype、attention implementation、device map |
| OpenVINO Model Server | OpenAI-compatible `embeddings` endpoint、Cohere-compatible `rerank` endpoint | 在 CPU/GPU 上服务 embedding 与 rerank，用于 RAG 组件 |

## 调参判断

### Embedding 吞吐低

先看 tokenization CPU 是否满，再看 GPU 利用率。如果 GPU 空，增大 `--max-batch-tokens` 或 `batch_size`；如果 GPU 满但吞吐低，降低输入长度、使用更小模型或低精度。

### 向量质量异常

优先检查 prompt 前缀、pooling、normalize 策略和模型 revision。BGE/E5/GTE 等模型常区分 query 与 passage prompt，漏掉前缀会让向量空间偏移。

### Rerank 延迟高

先限制候选文档数和最大 pair 长度，再调 batch。Reranker 的计算量往往是召回阶段的几十倍；不要把“召回 top_k”无脑传给 reranker。

### 内存或网络输出成为瓶颈

Embedding 输出可能很大：`rows * dim * bytes_per_value`。百万级数据集写 float32 向量会很快进入 GB 级，必要时使用 fp16/int8/binary embedding 或 `truncate_dim`，并把输出分区写入。

## 与生成式 LLM 的关键差别

- 没有逐 token decode，所以 `temperature`、`top_p` 这类采样参数通常无关。
- KV cache 不是主要容量项，输入 token batch 和 activation 更重要。
- p99 TTFT 不是核心指标，p99 request latency、samples/s、vectors/s、pair/s 更常用。
- 模板和 pooling 配置比采样更关键。

## 关键来源

- vLLM Embed example: https://docs.vllm.ai/en/stable/examples/pooling/embed/
- vLLM Score example: https://docs.vllm.ai/en/stable/examples/pooling/score/
- vLLM Pooling Models: https://docs.vllm.ai/en/stable/models/pooling_models/
- Hugging Face Text Embeddings Inference: https://huggingface.co/docs/text-embeddings-inference/en/index
- Hugging Face TEI CLI arguments: https://huggingface.co/docs/text-embeddings-inference/en/cli_arguments
- Hugging Face TEI README rerankers: https://github.com/huggingface/text-embeddings-inference#using-re-rankers-models
- Sentence Transformers `SentenceTransformer`: https://www.sbert.net/docs/package_reference/sentence_transformer/model.html
- OpenVINO Model Server embeddings demo: https://docs.openvino.ai/2025/model-server/ovms_demos_embeddings.html
- OpenVINO Model Server rerank demo: https://docs.openvino.ai/2025/model-server/ovms_demos_rerank.html
- OpenVINO GenAI endpoints: https://docs.openvino.ai/2025/model-server/ovms_docs_genai.html
