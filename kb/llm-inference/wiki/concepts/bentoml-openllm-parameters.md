---
type: Concept
title: BentoML / OpenLLM 参数模型
description: BentoML 是模型服务打包和部署框架，OpenLLM 是 BentoML 生态中的自托管 LLM serving 项目。它们不直接定义新的
  attention kernel；真正的 LLM 计算通常由 vLLM、Transformers、PyTorch、TGI 或其他后端完成。BentoML 负责把后端包装成
  service、API、容器、部署 a...
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# BentoML / OpenLLM 参数模型

BentoML 是模型服务打包和部署框架，OpenLLM 是 BentoML 生态中的自托管 LLM serving 项目。它们不直接定义新的 attention kernel；真正的 LLM 计算通常由 vLLM、Transformers、PyTorch、TGI 或其他后端完成。BentoML 负责把后端包装成 service、API、容器、部署 artifact 和云端/集群运行单元。

## 配置层次

| 层 | 代表配置 | 原理 |
|---|---|---|
| Service | `@bentoml.service(...)` | 声明服务、资源、traffic、worker 等运行属性 |
| API | `@bentoml.api` | 声明 HTTP API、输入输出和 streaming |
| 资源 | `resources={...}` | 声明 CPU、内存、GPU 等资源需求 |
| Traffic | `traffic={...}` | 设置超时、并发/请求处理边界 |
| Worker | `workers` | 控制服务副本内 worker 数；LLM GPU 服务通常要谨慎 |
| BentoVLLM 参数 | `BentoArgs`、`bentoml.use_arguments()` | 用模板参数批量生成/部署 vLLM Bento |
| Engine | vLLM engine args / Transformers config | 底层模型加载、KV cache、batch、采样和并行参数 |
| Deployment | BentoCloud / Kubernetes config | 云端资源、autoscaling、secret、volume、endpoint |

BentoML 的参数面分两层：BentoML 控制“服务怎么被运行”，vLLM 等 engine 控制“token 怎么被生成”。调优时要先定位问题属于哪一层。

## 常见参数

| 参数/字段 | 原理与影响 |
|---|---|
| `resources.gpu` | 服务需要的 GPU 数或 GPU 类型；影响调度和成本 |
| `resources.gpu_type` | 约束 GPU 型号；要匹配 CUDA/ROCm 镜像和模型 profile |
| `resources.cpu` / memory | tokenization、预处理、后处理、API 层开销 |
| `traffic.timeout` | 单请求超时；过短会截断长输出，过长会掩盖排队问题 |
| `endpoints.readyz` | readiness endpoint；可避免模型未加载完就接流量 |
| `image` | 服务镜像和系统依赖；影响 CUDA、FlashAttention、vLLM 版本 |
| `envs` | 注入 HF token、backend 环境变量和 engine 配置 |
| `workers` | 多 worker 可提升 CPU/API 并发，但 GPU LLM 中可能导致多进程争抢同一 GPU |
| service import path | 部署 artifact 的入口；决定容器如何加载服务 |
| secrets/env | Hugging Face token、API key、模型私有凭据 |
| model volume/cache | 权重缓存位置；影响冷启动 |
| vLLM args | `model`、`max_model_len`、`gpu_memory_utilization`、`tensor_parallel_size` 等 |
| OpenAI-compatible API | 让客户端按 OpenAI SDK 请求服务，但语义仍由后端和模板决定 |

## vLLM in BentoML

BentoML 官方 vLLM 示例展示的是“用 BentoML 管服务，用 vLLM 管推理”。典型结构：

1. BentoML service 初始化 vLLM engine。
2. API endpoint 接收 OpenAI 风格或自定义请求。
3. vLLM engine 处理 batching、KV cache、采样和 streaming。
4. BentoML/BentoCloud 负责容器、资源和部署。

这意味着 vLLM 的性能参数仍然按 [vLLM Engine Args 参数模型](vllm-engine-parameters.md) 理解；BentoML 只是在外层决定资源、超时、worker、镜像和 endpoint。

官方 BentoVLLM 模板还引入了参数化 Bento 的写法，常见字段包括：

