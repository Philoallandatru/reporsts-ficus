---
type: Concept
title: KServe Generative Inference 参数模型
description: KServe 把模型服务变成 Kubernetes-native 的 `InferenceService`、`ServingRuntime`
  和相关 runtime。对 LLM 来说，KServe 不是 vLLM 的替代品；它负责部署、流量、伸缩、存储和 runtime 抽象，底层 token 生成仍由
  vLLM、Hugging Face runtim...
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# KServe Generative Inference 参数模型

KServe 把模型服务变成 Kubernetes-native 的 `InferenceService`、`ServingRuntime` 和相关 runtime。对 LLM 来说，KServe 不是 vLLM 的替代品；它负责部署、流量、伸缩、存储和 runtime 抽象，底层 token 生成仍由 vLLM、Hugging Face runtime、Triton 等执行。

## 配置层次

| 层 | 代表字段/对象 | 原理 |
|---|---|---|
| `InferenceService` | `predictor.model`、`storageUri`、runtime、resources | 声明要部署的模型服务 |
| Runtime | `ServingRuntime`、ClusterServingRuntime | 决定使用 vLLM/Hugging Face/Triton 等 server |
| Hugging Face runtime | `modelFormat.name=huggingface`、runtime args | KServe generative runtime 的常用入口 |
| `LLMInferenceService` | `model`、`replicas/scaling`、`parallelism`、`router` | 更细的 LLM 专用配置模型 |
| Model source | `storageUri`、PVC、对象存储、Hub token | 决定权重从哪里来，影响冷启动 |
| Engine args | runtime args/env，如 vLLM 参数 | 透传到底层 engine |
| Resources | GPU/CPU/memory limits、node selector、tolerations | 决定 Pod 调度到什么节点 |
| Autoscaling | KServe/Knative/HPA annotations | 决定 replica 数、scale-to-zero 和并发目标 |
| Protocol | OpenAI-compatible、KServe v2、embedding/rerank endpoint | 决定客户端请求形状 |

## 生成式 runtime 能力

KServe generative inference 文档覆盖文本生成、embedding、rerank 和 OpenAI-compatible API。Hugging Face serving runtime 可使用 vLLM backend，并通过 `InferenceService` 暴露 OpenAI-compatible endpoint。

注意两条边界：

- KServe 负责“模型服务对象”和 Kubernetes 生命周期。
- vLLM/TGI/Triton 负责“实际推理参数”，如上下文、KV cache、batch、dtype 和并行。

## 常见参数/配置

| 参数/字段 | 原理与影响 |
|---|---|
| `storageUri` | 模型权重来源；慢存储会直接拉长冷启动 |
| `modelFormat.name=huggingface` | 选择 Hugging Face generative runtime |
| `args` | 传给 runtime/engine 的参数列表 |
| runtime image/tag | 决定 vLLM/TGI/Triton 版本和支持参数 |
| runtime args | 传给 vLLM 等 engine 的启动参数 |
| `resources.limits.nvidia.com/gpu` | Pod 申请 GPU；不正确会导致调度失败或 CPU fallback |
| node selector / tolerations | 约束 GPU 节点池、MIG 节点或专用硬件 |
| Hugging Face token secret | 拉 gated/private 模型 |
| autoscaling annotations | 控制 min/max replicas、target concurrency、scale-to-zero |
| readiness/liveness | 决定模型何时开始接流量 |
| protocol/version | OpenAI API、KServe v2 或 runtime 自定义 endpoint |

Hugging Face runtime 常见参数：

| 参数 | 作用 |
|---|---|
| `--model_name` | 对外服务模型名 |
| `--model_dir` | 本地/挂载模型目录 |
| `--model_id` | Hugging Face Hub 模型 id；存在时可覆盖 `model_dir` |
| `--model_revision` | 固定模型 revision |
| `--tokenizer_revision` | 固定 tokenizer revision |
| `--dtype` | 模型 dtype |
| `--task` | text-generation、embedding、rerank 等任务 |
| `--backend` | vLLM 或 Hugging Face backend |
| `--max_model_len` | 上下文上限 |
| `--trust_remote_code` | 是否执行模型仓库自定义代码 |
| `--disable_log_requests` | 减少请求日志，保护内容并降低日志成本 |

