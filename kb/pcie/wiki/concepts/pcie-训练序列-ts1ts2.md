---
title: PCIe 训练序列 (TS1/TS2)
summary: 链路初始化过程中交换的训练序列，用于建立位锁定、符号锁定以及协商链路参数
sources:
- pcie-ltssm.md
kind: concept
createdAt: '2026-08-16T06:41:15.342Z'
updatedAt: '2026-08-16T06:41:15.342Z'
tags:
- PCIe
- 信号完整性
- 链路初始化
aliases:
- pcie-训练序列-ts1ts2
- P训(
confidence: 0.9
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: 训练序列（Training Sequence，TS）是 PCIe 物理层链路训练过程中发送的特殊符号序列，用于建立位锁定、符号锁定以及在链路两端交换配置信息。TS1
  和 TS2 是两种主要的训练序列，分别用于不同的训练阶段。^[pcie-ltssm.md:124-144]
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCIe 训练序列 (TS1/TS2)

训练序列（Training Sequence，TS）是 PCIe 物理层链路训练过程中发送的特殊符号序列，用于建立位锁定、符号锁定以及在链路两端交换配置信息。TS1 和 TS2 是两种主要的训练序列，分别用于不同的训练阶段。^[pcie-ltssm.md:124-144]

## 概述

PCIe 链路在初始化过程中必须经过严格的训练才能进入正常工作状态。训练序列在这一过程中承担着关键作用，它们通过特定的比特模式帮助接收端建立同步，并携带配置信息供双方协商链路参数。^[pcie-ltssm.md:119-127]

### TS1 与 TS2 的区别

| 特性 | TS1 | TS2 |
|------|------|------|
| 用途 | 初始训练，建立位锁定 | 配置准备，进入 Configuration |
| 发送阶段 | Polling.Active | Polling.Configuration |
| 包含信息 | 链路和 Lane 基本信息 | 更详细的配置参数 |

^[pcie-ltssm.md:142-144]

## 在 LTSSM 中的角色

训练序列由 LTSSM（链路训练与状态状态机）控制发送，其使用贯穿多个关键状态：

### Polling 状态

Polling 状态是训练序列的主要使用阶段，包含以下子状态：

- **Polling.Active**：发送 TS1 序列，建立比特锁定（Bit Lock）
- **Polling.Configuration**：发送 TS2 序列，准备进入 Configuration 阶段
- **Polling.Compliance**：合规性测试模式 ^[pcie-ltssm.md:128-131]

### Recovery 状态

当链路发生错误需要恢复时，也会重新发送 TS1/TS2 序列。该状态的子状态包括：

- **Recovery.RcvrLock**：重新建立接收锁定
- **Recovery.RcvrCfg**：重新配置接收端
- **Recovery.Idle**：等待链路空闲
- **Recovery.Speed**：速度切换 ^[pcie-ltssm.md:286-290]

L1 状态退出时需要通过 TS1 序列快速重训练恢复链路同步。^[pcie-ltssm.md:241-244]

## TS1/TS2 字段结构

训练序列携带以下关键字段信息：

| 字段 | 含义 | 用途 |
|------|------|------|
| **Link Number** | 链路编号 | 标识当前训练的链路 |
| **Lane Number** | Lane 编号 | 用于去倾斜（De-skew），处理多 Lane 布线差异 |
| **Data Rate** | 支持的速度标识 | 协商双方共同支持的最高速度 |
| **Training Control** | 训练控制位 | 控制训练进程、复位请求等 |

^[pcie-ltssm.md:133-141]

## 训练流程

### 1. 位锁定与符号锁定

接收端在收到连续的 TS1/TS2 序列后，通过检测固定的比特模式来建立位锁定，从而正确识别比特边界。随后通过识别 10-bit 符号（Gen 1/2）或 130-bit 块（Gen 3+）的边界实现符号锁定。^[pcie-ltssm.md:119-127]

### 2. 去倾斜

在多 Lane 链路（如 x4、x8、x16）中，不同 Lane 的信号可能因布线长度差异而到达时间不同。TS1/TS2 中的 Lane Number 字段允许接收端识别每个符号所属的 Lane，并补偿这些延迟差异。^[pcie-ltssm.md:176]

### 3. 链路配置协商

通过 TS1/TS2 交换能力信息后，双方确定：

- 最终激活的 Lane 数量（可能发生宽度降级）
- 链路速度（Gen 1/2/3/4/5）
- Lane 极性反转是否启用
- 扰码器状态 ^[pcie-ltssm.md:148-155]

## 与其他 PCIe 概念的关联

训练序列是 PCIe 链路建立的核心机制，与多个关键概念紧密相关：

- PCIe LTSSM 状态机：训练序列由 LTSSM 控制发送
- [[PCIe 链路速度与编码]]：TS1/TS2 用于协商数据速率（2.5/5.0/8.0/16.0/32.0 GT/s）
- PCIe 链路配置与宽度协商：TS2 序列携带宽度协商信息
- PCIe 电源管理 (ASPM)：L1 状态退出依赖 TS1 重训练
- [[PCIe Recovery 状态]]：错误恢复时重新发送训练序列

---

## Sources

- [LTSSM 状态机详解](../../sources/pcie-ltssm.md) - 包含 TS1/TS2 在 Polling 和 Recovery 状态中的应用（第 119-144 行，241-244 行，286-290 行）

