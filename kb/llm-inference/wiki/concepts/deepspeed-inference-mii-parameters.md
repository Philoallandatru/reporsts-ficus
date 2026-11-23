---
type: Concept
title: DeepSpeed Inference / MII 参数模型
description: DeepSpeed Inference 更偏向 Python API 和引擎配置，MII 则在其上提供模型服务部署层。它们适合已有 DeepSpeed/PyTorch
  栈、需要 kernel injection、tensor parallel、CUDA Graph、Triton kernel 或 replica 管理的场景。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# DeepSpeed Inference / MII 参数模型

DeepSpeed Inference 更偏向 Python API 和引擎配置，MII 则在其上提供模型服务部署层。它们适合已有 DeepSpeed/PyTorch 栈、需要 kernel injection、tensor parallel、CUDA Graph、Triton kernel 或 replica 管理的场景。

## 参数分组

| 类别 | 常用参数/API | 原理与影响 |
|---|---|---|
| 引擎初始化 | `deepspeed.init_inference(model, config=...)`、`DeepSpeedInferenceConfig` | 把已有 PyTorch model 包装成 DeepSpeed 推理引擎 |
| kernel injection | `replace_with_kernel_inject`、`injection_policy` | 用 DeepSpeed 优化 kernel 替换 Transformer 层实现 |
| dtype/量化 | `dtype`、`quant`、MoQ 相关配置 | 可在 fp16/int8 等精度下运行；量化参数通常与 int8 dtype 搭配 |
| tensor parallel | `tensor_parallel.tp_size`、`mp_size` | 把模型切到多 GPU |
| CUDA Graph | `enable_cuda_graph` | 固定形状回放，减少 kernel launch overhead |
| Triton | `use_triton`、`triton_autotune` | 使用 Triton kernels；autotune 首次运行慢，后续可能更快 |
| ZeRO | `zero` | 复用 ZeRO 配置做参数/内存管理 |
| checkpoint | checkpoint/config 相关字段 | 控制 checkpoint 加载和模型并行 checkpoint 形态 |
| MII 服务 | `model_name_or_path`、`tokenizer`、`task`、`tensor_parallel`、`quantization_mode`、`replica_num`、`device_map` | 控制部署模型、并行、量化和多副本 |

## 关键参数原理

### `replace_with_kernel_inject`

启用后，DeepSpeed 会尝试把常见 Transformer 模块替换成推理优化 kernel。它能减少 Python/PyTorch 层开销并使用更合适的 fused kernel，但依赖模型结构匹配；自定义模型可能需要 `injection_policy`。

### `tensor_parallel.tp_size`

把模型层内大矩阵拆到多 GPU。适合模型单卡放不下或希望提高吞吐时使用。TP 的通信成本会随拓扑变化，普通 PCIe 环境下收益可能被 all-reduce 吃掉。

### `enable_cuda_graph`

CUDA Graph 把一段固定形状的 GPU work 捕获后回放，减少 launch overhead。它对稳定 batch/shape 更有效；动态 shape 太多时收益变小，且会增加预留内存。

### `use_triton` / `triton_autotune`

Triton kernels 可以在特定形状上提供更优性能。`triton_autotune` 会在首次运行中搜索更好的 kernel 配置，适合生产 warmup，不适合冷启动敏感场景直接暴露给用户。

### MII `replica_num`

MII 可部署多个副本做数据并行式扩容。副本数提高总吞吐，但每个副本都要占权重和 KV/运行内存；如果单副本已经显存吃紧，先解决量化或 TP。

## 调参建议

- 已有 PyTorch 服务：先用 `init_inference` 包装并启用 kernel injection，再评估数值一致性。
- 单卡装不下：优先 TP 或量化；不要把 CUDA Graph 当作省显存工具。
- 生产 warmup：开启 Triton autotune 和 CUDA Graph 前做固定形状预热。
- 多副本服务：用 MII replica 扩吞吐，但需要外层或内置路由和健康检查。

## 关键来源

- DeepSpeed inference initialization: https://deepspeed.readthedocs.io/en/latest/inference-init.html
- DeepSpeed-MII config: https://deepspeed-mii.readthedocs.io/en/rtd-staging/config.html
