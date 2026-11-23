---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 663b2cdfbfe9f412786cbc476092aa39fe5657e414de77a103d9e9597549e15d
  pageDirectory: concepts
  sources:
    - pcie-dllp-format.md
  confidence: 1
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - dllp-type-encoding
    - DTE
  citations:
    - file: pcie-dllp-format.md
      start: 79
      end: 80
    - file: pcie-dllp-format.md
      start: 77
      end: 79
    - file: pcie-dllp-format.md
      start: 52
      end: 60
    - file: pcie-dllp-format.md
      start: 104
      end: 108
    - file: pcie-dllp-format.md
      start: 132
      end: 134
    - file: pcie-dllp-format.md
      start: 152
      end: 157
    - file: pcie-dllp-format.md
      start: 180
      end: 183
    - file: pcie-dllp-format.md
      start: 207
      end: 213
    - file: pcie-dllp-format.md
      start: 275
      end: 277
    - file: pcie-dllp-format.md
      start: 228
      end: 245
    - file: pcie-dllp-format.md
      start: 330
      end: 394
    - file: pcie-dllp-format.md
      start: 396
      end: 415
title: DLLP Type Encoding
description: DLLP类型字段编码，定义Ack/Nak/FC/PM/Vendor等16种DLLP类型及其方向
tags:
  - pcie
  - protocol
  - packet-format
timestamp: "2026-08-16T06:37:11.119Z"
---

# DLLP Type Encoding

## 概述

DLLP Type 字段占据 DLLP 的第一个字节，用于定义 DLLP 的类型和子类型。该字段与第二个字节的保留位共同构成 **Type (2 bytes)** 区域，是所有 DLLP 固定格式的起始部分。^[pcie-dllp-format.md:79-80]

Type 字段采用特定的编码规则，不同的十六进制值对应不同的 DLLP 功能类别，包括确认/否认机制、流控制初始化、流控制更新、电源管理以及厂商自定义等五大类。^[pcie-dllp-format.md:77-79]

## 完整类型编码表

| Type Value | 名称 | 用途 | 方向 |
|------------|------|------|------|
| **0x00** | Ack | 确认 TLP 接收 | 双向 |
| **0x10** | Nak | 请求重传 TLP | 双向 |
| **0x20** | PM_Enter_L1 | 请求进入 L1 状态 | 双向 |
| **0x21** | PM_Enter_L23 | 请求进入 L2/L3 状态 | 下游→上游 |
| **0x24** | PM_Active_State_Request_L1 | 请求从 L1 退出到 L0 | 双向 |
| **0x30** | PM_Request_Ack | 电源管理请求确认 | 双向 |
| **0x40** | Vendor-Specific | 厂商自定义 | 双向 |
| **0x50** | InitFC1-P | 流控制初始化（Posted）| 双向 |
| **0x60** | InitFC1-NP | 流控制初始化（Non-Posted）| 双向 |
| **0x70** | InitFC1-Cpl | 流控制初始化（Completion）| 双向 |
| **0xC0** | InitFC2-P | 流控制初始化确认（Posted）| 双向 |
| **0xD0** | InitFC2-NP | 流控制初始化确认（Non-Posted）| 双向 |
| **0xE0** | InitFC2-Cpl | 流控制初始化确认（Completion）| 双向 |
| **0x80** | UpdateFC-P | 流控制更新（Posted）| 双向 |
| **0x90** | UpdateFC-NP | 流控制更新（Non-Posted）| 双向 |
| **0xA0** | UpdateFC-Cpl | 流控制更新（Completion）| 双向 |

*来源：[pcie-dllp-format.md:83-100]*

## 类型编码规律

### 高位 nibble 分组

Type 字段的高 4 位（nibble）定义了 DLLP 的大类别：

| 高位 nibble | 类别 | 说明 |
|-------------|------|------|
| **0x0** | Ack/Nak | 可靠传输机制 |
| **0x2** | PM (低功耗) | 电源管理请求 |
| **0x3** | PM 确认 | 电源状态变更确认 |
| **0x4** | Vendor | 厂商自定义 |
| **0x5-0x7** | InitFC1 / UpdateFC | 流控制初始化和更新 |
| **0xC-0xE** | InitFC2 | 流控制初始化确认 |

### Posted/Non-Posted/Completion 编码

流控制相关的 DLLP 类型采用一致的编码模式区分三种流量类别：

| 流控类型 | InitFC1 | InitFC2 | UpdateFC |
|----------|---------|---------|----------|
| Posted (P) | 0x50 | 0xC0 | 0x80 |
| Non-Posted (NP) | 0x60 | 0xD0 | 0x90 |
| Completion (Cpl) | 0x70 | 0xE0 | 0xA0 |

