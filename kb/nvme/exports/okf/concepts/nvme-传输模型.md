---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: b25d653c4fb9b04610ae52383ba60a5dc213099414257a3d13def221c994825f
  pageDirectory: concepts
  sources:
    - nvme-transport-models.md
  confidence: 1
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - nvme-传输模型
  citations:
    - file: nvme-transport-models.md
      start: 5
      end: 7
    - file: nvme-transport-models.md
      start: 11
      end: 16
    - file: nvme-transport-models.md
      start: 27
      end: 31
    - file: nvme-transport-models.md
      start: 42
      end: 44
    - file: nvme-transport-models.md
      start: 48
      end: 79
    - file: nvme-transport-models.md
      start: 93
      end: 104
    - file: nvme-transport-models.md
      start: 158
      end: 167
    - file: nvme-transport-models.md
      start: 169
      end: 178
    - file: nvme-transport-models.md
      start: 180
      end: 184
    - file: nvme-transport-models.md
      start: 108
      end: 113
    - file: nvme-transport-models.md
      start: 114
      end: 122
    - file: nvme-transport-models.md
      start: 125
      end: 133
    - file: nvme-transport-models.md
      start: 187
      end: 208
    - file: nvme-transport-models.md
      start: 210
      end: 218
title: NVMe 传输模型
description: NVMe 规范定义的两种基本通信模型：基于内存的传输和基于消息的传输，分别适用于本地 PCIe 连接和网络存储场景
tags:
  - nvme
  - storage
  - transport
timestamp: "2026-08-16T06:25:37.761Z"
---


# NVMe 传输模型

## 概述

NVMe 规范定义了主机（Host）与 NVM 子系统（NVM Subsystem）之间的两种基本通信模型：**基于内存的传输**（Memory-Based Transport）和**基于消息的传输**（Message-Based Transport）。传输层（Transport Layer）负责决定命令、响应和数据如何在主机和存储子系统之间传递。这两种模型的选择取决于底层的物理连接方式和传输协议。^[nvme-transport-models.md:5-7]

## 两种传输模型

### [基于内存的传输](/concepts/基于内存的传输.md)

**典型代表：PCIe**

在基于内存的传输模型中，主机和控制器共享内存空间。控制器可以直接访问主机内存中的提交队列（SQ）、完成队列（CQ）和数据缓冲区。通信通过MMIO和DMA完成。^[nvme-transport-models.md:11-16]

### [基于消息的传输](/concepts/基于消息的传输.md)

**典型代表：[NVMe-oF](/concepts/nvme-over-fabrics.md)（TCP、RDMA 等）**

在基于消息的传输模型中，主机和控制器通过网络结构（Fabric）交换封装的消息。命令和响应被打包成"胶囊"（Capsule），通过网络协议传递。^[nvme-transport-models.md:27-31]

基于消息的传输还可以进一步细分为两种子类型：
- **纯消息模式**（Message-Only）：所有数据都通过消息传递
- **消息/内存混合模式**（Message/Memory）：消息传递命令，但数据可能通过显式内存操作传输 ^[nvme-transport-models.md:42-44]

## [NVMe 传输架构分层](/concepts/nvme-传输架构分层.md)

NVMe 采用了清晰的分层架构，将传输无关的核心协议与具体的传输实现分离：

| 层级 | 说明 |
|------|------|
| **NVMe 核心架构** | 定义了与传输方式无关的通用接口和行为，如队列机制、命令集、控制器属性等 |
| **传输绑定层**（Transport Binding） | 将 NVMe 协议映射到具体的传输实现 |
| **NVMe 传输层** | 在底层网络之上提供可靠的传输服务 |
| **底层协议** | 如 PCIe、RDMA、TCP 等，这些协议本身不属于 NVMe 规范族 |

这种分层设计确保传输无关的 NVMe 接口位于绑定层之上、原生网络结构（Fabric）之下；原生网络服务不在 NVMe 规范族的范围内。^[nvme-transport-models.md:48-79]

## [胶囊机制](/concepts/胶囊机制.md)

### 什么是胶囊

在 [NVMe over Fabrics](/concepts/nvme-over-fabrics.md) 中，信息交换的基本单位是**胶囊（Capsule）**。胶囊是一个封装单元，可以包含一条命令或一个响应、可选的命令/响应数据，以及散布/聚集列表（SGL，Scatter-Gather List）。^[nvme-transport-models.md:93-104]

### 命令胶囊结构

命令胶囊（主机 → 控制器）由 64 字节的提交队列条目（SQE）加上后续的数据或额外的 SGL 组成。^[nvme-transport-models.md:158-167]

### 响应胶囊结构

