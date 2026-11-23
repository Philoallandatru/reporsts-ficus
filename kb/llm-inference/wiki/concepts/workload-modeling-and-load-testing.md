---
type: Concept
title: 推理负载建模与压测数据集
description: 压测 LLM 服务时，输入分布比工具名字更重要。短 prompt、短输出、无共享前缀的 synthetic 流量，无法代表 RAG、agent、代码生成或长文档抽取。负载建模的目标是让
  benchmark 暴露真实瓶颈，而不是生成好看的 tokens/s。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 推理负载建模与压测数据集

压测 LLM 服务时，输入分布比工具名字更重要。短 prompt、短输出、无共享前缀的 synthetic 流量，无法代表 RAG、agent、代码生成或长文档抽取。负载建模的目标是让 benchmark 暴露真实瓶颈，而不是生成好看的 tokens/s。

## 负载维度

| 维度 | 为什么重要 |
|---|---|
| prompt token 分布 | 决定 prefill、TTFT、KV 初始占用 |
| output token 分布 | 决定 decode 时间、TPOT、总 KV 增长 |
| 到达过程 | open-loop QPS 会暴露排队崩溃；closed-loop 并发更稳定 |
| 并发/请求数 | 决定 scheduler batch 和 KV live tokens |
| 共享 prefix 比例 | 决定 prefix cache / RadixAttention 收益 |
| 多模型/多 adapter 混合 | 决定路由、adapter cache 和 batch 分裂 |
| streaming | 影响 TTFT、ITL、client backpressure |
| 错误和超时 | 决定 retry/fallback 对尾延迟和成本的放大 |

## 常见数据集/生成方式

| 类型 | 用途 | 注意 |
|---|---|---|
| ShareGPT 类对话 | 模拟真实 chat prompt/output 长度 | 质量取决于清洗和长度分布 |
| BurstGPT / trace 类 | 模拟突发到达和真实 trace | 更适合 autoscaling 和排队评估 |
| random token | 压 kernel/token throughput | 不代表 tokenizer/template/cache |
| synthetic fixed length | 做容量边界和回归测试 | 容易过于理想 |
| Sonnet / long text | 长 prompt、prefix cache、chunked prefill 测试 | 要记录共享前缀比例 |
| prefix repetition | 专门验证 prefix cache 命中 | 要记录 prefix pool size 和共享长度 |
| 线上采样脱敏 | 最接近真实 | 需要隐私、合规和去标识化 |
| RAG/agent trace | 工具 schema、长 system prompt、多轮状态 | 必须固定 template 和工具顺序 |

vLLM benchmark 和 NVIDIA GenAI-Perf 都支持不同负载形状。关键不是“用哪个名字的数据集”，而是把 prompt/output 长度、到达率、并发、SLO 和硬件配置一起记录。

## Open-loop 与 closed-loop

Closed-loop：固定并发，完成一个请求再发下一个。它适合看给定并发下的稳定吞吐和延迟。

Open-loop：按到达率发请求，不等待前一个完成。它更接近线上流量，能暴露 queue buildup、admission control 和 autoscaling 滞后。

如果只做 closed-loop，系统可能看起来很稳；上线后 QPS 突增时却因为排队进入崩溃区。

多轮压测还要记录 session 级指标：session 数、并发 session、每个 session 的 turn 数、turn 间隔、共享 prefix 池。多轮 agent/chat 的 cache 行为和一次性 chat completion 不一样。

## SLO 与 goodput

压测应同时记录：

- TTFT SLO，例如 p95 TTFT < 1s。
- TPOT/ITL SLO，例如 p95 TPOT < 50ms。
- E2E latency SLO。
- 错误率和超时率。
- goodput：满足上述 SLO 的有效吞吐。

吞吐最高的配置不一定是可用配置。`max_num_batched_tokens`、并发和 KV cache 用到极限时，tokens/s 可能上升，但 p99 会先坏掉。

## Benchmark 记录模板

每次压测至少记录：

- 模型名、revision、dtype、量化、tokenizer/template。
- 框架版本、启动参数、硬件、GPU 拓扑。
- 数据集类型、prompt/output token 分布。
- 到达模型：open-loop QPS 或 closed-loop concurrency。
- SLO：TTFT/TPOT/E2E/error thresholds。
- 结果：p50/p95/p99 TTFT、TPOT、ITL、E2E、tokens/s、requests/s、goodput。
- 资源：GPU util、memory、KV usage、queue depth、cache hit rate。

## 调参路径

| 目标 | 压测方式 |
|---|---|
| 找最大稳定 QPS | open-loop 逐步升 QPS，看 queue 和 p99 |
| 找单实例最佳 batch | closed-loop 扫 concurrency / batch token budget |
| 验证 prefix cache | 设计固定系统 prompt 和共享工具 schema |
| 验证长上下文 | 使用长 prompt 分桶，不要用平均长度掩盖尾部 |
| 验证 autoscaling | 用 bursty 到达过程，不只是平稳 QPS |
| 验证 fallback/retry | 人工注入后端错误和超时 |

## 常见误区

- 用随机 token benchmark 直接推断 RAG 性能。
- 只报告 output tokens/s，不报告输入长度。
- 不固定 tokenizer/chat template。
- 不记录失败请求，导致 goodput 虚高。
- 压测客户端成瓶颈，却以为服务端满了。
- 一次改多个参数，无法归因。

## 与其他页面的关系

- [推理性能指标与基准测试](inference-benchmarking-metrics.md)：定义指标。
- [离线推理与批量推理](offline-and-batch-inference.md)：离线吞吐和在线压测口径不同。
- [推理容量规划公式](capacity-planning-formulas.md)：先算容量，再用压测验证。
- [推理观测、Metrics 与 Tracing](inference-observability-and-tracing.md)：压测结果必须有指标支撑。

## 关键来源

- vLLM Benchmark CLI: https://docs.vllm.ai/en/stable/benchmarking/cli/
- vLLM bench serve CLI: https://docs.vllm.ai/en/stable/cli/bench/serve/
- vLLM serving benchmark docs: https://docs.vllm.ai/en/stable/contributing/benchmarks.html
- NVIDIA GenAI-Perf: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html
- NVIDIA GenAI-Perf multi-turn: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/docs/multi_turn.html
- Triton Perf Analyzer load modes: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/docs/inference_load_modes.html
- NVIDIA NIM LLM metrics: https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html
- Triton Perf Analyzer CLI: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/docs/cli.html
- OpenTelemetry GenAI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- GuideLLM GitHub: https://github.com/vllm-project/guidellm
