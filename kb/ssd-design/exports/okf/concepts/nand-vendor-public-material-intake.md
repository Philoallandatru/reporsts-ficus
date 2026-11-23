---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 86026721308ab6640d8c4ea6f053351f6540e2d2cf39fbe60889630d0ee5eb94
  pageDirectory: concepts
  sources:
    - research-nand-controller-patent-notes-53079fdd.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - nand-vendor-public-material-intake
    - NVPMI
  citations:
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 18
      end: 20
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 21
      end: 23
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 24
      end: 26
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 27
      end: 29
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 30
      end: 32
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 33
      end: 35
title: NAND Vendor Public Material Intake
description: 系统性采集 Micron、Kioxia、Samsung、SK hynix、YMTC、Western Digital/Sandisk 等主要 NAND 原厂公开资料的方法论，包括着陆页、下载门户、代际页面和产品目录的优先级排序与适用条件。
tags:
  - vendor-intake
  - nand
  - methodology
timestamp: "2026-08-16T05:50:05.751Z"
---


# NAND 厂商公开资料采集

本页面记录 SSD 控制器知识库在采购公开 NAND 厂商资料时的采集策略、入口节点、可用理由及已知局限。采集目标不是替代私有数据手册，而是建立一组可比较、可追溯的字段，用于后续与硬件边界、平台兼容、遥测和量产页面的交叉验证。

## 采集原则

采集顺序遵循从高层入口到细节文档的递进关系：先用厂商官方产品页或概览页确认代际分类，再用下载/文档门户定位具体数据手册和技术说明，最后用白皮书或新闻稿补充术语和定位上下文。每个节点均需记录 URL、访问日期、文档版本和 SHA256（若可下载），以便后续追溯。

采集结果应进入控制器厂商公开资料 Intake、控制器硬件模块边界、控制器 RTL / IP 参考、量产需求与合规以及遥测、日志与现场调试等页面。

## Micron

| 用途 | 结论 | URL | 为何可用 | 已知局限 |
|---|---|---|---|---|
| 产品族总览 | 将 Micron NAND 产品族页面作为顶层采集入口；该页面按 SLC/MLC/TLC/QLC 分类组织，并链接至目录、数据手册、技术说明和白皮书。 | https://www.micron.com/products/storage/nand-flash | 页面为厂商自营，且按 NAND 类型结构化，适合跟踪产品族和设计相关文档。 | 产品页通常汇总能力描述，而非暴露完整的电气时序、命令行为或可靠性表格；许多详细数据手册可能需要目录筛选或客户访问权限。 |
| 详细文档采集 | 将 Micron 销售支持下载门户作为后续采集路径，用于获取数据手册、技术说明、兼容性指南、固件和软件。 | https://www.micron.com/sales-support/downloads | 官方文档发现入口，可按 NAND Flash 和托管 NAND 等存储类别筛选。 | 搜索结果可能随时间变化，部分文档可能受限于访问权限、修订或下架；采集时应归档文档标题、修订版本和检索日期。 |
| 代际概览 | 将 G8/G9 NAND 页面用于带宽、密度和文档可用性等代际级别备注。 | https://www.micron.com/products/storage/nand-flash/g9-nand | 代际页面将产品定位与具体文档链接关联，便于将控制器假设映射至 NAND 代际。 | 公开代际页面属于营销/概览材料；不应将标题带宽或密度声明作为完整接口需求使用，需配合数据手册交叉验证。 |

^[research-nand-controller-patent-notes-53079fdd.md:18-20]

## Kioxia

| 用途 | 结论 | URL | 为何可用 | 已知局限 |
|---|---|---|---|---|
| 技术入口 | 将 BiCS FLASH 产品页作为 Kioxia 的主要 NAND 技术采集节点。 | https://www.kioxia.com/en-jp/business/memory/bics.html | Kioxia 官方 3D 闪存技术页面，汇总 BiCS 代际、目标应用和技术定位。 | 未暴露完整的 die 级命令时序、耐用性、读重试或编程/擦除限制；应与产品简介或数据手册配合使用。 |
| 产品目录 | 将 Kioxia 存储器产品页作为 BiCS FLASH、UFS/e-MMC 和应用分段的辅助目录路径。 | https://www.kioxia.com/en-jp/business/memory.html | 厂商自营，可将原始 NAND 技术映射至与 SSD 和嵌入式存储设计相关的产品/应用族。 | 不是控制器集成指南；底层 NAND 接口和可靠性细节仍然有限。 |
| 术语锚定 | 将 Kioxia NAND/技术解说和历史页面用于锚定术语，如 NAND 发明、3D 闪存和 BiCS。 | https://www.kioxia.com/en-jp/rd/technology/nand-flash.html | 第一方教育性来源，适合作为术语表级事实和历史背景。 | 面向广泛受众编写；避免用作精确设计参数的证据。 |

