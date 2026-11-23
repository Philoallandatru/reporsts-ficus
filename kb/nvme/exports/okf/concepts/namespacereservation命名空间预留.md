---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 8dc2b58c358d9f8c73da990c4a5bb15d58f3b1aea430f76e4abe8796bdbaa4bc
  pageDirectory: concepts
  sources:
    - nvme-architecture-map.md
  confidence: 0.88
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - namespacereservation命名空间预留
  citations:
    - file: nvme-architecture-map.md
      start: 70
      end: 70
    - file: nvme-architecture-map.md
      start: 144
      end: 144
    - file: nvme-architecture-map.md
      start: 126
      end: 126
    - file: nvme-architecture-map.md
      start: 128
      end: 128
    - file: nvme-architecture-map.md
      start: 46
      end: 46
    - file: nvme-architecture-map.md
      start: 220
      end: 220
title: NamespaceReservation命名空间预留
description: 将访问权限绑定到Host Identifier而非controller路径的共享访问状态机，支持6种holder/registrant策略，命令处理时固化冲突决策
tags:
  - NVMe
  - 命名空间
  - 访问控制
timestamp: "2026-08-16T06:17:49.523Z"
---

# Namespace Reservation（命名空间预留）

## 概述

Namespace Reservation（命名空间预留）是 NVMe 规范中一种用于在多主机环境下控制共享 namespace 访问权限的机制。它将访问权限绑定到 **Host Identifier** 而非 [Controller](/concepts/controller.md) 路径，在命令开始处理的那一刻固化冲突决策。 ^[nvme-architecture-map.md:70]

Reservation 机制在共享 namespace 之上形成一个独立的 shared-access 状态机，涵盖以下核心操作：host 注册 key、获取或抢占有类型的 reservation、release 或 clear 状态、选择 power-loss persistence，并跨 dispersed participant 查看带 generation 计数的 registrant 记录。 ^[nvme-architecture-map.md:144]

## 核心概念

### Host Identifier 绑定

Reservation 将访问权限绑定到 **Host Identifier**，而非 [Controller](/concepts/controller.md) 路径。这一设计使得即使主机通过不同 [Controller](/concepts/controller.md) 访问 namespace，reservation 权限也能正确关联到发起操作的主机身份。 ^[nvme-architecture-map.md:70]

Host Identifier 的注册通过 Directive Exchange 机制进行协调，用于关联 [Controller](/concepts/controller.md) 与 reservation 权限。 ^[nvme-architecture-map.md:126]

### Holder 与 Registrant 策略

Namespace Reservation 应用 **6 种 holder/registrant 策略**，为不同场景下的多主机协调提供灵活的支持。这些策略定义了 reservation 的持有者（holder）与注册者（registrant）之间的权限关系。 ^[nvme-architecture-map.md:70]

### 冲突决策固化

在命令开始处理的那一刻，系统即固化冲突决策。这意味着所有并发访问的优先级判定在命令执行前已完成，确保了访问的一致性和可预测性。 ^[nvme-architecture-map.md:70]

## Reservation 状态机操作

Reservation 状态机支持以下操作类型：

| 操作 | 描述 |
|------|------|
| **注册 (Register)** | host 注册 key，建立 reservation 权限的基础 |
| **获取 (Acquire)** | 获取特定类型的 reservation |
| **抢占 (Preempt)** | 在特定条件下抢占已有的 reservation |
| **释放 (Release)** | 释放当前持有的 reservation |
| **清除 (Clear)** | 清除 reservation 状态 |
| **持久化选择** | 选择 power-loss 后的 reservation 持久化策略 |

^[nvme-architecture-map.md:144]

### Power-Loss Persistence

Reservation 机制支持选择 **power-loss persistence**（掉电持久化）策略，允许配置 reservation 状态在断电后是否保留。Feature 面的 reservation mask 与 PTPL (Pathtransform Persistence TLV) 配置控制了哪些 namespace reservation 变更需要上报，以及 reservation 状态是否在掉电后保留。 ^[nvme-architecture-map.md:128]

### Generation Count（代数计数）

跨 dispersed participant 查看的带 **generation 计数**的 registrant 记录，用于检测 reservation 状态的变更，确保分布式环境下的状态一致性。 ^[nvme-architecture-map.md:144]

## 与 ANA 的关系

Reservation 恢复通过 ANA 控制访问，直至状态被同步或被声明为 persistently lost。这一机制确保了在路径或节点故障场景下，reservation 状态能够被正确管理和恢复。 ^[nvme-architecture-map.md:46]

## 通知机制

Reservation Notification Log 提供 reservation 状态变更的通知通道。该日志是一条 destructive-read FIFO，其序号暴露已丢失的通知，使主机能够及时获知 reservation 相关的异步事件。 ^[nvme-architecture-map.md:220]

## 与 Dispersed Namespace 的关系

对于远端导出场景，namespace reservation 同样适用。跨 participating subsystem 成为 dispersed namespace 时，generation 计数的 registrant 记录确保了多参与者环境下 reservation 状态的一致性视图。 ^[nvme-architecture-map.md:144]

## 参见

- Namespace
- Namespace Sharing
- ANA
- Host Identifier
- Directive Exchange
- Reservation Notification Log
- Dispersed Namespace Lifecycle
- Namespace Write Protection
- Namespace Management Lifecycle

## Sources

^[nvme-architecture-map.md:70] ^[nvme-architecture-map.md:144] ^[nvme-architecture-map.md:126] ^[nvme-architecture-map.md:128] ^[nvme-architecture-map.md:220] ^[nvme-architecture-map.md:46]

# Citations

1. [nvme-architecture-map.md:70-70](/references/nvme-architecture-map-f141b52c.md)
2. [nvme-architecture-map.md:144-144](/references/nvme-architecture-map-f141b52c.md)
3. [nvme-architecture-map.md:126-126](/references/nvme-architecture-map-f141b52c.md)
4. [nvme-architecture-map.md:128-128](/references/nvme-architecture-map-f141b52c.md)
5. [nvme-architecture-map.md:46-46](/references/nvme-architecture-map-f141b52c.md)
6. [nvme-architecture-map.md:220-220](/references/nvme-architecture-map-f141b52c.md)
