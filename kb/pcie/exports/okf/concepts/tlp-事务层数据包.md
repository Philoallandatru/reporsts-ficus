---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: f7fb6060796db765f92618aa359e991d4251207677af36728aa34501fee3ad0b
  pageDirectory: concepts
  sources:
    - pcie-layering.md
    - pcie-tlp-format.md
  confidence: 0.95
  provenanceState: merged
  freshnessStatus: fresh
  aliases:
    - tlp-事务层数据包
  citations:
    - file: pcie-tlp-format.md
      start: 3
      end: 9
    - file: pcie-tlp-format.md
      start: 38
      end: 50
    - file: pcie-tlp-format.md
      start: 52
      end: 52
    - file: pcie-tlp-format.md
      start: 57
      end: 62
    - file: pcie-layering.md
      start: 56
      end: 91
    - file: pcie-tlp-format.md
      start: 131
      end: 141
    - file: pcie-tlp-format.md
      start: 145
      end: 162
    - file: pcie-tlp-format.md
      start: 164
      end: 168
    - file: pcie-tlp-format.md
      start: 170
      end: 175
    - file: pcie-tlp-format.md
      start: 178
      end: 186
    - file: pcie-tlp-format.md
      start: 189
      end: 194
    - file: pcie-tlp-format.md
      start: 196
      end: 211
    - file: pcie-tlp-format.md
      start: 213
      end: 217
    - file: pcie-tlp-format.md
      start: 219
      end: 223
    - file: pcie-tlp-format.md
      start: 437
      end: 489
    - file: pcie-tlp-format.md
      start: 495
      end: 516
    - file: pcie-tlp-format.md
      start: 518
      end: 544
title: TLP (事务层数据包)
description: 事务层数据包，是PCIe中携带实际事务信息的基本单元，包含Header、Data Payload和可选的ECRC
tags:
  - pcie
  - transaction-layer
  - packet-format
timestamp: "2026-08-16T06:39:28.421Z"
---


# TLP (事务层数据包)

**TLP (Transaction Layer Packet)** 是 PCI Express (PCIe) 协议中由**事务层**生成和处理的基本数据单元。所有在 PCIe 总线上传输的读写事务、消息请求和完成响应都以 TLP 的形式封装和传递。

---

## 概述

TLP 是 PCIe 通信的基本单元，由事务层构建并沿协议栈向下传递。 ^[pcie-tlp-format.md:3-9]

TLP 在协议栈中的位置如下：

```
应用层数据
    ↓
┌─────────────────────────────────┐
│  Transaction Layer (事务层)      │
│  生成 TLP：Header + Data         │
└─────────────┬───────────────────┘
              │ TLP
┌─────────────▼───────────────────┐
│  Data Link Layer (数据链路层)    │
│  添加 Sequence Number + LCRC     │
└─────────────┬───────────────────┘
              │ TLP + LCRC
┌─────────────▼───────────────────┐
│  Physical Layer (物理层)         │
│  Framing + Encoding             │
└─────────────────────────────────┘
```

---

## TLP 基本结构

TLP 由三个部分组成： ^[pcie-tlp-format.md:38-50]

| 组成部分 | 大小 | 说明 |
|---------|------|------|
| **Header** | 3 DW (12字节) 或 4 DW (16字节) | 控制信息和路由信息 |
| **Data Payload** | 0-1024 DW (最大 4096 字节) | 实际传输的数据（可选） |
| **ECRC** | 1 DW (4 字节) | 端到端 CRC 校验（可选） |

其中 **DW (Double Word)** = 32 bits = 4 字节。 ^[pcie-tlp-format.md:52]

### Header 类型

PCIe 定义了两种 Header 长度： ^[pcie-tlp-format.md:57-62]

- **3 DW Header (12 字节)**：用于 32 位地址事务、消息、完成
- **4 DW Header (16 字节)**：用于 64 位地址事务

---

## TLP 类型

PCIe 定义了多种 TLP 类型以支持不同的通信需求： ^[pcie-layering.md:56-91]

### 1. Memory Request (内存请求)

```
Memory Read Request (MRd)
Memory Write Request (MWr)
```

- 支持 32 位和 64 位地址
- Memory Write 为 **Posted** 事务，无需对方响应
- Memory Read 为 **Non-Posted** 事务，需要 Completion 响应

