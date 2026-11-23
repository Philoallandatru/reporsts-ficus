---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: df569cae9b386ff989f12dfb5448fe27640392de63208c13a063a00a1886b4e9
  pageDirectory: concepts
  sources:
    - nvme-architecture-map.md
  confidence: 0.88
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - controllermemorywindow控制器内存窗口
  citations:
    - file: nvme-architecture-map.md
      start: 30
      end: 30
    - file: nvme-architecture-map.md
      start: 78
      end: 78
    - file: nvme-architecture-map.md
title: ControllerMemoryWindow控制器内存窗口
description: 内存型控制器暴露的两种独立窗口：CMB支持queue/list/data placement；PMR具备显式的readiness与persistence-barrier契约，两者已使能地址范围不得重叠
tags:
  - NVMe
  - 内存管理
  - PCIe
timestamp: "2026-08-16T06:18:48.722Z"
---


# ControllerMemoryWindow控制器内存窗口

[Controller](/concepts/controller.md) Memory Window（控制器内存窗口，简称 CMW）是 NVMe 规范中定义的一组内存寻址机制，供 memory-based 控制器向 host 暴露可用于 I/O 操作的内存区域。^[nvme-architecture-map.md:30]^

## 概述

在 NVMe 架构中，memory-based 控制器（如 PCIe 传输的控制器）可以暴露两种相互独立的内存窗口类型，分别满足不同的数据通路和持久化需求。这两种窗口使 host 能够直接访问控制器端或控制器共享的内存资源，从而提升 I/O 效率或支持特定的高级特性。^[nvme-architecture-map.md:30]^

## 两种内存窗口类型

### CMB（Controller Memory Buffer）

CMB 是一种易失性、低延迟的内存区域，由控制器拥有并可供 host 用于以下用途：

- **Queue 放置**：存放 Submission Queue 和 Completion Queue
- **List 放置**：存放 PRP List 或 SGL Segment 等描述符结构
- **Data Placement**：存放用户 I/O 数据^[nvme-architecture-map.md:30,78]^

CMB 的典型应用场景是通过将关键数据结构放置在控制器本地内存中，减少 host 与控制器之间的内存往返延迟。

### PMR（Persistent Memory Region）

PMR 是一种具备显式语义契约的内存区域，与 CMB 相比，它提供了更严格的访问保证：

- **Readiness 契约**：定义了内存区域进入就绪状态的前置条件和时序
- **Persistence Barrier 契约**：定义了数据在掉电或异常情况下的持久化保证^[nvme-architecture-map.md:30]^

PMR 适用于需要明确数据持久化边界的场景，例如日志写入或需要确保数据落盘的元数据操作。

## 地址范围约束

一个控制器可以同时使能 CMB 和 PMR，但**两者已使能的控制器地址范围不得重叠**。这一约束确保了两种内存窗口在地址空间上的独立性和可预测性。^[nvme-architecture-map.md:30]^

## 相关概念

- Controller Properties：与传输无关的公共控制面，Controller Memory Window 的配置通过 Property 空间进行访问
- Controller initialization：控制器初始化过程中涉及 Admin Queue 属性的配置
- Data Pointer Layouts（PRP 与 SGL）：使用 CMB 存放的描述符类型
- Controller Data Queues：可在 CMB 中放置的队列结构
- Host Memory Buffer（HMB）：另一种 PCIe 内存设施，与 CMB 同属控制器内存体系

## Sources

^[nvme-architecture-map.md]

# Citations

1. [nvme-architecture-map.md:30-30](/references/nvme-architecture-map-f141b52c.md)
2. [nvme-architecture-map.md:78-78](/references/nvme-architecture-map-f141b52c.md)
3. [nvme-architecture-map.md](/references/nvme-architecture-map-f141b52c.md)
