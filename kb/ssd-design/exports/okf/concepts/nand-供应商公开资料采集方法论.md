---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 4b127a3aa6eb4f95dfcd22ab3bf1f179c1da0e2eb1c8ef7b6f2724bacff8c783
  pageDirectory: concepts
  sources:
    - research-nand-controller-patent-notes.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - nand-供应商公开资料采集方法论
  citations:
    - file: research-nand-controller-patent-notes.md
      start: 9
      end: 13
    - file: research-nand-controller-patent-notes.md
      start: 14
      end: 16
    - file: research-nand-controller-patent-notes.md
      start: 17
      end: 19
    - file: research-nand-controller-patent-notes.md
      start: 20
      end: 22
    - file: research-nand-controller-patent-notes.md
      start: 23
      end: 25
    - file: research-nand-controller-patent-notes.md
      start: 26
      end: 26
    - file: research-nand-controller-patent-notes.md
      start: 27
      end: 28
    - file: research-nand-controller-patent-notes.md
      start: 9
      end: 28
    - file: research-nand-controller-patent-notes.md
      start: 66
      end: 71
    - file: research-nand-controller-patent-notes.md
      start: 30
      end: 50
title: NAND 供应商公开资料采集方法论
description: 系统化采集 Micron、Kioxia、Samsung、SK hynix、YMTC、Western Digital/Sandisk 等 NAND 供应商官方公开资料的方法与入口
tags:
  - nand-vendor
  - source-intake
  - methodology
timestamp: "2026-08-16T05:51:23.698Z"
---

# NAND 供应商公开资料采集方法论

NAND 供应商公开资料往往不是完整的控制器规格书，而是一组分散的产品页、brief、datasheet、技术说明和白皮书。本页定义一套结构化的采集流程，把分散的公开资料变成可比较、可追溯的知识库字段输入。

## 采集目标

本方法论的目标是将公开资料转化为以下可使用字段：

- 供应商愿意公开承诺的核心能力边界
- 供应商使用的模块名和术语体系
- 哪些能力停留在 marketing 层而非可验证实现
- 哪些内容可以进入控制器硬件边界、平台兼容和遥测页面

## 主要供应商入口

不同供应商的公开资料入口和可信度存在差异，以下按供应商整理推荐入口及其局限性。

### Micron

| 入口类型 | 推荐入口 | 主要作用 | 局限性 |
|---|---|---|---|
| 产品家族总页 | Micron NAND 产品页 | 作为顶层入口节点，暴露 SLC/MLC/TLC/QLC 分类并链接到目录、datasheet、技术说明和白皮书 | 产品页通常只做能力摘要，不暴露完整的电气时序、命令行为或可靠性表格 |
| 下载与技术文档 | Micron 下载门户 | 作为后续采集路径，获取 datasheet、技术说明、兼容性指南、固件和软件 | 搜索结果会随时间变化，部分文档可能受限、修订或移除 |
| 代际参考页 | G8/G9 NAND 页面 | 连接产品定位与具体文档链接，用于将控制器假设映射到 NAND 代际 | 公开代际页面属于 marketing/overview 材料，不能将带宽或密度标称值当作完整接口要求 |

^[research-nand-controller-patent-notes.md:9-13]

### Kioxia

| 入口类型 | 推荐入口 | 主要作用 | 局限性 |
|---|---|---|---|
| 主要技术入口 | BiCS FLASH 产品页 | 作为 Kioxia 3D flash 技术的官方入口节点，汇总 BiCS 代际、目标应用和技术定位 | 不暴露完整的 die 级命令时序、耐久性、read-retry 或 program/erase 限制；需配合 product brief 或 datasheet 使用 |
| 次级目录路径 | Kioxia Memory 产品页 | 用于将原始 NAND 技术映射到 SSD 和嵌入式存储设计相关的应用家族 | 不是控制器集成指南，低级 NAND 接口和可靠性细节仍然有限 |
| 术语锚定 | NAND/技术说明与历史页面 | 作为一级教育来源，用于术语锚定如 NAND 发明、3D flash 和 BiCS | 面向广泛受众；避免用作精确设计参数的证据 |

^[research-nand-controller-patent-notes.md:14-16]

### Samsung

| 入口类型 | 推荐入口 | 主要作用 | 局限性 |
|---|---|---|---|
| 技术术语 | V-NAND 技术博客与术语页 | 采集 V-NAND 结构、charge trap flash、堆叠、channel holes 和 cell interference 术语 | 不是正式的 datasheet；定量标称值可能特定于产品/代际，应与官方产品文档交叉验证 |
| 最新代际信号 | 第九代 V-NAND 发布 | 获取最新的公开 TLC/QLC 代际标称值、接口速度、密度和低功耗设计背景：1Tb TLC、Toggle 5.1、最高 3.2Gbps | 新闻稿具有选择性；不定义 ONFI/Toggle 时序、read-retry 表、ECC 预算或控制器固件要求 |
| 主机放置上下文 | SSD/FDP 技术博客 | 作为主机放置上下文使用，而非 NAND 器件数据；连接数据放置与写放大和 NVMe FDP | 是实现叙事而非 NVMe 规范本身；正式行为必须追溯到 NVMe 文档 |

