---
title: 未完成命令（Outstanding Commands）
summary: 从提交到控制器到收到完成条目之间的命令状态，以及协议定义的终止条件
sources:
- nvme-command-ordering.md
kind: concept
createdAt: '2026-08-16T06:19:58.154Z'
updatedAt: '2026-08-16T06:19:58.154Z'
tags:
- nvme
- 命令生命周期
- 资源管理
aliases:
- 未完成命令outstanding-commands
confidence: 0.95
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: 在 NVMe 协议中，**未完成命令**（Outstanding Command）是指从主机提交给控制器开始，直到命令处理终止并被证明为止，仍处于等待完成状态的命令。理解未完成命令的边界定义对于资源管理、错误恢复和系统关机流程都至关重要。^[nvme-command-ordering.md:160-163]
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 未完成命令（Outstanding Commands）

## 概述

在 NVMe 协议中，**未完成命令**（Outstanding Command）是指从主机提交给控制器开始，直到命令处理终止并被证明为止，仍处于等待完成状态的命令。理解未完成命令的边界定义对于资源管理、错误恢复和系统关机流程都至关重要。^[nvme-command-ordering.md:160-163]

## 边界定义

一个命令从**提交到控制器**的那一刻起，直到满足以下任一条件之前，都处于未完成状态：

1. **正常完成**：主机收到该命令在完成队列（Completion Queue）中的完成条目
2. **协议定义的证明**：通过其他协议机制证明该命令的处理已经终止 ^[nvme-command-ordering.md:160-163]

这种设计确保了主机软件能够准确追踪每个命令的生命周期，无论命令是成功完成还是因各种原因被终止。^[nvme-command-ordering.md:180-185]

## 命令终止的协议证明

NVMe 协议定义了多种可以作为命令处理终止有效证明的场景：

| 终止方式 | 适用场景 | 说明 |
|---------|---------|------|
| **中止成功** | 所有命令 | 通过 中止命令（Abort 命令）成功中止目标命令 |
| **取消成功** | 支持取消的命令 | 通过 Cancel 操作成功取消目标命令 |
| **控制器状态变更** | 非 Fabrics 命令 | 观察到控制器进入"未就绪"或"关机完成"状态 |
| **队列删除** | 基于内存的 提交队列 | 删除命令所在的提交队列 |
| **连接断开** | Fabrics 传输 | Fabrics Disconnect 成功断开承载该 I/O 队列的连接 |
| **通信恢复** | 通信丢失后 | 在通信丢失后重新与同一控制器建立通信 ^[nvme-command-ordering.md:167-177] |

### 关键说明

- **中止命令（Abort）**：如果主机需要中止某个融合操作中的命令，必须分别为每个命令提交一个 Abort 命令 ^[nvme-command-ordering.md:82]
- **控制器状态变更**：仅适用于非 Fabrics 传输场景，Fabrics 环境需要通过连接断开来证明 ^[nvme-command-ordering.md:173, nvme-command-ordering.md:175-176]
- **队列删除**：仅限于基于内存的提交队列，这是因为基于消息的传输方式（如 Fabrics）有不同的命令隔离机制 ^[nvme-command-ordering.md:174]

## 实践意义

理解未完成命令的边界对以下场景非常重要：

- **资源管理**：主机需要追踪有多少命令处于未完成状态，以便合理分配内存缓冲区和系统资源
- **错误恢复**：当发生错误或通信中断时，主机需要确定哪些命令需要重试或清理
- **系统关机**：确保所有未完成命令得到妥善处理后再关闭系统，避免数据丢失或命令悬挂 ^[nvme-command-ordering.md:180-185]

## 相关概念

- 命令排序与仲裁：了解命令的处理流程和仲裁机制
- 提交队列（Submission Queue）：命令的提交载体
- 完成队列（Completion Queue）：命令完成的通知机制
- 融合操作（Fused Operation）：特殊的原子命令执行方式
- 中止命令（Abort Command）：强制终止命令的机制

## 规范参考

NVMe 规范对未完成命令的终止条件有详细定义，这些内容主要位于规范的第 123-124 页。协议通过这些明确的边界定义，为主机软件提供了可靠的状态判断依据。^[nvme-command-ordering.md:186]

---

## Sources

- [命令排序与仲裁 - NVMe 命令处理与未完成命令边界定义](../_source/nvme-command-ordering.md)

