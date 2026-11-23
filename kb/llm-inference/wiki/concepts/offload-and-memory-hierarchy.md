---
type: Concept
title: Offload 与内存层级
description: Offload 用更慢、更大的内存层级换取更大的模型、上下文或并发。它能让系统“跑起来”，但不保证更快。推理系统要同时考虑 HBM、CPU
  RAM、pinned memory、NVLink/PCIe 和磁盘/cache。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Offload 与内存层级

Offload 用更慢、更大的内存层级换取更大的模型、上下文或并发。它能让系统“跑起来”，但不保证更快。推理系统要同时考虑 HBM、CPU RAM、pinned memory、NVLink/PCIe 和磁盘/cache。

## 内存层级

| 层级 | 特点 | 常见用途 |
|---|---|---|
| GPU HBM | 最快、容量最小 | 权重、KV cache、activation、workspace |
| CPU RAM | 容量大、延迟高 | 权重 offload、KV offload、缓存池 |
| Pinned host memory | CPU 内存中可高效 DMA 的页锁定区域 | GPU/CPU 异步传输 staging |
| Unified/managed memory | CUDA 统一地址空间，按需迁移 | 简化编程，性能需谨慎验证 |
| SSD/磁盘 | 容量最大、延迟最高 | 模型加载、冷缓存 |

CUDA 文档把 host memory 和 device memory 视为独立 DRAM 空间；Unified Memory 提供统一地址空间并支持迁移/oversubscription，但 page fault 和迁移延迟可能把 p99 拉高。NVLink/NVSwitch 则决定 GPU-GPU 或 MoE all-to-all 是否能承受高通信量。

## 权重 offload

权重 offload 把部分权重放到 CPU RAM，计算时再搬到 GPU 或让部分层在 CPU 执行。它适合显存不够的单机部署，但 decode 时反复访问权重，PCIe 传输很容易成为瓶颈。

典型参数：

- `--cpu-offload-gb`
- `--offload-backend`
- `--offload-group-size`
- `--offload-num-in-group`
- `--offload-prefetch-step`
- `--gpu-layers`
- `--n-gpu-layers`
- backend/device map

## KV cache offload

KV cache offload 把不活跃或低优先级的 KV block 移出 GPU HBM。它适合长上下文、多会话、prefix cache 复用明显的服务。代价是 cache miss 时要把 KV 搬回 GPU，可能拉高 TPOT 或尾延迟。

典型参数：

- `kv-offloading-size`
- `kv-offloading-backend`
- `kv_cache_config.host_cache_size`
- `kv_cache_config.secondary_offload_min_priority`
- `cache_size`
- hierarchical cache / LMCache 相关配置

TensorRT-LLM 的 host cache 适合“驱逐到 CPU 后仍可能再次命中”的 KV block；如果某些 block 价值太低，可以用 secondary offload priority 让它们直接驱逐，避免浪费 CPU/GPU 传输。

## PCIe 与 NVLink

Offload 的真实速度常由互连决定：

- PCIe 带宽和延迟远弱于 HBM。
- NVLink/NVSwitch 更适合跨 GPU KV/activation/专家通信。
- 多 NUMA CPU 机器要注意 GPU 连接到哪个 CPU socket。

## Pinned memory

Pinned memory 可以让 GPU DMA 更高效，并支持异步拷贝。但它会占用不能被操作系统随意换出的物理内存；过量使用会影响系统整体内存管理。

## 调参建议

- 只为“能跑”而 offload 权重是合理的；追求低延迟时要谨慎。
- 长上下文服务优先考虑 KV cache dtype、prefix cache、context parallel，再考虑 KV offload。
- 使用 offload 后必须看 p95/p99，而不是只看平均吞吐。
- 多 GPU 系统先看拓扑，再决定把哪部分 offload 到哪里。
- 生产环境要给 CUDA graph、activation、通信 buffer 留 HBM 余量。

## 关键来源

- vLLM Engine Arguments: https://docs.vllm.ai/en/stable/configuration/engine_args/
- vLLM config API: https://docs.vllm.ai/en/stable/api/vllm/config/
- TensorRT-LLM KV Cache System: https://nvidia.github.io/TensorRT-LLM/features/kvcache.html
- SGLang HiCache: https://docs.sglang.io/docs/advanced_features/hicache
- NVIDIA CUDA C Programming Guide: https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html
- NVIDIA CUDA Unified Memory: https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/unified-memory.html
- NVIDIA NVLink: https://www.nvidia.com/en-us/data-center/nvlink/
- llama.cpp server README: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
