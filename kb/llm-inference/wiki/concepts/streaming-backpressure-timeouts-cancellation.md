---
type: Concept
title: Streaming、Backpressure、Timeout 与取消
description: Streaming 让用户更早看到 token，但它也把一次推理请求变成一条持续存在的链路：engine 每步 decode，server
  写出 chunk，网关保持连接，客户端持续读取。任何一段变慢，都会影响资源释放和尾延迟。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Streaming、Backpressure、Timeout 与取消

Streaming 让用户更早看到 token，但它也把一次推理请求变成一条持续存在的链路：engine 每步 decode，server 写出 chunk，网关保持连接，客户端持续读取。任何一段变慢，都会影响资源释放和尾延迟。

## Streaming 路径

| 阶段 | 发生的事 | 主要风险 |
|---|---|---|
| Decode loop | 模型逐 token 生成，并把 delta 交给 serving 层 | 长输出长期占用 KV cache 和活跃请求槽 |
| Serving server | 把 token 封装成 SSE、HTTP chunk 或 WebSocket 消息 | 慢客户端造成写缓冲堆积 |
| Gateway / proxy | 转发流式响应，执行认证、限流、超时 | idle timeout 或总超时切断长流 |
| Client | 消费事件、显示 token、处理取消和重试 | 断开后未通知后端，GPU 继续跑 |

在 OpenAI-compatible API 中，`stream=true` 通常表示服务端返回逐步增量事件。兼容层越多，越需要验证 chunk 结构、finish reason、usage 统计和错误语义是否被客户端正确解析。

## Backpressure

Backpressure 指下游消费速度跟不上上游生成速度。LLM streaming 中常见下游包括浏览器、移动网络、API gateway、日志/审计 sidecar 和 SDK 回调。

影响：

- 连接持续时间变长，占用 server worker、socket 和网关连接。
- 请求仍然占用 engine 的活跃序列和 KV cache。
- 如果服务端把 chunk 放进内存队列，慢客户端会放大内存压力。
- 如果网关 buffer 响应，用户看不到真正的 streaming，TTFT 观测会失真。

## Timeout 分层

| Timeout | 应放在哪里 | 作用 |
|---|---|---|
| 请求总时长 | 客户端、网关、平台 | 避免长输出无限占用连接 |
| idle / stream timeout | 网关、负载均衡器 | 避免长时间无 chunk 的连接挂住 |
| queue timeout | 网关或 serving 平台 | 请求还没进 engine 就快速失败 |
| engine timeout | 模型服务 | 防止异常请求长期占用 GPU |

客户端 timeout 如果短于网关和 engine，用户会看到错误，但后端未必停止生成。生产系统要确认 disconnect/cancel 可以传播到 serving server，再释放 engine 请求和 KV cache。

## 取消语义

取消不是“客户端不读了”这么简单。理想路径是：

1. 客户端关闭连接或发送取消信号。
2. 网关把断开传给 upstream。
3. Serving server 停止向该请求写 chunk。
4. Engine 从调度队列移除请求。
5. KV cache block、batch slot、统计上下文被释放。

如果第 2 到第 4 步断了，用户端看似取消成功，GPU 仍可能继续生成到 `max_tokens`。

## 参数映射

| 框架 / 层 | 参数族 | 调参含义 |
|---|---|---|
| OpenAI-compatible API | `stream=true`、SSE event parsing、finish reason、usage、background response cancel | 决定客户端如何消费增量 token；注意 background response 的取消 API 不等同于普通连接断开 |
| vLLM | OpenAI-compatible server streaming、engine/server timeout、request id、metrics | 核对 chunk 语义、取消传播和队列指标 |
| SGLang | `--stream-interval`、`--incremental-streaming-output`、`--stream-response-default-include-usage`、`--enable-streaming-session` | 控制 token chunk flush 频率、增量输出和 usage 是否随流返回 |
| TGI | streaming endpoint、`--max-concurrent-requests`、`--max-waiting-tokens`、`--waiting-served-ratio` | 控制同时存在的连接和等待请求插入 running batch 的节奏 |
| llama.cpp server | OpenAI-compatible streaming、`--timeout`、`--sse-ping-interval`、`--threads-http`、`--parallel` | 本地/边缘服务中确认 slot 是否被流式请求长期占用，SSE ping 是否能维持中间代理连接 |
| Ray Serve | `max_ongoing_requests`、`max_queued_requests`、request timeout / proxy 设置 | 控制每个 replica 同时处理多少长连接 |
| Envoy / AI Gateway | route `timeout`、`stream_idle_timeout`、`request_timeout`、`max_stream_duration`、retry/fallback、rate limit | 防止代理层中断或重复流式响应；Envoy 默认 route timeout 不适合长 streaming |

## 调参建议

- 先决定服务承诺：最长输出时长、最长 idle 间隔、客户端取消后的释放时限。
- Streaming 场景把并发按“活跃连接数”和“活跃 token 序列数”同时估算。
- 网关 idle timeout 要长于正常 token 间隔，短于异常挂起时间。
- 对 partial stream 不做盲目 retry；重试可能造成重复回答和额外成本。
- 日志系统不要同步阻塞 token chunk 写出。
- 压测时使用真正读取 streaming 的客户端，而不是只等完整响应。

## 常见误区

- TTFT 低就代表体验好：流式首 token 很快，但中途 token 间隔、断流和取消同样重要。
- 对 streaming 请求启用普通 HTTP retry：已经返回部分内容后，retry 很可能制造重复输出。
- 只在客户端设置 timeout：客户端超时不等于 GPU 释放。
- 代理默认配置未改：许多网关/负载均衡器默认不是为长时间 SSE 流设计的。
- 忽略慢消费者：少量慢客户端就可能占满连接和活跃请求槽。

## 关键来源

- OpenAI streaming responses: https://developers.openai.com/api/docs/guides/streaming-responses
- OpenAI streaming events: https://developers.openai.com/api/reference/resources/responses/streaming-events/
- OpenAI cancel response: https://developers.openai.com/api/reference/resources/responses/methods/cancel/
- vLLM OpenAI-compatible server: https://docs.vllm.ai/en/stable/serving/openai_compatible_server/
- SGLang server arguments: https://docs.sglang.io/docs/advanced_features/server_arguments
- TGI streaming: https://huggingface.co/docs/text-generation-inference/conceptual/streaming
- TGI launcher arguments: https://huggingface.co/docs/text-generation-inference/en/reference/launcher
- llama.cpp server README: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- Ray Serve deployment options: https://docs.ray.io/en/latest/serve/api/doc/ray.serve.deployment_decorator.html
- Ray Serve direct streaming: https://docs.ray.io/en/latest/serve/llm/user-guides/direct-streaming.html
- Envoy AI Gateway: https://aigateway.envoyproxy.io/docs/
- Envoy timeouts FAQ: https://www.envoyproxy.io/docs/envoy/latest/faq/configuration/timeouts
- Envoy buffer filter: https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/buffer_filter
- OpenAI API overview: https://developers.openai.com/api/reference/overview/
