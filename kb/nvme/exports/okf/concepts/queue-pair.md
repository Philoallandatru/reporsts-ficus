---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: b612bff25ef4fc5679393c820f0f1a650a6556414ee48157f6f03b9fefbe9c92
  pageDirectory: concepts
  sources:
    - nvme-document-map.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - queue-pair
  citations:
    - file: nvme-document-map.md
    - file: nvme-document-map.md
      start: 44
      end: 44
    - file: nvme-document-map.md
      start: 45
      end: 45
    - file: nvme-document-map.md
      start: 33
      end: 33
    - file: nvme-document-map.md
      start: 21
      end: 21
    - file: nvme-document-map.md
      start: 186
      end: 186
    - file: nvme-document-map.md
      start: 211
      end: 211
    - file: nvme-document-map.md
      start: 39
      end: 39
    - file: nvme-document-map.md
      start: 31
      end: 31
    - file: nvme-document-map.md
      start: 197
      end: 197
    - file: nvme-document-map.md
      start: 28
      end: 28
    - file: nvme-document-map.md
      start: 181
      end: 181
title: Queue Pair
description: NVMe核心的内存队列机制，由Submission Queue和Completion Queue组成，用于主机与控制器之间的异步命令提交与完成通知。
tags:
  - nvme
  - storage-architecture
  - command-processing
timestamp: "2026-08-16T06:23:04.626Z"
---


# 队列对（Queue Pair）

## 概述

队列对（Queue Pair，QP）是 NVMe 协议中用于 host 与 [Controller](/concepts/controller.md) 之间进行命令提交与完成通信的核心数据结构。每个队列对由一个提交队列（Submission Queue，SQ）和一个完成队列（Completion Queue，CQ）组成，配对使用以实现完整的异步命令处理模型。^[nvme-document-map.md]

## 基本结构

### 提交队列（Submission Queue）

提交队列是 host 写入命令请求的环形缓冲区。Host 将命令写入 SQ 后，通过写 doorbell 寄存器通知 controller有新命令待处理。SQ 中的每个条目称为提交队列条目（Submission Queue Entry，SQE），通常为 64 字节，遵循 NVMe 通用命令格式。^[nvme-document-map.md:44]

### 完成队列（Completion Queue）

完成队列用于 [Controller](/concepts/controller.md) 向 host 报告命令执行结果。每个完成条目称为完成队列条目（Completion Queue Entry，CQE），包含状态信息、命令标识符以及用于相位标签（Phase Tag）协议的相位位。Host 通过轮询或中断机制感知新完成的命令。^[nvme-document-map.md:45]

## 通信模型

### 处理与完成顺序

命令的处理顺序与完成顺序遵循特定的语义规则。Controller 按照仲裁机制选择待处理的命令，但并非所有 transport 都保证命令的顺序执行。某些 transport 可能提供可靠性与顺序保证，而具体保证取决于所采用的传输层实现。^[nvme-document-map.md:33]

### 队列优先级

NVMe 支持为 I/O 提交队列配置优先级。优先级机制允许 host 指定哪些队列的命令应优先被处理，这在多租户或 QoS 敏感的场景中具有重要意义。^[nvme-document-map.md:21]

## 创建与管理

### I/O 队列创建

I/O 队列的创建通过管理命令完成。Host 向 Admin 队列提交创建 I/O 队列的请求，controller 分配相应的资源后返回队列标识符。创建过程中需要指定队列大小等参数。^[nvme-document-map.md:21, 186]

### PCIe 特定机制

在 PCIe 传输中，队列操作依赖于 Shadow Doorbell 和 EventIdx buffer 机制。这些机制用于在 PCIe 环境下精确同步 host 与 [Controller](/concepts/controller.md) 之间的队列头尾指针，确保命令提交与完成通知的可靠性。^[nvme-document-map.md:186, 211]

### 队列级重置

队列级别的重置操作允许独立重置特定的队列对，而不影响其他队列或 [Controller](/concepts/controller.md) 的整体状态。不同传输层对队列重置的支持和实现方式可能有所不同。^[nvme-document-map.md:39]

## Fabrics 扩展

### Connect 协商

在 [NVMe over Fabrics](/concepts/nvme-over-fabrics.md) 环境中，队列对的建立涉及 Connect 过程的协商。协商内容包括 SQ 流控参数的确定、CQ 大小的配置，以及认证状态的建立。^[nvme-document-map.md:31, 197]

### 单条删除

Fabrics 传输支持单条删除（single delete）操作，允许独立移除队列对中的特定条目，这在处理特定命令中止场景时尤为重要。^[nvme-document-map.md:31]

### 队列通道

Fabrics 环境中的队列通道（queue channels）提供了与本地 PCIe 实现不同的队列管理语义，包括循环缓冲区的流控机制和命令中止的处理方式。^[nvme-document-map.md:28]

## 仲裁与中断

### 队列计数协商

Host 与 [Controller](/concepts/controller.md) 之间可以协商支持的队列数量上限。队列计数协商影响系统的并发 I/O 能力，是性能规划的重要参数。^[nvme-document-map.md:181]

### 中断合并

为减少中断开销并提高效率，系统支持中断合并（interrupt coalescing）机制。通过将多个完成事件合并为单一中断触发，减少 CPU 中断处理的开销。^[nvme-document-map.md:181]

## Disconnect 与清理

Disconnect 操作包含最终响应屏障（final-response barrier），确保所有挂起的命令完成或明确中止后才正式关闭队列对连接。这是保证命令生命周期完整性的关键机制。^[nvme-document-map.md:197]

## 相关概念

- [Controller](/concepts/controller.md) - 队列对所在的控制器上下文
- Association and Command Lifecycle - 队列对与 Association 的关联关系
- Command Ordering and Arbitration - 命令仲裁机制
- [Transport Models](/concepts/transport-models.md) - 传输层模型对队列对的影响
- Completion Queue Entry and Status - 完成队列条目格式与状态
- Common Command Format - 提交队列条目的通用格式

## Sources

^[nvme-document-map.md]

# Citations

1. [nvme-document-map.md](/references/nvme-document-map-a6b14ca3.md)
2. [nvme-document-map.md:44-44](/references/nvme-document-map-a6b14ca3.md)
3. [nvme-document-map.md:45-45](/references/nvme-document-map-a6b14ca3.md)
4. [nvme-document-map.md:33-33](/references/nvme-document-map-a6b14ca3.md)
5. [nvme-document-map.md:21-21](/references/nvme-document-map-a6b14ca3.md)
6. [nvme-document-map.md:186-186](/references/nvme-document-map-a6b14ca3.md)
7. [nvme-document-map.md:211-211](/references/nvme-document-map-a6b14ca3.md)
8. [nvme-document-map.md:39-39](/references/nvme-document-map-a6b14ca3.md)
9. [nvme-document-map.md:31-31](/references/nvme-document-map-a6b14ca3.md)
10. [nvme-document-map.md:197-197](/references/nvme-document-map-a6b14ca3.md)
11. [nvme-document-map.md:28-28](/references/nvme-document-map-a6b14ca3.md)
12. [nvme-document-map.md:181-181](/references/nvme-document-map-a6b14ca3.md)
