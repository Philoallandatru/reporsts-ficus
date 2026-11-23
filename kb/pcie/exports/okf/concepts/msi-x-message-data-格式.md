---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 97951cbe81de9e631bc03e0a1145f959b1935a00e32fdafb0debcbe48aa73ccb
  pageDirectory: concepts
  sources:
    - pcie-msix.md
  confidence: 0.9
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - msi-x-message-data-格式
    - MMD格
  citations:
    - file: pcie-msix.md
      start: 209
      end: 226
    - file: pcie-msix.md
      start: 215
      end: 216
    - file: pcie-msix.md
      start: 217
      end: 223
    - file: pcie-msix.md
      start: 224
      end: 226
    - file: pcie-msix.md
      start: 228
      end: 231
    - file: pcie-msix.md
      start: 397
      end: 417
    - file: pcie-msix.md
      start: 207
      end: 231
title: MSI-X Message Data 格式
description: 中断数据格式，包含中断向量号 (Bits 7-0)、投递模式 (Bits 10-8) 和触发模式 (Bit 15)
tags:
  - pcie
  - 中断
  - 数据格式
timestamp: "2026-08-16T06:43:05.704Z"
---

# MSI-X Message Data 格式

MSI-X Message Data 是 MSI-X 中断机制中用于携带中断信息的关键字段，定义在 MSI-X Table Entry 的偏移 0x08 处，共 32 位（其中低 16 位有效）。

---

## 字段结构

Message Data 的完整位布局如下：

```
15    14  11  10    8  7             0
┌─────┬─────┬───────┬────────────────┐
│ TM  │Rsvd │  DM   │   Vector       │
│ (1) │     │  (3)  │   (8)          │
└─────┴─────┴───────┴────────────────┘
```

| 位域 | 名称 | 宽度 | 说明 |
|------|------|------|------|
| Bit 7-0 | Interrupt Vector | 8 bits | 中断向量号，范围 0x20-0xFF（32-255） |
| Bit 10-8 | Delivery Mode | 3 bits | 投递模式 |
| Bit 14-11 | Reserved | 4 bits | 保留位 |
| Bit 15 | Trigger Mode | 1 bit | 触发模式 |

^[pcie-msix.md:209-226]

---

## 各字段详解

### Interrupt Vector（中断向量号）

Bit 7-0 指定目标 CPU 要处理的中断向量号，范围为 0x20 到 0xFF（十进制 32-255）。该向量号对应 APIC 中断向量表中的索引。^[pcie-msix.md:215-216]

### Delivery Mode（投递模式）

Bit 10-8 定义中断的投递方式：

| 值 | 模式 | 说明 |
|----|------|------|
| 000b | Fixed | 定向中断，直接投递到目标 CPU |
| 001b | Lowest Priority | 最低优先级，由中断控制器选择负载最轻的 CPU |
| 010b | SMI | 系统管理中断 |
| 100b | NMI | 不可屏蔽中断 |
| 101b | INIT | 初始化中断 |
| 111b | ExtINT | 外部中断（通过 I/O APIC 转发） |

^[pcie-msix.md:217-223]

### Trigger Mode（触发模式）

Bit 15 指定中断触发方式：
- **0 = Edge（边沿触发）**：推荐模式，信号上升沿触发
- **1 = Level（电平触发）**：电平敏感

^[pcie-msix.md:224-226]

---

## 使用示例

### 数据解析示例

```
0x0040:
  Binary: 0000 0000 0100 0000
  ├─ Bit 15 (TM):  0 → Edge 触发
  ├─ Bit 10-8 (DM): 000b → Fixed 投递模式
  └─ Bit 7-0: 0x40 → 中断向量 64

0x4123:
  Binary: 0100 0001 0010 0011
  ├─ Bit 15 (TM):  0 → Edge 触发
  ├─ Bit 10-8 (DM): 001b → Lowest Priority
  └─ Bit 7-0: 0x23 → 中断向量 35
```

^[pcie-msix.md:228-231]

### 实际中断发送流程中的 Message Data

当设备发送 MSI-X 中断时，Root Complex 从 TLP 中提取 Message Data 字段：

```
1. 设备读取 MSI-X Table Entry
   - Message Address: 0xFEE01000
   - Message Data: 0x0043    ← 解析为 Vector=0x43, Fixed, Edge
   - Vector Control: 0 (Unmasked)

2. 设备构造 Memory Write TLP
   - Address: 0xFEE01000
   - Data: 0x0043
   - Length: 1 DW

3. Root Complex 处理
   ├─> 识别为 MSI 地址范围
   ├─> 提取目标 CPU (Addr[19:12] = 1)
   └─> 提取中断向量 (Data[7:0] = 0x43)
       → 触发 CPU 1 的中断 0x43
```

^[pcie-msix.md:397-417]

---

## 与 Message Address 的配合

Message Data 与 [Message Address](/concepts/msi-x-message-address-格式.md) 共同构成完整的中断目标信息：

| 字段 | 作用 | 位置 |
|------|------|------|
| Message Address | 指定目标 CPU（APIC ID） | Table Entry +0x00 / +0x04 |
| Message Data | 指定中断向量和投递方式 | Table Entry +0x08 |

---

## 软件配置

在操作系统配置 MSI-X 中断时，通常由 OS 自动计算合适的 Message Data 值：

```c
// Linux 内核中的 MSI-X 向量配置
nr_vectors = pci_alloc_irq_vectors(pdev, 1, nr_vectors, PCI_IRQ_MSIX);
// 分配后，每个向量对应一个唯一的 Message Data
for (i = 0; i < nr_vectors; i++) {
    int irq = pci_irq_vector(pdev, i);
    request_irq(irq, handler, 0, "device", &data);
}
```

---

## 相关概念

- [MSI-X Table 结构](/concepts/msi-x-table-结构.md) — 了解 Message Data 在 Table Entry 中的完整位置
- MSI-X 中断发送 — 了解 Message Data 如何被设备使用
- PBA Pending Bit Array — 了解中断屏蔽时的挂起机制

---

## Sources

^[pcie-msix.md:207-231]

# Citations

1. [pcie-msix.md:209-226](/references/pcie-msix-66ea67aa.md)
2. [pcie-msix.md:215-216](/references/pcie-msix-66ea67aa.md)
3. [pcie-msix.md:217-223](/references/pcie-msix-66ea67aa.md)
4. [pcie-msix.md:224-226](/references/pcie-msix-66ea67aa.md)
5. [pcie-msix.md:228-231](/references/pcie-msix-66ea67aa.md)
6. [pcie-msix.md:397-417](/references/pcie-msix-66ea67aa.md)
7. [pcie-msix.md:207-231](/references/pcie-msix-66ea67aa.md)
