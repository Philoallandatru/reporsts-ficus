---
type: Concept
title: Envoy AI Gateway 与 Gateway API Inference Extension
description: LLM 网关层正在从“HTTP 反向代理”演化为“模型路由与推理策略层”。Envoy AI Gateway 和 Kubernetes Gateway
  API Inference Extension 都围绕 Gateway API / Kubernetes 生态，把模型服务路由、策略、限流和 backend 选择从应用代码中抽出来。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Envoy AI Gateway 与 Gateway API Inference Extension

LLM 网关层正在从“HTTP 反向代理”演化为“模型路由与推理策略层”。Envoy AI Gateway 和 Kubernetes Gateway API Inference Extension 都围绕 Gateway API / Kubernetes 生态，把模型服务路由、策略、限流和 backend 选择从应用代码中抽出来。

## 两类项目定位

| 项目 | 定位 | 主要职责 |
|---|---|---|
| Envoy AI Gateway | 基于 Envoy Gateway 的 AI 流量网关 | 统一 OpenAI/Anthropic 等 API、路由、策略、限流、failover |
| Gateway API Inference Extension | Kubernetes Gateway API 的推理扩展 | 用 `InferencePool`、Endpoint Picker 等对象做 model-aware routing |

它们与 LiteLLM 的差别是：LiteLLM 更像应用层 provider proxy；Envoy/Gateway API 更偏 Kubernetes/networking control plane。

## Envoy AI Gateway 参数面

| 参数/对象 | 原理 |
|---|---|
| AI backend / provider | 定义 OpenAI、Anthropic、自托管 OpenAI-compatible 后端 |
| route | 把请求按 path/model/provider 路由到后端 |
| `AIGatewayRoute` | 用 `parentRefs`、`hostnames`、`rules` 定义 AI 请求路由 |
| `AIServiceBackend` | 定义后端 schema、backendRef 和安全策略 |
| policy | 对 route 或 backend 附加限流、鉴权、header/body 处理等策略 |
| failover | 主 backend 失败时切换到备用后端 |
| rate limit | 控制请求速率、token/模型预算或 provider 配额 |
| credentials / secret | 管理 provider API key 或内部服务凭据 |
| observability | 记录请求、路由选择、错误、延迟和策略命中 |

网关层看到的是请求和模型名，不知道 GPU 内部 KV cache 是否满。因此 Envoy AI Gateway 更适合做跨 provider 治理，不能替代 vLLM/SGLang 的 engine admission control。

关键字段：

| 字段 | 作用 |
|---|---|
| `AIGatewayRoute.parentRefs` | 绑定到 Gateway |
| `AIGatewayRoute.hostnames` | 匹配主机名 |
| `rules.matches.headers` | 按 header 匹配请求 |
| `rules.backendRefs` | 指向 `AIServiceBackend` 或 `InferencePool` |
| `timeouts` | 请求/后端超时；streaming LLM 需要更长窗口 |
| `modelsOwnedBy`、`modelsCreatedAt` | 给模型列表/API 元数据填充 owner/time |
| `llmRequestCosts` | 抽取 token/cost metadata，用于 quota/rate limit |
| `modelNameOverride` | 把客户端模型名改写为后端模型名 |
| `weight` / `priority` | 做加权流量和优先级/failover |
| `headerMutation` / `bodyMutation` | 处理 provider-specific header/body |

`AIServiceBackend` 通常包含 `schema`、`backendRef` 和 `backendSecurityPolicyRef`。认证凭据应放在后端安全策略里，而不是让客户端直接携带 provider key。

## Gateway API Inference Extension 参数面

| 对象/概念 | 原理 |
|---|---|
| `InferencePool` | 一组可服务同类模型/推理请求的后端池 |
| `InferenceModel` | 把模型名和 pool/backend 关联起来 |
| Endpoint Picker / EPP | 根据模型、负载、指标或策略挑选具体 endpoint |
| Gateway / HTTPRoute | Kubernetes Gateway API 的入口与路由对象 |
| extensionRef | 把 Gateway API 路由接到推理扩展逻辑 |
| model-aware routing | 根据模型名、请求属性或后端状态做路由，而不是只按 URL |

这个扩展的核心思想是：LLM 请求的“最优后端”不仅取决于 HTTP path，还取决于模型、副本状态、缓存、负载、队列和硬件能力。

