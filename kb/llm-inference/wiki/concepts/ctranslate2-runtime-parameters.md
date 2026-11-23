---
type: Concept
title: CTranslate2 参数模型
description: CTranslate2 是面向 Transformer 模型的高效推理 runtime，覆盖 CPU 和 GPU，常用于翻译、Whisper、encoder-decoder、decoder-only
  生成等任务。它的参数面更接近“推理库”而不是 OpenAI-compatible LLM server。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# CTranslate2 参数模型

CTranslate2 是面向 Transformer 模型的高效推理 runtime，覆盖 CPU 和 GPU，常用于翻译、Whisper、encoder-decoder、decoder-only 生成等任务。它的参数面更接近“推理库”而不是 OpenAI-compatible LLM server。

## 核心定位

| 场景 | 适合度 | 原因 |
|---|---|---|
| CPU/GPU 高效 batch 推理 | 适合 | C++ runtime、量化、线程控制、批处理成熟 |
| 翻译 / seq2seq / Whisper | 很适合 | Translator、Generator、Whisper API 覆盖这些任务 |
| OpenAI-compatible chat serving | 不优先 | 需要自己包装服务和 chat template |
| 大模型高并发 KV serving | 看场景 | 没有 vLLM PagedAttention 那类 LLM 专用调度抽象 |

## 常见参数

| 类别 | 参数 | 原理与影响 |
|---|---|---|
| 设备 | `device="cpu" / "cuda"`、`device_index` | 控制模型实例放在哪个设备 |
| 精度 | `compute_type` | 控制 int8、float16、bfloat16、float32 等计算路径 |
| CPU 线程 | `intra_threads`、`inter_threads` | 控制单个 op 内线程数和并行请求/模型线程 |
| GPU 并行 | 多 `device_index`、实例池 | 多 GPU 或多实例并行 |
| 批处理 | `max_batch_size`、`batch_type="examples" / "tokens"`、`max_input_length` | 控制 batch 形状和输入截断；tokens batch 让计算量更稳定 |
| 生成 | `beam_size`、`patience`、`num_hypotheses`、`sampling_topk`、`sampling_topp`、`sampling_temperature`、`repetition_penalty`、`no_repeat_ngram_size` | 控制 beam search / sampling / 输出 |
| 静态前缀 | `static_prompt`、`cache_static_prompt` | 固定系统提示或公共 prompt 可缓存，减少重复计算 |
| 缓存 | runtime 内部 cache / memory allocator | 影响重复调用和显存/内存行为 |
| 模型转换 | converter CLI、`--quantization` | 把 HF/OpenNMT 等模型转成 CTranslate2 格式 |

`compute_type` 是最关键旋钮之一：CPU 上 int8 通常能显著降低内存带宽压力；GPU 上 float16/int8 的收益取决于硬件和模型结构。

## Generator 与 Translator

`ctranslate2.Generator` 适合 decoder-only 或语言模型生成；`ctranslate2.Translator` 更适合 encoder-decoder 翻译类任务。两者都可以设置设备、compute type、线程和 batch 参数，但请求级生成参数不同。

典型判断：

- 翻译/摘要/seq2seq：优先看 `Translator`。
- 语言模型续写：优先看 `Generator`。
- Whisper：使用 CTranslate2/Faster-Whisper 生态时看专门封装。

## 线程与吞吐

CPU 推理时：

- `intra_threads` 增大可加速单请求矩阵计算，但会抢占核心。
- `inter_threads` 增大可提升多请求并行，但过高会造成线程竞争。大吞吐 CPU 场景通常优先增加 `inter_threads`，并避免 `inter_threads * intra_threads` 明显超过物理核心数。
- batch 太小利用率低，batch 太大尾延迟高。

GPU 推理时：

- CPU tokenization 和前后处理仍可能成为瓶颈。
- 多 GPU 要确认设备列表和负载分配。
- 量化是否真的快取决于 kernel 支持。

## 模型转换与量化

CTranslate2 通常先把模型转换到专用格式，再部署。转换阶段的量化会影响运行时模型大小和计算 dtype。

注意：

- 转换产物和 tokenizer 要一起版本化。
- 量化后要重新验证输出质量。
- 不同硬件支持的 compute type 不同，不能只看模型目录。

## 与其他页面的关系

- 与 [ONNX Runtime GenAI](onnxruntime-genai-parameters.md) 一样，CTranslate2 适合本地/CPU/GPU 库级推理。
- 与 [Embedding、Reranker 与 Encoder 推理](embedding-and-reranker-inference.md) 的 CPU batch 思路相近。
- 与 [vLLM](vllm-engine-parameters.md) 相比，它不是面向大规模 chat serving 的默认选择。

## 关键来源

- CTranslate2 documentation: https://opennmt.net/CTranslate2/
- CTranslate2 GitHub: https://github.com/opennmt/ctranslate2
- CTranslate2 Generator API: https://opennmt.net/CTranslate2/python/ctranslate2.Generator.html
- CTranslate2 Translator API: https://opennmt.net/CTranslate2/python/ctranslate2.Translator.html
- CTranslate2 quantization: https://opennmt.net/CTranslate2/quantization.html
- CTranslate2 parallel and asynchronous execution: https://opennmt.net/CTranslate2/parallel.html
- CTranslate2 model conversion: https://opennmt.net/CTranslate2/conversion.html
- CTranslate2 Transformers conversion: https://opennmt.net/CTranslate2/guides/transformers.html
- CTranslate2 performance guide: https://opennmt.net/CTranslate2/performance.html
- CTranslate2 performance: https://github.com/OpenNMT/CTranslate2/blob/master/docs/performance.md
