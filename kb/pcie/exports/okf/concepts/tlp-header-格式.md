---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: dafc214efdee9bf1bd3493be638fb3defda705c52d0fb35e5ef6fb65dfc02845
  pageDirectory: concepts
  sources:
    - pcie-tlp-format.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - tlp-header-格式
    - TH格
  citations:
    - file: pcie-tlp-format.md
      start: 3
      end: 12
    - file: pcie-tlp-format.md
      start: 56
      end: 63
    - file: pcie-tlp-format.md
      start: 68
      end: 107
    - file: pcie-tlp-format.md
      start: 109
      end: 125
    - file: pcie-tlp-format.md
      start: 131
      end: 141
    - file: pcie-tlp-format.md
      start: 143
      end: 162
    - file: pcie-tlp-format.md
      start: 170
      end: 175
    - file: pcie-tlp-format.md
      start: 177
      end: 194
    - file: pcie-tlp-format.md
      start: 196
      end: 211
    - file: pcie-tlp-format.md
      start: 213
      end: 223
    - file: pcie-tlp-format.md
      start: 229
      end: 262
    - file: pcie-tlp-format.md
      start: 264
      end: 296
    - file: pcie-tlp-format.md
      start: 309
      end: 346
    - file: pcie-tlp-format.md
      start: 389
      end: 433
    - file: pcie-tlp-format.md
      start: 493
      end: 544
    - file: pcie-tlp-format.md
      start: 607
      end: 616
title: TLP Header 格式
description: TLP头部的标准结构，分为3 DW(32位地址)和4 DW(64位地址)两种格式，包含Fmt、Type、Length、Requester ID等关键字段
tags:
  - pcie
  - header
  - data-structure
timestamp: "2026-08-16T06:48:30.808Z"
---


# TLP Header 格式

## 概述

TLP Header 是事务层数据包（Transaction Layer Packet）的控制核心，用于携带事务的路由信息、属性参数和传输配置。TLP Header 必须与 Data Payload 组合才能构成完整的 TLP，在 PCIe 协议栈中由事务层生成后依次传递给数据链路层和物理层进行封装和传输。 ^[pcie-tlp-format.md:3-12]

TLP Header 根据地址宽度分为两种类型：**3 DW（12 字节）Header** 用于 32 位地址事务和消息，**4 DW（16 字节）Header** 用于 64 位地址事务。这种设计使协议能够灵活适配不同的寻址需求，同时最小化不必要的开销。 ^[pcie-tlp-format.md:56-63]

## Header 字段结构

### 3 DW Header 格式（通用）

3 DW Header 共 12 字节，分三个双字（Double Word）排列，各字段定义如下： ^[pcie-tlp-format.md:68-107]

**DW 0（字节 0-3）** 包含 TLP 的核心控制字段：

| 字段 | 位宽 | 功能说明 |
|------|------|----------|
| Fmt | 3 bits | 指示 Header 长度和数据存在性 |
| Type | 5 bits | 结合 Fmt 定义具体 TLP 类型 |
| R | 1 bit | 保留字段 |
| TC | 3 bits | 流量类别（0-7），用于 QoS 和虚拟通道映射 |
| Attr | 2+1 bits | 属性字段，指示排序和缓存一致性特性 |
| TH | 1 bit | TLP 处理提示 |
| TD | 1 bit | 指示是否存在 ECRC 摘要 |
| EP | 1 bit | 毒化位，标记数据可能不可靠 |
| AT | 2 bits | 地址类型 |
| Length | 10 bits | 数据负载长度，单位为 DW |

**DW 1（字节 4-7）** 包含请求者标识和字节使能：

| 字段 | 位宽 | 功能说明 |
|------|------|----------|
| Requester ID | 16 bits | 请求者的 BDF（Bus:Device:Function）地址 |
| Tag | 8 bits | 用于匹配 Request 和 Completion |
| Last DW BE | 4 bits | 最后一个 DW 的字节使能 |
| First DW BE | 4 bits | 第一个 DW 的字节使能 |

