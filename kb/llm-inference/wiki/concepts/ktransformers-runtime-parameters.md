---
type: Concept
title: KTransformers 参数模型
description: KTransformers 面向本地和低成本部署，核心思想是把大模型中的不同算子、层或专家映射到不同后端：一部分走 GPU kernel，一部分走
  CPU/内存优化路径，一部分使用量化权重或专用实现。它尤其常被用于 MoE、DeepSeek/Qwen/GLM/Kimi/MiniMax 系列和显存不足但系统内存较大的机器。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# KTransformers 参数模型

KTransformers 面向本地和低成本部署，核心思想是把大模型中的不同算子、层或专家映射到不同后端：一部分走 GPU kernel，一部分走 CPU/内存优化路径，一部分使用量化权重或专用实现。它尤其常被用于 MoE、DeepSeek/Qwen/GLM/Kimi/MiniMax 系列和显存不足但系统内存较大的机器。

当前主线更偏 `kt-kernel` 与 SGLang-KT：用 SGLang 提供服务、调度和 attention 路径，用 KTransformers/KT kernel 优化 CPU 侧 MoE expert 和异构放置。旧的 YAML operator injection 仍有参考价值，但生产前要区分当前 kt-kernel 路径和历史教程。

## 参数面

| 参数面 | 常见配置 | 作用 |
|---|---|---|
| 模型加载 | model path、tokenizer、config、revision、trust remote code | 决定加载哪个 HF/GGUF/量化 artifact |
| 配置注入 | YAML / rule-based operator override | 把 attention、MLP、MoE expert、linear 层映射到不同实现 |
| 设备映射 | CUDA device、CPU、NUMA、内存映射、offload | 控制权重和计算落在哪里 |
| 量化 | GGUF、Marlin、低比特权重、KV/cache dtype | 降低显存/内存和带宽压力 |
| 服务接口 | local generate、OpenAI-compatible server、host/port | 把本地运行时暴露给客户端 |
| 调度与缓存 | context length、KV cache、batch、prefill/decode 路径 | 控制上下文、延迟和内存占用 |

## kt-kernel / SGLang-KT 参数

| 参数 | 含义 | 调参方向 |
|---|---|---|
| `kt run <model>` / `kt chat` / `kt doctor` | 启动服务、连接服务、检查环境 | 快速验证硬件和模型路径 |
| `python -m sglang.launch_server ...` | 当前完整服务入口之一 | 需要和 SGLang 参数一起调 |
| `--kt-method` | CPU/MoE 权重精度与 kernel 路径，如 BF16、FP8、RAWINT4、AMXINT4、GPTQ_INT4 | 越低比特越省内存，但质量和 kernel 支持要验证 |
| `--kt-weight-path` | KT CPU 权重路径 | 避免每次启动重新转换或查找 |
| `--kt-cpuinfer` | CPU 推理线程数 | 通常不应超过物理核心；要结合 NUMA |
| `--kt-threadpool-count` | 线程池数量 | 常按 NUMA node 数设置 |
| `--kt-num-gpu-experts` | 每层放到 GPU 的 expert 数 | 增大可降低 CPU 压力，但增加 VRAM |
| `--kt-gpu-experts-ratio` | 按比例放 GPU expert | 设置后可能覆盖固定 expert 数 |
| `--kt-expert-placement-strategy` | `uniform`、`frequency`、`front-loading`、`random` | frequency 依赖真实 workload 统计 |
| `--init-expert-location` | expert 热度/放置初始文件 | 统计数据过期会误导放置 |
| `--kt-enable-dynamic-expert-update` | 推理中动态更新 expert 放置 | 可改善热 expert 命中，也会增加系统复杂度 |
| `--kt-gpu-prefill-token-threshold` | 长 prefill 下触发专家重分布/Layerwise Prefill | 影响 TTFT 和 GPU/CPU 重叠 |

KTransformers 的重要区别是：很多性能行为不只由 CLI 参数决定，还由 YAML/rule 配置决定。一个模型“能加载”不代表 attention、MoE expert、MLP 都落在期望后端上。

## Heterogeneous inference

