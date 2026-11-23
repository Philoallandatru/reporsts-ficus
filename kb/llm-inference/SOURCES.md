# 来源清单

资料核对日期：2026-08-20。

## 官方来源

| 框架 | 来源 | 用途 |
|---|---|---|
| llama.cpp | https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md | `llama-server` 的 common、sampling、server-specific 参数，含上下文、KV cache、GPU offload、continuous batching、API 服务参数 |
| llama.cpp | https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md | 后端构建与 CPU/GPU/Metal/SYCL/HIP/Vulkan/OpenVINO 等平台支持 |
| llama.cpp | https://github.com/ggml-org/llama.cpp/blob/master/convert_hf_to_gguf.py | Hugging Face checkpoint 转 GGUF 的转换脚本参数 |
| llama.cpp | https://github.com/ggml-org/llama.cpp/blob/master/tools/imatrix/README.md | `llama-imatrix` importance matrix 生成和参数 |
| llama.cpp | https://github.com/ggml-org/llama.cpp/blob/master/tools/cli/README.md | llama.cpp CLI、load mode、mmap/mlock/Direct I/O 等加载参数 |
| GGUF | https://github.com/ggml-org/ggml/blob/master/docs/gguf.md | GGUF 格式规范、metadata 和 tensor descriptors |
| llama-cpp-python | https://llama-cpp-python.readthedocs.io/en/latest/ | llama.cpp Python binding 官方文档 |
| llama-cpp-python | https://llama-cpp-python.readthedocs.io/en/latest/server/ | OpenAI-compatible server、server settings、config file、多模型路由 |
| llama-cpp-python | https://llama-cpp-python.readthedocs.io/en/latest/api-reference/ | `Llama(...)` 构造参数、context、batch、GPU offload、embedding、chat_format |
| llama-cpp-python | https://github.com/abetlen/llama-cpp-python | 官方仓库 |
| llama-cpp-python | https://github.com/abetlen/llama-cpp-python/blob/master/llama_cpp/llama.py | `Llama(...)` 构造参数源码 |
| llama-cpp-python | https://github.com/abetlen/llama-cpp-python/blob/main/llama_cpp/server/settings.py | server/model settings 源码 |
| vLLM | https://docs.vllm.ai/en/stable/configuration/engine_args/ | `vllm serve` / EngineArgs 的模型、并行、KV cache、prefix caching、offload、LoRA、调度等参数 |
| vLLM LLM Compressor | https://docs.vllm.ai/projects/llm-compressor/en/latest/ | vLLM 生态压缩/量化工具链入口 |
| vLLM LLM Compressor | https://docs.vllm.ai/projects/llm-compressor/en/latest/guides/compression_schemes/ | FP8、NVFP4、AWQ、GPTQ 等 compression schemes |
| vLLM LLM Compressor | https://docs.vllm.ai/projects/llm-compressor/en/0.8.1/examples/quantization_w8a8_fp8/ | FP8 W8A8 example |
| vLLM LLM Compressor | https://docs.vllm.ai/projects/llm-compressor/en/0.8.0/examples/quantization_w8a8_int8/ | INT8 W8A8 / SmoothQuant example |
| vLLM LLM Compressor | https://github.com/vllm-project/llm-compressor | LLM Compressor 官方仓库 |
| vLLM | https://docs.vllm.ai/en/latest/features/quantization/gptqmodel/ | GPTQModel quantization 支持 |
| vLLM | https://docs.vllm.ai/en/latest/configuration/engine_args.html | latest EngineArgs，含 renderer/preprocessing、model loading 相关字段 |
| vLLM | https://docs.vllm.ai/en/stable/design/paged_attention/ | PagedAttention / KV cache block 设计背景 |
| vLLM | https://docs.vllm.ai/en/stable/features/automatic_prefix_caching/ | Prefix caching 的启用、哈希与复用模型 |
| vLLM | https://docs.vllm.ai/en/stable/features/spec_decode/ | Speculative decoding 参数与限制 |
| vLLM | https://docs.vllm.ai/en/stable/features/quantization/ | vLLM 支持的量化方法与适用范围 |
| vLLM | https://docs.vllm.ai/en/stable/features/structured_outputs.html | guided decoding / structured outputs |
| vLLM | https://docs.vllm.ai/en/stable/features/reasoning_outputs.html | reasoning outputs、reasoning parser |
| vLLM | https://docs.vllm.ai/en/stable/features/multimodal_inputs/ | multimodal inputs、image/video/audio 预算与限制 |
| vLLM | https://docs.vllm.ai/en/stable/features/lora.html | LoRA serving、adapter 参数与 runtime loading |
| vLLM | https://docs.vllm.ai/en/v0.25.1/features/tool_calling/ | OpenAI-compatible tool calling 与 parser |
| vLLM | https://docs.vllm.ai/en/stable/cli/serve/ | serve CLI，含 multimodal、LoRA、安全、CORS、媒体域名等参数 |
| vLLM | https://docs.vllm.ai/en/stable/serving/online_serving/ | OpenAI-compatible online serving endpoint |
| vLLM | https://docs.vllm.ai/en/stable/contributing/benchmarks.html | vLLM benchmark 工具、serving benchmark 和指标口径 |
| vLLM | https://docs.vllm.ai/en/stable/benchmarking/cli/ | benchmark CLI，含 throughput / latency / serve 等测试入口 |
| vLLM | https://docs.vllm.ai/en/stable/cli/bench/throughput/ | 离线 engine throughput benchmark 参数 |
| vLLM | https://docs.vllm.ai/en/stable/examples/basic/offline_inference/ | offline inference 基础示例 |
| vLLM | https://docs.vllm.ai/en/stable/examples/features/openai_batch/ | OpenAI Batch JSONL 文件格式离线推理示例 |
| vLLM | https://docs.vllm.ai/en/stable/examples/pooling/embed/ | embedding / pooling task 示例 |
| vLLM | https://docs.vllm.ai/en/stable/examples/pooling/score/ | score / rerank 类 pooling task 示例 |
| vLLM | https://docs.vllm.ai/en/stable/models/pooling_models/ | pooling models、embed/score/reward/classification task 支持 |
| vLLM | https://docs.vllm.ai/en/stable/configuration/optimization/ | chunked prefill、prefix caching 等优化开关 |
| vLLM | https://docs.vllm.ai/en/stable/features/disagg_prefill.html | experimental disaggregated prefilling |
| vLLM | https://docs.vllm.ai/en/stable/features/disagg_prefill/ | experimental disaggregated prefilling、KV transfer 示例入口 |
| vLLM | https://docs.vllm.ai/en/stable/features/nixl_connector_usage/ | NixlConnector usage guide |
| vLLM | https://docs.vllm.ai/en/stable/features/nixl_connector_compatibility/ | NixlConnector compatibility matrix |
| vLLM | https://docs.vllm.ai/en/stable/deployment/integrations/dynamo/ | NVIDIA Dynamo integration |
| vLLM | https://docs.vllm.ai/en/stable/usage/troubleshooting/ | vLLM troubleshooting 入口 |
| vLLM | https://docs.vllm.ai/en/stable/features/ | attention backend、quantization、platform support 等兼容性矩阵 |
| vLLM | https://docs.vllm.ai/en/stable/features/automatic_prefix_caching.html | prefix caching、KV block hash 与缓存复用 |
| vLLM | https://docs.vllm.ai/en/stable/api/vllm/config/ | KV cache offload 配置字段 |
| vLLM | https://docs.vllm.ai/en/stable/design/metrics/ | production metrics 与监控字段 |
| vLLM | https://docs.vllm.ai/en/stable/design/cuda_graphs/ | CUDA Graph 捕获/回放设计 |
| vLLM | https://docs.vllm.ai/en/latest/design/attention_backends/ | attention backend 选择与互斥配置 |
| vLLM | https://docs.vllm.ai/en/latest/design/torch_compile/ | `torch.compile` 与 CUDA Graph capture sizes |
| vLLM | https://docs.vllm.ai/en/latest/features/context_extension/ | context extension 与 `hf-overrides` 配置 |
| vLLM | https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/ | expert parallel、EPLB、DeepEP backend 与 disaggregated serving |
| SGLang | https://docs.sglang.io/docs/advanced_features/server_arguments | `sglang.launch_server` / `sglang serve` 的服务参数、量化、并行、KV cache、LoRA、speculative decoding 等 |
| SGLang | https://docs.sglang.io/docs/advanced_features/hyperparameter_tuning | `--mem-fraction-static`、`--chunked-prefill-size`、`--max-running-requests`、CUDA graph 等调优建议 |
| SGLang | https://docs.sglang.io/docs/advanced_features/pd_disaggregation | prefill/decode disaggregation 架构 |
| SGLang | https://docs.sglang.io/docs/advanced_features/structured_outputs | structured outputs / constrained decoding |
| SGLang | https://docs.sglang.io/docs/advanced_features/expert_parallelism | expert parallelism 与 DeepEP 相关优化入口 |
| SGLang | https://docs.sglang.io/docs/advanced_features/hicache | hierarchical KV caching / HiCache |
| SGLang | https://docs.sglang.io/docs/basic_usage/openai_api_vision.md | OpenAI-compatible vision API |
| SGLang | https://docs.sglang.io/docs/advanced_features/vlm_query.md | VLM query 与多模态输入 |
| SGLang | https://docs.sglang.io/docs/advanced_features/lora.md | LoRA serving |
| SGLang | https://docs.sglang.io/docs/advanced_features/tool_parser.md | tool parser / function calling |
| SGLang | https://docs.sglang.io/docs/references/custom_chat_template.md | custom chat template |
| SGLang | https://docs.sglang.io/docs/basic_usage/sampling_params.md | sampling params 和请求参数 |
| SGLang | https://docs.sglang.io/docs/advanced_features/deterministic_inference | deterministic inference、batch-invariant 支持矩阵 |
| SGLang | https://sgl-project.github.io/advanced_features/separate_reasoning.html | separate reasoning content |
| Hugging Face TGI | https://huggingface.co/docs/text-generation-inference/reference/launcher | `text-generation-launcher` 参数，包括 sharding、quantize、KV cache dtype、batch token budget、服务端限流等 |
| Hugging Face TGI | https://huggingface.co/docs/text-generation-inference/conceptual/paged_attention | PagedAttention 概念 |
| Hugging Face TGI | https://huggingface.co/docs/text-generation-inference/conceptual/tensor_parallelism | Tensor parallelism 概念 |
| Hugging Face TGI | https://huggingface.co/docs/text-generation-inference/conceptual/speculation | Speculation / Medusa / n-gram 概念 |
| Hugging Face TGI | https://huggingface.co/docs/text-generation-inference/en/messages_api | OpenAI-compatible Messages API |
| Hugging Face TGI | https://huggingface.co/docs/text-generation-inference/en/supported_models | 支持模型/VLM 列表 |
| Hugging Face TGI | https://huggingface.co/docs/text-generation-inference/en/basic_tutorials/preparing_model | safetensors 与模型准备 |
| Hugging Face TGI | https://huggingface.co/docs/text-generation-inference/en/basic_tutorials/safety | `trust_remote_code` 与 pickle 安全说明 |
| Hugging Face TEI | https://huggingface.co/docs/text-embeddings-inference/en/index | Text Embeddings Inference 总览、embedding/rerank 服务 |
| Hugging Face TEI | https://huggingface.co/docs/text-embeddings-inference/en/cli_arguments | TEI launcher 参数，含 pooling、batch tokens、并发和 dtype |
| Hugging Face TEI | https://github.com/huggingface/text-embeddings-inference#using-re-rankers-models | TEI reranker / sequence-classification serving 示例 |
| Hugging Face TEI | https://github.com/huggingface/text-embeddings-inference | TEI 官方仓库、容器和 API 示例 |
| Hugging Face TEI | https://huggingface.co/docs/text-embeddings-inference/en/supported_models | TEI 支持模型、硬件和 backend |
| Hugging Face TEI | https://github.com/huggingface/text-embeddings-inference/blob/main/router/src/main.rs | TEI router CLI 参数源码入口 |
| Hugging Face TEI | https://github.com/huggingface/text-embeddings-inference/blob/main/backends/src/dtype.rs | TEI dtype 枚举源码 |
| Hugging Face Tokenizers | https://huggingface.co/docs/tokenizers/index | fast tokenizer 与 tokenization pipeline |
| Hugging Face Transformers | https://huggingface.co/docs/transformers/en/fast_tokenizers | fast tokenizer、Rust backend、padding/truncation |
| Hugging Face Transformers | https://huggingface.co/docs/transformers/en/quantization/awq | AWQ loading、`quantization_config`、fused modules、ExLlamaV2 backend |
| Hugging Face Transformers | https://huggingface.co/docs/transformers/en/quantization/gptq | GPTQModel、`GPTQConfig`、dataset、Marlin backend、AutoGPTQ 状态 |
| Hugging Face Transformers | https://huggingface.co/docs/transformers/en/quantization/quanto | Optimum Quanto、`QuantoConfig`、weight quantization |
| Hugging Face Transformers | https://huggingface.co/docs/transformers/en/main_classes/quantization | `GPTQConfig`、`AwqConfig` 等量化配置 API |
| Hugging Face Optimum | https://github.com/huggingface/optimum/blob/main/docs/source/llm_quantization/usage_guides/quantization.mdx | Optimum GPTQ / GPTQModel 使用说明 |
| Hugging Face Quanto | https://huggingface.co/blog/quanto-introduction | Quanto 设计与量化说明 |
| Hugging Face Quanto | https://github.com/huggingface/optimum-quanto | Optimum Quanto 官方仓库 |
| TensorRT-LLM | https://nvidia.github.io/TensorRT-LLM/commands/trtllm-serve/trtllm-serve.html | `trtllm-serve` 参数、OpenAI-compatible endpoints、YAML 配置、parallelism、KV cache、batch size |
| TensorRT-LLM | https://nvidia.github.io/TensorRT-LLM/features/paged-attention-ifb-scheduler.html | Paged attention、in-flight batching、request scheduling |
| TensorRT-LLM | https://nvidia.github.io/TensorRT-LLM/features/kvcache.html | KV cache 系统与 reuse |
| TensorRT-LLM | https://nvidia.github.io/TensorRT-LLM/features/quantization.html | TensorRT-LLM 权重、激活与 KV cache 量化 |
| TensorRT-LLM | https://nvidia.github.io/TensorRT-LLM/latest/features/quantization.html | latest TensorRT-LLM quantization 功能和支持矩阵 |
| TensorRT-LLM | https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/blogs/quantization-in-TRT-LLM.md | TensorRT-LLM quantization 背景说明 |
| TensorRT-LLM | https://nvidia.github.io/TensorRT-LLM/performance/performance-tuning-guide/fp8-quantization.html | FP8 quantization 性能调优 |
| TensorRT-LLM | https://github.com/NVIDIA/TensorRT-LLM/blob/main/examples/quantization/README.md | TensorRT-LLM quantization examples |
| TensorRT-LLM | https://nvidia.github.io/TensorRT-LLM/features/lora.html | LoRA support |
| TensorRT-LLM | https://nvidia.github.io/TensorRT-LLM/advanced/speculative-decoding.html | Medusa、EAGLE、NGram、Lookahead 等 speculative decoding |
| TensorRT-LLM | https://nvidia.github.io/TensorRT-LLM/features/long-sequence.html | long sequence、chunked context、context FMHA 等 |
| TensorRT-LLM | https://nvidia.github.io/TensorRT-LLM/advanced/expert-parallelism.html | MoE expert parallelism |
| TensorRT-LLM | https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html | KV cache reuse 与 eviction |
| TensorRT-LLM | https://nvidia.github.io/TensorRT-LLM/features/disagg-serving.html | disaggregated serving 与 KV cache transfer |
| TensorRT-LLM | https://nvidia.github.io/TensorRT-LLM/features/parallel-strategy.html | TP/PP/CP/EP 等并行策略 |
| TensorRT-LLM | https://nvidia.github.io/TensorRT-LLM/features/kvcache.html | KV cache block pool、host offload、prioritized eviction |
| TensorRT-LLM | https://nvidia.github.io/TensorRT-LLM/developer-guide/telemetry.html | telemetry manifest、metrics buckets、CUDA graph / MoE 配置项 |
| NVIDIA GenAI-Perf | https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html | LLM serving benchmark 指标与负载生成 |
| NVIDIA NIM | https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html | LLM benchmark 指标定义 |
| llama.cpp | https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md | GGUF 权重量化工具与量化误差说明 |
| Hugging Face Hub | https://huggingface.co/docs/hub/en/gguf | GGUF 文件格式和 Hugging Face Hub 支持说明 |
| AutoAWQ | https://casper-hansen.github.io/AutoAWQ/ | AutoAWQ 官方文档 |
| AutoAWQ | https://github.com/casper-hansen/AutoAWQ | AutoAWQ 官方仓库 |
| AutoAWQ | https://api.github.com/repos/casper-hansen/AutoAWQ | AutoAWQ 仓库归档状态核对 |
| AutoGPTQ | https://github.com/AutoGPTQ/AutoGPTQ/blob/main/README.md | AutoGPTQ README，含 unmaintained 状态说明 |
| AutoGPTQ | https://api.github.com/repos/AutoGPTQ/AutoGPTQ | AutoGPTQ 仓库归档状态核对 |
| GPTQModel | https://github.com/ModelCloud/GPTQModel | GPTQModel 官方仓库 |
| llama.cpp | https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md | GBNF grammar、JSON schema 到 grammar 的结构化输出说明 |
| llama.cpp | https://github.com/ggml-org/llama.cpp/blob/master/docs/multimodal.md | `mmproj`、OpenAI-compatible 多模态 server |
| llama.cpp | https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md | function calling、chat template、tool call handler |
| llama.cpp | https://github.com/ggml-org/llama.cpp/blob/master/docs/models.md | GGUF 模型和 LoRA 转换 |
| Ollama | https://docs.ollama.com/modelfile | `Modelfile` 指令、`PARAMETER`、采样、上下文、adapter、template |
| Ollama | https://docs.ollama.com/faq | `OLLAMA_CONTEXT_LENGTH`、`ollama ps`、服务环境变量 |
| Ollama | https://github.com/ollama/ollama/blob/main/docs/api.md | API options、structured outputs、vision inputs |
| Ollama | https://docs.ollama.com/capabilities/structured-outputs | JSON / JSON schema structured outputs |
| Xinference | https://inference.readthedocs.io/en/latest/ | Xinference 官方文档入口 |
| Xinference | https://inference.readthedocs.io/en/latest/getting_started/using_xinference.html | 单机、supervisor/worker 集群、API 和模型缓存入口 |
| Xinference | https://inference.readthedocs.io/en/latest/user_guide/launch.html | model launching、replica、replica_config、GPU 放置、batching 和 thinking mode |
| Xinference | https://inference.readthedocs.io/en/latest/user_guide/backends.html | backend 选择、vLLM/SGLang/llama.cpp/transformers 相关说明 |
| Xinference | https://inference.readthedocs.io/en/latest/user_guide/client_api.html | Python client API |
| Xinference | https://inference.readthedocs.io/en/latest/models/custom.html | custom model registration |
| Xinference | https://inference.readthedocs.io/en/latest/models/model_abilities/rerank.html | rerank 模型能力和 API |
| Xinference | https://github.com/xorbitsai/inference | 官方仓库 |
| Xinference | https://github.com/xorbitsai/inference/blob/main/xinference/client/restful/restful_client.py | REST client、OpenAI-compatible endpoint 映射源码 |
| LMDeploy | https://lmdeploy.readthedocs.io/en/latest/llm/api_server.html | OpenAI-compatible API server、`--tp`、`--session-len`、`--cache-max-entry-count` |
| LMDeploy | https://lmdeploy.readthedocs.io/en/v0.6.0/api/pipeline.html | `TurbomindEngineConfig` / `PytorchEngineConfig` 参数含 `session_len`、`cache_max_entry_count`、`block_size`、`enable_prefix_caching` |
| LMDeploy | https://lmdeploy.readthedocs.io/en/latest/inference/turbomind_config.html | TurboMind 权重量化、KV cache、continuous batching、blocked KV cache 等配置背景 |
| DeepSpeed | https://deepspeed.readthedocs.io/en/latest/inference-init.html | `DeepSpeedInferenceConfig`、kernel injection、tensor parallel、CUDA Graph、Triton、ZeRO、MoQ |
| DeepSpeed-MII | https://deepspeed-mii.readthedocs.io/en/rtd-staging/config.html | MII deployment config、replica、device map、tensor parallel、quantization mode |
| OpenVINO GenAI | https://docs.openvino.ai/2025/openvino-workflow-generative/inference-with-genai.html | `LLMPipeline`、`GenerationConfig`、streaming、beam search、speculative decoding、GGUF preview |
| OpenVINO GenAI | https://docs.openvino.ai/2025/api/genai_api/_autosummary/openvino_genai.SchedulerConfig.html | continuous batching、KV block/cache、prefix caching、dynamic split fuse 等 SchedulerConfig 字段 |
| OpenVINO Model Server | https://docs.openvino.ai/2025/model-server/ovms_demos_embeddings.html | OpenAI-compatible embeddings demo |
| OpenVINO Model Server | https://docs.openvino.ai/2025/model-server/ovms_demos_rerank.html | Cohere-compatible rerank demo |
| OpenVINO Model Server | https://docs.openvino.ai/2025/model-server/ovms_docs_genai.html | GenAI endpoints、embedding 与 rerank API 入口 |
| Ray Data | https://docs.ray.io/en/latest/data/batch_inference.html | batch inference 数据流水线 |
| Ray Data | https://docs.ray.io/en/latest/data/working-with-llms.html | Ray Data LLM APIs 与 vLLM/SGLang 批量处理 |
| Ray Data | https://docs.ray.io/en/latest/data/api/doc/ray.data.llm.vLLMEngineProcessorConfig.html | vLLMEngineProcessorConfig 的 batch、concurrency、engine kwargs |
| Ray Serve | https://docs.ray.io/en/latest/serve/llm/index.html | Ray Serve LLM 在线服务、OpenAI-compatible API、autoscaling |
| Ray Serve | https://docs.ray.io/en/latest/serve/llm/user-guides/configuration.html | Ray Serve LLM `LLMConfig`、model loading、engine kwargs、deployment config |
| Ray Serve | https://docs.ray.io/en/latest/serve/api/doc/ray.serve.llm.LLMConfig.html | `LLMConfig` API reference |
| Ray Serve | https://docs.ray.io/en/latest/serve/llm/user-guides/vllm-compatibility.html | Ray Serve LLM 与 vLLM engine 参数兼容性 |
| Ray Serve | https://docs.ray.io/en/latest/serve/llm/user-guides/prefix-aware-routing.html | Ray Serve LLM prefix-aware routing |
| Ray Serve | https://docs.ray.io/en/latest/serve/api/doc/ray.serve.deployment_decorator.html | deployment decorator 参数，含 `max_ongoing_requests`、`max_queued_requests` 等请求并发与队列控制 |
| Ray Serve | https://docs.ray.io/en/latest/serve/configure-serve-deployment.html | Serve deployment config、队列背压、request 并发控制 |
| Ray Serve | https://docs.ray.io/en/latest/serve/llm/user-guides/direct-streaming.html | LLM direct streaming |
| Ray Serve | https://github.com/ray-project/ray/blob/master/python/ray/llm/_internal/serve/core/configs/llm_config.py | Ray Serve LLM config 源码 |
| Sentence Transformers | https://www.sbert.net/docs/package_reference/sentence_transformer/model.html | `SentenceTransformer.encode`、batch、precision、normalize、backend |
| LMCache | https://docs.lmcache.ai/ | LMCache KV cache management 总览 |
| LMCache | https://docs.lmcache.ai/api_reference/configurations.html | LMCache 配置入口和存储参数 |
| LMCache | https://docs.lmcache.ai/api_reference/dynamic_connector.html | LMCache dynamic connector API |
| LMCache | https://docs.lmcache.ai/kv_cache/cpu_ram.html | CPU RAM backend 与 KV cache 层级 |
| LMCache | https://docs.lmcache.ai/getting_started/quickstart/disaggregated_prefill.html | LMCache disaggregated prefill quickstart |
| LMCache | https://docs.lmcache.ai/mp/configuration.html | LMCache MP sidecar/server 配置 |
| NVIDIA Dynamo | https://developer.nvidia.com/dynamo | Dynamo 分布式推理框架、KV-aware routing、NIXL 和多层 KV cache |
| NVIDIA Dynamo | https://docs.nvidia.com/dynamo/latest/ | Dynamo 官方文档入口 |
| NVIDIA Dynamo | https://docs.nvidia.com/dynamo/dev/cli/kv-aware-routing/overview | KV-aware routing 参数与适用场景 |
| NVIDIA Dynamo | https://docs.nvidia.com/dynamo/dev/cli/disaggregated-serving/overview | prefill/decode disaggregated serving |
| NVIDIA Dynamo | https://docs.nvidia.com/dynamo/dev/cli/kv-cache-offloading/overview | 本地 KV cache offloading |
| NVIDIA Dynamo | https://docs.nvidia.com/dynamo/v1.3.0/integrations/kv-cache-integrations/lm-cache | Dynamo 与 LMCache integration |
| NVIDIA Dynamo | https://github.com/ai-dynamo/dynamo | Dynamo 开源仓库和能力矩阵 |
| NIXL | https://github.com/ai-dynamo/nixl | NIXL 低延迟推理数据传输库 |
| NIXL | https://github.com/ai-dynamo/nixl/blob/main/docs/nixl.md | NIXL 文档 |
| OpenAI | https://developers.openai.com/api/docs/guides/batch | OpenAI Batch API |
| Hugging Face Transformers | https://huggingface.co/docs/transformers/en/main_classes/text_generation | `GenerationConfig`、`generate()` 采样/搜索/缓存参数 |
| Hugging Face Transformers | https://huggingface.co/docs/transformers/en/internal/generation_utils | generation utilities、streamer、logits processor/warper 等生成内部机制 |
| Hugging Face Transformers | https://huggingface.co/docs/transformers/en/internal/trainer_utils#transformers.set_seed | `set_seed` 与 deterministic 参数 |
| Hugging Face Transformers | https://huggingface.co/docs/transformers/en/generation_strategies | decoding strategies、beam/sample/assisted generation |
| Hugging Face Transformers | https://huggingface.co/docs/transformers/en/llm_tutorial | LLM 推理基础、chat template、streaming |
| Hugging Face Transformers | https://huggingface.co/docs/transformers/en/main_classes/model | 模型加载、`device_map`、`torch_dtype`、offload 相关参数 |
| Hugging Face Transformers | https://huggingface.co/docs/transformers/en/main_classes/quantization | `QuantizationConfig` API |
| Hugging Face Transformers | https://huggingface.co/docs/transformers/en/quantization/bitsandbytes | bitsandbytes 8-bit/4-bit 量化参数 |
| Hugging Face Transformers | https://huggingface.co/docs/transformers/assisted_decoding | assisted decoding / speculative-style decoding |
| Hugging Face Accelerate | https://huggingface.co/docs/accelerate/usage_guides/big_modeling | Big Model Inference、device map、CPU/disk offload |
| Hugging Face Accelerate | https://huggingface.co/docs/accelerate/en/package_reference/big_modeling | `load_checkpoint_and_dispatch`、`infer_auto_device_map` 等大模型工具 |
| ONNX Runtime GenAI | https://onnxruntime.ai/docs/genai/ | ONNX Runtime GenAI 总览 |
| ONNX Runtime GenAI | https://onnxruntime.ai/docs/genai/api/python.html | Python API、Config、Model、GeneratorParams、Generator、Adapters |
| ONNX Runtime GenAI | https://onnxruntime.ai/docs/genai/api/cpp.html | C++ API |
| ONNX Runtime GenAI | https://onnxruntime.ai/docs/genai/reference/config.html | `genai_config.json` 与 search options 配置 |
| ONNX Runtime GenAI | https://github.com/microsoft/onnxruntime-genai | 官方源码与示例 |
| ONNX Runtime GenAI | https://github.com/microsoft/onnxruntime-genai/blob/main/src/python/py/models/README.md | model builder、模型转换和量化 |
| ONNX Runtime GenAI | https://onnxruntime.ai/docs/genai/howto/build-model.html | 使用 Model Builder 构建模型 |
| ONNX Runtime | https://onnxruntime.ai/docs/execution-providers/ | Execution Provider 列表与硬件后端 |
| ONNX Runtime | https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html | ONNX Runtime 量化 |
| ONNX Runtime Web | https://onnxruntime.ai/docs/tutorials/web/ | ONNX Runtime Web tutorial、浏览器推理流程 |
| ONNX Runtime Web | https://onnxruntime.ai/docs/get-started/with-javascript/web.html | JavaScript Web package、WebGPU/WebNN import、支持矩阵 |
| ONNX Runtime Web | https://onnxruntime.ai/docs/tutorials/web/ep-webgpu.html | WebGPU Execution Provider、Graph Capture、GPU tensor / IO binding |
| ONNX Runtime Web | https://onnxruntime.ai/docs/tutorials/web/ep-webnn.html | WebNN Execution Provider、deviceType、powerPreference、MLTensor |
| ONNX Runtime Web | https://github.com/microsoft/onnxruntime | ONNX Runtime 官方仓库 |
| MLC LLM | https://llm.mlc.ai/docs/get_started/introduction | MLC LLM 总览、跨平台部署目标 |
| MLC LLM | https://llm.mlc.ai/docs/get_started/quick_start | quick start、serve/chat 示例 |
| MLC LLM | https://llm.mlc.ai/docs/deploy/rest.html | REST server 与 OpenAI-compatible API |
| MLC LLM | https://llm.mlc.ai/docs/deploy/cli.html | `mlc_llm chat` / `serve` CLI |
| MLC LLM | https://llm.mlc.ai/docs/deploy/python_engine.html | `MLCEngine` / `AsyncMLCEngine` |
| MLC LLM | https://llm.mlc.ai/docs/compilation/compile_models.html | 模型编译和 model lib |
| MLC LLM | https://llm.mlc.ai/docs/compilation/configure_quantization.html | 量化配置 |
| MLC LLM | https://llm.mlc.ai/docs/compilation/convert_weights.html | 权重转换 |
| MLC LLM | https://llm.mlc.ai/docs/deploy/mlc_chat_config.html | `mlc-chat-config.json` 配置 |
| WebLLM | https://webllm.mlc.ai/docs/ | WebLLM 官方文档入口 |
| WebLLM | https://webllm.mlc.ai/docs/user/get_started.html | WebLLM getting started、WebGPU 要求 |
| WebLLM | https://webllm.mlc.ai/docs/user/api_reference.html | `MLCEngine`、`CreateMLCEngine`、`appConfig`、chat config 和请求参数 |
| WebLLM | https://github.com/mlc-ai/web-llm | WebLLM 官方仓库、OpenAI compatibility、cache backend、worker 支持 |
| Transformers.js | https://huggingface.co/docs/transformers.js/index | Transformers.js 官方文档、pipeline、WebGPU、dtype 总览 |
| Transformers.js | https://huggingface.co/docs/transformers.js/api/pipelines | pipeline API、task/model/options |
| Transformers.js | https://huggingface.co/docs/transformers.js/guides/webgpu | WebGPU guide、`device: "webgpu"` |
| Transformers.js | https://huggingface.co/docs/transformers.js/guides/dtypes | dtype / quantized model guide |
| Transformers.js | https://github.com/huggingface/transformers.js | Transformers.js 官方仓库 |
| Triton Inference Server | https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/model_configuration.html | `config.pbtxt`、model configuration |
| Triton Inference Server | https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/batcher.html | dynamic / sequence batcher |
| Triton Inference Server | https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/tutorials/Conceptual_Guide/Part_2-improving_resource_utilization/README.html | dynamic batching 概念 |
| Triton TensorRT-LLM Backend | https://github.com/triton-inference-server/tensorrtllm_backend | TensorRT-LLM backend 官方仓库 |
| Triton TensorRT-LLM Backend | https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/tensorrtllm_backend/docs/model_config.html | TensorRT-LLM backend model config |
| Triton vLLM Backend | https://github.com/triton-inference-server/vllm_backend | vLLM backend 官方仓库 |
| Triton Python Backend | https://github.com/triton-inference-server/python_backend | Python backend、decoupled mode、custom logic |
| Triton vLLM Backend | https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/tutorials/Quick_Deploy/vLLM/README.html | Triton 部署 vLLM model |
| Triton Inference Server | https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/client_guide/openai_readme.html | Triton OpenAI-compatible frontend |
| Triton Inference Server | https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/docs/cli.html | Perf Analyzer CLI |
| Triton Inference Server | https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/model_analyzer.html | Model Analyzer |
| LiteLLM | https://docs.litellm.ai/docs/ | LiteLLM docs 总览 |
| LiteLLM | https://docs.litellm.ai/docs/proxy/configs | LiteLLM proxy config overview |
| LiteLLM | https://docs.litellm.ai/docs/providers/openai_compatible | OpenAI-compatible provider 接入 |
| LiteLLM | https://docs.litellm.ai/docs/routing | Router load balancing |
| LiteLLM | https://docs.litellm.ai/docs/proxy/load_balancing | Proxy load balancing |
| LiteLLM | https://docs.litellm.ai/docs/proxy/reliability | fallbacks / reliability |
| LiteLLM | https://docs.litellm.ai/docs/proxy/virtual_keys | virtual keys |
| LiteLLM | https://docs.litellm.ai/docs/proxy/users | users、budgets、rate limits |
| LiteLLM | https://docs.litellm.ai/docs/proxy/architecture | proxy request architecture |
| LiteLLM | https://docs.litellm.ai/docs/proxy/config_settings | proxy config settings |
| NVIDIA MIG | https://docs.nvidia.com/datacenter/tesla/mig-user-guide/ | MIG GPU partitioning 与隔离 |
| NVIDIA MIG | https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/introduction.html | MIG GPU instance / compute instance 背景 |
| NVIDIA MPS | https://docs.nvidia.com/deploy/mps/ | CUDA Multi-Process Service |
| NVIDIA MPS | https://docs.nvidia.com/deploy/mps/when-to-use-mps.html | MPS 适用场景 |
| NVIDIA NCCL | https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/overview.html | NCCL collectives / topology-aware communication |
| NVIDIA NCCL | https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html | NCCL 环境变量和通信调试 |
| NVIDIA CUDA | https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/environment-variables.html | CUDA environment variables、`CUDA_VISIBLE_DEVICES` |
| NVIDIA Kubernetes Device Plugin | https://github.com/NVIDIA/k8s-device-plugin | Kubernetes GPU resource 暴露、MIG strategy、device list strategy |
| NVIDIA GPU Operator | https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/ | Kubernetes driver、container toolkit、device plugin、DCGM exporter 管理 |
| NVIDIA DCGM | https://github.com/NVIDIA/dcgm-exporter | DCGM exporter / GPU Prometheus metrics |
| NVIDIA Kubernetes | https://docs.nvidia.com/datacenter/cloud-native/kubernetes/latest/index.html | MIG in Kubernetes / GPU resources |
| NVIDIA DCGM | https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html | DCGM 功能总览 |
| NVIDIA DCGM | https://docs.nvidia.com/datacenter/dcgm/latest/index.html | DCGM 文档入口 |
| NVIDIA DCGM | https://docs.nvidia.com/datacenter/dcgm/latest/installation/install-dcgm-exporter.html | DCGM exporter 安装 |
| KServe | https://kserve.github.io/website/docs/model-serving/generative-inference/overview | Generative Inference runtime overview |
| KServe | https://kserve.github.io/website/docs/model-serving/generative-inference/tasks/text-generation | Hugging Face/vLLM text generation runtime 参数和示例 |
| KServe | https://kserve.github.io/website/docs/model-serving/storage/providers/hf | Hugging Face storage provider、HF token、model storage |
| KServe | https://kserve.github.io/website/docs/model-serving/storage/overview | storage initializer、model storage overview |
| KServe | https://kserve.github.io/website/docs/model-serving/storage/providers/pvc | PVC model storage provider |
| KServe | https://kserve.github.io/website/docs/model-serving/generative-inference/llmisvc/llmisvc-configuration | LLMInferenceService model、parallelism、router、scaling 配置 |
| KServe | https://kserve.github.io/website/docs/reference/crd-api | KServe CRD API reference |
| KServe | https://github.com/kserve/kserve | KServe 官方仓库、CRD 和 runtime 入口 |
| vLLM | https://docs.vllm.ai/en/stable/deployment/integrations/kserve/ | vLLM KServe integration |
| Ray Serve | https://docs.ray.io/en/latest/serve/advanced-guides/advanced-autoscaling.html | Ray Serve autoscaling |
| Ray Serve | https://docs.ray.io/en/latest/serve/autoscaling-guide.html | Ray Serve autoscaling guide |
| KubeRay | https://docs.ray.io/en/latest/cluster/kubernetes/user-guides/rayservice.html | RayService 部署和滚动更新 |
| KubeRay | https://docs.ray.io/en/latest/cluster/kubernetes/user-guides/configuring-autoscaling.html | KubeRay autoscaling |
| KubeRay | https://docs.ray.io/en/latest/cluster/kubernetes/index.html | Ray on Kubernetes |
| BentoML | https://docs.bentoml.com/en/latest/build-with-bentoml/llm.html | BentoML LLM serving |
| BentoML | https://docs.bentoml.com/en/latest/build-with-bentoml/services.html | BentoML service、resources、traffic、workers 配置 |
| BentoML | https://docs.bentoml.com/en/latest/examples/vllm.html | BentoML vLLM example |
| BentoML | https://raw.githubusercontent.com/bentoml/BentoVLLM/main/llama3.1-8b-instruct/service.py | BentoVLLM `BentoArgs`、resources、traffic、vLLM CLI 映射 |
| BentoML | https://docs.bentoml.com/en/latest/build-with-bentoml/model-loading-and-management.html | BentoML model loading and management |
| OpenLLM | https://github.com/bentoml/OpenLLM | OpenLLM self-hosted OpenAI-compatible API |
| OpenLLM | https://raw.githubusercontent.com/bentoml/OpenLLM/main/src/openllm/__main__.py | OpenLLM CLI 参数入口 |
| Envoy AI Gateway | https://aigateway.envoyproxy.io/docs/ | Envoy AI Gateway 文档入口 |
| Envoy AI Gateway | https://aigateway.envoyproxy.io/docs/api/ | AIGatewayRoute、AIServiceBackend 等 API reference |
| Envoy AI Gateway | https://aigateway.envoyproxy.io/docs/capabilities/traffic/ | traffic routing、policy、rate limit、failover 能力 |
| Envoy AI Gateway | https://aigateway.envoyproxy.io/docs/capabilities/inference/aigatewayroute-inferencepool/ | AIGatewayRoute 使用 InferencePool |
| Envoy AI Gateway | https://aigateway.envoyproxy.io/docs/capabilities/inference/httproute-inferencepool/ | HTTPRoute 使用 InferencePool |
| Envoy AI Gateway | https://github.com/envoyproxy/ai-gateway | Envoy AI Gateway 官方仓库 |
| Gateway API Inference Extension | https://gateway-api-inference-extension.sigs.k8s.io/ | Kubernetes Gateway API 推理扩展文档 |
| Gateway API Inference Extension | https://github.com/kubernetes-sigs/gateway-api-inference-extension | InferencePool、InferenceModel、Endpoint Picker 官方仓库 |
| OpenTelemetry | https://opentelemetry.io/docs/specs/semconv/gen-ai/ | GenAI semantic conventions |
| OpenTelemetry | https://github.com/open-telemetry/semantic-conventions-genai | GenAI semantic conventions working repo |
| Prometheus | https://prometheus.io/docs/practices/naming/ | metric naming 和 label 实践 |
| Triton Inference Server | https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/metrics.html | Triton metrics |
| Hugging Face TGI | https://huggingface.co/docs/text-generation-inference/en/basic_tutorials/monitoring | TGI monitoring / Prometheus |
| Hugging Face TGI | https://huggingface.co/docs/text-generation-inference/en/reference/metrics | TGI metrics reference |
| SGLang | https://docs.sglang.io/docs/references/production_metrics | SGLang production metrics |
| Outlines | https://dottxt-ai.github.io/outlines/latest/ | Outlines structured generation docs |
| Outlines | https://github.com/dottxt-ai/outlines | Outlines source / README |
| Guidance | https://github.com/guidance-ai/guidance | Guidance constrained generation |
| LM Format Enforcer | https://github.com/noamgat/lm-format-enforcer | JSON schema / regex token filtering |
| XGrammar | https://xgrammar.mlc.ai/docs/ | XGrammar documentation |
| XGrammar | https://github.com/mlc-ai/xgrammar | XGrammar source / README |
| vLLM | https://docs.vllm.ai/en/latest/features/structured_outputs/ | 最新 structured outputs 接口与 backend |
| vLLM | https://docs.vllm.ai/en/stable/cli/bench/serve/ | `vllm bench serve` 数据集和负载参数 |
| NVIDIA GenAI-Perf | https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/docs/multi_turn.html | multi-turn benchmark 参数 |
| Triton Perf Analyzer | https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/docs/inference_load_modes.html | concurrency / request rate / custom load modes |
| GuideLLM | https://github.com/vllm-project/guidellm | LLM load testing tool |
| MLX LM | https://github.com/ml-explore/mlx-lm | Apple silicon LLM 推理、server、convert、quantize |
| MLX LM | https://raw.githubusercontent.com/ml-explore/mlx-lm/main/mlx_lm/generate.py | generate CLI 参数、KV cache / prompt cache / sampling |
| MLX LM | https://raw.githubusercontent.com/ml-explore/mlx-lm/main/mlx_lm/server.py | server 参数、prompt cache、CORS |
| MLX LM | https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md | LoRA / DoRA / full fine-tune 参数 |
| Apple MLX | https://ml-explore.github.io/mlx/build/html/index.html | MLX array framework 与 Apple silicon backend |
| CTranslate2 | https://opennmt.net/CTranslate2/ | CTranslate2 runtime 总览 |
| CTranslate2 | https://github.com/opennmt/ctranslate2 | CTranslate2 官方仓库 |
| CTranslate2 | https://opennmt.net/CTranslate2/python/ctranslate2.Generator.html | Generator API |
| CTranslate2 | https://opennmt.net/CTranslate2/python/ctranslate2.Translator.html | Translator API |
| CTranslate2 | https://opennmt.net/CTranslate2/quantization.html | quantization / compute type |
| CTranslate2 | https://opennmt.net/CTranslate2/parallel.html | parallel and asynchronous execution |
| CTranslate2 | https://opennmt.net/CTranslate2/conversion.html | model conversion |
| CTranslate2 | https://opennmt.net/CTranslate2/guides/transformers.html | Transformers model conversion |
| CTranslate2 | https://opennmt.net/CTranslate2/performance.html | performance guide |
| CTranslate2 | https://github.com/OpenNMT/CTranslate2/blob/master/docs/performance.md | performance tuning |
| ExLlamaV2 | https://github.com/turboderp-org/exllamav2 | ExLlamaV2 本地低比特 GPU 推理 |
| ExLlamaV2 | https://github.com/turboderp-org/exllamav2/blob/master/doc/convert.md | EXL2/GPTQ 转换与量化 |
| ExLlamaV2 | https://github.com/turboderp-org/exllamav2/blob/master/doc/dynamic.md | dynamic generator、paged attention、continuous batching |
| ExLlamaV2 | https://raw.githubusercontent.com/turboderp-org/exllamav2/master/examples/chat.py | chat example、sampler/cache 参数 |
| ExLlamaV2 | https://raw.githubusercontent.com/turboderp-org/exllamav2/master/exllamav2/model_init.py | model init、GPU split、tensor parallel 参数 |
| ONNX Runtime | https://onnxruntime.ai/docs/execution-providers/QNN-ExecutionProvider.html | Qualcomm QNN Execution Provider |
| ONNX Runtime | https://onnxruntime.ai/docs/execution-providers/OpenVINO-ExecutionProvider.html | OpenVINO Execution Provider |
| ONNX Runtime | https://onnxruntime.ai/docs/performance/model-optimizations/graph-optimizations.html | ONNX graph optimization |
| OpenVINO | https://docs.openvino.ai/2025/openvino-workflow/model-preparation.html | OpenVINO model preparation |
| OpenVINO | https://docs.openvino.ai/2025/openvino-workflow/running-inference/inference-devices-and-modes/npu-device.html | OpenVINO NPU device |
| OpenVINO | https://docs.openvino.ai/2025/openvino-workflow/running-inference/optimize-inference.html | OpenVINO optimize inference |
| TensorRT-LLM | https://nvidia.github.io/TensorRT-LLM/commands/trtllm-build.html | `trtllm-build` engine 构建参数 |
| TensorRT-LLM | https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/features/torch_compile_and_piecewise_cuda_graph.md | torch compile and piecewise CUDA graph |
| PyTorch | https://docs.pytorch.org/docs/stable/generated/torch.compile.html | `torch.compile` API |
| OpenVINO | https://docs.openvino.ai/2025/openvino-workflow/model-optimization.html | OpenVINO model optimization |
| NVIDIA NIM | https://docs.nvidia.com/nim/large-language-models/latest/introduction.html | NIM for LLMs 总览 |
| NVIDIA NIM | https://docs.nvidia.com/nim/large-language-models/latest/get-started/quickstart.html | NIM quickstart、容器启动、本地 cache |
| NVIDIA NIM | https://docs.nvidia.com/nim/large-language-models/latest/api-reference.html | OpenAI-compatible API reference |
| NVIDIA NIM | https://docs.nvidia.com/nim/large-language-models/latest/support-matrix.html | 支持模型、GPU 和 profile matrix |
| NVIDIA NIM | https://docs.nvidia.com/nim/large-language-models/latest/deployment/model-profiles-and-selection.html | model profiles and selection |
| NVIDIA NIM | https://docs.nvidia.com/nim/large-language-models/latest/deployment/model-download.html | model download、download-to-cache、checksum 验证 |
| NVIDIA NIM | https://docs.nvidia.com/nim/large-language-models/latest/observability.html | observability / metrics |
| NVIDIA NIM | https://docs.nvidia.com/nim/large-language-models/latest/reference/environment-variables.html | NIM environment variables |
| NVIDIA NIM | https://docs.nvidia.com/nim/large-language-models/latest/reference/logging-and-observability.html | logging、metrics、tracing |
| NVIDIA NIM | https://docs.nvidia.com/nim/large-language-models/latest/advanced-use-cases/finetune-lora.html | LoRA fine-tuning and serving |
| AWS Neuron | https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/index.html | Neuron libraries overview、NxD Inference |
| AWS Neuron | https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/neuronx-distributed/neuronx_distributed_inference_developer_guide.html | NeuronX Distributed inference developer guide |
| AWS Neuron | https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/developer_guides/vllm-user-guide.html | vLLM on Neuron user guide |
| AWS Neuron | https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/api-guides/api-guide.html | NeuronConfig、batch/context、TP 参数 |
| AWS Neuron | https://awsdocs-neuron.readthedocs-hosted.com/en/v2.28.0/libraries/transformers-neuronx/ | transformers-neuronx legacy notice |
| Optimum Neuron | https://huggingface.co/docs/optimum-neuron/en/guides/vllm_plugin | Optimum Neuron vLLM plugin |
| vLLM Neuron | https://docs.vllm.ai/en/v0.10.1/getting_started/installation/aws_neuron.html | vLLM AWS Neuron installation |
| vLLM Neuron | https://github.com/vllm-project/vllm-neuron | vLLM Neuron integration repository |
| AWS Neuron | https://awsdocs-neuron.readthedocs-hosted.com/en/latest/general/arch/neuron-features/neuron-caching.html | Neuron persistent compile cache |
| Google Cloud TPU | https://docs.cloud.google.com/tpu/docs/tpu-inference | TPU inference documentation |
| vLLM TPU | https://docs.vllm.ai/projects/tpu/en/latest/ | vLLM TPU documentation |
| vLLM TPU | https://docs.vllm.ai/en/v0.11.0/getting_started/installation/google_tpu.html | vLLM Google TPU installation |
| vLLM TPU | https://github.com/vllm-project/tpu-inference | TPU inference repository |
| vLLM TPU | https://github.com/vllm-project/tpu-inference/blob/main/docs/getting_started/quickstart.md | TPU quickstart |
| Google GKE | https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-vllm-tpu | Serve vLLM on TPU in GKE |
| Google GKE | https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-multihost-tpu-jetstream | Serve multi-host TPU with JetStream |
| Google GKE | https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-llm-tpu-jetstream-pytorch | Serve LLM with JetStream PyTorch on GKE |
| Google GKE | https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-gemma-tpu-jetstream | Serve Gemma with JetStream on TPU |
| Google JetStream | https://github.com/AI-Hypercomputer/JetStream | JetStream repository |
| Google JetStream | https://github.com/AI-Hypercomputer/jetstream-pytorch | jetstream-pytorch repository |
| Google JetStream | https://github.com/google/jetstream-pytorch/blob/main/benchmarks/summary.md | JetStream PyTorch benchmark parameters |
| Google MaxText | https://github.com/AI-Hypercomputer/maxtext | MaxText repository |
| Google MaxText | https://maxtext.readthedocs.io/en/latest/reference/architecture/architecture_overview.html | MaxText XLA / parallelism architecture |
| Google Cloud TPU | https://cloud.google.com/blog/products/compute/ai-hypercomputer-inference-updates-for-google-cloud-tpu-and-gpu | AI Hypercomputer inference update、Pathways / disaggregated serving |
| Intel IPEX-LLM | https://github.com/intel/ipex-llm | IPEX-LLM repository |
| Intel IPEX-LLM | https://ipex-llm-latest.readthedocs.io/ | IPEX-LLM documentation |
| Optimum Intel | https://huggingface.co/docs/optimum-intel/en/index | Optimum Intel documentation |
| Optimum Intel | https://huggingface.co/docs/optimum-intel/en/openvino/inference | Optimum Intel OpenVINO inference |
| Optimum Intel | https://github.com/huggingface/optimum-intel | Optimum Intel repository |
| OpenVINO | https://github.com/openvinotoolkit/openvino | OpenVINO repository |
| OpenVINO | https://docs.openvino.ai/2026/openvino-workflow-generative/inference-with-optimum-intel.html | OpenVINO with Optimum Intel |
| Intel Extension for PyTorch | https://intel.github.io/intel-extension-for-pytorch/ | Intel Extension for PyTorch documentation |
| vLLM | https://docs.vllm.ai/en/stable/design/prefix_caching/ | prefix caching design |
| OpenAI | https://developers.openai.com/api/docs/guides/prompt-caching | provider prompt caching |
| Amazon Bedrock | https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html | Bedrock prompt caching |
| Google Gemini | https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/context-cache/context-cache-overview | Gemini context caching |
| Triton Inference Server | https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/response_cache.html | Triton response cache |
| LiteLLM | https://docs.litellm.ai/docs/proxy/caching | proxy caching |
| LiteLLM | https://docs.litellm.ai/docs/caching/all_caches | caching providers |
| GPTCache | https://github.com/zilliztech/gptcache | semantic cache for LLMs |
| LMCache | https://docs.lmcache.ai/kv_cache/local_storage.html | KV cache local storage |
| vLLM | https://docs.vllm.ai/en/stable/features/kv_offloading_usage/ | KV offloading connector |
| Redis | https://redis.io/docs/latest/develop/use-cases/semantic-cache/ | Redis semantic cache |
| FlashAttention | https://github.com/Dao-AILab/flash-attention | IO-aware exact attention kernels、KV cache inference kernels |
| FlashInfer | https://docs.flashinfer.ai/ | LLM serving kernels、paged KV cache、decode/prefill attention |
| xFormers | https://facebookresearch.github.io/xformers/components/ops.html | memory efficient attention operators |
| NVIDIA CUDA | https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html | CUDA Graph、pinned memory、unified memory 等 CUDA 运行时机制 |
| NVIDIA cuBLAS | https://docs.nvidia.com/cuda/cublas/index.html#results-reproducibility | cuBLAS 结果可复现条件、workspace 与 stream 并发注意事项 |
| NVIDIA CUDA | https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/unified-memory.html | Unified Memory / managed memory |
| NVIDIA NVLink | https://www.nvidia.com/en-us/data-center/nvlink/ | GPU-GPU 互连与 MoE all-to-all 背景 |
| DeepEP | https://github.com/deepseek-ai/DeepEP | MoE expert parallel all-to-all communication library |
| Hugging Face Transformers | https://huggingface.co/docs/transformers/en/internal/rope_utils | RoPE scaling 类型与 `rope_parameters` |
| Qwen | https://qwen.readthedocs.io/en/latest/deployment/sglang.html | SGLang 部署 Qwen 时的 YaRN / rope_scaling 配置提醒 |
| Hugging Face safetensors | https://huggingface.co/docs/safetensors/en/index | safetensors 安全与 lazy loading |
| Hugging Face Transformers | https://huggingface.co/docs/transformers/en/chat_templating | chat template 与 message formatting |
| Hugging Face Transformers | https://huggingface.co/docs/transformers/en/chat_templating_writing | 编写 chat template 与 special tokens |
| OpenAI | https://developers.openai.com/api/docs/guides/function-calling | function calling / tool calling |
| OpenAI | https://developers.openai.com/api/docs/guides/structured-outputs | structured outputs 与 JSON schema |
| OpenAI | https://developers.openai.com/api/docs/guides/images-vision | image input、detail、patch/tile token 预算 |
| OpenAI | https://developers.openai.com/api/docs/guides/audio | audio input/output/transcription |
| GGUF | https://ggml-org-ggml.mintlify.app/formats/gguf | GGUF 格式规范说明 |
| OpenAI | https://developers.openai.com/api/docs/guides/streaming-responses | Streaming responses、SSE chunk 与客户端解析语义 |
| OpenAI | https://developers.openai.com/api/reference/resources/responses/streaming-events/ | Responses API streaming events |
| OpenAI | https://developers.openai.com/api/reference/resources/responses/methods/cancel/ | background response cancel API |
| OpenAI | https://developers.openai.com/api/docs/guides/reasoning | reasoning models、reasoning effort 和输出预算 |
| OpenAI | https://developers.openai.com/api/reference/overview/ | API 总览、debug request、request id、接口资源入口 |
| OpenAI | https://developers.openai.com/api/docs/guides/migrate-to-responses | Chat Completions 与 Responses API 迁移差异 |
| OpenAI | https://developers.openai.com/api/docs/guides/function-calling | function/tool calling 请求与返回结构 |
| vLLM | https://docs.vllm.ai/en/stable/serving/openai_compatible_server/ | OpenAI-compatible server 和后端扩展字段 |
| vLLM | https://docs.vllm.ai/en/stable/serving/online_serving/ | OpenAI、Responses、Cohere/Jina rerank 等 online serving endpoint |
| vLLM | https://docs.vllm.ai/en/stable/api/vllm/sampling_params.html | `SamplingParams` 请求级采样、penalty、stop 和长度控制 |
| NVIDIA NIM | https://docs.nvidia.com/nim/large-language-models/latest/api-reference.html | NIM OpenAI-compatible API reference |
| MLC LLM | https://llm.mlc.ai/docs/deploy/rest.html | REST server 与 OpenAI-compatible API |
| SGLang | https://docs.sglang.io/ | OpenAI/Hugging Face API 兼容、生产 serving 总览 |
| KServe | https://kserve.github.io/website/docs/model-serving/predictive-inference/autoscaling/kpa-autoscaler | Knative Pod Autoscaler 与 KServe autoscaling |
| Knative | https://knative.dev/docs/serving/autoscaling/ | Knative autoscaling 模型 |
| Knative | https://knative.dev/docs/serving/autoscaling/concurrency/ | concurrency target 与 container concurrency |
| Knative | https://knative.dev/docs/serving/load-balancing/target-burst-capacity/ | target burst capacity 与突发请求缓冲 |
| Knative | https://knative.dev/docs/serving/autoscaling/scale-to-zero/ | scale-to-zero 与冷启动背景 |
| KEDA | https://keda.sh/docs/2.20/concepts/scaling-deployments/ | 基于事件/指标扩缩容 deployment |
| KEDA | https://keda.sh/docs/2.20/reference/scaledobject-spec/ | ScaledObject 参数 |
| KEDA | https://keda.sh/docs/2.20/scalers/prometheus/ | Prometheus scaler |
| AWS SageMaker | https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-container-docs.html | SageMaker LMI container 文档入口 |
| AWS SageMaker | https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-models-frameworks-djl-serving.html | SageMaker DJL Serving 部署、model artifact 结构 |
| DJL Serving LMI | https://docs.djl.ai/master/docs/serving/serving/docs/lmi/index.html | LMI 文档入口 |
| DJL Serving LMI | https://docs.djl.ai/master/docs/serving/serving/docs/lmi/deployment_guide/configurations.html | `serving.properties`、环境变量、rolling batch、TP、队列等配置 |
| DJL Serving LMI | https://docs.djl.ai/master/docs/serving/serving/docs/lmi/user_guides/vllm_user_guide.html | LMI vLLM backend、量化、LoRA、advanced configs |
| DJL Serving LMI | https://github.com/deepjavalibrary/djl-serving/blob/master/serving/docs/lmi/user_guides/starting-guide.md | 简化环境变量、batch、concurrency、TP 配置 |
| FastChat | https://github.com/lm-sys/FastChat | FastChat serving、controller/worker/API server |
| FastChat | https://github.com/lm-sys/FastChat/blob/main/docs/openai_api.md?plain=1 | OpenAI-compatible API server |
| FastChat | https://github.com/lm-sys/FastChat/blob/main/fastchat/serve/openai_api_server.py | OpenAI API server source |
| FastChat | https://github.com/lm-sys/FastChat/blob/main/docs/vllm_integration.md | vLLM worker integration |
| Sonar/Aphrodite | https://github.com/PygmalionAI/aphrodite-engine | Aphrodite Engine 仓库重定向到 Sonar |
| Sonar | https://github.com/dphnAI/sonar | 当前 Sonar README、server 入口和能力矩阵 |
| Aphrodite Engine | https://pypi.org/project/aphrodite-engine/ | Python package 名称和项目演进背景 |
| Sonar | https://sonar.dphn.ai/reference/server-arguments/ | generated server arguments |
| Sonar | https://sonar.dphn.ai/serving/openai/ | OpenAI-compatible API |
| Sonar | https://sonar.dphn.ai/deployment/optimization/ | deployment optimization |
| Sonar | https://sonar.dphn.ai/reference/quantization/ | quantization support matrix |
| NVIDIA NIM Benchmarking | https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html | LLM benchmark 指标定义 |
| NVIDIA NIM Benchmarking | https://docs.nvidia.com/nim/benchmarking/llm/latest/overview.html | NIM benchmark 流程 |
| NVIDIA AIPerf | https://docs.nvidia.com/aiperf/reference/ai-perf-metrics-reference | AI inference 性能指标参考 |
| NVIDIA AIPerf | https://github.com/ai-dynamo/aiperf | AIPerf 工具仓库 |
| Google Cloud | https://cloud.google.com/products/compute/pricing | GPU/Compute 成本建模的公开价格入口 |
| Google Cloud | https://docs.cloud.google.com/compute/docs/gpus | GPU 类型与配置参考 |
| Anthropic | https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking | extended thinking 与 thinking token budget |
| Anthropic | https://docs.anthropic.com/en/api/messages | Messages API 中 thinking / max_tokens 相关字段 |
| Hugging Face Hub | https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables | HF_HOME、HF_HUB_CACHE、HF_TOKEN、offline/cache 环境变量 |
| Hugging Face Hub | https://huggingface.co/docs/huggingface_hub/en/guides/manage-cache | Hub cache refs/blobs/snapshots 管理 |
| Hugging Face Hub | https://huggingface.co/docs/huggingface_hub/en/guides/download | snapshot/download 与 revision 固定 |
| PyTorch | https://docs.pytorch.org/docs/stable/notes/randomness.html | PyTorch reproducibility、随机种子、确定性算法和库版本限制 |
| PyTorch | https://docs.pytorch.org/docs/2.9/generated/torch.use_deterministic_algorithms.html | deterministic algorithms API |
| Envoy | https://www.envoyproxy.io/docs/envoy/latest/faq/configuration/timeouts | route timeout、stream idle timeout、request timeout 等代理层超时 |
| Envoy | https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/buffer_filter | buffer filter 对 streaming 语义的影响 |
| LocalAI | https://localai.io/ | LocalAI 官方文档入口 |
| LocalAI | https://localai.io/docs/basics/getting_started/ | quickstart、OpenAI-compatible API base URL |
| LocalAI | https://localai.io/docs/features/text-generation/ | text generation、chat/completions/models API 示例 |
| LocalAI | https://localai.io/docs/advanced/model-configuration/ | 模型 YAML/config、backend、上下文、线程、grammar 等模型配置 |
| LocalAI | https://localai.io/docs/model-compatibility/ | backend、model family、embedding、streaming、加速兼容矩阵 |
| LocalAI | https://localai.io/docs/advanced/ | advanced usage、服务与模型配置入口 |
| LocalAI | https://github.com/mudler/LocalAI | LocalAI 官方仓库 |
| mistral.rs | https://ericlbuehler.github.io/mistral.rs/ | mistral.rs 官方文档入口 |
| mistral.rs | https://ericlbuehler.github.io/mistral.rs/guides/serve/openai-compatible-apis/ | OpenAI-compatible `/v1` serving |
| mistral.rs | https://ericlbuehler.github.io/mistral.rs/reference/cli/ | CLI reference |
| mistral.rs | https://ericlbuehler.github.io/mistral.rs/reference/cli/serve/ | serve CLI、OpenAI-compatible server 参数入口 |
| mistral.rs | https://ericlbuehler.github.io/mistral.rs/guides/quantization/quantize-a-model/ | `--quant`、`--isq`、UQFF/GGUF 量化 |
| mistral.rs | https://ericlbuehler.github.io/mistral.rs/guides/models/run-gguf/ | GGUF、`--mmproj`、`--tok-model-id`、multimodal GGUF |
| mistral.rs | https://ericlbuehler.github.io/mistral.rs/guides/perf/paged-attention/ | PagedAttention、KV cache block pool 和参数 |
| mistral.rs | https://ericlbuehler.github.io/mistral.rs/guides/customize/chat-templates/ | chat template 解析和 override |
| mistral.rs | https://ericlbuehler.github.io/mistral.rs/guides/customize/lora-adapters/ | LoRA adapter 加载、动态选择和限制 |
| mistral.rs | https://ericlbuehler.github.io/mistral.rs/guides/models/multimodal-input/ | OpenAI content part、多模态输入 |
| mistral.rs | https://github.com/ericlbuehler/mistral.rs | mistral.rs 官方仓库 |
| OpenAI | https://developers.openai.com/api/reference/resources/completions/methods/create/ | `logit_bias`、frequency/presence penalty、temperature/top_p、max_tokens 语义 |
| TabbyAPI | https://theroyallab.github.io/tabbyAPI | TabbyAPI 官方文档入口 |
| TabbyAPI | https://github.com/theroyallab/tabbyAPI | TabbyAPI 官方仓库 |
| TabbyAPI | https://github.com/theroyallab/tabbyAPI/blob/main/README.md | TabbyAPI README、当前 ExLlama runtime 说明 |
| TabbyAPI | https://github.com/theroyallab/tabbyAPI/blob/main/config_sample.yml | server/model/cache/API 配置样例 |
| TabbyAPI | https://github.com/theroyallab/tabbyAPI/blob/main/api_tokens_sample.yml | API token 配置样例 |
| TabbyAPI | https://github.com/theroyallab/tabbyAPI/blob/main/docs/01.-Getting-Started.md | getting started、安装和运行入口 |
| TabbyAPI | https://github.com/theroyallab/tabbyAPI/blob/main/docs/10.-Tool-Calling.md | tool calling 文档 |
| KoboldCpp | https://github.com/LostRuins/koboldcpp | KoboldCpp 官方仓库 |
| KoboldCpp | https://github.com/LostRuins/koboldcpp/blob/concedo/README.md | KoboldCpp README、运行、server 和参数入口 |
| KoboldCpp | https://github.com/LostRuins/koboldcpp/wiki | KoboldCpp wiki |
| llama-swap | https://github.com/mostlygeek/llama-swap | llama-swap 官方仓库 |
| llama-swap | https://github.com/mostlygeek/llama-swap/blob/main/README.md | 本地多模型切换和 OpenAI-compatible router |
| llama-swap | https://github.com/mostlygeek/llama-swap/blob/main/config.example.yaml | 模型 TTL、alias、profile 和 unload 示例配置 |
| KTransformers | https://kvcache-ai.github.io/ktransformers/ | KTransformers 官方文档入口 |
| KTransformers | https://github.com/kvcache-ai/ktransformers | KTransformers 官方仓库 |
| KTransformers | https://github.com/kvcache-ai/ktransformers/blob/main/README.md | 项目能力、异构推理、模型支持和使用入口 |
| KTransformers | https://github.com/kvcache-ai/ktransformers/blob/main/doc/en/DeepseekR1_V3_tutorial.md | DeepSeek R1/V3 本地推理、长上下文、FP8/kt-kernel 调优入口 |
| KTransformers | https://github.com/kvcache-ai/ktransformers/blob/main/kt-kernel/README.md | kt-kernel 高性能推理内核 |
| KTransformers | https://github.com/kvcache-ai/ktransformers/blob/main/doc/en/kt-kernel/experts-sched-Tutorial.md | expert scheduling、热专家放置和动态专家更新 |
| KTransformers | https://github.com/kvcache-ai/ktransformers/blob/main/doc/en/kt-kernel/Native-Precision-Tutorial.md | native precision / CPU MoE 精度路径 |
| KTransformers | https://github.com/kvcache-ai/ktransformers/blob/main/doc/en/kt-kernel/deepseek-v3.2-sglang-tutorial.md | DeepSeek V3.2 + SGLang-KT serving |
| KTransformers | https://github.com/kvcache-ai/ktransformers/blob/main/doc/en/prefix_cache.md | prefix cache |
| KTransformers | https://github.com/kvcache-ai/ktransformers/blob/main/doc/en/balance-serve.md | balance serve / 多实例服务入口 |
| KTransformers | https://madsys.cs.tsinghua.edu.cn/publication/ktransformers-unleashing-the-full-potential-of-cpu/gpu-hybrid-inference-for-moe-models/ | CPU/GPU hybrid inference for MoE paper page |
| llamafile | https://docs.mozilla.ai/llamafile | llamafile 官方文档入口 |
| llamafile | https://docs.mozilla.ai/llamafile/getting-started/quickstart | quickstart、外部权重和本地运行 |
| llamafile | https://docs.mozilla.ai/llamafile/using-llamafile/running_llamafile | running llamafile、服务和本地使用 |
| llamafile | https://docs.mozilla.ai/llamafile/reference/cli_arguments | CLI 参数 |
| llamafile | https://docs.mozilla.ai/llamafile/reference/security | security、sandbox、server/tools 风险 |
| llamafile | https://docs.mozilla.ai/llamafile/reference/technical_details | 技术细节、单文件运行时背景 |
| llamafile | https://docs.mozilla.ai/llamafile/reference/troubleshooting | troubleshooting |
| llamafile | https://github.com/mozilla-ai/llamafile | llamafile 官方仓库 |

