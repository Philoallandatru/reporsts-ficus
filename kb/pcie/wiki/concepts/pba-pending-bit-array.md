---
title: PBA (Pending Bit Array)
summary: 位图数组，用于记录被屏蔽的中断挂起状态，当中断被屏蔽时触发则设置对应位，解除屏蔽后由 OS 检查处理
sources:
- pcie-msix.md
kind: concept
createdAt: '2026-08-16T06:42:48.716Z'
updatedAt: '2026-08-16T06:42:48.716Z'
tags:
- pcie
- 中断
- 状态管理
aliases:
- pba-pending-bit-array
- P(BA
confidence: 0.95
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: PBA 是一个位图结构，存储在设备的 BAR（Base Address Register）空间中，每个 MSI-X 中断向量对应一个比特位。当某个中断向量被屏蔽（Masked）时，如果设备触发了该中断，则对应的
  PBA 位会被置 1，以标记该中断处于待处理状态。^[pcie-msix.md:239-249]
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PBA (Pending Bit Array)

## 概述

**PBA（Pending Bit Array，待处理位数组）** 是 MSI-X（Message Signaled Interrupts - Extended）中断机制中的重要组成部分，用于记录在中断被屏蔽期间设备触发的待处理中断。^[pcie-msix.md:239-249]

PBA 是一个位图结构，存储在设备的 BAR（Base Address Register）空间中，每个 MSI-X 中断向量对应一个比特位。当某个中断向量被屏蔽（Masked）时，如果设备触发了该中断，则对应的 PBA 位会被置 1，以标记该中断处于待处理状态。^[pcie-msix.md:239-249]

## 工作原理

### 屏蔽中断场景

PBA 的典型使用场景如下：

1. 某个 MSI-X 中断向量被屏蔽（Vector Control Bit 0 = 1）
2. 设备检测到相关事件并触发中断
3. 由于该中断被屏蔽，设备不发送 MSI Memory Write TLP（事务层数据包）
4. 设备在 PBA 中将对应位设置为 1
5. 操作系统稍后取消该中断的屏蔽状态
6. 操作系统检查 PBA，发现有挂起的中断
7. 操作系统重新触发或处理该中断 ^[pcie-msix.md:242-249]

这种机制确保了即使中断暂时被禁用，也不会丢失设备产生的中断信号。

### 与 MSI-X Table 的交互

在 MSI-X 架构中，PBA 与 MSI-X Table 协同工作：

```
┌─────────────────────────────────────────────┐
│  配置空间 MSI-X Capability                  │
│  ┌──────────────────────────────────────┐   │
│  │ Table: BAR=0, Offset=0x2000          │   │
│  │ PBA: BAR=0, Offset=0x3000            │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

- **MSI-X Table**：存储每个中断向量的配置信息（Message Address、Message Data、Vector Control）
- **PBA**：记录哪些中断在屏蔽期间被触发 ^[pcie-msix.md:22-25, pcie-msix.md:44-50]

## 数据结构

### PBA 格式

PBA 是一个**位图数组**，每个中断向量占用一个比特位，多个中断被打包成 64 位（QWORD）：

```
PBA Base (如 BAR 0 + 0x3000):

QWORD 0 (Offset 0x00):  Bits 0-63
┌───┬───┬───┬───┬───┬───┬───┬───┐
│63 │...│ 2 │ 1 │ 0 │   │   │   │
└───┴───┴───┴───┴───┴───┴───┴───┘
  ↑               ↑
  中断 63 挂起    中断 0 挂起

QWORD 1 (Offset 0x08):  Bits 64-127
┌───┬───┬───┬───┬───┬───┬───┬───┐
│127│...│66 │65 │64 │   │   │   │
└───┴───┴───┴───┴───┴───┴───┴───┘

...

总大小 = ceil(中断数量 / 64) * 8 字节
```

**计算示例**：

- 33 个中断向量：需要 ceil(33/64) = 1 个 QWORD = 8 字节
- 256 个中断向量：需要 ceil(256/64) = 4 个 QWORD = 32 字节 ^[pcie-msix.md:253-274]

### PBA 位置声明

PBA 的位置通过 PCI Express 配置空间中的 MSI-X Capability 结构声明：

```
Offset 0x08: PBA Offset/BIR (32-bit)
31                           3   2    0
┌──────────────────────────────┬───────┐
│   PBA Offset [31:3]          │  BIR  │
│   (8-byte 对齐)              │       │
└──────────────────────────────┴───────┘
```

- **BIR（BAR Indicator Register）**：指示 PBA 位于哪个 BAR（0-5）
- **PBA Offset**：PBA 在该 BAR 内的偏移地址（8 字节对齐） ^[pcie-msix.md:100-106]

## 读取与使用

### 读取示例

以下代码演示如何读取 PBA 并检查特定中断是否处于挂起状态：

```c
// 读取 PBA，检查中断 5 是否挂起
uint64_t pba_qword = read_pba(0);  // 读取 QWORD 0
bool pending = (pba_qword & (1ULL << 5)) != 0;

if (pending) {
    // 中断 5 在被屏蔽期间触发过
    handle_pending_interrupt(5);
}
```

该代码读取 PBA 的第一个 QWORD（包含中断 0-63），然后检查第 5 位是否被置位。^[pcie-msix.md:276-286]

### 调试与测试

在实际调试中，可以通过以下方式观察 PBA 的行为：

```c
// 屏蔽中断向量 5
uint32_t *table = (uint32_t *)(bar0_base + 0x2000);
table[5 * 4 + 3] |= 1;  // 设置 Vector Control Bit 0

// 触发 I/O，观察 PBA
uint64_t *pba = (uint64_t *)(bar0_base + 0x3000);
if (pba[0] & (1ULL << 5)) {
    printf("Interrupt 5 is pending\n");
}

// 取消屏蔽
table[5 * 4 + 3] &= ~1;
```

当中断被屏蔽后触发设备 I/O，PBA 中对应位会被置 1；取消屏蔽后，操作系统通常会检查并处理该挂起中断。^[pcie-msix.md:594-608]

## 典型应用场景

### NVMe 设备

在 NVMe 存储设备中，每个 I/O 队列对应一个独立的中断向量。当驱动程序动态调整中断屏蔽状态时，PBA 确保不会丢失任何 I/O 完成通知。^[pcie-msix.md:55-59]

### 多队列网卡

高速网卡使用多队列架构，每个 RX/TX 队列独立中断。PBA 机制允许系统在保持部分中断屏蔽的同时，不丢失其他队列的事件通知。^[pcie-msix.md:55-59]

## 相关概念

- MSI-X：支持最多 2048 个独立中断向量的高级中断机制
- MSI：Message Signaled Interrupts，PCIe 中断机制的基础
- MSI-X Table：存储 MSI-X 中断向量配置的结构
- MSI-X Capability：PCI 配置空间中声明 MSI-X 支持的结构
- BAR：Base Address Register，用于映射设备内存空间
- PCI Express：支持 MSI-X 的总线标准
- TLP：Transaction Layer Packet，PCIe 事务层数据包

---

## Sources

- [pcie-msix.md](../../sources/pcie-msix.md) — MSI-X 中断机制详解，包含 PBA 的完整描述和使用示例（行 235-287）

