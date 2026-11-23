---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 49ea38aa1e85878debf1a6d76594e478bbf603df3b4bbe793731db0a85e83811
  pageDirectory: concepts
  sources:
    - pcie-msix.md
  confidence: 0.9
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - msi-x-message-address-格式
    - MMA格
  citations:
    - file: pcie-msix.md
      start: 133
      end: 143
    - file: pcie-msix.md
      start: 405
      end: 411
    - file: pcie-msix.md
      start: 185
      end: 205
    - file: pcie-msix.md
      start: 414
      end: 415
    - file: pcie-msix.md
      start: 194
      end: 194
    - file: pcie-msix.md
      start: 195
      end: 196
    - file: pcie-msix.md
      start: 198
      end: 199
    - file: pcie-msix.md
      start: 201
      end: 205
    - file: pcie-msix.md
      start: 128
      end: 158
    - file: pcie-msix.md
      start: 406
      end: 417
    - file: pcie-msix.md
      start: 137
      end: 138
    - file: pcie-msix.md
      start: 338
      end: 342
title: MSI-X Message Address 格式
description: x86/x64 架构 MSI 地址格式，固定前缀 0xFEE00000，包含目标 CPU APIC ID (Bits 19-12) 和重定向提示位
tags:
  - pcie
  - 中断
  - 地址格式
timestamp: "2026-08-16T06:42:44.326Z"
---


# MSI-X Message Address 格式

## 概述

在 MSI-X 中断机制中，**Message Address**（消息地址）是用于将中断请求定向到目标 CPU 的 64 位地址。每个 MSI-X Table Entry 包含两个字段来存储这个消息地址 ^[pcie-msix.md:133-143]：

- **Message Address Lower (Offset 0x00)**：低 32 位
- **Message Address Upper (Offset 0x04)**：高 32 位

这两个字段组合成一个完整的 64 位地址，设备通过向该地址写入 Memory Write TLP 来触发中断 ^[pcie-msix.md:405-411]。

## x86/x64 架构的地址格式

在 x86/x64 架构下，MSI-X Message Address 具有特定的结构 ^[pcie-msix.md:185-205]：

```
┌────────┬──────┬────┬──────┬────────┬──┐
│ 0xFEE  │ Dest │ RH │ DM   │ Rsvd   │00│
│        │ (8)  │(1) │ (1)  │        │  │
└────────┴──────┴────┴──────┴────────┴──┘
```

### 各字段说明

| 位域 | 名称 | 说明 |
|------|------|------|
| Bit 31-20 | 固定前缀 | 固定值 `0xFEE`，标识 MSI 地址空间 |
| Bit 19-12 | Destination ID | 目标 CPU 的 APIC ID |
| Bit 3 | Redirection Hint (RH) | 重定向提示 |
| Bit 2 | Destination Mode (DM) | 目标模式 |
| Bit 1-0 | 对齐 | 必须为 00（4 字节对齐） |

### 字段详解

**固定前缀 (0xFEE)**：
- 该值标识了 MSI 专用地址范围，Root Complex 识别到此地址后会特殊处理 ^[pcie-msix.md:414-415]

**Destination ID (Bit 19-12)**：
- 指定目标 CPU 的 APIC ID
- 值范围 0-255 ^[pcie-msix.md:194]

**Redirection Hint (Bit 3)** ^[pcie-msix.md:195-196]：
- `0`：中断直接定向到 Destination ID 指定的 CPU
- `1`：由中断控制器选择目标 CPU

**Destination Mode (Bit 2)** ^[pcie-msix.md:198-199]：
- `0`：Physical 模式（物理 APIC ID）
- `1`：Logical 模式（逻辑模式）

## 地址计算示例

不同 CPU 对应不同的 Message Address ^[pcie-msix.md:201-205]：

| 目标 CPU | Message Address | 说明 |
|----------|-----------------|------|
| CPU 0 | `0xFEE00000` | Dest ID = 0 |
| CPU 1 | `0xFEE01000` | Dest ID = 1（偏移 0x1000）|
| CPU 2 | `0xFEE02000` | Dest ID = 2（偏移 0x2000）|

地址计算公式：`0xFEE00000 + (Destination_ID × 0x1000)`

## 完整 Table Entry 格式

Message Address 是 MSI-X Table Entry 的组成部分。每个 Entry 占 16 字节（4 个 DWORD）^[pcie-msix.md:128-158]：

```
Entry N (16 字节):

Offset 0x00: Message Address Lower  (Bits [31:2] + 2'b00)
Offset 0x04: Message Address Upper  (Bits [63:32])
Offset 0x08: Message Data           (见 [[MSI-X Message Data 格式]])
Offset 0x0C: Vector Control         (Bit 0 为 Mask 位)
```

## 与中断触发的关系

当设备发送 MSI-X 中断时 ^[pcie-msix.md:406-417]：

1. 设备读取 Table Entry 中的 Message Address 和 Message Data
2. 构造 Memory Write TLP：
   - **Address**：Message Address
   - **Data**：Message Data
3. Root Complex 接收 TLP 后：
   - 识别地址范围 `0xFEE00000-0xFEEFFFF` 为 MSI 地址
   - 从 `Addr[19:12]` 提取目标 CPU
   - 从 `Data[7:0]` 提取中断向量

## 配置注意事项

- Message Address 必须 4 字节对齐（低 2 位为 0）^[pcie-msix.md:137-138]
- 上电复位后，Message Address 内容未定义，OS 必须在启用 MSI-X 前配置所有 Entry ^[pcie-msix.md:338-342]
- 高 32 位通常为 0（仅支持 32 位地址寻址时）

## 相关概念

- MSI-X Table - 存储所有中断向量配置
- [MSI-X Message Data 格式](/concepts/msi-x-message-data-格式.md) - 中断数据的编码方式
- [PBA (Pending Bit Array)](/concepts/pba-pending-bit-array.md) - 记录被屏蔽的挂起中断
- APIC - 高级可编程中断控制器
- 中断亲和性 - 将中断绑定到特定 CPU

---

## Sources

- [PCIe MSI-X 详解](pcie-msix.md) - 包含 MSI-X 架构、Table 结构、Message Address 格式及配置流程的完整说明

# Citations

1. [pcie-msix.md:133-143](/references/pcie-msix-66ea67aa.md)
2. [pcie-msix.md:405-411](/references/pcie-msix-66ea67aa.md)
3. [pcie-msix.md:185-205](/references/pcie-msix-66ea67aa.md)
4. [pcie-msix.md:414-415](/references/pcie-msix-66ea67aa.md)
5. [pcie-msix.md:194-194](/references/pcie-msix-66ea67aa.md)
6. [pcie-msix.md:195-196](/references/pcie-msix-66ea67aa.md)
7. [pcie-msix.md:198-199](/references/pcie-msix-66ea67aa.md)
8. [pcie-msix.md:201-205](/references/pcie-msix-66ea67aa.md)
9. [pcie-msix.md:128-158](/references/pcie-msix-66ea67aa.md)
10. [pcie-msix.md:406-417](/references/pcie-msix-66ea67aa.md)
11. [pcie-msix.md:137-138](/references/pcie-msix-66ea67aa.md)
12. [pcie-msix.md:338-342](/references/pcie-msix-66ea67aa.md)