## 论文与研究来源

| 主题 | 来源 | 用途 |
|---|---|---|
| PagedAttention | https://arxiv.org/abs/2309.06180 | vLLM/PagedAttention 背景、block KV cache 与吞吐提升 |
| Iteration-level scheduling | https://www.usenix.org/conference/osdi22/presentation/yu | Orca 的 iteration-level scheduling 与 selective batching |
| Chunked prefill | https://arxiv.org/abs/2308.16369 | SARATHI 的 chunked-prefills 与 decode-maximal batching |
| Chunked prefill serving | https://arxiv.org/abs/2403.02310 | Sarathi-Serve 的调度与 bubble 降低 |
| Prefill/decode disaggregation | https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin | DistServe 的 prefill/decode 分离服务架构 |
| Speculative sampling | https://arxiv.org/abs/2302.01318 | draft model + target model 验证的基础算法 |
| Medusa | https://arxiv.org/abs/2401.10774 | 多 decoding heads speculative decoding |
| EAGLE | https://github.com/SafeAILab/EAGLE | EAGLE 系列 speculative decoding 实现与论文入口 |
| AWQ | https://arxiv.org/abs/2306.00978 | activation-aware weight-only quantization |
| GPTQ | https://arxiv.org/abs/2210.17323 | one-shot post-training quantization |
| LLM.int8 | https://arxiv.org/abs/2208.07339 | outlier-aware 8-bit LLM inference |
| FlashAttention | https://arxiv.org/abs/2205.14135 | IO-aware attention kernel 原理 |
| YaRN | https://arxiv.org/abs/2309.00071 | RoPE context window extension |
| RoPE | https://arxiv.org/abs/2104.09864 | Rotary position embedding 基础 |
| DeepSeek-V3 | https://arxiv.org/pdf/2412.19437 | MoE 部署、redundant experts、micro-batch overlap |
| FlashInfer | https://arxiv.org/abs/2501.01005 | serving-oriented attention/kernel generator 与 paged KV 支持 |
| DeepSeek-V2 | https://arxiv.org/abs/2405.04434 | MLA、DeepSeekMoE、长上下文和 KV cache 压缩背景 |
| FlexGen | https://arxiv.org/abs/2303.06865 | GPU/CPU/disk offloading 与有限 GPU 内存下的 generation serving |

## 版本注意

- 推理框架参数更新频繁，尤其是 vLLM、SGLang、TensorRT-LLM 的并行、KV cache 和 speculative decoding 相关字段。
- 生产使用前建议运行对应框架的 `--help` 或读取安装版本的 API 文档，确认参数名和默认值。
- 本知识库关注“参数语义和调参原理”，不是完整 CLI man page 的替代品。
