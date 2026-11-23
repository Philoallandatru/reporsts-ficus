---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 51dae59c9afc6eb94cbe0999e1d05194fb184facc13940c6fd6f933fb75ff70c
  pageDirectory: concepts
  sources:
    - pcie-msix.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - msi-x-capability-结构
    - MC结
  citations:
    - file: pcie-msix.md
      start: 67
      end: 69
    - file: pcie-msix.md
      start: 70
      end: 73
    - file: pcie-msix.md
      start: 75
      end: 89
    - file: pcie-msix.md
      start: 91
      end: 98
    - file: pcie-msix.md
      start: 100
      end: 106
    - file: pcie-msix.md
      start: 67
      end: 106
    - file: pcie-msix.md
      start: 108
      end: 120
    - file: pcie-msix.md
      start: 9
      end: 14
title: MSI-X Capability 结构
description: 位于 PCIe 配置空间的能力结构，包含控制寄存器、Table 位置信息和 PBA 位置信息，Cap ID 为 0x11
tags:
  - pcie
  - 配置空间
  - capability
timestamp: "2026-08-16T06:42:10.658Z"
---

# MSI-X Capability 结构

## 概述

MSI-X Capability 结构位于 PCIe 设备的配置空间中，用于声明和配置 MSI-X 中断能力。该结构包含 **4 个双字（16 字节）**，定义了 MSI-X 中断的核心配置参数，包括中断数量、表位置和待处理位数组位置。^[pcie-msix.md:67-69]

## Capability Header

### Capability ID 与 Next Pointer

偏移地址 `0x00` 处存储标准 PCI Capability Header：

```
Offset 0x00: Capability ID (0x11) + Next Pointer
┌─────────────────┬──────────────────────────┐
│   Next (8 bit)  │  Cap ID = 0x11 (8 bit)   │
└─────────────────┴──────────────────────────┘
```

MSI-X 的 Capability ID 固定为 **0x11**，用于标识此 Capability 类型。Next Pointer 指向配置空间中下一个 Capability 的位置（若为 `0x00` 则表示这是最后一个 Capability）。^[pcie-msix.md:70-73]

### Message Control 寄存器

偏移地址 `0x02` 处是 **16 位的 Message Control 寄存器**，包含以下字段：

```
Offset 0x02: Message Control (16-bit)
15              11   10       0
┌─────────────────┬───┬────────────────┐
│   Reserved      │ FM│ Table Size - 1 │
│                 │   │   (N-1)        │
└─────────────────┴───┴────────────────┘
```

**字段说明**：

| 位字段 | 名称 | 说明 |
|--------|------|------|
| Bit 10-0 | Table Size - 1 | 实际大小为此值 + 1，范围 0-2047（表示 1-2048 个中断向量） |
| Bit 14 | Function Mask (FM) | 1 = 屏蔽所有 MSI-X 中断；0 = 根据各 Entry 的 Vector Control 决定 |
| Bit 15 | MSI-X Enable | 1 = 启用 MSI-X；0 = 禁用 MSI-X（使用传统中断） |

^[pcie-msix.md:75-89]

## Table Offset 与 BIR

偏移地址 `0x04` 处定义了 **MSI-X Table 的位置**：

```
Offset 0x04: Table Offset/BIR (32-bit)
31                           3   2    0
┌──────────────────────────────┬───────┐
│   Table Offset [31:3]        │  BIR  │
│   (8-byte 对齐)              │       │
└──────────────────────────────┴───────┘
```

- **BIR (BAR Indicator Register)**：使用 3 位指示 Table 位于哪个 BAR（0-5）
- **Table Offset**：在该 BAR 内的偏移地址，要求 **8 字节对齐**

^[pcie-msix.md:91-98]

## PBA Offset 与 BIR

偏移地址 `0x08` 处定义了 **PBA (Pending Bit Array) 的位置**：

```
Offset 0x08: PBA Offset/BIR (32-bit)
31                           3   2    0
┌──────────────────────────────┬───────┐
│   PBA Offset [31:3]          │  BIR  │
│   (8-byte 对齐)              │       │
└──────────────────────────────┴───────┘
```

PBA Offset 与 BIR 的格式与 Table Offset/BIR 完全相同，同样要求 8 字节对齐。^[pcie-msix.md:100-106]

## 完整结构布局

MSI-X Capability 结构的完整布局如下：

| 偏移 | 大小 | 名称 | 说明 |
|------|------|------|------|
| 0x00 | 1 DW | Capability Header | ID=0x11, Next Pointer |
| 0x02 | 1 DW | Message Control | 表大小、全局掩码、启用位 |
| 0x04 | 1 DW | Table Offset/BIR | Table 所在 BAR 及偏移 |
| 0x08 | 1 DW | PBA Offset/BIR | PBA 所在 BAR 及偏移 |

^[pcie-msix.md:67-106]

## 实际读取示例

使用 `lspci` 查看 NVMe 设备的 MSI-X Capability 配置：

```bash
lspci -vvv -s 01:00.0 | grep -A5 MSI-X
  Capabilities: [70] MSI-X: Enable+ Count=33 Masked-
    Vector table: BAR=0 offset=00002000
    PBA: BAR=0 offset=00003000
```

**解读**：
- `Enable+`：MSI-X 已启用
- `Count=33`：33 个中断向量（Table Size = 32，即 Message Control 的表大小字段为 32）
- `Vector table`：位于 BAR 0，偏移 `0x2000`
- `PBA`：位于 BAR 0，偏移 `0x3000`

^[pcie-msix.md:108-120]

## 与 MSI 的区别

相比传统的 MSI Capability 结构，MSI-X 提供了以下改进：

| 特性 | MSI | MSI-X |
|------|-----|-------|
| 最大中断数量 | 32 | 2048 |
| 表位置 | 配置空间（固定） | BAR 空间（灵活） |
| 地址/数据配置 | 共享 | 每个向量独立 |
| 中断屏蔽 | 全局掩码 | 独立掩码（每个向量） |
| 向量分配 | 连续 | 可非连续分配 |

MSI-X 的表和 PBA 存放在 BAR 空间而非配置空间内，这种设计释放了宝贵的配置空间资源，同时允许使用更大的表和更灵活的配置。^[pcie-msix.md:9-14]

## 相关概念

- [MSI-X Table 结构](/concepts/msi-x-table-结构.md) — MSI-X 中断向量表的详细格式
- [PBA (Pending Bit Array)](/concepts/pba-pending-bit-array.md) — 待处理位数组的机制和用途
- BARs 详解 — PCIe 基址寄存器的配置和使用
- MSI Capability 结构 — 传统 MSI 中断机制的配置结构

---

## Sources

- [pcie-msix.md:63-120](pcie-msix.md:63-120) — MSI-X Capability 结构详解

# Citations

1. [pcie-msix.md:67-69](/references/pcie-msix-66ea67aa.md)
2. [pcie-msix.md:70-73](/references/pcie-msix-66ea67aa.md)
3. [pcie-msix.md:75-89](/references/pcie-msix-66ea67aa.md)
4. [pcie-msix.md:91-98](/references/pcie-msix-66ea67aa.md)
5. [pcie-msix.md:100-106](/references/pcie-msix-66ea67aa.md)
6. [pcie-msix.md:67-106](/references/pcie-msix-66ea67aa.md)
7. [pcie-msix.md:108-120](/references/pcie-msix-66ea67aa.md)
8. [pcie-msix.md:9-14](/references/pcie-msix-66ea67aa.md)
