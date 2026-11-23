---
type: Concept
title: Google TPU 与 JetStream 推理
description: TPU 推理和 GPU 推理的参数模型不同：TPU 通常以 slice、mesh、编译图、PJRT/XLA、batch 和 decode
  pipeline 为核心。Google 的 JetStream / MaxText / vLLM TPU 路线把 LLM serving 映射到 TPU v5e/v6e
  等硬件上。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Google TPU 与 JetStream 推理

TPU 推理和 GPU 推理的参数模型不同：TPU 通常以 slice、mesh、编译图、PJRT/XLA、batch 和 decode pipeline 为核心。Google 的 JetStream / MaxText / vLLM TPU 路线把 LLM serving 映射到 TPU v5e/v6e 等硬件上。

## 路线对照

| 路线 | 作用 |
|---|---|
| Cloud TPU inference docs | Google Cloud 上运行推理的基础入口 |
| vLLM TPU | vLLM 团队维护的 TPU inference 集成 |
| GKE + vLLM TPU | Kubernetes 上部署 vLLM TPU serving |
| JetStream | 面向 TPU 的 LLM serving engine / serving stack；更多作为架构和历史参考 |
| MaxText | JAX/TPU 上的 LLM 训练和推理参考实现 |
| jetstream-pytorch | PyTorch/XLA 相关 JetStream 路线 |

## TPU 推理关注点

| 参数/概念 | 原理与影响 |
|---|---|
| TPU type / slice | 决定总算力、HBM 和互连 |
| mesh / sharding | 模型参数、KV 和 batch 如何跨芯片切分 |
| batch size | 决定吞吐和编译 shape |
| max sequence / context | 决定 KV cache 和 XLA 编译形状 |
| prefill/decode split | 长 prompt 和 decode 阶段资源形态不同 |
| XLA compile cache | 编译耗时和冷启动关键 |
| serving framework | vLLM TPU、JetStream、MaxText serving 路线不同 |

TPU 上的“改一个参数”经常意味着新的编译 shape 或不同 sharding，因此压测要把编译时间、warmup 和 steady-state 分开记录。

## vLLM TPU

vLLM TPU 目标是让 vLLM 语义跑在 TPU 后端上。要注意：

- 支持模型、dtype、batch/context 上限以 TPU 项目文档为准。
- TPU 环境安装和 vLLM GPU 安装不同。
- 部署在 GKE 时还要配置 TPU node pool、资源请求和服务暴露。

## JetStream / MaxText

JetStream 是 Google/AI Hypercomputer 生态里的 TPU LLM serving 组件；MaxText 提供 JAX/TPU 参考模型和推理路径。它们适合：

- TPU 专用部署。
- 需要 TPU slice/mesh 管理。
- 已经在 JAX/TPU 生态内训练或服务模型。

Google GKE 文档和 JetStream 仓库都提示新部署更应优先看 vLLM TPU / `tpu-inference` 路线；JetStream 仍适合作为 continuous batching、KV cache optimization、multi-host TPU serving 和 Pathways runtime 架构参考。

## 调参判断

| 症状 | 优先检查 |
|---|---|
| 首次请求慢 | XLA compile / graph warmup 是否完成 |
| batch 改动后变慢或重编译 | shape 是否触发重新编译 |
| TPU 利用率低 | batch、sharding、host input pipeline 是否匹配 |
| 长上下文 OOM | KV cache、context length、mesh 切分 |
| GKE 部署不稳定 | TPU node pool、pod resource、driver/runtime、服务 readiness |

## 与其他页面的关系

- [图编译与 Engine 构建优化](graph-compilation-and-engine-build.md)：TPU/XLA 是典型图编译路径。
- [Kubernetes 模型服务部署](kubernetes-model-serving.md)：GKE + TPU 部署属于平台层。
- [推理负载建模与压测数据集](workload-modeling-and-load-testing.md)：TPU 压测要区分编译和 steady-state。

## 关键来源

- Google Cloud TPU inference: https://docs.cloud.google.com/tpu/docs/tpu-inference
- vLLM TPU docs: https://docs.vllm.ai/projects/tpu/en/latest/
- vLLM TPU installation: https://docs.vllm.ai/en/v0.11.0/getting_started/installation/google_tpu.html
- vLLM TPU inference GitHub: https://github.com/vllm-project/tpu-inference
- vLLM TPU quickstart: https://github.com/vllm-project/tpu-inference/blob/main/docs/getting_started/quickstart.md
- Serve vLLM on TPU in GKE: https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-vllm-tpu
- Serve multi-host TPU with JetStream on GKE: https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-multihost-tpu-jetstream
- Serve LLM with JetStream PyTorch on GKE: https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-llm-tpu-jetstream-pytorch
- Serve Gemma with JetStream on TPU: https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-gemma-tpu-jetstream
- JetStream GitHub: https://github.com/AI-Hypercomputer/JetStream
- jetstream-pytorch GitHub: https://github.com/AI-Hypercomputer/jetstream-pytorch
- JetStream PyTorch benchmark summary: https://github.com/google/jetstream-pytorch/blob/main/benchmarks/summary.md
- MaxText GitHub: https://github.com/AI-Hypercomputer/maxtext
- MaxText architecture overview: https://maxtext.readthedocs.io/en/latest/reference/architecture/architecture_overview.html
- Google Cloud AI Hypercomputer inference update: https://cloud.google.com/blog/products/compute/ai-hypercomputer-inference-updates-for-google-cloud-tpu-and-gpu
