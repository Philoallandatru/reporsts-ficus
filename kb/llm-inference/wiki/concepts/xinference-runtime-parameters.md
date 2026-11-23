---
type: Concept
title: Xinference 参数模型
description: Xinference 是一个多模型推理平台，把 LLM、embedding、rerank、图像、语音等模型统一成本地或集群服务。它的重点不是发明新的
  kernel，而是把 `transformers`、vLLM、SGLang、llama.cpp 等 backend 包装成 supervisor/worker
  管理、Web UI、REST API、Ope...
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Xinference 参数模型

Xinference 是一个多模型推理平台，把 LLM、embedding、rerank、图像、语音等模型统一成本地或集群服务。它的重点不是发明新的 kernel，而是把 `transformers`、vLLM、SGLang、llama.cpp 等 backend 包装成 supervisor/worker 管理、Web UI、REST API、OpenAI-compatible API 和模型生命周期控制。

## 参数面

| 参数面 | 常见字段 / 命令 | 作用 |
|---|---|---|
| 服务进程 | `xinference-local`、`xinference-supervisor`、`xinference-worker`、`-H/--host`、endpoint | 决定单机还是 supervisor/worker 集群，以及 API/UI 入口 |
| 模型启动 | `xinference launch`、`Client.launch_model`、`model_name`、`model_uid`、`model_type`、`model_size_in_billions`、`model_engine`、`model_format`、`quantization`、`model_path` | 定义要启动哪个模型、以哪个 backend 和 artifact 形态运行 |
| GPU 放置 | `n_gpu`、`gpu_idx`、`worker_ip`、`replica_config` | 把模型实例或每个 replica 放到指定 worker/GPU |
| Replica | `replica`、`add_model_replica`、`terminate_model_replica`、`XINFERENCE_ALLOW_MULTI_REPLICA_PER_GPU` | 同一模型启动多个实例，提升并发和可用性 |
| 请求限流 | `request_limits` | 给单个模型入口设置请求限制，避免一个模型拖垮整个 worker |
| Backend 参数 | vLLM / SGLang / llama.cpp / transformers 的透传参数、`--env`、backend-specific kwargs | 决定真实推理 engine 的显存、batch、KV cache 和并行策略 |
| 批处理 | `XINFERENCE_BATCH_SIZE`、`XINFERENCE_BATCH_INTERVAL`、backend continuous batching | 控制部分 backend 的请求合批和吞吐延迟权衡 |
| Reasoning | `--enable-thinking` | 对支持 thinking mode 的模型启用 reasoning 输出路径 |
| API 兼容 | OpenAI-compatible chat/completions/embeddings、原生 REST、Web UI | 让现有 OpenAI SDK 或平台调用模型 |
| Embedding / rerank | `model_type="embedding"`、`model_type="rerank"`、`/v1/embeddings`、`/v1/rerank` | embedding 与 rerank 是独立能力，不应混进 LLM 生成参数 |
| 模型缓存 / 注册 | `register_model`、`unregister_model`、`list_model_registrations`、`list_cached_models`、`confirm_and_remove_model`、cached/remove-cache | 区分模型定义、模型文件缓存和运行中模型 |

## 层次：Xinference 参数不等于 engine 参数

Xinference 调的是“平台层 + 模型元数据层 + backend 层”三套参数：

- 平台层：supervisor、worker、model UID、replica、worker/GPU 放置、模型缓存、API 入口。
- 模型元数据层：`model_name`、`model_type`、`model_format`、`quantization`、size、model path、custom registration。
- Backend 层：vLLM 的 KV cache 与 batch 参数、SGLang 的 scheduler 参数、llama.cpp 的 `n_ctx` / `n_gpu_layers` / `n_batch`，或 transformers 的 dtype/device/generation 参数。

因此，`model_engine="vllm"` 并不会让 Xinference 的所有字段都变成 vLLM 字段。先判断当前模型由哪个 backend 执行，再回到对应框架页看真实计算参数。

## Replica 与 GPU 放置

`replica` 表示同一模型启动多个实例。多卡时，一个常见部署是每张 GPU 一个 replica；显存足够时，也可以允许单 GPU 多 replica。Xinference 文档还提供 `replica_config`，用来把每个 replica 固定到指定 worker 和 GPU。

这类参数的原理是用更多模型副本换取更高请求并发。它不会降低单个请求的 decode 成本，也不会共享每个 replica 的 KV cache。副本越多，权重、KV cache、runtime buffer 的总显存占用越高。

