---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: df7744085a374a899e472bfc83400d0ca20cdc28a5e3ee6343ca40e963e7bf3a
  pageDirectory: concepts
  sources:
    - pcie-layering.md
  confidence: 0.9
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - lcrc-与-ecrc-错误检测
    - L与E错
  citations:
    - file: pcie-layering.md
      start: 25
      end: 25
    - file: pcie-layering.md
      start: 110
      end: 113
    - file: pcie-layering.md
      start: 260
      end: 277
    - file: pcie-layering.md
      start: 262
      end: 262
    - file: pcie-layering.md
      start: 263
      end: 267
    - file: pcie-layering.md
      start: 229
      end: 258
    - file: pcie-layering.md
      start: 275
      end: 275
title: LCRC 与 ECRC 错误检测
description: 链路CRC保护单跳传输，端到端CRC保护整个通信路径，两者在协议栈不同层次协同工作
tags:
  - pcie
  - error-detection
  - crc
timestamp: "2026-08-16T06:40:14.959Z"
---

# LCRC 与 ECRC 错误检测

## 概述

在 PCIe 协议中，错误检测机制分布在不同的协议层次，以确保数据在传输过程中的完整性。PCIe 采用两级 CRC 校验机制：

- **LCRC（Link CRC，链路 CRC）**：由数据链路层添加和保护
- **ECRC（End-to-End CRC，端到端 CRC）**：由事务层添加和保护

这两种 CRC 机制相互配合，共同构成了 PCIe 可靠传输的基石。^[pcie-layering.md:25, pcie-layering.md:110-113, pcie-layering.md:260-277]

## LCRC（Link CRC，链路 CRC）

### 定义与特性

LCRC 是 **32 位 CRC-32 校验和**，用于覆盖整个 TLP（Transaction Layer Packet），包括头部和数据载荷部分。^[pcie-layering.md:262]

LCRC 具有以下关键特性：

| 特性 | 说明 |
|------|------|
| **位宽** | 32 位（CRC-32） |
| **覆盖范围** | 整个 TLP（Header + Data） |
| **添加位置** | 数据链路层 |
| **验证位置** | 数据链路层 |
| **强制性** | 必须（所有设备必须支持） |
| **可见性** | 软件不可见，由硬件自动处理 |

### 工作机制

LCRC 由发送端的数据链路层自动计算并添加到 TLP 尾部，接收端的数据链路层负责验证。^[pcie-layering.md:263-267]

数据链路层在发送 TLP 时会执行以下步骤：

1. 在 TLP 尾部添加 **Sequence Number（序列号）**
2. 计算 TLP 的 LCRC 值并附加
3. 将完整的 TLP 发送到物理层进行传输

接收端数据链路层的验证流程：

1. 接收来自物理层的 TLP
2. 重新计算 LCRC 并与接收到的 LCRC 比较
3. 若匹配则发送 Ack DLLP；若不匹配则发送 Nak DLLP 请求重传

### 与 ACK/NAK 协议的关系

LCRC 是 ACK/NAK 协议的核心组成部分，用于检测传输过程中的位错误。^[pcie-layering.md:229-258]

```
发送方                                      接收方
  │                                            │
  ├──> TLP #101 (Seq=101, Data, LCRC) ───────>│
  │                                            ├─> 检查 LCRC
  │                                            ├─> LCRC Error!
  │    <────────── Nak DLLP (Seq=101) ────────┤
  │                                            │
  ├─> 从 Retry Buffer 重传 TLP #101           │
```

## ECRC（End-to-End CRC，端到端 CRC）

### 定义与特性

ECRC 是事务层提供的可选错误检测机制，占用 **4 字节**，用于端到端的数据完整性校验。^[pcie-layering.md:110-113]

ECRC 的特性：

| 特性 | 说明 |
|------|------|
| **位宽** | 32 位 |
| **覆盖范围** | TLP Header + Data（部分字段除外） |
| **添加位置** | 事务层 |
| **验证位置** | 事务层（最终目标设备） |
| **强制性** | 可选 |
| **配置方式** | 通过 PCIe AER（高级错误报告）能力寄存器使能 |

### TLP 结构中的 ECRC

```
┌───────────────────────────────────────────────────────────────┐
│                     TLP Header (3 or 4 DW)                    │
│  • Fmt/Type (格式/类型)                                        │
│  • Length (长度)                                               │
│  • Requester ID (请求者 ID)                                    │
│  • Tag (标签)                                                  │
│  • Address (地址) or Completer ID                             │
├───────────────────────────────────────────────────────────────┤
│                     Data Payload (0-1024 DW)                  │
│  • 实际数据内容                                                 │
│  • 最大 4096 字节                                              │
├───────────────────────────────────────────────────────────────┤
│                     ECRC (4 bytes)                            │  ← 可选
│  • End-to-End CRC                                             │
│  • 端到端数据完整性校验                                         │
└───────────────────────────────────────────────────────────────┘
```

