---
title: Power Management DLLP
summary: 电源管理DLLP，包括PM_Enter_L1/L23和PM_Request_Ack用于协商低功耗状态
sources:
- pcie-dllp-format.md
kind: concept
createdAt: '2026-08-16T06:37:28.332Z'
updatedAt: '2026-08-16T06:37:28.332Z'
tags:
- pcie
- power-management
- low-power
aliases:
- power-management-dllp
- PMD
confidence: 1
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: DLLP 是 PCIe 数据链路层专用的控制包，与承载用户数据的 TLP 不同，DLLP 承载链路控制信息。电源管理 DLLP 是其五大功能类别之一，用于协商电源状态转换。^[pcie-dllp-format.md:3-13]
  电源管理 DLLP 包括以下类型：^[pcie-dllp-format.md:86-90]
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Power Management DLLP

**Power Management DLLP**（电源管理数据链路层数据包）是 PCIe 数据链路层用于协商链路电源状态的专用控制包。它通过在两端端口之间交换 PM DLLP，实现从正常工作状态到低功耗状态的平滑转换，从而降低链路能耗。^[pcie-dllp-format.md:23-24]

## 概述

DLLP 是 PCIe 数据链路层专用的控制包，与承载用户数据的 TLP 不同，DLLP 承载链路控制信息。电源管理 DLLP 是其五大功能类别之一，用于协商电源状态转换。^[pcie-dllp-format.md:3-13] 电源管理 DLLP 包括以下类型：^[pcie-dllp-format.md:86-90]

| Type 值 | 名称 | 用途 | 方向 |
|---------|------|------|------|
| 0x20 | PM_Enter_L1 | 请求进入 L1 状态 | 双向 |
| 0x21 | PM_Enter_L23 | 请求进入 L2/L3 状态 | 下游→上游 |
| 0x24 | PM_Active_State_Request_L1 | 请求从 L1 退出到 L0 | 双向 |
| 0x30 | PM_Request_Ack | 电源管理请求确认 | 双向 |

## PM_Enter_L1

**PM_Enter_L1** 用于请求进入 L1 低功耗状态，是一种双向协商的电源管理机制。^[pcie-dllp-format.md:334-336]

### 格式

```
Byte 0-1:
┌─────────────┬──────────────────┐
│ Type = 0x20 │ Reserved         │
└─────────────┴──────────────────┘

Byte 2-5: Reserved (全 0)

Byte 6-7: CRC-16
```

PM_Enter_L1 DLLP 的有效载荷部分为空（Reserved 全 0），电源状态协商完全由 Type 字段和 PM_Request_Ack 确认机制完成。^[pcie-dllp-format.md:338-348]

### 进入 L1 流程

```
Port A 空闲检测：无 TLP 传输超过 T(idle)
  ↓
Port A: 发送 PM_Enter_L1 DLLP
  ↓
Port B: 收到 PM_Enter_L1
  ↓
Port B: 发送 PM_Request_Ack DLLP
  ↓
两端进入 L1 状态
```

当检测到链路空闲超过指定时间后，上游端口主动发送 PM_Enter_L1 请求。目标端口收到请求后，必须回复 PM_Request_Ack 确认，两端才能同步进入 L1 状态。^[pcie-dllp-format.md:350-364]

### L1 状态特性

进入 L1 状态后，链路两端会采取以下节能措施：^[pcie-dllp-format.md:360-363]

- **关闭 TX/RX 高速电路**：停止高速收发器以节省功耗
- **保持参考时钟**：保留参考时钟供给，以便快速恢复到工作状态
- **延迟要求**：L1 状态进入/退出延迟小于 10 微秒

L1 状态属于 ASPM（Active State Power Management）范畴，是一种硬件自动管理的低功耗状态，无需软件介入即可实现节能。^[pcie-dllp-format.md:566-574]

## PM_Enter_L23

