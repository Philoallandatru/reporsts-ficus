---
type: Concept
title: 请求调度公平性、优先级与队列策略
description: 推理服务的“调度”不只是把请求凑成 batch。在线系统还要回答三个更难的问题：谁先进入 GPU、谁可以继续占用 KV cache、谁在过载时被拒绝或降级。吞吐最高的策略不一定公平，公平的策略也不一定满足多租户隔离。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 请求调度公平性、优先级与队列策略

推理服务的“调度”不只是把请求凑成 batch。在线系统还要回答三个更难的问题：谁先进入 GPU、谁可以继续占用 KV cache、谁在过载时被拒绝或降级。吞吐最高的策略不一定公平，公平的策略也不一定满足多租户隔离。

## 三层调度

| 层 | 典型对象 | 常见控制 |
|---|---|---|
| Engine 调度 | prefill、decode、KV cache block、batch token | `max-num-batched-tokens`、`max-num-seqs`、`schedule-policy`、priority |
| Serving 平台 | replica、ongoing request、队列、autoscaling | `max_ongoing_requests`、`target_ongoing_requests`、`max_queued_requests`、KPA concurrency |
| 网关 / 租户层 | API key、team、route、budget、rate limit | RPM/TPM、并发上限、优先级、fallback、预算 |

Engine 层关心 GPU 利用率和 KV cache；平台层关心请求是否进入某个副本；网关层关心租户配额、模型别名和成本。如果只调其中一层，常见结果是：网关显示请求成功进入后端，但 engine 内部已经排了很长队。

## 公平性的来源

LLM 请求不是等长任务。一个请求可能只有 20 个 prompt token，另一个请求可能有 100k token；一个只要 10 个输出 token，另一个要流式输出几分钟。因此公平性至少有四种口径：

- Request fairness：每个请求等待时间相近。
- Token fairness：每个租户消耗的 input/output token 份额受控。
- Latency fairness：短请求不被长 prompt 长时间挡住。
- Tenant fairness：不同用户、team、priority class 不互相挤占预算。

Continuous batching 提升总体吞吐，但如果没有队列上限、长度分池或优先级约束，长请求仍然可能把短请求的 TTFT 拉高。

## 常见策略

| 策略 | 原理 | 适用场景 | 风险 |
|---|---|---|---|
| FCFS | 按到达顺序服务 | 单租户、负载长度相近 | 长 prompt 造成 head-of-line blocking |
| Prefix/cache-aware | 优先调度能复用前缀/KV 的请求 | RAG、agent、共享 system prompt | 提升吞吐但可能偏向热门前缀 |
| LPM / longest-prefix match | 根据最长可复用前缀选择请求 | SGLang RadixAttention、prefix-aware routing | 对无共享前缀流量收益小 |
| Priority | 请求带优先级，调度器优先服务高优先级 | 付费层级、交互请求优先于批处理 | 低优先级可能饥饿 |
| Admission control | 队列或并发达到上限就拒绝 | 生产 SLO、避免排队崩溃 | 需要客户端处理 429/503 |

优先级最好和 admission control 一起用。只提高高优先级请求的插队能力，却允许无限排队，会把低优先级请求变成不可预测的尾延迟。

## 参数映射

| 框架 / 层 | 参数族 | 调参含义 |
|---|---|---|
| vLLM | `--scheduling-policy {fcfs,priority}`、请求级 `priority`、preemption、`--max-num-seqs`、`--max-num-batched-tokens`、`--enable-chunked-prefill`、`--long-prefill-token-threshold` | 控制 engine 内请求排序、活跃序列数、每轮 token budget 和长 prompt 切块；priority 策略下数值较低的 priority 更早调度 |
| SGLang | `--schedule-policy`、`fcfs`、`lpm`、`random`、`priority`、`--enable-priority-scheduling`、`--schedule-low-priority-values-first`、`--max-running-requests`、`--max-queued-requests` | 在 FCFS、prefix-aware/LPM、priority 和并发队列之间取舍；priority 数值方向可配置 |
| TGI | `--max-concurrent-requests`、`--waiting-served-ratio`、`--max-waiting-tokens`、`--max-batch-total-tokens`、`--max-batch-prefill-tokens` | 控制 router 等待队列、prefill/decode 混合和 batch token 上限 |
| Ray Serve | `max_ongoing_requests`、`max_queued_requests`、`target_ongoing_requests`、autoscaling config | 控制每个 replica 接多少请求，以及何时扩容；队列满时让上游看到背压 |
| KServe / Knative | `scaleTarget`、`scaleMetric: concurrency`、`containerConcurrency`、`autoscaling.knative.dev/target`、KPA/HPA 参数 | 控制请求进入 Pod 的并发与扩缩容触发；Knative concurrency 是请求级，不理解 token 长短 |
| 网关 | rate limit、budget、route priority、fallback policy | 控制租户级流量、公平性和失败路径 |

## 调参路径

1. 先分清 queue time 在哪里：网关、平台队列、engine 队列，还是 prefill 内部。
2. 对长短请求混合的流量，先设置队列上限，再考虑按 prompt/output 长度分池。
3. 交互式请求和离线批处理不要共享同一个无优先级队列。
4. Prefix-aware 策略要同时监控 cache hit rate 和各租户等待时间，避免热门前缀吞掉调度机会。
5. 优先级必须配合低优先级的最大等待、降级或拒绝策略。

## 常见误区

- 只看 GPU utilization：GPU 很忙可能只是长请求堆积，不代表用户体验好。
- 只看 requests/s：短请求被长请求挡住时，平均吞吐仍可能很好。
- 把 `max_concurrent_requests` 当成吞吐旋钮：并发过高会让 queue time 和 KV cache 压力同时上升。
- 没有 admission control：过载时请求只是更晚失败，SLO 和成本都会变差。
- 网关限流很严格、engine 队列无限：限流看起来生效，但已进入后端的请求仍能制造长尾。

## 关键来源

- vLLM Engine Arguments: https://docs.vllm.ai/en/latest/configuration/engine_args.html
- vLLM troubleshooting: https://docs.vllm.ai/en/stable/usage/troubleshooting/
- SGLang server arguments: https://docs.sglang.io/docs/advanced_features/server_arguments
- SGLang hyperparameter tuning: https://docs.sglang.io/docs/advanced_features/hyperparameter_tuning
- TGI launcher arguments: https://huggingface.co/docs/text-generation-inference/en/reference/launcher
- Ray Serve deployment options: https://docs.ray.io/en/latest/serve/api/doc/ray.serve.deployment_decorator.html
- Ray Serve deployment config: https://docs.ray.io/en/latest/serve/configure-serve-deployment.html
- Ray Serve autoscaling guide: https://docs.ray.io/en/latest/serve/autoscaling-guide.html
- KServe KPA autoscaler: https://kserve.github.io/website/docs/model-serving/predictive-inference/autoscaling/kpa-autoscaler
- Knative autoscaling: https://knative.dev/docs/serving/autoscaling/
- Knative concurrency: https://knative.dev/docs/serving/autoscaling/concurrency/
