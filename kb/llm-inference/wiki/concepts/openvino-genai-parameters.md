---
type: Concept
title: OpenVINO GenAI 参数模型
description: OpenVINO GenAI 面向 Intel CPU/GPU/NPU 上的生成式模型推理。它更像 SDK 参数模型：通过 `LLMPipeline`、`VLMPipeline`、`GenerationConfig`、`SchedulerConfig`
  和设备属性组合，而不是只靠一个大型 server CLI。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# OpenVINO GenAI 参数模型

OpenVINO GenAI 面向 Intel CPU/GPU/NPU 上的生成式模型推理。它更像 SDK 参数模型：通过 `LLMPipeline`、`VLMPipeline`、`GenerationConfig`、`SchedulerConfig` 和设备属性组合，而不是只靠一个大型 server CLI。

## 参数分组

| 类别 | 常用参数/API | 原理与影响 |
|---|---|---|
| pipeline | `openvino_genai.LLMPipeline(model_dir, device)`、`ov::genai::LLMPipeline` | 指定模型目录和设备，设备可为 CPU/GPU/NPU 等 |
| 生成 | `GenerationConfig.max_new_tokens`、`num_beams`、`num_beam_groups`、`diversity_penalty`、采样字段 | 控制输出长度、beam search 和多样性 |
| streaming | `streamer` / `StreamerBase` | token 级输出回调，适合交互 UI |
| chat 状态 | `start_chat()`、`finish_chat()` | 管理多轮对话状态 |
| 编译缓存 | `ov::cache_dir(...)` | GPU/VLM 等场景可缓存编译产物，降低后续启动延迟 |
| continuous batching | `SchedulerConfig.cache_size`、`num_kv_blocks`、`block_size`、`max_num_seqs`、`dynamic_split_fuse`、`enable_prefix_caching` | 管理 KV cache block、并发 sequence 数和动态 split/fuse |
| speculative decoding | `draft_model(...)`、`GenerationConfig.num_assistant_tokens`、`SchedulerConfig.cache_size` | 用 draft model 生成候选 token，主模型验证 |
| LoRA | `Adapter`、`AdapterConfig`、`adapters(...)` | 构造或生成时应用 adapter |
| 模型格式 | OpenVINO IR、GGUF preview | IR 是推荐路线；GGUF 支持仍有模型拓扑限制 |

## 关键参数原理

### `GenerationConfig.max_new_tokens`

限制单次生成的新 token 数。它不控制输入长度，但直接限制 decode 步数和响应时间。服务接口应始终设置上限。

### Beam search 参数

`num_beams` 增加搜索分支，可能提高确定性任务质量，但计算和内存近似随 beam 数上升。`num_beam_groups` 与 `diversity_penalty` 用于 grouped beam search，让不同 beam 组更分散。

### Streaming

streamer 在每个 token/subword 生成时回调，可显著改善用户感知延迟，但不会减少总计算量。它也允许自定义停止逻辑。

### Speculative decoding

OpenVINO GenAI 文档示例使用 main model + draft model：draft model 自回归预测 K 个候选，main model 验证并纠错。`num_assistant_tokens` 控制每轮 draft token 数；`SchedulerConfig.cache_size` 控制调度/cache 相关容量。

### 编译缓存

OpenVINO 在目标设备上可能需要编译模型图。设置 cache dir 可把编译结果复用到后续运行，主要优化冷启动，不改变生成算法。

### SchedulerConfig

OpenVINO GenAI 的 continuous batching 通过 scheduler 管理请求和 KV cache。`cache_size` 或 `num_kv_blocks` 决定 KV cache 容量，`block_size` 决定分页粒度，`max_num_seqs` 控制并发序列数，`enable_prefix_caching` 允许复用公共前缀，`dynamic_split_fuse` 用于动态拆分/融合请求以改善吞吐。

## 调参建议

- CPU/GPU 本地部署：先固定模型 IR 和 device，再调 generation config。
- 交互应用：使用 streamer 降低感知等待。
- 质量优先：尝试 beam search；吞吐优先则保持 greedy/sampling。
- 加速 decode：使用 draft model + `num_assistant_tokens`，但要验证接受率。
- GGUF：仅在支持拓扑内使用；正式部署优先 IR/Optimum Intel 转换路线。

## 关键来源

- OpenVINO GenAI inference docs: https://docs.openvino.ai/2025/openvino-workflow-generative/inference-with-genai.html
- OpenVINO GenAI SchedulerConfig: https://docs.openvino.ai/2025/api/genai_api/_autosummary/openvino_genai.SchedulerConfig.html
