---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 4f22175a09aed40b2a50119413cb36c62510fe9bc2911989435f5ba10cb5da47
  pageDirectory: concepts
  sources:
    - pcie-dllp-format.md
  confidence: 1
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - dllp-data-link-layer-packet
    - D(LLP
  citations:
    - file: pcie-dllp-format.md
      start: 3
      end: 12
    - file: pcie-dllp-format.md
      start: 14
      end: 27
    - file: pcie-dllp-format.md
      start: 29
      end: 40
    - file: pcie-dllp-format.md
      start: 48
      end: 60
    - file: pcie-dllp-format.md
      start: 62
      end: 71
    - file: pcie-dllp-format.md
      start: 79
      end: 101
    - file: pcie-dllp-format.md
      start: 104
      end: 134
    - file: pcie-dllp-format.md
      start: 136
      end: 148
    - file: pcie-dllp-format.md
      start: 152
      end: 183
    - file: pcie-dllp-format.md
      start: 185
      end: 203
    - file: pcie-dllp-format.md
      start: 207
      end: 209
    - file: pcie-dllp-format.md
      start: 211
      end: 245
    - file: pcie-dllp-format.md
      start: 247
      end: 273
    - file: pcie-dllp-format.md
      start: 275
      end: 326
    - file: pcie-dllp-format.md
      start: 330
      end: 364
    - file: pcie-dllp-format.md
      start: 366
      end: 388
    - file: pcie-dllp-format.md
      start: 396
      end: 416
    - file: pcie-dllp-format.md
      start: 419
      end: 451
    - file: pcie-dllp-format.md
      start: 451
      end: 451
    - file: pcie-dllp-format.md
      start: 456
      end: 483
    - file: pcie-dllp-format.md
      start: 583
      end: 594
    - file: pcie-dllp-format.md
      start: 580
      end: 585
    - file: pcie-dllp-format.md
      start: 602
      end: 607
    - file: pcie-dllp-format.md
      start: 611
      end: 620
title: DLLP (Data Link Layer Packet)
description: 数据链路层专用控制包，用于链路管理、流控制和可靠性保证，固定8字节长度
tags:
  - pcie
  - data-link-layer
  - protocol
timestamp: "2026-08-16T06:36:35.893Z"
---

# DLLP（数据链路层数据包）

**DLLP（Data Link Layer Packet）** 是 PCIe 协议栈中数据链路层专用的控制数据包，用于链路管理、流控制和可靠性保证。与承载用户数据的 TLP（事务层数据包） 不同，DLLP 由数据链路层生成，专门负责链路层面的控制功能。^[pcie-dllp-format.md:3-12]

## 概述

DLLP 在 PCIe 协议栈中扮演着关键的辅助角色，其主要功能包括五个方面：确认机制（ACK/NAK）用于确认 TLP 的接收状态；流控制初始化（InitFC）用于在链路建立时交换缓冲区容量信息；流控制更新（UpdateFC）用于运行时实时更新可用信用；电源管理（PM）用于协商链路电源状态；厂商自定义（Vendor）用于厂商特定的链路控制需求。^[pcie-dllp-format.md:14-27]

在协议栈中的位置如下：DLLP 由数据链路层生成，与添加了序列号和 LCRC 的 TLP 并行传输至物理层。事务层生成 TLP，数据链路层为 TLP 添加序列号和 LCRC，同时生成 DLLP（ACK/NAK/FC），两者最终都经过物理层的编码和传输。^[pcie-dllp-format.md:29-40]

## 基本结构

所有 DLLP 都采用固定长度：**8 字节（64 位）**。其通用格式分为三个部分：Byte 0-1 为 DLLP 类型字段（2 字节）；Byte 2-5 为 DLLP 内容（类型特定，4 字节）；Byte 6-7 为 CRC-16 校验（2 字节）。^[pcie-dllp-format.md:48-60]

DLLP 与 TLP 在多个特性上存在显著差异。TLP 长度可变（12 字节至 4108 字节），由事务层生成，用于数据传输，包含序列号并需要 ACK 确认；而 DLLP 长度固定（8 字节），由数据链路层生成，用于链路控制，无序列号且不需要确认。^[pcie-dllp-format.md:62-71]

## DLLP 类型

### 类型编码

DLLP Type 字段占据第一个字节，定义了 DLLP 的类型和子类型。主要类型包括：Ack（0x00）用于确认 TLP 接收；Nak（0x10）用于请求重传 TLP；InitFC1 系列（0x50/0x60/0x70）用于流控制初始化；InitFC2 系列（0xC0/0xD0/0xE0）用于流控制初始化确认；UpdateFC 系列（0x80/0x90/0xA0）用于流控制更新；电源管理系列（0x20/0x21/0x24/0x30）用于电源状态协商；Vendor-Specific（0x40）用于厂商自定义。^[pcie-dllp-format.md:79-101]

## ACK/NAK 确认机制

### Ack DLLP

Ack DLLP（Type = 0x00）用于确认成功接收一个或多个 TLP。其格式中包含 AckNak Seq Number 字段（12 bits），表示已成功接收到序列号小于等于此值的所有 TLP，范围为 0-4095 的循环计数。^[pcie-dllp-format.md:104-134]

Ack DLLP 采用累积确认机制：发送方连续发送 Seq# 10, 11, 12, 13 时，接收方只需发送一个 Ack (Seq# = 13)，即可表示 10-13 全部成功接收。发送方收到 Ack 后，会清除重传缓冲区中 Seq# 小于等于该值的 TLP。^[pcie-dllp-format.md:136-148]

### Nak DLLP

Nak DLLP（Type = 0x10）用于请求重传从指定序列号开始的所有 TLP。其格式与 Ack DLLP 类似，但触发条件包括 LCRC 校验失败、TLP 序列号不连续（检测到丢包）或接收缓冲区溢出。^[pcie-dllp-format.md:152-183]

当发生错误时，例如接收方收到 20, 21, [22 LCRC 错误], 23，将发送 Nak (Seq# = 22)，发送方收到 Nak 后会重传 Seq# 大于等于 22 的所有 TLP。如果发送方在超时时间内未收到 Ack，也会自动重传所有未确认的 TLP。^[pcie-dllp-format.md:185-203]

## 流控制 DLLP

流控制 DLLP 用于管理接收缓冲区，防止溢出。这包括 InitFC1/InitFC2 用于链路初始化时交换缓冲区容量信息，以及 UpdateFC 用于运行时通知对方已释放的缓冲区空间。^[pcie-dllp-format.md:207-209]

### InitFC 初始化

InitFC1 在链路训练完成后由每个端口发送，InitFC2 在收到对方 InitFC1 后回复确认。InitFC DLLP 包含 HdrFC 字段（8 bits，表示可缓冲的 TLP 个数）和 DataFC 字段（12 bits，表示可缓冲的数据双字数量）。^[pcie-dllp-format.md:211-245]

InitFC 分为三种类型，分别对应 Posted 流量、Non-Posted 流量和 Completion 流量。初始化流程为：双方端口首先互相发送 InitFC1（包含各自缓冲区容量信息），然后发送 InitFC2 作为确认，确认完成后流控制初始化完成，可以开始发送 TLP。^[pcie-dllp-format.md:247-273]

### UpdateFC 运行时更新

UpdateFC 用于运行时通知对方已释放的缓冲区空间，发送时机为处理完 TLP 后释放缓冲区时。为减少 DLLP 数量，推荐采用批量更新策略，即积累释放一定数量后再发送。^[pcie-dllp-format.md:275-326]

## 电源管理 DLLP

电源管理 DLLP 用于协商链路电源状态。PM_Enter_L1（Type = 0x20）请求进入 L1 低功耗状态，当 Port A 检测到无 TLP 传输超过空闲时间后，发送 PM_Enter_L1 DLLP，Port B 收到后回复 PM_Request_Ack，两端进入 L1 状态（关闭 TX/RX 高速电路，保持参考时钟以便快速恢复）。^[pcie-dllp-format.md:330-364]

PM_Enter_L23（Type = 0x21）请求进入 L2/L3 深度睡眠状态，方向仅从下游设备到上游 RC/Switch。系统电源管理事件触发时，Root Complex 广播 PME_Turn_Off Message，设备停止发送 TLP 并发送 PM_Enter_L23 DLLP。^[pcie-dllp-format.md:366-388]

## 厂商自定义 DLLP

Vendor-Specific DLLP（Type = 0x40）用于厂商自定义的链路控制，可用于专有的调试和测试功能、厂商特定的性能优化或私有协议扩展。其格式中 Byte 2-5 为厂商定义内容。^[pcie-dllp-format.md:396-416]

## CRC-16 校验

DLLP 采用 CRC-16-IBM（多项式 x¹⁶ + x¹⁵ + x² + 1）进行校验，计算范围为 DLLP 的前 6 字节（Type + Content），初始值为 0xFFFF。如果 CRC 校验正确则正常处理 DLLP，如果 CRC 错误则丢弃该 DLLP。^[pcie-dllp-format.md:419-451]

需要特别注意的是，DLLP 不会被重传，这与 TLP 的可靠传输机制不同。^[pcie-dllp-format.md:451]

## DLLP 与 TLP 的关系

DLLP 和 TLP 在物理层混合传输，物理层通过帧头区分两者：TLP 以 STP（Start of TLP）开始，DLLP 以 SDP（Start of DLLP）开始。物理层可以插入 DLLP 而不影响 TLP 序列。^[pcie-dllp-format.md:456-483]

DLLP 不需要确认的原因在于其设计哲学：对于 Ack/Nak，发送方有超时重传机制；对于 UpdateFC，接收方会继续发送新的 UpdateFC；对于电源管理，电源状态变更有超时和重试机制。设计为不确认 DLLP 避免了递归确认问题（确认的确认）。^[pcie-dllp-format.md:583-594]

## 常见问题

**Q1: DLLP 丢失会怎样？**

Ack DLLP 丢失时，发送方超时后自动重传 TLP，无严重影响；UpdateFC DLLP 丢失时，发送方信用不更新，可能导致流控制阻塞，但不会丢数据；InitFC DLLP 丢失时，链路训练失败，需要重新训练。^[pcie-dllp-format.md:580-585]

**Q2: 流控制信用用完会怎样？**

事务层停止发送该类型的 TLP，等待 UpdateFC DLLP 补充信用。这不会导致丢包，只是增加延迟。^[pcie-dllp-format.md:602-607]

## 总结

DLLP 作为 PCIe 数据链路层的核心控制包，其关键特性可归纳为：固定 8 字节格式（Type 2B + Content 4B + CRC-16 2B）；五大类功能（Ack/Nak、InitFC、UpdateFC、PM、Vendor）；Ack/Nak 机制保证 TLP 可靠传输；流控制三步流程（InitFC1 → InitFC2 → UpdateFC）；电源管理协商低功耗状态；DLLP 丢失后依赖上层机制恢复而非自身重传。^[pcie-dllp-format.md:611-620]

---

## Sources

- [pcie-dllp-format.md](pcie-dllp-format.md) - DLLP 格式详解

---

## 相关链接

- TLP（事务层数据包） - 事务层数据包
- LCRC - 链路层循环冗余校验
- ACK/NAK 机制 - 可靠传输实现
- 流控制机制 - 信用管理
- LTSSM 状态机 - 链路训练
- 数据链路层 - PCIe 数据链路层概述

# Citations

1. [pcie-dllp-format.md:3-12](/references/pcie-dllp-format-55680021.md)
2. [pcie-dllp-format.md:14-27](/references/pcie-dllp-format-55680021.md)
3. [pcie-dllp-format.md:29-40](/references/pcie-dllp-format-55680021.md)
4. [pcie-dllp-format.md:48-60](/references/pcie-dllp-format-55680021.md)
5. [pcie-dllp-format.md:62-71](/references/pcie-dllp-format-55680021.md)
6. [pcie-dllp-format.md:79-101](/references/pcie-dllp-format-55680021.md)
7. [pcie-dllp-format.md:104-134](/references/pcie-dllp-format-55680021.md)
8. [pcie-dllp-format.md:136-148](/references/pcie-dllp-format-55680021.md)
9. [pcie-dllp-format.md:152-183](/references/pcie-dllp-format-55680021.md)
10. [pcie-dllp-format.md:185-203](/references/pcie-dllp-format-55680021.md)
11. [pcie-dllp-format.md:207-209](/references/pcie-dllp-format-55680021.md)
12. [pcie-dllp-format.md:211-245](/references/pcie-dllp-format-55680021.md)
13. [pcie-dllp-format.md:247-273](/references/pcie-dllp-format-55680021.md)
14. [pcie-dllp-format.md:275-326](/references/pcie-dllp-format-55680021.md)
15. [pcie-dllp-format.md:330-364](/references/pcie-dllp-format-55680021.md)
16. [pcie-dllp-format.md:366-388](/references/pcie-dllp-format-55680021.md)
17. [pcie-dllp-format.md:396-416](/references/pcie-dllp-format-55680021.md)
18. [pcie-dllp-format.md:419-451](/references/pcie-dllp-format-55680021.md)
19. [pcie-dllp-format.md:451-451](/references/pcie-dllp-format-55680021.md)
20. [pcie-dllp-format.md:456-483](/references/pcie-dllp-format-55680021.md)
21. [pcie-dllp-format.md:583-594](/references/pcie-dllp-format-55680021.md)
22. [pcie-dllp-format.md:580-585](/references/pcie-dllp-format-55680021.md)
23. [pcie-dllp-format.md:602-607](/references/pcie-dllp-format-55680021.md)
24. [pcie-dllp-format.md:611-620](/references/pcie-dllp-format-55680021.md)
