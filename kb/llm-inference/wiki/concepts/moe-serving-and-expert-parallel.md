---
type: Concept
title: MoE serving 与 expert parallel
description: MoE 模型每个 token 只激活部分 expert，但 expert 总权重很大。推理时的瓶颈常常不是普通 dense matmul，而是
  routing、expert dispatch、all-to-all 通信和专家负载不均衡。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# MoE serving 与 expert parallel

MoE 模型每个 token 只激活部分 expert，但 expert 总权重很大。推理时的瓶颈常常不是普通 dense matmul，而是 routing、expert dispatch、all-to-all 通信和专家负载不均衡。

## MoE 推理路径

```text
token hidden state
  -> router/gate 选择 top-k experts
  -> dispatch token 到对应 expert
  -> expert MLP 计算
  -> combine expert outputs
  -> 回到 dense attention/MLP 流程
```

## Expert parallel

Expert parallel 把不同 experts 放到不同 GPU。与 tensor parallel 不同，EP 通常不是切开每个 expert 的矩阵，而是把 expert 集合分配到不同设备。

| 并行方式 | MoE 中的角色 |
|---|---|
| TP | 切分 expert 或 dense 层内部矩阵 |
| EP | 把不同 experts 分给不同 GPU |
| DP | 复制 MoE replica 扩请求吞吐 |
| PP | 按层切分含 MoE 层的模型 |

## All-to-all 通信

MoE 的 token dispatch/combine 常需要 all-to-all：每张 GPU 都可能把 token 发给其他 GPU 上的 experts。通信量取决于 token batch size、top-k experts、expert 放置、router 负载均衡和 GPU interconnect。

普通 PCIe 下，MoE all-to-all 很容易吃掉计算收益；NVLink/NVSwitch/IB 网络和专门通信库会显著影响表现。

## DeepEP

DeepEP 是面向 MoE expert parallel 的通信库，目标是优化 expert dispatch/combine 的 all-to-all 通信。SGLang 等 serving 框架提供 DeepEP 集成，用于提升 MoE 模型推理吞吐。

vLLM 也支持 DeepEP 风格的 all-to-all backend，例如 high-throughput 与 low-latency 两类选择。一个实用经验是：prefill 池更看重吞吐，decode 池更看重低延迟；在 prefill/decode disaggregated serving 中，两边可以选择不同通信 backend。

## 负载均衡

MoE router 可能把大量 token 分到少数热门 expert，造成部分 GPU 忙、部分 GPU 闲。服务端需要关注：

- expert token 分布。
- overflow/drop 策略。
- batch 内 token 数是否足够平滑。
- EP 与 TP 的组合是否导致通信放大。

DeepSeek-V3 技术报告描述过 redundant experts 的部署策略：周期性检测高负载 expert，并用冗余专家缓解热点。vLLM 的 EPLB 也按窗口收集 expert load stats，周期性调整 expert distribution；它的关键参数包括窗口大小、重平衡间隔和冗余专家数。

## 关联参数

| 框架 | 参数 | 说明 |
|---|---|---|
| vLLM | `--enable-expert-parallel` | 对 MoE layer 启用 EP |
| vLLM | `--all2all-backend` | 选择 all-to-all backend，如 `deepep_high_throughput` / `deepep_low_latency` |
| vLLM | `--expert-placement-strategy` | expert 放置策略，常见 `linear` / `round_robin` |
| vLLM | `--enable-eplb` | 启用 Expert Parallel Load Balancer |
| vLLM | `--eplb-config` | 设置 EPLB 窗口、间隔、冗余专家等 |
| vLLM | `--enable-dbo` | Dual Batch Overlap，用于 overlap all-to-all 与 compute |
| SGLang | `--ep-size` | expert parallel size |
| TensorRT-LLM | `moe_expert_parallel_size`、`moe_tensor_parallel_size` | MoE EP/TP 配置项 |
| TensorRT-LLM | `moe_config.backend` | MoE backend，如 TensorRT-LLM、DeepGEMM、Triton 等 |

## 调参建议

- Dense 模型经验不能直接套到 MoE。
- MoE 首先看 expert 并行和 all-to-all，而不是只看 TP。
- 小 batch 下 MoE 通信开销占比更高；吞吐服务通常需要足够 batch。
- 多节点 MoE 要先确认网络拓扑，否则 EP 扩展可能变慢。
- 监控 expert 负载分布，比只看 GPU 平均利用率更有用。

## 关键来源

- TensorRT-LLM Expert Parallelism: https://nvidia.github.io/TensorRT-LLM/advanced/expert-parallelism.html
- TensorRT-LLM parallel strategy: https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/features/parallel-strategy.md
- TensorRT-LLM telemetry: https://nvidia.github.io/TensorRT-LLM/developer-guide/telemetry.html
- SGLang Expert Parallelism: https://docs.sglang.io/docs/advanced_features/expert_parallelism
- vLLM Expert Parallel Deployment: https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/
- DeepEP GitHub: https://github.com/deepseek-ai/DeepEP
- DeepSeek-V3 technical report: https://arxiv.org/pdf/2412.19437
- vLLM Engine Arguments: https://docs.vllm.ai/en/stable/configuration/engine_args/
