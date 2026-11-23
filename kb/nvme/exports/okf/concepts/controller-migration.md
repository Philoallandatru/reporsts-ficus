---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 583a9bf57130129aa50824531a90a0fc024a6572ecc2d94c9e35f835cb482985
  pageDirectory: concepts
  sources:
    - nvme-document-map.md
  confidence: 0.9
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - controller-migration
  citations:
    - file: nvme-document-map.md
      start: 104
      end: 104
    - file: nvme-document-map.md
      start: 143
      end: 143
    - file: nvme-document-map.md
      start: 104
      end: 105
    - file: nvme-document-map.md
      start: 105
      end: 105
    - file: nvme-document-map.md
      start: 184
      end: 185
    - file: nvme-document-map.md
      start: 146
      end: 151
    - file: nvme-document-map.md
      start: 54
      end: 54
    - file: nvme-document-map.md
      start: 61
      end: 61
    - file: nvme-document-map.md
      start: 206
      end: 210
    - file: nvme-document-map.md
      start: 77
      end: 77
    - file: nvme-document-map.md
      start: 129
      end: 129
    - file: nvme-document-map.md
      start: 97
      end: 97
    - file: nvme-document-map.md
      start: 99
      end: 100
title: Controller Migration
description: 主机管理的在线迁移能力，支持Suspend/Resume生命周期、分段状态传输、Queue Pair重建、change tracking及源/目的端状态同步。
tags:
  - nvme
  - virtualization
  - high-availability
timestamp: "2026-08-16T06:24:20.422Z"
---


# 控制器迁移（Controller Migration）

控制器迁移是 NVMe 规范中定义的一种机制，允许将控制器的运行时状态从一个物理位置（源）转移到另一个物理位置（目的），同时保持 association 的持续性和 command 处理的连续性。此功能主要面向 Fabrics 环境，支持 host 管理的热迁移（live migration）场景，使存储资源能够在不中断 I/O 的情况下在不同控制器或不同物理主机之间迁移。

## 核心概念与角色

控制器迁移涉及两个主要角色的协同工作：**源控制器**（Source Controller）和**目的控制器**（Destination Controller）。源控制器是当前处理 I/O Command 的活跃端点，负责捕获并导出自身的运行时状态；目的控制器则接收并加载该状态，接管后续的命令处理工作。迁移过程由 host 发起并全程管理，控制器本身不感知迁移的全貌，仅响应来自 host 的特定命令序列。^[nvme-document-map.md:104, nvme-document-map.md:143]

## 挂起与恢复生命周期（Suspend/Resume Lifecycle）

控制器迁移的核心生命周期由 Suspend（挂起）和 Resume（恢复）两个阶段构成。Suspend 阶段使源控制器停止接受新的 I/O Command，并将其运行时状态序列化以便传输；Resume 阶段使目的控制器加载这些状态并恢复命令处理能力。两个阶段之间的状态传输可分段进行，以适应大规模状态数据的传输需求。^[nvme-document-map.md:104-105]

在挂起过程中，控制器需要确保 Receive 侧的数据完整性，即在快照一致性约束下捕获所有待处理的命令和响应。目的控制器在恢复时需要验证接收到的状态数据是否完整且未被损坏，校验通过后方可提交状态并开放命令处理能力。^[nvme-document-map.md:104-105]

## 状态传输机制

### 分段 Set [Controller](/concepts/controller.md) State

控制器状态数据量可能较大，规范支持将状态数据分段传输。host 通过分段 Set [Controller](/concepts/controller.md) State 命令逐段将源控制器的状态数据写入目的控制器，每段传输后进行校验确认，全部接收完成后目的控制器执行状态提交。这种设计允许在带宽受限的网络环境中进行迁移，同时支持断点续传等容错机制。^[nvme-document-map.md:105]

### 队列状态镜像（Queue-State Mirror）

在控制器迁移过程中，[Queue Pair](/concepts/queue-pair.md)（包括 Submission Queue 和 Completion Queue）的状态是迁移数据的核心组成部分。源控制器的队列状态被镜像到目的控制器，包括已提交但尚未完成的命令、待处理的响应以及队列头尾指针等关键状态信息。目的控制器在恢复后能够从中断点继续处理，无需重新执行已完成的命令。^[nvme-document-map.md:105]