响应胶囊（子系统 → 主机）由 16 字节的完成队列条目（CQE）加上可选数据组成。^[nvme-transport-models.md:169-178]

**关键要点：**
- 命令胶囊在 SQE 之后**不会同时混合**数据和额外的 SGL
- SQE 中的**命令标识符**（Command Identifier）在该队列的所有未完成命令中必须唯一
- 响应 CQE 与之前的某个命令胶囊一一对应 ^[nvme-transport-models.md:180-184]

## 传输层与端口

### NVMe 传输层的职责

NVMe 传输层在底层网络结构之上提供以下服务：
- **可靠交付**：确保命令和数据正确传递
- **传输无关性**：与底层物理互联和协议无关 ^[nvme-transport-models.md:108-113]

### [NVM 子系统端口](/concepts/nvm-子系统端口.md)

**NVM 子系统端口**（NVM Subsystem Port）是一个协议接口，具有以下特性：

- 可以聚合一个或多个物理网络接口
- 通过 **NQN**（NVMe Qualified Name）和 **16 位端口 ID** 进行标识
- 一个端口可以支持多种传输协议
- 已连接的控制器会绑定到特定的子系统端口 ^[nvme-transport-models.md:114-122]

## 三种传输模型对比

| 传输模型 | 命令/响应传递方式 | 数据传输方式 |
|---------|-----------------|-------------|
| **基于内存** | 显式内存读/写操作 | 显式内存读/写操作 |
| **纯消息** | 胶囊/消息 | 仅通过胶囊/消息 |
| **消息/内存混合** | 胶囊 | 胶囊或显式内存操作 |

两种基于消息的子类型共享基于胶囊的命令和响应传输方式，区别在于数据如何移动。^[nvme-transport-models.md:125-133]

## 数据放置策略

基于消息的队列支持通过 SGL 进行数据传输，传输绑定定义了以下数据放置方式：

| SGL 选择的数据放置方式 | 处理结果 |
|---------------------|-------------|
| **内存地址** | 数据通过传输支持的内存事务传输（如 RDMA） |
| **偏移量** | 数据直接承载在命令或响应胶囊中 |
| **额外描述符段** | 描述符紧接 SQE 之后连续排列 |

**错误处理：**
- 违反描述符数量限制：命令会被中止，返回 **Invalid Number of SGL Descriptors** 错误
- SGL 偏移量无效：返回 **SGL Offset Invalid** 错误 ^[nvme-transport-models.md:187-208]

## 关键要点总结

1. **两种基本模型**：NVMe 支持基于内存和基于消息两种传输模型，分别适用于本地连接和网络存储场景
2. **细分类型**：基于消息的传输进一步分为纯消息和消息/内存混合两种子类型
3. **分层架构**：核心 NVMe 协议与具体传输实现通过绑定层清晰分离
4. **胶囊机制**：Fabrics 传输使用胶囊封装命令、响应和数据
5. **灵活数据放置**：通过 SGL 支持多种数据放置策略，平衡性能和网络效率
6. **可扩展性**：统一的架构允许 NVMe 支持从 PCIe 到各种网络传输协议 ^[nvme-transport-models.md:210-218]

## Sources

- [nvme-transport-models.md](../_source/nvme-transport-models.md)

# Citations

1. [nvme-transport-models.md:5-7](/references/nvme-transport-models-e40dda19.md)
2. [nvme-transport-models.md:11-16](/references/nvme-transport-models-e40dda19.md)
3. [nvme-transport-models.md:27-31](/references/nvme-transport-models-e40dda19.md)
4. [nvme-transport-models.md:42-44](/references/nvme-transport-models-e40dda19.md)
5. [nvme-transport-models.md:48-79](/references/nvme-transport-models-e40dda19.md)
6. [nvme-transport-models.md:93-104](/references/nvme-transport-models-e40dda19.md)
7. [nvme-transport-models.md:158-167](/references/nvme-transport-models-e40dda19.md)
8. [nvme-transport-models.md:169-178](/references/nvme-transport-models-e40dda19.md)
9. [nvme-transport-models.md:180-184](/references/nvme-transport-models-e40dda19.md)
10. [nvme-transport-models.md:108-113](/references/nvme-transport-models-e40dda19.md)
11. [nvme-transport-models.md:114-122](/references/nvme-transport-models-e40dda19.md)
12. [nvme-transport-models.md:125-133](/references/nvme-transport-models-e40dda19.md)
13. [nvme-transport-models.md:187-208](/references/nvme-transport-models-e40dda19.md)
14. [nvme-transport-models.md:210-218](/references/nvme-transport-models-e40dda19.md)
