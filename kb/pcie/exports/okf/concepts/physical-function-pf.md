---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: acdec7271eca1a962da84cd6b5140c8175d8e2ecfd174375c04e0d83131b8b4b
  pageDirectory: concepts
  sources:
    - pcie-sriov.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - physical-function-pf
    - PF(
  citations:
    - file: pcie-sriov.md
      start: 56
      end: 60
    - file: pcie-sriov.md
      start: 68
      end: 80
    - file: pcie-sriov.md
      start: 158
      end: 159
    - file: pcie-sriov.md
      start: 203
      end: 218
    - file: pcie-sriov.md
      start: 236
      end: 257
    - file: pcie-sriov.md
      start: 104
      end: 107
    - file: pcie-sriov.md
      start: 486
      end: 515
    - file: pcie-sriov.md
      start: 163
      end: 186
    - file: pcie-sriov.md
      start: 190
      end: 201
    - file: pcie-sriov.md
      start: 220
      end: 234
    - file: pcie-sriov.md
      start: 421
      end: 462
    - file: pcie-sriov.md
      start: 636
      end: 643
title: Physical Function (PF)
description: 完整的 PCIe 功能实体，包含 SR-IOV 扩展能力，负责管理和配置 VF，充当 VF 与物理硬件之间的桥梁
tags:
  - pcie
  - sriov
  - 硬件架构
timestamp: "2026-08-16T06:46:49.846Z"
---


# Physical Function (PF)

**Physical Function (PF)** 是 SR-IOV (Single Root I/O Virtualization) 架构中的核心组件，是支持 SR-IOV 功能的 PCIe 设备所具备的完整物理功能。

## 概述

Physical Function 是 PCIe 设备上**完整的 PCIe 功能单元**，它包含 SR-IOV 扩展能力，负责管理和配置该设备上的所有 Virtual Functions (VF)。在 SR-IOV 架构中，PF 充当 VF 的控制平面，而 VF 则专注于数据平面操作。^[pcie-sriov.md:56-60]

## 核心特性

PF 具有以下关键特性：

- **完整的配置空间**：PF 拥有标准 PCI 配置空间的所有功能，支持完整的设备配置和管理操作 ^[pcie-sriov.md:68-80]
- **SR-IOV 能力**：PF 包含 SR-IOV Extended Capability 结构，位于扩展配置空间 (0x100+) 的 0x160 偏移附近 ^[pcie-sriov.md:158-159]
- **VF 管理和控制**：PF 负责创建、销毁和配置 VF，通过 Num VFs 寄存器控制启用的 VF 数量 ^[pcie-sriov.md:203-218]
- **资源分配**：PF 管理 VF BARs 的地址分配，确保每个 VF 获得独立的地址空间 ^[pcie-sriov.md:236-257]

## PF 与 VF 对比

| 特性 | PF | VF |
|------|-----|-----|
| 完整配置空间 | ✓ | ✗ (简化) |
| SR-IOV 能力 | ✓ | ✗ |
| MSI-X 中断 | ✓ | ✓ |
| DMA 能力 | ✓ | ✓ |
| 独立 BARs | ✓ | ✓ |
| 数量 | 1 | 多个 (最多 256) |
| 用途 | 管理 | 数据传输 |

^[pcie-sriov.md:68-80]

## 系统架构中的角色

在 SR-IOV 系统架构中，PF 位于虚拟机与物理设备之间，承担以下职责：

```
VM1 ── VF1 ──┐
VM2 ── VF2 ──┼── PF ── 物理设备
VM3 ── VF3 ──┘
```

- **SR-IOV 配置**：设置 VF 数量、偏移量和步长等参数 ^[pcie-sriov.md:104-107]
- **VF 管理**：响应 Num VFs 寄存器的写入，创建或销毁虚拟功能 ^[pcie-sriov.md:486-515]
- **资源分配**：配置 VF BARs，分配每个 VF 的地址空间 ^[pcie-sriov.md:236-257]

## SR-IOV 能力结构

PF 的 SR-IOV Extended Capability 包含多个关键寄存器：

| 偏移 | 字段 | 说明 |
|------|------|------|
| 0x00 | Capability ID | 0x0010 (SR-IOV) |
| 0x08 | SR-IOV Control | VF Enable 等控制位 |
| 0x0C | Initial VFs | 硬件支持的最大 VF 数 |
| 0x0E | Total VFs | 当前可用 VF 数量 |
| 0x10 | Num VFs | 已启用的 VF 数量 |
| 0x14 | First VF Offset | 第一个 VF 的偏移 |
| 0x16 | VF Stride | VF 之间的步长 |

^[pcie-sriov.md:163-186]

### 控制寄存器

SR-IOV Control Register (偏移 0x08) 包含以下关键位：

| 位 | 字段 | 说明 |
|----|------|------|
| 0 | VF Enable | 使能 VF (1=启用) |
| 1 | VF Migration Enable | 使能 VF 迁移 |
| 3 | VF MSE | VF 内存空间使能 |
| 4 | ARI Capable Hierarchy | ARI 层次结构支持 |

^[pcie-sriov.md:190-201]

## BDF 地址分配

PF 拥有标准 BDF (Bus:Device.Function) 地址，VF 则在其基础上通过 First VF Offset 和 VF Stride 计算得出：

```
VF[i] BDF = PF BDF + First VF Offset + (i × VF Stride)
```

例如，若 PF 地址为 `01:00.0`，Offset 为 1，Stride 为 1，则 VF0 = `01:00.1`，VF1 = `01:00.2`，以此类推。^[pcie-sriov.md:220-234]

## 在 FEMU 中的实现

FEMU 通过 `PCIESriovPF` 结构体实现 PF 功能：

```c
typedef struct PCIESriovPF {
    PCIDevice *pf;                  // Physical Function
    uint16_t num_vfs;               // 当前 VF 数量
    uint16_t total_vfs;             // 最大 VF 数量
    uint16_t vf_offset;             // VF 偏移
    uint16_t vf_stride;             // VF 步长
    PCIDevice **vfs;                // VF 设备数组
    MemoryRegion *vf_bars[PCI_NUM_REGIONS]; // VF BARs
} PCIESriovPF;
```

通过 `pcie_sriov_pf_init()` 函数初始化 PF 的 SR-IOV 能力，设置 VF 数量、偏移、步长和设备 ID 等参数。^[pcie-sriov.md:421-462]

## 相关概念

- [Virtual Function (VF)](/concepts/virtual-function-vf.md) — PF 创建的轻量级虚拟功能
- SR-IOV — PF 和 VF 所在的 PCIe 虚拟化框架
- [PCIe 配置空间](/concepts/pcie-配置空间.md) — PF 配置空间的详细结构
- VFIO — 将 VF 分配给虚拟机的推荐方式

## 总结

Physical Function 是 SR-IOV 架构中的核心管理实体，每个支持 SR-IOV 的 PCIe 设备有且仅有一个 PF。PF 具备完整的 PCIe 功能，负责 VF 的生命周期管理和资源分配，使得单个物理设备能够高效地虚拟化为多个独立的虚拟设备，供虚拟机直接访问，从而实现接近原生性能的 I/O 虚拟化。^[pcie-sriov.md:56-60, pcie-sriov.md:636-643]

---

## Sources

- [SR-IOV 虚拟化详解 (pcie-sriov.md)](../pcie-sriov.md)

# Citations

1. [pcie-sriov.md:56-60](/references/pcie-sriov-08f3fcbf.md)
2. [pcie-sriov.md:68-80](/references/pcie-sriov-08f3fcbf.md)
3. [pcie-sriov.md:158-159](/references/pcie-sriov-08f3fcbf.md)
4. [pcie-sriov.md:203-218](/references/pcie-sriov-08f3fcbf.md)
5. [pcie-sriov.md:236-257](/references/pcie-sriov-08f3fcbf.md)
6. [pcie-sriov.md:104-107](/references/pcie-sriov-08f3fcbf.md)
7. [pcie-sriov.md:486-515](/references/pcie-sriov-08f3fcbf.md)
8. [pcie-sriov.md:163-186](/references/pcie-sriov-08f3fcbf.md)
9. [pcie-sriov.md:190-201](/references/pcie-sriov-08f3fcbf.md)
10. [pcie-sriov.md:220-234](/references/pcie-sriov-08f3fcbf.md)
11. [pcie-sriov.md:421-462](/references/pcie-sriov-08f3fcbf.md)
12. [pcie-sriov.md:636-643](/references/pcie-sriov-08f3fcbf.md)
