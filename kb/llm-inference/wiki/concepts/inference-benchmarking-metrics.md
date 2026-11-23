---
type: Concept
title: 推理性能指标与基准测试
description: LLM 推理 benchmark 不能只看 tokens/s。一个服务可能总吞吐很高，但首 token 很慢；也可能单请求很快，但并发一上来就排队。指标要按用户体验、系统吞吐和
  SLO 三层看。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 推理性能指标与基准测试

LLM 推理 benchmark 不能只看 tokens/s。一个服务可能总吞吐很高，但首 token 很慢；也可能单请求很快，但并发一上来就排队。指标要按用户体验、系统吞吐和 SLO 三层看。

## 核心指标

| 指标 | 含义 | 主要受什么影响 |
|---|---|---|
| TTFT | Time To First Token，发出请求到首个 token 返回 | 排队、tokenization、prefill、prefix cache |
| TPOT | Time Per Output Token，平均每个输出 token 时间 | decode batch、KV cache 读、kernel、通信 |
| ITL | Inter-token Latency，相邻 token 间隔 | decode 调度、流式输出、batch 干扰 |
| E2E latency | 请求总耗时 | TTFT + 输出长度 * TPOT |
| Output throughput | 每秒输出 token 数 | batch、并发、模型大小、硬件 |
| Request throughput | 每秒完成请求数 | 请求长度分布、队列和服务上限 |
| Goodput | 满足 SLO 的有效吞吐 | SLO、尾延迟、拒绝率 |
| Queue time | 请求进入计算前等待时间 | admission control、batching 策略 |

## 为什么平均值不够

生产服务更应该看 p50/p90/p95/p99：

- p50 代表普通体验。
- p95/p99 代表尾延迟和系统抖动。
- 平均值会掩盖少量超长 prompt 或排队峰值。

一个服务的 tokens/s 变高，但 p99 TTFT 变差，用户可能感觉更慢。

## Benchmark 输入要素

| 维度 | 需要固定/记录 |
|---|---|
| 模型 | 模型名、revision、dtype、量化方式 |
| tokenizer/template | tokenizer 版本、chat template、系统提示 |
| 输入分布 | prompt token 长度、输出 token 长度、共享 prefix 比例 |
| 并发模型 | closed-loop / open-loop、QPS、并发数 |
| 服务配置 | context、batch token budget、KV cache dtype、并行度 |
| 硬件 | GPU/CPU、显存、驱动、互连、容器 |
| SLO | TTFT/TPOT/E2E 阈值和错误率 |

## Closed-loop 与 open-loop

Closed-loop benchmark 通常是“固定并发，完成一个请求再发下一个”。它适合看系统在给定并发下的稳定表现。

Open-loop benchmark 通常按固定到达率发请求。它更接近真实线上流量，能暴露排队崩溃点，但配置更容易误读。

多轮 chat/agent 压测还要记录 session 数、每个 session 的 turn 数、turn 间隔和共享 prefix 池。一次性 request benchmark 无法代表长会话里的 prefix cache、KV 增长和工具 schema 复用。

## Goodput 与 SLO

Goodput 是“满足服务目标的有效吞吐”，比总 throughput 更适合生产容量规划。例如一个系统能输出 20k token/s，但只有一半请求满足 `TTFT < 1s` 和 `TPOT < 50ms`，那么对这个 SLO 的 goodput 不是 20k token/s。长上下文服务尤其需要把 TTFT SLO 和 TPOT SLO 分开看。

## 常见误区

- 只测短 prompt，却拿结果部署 RAG。
- 只看 output tokens/s，不看 TTFT。
- 只看平均延迟，不看尾延迟。
- 量化前后用不同 chat template。
- 开了 prefix cache，但 benchmark prompt 没有共享前缀。
- 并发压测没有设置请求拒绝/排队上限。
- 用 random/synthetic token 结果直接代表 RAG、agent 或长文档业务。

## 调参闭环

1. 固定模型和输入分布。
2. 记录 baseline：TTFT、TPOT、throughput、显存、错误率。
3. 一次只改一类参数：KV cache、batch、量化、并行、prefix cache。
4. 记录 p50/p95/p99，而不是只看平均值。
5. 用 goodput 判断是否满足 SLO。

## 关键来源

- vLLM Benchmarks: https://docs.vllm.ai/en/stable/contributing/benchmarks.html
- NVIDIA GenAI-Perf: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html
- NVIDIA GenAI-Perf multi-turn: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/docs/multi_turn.html
- NVIDIA NIM LLM benchmarking metrics: https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html
- Triton Perf Analyzer load modes: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/docs/inference_load_modes.html
- TGI launcher arguments: https://huggingface.co/docs/text-generation-inference/reference/launcher
- TensorRT-LLM serving metrics: https://nvidia.github.io/TensorRT-LLM/commands/trtllm-serve/trtllm-serve.html
