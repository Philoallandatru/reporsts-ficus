---
title: Namespace and Namespace Identifier
summary: 以 logical-block 形式呈现已格式化 NVM 的存储抽象；NSID 作为控制器命令句柄，作用域为 subsystem，区分命令句柄与持久化全局标识。
sources:
- nvme-context.md
kind: concept
createdAt: '2026-08-16T06:20:29.346Z'
updatedAt: '2026-08-16T06:20:29.346Z'
tags:
- nvme
- storage
- namespace
aliases:
- namespace-and-namespace-identifier
- Namespace Identifier and Namespace
- NANI
confidence: 0.95
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: 在 NVMe Base 规范中，**Namespace（命名空间）** 是 NVMe 存储系统中的核心抽象概念，代表由一个或多个控制器以逻辑块（logical-block）存储抽象形式呈现的一块已格式化非易失性存储器（NVM）。^[nvme-context.md:42-43]
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Namespace 和 Namespace Identifier

## 概述

在 NVMe Base 规范中，**Namespace（命名空间）** 是 NVMe 存储系统中的核心抽象概念，代表由一个或多个控制器以逻辑块（logical-block）存储抽象形式呈现的一块已格式化非易失性存储器（NVM）。^[nvme-context.md:42-43]

**Namespace Identifier（命名空间标识符，NSID）** 是用于操作命名空间的控制器命令句柄，其分配作用域为整个 NVM 子系统，但在各控制器上具有独立的 active/inactive 状态。^[nvme-context.md:45-46]

## Namespace

Namespace 本质上是 NVM 子系统中的存储资源单元。从 host 的视角看，Namespace 呈现为一系列连续的逻辑块地址（LBA），host 可以通过标准的读、写等 I/O 命令对这些逻辑块进行访问。^[nvme-context.md:42-43]

Namespace 在创建时会选择恰好一个 **I/O Command Set Association**，该绑定固化了 Namespace 的数据模型与命令解释，直到该 Namespace 的整个生命周期结束。^[nvme-context.md:372-373]

### 命名空间全局标识

每个 Namespace 都拥有一个持久化的全局标识 **Namespace Global Identifier**，可以用 EUI64、NGUID 或 UUID 来表示。这种全局标识与作为命令句柄的 NSID 相区分——NSID 是动态分配给控制器的句柄，而全局标识是 Namespace 自身的永久身份。^[nvme-context.md:112-113]

对于 **Dispersed Namespace（分散命名空间）**，它可以同时通过两个或多个 participating NVM 子系统中的控制器访问。不同的 participating 子系统可能拥有不同的本地 NSID，但通过相同的 NGUID（缺失时为 UUID）来关联同一个 Dispersed Namespace。^[nvme-context.md:431-433, nvme-context.md:602-603]

### 命名空间标签

**Namespace Admin Label** 是一个以 `\0` 结尾的 UTF-8 标签，用于人类可读的 Namespace 命名。成功执行 Sanitize 操作后，此标签会被复位为全零。^[nvme-context.md:503-504]

## Namespace Identifier (NSID)

NSID 是 host 与控制器之间用于引用 Namespace 的命令句柄。在提交 I/O 命令时，host 通过 NSID 来指定操作的目标 Namespace。^[nvme-context.md:45-46]

### 分配状态

- **Allocated NSID**：指 NVM 子系统中已存在的 Namespace 所对应的有效 NSID。^[nvme-context.md:53-54]
- **Active NSID**：指已分配且对应的 Namespace 已挂接到执行此判断的控制器的 NSID。^[nvme-context.md:50-51]

### 命名空间挂接

**Namespace Attachment（命名空间挂接）** 是使一个已分配的 Namespace 在某个 I/O 控制器上处于 active 状态的持久化关系。Namespace 的挂接管理与 Namespace 的创建/删除相互独立。^[nvme-context.md:479-480]

当 Namespace 被删除时，系统会依据请求路径产生一个控制器集合，它们会上报已启用的 attached-namespace 和 allocated-namespace 变更事件。^[nvme-context.md:518-519]

## 多路径与共享

### 多路径 I/O

**Multi-Path I/O** 是指在 1 个 host 与 1 个 Namespace 之间存在两条或更多完全独立的路径。^[nvme-context.md:375-376]

### 命名空间共享

**Namespace Sharing** 是指两个或多个 host 通过不同控制器访问同一公共共享 Namespace。^[nvme-context.md:378-379]

### 导出命名空间关联

**Exported Namespace Association** 是 Exported Namespace ID 与一个已挂接 active 的底层 Namespace（Underlying Namespace）之间的映射关系，该映射独立于后续对 Exported Namespace 的控制器挂接操作。^[nvme-context.md:542-543]

## 访问控制与保护

### ANA Group

**ANA Group（非对称命名空间访问组）** 是 NVM 子系统范围内的分组，其成员 Namespace 在控制器维度上共享同一非对称访问状态（asymmetric access state），并共同发生状态变迁。^[nvme-context.md:569-570]

### [[命名空间|命名空间]] Reservation

Namespace 支持 Reservation 机制，包括以下关键概念：

- **Namespace Registrant**：已为某个 Namespace 注册了 reservation key、可参与 reservation 访问策略的 host。^[nvme-context.md:563-564]
- **Reservation Holder**：当前持有某类型命名空间 reservation 的 registrant host。^[nvme-context.md:566-567]
- **Persist Through Power Loss (PTPL)**：一种决定 reservation 与 registrants 在掉电后是否保留的命名空间 reservation 状态。^[nvme-context.md:512-513]

### 命名空间写保护

**Namespace Write Protection** 是一种由子系统强制执行的命名空间状态机，管理涉及修改介质的命令，并在进入保护状态前提交易失性命名空间数据。^[nvme-context.md:515-516]

## 相关概念

- [[NVM Subsystem]] — 包含 Namespace 的上层边界
- [[Controller]] — 呈现 Namespace 的实体
- ANA Group — 共享非对称访问状态的 Namespace 分组
- Multi-Path I/O — 同一 host 与 Namespace 间的多条独立路径
- Namespace Identifier — Namespace 的命令句柄
- I/O Command Set — 绑定到 Namespace 的命令集

## Sources

^[nvme-context.md]

