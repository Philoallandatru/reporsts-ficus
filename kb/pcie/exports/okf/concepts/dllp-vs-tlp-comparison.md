---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 528ab700998028afc89f1cfdc6e8e443c2b9f3e8ddd34fe9a2114f0d44db937b
  pageDirectory: concepts
  sources:
    - pcie-dllp-format.md
  confidence: 1
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - dllp-vs-tlp-comparison
    - DVTC
  citations:
    - file: pcie-dllp-format.md
      start: 9
      end: 12
    - file: pcie-dllp-format.md
      start: 66
      end: 71
    - file: pcie-dllp-format.md
      start: 459
      end: 469
    - file: pcie-dllp-format.md
      start: 29
      end: 40
    - file: pcie-dllp-format.md
      start: 48
      end: 69
    - file: pcie-dllp-format.md
      start: 104
      end: 149
    - file: pcie-dllp-format.md
      start: 581
      end: 595
    - file: pcie-dllp-format.md
      start: 69
      end: 69
    - file: pcie-dllp-format.md
      start: 419
      end: 451
    - file: pcie-dllp-format.md
      start: 468
      end: 468
    - file: pcie-dllp-format.md
      start: 207
      end: 327
    - file: pcie-dllp-format.md
      start: 473
      end: 482
    - file: pcie-dllp-format.md
      start: 598
      end: 600
    - file: pcie-dllp-format.md
      start: 14
      end: 27
    - file: pcie-dllp-format.md
      start: 252
      end: 273
    - file: pcie-dllp-format.md
      start: 330
      end: 393
title: DLLP vs TLP Comparison
description: DLLP与TLP的对比：DLLP为8字节固定长度控制包，TLP为可变长度数据包，两者协议栈位置和用途不同
tags:
  - pcie
  - comparison
  - protocol
timestamp: "2026-08-16T06:37:23.462Z"
---


# DLLP 与 TLP 比较

## 概述

DLLP（Data Link Layer Packet）和 TLP（Transaction Layer Packet）是 PCIe 协议栈中两个核心的包类型，分别运行在不同的协议层次，具有不同的功能和特性。理解两者之间的区别对于掌握 PCIe 链路管理机制和数据传输原理至关重要。 ^[pcie-dllp-format.md:9-12]

DLLP 由数据链路层生成，用于承载链路控制信息；TLP 由事务层生成，用于承载用户数据和事务。这种分工使得协议能够有效地将数据传输功能与链路可靠性保证分离。 ^[pcie-dllp-format.md:9-12]

---

## 基本特性对比

| 特性 | DLLP | TLP |
|------|------|-----|
| **生成层** | 数据链路层 | 事务层 |
| **长度** | 固定 8 字节 | 可变（12-4108 字节） |
| **用途** | 链路控制（ACK/FC/PM） | 数据传输（Memory/IO/Config） |
| **序列号** | 无 | 有（12-bit） |
| **需要确认** | 否 | 是（通过 Ack DLLP） |
| **CRC** | CRC-16 (2 字节) | LCRC (4 字节) |
| **重传** | 不重传 | 支持重传 |
| **流控制** | 不消耗信用 | 消耗信用 |
| **物理层编码** | 与 TLP 相同 | 与 DLLP 相同 |

^[pcie-dllp-format.md:66-71] ^[pcie-dllp-format.md:459-469]

---

## 详细差异分析

### 生成层次与功能定位

DLLP 和 TLP 在协议栈中的位置决定了它们各自的功能角色。事务层负责处理来自软件或硬件的应用数据请求，生成 TLP 来执行 Memory Read、 Memory Write 等事务。而数据链路层则专注于链路的可靠传输，在 TLP 基础上添加序列号和 LCRC，并生成用于链路管理的 DLLP。 ^[pcie-dllp-format.md:29-40]

这种分层设计使得两层可以独立演进和优化。事务层可以专注于数据语义和事务ordering规则，而数据链路层则专注于物理链路的可靠性和流控制。

### 长度与格式差异

DLLP 采用固定长度设计，所有 DLLP 都是 8 字节（64 位），由以下部分组成：
- **字节 0-1**：DLLP Type + Reserved（2 字节）
- **字节 2-5**：DLLP Content（Type-Specific，4 字节）
- **字节 6-7**：CRC-16（2 字节）

这种固定格式简化了硬件实现，因为接收端可以预知 DLLP 的边界。相比之下，TLP 的长度是可变的，范围从 12 字节到 4108 字节不等，具体取决于事务类型、数据负载和可选的 ECRC 字段。 ^[pcie-dllp-format.md:48-69]

### 可靠性机制

TLP 的可靠传输依赖于 ACK/NAK 机制。发送方为每个 TLP 分配一个 12 位的序列号（Seq#），接收方通过 Ack DLLP 确认成功接收的 TLP，或通过 Nak DLLP 请求重传。当发送方在超时时间内未收到 Ack 时，会自动重传所有未确认的 TLP。 ^[pcie-dllp-format.md:104-149]

DLLP 则不参与这一可靠性机制。DLLP 本身不被确认，丢失后也不会重传。如果 Ack DLLP 丢失，发送方超时后会重传对应的 TLP；如果 UpdateFC DLLP 丢失，接收方会继续发送新的 UpdateFC 来补充信用。这种设计避免了递归确认的问题（确认的确认...）。 ^[pcie-dllp-format.md:581-595]

### 校验机制

