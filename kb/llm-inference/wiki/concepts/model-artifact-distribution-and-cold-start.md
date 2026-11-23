---
type: Concept
title: 模型 Artifact 分发、缓存与冷启动
description: LLM 服务的第一次请求慢，常常不是模型算得慢，而是权重还没稳定地到达机器：下载、解压、校验、格式转换、engine build、profile
  选择、CUDA graph capture 和 warmup 都可能在用户路径上发生。模型 artifact 分发是推理系统的“供应链 + 启动路径”问题。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 模型 Artifact 分发、缓存与冷启动

LLM 服务的第一次请求慢，常常不是模型算得慢，而是权重还没稳定地到达机器：下载、解压、校验、格式转换、engine build、profile 选择、CUDA graph capture 和 warmup 都可能在用户路径上发生。模型 artifact 分发是推理系统的“供应链 + 启动路径”问题。

## 冷启动阶段

| 阶段 | 典型耗时来源 |
|---|---|
| 镜像拉取 | CUDA/ROCm/vLLM/Triton/NIM 镜像大 |
| 权重下载 | Hugging Face Hub、S3、NGC、对象存储、PVC |
| cache 解析 | refs、blobs、snapshots、Xet/chunk cache |
| 安全加载 | safetensors、pickle/remote code、revision 校验 |
| engine 初始化 | dtype、quantization、TP/PP、KV cache 预分配 |
| engine build/compile | TensorRT-LLM、Neuron、OpenVINO、MLC、torch.compile |
| warmup | CUDA graph capture、真实 batch shape、tokenizer 初始化 |

上线前要把这些阶段拆开测，否则 steady-state benchmark 会掩盖冷启动风险。

## Hugging Face Hub cache

Hugging Face Hub cache 使用 refs、blobs、snapshots 等结构，把同一文件内容去重，并用 revision 指向具体 snapshot。关键环境变量：

| 变量 | 作用 |
|---|---|
| `HF_HOME` | Hugging Face 本地状态根目录 |
| `HF_HUB_CACHE` | Hub repo cache 目录 |
| `HF_TOKEN` | 私有/gated 模型访问 token |
| `HF_HUB_OFFLINE` | 离线模式，避免启动时访问网络 |
| `HF_HUB_ENABLE_HF_TRANSFER` | 启用 hf_transfer 加速路径 |
| `HF_XET_CACHE` / Xet cache | Xet chunk cache 相关路径 |

生产建议固定 model revision，把 cache 目录挂到持久卷或节点本地 NVMe。否则每次 Pod 重建都可能重新下载几十到几百 GB 权重。

## 模型格式与安全

| 格式/机制 | 冷启动影响 |
|---|---|
| safetensors | 安全、可按 tensor 访问，避免 pickle 任意代码执行风险 |
| PyTorch pickle/bin | 兼容广，但供应链风险更高 |
| GGUF | llama.cpp 本地加载友好，可 mmap |
| TensorRT engine | 启动快但 build 慢，shape/profile 固定 |
| ONNX/OpenVINO/MLC compiled artifact | 适合部署复用，但转换版本要固定 |

如果使用 `trust_remote_code`，冷启动路径会执行模型仓库代码；这既是安全边界，也是可复现性边界。

## 平台参数

| 平台 | 参数/概念 | 原理 |
|---|---|---|
| KServe | `storageUri`、PVC、HF storage provider、runtime args | 控制权重来源和 runtime 拉取方式 |
| KServe | storage initializer、LocalModelCache | 把远端模型拉到本地目录，或复用节点级缓存 |
| SageMaker LMI / DJL | model artifact `.tar.gz`、`option.model_id`、`option.revision`、`option.model_loading_timeout` | 控制模型来源、版本和加载超时 |
| NVIDIA NIM | `NGC_API_KEY`、`NIM_CACHE_PATH`、`NIM_MODEL_PROFILE`、`NIM_MODEL_PATH` | 控制 NGC 拉取、模型 cache、本地模型路径和 profile 选择 |
| NVIDIA NIM | `download-to-cache`、`--verify-checksums` | 预下载模型并校验 cache，适合 air-gap 或预热 |
| BentoML / OpenLLM | `BentoModel`、`HuggingFaceModel`、volume/cache、env/secrets、Bento artifact | 控制服务 artifact 与模型缓存 |
| vLLM / Ray Serve | model id、revision、download dir、engine kwargs、warmup | 控制模型下载、加载和 replica 冷启动 |
| Hugging Face Hub | `HF_HOME`、`HF_HUB_CACHE`、`HF_TOKEN`、offline mode | 控制通用模型缓存 |

