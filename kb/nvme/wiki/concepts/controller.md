---
title: Controller
summary: NVMe子系统中的核心逻辑实体，负责处理主机命令、管理队列对、配置属性及电源/热管理，支持静态/动态分配模型和多种类型（I/O/Administrative/Discovery）。
sources:
- nvme-document-map.md
kind: concept
createdAt: '2026-08-16T06:23:22.663Z'
updatedAt: '2026-08-16T06:23:22.663Z'
tags:
- nvme
- storage-architecture
- hardware-components
aliases:
- controller
confidence: 0.95
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: 在 NVMe 规范架构中，**Controller（控制器）** 是 host 与 NVM 子系统之间通信的核心抽象实体。它代表了一条从
  host 到非易失性存储介质的命令与数据通路，是 NVMe 协议中处理 I/O Command Set 和 Admin Command Set 的执行上下文。
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: archived
canonical_ref: ../../concepts/controller.md
---

# Controller

在 NVMe 规范架构中，**Controller（控制器）** 是 host 与 NVM 子系统之间通信的核心抽象实体。它代表了一条从 host 到非易失性存储介质的命令与数据通路，是 NVMe 协议中处理 I/O Command Set 和 Admin Command Set 的执行上下文。

## Controller 类型

NVMe 规范定义了三种主要的 Controller 类型：

**I/O Controller** 是最常见的控制器类型，负责处理主机与存储介质之间的实际 I/O 操作。它通过 [[Queue Pair]] 接收来自 host 的命令，执行数据读写操作，并将完成状态返回给 host。

**Administrative Controller** 专门用于处理管理面命令，支持配置、状态查询和系统管理操作。Host 通过它执行 Identify Controller、Get/Set Features 等管理命令来完成控制器初始化和运行时配置。

**Discovery Controller** 则是一种特殊的控制器类型，主要用于 [[nvme-over-fabrics|NVMe over Fabrics]] 环境。其功能是响应 Discovery Log Page 请求，帮助 host 发现网络中可用的 NVMe 子系统和端口。

## 分配模型

Controller 支持两种分配模型：**静态分配** 和 **动态分配**。静态分配的控制器在系统启动时即被配置并保持可用，而动态分配的控制器可以根据需要创建和释放，提供了更大的资源灵活性。

## 相关概念

Controller 与以下核心概念紧密关联：

- Controller Properties — 控制器属性定义了控制器的功能特征和配置参数
- Controller Enable Shutdown Reset — 控制器的使能、关机和复位状态机
- Association and Command Lifecycle — Controller 是 Association 建立的基础单元
- [[Queue Pair]] — 控制器通过 [[queue-pair|Queue Pair]] 与 host 交换命令
- Controller Virtualization Resources — 控制器虚拟化支持 SR-IOV 等高级特性
- [[Controller Migration]] — 控制器的在线迁移能力
- Controller Memory Windows — 控制器内存窗口机制

## 架构位置

在 NVMe 架构分层中，Controller 位于 [[Transport Models]] 之上、Namespace Access Models 之下。它通过 transport 层接收 capsule 封装的命令，通过命令路由机制将 Admin 命令和 I/O 命令分别交付给对应的命令处理逻辑，并最终操作底层的 Namespace 资源。

---

## Sources

^[nvme-document-map.md:19] — 文档图指示 Controller 章节覆盖静态/动态分配模型与 I/O/Administrative/Discovery 类型（PDF pp. 58-62）

