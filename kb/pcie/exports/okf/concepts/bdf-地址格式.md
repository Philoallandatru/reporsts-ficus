---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 1c182afaa8f8743f8883e0637e97ac5e658df724a33b9b380538b8063ae97779
  pageDirectory: concepts
  sources:
    - pcie-topology.md
  confidence: 1
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - bdf-地址格式
  citations:
    - file: pcie-topology.md
      start: 259
      end: 262
title: BDF 地址格式
description: PCIe 设备的唯一标识格式 Bus:Device.Function，用于在系统中定位和访问特定设备
tags:
  - pcie
  - addressing
  - identifier
timestamp: "2026-08-16T06:50:23.283Z"
---

# BDF 地址格式

BDF（Bus:Device.Function）地址格式是 PCIe 系统中用于唯一标识设备的核心编址方案。每个 PCIe 设备在系统中都拥有一个唯一的 BDF 地址。

---

## 概述

BDF 地址由三个部分组成，采用 `Bus:Device.Function` 的格式表示。这种地址格式直接对应 PCIe 配置空间中设备的位置信息，是系统识别和访问 PCIe 设备的基础。

---

## 地址组成

### Bus（总线号）

- **范围**：0-255（8 位）
- **含义**：标识设备所属的 PCIe 总线段
- **Root Complex** 负责管理所有总线号的分配

### Device（设备号）

- **范围**：0-31（5 位）
- **含义**：标识同一总线上的具体设备
- **每条总线**最多可容纳 32 个设备

### Function（功能号）

- **范围**：0-7（3 位）
- **含义**：标识同一设备内的不同功能单元
- **每个设备**最多支持 8 个功能

---

## 格式规范

标准 BDF 地址格式为：

```
Bus:Device.Function
```

- 每部分使用十六进制表示
- 三个部分之间用冒号（:）或点（.）分隔
- 常见写法：`01:00.0` 或 `0000:01:00.0`（带域前缀）

---

## 常见示例

根据 PCIe 拓扑中的设备枚举，BDF 地址具有如下典型示例：

| 设备类型 | BDF 地址 |
|---------|----------|
| GPU | `01:00.0` |
| NVMe SSD | `03:00.0` |
| 网卡 | `04:00.0` |

^[pcie-topology.md:259-262]

---

## BDF 与设备枚举

系统启动时，BIOS/UEFI 通过 PCIe 枚举过程为每个发现设备分配 BDF 地址。枚举过程从 Root Complex 的总线 0 开始递归扫描，为每个活动的链路分配唯一的总线号，并记录其下的设备与功能。

有关详细的枚举流程，请参阅 [PCIe 拓扑结构](/concepts/pcie-拓扑结构.md) 页面。

---

## 查看 BDF 地址

### Linux: lspci

```bash
# 树形视图（显示拓扑和 BDF）
$ lspci -tv

# 查看指定设备的详细信息
$ lspci -vvv -s 01:00.0
```

### Windows

- **设备管理器** → 选择设备 → 查看"位置路径"
- **资源管理器** 或 **devmgmt.msc** 中的设备属性

---

## 扩展概念

### ARI 模式

在启用 ARI（Alternative Routing-ID Interpretation）时，功能号范围可扩展至 0-255，允许单设备拥有最多 256 个功能。

### 域前缀

在 Linux 中，完整路径会包含 PCI 域（Domain），格式为 `DDDD:BB:DD.F`：

```
$ lspci -nn
0000:01:00.0 VGA compatible controller [0300]: NVIDIA Corporation [10DE:1B80]
```

---

## 与其他地址的关系

| 地址类型 | 用途 |
|---------|------|
| **BDF** | 设备标识与配置访问 |
| **BAR** | 内存/IO 空间映射 |
| **路由 ID** | TLP 事务转发 |

BDF 地址是访问设备 [PCIe 配置空间](/concepts/pcie-配置空间.md) 的入口，通过 `Bus:Device.Function` 组合可以定位到特定设备的配置头。

---

## Sources

- PCIe 拓扑结构](pcie-topology.md)

---

**相关页面**：
- [PCIe 拓扑结构](/concepts/pcie-拓扑结构.md)
- [PCIe 配置空间](/concepts/pcie-配置空间.md)
- 设备枚举

# Citations

1. [pcie-topology.md:259-262](/references/pcie-topology-477a9e9e.md)
