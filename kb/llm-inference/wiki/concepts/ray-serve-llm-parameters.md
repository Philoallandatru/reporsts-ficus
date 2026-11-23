---
type: Concept
title: Ray Serve LLM 参数模型
description: Ray Serve LLM 是把 vLLM 等推理 engine 包装成 Ray Serve 应用的在线服务层。它的核心价值不是替代 vLLM
  kernel，而是提供 Python 应用组合、replica 管理、autoscaling、Kubernetes/KubeRay 部署、OpenAI-compatible
  服务和平台级扩展。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Ray Serve LLM 参数模型

Ray Serve LLM 是把 vLLM 等推理 engine 包装成 Ray Serve 应用的在线服务层。它的核心价值不是替代 vLLM kernel，而是提供 Python 应用组合、replica 管理、autoscaling、Kubernetes/KubeRay 部署、OpenAI-compatible 服务和平台级扩展。

## 配置层次

| 层 | 代表字段 | 原理 |
|---|---|---|
| LLM 应用 | `LLMConfig` | 声明一个模型 deployment 的模型加载、engine、资源和服务参数 |
| 模型加载 | `model_loading_config` | 控制模型 id、served model name、tokenizer、revision 等 |
| Engine 透传 | `engine_kwargs` | 把 vLLM engine 参数传入底层，如上下文、dtype、并行、KV cache |
| Deployment | `deployment_config` | Ray Serve replica、autoscaling、并发和健康检查 |
| 资源 | `accelerator_type`、`accelerator_config`、`placement_group_config`、`ray_actor_options` | 控制 GPU/CPU 资源、placement group 和节点选择 |
| LoRA | `lora_config` | 控制动态 adapter 加载、每副本 adapter 上限和下载重试 |
| 可观测 | `log_engine_metrics`、`callback_config` | 控制 engine metrics 和回调 |
| 扩展 | `llm_engine`、`server_cls`、`experimental_configs` | 替换 engine/server 类或打开实验能力 |
| 应用编排 | Serve application config | 把多个 deployment、route prefix、runtime env 组合成服务 |

Ray Serve LLM 的调参要分清“Ray 层”和“engine 层”。`target_ongoing_requests` 这类参数调的是副本扩缩容；`gpu_memory_utilization`、`max_num_batched_tokens` 这类参数仍属于 vLLM。

## 常见参数

| 参数 | 原理与影响 |
|---|---|
| `model_loading_config.model_id` | 要加载的模型或 checkpoint |
| `model_loading_config.model_source` | 模型来源；可指向 Hugging Face 或内部路径 |
| `model_loading_config.tokenizer_source` | tokenizer 来源；与模型分开配置时要固定版本 |
| `engine_kwargs.tensor_parallel_size` | 单个 replica 内跨 GPU tensor parallel |
| `engine_kwargs.pipeline_parallel_size` | 单个 replica 内 pipeline parallel |
| `engine_kwargs.max_model_len` | 上下文上限和 KV cache 容量压力 |
| `engine_kwargs.gpu_memory_utilization` | vLLM 可用于 KV cache 等的 GPU 显存比例 |
| `engine_kwargs.max_num_seqs` | vLLM 单实例可调度序列数 |
| `engine_kwargs.kv_transfer_config` | 分离式服务或 KV connector 配置 |
| `deployment_config.num_replicas` | 固定 replica 数 |
| `deployment_config.autoscaling_config` | 根据 ongoing requests / queue 扩缩容 |
| `deployment_config.max_queued_requests` | Ray Serve 入口队列上限 |
| `max_ongoing_requests` | 单 replica 同时接受的请求上限 |
| `target_ongoing_requests` | autoscaling 的目标负载；越低越偏低延迟 |
| `accelerator_type` | 约束 replica 调度到指定加速器节点 |
| `lora_config.dynamic_lora_loading_path` | 动态 LoRA adapter 的加载路径 |
| `lora_config.max_num_adapters_per_replica` | 单副本最多加载多少 adapter |

字段名会随 Ray 版本演进。落地时以当前 Ray 文档和安装版本 schema 为准；知识库这里记录的是参数语义和调参位置。

