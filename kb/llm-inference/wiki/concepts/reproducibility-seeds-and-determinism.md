---
type: Concept
title: Reproducibility、Seed 与推理确定性
description: LLM 推理里的“确定性”是分层的。固定 seed 只能约束采样随机数；它不能自动固定 tokenizer、chat template、batch
  调度、GPU kernel、并行通信、量化误差和不同框架的默认参数。因此同一 prompt、同一模型名、同一个 seed，在不同部署栈里仍可能输出不同。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Reproducibility、Seed 与推理确定性

LLM 推理里的“确定性”是分层的。固定 seed 只能约束采样随机数；它不能自动固定 tokenizer、chat template、batch 调度、GPU kernel、并行通信、量化误差和不同框架的默认参数。因此同一 prompt、同一模型名、同一个 seed，在不同部署栈里仍可能输出不同。

## 确定性的层次

| 层 | 需要固定什么 | 不固定的后果 |
|---|---|---|
| 输入层 | tokenizer revision、chat template、special tokens、stop/eos | token 序列不同，后续都不可比 |
| 采样层 | `do_sample`、`temperature`、`top_p`、`top_k`、penalties、seed | 随机路径不同 |
| Engine 层 | batch 顺序、prefix cache、chunked prefill、调度策略 | 同请求在不同 batch 里数值路径不同 |
| Kernel 层 | dtype、attention backend、CUDA graph、量化 kernel | 浮点舍入和归约顺序不同 |
| 分布式层 | tensor/data/expert parallel、all-reduce/all-to-all | 通信归约顺序带来细小差异 |
| 运行环境 | GPU 型号、driver、CUDA/cuBLAS/PyTorch 版本 | 库选择不同算法或 workspace |

很多业务只需要“语义稳定”，不需要 bitwise reproducibility。评估脚本、回归测试、法律/审计场景才更接近 bitwise 或 token-level 稳定需求。

## Seed 能保证什么

Seed 通常只控制随机采样。它在这些情况下最有效：

- `do_sample=true` 且需要复现实验样本。
- 同一框架、同一版本、同一硬件、同一 batch 形状。
- tokenizer、prompt、sampling params 完全一致。

它不能保证：

- `temperature=0` 在所有框架和硬件上逐 token 完全一致。
- OpenAI-compatible 字段名一样就代表默认值一样。
- continuous batching 中请求被不同邻居合批后仍 bitwise 一致。
- 量化模型和未量化模型输出一致。

## Temperature 0 不是绝对确定

`temperature=0` 或 greedy decoding 会移除采样随机性，但不会移除数值不确定性。若两个候选 token 的 logit 极接近，微小的浮点差异、归约顺序或 kernel 选择都可能改变 argmax。分布式推理、低精度 attention、KV cache 量化和不同 tokenizer/template 都会放大这种差异。

## 参数映射

| 框架 / 层 | 参数族 | 调参含义 |
|---|---|---|
| Hugging Face Transformers | `GenerationConfig`、`do_sample`、`temperature`、`top_p`、`top_k`、`cache_implementation`、streamer | 固定生成策略、采样和缓存路径 |
| vLLM | engine/request seed、sampling params、scheduler/batch 参数、dtype、quantization、attention backend | 固定请求采样和 engine 数值路径 |
| SGLang | `--random-seed`、`--enable-deterministic-inference`、attention backend、Radix cache、sampling mode | 控制 serving 中更接近 batch-invariant 的执行路径；支持矩阵依赖 backend 和采样方式 |
| llama.cpp | `--seed`、sampling 参数、chat template、KV/cache dtype、GPU offload | 固定本地推理随机性和执行路径；默认随机 seed 不适合回归 |
| PyTorch | manual seed、deterministic algorithms、cuDNN benchmark、版本固定 | 控制训练/推理中 PyTorch 层面的随机性和算法选择 |
| CUDA/cuBLAS | workspace config、stream 并发、库版本 | 控制矩阵乘归约算法的可复现条件 |

## 回归测试建议

1. 固定模型 artifact 的 revision/hash，不只固定模型名。
2. 记录 tokenizer 文件、chat template、system prompt、tool schema 顺序。
3. 固定完整 sampling 参数；不要依赖框架默认值。
4. 对线上 serving，把 batch/scheduler 差异纳入不可复现风险。
5. 回归断言优先比较结构、字段和关键事实；只有必要时才断言完整 token 序列。
6. 需要逐 token 对齐时，在单请求、单 GPU、固定 dtype、固定版本下建立基线。

## 常见误区

- “设置 seed 就够了”：seed 只是随机源，不是全栈快照。
- “模型名相同就相同”：网关别名可能路由到不同 revision 或量化版本。
- “temperature=0 就可审计复现”：greedy 仍受数值路径影响。
- “Transformers 与 serving engine 应完全一致”：serving engine 的 KV cache、attention backend 和 batch 调度通常不同。
- “升级驱动不影响输出”：底层库可能改变 kernel 或归约算法。

## 关键来源

- Hugging Face Transformers generation: https://huggingface.co/docs/transformers/en/main_classes/text_generation
- Hugging Face generation utilities: https://huggingface.co/docs/transformers/en/internal/generation_utils
- Hugging Face set_seed: https://huggingface.co/docs/transformers/en/internal/trainer_utils#transformers.set_seed
- vLLM Engine Arguments: https://docs.vllm.ai/en/latest/configuration/engine_args.html
- SGLang deterministic inference: https://docs.sglang.io/docs/advanced_features/deterministic_inference
- llama.cpp server README: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- PyTorch reproducibility notes: https://docs.pytorch.org/docs/stable/notes/randomness.html
- PyTorch deterministic algorithms: https://docs.pytorch.org/docs/2.9/generated/torch.use_deterministic_algorithms.html
- NVIDIA cuBLAS results reproducibility: https://docs.nvidia.com/cuda/cublas/index.html#results-reproducibility
