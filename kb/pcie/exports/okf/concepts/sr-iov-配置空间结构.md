---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: b4e0a0894991e3e2d70dd8ad4d6671c80427e57795f8aa515e2d627322307706
  pageDirectory: concepts
  sources:
    - pcie-sriov.md
  confidence: 0.9
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - sr-iov-配置空间结构
  citations:
    - file: pcie-sriov.md
      start: 141
      end: 159
    - file: pcie-sriov.md
      start: 145
      end: 159
    - file: pcie-sriov.md
      start: 158
      end: 159
    - file: pcie-sriov.md
      start: 161
      end: 186
    - file: pcie-sriov.md
      start: 190
      end: 201
    - file: pcie-sriov.md
      start: 203
      end: 218
    - file: pcie-sriov.md
      start: 220
      end: 234
    - file: pcie-sriov.md
      start: 236
      end: 257
    - file: pcie-sriov.md
      start: 252
      end: 257
    - file: pcie-sriov.md
      start: 182
      end: 183
    - file: pcie-sriov.md
      start: 68
      end: 80
    - file: pcie-sriov.md
      start: 282
      end: 304
    - file: pcie-sriov.md
      start: 307
      end: 329
title: SR-IOV 配置空间结构
description: SR-IOV Extended Capability 位于 PCIe 扩展配置空间 (0x100+)，包含 Num VFs、VF Offset、VF Stride、VF BARs 等关键寄存器
tags:
  - pcie
  - 配置空间
  - 寄存器
timestamp: "2026-08-16T06:47:31.352Z"
---


# SR-IOV 配置空间结构

SR-IOV (Single Root I/O Virtualization) 的配置空间是实现硬件级虚拟化的核心机制。SR-IOV 扩展能力位于 PCIe 扩展配置空间 (0x100 地址之后)，其中定义了管理虚拟功能所需的所有寄存器和配置信息。 ^[pcie-sriov.md:141-159]

## PF 配置空间布局

[Physical Function (PF)](/concepts/physical-function-pf.md) 的配置空间在标准 PCI Header 之后，通过 Capabilities 链和 Extended Capabilities 链来扩展功能。标准 PCI Header 占用 0x00-0x3F 区域，Capabilities 区域从 0x40 开始，包含 PCIe Capability 和 MSI-X Capability 等标准能力。SR-IOV Extended Capability 则位于扩展配置空间，从 0x100 地址开始。 ^[pcie-sriov.md:145-159]

```
PF 配置空间布局：

0x00-0x3F: 标准 PCI Header
0x40+:     Capabilities
           ├── PCIe Capability
           ├── MSI-X Capability
           └── ...
0x100+:    Extended Capabilities
           ├── SR-IOV Extended Capability (关键!)
           ├── ARI (Alternative Routing-ID)
           └── ...
```

扩展配置空间的起始地址 0x100 是 PCIe 规范定义的基准偏移量，不同设备的 SR-IOV Capability 实际位置可能略有差异，通常在 0x160 左右。 ^[pcie-sriov.md:158-159]

## SR-IOV Extended Capability 结构

SR-IOV Extended Capability 是整个配置空间的核心部分，包含 0x3C (60 字节) 的寄存器定义。以下是完整的寄存器布局： ^[pcie-sriov.md:161-186]

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0x00 | 2 | Capability ID | 0x0010 (SR-IOV) |
| 0x02 | 2 | Next Capability | 指向下一个扩展能力的偏移 |
| 0x04 | 4 | SR-IOV Capabilities | 能力位字段 (只读) |
| 0x08 | 2 | SR-IOV Control | 控制寄存器 (读写) |
| 0x0A | 2 | SR-IOV Status | 状态寄存器 (只读) |
| 0x0C | 2 | Initial VFs | 硬件支持的最大 VF 数量 |
| 0x0E | 2 | Total VFs | 当前可用的 VF 总数 |
| 0x10 | 2 | Num VFs | 当前启用的 VF 数量 |
| 0x12 | 1 | Function Dependency | 功能依赖链接 |
| 0x13 | 1 | Reserved | 保留字段 |
| 0x14 | 2 | First VF Offset | 第一个 VF 的路由 ID 偏移 |
| 0x16 | 2 | VF Stride | VF 之间的路由 ID 步长 |
| 0x18 | 2 | Reserved | 保留字段 |
| 0x1A | 2 | VF Device ID | VF 的专用设备 ID |
| 0x1C | 4 | Supported Page Sizes | 支持的页大小位掩码 |
| 0x20 | 4 | System Page Size | 系统页大小 |
| 0x24 | 24 | VF BAR0-5 | VF 的 BAR 配置寄存器 (每个 BAR 4 字节) |
| 0x3C | 4 | VF Migration State | 迁移状态数组偏移 |

