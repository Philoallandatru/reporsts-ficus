---
type: Concept
title: 推理量化：权重、激活与 KV cache
description: 推理量化的目标是用更少 bit 表示权重、激活或 KV cache，从而降低显存/内存、提高吞吐或让更大模型能部署。它不是单一技术，而是一组不同位置、不同风险的压缩方法。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 推理量化：权重、激活与 KV cache

推理量化的目标是用更少 bit 表示权重、激活或 KV cache，从而降低显存/内存、提高吞吐或让更大模型能部署。它不是单一技术，而是一组不同位置、不同风险的压缩方法。

## 三类量化对象

| 对象 | 节省什么 | 风险 |
|---|---|---|
| 权重量化 | 模型权重显存、加载带宽 | 精度下降、kernel 不成熟时可能不快 |
| 激活量化 | 中间 activation 内存和算子带宽 | 对校准和 kernel 支持更敏感 |
| KV cache 量化 | 长上下文和并发显存 | 长文本、注意力分数、value 聚合质量风险 |

## 常见格式/方法

| 方法 | 常见框架 | 说明 |
|---|---|---|
| GGUF `Q4_K_M` / `Q5_K_M` / `Q8_0` 等 | llama.cpp / Ollama | 面向本地推理的模型文件和量化类型 |
| AWQ | vLLM / TGI / TensorRT-LLM / LMDeploy | 权重量化，强调激活感知的权重保护 |
| GPTQ | vLLM / TGI / TensorRT-LLM | 后训练权重量化，常见 4-bit 部署 |
| bitsandbytes | Transformers / vLLM / TGI | 8-bit/4-bit 加载与推理，生态覆盖广 |
| FP8 / NVFP4 | vLLM / TGI / TensorRT-LLM / SGLang | 新硬件上常见，依赖硬件和 kernel 支持 |
| KV cache FP8/int8/q4 | vLLM / llama.cpp / TGI / TensorRT-LLM / SGLang | 主要服务长上下文和高并发 |

## 方法差异

- AWQ 是 activation-aware weight-only quantization：离线观察 activation，把少量重要权重通道保护起来，再量化大部分权重。
- GPTQ 是 one-shot post-training quantization：用近似二阶信息逐层压缩权重，常见于 4-bit/3-bit 模型发布。
- bitsandbytes `LLM.int8()` 的核心是 outlier-aware：大多数矩阵乘走 8-bit，异常维度保留更高精度路径。
- GGUF 不是单个量化算法，而是 llama.cpp 生态的模型容器和张量格式，可承载多种量化类型。

## 为什么 4-bit 不一定更快

量化降低了内存量，但推理速度还取决于：

- 是否有高质量低精度 matmul kernel。
- 是否需要频繁反量化。
- batch size 和 sequence length 是否能吃满 kernel。
- GPU 是否原生支持该 dtype。
- 通信是否成为多 GPU 瓶颈。

因此“能跑更大模型”和“每 token 更快”是两个不同目标。

## KV cache 量化的特殊性

权重量化影响所有请求，KV cache 量化的收益随上下文和并发放大。短 prompt、低并发时，它可能收益不明显；长上下文、多用户服务时，它常是决定能否跑起来的关键。

风险：

- 低精度 K 可能影响 attention score。
- 低精度 V 可能影响上下文信息聚合。
- FP8 KV cache 往往需要 scaling factor；scale 不匹配会明显损伤质量。

## 选择路线

| 目标 | 优先选择 |
|---|---|
| 单卡装下更大模型 | 权重量化：AWQ/GPTQ/GGUF |
| 长上下文 OOM | KV cache 低精度 + 降上下文或并发 |
| 生产吞吐 | 框架原生推荐量化 + 官方 benchmark |
| 质量敏感 | bf16/fp16 权重，先不量化 KV cache |
| 本地 CPU/GPU 混合 | GGUF 量化类型和 llama.cpp/Ollama 参数 |

## 验证方法

- 用目标任务而不是通用困惑度单独判断。
- 分别评估短文本、长文本、多轮对话和结构化输出。
- 固定 seed、模型 revision、tokenizer、prompt template。
- 记录 TTFT、TPOT、吞吐、拒绝率和质量指标。

## 相关页面

- [模型转换、量化与校准流水线](model-conversion-quantization-pipeline.md)
- [GGUF 转换与 llama.cpp 量化工具链](gguf-conversion-and-llama-quantize.md)
- [AWQ、GPTQ 与 FP8 量化工具链](awq-gptq-fp8-quantization-toolchain.md)
- [模型格式、加载与供应链边界](model-formats-and-loading.md)

## 关键来源

- vLLM Quantization: https://docs.vllm.ai/en/stable/features/quantization/
- TGI launcher quantization options: https://huggingface.co/docs/text-generation-inference/reference/launcher
- TensorRT-LLM Quantization: https://nvidia.github.io/TensorRT-LLM/features/quantization.html
- llama.cpp server README: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- llama.cpp quantize README: https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md
- Hugging Face GGUF docs: https://huggingface.co/docs/hub/en/gguf
- LMDeploy TurboMind config: https://lmdeploy.readthedocs.io/en/latest/inference/turbomind_config.html
- AWQ paper: https://arxiv.org/abs/2306.00978
- GPTQ paper: https://arxiv.org/abs/2210.17323
- LLM.int8 paper: https://arxiv.org/abs/2208.07339
