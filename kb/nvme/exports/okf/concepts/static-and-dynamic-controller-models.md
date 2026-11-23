---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: bc87b2284791914961c8d4cbae0c2dd33fad257e553c05d137e37300678d122b
  pageDirectory: concepts
  sources:
    - nvme-context.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - static-and-dynamic-controller-models
    - Dynamic Controller Models and Static
    - SADCM
  citations:
    - file: nvme-context.md
      start: 24
      end: 28
    - file: nvme-context.md
      start: 24
      end: 25
    - file: nvme-context.md
      start: 27
      end: 28
    - file: nvme-context.md
      start: 18
      end: 28
title: Static and Dynamic Controller Models
description: 两种全子系统范围的控制器分配模型：Static 保留控制器身份与状态跨 reset 或 association；Dynamic 则按需分配、不保留先前状态。
tags:
  - nvme
  - controller
  - architecture
timestamp: "2026-08-16T06:19:56.953Z"
---

# 静态与动态控制器模型

静态控制器模型（Static [Controller](/concepts/controller.md) Model）与动态控制器模型（Dynamic [Controller](/concepts/controller.md) Model）是 NVMe 规范中定义的两种全子系统范围的控制器分配模型，它们在控制器的生命周期管理、身份保留和行为特性方面存在本质差异。 ^[nvme-context.md:24-28]

## 静态控制器模型

静态控制器模型是一种控制器分配模型，其核心特征是**控制器身份与已保存状态在 [Controller](/concepts/controller.md) Level Reset 后保留**。这意味着当发生控制器级别的复位操作时，控制器的标识信息及其在复位前保存的状态不会被清除或重新分配，而是继续维持原有的身份和配置。 ^[nvme-context.md:24-25]

对于 [NVMe over Fabrics](/concepts/nvme-over-fabrics.md) 实现，静态控制器模型还可能在**跨 Association 时保持**控制器的身份和状态。这一特性使得静态模型适用于需要维持长期连接状态、或要求在连接中断后快速恢复先前工作上下文的部署场景。 ^[nvme-context.md:24-25]

## 动态控制器模型

动态控制器模型是另一种控制器分配模型，其核心特征是**控制器按需分配，不保留任何先前 Association 的状态**。与静态模型不同，动态模型在每次建立连接时可能会分配全新的控制器资源，而之前建立的 Association 中的任何状态信息都不会被保留或继承。 ^[nvme-context.md:27-28]

这种设计使得动态模型更加灵活，适合需要频繁创建和销毁连接、或对资源分配有动态调整需求的环境。

## 对比与适用场景

| 特性 | 静态控制器模型 | 动态控制器模型 |
|------|---------------|---------------|
| 控制器身份保留 | [Controller](/concepts/controller.md) Level Reset 后保留 | 不保留 |
| 状态持续性 | 保存先前 Association 的状态 | 不保留先前状态 |
| Fabrics 跨 Association | 可能保持 | 不适用 |
| 适用场景 | 长期稳定连接、快速恢复 | 动态资源分配、灵活连接 |

## 相关概念

这两种模型都作用于 [NVM Subsystem](/concepts/nvm-subsystem.md) 范围内，其控制器行为与 Controller Level Reset、 Association 等核心概念紧密关联。在 [NVMe over Fabrics](/concepts/nvme-over-fabrics.md) 环境中，模型的选型直接影响 [Queue Pair](/concepts/queue-pair.md) 的建立方式以及 Keep Alive Timeout Time 的管理策略。

## Sources

^[nvme-context.md:18-28]

# Citations

1. [nvme-context.md:24-28](/references/nvme-context-d9974722.md)
2. [nvme-context.md:24-25](/references/nvme-context-d9974722.md)
3. [nvme-context.md:27-28](/references/nvme-context-d9974722.md)
4. [nvme-context.md:18-28](/references/nvme-context-d9974722.md)
