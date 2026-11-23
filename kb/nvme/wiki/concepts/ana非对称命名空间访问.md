---
title: ANA非对称命名空间访问
summary: 将访问建模为controller-to-group关系，组成员在同一Domain内共同变迁，状态包括Optimized/Non-Optimized/Inaccessible/Persistent
  Loss/瞬态Change
sources:
- nvme-architecture-map.md
kind: concept
createdAt: '2026-08-16T06:18:27.834Z'
updatedAt: '2026-08-16T06:18:27.834Z'
tags:
- NVMe
- 多路径
- 故障恢复
aliases:
- ana非对称命名空间访问
confidence: 0.87
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: ANA 将命名空间按访问特性划分为不同的 **ANA Group（ANA 组）**。属于同一组的成员在同一个 Domain 内共同变迁——当组的访问状态发生变化时，所有成员同步更新。^[nvme-architecture-map.md:146]
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# ANA 非对称命名空间访问

**ANA（非对称命名空间访问，Asymmetric Namespace Access）** 是 NVMe 规范中用于建模命名空间访问路径的一种机制。它将访问关系表达为 **controller-to-group（控制器到组）** 的映射，而非简单的 controller-to-namespace 二元对应。^[nvme-architecture-map.md:146]

## 核心概念

ANA 将命名空间按访问特性划分为不同的 **ANA Group（ANA 组）**。属于同一组的成员在同一个 Domain 内共同变迁——当组的访问状态发生变化时，所有成员同步更新。^[nvme-architecture-map.md:146]

每个 [[controller|Controller]] 相对于其挂接的 namespace 可以报告以下访问状态之一：

| 状态 | 含义 |
|------|------|
| **Optimized** | 访问路径处于最优状态 |
| **Non-Optimized** | 路径可用但非最优 |
| **Inaccessible** | 当前不可访问 |
| **Persistent Loss** | 持久性路径故障 |
| **Change**（瞬态） | 路径状态正处于过渡中 |

## 状态影响

当出现 adverse state（不良状态）时，ANA 不会简单关闭整个 Admin 平面，而是选择性地影响以下方面：

- **命令可用性**：阻止或限制发往受影响路径的命令
- **重试路由**：指导 host 将 I/O 重定向至替代路径
- **上报容量**：调整报告给 host 的可用存储容量 ^[nvme-architecture-map.md:146]

## ANA 日志

ANA 日志是 **controller-relative（控制器相对）** 的组状态与 attached namespace 快照，受以下机制保护：

- **Global change count**：整个 ANA 命名空间范围的变更计数器
- **Per-group change count**：每个 ANA 组的独立变更计数器 ^[nvme-architecture-map.md:206]

通知机制负责向 host 暴露重要的状态变迁，使其能够及时响应路径变化。

## 与相关特性的关系

- **Namespace Sharing**：共享 namespace 在挂接的 [[controller|Controller]] 间保持唯一的 NSID 与 Identify Namespace 视图，但访问特性按 [[controller|Controller]] 维度可能非对称 ^[nvme-architecture-map.md:32]
- **Domains and Divisions**：ANA reservation 恢复通过 ANA 控制访问，直至状态被同步或被声明为 persistently lost ^[nvme-architecture-map.md:46]
- **Reachability reporting**：Reachability 通知使对应的 topology 快照失效，ANA 是其核心支撑机制 ^[nvme-architecture-map.md:66]

## 设计动机

传统的对称存储访问模型假设所有 host 到 namespace 的路径具有相同的性能特征。但在实际部署中，特别是跨 Fabrics 的远端导出场景下，不同路径的延迟、带宽和可用性往往存在显著差异。ANA 通过声明式的方式让 [[controller|Controller]] 向 host 告知各路径的真实状态，使 host 能够据此做出最优的 I/O 调度决策 ^[nvme-architecture-map.md:146]。

---

## Sources

- [nvme-architecture-map.md](../_source/nvme-architecture-map.md)

---

## 相关概念

- Domain
- Namespace Sharing
- Domains and Divisions
- Reachability reporting
- Fabrics
- Asynchronous Event Reporting

