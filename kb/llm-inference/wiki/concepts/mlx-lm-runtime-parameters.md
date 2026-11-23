---
type: Concept
title: MLX LM 参数模型
description: MLX LM 是 Apple MLX 生态里的 LLM 推理/微调工具，面向 Apple silicon 本地运行。它不是数据中心高吞吐
  serving engine，而是 Mac、本地开发、端侧实验和轻量服务的好选择。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# MLX LM 参数模型

MLX LM 是 Apple MLX 生态里的 LLM 推理/微调工具，面向 Apple silicon 本地运行。它不是数据中心高吞吐 serving engine，而是 Mac、本地开发、端侧实验和轻量服务的好选择。

## 定位

| 场景 | 是否适合 | 原因 |
|---|---|---|
| Apple silicon 本地 chat / generate | 适合 | MLX 针对 Apple silicon 统一内存和 Metal 后端 |
| 本地 OpenAI-compatible 小服务 | 适合 | `mlx_lm.server` 可启动本地 server |
| 大规模多租户 GPU serving | 不优先 | 缺少 vLLM/SGLang/TGI 那样的集群调度和高并发控制面 |
| 快速量化/转换 Hugging Face 模型 | 适合 | CLI 支持 convert、quantize、generate |

MLX 的一个核心背景是 Apple silicon 的统一内存架构：CPU/GPU 共享内存池，模型大小受总内存和内存带宽影响，而不是传统“独立 GPU 显存”。

## 常见命令与参数

| 命令 / API | 常用参数 | 作用 |
|---|---|---|
| `mlx_lm.generate` | `--model`、`--prompt`、`--max-tokens`、`--temp`、`--top-p`、`--seed` | 本地文本生成 |
| `mlx_lm.generate` | `--system-prompt`、`--top-k`、`--min-p`、`--max-kv-size`、`--kv-bits`、`--kv-group-size`、`--prompt-cache-file` | 控制系统提示、采样、KV cache 容量/量化和前缀缓存 |
| `mlx_lm.chat` | `--model`、`--ignore-chat-template`、`--use-default-chat-template` | 交互式聊天和模板选择 |
| `mlx_lm.server` | `--model`、`--host`、`--port`、`--allowed-origins`、`--prompt-cache-size`、`--prompt-cache-bytes` | 启动 OpenAI-compatible 本地服务和 server 侧 prompt cache |
| `mlx_lm.convert` | `--hf-path`、`--mlx-path`、`--quantize`、`--q-bits`、`--q-group-size` | 转换 Hugging Face 权重为 MLX 格式，可量化 |
| `mlx_lm.lora` | `--model`、`--train`、`--data`、`--iters`、`--fine-tune-type`、`--adapter-path`、`--num-layers`、`--batch-size`、`--max-seq-length` | LoRA/DoRA/full fine-tune；量化 base model 时是 QLoRA 路径 |
| Python API | `load()`、`generate()`、streaming generate | 应用内集成 |

具体参数会随 MLX LM 版本变化，生产脚本应以安装版本的 CLI help 和 README 为准。

## 量化与内存

MLX LM 的量化常见参数包括 `--quantize`、`--q-bits`、`--q-group-size`。它们主要影响：

- 权重占用内存。
- 生成速度和质量。
- 是否能在本机统一内存中装下模型。

量化越低，模型越容易装下，但输出质量和 kernel 效率要实测。Mac 上还要留出系统、浏览器、IDE 等进程的内存；统一内存不是免费显存池。

## Prompt cache

MLX LM 支持 prompt cache 相关能力，用于缓存长 prompt 的中间状态。它适合：

- 固定 system prompt。
- 长文档反复问答。
- 多次生成共享同一前缀。

和 vLLM prefix cache 一样，它省的是重复 prefill；后续 decode 仍然要消耗时间和 KV 状态。

`--max-kv-size` 是长生成时很关键的内存/质量旋钮：限制 KV cache 后，运行时需要用旋转/截断方式管理历史上下文。KV 量化参数 `--kv-bits`、`--kv-group-size`、`--quantized-kv-start` 则是用更低精度保存后续 KV，适合统一内存紧张的 Mac。

## LoRA 与 adapter

MLX LM 支持 LoRA、DoRA 和 full fine-tune。推理时可以通过 adapter path 加载 adapter，也可以 fuse 成独立模型。对于本地知识库/个人模型场景，常见流程是：

1. 先 `convert` 或直接加载 Hugging Face 模型。
2. 用 `mlx_lm.lora` 在本地 JSONL 数据上微调 adapter。
3. 生成时传入 adapter，或 fuse 后发布一个独立 MLX 模型目录。

这和 [LoRA 与 adapter serving](lora-and-adapter-serving.md) 里的生产多 adapter 调度不同：MLX LM 更偏单机本地训练/推理，而不是高并发多租户 adapter cache。

## 调参判断

| 症状 | 优先动作 |
|---|---|
| 模型加载失败或内存压力大 | 使用更低量化、换更小模型、关闭其他占用统一内存的进程 |
| 首 token 慢 | 检查 prompt 长度、prompt cache、模型是否已冷启动 |
| 输出太随机 | 降低 `--temp` / `temperature`，收紧 `top_p` |
| 本地 server 慢 | 区分模型推理慢和 HTTP/client 端慢；Mac 本地服务不适合过高并发 |
| 迁移到 vLLM 后输出不同 | 检查 tokenizer、chat template、采样参数默认值 |

## 与其他页面的关系

- 与 [llama.cpp 参数模型](llama-cpp-runtime-parameters.md) 一样，MLX LM 是本地推理重要路径。
- 与 [MLC LLM 参数模型](mlc-llm-runtime-parameters.md) 相比，MLX LM 更聚焦 Apple silicon Python/CLI 生态，MLC 更偏跨平台编译。
- 与 [Transformers Generation 参数模型](huggingface-transformers-generation-parameters.md) 共享采样语义，但模型加载和设备运行时完全不同。

## 关键来源

- MLX LM GitHub: https://github.com/ml-explore/mlx-lm
- MLX LM generate source: https://raw.githubusercontent.com/ml-explore/mlx-lm/main/mlx_lm/generate.py
- MLX LM server source: https://raw.githubusercontent.com/ml-explore/mlx-lm/main/mlx_lm/server.py
- MLX LM LoRA docs: https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md
- Apple MLX documentation: https://ml-explore.github.io/mlx/build/html/index.html
