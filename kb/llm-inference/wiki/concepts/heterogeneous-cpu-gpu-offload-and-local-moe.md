---
type: Concept
title: CPU/GPU 混合 Offload 与本地 MoE 推理
description: 当模型太大、GPU 显存不够，或者 MoE 模型的 expert 权重远大于每 token 实际激活量时，部署者会考虑 CPU/GPU 混合推理：把一部分权重、KV
  cache 或 expert 放在 CPU/系统内存，把延迟敏感计算留在 GPU。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# CPU/GPU 混合 Offload 与本地 MoE 推理

当模型太大、GPU 显存不够，或者 MoE 模型的 expert 权重远大于每 token 实际激活量时，部署者会考虑 CPU/GPU 混合推理：把一部分权重、KV cache 或 expert 放在 CPU/系统内存，把延迟敏感计算留在 GPU。

这不是“免费扩显存”。它是在显存、系统内存、PCIe/NVLink、NUMA 和内存带宽之间重新分配瓶颈。

## 可以 offload 什么

| 对象 | Offload 后的收益 | 主要代价 |
|---|---|---|
| 权重层 | 模型能在小显存机器上跑 | 每层访问跨 PCIe/内存，TPOT 上升 |
| MoE expert | 只把活跃 expert 或热 expert 放 GPU | expert routing 不稳定会造成尾延迟 |
| KV cache | 支持更长上下文或更多会话 | 每步 attention 可能产生 KV 读写搬运 |
| Embedding / lm_head | 降低少量显存 | 可能增加首尾 token latency |
| 预处理 / tokenizer | 减少 GPU 外工作 | CPU worker 不足会抬高 TTFT |

## MoE 为什么特殊

Dense 模型每个 token 通常经过大部分权重；MoE 模型每个 token 只激活少数 expert，但所有 expert 权重都要可用。因此 MoE 更适合分层放置：

- Router、attention、共享层尽量放 GPU。
- 热 expert 可常驻 GPU。
- 冷 expert 或全部 expert 可放 CPU/内存，按需加载或访问。
- 如果 expert 每步都跨 PCIe 取权重，decode 会被传输拖住。
- 对 DeepSeek-V2 一类 MLA 架构，压缩 KV cache 能显著降低长上下文 KV 压力，但 attention/backend 支持和模板仍要对齐。

这类策略在 DeepSeek 等大 MoE 模型的本地部署中很常见，但收益高度依赖模型、量化、prompt 分布和硬件拓扑。

## 关键预算

| 预算 | 粗略判断 |
|---|---|
| GPU 显存 | 能放多少热权重、KV cache、activation 和 batch |
| 系统内存 | 能否容纳 offload 权重、page cache 和并发会话 |
| PCIe/NVLink | 每 token 需要搬多少权重/KV，链路是否成为 TPOT 瓶颈 |
| CPU 内存带宽 | expert/权重在 CPU 侧计算或解码时是否被带宽限制 |
| NUMA 拓扑 | CPU 内存节点和 GPU 是否跨 socket |
| 冷启动 | 权重 mmap、量化转换、page fault、cache warmup |

## 调参路径

1. 先确定目标：能跑、低延迟、低成本，还是长上下文。
2. 固定模型 artifact 和量化格式，再比较 offload 策略。
3. 记录每层/每 expert 的真实设备放置，不要只记录“启用了 offload”。
4. 用 TTFT、TPOT、p95/p99、page fault、CPU memory bandwidth、PCIe throughput 一起看。
5. 长上下文时同时估算 KV cache bytes；只 offload 权重可能仍然 OOM。
6. 多 socket 机器检查 NUMA binding、GPU locality 和线程亲和性。
7. 区分“CPU 直接算 expert”和“每步把 expert 搬到 GPU”：后者很容易被 PCIe 带宽卡死。

## 适合与不适合

适合：

- 单用户或低并发本地推理。
- 显存不足但系统内存充足。
- 大 MoE 模型，活跃 expert 少。
- 离线 batch 或可接受较高延迟的任务。

不适合：

- 严格 p99 在线服务。
- 高并发、多租户、长 streaming。
- PCIe 带宽弱或 NUMA 拓扑复杂但不可控。
- 需要逐 token 稳定复现的评估。

## 常见误区

- 只看模型加载成功：decode 速度可能慢到不可用。
- 只测短 prompt：长上下文会把 KV cache 和 page fault 问题暴露出来。
- 混用多个 offload 机制：权重 offload、KV offload、UVM、mmap 同时开时很难定位瓶颈。
- 忽略 page cache：第一次请求慢和后续请求快可能只是 OS cache warmup。
- 让网关无限排队：慢本地 runtime 会把上游请求堆成尾延迟。

## 相关页面

- [Offload 与内存层级](offload-and-memory-hierarchy.md)
- [MoE serving 与 expert parallel](moe-serving-and-expert-parallel.md)
- [KTransformers 参数模型](ktransformers-runtime-parameters.md)
- [llama.cpp 参数模型](llama-cpp-runtime-parameters.md)
- [CPU、边缘与 NPU 推理](cpu-edge-npu-inference.md)
- [推理容量规划公式](capacity-planning-formulas.md)

## 关键来源

- KTransformers documentation: https://kvcache-ai.github.io/ktransformers/
- KTransformers SOSP 2025 paper page: https://madsys.cs.tsinghua.edu.cn/publication/ktransformers-unleashing-the-full-potential-of-cpu/gpu-hybrid-inference-for-moe-models/
- KTransformers expert scheduling: https://github.com/kvcache-ai/ktransformers/blob/main/doc/en/kt-kernel/experts-sched-Tutorial.md
- llama.cpp server README: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- vLLM KV offloading: https://docs.vllm.ai/en/stable/features/kv_offloading_usage/
- TensorRT-LLM KV cache system: https://nvidia.github.io/TensorRT-LLM/features/kvcache.html
- NVIDIA CUDA Unified Memory: https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/unified-memory.html
- NVIDIA NVLink: https://www.nvidia.com/en-us/data-center/nvlink/
- DeepSeek-V2 paper: https://arxiv.org/abs/2405.04434
- FlexGen paper: https://arxiv.org/abs/2303.06865
