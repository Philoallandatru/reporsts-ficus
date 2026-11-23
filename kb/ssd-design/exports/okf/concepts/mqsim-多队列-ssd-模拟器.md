---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 014c392843658a6b13dd513c8805ada34338e21f3dc02bf2acf805ed9a0dc828
  pageDirectory: concepts
  sources:
    - research-source-catalog.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - mqsim-多队列-ssd-模拟器
    - M多S模
  citations:
    - file: research-source-catalog.md
      start: 77
      end: 78
title: MQSim 多队列 SSD 模拟器
description: 针对现代多队列 NVMe/SATA SSD 的性能建模模拟器，聚焦延迟和多队列调度研究
tags:
  - 仿真工具
  - 多队列建模
  - 延迟分析
timestamp: "2026-08-16T05:56:05.181Z"
---


# MQSim 多队列 SSD 模拟器

MQSim 是由卡内基梅隆大学 SAFARI 研究组开发的一款开源 NVMe/SATA SSD 模拟器，专注于现代多队列存储系统的性能建模与实验评估。该项目托管于 GitHub，其核心设计成果发表于 USENIX FAST '18 会议。

## 背景与定位

SSD 模拟器在存储系统研究中扮演重要角色，帮助研究者在不依赖真实硬件的情况下探索 FTL 算法、调度策略、队列调度和性能瓶颈。MQSim 的设计目标是为 NVMe 和 SATA 两种主流主机接口下的 SSD 提供精确的多队列建模能力，重点关注现代 SSD 内部并行度、队列调度延迟和端到端 I/O 延迟的模拟精度。^[research-source-catalog.md:77-78]

## 主要功能与特性

MQSim 支持对 NVMe 和 SATA 两种接口协议的 SSD 进行模拟。模拟器内置了 NAND flash 通道（channel）、芯片（die）、晶片（plane）和块（block）等物理并行层级的建模，能够模拟 SSD 内部的多级并行结构以及由此产生的资源竞争和调度延迟。^[research-source-catalog.md:77-78]

在多队列建模方面，MQSim 精确模拟了 NVMe 多队列（Multi-Queue）机制的排队行为，包括主机侧提交队列（Submission Queue）与完成队列（Completion Queue）的门铃（doorbell）交互、队列深度变化以及并发命令的执行路径。

模拟器还提供了可配置的延迟模型，覆盖 NAND 读写延迟、通道争用延迟和内部调度开销等关键路径，便于开展不同工作负载下的性能评估。

## 学术来源

MQSim 由卡内基梅隆大学（CMU）SAFARI 研究组开发并维护，相关论文发表于 USENIX FAST 2018。研究者可通过该论文深入了解 MQSim 的架构设计、验证方法以及与真实硬件的对标结果。^[research-source-catalog.md:77-78]

## 与同类工具的关系

在 SSD 仿真领域，MQSim 与 FEMU、SimpleSSD、FlashSim 等工具存在功能上的交叉与互补关系。研究目录中将这些工具并列收录，便于研究者根据实验需求选择合适的仿真平台：

| 模拟器 | 特点 | 典型用途 |
|---|---|---|
| MQSim | 多队列 NVMe/SATA 建模、精确延迟 | 存储系统性能评估、FTL 算法研究 |
| FEMU | QEMU/KVM 集成、Blackbox 模式 | 快速实验、非精确 NAND 时序 |
| SimpleSSD | 全系统集成（gem5） | 完整系统仿真、CPU-存储协同设计 |
| FlashSim | 早期 NAND 模拟、FTL 算法对比 | 教学与经典 FTL 算法原型 |

MQSim 与 FEMU、SimpleSSD 被并列为控制器和仿真行为对照的重要参考工具，可用于交叉验证命令生命周期、FTL 抽象、延迟与队列行为。^[research-source-catalog.md:77-78]

## 使用方式

MQSim 的源代码托管于 GitHub 公开仓库，研究者可通过官方仓库获取源码、参数配置文件以及使用文档。在使用时应注意结合 FAST '18 论文理解其精度边界和适用场景。

## 参见

- FEMU QEMU NVMe SSD 模拟器 — 基于 QEMU/KVM 的 NVMe SSD 仿真环境
- SimpleSSD 全系统 SSD 模拟器 — 与 gem5 集成的全系统 SSD 模拟平台
- FlashSim NAND SSD 模拟器 — 早期 NAND SSD 模拟与 FTL 算法对比工具

## Sources

- [^1]: 研究来源目录 — MQSim 官方仓库与 FAST '18 论文条目 ^[research-source-catalog.md:77-78]

# Citations

1. [research-source-catalog.md:77-78](/references/research-source-catalog-b219c498.md)
