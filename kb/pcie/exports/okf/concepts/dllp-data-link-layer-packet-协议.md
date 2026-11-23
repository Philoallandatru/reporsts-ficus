---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 65f5e6ef1cbef827a35dc3603975aa259e2b3295793d15175e7e176895a1d55c
  pageDirectory: concepts
  sources:
    - pcie-spec-analysis.md
  confidence: 0.93
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - dllp-data-link-layer-packet-协议
    - D(LLP协
  citations:
    - file: pcie-spec-analysis.md
      start: 188
      end: 190
    - file: pcie-spec-analysis.md
      start: 193
      end: 195
    - file: pcie-spec-analysis.md
      start: 200
      end: 205
    - file: pcie-spec-analysis.md
      start: 193
      end: 193
    - file: pcie-spec-analysis.md
      start: 198
      end: 199
    - file: pcie-spec-analysis.md
      start: 194
      end: 194
    - file: pcie-spec-analysis.md
      start: 202
      end: 202
    - file: pcie-spec-analysis.md
      start: 204
      end: 204
    - file: pcie-spec-analysis.md
      start: 206
      end: 206
    - file: pcie-spec-analysis.md
      start: 196
      end: 197
title: DLLP (Data Link Layer Packet) 协议
description: 数据链路层数据包，包含ACK/NAK确认机制、流量控制初始化和重试缓冲
tags:
  - PCIe
  - 数据链路层
  - 可靠传输
timestamp: "2026-08-16T06:46:12.345Z"
---


# DLLP（Data Link Layer Packet）协议

## 概述

DLLP（Data Link Layer Packet，数据链路层数据包）是 PCI Express 协议中位于PCI Express数据链路层的核心协议元素。它负责在相邻PCI Express设备之间提供可靠的数据传输服务，是确保TLP（Transaction Layer Packet，事务层数据包）能够正确交付的关键机制。 ^[pcie-spec-analysis.md:188-190]

DLLP 在物理层之上、事务层之下运行，其主要功能包括：流量控制初始化、确认/否定应答（ACK/NAK）、信用更新以及电源管理协议等。该协议通过 LCRC（Link CRC，链路循环冗余校验）和序列号机制，为上层事务层提供可靠的链路级数据传输服务。 ^[pcie-spec-analysis.md:193-195]

## DLLP 类型

根据 PCI Express Base Specification 5.0 版本，数据链路层定义了以下主要 DLLP 类型：

| DLLP 类型 | 功能描述 |
|-----------|----------|
| **Ack** | 确认收到来自对端的 TLP |
| **Nak** | 请求对端重传已发送的 TLP |
| **InitFC1** | 流量控制初始化阶段 1 |
| **InitFC2** | 流量控制初始化阶段 2 |
| **UpdateFC** | 运行期间更新流量控制信用 |
| **PM** | 电源管理协议控制 |
| **Vendor-Specific** | 厂商自定义 DLLP |

^[pcie-spec-analysis.md:200-205]

### Ack/Nak DLLP

Ack（确认）和 Nak（否定确认）DLLP 用于实现数据链路层的可靠传输机制。当接收端正确收到一个 TLP 时，会向发送端返回一个 Ack DLLP；如果检测到错误，则返回 Nak DLLP 请求重传。发送端维护一个重传缓冲区（Retry Buffer），在收到 Nak 后会重新发送相应的 TLP。 ^[pcie-spec-analysis.md:193, pcie-spec-analysis.md:198-199]

### 流量控制 DLLP

流量控制初始化分为两个阶段：InitFC1 和 InitFC2。这两个阶段用于在链路建立初期交换双方接收缓冲区的信用信息。完成初始化后，运行期间的信用更新通过 UpdateFC DLLP 实现，确保发送端始终了解接收端的可用缓冲空间。 ^[pcie-spec-analysis.md:194, 202]

### 电源管理 DLLP

电源管理（PM）DLLP 用于链路电源状态转换的控制信令，支持 L0s、L1 等低功耗状态的进入和退出。 ^[pcie-spec-analysis.md:204]

## 数据链路层状态机

数据链路层通过数据链路控制状态机（Data Link Control and Status State Machine）管理链路状态。该状态机负责协调 DLLP 的发送与接收，包括：

- **DL_Init**：链路初始化状态，执行 InitFC1 和 InitFC2 流程
- **DL_Active**：链路激活状态，正常传输 TLP 和 DLLP
- **DL_Down**：链路断开或错误状态
- **DL_Inactive**：链路非活跃状态

状态转换过程中会触发相应的 DLLP 交换以完成协议握手。 ^[pcie-spec-analysis.md:193, 206]

## LCRC 与序列号

为确保传输可靠性，DLLP 携带 LCRC 校验字段，接收端通过检查 LCRC 来验证 DLLP 完整性。同时，数据链路层为每个 TLP 分配一个 12 位的序列号（Sequence Number），用于标识和追踪 TLP 的发送顺序，配合 Ack/Nak 机制实现可靠交付。 ^[pcie-spec-analysis.md:196-197]

## 与其他层的关系

DLLP 位于 PCI Express 协议栈的**数据链路层**，是该层与对端设备通信的唯一机制。其上下层关系如下：

- **上层（事务层）**：DLLP 封装来自事务层的 TLP，将其传递给物理层传输
- **下层（物理层）**：物理层负责 DLLP 的实际编码和信号传输
- **对端设备**：DLLP 在两个相邻设备之间直接交换，不经过中间交换节点

## 相关概念

- PCI Express
- TLP
- LCRC
- LTSSM
- PCI Express 电源管理
- PCI Express 流量控制

---

## Sources

- [PCI Express Base Specification Analysis](https://www.google.com/search?q=PCI+Express+Base+Specification+Revision+5.0) — 基于 PCI Express Base Specification Revision 5.0 Version 1.0（2019年5月22日发布）的文档分析

# Citations

1. [pcie-spec-analysis.md:188-190](/references/pcie-spec-analysis-43772b7d.md)
2. [pcie-spec-analysis.md:193-195](/references/pcie-spec-analysis-43772b7d.md)
3. [pcie-spec-analysis.md:200-205](/references/pcie-spec-analysis-43772b7d.md)
4. [pcie-spec-analysis.md:193-193](/references/pcie-spec-analysis-43772b7d.md)
5. [pcie-spec-analysis.md:198-199](/references/pcie-spec-analysis-43772b7d.md)
6. [pcie-spec-analysis.md:194-194](/references/pcie-spec-analysis-43772b7d.md)
7. [pcie-spec-analysis.md:202-202](/references/pcie-spec-analysis-43772b7d.md)
8. [pcie-spec-analysis.md:204-204](/references/pcie-spec-analysis-43772b7d.md)
9. [pcie-spec-analysis.md:206-206](/references/pcie-spec-analysis-43772b7d.md)
10. [pcie-spec-analysis.md:196-197](/references/pcie-spec-analysis-43772b7d.md)
