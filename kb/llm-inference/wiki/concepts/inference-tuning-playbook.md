---
type: Concept
title: 推理调参决策手册
description: 这页不是按框架列参数，而是按症状给调参路径。多数推理问题都能归到五类：显存不够、首 token 慢、生成 token 慢、吞吐低、输出不可控。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 推理调参决策手册

这页不是按框架列参数，而是按症状给调参路径。多数推理问题都能归到五类：显存不够、首 token 慢、生成 token 慢、吞吐低、输出不可控。

相关机制页：

- [KV cache 与 PagedAttention](kv-cache-and-paged-attention.md)
- [跨框架参数对照表](cross-framework-parameter-map.md)
- [Continuous batching 与推理调度](continuous-batching-and-scheduling.md)
- [推理量化](inference-quantization.md)
- [模型转换、量化与校准流水线](model-conversion-quantization-pipeline.md)
- [Speculative decoding](speculative-decoding.md)
- [采样与结构化输出](sampling-and-structured-output.md)
- [Logits Processor、惩罚项与长度控制](logits-processors-penalties-and-length-control.md)
- [推理性能指标与基准测试](inference-benchmarking-metrics.md)
- [多 GPU 并行推理](distributed-parallel-inference.md)
- [Attention kernel 与运行时优化](attention-kernels-and-runtime-optimization.md)
- [长上下文推理](long-context-inference.md)
- [MoE serving 与 expert parallel](moe-serving-and-expert-parallel.md)
- [Offload 与内存层级](offload-and-memory-hierarchy.md)
- [CPU/GPU 混合 Offload 与本地 MoE 推理](heterogeneous-cpu-gpu-offload-and-local-moe.md)
- [生产服务与运维控制面](production-serving-operations.md)
- [离线推理与批量推理](offline-and-batch-inference.md)
- [Embedding、Reranker 与 Encoder 推理](embedding-and-reranker-inference.md)
- [Disaggregated serving 与 KV transfer](disaggregated-serving-and-kv-transfer.md)
- [推理容量规划公式](capacity-planning-formulas.md)
- [推理排障手册](inference-troubleshooting-runbook.md)
- [LLM 网关与路由层参数](llm-gateway-routing-parameters.md)
- [GPU 拓扑、隔离与集群资源](gpu-topology-and-isolation.md)
- [Kubernetes 模型服务部署](kubernetes-model-serving.md)
- [推理观测、Metrics 与 Tracing](inference-observability-and-tracing.md)
- [结构化解码库生态](constrained-decoding-libraries.md)
- [推理负载建模与压测数据集](workload-modeling-and-load-testing.md)
- [CPU、边缘与 NPU 推理](cpu-edge-npu-inference.md)
- [WebLLM 参数模型](webllm-runtime-parameters.md)
- [Transformers.js 参数模型](transformers-js-runtime-parameters.md)
- [ONNX Runtime Web 参数模型](onnxruntime-web-parameters.md)
- [图编译与 Engine 构建优化](graph-compilation-and-engine-build.md)
- [推理缓存层：Response、Semantic、Prompt 与 KV](inference-caching-layers.md)
- [OpenAI-compatible API 语义与兼容边界](openai-compatible-api-semantics.md)
- [Autoscaling 与 Admission Control](autoscaling-and-admission-control.md)
- [推理成本与效率模型](inference-cost-and-efficiency.md)
- [NVIDIA Dynamo、LMCache 与 NIXL 参数模型](nvidia-dynamo-lmcache-nixl-parameters.md)
- [Envoy AI Gateway 与 Gateway API Inference Extension](envoy-ai-gateway-and-inference-extension.md)
- [Reasoning / Thinking Token 预算与 Parser](reasoning-token-budget-and-parser.md)
- [Tokenization、Validation 与预处理性能](tokenization-validation-preprocessing.md)
- [模型 Artifact 分发、缓存与冷启动](model-artifact-distribution-and-cold-start.md)
- [模型生命周期、热切换与保活](model-lifecycle-hot-swap-and-keepalive.md)
- [请求调度公平性、优先级与队列策略](request-scheduling-fairness-and-priority.md)
- [Streaming、Backpressure、Timeout 与取消](streaming-backpressure-timeouts-cancellation.md)
- [Reproducibility、Seed 与推理确定性](reproducibility-seeds-and-determinism.md)

