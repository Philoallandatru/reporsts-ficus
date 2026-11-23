---
type: Concept
title: Autoscaling 与 Admission Control
description: LLM 服务的扩缩容不能只看 CPU 或 GPU utilization。GPU 利用率高可能是健康的满载，也可能是长 prompt 把队列拖爆；GPU
  利用率低也可能是 scheduler batch 太小、数据没送上来或新副本还在冷启动。更可靠的控制变量是 queue time、waiting/running
  requests、KV cache 占...
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Autoscaling 与 Admission Control

LLM 服务的扩缩容不能只看 CPU 或 GPU utilization。GPU 利用率高可能是健康的满载，也可能是长 prompt 把队列拖爆；GPU 利用率低也可能是 scheduler batch 太小、数据没送上来或新副本还在冷启动。更可靠的控制变量是 queue time、waiting/running requests、KV cache 占用、TTFT/TPOT、goodput 和错误率。

## 分层视角

| 层 | 控制对象 | 典型参数 |
|---|---|---|
| Engine admission | 单实例接多少请求和 token | `max_num_seqs`、`max-running-requests`、`max-concurrent-requests`、`job_queue_size` |
| Pod autoscaling | 副本数量 | Knative/KServe concurrency、Ray Serve autoscaling、HPA/KEDA ScaledObject |
| Cluster autoscaling | 节点/GPU 数量 | node pool、GPU quota、MIG slice、spot/on-demand |
| Gateway admission | 谁能进来、怎么排队/拒绝 | RPM/TPM、parallel requests、budget、fallback、retry |

顺序通常是：先把单实例 admission 设到不会 OOM 和不会尾延迟失控，再让平台按队列/并发/延迟扩副本，最后用网关限流保护整体。

## 关键指标

| 指标 | 说明 | 调参用途 |
|---|---|---|
| waiting requests / queue time | 请求进入 engine 后等待调度的时间 | 判断是否需要扩副本或收紧入口 |
| running requests / ongoing requests | 当前正在处理的请求 | 作为 Ray Serve、KServe/Knative 类 autoscaling 目标 |
| live tokens / KV cache usage | 当前占用 KV cache 的 token 数 | 判断并发是否受显存而非算力限制 |
| TTFT | 首 token 延迟 | 识别 prefill、排队、冷启动和 prefix cache 问题 |
| TPOT / ITL | 生成 token 间隔 | 识别 decode、batch、kernel、通信瓶颈 |
| goodput | 满足 SLO 的吞吐 | 比总 tokens/s 更适合做容量决策 |
| rejection / timeout rate | 入口拒绝和超时 | 判断 admission control 是否过紧或系统已过载 |

## Engine 侧准入

Engine 的准入控制是第一道保护，目标不是“永远不拒绝”，而是在不可服务时尽早拒绝，避免所有请求一起变慢。

| 参数族 | 原理 |
|---|---|
| 最大并发请求 | 限制同时占 KV cache 的序列数，防止并发高时 OOM |
| 最大 queued requests / job queue | 限制排队深度，避免排队时间无限增长 |
| batch token budget | 限制每轮调度 token 数，平衡吞吐和尾延迟 |
| max input/output/model length | 控制单请求最坏资源占用 |
| prefix/KV cache budget | 控制可复用上下文和活跃上下文的显存比例 |

如果 engine 已经排队严重，继续让网关重试通常会放大压力。此时应先拒绝或降级低优先级流量。

## KServe / Knative

Knative Pod Autoscaler 常以并发作为扩缩容信号，也支持 scale-to-zero。对 LLM 服务，scale-to-zero 会带来权重加载、engine 初始化和 warmup 冷启动成本；生产上通常需要设置最小副本或预热策略。

KServe 基于 Kubernetes/Knative 把 model server 包装成 `InferenceService`。它适合统一 runtime、流量管理和平台化部署，但仍要依赖 engine 暴露的健康检查和 metrics 来做 LLM 特有调参。

