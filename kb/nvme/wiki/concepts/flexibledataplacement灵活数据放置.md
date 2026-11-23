---
title: FlexibleDataPlacement灵活数据放置
summary: 用host指定的Reclaim Group/Reclaim Unit placement替换Endurance Group内的NVM Set分支，命令通过namespace-local的Placement
  Handle与Reclaim Group选择数据放置位置
sources:
- nvme-architecture-map.md
kind: concept
createdAt: '2026-08-16T06:18:05.229Z'
updatedAt: '2026-08-16T06:18:05.229Z'
tags:
- NVMe
- 数据布局
- 存储管理
aliases:
- flexibledataplacement灵活数据放置
confidence: 0.9
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: Flexible Data Placement（FDP）是 NVMe 规范中一项用于控制数据写入位置的高级功能。该特性在已启用的 Endurance
  Group 内提供了一种替代 NVM Set 的 host 驱动数据放置机制，使 host 能够更细粒度地管理写入数据的物理位置。^[nvme-architecture-map.md:60]
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Flexible Data Placement（灵活数据放置）

Flexible Data Placement（FDP）是 NVMe 规范中一项用于控制数据写入位置的高级功能。该特性在已启用的 Endurance Group 内提供了一种替代 NVM Set 的 host 驱动数据放置机制，使 host 能够更细粒度地管理写入数据的物理位置。^[nvme-architecture-map.md:60]

## 核心机制

FDP 将数据放置的组织结构从静态的 NVM Set 分支替换为 **host 指定的 Reclaim Group → Reclaim Unit** 二级映射。^[nvme-architecture-map.md:60]

- **Placement Handle**：每个 namespace 拥有一个本地的 Placement Handle，用于选择一个 Reclaim Group。
- **Reclaim Unit**：Placement Handle 解析为每个 Reclaim Group 中的一个 Reclaim Unit，数据将被写入该单元。
- **重定向能力**：当一个 Reclaim Unit 写满时，host 可以通过 I/O Management Send 命令将 Placement Identifier 重新指向一个空的 Reclaim Unit。^[nvme-architecture-map.md:60,142]

## 运行时视图

FDP 将静态的 Endurance Group 配置与三份运行时视图关联：^[nvme-architecture-map.md:218]

1. **Handle Ownership（句柄所有权）**：记录当前各 Placement Handle 的归属状态。
2. **写/擦统计**：跟踪每个 Reclaim Unit 的写入和擦除次数，反映饱和程度。
3. **Oldest-First 事件历史**：在启用后维护一份按时间顺序的事件记录，用于分析和管理。

## Placement Identifier 的解释

Placement Identifier 的具体含义取决于 Endurance Group 的配置，特别是 **RGIF（Reclaim Group Indicator Flag）** 字段。RGIF 决定了 Identifier 的高位是否用于选择 Reclaim Group。^[nvme-architecture-map.md:218]

## 相关功能

同一个 FDP extended-capability 区域还定义了以下相关功能：^[nvme-architecture-map.md:62]

- **Write Placement 路径**：提供明确的数据放置写入路径。
- **Host-Initiated Refresh**：全 subsystem 范围的 host 驱动刷新机制。
- **Controller Migration 扩展**：将由 [[Controller Migration]] 管理的源/目的工作流进行扩展。

## 与 Directive 的关系

FDP 共享 Directive Exchange 的编码框架，但将实际的数据放置职责委托给 FDP 自身，而非定义独立的 Send/Receive 操作。^[nvme-architecture-map.md:172]

## 命令交互

- **I/O Management Receive**：返回 FDP Reclaim Unit Handle 的状态信息。^[nvme-architecture-map.md:142]
- **I/O Management Send**：将 FDP Placement Identifier 重新指向空的 Reclaim Unit，并显式声明 partial failure 与 concurrent-write 语义。^[nvme-architecture-map.md:142]

---

## Sources

- nvme-architecture-map.md — Architecture map（架构图）
- flexible-data-placement-configurations.md — Flexible Data Placement Configurations（灵活数据放置配置）