^[research-nand-controller-patent-notes.md:17-19]

### SK hynix

| 入口类型 | 推荐入口 | 主要作用 | 局限性 |
|---|---|---|---|
| 顶层公共入口 | SK hynix 官网 | 官方企业门户，链接到包括 NAND Storage 和 SSD 的产品与解决方案 | 网站范围广泛，不进行更深度导航或客户访问可能无法获取详细 NAND 文档 |
| 代际里程碑 | 4D NAND 新闻标签及 238 层/321 层发布 | 作为 4D NAND 技术和新闻更新的一级发现路径；给出 321-high 1Tb TLC 4D NAND 量产的具体公开细节 | 新闻内容以里程碑为导向；不能替代 die datasheet、ONFI/Toggle 时序或固件集成要求 |

^[research-nand-controller-patent-notes.md:20-22]

### YMTC

| 入口类型 | 推荐入口 | 主要作用 | 局限性 |
|---|---|---|---|
| 产品列表 | 3D NAND Flash Memory 产品列表 | 识别商用 3D NAND 产品如 X4-9060、X4-9070、X4-6080、X3-9070 和 X3-6070 | 公开页面内容简短；可能省略详细的 die 时序、命令集、可靠性和资质数据 |
| 架构说明 | Xtacking 页面 | 一级架构材料，与 NAND 吞吐量、系统级性能和定制 NAND 解决方案标称值直接相关 | 是高层架构定位；不能单独推断精确接口时序、wafer-bonding 良率或控制器兼容性 |
| 产品上下文 | 产品页面和发布说明 | 明确提及 PC300、PCIe 4.0 NVMe、HMB、SLC cache 和基于 Xtacking 的 NAND | 描述 SSD 产品而非原始 NAND 行为；cache 策略细节不足以重建固件算法 |

^[research-nand-controller-patent-notes.md:23-25]

### Western Digital / Sandisk

2025 年 2 月 24 日，Western Digital 宣布完成其 Flash 业务的分离。当前的 flash 材料应在 Sandisk 下查找。^[research-nand-controller-patent-notes.md:26]

| 入口类型 | 推荐入口 | 主要作用 | 局限性 |
|---|---|---|---|
| 历史采集（2025 前） | WD 历史 BiCS 新闻稿 | 用于 BiCS3/BiCS5/BiCS8 时间线和 Kioxia/WD 联合开发上下文 | 是新闻稿而非器件 datasheet；后期代际细节需从 Kioxia/Sandisk 当前页面验证 |
| 当前采集（2025 后） | Sandisk 当前 BiCS10 发布 | 获取当前公开 BiCS10 TLC 标称值如 4.8Gb/s 接口速度和密度/功耗定位 | 不是控制器编程手册；详细的 NAND 接口、ECC、时序和可靠性信息可能仍为非公开或客户受限 |

^[research-nand-controller-patent-notes.md:27-28]

## 采集顺序

### 第一步：固定资料身份

首先记录以下元数据：

- 供应商名称（vendor）
- 产品系列（product family）
- 文档版本（document version）
- 来源 URL
- 访问日期（access date）
- 本地文件名
- SHA256 校验值（如可下载）
- 是否公开（public/gated）

对于网页内容，应同时保留 URL 和访问日期以便后续追溯。^[research-nand-controller-patent-notes.md:9-28]

### 第二步：提取功能边界

优先提取以下字段，决定"供应商愿意公开承诺什么"：

- PCIe 代际（如 PCIe 4.0/5.0）
- NAND 接口类型（ONFI/Toggle）
- 接口速度标称值
- NAND 代际（如 G9/G10/BiCS8/BiCS10）
- DRAM-less / HMB 支持
- 企业级 / 客户端定位
- 可靠性和 ECC 能力描述
- 安全特性（secure boot、signed firmware）

### 第三步：提取接口和模块名

从更详细的资料中提取术语体系：

- 控制器模块命名（如 host interface、controller front end、flash scheduler、memory controller）
- NAND 相关术语（如 plane、die、channel、block、page）
- ECC/LDPC/RAID-like 相关术语
- 寄存器、队列、doorbell 命名约定

这些词汇将影响知识库里的模块边界和验证表述。

### 第四步：提取生命周期语义

重点关注以下内容：

- firmware download / commit / activation / rollback 的公开表述
- secure boot / signed firmware 的支持声明
- telemetry / health log / persistent event 的说明
- factory test / diagnostics / recovery mode 的描述
- 平台兼容性相关说明

## 可信度分级

| 级别 | 说明 | 用途 |
|---|---|---|
| explicit product brief | 页面或 PDF 明确声明 | 可进入 vendor intake |
| guide / product guide | 更详细但仍属公开参考 | 可用于接口和模块边界 |
| marketing language | 只有定位或卖点 | 只用于术语和 backlog |
| inferred | 从产品命名、市场定位或对标项目推断 | 仅供探索，不作事实 |

