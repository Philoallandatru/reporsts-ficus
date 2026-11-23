---
type: Concept
title: 模型格式、加载与供应链边界
description: 模型加载阶段决定的不只是“能不能跑”，还包括安全边界、冷启动时间、内存映射方式、tokenizer/template 版本和 kernel
  可用性。生产环境应该把模型加载当作供应链流程，而不是临时下载文件。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 模型格式、加载与供应链边界

模型加载阶段决定的不只是“能不能跑”，还包括安全边界、冷启动时间、内存映射方式、tokenizer/template 版本和 kernel 可用性。生产环境应该把模型加载当作供应链流程，而不是临时下载文件。

## 常见格式

| 格式 | 常见生态 | 特点 |
|---|---|---|
| safetensors | Hugging Face / vLLM / TGI / Transformers | 安全、可 lazy load / memory map，避免 pickle 执行风险 |
| PyTorch `.bin` | 旧 HF 模型 | 兼容广，但 pickle 风险和加载开销更高 |
| GGUF | llama.cpp / Ollama | 面向本地推理，包含 tensor 和 metadata，承载多种量化 |
| TensorRT engine | TensorRT-LLM | 编译后的高性能部署 artifact |
| AWQ/GPTQ/bnb | 多框架 | 权重量化格式，依赖 kernel 支持 |

TGI 文档明确把 safetensors 作为 tensor parallelism 所需格式；如果仓库同时有 safetensors 和 PyTorch weights，通常优先加载 safetensors。它的 safety 文档也提醒：pickle 权重和 `trust_remote_code` 都是显式信任边界。

## Revision pinning

从 Hugging Face 或远程仓库加载模型时，应该固定：

- model revision / commit。
- tokenizer revision。
- config revision。
- chat template。
- adapter revision。

否则同一个模型名可能在未来指向不同文件，导致 tokenizer、template、权重或 remote code 改变。

## `trust_remote_code`

`trust_remote_code` 允许执行模型仓库中的自定义 Python 代码。它对自定义 architecture 很有用，但也是供应链风险。生产环境建议：

- 固定 revision。
- 审计仓库代码。
- 在隔离环境构建镜像。
- 不对用户输入动态开启。

## mmap / mlock / lazy loading

| 机制 | 作用 | 风险 |
|---|---|---|
| mmap | 文件映射到虚拟内存，减少复制和冷启动峰值 | 首次访问可能 page fault |
| mlock | 锁定内存避免换出 | 占用物理内存，可能影响系统 |
| lazy load | 按需加载 tensor | 首次请求可能变慢 |
| direct I/O | 绕过部分页缓存 | 对磁盘和文件系统更敏感 |

## 调参建议

- 生产镜像内固定模型 artifact，避免启动时拉远程 latest。
- safetensors 优先于 pickle `.bin`。
- GGUF 量化模型要记录量化类型，不只记录模型名。
- tokenizer/chat template 要和权重同版本保存。
- 冷启动 benchmark 要包含模型加载和首轮 warmup，而不是只测热状态。

## 相关页面

- [模型转换、量化与校准流水线](model-conversion-quantization-pipeline.md)
- [GGUF 转换与 llama.cpp 量化工具链](gguf-conversion-and-llama-quantize.md)
- [AWQ、GPTQ 与 FP8 量化工具链](awq-gptq-fp8-quantization-toolchain.md)
- [推理量化：权重、激活与 KV cache](inference-quantization.md)

## 关键来源

- Hugging Face safetensors: https://huggingface.co/docs/safetensors/en/index
- Hugging Face GGUF docs: https://huggingface.co/docs/hub/en/gguf
- GGUF format spec: https://ggml-org-ggml.mintlify.app/formats/gguf
- TGI preparing model: https://huggingface.co/docs/text-generation-inference/en/basic_tutorials/preparing_model
- TGI safety: https://huggingface.co/docs/text-generation-inference/en/basic_tutorials/safety
- vLLM Engine Arguments: https://docs.vllm.ai/en/stable/configuration/engine_args/
- llama.cpp server README: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- llama.cpp build docs: https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md
- llama.cpp models: https://github.com/ggml-org/llama.cpp/blob/master/docs/models.md
- Ollama Modelfile: https://docs.ollama.com/modelfile