Ray 文档和 vLLM Python 配置通常使用 snake_case。不要把 vLLM CLI 的 `--max-model-len` 直接写进 dict；应写成 `max_model_len`。

## Autoscaling 心智模型

Ray Serve autoscaling 观察每个 deployment 的 ongoing requests 和队列，再调整 replica 数。对 LLM 需要额外注意：

- 一个 replica 里可能有 vLLM 自己的 continuous batching 队列。
- Ray 的 ongoing request 不等于 GPU 内部活跃 token 数。
- 扩出新 replica 后仍有模型下载、加载、warmup 和 CUDA graph capture。
- `max_ongoing_requests` 太大时，单个 replica 会吃下过多请求，tail latency 可能变差。

因此，Ray Serve LLM 适合把平台层扩缩容和 engine metrics 一起看：Ray 看 replica/queue，vLLM 看 waiting requests、TTFT、TPOT、KV cache 和 batch token。

## 适用场景

| 场景 | 判断 |
|---|---|
| Python 服务里组合 RAG、工具、多个模型 deployment | 很合适 |
| KubeRay 上运行多模型在线服务 | 很合适 |
| 只想单机跑一个 vLLM OpenAI server | 可能直接用 vLLM 更简单 |
| 极致单实例 kernel 调优 | 主要看底层 vLLM/SGLang/TensorRT-LLM |
| 离线批量推理 | Ray Data LLM 更合适 |

## 常见误调

| 误调 | 后果 | 修正 |
|---|---|---|
| 只调 Ray replica，不调 engine batch/KV | 副本变多但单副本仍低效 | 结合 vLLM engine args 调优 |
| `target_ongoing_requests` 太高 | 请求堆在单副本，p99 上升 | 降低 target，增加 replica，设置 max queue |
| 新副本立即接流量 | 冷启动请求很慢 | readiness 后做模型 warmup |
| 每个 replica 申请 GPU 不明确 | 调度到错误节点或资源争用 | 明确 accelerator / actor GPU 资源 |
| Ray Data 和 Ray Serve 参数混用 | 在线延迟和离线吞吐都不理想 | 在线用 Serve，离线用 Data LLM |
| `log_engine_metrics=True` 同时关闭 vLLM stats | 配置被拒绝或 metrics 缺失 | 不要在 `engine_kwargs` 中设置冲突的 `disable_log_stats` |
| 继续引用旧文档 URL | 配置字段过时 | 使用当前 `serve/llm/index.html` 和 configuration reference |
| 使用旧实验字段名 | 配置不生效 | 以当前 schema 为准，例如 ingress/router 实验字段会变更 |

## 与其他页面的关系

- [Kubernetes 模型服务部署](kubernetes-model-serving.md)：Ray Serve 在 KubeRay 上的部署位置。
- [Autoscaling 与 Admission Control](autoscaling-and-admission-control.md)：Ray Serve 扩缩容参数的原理。
- [vLLM Engine Args 参数模型](vllm-engine-parameters.md)：`engine_kwargs` 的主要落点。
- [离线推理与批量推理](offline-and-batch-inference.md)：Ray Data LLM 与在线 Serve 的边界。

## 关键来源

- Ray Serve LLM overview: https://docs.ray.io/en/latest/serve/llm/index.html
- Ray Serve LLM configuration: https://docs.ray.io/en/latest/serve/llm/user-guides/configuration.html
- Ray Serve LLMConfig API: https://docs.ray.io/en/latest/serve/api/doc/ray.serve.llm.LLMConfig.html
- Ray Serve vLLM compatibility: https://docs.ray.io/en/latest/serve/llm/user-guides/vllm-compatibility.html
- Ray Serve autoscaling guide: https://docs.ray.io/en/latest/serve/autoscaling-guide.html
- Ray Serve advanced autoscaling: https://docs.ray.io/en/latest/serve/advanced-guides/advanced-autoscaling.html
- Ray Serve prefix-aware routing: https://docs.ray.io/en/latest/serve/llm/user-guides/prefix-aware-routing.html
- Ray LLMConfig source: https://github.com/ray-project/ray/blob/master/python/ray/llm/_internal/serve/core/configs/llm_config.py
