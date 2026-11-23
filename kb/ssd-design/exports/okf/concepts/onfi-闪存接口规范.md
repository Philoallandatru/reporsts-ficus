---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: d3e65c20515d40d2ad192d2f4fca6bf8427498498d692e379a26cfdf96c9f3e9
  pageDirectory: concepts
  sources:
    - source-catalog-3e9312b0.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - onfi-闪存接口规范
  citations:
    - file: source-catalog-3e9312b0.md
      start: 18
      end: 19
title: ONFI 闪存接口规范
description: Open NAND Flash Interface 规范定义 NAND 器件的命令、地址、数据、电气和时序模型，是 NAND 介质与控制器接口的权威标准。
tags:
  - 标准规范
  - NAND
  - 接口协议
timestamp: "2026-08-16T06:00:16.484Z"
---


# ONFI 闪存接口规范

## 概述

ONFI（Open NAND Flash Interface）是一套由 ONFI 工作组制定的开放标准，旨在标准化 NAND Flash 器件的命令、地址、数据传输、电气特性和时序模型。 ^[source-catalog-3e9312b0.md:18-19]

ONFI 规范的主要作用是降低 SSD 控制器与不同厂商 NAND Flash 之间的集成复杂度。通过统一的接口定义，控制器设计者可以在不修改固件的情况下，使用来自不同供应商的 NAND 器件。 ^[source-catalog-3e9312b0.md:18-19]

## 规范覆盖范围

ONFI 规范定义了以下几个层面的标准：

| 层面 | 说明 |
|---|---|
| **命令集** | 读、写、擦除、状态查询等操作的标准化命令码和协议 |
| **地址格式** | 行地址（block、page）与列地址（byte within page）的编码方式 |
| **数据传输** | 数据总线的宽度、传输时序和突发模式 |
| **电气特性** | 信号完整性、电源要求、I/O 电平标准 |
| **时序模型** | 命令发出到数据返回的各阶段延迟参数 |

这些定义共同构成了控制器与 NAND 介质之间可靠通信的基础。

## 在 SSD 架构中的位置

ONFI 规范位于 SSD 控制器硬件边界的**后端模块**层级。控制器通过 NAND PHY/Controller 模块与 NAND 介质交互，该模块的实现必须符合 ONFI 规范定义的时间参数和协议序列。 ^[source-catalog-3e9312b0.md:18-19]

SSD 控制器固件在执行 Flash I/O 时，涉及以下与 ONFI 相关的关键操作：

- 通过命令/地址/数据周期与 NAND 通信
- 监控 ready/busy 信号以判断操作完成状态
- 处理 program fail、erase fail 等错误状态
- 读取和解析 NAND 的 ID 参数页

## 规范版本演进

ONFI 标准随着 NAND 技术的发展持续更新。规范版本记录在 [ONFI 官方规范页面](https://onfi.org/specs.html)，包含各代际的时序改进和新增功能定义。

不同 ONFI 版本通常会在以下方面有所差异：

- 最大传输速率
- 异步/同步切换机制
- 多 plane 操作支持
- DDR 时序参数

## 与其他标准的关系

ONFI 定义的是**设备侧** NAND 接口规范，而主机侧的存储协议（如 NVMe）通过 SSD 控制器与 ONFI 接口衔接。这一关系在 SSD 控制器硬件模块边界的分层设计中得以体现。 ^[source-catalog-3e9312b0.md:18-19]

JEDEC 标准（如 JESD230G）则从系统层面定义了 NAND Flash 接口的互操作性要求，可与 ONFI 规范相互参照。

## 固件开发要点

基于 ONFI 规范进行 SSD 固件开发时，需关注以下方面：

- **时序合规**：严格按照规范中的 tR、tPROG、tBERS 等参数控制命令间隔
- **错误处理**：根据 ONFI 定义的 status register 位判断操作结果
- **多 die 操作**：如支持 multi-die/plane 并发，需遵循规范中的交错时序要求
- **参数页解析**：通过读取 NAND ONFI parameter page 获取器件能力

## 相关概念

- NAND Flash — ONFI 所规范的底层存储介质
- 控制器硬件模块边界 — SSD 控制器各模块的职责划分，ONFI 接口属于后端 PHY/Controller 层级
- ECC、LDPC 与可靠性管理 — NAND 数据通路上的纠错机制，与 ONFI 数据传输紧密相关
- Flash Scheduler、Channel/Die/Plane Arbitration 与 Read Priority — 基于 ONFI 接口实现的调度策略

## 关键来源

- [ONFI Specifications](https://onfi.org/specs.html) — 规范的官方发布页面
- [NVM Express Specifications](https://nvmexpress.org/specifications/) — 主机侧存储协议标准
- [JEDEC JESD230G](https://www.jedec.org/) — NAND Flash 接口互操作性标准
- [控制器硬件模块边界](controller-hardware-module-boundaries.md) — SSD 控制器模块划分

# Citations

1. [source-catalog-3e9312b0.md:18-19](/references/source-catalog-3e9312b0-99ccdd71.md)
