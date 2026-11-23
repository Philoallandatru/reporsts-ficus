---
type: Concept
title: Ollama Modelfile 与服务参数
description: Ollama 把本地模型封装成可运行的模型包，参数主要通过 `Modelfile` 的 `PARAMETER`、运行时 API options
  和服务环境变量控制。它适合本地开发和轻量部署，参数面比 vLLM/TGI 简洁。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Ollama Modelfile 与服务参数

Ollama 把本地模型封装成可运行的模型包，参数主要通过 `Modelfile` 的 `PARAMETER`、运行时 API options 和服务环境变量控制。它适合本地开发和轻量部署，参数面比 vLLM/TGI 简洁。

## Modelfile 指令

| 指令 | 作用 |
|---|---|
| `FROM` | 定义基础模型，可来自模型名/tag、本地 safetensors 目录或 GGUF 文件 |
| `PARAMETER` | 设置模型运行参数 |
| `TEMPLATE` | 定义 prompt 模板 |
| `SYSTEM` | 设置系统消息 |
| `ADAPTER` | 应用 LoRA / QLoRA adapter |
| `MESSAGE` | 预置消息历史 |
| `REQUIRES` | 指定最低 Ollama 版本 |

## 常用 `PARAMETER`

| 参数 | 原理与影响 |
|---|---|
| `num_ctx` | 上下文窗口大小；越大 KV cache 占用越高 |
| `num_predict` | 最大生成 token 数；`-1` 表示无限生成语义，生产 API 应设置上限 |
| `temperature` | 控制概率分布尖锐程度；低值更稳定，高值更多样 |
| `top_k` | 只在前 K 个候选中采样 |
| `top_p` | 在累计概率达到 P 的候选集合中采样 |
| `min_p` | 按最高概率的相对比例过滤低概率 token |
| `repeat_last_n` | 重复惩罚回看窗口 |
| `repeat_penalty` | 重复惩罚强度 |
| `seed` | 随机种子；便于复现实验 |
| `stop` | 停止序列，可重复声明多个 |
| `draft_num_predict` | 有 draft model 或嵌入式 MTP tensors 时每步预测的 speculative draft token 数 |

## 服务与运行时

| 参数面 | 常用方式 | 说明 |
|---|---|---|
| 全局上下文 | `OLLAMA_CONTEXT_LENGTH=8192 ollama serve` | 设置默认上下文窗口 |
| 交互运行 | `/set parameter num_ctx 4096` | 在 `ollama run` 中调整 |
| API 请求 | `options.num_ctx`、`options.temperature` 等 | 单请求覆盖运行参数 |
| GPU 检查 | `ollama ps` | 查看模型在 CPU/GPU/混合内存中的加载比例 |
| 服务地址 | `OLLAMA_HOST` | 配置监听地址 |

## 关键参数原理

### `num_ctx`

它是 Ollama 中最重要的资源参数之一。增加 `num_ctx` 会让模型能看更长历史，也会增加 KV cache 占用。默认上下文可以通过环境变量设置，单模型也可以在 Modelfile 中写死。

### 采样组合

Ollama 的 `temperature`、`top_k`、`top_p`、`min_p` 与 llama.cpp 的采样模型高度相似。实际调参时应少量改变：例如代码生成用低温度和适中 `top_p`，头脑风暴用较高温度和更开放的候选集。

### `TEMPLATE` 与 `SYSTEM`

很多“模型不听话”不是采样问题，而是 chat template 与模型训练格式不匹配。Ollama 允许把模板固定进模型包，适合团队统一默认 prompt 格式。

### `ADAPTER`

Adapter 会把 LoRA/QLoRA 权重叠加到基础模型。它改变模型行为但不等于完整 fine-tuned 模型；多个 adapter 的兼容性需要验证。

## 调参建议

- 本地聊天：先调 `num_ctx`、`temperature`、`top_p`，不要急着改模板。
- 长文档问答：调高 `num_ctx` 后用 `ollama ps` 确认是否仍在 GPU 或可接受的混合模式。
- 稳定格式输出：降低 `temperature`，设置 `stop`，必要时改 `TEMPLATE`。
- 可复现实验：固定 `seed`、模型 tag 和 Modelfile。

## 关键来源

- Ollama Modelfile reference: https://docs.ollama.com/modelfile
- Ollama FAQ: https://docs.ollama.com/faq