这个结构的设计使得 PF 可以集中管理所有 VF 的配置信息，包括数量控制、地址分配和中断配置。 ^[pcie-sriov.md:161-186]

## 关键寄存器详解

### SR-IOV Control Register (偏移 0x08)

Control 寄存器用于启用和控制 VF 的各项功能，包含多个关键控制位： ^[pcie-sriov.md:190-201]

| Bits | Field | Description |
|------|-------|-------------|
| 0 | VF Enable | 使能 VF (1=启用) |
| 1 | VF Migration Enable | 使能 VF 迁移功能 |
| 2 | VF Migration Interrupt En | VF 迁移中断使能 |
| 3 | VF MSE (Memory Space En) | VF 内存空间使能 |
| 4 | ARI Capable Hierarchy | ARI 层次结构支持 |
| 5-15 | Reserved | 保留字段 |

VF Enable 位是最核心的控制位，只有设置此位后，VF 才会被激活并响应 PCI 事务。VF MSE 位则控制 VF 是否可以访问其 BAR 映射的内存空间。 ^[pcie-sriov.md:190-201]

### VF 数量相关寄存器

三个 VF 数量相关寄存器承担不同的职责： ^[pcie-sriov.md:203-218]

**Initial VFs** (偏移 0x0C，只读) 表示硬件固件支持的最大 VF 数量，这是设备出厂时确定的固定值，例如某些高端网卡支持 256 个 VF。

**Total VFs** (偏移 0x0E，只读) 表示当前系统配置下可用的 VF 数量。由于系统资源限制或 BIOS 配置，该值可能小于 Initial VFs。

**Num VFs** (偏移 0x10，读写) 是软件实际启用 VF 的数量。驱动程序通过写入此字段来创建指定数量的 VF，取值范围为 0 到 Total VFs。 ^[pcie-sriov.md:203-218]

### VF 地址分配寄存器

First VF Offset 和 VF Stride 两个寄存器共同决定了每个 VF 的 BDF 地址 分配方案： ^[pcie-sriov.md:220-234]

**First VF Offset** 定义了第一个 VF 相对于 PF 路由 ID 的偏移量。例如，当 PF 为 01:00.0，Offset 为 1 时，第一个 VF 的地址为 01:00.1。

**VF Stride** 定义相邻 VF 之间路由 ID 的步长，通常为 1 表示连续分配。在某些支持 Function Level Reset 的设备上，该值可能为 2 或更大。

VF BDF 地址的计算公式为：VF[i] BDF = PF BDF + First VF Offset + (i × VF Stride)。这种设计允许灵活配置 VF 的地址分布。 ^[pcie-sriov.md:220-234]

### [VF BARs 配置](/concepts/vf-bars-配置.md)

VF BARs 配置在 SR-IOV Extended Capability 的 0x24-0x38 区域，每个 VF BAR 占用 4 字节，共 6 个 BAR (对应 BAR0-BAR5)。与标准 BAR 配置 不同，VF BARs 的配置统一存放在 PF 的配置空间中，而不是每个 VF 拥有独立的 BAR 寄存器。 ^[pcie-sriov.md:236-257]

VF BARs 的配置方式与标准 BAR 类似，支持 32 位内存、64 位内存和 IO 地址类型。软件写入全 1 来查询 BAR 大小时，硬件返回的基地址是每个 VF 独立地址范围内的值。 ^[pcie-sriov.md:236-257]

```
示例：VF BAR0 配置为 64-bit Memory，4KB 大小
偏移 0x24: 0xFFFFF00C (低 32 位，64-bit + Prefetchable)
偏移 0x28: 0xFFFFFFFF (高 32 位)

每个 VF 获得的独立 BAR 地址：
VF0 BAR0: 0xF0000000 (4KB)
VF1 BAR0: 0xF0001000 (4KB)
VF2 BAR0: 0xF0002000 (4KB)
```

