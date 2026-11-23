---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: ae6fa87ba38127b096f11df8637d48ae542c2ba967c68ab56dc9b368db977a67
  pageDirectory: concepts
  sources:
    - pcie-sriov.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - sr-iov-概述
  citations:
    - file: pcie-sriov.md
      start: 3
      end: 3
    - file: pcie-sriov.md
      start: 9
      end: 9
    - file: pcie-sriov.md
      start: 26
      end: 30
    - file: pcie-sriov.md
      start: 48
      end: 51
    - file: pcie-sriov.md
      start: 56
      end: 60
    - file: pcie-sriov.md
      start: 62
      end: 66
    - file: pcie-sriov.md
      start: 69
      end: 80
    - file: pcie-sriov.md
      start: 84
      end: 117
    - file: pcie-sriov.md
      start: 121
      end: 137
    - file: pcie-sriov.md
      start: 141
      end: 186
    - file: pcie-sriov.md
      start: 263
      end: 329
    - file: pcie-sriov.md
      start: 334
      end: 352
    - file: pcie-sriov.md
      start: 358
      end: 376
    - file: pcie-sriov.md
      start: 397
      end: 410
    - file: pcie-sriov.md
      start: 557
      end: 569
    - file: pcie-sriov.md
      start: 608
      end: 621
    - file: pcie-sriov.md
      start: 653
      end: 665
title: SR-IOV 概述
description: Single Root I/O Virtualization 是 PCIe 规范的硬件虚拟化扩展，允许单个物理设备虚拟为多个独立 Virtual Function 直接分配给虚拟机
tags:
  - pcie
  - 虚拟化
  - 硬件虚拟化
timestamp: "2026-08-16T06:46:45.505Z"
---


# SR-IOV 概述

Single Root I/O Virtualization (SR-IOV) 是 PCIe 规范中的关键虚拟化特性，允许单个物理设备虚拟为多个独立的虚拟设备，直接分配给虚拟机使用，从而实现接近原生性能的 I/O 虚拟化解决方案。 ^[pcie-sriov.md:3, pcie-sriov.md:9]

## 为什么需要 SR-IOV？

传统 I/O 虚拟化采用软件模拟方式，所有虚拟机的 I/O 流量都必须经过 Hypervisor 层进行转发和处理。这种方式存在以下问题：

- 所有 I/O 必须经过 Hypervisor，导致频繁的上下文切换
- CPU 占用率较高
- 延迟高、吞吐量低 ^[pcie-sriov.md:26-30]

SR-IOV 通过硬件级虚拟化解决了这些性能瓶颈。虚拟机可以直接访问分配给它的虚拟设备，绕过 Hypervisor 的软件转发层，从而实现接近原生性能 (Near-native Performance) 的 I/O 访问。 ^[pcie-sriov.md:48-51]

## 核心概念

### [Physical Function (PF)](/concepts/physical-function-pf.md)

Physical Function 是完整的 PCIe 功能单元，具有以下特性：

- 拥有完整的 [PCIe 配置空间](/concepts/pcie-配置空间.md)
- 包含 SR-IOV 扩展能力
- 负责管理和配置 Virtual Functions
- 通常由 Hypervisor 控制 ^[pcie-sriov.md:56-60]

### [Virtual Function (VF)](/concepts/virtual-function-vf.md)

Virtual Function 是轻量级的 PCIe 功能单元，具有以下特点：

- 采用简化的配置空间设计
- 专注于数据路径传输
- 共享 PF 的硬件资源
- 可直接分配给单个虚拟机使用 ^[pcie-sriov.md:62-66]

### PF 与 VF 对比

| 特性 | PF | VF |
|------|-----|-----|
| 完整配置空间 | ✓ | ✗ (简化) |
| SR-IOV 能力 | ✓ | ✗ |
| MSI-X 中断 | ✓ | ✓ |
| DMA 能力 | ✓ | ✓ |
| 独立 BARs | ✓ | ✓ |
| 数量 | 1 | 多个 (最多 256) |
| 用途 | 管理 | 数据传输 |

^[pcie-sriov.md:69-80]

## 架构

### 拓扑结构

在 SR-IOV 架构中，物理设备包含一个 PF，多个 VF 共享 PF 的物理资源。每个 VF 拥有独立的 BARs 地址空间和 MSI-X 中断能力，可被直接分配给不同的虚拟机使用。 ^[pcie-sriov.md:84-117]

### BDF 地址分配

SR-IOV 设备使用特殊的 BDF (Bus:Device.Function) 地址方案：

- PF 地址通常为如 `01:00.0`
- VF 地址在 PF 基础上连续分配，如 `01:00.1`、`01:00.2` 等
- 每个设备最多 8 个 Function，超出后进位到下一个 Device 号 ^[pcie-sriov.md:121-137]

## 配置空间

### SR-IOV Extended Capability

SR-IOV Extended Capability 结构位于扩展配置空间 (0x100+)，包含以下关键寄存器： ^[pcie-sriov.md:141-186]

