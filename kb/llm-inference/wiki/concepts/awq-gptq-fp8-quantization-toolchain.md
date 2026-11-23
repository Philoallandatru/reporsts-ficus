---
type: Concept
title: AWQ、GPTQ 与 FP8 量化工具链
description: AWQ、GPTQ、FP8/NVFP4 是生产 LLM serving 里最常见的非 GGUF 量化路线。它们通常以 Hugging Face
  checkpoint、`quantization_config`、compressed-tensors、TensorRT-LLM engine 或 runtime-specific
  artifact 形式出现，最...
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# AWQ、GPTQ 与 FP8 量化工具链

AWQ、GPTQ、FP8/NVFP4 是生产 LLM serving 里最常见的非 GGUF 量化路线。它们通常以 Hugging Face checkpoint、`quantization_config`、compressed-tensors、TensorRT-LLM engine 或 runtime-specific artifact 形式出现，最终由 vLLM、TGI、TensorRT-LLM、SGLang、Transformers、LMDeploy 等加载。

## 工具和格式

| 工具 / 生态 | 主要产物 | 关键参数 | 备注 |
|---|---|---|---|
| LLM Compressor | compressed-tensors、FP8、NVFP4、AWQ、GPTQ 等 | recipe、scheme、dataset、calibration、offloading | vLLM 文档项目，适合面向 vLLM/Transformers 的现代压缩流程 |
| Transformers AWQ | AWQ checkpoint + `quantization_config` | `quant_method=awq`、`group_size`、`bits`、`version`、`do_fuse`、`fuse_max_seq_len` | Transformers 支持加载 AWQ；fused modules 和 FlashAttention2 组合需看限制 |
| GPTQModel / Transformers GPTQ | GPTQ int4 checkpoint | `GPTQConfig(bits, dataset, tokenizer, backend)`、`device_map`、`max_memory` | Transformers 文档说明 AutoGPTQ 不再受支持，建议 GPTQModel |
| AutoAWQ | AWQ quantize / inference | `w_bit`、`q_group_size`、`zero_point`、`version`、`calib_data`、`max_calib_samples`、`max_calib_seq_len` | GitHub API 显示仓库已归档；新项目优先看 LLM Compressor 或 runtime 官方路线 |
| AutoGPTQ | legacy GPTQ checkpoint | `bits`、`group_size`、`desc_act`、`damp_percent`、`sym`、`use_marlin` | GitHub API 显示仓库已归档；README 也建议迁到 GPTQModel |
| TensorRT-LLM quantization | TensorRT-LLM engine / checkpoint | FP8、INT8/INT4、AWQ/GPTQ、SmoothQuant、KV cache quant | 强依赖 GPU 架构、TensorRT-LLM 版本和 engine build 配置 |
| Optimum Quanto | Transformers runtime quant | `QuantoConfig(weights=...)` | Transformers 集成主要是 weight quant；activation/calibration/QAT 需直接用 Quanto |

## AWQ

AWQ 的核心是 activation-aware weight-only quantization：用校准激活识别重要权重通道，保护少量关键权重，再压缩大部分权重到低 bit。常见配置包括：

- `bits`：通常 4-bit。
- `group_size`：常见 128；影响压缩粒度、质量和 kernel 支持。
- `zero_point` / 对称性设置：影响量化误差和 kernel 兼容。
- `calib_data`、`max_calib_samples`、`max_calib_seq_len`：控制激活统计使用的数据分布和长度。
- fused modules：可提升速度，但和某些优化组合互斥。
- kernel 版本：GEMM、Marlin、ExLlamaV2 等路径的硬件支持不同。

## GPTQ

GPTQ 是后训练权重量化方法，常见 int4 checkpoint。当前 Transformers 文档明确建议使用 GPTQModel，而不是已经不维护的 AutoGPTQ。关键配置包括：

- `bits`：量化 bit 数。
- `dataset`：校准数据，Transformers 示例使用 `c4`，也支持字符串列表。
- `tokenizer`：用于准备校准数据。
- `device_map` / `max_memory`：大模型量化时控制 CPU/GPU 内存分配。
- `backend="marlin"`：使用 Marlin 这类推理 kernel，但不是所有 checkpoint/硬件都兼容。

`desc_act`、`damp_percent`、`sym` 和 `group_size` 会影响 GPTQ 误差分布与 kernel 兼容。迁移旧 AutoGPTQ artifact 时，不要只看 config 字段名相同；GPTQModel、Transformers 和 vLLM 的兼容说明要一起核对。

## FP8 / NVFP4

