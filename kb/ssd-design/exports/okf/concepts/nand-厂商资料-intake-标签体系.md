---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: d7b086b8e996ebee1e1429c83158732360d05d69f4c84e2005f991c75fc7a89a
  pageDirectory: concepts
  sources:
    - research-nand-controller-patent-notes-53079fdd.md
  confidence: 0.88
  provenanceState: merged
  freshnessStatus: fresh
  aliases:
    - nand-厂商资料-intake-标签体系
    - N厂I标
  citations:
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 1
      end: 12
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 18
      end: 21
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 22
      end: 24
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 25
      end: 27
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 28
      end: 30
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 31
      end: 33
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 34
      end: 36
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 70
      end: 86
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 73
      end: 79
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 80
      end: 82
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 83
      end: 86
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 36
      end: 43
title: NAND 厂商资料 Intake 标签体系
description: 按厂商（Micron/Kioxia/Samsung/SK hynix/YMTC/WD-Sandisk）和按专利主题（PLP/SLC-cache/FDP-placement）两个维度的标签命名约定与使用场景。
tags:
  - metadata
  - tagging
  - intake
timestamp: "2026-08-16T05:51:00.315Z"
---


# NAND 厂商资料 Intake 标签体系

本文档定义用于采集和分类 NAND 闪存原厂公开资料的一套标签体系。标签体系覆盖主要 NAND 原厂的公开资料入口、CPC 专利分类入口，以及与 SSD 固件/控制器设计直接相关的专题标签。^[research-nand-controller-patent-notes-53079fdd.md:1-12]

## 设计目标

标签体系服务于以下目标：

- **资料定位**：为每个原厂的公开资料提供稳定、可追溯的入口节点，便于持续追踪产品代际演进和文档更新。
- **可信度区分**：区分原厂自述（product brief、guide）、白皮书、营销语言和推断性结论，防止将营销卖点误作设计依据。
- **模块归属**：让采集结果能够自动流向知识库中的相关页面——如[控制器硬件模块边界](controller-hardware-module-boundaries.md)、[ECC/LDPC 与可靠性管理](ecc-ldpc-reliability-management.md)、[控制器厂商数据采集与建模](controller-vendor-public-material-intake.md)。
- **版本可追溯**：每条记录需携带文档版本、访问日期和本地文件名，确保后续复核可还原原始来源。^[research-nand-controller-patent-notes-53079fdd.md:1-12]

## 原厂资料 Intake 节点

### Micron

Micron 的 NAND 产品家族页面作为顶层入口节点，按 SLC/MLC/TLC/QLC 分类组织，并链接至产品目录、数据表、技术说明和白皮书。销售支持下载门户（sales-support/downloads）作为后续采集路径，可按存储类别筛选 NAND Flash 和 Managed NAND 文档。G8/G9 NAND 页面提供代际级别的带宽、密度和文档可用性备注。^[research-nand-controller-patent-notes-53079fdd.md:18-21]

Micron 页面适合跟踪产品家族和设计相关文档，但产品页通常只做能力概述，不暴露完整的电气时序、命令行为或可靠性参数表。许多详细数据表可能需要通过目录筛选或客户权限获取。采集时应记录文档标题、版本号和检索日期。^[research-nand-controller-patent-notes-53079fdd.md:18-21]

### Kioxia

Kioxia 的 BiCS FLASH 产品页面作为主要 NAND 技术入口节点，汇总了 BiCS 代际、目标应用和技术定位。内存产品页面作为次级目录路径，涵盖 BiCS FLASH、UFS/e-MMC 和应用细分。NAND/技术解说和历史页面用于锚定术语（如 NAND 发明历史、3D flash、BiCS 命名来源）。^[research-nand-controller-patent-notes-53079fdd.md:22-24]