TLP 使用 32 位的 LCRC（Link CRC）进行错误检测，可选还支持端到端的 ECRC。较长的 CRC 提供了更强的错误检测能力，适用于携带重要数据的包。DLLP 则使用 16 位的 CRC-16（基于多项式 x¹⁶ + x¹⁵ + x² + 1），覆盖 DLLP 的前 6 字节。当 DLLP 的 CRC 错误时，该包被直接丢弃。 ^[pcie-dllp-format.md:69] ^[pcie-dllp-format.md:419-451]

### 流控制

TLP 的传输受到流控制机制的约束。每个接收端口公告其缓冲区容量（通过 InitFC DLLP 交换），发送方必须根据可用的信用（Credit）来发送 TLP。发送每种类型的 TLP 会消耗相应的 Header Credit 或 Data Credit。 ^[pcie-dllp-format.md:468] ^[pcie-dllp-format.md:207-327]

DLLP 本身不消耗任何信用，也不会影响流控制。UpdateFC DLLP 用于通知对方已释放的缓冲区空间，从而补充信用。这种设计确保了链路控制信息能够优先传输，不会因为信用耗尽而被阻塞。

---

## 混合传输机制

DLLP 和 TLP 在物理层上混合传输，物理层可以通过插入 DLLP 而不影响 TLP 的传输顺序。这种机制允许链路控制信息（如 Ack、Nak、UpdateFC）能够及时传达，而不会干扰数据事务的处理。 ^[pcie-dllp-format.md:473-482]

物理层通过帧头来区分 DLLP 和 TLP：
- TLP 以 `STP`（Start of TLP）开始
- DLLP 以 `SDP`（Start of DLLP）开始

这种明确的分隔符设计使得接收端能够正确解析两种不同类型的包。 ^[pcie-dllp-format.md:598-600]

---

## 功能对比总结

| 功能 | DLLP | TLP |
|------|------|-----|
| **ACK/NAK** | 提供确认机制 | 需要被确认 |
| **流控制初始化** | InitFC1 → InitFC2 | 依赖 DLLP 完成 |
| **流控制更新** | UpdateFC | 消耗信用 |
| **电源管理** | PM_Enter_L1/L23 | 无 |
| **厂商自定义** | Vendor-Specific DLLP | 无 |
| **事务类型** | 无 | Memory/IO/Config/NPMSG |

^[pcie-dllp-format.md:14-27] ^[pcie-dllp-format.md:459-469]

---

## 典型应用场景

在实际系统中，DLLP 和 TLP 通常按照以下模式交互：

1. **链路初始化阶段**：双方通过 InitFC1/InitFC2 DLLP 交换缓冲区容量信息，建立流控制信用体系。
2. **数据传输阶段**：发送方根据可用信用发送 TLP，接收方通过 UpdateFC DLLP 补充信用。
3. **可靠性保障**：接收方通过 Ack/Nak DLLP 确认 TLP 接收状态，发送方根据反馈重传失败的 TLP。
4. **电源管理**：在空闲时通过 PM_Enter_L1 DLLP 协商进入低功耗状态。 ^[pcie-dllp-format.md:252-273] ^[pcie-dllp-format.md:330-393]

---

## 相关概念

- PCIe 协议栈 - 整体架构概述
- 数据链路层 - DLLP 的生成层
- 事务层 - TLP 的生成层
- 物理层 - 包的传输层
- ACK/NAK 机制 - TLP 可靠传输保证
- 流控制 - 信用管理与缓冲区管理
- 电源管理 - L0/L1/L2/L3 状态转换

---

## 总结

DLLP 和 TLP 是 PCIe 协议中相辅相成的两类包。TLP 负责端到端的数据传输，承载用户事务；DLLP 负责点到点的链路管理，提供可靠性和流控制保障。两者虽然传输机制不同，但在物理层共享相同的编码方式，能够高效地共存于同一条链路上。理解它们之间的区别和联系是掌握 PCIe 技术的重要基础。

---

## Sources

- [pcie-dllp-format.md](../sources/pcie-dllp-format.md) — DLLP 格式详解，涵盖 DLLP 结构、类型、工作机制及 DLLP vs TLP 对比表

# Citations

1. [pcie-dllp-format.md:9-12](/references/pcie-dllp-format-55680021.md)
2. [pcie-dllp-format.md:66-71](/references/pcie-dllp-format-55680021.md)
3. [pcie-dllp-format.md:459-469](/references/pcie-dllp-format-55680021.md)
4. [pcie-dllp-format.md:29-40](/references/pcie-dllp-format-55680021.md)
5. [pcie-dllp-format.md:48-69](/references/pcie-dllp-format-55680021.md)
6. [pcie-dllp-format.md:104-149](/references/pcie-dllp-format-55680021.md)
7. [pcie-dllp-format.md:581-595](/references/pcie-dllp-format-55680021.md)
8. [pcie-dllp-format.md:69-69](/references/pcie-dllp-format-55680021.md)
9. [pcie-dllp-format.md:419-451](/references/pcie-dllp-format-55680021.md)
10. [pcie-dllp-format.md:468-468](/references/pcie-dllp-format-55680021.md)
11. [pcie-dllp-format.md:207-327](/references/pcie-dllp-format-55680021.md)
12. [pcie-dllp-format.md:473-482](/references/pcie-dllp-format-55680021.md)
13. [pcie-dllp-format.md:598-600](/references/pcie-dllp-format-55680021.md)
14. [pcie-dllp-format.md:14-27](/references/pcie-dllp-format-55680021.md)
15. [pcie-dllp-format.md:252-273](/references/pcie-dllp-format-55680021.md)
16. [pcie-dllp-format.md:330-393](/references/pcie-dllp-format-55680021.md)
