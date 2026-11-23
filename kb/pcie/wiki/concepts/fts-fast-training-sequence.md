---
title: FTS (Fast Training Sequence)
summary: 从 L0s 快速恢复到 L0 所需的训练序列，用于接收器快速锁定时钟
sources:
- pcie-aspm.md
kind: concept
createdAt: '2026-08-16T06:34:26.698Z'
updatedAt: '2026-08-16T06:34:26.698Z'
tags:
- pcie
- link-training
- recovery
aliases:
- fts-fast-training-sequence
- F(TS
confidence: 0.95
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: FTS 的核心作用是在链路从低功耗状态退出时，快速恢复时钟锁定，使接收器能够重新正确解析数据。由于 L0s 状态仅关闭了发送器电路而保持接收器运行，因此恢复过程相对简单，需要的只是重新锁定时钟。
  ^[pcie-aspm.md:99-105]
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# FTS (Fast Training Sequence)

**FTS (Fast Training Sequence，快速训练序列)** 是 PCIe 链路从低功耗状态快速恢复到正常工作状态所使用的训练序列，主要用于 ASPM 机制中从 L0s 状态返回 L0 状态的过程。 ^[pcie-aspm.md:120-131]

## 概述

FTS 的核心作用是在链路从低功耗状态退出时，快速恢复时钟锁定，使接收器能够重新正确解析数据。由于 L0s 状态仅关闭了发送器电路而保持接收器运行，因此恢复过程相对简单，需要的只是重新锁定时钟。 ^[pcie-aspm.md:99-105]

**FTS 的主要特点**：

- 用于快速时钟恢复的训练序列 ^[pcie-aspm.md:122]
- 退出延迟仅为 200-500 纳秒 ^[pcie-aspm.md:82,117]
- 由发送端自动发送，接收端通过识别该序列完成时钟恢复 ^[pcie-aspm.md:102-104]

## 编码方式

FTS 的具体实现取决于 PCIe 的物理层编码方式。不同代际的 PCIe 使用不同的编码方案，导致 FTS 的具体形式也有所不同。 ^[pcie-aspm.md:124-131]

### 8b/10b 编码（Gen 1-2）

对于采用 8b/10b 编码的 PCIe Gen 1 和 Gen 2 链路，FTS 序列由多个 **K28.1** 符号组成。这些特殊的控制符号具有唯一性，易于接收器识别和同步。 ^[pcie-aspm.md:125-126]

发送的 K28.1 符号数量 **N** 由链路的 Link Capabilities 寄存器定义。这个数值代表了接收器成功锁定时钟所需的最小训练符号数。 ^[pcie-aspm.md:126]

### 128b/130b 编码（Gen 3+）

对于 PCIe Gen 3 及更高版本，采用的 128b/130b 编码方案使用 **EIEOS (Electrical Idle Exit OS)** 作为退出空闲状态的训练序列。相比 8b/10b 编码，这种方式具有更快的恢复机制。 ^[pcie-aspm.md:128-130]

## L0s 到 L0 的状态转换

FTS 在 L0s 状态退出过程中扮演关键角色。当链路从 L0s 返回到 L0 活动状态时，会经历以下步骤： ^[pcie-aspm.md:99-105, pcie-aspm.md:107-118]

```
L0            L0s              L0
 │  空闲检测   │   需要发送      │
 ├────────────>│                │
 │  发送 EIOS  │                │
 │  关闭 TX    │   启动 TX      │
 │             ├───────────────>│
 │             │  发送 FTS      │
 │             │  时钟恢复      │
                │                │
         延迟: 200-500 ns
```

1. **检测到待发送的 TLP**：当有数据需要传输时，发送器启动
2. **启动发送器**：发送器电路重新通电
3. **发送 FTS**：发送快速训练序列，让接收器重新锁定时钟
4. **接收器锁定时钟**：接收器通过解析 FTS 恢复位同步
5. **恢复到 L0**：链路恢复正常数据传输

整个过程的退出延迟仅为 **200-500 纳秒**，这使得 L0s 非常适合处理短暂的链路空闲场景。 ^[pcie-aspm.md:82,117]

## 与其他训练序列的区别

PCIe 链路在不同的场景下使用多种训练序列，FTS 是其中延迟最低的一种。

| 序列类型 | 用途 | 延迟 | 应用场景 |
|---------|------|------|---------|
| TS1/TS2 | 链路初始化和重新训练 | 毫秒级 | 上电、热复位、链路重建 |
| FTS | L0s 快速恢复 | 微秒级 | 短暂空闲后恢复 |
| EIEOS | Gen 3+ 退出空闲 | 微秒级 | 128b/130b 编码的空闲退出 |

FTS 专门针对 L0s 状态设计，因为 L0s 仅关闭发送器而保持接收器时钟运行，所以恢复所需时间很短。相比之下，从 L1 或更深层的低功耗状态退出时，需要执行完整的链路训练过程（TS1/TS2），延迟会达到毫秒级别。 ^[pcie-aspm.md:163-168]

## 配置参数

FTS 相关的配置参数位于 PCIe 配置空间的 Link Capabilities 寄存器中。虽然 FTS 序列本身由硬件自动处理，但 Link Capabilities 中的 L0s Exit Latency 字段描述了链路的预期 FTS 恢复时间。 ^[pcie-aspm.md:289-325]

```
Bit 14-12: L0s Exit Latency (Upstream)
  000b = < 64 ns
  001b = 64-128 ns
  010b = 128-256 ns
  011b = 256-512 ns
  100b = 512 ns - 1 μs
  ...
```

操作系统和驱动程序可以根据这些延迟参数来决定是否启用 ASPM L0s，以平衡功耗节省与性能影响。

## 实际应用考量

在设计或配置 PCIe 系统时，FTS 的存在使得 L0s 成为了一种几乎无性能损失的低功耗方案。 ^[pcie-aspm.md:270-277]

对于高频率小请求的工作负载（如随机读取），虽然每次 L0s 恢复仅需数百纳秒，但频繁的进入和退出可能会累积显著延迟。这种情况下，可以考虑禁用 ASPM 或仅启用 L1 状态。 ^[pcie-aspm.md:271-272]

对于批量传输配合长时间空闲的场景，L0s 能够在短暂空闲时快速恢复，同时在长时间空闲时进入更深的 L1 状态，这是性能和功耗之间的理想平衡。 ^[pcie-aspm.md:275-277]

---

## 总结

FTS (快速训练序列) 是 PCIe ASPM 机制中实现低功耗快速恢复的关键技术。通过发送特殊的训练符号序列，FTS 使接收器能够在极短时间内重新锁定时钟，从而支持 L0s 状态 200-500 纳秒的快速退出延迟。这一特性使得 L0s 成为一种几乎无感知、同时又能节省 10-20% 功耗的低功耗状态，非常适合处理短暂的链路空闲场景。

---

## Sources

- ASPM (Active State Power Management) 电源管理](pcie-aspm.md)