### 2. IO Request (IO 请求)

```
IO Read Request (IORd)
IO Write Request (IOWr)
```

- 仅支持 32 位地址
- 用于访问传统 IO 地址空间
- Non-Posted 事务

### 3. Configuration Request (配置请求)

```
Configuration Read (CfgRd0/CfgRd1)
Configuration Write (CfgWr0/CfgWr1)
```

- **Type 0**：访问直连设备
- **Type 1**：通过 Bridge 访问下游设备
- 用于设备枚举和配置空间访问

### 4. Message Request (消息请求)

```
Message (Msg)
Message with Data (MsgD)
```

用于中断、电源管理、错误报告等事件通知，例如 MSI/MSI-X 中断。

### 5. Completion (完成响应)

```
Completion (Cpl)
Completion with Data (CplD)
```

用于响应 Non-Posted 请求（如 Memory Read、IO 访问、配置访问）。

---

## TLP Header 字段详解

### Fmt (Format) - 3 位

指示 TLP 的基本格式： ^[pcie-tlp-format.md:131-141]

| Fmt 值 | 含义 |
|--------|------|
| 000b | 3 DW Header, 无数据 |
| 001b | 4 DW Header, 无数据 |
| 010b | 3 DW Header, 带数据 |
| 011b | 4 DW Header, 带数据 |
| 100b | TLP Prefix (PCIe 3.0+) |

### Type - 5 位

结合 Fmt 字段，完整定义 TLP 类型： ^[pcie-tlp-format.md:145-162]

| Fmt[2:0] | Type[4:0] | TLP 类型 |
|----------|-----------|---------|
| 000b | 00000b | Memory Read Request (MRd) |
| 010b | 00000b | Memory Write Request (MWr) |
| 000b | 00010b | IO Read Request |
| 010b | 00010b | IO Write Request |
| 000b | 00100b | Configuration Read Type 0 |
| 010b | 00100b | Configuration Write Type 0 |
| 000b | 1xxxxb | Message (Msg) |
| 010b | 1xxxxb | Message with Data (MsgD) |
| 000b | 01010b | Completion (Cpl) |
| 010b | 01010b | Completion with Data (CplD) |

### TC (Traffic Class) - 3 位

流量类别，用于 虚拟通道 映射和 QoS 控制。共 8 个等级 (0-7)，默认使用 TC0。 ^[pcie-tlp-format.md:164-168]

### Length - 10 位

数据负载长度，单位为 DW (4 字节)： ^[pcie-tlp-format.md:170-175]

- **0**：表示 1024 DW (4096 字节)
- **1-1023**：实际 DW 数量
- **最大**：4096 字节

### Requester ID - 16 位

请求者的 BDF (Bus:Device.Function) 地址： ^[pcie-tlp-format.md:178-186]

```
┌────────────┬──────────────┬───────────────┐
│   Bus      │   Device     │   Function    │
│  (8 bits)  │   (5 bits)   │   (3 bits)    │
└────────────┴──────────────┴───────────────┘
```

### Tag - 8 位

用于匹配 Non-Posted Request 和其 Completion。发起方生成唯一 Tag，Completion 必须携带相同的 Tag，最多允许 256 个并发未完成请求。 ^[pcie-tlp-format.md:189-194]

### Byte Enable (BE)

指示 DW 中哪些字节有效： ^[pcie-tlp-format.md:196-211]

- **First DW BE**：第一个 DW 的字节使能
- **Last DW BE**：最后一个 DW 的字节使能

### EP (Error/Poisoned) - 1 位

指示 TLP 数据可能不可靠。EP=1 表示数据被"毒化"（检测到错误但仍转发）。 ^[pcie-tlp-format.md:213-217]

### TD (TLP Digest) - 1 位

指示是否包含 ECRC： ^[pcie-tlp-format.md:219-223]

- **0**：无 ECRC
- **1**：TLP 末尾包含 ECRC

---

## [TLP 路由机制](/concepts/tlp-路由机制.md)

PCIe 定义了三种 TLP 路由方式： ^[pcie-tlp-format.md:437-489]

### 1. Address-Based Routing (基于地址)

