---
type: Concept
title: Attention kernel 与运行时优化
description: 推理框架的很多“神秘参数”最后都会落到 kernel 和运行时：attention backend 选什么、CUDA Graph 捕获哪些
  batch shape、Triton/FlashAttention/FlashInfer 是否支持当前 dtype、量化 kernel 是否真的快。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Attention kernel 与运行时优化

推理框架的很多“神秘参数”最后都会落到 kernel 和运行时：attention backend 选什么、CUDA Graph 捕获哪些 batch shape、Triton/FlashAttention/FlashInfer 是否支持当前 dtype、量化 kernel 是否真的快。

## 为什么 attention kernel 重要

Decode 阶段每生成一个 token 都要读取历史 KV cache。长上下文和高并发下，attention 往往不是简单的 FLOPs 问题，而是显存带宽、cache layout、block table 查询和 kernel launch overhead 的组合问题。

| 机制 | 解决的问题 | 典型影响 |
|---|---|---|
| FlashAttention | 减少 HBM 读写，做 IO-aware exact attention | prefill/长序列 attention 更快 |
| FlashInfer | 面向 LLM serving 的 prefill/decode/paged KV kernels | decode、paged KV cache、采样等服务场景 |
| xFormers memory efficient attention | 降低 attention 内存占用 | 训练/推理都可能受益 |
| Triton kernels | 快速实现特定形状 fused kernel | 框架可针对模型和硬件定制 |
| CUDA Graph | 捕获固定执行图，减少 launch overhead | decode 小 batch/固定 shape 更明显 |

## FlashAttention

FlashAttention 的核心是减少 attention 过程中对 HBM 的读写，把中间结果更多留在 SRAM/register 中，同时保持 exact attention。推理中它主要影响 prefill 和长序列 attention；decode 的瓶颈还取决于 KV cache layout 和 batch 组织。

## FlashInfer

FlashInfer 更贴近 LLM serving：它提供 paged KV cache、prefill/decode attention、sampling 等 kernel。对于使用 block KV cache 的服务框架，attention backend 必须理解 block table 和不同请求长度，否则理论 batch 很大，实际 kernel 仍然低效。

FlashInfer 的定位不是“另一个 FlashAttention”，而是 serving kernel library / generator：它覆盖 paged/ragged KV cache、decode/prefill/append、MLA、cascade attention、sparse attention 等更贴近线上推理的路径。换句话说，FlashAttention 解决 dense attention IO，FlashInfer 更关注 serving runtime 的 KV layout 和动态请求形状。

## CUDA Graph

CUDA Graph 把一段 GPU work 捕获成图，后续重复回放，减少 CPU launch overhead。它适合 decode 这类大量重复、形状相对稳定的步骤。代价是：

- 需要为捕获形状预留内存。
- 动态 shape 太多时 graph 命中率下降。
- warmup 阶段会变长。
- batch size 上限越大，graph buffer 可能越占显存。

vLLM v1 支持 full / piecewise CUDA Graph，并由运行时 dispatcher 根据 shape 选择模式；`torch.compile` 和 CUDA Graph capture sizes 会共同影响哪些 batch shape 被捕获。SGLang 则把 CUDA Graph 的最大 batch 和 padding 控制暴露成 server 参数。

## 参数映射

| 目标 | 常见参数 |
|---|---|
| 选择 attention backend | `attention-backend`、`--attention-backend`、环境变量 |
| 分开选择 prefill/decode backend | `--prefill-attention-backend`、`--decode-attention-backend` |
| CUDA graph decode | `cuda-graph-max-bs-decode`、`--cuda-graphs`、graph capture batch sizes |
| 禁用 graph / eager debug | `--enforce-eager`、`--disable-cuda-graph` |
| 禁用自定义 kernel | `--disable-custom-kernels` |
| Torch compile | `--enable-torch-compile`、`torch.compile` 相关配置 |
| Triton autotune | `use_triton`、`triton_autotune` |
| Graph 指标 | `--cudagraph-metrics`、telemetry CUDA graph fields |

## 调参建议

- 小 batch decode 慢：检查 CUDA Graph 是否启用，以及捕获 batch size 是否覆盖真实流量。
- 长 prompt prefill 慢：检查 FlashAttention/FlashInfer backend 是否可用，是否被 dtype、GPU 架构或模型结构禁用。
- 量化后不变快：确认低精度 kernel 是否原生支持当前 GPU 和 batch shape。
- OOM 出现在启用 graph 后：降低 graph 最大 batch 或给 activation/graph buffer 留更多显存。

## 关键来源

- FlashAttention GitHub: https://github.com/Dao-AILab/flash-attention
- FlashAttention paper: https://arxiv.org/abs/2205.14135
- FlashInfer docs: https://docs.flashinfer.ai/
- FlashInfer paper: https://arxiv.org/abs/2501.01005
- xFormers ops docs: https://facebookresearch.github.io/xformers/components/ops.html
- NVIDIA CUDA C Programming Guide: https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html
- vLLM CUDA Graphs: https://docs.vllm.ai/en/stable/design/cuda_graphs/
- vLLM Attention Backends: https://docs.vllm.ai/en/latest/design/attention_backends/
- vLLM Torch Compile Integration: https://docs.vllm.ai/en/latest/design/torch_compile/
- SGLang Hyperparameter Tuning: https://docs.sglang.io/docs/advanced_features/hyperparameter_tuning
- DeepSpeed inference initialization: https://deepspeed.readthedocs.io/en/latest/inference-init.html
