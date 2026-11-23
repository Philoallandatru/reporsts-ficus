---
type: Concept
title: 多模态推理与媒体 token 预算
description: 多模态推理把图像、视频或音频转换成模型可读的 token/embedding，再与文本 token 一起进入语言模型。部署时最容易低估的是媒体
  token 预算：一张高分辨率图、一段视频或多张图会显著吃掉上下文窗口、prefill 计算和 KV cache。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 多模态推理与媒体 token 预算

多模态推理把图像、视频或音频转换成模型可读的 token/embedding，再与文本 token 一起进入语言模型。部署时最容易低估的是媒体 token 预算：一张高分辨率图、一段视频或多张图会显著吃掉上下文窗口、prefill 计算和 KV cache。

## 推理路径

```text
image / video / audio
  -> preprocessor
  -> vision/audio encoder
  -> projector / adapter
  -> multimodal embeddings
  -> language model prefill + decode
```

llama.cpp 常见参数是 `--mmproj` / `--mmproj-auto`；Ollama 用模型能力和 API `images` 字段；vLLM/SGLang/TensorRT-LLM 更偏 OpenAI-compatible multimodal API 和模型配置。

## 媒体 token 成本

| 媒体 | 成本来源 | 调参影响 |
|---|---|---|
| 单图 | patch 数、分辨率、裁剪策略、projector 输出 token 数 | 增加 prefill 和 KV cache |
| 多图 | 每张图 token 数累加 | 很容易超过上下文预算 |
| 视频 | 帧数 * 每帧 token 数 | 需要限制帧率、采样帧数或分辨率 |
| 音频 | chunk、特征帧、encoder 输出长度 | 长音频需要分段或摘要 |

OpenAI 的 image input 文档明确把图像也计入 token 预算；不同模型族使用 patch-based 或 tile-based 规则，`detail=low/high/original/auto` 会影响 token、延迟和坐标精度。开源 serving 中也要用类似思路估算：视频约等于帧数乘以每帧视觉 token，音频约等于特征帧或 encoder 输出长度。

## 常见控制面

| 目标 | 参数/配置 |
|---|---|
| 限制媒体来源 | `--allowed-media-domains`、网关 allowlist |
| 限制每 prompt 媒体数量 | `--limit-mm-per-prompt`、media count limits |
| 视频采样 | `--media-io-kwargs`、`num_frames`、`video_pruning_rate` |
| 限制图像 token | `--image-min-tokens`、`--image-max-tokens`、模型 processor 参数 |
| 加载 projector | `--mmproj`、`--mmproj-auto`、multimodal config |
| 多模态缓存 | `--mm-processor-cache-gb`、processor cache、prefix cache |
| API 输入 | OpenAI-compatible `messages[].content` 中的 image/audio/video items |

## 性能影响

- 多模态请求通常 TTFT 更高，因为媒体预处理和 encoder/projector 会发生在 prefill 前。
- 媒体 token 会占用上下文窗口，减少可放入的文本 token。
- 多图/视频请求需要更严格的 admission control，否则小批量就能占满 KV cache。
- 如果媒体来自远程 URL，下载、解码和安全校验也会进入端到端延迟。

## 调参建议

- 为多模态 deployment 单独设 `max-input-tokens` / media count / media size 限制。
- 对外部 URL 设置 allowed domains，避免服务端变成任意 URL fetcher。
- 视频优先限制帧数和分辨率，而不是只限制请求体大小。
- 多模态模型的 chat template 和 special tokens 要按模型官方说明使用。
- precomputed embeddings 只给可信调用方开放；错误 shape 可能导致 engine 崩溃或异常资源占用。

## 关键来源

- OpenAI Images and Vision: https://developers.openai.com/api/docs/guides/images-vision
- OpenAI Audio: https://developers.openai.com/api/docs/guides/audio
- vLLM Multimodal Inputs: https://docs.vllm.ai/en/stable/features/multimodal_inputs/
- vLLM Serve CLI: https://docs.vllm.ai/en/stable/cli/serve/
- SGLang Vision API: https://docs.sglang.io/docs/basic_usage/openai_api_vision.md
- SGLang Multimodal Models: https://docs.sglang.io/docs/supported-models/multimodal_language_models.md
- llama.cpp multimodal: https://github.com/ggml-org/llama.cpp/blob/master/docs/multimodal.md
- Ollama API: https://github.com/ollama/ollama/blob/main/docs/api.md
