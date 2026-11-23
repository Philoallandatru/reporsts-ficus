---
title: Controller类型与分类
summary: Controller的两维分类体系：静态/动态分配模型 × I/O/Administrative/Discovery功能类型；内存型控制器为静态，发现控制器为动态
sources:
- nvme-architecture-map.md
kind: concept
createdAt: '2026-08-16T06:17:41.176Z'
updatedAt: '2026-08-16T06:17:41.176Z'
tags:
- NVMe
- 控制器
- 资源管理
aliases:
- controller类型与分类
confidence: 0.92
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: 在 NVMe 架构中，**Controller** 是面向 [[NVM Subsystem]] 的 host 接口，承担着命令收发、队列管理以及存储资源与主机之间的协调工作。^[nvme-architecture-map.md:18]
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# [[controller|Controller]] 类型与分类

在 NVMe 架构中，**Controller** 是面向 [[NVM Subsystem]] 的 host 接口，承担着命令收发、队列管理以及存储资源与主机之间的协调工作。^[nvme-architecture-map.md:18]

## 双重分类体系

[[controller|Controller]] 的分类遵循两条相互独立的维度，两者的划分互不依赖：

### 按分配模型划分：Static 与 Dynamic

| 分配模型 | 说明 |
|---|---|
| **Static（静态）** | [[controller|Controller]] 在子系统初始化时预先分配资源，运行期间资源分配关系固定不变。Memory-based transport（如 PCIe）上的 [[controller|Controller]] 属于此类。 |
| **Dynamic（动态）** | [[controller|Controller]] 的资源分配可在运行时动态调整。Discovery [[controller|Controller]] 属于此类，其连接生命周期与资源占用随需变化。 |

这种划分直接决定了控制器实例化时机与资源管理方式。^[nvme-architecture-map.md:26]

### 按功能类型划分

| 功能类型 | 说明 |
|---|---|
| **I/O Controller** | 执行用户数据 I/O 操作，提供完整的命令处理能力。 |
| **Administrative Controller** | 仅处理管理命令，负责子系统配置、控制面操作等管理职责。 |
| **Discovery Controller** | 专用于 发现服务，在 Fabrics 拓扑中为 host 指明可达子系统的路径。^[nvme-architecture-map.md:20] |

所有类型的 [[controller|Controller]] 均保留一组公共的 **Admin Queue pair**（Submission Queue 与 Completion Queue），用于处理管理类命令。唯有 I/O [[controller|Controller]] 提供用户数据 I/O 能力。^[nvme-architecture-map.md:26]

## [[controller|Controller]] 与 Transport 的关系

[[controller|Controller]] 的分配模型与其所依赖的 transport 类型存在对应关系：

- **Memory-based transport**（例如 PCIe）：采用静态分配模型，控制器在初始化时即完成资源映射与队列配置。
- **Message-based transport**（例如 Fabrics）：采用动态分配模型，控制器通过 Connect 过程在运行时建立，并通过 Property Get/Set 访问 Controller Property 空间。^[nvme-architecture-map.md:28]

## 相关概念

- Controller Property 空间 — 与 transport 无关的公共控制面
- Controller Memory Windows — 静态 [[controller|Controller]] 的可选内存窗口机制
- Controller initialization — 控制器初始化流程
- Controller Virtualization Resources — 虚拟化环境下的 VQ/VI 资源分配
- [[Controller Migration]] — 控制器状态迁移机制
- Command arbitration — 控制器内的命令仲裁规则

---

## Sources

^[nvme-architecture-map.md:18] ^[nvme-architecture-map.md:20] ^[nvme-architecture-map.md:26] ^[nvme-architecture-map.md:28]

