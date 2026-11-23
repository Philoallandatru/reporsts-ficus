---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 68a37aac79045288971aea530dd7d7f2dd4d4cf90f6fafeada662dc9ac39c6cb
  pageDirectory: concepts
  sources:
    - nvme-command-ordering.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - 融合操作fused-operation
  citations:
    - file: nvme-command-ordering.md
      start: 53
      end: 53
    - file: nvme-command-ordering.md
      start: 7
      end: 10
    - file: nvme-command-ordering.md
      start: 57
      end: 65
    - file: nvme-command-ordering.md
      start: 69
      end: 69
    - file: nvme-command-ordering.md
      start: 70
      end: 70
    - file: nvme-command-ordering.md
      start: 75
      end: 82
    - file: nvme-command-ordering.md
      start: 85
      end: 86
    - file: nvme-command-ordering.md
title: 融合操作（Fused Operation）
description: 将两个命令绑定为原子执行单元的协议特性，两个命令要么都成功要么都不执行
tags:
  - nvme
  - 原子性
  - 命令处理
timestamp: "2026-08-16T06:19:25.402Z"
---


# 融合操作（Fused Operation）

## 概述

**融合操作**（Fused Operation）是一种可选的 NVMe 协议特性，它将两个命令绑定为一个原子执行单元。这意味着这两个命令要么都成功执行，要么都不执行，中间不会插入其他操作。^[nvme-command-ordering.md:53]

融合操作为 I/O 命令提供了原子性保证，是 NVMe 协议处理命令依赖关系的两种特殊机制之一，另一种是由特定 I/O 命令集（I/O Command Set）规范定义的命令集特定原子操作。^[nvme-command-ordering.md:7-10]

## 技术要求

融合操作必须满足以下所有条件才能正确执行：

| 要求项 | 具体规则 |
|--------|----------|
| **队列位置** | 两个命令必须占用同一个 提交队列（SQ）中的相邻条目（Entry） |
| **环绕支持** | 允许从队列的最后一个槽位环绕到第一个槽位 |
| **执行保证** | 按顺序执行，中间不会插入其他操作 |
| **完成方式** | 每个命令各自产生一个完成条目（Completion Entry） |
| **提交方式** | 必须通过单次提交操作暴露给控制器 |

^[nvme-command-ordering.md:57-65]

## 不同传输方式的提交规则

### 基于内存的队列

对于基于内存的队列（Memory-based Queue），两个融合命令通过一次尾门铃（Tail Doorbell）寄存器更新提交两个命令。^[nvme-command-ordering.md:69]

### [基于消息的传输](/concepts/基于消息的传输.md)

对于基于消息的传输（Message-based Transport），控制器需要按顺序交付两个命令，且同一 提交队列 中没有其他消息（Capsule）插入。^[nvme-command-ordering.md:70]

## 错误处理

融合操作的错误处理机制如下：

| 错误场景 | 控制器行为 |
|----------|------------|
| 请求的融合操作不受支持 | 以"命令字段无效"（Invalid Field in Command）状态中止 |
| 相邻命令缺失或格式错误 | 以"由于缺少融合命令而中止"（Command Aborted due to Missing Fused Command）状态中止非零 `FUSE` 字段的命令 |
| 第一个命令执行失败 | 中止第二个命令 |
| 第二个命令执行失败 | 第一个命令的完成状态由该融合操作定义 |
| 主机需要中止融合操作 | 必须分别为每个命令提交一个 Abort 命令 |

^[nvme-command-ordering.md:75-82]

## 规范定义

具体支持哪些原子操作以及融合操作的适用范围，由相应的 **I/O 命令集规范**（I/O Command Set Specification）定义。不同的 I/O 命令集可能定义不同的融合操作类型和语义。^[nvme-command-ordering.md:85-86]

## 相关概念

- 提交队列（Submission Queue）：融合操作中两个命令必须位于同一 SQ 中
- 完成队列（Completion Queue）：每个融合命令都会产生独立的完成条目
- 命令仲裁（Command Arbitration）：融合操作与命令仲裁机制协同工作
- 原子性（Atomicity）：融合操作是 NVMe 协议提供原子性保证的方式之一

## Sources

^[nvme-command-ordering.md]

# Citations

1. [nvme-command-ordering.md:53-53](/references/nvme-command-ordering-9a263904.md)
2. [nvme-command-ordering.md:7-10](/references/nvme-command-ordering-9a263904.md)
3. [nvme-command-ordering.md:57-65](/references/nvme-command-ordering-9a263904.md)
4. [nvme-command-ordering.md:69-69](/references/nvme-command-ordering-9a263904.md)
5. [nvme-command-ordering.md:70-70](/references/nvme-command-ordering-9a263904.md)
6. [nvme-command-ordering.md:75-82](/references/nvme-command-ordering-9a263904.md)
7. [nvme-command-ordering.md:85-86](/references/nvme-command-ordering-9a263904.md)
8. [nvme-command-ordering.md](/references/nvme-command-ordering-9a263904.md)
