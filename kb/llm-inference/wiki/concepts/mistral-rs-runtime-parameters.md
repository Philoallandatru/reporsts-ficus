---
type: Concept
title: mistral.rs 参数模型
description: mistral.rs 是 Rust 编写的 LLM/VLM 推理运行时和服务端，强调本地推理、OpenAI-compatible serving、多量化格式和较丰富的模型架构支持。它和
  llama.cpp 一样适合本地/边缘场景，也提供 server 模式用于把模型暴露成 API。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# mistral.rs 参数模型

mistral.rs 是 Rust 编写的 LLM/VLM 推理运行时和服务端，强调本地推理、OpenAI-compatible serving、多量化格式和较丰富的模型架构支持。它和 llama.cpp 一样适合本地/边缘场景，也提供 server 模式用于把模型暴露成 API。

## 参数面

| 参数面 | 常见参数 / 概念 | 作用 |
|---|---|---|
| Serving | `serve`、`--host`、`--port`、OpenAI-compatible `/v1` endpoint、chat/completions/responses/embeddings | 把本地模型暴露成服务 |
| 模型加载 | `--model-id/-m`、`--tokenizer/-t`、`--arch`、`--dtype`、`--format`、`--quantized-file/-f`、`--mmproj`、`--tok-model-id` | 决定加载哪个模型和如何格式化消息 |
| 量化 | `--quant`、GGUF、UQFF、GPTQ/AWQ、`--isq`、dtype | 降低权重显存/内存和带宽压力 |
| KV cache / PagedAttention | `--max-seq-len`、`--max-batch-size`、`--max-seqs`、`--no-kv-cache`、`--prefix-cache-n`、PagedAttention 参数 | 控制上下文、并发和内存占用 |
| Device | `--cpu`、`--device-layers`、`--topology`、CUDA、Metal 等后端 | 决定真实计算路径和可用 dtype |
| Adapter / LoRA | `--enable-lora`、`--lora`、`--lora-modules`、`--lora-max-adapters`、`--lora-max-rank` | 复用基础模型服务多个任务 |
| 多模态 | OpenAI content part、`--image`、`--audio`、`--video`、`--mmproj` | 图像/音频/视频输入会消耗额外预处理和 token 预算 |

具体参数名随 mistral.rs 版本更新较快，生产部署前应以 `mistralrs-server --help` / 官方 CLI reference 为准。

## ISQ 与离线量化的区别

mistral.rs 文档把 in-situ quantization（ISQ）作为一个重要能力：模型可以在加载后按指定方式量化，而不一定提前准备量化权重文件。`--quant` 更偏选择现成量化 artifact，`--isq` 更偏运行时量化路径。

这带来两类取舍：

- 部署简单：可以从普通权重出发，在本机转换成更省内存的执行形态。
- 启动成本增加：量化发生在加载路径上，冷启动时间和峰值内存要单独评估。

如果服务要求快速弹性扩容，预先准备量化 artifact 往往比每个副本启动时做 ISQ 更稳定。

## PagedAttention 与上下文

PagedAttention 的目标和 vLLM 类似：把 KV cache 切成块，减少长上下文和多请求并发下的内存碎片。调参时要把三件事一起看：

- 上下文窗口越大，单请求最大 KV cache 越大。
- 并发越高，同时活跃的 KV block 越多。
- 量化和 cache dtype 会改变显存/内存占用，但也可能影响数值路径。

相关参数包括 `--paged-attn auto|on|off`、`--pa-memory-mb`、`--pa-memory-fraction`、`--pa-context-len`、`--pa-block-size`、`--pa-cache-type`。官方文档说明默认策略会按后端选择：CUDA 更适合开启，Metal/CPU 路径通常不同。

## Chat template 与 LoRA

Chat template 解析顺序会影响 role、system prompt、tool message 和 special token。mistral.rs 支持显式 Jinja template、processor config、命令行 override、模型仓库 template 和 GGUF metadata 等来源；迁移模型时要记录真实生效的模板。

LoRA 路径支持启动时加载和动态选择 adapter。它适合一个 base model 服务多个任务，但必须确认 adapter 与 base model 匹配；runtime 兼容检查不能替代训练基座审计。

## 调参路径

| 目标 | 优先调参 |
|---|---|
| 本地能跑 | 先选量化格式、device、context length，再调采样 |
| 降低内存 | GGUF/GPTQ/AWQ/ISQ、KV cache dtype、上下文长度 |
| 降低延迟 | 确认硬件 backend、生效 dtype、PagedAttention、prompt 长度 |
| API 兼容 | 核对 OpenAI-compatible streaming、chat template、stop/eos、tool/JSON 支持 |
| 多模型/adapter | 先验证加载和切换成本，再评估并发 |

## 常见误区

- 把 ISQ 当成免费：它节省运行内存，但可能增加冷启动和转换时间。
- 对已经量化的低 bit GGUF 再做 ISQ：可能叠加质量损失。
- 只看模型架构支持：真正能否生产使用还取决于 tokenizer、chat template、VLM processor 和量化路径。
- `--host 0.0.0.0` 直接暴露服务：生产应配认证代理或限制监听地址。
- 用 `temperature=0` 做跨后端一致性验收：不同 dtype、cache 和 kernel 仍可能产生差异。
- 忽略 server 层：本地单请求速度好，不代表 OpenAI-compatible server 在并发下也稳定。

## 相关页面

- [模型格式、加载与供应链边界](model-formats-and-loading.md)
- [推理量化](inference-quantization.md)
- [KV cache 与 PagedAttention](kv-cache-and-paged-attention.md)
- [OpenAI-compatible API 语义与兼容边界](openai-compatible-api-semantics.md)

## 关键来源

- mistral.rs documentation: https://ericlbuehler.github.io/mistral.rs/
- mistral.rs OpenAI-compatible serving: https://ericlbuehler.github.io/mistral.rs/guides/serve/openai-compatible-apis/
- mistral.rs CLI reference: https://ericlbuehler.github.io/mistral.rs/reference/cli/
- mistral.rs serve CLI reference: https://ericlbuehler.github.io/mistral.rs/reference/cli/serve/
- mistral.rs quantization: https://ericlbuehler.github.io/mistral.rs/guides/quantization/quantize-a-model/
- mistral.rs GGUF guide: https://ericlbuehler.github.io/mistral.rs/guides/models/run-gguf/
- mistral.rs PagedAttention: https://ericlbuehler.github.io/mistral.rs/guides/perf/paged-attention/
- mistral.rs chat templates: https://ericlbuehler.github.io/mistral.rs/guides/customize/chat-templates/
- mistral.rs LoRA adapters: https://ericlbuehler.github.io/mistral.rs/guides/customize/lora-adapters/
- mistral.rs multimodal input: https://ericlbuehler.github.io/mistral.rs/guides/models/multimodal-input/
- mistral.rs GitHub: https://github.com/ericlbuehler/mistral.rs
