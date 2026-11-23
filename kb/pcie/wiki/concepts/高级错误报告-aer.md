---
title: 高级错误报告 AER
summary: 提供不可纠正和可纠正错误的详细检测、日志记录和报告机制，包括 DLP、POISON_TLP、ECRC 等错误类型
sources:
- pcie-implementation-analysis.md
kind: concept
createdAt: '2026-08-16T06:38:31.678Z'
updatedAt: '2026-08-16T06:38:31.678Z'
tags:
- 硬件协议
- 错误处理
- 可靠性
aliases:
- 高级错误报告-aer
confidence: 0.9
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: AER 是 PCIe 能力结构的重要组成部分，允许设备检测、记录并向系统软件报告各类错误。与传统的 PCI 错误报告机制相比，AER 提供了更细粒度的错误分类和更详细的错误状态信息。^[pcie-implementation-analysis.md:180-182]
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 高级错误报告 (AER)

**高级错误报告**（Advanced Error Reporting，简称 AER）是 PCI Express 规范中定义的一套详细的错误检测和报告机制，旨在提供更丰富的错误信息以支持系统可靠性和调试能力。^[pcie-implementation-analysis.md:180-182]

## 概述

AER 是 PCIe 能力结构的重要组成部分，允许设备检测、记录并向系统软件报告各类错误。与传统的 PCI 错误报告机制相比，AER 提供了更细粒度的错误分类和更详细的错误状态信息。^[pcie-implementation-analysis.md:180-182]

### 在 FEMU 中的实现

FEMU 提供了完整的 AER 实现，核心代码位于 `/hw/pci/pcie_aer.c`。该实现包括错误注入、日志记录和 TLP 前缀日志等高级调试功能。^[pcie-implementation-analysis.md:200-203]

主要函数包括：
- `pcie_aer_inject_error()`：用于注入和测试错误场景
- TLP 前缀日志功能：支持高级调试和错误追踪

## 错误分类

AER 将错误分为两大类别：**不可纠正错误**和**可纠正错误**。^[pcie-implementation-analysis.md:184-198]

### 不可纠正错误 (Uncorrectable Errors)

不可纠正错误通常表示严重的硬件或协议问题，系统无法自动恢复，需要软件介入处理。^[pcie-implementation-analysis.md:186-192]

| 错误代码 | 全称 | 说明 |
|---------|------|------|
| `DLP` | Data Link Protocol Error | 数据链路层协议错误 |
| `POISON_TLP` | Poisoned TLP | TLP 被标记为"有毒"，表示数据损坏 |
| `FCP` | Flow Control Protocol Error | 流控制协议错误 |
| `MALF_TLP` | Malformed TLP | 格式错误的 TLP 包 |
| `ECRC` | End-to-End CRC Error | 端到端 CRC 校验错误 |
| `UNSUP` | Unsupported Request | 不支持的请求 |

### 可纠正错误 (Correctable Errors)

可纠正错误是可以在硬件层面自动恢复的错误，通常不会导致数据丢失或系统故障。^[pcie-implementation-analysis.md:194-198]

| 错误代码 | 全称 | 说明 |
|---------|------|------|
| `BAD_TLP` | Bad TLP | 检测到 TLP 错误，通过重传恢复 |
| `BAD_DLLP` | Bad DLLP | 数据链路层包错误，通过重传恢复 |
| `REPLAY_NUM_ROLLOVER` | Replay Number Rollover | 重传计数器溢出 |
| `REPLAY_TIMER_TIMEOUT` | Replay Timer Timeout | 重传超时 |

## 错误报告流程

AER 定义了标准的错误处理流程，确保错误能够被正确检测、记录并上报给系统软件。^[pcie-implementation-analysis.md:205-208]

```
错误检测 → 错误日志记录 → 错误消息生成 → 上报至 Root Complex
```

1. **错误检测**：硬件在事务层或数据链路层检测到错误条件
2. **错误日志记录**：将错误信息记录到设备的 AER 相关寄存器中
3. **错误消息生成**：构造错误消息（Error Message）TLP
4. **上报至 Root Complex**：通过 PCIe 消息机制将错误通知给系统

## AER 与 TLP 前缀

AER 机制与 事务层包 (TLP) 前缀紧密相关。TLP 前缀可用于携带额外的错误相关信息，FEMU 的 AER 实现支持 TLP 前缀日志功能，便于深入调试错误场景。^[pcie-implementation-analysis.md:142-143]

### FEMU 中的错误类型定义

在 FEMU 代码中，AER 实现了以下 TLP 相关错误类型：

- `POISON_TLP`：被标记为有毒的 TLP，表示有效载荷数据已损坏
- `MALF_TLP`：格式畸形的 TLP，硬件无法正确解析

## 相关概念

- PCI Express 配置空间：AER 能力结构存储于配置空间中
- 事务层包 (TLP)：错误报告的基本单元
- 数据链路层包 (DLLP)：链路层的错误检测
- 端到端 CRC (ECRC)：TLP 的端到端完整性校验
- 链路 CRC (LCRC)：链路层的数据完整性校验
- 根复合体 (Root Complex)：接收和转发错误消息的目的地
- 高级错误报告：本词条

## 代码映射

FEMU 代码与 PCIe 规范的对应关系如下：

| 规范概念 | FEMU 实现 |
|---------|----------|
| AER 错误代码 | `PCI_ERR_UNC_*` / `PCI_ERR_COR_*` 常量 |
| 不可纠正错误状态寄存器 | AER 实现相关寄存器 |
| 可纠正错误状态寄存器 | AER 实现相关寄存器 |

## 总结

高级错误报告（AER）是 PCIe 架构中确保系统可靠性的关键机制。通过将错误细分为不可纠正和可纠正两大类，AER 使系统软件能够根据错误类型采取适当的恢复措施。FEMU 的完整 AER 实现展示了这一机制在实际硬件模拟中的应用。^[pcie-implementation-analysis.md:180-209]

---

## Sources

- [PCI Express 深度分析报告 (基于 FEMU 代码库)](../../sources/pcie-implementation-analysis.md)

