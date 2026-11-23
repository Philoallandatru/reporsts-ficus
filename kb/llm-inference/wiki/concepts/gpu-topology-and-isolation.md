---
type: Concept
title: GPU 拓扑、隔离与集群资源
description: LLM 推理参数里很多“看似框架内部”的问题，其实来自硬件拓扑：GPU 之间怎么连、进程怎么共享 GPU、Kubernetes 怎么暴露
  GPU、监控能看到哪些计数器。TP/PP/EP、KV transfer、offload 和多实例部署都绕不开这一层。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# GPU 拓扑、隔离与集群资源

LLM 推理参数里很多“看似框架内部”的问题，其实来自硬件拓扑：GPU 之间怎么连、进程怎么共享 GPU、Kubernetes 怎么暴露 GPU、监控能看到哪些计数器。TP/PP/EP、KV transfer、offload 和多实例部署都绕不开这一层。

## 拓扑决定什么

| 拓扑/资源 | 影响 |
|---|---|
| PCIe | CPU-GPU、GPU-GPU 经主机侧传输；offload 和跨卡通信更容易受限 |
| NVLink / NVSwitch | 高带宽 GPU-GPU 互连，适合 TP、EP all-to-all、KV transfer |
| NUMA | CPU tokenizer、pinned memory、network/NIC 与 GPU 亲和性 |
| MIG | 把一张支持 MIG 的 GPU 切成多个隔离实例 |
| MPS | 多进程共享同一 GPU，上下文切换更轻，但隔离弱于 MIG |
| GPUDirect RDMA | NIC 与 GPU 直接传输，适合跨节点 KV transfer / distributed inference |

容量规划时不要只看“几张卡”。同样是 8 GPU，NVSwitch 机器和 PCIe 机器对 tensor parallel、expert parallel、disaggregated serving 的上限完全不同。

## MIG 与 MPS

### MIG

MIG 把一张 GPU 分成多个 GPU instance，每个 instance 有独立的计算、显存、cache 和内存带宽切片。它适合：

- 多租户小模型或 embedding/rerank 服务。
- 需要更强资源隔离和 predictable QoS 的场景。
- 把大 GPU 切给多个低负载服务。

它不适合需要整卡显存或高带宽跨 slice 通信的大 LLM。Tensor parallel 跨 MIG slice 通常不是理想路线；大模型更常用整卡或多整卡。

### MPS

MPS 让多个 CUDA 进程共享同一 GPU execution context，减少多进程上下文切换开销。它适合小 kernel、多进程轻推理或低利用率场景。

注意：

- MPS 不是强隔离，故障和资源争用会互相影响。
- MPS 不能替代 serving engine 的 continuous batching。
- LLM 大 batch decode 通常更应该在一个 engine 内合批，而不是让多个进程抢同一 GPU。

## Kubernetes GPU 暴露

Kubernetes 通常通过 NVIDIA device plugin 把 GPU 暴露成资源，例如 `nvidia.com/gpu: 1`。GPU Operator 则把 driver、container toolkit、device plugin、DCGM exporter 等组件打包成集群级安装和生命周期管理。

常见参数/概念：

| 参数/概念 | 作用 |
|---|---|
| `resources.limits.nvidia.com/gpu` | Pod 申请 GPU 数量 |
| `NVIDIA_VISIBLE_DEVICES` | 容器内可见 GPU/MIG device |
| `CUDA_VISIBLE_DEVICES` | CUDA 进程内可见设备顺序与集合 |
| `CUDA_DEVICE_ORDER=PCI_BUS_ID` | 让 CUDA 设备枚举顺序更贴近 PCI bus 顺序，方便和 `nvidia-smi` 对齐 |
| device plugin `deviceListStrategy` | GPU id 通过 envvar、volume mount、CDI 等方式注入 |
| MIG strategy | 集群是否把 MIG slice 暴露为可调度资源 |
| DCGM exporter | 暴露 GPU 利用率、显存、温度、功耗、XID、NVLink 等指标 |

`CUDA_VISIBLE_DEVICES=2,1` 不只是隐藏设备，也会重映射进程内 device ordinal：程序看到的 `cuda:0` 可能对应物理 GPU 2。排查多进程或容器内 GPU 绑定时，要同时记录物理 id、UUID、容器注入变量和框架内部 device id。

## NCCL 与通信

Tensor parallel、pipeline parallel、expert parallel 和分布式 KV transfer 都可能依赖 NCCL 或其他通信库。常见排查点：

- NCCL 是否识别到 NVLink/NVSwitch 或 RDMA。
- 多机环境变量、网络接口、IB/RDMA 设置是否一致。
- 容器内是否有正确的驱动、CUDA、NCCL 和设备文件。
- `NCCL_DEBUG=INFO` 可用于查看拓扑和连接路径。

如果通信走错路径，表现常常不是直接失败，而是 TP/EP 后吞吐不升反降。

## 调参判断

| 症状 | 可能原因 | 优先动作 |
|---|---|---|
| TP 后更慢 | GPU 间通信走 PCIe/网络瓶颈 | 查看 NCCL 拓扑、NVLink、IB/RDMA |
| 同卡多实例互相影响 | 多进程抢显存/SM/cache | 改用单 engine 合批、MIG、或明确显存预算 |
| offload p99 很差 | CPU/GPU/NIC 拓扑和带宽不够 | 绑定 NUMA、减少 offload、用 pinned memory |
| Kubernetes Pod 看不到 GPU | device plugin / runtime class / env 注入问题 | 检查 GPU Operator、device plugin、容器运行时 |
| GPU metrics 缺失 | DCGM exporter 或权限配置不对 | 检查 exporter、Prometheus scrape 和 pod 权限 |

## 与其他机制的关系

- [多 GPU 并行推理](distributed-parallel-inference.md)：并行策略必须匹配硬件互连。
- [Disaggregated serving 与 KV transfer](disaggregated-serving-and-kv-transfer.md)：KV transfer 上限取决于 GPU/NIC/网络。
- [Offload 与内存层级](offload-and-memory-hierarchy.md)：CPU/GPU 传输路径直接影响尾延迟。
- [推理容量规划公式](capacity-planning-formulas.md)：显存之外还要算通信和带宽。

## 关键来源

- NVIDIA MIG User Guide: https://docs.nvidia.com/datacenter/tesla/mig-user-guide/
- NVIDIA MIG introduction: https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/introduction.html
- NVIDIA MPS: https://docs.nvidia.com/deploy/mps/
- NVIDIA MPS when to use: https://docs.nvidia.com/deploy/mps/when-to-use-mps.html
- NVIDIA NCCL overview: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/overview.html
- NVIDIA NCCL environment variables: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html
- CUDA environment variables: https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/environment-variables.html
- NVIDIA Kubernetes Device Plugin: https://github.com/NVIDIA/k8s-device-plugin
- NVIDIA GPU Operator: https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/
- NVIDIA Kubernetes GPU docs: https://docs.nvidia.com/datacenter/cloud-native/kubernetes/latest/index.html
- NVIDIA DCGM exporter: https://github.com/NVIDIA/dcgm-exporter
- NVIDIA DCGM feature overview: https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html
- NVIDIA DCGM docs: https://docs.nvidia.com/datacenter/dcgm/latest/index.html
- NVIDIA DCGM exporter install: https://docs.nvidia.com/datacenter/dcgm/latest/installation/install-dcgm-exporter.html
- NVIDIA NVLink: https://www.nvidia.com/en-us/data-center/nvlink/
