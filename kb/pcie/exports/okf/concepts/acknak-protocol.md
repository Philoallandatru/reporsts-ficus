---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: eb2ccf0e6a4754abb84ae870e740fb053373625b987cf307c706b8f98cb18faf
  pageDirectory: concepts
  sources:
    - pcie-dllp-format.md
  confidence: 1
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - acknak-protocol
  citations:
    - file: pcie-dllp-format.md
      start: 14
      end: 27
    - file: pcie-dllp-format.md
      start: 3
      end: 9
    - file: pcie-dllp-format.md
      start: 104
      end: 108
    - file: pcie-dllp-format.md
      start: 110
      end: 128
    - file: pcie-dllp-format.md
      start: 132
      end: 134
    - file: pcie-dllp-format.md
      start: 136
      end: 141
    - file: pcie-dllp-format.md
      start: 143
      end: 148
    - file: pcie-dllp-format.md
      start: 152
      end: 156
    - file: pcie-dllp-format.md
      start: 158
      end: 176
    - file: pcie-dllp-format.md
      start: 180
      end: 183
    - file: pcie-dllp-format.md
      start: 185
      end: 196
    - file: pcie-dllp-format.md
      start: 198
      end: 203
    - file: pcie-dllp-format.md
      start: 83
      end: 100
    - file: pcie-dllp-format.md
      start: 71
      end: 71
    - file: pcie-dllp-format.md
      start: 589
      end: 594
    - file: pcie-dllp-format.md
      start: 617
      end: 620
    - file: pcie-dllp-format.md
title: Ack/Nak Protocol
description: 确认/否认机制，通过序列号累计确认保证TLP可靠传输，丢失时触发重传
tags:
  - pcie
  - reliability
  - error-recovery
timestamp: "2026-08-16T06:36:47.017Z"
---


# [ACK/NAK 协议](/concepts/acknak-协议.md)

Ack/Nak 协议是 PCIe 数据链路层 实现可靠传输的核心机制，用于确认 TLP（事务层包） 的接收状态并触发必要时的重传。^[pcie-dllp-format.md:14-27]

---

## 概述

在 PCIe 协议栈中，数据链路层负责在发送端为每个 TLP 添加序列号（Seq#）和 LCRC 校验码，接收端则通过 Ack/Nak 协议反馈接收结果。^[pcie-dllp-format.md:3-9]

Ack/Nak 协议的核心功能包括：

- **确认机制**：通过 Ack DLLP 确认已成功接收的 TLP，允许发送端释放重传缓冲区中的数据
- **重传机制**：通过 Nak DLLP 请求重传从指定序列号开始的所有 TLP
- **超时保护**：当发送端在超时时间内未收到 Ack 时，自动重传所有未确认的 TLP

---

## Ack DLLP

### 用途与格式

Ack（确认）DLLP 用于通知发送端已成功接收一个或多个 TLP。^[pcie-dllp-format.md:104-108]

Ack DLLP 的 Type 值为 **0x00**，其结构如下：^[pcie-dllp-format.md:110-128]

```
Byte 0-1:
┌─────────────┬──────────────────┐
│ Type = 0x00 │ Reserved (0x00)  │
└─────────────┴──────────────────┘

Byte 2-5:
┌──────────────────────────────────┐
│  Reserved  │  AckNak Seq Number  │
│  (20 bits) │    (12 bits)        │
└──────────────────────────────────┘

Byte 6-7:
┌──────────────────────────────────┐
│           CRC-16                 │
└──────────────────────────────────┘
```

### AckNak Seq Number 字段

**AckNak Seq Number** 是 12 位字段，范围为 0-4095（循环计数），表示已成功接收到**序列号小于等于此值的所有 TLP**。^[pcie-dllp-format.md:132-134]

### 工作机制

Ack DLLP 的典型工作流程如下：^[pcie-dllp-format.md:136-141]

```
发送方：发送 TLP with Seq# = 100
接收方：成功接收 → 发送 Ack DLLP (AckNak Seq# = 100)
发送方：收到 Ack → 清除重传缓冲区中 Seq# ≤ 100 的 TLP
```

### 累积确认特性

Ack DLLP 支持**累积确认**，这意味着发送单个 Ack 即可确认多个连续接收的 TLP：^[pcie-dllp-format.md:143-148]

```
发送方连续发送：Seq# 10, 11, 12, 13
接收方只需发送：Ack (Seq# = 13)
  → 表示 10-13 全部成功接收
```

这一特性显著减少了 Ack DLLP 的发送数量，提高了协议效率。

---

## Nak DLLP

### 用途与格式

Nak（否认）DLLP 用于请求发送端重传从指定序列号开始的所有 TLP。^[pcie-dllp-format.md:152-156]

Nak DLLP 的 Type 值为 **0x10**，其结构与 Ack DLLP 相同：^[pcie-dllp-format.md:158-176]

```
Byte 0-1:
┌─────────────┬──────────────────┐
│ Type = 0x10 │ Reserved (0x00)  │
└─────────────┴──────────────────┘

Byte 2-5:
┌──────────────────────────────────┐
│  Reserved  │  AckNak Seq Number  │
│  (20 bits) │    (12 bits)        │
└──────────────────────────────────┘

Byte 6-7:
┌──────────────────────────────────┐
│           CRC-16                 │
└──────────────────────────────────┘
```

