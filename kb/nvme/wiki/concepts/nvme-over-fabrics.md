---
title: NVMe over Fabrics
summary: 将 NVMe 协议扩展到网络结构上的传输绑定规范，支持 RDMA、TCP 等底层网络协议实现远程存储访问
sources:
- nvme-transport-models.md
kind: concept
createdAt: '2026-08-16T06:26:22.884Z'
updatedAt: '2026-08-16T06:26:22.884Z'
tags:
- nvme
- fabrics
- rdma
- tcp
- network-storage
aliases:
- nvme-over-fabrics
- NOF
confidence: 1
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: NVMe over Fabrics（简称 NVMe-oF）是一种将 NVMe 协议扩展到网络存储场景的传输架构。它基于**消息传输模型**（Message-Based
  Transport），通过 Fabrics（网络结构）实现主机与 NVM 子系统之间的远程通信。与传统的基于内存的传输（如 PCIe）不同，NVMe over
  Fabrics 使用封装的...
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# NVMe over Fabrics

## 概述

NVMe over Fabrics（简称 NVMe-oF）是一种将 NVMe 协议扩展到网络存储场景的传输架构。它基于**消息传输模型**（Message-Based Transport），通过 Fabrics（网络结构）实现主机与 NVM 子系统之间的远程通信。与传统的基于内存的传输（如 PCIe）不同，NVMe over Fabrics 使用封装的消息进行命令和响应的交换。^[nvme-transport-models.md:29-31]

NVMe over Fabrics 支持多种底层传输协议，包括 **RDMA** 和 **TCP** 等，为分布式存储场景提供了高性能、低延迟的存储访问能力。^[nvme-transport-models.md:29-31]

## 架构分层

NVMe 规范采用了清晰的分层架构，将传输无关的核心协议与具体的传输实现分离：

- **NVMe 核心架构**：定义了与传输方式无关的通用接口和行为，包括队列机制、命令集和控制器属性等 ^[nvme-transport-models.md:74-75]
- **传输绑定层**：将 NVMe 协议映射到具体的传输实现 ^[nvme-transport-models.md:75]
- **NVMe 传输层**：在底层网络之上提供可靠的传输服务 ^[nvme-transport-models.md:76]
- **底层协议**：如 RDMA、TCP 等，这些协议本身不属于 NVMe 规范族 ^[nvme-transport-models.md:77]

这种分层设计确保了传输无关的 NVMe 接口位于绑定层之上、原生网络结构之下。原生网络服务不在 NVMe 规范族的范围内。^[nvme-transport-models.md:79]

## [[胶囊机制|胶囊机制]]

在 NVMe over Fabrics 中，信息交换的基本单位是**胶囊（Capsule）**。胶囊是一个封装单元，可以包含一条命令或响应、可选的命令/响应数据，以及散布/聚集列表（SGL）。^[nvme-transport-models.md:95-103]

### 命令胶囊结构

命令胶囊从主机发送到控制器，其结构如下：

- **字节 0-63**：64 字节的 SQE（提交队列条目）
- **字节 64 至 N-1**：数据或额外的 SGL（散布/聚集列表） ^[nvme-transport-models.md:159-167]

### 响应胶囊结构

响应胶囊从子系统返回主机，其结构如下：

- **字节 0-15**：16 字节的 CQE（完成队列条目）
- **字节 16 至 N-1**：可选数据 ^[nvme-transport-models.md:169-178]

### 关键规则

- 命令胶囊在 SQE 之后不会同时混合数据和额外的 SGL ^[nvme-transport-models.md:181]
- SQE 中的命令标识符在该队列的所有未完成命令中必须唯一 ^[nvme-transport-models.md:182]
- 响应 CQE 与之前的某个命令胶囊一一对应 ^[nvme-transport-models.md:183]

## [[nvm-子系统端口|NVM 子系统端口]]

**NVM 子系统端口**（NVM Subsystem Port）是 NVMe over Fabrics 中的协议接口，具有以下特性：

- 可以聚合一个或多个物理网络接口 ^[nvme-transport-models.md:118]
- 通过 **NQN**（NVMe Qualified Name）和 **16 位端口 ID** 进行标识 ^[nvme-transport-models.md:119]
- 一个端口可以支持多种传输协议 ^[nvme-transport-models.md:120]
- 已连接的控制器会绑定到特定的子系统端口 ^[nvme-transport-models.md:121]

## 数据放置策略

NVMe over Fabrics 支持多种数据放置策略，通过 SGL（Scatter-Gather List）实现：

| SGL 选择的数据放置方式 | 说明 |
|----------------------|------|
| **内存地址** | 数据通过传输支持的内存事务传输（如 RDMA） ^[nvme-transport-models.md:191] |
| **偏移量** | 数据直接承载在命令或响应胶囊中 ^[nvme-transport-models.md:192] |
| **额外描述符段** | 描述符紧接 SQE 之后连续排列 ^[nvme-transport-models.md:193] |

对于胶囊内数据，额外的胶囊内 SGL 从字节 64 开始，胶囊内命令数据从字节偏移量 `64 + ICDOFF × 16` 开始，中间的任何字节都是未定义的。^[nvme-transport-models.md:197-200]

## 传输模型对比

NVMe 定义了两种基本传输模型：

| 传输模型 | 命令/响应传递方式 | 数据传输方式 |
|---------|-----------------|-------------|
| **基于内存**（如 PCIe） | 显式内存读/写操作 | 显式内存读/写操作 ^[nvme-transport-models.md:129] |
| **基于消息**（如 Fabrics） | 胶囊/消息 | 取决于具体子类型 ^[nvme-transport-models.md:130-131] |

基于消息的传输还可以进一步细分为两种子类型：

- **纯消息模式**：所有数据都通过消息传递 ^[nvme-transport-models.md:43]
- **消息/内存混合模式**：消息传递命令，但数据可能通过显式内存操作传输 ^[nvme-transport-models.md:44]

## 错误处理

传输绑定层定义了与 SGL 相关的错误处理机制：

- 违反描述符数量限制：命令会被中止，返回 **Invalid Number of SGL Descriptors** 错误 ^[nvme-transport-models.md:205]
- SGL 偏移量无效：返回 **SGL Offset Invalid** 错误 ^[nvme-transport-models.md:206]

## 优势

NVMe over Fabrics 的主要优势包括：

1. **可扩展性**：统一的架构允许 NVMe 支持从 PCIe 到各种网络传输协议 ^[nvme-transport-models.md:217]
2. **灵活数据放置**：通过 SGL 支持多种数据放置策略，平衡性能和网络效率 ^[nvme-transport-models.md:216]
3. **低延迟**：利用 RDMA 等高速网络技术实现接近本地存储的访问延迟
4. **多传输支持**：兼容 RDMA、TCP 等多种网络传输协议，适应不同网络环境

---

## _sources

- [nvme-transport-models.md](../../sources/nvme-transport-models.md)