## 症状 1：启动或长 prompt OOM

优先顺序：

1. 降低上下文上限：`ctx-size`、`max-model-len`、`session-len`、`num_ctx`。
2. 降低 prefill 峰值：`ubatch-size`、`chunked-prefill-size`、`max-batch-prefill-tokens`。
3. 降低 KV cache 精度：`cache-type-k/v`、`kv-cache-dtype`、`quant_policy`。
4. 降低并发：`parallel`、`max-running-requests`、`max-concurrent-requests`。
5. 降低权重显存：权重量化、CPU offload、少放 GPU layers。
6. 长上下文场景单独检查 RoPE scaling、sliding window、KV eviction 和 context parallel。

判断：

- prompt 一长就炸，多半是 prefill activation 或 KV cache。
- 并发一高就炸，多半是 KV cache 或 decode batch。
- 模型刚加载就炸，多半是权重/量化/TP 配置。

## 症状 2：TTFT 首 token 慢

优先顺序：

1. 开 prefix cache / RadixAttention / KV reuse。
2. 减少 prompt token，或把固定系统 prompt 缓存起来。
3. 降低 `max-batch-prefill-tokens` 的争用，避免大 prompt 阻塞小请求。
4. 使用 chunked prefill，但要验证它是否改善尾延迟还是只避免 OOM。
5. 检查 tokenizer worker / validation worker 是否成为 CPU 瓶颈。

判断：

- TTFT 慢、TPOT 正常：prefill 或排队问题。
- TTFT 和 TPOT 都慢：模型计算、offload 或并行通信问题。

## 症状 3：TPOT / decode 慢

优先顺序：

1. 增大 decode batch，但别越过延迟 SLO。
2. 开启 CUDA graph 或框架推荐的 decode graph 参数。
3. 提高 GPU offload / TP，让权重计算更多在 GPU。
4. 减少 CPU offload，除非单纯为了能跑。
5. 尝试 speculative decoding，尤其是重复性强或模板化任务。
6. 检查 attention backend / paged KV kernel 是否匹配当前 GPU、dtype 和上下文长度。

判断：

- GPU 利用率低且队列高：调度/batch 可能太保守。
- GPU 利用率高但 tokens/s 低：模型太大、量化 kernel 不佳或通信瓶颈。

## 症状 4：吞吐低但显存还有余量

优先顺序：

1. 增加 KV cache 预算：`gpu-memory-utilization`、`mem-fraction-static`、`cache-max-entry-count`、`kv_cache_free_gpu_memory_fraction`。
2. 增加并发：`max-running-requests`、`max-concurrent-requests`、`parallel`。
3. 增加 batch token budget：`max-batch-total-tokens`、`max-num-batched-tokens`、`max_num_tokens`。
4. 使用 data parallel / 多副本，而不是继续拉单实例 batch。
5. 开 prefix cache，减少重复 prefill。
6. MoE 模型检查 expert 负载、all-to-all 和 DeepEP/EP 配置。

判断：

- 小请求多：batch/request 数限制更关键。
- 长请求多：batch token budget 和 KV cache 更关键。

## 症状 5：输出不稳定或格式漂移

优先顺序：

1. 降低 `temperature`。
2. 收紧 `top_p` / `top_k` / `min_p`。
3. 增加 stop sequences。
4. 使用 JSON schema / grammar / guided decoding。
5. 修正 chat template，不要只调采样。

判断：

- 内容飘：采样和 prompt 问题。
- 格式错：优先用结构化解码。
- 角色错乱：chat template / system prompt 问题。

## 症状 6：线上 p99 延迟突然变差

优先顺序：

