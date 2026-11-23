---
title: SSD 领域专利查询启动器
summary: FTL/GC/Wear Leveling、PLP/掉电保护、LDPC/软解码、SLC Cache/pSLC、Placement/FDP、NAND
  Disturb/Retention 等六大主题的专利查询模板与关键词策略
sources:
- research-nand-controller-patent-notes.md
kind: concept
createdAt: '2026-08-16T05:52:26.838Z'
updatedAt: '2026-08-16T05:52:26.838Z'
tags:
- patent
- query-template
- ssd
aliases:
- ssd-领域专利查询启动器
confidence: 0.9
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: 本页面整理了 SSD 固件与硬件设计背景下的专利查询入口、分类体系和可复用查询语句。其目标是帮助研究者在进入具体专利挖掘之前，先建立一套有结构的起点，而不是随机浏览专利数据库。
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# SSD 领域专利查询启动器

本页面整理了 SSD 固件与硬件设计背景下的专利查询入口、分类体系和可复用查询语句。其目标是帮助研究者在进入具体专利挖掘之前，先建立一套有结构的起点，而不是随机浏览专利数据库。

本启动器与 控制器硬件模块边界 和 控制器 RTL / IP 参考 共同构成 SSD 技术调研的三条主线：硬件边界定义接口、RTL 参考映射实现细节、专利查询追踪创新来源。

## 1 专利查询工具

| 工具 | 适用场景 | 入口 |
|---|---|---|
| Google Patents 高级搜索 | 快速发现、 assignee 过滤、CPC 过滤、引用链追踪、机器翻译 | https://www.google/advanced_patent_search |
| USPTO Patent Public Search | 权威美国专利检索入口，包含基础和高级搜索 | https://www.uspto.gov/patents/search/patent-public-search |
| USPTO Patent Center | 按申请号、专利号、PCT 号或公开号查询申请状态和文件 | https://patentcenter.uspto.gov/search |

Google Patents 适合做第一轮广度发现，USPTO Patent Center 适合确认法律状态和审查历史。^[research-nand-controller-patent-notes.md:34-36]

## 2 CPC 分类体系

SSD 相关专利主要分布在以下 CPC 类目：

| CPC 类目 | 覆盖范围 | 查询注意事项 |
|---|---|---|
| **G06F 3/06** | SSD 控制器、固件、FTL、GC、磨损均衡、命名空间、流写入、放置策略 | G06F 类目较宽，需配合 "solid state drive"、"flash translation layer"、"garbage collection"、"wear leveling"、"write amplification" 等关键词过滤。^[research-nand-controller-patent-notes.md:38-39] |
| **G06F 12/00** | 内存寻址与分配，与 FTL 映射表、缓存、放置有重叠 | 非 SSD 专用类目，需配合 "NAND"、"SSD"、"FTL" 减少无关结果。^[research-nand-controller-patent-notes.md:39] |
| **G11C 16/00** | 可擦除可编程只读存储器，包含 NAND 编程/读取/擦除、干扰、保持、磨损机制 | 更偏重存储器件内部结构，与控制器发明组合查询效果更好。^[research-nand-controller-patent-notes.md:41-42] |
| **H03M 13** | LDPC、BCH、Reed-Solomon、软判决解码、迭代解码、速率兼容 LDPC | 通信导向结果较多，需配合 "NAND"、"flash memory"、"SSD controller"、"read retry" 约束。^[research-nand-controller-patent-notes.md:43] |
| **H10B** | 半导体/固态存储器件结构，3D NAND 核心/外围/阶梯结构 | 器件结构导向，可能遗漏固件、主机接口和系统级 SSD 专利。^[research-nand-controller-patent-notes.md:42] |

CPC 符号经常修订，建议在 intake 时记录 CPC 版本和查询日期。^[research-nand-controller-patent-notes.md:37]

## 3 关键主题种子专利

以下专利可作为各主题的种子文档，通过引用链和家族链接扩展检索范围：

| 主题 | 种子专利 | 说明 |
|---|---|---|
| FTL / GC / 磨损均衡 | US20120317377A1 | 明确讨论 FTL 行为、块压缩、动态/静态磨损均衡和逻辑到物理重映射。^[research-nand-controller-patent-notes.md:44] |
| 掉电保护 (PLP) | US20170185335A1 | 明确描述 SSD 掉电保护、备用电源和易失性缓冲刷新行为。^[research-nand-controller-patent-notes.md:45] |
| SLC 缓存 | US20220129168A1 | 明确覆盖 SLC 存储单元作为 MLC 容量交换的高速缓存策略。^[research-nand-controller-patent-notes.md:46] |
| LDPC 可靠性监控 | US8413029B2 | 明确讨论 LDPC 解码、纠错统计和存储设备误码率观测。^[research-nand-controller-patent-notes.md:47] |
| 灵活数据放置 (FDP) | US12405729B2 | 明确引用 FDP、回收单元、句柄和设备级 GC 影响。^[research-nand-controller-patent-notes.md:48] |

