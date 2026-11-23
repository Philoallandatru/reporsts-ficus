---
type: Concept
title: 推理排障手册
description: 推理问题最容易被误判为“模型慢”或“显存不够”。实际排障要先把问题拆成加载、tokenization、prefill、decode、KV
  cache、网络/存储和输出质量几个阶段。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 推理排障手册

推理问题最容易被误判为“模型慢”或“显存不够”。实际排障要先把问题拆成加载、tokenization、prefill、decode、KV cache、网络/存储和输出质量几个阶段。

## 快速定位

| 症状 | 首先看 | 常见原因 |
|---|---|---|
| 启动失败 | 模型加载日志、权重格式、revision | `trust_remote_code`、dtype/quant 不支持、显存不足 |
| 长 prompt OOM | 输入 token、KV cache usage、prefill batch | context 太大、KV dtype 太大、chunked prefill 未开 |
| TTFT 高 | queue time、prefill time、prefix cache hit | 排队、长 prompt、模板变化导致 cache miss |
| TPOT 高 | decode batch、GPU 利用率、attention backend | batch 太小/太大、kernel 不匹配、offload |
| p99 抖动 | queue depth、KV eviction、CUDA graph hit | admission control 过宽、cache thrashing、未 warmup |
| 输出格式错 | chat template、stop、guided decoding | 模板错配、采样太松、schema/parser 不一致 |

## OOM 分型

### 模型加载 OOM

特征：刚启动或加载权重时失败。

处理顺序：

1. 降低权重精度或使用量化模型。
2. 增加 tensor parallel / pipeline parallel。
3. 降低 `gpu-memory-utilization` 以给 runtime 留 headroom。
4. 检查是否同卡已有其他进程。
5. 必要时启用 CPU offload，但要接受延迟上升。

### 长 prompt / prefill OOM

特征：短请求正常，长输入或大 batch 失败。

处理顺序：

1. 降低 `max_model_len` / `ctx-size` / `session-len`。
2. 开启或缩小 chunked prefill。
3. 降低 `max_num_batched_tokens`、`max-batch-prefill-tokens` 或数据层 `batch_size`。
4. 把超长样本分桶单独处理。

### 并发 OOM

特征：单请求正常，并发升高后失败。

处理顺序：

1. 降低 `max_num_seqs`、`max-running-requests`、`parallel`。
2. 降低 KV cache dtype。
3. 增加 KV cache pool 或降低上下文上限。
4. 检查 beam、best_of、多候选输出是否扩大了活跃 sequence。

## Cache thrashing

Cache thrashing 指 KV/prefix cache 频繁分配、淘汰、回填，导致显存占用看似正常但 TTFT/p99 变差。

信号：

- prefix cache hit rate 突然下降。
- KV eviction 或 offload hit/miss 波动。
- 长 prompt 请求进入后，短请求 TTFT 也变差。
- 分离式服务中 KV load/transfer 失败或重试变多。

处理：

1. 固定 tokenizer、chat template、system prompt 和 tool schema 顺序。
2. 对长短请求分池或分队列。
3. 限制最大上下文和最大排队请求。
4. 对 RAG/agent 公共前缀使用 prefix cache，但注意多租户 hash 隔离。
5. 对分离式架构检查 connector compatibility、KV role 和 failure policy。

## Tokenizer / chat template mismatch

特征：模型能运行，但回答角色错乱、tool call 格式漂移、stop 不生效、输出质量显著低于预期。

检查：

- 训练时使用的 chat template 是否和服务端一致。
- special tokens 是否重复添加或漏加。
- tool schema 是否在模板中以模型预期方式呈现。
- batch/offline 任务是否和线上服务使用相同模板。
- tokenizer revision 是否和权重 revision 一致。

不要先调 `temperature`。模板错配时，采样越收紧只是更稳定地产生错误格式。

## Graph / JIT / warmup 问题

很多运行时会使用 CUDA Graph、`torch.compile`、Triton 或 TensorRT engine。它们对 batch shape、sequence length 和 dtype 更敏感。

信号：

- 启动后前几批明显慢。
- 某些 batch shape 延迟尖刺。
- 升级模型或框架后 p99 变差，平均值变化不大。

处理：

1. 做覆盖真实长度分布的 warmup，而不只是短 prompt。
2. 检查 CUDA graph capture sizes 或 framework 推荐的 graph 参数。
3. 分桶输入长度，减少 shape 抖动。
4. 出现奇怪崩溃时先关掉 graph/JIT 验证是否相关。

## MoE imbalance

MoE 模型的慢不一定来自总参数量，而可能来自专家路由不均或 all-to-all。

信号：

- GPU 间利用率差异大。
- expert parallel 打开后吞吐没有提升。
- 网络 all-to-all 时间占比高。
- 少数 expert 成为热点。

处理：

1. 检查 expert parallel、data parallel、tensor parallel 的组合。
2. 开启或调优 EPLB / load balancing。
3. 使用 DeepEP 等通信 backend 时确认硬件和版本匹配。
4. 对长上下文 MoE 同时观察 prefill 和 decode，别只看总 tokens/s。

## Offload tail latency

CPU/KV offload 能让模型跑起来，但尾延迟常被 PCIe/NVLink/内存带宽放大。

信号：

- 平均延迟可接受，p99 很差。
- GPU 利用率不满，但请求在等待数据搬运。
- 上下文或并发稍增就出现阶梯式变慢。

处理：

1. 优先减少 offload 量，或者降低上下文/并发。
2. 使用 pinned memory、合适的 chunk/block 大小。
3. 监控 offload hit/miss 和传输时间。
4. 如果 offload 只是为了装下权重，优先考虑量化或更多 GPU。

## 最小复现模板

每个问题至少记录：

- 模型名、revision、权重格式、dtype、量化方式。
- 框架版本、启动参数、硬件和驱动。
- tokenizer 和 chat template 版本。
- 输入 token 长度分布、输出长度、并发/QPS。
- TTFT、TPOT、p95/p99、显存、错误日志。
- 是否开启 prefix cache、chunked prefill、CUDA graph、offload、LoRA、MoE parallel。

## 关键来源

- vLLM Troubleshooting: https://docs.vllm.ai/en/stable/usage/troubleshooting/
- vLLM Production Metrics: https://docs.vllm.ai/en/stable/design/metrics/
- vLLM CUDA Graphs: https://docs.vllm.ai/en/stable/design/cuda_graphs/
- vLLM torch.compile: https://docs.vllm.ai/en/latest/design/torch_compile/
- SGLang Hyperparameter Tuning: https://docs.sglang.io/docs/advanced_features/hyperparameter_tuning
- TensorRT-LLM Telemetry: https://nvidia.github.io/TensorRT-LLM/developer-guide/telemetry.html
- TensorRT-LLM KV Cache System: https://nvidia.github.io/TensorRT-LLM/features/kvcache.html
- Hugging Face Transformers Chat Templates: https://huggingface.co/docs/transformers/en/chat_templating