^[research-nand-controller-patent-notes-53079fdd.md:21-23]

## Samsung

| 用途 | 结论 | URL | 为何可用 | 已知局限 |
|---|---|---|---|---|
| 术语采集 | 将 Samsung Semiconductor V-NAND 技术博客和术语表页面用于 V-NAND 结构、电荷陷阱闪存、堆叠、通孔和单元间干扰术语的采集。 | https://semiconductor.samsung.com/news-events/tech-blog/the-future-of-nand-technology/ | 第一方 Samsung Semiconductor 材料，提供对控制器有用的概念，如干扰、写入/读取延迟和跨 V-NAND 代际的功耗变化。 | 非正式数据手册；定量声明可能为特定产品/代际，应与官方产品文档交叉验证。 |
| 最新代际 | 将 Samsung 第九代 V-NAND 发布作为最新公开 TLC/QLC 代际声明、接口速度、密度和低功耗设计背景的采集节点。 | https://semiconductor.samsung.com/news-events/news/samsung-electronics-begins-industrys-first-mass-production-of-9th-gen-v-nand/ | 第一方发布，提供具体公开信号：1Tb TLC、Toggle 5.1、最高 3.2Gbps、位密度提升和 PCIe 5.0 定位。 | 新闻稿具有选择性；未定义 ONFI/Toggle 时序、读重试表、ECC 预算或控制器固件要求。 |
| 应用上下文 | 将 Samsung SSD/FDP 技术博客仅作为主机放置上下文使用，不作为 NAND 器件数据来源。 | https://semiconductor.samsung.com/news-events/tech-blog/nvme-fdp-a-promising-new-ssd-data-placement-approach/ | 主流 SSD 厂商的第一方技术评论，将数据放置与写入放大和 NVMe FDP 关联。 | 属于实现叙事，而非 NVMe 规范本身；正式行为必须追溯至 NVMe 文档。 |

^[research-nand-controller-patent-notes-53079fdd.md:24-26]

## SK hynix

| 用途 | 结论 | URL | 为何可用 | 已知局限 |
|---|---|---|---|---|
| 顶层入口 | 将 SK hynix 官方公司/产品入口作为 NAND 存储和 SSD 类别的顶层公开采集节点。 | https://www.skhynix.com/ | 官方企业门户，链接至包括 NAND 存储和 SSD 在内的产品与解决方案。 | 网站覆盖面广，若无更深入导航或客户访问权限，可能无法暴露详细 NAND 部件文档。 |
| 代际里程碑 | 将 SK hynix 4D NAND 新闻室标签及相关发布用于 238 层和 321 层 4D NAND 里程碑的采集。 | https://news.skhynix.com/en/tag/4d-nand/ | 第一方新闻室材料，将 4D NAND 技术新闻和发布汇集在一个稳定的发现路径中。 | 新闻室内容以里程碑为导向，不能替代 die 数据手册、ONFI/Toggle 时序或固件集成要求。 |
| 代际声明 | 将 321 层/238 层官方发布用于具体的公开代际声明和存储产品定位。 | https://news.skhynix.com/en/sk-hynix-starts-mass-production-of-world-first-321-high-nand/ | 提供官方公开细节：321 层 1Tb TLC 4D NAND 量产，适用于代际时间线采集。 | 声明属于厂商定位；耐用性、原始误码率、读取延迟分布和 ECC 假设未完全指定。 |

^[research-nand-controller-patent-notes-53079fdd.md:27-29]

## YMTC

| 用途 | 结论 | URL | 为何可用 | 已知局限 |
|---|---|---|---|---|
| 产品族总览 | 将 YMTC 3D NAND Flash Memory 产品列表作为 X1/X2/X3/X4 TLC/QLC 代际的顶层采集节点。 | https://www.ymtc.com/en/buslist.html?cat=35%3Fcat%3D35 | 官方产品列表，标识商业 3D NAND 产品（如 X4-9060、X4-9070、X4-6080、X3-9070、X3-6070）。 | 公开页面内容简短，可能省略详细的 die 时序、命令集、可靠性和资质数据。 |
| 架构说明 | 将 YMTC Xtacking 页面用于存储阵列与外围电路在架构层面的分离说明。 | https://www.ymtc.com/en/technicalintroduction.html | 第一方架构材料，与 NAND 吞吐量、系统级性能和定制 NAND 解决方案声明直接相关。 | 属于高层架构定位；不应单独从中推断确切接口时序、晶圆键合良率或控制器兼容性。 |
| SSD 产品上下文 | 将 YMTC 产品页面和发布公告用于 HMB、SLC 缓存、混合缓存、DRAM-less 和企业/客户端 SSD 示例的采集。 | https://www.ymtc.com/en/news/37.html | 官方发布说明，明确提及 PC300、PCIe 4.0 NVMe、HMB、SLC 缓存和基于 Xtacking 的 NAND。 | 描述 SSD 产品而非原始 NAND 行为；缓存策略细节不足以重建固件算法。 |

