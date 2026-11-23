---
type: Concept
title: 图编译与 Engine 构建优化
description: 很多推理框架的性能不是运行时一瞬间决定的，而是在“模型转换、图优化、engine build、compile cache、CUDA Graph
  capture”阶段决定的。这里的参数通常更难调，因为它们改变了模型执行图本身。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 图编译与 Engine 构建优化

很多推理框架的性能不是运行时一瞬间决定的，而是在“模型转换、图优化、engine build、compile cache、CUDA Graph capture”阶段决定的。这里的参数通常更难调，因为它们改变了模型执行图本身。

## 编译层次

| 层次 | 代表 | 作用 |
|---|---|---|
| Python graph capture | `torch.compile`、TorchDynamo/Inductor | 捕获 Python/PyTorch 执行图，减少 eager overhead |
| CUDA Graph | vLLM、TensorRT-LLM、PyTorch | 捕获固定 shape 的 GPU kernel launch 序列 |
| Engine build | TensorRT-LLM `trtllm-build` | 为目标 GPU 构建优化 engine |
| ONNX graph optimization | ONNX Runtime | constant folding、operator fusion、layout optimization |
| IR / model optimization | OpenVINO Model Optimizer / OV pipeline | 转换和优化模型到 OpenVINO IR |
| TVM compile | MLC LLM | 为 CUDA/Metal/Vulkan/WebGPU 等目标生成模型库 |

## TensorRT-LLM engine build

TensorRT-LLM 的 build 阶段会固化很多容量上限和 kernel 选择。常见参数包括：

- `--checkpoint_dir` / `--model_config`：输入模型。
- `--output_dir`：engine 输出。
- `--max_batch_size`、`--max_input_len`、`--max_seq_len`、`--max_num_tokens`：容量上限。
- `--gemm_plugin`、`--gpt_attention_plugin`、`--remove_input_padding`：kernel/plugin 优化。
- TP/PP/EP 相关参数：决定多 GPU engine 形状。
- quantization / dtype：决定权重、激活、KV cache 精度路径。

build 得太保守，运行时吞吐上不去；build 得太大，engine 显存和构建时间上升。

## CUDA Graph 与 shape

CUDA Graph 通过捕获一组 GPU 操作并回放，减少 kernel launch 开销。它适合 decode 这种重复形状明显的循环，但对动态 shape 敏感。

常见问题：

- 真实 batch shape 不在 capture sizes 内，回退 eager。
- 首次请求触发 capture，冷启动变慢。
- graph 占用额外显存。
- 调试困难，异常栈不如 eager 清楚。

因此生产要做 warmup，并让 warmup 覆盖真实 batch 和 sequence 分布。

TensorRT-LLM 还提供 torch compile 与 piecewise CUDA Graph 相关路径：不是整段都能 capture 时，可让部分 attention 或动态段保持 eager，其余片段用 graph/compile 降低 launch overhead。它的收益同样依赖真实 shape 分布。

## `torch.compile`

`torch.compile` 能减少 PyTorch eager overhead，融合部分图并生成优化 kernel。vLLM 等框架会在内部使用 compile/CUDA Graph 组合。

PyTorch 的 `mode`、`dynamic` 和 backend 选择会影响编译时间、动态 shape 支持和运行速度。对 serving 来说，`reduce-overhead` 这类模式常用于降低 Python 与 launch overhead，但首次编译成本和 graph 额外内存必须纳入 warmup。

调参判断：

- p99 有奇怪尖刺：检查是否发生新 shape 编译。
- 启动或首次请求慢：可能是 compile/capture。
- 行为异常：先用 eager 模式验证正确性，再逐步打开 compile/graph。

## ONNX Runtime 图优化

ONNX Runtime 提供 basic、extended、layout 等图优化级别，目标包括：

- 删除无用节点。
- 常量折叠。
- 算子融合。
- 布局转换。
- EP 特定优化。

图优化要和 Execution Provider 一起看：某个优化可能让 CUDA/OpenVINO/QNN 更容易接管，也可能因 shape 或算子支持导致 fallback。

## OpenVINO 与 MLC

OpenVINO 的模型准备和优化强调把模型转换到适合 Intel 设备的 IR/compiled model，并通过性能 hint、batch、stream、precision 等方式调优。

MLC LLM 则把模型编译成目标平台模型库。`mlc_llm compile` 的 `--device`、`--quantization`、`--overrides` 和 `--output` 会直接影响部署产物。

## 调参判断

| 症状 | 可能原因 | 优先动作 |
|---|---|---|
| 首次请求慢 | compile / engine load / CUDA Graph capture | 预编译、warmup、缓存 engine |
| 升级后性能变差 | kernel/graph 选择变化 | 固定版本，记录 engine build 参数 |
| 某些长度特别慢 | shape 未被 graph 捕获或编译 | 分桶长度，增加 capture sizes |
| 显存比预估高 | graph workspace、engine workspace、activation reserve | 降低 capture 范围，减小 build 上限 |
| EP/NPU 没加速 | 图优化或算子覆盖不匹配 | 检查 provider assignment 和 fallback |

## 与其他页面的关系

- [Attention kernel 与运行时优化](attention-kernels-and-runtime-optimization.md)：关注 kernel，本页关注 graph/engine 构建层。
- [推理排障手册](inference-troubleshooting-runbook.md)：graph/JIT warmup 是常见 p99 问题。
- [TensorRT-LLM Serving 参数模型](tensorrt-llm-serving-parameters.md)：serving 参数之外，engine build 决定容量边界。
- [MLC LLM 参数模型](mlc-llm-runtime-parameters.md)：MLC 的核心就是编译部署。

## 关键来源

- TensorRT-LLM `trtllm-build`: https://nvidia.github.io/TensorRT-LLM/commands/trtllm-build.html
- TensorRT-LLM torch compile and piecewise CUDA Graph: https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/features/torch_compile_and_piecewise_cuda_graph.md
- vLLM CUDA Graphs: https://docs.vllm.ai/en/stable/design/cuda_graphs/
- vLLM torch.compile: https://docs.vllm.ai/en/latest/design/torch_compile/
- PyTorch `torch.compile`: https://docs.pytorch.org/docs/stable/generated/torch.compile.html
- ONNX Runtime graph optimizations: https://onnxruntime.ai/docs/performance/model-optimizations/graph-optimizations.html
- OpenVINO model preparation: https://docs.openvino.ai/2025/openvino-workflow/model-preparation.html
- OpenVINO model optimization: https://docs.openvino.ai/2025/openvino-workflow/model-optimization.html
- OpenVINO optimize inference: https://docs.openvino.ai/2025/openvino-workflow/running-inference/optimize-inference.html
- MLC LLM compile models: https://llm.mlc.ai/docs/compilation/compile_models.html