| 寄存器 | 功能 |
|--------|------|
| Initial VFs | 设备支持的最大 VF 数量（硬件固定值） |
| Total VFs | 当前可用的 VF 数量 |
| Num VFs | 当前启用的 VF 数量（可软件配置） |
| First VF Offset | 第一个 VF 相对于 PF 的偏移 |
| VF Stride | 相邻 VF 之间的步长 |
| VF Device ID | VF 的专用设备标识符 |

### 启用 VF

启用 VF 的基本流程如下：

1. **检测支持**：通过 `lspci -vvv` 检查设备是否支持 SR-IOV
2. **配置 Num VFs**：向 SR-IOV 控制寄存器写入要启用的 VF 数量
3. **设置 VF Enable 位**：在 SR-IOV Control Register 中设置 VFE 位
4. **等待 VF 就绪**：硬件完成 VF 资源分配后即可使用 ^[pcie-sriov.md:263-329]

Linux 系统可通过 sysfs 接口管理 VF：

```bash
# 查看支持的 VF 数量
cat /sys/bus/pci/devices/0000:01:00.0/sriov_totalvfs

# 启用 8 个 VF
echo 8 > /sys/bus/pci/devices/0000:01:00.0/sriov_numvfs
```

^[pcie-sriov.md:334-352]

## 虚拟机分配

### VFIO 方式

VFIO (Virtual Function I/O) 是 Linux 推荐的设备直通框架，可将 VF 安全地分配给虚拟机： ^[pcie-sriov.md:358-376]

1. 将 VF 绑定到 vfio-pci 驱动
2. 在 QEMU/KVM 中使用 `vfio-pci` 设备模型
3. 虚拟机内部可使用标准驱动程序

### 虚拟机内部视图

分配给虚拟机后，VF 对虚拟机来说就像真实的物理设备。虚拟机可以使用标准的设备驱动，无需特殊的虚拟化支持。 ^[pcie-sriov.md:397-410]

## 性能与安全

### 性能优化

选择合适的 VF 数量需要考虑以下因素：

- CPU 核心数（每个 VF 需要 CPU 资源）
- 内存带宽（每个 VF 需要 DMA 通道）
- 设备硬件队列数量
- 虚拟机的实际需求 ^[pcie-sriov.md:557-569]

### 安全隔离

SR-IOV 提供的隔离包括：

- **DMA 隔离**：通过 IOMMU 实现
- **中断隔离**：基于 MSI-X 机制
- **配置空间隔离**：VF 拥有独立的配置空间

但需要注意，SR-IOV 不提供物理链路的带宽隔离，也不包含针对侧信道攻击的防护措施。 ^[pcie-sriov.md:608-621]

## 适用场景

**适合使用 SR-IOV**：

- 高性能网络应用 (NFV, SDN)
- GPU 虚拟化 (vGPU)
- 存储虚拟化 (NVMe)
- HPC 集群

**不适合使用 SR-IOV**：

- 虚拟机需要频繁迁移的场景
- 需要细粒度 QoS 控制的环境
- 设备不支持 SR-IOV 的情况
- 成本敏感场景 ^[pcie-sriov.md:653-665]

## 相关技术

- PCIe — SR-IOV 的基础协议
- VFIO — 设备直通的推荐框架
- BARs — VF 的地址空间映射
- MSI-X — VF 的中断机制
- IOMMU — DMA 和内存隔离的基础

---

## Sources

- [SR-IOV 虚拟化详解 (pcie-sriov.md)](pcie-sriov.md)

# Citations

1. [pcie-sriov.md:3-3](/references/pcie-sriov-08f3fcbf.md)
2. [pcie-sriov.md:9-9](/references/pcie-sriov-08f3fcbf.md)
3. [pcie-sriov.md:26-30](/references/pcie-sriov-08f3fcbf.md)
4. [pcie-sriov.md:48-51](/references/pcie-sriov-08f3fcbf.md)
5. [pcie-sriov.md:56-60](/references/pcie-sriov-08f3fcbf.md)
6. [pcie-sriov.md:62-66](/references/pcie-sriov-08f3fcbf.md)
7. [pcie-sriov.md:69-80](/references/pcie-sriov-08f3fcbf.md)
8. [pcie-sriov.md:84-117](/references/pcie-sriov-08f3fcbf.md)
9. [pcie-sriov.md:121-137](/references/pcie-sriov-08f3fcbf.md)
10. [pcie-sriov.md:141-186](/references/pcie-sriov-08f3fcbf.md)
11. [pcie-sriov.md:263-329](/references/pcie-sriov-08f3fcbf.md)
12. [pcie-sriov.md:334-352](/references/pcie-sriov-08f3fcbf.md)
13. [pcie-sriov.md:358-376](/references/pcie-sriov-08f3fcbf.md)
14. [pcie-sriov.md:397-410](/references/pcie-sriov-08f3fcbf.md)
15. [pcie-sriov.md:557-569](/references/pcie-sriov-08f3fcbf.md)
16. [pcie-sriov.md:608-621](/references/pcie-sriov-08f3fcbf.md)
17. [pcie-sriov.md:653-665](/references/pcie-sriov-08f3fcbf.md)
