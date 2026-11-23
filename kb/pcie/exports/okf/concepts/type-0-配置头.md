---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 11e8d565da1d1f33e659695583cff0c3d78aec20a14885ab3a25918e882a4130
  pageDirectory: concepts
  sources:
    - pcie-config-space.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - type-0-配置头
    - T0配
  citations:
    - file: pcie-config-space.md
      start: 36
      end: 40
    - file: pcie-config-space.md
      start: 128
      end: 134
    - file: pcie-config-space.md
      start: 38
      end: 80
    - file: pcie-config-space.md
      start: 88
      end: 90
    - file: pcie-config-space.md
      start: 103
      end: 105
    - file: pcie-config-space.md
      start: 144
      end: 166
    - file: pcie-config-space.md
      start: 177
      end: 197
    - file: pcie-config-space.md
      start: 114
      end: 140
    - file: pcie-config-space.md
      start: 45
      end: 48
    - file: pcie-config-space.md
      start: 201
      end: 203
    - file: pcie-config-space.md
      start: 207
      end: 226
    - file: pcie-config-space.md
      start: 269
      end: 272
    - file: pcie-config-space.md
      start: 276
      end: 280
    - file: pcie-config-space.md
      start: 293
      end: 301
    - file: pcie-config-space.md
      start: 73
      end: 75
    - file: pcie-config-space.md
      start: 36
      end: 80
    - file: pcie-config-space.md
      start: 468
      end: 478
    - file: pcie-config-space.md
      start: 496
      end: 497
title: Type 0 配置头
description: PCIe端点设备的标准化配置空间头结构，包含Vendor ID、Device ID、Command/Status、BARs、能力指针等关键字段的布局定义
tags:
  - pcie
  - header
  - structure
timestamp: "2026-08-16T06:35:09.467Z"
---


# Type 0 配置头

## 概述

Type 0 配置头是 PCIe 配置空间中用于端点设备（Endpoint Device）的标准头部结构。它位于配置空间的前 64 字节区域（偏移 0x00-0x3F），定义了设备识别、地址映射、能力声明和控制状态等核心信息。^[pcie-config-space.md:36-40]

Type 0 Header 专用于非桥接设备，如 NVMe 控制器、网卡、显卡等。相比 Type 1 Header（用于 PCI-to-PCI Bridge），Type 0 不包含总线编号、子ordinate 总线范围等桥接相关字段，而是提供了更多的 BAR（Base Address Register）用于地址映射。^[pcie-config-space.md:128-134]

## 布局结构

Type 0 Header 的完整布局如下：

```
偏移    +0x0   +0x1   +0x2   +0x3   +0x4   +0x5   +0x6   +0x7
       ┌──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┐
0x00   │  Vendor ID (16)   │  Device ID (16)   │             │
       ├───────────────────┴───────────────────┤             │
0x04   │      Command (16)     │    Status (16) │             │
       ├──────┬──────┬─────────┴───────────────┤             │
0x08   │ Rev  │    Class Code (24 bits)        │  Header    │
       ├──────┼──────┬──────┬──────────────────┤   Type 0   │
0x0C   │Cache │Lat   │Header│  BIST            │             │
       ├──────┴──────┴──────┴──────────────────┤             │
0x10   │         BAR 0 (32/64 bit)             │             │
       ├───────────────────────────────────────┤             │
0x14   │         BAR 1 (32/64 bit)             │             │
       ├───────────────────────────────────────┤             │
0x18   │         BAR 2 (32/64 bit)             │             │
       ├───────────────────────────────────────┤             │
0x1C   │         BAR 3 (32/64 bit)             │             │
       ├───────────────────────────────────────┤             │
0x20   │         BAR 4 (32/64 bit)             │             │
       ├───────────────────────────────────────┤             │
0x24   │         BAR 5 (32/64 bit)             │             │
       ├───────────────────────────────────────┤             │
0x28   │      CardBus CIS Pointer              │             │
       ├───────────────────┬───────────────────┤             │
0x2C   │ Subsystem Vendor  │ Subsystem Device  │             │
       ├───────────────────┴───────────────────┤             │
0x30   │      Expansion ROM Base Address       │             │
       ├──────┬────────────────────────────────┤             │
0x34   │ Cap  │        Reserved                │             │
       │ Ptr  │                                │             │
       ├──────┴────────────────────────────────┤             │
0x38   │            Reserved                   │             │
       ├──────┬──────┬──────┬──────────────────┤             │
0x3C   │ Int  │ Int  │Min   │  Max Lat         │             │
       │ Line │ Pin  │Grant │                  │             │
       └──────┴──────┴──────┴──────────────────┘             │
```