**DW 2（字节 8-11）** 根据 TLP 类型承载不同信息：

- 对于 Memory Request：32 位内存地址（低 2 位恒为 0，对齐到 DW）
- 对于 Configuration Request：目标设备的 Bus/Dev/Fun 和寄存器地址
- 对于 Completion：Completer ID 和完成状态

### 4 DW Header 格式（64 位地址）

4 DW Header 在 3 DW Header 基础上增加两个双字来存储高位地址： ^[pcie-tlp-format.md:109-125]

- **DW 2（字节 8-11）**：Address[63:32]，64 位地址的高 32 位
- **DW 3（字节 12-15）**：Address[31:2]，64 位地址的低 30 位

这种格式专用于需要访问超过 4GB 地址空间的内存事务。

## 关键字段详解

### Fmt（Format）字段

Fmt 字段用 3 位编码指示 Header 的长度和数据载荷的存在性： ^[pcie-tlp-format.md:131-141]

| Fmt 值 | 含义 |
|--------|------|
| 000b | 3 DW Header，无数据 |
| 001b | 4 DW Header，无数据 |
| 010b | 3 DW Header，带数据 |
| 011b | 4 DW Header，带数据 |
| 100b | TLP Prefix（PCIe 3.0+） |

### Type 字段

Type 字段与 Fmt 字段组合共同定义完整的 TLP 类型： ^[pcie-tlp-format.md:143-162]

| Fmt | Type | TLP 类型 |
|-----|------|----------|
| 000b | 00000b | Memory Read Request（32 位） |
| 001b | 00000b | Memory Read Request（64 位） |
| 010b | 00000b | Memory Write Request（32 位） |
| 011b | 00000b | Memory Write Request（64 位） |
| 000b | 00010b | IO Read Request |
| 010b | 00010b | IO Write Request |
| 000b | 00100b | Configuration Read Type 0 |
| 010b | 00100b | Configuration Write Type 0 |
| 000b | 00101b | Configuration Read Type 1 |
| 010b | 00101b | Configuration Write Type 1 |
| 000b | 1xxxxxb | Message Request |
| 010b | 1xxxxxb | Message Request with Data |
| 000b | 01010b | Completion |
| 010b | 01010b | Completion with Data |

### Length 字段

Length 字段以 DW（4 字节）为单位表示数据负载长度，共 10 位。需要注意当 Length 为 0 时实际表示 1024 DW（4096 字节）。 ^[pcie-tlp-format.md:170-175]

### Requester ID 与 Tag

Requester ID 使用 16 位编码请求者的 BDF 地址，其中 Bus 占 8 位、Device 占 5 位、Function 占 3 位。Tag 字段占 8 位，允许发起最多 256 个并发未完成的 Non-Posted 请求，Completion 必须携带与原请求相同的 Tag 才能正确匹配。 ^[pcie-tlp-format.md:177-194]

### [Byte Enable 字段](/concepts/byte-enable-字段.md)

Byte Enable 用于指示数据传输中哪些字节有效。First DW BE 表示首个双字中有效的字节，Last DW BE 表示末尾双字中有效的字节。这一机制使 TLP 支持非对齐和非整 DW 的数据传输。 ^[pcie-tlp-format.md:196-211]

### TD 与 EP 字段

TD（TLP Digest）位指示 TLP 末尾是否包含 ECRC（端到端 CRC）校验字段。EP（Error/Poisoned）位标记数据是否被"毒化"，即在检测到错误但仍需要转发的情况下使用。 ^[pcie-tlp-format.md:213-223]

## 常见 TLP 的 Header 格式

### Memory Read Request（MRd）

Memory Read Request 使用 3 DW Header（32 位地址）或 4 DW Header（64 位地址），无数据负载。Header 中 Length 字段表示要读取的 DW 数量，接收方通过 Completion with Data 返回数据。 ^[pcie-tlp-format.md:229-262]