1. 看 queue time 和 waiting requests，确认是否进入排队崩溃。
2. 看 KV cache usage / eviction / offload hit-miss，确认是否 cache 抖动。
3. 看 prefix cache hit rate，确认公共前缀是否被版本或模板变化破坏。
4. 看 CUDA graph 命中和 warmup 是否覆盖当前 batch shape。
5. 看 rate limit、max queued requests 和 admission control 是否过宽。

## 症状 7：离线批量吞吐低

优先顺序：

1. 区分数据层 batch 和 engine 层 batch：先看 GPU 是否在等数据。
2. 增大数据层 `batch_size`、`concurrency` 或 worker/replica 数。
3. 调大 engine 的 batch token budget，但观察 OOM 和长样本重试成本。
4. 按输入长度分桶，避免少数超长样本拖慢整批。
5. 固定 `custom_id`、模型 revision、采样参数和 chat template，保证输出可追溯。

## 症状 8：Embedding/Rerank 结果质量或成本异常

优先顺序：

1. 检查 pooling、normalize、prompt 前缀和模型 revision。
2. 对 reranker 限制候选文档数和 pair 最大 token 长度。
3. 增大 `max-batch-tokens` / `batch_size` 前先确认 tokenization 不是 CPU 瓶颈。
4. 估算向量输出体积，必要时使用 fp16/int8、binary embedding 或 `truncate_dim`。
5. 离线 embedding 与线上召回必须使用同一模型、模板和归一化策略。

## 症状 9：Prefill/decode 分离收益不明显

优先顺序：

1. 先算 KV transfer bytes，确认网络/互连带宽足够。
2. 只对长 prompt、短输出、TTFT 受 prefill 影响明显的业务启用。
3. 检查 KV connector、KV role、failure policy 和 compatibility matrix。
4. 对长短请求分池，避免短请求承担长 prompt 的 KV transfer 成本。
5. 监控 transfer time、KV load failure、prefix cache hit rate 和 p99 TTFT。

## 症状 10：同一模型在不同部署栈输出不一致

优先顺序：

1. 对齐 tokenizer、chat template、special tokens、stop/eos。
2. 对齐 `GenerationConfig` / sampling params，不要只看 OpenAI-compatible 字段名是否相同。
3. 检查权重量化、ONNX/MLC 编译产物和 execution provider 是否改变数值路径。
4. 对比 Transformers 本地输出，把它作为语义基线。
5. 网关层确认 `model_name` 没有路由到多个真实模型版本。

## 症状 11：多后端服务成功率或成本不可控

优先顺序：

1. 在网关层设置 virtual key、team/user budget、RPM/TPM 和并发限制。
2. 给 provider 临时错误配置 retry/fallback，但不要重试确定性输入错误。
3. 为每个 model alias 记录真实 backend、model revision、默认采样和模板。
4. 分开观测 gateway latency、provider latency、engine queue time、TTFT 和 TPOT。

## 症状 12：Kubernetes 扩容后吞吐不升

优先顺序：

1. 检查 Pod 是否真的拿到独立 GPU/MIG slice，而不是多个副本挤同一设备。
2. 检查网关/Service 是否把流量打到新副本。
3. 检查权重冷启动是否让新副本长期未就绪。
4. 检查 NCCL/NVLink/RDMA 路径，确认多 GPU 通信没有走慢路径。
5. 用 DCGM、engine metrics 和 gateway metrics 同时看，避免只看 Pod 数。

## 症状 13：压测数据好看，上线体验差

优先顺序：

1. 对齐 prompt/output 长度分布，不要用短 synthetic 流量代表真实 RAG/agent。
2. 使用 open-loop 压测看排队崩溃点。
3. 记录 prefix sharing、template、tool schema 和 tokenizer revision。
4. 用 goodput 而不是总 tokens/s 判断可用容量。
5. 把网关 retry/fallback 纳入 E2E latency 和成本。

## 症状 14：本地/端侧能跑但很慢

优先顺序：

1. 确认模型是否真的跑在目标后端：Metal、OpenVINO、QNN、CUDA、WebGPU，而不是 CPU fallback。
2. 降低权重量化 bits、上下文长度和输出长度。
3. 调整 CPU 线程、batch 和内存映射；CPU/NPU 不适合直接套 GPU serving 参数。
4. 对 Apple silicon 关注统一内存压力；对 NPU 关注模型转换和算子覆盖。
5. 固定转换/编译产物版本，避免“同名模型”实际执行图不同。