SQ（Submission Queue）和 CQ（Completion Queue）的重建需要严格遵循原有的队列标识符和优先级配置，以确保 host 侧的门铃（doorbell）机制能够正确路由命令。^[nvme-document-map.md:105]

## 变更追踪（Change Tracking）

控制器迁移过程中，源控制器在 Suspend 之后可能仍发生某些状态变更（如异步事件上报、内部缓冲区更新等）。规范定义了变更追踪机制（参见 Migration Change Tracking），用于记录 Suspend 与状态传输之间发生的状态差异，确保目的控制器最终接收到的状态是完整的。host 通过 Track Receive/Send 命令配合 User Data Migration Queue（UDMQ）日志来管理和同步这些变更。^[nvme-document-map.md:143, nvme-document-map.md:184-185]

## 迁移流程概述

典型的 host 管理热迁移流程包括以下步骤：

1. **Change Tracking 启动**：host 通知源控制器开启变更追踪模式；
2. **源端 Suspend**：host 发送 Suspend 命令，源控制器停止接受新命令并冻结状态；
3. **状态传输**：host 分段读取源控制器的状态数据，通过 Set [Controller](/concepts/controller.md) State 命令写入目的控制器；
4. **校验与提交**：目的控制器验证状态完整性后提交状态；
5. **目的端 Resume**：目的控制器恢复命令处理能力，host 更新路由信息以指向新控制器。

整个过程中，Keep Alive 机制需要被妥善管理，以避免因迁移耗时过长而触发超时断开。^[nvme-document-map.md:143, nvme-document-map.md:146-151]

## 与其他机制的关系

控制器迁移与 Controller Data Queues 机制存在交互。CDQ（Controller Data Queue）生命周期中涉及的 host-memory 队列数据需要包含在迁移状态中，UDMQ 日志记录了迁移相关的队列操作历史。^[nvme-document-map.md:54, nvme-document-map.md:61, nvme-document-map.md:206-210]

迁移完成后，Namespace Access Models 中的 ANA（Asymmetric Namespace Access）路径状态可能需要更新，以确保多路径 I/O 配置能够正确识别控制器位置的变化。^[nvme-document-map.md:77, nvme-document-map.md:129]

## 功能约束与适用性

控制器迁移功能受 [Controller](/concepts/controller.md) 类型和 I/O Command Set 支持情况的约束。规范定义了 [Controller](/concepts/controller.md) 的状态格式（Controller State Format），host 通过 Identify Command 发现控制器是否支持迁移能力以及支持的具体迁移模式。迁移仅限于同一 specification family 内的控制器之间进行，且源和目的控制器应具备兼容的 capability 轮廓。^[nvme-document-map.md:97, nvme-document-map.md:99-100]

---

## Sources

- [nvme-document-map.md](../nvme-document-map.md)

# Citations

1. [nvme-document-map.md:104-104](/references/nvme-document-map-a6b14ca3.md)
2. [nvme-document-map.md:143-143](/references/nvme-document-map-a6b14ca3.md)
3. [nvme-document-map.md:104-105](/references/nvme-document-map-a6b14ca3.md)
4. [nvme-document-map.md:105-105](/references/nvme-document-map-a6b14ca3.md)
5. [nvme-document-map.md:184-185](/references/nvme-document-map-a6b14ca3.md)
6. [nvme-document-map.md:146-151](/references/nvme-document-map-a6b14ca3.md)
7. [nvme-document-map.md:54-54](/references/nvme-document-map-a6b14ca3.md)
8. [nvme-document-map.md:61-61](/references/nvme-document-map-a6b14ca3.md)
9. [nvme-document-map.md:206-210](/references/nvme-document-map-a6b14ca3.md)
10. [nvme-document-map.md:77-77](/references/nvme-document-map-a6b14ca3.md)
11. [nvme-document-map.md:129-129](/references/nvme-document-map-a6b14ca3.md)
12. [nvme-document-map.md:97-97](/references/nvme-document-map-a6b14ca3.md)
13. [nvme-document-map.md:99-100](/references/nvme-document-map-a6b14ca3.md)