vLLM backend 常见透传参数包括 `--quantization`、`--tensor_parallel_size`、`--gpu_memory_utilization`、`--max_model_len` 和 `--enforce_eager`。CPU vLLM 场景还要关注 `VLLM_CPU_KVCACHE_SPACE`、`VLLM_CPU_OMP_THREADS_BIND`、`VLLM_ENABLE_V1_MULTIPROCESSING` 这类环境变量。

## LLMInferenceService

KServe 的 LLMInferenceService 把模型、worker、prefill、router 和并行拆成更明确的 LLM 配置面：

| 字段族 | 作用 |
|---|---|
| `model.uri`、`model.name` | 模型来源和对外模型名 |
| `model.lora.adapters` | LoRA adapter 配置 |
| `replicas` / `scaling` | 固定副本或扩缩容配置 |
| `parallelism.tensor` | tensor parallel |
| `parallelism.data` / `dataLocal` | data parallel / 本地 data parallel |
| `parallelism.expert` | MoE expert parallel |
| `template.worker` / `template.prefill` | worker 和 prefill worker 模板 |
| `router.gateway` / `router.route` / `router.scheduler` | 网关、路由和调度配置 |

常见约束：`replicas` 和 `scaling` 不应混用；`route.spec` 和 `route.refs` 不应同时配置；data parallel 与 local data parallel 需要和 worker 组、GPU 数匹配。

## 调参路径

| 症状 | 可能原因 | 优先动作 |
|---|---|---|
| Pod 长时间未 ready | 权重下载慢、runtime 初始化慢、engine warmup 慢 | 检查 `storageUri`、secret、临时盘、readiness timeout |
| 扩容后吞吐不升 | 新 Pod 没拿到 GPU、Service 未路由、engine 参数太保守 | 检查 GPU limits、endpoint、engine metrics |
| scale-to-zero 后首请求很慢 | 大模型冷启动 | 设置 min replicas、权重缓存、预热 |
| OpenAI endpoint 正常但质量不一致 | runtime image、模型 revision、template 不一致 | 固定镜像 tag、模型 revision、chat template |
| embedding/rerank 延迟高 | 用了生成式 LLM 的调参方式 | 按 encoder batch tokens、pair 数和 pooling 调 |
| CPU 场景特别慢或 OOM | dtype/context/KV cache 不适合 CPU | 用 bf16、限制 `max_model_len`，设置 CPU KV cache 空间 |
| LLMInferenceService 状态异常 | replicas/scaling、route 或 DP 配置冲突 | 按 CRD 约束拆开验证 |

## 与 Ray Serve/BentoML 的区别

| 平台 | 更适合 |
|---|---|
| KServe | Kubernetes-native 多团队平台、标准化 runtime、CRD 管理 |
| Ray Serve | Python deployment graph、Ray 集群、vLLM replica/autoscaling |
| BentoML | 打包 service artifact、API 服务、BentoCloud/Kubernetes 部署 |
| Triton | 通用模型服务器、多 backend、多模型协议和性能工具 |

KServe 常作为平台层入口，底下可以接 vLLM、Triton 或自定义 runtime；不要把它和底层 engine 放在同一参数表里调。

## 与其他页面的关系

- [Kubernetes 模型服务部署](kubernetes-model-serving.md)：KServe 在整体栈中的位置。
- [Autoscaling 与 Admission Control](autoscaling-and-admission-control.md)：KServe/Knative/HPA 扩缩容原理。
- [vLLM Engine Args 参数模型](vllm-engine-parameters.md)：runtime args 的底层含义。
- [Hugging Face TEI 参数模型](huggingface-tei-parameters.md)：embedding/rerank 专用服务的参数差异。

## 关键来源

- KServe Generative Inference overview: https://kserve.github.io/website/docs/model-serving/generative-inference/overview
- KServe Text Generation task: https://kserve.github.io/website/docs/model-serving/generative-inference/tasks/text-generation
- KServe LLMInferenceService configuration: https://kserve.github.io/website/docs/model-serving/generative-inference/llmisvc/llmisvc-configuration
- KServe CRD API reference: https://kserve.github.io/website/docs/reference/crd-api
- KServe KPA autoscaler: https://kserve.github.io/website/docs/model-serving/predictive-inference/autoscaling/kpa-autoscaler
- KServe HPA autoscaler: https://kserve.github.io/website/docs/model-serving/predictive-inference/autoscaling/hpa-autoscaler
- vLLM KServe integration: https://docs.vllm.ai/en/stable/deployment/integrations/kserve/
- KServe repository: https://github.com/kserve/kserve