^[pcie-config-space.md:38-80]

## 关键字段详解

### 设备识别字段（0x00-0x0F）

| 偏移 | 字段 | 位宽 | 说明 |
|------|------|------|------|
| 0x00 | Vendor ID | 16 bits | 设备制造商标识，由 PCI-SIG 分配^[pcie-config-space.md:88-90] |
| 0x02 | Device ID | 16 bits | 特定设备型号，由厂商分配^[pcie-config-space.md:103-105] |
| 0x04 | Command | 16 bits | 控制设备基本操作（如内存访问、DMA、中断）^[pcie-config-space.md:144-166] |
| 0x06 | Status | 16 bits | 报告设备状态和能力^[pcie-config-space.md:177-197] |
| 0x09 | Class Code | 24 bits | 设备类型标准分类（Base+Sub+Prog IF）^[pcie-config-space.md:114-140] |

**Header Type 字段**（偏移 0x0E）标识配置头类型：
- `0x00` = Type 0（端点设备）
- `0x01` = Type 1（PCI-to-PCI Bridge）
- Bit 7 = 1 表示多功能设备

^[pcie-config-space.md:45-48]

### Base Address Registers（0x10-0x27）

BARs 定义设备的内存或 I/O 地址空间映射，是 Type 0 Header 中最核心的字段之一。^[pcie-config-space.md:201-203]

**内存 BAR 格式**（Bit 0 = 0）：
```
Bit 0:    0 = Memory Space
Bit 2-1:  Type (00=32-bit, 10=64-bit)
Bit 3:    Prefetchable (可预取)
Bit 31-4: Base Address (16-byte 对齐)
```

**I/O BAR 格式**（Bit 0 = 1）：
```
Bit 0:    1 = I/O Space
Bit 31-2: Base Address (4-byte 对齐)
```

^[pcie-config-space.md:207-226]

**实际应用示例**：
- **BAR0**：通常用于设备寄存器（如 NVMe Controller Registers）
- **BAR1**：MSI-X 表格和 PBA（如果启用 MSI-X）
- **BAR2-5**：额外的内存区域或设备特定功能

^[pcie-config-space.md:269-272]

### Capabilities Pointer（0x34）

指向第一个能力结构的偏移（必须 DWORD 对齐）。如果 Status 寄存器的 Bit 4 为 1，表示存在能力链表。^[pcie-config-space.md:276-280]

**常见能力 ID**：

| ID | 能力名称 | 用途 |
|----|---------|------|
| 0x01 | Power Management | 电源管理 (D0-D3) |
| 0x05 | MSI | 消息信号中断 |
| 0x10 | PCIe Capability | PCIe 专用能力 |
| 0x11 | MSI-X | 扩展消息中断 |

^[pcie-config-space.md:293-301]

### 中断相关字段（0x3C-0x3F）

| 偏移 | 字段 | 说明 |
|------|------|------|
| 0x3C | Interrupt Line | 报告中断连接（操作系统使用） |
| 0x3D | Interrupt Pin | 报告使用的中断引脚（INTx A/B/C/D） |
| 0x3E | Min Grant | 设备期望的最小总线占用时间 |
| 0x3F | Max Latency | 设备期望的最大延迟 |

^[pcie-config-space.md:73-75]

## 与 Type 1 Header 的区别

