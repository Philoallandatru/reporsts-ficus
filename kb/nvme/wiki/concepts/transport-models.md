---
title: Transport Models
summary: NVMe传输层抽象模型，支持PCIe和Fabrics（包括RDMA/TCP/FC等）两种分类，定义capsule、port、flow control及消息队列传输契约。
sources:
- nvme-document-map.md
kind: concept
createdAt: '2026-08-16T06:23:39.310Z'
updatedAt: '2026-08-16T06:23:39.310Z'
tags:
- nvme
- transport-layer
- interconnect
aliases:
- transport-models
confidence: 0.95
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: 传输模型（Transport Models）是 NVMe 规范中定义的核心概念，描述了命令和数据如何在主机（Host）与控制器（Controller）之间进行传输。传输模型定义了多种传输类型、分层架构以及数据放置契约，是理解
  NVMe 协议通信机制的基础。 ^[nvme-document-map.md:10]
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: archived
canonical_ref: ../../concepts/transport-models.md
---

# 传输模型

传输模型（Transport Models）是 NVMe 规范中定义的核心概念，描述了命令和数据如何在主机（Host）与控制器（Controller）之间进行传输。传输模型定义了多种传输类型、分层架构以及数据放置契约，是理解 NVMe 协议通信机制的基础。 ^[nvme-document-map.md:10]

## 分类与适用范围

NVMe 规范定义了多种传输模型类型，以适应不同的物理介质和应用场景。传输模型的选择影响命令封装方式、数据传输路径以及协议栈的分层设计。规范根据传输介质的不同，对传输模型进行了系统化的分类。 ^[nvme-document-map.md:10]

PCIe 传输是最直接的传输模型，适用于直接连接到主机总线适配器的 NVMe 设备。Fabrics 传输模型则面向网络化存储场景，支持通过以太网、InfiniBand 等网络结构连接远程 NVMe 设备。不同传输模型在命令结构和数据路径上存在差异，但共享 NVMe 协议的核心语义。 ^[nvme-document-map.md:10]

## Fabrics 分层架构

在 Fabrics 环境下，传输模型采用分层架构设计。这种分层方式将协议栈划分为多个抽象层次，使得上层命令结构与底层传输机制保持独立。分层设计允许同一命令语义通过不同的物理传输实现，同时保持了协议的互操作性。 ^[nvme-document-map.md:10]

Port（端口）是 Fabrics 分层架构中的关键元素，定义了主机与子系统之间的连接端点。每个 Port 代表一个独立的通信通道，可支持多个并发连接。Capsule（胶囊）则是 Fabrics 中命令和数据传输的基本单元，封装了完整的命令请求或响应信息。 ^[nvme-document-map.md:10]

## 命令胶囊与响应布局

Command Capsule（命令胶囊）定义了从主机发送到控制器的命令结构。每个命令胶囊包含固定格式的元数据区域和可变长的数据区域。规范详细规定了胶囊的内部布局，包括命令标识符、数据指针（PRP/SGL）以及元数据字段的位置和大小。 ^[nvme-document-map.md:30]

Response Capsule（响应胶囊）则携带命令执行的结果信息，包括完成状态、数据传输长度以及可选的错误信息。响应胶囊的格式同样遵循规范定义的布局契约，确保主机能够正确解析控制器返回的结果。 ^[nvme-document-map.md:30]

## 内存数据放置契约

传输模型区分了两种主要的数据放置方式：**胶囊内数据放置**（In-Capsule Data Placement）和**内存数据放置**（Memory Data Placement）。

胶囊内数据放置指将小块数据直接嵌入命令胶囊中进行传输，适用于数据量较小的 I/O 操作。这种方式可以减少传输延迟和 DMA 操作次数，但受到胶囊最大尺寸的限制。规范定义了 message queue capsule 的大小约束，超出此限制的数据必须通过其他方式传输。 ^[nvme-document-map.md:29, nvme-document-map.md:30]

内存数据放置则依赖主机内存缓冲区，通过 PRP（Physical Region Page）或 SGL（Scatter-Gather List）描述符指向实际数据位置。SGL 描述符定义了复杂的数据传输契约，支持非连续内存区域的描述和传输。规范对 SGL 传输契约进行了详细规定，包括描述符格式、地址对齐要求以及链式 SGL 的构造规则。 ^[nvme-document-map.md:29, nvme-document-map.md:30]

## 与队列对的关联

传输模型与 [[Queue Pair]]（队列对）机制紧密关联。队列对由提交队列（Submission Queue, SQ）和完成队列（Completion Queue, CQ）组成，是 NVMe 命令处理的核心机制。传输模型决定了队列对在特定物理介质上的实现方式。 ^[nvme-document-map.md:10, nvme-document-map.md:11]

在 Fabrics 环境下，队列对通过流控机制（Flow Control）管理命令传输，确保发送端和接收端之间的数据一致性。传输层负责维护队列状态，包括队列创建、删除以及复位操作。不同传输模型的队列通道（Queue Channel）实现各有特点，PCIe 使用门铃寄存器机制，而 Fabrics 则基于消息传递。 ^[nvme-document-map.md:28, nvme-document-map.md:33, nvme-document-map.md:39]

## 相关概念

- [[Queue Pair]]：队列对机制与传输模型的实现
- Fabrics Discovery and Authentication：Fabrics 环境下的发现与认证过程
- [[Controller]]：控制器与传输层的交互
- Command Sets：命令集如何通过不同传输模型路由

## 资料来源

^[nvme-document-map.md]

