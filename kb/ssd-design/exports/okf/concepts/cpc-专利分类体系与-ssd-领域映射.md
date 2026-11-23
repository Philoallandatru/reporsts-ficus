---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 64e1ac207af1ad9666b17ebd3556a53ab3643b30efcd933476d0c623e28e8f4b
  pageDirectory: concepts
  sources:
    - research-nand-controller-patent-notes-53079fdd.md
  confidence: 0.92
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - cpc-专利分类体系与-ssd-领域映射
    - C专S领
  citations:
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 44
      end: 45
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 45
      end: 45
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 51
      end: 51
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 46
      end: 46
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 47
      end: 47
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 48
      end: 48
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 49
      end: 49
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 50
      end: 50
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 51
      end: 56
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 41
      end: 43
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 58
      end: 67
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 69
      end: 85
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 44
      end: 44
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 56
      end: 56
title: CPC 专利分类体系与 SSD 领域映射
description: G06F 3/06（数字 I/O 到记录介质）、G06F 12/00（内存寻址/分配）、G11C 16/00（NAND 编程/读取/擦除）、H03M 13（LDPC/BCH 编码）、H10B（3D NAND 器件结构）等 CPC 分类号在 SSD/闪存专利检索中的应用与局限。
tags:
  - patent
  - cpc-classification
  - ssd
timestamp: "2026-08-16T05:49:42.856Z"
---


# CPC 专利分类体系与 SSD 领域映射

CPC（Cooperative Patent Classification，合作专利分类）是由美国专利商标局（USPTO）和欧洲专利局（EPO）联合管理的专利分类体系，广泛用于 SSD 控制器、固件、介质管理与可靠性领域的专利检索与归类。本页面整理 CPC 主干分类与 SSD 各子领域之间的对应关系，为知识库的专利检索入口提供结构化参考。 ^[research-nand-controller-patent-notes-53079fdd.md:44-45]

## 主要分类节点

### G06F 3/06 —— SSD 控制器与存储接口

G06F 3/06 是 SSD 相关专利的首要入口，USPTO 将其定义为"数字输入/输出至记录载体的操作"，涵盖 RAID、仿真记录载体和网络化记录载体等场景。^[research-nand-controller-patent-notes-53079fdd.md:45]

适用关键词包括：`solid state drive`、`flash translation layer`、`garbage collection`、`wear leveling`、`write amplification`、`namespace`、`stream`、`FDP`。由于 G06F 类目较广，建议结合 assignee 过滤器和日期过滤以缩小结果范围。 ^[research-nand-controller-patent-notes-53079fdd.md:45]

该分类下的典型专利示例可见于 FTL 垃圾收集与磨损均衡_seed 专利，其文本明确讨论了 FTL 行为、块压缩、动态磨损均衡、静态磨损均衡和逻辑至物理地址重映射。 ^[research-nand-controller-patent-notes-53079fdd.md:51]

### G06F 12/00 —— 内存寻址与分配

G06F 12/00 用于覆盖内存系统或架构内的访问、寻址或分配操作，在 SSD 语境下常与 FTL 映射表、缓存管理和数据放置存在交叉。 ^[research-nand-controller-patent-notes-53079fdd.md:46]

该分类并非 SSD 专用，建议与 `NAND`、`SSD`、`FTL` 或 `non-volatile memory` 等关键词组合使用，以排除通用内存管理专利。 ^[research-nand-controller-patent-notes-53079fdd.md:46]

### G06F 11/00 —— 错误检测与纠正

G06F 11/00 是计算系统错误检测、纠错和监控的总分类，与 SSD 控制器层面的错误处理机制直接相关。 ^[research-nand-controller-patent-notes-53079fdd.md:47]

需注意：LDPC 码字构造本身通常归入 H03M 13，NAND 芯片级测试与修复则可能归入 G11C 29/00，检索时应使用交叉分类查询以获得完整覆盖。 ^[research-nand-controller-patent-notes-53079fdd.md:47]

### G11C 16/00 —— NAND 器件物理与电路

G11C 16/00 覆盖可擦除可编程只读存储器，尤其包括 NAND 编程/读取/擦除、干扰、感知、阈值、保持和磨损机制等子主题。 ^[research-nand-controller-patent-notes-53079fdd.md:48]