## 冷启动调参

| 症状 | 可能原因 | 优先动作 |
|---|---|---|
| Pod 长时间 Pending | GPU 节点/镜像/资源不足 | 检查 node pool、image pull、GPU limits |
| Pod Running 但未 Ready | 权重下载或模型加载慢 | 检查 cache、storage、token、loading timeout |
| 首请求特别慢 | warmup/CUDA graph/compile 在用户路径上 | readiness 后做真实 shape warmup |
| 每次扩容都重新下载 | cache 没持久化 | PVC、本地 NVMe、预拉权重 |
| 模型今天变了 | 未固定 revision/tag | pin revision、镜像 tag 和 engine version |
| 同模型不同节点表现不同 | profile/engine build 不一致 | 固定 profile、build artifact 和启动参数 |
| Windows/共享盘 cache 体积异常 | symlink 不可用导致复制大文件 | 检查 Hub cache 行为，避免复制型缓存 |
| NIM profile 与参数不一致 | backend-native args 覆盖 profile 预期 | 固定 profile，并记录覆盖项 |
| KServe 每个 Pod 都重拉对象存储 | storage initializer 没有复用缓存 | 使用 PVC、LocalModelCache 或节点预热 |

## 调参建议

- 把下载时间、加载时间、engine build、warmup 和首请求 TTFT 分开记录。
- 生产固定 model revision、tokenizer revision、runtime image tag 和 engine build 参数。
- 大模型 scale-to-zero 默认谨慎；保留 min replicas 或热备副本。
- 对私有模型，用 secret 注入 token，不要把 token 写进 artifact。
- 对多节点服务，让 cache 与节点亲和性配合，减少重复下载。
- 对 NIM/TensorRT-LLM/Neuron/TPU 类 profile/compile 场景，区分冷启动和 steady-state。

## 与其他页面的关系

- [模型格式、加载与供应链边界](model-formats-and-loading.md)：格式、安全和 revision pinning。
- [Kubernetes 模型服务部署](kubernetes-model-serving.md)：Pod、PVC、GPU 和 rollout。
- [KServe Generative Inference 参数模型](kserve-generative-inference-parameters.md)：`storageUri` 和 runtime args。
- [SageMaker / DJL Serving LMI 参数模型](sagemaker-djl-lmi-parameters.md)：LMI artifact 和 loading timeout。
- [NVIDIA NIM for LLMs 参数模型](nvidia-nim-llm-parameters.md)：NIM profile 和 cache。
- [图编译与 Engine 构建优化](graph-compilation-and-engine-build.md)：engine build 和编译产物。

## 关键来源

- Hugging Face Hub environment variables: https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables
- Hugging Face Hub cache management: https://huggingface.co/docs/huggingface_hub/en/guides/manage-cache
- Hugging Face Hub download guide: https://huggingface.co/docs/huggingface_hub/en/guides/download
- safetensors documentation: https://huggingface.co/docs/safetensors/en/index
- Hugging Face Transformers model loading: https://huggingface.co/docs/transformers/en/main_classes/model
- KServe Hugging Face storage provider: https://kserve.github.io/website/docs/model-serving/storage/providers/hf
- KServe storage overview: https://kserve.github.io/website/docs/model-serving/storage/overview
- KServe PVC storage provider: https://kserve.github.io/website/docs/model-serving/storage/providers/pvc
- KServe Text Generation task: https://kserve.github.io/website/docs/model-serving/generative-inference/tasks/text-generation
- SageMaker LMI container documentation: https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-container-docs.html
- DJL LMI configurations: https://docs.djl.ai/master/docs/serving/serving/docs/lmi/deployment_guide/configurations.html
- NVIDIA NIM model profiles: https://docs.nvidia.com/nim/large-language-models/latest/deployment/model-profiles-and-selection.html
- NVIDIA NIM model download: https://docs.nvidia.com/nim/large-language-models/latest/deployment/model-download.html
- NVIDIA NIM quickstart: https://docs.nvidia.com/nim/large-language-models/latest/get-started/quickstart.html
- NVIDIA NIM environment variables: https://docs.nvidia.com/nim/large-language-models/latest/reference/environment-variables.html
- BentoML model loading and management: https://docs.bentoml.com/en/latest/build-with-bentoml/model-loading-and-management.html