`replica_config` 用于精确放置每个副本。它和模型级 `worker_ip`、`n_gpu`、`gpu_idx` 是互斥思路：前者逐副本声明位置，后者让调度器按模型级约束选择。两套混用容易让实际放置不可解释。

## Backend 选择

| Backend | 适合场景 | 主要继续查看 |
|---|---|---|
| vLLM | 高吞吐在线服务、PagedAttention、continuous batching、prefix cache | [vLLM Engine Args 参数模型](vllm-engine-parameters.md) |
| SGLang | 结构化生成、RadixAttention、长上下文、复杂服务策略 | [SGLang Server Arguments 参数模型](sglang-server-parameters.md) |
| llama.cpp | GGUF、本地 CPU/GPU offload、轻量服务 | [llama.cpp 参数模型](llama-cpp-runtime-parameters.md) |
| transformers | 兼容 Hugging Face 模型和普通 PyTorch 生成路径 | [Transformers Generation 参数模型](huggingface-transformers-generation-parameters.md) |

## 常见误调风险

| 风险 | 表现 | 处理 |
|---|---|---|
| 把 replica 当作 tensor parallel | 显存翻倍但单请求没有变快 | 需要分片大模型时看 backend 的 TP/PP 参数 |
| 每 GPU 多 replica 过多 | TTFT 上升、OOM、GPU 利用率抖动 | 先按每卡 1 replica 压测，再逐步增加 |
| `model_uid` / alias 不稳定 | 客户端请求打到不同 revision、quant 或模板 | 为生产模型固定 UID、revision、format、quantization |
| backend 参数透传错层 | 参数被忽略，或启动成功但性能不变 | 查 `model_engine`，再用对应 backend 官方参数核对 |
| worker/GPU 放置错误 | 模型跑到错误节点、跨节点冷启动、负载不均 | 使用 `replica_config` 明确 worker 和 `gpu_idx` |
| `request_limits` 太松或太紧 | 单模型压垮 worker，或吞吐被人为压低 | 按 TTFT、TPOT、queue time 和错误率调限 |
| 混淆注册与缓存 | 删除 cache 后模型定义仍存在，或注销后权重仍占磁盘 | 分别审计 model registration、cached model 和 running model |
| rerank/embedding 参数混用 | rerank 结果数量、文档返回字段和 embedding batch 搞混 | 按 `model_type` 分开记录 API 字段 |
| 只看 OpenAI-compatible API | chat template、tool、usage、streaming 语义和 OpenAI 不完全一致 | 用目标客户端做兼容性回归 |

## 调参路径

1. 先选择 `model_engine`，确定底层 engine 的能力边界。
2. 固定 `model_uid`、模型格式、量化和 revision，避免请求语义漂移。
3. 单 replica 跑通后，再增加 `replica`，观察 GPU 显存、TTFT、TPOT 和排队时间。
4. 多 worker 集群用 `replica_config` 固定关键模型的位置，避免调度器把大模型放到不合适的卡。
5. 给高成本模型配置 `request_limits`，把入口背压放在模型层而不是等 worker 被打满。
6. 若是 vLLM/SGLang backend，把 KV cache、batch token、prefix cache、并行参数放到 backend 层调。

## 相关页面

- [vLLM Engine Args 参数模型](vllm-engine-parameters.md)
- [SGLang Server Arguments 参数模型](sglang-server-parameters.md)
- [llama.cpp 参数模型](llama-cpp-runtime-parameters.md)
- [模型生命周期、热切换与保活](model-lifecycle-hot-swap-and-keepalive.md)
- [跨框架参数对照表](cross-framework-parameter-map.md)

## 关键来源

- Xinference documentation: https://inference.readthedocs.io/en/latest/
- Xinference getting started: https://inference.readthedocs.io/en/latest/getting_started/using_xinference.html
- Xinference model launching: https://inference.readthedocs.io/en/latest/user_guide/launch.html
- Xinference backends: https://inference.readthedocs.io/en/latest/user_guide/backends.html
- Xinference client API: https://inference.readthedocs.io/en/latest/user_guide/client_api.html
- Xinference custom models: https://inference.readthedocs.io/en/latest/models/custom.html
- Xinference rerank models: https://inference.readthedocs.io/en/latest/models/model_abilities/rerank.html
- Xinference GitHub: https://github.com/xorbitsai/inference
- Xinference REST client source: https://github.com/xorbitsai/inference/blob/main/xinference/client/restful/restful_client.py
