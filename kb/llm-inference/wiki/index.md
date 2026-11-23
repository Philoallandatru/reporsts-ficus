# LLM Inference Wiki

## 学习路径

1. [推理参数分类总览](concepts/inference-parameter-taxonomy.md)
2. [KV cache 与 PagedAttention](concepts/kv-cache-and-paged-attention.md)
3. [Continuous batching 与推理调度](concepts/continuous-batching-and-scheduling.md)
4. [推理调参决策手册](concepts/inference-tuning-playbook.md)
5. 按框架阅读具体参数页

## 推理机制索引

| 机制 | 解决的问题 | 入口 |
|---|---|---|
| KV cache / PagedAttention | 长上下文、并发与显存碎片 | [KV cache 与 PagedAttention](concepts/kv-cache-and-paged-attention.md) |
| Cross-framework parameter map | 同类参数在不同框架里的命名和语义差异 | [跨框架参数对照表](concepts/cross-framework-parameter-map.md) |
| Continuous batching / chunked prefill | GPU 利用率、TTFT、队列调度 | [Continuous batching 与推理调度](concepts/continuous-batching-and-scheduling.md) |
| 推理量化 | 权重显存、KV cache 显存、低精度 kernel | [推理量化](concepts/inference-quantization.md) |
| 转换 / 校准 / artifact | HF checkpoint 到 GGUF/AWQ/GPTQ/FP8、校准数据、发布验收 | [模型转换、量化与校准流水线](concepts/model-conversion-quantization-pipeline.md) |
| GGUF quant 工具链 | convert_hf_to_gguf、llama-quantize、imatrix、metadata | [GGUF 转换与 llama.cpp 量化工具链](concepts/gguf-conversion-and-llama-quantize.md) |
| AWQ / GPTQ / FP8 工具链 | LLM Compressor、GPTQModel、AutoAWQ、TensorRT-LLM quant | [AWQ、GPTQ 与 FP8 量化工具链](concepts/awq-gptq-fp8-quantization-toolchain.md) |
| Speculative decoding | 降低 decode 步数和单 token 延迟 | [Speculative decoding](concepts/speculative-decoding.md) |
| 采样与结构化输出 | 输出质量、多样性、JSON/grammar 约束 | [采样与结构化输出](concepts/sampling-and-structured-output.md) |
| Logits processor / penalty | repetition、presence/frequency penalty、logit bias、长度控制 | [Logits Processor、惩罚项与长度控制](concepts/logits-processors-penalties-and-length-control.md) |
| Benchmark 指标 | TTFT、TPOT、throughput、goodput、SLO | [推理性能指标与基准测试](concepts/inference-benchmarking-metrics.md) |
| 多 GPU 并行 | 模型放置、跨卡通信、扩吞吐 | [多 GPU 并行推理](concepts/distributed-parallel-inference.md) |
| Attention kernel / runtime | FlashAttention、FlashInfer、CUDA Graph、Triton | [Attention kernel 与运行时优化](concepts/attention-kernels-and-runtime-optimization.md) |
| 长上下文推理 | RoPE scaling、YaRN、滑动窗口、KV eviction | [长上下文推理](concepts/long-context-inference.md) |
| MoE serving | expert parallel、routing、all-to-all、DeepEP | [MoE serving 与 expert parallel](concepts/moe-serving-and-expert-parallel.md) |
| Offload / 内存层级 | CPU offload、KV offload、PCIe/NVLink、pinned memory | [Offload 与内存层级](concepts/offload-and-memory-hierarchy.md) |
| 异构 CPU/GPU offload | 本地 MoE、expert offload、PCIe/NUMA、系统内存带宽 | [CPU/GPU 混合 Offload 与本地 MoE 推理](concepts/heterogeneous-cpu-gpu-offload-and-local-moe.md) |
| 生产服务控制面 | admission control、rate limit、metrics、warmup、autoscaling | [生产服务与运维控制面](concepts/production-serving-operations.md) |
| 多模态推理 | 图像/视频 token、vision encoder、projector、媒体限制 | [多模态推理与媒体 token 预算](concepts/multimodal-inference.md) |
| LoRA / adapter serving | 多 adapter 合批、rank、cache、量化兼容 | [LoRA 与 adapter serving](concepts/lora-and-adapter-serving.md) |
| 模型格式与加载 | safetensors、GGUF、revision、mmap、remote code | [模型格式、加载与供应链边界](concepts/model-formats-and-loading.md) |
| Tokenizer / chat template | special tokens、tool messages、模板错配 | [Tokenizer、chat template 与 token 预算](concepts/tokenizer-and-chat-templates.md) |
| Tool/function calling | tool schema、guided decoding、parser、OpenAI-compatible API | [Tool/function calling 推理路径](concepts/tool-calling-inference.md) |
| 安全与多租户 | API key、CORS、allowed media domains、limits、隔离 | [推理安全与多租户边界](concepts/inference-security-and-multitenancy.md) |
| 离线 / 批量推理 | JSONL batch、数据流水线、engine batch、重试 | [离线推理与批量推理](concepts/offline-and-batch-inference.md) |
| Embedding / reranker | pooling、向量输出、cross-encoder、pair batch | [Embedding、Reranker 与 Encoder 推理](concepts/embedding-and-reranker-inference.md) |
| Disaggregated serving | prefill/decode 分离、KV transfer、connector | [Disaggregated serving 与 KV transfer](concepts/disaggregated-serving-and-kv-transfer.md) |
| 容量规划 | 权重显存、KV cache、并发、带宽公式 | [推理容量规划公式](concepts/capacity-planning-formulas.md) |
| 排障 runbook | OOM、cache thrashing、template mismatch、tail latency | [推理排障手册](concepts/inference-troubleshooting-runbook.md) |
| 网关 / 路由 | fallback、retry、virtual key、budget、rate limit | [LLM 网关与路由层参数](concepts/llm-gateway-routing-parameters.md) |
| GPU 拓扑 / 隔离 | MIG、MPS、NVLink、NCCL、DCGM、device plugin | [GPU 拓扑、隔离与集群资源](concepts/gpu-topology-and-isolation.md) |
| Kubernetes 部署 | KServe、Ray Serve、KubeRay、BentoML、权重缓存 | [Kubernetes 模型服务部署](concepts/kubernetes-model-serving.md) |
| 观测 / tracing | OpenTelemetry、Prometheus、metrics、告警 | [推理观测、Metrics 与 Tracing](concepts/inference-observability-and-tracing.md) |
| 结构化解码库 | Outlines、Guidance、LMFE、XGrammar、GBNF | [结构化解码库生态](concepts/constrained-decoding-libraries.md) |
| 负载建模 / 压测 | ShareGPT、synthetic、open-loop、goodput、SLO | [推理负载建模与压测数据集](concepts/workload-modeling-and-load-testing.md) |
| CPU / 边缘 / NPU | CPU BLAS、Apple silicon、OpenVINO、QNN、WebGPU | [CPU、边缘与 NPU 推理](concepts/cpu-edge-npu-inference.md) |
| Browser / WebGPU | WebLLM、Transformers.js、ONNX Runtime Web、WASM/WebGPU/WebNN | [WebLLM 参数模型](concepts/webllm-runtime-parameters.md) |
| 图编译 / engine build | TensorRT build、CUDA Graph、torch.compile、ONNX/OpenVINO/MLC | [图编译与 Engine 构建优化](concepts/graph-compilation-and-engine-build.md) |
| 缓存层 | response cache、semantic cache、prefix cache、KV offload | [推理缓存层](concepts/inference-caching-layers.md) |
| OpenAI-compatible API | endpoint、streaming、tool call、usage、兼容边界 | [OpenAI-compatible API 语义](concepts/openai-compatible-api-semantics.md) |
| Autoscaling / admission | 队列、并发、KPA、Ray Serve、KEDA、限流 | [Autoscaling 与 Admission Control](concepts/autoscaling-and-admission-control.md) |
| 成本 / 效率 | cost/token、goodput、缓存命中、SLO 成本 | [推理成本与效率模型](concepts/inference-cost-and-efficiency.md) |
| 分布式 KV-aware serving | Dynamo、LMCache、NIXL、router、multi-tier KV cache | [NVIDIA Dynamo、LMCache 与 NIXL 参数模型](concepts/nvidia-dynamo-lmcache-nixl-parameters.md) |
| AI 网关 / 推理扩展 | Envoy AI Gateway、InferencePool、Endpoint Picker、model-aware routing | [Envoy AI Gateway 与 Gateway API Inference Extension](concepts/envoy-ai-gateway-and-inference-extension.md) |
| Reasoning / thinking token | reasoning effort、thinking budget、parser、hidden token 成本 | [Reasoning / Thinking Token 预算与 Parser](concepts/reasoning-token-budget-and-parser.md) |
| Tokenization / validation | tokenizer worker、chat template、请求校验、预处理 CPU 瓶颈 | [Tokenization、Validation 与预处理性能](concepts/tokenization-validation-preprocessing.md) |
| Artifact / cold start | Hugging Face cache、storageUri、NIM profile、模型下载、warmup | [模型 Artifact 分发、缓存与冷启动](concepts/model-artifact-distribution-and-cold-start.md) |
| Model lifecycle / hot swap | 模型加载、卸载、keepalive、drain、alias/version 固定 | [模型生命周期、热切换与保活](concepts/model-lifecycle-hot-swap-and-keepalive.md) |
| Fairness / priority queue | 多租户公平性、优先级、长短请求互相影响、队列上限 | [请求调度公平性、优先级与队列策略](concepts/request-scheduling-fairness-and-priority.md) |
| Streaming / cancellation | SSE、backpressure、timeout、客户端断开、partial retry | [Streaming、Backpressure、Timeout 与取消](concepts/streaming-backpressure-timeouts-cancellation.md) |
| Reproducibility / seed | seed、temperature=0、batch 调度、CUDA/cuBLAS 确定性 | [Reproducibility、Seed 与推理确定性](concepts/reproducibility-seeds-and-determinism.md) |