### Memory Write Request（MWr）

Memory Write Request 同样使用 3 DW 或 4 DW Header，但 Fmt 字段指示存在 Data Payload。MWr 是 Posted Transaction，无需 Completion 响应，因此更高效但无法确认写入成功。 ^[pcie-tlp-format.md:264-296]

### Configuration Request

Configuration Request 分为 Type 0 和 Type 1 两种。Type 0 用于访问直连设备，Type 1 用于通过 Bridge 访问下游设备。DW 2 字段包含目标 Bus/Device/Function 号以及扩展寄存器和寄存器号信息。 ^[pcie-tlp-format.md:309-346]

### Completion（Cpl/CplD）

Completion 用于响应 Non-Posted 请求，其 Header 结构与前述 Request 类似，但 DW 1 和 DW 2 包含不同的字段：Completer ID 标识完成者，Status 字段指示完成状态（成功、不支持的请求、重试或中止），Byte Count 表示剩余待传输字节数。 ^[pcie-tlp-format.md:389-433]

## TLP Header 与协议栈

在 PCIe 协议栈中，TLP Header 的生成和传输遵循特定的流程。发送端事务层首先检查流控制信用（Flow Control Credit），然后根据事务类型构建 Header，设置 Fmt/Type、地址/ID、Length、Tag 和 Byte Enable 等字段，最后将 Header 与 Data Payload 组合并计算可选的 ECRC。接收端事务层验证 ECRC 后解析 Header，根据路由信息决定是本地处理还是转发。 ^[pcie-tlp-format.md:493-544]

## 总结

TLP Header 是 PCIe 事务层用于描述事务特征和控制传输行为的核心数据结构。3 DW 和 4 DW 两种 Header 格式分别支持 32 位和 64 位地址事务，Fmt/Type 字段组合定义了 Memory、IO、Configuration、Message 和 Completion 等多种事务类型。Requester ID 和 Tag 字段共同支持 Non-Posted Transaction 的请求-完成匹配机制，而 Byte Enable 字段提供了灵活的数据字节使能能力。 ^[pcie-tlp-format.md:607-616]

---

## Sources

- [pcie-tlp-format.md](pcie-tlp-format.md)

# Citations

1. [pcie-tlp-format.md:3-12](/references/pcie-tlp-format-b49f845d.md)
2. [pcie-tlp-format.md:56-63](/references/pcie-tlp-format-b49f845d.md)
3. [pcie-tlp-format.md:68-107](/references/pcie-tlp-format-b49f845d.md)
4. [pcie-tlp-format.md:109-125](/references/pcie-tlp-format-b49f845d.md)
5. [pcie-tlp-format.md:131-141](/references/pcie-tlp-format-b49f845d.md)
6. [pcie-tlp-format.md:143-162](/references/pcie-tlp-format-b49f845d.md)
7. [pcie-tlp-format.md:170-175](/references/pcie-tlp-format-b49f845d.md)
8. [pcie-tlp-format.md:177-194](/references/pcie-tlp-format-b49f845d.md)
9. [pcie-tlp-format.md:196-211](/references/pcie-tlp-format-b49f845d.md)
10. [pcie-tlp-format.md:213-223](/references/pcie-tlp-format-b49f845d.md)
11. [pcie-tlp-format.md:229-262](/references/pcie-tlp-format-b49f845d.md)
12. [pcie-tlp-format.md:264-296](/references/pcie-tlp-format-b49f845d.md)
13. [pcie-tlp-format.md:309-346](/references/pcie-tlp-format-b49f845d.md)
14. [pcie-tlp-format.md:389-433](/references/pcie-tlp-format-b49f845d.md)
15. [pcie-tlp-format.md:493-544](/references/pcie-tlp-format-b49f845d.md)
16. [pcie-tlp-format.md:607-616](/references/pcie-tlp-format-b49f845d.md)