硬件负责在每个 VF 的配置空间中自动映射其 BAR 地址范围，确保不同 VF 之间的内存空间相互隔离。 ^[pcie-sriov.md:252-257]

### 页大小配置

Supported Page Sizes (偏移 0x1C) 和 System Page Size (偏移 0x20) 用于配置 VF 的 IOMMU 页表映射。Supported Page Sizes 是一个位掩码，标识设备支持的所有页大小选项；System Page Size 则由系统软件设置，指定实际使用的页大小。 ^[pcie-sriov.md:182-183]

## 与 VF 配置空间的对比

VF 的配置空间相对于 PF 大幅简化，这是 SR-IOV 设计的核心原则之一。VF 不需要完整的 SR-IOV Capability 结构，而是共享 PF 管理的资源： ^[pcie-sriov.md:68-80]

| 特性 | PF | VF |
|------|----|----|
| 完整配置空间 | ✓ | ✗ (简化) |
| SR-IOV 能力 | ✓ | ✗ |
| MSI-X 中断 | ✓ | ✓ |
| DMA 能力 | ✓ | ✓ |
| 独立 BARs | ✓ | ✓ (通过 PF 配置) |
| 数量 | 1 | 多个 (最多 256) |
| 用途 | 管理 | 数据传输 |

VF 保留了标准 PCI Header 的核心部分，可以响应配置读取和写入操作，但配置空间的深度和功能数量都显著减少。 ^[pcie-sriov.md:68-80]

## 配置空间访问流程

在 Linux 系统中，SR-IOV 配置空间的访问通常由 PCI 子系统自动处理。驱动程序首先通过 `pci_find_ext_capability()` 函数查找 SR-IOV Extended Capability 的位置，然后使用标准 PCI 配置访问函数读取或写入各寄存器。 ^[pcie-sriov.md:282-304]

启用 VF 的典型流程包括：查找 SR-IOV Capability、读取 Total VFs 获取可用数量、配置 VF BARs 和页大小、写入 Num VFs 指定要启用的数量、最后设置 VF Enable 控制位。整个过程中，硬件会自动分配 VF 的 BDF 地址并配置 BAR 映射。 ^[pcie-sriov.md:307-329]

## 相关概念

- [PCIe 配置空间](/concepts/pcie-配置空间.md) - 了解标准配置空间和扩展配置空间的基础知识
- BDF 地址 - SR-IOV 中 VF 地址分配的具体机制
- BAR 配置 - VF BARs 的详细配置方法
- MSI-X 中断 - VF 使用的中断机制
- VFIO - 将 VF 分配给虚拟机的推荐方法

---

## Sources

- [SR-IOV 虚拟化详解 (pcie-sriov.md)](pcie-sriov.md)

# Citations

1. [pcie-sriov.md:141-159](/references/pcie-sriov-08f3fcbf.md)
2. [pcie-sriov.md:145-159](/references/pcie-sriov-08f3fcbf.md)
3. [pcie-sriov.md:158-159](/references/pcie-sriov-08f3fcbf.md)
4. [pcie-sriov.md:161-186](/references/pcie-sriov-08f3fcbf.md)
5. [pcie-sriov.md:190-201](/references/pcie-sriov-08f3fcbf.md)
6. [pcie-sriov.md:203-218](/references/pcie-sriov-08f3fcbf.md)
7. [pcie-sriov.md:220-234](/references/pcie-sriov-08f3fcbf.md)
8. [pcie-sriov.md:236-257](/references/pcie-sriov-08f3fcbf.md)
9. [pcie-sriov.md:252-257](/references/pcie-sriov-08f3fcbf.md)
10. [pcie-sriov.md:182-183](/references/pcie-sriov-08f3fcbf.md)
11. [pcie-sriov.md:68-80](/references/pcie-sriov-08f3fcbf.md)
12. [pcie-sriov.md:282-304](/references/pcie-sriov-08f3fcbf.md)
13. [pcie-sriov.md:307-329](/references/pcie-sriov-08f3fcbf.md)
