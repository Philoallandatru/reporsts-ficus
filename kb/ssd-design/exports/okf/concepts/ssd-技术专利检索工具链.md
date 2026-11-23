---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 569930e46d5c6d986c49842d0f75d5d1007c122f579b950f49d1190279d51745
  pageDirectory: concepts
  sources:
    - research-nand-controller-patent-notes.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - ssd-技术专利检索工具链
  citations:
    - file: research-nand-controller-patent-notes.md
      start: 34
      end: 34
    - file: research-nand-controller-patent-notes.md
      start: 36
      end: 36
    - file: research-nand-controller-patent-notes.md
      start: 37
      end: 37
    - file: research-nand-controller-patent-notes.md
      start: 37
      end: 43
    - file: research-nand-controller-patent-notes.md
      start: 38
      end: 38
    - file: research-nand-controller-patent-notes.md
      start: 40
      end: 40
    - file: research-nand-controller-patent-notes.md
      start: 42
      end: 42
    - file: research-nand-controller-patent-notes.md
      start: 44
      end: 48
    - file: research-nand-controller-patent-notes.md
      start: 44
      end: 44
    - file: research-nand-controller-patent-notes.md
      start: 48
      end: 48
    - file: research-nand-controller-patent-notes.md
      start: 53
      end: 60
    - file: research-nand-controller-patent-notes.md
      start: 55
      end: 55
    - file: research-nand-controller-patent-notes.md
      start: 59
      end: 59
    - file: research-nand-controller-patent-notes.md
      start: 7
      end: 28
    - file: research-nand-controller-patent-notes.md
      start: 26
      end: 26
    - file: research-nand-controller-patent-notes.md
    - file: research-nand-controller-patent-notes.md
      start: 62
      end: 78
    - file: research-nand-controller-patent-notes.md
      start: 8
      end: 8
title: SSD 技术专利检索工具链
description: Google Patents Advanced Search、USPTO Patent Public Search、USPTO Patent Center 的适用场景与分工
tags:
  - patent
  - search-tool
  - uspto
  - google-patents
timestamp: "2026-08-16T05:51:54.739Z"
---


# SSD 技术专利检索工具链

本文档整理 SSD 控制器与 NAND 相关技术专利检索的工具链，包括检索入口、CPC 分类体系、典型查询模板和厂商公开资料采集路径。目标是为固件/硬件设计团队提供一套可追溯、可复用的专利情报采集流程。

## 检索工具入口

专利检索应区分两类场景：广度发现与法律状态核验。Google Patents 适合快速发现 SSD/FTL/LDPC 相关专利，支持 assignee 过滤、CPC 过滤、引用链追踪和机器翻译。^[research-nand-controller-patent-notes.md:34]

| 工具 | 适用场景 | 主要能力 |
|---|---|---|
| Google Patents 高级检索 | 广度发现、关键词探索、种子专利扩展 | assignee/CPC 过滤、引用/家族链接、机器翻译 |
| USPTO Patent Public Search | 权威美国专利与公开申请检索 | 基础/高级检索、全文访问 |
| USPTO Patent Center | 已知申请号/专利号的深度核验 | 申请状态追踪、文件包装配 |
| CPC 官方表 | 分类版本确认与符号查新 | 当前 CPC 版本查阅 |

USPTO Patent Center 是美国专利的法定检索入口，但不适合宽泛发现；已知候选专利后用它核验法律状态。^[research-nand-controller-patent-notes.md:36] CPC 分类表由 USPTO 和 EPO 联合管理，符号版本更新频繁，建议在采集时记录 CPC 版本和日期。^[research-nand-controller-patent-notes.md:37]

## CPC 分类体系与 SSD 相关符号

CPC（合作专利分类）是 SSD 专利检索的主要分类词汇。核心符号覆盖存储控制器、错误纠正、NAND 器件物理和 LDPC 编码四个层面。^[research-nand-controller-patent-notes.md:37-43]

| CPC 符号 | 覆盖领域 | 典型关键词 |
|---|---|---|
| G06F 3/06 | SSD 控制器、主机接口、FTL、GC、磨损均衡、命名空间、流、放置 | solid state drive, flash translation layer, garbage collection, wear leveling, write amplification, namespace, stream, FDP |
| G06F 12/00 | 内存寻址/分配，与 FTL 映射、缓存、放置重叠 | NAND, SSD, FTL, non-volatile memory |
| G06F 11/00 | 计算系统错误检测/纠正与监控 | NAND, flash memory, SSD controller, read retry |
| G11C 16/00 | 可擦除可编程只读存储器，含 NAND program/read/erase、干扰、保持、阈值 | program disturb, read disturb, retention, wearout |
| H10B | 半导体/固态存储器件结构，含 3D NAND 核心/外围/阶梯结构 | NAND string, core region, peripheral region, staircase |
| H03M 13 | LDPC、BCH、Reed-Solomon、迭代解码、软判决译码 | soft decoding, LLR, read threshold, decoder latency |