种子专利的价值在于提供关键词、 assignee 、CPC 符号和引用链，而非覆盖完整主题分类。^[research-nand-controller-patent-notes.md:44-48]

## 4 可复用查询语句

以下查询可直接用于 Google Patents，覆盖 SSD 领域核心议题：

| 主题 | 查询语句 | 覆盖范围 | 注意事项 |
|---|---|---|---|
| FTL / GC / 磨损均衡 | `flash translation layer SSD "garbage collection" "wear leveling"` | FTL 映射、GC、压缩、磨损均衡专利 | 可重复使用 "logical to physical"、"mapping table"、"valid page"、"block compaction" 变体。^[research-nand-controller-patent-notes.md:55] |
| PLP / 掉电保护 | `"solid state drive" "power loss protection" capacitor flush` | SSD PLP 硬件能量储备和固件刷新/关机行为 | 变体词包括 "sudden power off recovery"、"SPOR"、"power fail"、"backup power"。^[research-nand-controller-patent-notes.md:56] |
| LDPC / 软判决解码 | `NAND LDPC "soft decoding" "read retry"` | NAND 可靠性、ECC 和控制器读恢复管道 | 需配合 NAND、flash memory、SSD controller 或 G06F/G11C 类目约束，避免通信类专利。^[research-nand-controller-patent-notes.md:57] |
| SLC 缓存 / pSLC | `"SLC cache" SSD TLC QLC "pseudo-SLC"` | 以 SLC 模式编程多比特单元换取写性能的控制器策略 | 许多专利避免 "SLC cache" 表述，建议补充 "single level mode"、"folding"、"hybrid cache"。^[research-nand-controller-patent-notes.md:58] |
| 放置 / FDP / 流 | `"flexible data placement" SSD "reclaim unit" "placement identifier"` | 现代主机导向放置和与内部 GC、写放大交互的 FDP 类接口 | 老专利可能使用 "write stream"、"data temperature"、"hot/cold data"、"host hint"。^[research-nand-controller-patent-notes.md:59] |
| NAND 器件 / 干扰 / 保持 | `"NAND flash" "threshold voltage" disturb retention "read retry"` | 控制器固件必须补偿的低层器件行为 | 可能检索到器件/电路专利，建议配合 G11C/H10B 与 G06F 组合。^[research-nand-controller-patent-notes.md:60] |

## 5 Intake 标签体系

为保持知识库可追溯性，建议对采集的专利资料使用以下标签：

| 标签前缀 | 用途 | 示例 |
|---|---|---|
| `vendor/{vendor}/nand` | 原始 NAND 器件页面、代际说明、数据表、技术笔记 | `vendor/micron/nand`、`vendor/kioxia/bics`、`vendor/skhynix/4d-nand` |
| `vendor/{vendor}/v-nand` | 特定厂商的 V-NAND / BiCS / Xtacking 等架构说明 | `vendor/samsung/v-nand`、`vendor/wd-sandisk/bics` |
| `patent/cpc/{symbol}` | 按 CPC 类目归档的专利检索结果 | `patent/cpc/g06f-3-06`、`patent/cpc/h03m-13` |
| `patent/topic/{topic}` | 按 SSD 设计问题聚类的专利集合 | `patent/topic/plp`、`patent/topic/slc-cache`、`patent/topic/fdp-placement` |

^[research-nand-controller-patent-notes.md:62-78]

## 6 与其他知识库页面的关系

本启动器处于调研流程的上游，其产出应流向以下页面：

- 控制器硬件模块边界：专利中披露的模块划分可与知识库已有的前端/后端模块表对照。
- 控制器 RTL / IP 参考：专利中的接口描述可与 AMD PG329、Cosmos+ 等公开参考设计交叉验证。
- DRAM-less SSD 与 Host Memory Buffer：HMB 相关专利可补充知识库中未覆盖的主机侧内存借用策略。
- ECC、LDPC 与可靠性管理：LDPC 专利与知识库中的 retry ladder、软判决路径直接对应。
- 控制器厂商数据采集与建模：专利 assignee 可用于补充 vendor intake 中的产品路线图。

## 7 常见误区

- 把 marketing feature list 当成可实现接口，专利描述同样存在选择性披露问题。
- 把专利中的模块名称直接映射为 RTL 模块边界，实际实现可能有很大差异。
- 把 "enterprise" 或 "client" 当成统一功能集合，不区分具体代际和地区家族。
- 忽略 CPC 修订：同一发明在不同时期的 CPC 分类可能不同。
- 只看单一 assignee，忽略了初创公司和学术机构的创新。

## Sources

- [research-nand-controller-patent-notes.md](../../sources/research-nand-controller-patent-notes.md)

