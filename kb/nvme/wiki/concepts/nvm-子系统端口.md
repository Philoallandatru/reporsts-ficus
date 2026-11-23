---
title: NVM 子系统端口
summary: 通过 NQN 和 16 位端口 ID 标识的协议接口，可聚合多个物理网络接口并支持多种传输协议
sources:
- nvme-transport-models.md
kind: concept
createdAt: '2026-08-16T06:26:04.799Z'
updatedAt: '2026-08-16T06:26:04.799Z'
tags:
- nvme
- fabrics
- port
- nqn
aliases:
- nvm-子系统端口
confidence: 1
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: NVM 子系统端口（NVM Subsystem Port）是 NVMe 传输层架构中的一个核心概念，定义为主机与 NVM 子系统之间的协议接口。
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# NVM 子系统端口

NVM 子系统端口（NVM Subsystem Port）是 NVMe 传输层架构中的一个核心概念，定义为主机与 NVM 子系统之间的协议接口。

## 定义与角色

NVM 子系统端口是 NVMe 传输层在底层网络结构之上提供可靠传输服务的关键组成部分。它作为协议接口，承载着主机与存储子系统之间的通信职责。

## 主要特性

### 物理接口聚合

一个 NVM 子系统端口可以聚合一个或多个物理网络接口，这种设计提供了网络层面的冗余和负载均衡能力。

### 标识机制

NVM 子系统端口通过以下两种方式进行唯一标识：

- **NQN**（NVMe Qualified Name）：全局唯一的子系统名称
- **16 位端口 ID**：用于在子系统内部标识特定端口

### 多协议支持

单个端口可以同时支持多种传输协议，例如 NVMe over RDMA、NVMe over TCP 等，这为部署提供了极大的灵活性。

### 控制器绑定

已建立的 NVMe 控制器会绑定到特定的 NVM 子系统端口，这种绑定关系统确保了通信路径的确定性和可靠性。

## 与传输层的关系

NVM 子系统端口位于 NVMe 传输层架构的传输绑定层（Transport Binding Layer）。传输绑定层负责将 NVMe 协议映射到具体的传输实现，如 RDMA、TCP 等物理网络协议。这种分层设计使核心 NVMe 协议与底层传输介质解耦，提高了协议的可扩展性和通用性。

## 相关概念

- [[NVMe over Fabrics]]
- 传输绑定层
- NQN
- 胶囊（Capsule）机制
- PCIe

## Sources

^[nvme-transport-models.md:114-123]

