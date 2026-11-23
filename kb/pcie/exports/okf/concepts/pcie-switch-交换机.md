---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 549067eaf5c9320ecf77945e8e2c50ef4a4b810a97c39a986d7911a444267d28
  pageDirectory: concepts
  sources:
    - pcie-topology.md
  confidence: 1
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - pcie-switch-交换机
    - PS交
  citations:
    - file: pcie-topology.md
      start: 48
      end: 48
    - file: pcie-topology.md
      start: 50
      end: 52
    - file: pcie-topology.md
      start: 54
      end: 67
    - file: pcie-topology.md
      start: 69
      end: 73
    - file: pcie-topology.md
      start: 328
      end: 335
    - file: pcie-topology.md
      start: 75
      end: 77
    - file: pcie-topology.md
      start: 155
      end: 178
    - file: pcie-topology.md
      start: 230
      end: 232
    - file: pcie-topology.md
      start: 247
      end: 252
    - file: pcie-topology.md
      start: 337
      end: 344
    - file: pcie-topology.md
      start: 343
      end: 344
    - file: pcie-topology.md
      start: 358
      end: 366
title: PCIe Switch 交换机
description: 扩展 PCIe 连接数量的桥接设备，具有上行端口和多个下行端口，支持透明和非透明两种工作模式
tags:
  - pcie
  - hardware
  - switch
timestamp: "2026-08-16T06:49:59.690Z"
---


# PCIe Switch 交换机

## 概述

PCIe Switch（交换机）是一种用于**扩展 PCIe 连接数量**的桥接设备。它是 PCIe [树形拓扑](/concepts/pcie-拓扑结构.md)中的关键组件，能够将一个上行端口扩展为多个下行端口，从而连接更多 Endpoint 设备。 ^[pcie-topology.md:48-48]

---

## 基本结构

PCIe Switch 由以下两部分组成：

### 上行端口（Upstream Port）

上行端口用于**连接 Root Complex 或上级 Switch**，负责接收来自上游的数据包并转发到相应的下行端口。 ^[pcie-topology.md:50-52]

### 下行端口（Downstream Port）

下行端口用于**连接下级设备或其他 Switch**，负责将来自上行端口的数据包转发到目标设备。Switch 通常提供多个下行端口，常见配置为 4 口、8 口或更多。 ^[pcie-topology.md:50-52]

```
            上行端口 (x8)
                ▲
                │
        ┌───────┴───────┐
        │    Switch     │
        │   (内部路由)   │
        └───┬───┬───┬───┘
            │   │   │
         下行端口 (x4 each)
            │   │   │
          设备 设备 设备
```

---

## 工作原理

Switch 的核心是一个**内部路由器**，负责根据数据包的目标地址将其从上行端口转发到正确的下行端口，或从下行端口转发到上行端口或其他下行端口。这种内部路由机制使得 Switch 能够高效地管理多个设备之间的通信。 ^[pcie-topology.md:54-67]

---

## Lane 分配

Switch 的各个端口可以配置不同的 Lane 宽度，实际带宽取决于端口配置。以下是一个典型的 Lane 分配示例： ^[pcie-topology.md:69-73]

| 端口类型 | Lane 宽度 | 连接设备 |
|---------|----------|---------|
| 上行链路 | x8 | 连接到 Root Complex |
| 下行链路 1 | x4 | 显卡 |
| 下行链路 2 | x2 | NVMe SSD |
| 下行链路 3 | x2 | 网卡 |

需要注意的是，如果 Switch 的上行链路带宽小于所有下行链路带宽之和，在多个设备同时传输数据时会出现**带宽竞争**的情况。 ^[pcie-topology.md:328-335]

---

## 透明与非透明 Switch

### 透明 Switch

透明 Switch（Transparent Switch）是标准工作模式，**下游设备对软件完全可见**。系统可以直接枚举和管理所有连接的设备，无需特殊配置。 ^[pcie-topology.md:75-77]

### 非透明 Switch（NTB）

非透明桥接（Non-Transparent Bridge, NTB）是一种特殊模式，用于**隔离不同的地址空间**，常见于多主机系统。NTB 允许不同主机系统通过 Switch 进行通信，同时保持各自的地址空间独立性。 ^[pcie-topology.md:75-77]

---

## 在拓扑中的位置

在典型的服务器系统中，Switch 通常位于 Root Complex 和多个 Endpoint 之间。以下是一个带 Switch 的服务器拓扑示例： ^[pcie-topology.md:155-178]

