---
type: Concept
title: 模型转换、量化与校准流水线
description: 推理框架的很多“参数问题”其实在模型 artifact 生成阶段就已经决定了：权重格式、量化算法、校准数据、tokenizer、chat
  template、metadata、adapter 合并方式、engine build 目标。部署时应该把转换和量化当作可复现流水线，而不是临时下载别人发布的文件。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 模型转换、量化与校准流水线

推理框架的很多“参数问题”其实在模型 artifact 生成阶段就已经决定了：权重格式、量化算法、校准数据、tokenizer、chat template、metadata、adapter 合并方式、engine build 目标。部署时应该把转换和量化当作可复现流水线，而不是临时下载别人发布的文件。

Hugging Face Hub 下载工具支持按 `revision` 固定分支、tag 或 commit。生产流水线应该把这个 revision 写进模型包或构建记录；否则同一个 repo id 未来可能解析到不同权重、tokenizer 或 chat template。

## 标准流水线

| 阶段 | 输入 | 输出 | 需要固定的参数 |
|---|---|---|---|
| 源模型冻结 | HF repo、本地 checkpoint、adapter | 固定 revision 的源目录 | model revision、tokenizer revision、config、license、trust remote code 审计 |
| 格式转换 | safetensors/PyTorch -> GGUF/MLX/OpenVINO/TensorRT engine 等 | 运行时可加载 artifact | `outtype`、metadata、split/shard、tokenizer/chat template、特殊头如 mmproj/MTP |
| 校准数据准备 | 真实 prompt、通用文本、任务样本 | calibration corpus | 数据域、token 数、是否包含 special tokens、是否覆盖长上下文/tool/代码 |
| 量化 | 高精度 artifact、校准数据 | AWQ/GPTQ/GGUF/FP8/int4 等低精度模型 | bits、group size、sym/asym、activation order、KV dtype、imatrix、输出层/embedding 是否保留高精度 |
| 打包发布 | 权重、tokenizer、config、模板、README | 可部署模型包 | revision tag、quantization_config、runtime 兼容矩阵、基准结果 |
| 运行时验收 | 目标框架和硬件 | 可上线配置 | load test、质量回归、TTFT/TPOT、显存、stream/tool/JSON 兼容 |

## 为什么校准数据重要

AWQ、GPTQ、FP8 静态量化、llama.cpp imatrix 这类方法都会借助样本估计“哪些权重、通道或激活更重要”。校准数据离线上任务越远，量化误差越可能集中到业务关心的 token 分布上。

校准集至少要覆盖：

- 真实系统 prompt 和 chat template。
- 常见用户输入长度，而不是只有短句。
- 业务输出结构，例如 JSON、代码、SQL、工具调用。
- 多语言或专业术语。
- 长上下文/RAG 场景中的检索片段格式。

## Artifact 不是只有权重

一个可复现推理 artifact 应包含：

- 权重文件和量化配置。
- tokenizer 文件、special token、chat template。
- generation 默认值和 stop/eos 策略。
- adapter / LoRA 的版本和合并策略。
- 模型 metadata，例如 GGUF metadata、HF `quantization_config`、engine build config。
- 目标 runtime 版本和硬件说明。

只记录“Q4”或“AWQ 4-bit”是不够的。不同 group size、kernel、校准集和保留层策略会产生不同质量和速度。

## 常见量化路线

| 路线 | 典型产物 | 适合 runtime | 关注点 |
|---|---|---|---|
| GGUF quant | `Q4_K_M`、`Q5_K_M`、`Q8_0`、IQ 系列 | llama.cpp、Ollama、KoboldCpp、llamafile | metadata、chat template、imatrix、是否从高精度 GGUF 量化 |
| AWQ | HF repo + `quantization_config` | vLLM、TGI、Transformers、TensorRT-LLM、LMDeploy | group size、fused kernel、FlashAttention 兼容 |
| GPTQ / GPTQModel | int4 GPTQ checkpoint | Transformers、vLLM、SGLang、部分 TGI/TensorRT 路线 | dataset、bits、Marlin backend、legacy AutoGPTQ 兼容 |
| FP8 / NVFP4 | FP8 weight/activation/KV artifact | vLLM、TensorRT-LLM、SGLang、NIM | 硬件支持、scale、calibration、KV cache 精度 |
| runtime-only quant | bitsandbytes、Quanto、torchao | Transformers / Python 服务 | 方便试验，但生产需确认 kernel 和保存格式 |

## 误调风险

| 风险 | 表现 | 处理 |
|---|---|---|
| 从已量化模型再次量化 | 质量明显下降，结构化输出更不稳 | 尽量从 fp16/bf16/f32 源权重量化 |
| 校准集太小或错域 | benchmark 看似正常，真实任务退化 | 使用业务样本 + 通用样本混合校准 |
| 只保存权重不保存 tokenizer/template | chat role、tool call、stop token 漂移 | 发布 artifact 时绑定 tokenizer 和 template |
| 量化格式和 runtime 不匹配 | 加载失败或退回慢 kernel | 在目标框架版本上做加载和性能验收 |
| 输出层/embedding 过度量化 | 罕见 token、JSON 标点、代码符号出错 | 对敏感层保留高精度或单独验证 |
| FP8 scale 错配 | 长上下文或高激活值场景崩质量 | 记录 scale 生成方式，并做分布外回归 |

## 推荐验收

1. 加载验收：目标 runtime 能加载，日志显示使用了预期 kernel。
2. 短文本质量：常见问答、摘要、分类。
3. 长上下文质量：RAG、长文档、多轮对话。
4. 格式质量：JSON schema、tool calling、代码块。
5. 性能：TTFT、TPOT、throughput、显存、峰值内存。
6. 稳定性：多并发、streaming 取消、热重启、冷启动。

## 相关页面

- [推理量化：权重、激活与 KV cache](inference-quantization.md)
- [模型格式、加载与供应链边界](model-formats-and-loading.md)
- [GGUF 转换与 llama.cpp 量化工具链](gguf-conversion-and-llama-quantize.md)
- [AWQ、GPTQ 与 FP8 量化工具链](awq-gptq-fp8-quantization-toolchain.md)
- [跨框架参数对照表](cross-framework-parameter-map.md)

## 关键来源

- llama.cpp quantize README: https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md
- llama.cpp imatrix README: https://github.com/ggml-org/llama.cpp/blob/master/tools/imatrix/README.md
- llama.cpp HF to GGUF converter: https://github.com/ggml-org/llama.cpp/blob/master/convert_hf_to_gguf.py
- Hugging Face GGUF docs: https://huggingface.co/docs/hub/en/gguf
- vLLM LLM Compressor: https://docs.vllm.ai/projects/llm-compressor/en/latest/
- Transformers AWQ docs: https://huggingface.co/docs/transformers/en/quantization/awq
- Transformers GPTQ docs: https://huggingface.co/docs/transformers/en/quantization/gptq
- TensorRT-LLM Quantization: https://nvidia.github.io/TensorRT-LLM/latest/features/quantization.html
- Hugging Face Hub download guide: https://huggingface.co/docs/huggingface_hub/en/guides/download
