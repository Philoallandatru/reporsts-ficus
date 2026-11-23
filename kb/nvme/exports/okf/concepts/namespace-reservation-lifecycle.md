---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 131367f87f24e97f9022a8042bf7b71370dee28486e6c7cf55ad10d576a22c59
  pageDirectory: concepts
  sources:
    - nvme-document-map.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - namespace-reservation-lifecycle
    - NRL
  citations:
    - file: nvme-document-map.md
      start: 157
      end: 158
    - file: nvme-document-map.md
      start: 201
      end: 202
title: Namespace Reservation Lifecycle
description: 多主机环境下命名空间预留机制，处理冲突时机、host-path身份、按类型划分权利、命令冲突矩阵、注册/抢占/清除与通知流程。
tags:
  - nvme
  - storage-virtualization
  - concurrency
timestamp: "2026-08-16T06:24:03.777Z"
---


# 命名空间预留生命周期（Namespace Reservation Lifecycle）

命名空间预留机制是 NVMe 规范中用于控制多主机对命名空间访问权限的核心功能。该机制确保在共享或私有访问模型下，多个主机能够协调对同一命名空间的访问，避免数据冲突和竞争条件。

## 基本概念

命名空间预留允许一个主机对特定命名空间获得独占或受控的访问权限。预留系统通过 Reservation Notification Log 记录预留变更通知，支持跨路径（multi-path）的预留管理。在分散式命名空间（dispersed namespace）场景下，预留握手协议确保参与者之间的预留状态一致性。

预留机制涉及两类记录结构：基础记录（basic registrant record）和扩展记录（extended registrant record），分别对应不同的信息完整度需求。

## 支持合约与权利层级

NVMe 规范定义了基于预留类型的差异化权利体系。控制器需要声明其对预留功能的支持能力，不同的预留类型对应不同的操作权限集合。

在冲突发生时，规范明确了各参与者的权利边界和处理规则。主机路径身份（host-path identity）用于标识发起预留操作的具体路径，这对于多路径环境下的预留管理尤为重要。

## 命令集

预留生命周期涉及以下核心管理命令：

- **Reservation Acquire**：获取预留权限
- **Reservation Register**：注册预留参与者
- **Reservation Release**：释放已获取的预留
- **Reservation Report**：查询当前预留状态

这些命令共同构成了完整的预留生命周期管理接口，支持预留的获取、注册、释放和状态查询四个主要阶段。

## 命令冲突矩阵

规范定义了各命令之间的冲突规则矩阵。当多个主机或路径同时发起冲突的预留操作时，控制器根据预设规则决定操作的执行顺序和结果。

冲突处理时机（conflict timing）是该矩阵中的关键要素，规范确保在并发场景下预留状态的一致性和可预测性。

## 抢占与中止

预留机制支持抢占（preempt）和中止（abort）操作，允许已获得预留权限的主机强制终止其他参与者的预留状态。这些操作受到严格的权限校验约束，确保只有符合条件的主机才能执行此类高权限操作。

## 清除与通知

当预留状态需要重置时，清除（clear）操作会将命名空间恢复至未预留状态。所有预留变更都会通过 Reservation Notification Log 记录，通知机制允许其他主机感知预留状态的变动。

## 与分散式命名空间的关系

在分散式命名空间中，预留机制需要跨多个参与者协调。预留握手协议确保所有参与者对预留状态的变更达成一致。预留的权利范围可扩展至跨参与者维度，支持更复杂的分布式存储场景。

## 相关概念

- Namespace Access Models：命名空间访问模型定义了共享、私有和分散式访问模式
- Namespace Management Lifecycle：命名空间管理生命周期涵盖命名空间的创建、删除和状态管理
- Reservation Notification Log：预留通知日志记录所有预留变更事件
- Dispersed Namespace Lifecycle：分散式命名空间生命周期描述分散式拓扑下的管理机制

## Sources

^[nvme-document-map.md:157-158, nvme-document-map.md:201-202]

# Citations

1. [nvme-document-map.md:157-158](/references/nvme-document-map-a6b14ca3.md)
2. [nvme-document-map.md:201-202](/references/nvme-document-map-a6b14ca3.md)