## 症状 14b：浏览器/WebGPU 推理加载慢或不稳定

优先顺序：

1. 先做 feature detection：WebGPU/WebNN 不可用时准备 WASM 或服务端 fallback。
2. 检查模型下载体积、cacheBackend、IndexedDB/Cache API 命中和版本清理策略。
3. 限制 context window、max output tokens 和同时运行的 pipeline/engine 数。
4. WebLLM 使用 Worker / Service Worker；Transformers.js 避免大模型长生成阻塞 UI。
5. ONNX Runtime Web 检查 `executionProviders`、WASM threads/SIMD、WebGPU IO binding 和算子 fallback。

## 症状 15：首批请求慢或升级后性能漂移

优先顺序：

1. 区分权重加载、engine build、`torch.compile`、CUDA Graph capture 和模型 warmup。
2. 生产使用预编译 engine/model lib，并缓存转换产物。
3. warmup 覆盖真实 batch shape 和上下文长度，而不是只跑短 prompt。
4. 记录 TensorRT-LLM build 参数、ONNX graph optimization level、MLC compile overrides。
5. 异常时先回到 eager/未编译路径验证正确性，再逐步打开 graph/compile。

## 症状 16：专用加速器上改参数后重新变慢

优先顺序：

1. 判断是否触发重新编译：Neuron、TPU/XLA、OpenVINO、TensorRT engine 都可能把 shape 固化。
2. 检查 persistent cache / compile cache 是否命中。
3. 确认 batch、context、TP/sharding、profile 是否仍匹配硬件。
4. 把冷启动、compile 时间和 steady-state latency 分开记录。
5. 不要把 CUDA/vLLM GPU 参数直接套到 Neuron/TPU/NPU 后端。

## 症状 17：加缓存后质量或安全出问题

优先顺序：

1. 区分 response cache、semantic cache、prefix cache 和 KV cache，先定位是哪一层命中。
2. Response cache key 必须包含 model revision、template、sampling、tenant/permission scope。
3. Semantic cache 要设置 metadata filter、TTL 和足够高的相似度阈值。
4. Prefix cache 命中低时检查 tokenizer、tool schema 顺序和 system prompt 是否变化。
5. 涉及用户私有上下文或实时状态的请求，默认不要跨租户共享缓存。

## 症状 18：OpenAI-compatible 接入后行为不一致

优先顺序：

1. 对齐 tokenizer、chat template、special tokens、stop/eos 和默认 sampling。
2. 检查 streaming chunk、usage、finish reason 和 tool call delta 是否被客户端正确解析。
3. 如果使用 tool calling，固定 parser、tool schema 顺序和模型 revision。
4. 区分标准 OpenAI 字段和后端扩展字段；迁移后端时先关闭扩展。
5. 网关层记录真实 backend，而不是只记录 `model` alias。

## 症状 19：Autoscaling 后 p99 仍然很差

优先顺序：

1. 看 engine queue time，而不是只看 Pod 数或 GPU utilization。
2. 检查新副本是否完成权重加载、warmup 和 CUDA graph capture。
3. 限制 max queue / ongoing requests，让过载快速失败或降级。
4. 按请求长度分池，避免长 prompt 把短请求一起拖慢。
5. 用 TTFT、TPOT、goodput 和 rejection rate 一起评估扩容阈值。

## 症状 20：成本/token 高但吞吐看起来不错

优先顺序：

1. 用 goodput 而不是总 tokens/s 重新计算成本。
2. 把失败重试、fallback、冷启动和空闲副本计入成本。
3. 分开 input-heavy、output-heavy 和 mixed 负载建模。
4. 评估 prefix/prompt cache 命中率，确认模板和 revision 没有破坏缓存。
5. 量化或 speculative decoding 之前先跑质量回归，避免便宜但不可用。

## 症状 21：Embedding/Rerank 服务吞吐低或质量漂移

