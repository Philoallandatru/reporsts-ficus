---
type: Concept
title: 推理观测、Metrics 与 Tracing
description: LLM 推理观测不能只看 GPU 利用率。一个线上请求会经过 gateway、队列、tokenizer、prefill、decode、KV
  cache、streaming、network 和日志系统；任何一层慢了，用户看到的都是“模型慢”。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 推理观测、Metrics 与 Tracing

LLM 推理观测不能只看 GPU 利用率。一个线上请求会经过 gateway、队列、tokenizer、prefill、decode、KV cache、streaming、network 和日志系统；任何一层慢了，用户看到的都是“模型慢”。

## 分层指标

| 层 | 关键指标 |
|---|---|
| Gateway | request count、route、retry/fallback count、auth failures、provider latency |
| Queue / scheduler | waiting requests、queue time、running requests、batch size、preemption |
| Tokenization | prompt tokens、template time、tokenizer worker latency |
| Prefill | TTFT、prefill tokens/s、chunked prefill、prefix cache hit |
| Decode | TPOT、ITL、output tokens/s、decode batch、CUDA graph hit |
| KV cache | cache usage、eviction、swap/offload、prefix cache hits |
| GPU | utilization、memory used、power、temperature、XID、NVLink |
| Client | E2E latency、stream gaps、timeouts、disconnects |

把指标分层后，排障会快很多：TTFT 高看 queue/prefill/cache，TPOT 高看 decode/kernel/communication，E2E 高但 TTFT/TPOT 正常则看 streaming/network/client。

## OpenTelemetry GenAI 语义

OpenTelemetry 的 GenAI semantic conventions 为模型请求提供统一 span/metric 属性，例如 operation、system/provider、request model、response model、token usage、finish reason 等。它适合跨网关、应用和模型服务做统一 tracing。

实践原则：

- trace id 从入口 API 传到网关和模型服务。
- 记录 logical model alias 和真实 backend model。
- token usage、latency 和 cost 要在同一 trace 上关联。
- 不要默认记录完整 prompt/output；隐私和成本都很敏感。

## Prometheus 指标设计

Prometheus 指标要避免高基数 label。不要把 `prompt_hash`、`user_id`、完整模型路径、request id 放进 label；这些应进日志或 trace attributes。

适合 label：

- `model_name` / model alias。
- `backend` / provider。
- `route` / endpoint。
- `status_code` / error class。
- `gpu` / instance id。

不适合 label：

- 完整 prompt。
- request id。
- 用户自然语言输入。
- 高变化的 adapter 名称，除非 cardinality 可控。

## 框架观测入口

| 框架 | 观测入口 | 关注点 |
|---|---|---|
| vLLM | production metrics / Prometheus | request、scheduler、KV cache、prefix cache、token counters |
| TGI | Prometheus metrics / monitoring | router、batch、token、request latency、batch forward/inference duration |
| Triton | metrics endpoint | infer count、queue、compute、GPU metrics、cache |
| TensorRT-LLM | telemetry / stats | IFB、KV cache、CUDA graph、MoE、latency buckets |
| SGLang | production metrics / Prometheus | prompt/generation tokens、token usage、cache hit rate、TTFT |
| NVIDIA DCGM | GPU metrics | 显存、SM、功耗、温度、NVLink、XID |
| GenAI-Perf | benchmark metrics | TTFT、ITL、TPOT、throughput、goodput |

## 告警建议

| 告警 | 说明 |
|---|---|
| p95/p99 TTFT 高 | prefill、queue、prefix cache 或冷启动问题 |
| p95/p99 TPOT 高 | decode、kernel、通信或 offload 问题 |
| queue depth 持续增长 | admission control 失效或容量不足 |
| KV usage 接近上限 | OOM/preemption/cache thrashing 风险 |
| prefix cache hit rate 突降 | template/revision/tool schema 变化 |
| GPU XID / ECC / temperature | 硬件或驱动问题 |
| retry/fallback 激增 | 后端故障、限流或网关策略过激 |

## 常见误区

- 只看平均 latency，不看 p95/p99。
- 只看 GPU utilization，不看 queue time 和 token throughput。
- 用 request/s 比较不同输出长度的服务。
- 把每个用户 id 放进 Prometheus label。
- 网关和 engine 分开看，导致 retry/fallback 成本被漏算。

## 与其他页面的关系

- [推理性能指标与基准测试](inference-benchmarking-metrics.md)：定义 TTFT、TPOT、ITL、goodput。
- [推理排障手册](inference-troubleshooting-runbook.md)：观测是排障证据。
- [LLM 网关与路由层参数](llm-gateway-routing-parameters.md)：网关需要记录 route/retry/fallback。
- [GPU 拓扑、隔离与集群资源](gpu-topology-and-isolation.md)：GPU metrics 来自 DCGM 等底层组件。

## 关键来源

- OpenTelemetry GenAI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- OpenTelemetry GenAI semantic conventions GitHub: https://github.com/open-telemetry/semantic-conventions-genai
- Prometheus metric naming: https://prometheus.io/docs/practices/naming/
- vLLM production metrics: https://docs.vllm.ai/en/stable/design/metrics/
- Triton metrics: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/metrics.html
- TensorRT-LLM telemetry: https://nvidia.github.io/TensorRT-LLM/developer-guide/telemetry.html
- TGI monitoring: https://huggingface.co/docs/text-generation-inference/en/basic_tutorials/monitoring
- TGI metrics reference: https://huggingface.co/docs/text-generation-inference/en/reference/metrics
- SGLang production metrics: https://docs.sglang.io/docs/references/production_metrics
- NVIDIA DCGM exporter: https://github.com/NVIDIA/dcgm-exporter
- NVIDIA GenAI-Perf: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html