^[research-nand-controller-patent-notes-53079fdd.md:30-32]

## Western Digital / Sandisk

| 用途 | 结论 | URL | 为何可用 | 已知局限 |
|---|---|---|---|---|
| 主体分离说明 | 将 2025 年之前的 Western Digital 闪存/NAND 页面仅视为历史采集；Western Digital 于 2025-02-24 宣布完成闪存业务分离。 | https://www.westerndigital.com/company/newsroom/press-releases/2025/2025-02-24-western-digital-completes-planned-company-separation | Western Digital 官方发布，阐明后续采集的 corporation 来源归属：当前闪存材料应在 Sandisk 下检查。 | 较旧的 WD 页面仍有宝贵的历史证据价值，但新的 NAND/闪存细节可能移至 Sandisk；不要将分离后的 WD HDD 材料与 Sandisk 闪存材料混用。 |
| 历史 BiCS 时间线 | 将 Western Digital 的历史 BiCS 新闻稿用于 BiCS3/BiCS5/BiCS8 时间线和 Kioxia/WD 联合开发上下文。 | https://www.westerndigital.com/company/newsroom/press-releases/2020/2020-01-30-western-digital-extends-storage-leadership-with-bics5-3d-nand-technology | 第一方 WD 发布，适用于历史 BiCS 代际映射，尤其是在 Sandisk 分离之前。 | 属于新闻稿而非器件数据手册；后续代际细节需从 Kioxia/Sandisk 当前页面验证。 |
| 当前闪存采集 | 将 Sandisk 当前 BiCS10 和 Kioxia/Sandisk 联合发布作为分离后当前闪存采集路径。 | https://www.sandisk.com/company/newsroom/press-releases/2026/2026-07-02-sandisk-announces-bics10-1tb-tlc | 第一方 Sandisk 来源，提供当前公开 BiCS10 TLC 声明，如 4.8Gb/s 接口速度和密度/功耗定位。 | 非控制器编程手册；详细的 NAND 接口、ECC、时序和可靠性信息可能仍为非公开或客户限定。 |

^[research-nand-controller-patent-notes-53079fdd.md:33-35]

## 可信度分级

公开资料的可靠程度随文档类型显著变化。产品简介或新闻稿通常属于 marketing 语言，仅可用于术语和 backlog，不能作为接口需求。产品和功能指南更为详细，可用于接口和模块边界识别，但同样需交叉验证。明确的产品简介页面可直接进入 vendor intake，作为能力边界的初步锚定。

从公开资料推断的代际特性或兼容性假设应标记为推断级，仅供探索用途，不宜直接写入设计规范。

## 常见误区

- 将 marketing 功能列表误当作可实现接口。
- 将产品指南中的模块名称直接映射为 RTL 模块边界。
- 将"企业级"或"客户端"视为统一功能集合，不区分具体代际差异。
- 将公开资料的术语误写成已验证实现细节。
- 未记录版本和 SHA256，导致后续无法追溯。

## 相关概念

控制器硬件模块边界 — 硬件模块之间的职责划分，需与 NAND 接口特性交叉验证。

控制器 RTL / IP 参考 — RTL 层面的模块切分参考，可结合 NAND 支持术语进行接口设计核对。

控制器厂商数据采集与建模 — 更通用的厂商资料采集流程，包含产品页、指南、白皮书和源码等多种来源的采集策略。

ECC、LDPC 与可靠性管理 — NAND 可靠性管理的核心机制，依赖厂商公开的读重试表、ECC 预算和 endurance 数据。

DRAM-less SSD 与 Host Memory Buffer — 控制器 memory 架构设计，与厂商对 DRAM-less/HMB 能力的公开表述相关。

## 来源

- research-nand-controller-patent-notes-53079fdd.md

# Citations

1. [research-nand-controller-patent-notes-53079fdd.md:18-20](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
2. [research-nand-controller-patent-notes-53079fdd.md:21-23](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
3. [research-nand-controller-patent-notes-53079fdd.md:24-26](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
4. [research-nand-controller-patent-notes-53079fdd.md:27-29](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
5. [research-nand-controller-patent-notes-53079fdd.md:30-32](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
6. [research-nand-controller-patent-notes-53079fdd.md:33-35](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
