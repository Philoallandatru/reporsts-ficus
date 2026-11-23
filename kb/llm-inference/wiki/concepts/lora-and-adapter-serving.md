---
type: Concept
title: LoRA 与 adapter serving
description: LoRA / adapter serving 允许同一个基础模型承载多个微调行为。它节省权重显存和部署数量，但会引入 adapter 加载、rank
  限制、合批兼容、缓存和多租户隔离问题。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# LoRA 与 adapter serving

LoRA / adapter serving 允许同一个基础模型承载多个微调行为。它节省权重显存和部署数量，但会引入 adapter 加载、rank 限制、合批兼容、缓存和多租户隔离问题。

## LoRA 推理原理

LoRA 把某些线性层的增量权重表示为低秩矩阵：

```text
W' = W + scale * A * B
```

推理时基础权重 `W` 共享，adapter 的 `A/B` 按请求选择。多个 adapter 同时服务时，框架要么把 LoRA 运算融合进 kernel，要么按 adapter 分组/拆批。

## 关键参数

| 参数族 | 含义 |
|---|---|
| enable lora | 是否启用 LoRA 路径 |
| max loras | 一个 batch 或实例中可同时活跃的 adapter 数 |
| max lora rank | 支持的最大 rank；rank 越高，adapter 计算/显存越高 |
| lora dtype | adapter 权重 dtype |
| fully sharded loras | TP 场景下 LoRA 是否随主权重分片 |
| adapter cache | 动态加载 adapter 时的缓存容量和 eviction |

vLLM 的关键边界是 `--max-loras`、`--max-lora-rank`、`--max-cpu-loras`、`--lora-dtype` 和 `--fully-sharded-loras`。SGLang 则暴露 `--max-loras-per-batch`、`--max-loaded-loras`、`--lora-eviction-policy`、`--lora-backend` 等更明确的 adapter pool 控制。调参时不要只看“能加载几个 adapter”，还要看同一 batch 中能混多少 adapter。

## 合批风险

同一基础模型但不同 adapter 的请求不一定能完美合批：

- 不同 adapter 需要不同 LoRA 权重参与计算。
- 不同 rank 可能导致 kernel shape 不一致。
- 多 adapter 同 batch 会增加额外 gather / matmul / fusion 开销。
- 结构化输出、采样参数、工具调用也可能进一步降低合批效率。

## 与量化/并行的关系

- 权重量化基础模型后，LoRA adapter 通常仍可用，但 kernel 是否高效取决于框架。
- TP 下 LoRA 权重要和基础权重切分策略匹配；否则会出现额外通信。
- PP 下 adapter 需要按层分布到对应 stage。
- 多租户动态 LoRA 要限制 adapter 来源和大小，避免任意文件加载。

## 调参建议

- 生产先限制 `max_loras` 和 `max_lora_rank`，防止 adapter 爆炸。
- 热门 adapter 常驻；冷门 adapter 走动态加载和缓存。
- 如果 adapter 很多，按 adapter 分组路由可能比一个实例混跑更稳。
- 每次新增 adapter 都要做质量和延迟回归；LoRA 不是无成本配置。

## 关键来源

- vLLM LoRA: https://docs.vllm.ai/en/stable/features/lora.html
- vLLM Serve CLI: https://docs.vllm.ai/en/stable/cli/serve/
- SGLang LoRA: https://docs.sglang.io/docs/advanced_features/lora.md
- TensorRT-LLM LoRA: https://nvidia.github.io/TensorRT-LLM/features/lora.html
- llama.cpp server README: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- llama.cpp models: https://github.com/ggml-org/llama.cpp/blob/master/docs/models.md
- Ollama Modelfile: https://docs.ollama.com/modelfile
