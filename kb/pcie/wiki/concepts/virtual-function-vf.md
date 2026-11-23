---
title: Virtual Function (VF)
summary: 轻量级 PCIe 功能，专注于数据传输路径，共享 PF 资源，可直接分配给虚拟机使用
sources:
- pcie-sriov.md
kind: concept
createdAt: '2026-08-16T06:47:14.151Z'
updatedAt: '2026-08-16T06:47:14.151Z'
tags:
- pcie
- sriov
- 虚拟化
aliases:
- virtual-function-vf
- VF(
confidence: 0.95
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: VF 作为轻量级的 PCIe 功能，具有以下核心特性：
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 虚拟功能（Virtual Function，VF）

## 概述

**虚拟功能（Virtual Function，VF）** 是 SR-IOV（Single Root I/O Virtualization）架构中的轻量级 PCIe 功能组件。VF 由物理功能（PF）创建并共享 PF 的硬件资源，专注于数据路径传输而非管理控制。在虚拟化环境中，VF 可以直接分配给虚拟机使用，使虚拟机能够以接近原生设备的性能访问硬件资源。^[pcie-sriov.md:62-66]

## 核心特性

VF 作为轻量级的 PCIe 功能，具有以下核心特性：

- **专注于数据路径**：VF 主要承担数据传输功能，不参与设备管理和配置控制 ^[pcie-sriov.md:63-64]
- **共享 PF 资源**：多个 VF 共享同一个 PF 的硬件资源，包括物理链路和底层硬件队列 ^[pcie-sriov.md:65]
- **直接分配给 VM**：VF 可以直接分配给虚拟机，虚拟机内的操作系统和驱动程序将其视为真实物理设备 ^[pcie-sriov.md:66]
- **支持 MSI-X 中断**：VF 具备独立的 MSI-X 中断能力，可实现高效的中断处理 ^[pcie-sriov.md:75]
- **具备 DMA 能力**：VF 支持直接内存访问（DMA），可独立进行内存读写操作 ^[pcie-sriov.md:76]
- **拥有独立 BARs**：每个 VF 都分配有独立的 BAR（Base Address Register）地址空间用于内存映射 ^[pcie-sriov.md:77, pcie-sriov.md:252-256]

## VF 与 PF 对比

VF 与 PF 在功能和职责上存在显著差异 ^[pcie-sriov.md:69-80]：

| 特性 | PF | VF |
|------|----|----|
| 完整配置空间 | ✓ | ✗（简化） |
| SR-IOV 能力 | ✓ | ✗ |
| MSI-X 中断 | ✓ | ✓ |
| DMA 能力 | ✓ | ✓ |
| 独立 BARs | ✓ | ✓ |
| 数量 | 1 | 多个（最多 256） |
| 用途 | 管理 | 数据传输 |

PF 是完整的 PCIe 功能，包含了 SR-IOV 扩展能力，用于管理和配置 VF；而 VF 是简化版本，移除了 SR-IOV 相关能力，专注于高效的数据传输 ^[pcie-sriov.md:56-66]。

## VF 寻址机制

### BDF 地址分配

VF 使用特殊的 BDF（Bus:Device.Function）地址方案进行分配 ^[pcie-sriov.md:119-137]：

```
VF 地址分配示例：
VF0: Bus 1, Device 0, Function 1 → 01:00.1
VF1: Bus 1, Device 0, Function 2 → 01:00.2
VF2: Bus 1, Device 0, Function 3 → 01:00.3
...
VF7: Bus 1, Device 1, Function 0 → 01:01.0 (跨设备号)
```

VF 的 BDF 地址通过以下规则计算 ^[pcie-sriov.md:232-234]：

```
VF[i] BDF = PF BDF + First VF Offset + (i × VF Stride)
```

其中 First VF Offset 表示第一个 VF 相对于 PF 的 Routing ID 偏移，VF Stride 表示相邻 VF 之间的 Routing ID 步长，通常为 1。每个 PCIe 设备最多支持 8 个 Function，超过后进位到下一个 Device 号 ^[pcie-sriov.md:134-136]。

## VF BAR 配置

### VF BARs 结构

VF BARs 与普通 BARs 类似，但其配置信息存储在 PF 的 SR-IOV Extended Capability 结构中 ^[pcie-sriov.md:236-257]：

```
VF BAR 配置（每个 BAR 占 4 字节）：
VF BAR0 (偏移 0x24): VF 的第一个 BAR
VF BAR1 (偏移 0x28): VF 的第二个 BAR
...
VF BAR5 (偏移 0x38): VF 的第六个 BAR
```

### BAR 地址分配示例

每个 VF 都会获得独立的 BAR 地址空间 ^[pcie-sriov.md:252-256]：

```
VF0 BAR0: 0xF0000000 (4KB)
VF1 BAR0: 0xF0001000 (4KB)
VF2 BAR0: 0xF0002000 (4KB)
...
```

## VF 启用流程

### 启用步骤

在 Linux 系统中，VF 的启用主要通过 sysfs 接口完成 ^[pcie-sriov.md:332-352]：

1. **查看支持的 VF 数量**：
   ```bash
   cat /sys/bus/pci/devices/0000:01:00.0/sriov_totalvfs
   ```

2. **启用指定数量的 VF**：
   ```bash
   echo 8 > /sys/bus/pci/devices/0000:01:00.0/sriov_numvfs
   ```

3. **验证 VF 已创建**：
   ```bash
   lspci | grep "Virtual Function"
   ```

4. **禁用 VF**：
   ```bash
   echo 0 > /sys/bus/pci/devices/0000:01:00.0/sriov_numvfs
   ```

### 驱动层面实现

从驱动代码角度，启用 VF 需要写入 SR-IOV 配置空间中的相关寄存器 ^[pcie-sriov.md:307-329]：

1. 向 `Num VFs` 寄存器写入目标 VF 数量
2. 设置 `VF Enable` 和 `VF MSE (Memory Space Enable)` 控制位
3. 等待 VF 就绪

## VF 分配给虚拟机

### [[vfio-设备直通|VFIO 设备直通]]

VFIO（Virtual Function I/O）是现代 Linux 推荐的 VF 分配方式，提供安全的设备直通能力 ^[pcie-sriov.md:358-376]：

1. 将 VF 绑定到 vfio-pci 驱动：
   ```bash
   echo 0000:01:00.1 > /sys/bus/pci/devices/0000:01:00.1/driver/unbind
   echo "8086 154c" > /sys/bus/pci/drivers/vfio-pci/new_id
   ```

2. 在 QEMU/KVM 中配置虚拟机使用 VF：
   ```bash
   qemu-system-x86_64 -device vfio-pci,host=01:00.1
   ```

### 虚拟机内部视图

分配给 VM 后，VF 对虚拟机操作系统表现为标准的 PCIe 设备 ^[pcie-sriov.md:398-410]：

```bash
# 在 VM 内部查看设备
lspci
00:05.0 Ethernet controller: Intel Virtual Function

# VF 像真实设备一样工作
ip link show
eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 ...
```

## 性能优化考量

### VF 数量选择

选择合适的 VF 数量需要综合考虑多种因素 ^[pcie-sriov.md:557-569]：

- **CPU 核心数**：每个 VF 需要 CPU 资源进行处理
- **内存带宽**：每个 VF 需要独立的 DMA 通道
- **设备硬件队列**：VF 数量不应超过硬件队列数
- **VM 实际需求**：根据工作负载合理分配

**建议配置**：
- 高性能场景：每个 VM 使用 1-2 个 VF
- 密集整合场景：每个 VM 使用 4-8 个 VF
- 避免过度分配：VF 数量不应超过物理资源容量

### 中断亲和性优化

可以将 VF 中断绑定到特定 CPU 核心，以实现与 VM vCPU 的对齐优化 ^[pcie-sriov.md:571-578]：

```bash
echo 2 > /proc/irq/125/smp_affinity_list  # 绑定到 CPU 2
```

## 安全考虑

SR-IOV 提供的安全隔离包括 DMA 隔离（通过 IOMMU）、中断隔离（通过 MSI-X）和配置空间隔离。然而，它不提供物理链路的隔离（存在带宽竞争），也不包含针对侧信道攻击的防护措施。 ^[pcie-sriov.md:608-621]

## 相关概念

- SR-IOV — VF 所基于的 PCIe 虚拟化技术框架
- [[Physical Function (PF)]] — 创建和管理 VF 的完整 PCIe 功能
- [[PCIe 配置空间]] — VF 配置信息的存储结构
- VFIO — 推荐用于 VF 设备直通的 Linux 框架
- MSI-X 中断 — VF 使用的中断机制
- BAR — VF 地址空间映射的基础寄存器

## 总结

虚拟功能（VF）是 SR-IOV 架构中的核心组件，通过将单个物理设备虚拟为多个轻量级功能，实现了高性能的 I/O 虚拟化。VF 专注于数据路径传输，支持独立的 DMA 和中断能力，可以直接分配给虚拟机使用，使虚拟机获得接近原生设备的 I/O 性能。在实际部署中，需要根据物理资源容量合理规划 VF 数量，并通过 VFIO 等框架实现安全的设备直通。

---

## 参考资料

^[pcie-sriov.md]