## Ray Serve

Ray Serve autoscaling 的核心是 deployment replica 数、单 replica 的 `max_ongoing_requests` 和 autoscaling 的目标 ongoing requests。对 vLLM/SGLang 这类 engine，Ray 层的 ongoing requests 不等于 GPU 内部 token batch；它只是外层副本负载信号。

调参时要同时看两层：

- Ray 层：replica 是否扩起来、每个 replica 是否排队。
- Engine 层：KV cache 是否满、batch token budget 是否满、TTFT/TPOT 是否恶化。

## KEDA / Prometheus

KEDA 可根据 Prometheus 查询、队列长度或其他事件源扩缩容。对 LLM，更有意义的 scaler 往往是：

- waiting requests 或 queue time。
- p95/p99 TTFT。
- active tokens / KV cache usage。
- gateway pending requests。
- 每模型或每租户的请求速率。

用 GPU utilization 做唯一 scaler 容易误判：decode-heavy 负载、prefill-heavy 负载、MoE all-to-all 和 offload 都可能表现出不同 utilization 形态。

## 常见错误

| 错误 | 后果 | 更好的做法 |
|---|---|---|
| 只按 GPU utilization 扩容 | 扩缩容滞后或误扩 | 同时看队列、TTFT、TPOT、KV cache |
| 把队列设得很大 | 平均成功率看似高，p99 崩溃 | 设置 max queue 和超时，过载时快速失败 |
| scale-to-zero 跑大模型 | 冷启动 TTFT 极高 | 保留 min replicas，做权重缓存和 warmup |
| 网关无限 retry | 放大过载和成本 | 只对临时错误 retry，确定性错误直接返回 |
| 新副本未 warmup 就接流量 | 首批请求慢、CUDA graph 未捕获 | readiness 之后再做真实 shape warmup |

## 调参顺序

1. 用真实长度分布压测单实例，找出不会 OOM 的并发和 token budget。
2. 设置 engine 级最大请求、最大队列、上下文和输出长度。
3. 用 queue time、TTFT、TPOT 和 goodput 找扩容阈值。
4. 平台层设置 min/max replicas、scale-up/down 窗口和冷启动保护。
5. 网关层设置 per-tenant RPM/TPM/并发/budget，防止一个租户拖垮全局。

## 与其他页面的关系

- [Kubernetes 模型服务部署](kubernetes-model-serving.md)：平台部署层。
- [推理观测、Metrics 与 Tracing](inference-observability-and-tracing.md)：需要哪些指标。
- [推理性能指标与基准测试](inference-benchmarking-metrics.md)：TTFT、TPOT、goodput 的口径。
- [LLM 网关与路由层参数](llm-gateway-routing-parameters.md)：入口治理和 fallback。
- [推理容量规划公式](capacity-planning-formulas.md)：把 token、显存和吞吐转成容量。

## 关键来源

- KServe KPA autoscaler: https://kserve.github.io/website/docs/model-serving/predictive-inference/autoscaling/kpa-autoscaler
- Knative autoscaling: https://knative.dev/docs/serving/autoscaling/
- Knative scale to zero: https://knative.dev/docs/serving/autoscaling/scale-to-zero/
- Ray Serve autoscaling guide: https://docs.ray.io/en/latest/serve/autoscaling-guide.html
- Ray Serve advanced autoscaling: https://docs.ray.io/en/latest/serve/advanced-guides/advanced-autoscaling.html
- KEDA scaling deployments: https://keda.sh/docs/2.20/concepts/scaling-deployments/
- KEDA ScaledObject spec: https://keda.sh/docs/2.20/reference/scaledobject-spec/
- KEDA Prometheus scaler: https://keda.sh/docs/2.20/scalers/prometheus/
- vLLM metrics design: https://docs.vllm.ai/en/stable/design/metrics/
- SGLang production metrics: https://docs.sglang.io/docs/references/production_metrics