用于 Memory Request。Switch/Bridge 比较 TLP 地址与自身管理的地址窗口进行转发。

### 2. ID-Based Routing (基于 ID)

用于 Configuration Request 和 Completion。使用 Bus:Device.Function 地址进行路由，Completion 使用 Requester ID 反向路由。

### 3. Implicit Routing (隐式路由)

用于某些 Message（如 INTx 中断）。根据消息类型和端口类型决定路由路径。

---

## [TLP 处理流程](/concepts/tlp-处理流程.md)

### 发送方处理流程

```
1. 应用层发起事务请求
   ↓
2. 事务层检查流控制信用
   ↓
3. 构建 TLP Header (Fmt/Type, 地址/ID, Length, Tag, BE)
   ↓
4. 添加 Data Payload (如果有)
   ↓
5. 计算并添加 ECRC (如果启用)
   ↓
6. 消耗流控制信用
   ↓
7. 传递给数据链路层
```

^[pcie-tlp-format.md:495-516]

### 接收方处理流程

```
1. 从数据链路层接收 TLP
   ↓
2. 验证 ECRC (如果存在)
   ↓
3. 解析 Header
   ↓
4. 路由判断 (本设备处理或转发)
   ↓
5. 处理事务
   ↓
6. 生成 Completion (如果是 Non-Posted)
   ↓
7. 更新流控制信用
```

^[pcie-tlp-format.md:518-544]

---

## 相关概念

- 事务层：生成和处理 TLP 的 PCIe 协议层
- 数据链路层：为 TLP 添加序列号和 LCRC，提供可靠传输
- DLLP：数据链路层控制包，用于 ACK/NAK 和流控制
- 虚拟通道：基于 TC 标签实现流量分类和 QoS
- 流控制：基于信用的机制，防止缓冲区溢出
- 排序规则：保证 TLP 顺序一致性的规则
- ECRC：端到端 CRC，提供数据完整性校验

---

## 总结

TLP 是 PCIe 协议中承载所有事务的基本单元：

1. **结构**：由 Header (3/4 DW)、Data Payload (最大 4096 字节) 和可选 ECRC 组成
2. **类型**：支持 Memory、IO、Configuration、Message 和 Completion 五种事务类型
3. **路由**：通过地址、ID 或隐式方式在 PCIe 网络中传递
4. **处理**：经过事务层、数据链路层、物理层的封装和传递

---

## Sources

- PCIe 三层协议模型](../architecture/pcie-layering.md)
- [TLP 格式详解](../transaction-layer/tlp-format.md)

# Citations

1. [pcie-tlp-format.md:3-9](/references/pcie-tlp-format-b49f845d.md)
2. [pcie-tlp-format.md:38-50](/references/pcie-tlp-format-b49f845d.md)
3. [pcie-tlp-format.md:52-52](/references/pcie-tlp-format-b49f845d.md)
4. [pcie-tlp-format.md:57-62](/references/pcie-tlp-format-b49f845d.md)
5. [pcie-layering.md:56-91](/references/pcie-layering-3c12192c.md)
6. [pcie-tlp-format.md:131-141](/references/pcie-tlp-format-b49f845d.md)
7. [pcie-tlp-format.md:145-162](/references/pcie-tlp-format-b49f845d.md)
8. [pcie-tlp-format.md:164-168](/references/pcie-tlp-format-b49f845d.md)
9. [pcie-tlp-format.md:170-175](/references/pcie-tlp-format-b49f845d.md)
10. [pcie-tlp-format.md:178-186](/references/pcie-tlp-format-b49f845d.md)
11. [pcie-tlp-format.md:189-194](/references/pcie-tlp-format-b49f845d.md)
12. [pcie-tlp-format.md:196-211](/references/pcie-tlp-format-b49f845d.md)
13. [pcie-tlp-format.md:213-217](/references/pcie-tlp-format-b49f845d.md)
14. [pcie-tlp-format.md:219-223](/references/pcie-tlp-format-b49f845d.md)
15. [pcie-tlp-format.md:437-489](/references/pcie-tlp-format-b49f845d.md)
16. [pcie-tlp-format.md:495-516](/references/pcie-tlp-format-b49f845d.md)
17. [pcie-tlp-format.md:518-544](/references/pcie-tlp-format-b49f845d.md)
