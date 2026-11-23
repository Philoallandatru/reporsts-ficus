---
title: 主流 NAND 技术路线图
summary: BiCS FLASH（Kioxia/Sandisk）、V-NAND（Samsung）、4D NAND（SK hynix）、Xtacking（YMTC）四大
  3D NAND 架构流派及其公开资料入口
sources:
- research-nand-controller-patent-notes.md
kind: concept
createdAt: '2026-08-16T05:52:17.011Z'
updatedAt: '2026-08-16T05:52:17.011Z'
tags:
- nand-vendor
- 3d-nand
- technology-taxonomy
aliases:
- 主流-nand-技术路线图
- 主N技
confidence: 0.9
provenanceState: merged
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: 本文整理目前公开资料中主流 NAND 原厂的技术路线图，重点覆盖 3D NAND 的层数演进、接口速率、架构创新和主要厂商的技术定位。所有事实均来自各厂商官方发布页面、官方新闻稿或官方专利/技术说明页面；未进入公开资料的内容不做推断。
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 主流 NAND 技术路线图

本文整理目前公开资料中主流 NAND 原厂的技术路线图，重点覆盖 3D NAND 的层数演进、接口速率、架构创新和主要厂商的技术定位。所有事实均来自各厂商官方发布页面、官方新闻稿或官方专利/技术说明页面；未进入公开资料的内容不做推断。

## 技术演进维度

3D NAND 技术路线图主要沿以下几条轴线展开：

| 演进轴 | 说明 |
|---|---|
| **层数** | 从早期 32/48 层发展到当前 200+ 层至 300+ 层，层数直接影响存储密度和单位成本 |
| **接口速率** | 从 Toggle 2.0 / ONFI 3.0 的约 400 MT/s 演进到 Toggle 5.1 的 3.2 GT/s 和 4.8 GT/s |
| **Cell 类型** | SLC → MLC → TLC → QLC → PLC，位密度逐步提升，但写入寿命和延迟相应下降 |
| **架构创新** | 各厂商的独特外围电路布局和 3D 结构方案，如 Xtacking（YMTC）、4D NAND（SK hynix）、V-NAND（Samsung）等 |
| **接口协议** | ONFI 与 Toggle DDR 两大阵营各自迭代，PCIe 5.0/6.0 对 NVMe SSD 的带宽需求反向推动 NAND 接口升级 |

## 主要厂商技术路线

### Samsung V-NAND

Samsung 采用 **charge trap flash (CTF)** 结构的 **V-NAND** 技术路线，通过在垂直通道孔中堆叠 NAND 字符串来提升密度并降低 cell 间干扰。V-NAND 9（第 9 代）已实现 1 Tb TLC 容量，接口为 Toggle 5.1，速率最高可达 **3.2 GT/s**，并已支持 PCIe 5.0 SSD 的带宽需求。 ^[research-nand-controller-patent-notes.md:17-18]

Samsung 官方技术博客将 V-NAND 的结构要点总结为：charge trap 取代传统浮栅、channel hole（通道孔）垂直堆叠、cell 干扰控制和代际间的读写延迟与功耗优化。 ^[research-nand-controller-patent-notes.md:17] 但这些博客属于工程解说而非数据手册，具体的 ONFI/Toggle 时序参数、read-retry 表格和 ECC 预算需要查阅官方产品数据表。 ^[research-nand-controller-patent-notes.md:18]

### Kioxia / Western Digital / Sandisk BiCS FLASH

Kioxia 与 Sandisk（原 Western Digital闪存部门）联合开发 **BiCS FLASH** 系列，当前已演进到 **BiCS10**。Sandisk 2026 年 7 月发布的 BiCS10 TLC 公开参数显示接口速率达 **4.8 Gb/s**，并强调位密度和功耗优化。 ^[research-nand-controller-patent-notes.md:28]

历史路线上，BiCS3、BiCS5、BiCS8 等代际的发布节点可从 Western Digital 官方新闻稿追溯，这些代际与 Kioxia 的产品页共同构成了 BiCS 路线图的时间轴。 ^[research-nand-controller-patent-notes.md:27] 2025 年 2 月 24 日，Western Digital 正式完成闪存业务分离，此后闪存相关资料应从 Sandisk 官方渠道采集，不再混合 Western Digital 的 HDD 内容。 ^[research-nand-controller-patent-notes.md:26]

Kioxia 官网的 BiCS FLASH 页面是该技术路线的顶层入口，汇总了各代 BiCS 的定位、应用场景和技术概要。页面本身不暴露完整的 die 级命令时序、 endurance 曲线或 read-retry 参数，需配 合产品简报或数据手册使用。 ^[research-nand-controller-patent-notes.md:14]

### SK hynix 4D NAND

SK hynix 采用 **4D NAND** 品牌命名，强调在垂直方向之外增加外围电路的平面密度优化。当前量产节点包括 **238 层**和 **321 层** 4D NAND。官方新闻稿确认 321 层为全球首款量产的 321-high 1 Tb TLC 4D NAND。 ^[research-nand-controller-patent-notes.md:21-22]