优先顺序：

1. 先确认这是 TEI/vLLM pooling/Sentence Transformers/OpenVINO 哪条路径，不要套用生成式 LLM 采样参数。
2. 吞吐低时看 tokenization worker、`max-batch-tokens`、输入长度和向量输出带宽。
3. 质量漂移时优先检查 pooling、query/passage prompt、normalize、truncate dim 和模型 revision。
4. Rerank 延迟高时先限制候选文档数和 pair 长度，再调 batch。
5. OpenAI-compatible embedding endpoint 返回正常不代表 pooling/prompt 正确。

## 症状 22：Ray Serve LLM 扩容了但单副本仍慢

优先顺序：

1. 区分 Ray 层 replica/autoscaling 与 vLLM engine 层 batch/KV 参数。
2. 检查 `target_ongoing_requests`、`max_ongoing_requests` 是否让请求堆在单副本。
3. 检查 `engine_kwargs` 是否传入了正确的上下文、TP、显存利用率和 batch token 预算。
4. 新副本接流量前确认模型加载、warmup 和 readiness。
5. 在线服务用 Ray Serve，离线批处理用 Ray Data LLM，避免参数混用。

## 症状 23：Dynamo/LMCache/NIXL 后 TTFT 没降

优先顺序：

1. 先算 KV transfer bytes，确认网络、RDMA、NVLink/PCIe 路径能支撑。
2. 看 KV/cache hit rate 和 router 决策，确认请求被路由到有前缀/KV 的 worker。
3. 检查 tokenizer、chat template、tool schema 和 revision 是否破坏 prefix hash。
4. 监控 transfer time、KV load failure、queue time、prefill time 和 decode time。
5. 如果是短 prompt 随机负载，优先回到单 engine batch/replica 调优。

## 症状 24：BentoML/OpenLLM 服务启动了但 GPU 利用或延迟异常

优先顺序：

1. 区分 BentoML service 层和 vLLM/Transformers engine 层。
2. GPU LLM 先避免多个 worker 抢同一 GPU；确认 engine 自己的 continuous batching 生效。
3. 检查 `traffic.timeout`、资源声明、Hugging Face token、权重缓存和 warmup。
4. OpenAI-compatible API 正常时仍要核对 chat template、sampling 和模型 revision。
5. 如果瓶颈在 KV cache/batch，回到底层 engine 参数页调。

## 症状 25：KServe 部署 ready 慢或扩容后没效果

优先顺序：

1. 检查 `storageUri`、secret、PVC/对象存储和临时盘，先排除权重拉取慢。
2. 检查 runtime image/tag 和 engine args 是否与目标 vLLM/TGI/Triton 版本匹配。
3. 确认 Pod 拿到独立 GPU/MIG slice，并且 readiness 在 warmup 后才放流量。
4. Knative/KServe/HPA 的并发目标要结合 engine queue/TTFT/TPOT。
5. scale-to-zero 对大模型默认谨慎，优先保留 min replicas。

## 症状 26：AI Gateway 统一路由后质量、成本或延迟波动

优先顺序：

1. 检查一个模型别名是否路由到不同 revision、template 或采样默认值。
2. failover/retry 只用于临时后端错误，不要重试 prompt 太长、schema 错等确定性错误。
3. 限流同时设在 gateway 和 engine admission，避免请求只是在 engine 内排队。
4. 记录 route decision、backend、provider latency、engine queue time、TTFT 和 TPOT。
5. 多租户场景让 route/cache metadata 带 tenant、scope 和预算。

## 症状 27：Reasoning 模型答案短、慢或成本异常

优先顺序：

1. 确认 reasoning/thinking token 是否和最终答案共享输出预算。
2. 降低 reasoning effort 或 thinking budget，给最终答案留足 token。
3. 自托管模型检查 reasoning parser、chat template、stop token 和 streaming delta。
4. Tool/JSON 输出场景确认 reasoning 内容不会混进结构化字段。
5. 成本报表单独记录 hidden/reasoning token、answer token 和截断率。

## 症状 28：GPU 空闲但 TTFT 高