Kioxia 页面适合将原始 NAND 技术映射到 SSD 和嵌入式存储设计相关的产品/应用家族，但不提供控制器集成指南，底层 NAND 接口和可靠性细节仍然有限。技术解说页面面向一般受众，不宜用作精确设计参数的证据。^[research-nand-controller-patent-notes-53079fdd.md:22-24]

### Samsung

Samsung Semiconductor 的 V-NAND 技术博客和术语表页面作为 V-NAND 结构、电荷陷阱 flash、堆叠、通孔和 cell 间干扰等术语的入口。第九代 V-NAND 发布页面作为最新公开 TLC/QLC 代际声明的节点，涵盖 1Tb TLC、Toggle 5.1、高达 3.2Gbps 接口速率、位密度提升和 PCIe 5.0 定位背景。SSD/FDP 技术博客仅作为主机放置上下文使用，不作为 NAND 器件数据来源。^[research-nand-controller-patent-notes-53079fdd.md:25-27]

Samsung 的博客材料属于解释性内容而非正式数据表，定量声明可能因产品/代际而异，应与官方产品文档交叉验证。新闻稿具有选择性，不定义 ONFI/Toggle 时序、read-retry 表、ECC 预算或控制器固件要求。^[research-nand-controller-patent-notes-53079fdd.md:25-27]

### SK hynix

SK hynix 官方公司/产品页面作为 NAND Storage 和 SSD 类别的顶层公共采集入口，链接至包括 NAND Storage 和 SSD 在内的产品与解决方案。4D NAND 新闻室标签及相关发布作为 238 层和 321 层 4D NAND 里程碑的采集路径。321 层/238 层官方发布提供具体的公共代际声明和存储产品定位。^[research-nand-controller-patent-notes-53079fdd.md:28-30]

SK hynix 新闻室内容以里程碑为导向，不能替代 die 数据表、ONFI/Toggle 时序或固件集成需求。公开声明属于原厂定位，耐久性、原始误码率、读延迟分布和 ECC 假设未完全明确。^[research-nand-controller-patent-notes-53079fdd.md:28-30]

### YMTC

YMTC 的 3D NAND Flash Memory 产品列表作为 X1/X2/X3/X4 TLC/QLC 代际的顶层入口节点，列出商业化 3D NAND 产品（如 X4-9060、X4-9070、X4-6080、X3-9070、X3-6070）。Xtacking 页面作为架构级采集节点，反映存储阵列与外围电路的分离。产品和发布页面（如 PC300、PCIe 4.0 NVMe、HMB、SLC 缓存）作为 HMB、SLC 缓存、混合缓存、DRAM-less 和企业/客户端 SSD 示例的采集来源。^[research-nand-controller-patent-notes-53079fdd.md:31-33]

YMTC 页面适合采集 Xtacking 架构信息及其与 NAND 吞吐量和系统级性能的关联，但属于高层架构定位，不宜单独推断精确接口时序、晶圆键合良率或控制器兼容性。公共页面较简短，可能遗漏详细的 die 时序、命令集、可靠性和资质数据。^[research-nand-controller-patent-notes-53079fdd.md:31-33]

### Western Digital / Sandisk

Western Digital 在 2025 年 2 月 24 日宣布完成闪存业务分离。2025 年之前的 WD 闪存/NAND 页面仅作为历史采集使用。当前闪存材料应转向 Sandisk 官方渠道获取。Western Digital 的历史 BiCS 新闻稿（BiCS3/BiCS5/BiCS8 时间线）仍作为 Kioxia/WD 联合开发历史背景的有效证据。Sandisk 当前的 BiCS10 和 Kioxia/Sandisk 联合发布作为分离后的当前闪存采集路径。^[research-nand-controller-patent-notes-53079fdd.md:34-36]

WD/Sandisk 企业历史可能混淆来源归属，采集时需精确记录发布日期和公司名称。Sandisk 的 BiCS10 页面提供当前公开 TLC 声明（如 4.8Gb/s 接口速率和密度/功耗定位），但不是控制器编程手册，详细 NAND 接口、ECC、时序和可靠性信息可能仍为非公开或客户受限。^[research-nand-controller-patent-notes-53079fdd.md:34-36]

