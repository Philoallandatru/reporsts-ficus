---
type: Concept
title: Continuous batching 与推理调度
description: LLM serving 的调度难点来自请求长度不一致：有的请求 prompt 很长，有的请求只生成几个 token；有的请求刚进入 prefill，有的请求正在
  decode。Continuous batching / in-flight batching 的目标是让 GPU 在这些不规则请求之间持续有活干。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Continuous batching 与推理调度

LLM serving 的调度难点来自请求长度不一致：有的请求 prompt 很长，有的请求只生成几个 token；有的请求刚进入 prefill，有的请求正在 decode。Continuous batching / in-flight batching 的目标是让 GPU 在这些不规则请求之间持续有活干。

## Prefill 与 decode

| 阶段 | 输入 | 主要瓶颈 | 关键指标 |
|---|---|---|---|
| Prefill | 一整段 prompt tokens | 计算密集、activation 峰值、长 prompt 排队 | TTFT |
| Decode | 每步一个新 token | 内存带宽、KV cache 读取、调度开销 | TPOT / ITL |

Prefill 决定首 token 延迟，decode 决定持续生成速度。一个高吞吐服务必须同时管理这两类工作，而不是只追求大 batch。

## Static batching 的问题

传统 static batching 会等一批请求一起开始，直到这一批都结束。对于 LLM，这会浪费大量 GPU 时间：

- 短请求结束后，batch 中的位置空着。
- 长请求拖住整批请求。
- 新请求不能及时加入，排队时间变长。

## Continuous batching / in-flight batching

Continuous batching 允许调度器在 decode 循环中不断加入新请求、移除完成请求。TensorRT-LLM 称为 in-flight batching，vLLM、SGLang、TGI、LMDeploy 等也有类似调度。

Orca 论文把这种思路称为 iteration-level scheduling：调度单位不是“完整请求”，而是每一轮 token 生成迭代。这样短请求完成后可以立刻释放位置，新请求也能在后续迭代加入。

它提高吞吐，但也引入调度权衡：

- 新请求插入越积极，TTFT 越好，但正在 decode 的请求可能被 prefill 打断。
- Decode batch 越大，吞吐越好，但单请求 token 间隔可能变差。
- 长 prompt 如果一次性 prefill，会拖慢队列；切块能改善公平性。

## Chunked prefill

Chunked prefill 把长 prompt 分成多块，每块作为可调度单元。它的价值是：

- 降低单次 prefill 的 activation 峰值。
- 避免超长 prompt 长时间独占 GPU。
- 允许 decode 请求穿插执行，改善尾延迟。

代价是 prefill 被拆成更多步骤，调度和 kernel launch 开销增加，TTFT 未必总是下降。

SARATHI/Sarathi-Serve 的核心观察是：prefill 更偏 compute-bound，decode 更偏 memory-bandwidth-bound。把 prefill chunk 和 decode 请求混合，可以让不同瓶颈的工作互相“填空”，减少 GPU pipeline bubble。

## Prefill/decode disaggregation

更大规模服务会把 prefill 和 decode 分到不同实例或 GPU 池：

- Prefill worker 负责大块 prompt 计算和首段 KV 生成。
- Decode worker 负责稳定的小步生成。
- 中间需要传输 KV cache 或中间状态。

这种架构适合长 prompt、RAG、agent 工具调用密集的服务。它的代价是系统复杂度和跨节点/跨 GPU 传输开销。

DistServe 的设计目标就是把 TTFT 和 TPOT 分开优化：prefill 池按大 prompt 计算扩容，decode 池按持续生成扩容，中间通过 KV 传输连接。vLLM 和 TensorRT-LLM 也都有 disaggregated prefilling/serving 方向的实现或实验功能。

## 常见参数映射

| 目标 | 参数族 |
|---|---|
| 限制同一轮 token 数 | `max-num-batched-tokens`、`max-batch-total-tokens`、`max_num_tokens` |
| 限制活跃请求数 | `max-running-requests`、`max-concurrent-requests`、`max-num-seqs`、`parallel` |
| 控制 prefill 峰值 | `chunked-prefill-size`、`max-batch-prefill-tokens`、`ubatch-size` |
| 控制等待队列 | `max-queued-requests`、`max-waiting-tokens`、`waiting-served-ratio` |
| 控制调度策略 | `schedule-policy`、FCFS/LPM、priority scheduling |

## 调参建议

- TTFT 高但 decode 快：优化 prefill，启用 prefix cache，降低长 prompt 抢占。
- TPOT 高但 TTFT 正常：扩大/缩小 decode batch 对比，检查 KV cache 读带宽和 CUDA graph。
- 长 prompt OOM：先降 chunked prefill/microbatch，而不是直接降模型。
- 多租户服务：设置排队上限；无限排队通常只会把延迟问题藏起来。

## 关键来源

- TensorRT-LLM Paged Attention / IFB / Scheduler: https://nvidia.github.io/TensorRT-LLM/features/paged-attention-ifb-scheduler.html
- Orca OSDI 2022: https://www.usenix.org/conference/osdi22/presentation/yu
- vLLM Optimization / Chunked Prefill: https://docs.vllm.ai/en/stable/configuration/optimization/
- SARATHI: https://arxiv.org/abs/2308.16369
- Sarathi-Serve: https://arxiv.org/abs/2403.02310
- SGLang Hyperparameter Tuning: https://docs.sglang.io/docs/advanced_features/hyperparameter_tuning
- SGLang PD Disaggregation: https://docs.sglang.io/docs/advanced_features/pd_disaggregation
- DistServe OSDI 2024: https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin
- vLLM Disaggregated Prefilling: https://docs.vllm.ai/en/stable/features/disagg_prefill.html
- TGI launcher arguments: https://huggingface.co/docs/text-generation-inference/reference/launcher
- vLLM Engine Arguments: https://docs.vllm.ai/en/stable/configuration/engine_args/