传统 GPU serving 通常试图把整个模型放进 GPU；KTransformers 更像“算子级分工”：

- Attention / MLA 这类对延迟敏感、GPU 友好的算子尽量放 GPU。
- MoE expert 权重很大但每个 token 只激活少数 expert，可考虑 CPU/内存侧或分层 offload。
- Linear/MLP 可根据量化格式、batch 和设备带宽选择专用 kernel。
- KV cache 放置要和 attention 后端匹配，否则每步 decode 会被搬运拖慢。
- Expert Deferral 一类策略会把部分 expert 计算延后，与 GPU attention 或后续阶段重叠，以提高 CPU/GPU 并行度。

这种路线适合显存不够、但 CPU 内存充足且可接受较高单 token 延迟的场景；不适合对 p99 延迟和高并发吞吐要求很硬的在线服务。

## MoE 调参重点

| 目标 | 优先检查 |
|---|---|
| 降低显存 | expert 权重 offload、低比特量化、只把热路径放 GPU |
| 降低 TPOT | active expert 是否频繁跨 PCIe 访问、CPU 内存带宽是否满 |
| 降低 TTFT | attention/prefill 是否在 GPU，长 prompt 是否触发大量权重搬运 |
| 稳定输出 | tokenizer/template、量化格式、expert 实现和 dtype 是否固定 |
| 减少冷启动 | 预转换 artifact、固定 YAML、避免启动时大量转换 |

## 常见误区

- 把“显存够了”当成“速度够了”：CPU offload 会把瓶颈转移到内存带宽和 PCIe。
- YAML/rule 没版本化：旧 operator injection 规则按匹配顺序生效，同一模型路径配不同规则，性能和数值都可能变化。
- 只看平均 tokens/s：MoE expert 命中不同，尾延迟可能很散。
- 忽略 NUMA：多路 CPU 或多 GPU 机器上，权重所在内存节点和 GPU 拓扑会明显影响性能。
- 让热 expert 统计脱离真实 workload：frequency 放置可能反而拖慢。
- 把它当成 vLLM 替代品：KTransformers 更偏本地/异构优化，不一定提供同等成熟的队列、监控和多租户控制面。

## 相关页面

- [MoE serving 与 expert parallel](moe-serving-and-expert-parallel.md)
- [Offload 与内存层级](offload-and-memory-hierarchy.md)
- [CPU、边缘与 NPU 推理](cpu-edge-npu-inference.md)
- [模型格式、加载与供应链边界](model-formats-and-loading.md)
- [GPU 拓扑、隔离与集群资源](gpu-topology-and-isolation.md)

## 关键来源

- KTransformers documentation: https://kvcache-ai.github.io/ktransformers/
- KTransformers GitHub: https://github.com/kvcache-ai/ktransformers
- KTransformers README: https://github.com/kvcache-ai/ktransformers/blob/main/README.md
- KTransformers DeepSeek R1/V3 tutorial: https://github.com/kvcache-ai/ktransformers/blob/main/doc/en/DeepseekR1_V3_tutorial.md
- KTransformers kt-kernel README: https://github.com/kvcache-ai/ktransformers/blob/main/kt-kernel/README.md
- KTransformers expert scheduling: https://github.com/kvcache-ai/ktransformers/blob/main/doc/en/kt-kernel/experts-sched-Tutorial.md
- KTransformers native precision: https://github.com/kvcache-ai/ktransformers/blob/main/doc/en/kt-kernel/Native-Precision-Tutorial.md
- KTransformers DeepSeek V3.2 + SGLang-KT: https://github.com/kvcache-ai/ktransformers/blob/main/doc/en/kt-kernel/deepseek-v3.2-sglang-tutorial.md
- KTransformers prefix cache: https://github.com/kvcache-ai/ktransformers/blob/main/doc/en/prefix_cache.md
- KTransformers balance serve: https://github.com/kvcache-ai/ktransformers/blob/main/doc/en/balance-serve.md
- KTransformers SOSP 2025 paper page: https://madsys.cs.tsinghua.edu.cn/publication/ktransformers-unleashing-the-full-potential-of-cpu/gpu-hybrid-inference-for-moe-models/
