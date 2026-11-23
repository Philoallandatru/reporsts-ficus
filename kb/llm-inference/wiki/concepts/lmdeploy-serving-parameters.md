---
type: Concept
title: LMDeploy Serving 参数模型
description: LMDeploy 是 OpenMMLab/InternLM 生态的压缩、部署和服务工具，常见在线入口是 `lmdeploy serve api_server`。它支持
  OpenAI-compatible API，并通过 TurboMind 或 PyTorch backend 管理模型、KV cache 和 batch。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# LMDeploy Serving 参数模型

LMDeploy 是 OpenMMLab/InternLM 生态的压缩、部署和服务工具，常见在线入口是 `lmdeploy serve api_server`。它支持 OpenAI-compatible API，并通过 TurboMind 或 PyTorch backend 管理模型、KV cache 和 batch。

## 参数分组

| 类别 | 常用参数 | 原理与影响 |
|---|---|---|
| 服务入口 | `lmdeploy serve api_server MODEL`、`--server-port`、`--server-name`、`--model-name` | 暴露 OpenAI-compatible endpoint |
| backend | `--backend turbomind|pytorch`、`--model-format` | TurboMind 偏高性能 serving，PyTorch backend 更贴近 HF 模型生态 |
| 并行 | `--tp` | Tensor parallel GPU 数量 |
| 上下文 | `--session-len` / `session_len` | 单 sequence 最大上下文/会话长度 |
| KV cache | `--cache-max-entry-count` / `cache_max_entry_count`、`block_size`、`cache_block_seq_len`、`cache_chunk_size` | 控制 KV cache 占 GPU 显存比例和 block 分配 |
| batch | `max_batch_size`、`prefill_interval` | 推理最大 batch 和 prefill 调度间隔 |
| prefix cache | `enable_prefix_caching` | 复用相同 prompt/prefix 的 cache block |
| KV 量化 | `quant_policy` | 例如 KV 8-bit 量化策略 |

## 关键参数原理

### `--tp`

Tensor parallel 会把模型权重和计算拆到多张 GPU。适合模型单卡放不下或单卡延迟过高时使用。通信开销随 GPU 拓扑变化很大，PCIe 环境下不要盲目拉高。

### `--session-len`

LMDeploy 的 session length 类似其他框架的上下文窗口上限。它决定一个会话可容纳多少 token，同时推动 KV cache 上限。服务 RAG/长文档时要显式设置，并配合 cache 占比调优。

### `--cache-max-entry-count`

官方文档把它描述为调整 GPU memory ratio for K/V cache；API 文档中也说明新版语义是使用 free GPU memory 的比例。值越大，可缓存的 KV token 越多；值越小，显存更稳但并发和长上下文下降。

### `block_size` / `cache_block_seq_len`

分页 KV cache 的 block 粒度。较小 block 有利于减少碎片，较大 block 可能减少管理开销。通常不作为第一优先级调参，除非你在做长上下文或高并发压测。

### `enable_prefix_caching`

当多个请求共享系统 prompt、few-shot 示例或 RAG 模板时，prefix caching 能减少重复 prefill。收益取决于前缀重复程度。

## 调参建议

- 单卡服务：先设置合理 `--session-len`，再用 `--cache-max-entry-count` 找最大稳定并发。
- 多卡服务：`--tp` 从 2 开始压测，确认通信收益大于开销。
- 长上下文：降低 `max_batch_size` 或 cache 占比，避免 session length 与并发同时拉满。
- 生产服务：固定 `model-name`，避免客户端因模型名变化无法复用。

## 关键来源

- LMDeploy API server: https://lmdeploy.readthedocs.io/en/latest/llm/api_server.html
- LMDeploy pipeline API: https://lmdeploy.readthedocs.io/en/v0.6.0/api/pipeline.html
