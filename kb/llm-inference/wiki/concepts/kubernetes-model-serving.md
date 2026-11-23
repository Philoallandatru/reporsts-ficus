---
type: Concept
title: Kubernetes 模型服务部署
description: Kubernetes 层不直接提升单 token 速度，但决定模型服务能否被可靠调度、扩缩容、滚动发布、缓存权重、暴露 GPU 和观测。vLLM、TGI、TensorRT-LLM、Triton、KServe、Ray
  Serve 解决的是不同层的问题，混在一起看很容易误调。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Kubernetes 模型服务部署

Kubernetes 层不直接提升单 token 速度，但决定模型服务能否被可靠调度、扩缩容、滚动发布、缓存权重、暴露 GPU 和观测。vLLM、TGI、TensorRT-LLM、Triton、KServe、Ray Serve 解决的是不同层的问题，混在一起看很容易误调。

## 栈分层

| 层 | 代表 | 主要职责 |
|---|---|---|
| Engine | vLLM、SGLang、TGI、TensorRT-LLM、llama.cpp | 加载模型、KV cache、batching、decode |
| Model server | Triton、TGI server、vLLM OpenAI server | 协议、模型进程、metrics |
| Platform / operator | KServe、Ray Serve on KubeRay、BentoML | 部署、autoscaling、rollout、runtime abstraction |
| Gateway | LiteLLM、Envoy AI Gateway、API Gateway | 鉴权、路由、fallback、budget、rate limit |
| Cluster substrate | Kubernetes、GPU Operator、device plugin | 调度、GPU 资源、网络、存储 |

KServe 不替代 vLLM；Ray Serve 也不替代 GPU kernel。它们负责把 engine 变成可运营的 Kubernetes 服务。

## KServe

KServe 通过 `InferenceService`、`ServingRuntime` 或 LLM 相关 runtime 把模型部署成 Kubernetes-native 服务。它适合多团队、多模型、需要流量管理/自动扩缩容的平台场景。

关注点：

- runtime 选择：Hugging Face serving runtime、vLLM integration、Triton runtime 等。
- GPU 资源：`resources.limits.nvidia.com/gpu`、node selector、tolerations。
- 权重来源：PVC、对象存储、Hugging Face token、storage initializer。
- autoscaling：Knative/KServe/HPA/自定义指标。
- 多模型版本：canary、rollout、traffic split。

KServe 的 Hugging Face generative runtime 使用 vLLM backend，支持 OpenAI-compatible endpoint，并覆盖 text generation、embedding、rerank 等任务。vLLM 官方也给出 KServe 集成入口。

## Ray Serve / KubeRay

Ray Serve 适合 Python 业务逻辑、多个 deployment 组合、LLM replica 管理和 autoscaling。KubeRay 提供 `RayCluster`、`RayService` 等 Kubernetes CRD。

典型参数：

| 参数/概念 | 作用 |
|---|---|
| `num_replicas` / autoscaling config | 控制 deployment replica 数 |
| `max_ongoing_requests` | 单 replica 同时处理请求上限 |
| `target_ongoing_requests` | autoscaling 目标负载 |
| `ray_actor_options.num_gpus` | 每个 replica 申请 GPU |
| RayService | 生产 Ray 服务部署和滚动更新 |
| Serve application config | 声明 deployment graph、routes、runtime_env |

Ray Serve LLM 更偏在线服务；Ray Data LLM 更偏离线批量推理。不要把两个场景的 batch/concurrency 参数混用。

## BentoML

BentoML 适合把模型服务打包成可部署 artifact，提供 API server、service 抽象和容器化工作流。它常用于平台团队把模型推理服务标准化；具体 LLM engine 仍需要根据 vLLM/TGI/Transformers 等后端选择。BentoML 文档中的 vLLM 示例更偏“用 BentoML 包装 vLLM 服务”，OpenLLM 则是 BentoML 生态中的自托管 OpenAI-compatible API 项目。

关注点：

- service 入口和 API schema。
- model artifact 与容器构建。
- GPU 资源声明。
- autoscaling/部署目标与 BentoCloud 或 Kubernetes 集成。

## 权重存储与冷启动

LLM 权重很大，Kubernetes 部署常见慢点不是 engine，而是拉权重：

- 从 Hugging Face 或对象存储下载慢。
- storage initializer 内存/临时盘不够。
- scale-to-zero 后重新下载。
- 多副本同时拉同一大模型造成网络/磁盘风暴。

生产常用：

- PVC 或本地 NVMe 缓存。
- 镜像内置小模型或 tokenizer。
- 节点亲和性绑定有缓存的节点。
- 预热 pod 和滚动发布。

## 调参判断

| 症状 | 可能原因 | 优先动作 |
|---|---|---|
| Pod 启动很慢 | 权重下载/解压/转换 | PVC、本地缓存、预热、增大临时盘 |
| HPA 扩了但吞吐不升 | GPU/模型副本没真正增加，或共享同一瓶颈 | 检查 GPU limits、node capacity、gateway routing |
| scale down 后下一次 TTFT 很高 | 冷启动和权重重新加载 | 保留 min replicas、预热、权重缓存 |
| 多版本发布质量波动 | traffic split 后模型 revision/template 不一致 | 固定 revision、模板、采样默认值 |
| 单 pod 多 GPU 不工作 | NCCL、host network、device plugin 或容器权限问题 | 检查通信和 GPU 可见性 |

## 与其他页面的关系

- [GPU 拓扑、隔离与集群资源](gpu-topology-and-isolation.md)：解释 Pod 里的 GPU 为什么这样出现。
- [NVIDIA Triton Inference Server LLM 参数模型](triton-inference-server-llm-parameters.md)：Triton 是模型服务器，可作为 KServe runtime。
- [LLM 网关与路由层参数](llm-gateway-routing-parameters.md)：网关处理跨 deployment 路由和配额。
- [生产服务与运维控制面](production-serving-operations.md)：Kubernetes 是控制面落地环境。

## 关键来源

- KServe Generative Inference runtime overview: https://kserve.github.io/website/docs/model-serving/generative-inference/overview
- vLLM KServe integration: https://docs.vllm.ai/en/stable/deployment/integrations/kserve/
- Ray Serve LLM: https://docs.ray.io/en/latest/serve/llm/index.html
- Ray Serve autoscaling: https://docs.ray.io/en/latest/serve/advanced-guides/advanced-autoscaling.html
- Ray Serve autoscaling guide: https://docs.ray.io/en/latest/serve/autoscaling-guide.html
- KubeRay RayService: https://docs.ray.io/en/latest/cluster/kubernetes/user-guides/rayservice.html
- KubeRay autoscaling: https://docs.ray.io/en/latest/cluster/kubernetes/user-guides/configuring-autoscaling.html
- Ray on Kubernetes: https://docs.ray.io/en/latest/cluster/kubernetes/index.html
- BentoML LLM: https://docs.bentoml.com/en/latest/build-with-bentoml/llm.html
- BentoML vLLM example: https://docs.bentoml.com/en/latest/examples/vllm.html
- OpenLLM GitHub: https://github.com/bentoml/OpenLLM
- NVIDIA Kubernetes Device Plugin: https://github.com/NVIDIA/k8s-device-plugin
- NVIDIA GPU Operator: https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/