FP8 和 NVFP4 更依赖硬件和 runtime。它们可能覆盖权重、激活、KV cache 或混合方案。和 AWQ/GPTQ 相比，FP8 的关键风险通常不是“文件能不能加载”，而是 scale、校准、kernel 和 GPU 架构是否匹配。

生产中要记录：

- 量化对象：weight、activation、KV cache。
- scale 生成方式：dynamic、static、per-token、per-channel、block。
- 校准数据和 token 数。
- 目标硬件：Ampere、Hopper、Blackwell、ROCm、CPU/XPU 等。
- runtime：vLLM、TensorRT-LLM、SGLang、NIM 的版本和支持矩阵。

## 选择路线

| 目标 | 优先路线 | 注意 |
|---|---|---|
| vLLM 生产部署 | vLLM 支持矩阵 + LLM Compressor / 官方支持的 AWQ/GPTQ/FP8 | 先确认 `--quantization` 与模型 config 一致 |
| NVIDIA 高性能 engine | TensorRT-LLM quantization + engine build | engine build 参数和 GPU 架构绑定 |
| Transformers 快速试验 | AWQ/GPTQ/Quanto 文档路线 | 方便但吞吐不一定等于 serving engine |
| 维护 legacy GPTQ | GPTQModel 优先，AutoGPTQ 仅兼容旧 artifact | 注意 checkpoint 不一定互相兼容 |
| 极致低显存 | 低 bit AWQ/GPTQ/GGUF/IQ | 必须做业务质量回归 |

## 常见误调风险

| 风险 | 表现 | 处理 |
|---|---|---|
| 量化配置缺失 | runtime 不知道使用哪个 kernel，或按 fp16 加载 | 确认 `quantization_config` / compressed config 被保存 |
| AutoGPTQ 旧 checkpoint | 新 Transformers/vLLM/SGLang 加载异常 | 先查 GPTQModel 或目标 runtime 兼容说明 |
| `group_size` 不受 kernel 支持 | 加载成功但退回慢路径 | 用目标硬件跑 microbenchmark |
| fused AWQ 和其他优化冲突 | FlashAttention、adapter 或长上下文行为异常 | 逐项启用并做回归 |
| 校准数据过短 | 长上下文/RAG 质量掉得多 | 加入长上下文和业务模板后的样本 |
| FP8 scale 错 | 高激活、MoE、长上下文质量不稳 | 记录 scale granularity，并对 outlier 场景测试 |

## 相关页面

- [模型转换、量化与校准流水线](model-conversion-quantization-pipeline.md)
- [推理量化：权重、激活与 KV cache](inference-quantization.md)
- [vLLM Engine Args 参数模型](vllm-engine-parameters.md)
- [TensorRT-LLM Serving 参数模型](tensorrt-llm-serving-parameters.md)
- [Hugging Face TGI Launcher 参数模型](tgi-launcher-parameters.md)

## 关键来源

- vLLM LLM Compressor: https://docs.vllm.ai/projects/llm-compressor/en/latest/
- LLM Compressor compression schemes: https://docs.vllm.ai/projects/llm-compressor/en/latest/guides/compression_schemes/
- vLLM Quantization: https://docs.vllm.ai/en/stable/features/quantization/
- TGI quantization: https://huggingface.co/docs/text-generation-inference/en/conceptual/quantization
- Transformers AWQ docs: https://huggingface.co/docs/transformers/en/quantization/awq
- Transformers GPTQ docs: https://huggingface.co/docs/transformers/en/quantization/gptq
- Transformers Quanto docs: https://huggingface.co/docs/transformers/en/quantization/quanto
- Transformers quantization main classes: https://huggingface.co/docs/transformers/en/main_classes/quantization
- Optimum GPTQ docs: https://github.com/huggingface/optimum/blob/main/docs/source/llm_quantization/usage_guides/quantization.mdx
- Quanto blog: https://huggingface.co/blog/quanto-introduction
- Optimum Quanto GitHub: https://github.com/huggingface/optimum-quanto
- TensorRT-LLM Quantization: https://nvidia.github.io/TensorRT-LLM/latest/features/quantization.html
- TensorRT-LLM FP8 guide: https://nvidia.github.io/TensorRT-LLM/performance/performance-tuning-guide/fp8-quantization.html
- TensorRT-LLM quantization examples: https://github.com/NVIDIA/TensorRT-LLM/blob/main/examples/quantization/README.md
- AutoAWQ docs: https://casper-hansen.github.io/AutoAWQ/
- AutoGPTQ README: https://github.com/AutoGPTQ/AutoGPTQ/blob/main/README.md
- GPTQModel GitHub: https://github.com/ModelCloud/GPTQModel
- vLLM GPTQModel docs: https://docs.vllm.ai/en/latest/features/quantization/gptqmodel/
