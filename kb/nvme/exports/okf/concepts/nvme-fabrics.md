---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 952813cccdce10ca8d0cb9a190b76d506ece082252313fc7240c5c953ab83ecc
  pageDirectory: concepts
  sources:
    - nvme-controller.md
  confidence: 0.85
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - nvme-fabrics
  citations:
    - file: nvme-controller.md
      start: 38
      end: 38
    - file: nvme-controller.md
      start: 53
      end: 53
    - file: nvme-controller.md
      start: 26
      end: 29
    - file: nvme-controller.md
      start: 59
      end: 62
    - file: nvme-controller.md
      start: 38
      end: 42
    - file: nvme-controller.md
      start: 46
      end: 46
    - file: nvme-controller.md
      start: 52
      end: 57
title: NVMe Fabrics
description: 基于消息传递的网络环境，支持控制器发现和服务定位，常配合发现控制器使用
tags:
  - NVMe
  - 网络存储
  - Fabrics
timestamp: "2026-08-16T06:23:02.241Z"
---

# NVMe Fabrics

## 概述

NVMe Fabrics 是 NVMe 规范中定义的远程直接内存访问（RDMA）或基于网络的传输架构，它将 NVMe 的高性能命令集扩展到网络互联环境中。与传统的 PCIe 本地连接不同，Fabrics 通过消息传递模型实现主机与存储子系统之间的通信，使分布式存储资源能够像本地 NVMe 设备一样被访问。 ^[nvme-controller.md:38]

## 传输模型

Fabrics 采用**基于消息的传输模型**，这是其与 PCIe（基于内存的传输）的核心区别。在基于消息的模型中，命令和数据通过消息封装后在网络中传递，控制器接收后再解析执行。这种设计使得 Fabrics 能够支持长距离连接和多点共享存储资源。 ^[nvme-controller.md:38, 53]

## [控制器类型](/concepts/控制器类型.md)

在 Fabrics 环境中，控制器承担多种角色：

| [控制器类型](/concepts/控制器类型.md) | 功能描述 | 是否处理用户 I/O |
|---|---|---|
| **I/O 控制器** | 访问命名空间，执行用户数据读写操作 | 是 |
| **发现控制器** | 帮助主机在 Fabrics 环境中发现可用服务 | 否 |
| **管理控制器** | 管理命名空间、虚拟化、健康状态或子系统操作 | 否 |

所有类型的控制器都需要配置一对管理队列（提交队列和完成队列），用于控制命令的处理。 ^[nvme-controller.md:26-29, nvme-controller.md:59-62]

## [静态与动态控制器](/concepts/静态与动态控制器.md)

Fabrics 环境中的控制器分配策略具有灵活性，可选择**静态**或**动态**模式：

- **静态控制器**：使用固定 ID，保存的配置在控制器级重置后仍可保留。这种模式适合需要持久化连接状态的场景。
- **动态控制器**：按需分配，新的会话从没有历史状态开始。发现控制器通常采用动态模式。

相比之下，PCIe 控制器仅支持静态模式，而 Fabrics 则支持两种模式，为不同的部署需求提供了更多选择。 ^[nvme-controller.md:38-42]

## Fabrics 存储的典型配置

一套 Fabrics 存储系统通常向不同客户端提供多种控制器服务：

- **管理控制器**：供管理员进行系统配置和管理操作
- **I/O 控制器**：供业务服务器执行实际的数据读写
- **发现控制器**：帮助新加入的主机发现可用服务

这些控制器可以共存于同一子系统内，但职责明确——发现和管理控制器不能替代用户数据 I/O 操作。 ^[nvme-controller.md:46, nvme-controller.md:59-62]

## 控制器维度归纳

理解 NVMe Fabrics 需要掌握以下四个维度：

| 维度 | 可选值 | 回答的问题 |
|---|---|---|
| 传输模型 | 基于内存 / 基于消息 | 命令和数据怎样传递？ |
| 分配模型 | 静态 / 动态 | 控制器何时创建、状态是否保留？ |
| 功能角色 | I/O / 发现 / 管理 | 它能提供什么服务？ |
| 资源角色 | 主控制器 / 从属控制器 | 虚拟化资源怎样管理？ |

例如，"使用 Fabrics 的动态 I/O 控制器"同时占据了前三个维度，是一种常见的生产部署配置。 ^[nvme-controller.md:52-57]

## 相关概念

- NVMe — Fabrics 的基础协议框架
- 控制器 — Fabrics 架构中的核心组件
- [命名空间](/concepts/命名空间.md) — 主机实际读写的逻辑存储对象
- 提交队列 — 主机向控制器提交命令的机制
- 完成队列 — 控制器返回命令执行结果的机制

## 规范依据

- [控制器、队列与命令处理，PDF 第 29 页](../_source/pages/page-029.md)
- [静态与动态控制器，PDF 第 58 页](../_source/pages/page-058.md)
- [控制器类型与管理队列，PDF 第 59-62 页](../_source/pages/page-059.md)
- [控制器类型和资源管理术语，PDF 第 28-35 页](../_source/pages/page-028.md)

## Sources

- [nvme-controller.md](../_source/nvme-controller.md)

# Citations

1. [nvme-controller.md:38-38](/references/nvme-controller-f4073d6a.md)
2. [nvme-controller.md:53-53](/references/nvme-controller-f4073d6a.md)
3. [nvme-controller.md:26-29](/references/nvme-controller-f4073d6a.md)
4. [nvme-controller.md:59-62](/references/nvme-controller-f4073d6a.md)
5. [nvme-controller.md:38-42](/references/nvme-controller-f4073d6a.md)
6. [nvme-controller.md:46-46](/references/nvme-controller-f4073d6a.md)
7. [nvme-controller.md:52-57](/references/nvme-controller-f4073d6a.md)
