---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 243aeb62f26d67a7e2ab12ea31b7a6e845ae7cd09676ee6cf55c0f66599922c0
  pageDirectory: concepts
  sources:
    - nvme-context.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - nvm-subsystem
  citations:
    - file: nvme-context.md
      start: 18
      end: 19
    - file: nvme-context.md
      start: 21
      end: 22
    - file: nvme-context.md
      start: 42
      end: 43
    - file: nvme-context.md
      start: 321
      end: 322
    - file: nvme-context.md
      start: 351
      end: 352
    - file: nvme-context.md
      start: 383
      end: 384
    - file: nvme-context.md
      start: 392
      end: 396
    - file: nvme-context.md
      start: 428
      end: 429
    - file: nvme-context.md
      start: 151
      end: 152
    - file: nvme-context.md
title: NVM Subsystem
description: NVMe 架构的核心边界，包含 controllers、ports、namespaces 及其底层 NVM 资源，提供 host 与非易失存储之间的接口抽象。
tags:
  - nvme
  - storage-architecture
  - subsystem
timestamp: "2026-08-16T06:19:59.299Z"
---

# NVM 子系统

**NVM Subsystem**（非易失性内存子系统）是 NVMe 规范中的核心边界概念，它将controllers（控制器）、ports（端口）、namespaces（命名空间）及其底层 NVM 资源封装为一个独立的管理单元。^[nvme-context.md:18-19]

## 概念定位

NVM Subsystem 位于 NVMe 规范模型的最顶层，是 host 与存储介质之间所有交互的承载实体。它定义了资源的可见性与访问边界：控制器通过 ports 向 host 暴露接口，而 namespaces 则以 logical-block 存储抽象的形式向控制器提供已格式化的 NVM 空间。^[nvme-context.md:18-19, nvme-context.md:21-22, nvme-context.md:42-43]

## 子系统组件

一个 NVM Subsystem 通常包含以下核心组件：

| 组件 | 说明 |
|------|------|
| [Controller](/concepts/controller.md) | 面向 host 的接口，负责暴露属性、处理命令、访问 namespaces |
| Namespace | 由一个或多个控制器以 logical-block 抽象呈现的已格式化 NVM 存储空间 |
| NVM Subsystem Port | 通过 [NVMe over Fabrics](/concepts/nvme-over-fabrics.md) 协议与 fabric 交互的接口，可由一个或多个物理 fabric 接口组成 |
| 底层 NVM 资源 | 实际的非易失性存储介质及相关硬件资源 |

## 子系统层面的操作

NVM Subsystem 作为一个原子边界，参与以下关键操作：

- **NVM Subsystem Reset**：影响整个子系统范围的复位操作，可通过 `NSSR` 触发，并在 NVM Subsystem Shutdown 完成后用于恢复系统状态。^[nvme-context.md:321-322]

- **NVM Subsystem Shutdown**：由某一控制器发起，作用范围覆盖该控制器所属 Domain 内的所有 [Controller](/concepts/controller.md) 或整个 NVM subsystem；在恢复常规执行前必须进行一次 NVM Subsystem Reset。^[nvme-context.md:351-352]

## 存储资源组织

在子系统内部，NVM 资源通过 Domain 进行分组管理。每个 Domain 进一步包含 Endurance Group，而 Endurance Group 内部又可划分出 NVM Set，最终从 NVM Set 中分配得到 namespace。这种层级结构为容量规划、耐久度管理和资源隔离提供了灵活的边界。^[nvme-context.md:383-384, nvme-context.md:392-396]

## 导出的 NVM 子系统

**Exported NVM Subsystem** 是将底层 NVM 资源逻辑化并呈现给远端访问者的实体。这种抽象使得分布式存储架构（如 NVMe over Fabrics）能够跨网络暴露本地存储资源。^[nvme-context.md:428-429]

## 特殊子系统类型

- **Discovery Service**：一种仅包含 Discovery Controller 的特殊 NVM Subsystem，其唯一功能是向 host 提供可达子系统与路径信息。^[nvme-context.md:151-152]

## 相关概念

- [Controller](/concepts/controller.md)
- Namespace
- Domain
- Endurance Group
- NVM Set
- NVM Subsystem Port
- Association
- Exported NVM Subsystem
- Discovery Service

## 来源

^[nvme-context.md] — NVM Express Base Specification Revision 2.1 概念词汇表

# Citations

1. [nvme-context.md:18-19](/references/nvme-context-d9974722.md)
2. [nvme-context.md:21-22](/references/nvme-context-d9974722.md)
3. [nvme-context.md:42-43](/references/nvme-context-d9974722.md)
4. [nvme-context.md:321-322](/references/nvme-context-d9974722.md)
5. [nvme-context.md:351-352](/references/nvme-context-d9974722.md)
6. [nvme-context.md:383-384](/references/nvme-context-d9974722.md)
7. [nvme-context.md:392-396](/references/nvme-context-d9974722.md)
8. [nvme-context.md:428-429](/references/nvme-context-d9974722.md)
9. [nvme-context.md:151-152](/references/nvme-context-d9974722.md)
10. [nvme-context.md](/references/nvme-context-d9974722.md)