优先顺序：

1. 分开看 preprocessing、tokenization、validation、engine queue 和 prefill。
2. 增加 tokenizer/validation worker 前先确认 CPU、线程和内存不是新瓶颈。
3. 固定 chat template 和 tokenizer revision，避免 prompt token 数漂移。
4. 对 tool/agent 流量压缩 tool schema 和历史消息。
5. 多模态请求检查媒体下载、解码、processor 和安全域名限制。

## 症状 29：扩容或发布后首批请求很慢

优先顺序：

1. 分开记录镜像拉取、权重下载、模型加载、engine build、warmup 和首请求时间。
2. 固定模型 revision、runtime image tag、profile 和 engine build 参数。
3. 使用 PVC/本地 NVMe/cache 复用权重，避免每个 Pod 重新下载。
4. readiness 之后用真实 batch shape 做 warmup，再接生产流量。
5. 大模型谨慎 scale-to-zero，必要时保留 min replicas 或热备。

## 症状 30：多租户或长短请求互相影响

优先顺序：

1. 分开看 gateway queue、platform queue 和 engine queue，不要只看总体延迟。
2. 给 engine 和平台队列设置 `max_queued_requests` / `max_ongoing_requests` 一类上限。
3. 交互请求、批处理请求和长上下文请求分池，必要时用 priority。
4. Prefix-aware/LPM 调度要同时看 cache hit rate 和低优先级等待时间。
5. 多租户按 token、请求数、并发和预算一起限流。

## 症状 31：Streaming 断开后 GPU 还在跑

优先顺序：

1. 确认客户端断开是否传到网关，再传到 serving server。
2. 检查 serving server 是否把取消请求从 engine 调度队列移除。
3. 给 streaming 设置总 timeout、idle timeout 和最大输出 token。
4. 对已经返回 partial stream 的请求谨慎 retry，避免重复输出和重复计费。
5. 压测时使用真正消费 SSE/chunk 的客户端，模拟慢消费者。

## 症状 32：同 seed 或 temperature=0 仍不能完全复现

优先顺序：

1. 固定模型 revision、tokenizer、chat template、special tokens、stop/eos。
2. 固定完整 `GenerationConfig` / sampling params，不要依赖默认值。
3. 在单请求、单 GPU、固定 dtype 和固定版本下建立逐 token 基线。
4. 检查 batch 调度、prefix cache、chunked prefill、attention backend 和量化 kernel。
5. 分布式/低精度服务优先做语义或结构回归，除非业务确实要求 bitwise 复现。

## 症状 33：调了 penalty 后输出更怪

优先顺序：

1. 先确认是不是 prompt/template 导致复读，不要立刻加大 repetition penalty。
2. JSON、代码、SQL、协议输出优先使用 schema/grammar，而不是强行惩罚重复 token。
3. 固定 tokenizer 后再设置 `logit_bias`，不同模型的 token ID 不能复用。
4. `min_tokens` / `min_new_tokens` 只在确实需要长答时使用，避免阻止 EOS。
5. 多候选、beam、best-of 会放大 KV cache 和延迟，容量估算要按候选序列数算。

## 症状 34：LocalAI / mistral.rs 这类本地兼容层能跑但线上不稳

优先顺序：

1. 先确认真实 backend、device、dtype、量化格式和模型 artifact，不要只看 OpenAI-compatible API。
2. LocalAI 检查模型 YAML、`context_size`、线程、GPU offload、预加载和 backend 支持的字段。
3. mistral.rs 检查 serve 参数、ISQ/量化路径、PagedAttention、KV cache 和 chat template。
4. 如果瓶颈是高并发调度，评估是否应换 vLLM/SGLang/TGI 这类 engine-first serving。
5. 客户端迁移时重点回归 stream chunk、stop/eos、usage、tool/JSON 和默认采样。

## 症状 35：CPU/GPU 混合 offload 能跑但 token 很慢

优先顺序：

