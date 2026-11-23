---
type: Concept
title: llama.cpp 参数模型
description: llama.cpp 的参数面向本地和轻量服务：GGUF 模型、CPU/GPU 混合执行、KV cache dtype、上下文长度、采样和
  `llama-server` 的 continuous batching。它的关键调参问题通常是“模型权重、KV cache、计算 buffer 在 CPU/GPU/RAM/VRAM
  中怎么分配”。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# llama.cpp 参数模型

llama.cpp 的参数面向本地和轻量服务：GGUF 模型、CPU/GPU 混合执行、KV cache dtype、上下文长度、采样和 `llama-server` 的 continuous batching。它的关键调参问题通常是“模型权重、KV cache、计算 buffer 在 CPU/GPU/RAM/VRAM 中怎么分配”。

## 参数分组

| 类别 | 常用参数 | 原理与影响 |
|---|---|---|
| CPU 线程 | `--threads`、`--threads-batch`、`--cpu-mask`、`--cpu-range`、`--numa` | generation 和 prompt/batch processing 可用不同线程数；NUMA/affinity 用于减少跨 socket 访存抖动 |
| 上下文 | `--ctx-size`、`--keep`、`--context-shift` | `ctx-size` 决定单 slot 可见 token 窗口，也决定 KV cache 预留规模；`context-shift` 让长生成时滚动窗口 |
| batch | `--batch-size`、`--ubatch-size` | 逻辑 batch 控制一次处理的最大 token 数；micro-batch 影响实际 kernel 分块与显存峰值 |
| KV cache | `--kv-offload` / `--no-kv-offload`、`--cache-type-k`、`--cache-type-v`、`--kv-unified`、`--cache-ram` | K/V cache 可用 f32/f16/bf16/q8/q4/q5 等类型；压低 dtype 可换取长上下文和更多 slot |
| GPU offload | `--device`、`--gpu-layers` / `--n-gpu-layers`、`--split-mode`、`--tensor-split`、`--main-gpu`、`--fit` | 把部分或全部层放到 VRAM；多 GPU 可按 layer/row/tensor 拆分 |
| RoPE 扩展 | `--rope-scaling`、`--rope-scale`、`--rope-freq-base`、`--rope-freq-scale`、`--yarn-*` | 用 RoPE/YaRN 改写位置编码尺度以扩展上下文；过度扩展会损伤长距离质量 |
| 模型来源 | `--model`、`--model-url`、`--hf-repo`、`--hf-file`、`--hf-token`、`--load-mode` | 支持本地文件、URL、HF repo；`load-mode` 控制 mmap/mlock/DirectIO 等加载行为 |
| LoRA/控制向量 | `--lora`、`--lora-scaled`、`--control-vector`、`--control-vector-layer-range` | 启动时叠加 adapter 或控制向量 |
| 采样 | `--samplers`、`--temperature`、`--top-k`、`--top-p`、`--min-p`、`--repeat-penalty`、`--presence-penalty`、`--frequency-penalty`、`--mirostat`、`--grammar`、`--json-schema` | 支持多 sampler 顺序组合和 grammar/JSON schema 约束 |
| 服务 | `--host`、`--port`、`--parallel`、`--cont-batching`、`--cors-origins`、`--api-key`、`--metrics` | `parallel` 是 server slots；continuous batching 允许多用户并发 decode |
| 多模态 | `--mmproj`、`--mmproj-auto`、`--mmproj-offload`、`--image-min-tokens`、`--image-max-tokens` | VLM 需要 projector；图像 token 数会进入上下文预算 |
| prompt/cache 复用 | `--cache-prompt`、`--cache-reuse`、`--lookup-cache-static`、`--lookup-cache-dynamic` | 复用提示词或 lookup cache，降低重复 prefill 成本 |
| 推测解码 | `--spec-draft-*`、draft KV cache dtype、draft token 数参数 | draft model 先猜多个 token，target model 验证，减少主模型 decode forward 次数 |

## 关键参数原理

### `--ctx-size`

上下文大小是最容易被误认为“只是输入长度”的参数。实际它会决定 KV cache 可容纳的 token 数。更大的上下文让模型能看更长历史，但也会线性增加 KV cache 需求。若显存不够，优先降低 `--ctx-size`、KV cache dtype 或 server slot 数。

### `--gpu-layers`

该参数控制最多多少层权重放入 VRAM。值越大，矩阵计算越多地在 GPU 上完成，吞吐通常越高；但权重占用会挤压 KV cache 和临时 buffer。`auto` / `all` 适合快速试跑，生产调优应看实际显存余量。

### `--cache-type-k` / `--cache-type-v`

K/V cache dtype 直接影响长上下文容量。f16 是稳妥默认；q8/q4/q5 能显著降低 KV cache 占用，尤其对长上下文有用。风险是注意力分数和 value 聚合的数值误差增加，需要用目标任务验证。

### `--batch-size` 与 `--ubatch-size`

`batch-size` 是逻辑最大 batch token 数，`ubatch-size` 是实际计算分块。前者太低会让 prompt processing 慢，后者太高容易造成显存峰值过大。OOM 发生在长 prompt prefill 时，可以先降 `--ubatch-size`。

### `--parallel` 与 `--cont-batching`

`--parallel` 控制 server slot 数，slot 越多并发越强，但每个 slot 都要占 KV cache。`--cont-batching` 开启后，新请求可以持续加入 batch，提升吞吐；如果追求极低单请求延迟，可以对比关闭后的表现。

### `--cache-prompt` / `--cache-reuse`

这类参数让重复 prompt 可以复用已经计算过的 KV cache。固定 system prompt、工具说明、few-shot 模板越长，收益越明显。它节省的是 prefill 计算，不会让每个活跃 slot 的 KV cache 免费消失。

### `--rope-*` / `--yarn-*`

这些参数用于扩展 RoPE 模型上下文。它们改变位置频率映射，不是无损扩容。适合模型支持或社区验证过的长上下文配置；不要只因为能启动就认为长上下文质量可靠。

## 调参建议

- 单机本地聊天：先用 `--gpu-layers auto`、`--ctx-size` 取模型默认或 4K/8K，确认模型完整进入 GPU/RAM。
- 显存不足：降低 `--ctx-size`，降低 `--gpu-layers`，或把 `--cache-type-k/v` 调到 q8/q4。
- 长 prompt OOM：先降 `--ubatch-size`，再降 `--ctx-size` 或 KV cache dtype。
- 多用户服务：设置 `--parallel`，保留 `--cont-batching`，用实际并发压测找 KV cache 与延迟平衡点。
- 结构化输出：优先使用 `--json-schema` 或 `--grammar`，不要只靠采样参数约束格式。

## 关键来源

- llama.cpp server README: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- llama.cpp build docs: https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md
