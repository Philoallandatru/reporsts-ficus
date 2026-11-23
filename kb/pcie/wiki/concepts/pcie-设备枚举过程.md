---
title: PCIe 设备枚举过程
summary: 系统启动时通过 BIOS/UEFI 自动发现 PCIe 设备的递归扫描过程，包括链路训练、配置读取、总线编号分配和 BAR 配置
sources:
- pcie-topology.md
kind: concept
createdAt: '2026-08-16T06:49:58.937Z'
updatedAt: '2026-08-16T06:49:58.937Z'
tags:
- pcie
- enumeration
- boot-process
aliases:
- pcie-设备枚举过程
confidence: 1
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: PCIe 设备枚举是指系统在启动时自动发现和识别所有 PCIe 设备的过程。该过程由 BIOS/UEFI 主导，遵循 PCIe 的[[PCIe
  树形拓扑结构|树形拓扑结构]]，从 Root Complex（根复合体）开始，逐层向下扫描，最终完成对所有设备的发现与配置。 ^[pcie-topology.md:200-205]
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCIe 设备枚举过程

## 概述

PCIe 设备枚举是指系统在启动时自动发现和识别所有 PCIe 设备的过程。该过程由 BIOS/UEFI 主导，遵循 PCIe 的[[PCIe 树形拓扑结构|树形拓扑结构]]，从 Root Complex（根复合体）开始，逐层向下扫描，最终完成对所有设备的发现与配置。 ^[pcie-topology.md:200-205]

## 枚举流程详解

### 1. 启动阶段

系统加电后，BIOS/UEFI 首先扫描 Root Complex 上的所有 Root Port（根端口）。每个 Root Port 代表一个独立的 PCIe 总线入口。 ^[pcie-topology.md:206-209]

### 2. 链路状态检查

对于每个 Root Port，系统首先检查物理链路是否已训练完成（Link Training）。如果链路尚未训练，则跳过该端口；如果链路已训练，则继续进行设备探测。 ^[pcie-topology.md:211-216]

### 3. 配置读取

系统通过发送 Configuration Read 请求来探测设备。对于已训练链路的每个可能的设备编号（0-31）和功能编号（0-7），系统尝试读取设备的 Vendor ID。 ^[pcie-topology.md:218-221]

- **无响应**：表示该位置无设备
- **有响应且 Vendor ID ≠ 0xFFFF**：发现有效设备

### 4. 读取设备信息

一旦发现设备，系统读取关键的配置信息，包括： ^[pcie-topology.md:223]

- **Vendor ID**：供应商标识
- **Device ID**：设备标识
- **Class Code**：设备类型（显卡、存储、网络等）

### 5. 总线编号分配

系统为新发现的总线分配总线编号（Bus Number），编号范围为 0-255（8 位）。每个 Bridge 或 Switch 下游端口都会分配一个新的总线编号。 ^[pcie-topology.md:225, pcie-topology.md:295-297]

### 6. BAR 配置

系统配置设备的 BAR（Base Address Register），为每个 BAR 分配内存或 I/O 地址空间，确保 CPU 能够访问设备的寄存器。 ^[pcie-topology.md:227-228]

### 7. 递归扫描

根据设备类型，枚举过程分为两种路径： ^[pcie-topology.md:230-234]

- **如果是 Bridge 或 PCIe Switch**：系统递归扫描该桥接设备下游的所有总线
- **如果是 Endpoint（端点设备）**：枚举完成，后续加载相应驱动程序

## 总线编号分配示例

典型的桌面系统中，总线编号分配如下： ^[pcie-topology.md:237-263]

```
Bus 0 (Root Bus)
 ├─ Device 0: Root Port 0
 │   └─ Bus 1
 │       └─ Device 0: GPU (Endpoint)
 │
 ├─ Device 1: Root Port 1
 │   └─ Bus 2
 │       └─ Device 0: Switch
 │           ├─ Bus 3 (下行端口 0)
 │           │   └─ Device 0: NVMe SSD
 │           │
 │           └─ Bus 4 (下行端口 1)
 │               └─ Device 0: Network Card
 │
 └─ Device 2: Root Port 2
     └─ Bus 5
         └─ Device 0: Wi-Fi Card
```

对应的 BDF（Bus:Device.Function）地址格式： ^[pcie-topology.md:259-262]

| 设备 | BDF 地址 |
|------|----------|
| GPU | 01:00.0 |
| NVMe SSD | 03:00.0 |
| Network Card | 04:00.0 |

## 枚举约束与限制

### 数量限制

- **每条总线**：最多 32 个设备
- **每个设备**：最多 8 个功能（Function 0-7）
- **ARI 模式**：支持最多 256 个功能（扩展编号方案）
- **总线编号**：0-255（8 位），实际深度通常不超过 5-7 层 ^[pcie-topology.md:299-302]

## 验证工具

### Linux: lspci

使用 `lspci -tv` 可以查看系统的 PCIe 树形拓扑结构： ^[pcie-topology.md:269-283]

```bash
$ lspci -tv

-[0000:00]-+-00.0  Intel Corporation Host Bridge
           +-01.0-[01]----00.0  NVIDIA Corporation GPU
           +-02.0-[02-04]----00.0  Switch Upstream Port
           |                 +-00.0-[03]----00.0  Samsung NVMe SSD
           |                 \-01.0-[04]----00.0  Intel 10GbE NIC
           \-03.0-[05]----00.0  Intel Wi-Fi Adapter
```

查看特定设备的详细信息： ^[pcie-topology.md:282]

```bash
$ lspci -vvv -s 01:00.0  # 查看 GPU 的详细配置
```

## 总结

PCIe 设备枚举是系统启动时的关键初始化过程，其核心要点包括： ^[pcie-topology.md:380-386]

1. **树形遍历**：从 Root Complex 出发，按树形结构逐层向下发现设备
2. **配置读取**：通过读取配置空间获取设备标识信息
3. **地址分配**：为每条总线分配唯一编号，为每个 BAR 分配地址空间
4. **递归处理**：Bridge 和 Switch 触发递归枚举，Endpoint 则完成枚举

枚举过程确保了操作系统能够准确识别系统中所有 PCIe 设备，并为后续驱动程序加载和资源分配奠定基础。

---

## Sources

- PCIe 拓扑结构](pcie-topology.md) - 设备枚举过程（第 200-263 行）