这种编码设计使得硬件可以通过简单的位操作快速识别 DLLP 的功能类别。

## 类型字段位置

在 DLLP 的固定 8 字节格式中，Type 字段位于起始位置：

```
┌────────────────────────────────────────────────────┐
│  Byte 0: Type Field    │  Byte 1: Reserved (0x00) │
├────────────────────────────────────────────────────┤
│  Byte 2-5: DLLP Content (Type-Specific)            │
├────────────────────────────────────────────────────┤
│  Byte 6-7: CRC-16                                  │
└────────────────────────────────────────────────────┘
```

Type 字段位于 Byte 0，Byte 1 固定为保留位（0x00）。^[pcie-dllp-format.md:52-60]

## 类型详解

### Ack/Nak 类型 (0x00 / 0x10)

**Ack (0x00)** 用于确认成功接收一个或多个 TLP，其 Type 字段后跟随 AckNak Seq Number（12 bits），表示已成功接收到序列号小于等于此值的所有 TLP。^[pcie-dllp-format.md:104-108, pcie-dllp-format.md:132-134]

**Nak (0x10)** 用于请求重传从指定序列号开始的所有 TLP，当检测到 LCRC 校验失败、TLP 序列号不连续或接收缓冲区溢出时触发。^[pcie-dllp-format.md:152-157, pcie-dllp-format.md:180-183]

### 流控制类型 (0x50-0x70, 0x80-0xA0, 0xC0-0xE0)

流控制 DLLP 用于管理接收缓冲区，防止溢出。InitFC1 用于链路初始化时交换缓冲区容量信息，InitFC2 在收到对方 InitFC1 后进行确认，UpdateFC 则在运行时通知对方已释放的缓冲区空间。^[pcie-dllp-format.md:207-213, pcie-dllp-format.md:275-277]

流控制 DLLP 的 Content 字段包含 **HdrFC**（8 bits，表示可缓冲的 TLP Header 个数）和 **DataFC**（12 bits，表示可缓冲的 Data DWORD 数）。^[pcie-dllp-format.md:228-245]

### 电源管理类型 (0x20-0x30)

**PM_Enter_L1 (0x20)** 请求进入 L1 低功耗状态，**PM_Enter_L23 (0x21)** 请求进入 L2/L3 深度睡眠状态，**PM_Request_Ack (0x30)** 用于确认电源状态变更请求。^[pcie-dllp-format.md:330-394]

### 厂商自定义类型 (0x40)

**Vendor-Specific (0x40)** 允许厂商定义私有的链路控制信息，可用于专有的调试和测试功能、厂商特定的性能优化或私有协议扩展。^[pcie-dllp-format.md:396-415]

## 与 TLP Type 编码的对比

DLLP Type 与 TLP 中的 Type 字段有本质区别：

| 特性 | DLLP Type | TLP Type |
|------|------------|----------|
| 位置 | Byte 0 | 位于 TLP Header 内 |
| 位宽 | 1 字节 | 1 字节（或 5 字节带 Ext）|
| 功能 | 链路控制 | 事务类型定义 |
| 重传 | 不需要 ACK | 需要 Ack DLLP 确认 |

---

## Sources

- [pcie-dllp-format.md](pcie-dllp-format.md) — DLLP 格式详解

---

## 相关概念

- Ack/Nak 机制 — DLLP 实现的可靠传输机制
- TLP Format — 事务层包的格式
- Flow Control — 流控制机制详解
- Data Link Layer — 数据链路层概述

# Citations

1. [pcie-dllp-format.md:79-80](/references/pcie-dllp-format-55680021.md)
2. [pcie-dllp-format.md:77-79](/references/pcie-dllp-format-55680021.md)
3. [pcie-dllp-format.md:52-60](/references/pcie-dllp-format-55680021.md)
4. [pcie-dllp-format.md:104-108](/references/pcie-dllp-format-55680021.md)
5. [pcie-dllp-format.md:132-134](/references/pcie-dllp-format-55680021.md)
6. [pcie-dllp-format.md:152-157](/references/pcie-dllp-format-55680021.md)
7. [pcie-dllp-format.md:180-183](/references/pcie-dllp-format-55680021.md)
8. [pcie-dllp-format.md:207-213](/references/pcie-dllp-format-55680021.md)
9. [pcie-dllp-format.md:275-277](/references/pcie-dllp-format-55680021.md)
10. [pcie-dllp-format.md:228-245](/references/pcie-dllp-format-55680021.md)
11. [pcie-dllp-format.md:330-394](/references/pcie-dllp-format-55680021.md)
12. [pcie-dllp-format.md:396-415](/references/pcie-dllp-format-55680021.md)
