---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 7fa54d76e5c13fd1c1a587f7c0fccc933d382a814180cb085f0f10c23eceaf6d
  pageDirectory: concepts
  sources:
    - pcie-implementation-analysis.md
  confidence: 0.9
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - sr-iov-单根-io-虚拟化
    - S单I虚
  citations:
    - file: pcie-implementation-analysis.md
      start: 236
      end: 237
    - file: pcie-implementation-analysis.md
      start: 238
      end: 239
    - file: pcie-implementation-analysis.md
      start: 242
      end: 243
title: SR-IOV 单根 IO 虚拟化
description: 允许单个物理设备通过 PF 和 VF 机制虚拟为多个独立虚拟功能，支持高效硬件虚拟化
tags:
  - 虚拟化
  - 硬件加速
  - IO虚拟化
timestamp: "2026-08-16T06:38:37.096Z"
---

# SR-IOV 单根 IO 虚拟化

**SR-IOV**（Single Root I/O Virtualization，单根 IO 虚拟化）是一种硬件辅助的 PCIe 设备虚拟化技术，允许单个物理设备向虚拟机提供多个独立的虚拟功能（Virtual Function，VF），从而实现高性能的 IO 虚拟化。

## 工作原理

SR-IOV 的核心思想是将一个物理 PCIe 设备拆分为多个虚拟功能。在这一架构中，存在两种关键组件：

- **PF（Physical Function，物理功能）**：这是设备的完整物理功能，拥有完整的 PCIe 设备能力。PF 负责管理所有 VF 的配置和资源分配，并可以作为普通 PCIe 设备被主机系统识别和管理。 ^[pcie-implementation-analysis.md:236-237]
- **VF（Virtual Function，虚拟功能）**：每个 VF 是 PF 的轻量级虚拟化副本，拥有独立的配置空间和 BARs（基地址寄存器）。VF 允许虚拟机直接访问硬件资源，无需hypervisor 介入 IO 数据路径，从而显著降低虚拟化开销。 ^[pcie-implementation-analysis.md:238-239]

当启用 SR-IOV 时，物理设备会被实例化为一个 PF 和多个 VF，每个 VF 都有自己独立的 PCIe 配置空间。这使得每个 VF 看起来像是连接到 PCIe 总线上的一个独立设备，虚拟机可以直接识别和使用这些虚拟设备。

## 在 FEMU 中的实现

FEMU（基于 QEMU 的 NVMe 模拟器）提供了 SR-IOV 的完整软件实现，用于研究和开发目的。实现位于 `/hw/pci/pcie_sriov.c` 文件中，包含了两个核心函数：

- `pcie_sriov_pf_init()`：用于初始化物理功能
- `pcie_sriov_vf_register()`：用于注册虚拟功能 ^[pcie-implementation-analysis.md:242-243]

这种代码实现展示了如何将 SR-IOV 规范中的概念映射到实际的软件架构中，为开发者理解 SR-IOV 的内部工作机制提供了有价值的参考。

## 技术优势

SR-IOV 为虚拟化环境带来了显著的性能提升和资源效率。由于 VF 可以被虚拟机直接访问，数据包可以直接在虚拟机和物理设备之间传输，无需经过软件模拟层。这消除了传统 virtio 或 emulated device 方案中的拷贝和上下文切换开销，使得虚拟机能够接近原生设备的性能水平。

此外，SR-IOV 还简化了虚拟机的资源管理。管理员可以为不同的虚拟机分配不同数量的 VF，根据工作负载需求灵活调整资源配额，同时保持硬件级别的隔离性和安全性。

## 常见应用场景

SR-IOV 广泛部署在以下场景中：

- **网络虚拟化**：SR-IOV NIC（网卡）允许虚拟机直接使用物理网卡的 VF，实现近乎原生的网络性能
- **存储虚拟化**：NVMe 设备支持 SR-IOV，使虚拟机能够直接访问 NVMe SSD 的性能
- **GPU 虚拟化**：部分高端 GPU 支持 SR-IOV，可为多个虚拟机提供 GPU 计算资源

## 相关概念

SR-IOV 与多个相关技术紧密关联：

- PCI Express — SR-IOV 构建的基础总线标准
- 配置空间 — VF 拥有独立的配置空间
- BAR — VF 使用独立的基地址寄存器进行地址映射
- 事务层包 (TLP) — VF 与主机之间的数据传输单元
- MSI-X — VF 常用的中断机制

## 术语表

| 术语 | 全称 | 说明 |
|------|------|------|
| SR-IOV | Single Root I/O Virtualization | 单根 IO 虚拟化标准 |
| PF | Physical Function | 物理功能，设备的完整功能实体 |
| VF | Virtual Function | 虚拟功能，PF 的轻量级虚拟化副本 |

---

## Sources

- pcie-implementation-analysis.md:232-243 (SR-IOV 章节)
- pcie-implementation-analysis.md:389 (术语表 SR-IOV 条目)
- pcie-implementation-analysis.md:398-399 (术语表 VF/PF 条目)

# Citations

1. [pcie-implementation-analysis.md:236-237](/references/pcie-implementation-analysis-7e110edb.md)
2. [pcie-implementation-analysis.md:238-239](/references/pcie-implementation-analysis-7e110edb.md)
3. [pcie-implementation-analysis.md:242-243](/references/pcie-implementation-analysis-7e110edb.md)