### 保护范围

与 LCRC 不同，ECRC 的设计目的是为整个数据传输路径提供端到端保护。它能够检测以下错误类型：^[pcie-layering.md:275]

- **Switch 内部错误**：数据在交换芯片内部处理时可能发生的错误
- **内存错误**：数据存储在系统内存中可能发生的位翻转等错误
- **软件配置错误**：事务层处理过程中可能出现的配置问题

## LCRC 与 ECRC 对比

| 特性 | LCRC | ECRC |
|------|------|------|
| **覆盖范围** | 每一跳（逐跳） | 端到端（整个路径） |
| **添加位置** | 数据链路层 | 事务层 |
| **验证位置** | 每跳（接收方数据链路层） | 最终目标（接收方事务层） |
| **保护对象** | 链路传输错误 | Switch 内部错误、内存错误 |
| **协议层** | 数据链路层 | 事务层 |
| **强制性** | 必须支持 | 可选 |
| **重传机制** | 支持（LCRC 错误触发重传） | 不支持（错误报告但不重传） |
| **检测时机** | 每跳立即检测 | 到达最终目标设备后检测 |

### 工作层次对比

```
┌─────────────────────────────────────────────────────────────┐
│          Software Layer (软件层)                            │
└────────────────┬───────────────────────────────────────────┘
                 │
┌────────────────▼───────────────────────────────────────────┐
│     Transaction Layer (事务层 - TL)                        │
│  • ECRC 在此添加和验证                                       │
│  • 检测 Switch 内部错误、内存错误                            │
└────────────────┬───────────────────────────────────────────┘
                 │ TLP + ECRC（可选）
┌────────────────▼───────────────────────────────────────────┐
│     Data Link Layer (数据链路层 - DLL)                      │
│  • LCRC 在此添加和验证                                      │
│  • ACK/NAK 协议保证可靠传输                                 │
│  • 检测链路传输错误                                         │
└────────────────┬───────────────────────────────────────────┘
                 │ TLP + LCRC + Sequence Number
┌────────────────▼───────────────────────────────────────────┐
│     Physical Layer (物理层 - PHY)                           │
│  • 串行化/解串行化                                          │
│  • 8b/10b 或 128b/130b 编码                                 │
└─────────────────────────────────────────────────────────────┘
```

## 错误检测流程

### 发送路径

1. **事务层**：构造 TLP，可选添加 ECRC
2. **数据链路层**：添加序列号，计算并附加 LCRC
3. **物理层**：编码、串行化并发送

### 接收路径

1. **物理层**：接收串行数据，解码、反串行化
2. **数据链路层**：验证 LCRC
   - LCRC 正确 → 发送 Ack DLLP，移除 LCRC 和序列号，向上传递
   - LCRC 错误 → 发送 Nak DLLP，请求重传
3. **事务层**：验证 ECRC（如果存在）
   - ECRC 正确 → 处理 TLP
   - ECRC 错误 → 记录错误状态，可能触发错误中断

## 配置与软件支持

ECRC 的使能和验证通常通过以下机制控制：

- **PCIe AER（Advanced Error Reporting）**：高级错误报告能力
- **Device Control Register**：设备控制寄存器中的 ECRC 相关位
- **ECRC Check Enable**：允许端点检查收到的 TLP 的 ECRC
- **ECRC Generate Enable**：允许端点为发出的 TLP 生成 ECRC

LCRC 的验证由硬件自动完成，软件通常不需要直接配置。当 LCRC 错误发生时，数据链路层会自动触发重传机制，软件可能通过错误日志获知发生了重传事件。

---

## Sources

- PCIe 三层协议模型](../introduction/pcie-layering.md)

# Citations

1. [pcie-layering.md:25-25](/references/pcie-layering-3c12192c.md)
2. [pcie-layering.md:110-113](/references/pcie-layering-3c12192c.md)
3. [pcie-layering.md:260-277](/references/pcie-layering-3c12192c.md)
4. [pcie-layering.md:262-262](/references/pcie-layering-3c12192c.md)
5. [pcie-layering.md:263-267](/references/pcie-layering-3c12192c.md)
6. [pcie-layering.md:229-258](/references/pcie-layering-3c12192c.md)
7. [pcie-layering.md:275-275](/references/pcie-layering-3c12192c.md)