| 字段 | 作用 |
|---|---|
| `name` | Bento/service 名称 |
| `model_id` | Hugging Face 或本地模型 id |
| `gpu_type` | 目标 GPU 类型 |
| `tp` / `dp` | tensor parallel / data parallel 规模 |
| `port` | 服务监听端口 |
| `max_model_len` | 上下文上限，直接影响 KV cache |
| `kv_cache_dtype` | KV cache 精度 |
| `kv_transfer_config` | KV transfer / disaggregated serving 相关配置 |
| `reasoning_parser` / `tool_parser` | reasoning/tool call parser |
| `cli_args` | 追加传给 vLLM CLI 的参数 |
| `envs` | 追加环境变量 |
| `hf_generation_config` | Hugging Face generation config |

## OpenLLM 定位

OpenLLM 是 BentoML 生态中的自托管 OpenAI-compatible API 项目，适合快速把开源模型变成 API 服务。它更像“模型仓库 + BentoML Bento + OpenAI-compatible API”的封装，而不是一个独立 kernel backend。对高吞吐、长上下文、LoRA、多 GPU 等细节，仍要看其底层 backend 和版本支持。

常见 CLI 语义：

| 参数 | 作用 |
|---|---|
| `openllm serve <model:version>` | 选择模型仓库中的 Bento 并启动 |
| `--repo` | 指向模型/Bento 仓库 |
| `--port` | 服务端口 |
| `--env NAME` / `--env NAME=value` | 注入环境变量 |
| `--arg key=value` | 把参数转交给 BentoML 模板参数 |
| `openllm deploy --instance-type` | 部署时选择实例类型 |
| `openllm deploy --context` | 部署上下文 |

## 常见误调

| 误调 | 后果 | 修正 |
|---|---|---|
| 把 BentoML worker 当成 vLLM batch | 多 worker 抢 GPU，显存翻倍或吞吐下降 | GPU LLM 先用单 worker + engine batching 验证 |
| 只调 `traffic.timeout` | 超时少了但用户等更久 | 同时看 engine queue、TTFT、TPOT |
| service 层资源声明过小 | 容器能启动但 tokenization/预处理慢 | 给 API 层足够 CPU/内存 |
| 没有权重缓存 | 每次部署/扩容都慢 | 配置 volume/cache，预热模型 |
| OpenAI API 返回成功但输出漂移 | chat template/sampling/backend 不一致 | 固定模型 revision、template 和采样参数 |
| `tp` 和 GPU 数不一致 | 进程启动失败或跨卡效率很差 | 让 `tp`、`dp`、GPU 数和拓扑匹配 |
| 只写模型名不写版本 | OpenLLM 可能匹配到非预期 Bento | 固定 `<model:version>` 或 repo revision |
| gated 模型缺少 token | 权重下载失败 | 通过 env/secret 注入 `HF_TOKEN` |

## 与其他页面的关系

- [vLLM Engine Args 参数模型](vllm-engine-parameters.md)：BentoML vLLM service 的底层 engine。
- [Kubernetes 模型服务部署](kubernetes-model-serving.md)：BentoML 在平台部署层的位置。
- [OpenAI-compatible API 语义与兼容边界](openai-compatible-api-semantics.md)：OpenLLM/BentoML API 兼容不等于语义一致。
- [Autoscaling 与 Admission Control](autoscaling-and-admission-control.md)：BentoCloud/Kubernetes autoscaling 需要结合 engine 指标。

## 关键来源

- BentoML LLM guide: https://docs.bentoml.com/en/latest/build-with-bentoml/llm.html
- BentoML services: https://docs.bentoml.com/en/latest/build-with-bentoml/services.html
- BentoML vLLM example: https://docs.bentoml.com/en/latest/examples/vllm.html
- BentoVLLM service.py: https://raw.githubusercontent.com/bentoml/BentoVLLM/main/llama3.1-8b-instruct/service.py
- OpenLLM repository: https://github.com/bentoml/OpenLLM
- OpenLLM CLI source: https://raw.githubusercontent.com/bentoml/OpenLLM/main/src/openllm/__main__.py
