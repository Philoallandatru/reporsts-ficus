---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: a4fcf9f71379c4a3df3093d4847c599f25bf8af2c0b7308cfeb1893b518c1632
  pageDirectory: concepts
  sources:
    - nvme-transport-models.md
  confidence: 1
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - nvme-传输架构分层
  citations:
    - file: nvme-transport-models.md
      start: 5
      end: 7
    - file: nvme-transport-models.md
      start: 74
      end: 74
    - file: nvme-transport-models.md
      start: 75
      end: 75
    - file: nvme-transport-models.md
      start: 76
      end: 76
    - file: nvme-transport-models.md
      start: 110
      end: 112
    - file: nvme-transport-models.md
      start: 77
      end: 77
    - file: nvme-transport-models.md
      start: 79
      end: 79
    - file: nvme-transport-models.md
      start: 83
      end: 90
title: NVMe 传输架构分层
description: 将传输无关的核心协议与具体传输实现分离的架构设计，包含核心架构层、传输绑定层、NVMe 传输层和底层网络协议层
tags:
  - nvme
  - architecture
  - layering
timestamp: "2026-08-16T06:25:55.186Z"
---

# NVMe 传输架构分层

## 概述

NVMe 采用清晰的分层架构设计，将传输无关的NVMe核心协议与具体的传输实现分离。这种设计确保了 NVMe 能够在多种物理连接和传输协议上保持统一的接口和行为规范。NVMe 规范定义了主机（Host）与 NVM 子系统（NVM Subsystem）之间的两种基本通信模型：基于内存的传输（Memory-Based Transport）和基于消息的传输（Message-Based Transport）。传输层（Transport Layer）负责决定命令、响应和数据如何在主机和存储子系统之间传递。^[nvme-transport-models.md:5-7]

## 架构分层

NVMe 传输架构从上到下分为四个层次，每个层次都有明确的职责边界：

```text
┌─────────────────────────────────────────────────────┐
│  NVMe 核心架构                                       │
│  (队列机制、命令集、控制器属性等)                    │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│  传输绑定层 (Transport Binding)                      │
│  (传输特定的适配和服务)                              │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│  NVMe 传输层 (NVMe Transport)                        │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│  底层网络协议 / 物理网络结构                         │
│  (不属于 NVMe 规范范围)                              │
└─────────────────────────────────────────────────────┘
```

### NVMe 核心架构

最上层是 NVMe 核心架构，定义了与传输方式无关的通用接口和行为，包括队列机制、命令集和控制器属性等关键组件。这些核心功能不依赖于具体的物理连接方式，为上层提供了统一的抽象接口。^[nvme-transport-models.md:74]

### 传输绑定层

传输绑定层负责将 NVMe 协议映射到具体的传输实现。该层根据不同的底层物理连接方式（如 PCIe、RDMA、TCP 等）提供相应的适配和服务。通过这种绑定机制，同一套 NVMe 命令集可以在不同的传输协议上运行。^[nvme-transport-models.md:75]

### NVMe 传输层

NVMe 传输层在底层网络之上提供可靠的传输服务，其主要职责包括确保命令和数据的正确传递，同时保持与底层物理互联和协议的无关性。传输层是连接上层协议和底层网络的桥梁。^[nvme-transport-models.md:76, nvme-transport-models.md:110-112]

### 底层网络协议

最底层是底层网络协议或物理网络结构，包括 PCIe、RDMA、TCP 等。这些协议本身不属于 NVMe 规范族的范围，而是由各自的标准组织定义。NVMe 规范通过传输绑定层来适配这些多样化的物理连接技术。^[nvme-transport-models.md:77]

## 设计原则

这种分层设计确保传输无关的 NVMe 接口位于绑定层之上、原生网络结构（Fabric）之下。原生网络服务不在 NVMe 规范族的范围内，而是由底层网络协议自行定义。这种职责分离使得 NVMe 具备良好的可扩展性，能够适应从本地连接到分布式网络存储的各种应用场景。^[nvme-transport-models.md:79]

## 规范文档组织

NVMe 规范族采用模块化的文档组织方式：

- **基础规范（Base Specification）**：有意涵盖两种传输模型的通用部分
- **各传输规范**：将 NVMe 协议绑定到具体传输实现，例如 NVMe over PCIe、NVMe over RDMA、NVMe over TCP

这种文档结构反映了架构分层的设计理念，便于不同传输协议的实现者和用户理解规范的各个层面。^[nvme-transport-models.md:83-90]

## 关键要点

1. **清晰的职责边界**：每层只关注自己的功能，各层之间通过明确定义的接口交互
2. **传输无关性**：核心 NVMe 协议独立于底层物理传输方式
3. **可扩展性**：统一的架构允许 NVMe 支持从 PCIe 到各种网络传输协议
4. **模块化实现**：不同厂商可以专注于特定传输绑定的实现，而不必关心其他层面

## Sources

- [NVMe 传输模型（Transport Models）](nvme-transport-models.md)

# Citations

1. [nvme-transport-models.md:5-7](/references/nvme-transport-models-e40dda19.md)
2. [nvme-transport-models.md:74-74](/references/nvme-transport-models-e40dda19.md)
3. [nvme-transport-models.md:75-75](/references/nvme-transport-models-e40dda19.md)
4. [nvme-transport-models.md:76-76](/references/nvme-transport-models-e40dda19.md)
5. [nvme-transport-models.md:110-112](/references/nvme-transport-models-e40dda19.md)
6. [nvme-transport-models.md:77-77](/references/nvme-transport-models-e40dda19.md)
7. [nvme-transport-models.md:79-79](/references/nvme-transport-models-e40dda19.md)
8. [nvme-transport-models.md:83-90](/references/nvme-transport-models-e40dda19.md)