SK hynix 的 4D NAND 新闻room 标签页（tag: 4D NAND）是公开技术里程碑的稳定发现路径，但内容以关键节点为主，不替代 die 数据手册、ONFI/Toggle 时序或固件集成需求。 ^[research-nand-controller-patent-notes.md:21]

### YMTC Xtacking

YMTC 的 **Xtacking** 架构将 NAND 存储阵列与外围控制电路分别制造后通过晶圆键合（wafer bonding）方式集成，理论上可独立优化阵列工艺和外围电路工艺，从而在接口带宽和单位密度上实现差异化。 ^[research-nand-controller-patent-notes.md:25]

Xtacking 架构对应 YMTC 的 X 系列 NAND 产品线：X1、X2、X3、X4 分别代表不同代际的 TLC/QLC 产品，如 X4-9060、X4-9070、X4-6080 等已在 YMTC 官方产品列表公开。 ^[research-nand-controller-patent-notes.md:23] 需要注意的是，公开页面信息较为简略，详细的 die 时序、命令集和可靠性参数可能需要通过产品数据表获取。 ^[research-nand-controller-patent-notes.md:23]

### Micron G8 / G9 NAND

Micron 的 NAND 产品族页面按 SLC/MLC/TLC/QLC 分类组织，是顶层 intake 节点，并链接至各代产品目录、数据手册、技术说明和白皮书。 ^[research-nand-controller-patent-notes.md:11] G9 NAND 页面用于获取带宽、密度和文档可用性的代际级参考，具体接口时序和 ECC 需求仍需查阅数据手册。 ^[research-nand-controller-patent-notes.md:13]

## 接口速率对比

| 厂商 / 代际 | 接口标准 | 最高速率 | 代表产品 / 声明 |
|---|---|---|---|
| Samsung V-NAND 9 | Toggle 5.1 | 3.2 GT/s | 1 Tb TLC |
| Sandisk BiCS10 | 未明确标注 | 4.8 Gb/s | 1 Tb TLC |
| SK hynix 321-layer 4D | 未公开（推测 Toggle 4.x 或更新） | 未公开 | 1 Tb TLC 量产 |
| YMTC X 系列 | 未公开统一标准 | 未在公开页面列明 | X4 系列 TLC/QLC |
| Micron G9 | 未公开 | 未公开 | 未列明具体 die |

各厂商官方页面均以定位和卖点为主，具体接口参数需对照 ONFI/Toggle 规范和实际数据手册。 ^[research-nand-controller-patent-notes.md]

## 代际层数参考（公开声明）

| 代际区间 | 代表节点 | 备注 |
|---|---|---|
| 早期 3D | 32/48 层 | 2D NAND 向 3D 过渡阶段 |
| 中期 3D | 64/96/128 层 | 主流 TLC 密度快速提升 |
| 当前主流 | 176/232/238 层 | SK hynix 238L、Micron 232L 等 |
| 近期量产 | 321 层 | SK hynix 321L 为公开最高层数声明 |
| 在研方向 | 400+ 层 | 部分厂商在路线图中提及，尚未大规模量产公开 |

上表数据来自厂商公开新闻稿和技术博客，层数本身是密度指标而非直接性能指标，实际性能还受接口速率、cell 类型和 ECC 设计影响。

## 技术路线图使用注意事项

- **公开资料与私有数据手册的差距**：厂商官网、新闻稿和技术博客适合建立代际定位和功能边界的宏观认知；详细的 NAND 命令时序、read-retry 表格、raw bit error rate (RBER) 分布和 ECC 预算通常需要签署 NDA 后获取。 ^[research-nand-controller-patent-notes.md]
- **Press release 的选择性**：新闻稿只选择性披露对营销有利的参数，不代表完整规格；将接口速率和层数声明当作完整接口需求使用时存在风险。 ^[research-nand-controller-patent-notes.md:18]
- **数据新鲜度**：YMTC、Kioxia 和 SK hynix 的页面更新频率不一致，建议在 intake 时记录访问日期和 sha256（可下载内容），便于后续追溯版本变更。 ^[research-nand-controller-patent-notes.md:5]

## 相关概念

NAND 介质参数手册 — 收录具体 NAND die 的数据手册和参数页面链接。  
控制器硬件模块边界 — NAND 接口与 SSD 控制器的硬件边界定义。  
ECC、LDPC 与可靠性管理 — 3D NAND 可靠性机制与控制器纠错策略。  
Flash Scheduler、Channel/Die/Plane Arbitration 与 Read Priority — NAND 并行度与调度机制。  
DRAM-less SSD 与 Host Memory Buffer — HMB 与无 DRAM SSD 的设计考量。

## Sources

^[research-nand-controller-patent-notes.md:11-28] — NAND 厂商公开资料 intake 表，包含 Micron、Kioxia、Samsung、SK hynix、YMTC、Western Digital / Sandisk 的产品页、新闻稿和技术说明页面入口及可信度评估。

