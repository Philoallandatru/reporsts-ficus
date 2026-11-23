---
title: ACK/NAK 协议
summary: 数据链路层的可靠传输协议，通过序列号、确认/否定应答和重试缓冲区确保TLP正确到达目的地
sources:
- pcie-layering.md
kind: concept
createdAt: '2026-08-16T06:39:52.954Z'
updatedAt: '2026-08-16T06:39:52.954Z'
tags:
- pcie
- data-link-layer
- reliable-transmission
aliases:
- acknak-协议
confidence: 0.95
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: ACK/NAK 协议是 PCIe 数据链路层 的核心可靠传输机制，负责确保事务层数据包（TLP）能够正确无误地从发送端到达接收端。^[pcie-layering.md:212-214]
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# ACK/NAK 协议

## 概述

ACK/NAK 协议是 PCIe 数据链路层 的核心可靠传输机制，负责确保事务层数据包（TLP）能够正确无误地从发送端到达接收端。^[pcie-layering.md:212-214]

当发送方通过链路发送 TLP 时，接收方会对每个 TLP 进行完整性校验。如果校验通过，接收方返回 **Ack DLLP**（确认）应答；如果校验失败，则返回 **Nak DLLP**（否认）请求发送方重传。^[pcie-layering.md:220-224]

该协议位于 PCIe 协议栈的数据链路层，处于事务层和物理层之间，向上层屏蔽了链路传输的错误处理细节。^[pcie-layering.md:22-27]

---

## 工作流程

ACK/NAK 协议的交互过程如下：

```
发送方                                      接收方
  │                                            │
  ├──> TLP #100 (Seq=100, Data, LCRC) ───────>│
  │                                            ├─> 检查 LCRC
  │                                            ├─> LCRC OK
  │    <────────── Ack DLLP (Seq=100) ────────┤
  │                                            │
  ├─> TLP 从 Retry Buffer 中删除              │
  │                                            │
  ├──> TLP #101 (Seq=101, Data, LCRC) ───────>│
  │                                            ├─> 检查 LCRC
  │                                            ├─> LCRC Error!
  │    <────────── Nak DLLP (Seq=101) ────────┤
  │                                            │
  ├─> 从 Retry Buffer 重传 TLP #101           │
  ├──> TLP #101 (重传) ──────────────────────>│
  │                                            ├─> LCRC OK
  │    <────────── Ack DLLP (Seq=101) ────────┤
```

具体步骤说明：

1. **发送 TLP**：发送方为每个 TLP 添加序列号（Sequence Number）和 LCRC 校验码后发送，同时将 TLP 副本存入 Retry Buffer。^[pcie-layering.md:235-241]
2. **校验与确认**：接收方对收到的 TLP 进行 LCRC 校验，若校验成功则返回 Ack DLLP，校验失败则返回 Nak DLLP。^[pcie-layering.md:244-246]
3. **确认清除**：发送方收到 Ack 后，从 Retry Buffer 中删除对应的 TLP 副本。^[pcie-layering.md:241]
4. **错误重传**：发送方收到 Nak 后，从 Retry Buffer 中取出对应 TLP 进行重传，直到收到确认。^[pcie-layering.md:248-251]

---

## 关键特性

### 序列号（Sequence Number）

ACK/NAK 协议使用 **12 位序列号**，编号范围为 0-4095，采用循环使用的方式。^[pcie-layering.md:256] 每个 TLP 在发送时都会被分配一个唯一的序列号，接收方通过序列号识别 TLP 的顺序和完整性。

### 重传缓冲区（Retry Buffer）

发送方维护 **Retry Buffer**，用于存储所有已发送但尚未收到确认的 TLP。^[pcie-layering.md:258] 只要 TLP 未被确认，它就会一直保留在缓冲区中，以便需要时进行重传。

### 超时重传机制

除了接收 Nak 后主动重传外，发送方还维护一个 **Replay Timer（重放计时器）**。如果在超时时间内未收到对应 TLP 的 ACK，计时器会触发自动重传，确保在 ACK 意外丢失的情况下也能恢复通信。^[pcie-layering.md:257]

---

## LCRC 校验

LCRC（Link CRC）是 ACK/NAK 协议进行错误检测的基础。它是一个 **32 位 CRC-32 校验和**，覆盖整个 TLP 的头部和数据载荷。^[pcie-layering.md:262]

LCRC 由数据链路层自动添加和验证，软件不可见，由硬件自动处理。^[pcie-layering.md:266-267] LCRC 校验在每一跳（逐跳）进行，用于检测链路传输过程中的位错误。^[pcie-layering.md:274-275]

与事务层的 端到端 CRC（ECRC） 不同，LCRC 仅保护当前链路段，而 ECRC 覆盖从源设备到目标设备的整个路径。^[pcie-layering.md:273-276]

---

## 相关概念

- PCIe 三层协议模型 — 了解 ACK/NAK 协议所在的协议层次
- TLP（事务层数据包） — ACK/NAK 协议保护传输的数据包
- DLLP（数据链路层数据包） — 包含 Ack 和 Nak 两种协议报文
- LCRC — 用于检测链路传输错误的校验机制
- Retry Buffer — 存储待确认 TLP 的缓冲区

---

## 参考资料

- **PCIe Base Specification** — Chapter 3 (Data Link Layer)
- **PCIe 分层架构** — FEMU `/hw/pci/pcie_aer.c` 中的错误注入实现

---

## Sources

^[pcie-layering.md:205-258]

