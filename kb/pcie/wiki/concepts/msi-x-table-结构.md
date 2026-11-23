---
title: MSI-X Table 结构
summary: 存储在 BAR 空间中的中断配置表，每个 Entry 16 字节，包含 Message Address (64-bit)、Message Data
  (32-bit) 和 Vector Control
sources:
- pcie-msix.md
kind: concept
createdAt: '2026-08-16T06:42:35.264Z'
updatedAt: '2026-08-16T06:42:35.264Z'
tags:
- pcie
- 中断
- 内存映射
aliases:
- msi-x-table-结构
- MT结
confidence: 0.95
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: MSI-X Table 是 MSI-X 中断机制的核心配置数据结构，存储在设备的 BAR 空间中。每个中断向量在表中对应一个独立的 Entry，支持独立配置地址、数据和掩码状态。^[pcie-msix.md:124-128]
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# MSI-X Table 结构

MSI-X Table 是 MSI-X 中断机制的核心配置数据结构，存储在设备的 BAR 空间中。每个中断向量在表中对应一个独立的 Entry，支持独立配置地址、数据和掩码状态。^[pcie-msix.md:124-128]

## Table Entry 格式

每个 Table Entry 占 **16 字节**，由 4 个 DWORD（32 位）组成：

```
┌──────────────────────────────────────────────────────────────┐
│                     MSI-X Table Entry (16 字节)              │
├─────────────────┬─────────────────┬─────────────────┬────────┤
│  Msg Addr Low   │  Msg Addr High  │   Msg Data      │ Vector │
│   (DWORD 0)     │   (DWORD 1)     │   (DWORD 2)     │ Ctrl   │
│    0x00-0x03    │    0x04-0x07    │    0x08-0x0B    │0x0C-0x0F│
└─────────────────┴─────────────────┴─────────────────┴────────┘
```

| 字段 | 偏移 | 大小 | 说明 |
|------|------|------|------|
| Message Address Lower | 0x00 | 32 bit | 中断目标地址低 32 位 |
| Message Address Upper | 0x04 | 32 bit | 中断目标地址高 32 位 |
| Message Data | 0x08 | 32 bit | 中断数据（低 16 位有效） |
| Vector Control | 0x0C | 32 bit | 中断掩码控制 |

^[pcie-msix.md:128-158]

## Message Address 格式

Message Address 指定中断消息的目标内存地址。x86/x64 架构使用固定前缀 `0xFEE00000`，格式如下：

```
Bit 31-20:  0xFEE (固定前缀，表示 APIC 地址空间)
Bit 19-12:  Destination ID (目标 CPU 的 APIC ID)
Bit 3:      Redirection Hint (重定向提示)
            - 0 = 定向到 Destination ID 指定的 CPU
            - 1 = 由中断控制器动态选择目标 CPU
Bit 2:      Destination Mode (目标模式)
            - 0 = Physical (物理 APIC ID)
            - 1 = Logical (逻辑模式)
Bit 1-0:    00 (固定，必须为 0)
```

常见配置示例：

| 地址 | 目标 CPU |
|------|----------|
| 0xFEE00000 | CPU 0 |
| 0xFEE01000 | CPU 1 |
| 0xFEE02000 | CPU 2 |

^[pcie-msix.md:182-205]

## Message Data 格式

Message Data 包含中断向量号和投递模式信息：

```
Bit 15:    Trigger Mode (触发模式)
            - 0 = Edge (边沿触发，推荐)
            - 1 = Level (电平触发)
Bit 14:    Reserved
Bit 10-8:  Delivery Mode (投递模式)
            - 000b = Fixed (定向中断)
            - 001b = Lowest Priority (最低优先级)
            - 010b = SMI (系统管理中断)
            - 100b = NMI (不可屏蔽中断)
            - 101b = INIT (初始化)
            - 111b = ExtINT (外部中断)
Bit 7-0:   Interrupt Vector (中断向量号，范围 0x20-0xFF)
```

配置示例：
- `0x0040` → Vector 0x40, Fixed 投递, Edge 触发
- `0x4123` → Vector 0x23, Fixed 投递, Edge 触发

^[pcie-msix.md:207-231]

## Vector Control

Vector Control 字段用于单独控制每个中断向量的启用/屏蔽状态：

```
Bit 31-1:  Reserved
Bit 0:     Mask Bit
            - 0 = Unmasked (启用此中断)
            - 1 = Masked (屏蔽此中断)
```

当 Mask Bit 置 1 时，设备触发该中断不会发送 MSI 消息，而是将对应位置于 [[PBA (Pending Bit Array)|PBA]] 中，等待后续处理。^[pcie-msix.md:150-158]

## 完整 Table 布局

Table 的基地址由 Capability 结构的 Table Offset/BIR 字段指定。每个 Entry 顺序排列，Entry N 的偏移量为 `N × 16`：

```
Table Base (如 BAR 0 + 0x2000):

Entry 0:  [0x00 - 0x0F]  ← 中断向量 0
  +0x00: Msg Addr Low
  +0x04: Msg Addr High
  +0x08: Msg Data
  +0x0C: Vector Control

Entry 1:  [0x10 - 0x1F]  ← 中断向量 1
  +0x10: Msg Addr Low
  +0x14: Msg Addr High
  +0x18: Msg Data
  +0x1C: Vector Control

Entry 2:  [0x20 - 0x2F]  ← 中断向量 2
  ...

Entry N:  [N×16 - N×16+15]
```

总 Table 大小 = 中断向量数量 × 16 字节 ^[pcie-msix.md:160-180]

## 读取 Table 内容

通过 PCI BAR 映射可以直接读取 Table 内容：

```bash
# 假设 BAR 0 映射到 0xf8000000，Table 在偏移 0x2000
devmem 0xf8002000 64   # Entry 0 的 Message Address
devmem 0xf8002008 32   # Entry 0 的 Message Data
devmem 0xf800200c 32   # Entry 0 的 Vector Control
```

Python 读取示例：

```python
with open('/sys/bus/pci/devices/0000:01:00.0/resource0', 'r+b') as f:
    mm = mmap.mmap(f.fileno(), 0)
    addr_low = struct.unpack('<I', mm[0x2000:0x2004])[0]
    addr_high = struct.unpack('<I', mm[0x2004:0x2008])[0]
    msg_data = struct.unpack('<I', mm[0x2008:0x200c])[0]
    vec_ctrl = struct.unpack('<I', mm[0x200c:0x2010])[0]
```

^[pcie-msix.md:537-566]

---

## Sources

- [MSI-X 详解](../../sources/pcie-msix.md) — 包含完整的 MSI-X Table 结构定义和配置示例

---

## 相关概念

- MSI-X 详解 — MSI-X 中断机制完整概述
- [[PBA (Pending Bit Array)]] — Pending Bit Array 用于记录屏蔽期间触发的中断
- MSI 中断 — 对比 MSI 与 MSI-X 的差异
- BAR 配置空间 — 了解 MSI-X Table 的存储位置如何通过 BAR 指定

