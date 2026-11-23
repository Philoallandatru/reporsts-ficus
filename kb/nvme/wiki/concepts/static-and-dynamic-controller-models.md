---
title: Static and Dynamic Controller Models
summary: 两种全子系统范围的控制器分配模型：Static 保留控制器身份与状态跨 reset 或 association；Dynamic 则按需分配、不保留先前状态。
sources:
- nvme-context.md
kind: concept
createdAt: '2026-08-16T06:19:56.953Z'
updatedAt: '2026-08-16T06:19:56.953Z'
tags:
- nvme
- controller
- architecture
aliases:
- static-and-dynamic-controller-models
- Dynamic Controller Models and Static
- SADCM
confidence: 0.95
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: 静态控制器模型（Static [[controller|Controller]] Model）与动态控制器模型（Dynamic [[controller|Controller]]
  Model）是 NVMe 规范中定义的两种全子系统范围的控制器分配模型，它们在控制器的生命周期管理、身份保留和行为特性方面存在本质差异。 ^[nvme-context.md:...
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 静态与动态控制器模型

静态控制器模型（Static [[controller|Controller]] Model）与动态控制器模型（Dynamic [[controller|Controller]] Model）是 NVMe 规范中定义的两种全子系统范围的控制器分配模型，它们在控制器的生命周期管理、身份保留和行为特性方面存在本质差异。 ^[nvme-context.md:24-28]

## 静态控制器模型

静态控制器模型是一种控制器分配模型，其核心特征是**控制器身份与已保存状态在 [[controller|Controller]] Level Reset 后保留**。这意味着当发生控制器级别的复位操作时，控制器的标识信息及其在复位前保存的状态不会被清除或重新分配，而是继续维持原有的身份和配置。 ^[nvme-context.md:24-25]

对于 [[nvme-over-fabrics|NVMe over Fabrics]] 实现，静态控制器模型还可能在**跨 Association 时保持**控制器的身份和状态。这一特性使得静态模型适用于需要维持长期连接状态、或要求在连接中断后快速恢复先前工作上下文的部署场景。 ^[nvme-context.md:24-25]

## 动态控制器模型

动态控制器模型是另一种控制器分配模型，其核心特征是**控制器按需分配，不保留任何先前 Association 的状态**。与静态模型不同，动态模型在每次建立连接时可能会分配全新的控制器资源，而之前建立的 Association 中的任何状态信息都不会被保留或继承。 ^[nvme-context.md:27-28]

这种设计使得动态模型更加灵活，适合需要频繁创建和销毁连接、或对资源分配有动态调整需求的环境。

## 对比与适用场景

| 特性 | 静态控制器模型 | 动态控制器模型 |
|------|---------------|---------------|
| 控制器身份保留 | [[controller|Controller]] Level Reset 后保留 | 不保留 |
| 状态持续性 | 保存先前 Association 的状态 | 不保留先前状态 |
| Fabrics 跨 Association | 可能保持 | 不适用 |
| 适用场景 | 长期稳定连接、快速恢复 | 动态资源分配、灵活连接 |

## 相关概念

这两种模型都作用于 [[NVM Subsystem]] 范围内，其控制器行为与 Controller Level Reset、 Association 等核心概念紧密关联。在 [[nvme-over-fabrics|NVMe over Fabrics]] 环境中，模型的选型直接影响 [[Queue Pair]] 的建立方式以及 Keep Alive Timeout Time 的管理策略。

## Sources

^[nvme-context.md:18-28]

