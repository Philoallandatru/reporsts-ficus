---
type: Concept
title: Intel IPEX-LLM 与 Optimum Intel 推理
description: Intel 推理路线不只有 OpenVINO GenAI。IPEX-LLM、Optimum Intel、Intel Extension for
  PyTorch 和 OpenVINO 组成了从 PyTorch 到 OpenVINO IR、从 CPU 到 Intel GPU/NPU 的多条路径。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Intel IPEX-LLM 与 Optimum Intel 推理

Intel 推理路线不只有 OpenVINO GenAI。IPEX-LLM、Optimum Intel、Intel Extension for PyTorch 和 OpenVINO 组成了从 PyTorch 到 OpenVINO IR、从 CPU 到 Intel GPU/NPU 的多条路径。

## 路线对照

| 路线 | 作用 | 适合场景 |
|---|---|---|
| IPEX-LLM | 低比特 LLM 推理、Intel CPU/GPU/XPU 生态 | 本地/边缘、Intel GPU、低比特实验 |
| Optimum Intel | Hugging Face Optimum 与 OpenVINO / IPEX 集成 | Transformers 模型部署到 Intel 后端 |
| OpenVINO GenAI | Intel 官方 GenAI pipeline 和 SchedulerConfig | 生产化 CPU/GPU/NPU 推理 |
| Intel Extension for PyTorch | PyTorch 层优化 | 保持 PyTorch API 的推理/训练优化 |
| ONNX Runtime OpenVINO EP | ONNX Runtime 中接入 OpenVINO backend | 跨平台 ONNX 部署 |

## 参数分组

| 类别 | 典型参数/概念 | 原理与影响 |
|---|---|---|
| device | CPU、GPU、XPU、NPU、OpenVINO device string | 决定执行后端 |
| precision | int4/int8/fp16/bf16/fp32 | 权重和计算精度，影响内存和 kernel |
| conversion | OpenVINO export、Optimum export、IPEX-LLM optimize | 把 HF/PyTorch 模型转成目标 runtime 形态 |
| batch/context | batch size、sequence length、KV cache | 决定内存和吞吐 |
| threading | CPU thread / stream / performance hints | CPU 场景关键 |
| graph optimization | OpenVINO compile model、cache、NNCF | 降低启动和推理开销 |

## Optimum Intel

Optimum Intel 让 Hugging Face 模型更容易导出和运行在 Intel 后端。常见路径：

- 使用 OpenVINO backend 导出模型。
- 配合量化/优化工具降低 footprint。
- 在 Transformers pipeline 或 Optimum API 中加载优化模型。

它适合已有 Hugging Face 模型和应用，希望迁移到 Intel CPU/GPU/NPU 的场景。

## IPEX-LLM

IPEX-LLM 关注低比特 LLM 推理和 Intel 硬件优化。它适合阅读历史方案和本地实验，但官方仓库当前已归档，并提示不再保证维护、修复或支持。新生产路线应优先评估 OpenVINO / Optimum Intel。

历史 IPEX-LLM 常见用法包括 `load_in_4bit=True`、`.to("xpu")`，以及 Intel GPU/iGPU/Arc 低比特推理。把这些经验迁移到生产时，要重新核对当前 OpenVINO/Optimum Intel 的量化和 device API。

## OpenVINO 低比特与 KV cache

OpenVINO with Optimum Intel 文档覆盖 dynamic quantization、weight compression 和 KV cache quantization。常见配置包括：

- `DYNAMIC_QUANTIZATION_GROUP_SIZE`：控制或关闭 dynamic quantization group。
- KV cache dtype：`u8`、`u4`、`bf16`、`f16` 等。
- `KEY_CACHE_GROUP_SIZE`、`VALUE_CACHE_GROUP_SIZE`：控制 KV cache 量化 group size。

这些参数和 [推理量化](inference-quantization.md) 直接相关：要分清权重量化、activation/dynamic quantization 和 KV cache 量化。

## 调参判断

| 症状 | 优先检查 |
|---|---|
| 没有加速 | 是否跑在目标 Intel backend，是否 fallback |
| 内存过高 | 低比特量化、OpenVINO weight compression、上下文长度 |
| CPU 吞吐低 | 线程、stream、NUMA、batch |
| NPU 不工作 | 模型是否支持、算子覆盖、OpenVINO/driver 版本 |
| 输出不同 | 量化、导出版本、tokenizer/template 是否一致 |

## 与其他页面的关系

- [OpenVINO GenAI 参数模型](openvino-genai-parameters.md)：Intel GenAI runtime 的主生产路径。
- [CPU、边缘与 NPU 推理](cpu-edge-npu-inference.md)：本页是 Intel 生态展开。
- [ONNX Runtime GenAI 参数模型](onnxruntime-genai-parameters.md)：ONNX Runtime OpenVINO EP 是另一条入口。

## 关键来源

- IPEX-LLM GitHub: https://github.com/intel/ipex-llm
- IPEX-LLM documentation: https://ipex-llm-latest.readthedocs.io/
- Optimum Intel documentation: https://huggingface.co/docs/optimum-intel/en/index
- Optimum Intel OpenVINO inference: https://huggingface.co/docs/optimum-intel/en/openvino/inference
- Optimum Intel GitHub: https://github.com/huggingface/optimum-intel
- OpenVINO GitHub: https://github.com/openvinotoolkit/openvino
- OpenVINO with Optimum Intel: https://docs.openvino.ai/2026/openvino-workflow-generative/inference-with-optimum-intel.html
- Intel Extension for PyTorch: https://intel.github.io/intel-extension-for-pytorch/