**PM_Enter_L23** 用于请求进入 L2/L3 深度睡眠状态，其传输方向仅限于从下游设备指向上游 Root Complex 或 Switch。^[pcie-dllp-format.md:366-371]

### 方向限制

PM_Enter_L23 必须从下游端口（设备）向上游端口（RC/Switch）发送，这一方向限制确保了电源管理请求的合理性——通常由系统电源管理事件触发，而非链路上的随机协商。^[pcie-dllp-format.md:370]

### 进入 L2/L3 流程

```
系统电源管理事件（如休眠）
  ↓
Root Complex: 广播 PME_Turn_Off Message
  ↓
设备: 停止发送 TLP
  ↓
设备: 发送 PM_Enter_L23 DLLP（如果是 Active 状态）
  ↓
Root Complex: 收到所有设备的 PM_Enter_L23
  ↓
进入 L2/L3 状态
```

该流程由系统电源管理事件触发，Root Complex 首先广播 PME_Turn_Off 消息通知所有设备准备进入低功耗状态。设备收到通知后停止发送新的 TLP，并回复 PM_Enter_L23 DLLP。Root Complex 收集所有设备的确认后，协调整个链路进入 L2/L3 状态。^[pcie-dllp-format.md:372-388]

### L2/L3 状态特性

L2/L3 状态的功耗节省程度比 L1 更高，但也需要更长的恢复时间：^[pcie-dllp-format.md:384-388]

- **关闭 TX/RX**：与 L1 类似，关闭高速收发器
- **可选关闭参考时钟**：L3 状态下可以完全关闭参考时钟以进一步节能
- **恢复时间**：L2 状态恢复时间小于 100 微秒，L3 状态恢复时间超过 1 毫秒

## PM_Request_Ack

**PM_Request_Ack** 用于确认电源状态变更请求，是电源状态协商流程中的必要组成部分。^[pcie-dllp-format.md:390-393] 当端口收到 PM_Enter_L1 请求后，必须发送 PM_Request_Ack 作为确认响应。只有收到对方的确认后，发送方才认为协商成功并进入目标电源状态。^[pcie-dllp-format.md:356-359]

## PM_Active_State_Request_L1

**PM_Active_State_Request_L1**（Type = 0x24）用于请求从 L1 状态退出并返回 L0 工作状态。^[pcie-dllp-format.md:89] 当链路需要恢复数据传输时，端口发送此 DLLP 通知对端准备接收 TLP。该 DLLP 同样是双向传输，表明 L0 和 L1 之间的转换需要双方协调。^[pcie-dllp-format.md:89]

## DLLP 与电源状态转换

电源管理 DLLP 在 PCIe 协议栈中与其他层级的电源管理机制协同工作。事务层的 ASPM 配置控制着何时允许进入 L0s/L1 状态，而数据链路层的 PM DLLP 则负责实际的协商过程。物理层的 LTSSM 状态机处理链路训练期间的电源状态转换。

### 电源状态协商要点

电源管理 DLLP 的设计体现了以下设计原则：^[pcie-dllp-format.md:589-594]

1. **确认机制**：PM_Enter_L1 需要 PM_Request_Ack 确认，确保两端同步进入低功耗状态
2. **无重传机制**：与 Ack/Nak DLLP 不同，PM DLLP 丢失后依赖超时和重试机制恢复
3. **延迟敏感**：L1 状态设计为低延迟（<10μs），适合短暂空闲场景

## 相关概念

- DLLP 格式详解 — DLLP 的通用结构和各类 DLLP 概述
- ACK/NAK 机制 — Ack/Nak DLLP 实现的可靠传输机制
- 流控制 DLLP — InitFC 和 UpdateFC DLLP 实现的缓冲区管理
- ASPM — Active State Power Management，事务层的电源管理配置
- LTSSM — Link Training and Status State Machine，链路训练状态机

---

## Sources

- [DLLP 格式详解 (pcie-dllp-format.md)](../../sources/pcie-dllp-format.md) — 第 23-24, 86-90, 330-394 行

