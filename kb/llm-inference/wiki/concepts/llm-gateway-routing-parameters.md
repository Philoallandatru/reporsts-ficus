---
type: Concept
title: LLM 网关与路由层参数
description: LLM 网关不直接运行模型，它位于应用和推理后端之间，负责把请求路由到 vLLM、TGI、SGLang、云模型或多个 provider。典型能力包括
  OpenAI-compatible API、model alias、fallback、retry、rate limit、budget、virtual key、日志和观测。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# LLM 网关与路由层参数

LLM 网关不直接运行模型，它位于应用和推理后端之间，负责把请求路由到 vLLM、TGI、SGLang、云模型或多个 provider。典型能力包括 OpenAI-compatible API、model alias、fallback、retry、rate limit、budget、virtual key、日志和观测。

## 它解决的问题

| 问题 | 网关层能力 |
|---|---|
| 多 provider / 多 deployment | 统一 OpenAI 格式，按 model alias 路由 |
| 单后端故障 | fallback 到备用 model group |
| 区域或实例负载不均 | load balancing、cooldown、健康检查 |
| 成本失控 | budget、spend tracking、per-key 限额 |
| 多团队共享 | virtual keys、team/user rate limits、model restriction |
| 统一观测 | request logging、cost、latency、callbacks |

LiteLLM Proxy 是这个层的代表：它不是 vLLM 这样的 engine，而是把请求翻译、鉴权、路由和治理放在模型服务前面。

## 参数分组

| 类别 | 典型参数 | 原理与影响 |
|---|---|---|
| 模型列表 | `model_list`、`model_name`、`litellm_params.model`、`api_base`、`api_key` | 把一个逻辑模型名映射到多个真实部署 |
| OpenAI-compatible provider | `model: openai/<model>`、`api_base` | 把自托管 vLLM/TGI/MLC/Triton wrapper 接成 OpenAI 风格 provider |
| 负载均衡 | `rpm`、`tpm`、routing strategy、order | 根据速率限制、优先级或策略选择部署 |
| fallback | `fallbacks`、model-level fallbacks | 主模型失败或重试耗尽后切到备用模型 |
| retry | `num_retries`、timeout、backoff | 临时错误恢复；过多 retry 会放大尾延迟和成本 |
| cooldown | cooldown time / unhealthy deployment tracking | 避免继续把流量打到异常 deployment |
| virtual keys | key、user、team、metadata | 多租户鉴权与配额边界 |
| budget | `max_budget`、`budget_duration`、soft budget | 控制 key/user/team 的成本窗口 |
| rate limit | RPM、TPM、parallel request limit | 控制请求速率、token 速率和并发 |
| logging | callbacks、spend tracking、audit logs | 追踪成本、错误和延迟 |
| guardrails | PII/content filters、pre-call hooks | 请求进入模型前后做安全与合规检查 |

## 路由层与推理层的边界

路由层看到的是“请求”和“模型别名”；推理层看到的是 token、KV cache、batch 和 GPU。

不要期待网关自动解决 engine 级瓶颈：

- vLLM 的 `max_num_batched_tokens` 太低，LiteLLM 不能让单实例更快。
- TensorRT-LLM engine 构建时 `max_batch_size` 太小，网关只能分流，不能扩大 engine 能力。
- 如果所有后端都共享同一块 GPU，load balancing 可能只是在同一瓶颈上绕圈。

网关真正擅长的是跨实例、跨区域、跨 provider 的可靠性和治理。

## 调参判断

### 错误率高

先区分 provider 错误、网关鉴权错误和后端 engine 错误。只有 provider/实例级临时错误适合 fallback；prompt 太长、schema 错、模型不支持 tool call 这类确定性错误不应该盲目重试。

### 尾延迟高

减少 retry 次数、设置合理 timeout，并按后端真实延迟分层。fallback 可以提高成功率，但也可能让用户等完主模型超时后再等备用模型。

### 成本异常

给 virtual key、team 和 user 设置 budget/rate limit。按模型别名限制可用模型，避免低优先级业务误打高价模型。

### 质量波动

检查一个 `model_name` 是否路由到多个真实模型版本。如果 alias 后面混了不同模型、不同 prompt template 或不同 sampling 默认值，输出会不稳定。

## 与其他机制的关系

- [生产服务与运维控制面](production-serving-operations.md)：网关是控制面的一部分，负责鉴权、限流、观测和治理。
- [推理安全与多租户边界](inference-security-and-multitenancy.md)：virtual key、budget、rate limit 是多租户隔离的关键。
- [推理性能指标与基准测试](inference-benchmarking-metrics.md)：网关层要额外记录 route decision、retry/fallback count、provider latency。
- [推理排障手册](inference-troubleshooting-runbook.md)：排障时要区分 gateway time、queue time、prefill time 和 decode time。

## 关键来源

- LiteLLM documentation: https://docs.litellm.ai/docs/
- LiteLLM proxy config overview: https://docs.litellm.ai/docs/proxy/configs
- LiteLLM OpenAI-compatible provider: https://docs.litellm.ai/docs/providers/openai_compatible
- LiteLLM Router load balancing: https://docs.litellm.ai/docs/routing
- LiteLLM Proxy load balancing: https://docs.litellm.ai/docs/proxy/load_balancing
- LiteLLM fallbacks: https://docs.litellm.ai/docs/proxy/reliability
- LiteLLM virtual keys: https://docs.litellm.ai/docs/proxy/virtual_keys
- LiteLLM budgets and rate limits: https://docs.litellm.ai/docs/proxy/users
- LiteLLM request architecture: https://docs.litellm.ai/docs/proxy/architecture
- LiteLLM config settings: https://docs.litellm.ai/docs/proxy/config_settings
