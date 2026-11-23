---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 3f562d50305ba78ba48d267a6a65dcfe9fd1ad2e3d3b3b098afd81b610b32a4b
  pageDirectory: concepts
  sources:
    - pcie-layering.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - pcie-流控制机制
  citations:
    - file: pcie-layering.md
      start: 116
      end: 123
    - file: pcie-layering.md
      start: 16
      end: 26
    - file: pcie-layering.md
      start: 120
      end: 123
    - file: pcie-layering.md
      start: 138
      end: 153
    - file: pcie-layering.md
      start: 133
      end: 136
    - file: pcie-layering.md
      start: 125
      end: 131
    - file: pcie-layering.md
      start: 224
      end: 225
    - file: pcie-layering.md
      start: 225
      end: 225
title: PCIe 流控制机制
description: 基于信用的流控制机制，接收方向发送方通告可用缓冲区空间，防止发送方超出接收方处理能力
tags:
  - pcie
  - flow-control
  - credit-based
timestamp: "2026-08-16T06:39:39.063Z"
---


# PCIe 流控制机制

## 概述

PCIe 流控制（Flow Control）是一种基于**信用 (Credit)** 的机制，用于防止发送方发送超过接收方缓冲区容量的数据，确保数据链路不会因接收方缓冲区溢出而导致丢包。^[pcie-layering.md:116-123]

流控制机制由**事务层**和**数据链路层**共同实现。在事务层，流控制负责管理数据包的发送节奏；在数据链路层，通过 **DLLP (Data Link Layer Packet)** 进行流控制初始化和运行时更新。^[pcie-layering.md:16-26]

## 信用机制原理

### 基本工作方式

流控制的核心思想是**接收方通告、发送方遵循**。接收方定期向发送方报告其可用缓冲区空间（信用），发送方根据可用信用决定是否可以发送数据包。^[pcie-layering.md:120-123]

具体流程如下：
- 接收方通过 DLLP 告知发送方当前可用的缓冲区空间
- 发送方在发送 TLP 时消耗相应信用
- 接收方处理完数据后，返还信用给发送方
- 当信用耗尽时，发送方必须暂停发送，等待信用返还 ^[pcie-layering.md:138-153]

### 信用类型

PCIe 定义了两种信用单位：^[pcie-layering.md:133-136]

| 信用类型 | 说明 | 计数单位 |
|----------|------|----------|
| **Header Credits (HDR)** | TLP 头部数量 | 个数 |
| **Data Credits (DATA)** | 数据负载大小 | DW (Double Word, 32位) |

## 流控制类型

根据事务类型的不同，流控制分为三种类型：^[pcie-layering.md:125-131]

| 类型 | 缩写 | 说明 | 示例 |
|------|------|------|------|
| **Posted** | P | 无需响应的请求，发送后即完成 | Memory Write, Message |
| **Non-Posted** | NP | 需要 Completion 响应的请求 | Memory Read, IO 读写, 配置读写 |
| **Completion** | Cpl | 对 NP 请求的响应 | Completion, Completion with Data |

## 初始化过程

在链路训练完成后，需要进行流控制初始化。数据链路层使用 **InitFC1** 和 **InitFC2** 两种 DLLP 完成初始化过程。^[pcie-layering.md:224-225]

初始化过程中，接收方向发送方通告其所有虚拟通道的初始信用值，确保双方在正常数据传输前对缓冲区容量达成共识。

## 运行时更新

在正常数据传输过程中，接收方通过 **UpdateFC** DLLP 定期向发送方更新可用信用信息。当接收方处理完数据并释放缓冲区后，会返还相应的信用，使发送方能够继续发送数据。^[pcie-layering.md:225]

## 工作示例

以下示例展示了流控制的实际工作过程：^[pcie-layering.md:138-153]

```
接收方 → 发送方: "我有 10 个 Posted Header Credits, 256 DW Data Credits"

发送方发送 Memory Write (1 HDR + 64 DW Data):
  - 剩余: 9 HDR, 192 DATA

发送方发送 Memory Write (1 HDR + 128 DW Data):
  - 剩余: 8 HDR, 64 DATA

发送方发送 Memory Write (1 HDR + 64 DW Data):
  - 剩余: 7 HDR, 0 DATA  ← 数据信用耗尽，必须等待

接收方处理完数据后:
  → 发送方: "返还 256 DW Data Credits"
  - 现在: 7 HDR, 256 DATA  ← 可以继续发送
```

当数据信用耗尽时，发送方必须暂停发送，直到接收方通过 UpdateFC DLLP 返还信用。这种机制有效防止了缓冲区溢出，确保了数据传输的可靠性。

---

## 相关主题

- [PCIe 三层协议模型](/concepts/pcie-三层协议模型.md) - 了解流控制在协议栈中的位置
- PCIe 数据链路层 - 包含 ACK/NAK 协议和 DLLP 详解
- PCIe 事务层 - TLP 类型和虚拟通道
- [PCIe 虚拟通道](/concepts/pcie-虚拟通道.md) - 多虚拟通道下的流控制

---

## Sources

- PCIe 三层协议模型](../pcie-layering.md)

# Citations

1. [pcie-layering.md:116-123](/references/pcie-layering-3c12192c.md)
2. [pcie-layering.md:16-26](/references/pcie-layering-3c12192c.md)
3. [pcie-layering.md:120-123](/references/pcie-layering-3c12192c.md)
4. [pcie-layering.md:138-153](/references/pcie-layering-3c12192c.md)
5. [pcie-layering.md:133-136](/references/pcie-layering-3c12192c.md)
6. [pcie-layering.md:125-131](/references/pcie-layering-3c12192c.md)
7. [pcie-layering.md:224-225](/references/pcie-layering-3c12192c.md)
8. [pcie-layering.md:225-225](/references/pcie-layering-3c12192c.md)
