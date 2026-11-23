---
type: Concept
title: 多 GPU 并行推理
description: 多 GPU 推理不是“GPU 越多越快”。不同并行方式解决不同瓶颈：单卡装不下、单卡算不快、单实例吞吐不够、MoE expert 太多、上下文太长。每一种都会引入通信和调度成本。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 多 GPU 并行推理

多 GPU 推理不是“GPU 越多越快”。不同并行方式解决不同瓶颈：单卡装不下、单卡算不快、单实例吞吐不够、MoE expert 太多、上下文太长。每一种都会引入通信和调度成本。

## 并行方式

| 方式 | 缩写 | 切什么 | 主要用途 | 主要代价 |
|---|---|---|---|---|
| Tensor parallel | TP | 单层矩阵/attention/MLP | 单层权重或计算太大 | 高频 all-reduce/all-gather |
| Pipeline parallel | PP | Transformer layers | 总层数/总权重太大 | 流水线气泡、调度复杂 |
| Data parallel | DP | 模型副本 | 提升总请求吞吐 | 每副本占完整权重 |
| Expert parallel | EP | MoE experts | 分散专家权重和计算 | 路由与 all-to-all |
| Context parallel | CP/DCP | 长上下文 attention/KV | 超长上下文和 KV 压力 | 跨卡 attention/KV 通信 |

## Tensor parallel

TP 把一个大矩阵拆到多 GPU，每张卡计算一部分，再通信合并结果。它适合模型单层太大或单卡放不下的场景。NVLink/NVSwitch 上收益更好，普通 PCIe 上通信可能吃掉速度收益。

## Pipeline parallel

PP 按层切分模型，例如前 20 层在 GPU0，后 20 层在 GPU1。它能降低每卡权重压力，但单请求会依次经过多个 stage。batch 太小会有流水线气泡；batch 足够大时吞吐更好。

## Data parallel

DP 复制完整模型到多个副本，路由把请求分给不同副本。它最简单、隔离性好，适合模型单卡能放下但总 QPS 不够。代价是每张卡都保存完整权重，KV cache 也不共享。

## Expert parallel

MoE 模型每个 token 只激活部分 expert，但 expert 总权重很大。EP 把 expert 分散到多卡。瓶颈通常不是普通 matmul，而是 token dispatch/combine 和 all-to-all 通信。

## Context parallel

长上下文下，KV cache 和 attention 计算会变成主要压力。Context parallel 把上下文维度切分，让多卡共同处理长序列。它适合 128K、1M 这类长上下文服务，但对通信和实现要求更高。

## 组合方式

常见组合：

- TP + DP：每个副本内部多卡切模型，再复制多个副本扩吞吐。
- TP + PP：超大 dense model 单副本部署。
- TP + EP：MoE 模型常见。
- PP/TP + prefill/decode disaggregation：大规模长 prompt 服务。

## 选择顺序

1. 如果模型单卡能放下，优先用 DP 多副本扩吞吐，系统简单。
2. 如果模型单卡放不下，先尝试 TP；TP 通信不划算时再引入 PP。
3. 如果是 MoE，优先分析 expert 权重和 token routing，再决定 EP/TP 组合。
4. 如果瓶颈是长上下文 KV/attention，考虑 CP/DCP、KV cache 量化和 prefill/decode disaggregation。
5. 如果瓶颈是请求排队，不要只加 TP；可能需要 DP 或更好的 admission control。

## 调参建议

- 单卡能放下：优先 DP 多副本扩吞吐，简单可靠。
- 单卡放不下：先 TP，再考虑 PP。
- PCIe 机器：谨慎提高 TP，压测通信瓶颈。
- MoE：关注 EP 和 router/all-to-all 指标。
- 长上下文：关注 CP/DCP、KV cache dtype、prefix cache 和 disaggregation。

## 关键来源

- vLLM Engine Arguments: https://docs.vllm.ai/en/stable/configuration/engine_args/
- TGI Tensor Parallelism: https://huggingface.co/docs/text-generation-inference/conceptual/tensor_parallelism
- TensorRT-LLM `trtllm-serve`: https://nvidia.github.io/TensorRT-LLM/commands/trtllm-serve/trtllm-serve.html
- SGLang Server Arguments: https://docs.sglang.io/docs/advanced_features/server_arguments
- DeepSpeed inference initialization: https://deepspeed.readthedocs.io/en/latest/inference-init.html
- TensorRT-LLM parallel strategy: https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/features/parallel-strategy.md
- NVIDIA Megatron Core parallelism guide: https://docs.nvidia.com/megatron-core/developer-guide/latest/user-guide/parallelism-guide.html