^[research-nand-controller-patent-notes.md:9-28]

## 字段模板

每条记录至少应包含以下字段：

```
vendor: string
product_family: string
source_url: string
access_date: string
document_version: string
sha256: string | null
host_interface: string | null
nand_interface: string | null
memory_architecture: string | null
reliability_ecc: string | null
security: string | null
firmware_lifecycle: string | null
telemetry_diagnostics: string | null
confidence_level: explicit | guide | marketing | inferred
```

## 常见误区

| 误区 | 说明 |
|---|---|
| 把 marketing feature list 当成可实现接口 | 供应商页面上的功能列表不等于硬件/固件实现 |
| 把 guide 里的模块名称直接当成 RTL 模块边界 | 模块名是供应商术语，不等于 RTL 切分 |
| 把"企业级"或"客户端"当成统一功能集合 | 不区分具体代际会导致错误假设 |
| 把公开资料的术语误写成已验证实现细节 | marketing 术语和工程术语之间存在差距 |
| 没记录版本和 SHA256 | 后续无法追溯文档变更 |

^[research-nand-controller-patent-notes.md:9-28]

## 采集标签体系

为便于知识库分类管理，建议使用以下标签前缀：

| 标签前缀 | 适用场景 |
|---|---|
| `vendor/micron/nand` | Micron NAND 落地页、代际页面、datasheet、技术说明和下载门户记录 |
| `vendor/kioxia/bics` | BiCS FLASH 代际、Kioxia Memory 页面和 Kioxia/Sandisk 联合 BiCS 发布 |
| `vendor/samsung/v-nand` | V-NAND 术语、V-NAND 代际发布和 Samsung SSD/FDP 技术上下文 |
| `vendor/skhynix/4d-nand` | 4D NAND 发布、238 层/321 层说明和 SK hynix 存储解决方案里程碑 |
| `vendor/ymtc/xtacking` | Xtacking 架构、X 系列 NAND 和提及 HMB/SLC/hybrid cache 的 YMTC SSD 页面 |
| `vendor/wd-sandisk/bics` | 历史 WD BiCS 说明和 2025 年分离后 Sandisk BiCS 说明 |

^[research-nand-controller-patent-notes.md:66-71]

## 输出去向

采集结果应进入以下知识库位置：

- Controller Vendor 公开资料 Intake：供应商公开能力边界
- 控制器硬件模块边界：模块名和术语映射
- 控制器 RTL / IP 参考：接口级设计核对
- 量产需求与合规：平台兼容和资质要求
- 遥测、日志与现场调试：telemetry 和 diagnostics

## 与专利采集的关系

公开资料采集和专利采集是两条独立但互补的路径。专利搜索更适合获取实现细节和设计动机，而供应商公开资料更适合获取公开承诺和术语体系。两者应分别维护，专利内容不应混入供应商公开资料记录。^[research-nand-controller-patent-notes.md:30-50]

## Sources

- NAND Controller and Patent Research Notes

## Related Concepts

- 控制器硬件模块边界 — 硬件模块划分如何受供应商术语影响
- 控制器 RTL / IP 参考 — 将供应商模块名映射到 RTL 接口
- 控制器厂商数据采集与建模 — 控制器厂商公开资料的系统化采集方法
- ECC、LDPC 与可靠性管理 — NAND 可靠性与供应商 ECC 公开描述的对应关系
- DRAM-less SSD 与 Host Memory Buffer — HMB 能力边界如何受供应商公开承诺约束
- 量产需求与合规 — 平台兼容和资质如何依赖供应商公开文档

# Citations

1. [research-nand-controller-patent-notes.md:9-13](/references/research-nand-controller-patent-notes-8985793f.md)
2. [research-nand-controller-patent-notes.md:14-16](/references/research-nand-controller-patent-notes-8985793f.md)
3. [research-nand-controller-patent-notes.md:17-19](/references/research-nand-controller-patent-notes-8985793f.md)
4. [research-nand-controller-patent-notes.md:20-22](/references/research-nand-controller-patent-notes-8985793f.md)
5. [research-nand-controller-patent-notes.md:23-25](/references/research-nand-controller-patent-notes-8985793f.md)
6. [research-nand-controller-patent-notes.md:26-26](/references/research-nand-controller-patent-notes-8985793f.md)
7. [research-nand-controller-patent-notes.md:27-28](/references/research-nand-controller-patent-notes-8985793f.md)
8. [research-nand-controller-patent-notes.md:9-28](/references/research-nand-controller-patent-notes-8985793f.md)
9. [research-nand-controller-patent-notes.md:66-71](/references/research-nand-controller-patent-notes-8985793f.md)
10. [research-nand-controller-patent-notes.md:30-50](/references/research-nand-controller-patent-notes-8985793f.md)