| 字段 | Type 0 | Type 1 |
|------|--------|--------|
| BARs 数量 | 6 个（0x10-0x27） | 2 个（0x10-0x17） |
| Cardbus CIS Pointer | 有（0x28） | 无 |
| 扩展 ROM Base Address | 有（0x30） | 无 |
| 总线编号字段 | 无 | 有（Primary/Secondary/Subordinate） |
| I/O 限制寄存器 | 无 | 有 |
| 内存限制寄存器 | 无 | 有 |

^[pcie-config-space.md:36-80]

## 调试与验证

使用 `lspci` 可以查看 Type 0 Header 的详细信息：

```bash
# 查看完整配置空间
lspci -xxx -s 01:00.0        # 前 256 字节（Type 0 Header 在此范围）
lspci -xxxx -s 01:00.0       # 完整 4096 字节

# 解析设备信息
lspci -vvv -s 01:00.0
```

^[pcie-config-space.md:468-478]

通过 `/sys/bus/pci/devices/` 也可以直接读取配置空间：

```bash
# 十六进制转储
hexdump -C /sys/bus/pci/devices/0000:01:00.0/config
```

^[pcie-config-space.md:496-497]

---

## 相关页面

- 配置空间布局详解
- [PCIe 配置空间](/concepts/pcie-配置空间.md)
- Base Address Register
- 能力结构详解
- [ECAM 机制](/concepts/ecam-机制.md)
- 设备枚举过程

---

## Sources

- [pcie-config-space.md:36-80](pcie-config-space.md:36-80) — Type 0 Header 布局结构图
- [pcie-config-space.md:88-105](pcie-config-space.md:88-105) — Vendor ID、Device ID 字段说明
- [pcie-config-space.md:114-140](pcie-config-space.md:114-140) — Class Code 字段说明
- [pcie-config-space.md:144-166](pcie-config-space.md:144-166) — Command Register 说明
- [pcie-config-space.md:177-197](pcie-config-space.md:177-197) — Status Register 说明
- [pcie-config-space.md:201-272](pcie-config-space.md:201-272) — BARs 详解
- [pcie-config-space.md:276-314](pcie-config-space.md:276-314) — Capabilities Pointer 说明
- [pcie-config-space.md:468-497](pcie-config-space.md:468-497) — 调试方法

# Citations

1. [pcie-config-space.md:36-40](/references/pcie-config-space-e97358dd.md)
2. [pcie-config-space.md:128-134](/references/pcie-config-space-e97358dd.md)
3. [pcie-config-space.md:38-80](/references/pcie-config-space-e97358dd.md)
4. [pcie-config-space.md:88-90](/references/pcie-config-space-e97358dd.md)
5. [pcie-config-space.md:103-105](/references/pcie-config-space-e97358dd.md)
6. [pcie-config-space.md:144-166](/references/pcie-config-space-e97358dd.md)
7. [pcie-config-space.md:177-197](/references/pcie-config-space-e97358dd.md)
8. [pcie-config-space.md:114-140](/references/pcie-config-space-e97358dd.md)
9. [pcie-config-space.md:45-48](/references/pcie-config-space-e97358dd.md)
10. [pcie-config-space.md:201-203](/references/pcie-config-space-e97358dd.md)
11. [pcie-config-space.md:207-226](/references/pcie-config-space-e97358dd.md)
12. [pcie-config-space.md:269-272](/references/pcie-config-space-e97358dd.md)
13. [pcie-config-space.md:276-280](/references/pcie-config-space-e97358dd.md)
14. [pcie-config-space.md:293-301](/references/pcie-config-space-e97358dd.md)
15. [pcie-config-space.md:73-75](/references/pcie-config-space-e97358dd.md)
16. [pcie-config-space.md:36-80](/references/pcie-config-space-e97358dd.md)
17. [pcie-config-space.md:468-478](/references/pcie-config-space-e97358dd.md)
18. [pcie-config-space.md:496-497](/references/pcie-config-space-e97358dd.md)