## 标签命名规范

标签采用三级结构，格式为 `层级一/层级二/层级三`，便于按类别过滤和路由：

| 层级 | 含义 | 示例 |
|---|---|---|
| 层级一 | 大类 | `vendor`、`patent`、`topic` |
| 层级二 | 原厂或 CPC 分类 | `micron`、`kioxia`、`g06f-3-06` |
| 层级三 | 具体技术或子类 | `nand`、`bics`、`plp` |

标签命名统一使用小写和连字符（`-`），避免空格或特殊字符。所有标签需关联来源 URL、访问日期和文档版本。^[research-nand-controller-patent-notes-53079fdd.md:70-86]

## Intake 标签参考表

### 供应商标签

| 标签 | 适用范围 | 入口 URL | 采集注意事项 |
|---|---|---|---|
| `vendor/micron/nand` | Micron NAND 首页、代际页面、数据表、技术说明和下载门户记录 | https://www.micron.com/products/storage/nand-flash | 将 Micron 原始 NAND 和 Managed NAND 材料与 SSD 产品材料分开 |
| `vendor/kioxia/bics` | BiCS FLASH 代际、Kioxia 内存页面和 Kioxia/Sandisk 联合 BiCS 发布 | https://www.kioxia.com/en-jp/business/memory/bics.html | BiCS 是 Kioxia 和联合发布中反复出现的公共技术名称 |
| `vendor/samsung/v-nand` | V-NAND 术语表、V-NAND 代际发布和 Samsung SSD/FDP 技术上下文 | https://semiconductor.samsung.com/support/tools-resources/dictionary/semiconductor-glossary-3d-v-nand-flash-memory/ | 与 Samsung 自身公开术语保持一致 |
| `vendor/skhynix/4d-nand` | 4D NAND 发布、238 层/321 层备注和 SK hynix 存储解决方案里程碑 | https://news.skhynix.com/en/tag/4d-nand/ | 与原厂公开技术品牌匹配 |
| `vendor/ymtc/xtacking` | Xtacking 架构、X 系列 NAND 和提及 HMB/SLC/混合缓存的 YMTC SSD 页面 | https://www.ymtc.com/en/technicalintroduction.html | Xtacking 是 YMTC 的关键公共架构线索 |
| `vendor/wd-sandisk/bics` | Western Digital 历史 BiCS 备注和 Sandisk 当前 BiCS 发布（2025 年分离后） | https://www.sandisk.com/sandisk-separation-faqs | 分离 FAQ 阐明了为何当前闪存采集应优先使用 Sandisk |

^[research-nand-controller-patent-notes-53079fdd.md:73-79]

### 专利 CPC 标签

| 标签 | 适用范围 | 入口 URL | 采集注意事项 |
|---|---|---|---|
| `patent/cpc/g06f-3-06` | SSD 控制器、主机接口、存储虚拟化、FTL、GC、放置和 RAID 类存储专利 | https://www.uspto.gov/web/patents/classification/cpc/html/cpc-G06F.html | G06F 3/06 是数字 I/O 到记录载体的宽泛 CPC 锚点 |
| `patent/cpc/g11c-16` | NAND 编程/读取/擦除、传感、干扰、保持、磨损和存储单元行为 | https://www.uspto.gov/web/patents/classification/cpc/html/cpc-G11C.html | G11C 16/00 及其子组覆盖可擦除可编程只读存储器 |
| `patent/cpc/h03m-13` | LDPC/BCH/RS 编码、迭代解码、软解码和 ECC 硬件实现 | https://www.uspto.gov/web/patents/classification/cpc/html/cpc-H03M.html | H03M 13 包含 LDPC 特定分支和解码方法子组 |
| `patent/cpc/h10b` | 半导体/固态存储器件结构，尤其是 3D NAND 核心/外围/阶梯结构概念 | https://www.uspto.gov/web/patents/classification/cpc/html/defH10B.html | H10B 设备结构导向强，可能遗漏固件、主机接口和系统级 SSD 专利 |

