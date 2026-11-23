---
type: Concept
title: SageMaker / DJL Serving LMI 参数模型
description: AWS SageMaker Large Model Inference (LMI) containers 是把 DJL Serving、后端推理库和
  SageMaker endpoint 约定打包起来的部署栈。它不是一个独立 kernel engine；实际推理常由 vLLM、TensorRT-LLM 或其他后端完成，LMI
  负责容器、模型加载、han...
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# SageMaker / DJL Serving LMI 参数模型

AWS SageMaker Large Model Inference (LMI) containers 是把 DJL Serving、后端推理库和 SageMaker endpoint 约定打包起来的部署栈。它不是一个独立 kernel engine；实际推理常由 vLLM、TensorRT-LLM 或其他后端完成，LMI 负责容器、模型加载、handler、队列和 SageMaker endpoint 集成。

## 配置入口

| 入口 | 作用 | 注意 |
|---|---|---|
| `serving.properties` | 每个模型的配置文件 | 多模型 endpoint 时尤其重要 |
| 环境变量 | 容器级全局配置 | `option.` 字段可转为 `OPTION_` 前缀 |
| SageMaker model artifact | `.tar.gz` 内含权重、`serving.properties`、可选 `model.py` | Python mode 下可只给 `option.model_id` |
| 自定义 handler | `model.py` 或 `option.entryPoint` | 需要自定义输入/输出 schema 时使用 |

LMI 文档建议在 `serving.properties` 和环境变量之间选择一种主要方式。两者混用时，模型配置会覆盖环境变量。

## 常用 `serving.properties`

```properties
engine=Python
option.model_id=meta-llama/Llama-...
option.revision=<commit-or-branch>
option.trust_remote_code=false
option.tensor_parallel_degree=max
option.rolling_batch=vllm
option.max_rolling_batch_size=64
option.dtype=fp16
```

## 参数分组

| 参数 | 原理与影响 |
|---|---|
| `engine` | LMI 常用 `Python` 或 `MPI`；决定 DJL Serving 如何启动推理代码 |
| `job_queue_size` | 模型服务队列长度；过大增加尾延迟，过小容易拒绝突发 |
| `option.model_id` | Hugging Face Hub id 或 S3 模型前缀；影响冷启动和供应链边界 |
| `option.revision` | 固定模型 artifact 版本；避免 Hub 上游变化导致不可复现 |
| `option.trust_remote_code` | 是否执行模型仓库自定义代码；安全边界参数 |
| `option.rolling_batch` | 选择 continuous batching 后端，如 `vllm` 或 `trtllm` |
| `option.max_rolling_batch_size` | 单模型可同时处理的最大请求/序列数；吞吐和显存的主旋钮 |
| `option.dtype` | 权重加载 dtype，如 fp16/bf16；影响显存、吞吐和硬件兼容 |
| `option.tensor_parallel_degree` | 每个模型副本跨多少 GPU 做 tensor parallel；设为 `max` 会跨可用 GPU |
| `option.entryPoint` | 内置 handler 或自定义脚本入口 |
| `option.parallel_loading` | 多 worker 并行加载；可缩短启动，但需要足够 CPU 内存 |
| `option.model_loading_timeout` | 模型加载超时时间；SageMaker 上还要匹配容器健康检查超时 |
| `option.output_formatter` | 输出格式，如 `json` 或 `jsonlines` |

DJL LMI 的简化配置还常见 `MAX_BATCH_SIZE`、`MAX_CONCURRENT_REQUESTS` 和 `TENSOR_PARALLEL_DEGREE` 等环境变量名。它们适合 SageMaker 单模型容器快速部署；多模型或复杂配置更适合显式写入 `serving.properties`。

## vLLM 后端映射

LMI 的 vLLM 支持既有 LMI 自己处理的字段，也有传给 vLLM 的透传字段。常见映射：

| LMI 字段 | vLLM 语义 |
|---|---|
| `option.tensor_parallel_degree` | tensor parallel size |
| `option.rolling_batch=vllm` | 使用 vLLM rolling/continuous batching |
| `option.max_rolling_batch_size` | 最大并发序列/请求容量 |
| `option.max_rolling_batch_prefill_tokens` | 对应 vLLM 的 `max_num_batched_tokens` 类 token budget |
| `option.quantize` | 运行时量化选项；预量化模型通常不建议显式设置 |
| `option.enable_lora` | 启用 vLLM LoRA adapter 支持 |
| `option.max_loras`、`option.max_lora_rank`、`option.max_cpu_loras` | adapter cache 和并发 adapter 预算 |

LMI 文档特别提醒：如果模型已经是 AWQ/GPTQ/FP8 等预量化格式，不要盲目设置 `option.quantize`，否则可能限制 vLLM 自动选择更优 kernel。

## SageMaker 侧注意点

| 问题 | 原因 | 建议 |
|---|---|---|
| endpoint 启动失败 | 模型加载超过健康检查窗口 | 增大 `option.model_loading_timeout` 和容器启动健康检查时间 |
| Hub 模型今天能跑明天不能跑 | 上游文件或代码变化 | 固定 `option.revision`，必要时把 artifact 放 S3 |
| 多 GPU 成本高但吞吐不升 | TP 跨卡通信或副本数不合理 | 比较 `tensor_parallel_degree=max` 与多个小副本 |
| 队列堆积 | `job_queue_size` 太大或 batch 预算不足 | 同时看队列、TTFT、显存和 max rolling batch |
| 自定义格式接入困难 | 默认 handler schema 不匹配 | 使用 LMI handler schema 或自定义 `model.py` |

## 与其他页面的关系

- [vLLM Engine Args 参数模型](vllm-engine-parameters.md)：理解后端透传字段。
- [TensorRT-LLM Serving 参数模型](tensorrt-llm-serving-parameters.md)：LMI TensorRT-LLM 容器背后的 engine。
- [Autoscaling 与 Admission Control](autoscaling-and-admission-control.md)：`job_queue_size` 和 endpoint 扩缩容的边界。
- [模型格式、加载与供应链边界](model-formats-and-loading.md)：`revision`、S3 artifact 和 remote code。
- [推理成本与效率模型](inference-cost-and-efficiency.md)：SageMaker endpoint 成本建模。

## 关键来源

- AWS SageMaker LMI container documentation: https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-container-docs.html
- AWS SageMaker deploy models with DJL Serving: https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-models-frameworks-djl-serving.html
- DJL LMI configurations: https://docs.djl.ai/master/docs/serving/serving/docs/lmi/deployment_guide/configurations.html
- DJL LMI vLLM user guide: https://docs.djl.ai/master/docs/serving/serving/docs/lmi/user_guides/vllm_user_guide.html
- DJL LMI index: https://docs.djl.ai/master/docs/serving/serving/docs/lmi/index.html
- DJL LMI starting guide: https://github.com/deepjavalibrary/djl-serving/blob/master/serving/docs/lmi/user_guides/starting-guide.md
