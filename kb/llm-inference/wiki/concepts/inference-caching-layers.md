---
type: Concept
title: 推理缓存层：Response、Semantic、Prompt 与 KV
description: LLM 推理里“cache”这个词常被混用。Response cache、semantic cache、prompt/prefix cache、KV
  cache、KV offload 解决的是不同问题，放错层会导致隐私、质量或性能问题。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 推理缓存层：Response、Semantic、Prompt 与 KV

LLM 推理里“cache”这个词常被混用。Response cache、semantic cache、prompt/prefix cache、KV cache、KV offload 解决的是不同问题，放错层会导致隐私、质量或性能问题。

## 缓存层级

| 层级 | 缓存内容 | 命中条件 | 省掉什么 |
|---|---|---|---|
| Response cache | 完整请求到完整响应 | 请求完全相同或 key 相同 | 整次模型调用 |
| Semantic cache | 相似问题到已有响应 | embedding 相似度超过阈值 | 近似整次模型调用 |
| Provider prompt/context cache | provider 侧缓存的 prompt/context | 静态前缀或显式 cache resource | provider 侧输入重算 |
| Prompt/prefix cache | 公共 prompt 的 KV block | token 前缀完全一致 | 重复 prefill |
| KV cache | 当前活跃序列历史 K/V | 同一请求 decode 历史 | 重算历史 token |
| KV offload/storage | KV 从 GPU 移到 CPU/SSD/远端 | 需要回读历史 KV | GPU 显存 |

这些缓存命中条件不同。Prefix cache 通常要求 token 完全一致；semantic cache 只要求语义相近，但可能返回不合适或过期答案。

## Engine 内缓存

Engine 内缓存包括：

- KV cache：每个活跃请求 decode 必需。
- Prefix cache：复用公共前缀 prefill。
- KV offload/storage：把 KV 放到 CPU/local storage/remote store。
- CUDA/graph compile cache：减少启动或新 shape 成本。

典型参数和入口：

| 框架 | 参数/入口 |
|---|---|
| vLLM | automatic prefix caching、KV offload config |
| SGLang | RadixAttention、HiCache |
| TensorRT-LLM | KV cache reuse、host offload |
| LMCache | CPU RAM、local storage、remote KV、dynamic connector |
| NIM | KV cache reuse / profile 封装 |

## 网关/应用缓存

网关或应用层缓存包括：

- LiteLLM response cache。
- Redis semantic cache。
- GPTCache 类 semantic cache。
- 自建 key-value response cache。

它们适合：

- FAQ、固定问答、低风险重复请求。
- 离线批处理去重。
- 成本控制。

它们不适合：

- 用户上下文敏感请求。
- 有权限边界的数据。
- 需要最新状态的查询。
- 高风险医疗/法律/财务答案。

## Provider prompt/context cache

Provider 侧 prompt/context cache 位于应用和底层 engine 之间。它通常不暴露 KV block 细节，而是通过 cached token metrics、cache checkpoint 或 explicit cache resource 告诉用户哪些输入被复用。

典型形态：

- OpenAI prompt caching：通过 cached token 相关 usage 字段观察命中。
- Amazon Bedrock prompt caching：在 prompt 中设置 cache checkpoint，静态 prefix 改动会 miss。
- Gemini context caching：implicit cache 默认可用，explicit cache 通过 resource name 引用并设置 TTL。

它和 engine prefix cache 的共同点是优化长输入复用；区别是 provider cache 的 key、TTL、隔离和计费规则由 provider 控制。

## 调参判断

| 症状 | 可能原因 | 处理 |
|---|---|---|
| Prefix cache 命中低 | tokenizer/template/tool schema 顺序变化 | 固定模板和工具 schema 顺序 |
| Semantic cache 答非所问 | 相似度阈值过低或 embedding 模型不匹配 | 提高阈值、加 metadata filter、只缓存低风险任务 |
| Response cache 泄露隐私 | cache key 没包含租户/权限 | key 加 tenant/user/scope，或禁用共享 cache |
| KV offload p99 高 | CPU/SSD/网络回读慢 | 降低 offload、增加 GPU 显存、优化拓扑 |
| 缓存后输出不可复现 | 采样参数、模型 revision 未进入 cache key | cache key 包含模型、revision、template、sampling |

## Cache key 建议

Response cache 至少包含：

- model alias 和真实 model revision。
- tokenizer/chat template 版本。
- system prompt / tool schema hash。
- request body 规范化 hash。
- sampling 参数。
- tenant/user/permission scope。

Semantic cache 还要包含：

- embedding 模型和维度。
- 相似度阈值。
- metadata filter。
- TTL 和失效策略。

## 与其他页面的关系

- [KV cache 与 PagedAttention](kv-cache-and-paged-attention.md)：解释 KV 与 prefix cache。
- [Disaggregated serving 与 KV transfer](disaggregated-serving-and-kv-transfer.md)：KV offload/storage 和 transfer 是底层缓存问题。
- [LLM 网关与路由层参数](llm-gateway-routing-parameters.md)：response/semantic cache 常在网关层配置。
- [推理安全与多租户边界](inference-security-and-multitenancy.md)：缓存必须带租户和权限边界。

## 关键来源

- vLLM prefix caching: https://docs.vllm.ai/en/stable/design/prefix_caching/
- OpenAI prompt caching: https://developers.openai.com/api/docs/guides/prompt-caching
- Amazon Bedrock prompt caching: https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html
- Gemini context caching: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/context-cache/context-cache-overview
- Triton response cache: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/response_cache.html
- LiteLLM proxy caching: https://docs.litellm.ai/docs/proxy/caching
- LiteLLM caching providers: https://docs.litellm.ai/docs/caching/all_caches
- GPTCache GitHub: https://github.com/zilliztech/gptcache
- LMCache documentation: https://docs.lmcache.ai/
- LMCache local storage: https://docs.lmcache.ai/kv_cache/local_storage.html
- vLLM KV offloading: https://docs.vllm.ai/en/stable/features/kv_offloading_usage/
- Redis semantic cache: https://redis.io/docs/latest/develop/use-cases/semantic-cache/