```
                ┌────────────────────────────┐
                │          CPU               │
                │  ┌───────────────────────┐ │
                │  │   Root Complex        │ │
                │  └───┬───────────┬───────┘ │
                └──────┼───────────┼─────────┘
                       │ x16       │ x8
                       │           │
           ┌────────────▼──┐   ┌───▼──────────────┐
           │     GPU       │   │   PCIe Switch    │
           │  (Endpoint)   │   │  ┌────────────┐  │
           └───────────────┘   │  │  Internal  │  │
                               │  │   Router   │  │
                               │  └─┬──┬──┬──┬─┘  │
                               └────┼──┼──┼──┼────┘
                                    │  │  │  │
                       ┌────────────┘  │  │  └──────────┐
                       │               │  │             │
                   ┌───▼───┐      ┌───▼──▼───┐    ┌───▼────┐
                   │ NVMe  │      │  NVMe    │    │ 10GbE  │
                   │  SSD  │      │   SSD    │    │  NIC   │
                   └───────┘      └──────────┘    └────────┘
```

---

## 设备枚举

在系统启动时的 PCIe 枚举过程中，Switch 作为 **Type 1 设备**（桥接设备）被识别和配置。枚举过程大致如下： ^[pcie-topology.md:230-232]

1. BIOS/UEFI 扫描 Root Complex 的所有 Root Port
2. 对每个已训练链路的 Port 发送 Configuration Read 请求
3. 如果发现 Switch（识别为桥接设备），读取其总线编号配置
4. **递归扫描下游总线**，为 Switch 的每个下行端口分配独立的总线号
5. 继续枚举 Switch 下游连接的所有设备

总线编号分配示例： ^[pcie-topology.md:247-252]

```
Bus 0 (Root Bus)
  ├─ Device 1: Root Port 1
  │   └─ Bus 2
  │       └─ Device 0: Switch
  │           ├─ Bus 3 (下行端口 0)
  │           │   └─ Device 0: NVMe SSD
  │           │
  │           └─ Bus 4 (下行端口 1)
  │               └─ Device 0: Network Card
```

---

## P2P 通信

同一 Switch 下的设备支持 **P2P（点对点）通信**，即设备之间可以直接交换数据而无需经过 Root Complex。这种通信方式可以降低延迟并减少 Root Complex 的带宽压力。 ^[pcie-topology.md:337-344]

实现 P2P 通信需要 **ACS（Access Control Services）** 的支持，该特性允许软件配置哪些设备可以相互通信。 ^[pcie-topology.md:337-344]

对于不同 Switch 下的设备，通信必须经过共同的父节点（通常是 Root Complex）。 ^[pcie-topology.md:343-344]

---

## 软件模拟

在 FEMU/QEMU 等仿真平台中，Switch 的模拟涉及多个组件： ^[pcie-topology.md:358-366]

```c
// 创建 Switch 上行端口
pcie_switch_upstream_port_realize(...);

// 创建 Switch 下行端口
pcie_switch_downstream_port_realize(...);
```

这些函数分别创建 Switch 的上行端口和下行端口模拟对象，构成了完整的 Switch 设备模型。

---

## 总结

PCIe Switch 是构建复杂 PCIe 系统拓扑的关键组件，其核心要点包括：

- **扩展连接**：将单一 PCIe 链路扩展为多条下行链路
- **内部路由**：通过内部路由器高效转发数据包
- **灵活配置**：支持不同的 Lane 分配和端口配置
- **地址隔离**：非透明 Switch 可实现地址空间隔离
- **P2P 支持**：同一 Switch 下的设备可进行点对点通信

---

## 相关概念

- [PCIe 拓扑结构](/concepts/pcie-拓扑结构.md) - Switch 在整体拓扑中的位置
- Root Complex - Switch 的上游连接对象
- Endpoint - Switch 的下游连接对象
- [配置空间](/concepts/pcie-配置空间.md) - Switch 的配置头结构

---

## Sources

- PCIe 拓扑结构](pcie-topology.md)

# Citations

1. [pcie-topology.md:48-48](/references/pcie-topology-477a9e9e.md)
2. [pcie-topology.md:50-52](/references/pcie-topology-477a9e9e.md)
3. [pcie-topology.md:54-67](/references/pcie-topology-477a9e9e.md)
4. [pcie-topology.md:69-73](/references/pcie-topology-477a9e9e.md)
5. [pcie-topology.md:328-335](/references/pcie-topology-477a9e9e.md)
6. [pcie-topology.md:75-77](/references/pcie-topology-477a9e9e.md)
7. [pcie-topology.md:155-178](/references/pcie-topology-477a9e9e.md)
8. [pcie-topology.md:230-232](/references/pcie-topology-477a9e9e.md)
9. [pcie-topology.md:247-252](/references/pcie-topology-477a9e9e.md)
10. [pcie-topology.md:337-344](/references/pcie-topology-477a9e9e.md)
11. [pcie-topology.md:343-344](/references/pcie-topology-477a9e9e.md)
12. [pcie-topology.md:358-366](/references/pcie-topology-477a9e9e.md)
