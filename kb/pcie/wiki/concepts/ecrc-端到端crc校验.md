---
title: ECRC (端到端CRC校验)
summary: TLP的可选端到端CRC校验字段，用于数据完整性保护，由TD位指示是否存在
sources:
- pcie-tlp-format.md
kind: concept
createdAt: '2026-08-16T06:49:12.844Z'
updatedAt: '2026-08-16T06:49:12.844Z'
tags:
- pcie
- integrity
- error-detection
aliases:
- ecrc-端到端crc校验
confidence: 0.9
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: 在 PCIe 协议栈中，TLP（Transaction Layer Packet）的完整结构包含三个部分：
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# ECRC (端到端 CRC 校验)

**ECRC**（End-to-End CRC，端到端循环冗余校验）是 PCIe 协议中用于保证事务层数据完整性的可选校验机制。它由事务层生成并在整条数据传输路径中保持不变，提供从发送端到接收端的端到端数据保护。^[pcie-tlp-format.md:12, pcie-tlp-format.md:48-50]

## 概述

在 PCIe 协议栈中，TLP（Transaction Layer Packet）的完整结构包含三个部分：

- **Header**（头部）：3 或 4 个双字（DW），携带控制信息和路由信息
- **Data Payload**（数据负载）：0 到 1024 个双字，最大 4096 字节
- **ECRC**：1 个双字（4 字节），可选的端到端 CRC 校验字段 ^[pcie-tlp-format.md:40-53]

ECRC 的核心作用是在事务层验证数据的完整性。与链路层 CRC（LCRC）不同，LCRC 只能在相邻节点之间提供保护，而 ECRC 从源设备的事务层一直保持到目标设备的事务层，覆盖整个端到端路径。^[pcie-tlp-format.md:12,25]

## 结构与位置

ECRC 固定为 1 个双字（4 字节），位于 TLP 的最末尾。其在 TLP 中的位置如下：

```
┌────────────────────────────────────────────────────┐
│           TLP Header (3 or 4 DW)                   │
│  Byte 0-11 (3 DW) or 0-15 (4 DW)                   │
├────────────────────────────────────────────────────┤
│           Data Payload (0-1024 DW)                 │  可选
│  最大 4096 字节                                     │
├────────────────────────────────────────────────────┤
│           ECRC (1 DW = 4 bytes)                    │  可选
│  端到端 CRC 校验                                    │
└────────────────────────────────────────────────────┘
```

## TD 位与 ECRC 使能

TLP Header 中的 **TD 位**（TLP Digest）是决定是否携带 ECRC 的关键字段：

| TD 值 | 含义 |
|-------|------|
| **0** | 无 ECRC 字段 |
| **1** | TLP 末尾包含 ECRC |

接收方通过检查 TD 位即可判断该 TLP 是否包含 ECRC，并进行相应的校验处理。^[pcie-tlp-format.md:219-223]

## 处理流程

### 发送方处理

在 TLP 发送过程中，事务层的处理步骤如下：

1. 构建 TLP Header，填充地址、ID、长度等字段
2. 添加 Data Payload（如有）
3. **计算并添加 ECRC**（如果 ECRC 功能已启用）
4. 传递给数据链路层（该层会添加 LCRC 和序列号）^[pcie-tlp-format.md:505-516]

### 接收方处理

接收方对包含 ECRC 的 TLP 处理流程为：

1. 从数据链路层接收 TLP
2. **验证 ECRC**（如果存在）
   - 若校验失败：标记为 Poisoned 或丢弃该 TLP
   - 若校验通过：继续正常处理
3. 解析 Header 并进行路由判断
4. 处理事务并更新流控制信用 ^[pcie-tlp-format.md:521-543]

## 错误处理

当 ECRC 校验失败时，接收方有多种处理策略：

- **标记为 Poisoned**：将 TLP 的 EP（Error/Poisoned）位置位后继续转发
- **直接丢弃**：丢弃校验失败的 TLP，不向上游传递错误数据

这种设计允许系统根据需求选择容错策略，在数据可靠性和传输连续性之间取得平衡。^[pcie-tlp-format.md:214-217, pcie-tlp-format.md:523-525]

## 与 LCRC 的区别

| 特性 | ECRC | LCRC |
|------|------|------|
| **作用位置** | 事务层 | 数据链路层 |
| **覆盖范围** | 端到端（源到目标） | 链路级（相邻节点） |
| **校验内容** | Header + Data Payload | 整个 TLP + Seq# |
| **生成位置** | 事务层 | 数据链路层 |
| **用途** | 事务完整性验证 | 链路传输保护 |

两者相互配合，LCRC 保护相邻节点间的每次转发，ECRC 保护端到端的整体数据完整性。^[pcie-tlp-format.md:12,25]

## 配置与使能

ECRC 功能通常通过 PCIe 设备的配置空间进行使能控制。设备需要支持 AER（高级错误报告）能力才能配置 ECRC 校验功能。^[pcie-tlp-format.md:565-571]

---

## 相关概念

TLP 格式详解 — 了解 ECRC 在 TLP 中的具体位置和格式

数据链路层 — 了解 LCRC 与 ECRC 的配合机制

流控制机制 — 了解 TLP 传输的整体流程

事务类型详解 — 了解各种 TLP 类型如何配合 ECRC 使用

---

## 参考资料

- PCIe Base Specification Chapter 2 (Transaction Layer)
- Figure 2-3 to 2-10 (TLP Format diagrams)
- Table 2-3 (Fmt/Type encoding)