## 框架索引

| 框架 | 最适合关注的参数面 | 入口 |
|---|---|---|
| llama.cpp | 本地推理、GGUF、CPU/GPU offload、KV cache dtype、continuous batching | [llama.cpp 参数模型](concepts/llama-cpp-runtime-parameters.md) |
| llama-cpp-python | Python binding、OpenAI-compatible server、`Llama(...)`、多模型 config | [llama-cpp-python 参数模型](concepts/llama-cpp-python-runtime-parameters.md) |
| vLLM | 高吞吐服务、PagedAttention、continuous batching、prefix caching、GPU memory budget、LoRA | [vLLM Engine Args 参数模型](concepts/vllm-engine-parameters.md) |
| SGLang | 结构化生成、RadixAttention、长上下文、多种并行、prefill/decode disaggregation | [SGLang Server Arguments 参数模型](concepts/sglang-server-parameters.md) |
| Hugging Face TGI | Hugging Face 生态部署、router 限流、batch token budget、sharding、LoRA | [TGI Launcher 参数模型](concepts/tgi-launcher-parameters.md) |
| TensorRT-LLM | NVIDIA 生产部署、TensorRT/PyTorch backend、in-flight batching、KV cache reuse、TP/PP/EP | [TensorRT-LLM Serving 参数模型](concepts/tensorrt-llm-serving-parameters.md) |
| Ollama | 本地模型封装、Modelfile、采样默认值、上下文窗口、adapter/template | [Ollama 参数模型](concepts/ollama-runtime-parameters.md) |
| LMDeploy | OpenMMLab 生态、TurboMind/PyTorch backend、KV cache 占比、session length | [LMDeploy 参数模型](concepts/lmdeploy-serving-parameters.md) |
| DeepSpeed Inference / MII | DeepSpeed kernel injection、tensor parallel、CUDA Graph、Triton、MII 副本服务 | [DeepSpeed 参数模型](concepts/deepspeed-inference-mii-parameters.md) |
| OpenVINO GenAI | Intel CPU/GPU/NPU 推理、GenerationConfig、beam search、speculative decoding | [OpenVINO GenAI 参数模型](concepts/openvino-genai-parameters.md) |
| Hugging Face Transformers | `GenerationConfig`、chat template、device map、streamer、assisted decoding | [Transformers Generation 参数模型](concepts/huggingface-transformers-generation-parameters.md) |
| ONNX Runtime GenAI | ONNX 本地/端侧推理、Execution Provider、SearchOptions、Adapters | [ONNX Runtime GenAI 参数模型](concepts/onnxruntime-genai-parameters.md) |
| ONNX Runtime Web | 浏览器 ONNX runtime、WASM/WebGPU/WebNN EP、SessionOptions、IO binding | [ONNX Runtime Web 参数模型](concepts/onnxruntime-web-parameters.md) |
| MLC LLM | TVM 编译部署、跨平台 runtime、量化、REST/OpenAI API | [MLC LLM 参数模型](concepts/mlc-llm-runtime-parameters.md) |
| WebLLM | 浏览器内 LLM、WebGPU、MLC artifact、OpenAI-compatible chat、cache | [WebLLM 参数模型](concepts/webllm-runtime-parameters.md) |
| Transformers.js | 浏览器/Node pipeline、ONNX Runtime、WASM/WebGPU、dtype | [Transformers.js 参数模型](concepts/transformers-js-runtime-parameters.md) |
| NVIDIA Triton | 通用模型服务器、TensorRT-LLM/vLLM backend、dynamic batching、instance group | [Triton LLM 参数模型](concepts/triton-inference-server-llm-parameters.md) |
| MLX LM | Apple silicon 本地推理、MLX 格式、量化、prompt cache、server | [MLX LM 参数模型](concepts/mlx-lm-runtime-parameters.md) |
| CTranslate2 | CPU/GPU Transformer runtime、compute type、线程、batch、转换量化 | [CTranslate2 参数模型](concepts/ctranslate2-runtime-parameters.md) |
| ExLlamaV2 | NVIDIA 本地低比特推理、EXL2/GPTQ、KV cache、GPU split | [ExLlamaV2 参数模型](concepts/exllamav2-runtime-parameters.md) |
| NVIDIA NIM | NVIDIA 生产微服务、profile、OpenAI API、LoRA、metrics | [NVIDIA NIM 参数模型](concepts/nvidia-nim-llm-parameters.md) |
| AWS Neuron | Inferentia/Trainium、Neuron compile、TP、persistent cache、vLLM Neuron | [AWS Neuron 参数模型](concepts/aws-neuron-inference-parameters.md) |
| Google TPU / JetStream | TPU slice、XLA compile、vLLM TPU、JetStream、MaxText | [Google TPU 与 JetStream 推理](concepts/google-tpu-jetstream-inference.md) |
| Intel IPEX / Optimum | Intel CPU/GPU/NPU、OpenVINO、low-bit、Optimum Intel | [Intel IPEX-LLM 与 Optimum Intel](concepts/intel-ipex-optimum-inference.md) |
| SageMaker / DJL LMI | SageMaker endpoint、LMI container、serving.properties、vLLM/TRT-LLM backend | [SageMaker / DJL LMI 参数模型](concepts/sagemaker-djl-lmi-parameters.md) |
| FastChat / Sonar-Aphrodite | OpenAI-compatible demo/worker 编排、vLLM-family engine、量化/API 扩展 | [FastChat 与 Sonar/Aphrodite 参数模型](concepts/fastchat-and-aphrodite-parameters.md) |
| Hugging Face TEI | embedding、rerank、pooling、batch tokens、tokenization workers | [Hugging Face TEI 参数模型](concepts/huggingface-tei-parameters.md) |
| Ray Serve LLM | Ray Serve deployment、LLMConfig、engine_kwargs、autoscaling | [Ray Serve LLM 参数模型](concepts/ray-serve-llm-parameters.md) |
| BentoML / OpenLLM | service artifact、resources、traffic、worker、vLLM wrapper | [BentoML / OpenLLM 参数模型](concepts/bentoml-openllm-parameters.md) |
| KServe Generative Inference | InferenceService、ServingRuntime、storageUri、vLLM runtime、autoscaling | [KServe Generative Inference 参数模型](concepts/kserve-generative-inference-parameters.md) |
| LocalAI | 本地 OpenAI-compatible API、模型 YAML、backend、grammar、embedding | [LocalAI 参数模型](concepts/localai-runtime-parameters.md) |
| Xinference | 多模型平台、supervisor/worker、replica、backend engine 选择 | [Xinference 参数模型](concepts/xinference-runtime-parameters.md) |
| mistral.rs | Rust 本地推理、OpenAI-compatible server、ISQ、GGUF、PagedAttention | [mistral.rs 参数模型](concepts/mistral-rs-runtime-parameters.md) |
| KTransformers | CPU/GPU 异构推理、MoE expert offload、kt-kernel、本地大模型 | [KTransformers 参数模型](concepts/ktransformers-runtime-parameters.md) |
| llamafile | 单文件本地 LLM、llama.cpp/ggml、浏览器 UI、轻量服务 | [llamafile 参数模型](concepts/llamafile-runtime-parameters.md) |
| TabbyAPI | ExLlama-family API server、低比特本地 GPU、模型加载/卸载、LoRA | [TabbyAPI 参数模型](concepts/tabbyapi-runtime-parameters.md) |
| KoboldCpp | 本地 GGUF/Web UI/Kobold API、llama.cpp 风格 CPU/GPU offload | [KoboldCpp 参数模型](concepts/koboldcpp-runtime-parameters.md) |