1. 记录真实层/expert/KV cache 放置，确认哪些计算每 token 都跨 PCIe 或系统内存。
2. MoE 模型先把 attention、router、热 expert 留在 GPU，再考虑冷 expert offload。
3. 检查 NUMA、CPU 内存带宽、page fault、mmap/page cache warmup 和 PCIe/NVLink throughput。
4. 降低上下文和并发，确认瓶颈是权重搬运还是 KV cache 搬运。
5. 如果 p99 是目标，优先换高吞吐 serving 或更小/更强量化模型，而不是继续堆 offload。

## 症状 36：模型热切换后延迟或质量漂移

优先顺序：

1. 为每个 alias 固定真实 model id、revision、quantization、template、default sampling 和 adapter。
2. 切换前先 drain 旧请求，尤其是长 streaming 和 tool calling 请求。
3. 区分 disk cache、loaded、warm 三种状态；权重在磁盘不代表首 token 快。
4. 对 Ollama/LocalAI/TabbyAPI/llama-swap 这类多模型入口记录 load/unload/keepalive 事件。
5. 如果显存碎片或冷启动频繁，拆分模型池或保留 min warm replicas。

## 症状 37：迁移框架后同样参数效果完全不同

优先顺序：

1. 先确认参数属于哪一层：网关、平台包装层、engine、kernel，还是请求采样。
2. 用 [跨框架参数对照表](cross-framework-parameter-map.md) 把同类参数映射到目标框架原名。
3. 区分 replica、worker、tensor parallel、GPU layer offload：它们都可能用多 GPU，但资源模型不同。
4. 上下文迁移时同时迁移 KV cache budget、并发序列数和 batch token budget。
5. OpenAI-compatible API 迁移后重点回归 stream、usage、tool calling、stop/eos 和默认 sampling。

## 症状 38：量化模型能加载但质量明显变差

优先顺序：

1. 确认是否从 fp16/bf16/f32 源权重量化，避免从低 bit artifact 二次量化。
2. 检查 calibration dataset 是否覆盖真实语言、prompt 模板、长上下文和结构化输出。
3. GGUF 路线检查 quant type、imatrix、output/embedding tensor 是否过度量化。
4. AWQ/GPTQ 路线检查 bits、group size、sym/asym、kernel backend 和 runtime 兼容矩阵。
5. FP8 路线检查 scale 生成方式、硬件架构和 KV cache dtype。

## 框架参数对照

| 目标 | llama.cpp | vLLM | SGLang | TGI | TensorRT-LLM | Ollama | LMDeploy |
|---|---|---|---|---|---|---|---|
| 上下文 | `--ctx-size` | `--max-model-len` | `--context-length` | `--max-total-tokens` / `--max-input-tokens` | `--max_seq_len` | `num_ctx` | `--session-len` |
| KV 预算 | `--cache-type-k/v`、`--parallel` | `--gpu-memory-utilization`、`--kv-cache-memory-bytes` | `--mem-fraction-static` | `--max-batch-total-tokens`、`--kv-cache-dtype` | `--kv_cache_free_gpu_memory_fraction` | 间接由 `num_ctx` 决定 | `--cache-max-entry-count` |
| 并发 | `--parallel`、`--cont-batching` | batch/scheduler args | `--max-running-requests` | `--max-concurrent-requests` | `--max_batch_size` | 服务级并发较少暴露 | `max_batch_size` |
| 预填充 | `--batch-size`、`--ubatch-size` | chunked prefill / scheduler 参数 | `--chunked-prefill-size` | `--max-batch-prefill-tokens` | `--max_num_tokens` | 无明显独立项 | `prefill_interval` |
| 多 GPU | `--gpu-layers`、`--split-mode`、`--tensor-split` | `--tp`、`--pp`、`--dp` | `--tp`、`--dp`、`--nnodes` | `--num-shard` | `--tp_size`、`--pp_size`、`--ep_size` | 自动/较少暴露 | `--tp` |
| 采样 | `--temperature`、`--top-p`、`--top-k` 等 | 请求级 sampling params | 请求级 sampling params | 请求级 sampling params | OpenAI-compatible request / generation config | `PARAMETER` | request / pipeline config |

## 关键来源

- [来源清单](../../SOURCES.md)
