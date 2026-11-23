---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 03c070fad5bf3cbd9edfec28916499697567b6a4776583ca5244732b17242b3c
  pageDirectory: concepts
  sources:
    - research-nand-controller-patent-notes.md
  confidence: 0.85
  provenanceState: inferred
  freshnessStatus: fresh
  aliases:
    - ymtc-xtacking-架构
    - YX架
  citations:
    - file: research-nand-controller-patent-notes.md
      start: 24
      end: 24
    - file: research-nand-controller-patent-notes.md
      start: 23
      end: 25
    - file: research-nand-controller-patent-notes.md
      start: 23
      end: 23
    - file: research-nand-controller-patent-notes.md
      start: 25
      end: 25
    - file: research-nand-controller-patent-notes.md
title: YMTC Xtacking 架构
description: 长江存储自研的存储阵列与外围电路分离式 3D NAND 架构，及其对系统级性能与定制化 NAND 方案的影响
tags:
  - ymtc
  - xtacking
  - nand-architecture
  - 3d-nand
timestamp: "2026-08-16T05:52:54.433Z"
---


# YMTC Xtacking 架构

YMTC Xtacking 是长江存储（Yangtze Memory Technologies Co., Ltd.）为其 3D NAND 闪存开发的一种核心架构技术。该架构通过将 NAND Cell Array（存储阵列）和 CMOS Peripheral Circuit（CMOS 外围电路）在晶圆级别分离制造后进行键合，实现了两部分电路的独立优化。^[research-nand-controller-patent-notes.md:24]

## 架构设计原理

传统 3D NAND 采用在同一晶圆上连续形成存储阵列和外围电路的方式，限制了工艺节点的独立选择。Xtacking 架构的核心创新在于采用 wafer-to-wafer（晶圆对晶圆）键合工艺，将存储阵列晶圆与外围电路晶圆分别制造后进行面对面键合。^[research-nand-controller-patent-notes.md:24]

这种分离设计允许存储阵列和外围电路各自采用最适合自身的工艺节点。存储阵列可专注于提升存储密度和堆叠层数，外围电路则可采用更先进或更定制化的晶体管工艺以优化速度和功耗。^[research-nand-controller-patent-notes.md:24]

## 技术特点

| 特性 | 说明 |
|---|---|
| 晶圆键合 | 采用晶圆对晶圆键合工艺实现存储阵列与外围电路的集成 |
| 独立工艺优化 | 两部分电路可选择各自最优的制造工艺 |
| 系统级性能提升 | 直接影响 NAND 读写吞吐量 |
| 定制化 NAND 方案 | 支持针对不同应用场景的定制化设计 |

## Xtacking 代际与产品

YMTC 已推出多代 Xtacking 技术，并基于该架构推出了多个 NAND 产品系列。^[research-nand-controller-patent-notes.md:23-25]

### 产品系列

- **X4 系列**：QLC（Quad-Level Cell）产品线，包括 X4-9060、X4-9070、X4-6080 等型号
- **X3 系列**：TLC（Triple-Level Cell）产品线，包括 X3-9070、X3-6070 等型号

这些产品均基于 Xtacking 架构制造，体现了该技术在商业化量产中的应用。^[research-nand-controller-patent-notes.md:23]

## 在 SSD 产品中的应用

YMTC 的 Xtacking NAND 已应用于多种 SSD 产品。例如 PC300 系列是一款支持 PCIe 4.0 NVMe 的 SSD，采用了 HMB（Host Memory Buffer）和 SLC Cache 技术，并基于 Xtacking NAND。^[research-nand-controller-patent-notes.md:25]

Xtacking 架构对 SSD 产品的直接益处体现在更高的接口传输速率和更好的系统级性能表现。^[research-nand-controller-patent-notes.md:24]

## 已知局限

公开的 Xtacking 技术资料主要为架构层面的概述性介绍，详细的 Die 级别时序参数、命令集定义、可靠性规格以及控制器兼容性信息尚未全面公开。在进行控制器设计或固件开发时，不宜从公开材料直接推断精确的接口时序、晶圆键合良率数据或控制器对接细节，应结合实际产品规格书和器件 datasheet 进行确认。^[research-nand-controller-patent-notes.md:24]

## 相关概念

- NAND 介质参数手册：如需进行控制器设计对接，需要获取 NAND 器件的具体时序和参数
- 控制器硬件模块边界：将 NAND 接口集成到 SSD 控制器时需要关注的模块边界
- ECC、LDPC 与可靠性管理：与 NAND 可靠性管理相关的控制器设计考量
- DRAM-less SSD 与 Host Memory Buffer：HMB 等技术在 Xtacking NAND SSD 中的应用

## 来源

^[research-nand-controller-patent-notes.md]

# Citations

1. [research-nand-controller-patent-notes.md:24-24](/references/research-nand-controller-patent-notes-8985793f.md)
2. [research-nand-controller-patent-notes.md:23-25](/references/research-nand-controller-patent-notes-8985793f.md)
3. [research-nand-controller-patent-notes.md:23-23](/references/research-nand-controller-patent-notes-8985793f.md)
4. [research-nand-controller-patent-notes.md:25-25](/references/research-nand-controller-patent-notes-8985793f.md)
5. [research-nand-controller-patent-notes.md](/references/research-nand-controller-patent-notes-8985793f.md)