G06F 3/06 是 SSD 控制器专利检索的锚点符号，但该类较宽泛，需配合关键词过滤以减少无关结果。^[research-nand-controller-patent-notes.md:38] LDPC 代码构造本身常归入 H03M 13，而 NAND 器件测试/修复可能归入 G11C 29/00。^[research-nand-controller-patent-notes.md:40] H10B 偏器件结构，固件策略类专利较少命中该类。^[research-nand-controller-patent-notes.md:42]

## 种子专利参考

种子专利是检索扩展的起点，用于收割关键词、 assignee、CPC 符号、引用链和家族链接。^[research-nand-controller-patent-notes.md:44-48]

| 领域 | 种子专利用途 | 链接 |
|---|---|---|
| FTL / GC / 磨损均衡 | 涵盖 FTL 行为、块压缩、动态/静态磨损均衡、逻辑到物理重映射 | https://patents.google.com/patent/US20120317377A1 |
| PLP / 掉电保护 | 涵盖 SSD 掉电保护、备用电源、超级电容、易失性缓冲刷新行为 | https://patents.google.com/patent/US20170185335A1 |
| SLC 缓存 | 涵盖 SLC 单元作为 MLC 容量交换的高速缓存管理 | https://patents.google.com/patent/US20220129168A1 |
| LDPC 监控 | 涵盖 LDPC 译码能力调整、纠错统计、存储设备错误率观测 | https://patents.google.com/patent/US8413029B2 |
| FDP / 放置 | 涵盖灵活数据放置、回收单元、句柄、设备级 GC 影响 | https://patents.google.com/patent/US12405729B2 |

单个种子专利不是完整分类体系，应通过它扩展关键词、 assignee 和引用网络。^[research-nand-controller-patent-notes.md:44] FDP 同时是标准特性，专利检索应与 NVMe 规范采集分离，避免将规范性协议行为与主张实现混淆。^[research-nand-controller-patent-notes.md:48]

## 可复用查询模板

以下查询模板可直接用于 Google Patents 搜索，覆盖 SSD 固件与控制器核心领域。^[research-nand-controller-patent-notes.md:53-60]

| 主题 | 初始查询策略 | 补充术语 |
|---|---|---|
| FTL / GC / 磨损均衡 | `"flash translation layer" SSD "garbage collection" "wear leveling"` | logical to physical, mapping table, valid page, block compaction |
| PLP / 掉电保护 | `"solid state drive" "power loss protection" capacitor flush` | sudden power off recovery, SPOR, power fail, backup power, supercapacitor |
| LDPC / 软判决 | `NAND LDPC "soft decoding" "read retry"` | soft bit, LLR, read threshold, NAND, flash memory, SSD controller |
| SLC 缓存 / pSLC | `"SLC cache" SSD TLC QLC "pseudo-SLC"` | single level mode, folding, hybrid cache, multi-level memory |
| 放置 / FDP / 流 | `"flexible data placement" SSD "reclaim unit" "placement identifier"` | write stream, data temperature, hot/cold data, host hint |
| NAND 器件 / 干扰 | `"NAND flash" "threshold voltage" disturb retention "read retry"` | — |

FTL 查询可能过度拟合使用确切术语 "FTL" 的文档，需用逻辑到物理映射、映射表、块压缩等变体补充。^[research-nand-controller-patent-notes.md:55] 放置类专利较新，旧专利可能使用 write stream、data temperature 或 host hint 等术语。^[research-nand-controller-patent-notes.md:59]

## 厂商公开资料采集

厂商公开资料通常分散在产品页、brief、guide、白皮书和应用说明中，需要一套稳定的采集流程将其转化为可比较的字段。^[research-nand-controller-patent-notes.md:7-28]

### 采集优先级

| 优先级 | 内容 | 作用 |
|---|---|---|
| 1 | vendor、product family、document version、source URL、access date、sha256、是否公开 | 建立资料身份与可追溯性 |
| 2 | PCIe generation、NVMe version、lane 数、DRAM-less / HMB 支持、enterprise / client 定位 | 确定厂商公开承诺的功能边界 |
| 3 | register / queue / doorbell 名称、PRP / SGL / DMA 边界、NAND 支持术语、ECC / LDPC / RAID-like 术语 | 提取接口和模块名称 |
| 4 | firmware download / commit / activation / rollback、secure boot、telemetry、diagnostics、recovery mode | 提取生命周期语义 |

### 主要 NAND 厂商公开入口

| 厂商 | 顶级入口 | 适用内容 |
|---|---|---|
| Micron | NAND 产品系列页、下载与技术支持门户、G8/G9 NAND 页面 | SLC/MLC/TLC/QLC 分类、data sheet、技术笔记、固件 |
| Kioxia | BiCS FLASH 产品页、内存产品目录页、技术解释与历史页 | BiCS 代际、应用分段、术语锚定 |
| Samsung | V-NAND 技术博客与术语表、第九代 V-NAND 发布页 | V-NAND 结构、干扰术语、代际带宽与密度claims |
| SK hynix | 官方公司/产品入口、4D NAND 新闻标签、321 层/238 层发布 | 4D NAND 里程碑、238 层/321 层具体claims |
| YMTC | 3D NAND Flash Memory 产品列表、Xtacking 架构页面 | X1/X2/X3/X4 代际、晶圆键合架构定位 |
| Sandisk | BiCS10 发布页（2025 年 WD 闪存业务分离后） | 当前 BiCS10 TLC claims、密度与功耗定位 |

