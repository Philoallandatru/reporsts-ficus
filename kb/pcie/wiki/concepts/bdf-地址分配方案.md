---
title: BDF 地址分配方案
summary: SR-IOV 设备使用 Bus:Device.Function 地址格式，VF 通过 First VF Offset 和 VF Stride 计算得出
sources:
- pcie-sriov.md
kind: concept
createdAt: '2026-08-16T06:48:02.255Z'
updatedAt: '2026-08-16T06:48:02.255Z'
tags:
- pcie
- 寻址
- bdf
aliases:
- bdf-地址分配方案
confidence: 0.9
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: BDF（Bus:Device.Function）地址分配方案是 SR-IOV 技术中用于标识 PCIe 设备及其虚拟功能的关键机制。该方案定义了
  Physical Function（PF）和 Virtual Function（VF）在 PCIe 总线上的地址分配规则。 ^[pcie-sriov.md:121-122]
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# BDF 地址分配方案

BDF（Bus:Device.Function）地址分配方案是 SR-IOV 技术中用于标识 PCIe 设备及其虚拟功能的关键机制。该方案定义了 Physical Function（PF）和 Virtual Function（VF）在 PCIe 总线上的地址分配规则。 ^[pcie-sriov.md:121-122]

## 概述

SR-IOV 设备采用特殊的 BDF 地址方案来组织 PF 和 VF 的地址空间。这种分配方式确保了每个虚拟功能都能获得唯一且可预测的设备标识符，便于系统软件进行管理和分配。 ^[pcie-sriov.md:121-122]

## PF 地址分配

Physical Function（物理功能）使用标准的 PCIe 设备地址格式。以典型的 SR-IOV 网卡为例，其 PF 地址通常表示为：

```
Bus 1, Device 0, Function 0 → 01:00.0
```

PF 作为完整的 PCIe 功能设备，拥有完整的配置空间和所有标准 PCI 能力。PF 负责管理和配置 VF，是 SR-IOV 功能的核心控制点。 ^[pcie-sriov.md:124, pcie-sriov.md:56-60]

## VF 地址分配规则

Virtual Function（虚拟功能）的地址在 PF 基础上按照特定规则连续分配：

```
VF0: Bus 1, Device 0, Function 1 → 01:00.1
VF1: Bus 1, Device 0, Function 2 → 01:00.2
VF2: Bus 1, Device 0, Function 3 → 01:00.3
...
VF7: Bus 1, Device 1, Function 0 → 01:01.0 (跨设备号)
```

VF 地址分配遵循以下核心规则：

- **Bus 号规则**：VF 的 Bus 号等于 PF Bus 号加上偏移量（Offset）
- **连续递增**：VF 的 Device.Function 值连续递增
- **进位规则**：每个设备最多支持 8 个 Function（Function 0-7），超出后进位到下一个 Device ^[pcie-sriov.md:133-137]

## 地址计算公式

VF 的 BDF 地址可通过以下公式精确计算：

```
VF[i] BDF = PF BDF + First VF Offset + (i × VF Stride)
```

其中关键参数定义如下：

| 参数 | 说明 |
|------|------|
| **First VF Offset** | 第一个 VF 相对于 PF Routing ID 的偏移量 |
| **VF Stride** | 相邻 VF 之间的 Routing ID 步长，通常为 1 |
| **i** | VF 的索引序号（从 0 开始） |

以实际数据为例，若 PF 地址为 `01:00.0`，First VF Offset 为 1，VF Stride 为 1，则：

- VF0 = 01:00.0 + 1 = **01:00.1**
- VF1 = 01:00.0 + 2 = **01:00.2**
- VF2 = 01:00.0 + 3 = **01:00.3** ^[pcie-sriov.md:220-234]

## SR-IOV 配置空间中的相关寄存器

在 SR-IOV Extended Capability 结构中，有两个关键寄存器控制 VF 的地址分配：

| 寄存器偏移 | 名称 | 用途 |
|-----------|------|------|
| 0x14 | First VF Offset | 定义首个 VF 的路由 ID 偏移 |
| 0x16 | VF Stride | 定义相邻 VF 之间的步长 |

这些寄存器位于扩展配置空间（偏移通常在 0x160 左右），软件可通过修改这些值来调整 VF 的地址分配模式。 ^[pcie-sriov.md:178, pcie-sriov.md:220-231]

## 实际应用示例

在 Linux 系统中，可通过 `lspci` 命令查看 SR-IOV 设备的 BDF 分配情况：

```bash
# 查看 PF 和 VF 的 BDF 地址
lspci -vvv -s 01:00.0 | grep -i "SR-IOV"

# 输出示例
01:00.0 Ethernet controller: Intel 82599
        Capabilities: [160] Single Root I/O Virtualization (SR-IOV)
01:00.1 Ethernet controller: Intel Virtual Function
01:00.2 Ethernet controller: Intel Virtual Function
01:00.3 Ethernet controller: Intel Virtual Function
```

启用 VF 后，系统会自动按照 BDF 地址分配方案为每个 VF 分配唯一地址，地址格式从 PF 的 `01:00.0` 开始依次递增。 ^[pcie-sriov.md:265-276, pcie-sriov.md:344-352]

## 特殊情况

某些场景下 VF Stride 可能大于 1（例如支持 Function Level Reset 的设备）。此时 VF 地址之间会存在间隔：

```
VF Stride = 2 时：
VF0: 01:00.1
VF1: 01:00.3 (跳过 Function 2)
VF2: 01:00.5 (跳过 Function 4)
```

这种设计为某些高级功能（如 VFIO 设备直通的隔离需求）提供了灵活性。 ^[pcie-sriov.md:228-230]

## 相关概念

- SR-IOV — 单根 I/O 虚拟化技术
- Physical Function — 物理功能
- Virtual Function — 虚拟功能
- BAR 配置空间 — VF 地址空间映射
- VFIO — 虚拟功能 I/O 直通框架

---

## Sources

- [SR-IOV 虚拟化详解](../../sources/pcie-sriov.md) — BDF 地址分配方案（第 119-137 行）、VF 地址计算公式（第 220-234 行）

