---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: cdc611695a721d900a2cf418cc2c4123174a1d899141310ae6e659788611da8b
  pageDirectory: concepts
  sources:
    - nvme-controller-initialization.md
  confidence: 0.9
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - io-队列创建顺序
  citations:
    - file: nvme-controller-initialization.md
      start: 69
      end: 71
    - file: nvme-controller-initialization.md
      start: 85
      end: 85
    - file: nvme-controller-initialization.md
      start: 69
      end: 85
title: I/O 队列创建顺序
description: NVMe 规范要求先创建完成队列（CQ）后创建提交队列（SQ），Fabrics 传输则通过 Connect 命令创建队列对（QP）。
tags:
  - NVMe
  - 队列
  - I/O
timestamp: "2026-08-16T06:21:52.047Z"
---


# I/O 队列创建顺序

在 NVMe 控制器初始化流程中，I/O 队列的创建需要遵循特定的顺序，以确保命令能正确提交和完成处理。

## 基本原则

对于基于内存的传输（如 PCIe），I/O 队列必须**先创建完成队列（CQ），后创建提交队列（SQ）**。这一顺序是强制性的，因为提交队列在创建时需要关联到对应的完成队列。 ^[nvme-controller-initialization.md:69-71]

## PCIe 传输的创建流程

基于 PCIe 的控制器在创建 I/O 队列前，需要先通过 Set Features 命令设置队列数量，并通过配置中断为后续操作做好准备。完整的创建步骤如下：

1. **设置队列数量**：通过 Set Features 协商主机与控制器之间支持的 I/O 队列数量
2. **配置中断**：设置中断聚合和向量分配
3. **创建完成队列（Create CQ）**：分配 CQ 内存并注册到控制器
4. **创建提交队列（Create SQ）**：创建 SQ 并关联到已创建的 CQ ^[nvme-controller-initialization.md:85]

## Fabrics 传输的创建流程

对于基于消息的传输（如 NVMe-oF Fabrics），I/O 队列的创建机制与 PCIe 不同。主机首先需要查询控制器能力寄存器 `CAP.MQES` 以获取最大队列深度限制，然后对每个 I/O 队列对执行 Connect 命令来建立连接。这种方式会在单个操作中同时创建提交队列和完成队列，形成队列对（Queue Pair）。 ^[nvme-controller-initialization.md:85]

## 为什么必须先创建 CQ

完成队列必须先于提交队列创建，原因在于 SQ 需要在其创建参数中指定关联的 CQ 标识符。如果 CQ 尚未存在，SQ 的创建将无法完成关联过程，可能导致命令提交后无法正确路由完成状态。 ^[nvme-controller-initialization.md:69-71]

## 相关概念

[控制器初始化](/concepts/控制器初始化.md) — I/O 队列创建是控制器初始化流程的核心步骤之一

完成队列 — 存储控制器返回的命令完成状态

提交队列 — 主机提交 I/O 命令的队列

NVMe-oF Fabrics — 基于消息传输的 [NVMe over Fabrics](/concepts/nvme-over-fabrics.md) 协议

## Sources

^[nvme-controller-initialization.md:69-85]

# Citations

1. [nvme-controller-initialization.md:69-71](/references/nvme-controller-initialization-1b5c7c04.md)
2. [nvme-controller-initialization.md:85-85](/references/nvme-controller-initialization-1b5c7c04.md)
3. [nvme-controller-initialization.md:69-85](/references/nvme-controller-initialization-1b5c7c04.md)