## 核心概念

- [参数分类总览](concepts/inference-parameter-taxonomy.md)
- [跨框架参数对照表](concepts/cross-framework-parameter-map.md)
- [KV cache 与 PagedAttention](concepts/kv-cache-and-paged-attention.md)
- [Continuous batching 与推理调度](concepts/continuous-batching-and-scheduling.md)
- [推理量化](concepts/inference-quantization.md)
- [模型转换、量化与校准流水线](concepts/model-conversion-quantization-pipeline.md)
- [GGUF 转换与 llama.cpp 量化工具链](concepts/gguf-conversion-and-llama-quantize.md)
- [AWQ、GPTQ 与 FP8 量化工具链](concepts/awq-gptq-fp8-quantization-toolchain.md)
- [Speculative decoding](concepts/speculative-decoding.md)
- [采样与结构化输出](concepts/sampling-and-structured-output.md)
- [Logits Processor、惩罚项与长度控制](concepts/logits-processors-penalties-and-length-control.md)
- [推理性能指标与基准测试](concepts/inference-benchmarking-metrics.md)
- [多 GPU 并行推理](concepts/distributed-parallel-inference.md)
- [Attention kernel 与运行时优化](concepts/attention-kernels-and-runtime-optimization.md)
- [长上下文推理](concepts/long-context-inference.md)
- [MoE serving 与 expert parallel](concepts/moe-serving-and-expert-parallel.md)
- [Offload 与内存层级](concepts/offload-and-memory-hierarchy.md)
- [CPU/GPU 混合 Offload 与本地 MoE 推理](concepts/heterogeneous-cpu-gpu-offload-and-local-moe.md)
- [生产服务与运维控制面](concepts/production-serving-operations.md)
- [多模态推理与媒体 token 预算](concepts/multimodal-inference.md)
- [LoRA 与 adapter serving](concepts/lora-and-adapter-serving.md)
- [模型格式、加载与供应链边界](concepts/model-formats-and-loading.md)
- [Tokenizer、chat template 与 token 预算](concepts/tokenizer-and-chat-templates.md)
- [Tool/function calling 推理路径](concepts/tool-calling-inference.md)
- [推理安全与多租户边界](concepts/inference-security-and-multitenancy.md)
- [离线推理与批量推理](concepts/offline-and-batch-inference.md)
- [Embedding、Reranker 与 Encoder 推理](concepts/embedding-and-reranker-inference.md)
- [Disaggregated serving 与 KV transfer](concepts/disaggregated-serving-and-kv-transfer.md)
- [推理容量规划公式](concepts/capacity-planning-formulas.md)
- [推理排障手册](concepts/inference-troubleshooting-runbook.md)
- [LLM 网关与路由层参数](concepts/llm-gateway-routing-parameters.md)
- [GPU 拓扑、隔离与集群资源](concepts/gpu-topology-and-isolation.md)
- [Kubernetes 模型服务部署](concepts/kubernetes-model-serving.md)
- [推理观测、Metrics 与 Tracing](concepts/inference-observability-and-tracing.md)
- [结构化解码库生态](concepts/constrained-decoding-libraries.md)
- [推理负载建模与压测数据集](concepts/workload-modeling-and-load-testing.md)
- [CPU、边缘与 NPU 推理](concepts/cpu-edge-npu-inference.md)
- [WebLLM 参数模型](concepts/webllm-runtime-parameters.md)
- [Transformers.js 参数模型](concepts/transformers-js-runtime-parameters.md)
- [ONNX Runtime Web 参数模型](concepts/onnxruntime-web-parameters.md)
- [图编译与 Engine 构建优化](concepts/graph-compilation-and-engine-build.md)
- [推理缓存层：Response、Semantic、Prompt 与 KV](concepts/inference-caching-layers.md)
- [OpenAI-compatible API 语义与兼容边界](concepts/openai-compatible-api-semantics.md)
- [Autoscaling 与 Admission Control](concepts/autoscaling-and-admission-control.md)
- [推理成本与效率模型](concepts/inference-cost-and-efficiency.md)
- [NVIDIA Dynamo、LMCache 与 NIXL 参数模型](concepts/nvidia-dynamo-lmcache-nixl-parameters.md)
- [Envoy AI Gateway 与 Gateway API Inference Extension](concepts/envoy-ai-gateway-and-inference-extension.md)
- [Reasoning / Thinking Token 预算与 Parser](concepts/reasoning-token-budget-and-parser.md)
- [Tokenization、Validation 与预处理性能](concepts/tokenization-validation-preprocessing.md)
- [模型 Artifact 分发、缓存与冷启动](concepts/model-artifact-distribution-and-cold-start.md)
- [模型生命周期、热切换与保活](concepts/model-lifecycle-hot-swap-and-keepalive.md)
- [请求调度公平性、优先级与队列策略](concepts/request-scheduling-fairness-and-priority.md)
- [Streaming、Backpressure、Timeout 与取消](concepts/streaming-backpressure-timeouts-cancellation.md)
- [Reproducibility、Seed 与推理确定性](concepts/reproducibility-seeds-and-determinism.md)
- [调参决策手册](concepts/inference-tuning-playbook.md)

## 一句话地图

推理性能通常由四个预算共同决定：模型权重显存、KV cache 显存、prefill 计算、decode 调度。大部分参数只是从不同角度在这四个预算之间重新分配空间和时间。
