---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 3f1bfeed34651afd4a4af462504b8de5fca9b9b00ecae462ae93586c669f6fb5
  pageDirectory: concepts
  sources:
    - pcie-tlp-format.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - tlp-类型详解
  citations:
    - file: pcie-tlp-format.md
      start: 147
      end: 163
    - file: pcie-tlp-format.md
      start: 9
      end: 12
    - file: pcie-tlp-format.md
      start: 56
      end: 63
    - file: pcie-tlp-format.md
      start: 229
      end: 263
    - file: pcie-tlp-format.md
      start: 231
      end: 232
    - file: pcie-tlp-format.md
      start: 264
      end: 285
    - file: pcie-tlp-format.md
      start: 298
      end: 308
    - file: pcie-tlp-format.md
      start: 309
      end: 346
    - file: pcie-tlp-format.md
      start: 313
      end: 331
    - file: pcie-tlp-format.md
      start: 348
      end: 387
    - file: pcie-tlp-format.md
      start: 381
      end: 387
    - file: pcie-tlp-format.md
      start: 389
      end: 433
    - file: pcie-tlp-format.md
      start: 462
      end: 481
    - file: pcie-tlp-format.md
      start: 283
      end: 285
    - file: pcie-tlp-format.md
      start: 131
      end: 162
    - file: pcie-tlp-format.md
      start: 437
      end: 490
    - file: pcie-tlp-format.md
      start: 1
      end: 634
title: TLP 类型详解
description: PCIe定义的五种TLP类型：Memory Read/Write、IO Read/Write、Configuration Read/Write、Message、Completion，通过Fmt/Type组合标识
tags:
  - pcie
  - transaction
  - protocol
timestamp: "2026-08-16T06:48:57.576Z"
---

# TLP 类型详解

Transaction Layer Packet（TLP 类型）是 PCIe 事务层用于在设备间传输数据的核心单元。根据传输需求不同，PCIe 定义了多种 TLP 类型，每种类型通过 **Fmt** 和 **Type** 字段的组合唯一标识。 ^[pcie-tlp-format.md:147-163]

## 概述

TLP 类型主要分为五大类：

| 类别 | 用途 | 路由方式 |
|------|------|----------|
| **Memory Request** | 内存读写访问 | 基于地址 |
| **IO Request** | IO 地址空间访问 | 基于地址 |
| **Configuration Request** | 设备配置空间访问 | 基于 ID |
| **Message Request** | 中断、错误、电源管理等消息 | 隐式或基于 ID |
| **Completion** | 响应 Non-Posted 请求 | 基于 ID（反向路由）|

所有 TLP 类型共享相同的基本结构：由 Header（3 DW 或 4 DW）、可选 Data Payload 和可选 ECRC 组成，但不同类型的 Header 字段内容有所差异。 ^[pcie-tlp-format.md:9-12, pcie-tlp-format.md:56-63]

---

## Memory Request（内存请求）

内存请求是 PCIe 中最常用的 TLP 类型，用于在内存地址空间进行数据读写。 ^[pcie-tlp-format.md:229-263]

### Memory Read Request (MRd)

**用途**：从内存地址读取数据，属于 **Non-Posted** 事务，需要 Completion 响应返回数据。 ^[pcie-tlp-format.md:231-232]

**格式特点**：
- 支持 32 位地址（3 DW Header）和 64 位地址（4 DW Header）
- 无 Data Payload（读请求本身不携带数据）
- Length 字段以 DW（4 字节）为单位

**Type 字段编码**：
| Fmt | Type | 含义 |
|-----|------|------|
| 000b | 00000b | Memory Read Request（32 位地址）|
| 001b | 00000b | Memory Read Request（64 位地址）|

### Memory Write Request (MWr)

**用途**：向内存地址写入数据，属于 **Posted** 事务，无需 Completion 响应。 ^[pcie-tlp-format.md:264-285]

**格式特点**：
- 支持 32 位和 64 位地址
- 携带 Data Payload
- 高效但无法确认写入成功

**Type 字段编码**：
| Fmt | Type | 含义 |
|-----|------|------|
| 010b | 00000b | Memory Write Request（32 位地址）|
| 011b | 00000b | Memory Write Request（64 位地址）|

---

## IO Request（IO 请求）

IO 请求用于访问 x86 架构的 IO 地址空间（传统的 I/O 端口地址）。该类型在现代系统中已较少使用。 ^[pcie-tlp-format.md:298-308]

**格式特点**：
- 仅支持 32 位地址
- 最大 4 字节传输
- 属于 **Non-Posted** 事务，需要 Completion 响应
- 使用 3 DW Header