该分类更偏向存储器件内部行为，与 SSD 固件策略的专利存在交叉但侧重不同。组合 G06F 3/06 进行联合查询，有助于覆盖同时涉及器件行为和控制器发明的专利。 ^[research-nand-controller-patent-notes-53079fdd.md:48]

### H10B —— 存储器器件结构

H10B 用于横跨检查单个电子存储器器件结构，尤其涉及 3D NAND 核心/外围/阶梯结构概念。 ^[research-nand-controller-patent-notes-53079fdd.md:49]

该分类以器件结构为主，会遗漏大量固件、主机接口和系统级 SSD 专利，因此仅作为辅助验证手段使用。 ^[research-nand-controller-patent-notes-53079fdd.md:49]

### H03M 13 —— LDPC 与信道编码

H03M 13 是 LDPC、BCH、Reed-Solomon、迭代译码、软判决译码、率兼容 LDPC 和实现复杂度相关专利的归属分类。 ^[research-nand-controller-patent-notes-53079fdd.md:50]

该分类并非存储专用，建议结合 `NAND`、`flash memory`、`SSD controller`、`read retry`、`soft bit`、`LLR` 和 `decoder latency` 等关键词约束结果。 ^[research-nand-controller-patent-notes-53079fdd.md:50]

## SSD 子领域与 CPC 映射表

| SSD 子领域 | 主要 CPC 分类 | 辅助 CPC 分类 | 典型关键词 |
|---|---|---|---|
| FTL / 垃圾回收 / 磨损均衡 | G06F 3/06 | G06F 12/00 | `flash translation layer`、`logical to physical`、`mapping table`、`block compaction` |
| 错误纠正 / LDPC / 软判决 | H03M 13 | G06F 11/00 | `LDPC`、`soft decoding`、`read retry`、`LLR`、`read threshold` |
| NAND 器件物理 / 干扰 / 保持性 | G11C 16/00 | H10B | `threshold voltage`、`disturb`、`retention`、`read disturb`、`P/E cycle` |
| 掉电保护 / PLP | G06F 3/06 | G06F 11/00 | `power loss protection`、`capacitor`、`backup power`、`super capacitor` |
| SLC 缓存 / 混合级存储 | G06F 3/06 | — | `SLC cache`、`pseudo-SLC`、`hybrid cache`、`folding`、`direct-to-TLC` |
| 数据放置 / FDP / Stream | G06F 3/06 | — | `flexible data placement`、`reclaim unit`、`placement identifier`、`write stream` |

## 种子专利参考

以下专利可用作各子领域检索的种子，通过 Google Patents 获取后可追踪引用、 assignee 和同族信息：

| 子领域 | 种子专利主题 | 用途 |
|---|---|---|
| FTL / GC / 磨损均衡 | FTL, block compaction, dynamic/static wear leveling | 收割关键词、 assignee、CPC 标记和后向引用 |
| 掉电保护 | SSD power loss protection, backup power source | 提取硬件能量储备与固件 flush/shutdown 行为描述 |
| SLC 缓存 | SLC/MLC/TLC cache management | 识别混合级非易失存储的控制器策略 |
| LDPC | LDPC decoding, error statistics, storage device monitoring | 关联纠错统计与存储设备 LDPC 监控 |
| 数据放置 / FDP | Flexible data placement, reclaim unit, device-level GC | 对齐 NVMe FDP 标准术语与专利实现描述 |

^[research-nand-controller-patent-notes-53079fdd.md:51-56]

## 检索工具建议

| 工具 | 适用场景 | 局限 |
|---|---|---|
| Google Patents 高级检索 | 快速发现、assignee 过滤、CPC 过滤、引用追踪、机器翻译 | 非法律记录系统，法律状态需通过 USPTO Patent Center 核实 |
| USPTO Patent Public Search | 权威美国专利检索入口，包含基础和高级检索 | 侧重美国专利；CN/EP/WO 同族需通过 Google Patents 或各国专利局补充 |
| USPTO Patent Center | 按申请号、专利号、PCT 号或公开号查询申请状态和文档 | 不便于大规模关键词发现，适合已知专利的确认而非首轮挖掘 |