### Nak 触发条件

接收方在以下情况下会发送 Nak DLLP：^[pcie-dllp-format.md:180-183]

1. **LCRC 校验失败**：接收到的 TLP 在传输过程中发生位错误
2. **TLP 序列号不连续**：检测到丢包或包顺序错误
3. **接收缓冲区溢出**：处理能力不足导致缓冲区溢出

### 重传流程

Nak DLLP 的典型重传流程如下：^[pcie-dllp-format.md:185-196]

```
发送方：TLP Seq# 20, 21, 22, 23
接收方：收到 20, 21, [22 LCRC 错误], 23
        ↓
        发送 Nak (Seq# = 22)
        ↓
发送方：收到 Nak → 重传 Seq# ≥ 22 的所有 TLP
        重传 22, 23
        ↓
接收方：收到 22, 23 → 发送 Ack (Seq# = 23)
```

### 超时重传机制

除了 Nak 触发的重传外，发送端还实现了**超时重传机制**作为补充保护：^[pcie-dllp-format.md:198-203]

```
如果发送方在超时时间内未收到 Ack：
  → 自动重传所有未确认的 TLP
  → 不需要 Nak
```

这一机制确保了在 Ack 或 Nak DLLP 丢失的情况下，传输可靠性仍能得到保障。

---

## 协议状态机

Ack/Nak 协议涉及发送端和接收端两侧的状态管理：

| 状态 | 发送端行为 | 接收端行为 |
|------|-----------|-----------|
| **正常** | 发送 TLP，缓存并等待 Ack | 校验 LCRC，连续则发送 Ack |
| **异常** | 收到 Nak 或超时，重传 TLP | 检测错误，发送 Nak |
| **恢复** | 重传完成后继续发送新 TLP | 接收重传 TLP，更新 Ack Seq# |

---

## 与 DLLP 整体的关系

Ack/Nak DLLP 是 DLLP 的五种主要类型之一，其他四种类型包括：^[pcie-dllp-format.md:14-27, pcie-dllp-format.md:83-100]

| 类型 | 用途 |
|------|------|
| **Ack (0x00)** | 确认 TLP 接收 |
| **Nak (0x10)** | 请求重传 TLP |
| **InitFC** | 流控制初始化 |
| **UpdateFC** | 流控制更新 |
| **PM** | 电源管理 |

值得注意的是，**DLLP 本身不需要被确认**。与 TLP 不同，DLLP 丢失后不会触发重传，而是依赖上层机制（如发送端的超时重传或接收端的重复发送）进行恢复。^[pcie-dllp-format.md:71, pcie-dllp-format.md:589-594]

---

## 总结

Ack/Nak 协议是 PCIe 数据链路层保证可靠传输的关键机制：

1. **Ack DLLP** 通过累积确认机制高效地通知发送端哪些 TLP 已成功接收
2. **Nak DLLP** 在检测到错误时触发选择性重传，只重传从错误点开始的所有 TLP
3. **超时机制** 作为补充保护，防止 Ack/Nak DLLP 丢失导致的传输死锁
4. **协议设计** 避免了递归确认问题，简化了协议复杂度

这些机制共同确保了在不可靠的物理链路上可靠传输 TLP 的目标。^[pcie-dllp-format.md:617-620]

---

## 相关概念

- 数据链路层
- DLLP 格式详解
- TLP 格式
- 流控制机制
- LTSSM 状态机

---

## Sources

^[pcie-dllp-format.md]

# Citations

1. [pcie-dllp-format.md:14-27](/references/pcie-dllp-format-55680021.md)
2. [pcie-dllp-format.md:3-9](/references/pcie-dllp-format-55680021.md)
3. [pcie-dllp-format.md:104-108](/references/pcie-dllp-format-55680021.md)
4. [pcie-dllp-format.md:110-128](/references/pcie-dllp-format-55680021.md)
5. [pcie-dllp-format.md:132-134](/references/pcie-dllp-format-55680021.md)
6. [pcie-dllp-format.md:136-141](/references/pcie-dllp-format-55680021.md)
7. [pcie-dllp-format.md:143-148](/references/pcie-dllp-format-55680021.md)
8. [pcie-dllp-format.md:152-156](/references/pcie-dllp-format-55680021.md)
9. [pcie-dllp-format.md:158-176](/references/pcie-dllp-format-55680021.md)
10. [pcie-dllp-format.md:180-183](/references/pcie-dllp-format-55680021.md)
11. [pcie-dllp-format.md:185-196](/references/pcie-dllp-format-55680021.md)
12. [pcie-dllp-format.md:198-203](/references/pcie-dllp-format-55680021.md)
13. [pcie-dllp-format.md:83-100](/references/pcie-dllp-format-55680021.md)
14. [pcie-dllp-format.md:71-71](/references/pcie-dllp-format-55680021.md)
15. [pcie-dllp-format.md:589-594](/references/pcie-dllp-format-55680021.md)
16. [pcie-dllp-format.md:617-620](/references/pcie-dllp-format-55680021.md)
17. [pcie-dllp-format.md](/references/pcie-dllp-format-55680021.md)