**Type 字段编码**：
| Fmt | Type | 含义 |
|-----|------|------|
| 000b | 00010b | IO Read Request |
| 010b | 00010b | IO Write Request |

---

## Configuration Request（配置请求）

配置请求用于访问 PCIe 设备的配置空间（Configuration Space），这是枚举和配置 PCIe 设备的主要机制。 ^[pcie-tlp-format.md:309-346]

### Type 0 与 Type 1

PCIe 定义了两种配置请求类型：

| 类型 | 用途 | 说明 |
|------|------|------|
| **Type 0** | 访问直连设备 | 用于最终目标设备 |
| **Type 1** | 通过 Bridge 访问下游设备 | 用于在总线上转发配置请求 |

**Header DW 2 字段结构**：
```
┌───────────────────────────────────────────────────┐
│  Bus (8)  │ Dev (5)  │ Func (3) │ Ext Reg (4) │ Reg (6) │ 00 │
└───────────────────────────────────────────────────┘
```

- **Bus/Device/Function**：标识目标设备
- **Ext Reg**：扩展寄存器号（PCIe 新增）
- **Reg**：寄存器号

**Type 字段编码**：
| Fmt | Type | 含义 |
|-----|------|------|
| 000b | 00100b | Configuration Read Type 0 |
| 010b | 00100b | Configuration Write Type 0 |
| 000b | 00101b | Configuration Read Type 1 |
| 010b | 00101b | Configuration Write Type 1 |

配置请求属于 **Non-Posted** 事务，写操作需要 Completion 确认。 ^[pcie-tlp-format.md:313-331]

---

## Message Request（消息请求）

消息请求用于传输中断、电源管理、错误报告等控制信息，是 PCIe 替代传统 PCI 边带信号的重要机制。 ^[pcie-tlp-format.md:348-387]

### 格式特点

消息请求使用 3 DW Header，Type 字段使用 **1xxxxxb** 编码表示消息类：

| Fmt | Type | 含义 |
|-----|------|------|
| 000b | 1xxxxb | Message（无数据）|
| 010b | 1xxxxb | Message with Data（有数据）|

### 常见消息类型

| Message Code | 类型 | 用途 |
|--------------|------|------|
| 0x10/0x11 | INTx Interrupt | 传统中断断言/取消 |
| 0x14 | PM_Active_State_Nak | 电源管理状态拒绝 |
| 0x18 | PM_PME | 电源管理事件 |
| 0x20 | ERR_COR | 可纠正错误 |
| 0x21 | ERR_NONFATAL | 非致命错误 |
| 0x22 | ERR_FATAL | 致命错误 |
| 0x30 | MSI/MSI-X | 消息信号中断 |

### MSI 中断

MSI（Message Signaled Interrupt）是 PCIe 推荐的中断方式，本质上是一个特殊的 Memory Write 请求，写入特定地址（通常为 0xFEE00000），Data 字段包含中断向量信息。 ^[pcie-tlp-format.md:381-387]

---

## Completion（完成包）

Completion 用于响应 **Non-Posted** 请求（Memory Read、IO 访问、Configuration 访问），返回请求的数据或状态。 ^[pcie-tlp-format.md:389-433]

### 格式特点

Completion 响应包含与原请求匹配的信息，用于反向路由：

**关键字段**：
- **Completer ID**：完成者的 BDF 地址
- **Status**：完成状态（3 bits）
- **Byte Count**：剩余字节数
- **Requester ID**：原请求者的 ID（用于反向路由）
- **Tag**：原请求的 Tag（用于匹配）
- **Lower Address**：数据在读请求中的偏移

### Status 字段

| Status | 含义 | 说明 |
|--------|------|------|
| 000b | SC (Successful Completion) | 成功完成 |
| 001b | UR (Unsupported Request) | 不支持的请求 |
| 010b | CRS (Configuration Request Retry Status) | 配置请求重试 |
| 100b | CA (Completer Abort) | 完成者异常终止 |

### Type 字段编码

| Fmt | Type | 含义 |
|-----|------|------|
| 000b | 01010b | Completion（无数据）|
| 010b | 01010b | Completion with Data（有数据）|

### 路由机制

Completion 使用 **ID-Based Routing**，通过 **Requester ID** 实现反向路由：请求者发起请求时记录自己的 BDF，Completion 响应携带该 ID，沿原路径返回。 ^[pcie-tlp-format.md:462-481]

---

## TLP 类型速查表