^[research-nand-controller-patent-notes-53079fdd.md:41-43]

## 可复用查询语句

以下查询语句可直接在 Google Patents 使用，建议根据具体需求增删关键词并限定 assignee 或日期范围：

| 主题 | 查询示例 |
|---|---|
| FTL / 垃圾回收 / 磨损均衡 | `flash translation layer` SSD `garbage collection` `wear leveling` |
| 掉电保护 | `solid state drive` `power loss protection` capacitor flush |
| LDPC / 软判决 | NAND LDPC `soft decoding` `read retry` |
| SLC 缓存 / pSLC | `SLC cache` SSD TLC QLC `pseudo-SLC` |
| 数据放置 / FDP / Stream | `flexible data placement` SSD `reclaim unit` `placement identifier` |
| NAND 器件 / 干扰 / 保持性 | `NAND flash` `threshold voltage` disturb retention `read retry` |

^[research-nand-controller-patent-notes-53079fdd.md:58-67]

## 摄入标签约定

知识库中建议为专利摄入记录分配以下标签，以支持后续检索和归类：

| 标签 | 适用对象 |
|---|---|
| `patent/cpc/g06f-3-06` | SSD 控制器、主机接口、FTL、GC、放置、RAID 类存储专利 |
| `patent/cpc/g11c-16` | NAND 编程/读取/擦除、感知、干扰、保持性、磨损机制专利 |
| `patent/cpc/h03m-13` | LDPC/BCH/RS 编码、迭代译码、软判决、ECC 硬件实现专利 |
| `patent/topic/plp` | 掉电保护、瞬时断电恢复、电容备份 flush、元数据持久化专利 |
| `patent/topic/slc-cache` | SLC 缓存、伪 SLC、混合缓存、折叠、动态单级/多级配置专利 |
| `patent/topic/fdp-placement` | FDP、Stream、放置标识符、回收单元、热/冷数据分离、WAF 降低专利 |

^[research-nand-controller-patent-notes-53079fdd.md:69-85]

## 注意事项

- CPC 分类符号频繁修订，建议在摄入时记录 CPC 版本和日期，并在后续审查中关注重新分类提示。 ^[research-nand-controller-patent-notes-53079fdd.md:44]
- 公开专利可能使用与标准协议不同的术语；早期 FDP 相关发明可能出现在 `stream`、`data temperature`、`host hint` 等查询下，而非 FDP 本身。 ^[research-nand-controller-patent-notes-53079fdd.md:56]
- 专利检索应与 NVMe 规范摄入分开进行，以避免将规范性协议行为与声称的实现方式混淆。 ^[research-nand-controller-patent-notes-53079fdd.md:56]
- Marketing 功能列表不等于可实现接口；指南中的模块名称不等于 RTL 模块边界；需区分产品定位语言与工程接口描述。 ^[research-nand-controller-patent-notes-53079fdd.md:45]

## Sources

- [NAND Controller and Patent Research Notes](../../sources/research-nand-controller-patent-notes-53079fdd.md)

# Citations

1. [research-nand-controller-patent-notes-53079fdd.md:44-45](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
2. [research-nand-controller-patent-notes-53079fdd.md:45-45](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
3. [research-nand-controller-patent-notes-53079fdd.md:51-51](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
4. [research-nand-controller-patent-notes-53079fdd.md:46-46](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
5. [research-nand-controller-patent-notes-53079fdd.md:47-47](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
6. [research-nand-controller-patent-notes-53079fdd.md:48-48](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
7. [research-nand-controller-patent-notes-53079fdd.md:49-49](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
8. [research-nand-controller-patent-notes-53079fdd.md:50-50](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
9. [research-nand-controller-patent-notes-53079fdd.md:51-56](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
10. [research-nand-controller-patent-notes-53079fdd.md:41-43](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
11. [research-nand-controller-patent-notes-53079fdd.md:58-67](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
12. [research-nand-controller-patent-notes-53079fdd.md:69-85](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
13. [research-nand-controller-patent-notes-53079fdd.md:44-44](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
14. [research-nand-controller-patent-notes-53079fdd.md:56-56](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
