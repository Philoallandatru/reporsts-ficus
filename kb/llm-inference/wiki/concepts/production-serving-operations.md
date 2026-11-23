---
type: Concept
title: 生产服务与运维控制面
description: 推理框架参数最终要进入生产控制面：如何接收请求、拒绝过载、记录指标、预热模型、滚动发布、扩缩容和定位故障。没有这些，单机 benchmark
  再好也不等于可用服务。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 生产服务与运维控制面

推理框架参数最终要进入生产控制面：如何接收请求、拒绝过载、记录指标、预热模型、滚动发布、扩缩容和定位故障。没有这些，单机 benchmark 再好也不等于可用服务。

## Admission control

Admission control 决定请求是否进入系统。它比无限排队更健康，因为 LLM 请求可能非常长，队列一旦堆积，后续请求即使最终执行也已经超过 SLO。

常见控制：

- 最大并发请求数。
- 最大排队请求数。
- 最大输入 token。
- 最大总 token。
- 最大输出 token。
- 每用户/API key rate limit。

在 chunked prefill 场景下，admission control 不能只看第一个 chunk 是否放得下。vLLM 的 `--scheduler-reserve-full-isl` 就是为了按完整输入长度预留 KV cache，避免接收过多长 prompt 后触发 KV thrashing。

## Queue limits

队列限制应该和 SLO 绑定。比如聊天服务可以接受短暂排队，但代码补全或语音交互可能必须快速拒绝。无限队列会让平均吞吐看起来稳定，却让 p99 延迟不可控。

## Metrics

生产指标至少覆盖：

| 层面 | 指标 |
|---|---|
| 用户体验 | TTFT、TPOT/ITL、E2E latency、错误率 |
| 调度 | queue time、running requests、waiting requests、batch token count |
| 资源 | GPU memory、KV cache usage、CPU memory、GPU utilization |
| 缓存 | prefix cache hit rate、KV eviction、offload hit/miss |
| 业务 | requests/sec、tokens/sec、goodput、拒绝率 |

TensorRT-LLM 的 telemetry manifest 把 request queue time、time to first token、time per output token、prefill/decode time 等 bucket 暴露为 Prometheus 配置项。vLLM metrics 也区分 server-level 与 request-level metrics，后者更接近 SLO 视角。

## Warmup

首次请求慢通常来自模型加载、CUDA kernel 编译、CUDA Graph capture、Triton autotune、KV cache pool 初始化和 tokenizer/cache 初始化。生产发布前应 warmup：

- 典型短 prompt。
- 典型长 prompt。
- 典型 batch size。
- 结构化输出路径。
- LoRA/adapters 路径。

vLLM 提供 JIT monitor，SGLang 也有 server warmup 相关开关。warmup 不只是发一个短请求，而是要覆盖真实服务会遇到的 shape、backend 和路径。

## Autoscaling

LLM autoscaling 不能只看 GPU 利用率。更可靠的信号包括：

- queue time 增长。
- goodput 下降。
- p95/p99 TTFT 或 TPOT 超 SLO。
- KV cache usage 接近上限。
- 请求到达率持续高于服务能力。

## 发布与回滚

模型服务发布需要固定：

- 模型 revision。
- tokenizer revision。
- chat template。
- 量化格式。
- 采样默认值。
- max token 限制。
- 结构化输出 backend。

这些变化都可能改变质量或容量，应该像代码发布一样记录。

## 调参建议

- 生产优先设置拒绝边界，再做吞吐优化。
- 监控 prefix cache 命中率，否则缓存参数可能只是占显存。
- 每次改 `max-model-len`、batch token budget、KV dtype，都要重新做容量压测。
- 针对不同 workload 建独立 deployment，比一个万能 deployment 更稳。

## 关联参数

| 框架 | 参数 | 说明 |
|---|---|---|
| vLLM | `--max-num-batched-tokens`、`--max-num-seqs` | 单轮 token / sequence 调度上限 |
| vLLM | `--scheduling-policy` | FCFS 或 priority scheduling |
| vLLM | `--watermark` | 为 admission 保留 KV block headroom |
| vLLM | `--kv-cache-metrics`、`--kv-cache-metrics-sample` | KV residency / reuse 指标 |
| vLLM | `--enable-logging-iteration-details` | 记录每轮调度细节 |
| SGLang | `--max-running-requests`、`--max-queued-requests` | 运行中请求和队列上限 |
| SGLang | `--schedule-policy fcfs|lpm` | 先来先服务或最长前缀匹配 |
| SGLang | `--enable-priority-scheduling`、`--enable-metrics` | 优先级调度与 Prometheus metrics |
| TGI | `--max-concurrent-requests`、`--max-batch-total-tokens` | 并发与 batch token budget |
| TensorRT-LLM | `prometheus_metrics_config.*_buckets` | Prometheus latency buckets |

## 关键来源

- vLLM Metrics design: https://docs.vllm.ai/en/stable/design/metrics/
- vLLM Engine Arguments: https://docs.vllm.ai/en/stable/configuration/engine_args/
- TGI launcher arguments: https://huggingface.co/docs/text-generation-inference/reference/launcher
- TGI launcher tutorial: https://huggingface.co/docs/text-generation-inference/en/basic_tutorials/launcher
- TensorRT-LLM `trtllm-serve`: https://nvidia.github.io/TensorRT-LLM/commands/trtllm-serve/trtllm-serve.html
- TensorRT-LLM telemetry: https://nvidia.github.io/TensorRT-LLM/developer-guide/telemetry.html
- NVIDIA GenAI-Perf: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html
- NVIDIA NIM LLM benchmarking metrics: https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html