| Fmt[2:0] | Type[4:0] | TLP 类型 | Posted? |
|----------|-----------|---------|---------|
| 000b | 00000b | Memory Read Request（32 位）| No |
| 010b | 00000b | Memory Write Request（32 位）| Yes |
| 001b | 00000b | Memory Read Request（64 位）| No |
| 011b | 00000b | Memory Write Request（64 位）| Yes |
| 000b | 00010b | IO Read Request | No |
| 010b | 00010b | IO Write Request | No |
| 000b | 00100b | Config Read Type 0 | No |
| 010b | 00100b | Config Write Type 0 | No |
| 000b | 00101b | Config Read Type 1 | No |
| 010b | 00101b | Config Write Type 1 | No |
| 000b | 1xxxxb | Message（无数据）| Yes |
| 010b | 1xxxxb | Message with Data | Yes |
| 000b | 01010b | Completion（无数据）| N/A |
| 010b | 01010b | Completion with Data | N/A |

> **Posted vs Non-Posted**：
> - **Posted**：发送后无需等待响应（适用于 Memory Write、Message）
> - **Non-Posted**：必须等待 Completion 响应才能确认完成（适用于 Memory Read、IO、Configuration） ^[pcie-tlp-format.md:283-285]

---

## Fmt/Type 字段组合详解

Fmt（Format）和 Type 字段共同定义 TLP 的完整类型：

**Fmt 字段**（3 bits）定义 Header 格式和是否有数据：
| Fmt | 含义 |
|-----|------|
| 000b | 3 DW Header，无数据 |
| 001b | 4 DW Header，无数据 |
| 010b | 3 DW Header，有数据 |
| 011b | 4 DW Header，有数据 |
| 100b | TLP Prefix（PCIe 3.0+）|

**Type 字段**（5 bits）定义事务类型，结合 Fmt 确定具体操作。 ^[pcie-tlp-format.md:131-162]

---

## 路由方式总结

PCIe 根据 TLP 类型采用不同的路由机制：

| 路由方式 | 适用 TLP 类型 | 路由依据 |
|----------|-------------|----------|
| **Address-Based** | Memory Request, IO Request | TLP Header 中的地址字段 |
| **ID-Based** | Configuration Request, Completion | Bus:Device.Function ID |
| **Implicit** | 部分 Message（如 INTx）| 消息类型和端口类型 |

设备根据路由信息将 TLP 转发到正确的目标端口，或在接收后处理。 ^[pcie-tlp-format.md:437-490]

---

## 相关概念

- PCIe 协议栈 - TLP 在协议栈中的位置
- TLP 格式详解 - TLP 的完整结构（Header、Data、ECRC）
- 流控制机制 - TLP 发送的信用管理
- 排序规则 - TLP 的处理顺序约束
- DLLP 格式 - 数据链路层的应答机制

---

## Sources

^[pcie-tlp-format.md:1-634]

# Citations

1. [pcie-tlp-format.md:147-163](/references/pcie-tlp-format-b49f845d.md)
2. [pcie-tlp-format.md:9-12](/references/pcie-tlp-format-b49f845d.md)
3. [pcie-tlp-format.md:56-63](/references/pcie-tlp-format-b49f845d.md)
4. [pcie-tlp-format.md:229-263](/references/pcie-tlp-format-b49f845d.md)
5. [pcie-tlp-format.md:231-232](/references/pcie-tlp-format-b49f845d.md)
6. [pcie-tlp-format.md:264-285](/references/pcie-tlp-format-b49f845d.md)
7. [pcie-tlp-format.md:298-308](/references/pcie-tlp-format-b49f845d.md)
8. [pcie-tlp-format.md:309-346](/references/pcie-tlp-format-b49f845d.md)
9. [pcie-tlp-format.md:313-331](/references/pcie-tlp-format-b49f845d.md)
10. [pcie-tlp-format.md:348-387](/references/pcie-tlp-format-b49f845d.md)
11. [pcie-tlp-format.md:381-387](/references/pcie-tlp-format-b49f845d.md)
12. [pcie-tlp-format.md:389-433](/references/pcie-tlp-format-b49f845d.md)
13. [pcie-tlp-format.md:462-481](/references/pcie-tlp-format-b49f845d.md)
14. [pcie-tlp-format.md:283-285](/references/pcie-tlp-format-b49f845d.md)
15. [pcie-tlp-format.md:131-162](/references/pcie-tlp-format-b49f845d.md)
16. [pcie-tlp-format.md:437-490](/references/pcie-tlp-format-b49f845d.md)
17. [pcie-tlp-format.md:1-634](/references/pcie-tlp-format-b49f845d.md)
