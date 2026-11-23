---
type: Concept
title: ONNX Runtime GenAI 参数模型
description: ONNX Runtime GenAI 把 LLM 生成循环封装到 ONNX Runtime 之上：模型加载、tokenization、logits
  processing、search/sampling、KV cache、多模态处理和 adapter 都由 `onnxruntime-genai` API 管理。它的重点是本地、端侧、Windows/CPU...
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# ONNX Runtime GenAI 参数模型

ONNX Runtime GenAI 把 LLM 生成循环封装到 ONNX Runtime 之上：模型加载、tokenization、logits processing、search/sampling、KV cache、多模态处理和 adapter 都由 `onnxruntime-genai` API 管理。它的重点是本地、端侧、Windows/CPU/GPU/NPU 等硬件可移植部署。

## 核心抽象

| 抽象 | 作用 | 常见参数/方法 |
|---|---|---|
| `Config` | 加载模型配置并选择 execution provider | `append_provider()`、`set_provider_option()`、`clear_providers()` |
| `Model` | 从模型目录或 Config 加载 ONNX GenAI 模型 | model path、`genai_config.json` |
| `Tokenizer` / `TokenizerStream` | 编码输入和流式解码输出 token | `encode()`、`decode()`、stream decode |
| `GeneratorParams` | 设置输入、搜索选项和 logits 处理 | `set_search_options()`、`input_ids` |
| `Generator` | 增量生成循环 | `compute_logits()`、`generate_next_token()`、`is_done()` |
| `Adapters` | 加载和启用 LoRA/adapter | adapter path、adapter name |
| `MultiModalProcessor` | 图像/音频等多模态输入预处理 | images、audios、prompt |

## Execution Provider

ONNX Runtime 的硬件选择通过 Execution Provider 完成。GenAI 的 `Config.append_provider("CUDAExecutionProvider")` 或 C++ 的 `AppendProvider` 会把可支持的子图交给对应 EP。

典型 EP 思路：

- CPUExecutionProvider：通用、最稳定，适合基线和端侧 CPU。
- CUDAExecutionProvider：NVIDIA GPU。
- TensorRTExecutionProvider：ONNX Runtime 层面的 TensorRT 加速，适合固定 shape/图优化场景。
- DirectML / OpenVINO / QNN / CoreML 等：面向 Windows、Intel、移动或 NPU 场景。

调参时不要只看“有没有 GPU”。同一模型在不同 EP 上的 kernel 覆盖、fallback 和内存布局可能不同；需要记录 provider 列表和 provider options。

## SearchOptions 与采样

`GeneratorParams.set_search_options()` 控制生成策略。常见字段与其他框架类似：

| 参数 | 含义 |
|---|---|
| `max_length` / `max_new_tokens` | 生成长度边界 |
| `do_sample` | 是否采样 |
| `temperature` | logits 缩放 |
| `top_k` / `top_p` | 候选 token 截断 |
| `repetition_penalty` | 重复惩罚 |
| `num_beams` | beam search 宽度 |
| `batch_size` / `num_return_sequences` | 一次生成的序列数和返回数 |
| `no_repeat_ngram_size` / `length_penalty` | beam/search 后处理 |
| `past_present_share_buffer` | KV cache buffer 共享策略，影响内存 |
| `random_seed` | 采样可复现性 |

原则和 [采样与结构化输出](sampling-and-structured-output.md) 一致：采样控制质量和多样性，beam 会扩大计算，长度参数同时影响 latency 和 KV cache。

## Model Builder 与量化

ONNX Runtime GenAI 的 model builder 用来把 PyTorch/Hugging Face 模型转换成优化后的 ONNX GenAI 模型，并可生成量化权重。它解决的是“部署前的模型构建”问题，不是请求级调参。

常见关注点：

- `genai_config.json` 必须和模型结构、tokenizer、搜索配置兼容。
- int4/int8 量化能显著降低权重体积，但要验证模型质量和 EP 支持。
- ONNX 图优化和量化格式会影响哪些 kernel 能被目标 EP 接管。
- 模型构建产物要和运行时版本一起记录，否则很难复现性能差异。

## Adapter serving

ONNX Runtime GenAI API 暴露 `Adapters`，可加载 adapter 并在生成时选择。和 vLLM/SGLang 的 LoRA serving 相比，它更偏本地 API 级集成，而不是多租户高并发 adapter 调度。

要注意：

- adapter 与 base model 的结构、rank、dtype 必须兼容。
- 多 adapter 切换会增加内存和加载管理复杂度。
- 端侧场景要考虑 adapter 文件大小和冷加载时间。

## 调参判断

| 症状 | 优先检查 |
|---|---|
| 输出慢 | EP 是否生效、是否有 CPU fallback、量化 kernel 是否被支持 |
| 显存/内存高 | 权重量化、KV cache 长度、beam 数、provider memory options |
| 输出格式异常 | tokenizer、chat template、`genai_config.json`、stop/eos |
| 首次运行慢 | ONNX 图优化、provider 初始化、模型文件加载 |
| 跨设备结果差异 | EP fallback、量化误差、算子覆盖差异 |

## 与其他框架的关系

- 与 [OpenVINO GenAI](openvino-genai-parameters.md) 一样，ONNX Runtime GenAI 更强调硬件可移植和本地部署。
- 与 [Transformers](huggingface-transformers-generation-parameters.md) 相比，它需要先转换/构建 ONNX GenAI 模型。
- 与 vLLM/TGI 相比，它不是高并发云端 serving 的默认首选，但适合 Windows、边缘和应用内嵌。

## 关键来源

- ONNX Runtime GenAI: https://onnxruntime.ai/docs/genai/
- ONNX Runtime GenAI Python API: https://onnxruntime.ai/docs/genai/api/python.html
- ONNX Runtime GenAI C++ API: https://onnxruntime.ai/docs/genai/api/cpp.html
- ONNX Runtime GenAI config reference: https://onnxruntime.ai/docs/genai/reference/config.html
- ONNX Runtime GenAI GitHub: https://github.com/microsoft/onnxruntime-genai
- ONNX Runtime GenAI Model Builder: https://github.com/microsoft/onnxruntime-genai/blob/main/src/python/py/models/README.md
- Build models with Model Builder: https://onnxruntime.ai/docs/genai/howto/build-model.html
- ONNX Runtime Execution Providers: https://onnxruntime.ai/docs/execution-providers/
- ONNX Runtime quantization: https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html
