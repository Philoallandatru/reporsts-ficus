# LLM 推理框架参数知识库

这是一个面向部署和性能调优的 LLM inference wiki，收集主流推理框架的启动参数、运行参数、采样参数和背后的系统原理。

当前覆盖日期：2026-08-20。

## 快速入口

- [知识库首页](wiki/index.md)
- [概念索引](CONCEPT_INDEX.md)
- [参数分类总览](wiki/concepts/inference-parameter-taxonomy.md)
- [跨框架参数对照表](wiki/concepts/cross-framework-parameter-map.md)
- [调参决策手册](wiki/concepts/inference-tuning-playbook.md)
- [来源清单](SOURCES.md)

## 推理机制页

- [KV cache 与 PagedAttention](wiki/concepts/kv-cache-and-paged-attention.md)
- [跨框架参数对照表](wiki/concepts/cross-framework-parameter-map.md)
- [Continuous batching 与推理调度](wiki/concepts/continuous-batching-and-scheduling.md)
- [推理量化：权重、激活与 KV cache](wiki/concepts/inference-quantization.md)
- [模型转换、量化与校准流水线](wiki/concepts/model-conversion-quantization-pipeline.md)
- [GGUF 转换与 llama.cpp 量化工具链](wiki/concepts/gguf-conversion-and-llama-quantize.md)
- [AWQ、GPTQ 与 FP8 量化工具链](wiki/concepts/awq-gptq-fp8-quantization-toolchain.md)
- [Speculative decoding](wiki/concepts/speculative-decoding.md)
- [采样与结构化输出](wiki/concepts/sampling-and-structured-output.md)
- [Logits Processor、惩罚项与长度控制](wiki/concepts/logits-processors-penalties-and-length-control.md)
- [推理性能指标与基准测试](wiki/concepts/inference-benchmarking-metrics.md)
- [多 GPU 并行推理](wiki/concepts/distributed-parallel-inference.md)
- [Attention kernel 与运行时优化](wiki/concepts/attention-kernels-and-runtime-optimization.md)
- [长上下文推理](wiki/concepts/long-context-inference.md)
- [MoE serving 与 expert parallel](wiki/concepts/moe-serving-and-expert-parallel.md)
- [Offload 与内存层级](wiki/concepts/offload-and-memory-hierarchy.md)
- [CPU/GPU 混合 Offload 与本地 MoE 推理](wiki/concepts/heterogeneous-cpu-gpu-offload-and-local-moe.md)
- [生产服务与运维控制面](wiki/concepts/production-serving-operations.md)
- [多模态推理与媒体 token 预算](wiki/concepts/multimodal-inference.md)
- [LoRA 与 adapter serving](wiki/concepts/lora-and-adapter-serving.md)
- [模型格式、加载与供应链边界](wiki/concepts/model-formats-and-loading.md)
- [Tokenizer、chat template 与 token 预算](wiki/concepts/tokenizer-and-chat-templates.md)
- [Tool/function calling 推理路径](wiki/concepts/tool-calling-inference.md)
- [推理安全与多租户边界](wiki/concepts/inference-security-and-multitenancy.md)
- [离线推理与批量推理](wiki/concepts/offline-and-batch-inference.md)
- [Embedding、Reranker 与 Encoder 推理](wiki/concepts/embedding-and-reranker-inference.md)
- [Disaggregated serving 与 KV transfer](wiki/concepts/disaggregated-serving-and-kv-transfer.md)
- [推理容量规划公式](wiki/concepts/capacity-planning-formulas.md)
- [推理排障手册](wiki/concepts/inference-troubleshooting-runbook.md)
- [LLM 网关与路由层参数](wiki/concepts/llm-gateway-routing-parameters.md)
- [GPU 拓扑、隔离与集群资源](wiki/concepts/gpu-topology-and-isolation.md)
- [Kubernetes 模型服务部署](wiki/concepts/kubernetes-model-serving.md)
- [推理观测、Metrics 与 Tracing](wiki/concepts/inference-observability-and-tracing.md)
- [结构化解码库生态](wiki/concepts/constrained-decoding-libraries.md)
- [推理负载建模与压测数据集](wiki/concepts/workload-modeling-and-load-testing.md)
- [CPU、边缘与 NPU 推理](wiki/concepts/cpu-edge-npu-inference.md)
- [WebLLM 参数模型](wiki/concepts/webllm-runtime-parameters.md)
- [Transformers.js 参数模型](wiki/concepts/transformers-js-runtime-parameters.md)
- [ONNX Runtime Web 参数模型](wiki/concepts/onnxruntime-web-parameters.md)
- [图编译与 Engine 构建优化](wiki/concepts/graph-compilation-and-engine-build.md)
- [推理缓存层：Response、Semantic、Prompt 与 KV](wiki/concepts/inference-caching-layers.md)
- [OpenAI-compatible API 语义与兼容边界](wiki/concepts/openai-compatible-api-semantics.md)
- [Autoscaling 与 Admission Control](wiki/concepts/autoscaling-and-admission-control.md)
- [推理成本与效率模型](wiki/concepts/inference-cost-and-efficiency.md)
- [NVIDIA Dynamo、LMCache 与 NIXL 参数模型](wiki/concepts/nvidia-dynamo-lmcache-nixl-parameters.md)
- [Envoy AI Gateway 与 Gateway API Inference Extension](wiki/concepts/envoy-ai-gateway-and-inference-extension.md)
- [Reasoning / Thinking Token 预算与 Parser](wiki/concepts/reasoning-token-budget-and-parser.md)
- [Tokenization、Validation 与预处理性能](wiki/concepts/tokenization-validation-preprocessing.md)
- [模型 Artifact 分发、缓存与冷启动](wiki/concepts/model-artifact-distribution-and-cold-start.md)
- [模型生命周期、热切换与保活](wiki/concepts/model-lifecycle-hot-swap-and-keepalive.md)
- [请求调度公平性、优先级与队列策略](wiki/concepts/request-scheduling-fairness-and-priority.md)
- [Streaming、Backpressure、Timeout 与取消](wiki/concepts/streaming-backpressure-timeouts-cancellation.md)
- [Reproducibility、Seed 与推理确定性](wiki/concepts/reproducibility-seeds-and-determinism.md)