关键字段：

| 字段 | 作用 |
|---|---|
| `InferencePool.spec.targetPorts` | 后端推理服务端口 |
| `InferencePool.spec.selector` | 选择参与 pool 的后端 Pod/endpoint |
| `InferencePool.spec.endpointPickerRef` | 指向 Endpoint Picker 服务 |
| `HTTPRoute.backendRefs.group` | 使用 `inference.networking.k8s.io` |
| `HTTPRoute.backendRefs.kind` | 指向 `InferencePool` |

Envoy AI Gateway 的 `AIGatewayRoute` 也可以把 backend 指向 `InferencePool`。不过当 backend 是 `InferencePool` 时，部分普通 backend mutation/failover 字段不会按普通 `AIServiceBackend` 方式生效，部署时要按官方兼容矩阵确认。

## 适用场景

| 场景 | 价值 |
|---|---|
| 多模型共享 Kubernetes 网关 | 把模型路由从应用代码迁到 Gateway API |
| 多 provider / 自托管混合 | 统一鉴权、路由、限流和 failover |
| 平台团队管理 LLM 后端池 | 用 CRD 和 policy 管控后端 |
| 需要模型感知路由 | endpoint picker 可引入模型/负载/缓存维度 |
| 简单单模型服务 | 可能直接用 vLLM/TGI server 更简单 |

## 常见误调

| 误调 | 后果 | 修正 |
|---|---|---|
| 只按 path 路由所有模型 | 不同模型/硬件混在一个池里 | 按模型能力、上下文、硬件和成本拆 backend/pool |
| 网关无限 failover/retry | 放大过载和成本 | 限制 retry，区分确定性错误和临时错误 |
| 网关限流与 engine 限流脱节 | 网关放进来的请求仍在 engine 排队崩溃 | 同时配置 gateway rate limit 和 engine max queue |
| 只记录网关 latency | 无法定位 prefill/decode/KV 瓶颈 | 关联 gateway、platform 和 engine metrics |
| 缓存/模型路由缺少租户维度 | 数据隔离和成本归因风险 | route metadata 带 tenant/user/model revision |
| 跨 namespace 引用失败 | Gateway API 引用被拒绝 | 配置 `ReferenceGrant` |
| token quota 不生效 | quota model name 与 override 后模型名不匹配 | 对齐 `perModelQuotas.modelName` 和 `modelNameOverride` |
| 把普通 Service 当 InferencePool | Endpoint Picker 不参与 | 使用 `InferencePool` CRD 和正确 backendRef group/kind |

## 与其他页面的关系

- [LLM 网关与路由层参数](llm-gateway-routing-parameters.md)：LiteLLM 等应用层网关的参数模型。
- [OpenAI-compatible API 语义与兼容边界](openai-compatible-api-semantics.md)：网关统一 API 不代表后端语义一致。
- [Autoscaling 与 Admission Control](autoscaling-and-admission-control.md)：网关限流必须和 engine admission 配合。
- [NVIDIA Dynamo、LMCache 与 NIXL 参数模型](nvidia-dynamo-lmcache-nixl-parameters.md)：更深的 KV-aware routing 和分布式 serving。
- [Kubernetes 模型服务部署](kubernetes-model-serving.md)：Gateway API 在 Kubernetes serving 栈里的位置。

## 关键来源

- Envoy AI Gateway documentation: https://aigateway.envoyproxy.io/docs/
- Envoy AI Gateway API reference: https://aigateway.envoyproxy.io/docs/api/
- Envoy AI Gateway traffic capabilities: https://aigateway.envoyproxy.io/docs/capabilities/traffic/
- Envoy AI Gateway AIGatewayRoute with InferencePool: https://aigateway.envoyproxy.io/docs/capabilities/inference/aigatewayroute-inferencepool/
- Envoy AI Gateway HTTPRoute with InferencePool: https://aigateway.envoyproxy.io/docs/capabilities/inference/httproute-inferencepool/
- Envoy AI Gateway repository: https://github.com/envoyproxy/ai-gateway
- Gateway API Inference Extension documentation: https://gateway-api-inference-extension.sigs.k8s.io/
- Gateway API Inference Extension repository: https://github.com/kubernetes-sigs/gateway-api-inference-extension