^[research-nand-controller-patent-notes-53079fdd.md:80-82]

### 专题标签

| 标签 | 适用范围 | 入口 URL | 采集注意事项 |
|---|---|---|---|
| `patent/topic/plp` | 掉电保护、突发断电恢复、电容备用冲洗和元数据保留 | https://patents.google.com/?q=%22power+loss+protection%22+SSD+NAND | PLP 专利通常桥接硬件能量储备和固件恢复行为 |
| `patent/topic/slc-cache` | SLC 缓存、伪 SLC、混合缓存、折叠和动态单级/多级配置 | https://patents.google.com/?q=%22SLC+cache%22+SSD+%22hybrid+cache%22 | 捕捉影响写延迟崖、QoS 和耐久性的固件策略领域 |
| `patent/topic/fdp-placement` | FDP、流、主机提示、放置标识符、回收单元、冷热数据分离和 WAF 降低 | https://patents.google.com/?q=SSD+%22data+placement%22+%22write+amplification%22+%22host+hint%22 | 按设计问题而非单一协议术语对放置专利进行分组 |

^[research-nand-controller-patent-notes-53079fdd.md:83-86]

## 与知识库其他页面的关系

本标签体系采集的结果应按以下路径流入知识库：

| 采集内容 | 流向页面 |
|---|---|
| NAND 接口时序、代际参数、可靠性规格 | NAND 介质参数手册 |
| ECC/LDPC 能力、read retry、UBER 承诺 | ECC、LDPC 与可靠性管理 |
| 控制器模块命名、接口描述、生命周期语义 | 控制器厂商数据采集与建模 |
| 固件下载、提交、回滚、安全启动表述 | 量产需求与合规 |
| 健康日志、遥测字段、诊断接口 | 遥测、日志与现场调试 |

标签体系本身属于元数据层，定义的是"哪些文档值得采集"和"采集结果如何归类"，而非具体的技术规格。^[research-nand-controller-patent-notes-53079fdd.md:1-12]

## 常见采集误区

- **营销语言当设计承诺**：将 vendor brief 中的卖点列表直接当作可实现接口。
- **代际混用**：将"Enterprise"或"Client"作为统一功能集合，不区分具体代际和型号差异。
- **术语冒领**：把 guide 中的模块名称直接映射为 RTL 模块边界。
- **版本缺失**：未记录文档版本和访问日期，导致后续无法追溯采集状态。
- **标签过度细分**：为每个 vendor 的每个代际创建独立标签，导致标签爆炸且无法聚合。^[research-nand-controller-patent-notes-53079fdd.md:36-43]

## Sources

- [research-nand-controller-patent-notes-53079fdd.md](sources/research-nand-controller-patent-notes-53079fdd.md)

# Citations

1. [research-nand-controller-patent-notes-53079fdd.md:1-12](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
2. [research-nand-controller-patent-notes-53079fdd.md:18-21](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
3. [research-nand-controller-patent-notes-53079fdd.md:22-24](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
4. [research-nand-controller-patent-notes-53079fdd.md:25-27](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
5. [research-nand-controller-patent-notes-53079fdd.md:28-30](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
6. [research-nand-controller-patent-notes-53079fdd.md:31-33](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
7. [research-nand-controller-patent-notes-53079fdd.md:34-36](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
8. [research-nand-controller-patent-notes-53079fdd.md:70-86](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
9. [research-nand-controller-patent-notes-53079fdd.md:73-79](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
10. [research-nand-controller-patent-notes-53079fdd.md:80-82](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
11. [research-nand-controller-patent-notes-53079fdd.md:83-86](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
12. [research-nand-controller-patent-notes-53079fdd.md:36-43](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