## 框架页

- [llama.cpp 参数模型](wiki/concepts/llama-cpp-runtime-parameters.md)
- [llama-cpp-python 参数模型](wiki/concepts/llama-cpp-python-runtime-parameters.md)
- [vLLM Engine Args 参数模型](wiki/concepts/vllm-engine-parameters.md)
- [SGLang Server Arguments 参数模型](wiki/concepts/sglang-server-parameters.md)
- [Hugging Face TGI Launcher 参数模型](wiki/concepts/tgi-launcher-parameters.md)
- [TensorRT-LLM Serving 参数模型](wiki/concepts/tensorrt-llm-serving-parameters.md)
- [Ollama Modelfile 与服务参数](wiki/concepts/ollama-runtime-parameters.md)
- [LMDeploy Serving 参数模型](wiki/concepts/lmdeploy-serving-parameters.md)
- [DeepSpeed Inference / MII 参数模型](wiki/concepts/deepspeed-inference-mii-parameters.md)
- [OpenVINO GenAI 参数模型](wiki/concepts/openvino-genai-parameters.md)
- [Hugging Face Transformers Generation 参数模型](wiki/concepts/huggingface-transformers-generation-parameters.md)
- [ONNX Runtime GenAI 参数模型](wiki/concepts/onnxruntime-genai-parameters.md)
- [ONNX Runtime Web 参数模型](wiki/concepts/onnxruntime-web-parameters.md)
- [MLC LLM 参数模型](wiki/concepts/mlc-llm-runtime-parameters.md)
- [WebLLM 参数模型](wiki/concepts/webllm-runtime-parameters.md)
- [Transformers.js 参数模型](wiki/concepts/transformers-js-runtime-parameters.md)
- [NVIDIA Triton Inference Server LLM 参数模型](wiki/concepts/triton-inference-server-llm-parameters.md)
- [MLX LM 参数模型](wiki/concepts/mlx-lm-runtime-parameters.md)
- [CTranslate2 参数模型](wiki/concepts/ctranslate2-runtime-parameters.md)
- [ExLlamaV2 参数模型](wiki/concepts/exllamav2-runtime-parameters.md)
- [NVIDIA NIM for LLMs 参数模型](wiki/concepts/nvidia-nim-llm-parameters.md)
- [AWS Neuron / Inferentia 推理参数模型](wiki/concepts/aws-neuron-inference-parameters.md)
- [Google TPU 与 JetStream 推理](wiki/concepts/google-tpu-jetstream-inference.md)
- [Intel IPEX-LLM 与 Optimum Intel 推理](wiki/concepts/intel-ipex-optimum-inference.md)
- [SageMaker / DJL Serving LMI 参数模型](wiki/concepts/sagemaker-djl-lmi-parameters.md)
- [FastChat 与 Sonar/Aphrodite 参数模型](wiki/concepts/fastchat-and-aphrodite-parameters.md)
- [Hugging Face TEI 参数模型](wiki/concepts/huggingface-tei-parameters.md)
- [Ray Serve LLM 参数模型](wiki/concepts/ray-serve-llm-parameters.md)
- [BentoML / OpenLLM 参数模型](wiki/concepts/bentoml-openllm-parameters.md)
- [KServe Generative Inference 参数模型](wiki/concepts/kserve-generative-inference-parameters.md)
- [LocalAI 参数模型](wiki/concepts/localai-runtime-parameters.md)
- [Xinference 参数模型](wiki/concepts/xinference-runtime-parameters.md)
- [mistral.rs 参数模型](wiki/concepts/mistral-rs-runtime-parameters.md)
- [KTransformers 参数模型](wiki/concepts/ktransformers-runtime-parameters.md)
- [llamafile 参数模型](wiki/concepts/llamafile-runtime-parameters.md)
- [TabbyAPI 参数模型](wiki/concepts/tabbyapi-runtime-parameters.md)
- [KoboldCpp 参数模型](wiki/concepts/koboldcpp-runtime-parameters.md)

## 使用方式

把每个框架页当作部署前 checklist：

1. 先读 [参数分类总览](wiki/concepts/inference-parameter-taxonomy.md)，理解模型加载、KV cache、并发调度、采样、量化、并行和服务边界。
2. 再读机制页，理解 KV cache、batching、跨框架参数映射、队列公平性、streaming/取消、量化、转换/校准、speculation、确定性、reasoning token、采样/logits processor、结构化输出、OpenAI-compatible API、tokenization/validation、并行、batch/offline、embedding/rerank、容量规划、GPU/Kubernetes 部署、端侧/WebGPU、autoscaling、分布式 KV-aware serving、冷启动、观测、成本和 benchmark 指标。
3. 再进入具体框架页，把参数名映射到该框架的实际 CLI、配置文件或 API 字段。
4. 最后按 [调参决策手册](wiki/concepts/inference-tuning-playbook.md) 根据目标选择方向：降低延迟、提高吞吐、扩大上下文、压缩显存或控制输出质量。

## 维护约定

- 优先引用官方文档、官方源码 README、官方 API 文档。
- 参数名只记录部署中最常用和最容易误调的集合；完整列表以官方 help/API 文档为准。
- 每页末尾保留“关键来源”，便于后续刷新。
