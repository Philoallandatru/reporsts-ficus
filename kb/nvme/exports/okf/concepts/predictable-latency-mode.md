---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: e3207de08d318c9f723db2ac36817d902f56d36cdb3d480a9ff2f4b2d58631f4
  pageDirectory: concepts
  sources:
    - nvme-context.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - predictable-latency-mode
    - PLM
  citations:
    - file: nvme-context.md
      start: 282
      end: 283
    - file: nvme-context.md
      start: 623
      end: 624
    - file: nvme-context.md
      start: 626
      end: 627
    - file: nvme-context.md
      start: 651
      end: 652
    - file: nvme-context.md
title: Predictable Latency Mode
description: NVM Set 运行模式，在 Deterministic Window（确定性延迟保证）与 Non-Deterministic Window（准备阶段）之间交替，以提供有界的 I/O 延迟。
tags:
  - nvme
  - latency
  - performance
  - nvm-set
timestamp: "2026-08-16T06:20:52.245Z"
---


# Predictable Latency Mode

Predictable Latency Mode（可预测延迟模式）是一种 NVM Set 运行模式，在两个交替阶段之间切换：一个是有界的 Deterministic Window（确定性窗口），另一个是面向准备的 Non-Deterministic Window（非确定性窗口）。

^[nvme-context.md:282-283]

## Deterministic Window（确定性窗口）

在 Deterministic Window 期间，一个 NVM Set 在 host 消耗未超过所报告预算时，能够提供确定性的读/写延迟。这意味着 host 可以对 I/O 操作的响应时间做出可靠的预测，适用于对延迟敏感的应用场景。 ^[nvme-context.md:623-624]

## Non-Deterministic Window（非确定性窗口）

Non-Deterministic Window 是面向准备的阶段，在此期间系统进行内部维护或资源准备操作，可能导致延迟不可预测。该阶段的存在确保了确定性窗口期间能够维持稳定的性能表现。

## 相关特性

### Read Recovery Level（读恢复级别）

Read Recovery Level 是一种 NVM Set 属性，用于在读完成时间与恢复开销之间进行权衡。恢复级别从可选的最大恢复到强制的 Fast Fail 依次排序，host 可根据应用需求选择合适的级别。 ^[nvme-context.md:626-627]

### SQ Association（提交队列关联）

在 I/O [Queue Pair](/concepts/queue-pair.md) 创建时，可以指定一个可选的 SQ Association hint，命名一个 NVM Set。该 NVM Set 的 namespace 应优先使用本队列，以维持 Predictable Latency 行为。 ^[nvme-context.md:651-652]

## 应用场景

Predictable Latency Mode 主要用于需要严格延迟保证的场景，例如实时系统、金融交易处理或工业控制应用。通过在确定性窗口期间提供可预测的延迟，host 软件能够做出精确的时间安排和资源调度决策。

## 参见

- NVM Set
- Deterministic Window
- Read Recovery Level
- [Queue Pair](/concepts/queue-pair.md)
- Endurance Group

## Sources

^[nvme-context.md]

# Citations

1. [nvme-context.md:282-283](/references/nvme-context-d9974722.md)
2. [nvme-context.md:623-624](/references/nvme-context-d9974722.md)
3. [nvme-context.md:626-627](/references/nvme-context-d9974722.md)
4. [nvme-context.md:651-652](/references/nvme-context-d9974722.md)
5. [nvme-context.md](/references/nvme-context-d9974722.md)
