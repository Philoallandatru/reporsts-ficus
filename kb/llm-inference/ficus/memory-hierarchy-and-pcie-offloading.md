---
type: Concept
title: 电脑硬件与推理数据流入门：SSD、内存、PCIe 与显存
description: 用厨房类比讲透大模型运行时数据如何从硬盘流向显卡：mmap、缺页中断、Page Cache、PCIe 带宽瓶颈，以及 Nsight Profiling
  在看什么。
tags:
- llm
- beginner
- memory-hierarchy
- pcie
- profiling
createdAt: '2026-11-22'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 电脑硬件与推理数据流入门：SSD、内存、PCIe 与显存

跑本地大模型慢，80% 的时候不是显卡算力不够，而是**“数据在路上堵车了”**。把电脑里的存储层级想象成一个餐厅厨房，就能立刻看懂所有引擎的区别。

---

## 一、 四层存储架构与速度鸿沟

| 硬件层级 | 厨房类比 | 典型容量（本机） | 实测/典型速度 | 角色 |
|---|---|---:|---:|---|
| **GPU 显存 (VRAM)** | **主厨手边 1 米的切菜台** | 16 GiB (RTX 5080) | **~960 GB/s** | 放模型热点权重、当前 KV 缓存，算力直接伸手拿 |
| **PCIe 总线** | **连接厨房与储藏室的窄门** | — | **~32.6 GB/s** | 所有内存与显存之间的数据搬运都得过这扇门（慢 ~30 倍！） |
| **主机内存 (RAM)** | **走廊尽头的储藏室** | 87.4 GiB | ~60–90 GB/s | 放不进显存的 MoE 冷专家、被换出的长上下文 KV 历史 |
| **NVMe SSD 硬盘** | **楼下的地下冷库** | 数 TB | ~3–7 GB/s | 存放几十到上百 GB 的 GGUF 模型文件 |

**核心规律**：每往下一层，容量大 10 倍，但速度慢 10~30 倍。

---

## 二、 引擎加载模型的两种方式：`mmap` vs 预打包 `Arena`

1. **什么是 `mmap`（内存映射）与缺页中断（Page Fault）？**
   - `llama.cpp` 默认常用 `mmap`：启动时**并不真把 60 GB 模型读进内存**，而是向操作系统登记一张“虚拟地图”（所以 22 秒就能启动）。
   - 等推理真正用到某一块权重时，CPU 发现“这块还没进内存”，就会触发一次**缺页中断（Page Fault）**，临时从 SSD 或操作系统的 **Page Cache（文件页缓存）** 里把那一小块拉进物理内存（我们在实测里看到进程内存 RSS 从 `7.3 GB` 一路爬升到 `38.5 GB`）。
2. **什么是 Direct I/O / 预打包 Arena？**
   - 像 `Strata` 在内存充足时，会在启动阶段花几十秒主动把所有专家解包重排进一块连续的内存区域（`Expert Arena`），推理期间**零缺页抖动**；内存不够时则通过 Direct I/O 有界地按需从 SSD 读。

---

## 三、 看懂性能监测与 Profiling 里的常见词

当用 **Nsight Systems (`nsys`)** 对推理过程做显微级抓包时，最常看到这 4 个指标：

1. **H2D / D2H / D2D**：
   - **H2D (Host to Device)**：主机内存 → 显卡显存（比如上传未命中的专家或召回 KV）。
   - **D2H (Device to Host)**：显卡显存 → 主机内存（比如把选中的专家 ID 传回 CPU，或把旧 KV 换出到内存）。
   - **D2D (Device to Device)**：显卡显存内部自己腾挪整理。
2. **`cudaStreamSynchronize`（同步死等）**：
   - CPU 让 GPU 停下来等某件事做完（比如等 H2D 搬运完成）。在 `llama.cpp` 的 profiling 中，这一项经常占掉 CUDA API 耗时的 60% 以上，是 GPU 空转的主要元凶。
3. **CUDA Graph（计算图打包）**：
   - 正常情况下，CPU 要一条一条发指令叫 GPU 干活（发几万次指令本身就很慢）。CUDA Graph 把几百上千个算子预先录成“一整套宏动作”，CPU 只需喊一嗓子（`cudaGraphLaunch`）就能连续执行，极大减少 CPU-GPU 沟通成本。
4. **SMs Active（显卡核心活跃度）**：
   - 显卡里的计算核心真正忙起来的时间比例。如果算力核心活跃度只有 37%（比如在等 PCIe 传数据），说明瓶颈在**数据传输/同步**而不是显卡算力。

## 相关链接
- [[llm-inference-basics-and-kv-cache|大模型推理入门：Prefill、Decode、TTFT 与 KV Cache]]
- [[strata-vs-llamacpp-profiling-and-scenarios|Strata 与 llama.cpp 多场景实测、Nsight Profiling 与模块学习路线]]