Western Digital 于 2025 年 2 月 24 日宣布完成闪存业务分离，当前闪存资料应查阅 Sandisk。^[research-nand-controller-patent-notes.md:26] 新闻稿和营销页面不暴露完整的器件时序、ECC 预算或控制器固件要求，应交叉验证 data sheet 或产品指南。^[research-nand-controller-patent-notes.md]

### 可信度分级

| 级别 | 说明 | 适用场景 |
|---|---|---|
| explicit product brief | 页面或 PDF 明确声明 | 可进入 vendor intake |
| guide / product guide | 细节更丰富但仍属公开参考 | 用于接口和模块边界 |
| marketing language | 只有定位或卖点描述 | 仅用于术语和 backlog |
| inferred | 从产品命名、市场定位或对标项目推断 | 仅供探索，不作事实 |

## 采集标签体系

为便于知识库分类与追溯，建议使用以下标签体系：^[research-nand-controller-patent-notes.md:62-78]

| 标签前缀 | 用途 | 示例 |
|---|---|---|
| `vendor/{厂商}/{技术}` | 厂商 NAND/SSD 公开资料 | `vendor/micron/nand`、`vendor/kioxia/bics`、`vendor/samsung/v-nand` |
| `patent/cpc/{符号}` | 按 CPC 分类的专利采集 | `patent/cpc/g06f-3-06`、`patent/cpc/h03m-13` |
| `patent/topic/{主题}` | 按技术主题聚合的专利采集 | `patent/topic/plp`、`patent/topic/slc-cache`、`patent/topic/fdp-placement` |

## 常见采集误区

- 将营销特性列表等同于可实现接口。^[research-nand-controller-patent-notes.md:8]
- 将 guide 中的模块名称直接当作 RTL 模块边界。^[research-nand-controller-patent-notes.md:8]
- 将 "enterprise" 或 "client" 当成统一功能集合，不区分具体代际。^[research-nand-controller-patent-notes.md:8]
- 未记录版本和 sha256，导致后续无法追溯。^[research-nand-controller-patent-notes.md:8]
- 将公开资料的术语误写成已验证的实现细节。^[research-nand-controller-patent-notes.md:8]

## 工具链输出流向

采集结果应进入以下知识库页面：

- 控制器厂商数据采集与建模
- 控制器硬件模块边界
- 控制器 RTL / IP 参考
- ECC、LDPC 与可靠性管理
- DRAM-less SSD 与 Host Memory Buffer
- 量产需求与合规
- 遥测、日志与现场调试

## Sources

- research-nand-controller-patent-notes.md

[research-nand-controller-patent-notes.md]: research-nand-controller-patent-notes.md

# Citations

1. [research-nand-controller-patent-notes.md:34-34](/references/research-nand-controller-patent-notes-8985793f.md)
2. [research-nand-controller-patent-notes.md:36-36](/references/research-nand-controller-patent-notes-8985793f.md)
3. [research-nand-controller-patent-notes.md:37-37](/references/research-nand-controller-patent-notes-8985793f.md)
4. [research-nand-controller-patent-notes.md:37-43](/references/research-nand-controller-patent-notes-8985793f.md)
5. [research-nand-controller-patent-notes.md:38-38](/references/research-nand-controller-patent-notes-8985793f.md)
6. [research-nand-controller-patent-notes.md:40-40](/references/research-nand-controller-patent-notes-8985793f.md)
7. [research-nand-controller-patent-notes.md:42-42](/references/research-nand-controller-patent-notes-8985793f.md)
8. [research-nand-controller-patent-notes.md:44-48](/references/research-nand-controller-patent-notes-8985793f.md)
9. [research-nand-controller-patent-notes.md:44-44](/references/research-nand-controller-patent-notes-8985793f.md)
10. [research-nand-controller-patent-notes.md:48-48](/references/research-nand-controller-patent-notes-8985793f.md)
11. [research-nand-controller-patent-notes.md:53-60](/references/research-nand-controller-patent-notes-8985793f.md)
12. [research-nand-controller-patent-notes.md:55-55](/references/research-nand-controller-patent-notes-8985793f.md)
13. [research-nand-controller-patent-notes.md:59-59](/references/research-nand-controller-patent-notes-8985793f.md)
14. [research-nand-controller-patent-notes.md:7-28](/references/research-nand-controller-patent-notes-8985793f.md)
15. [research-nand-controller-patent-notes.md:26-26](/references/research-nand-controller-patent-notes-8985793f.md)
16. [research-nand-controller-patent-notes.md](/references/research-nand-controller-patent-notes-8985793f.md)
17. [research-nand-controller-patent-notes.md:62-78](/references/research-nand-controller-patent-notes-8985793f.md)
18. [research-nand-controller-patent-notes.md:8-8](/references/research-nand-controller-patent-notes-8985793f.md)
