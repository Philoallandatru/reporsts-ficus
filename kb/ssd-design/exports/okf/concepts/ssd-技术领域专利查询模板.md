---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: bde6057c70fd0a002b897111a09adeff975551914b85a842fe68a08fcca5a5e3
  pageDirectory: concepts
  sources:
    - research-nand-controller-patent-notes-53079fdd.md
  confidence: 0.9
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - ssd-技术领域专利查询模板
  citations:
    - file: research-nand-controller-patent-notes-53079fdd.md
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 41
      end: 44
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 45
      end: 50
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 58
      end: 68
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 61
      end: 63
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 64
      end: 66
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 67
      end: 69
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 70
      end: 72
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 73
      end: 75
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 76
      end: 78
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 51
      end: 56
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 69
      end: 84
title: SSD 技术领域专利查询模板
description: FTL/垃圾回收/磨损均衡、PLP/掉电保护、LDPC/软解码、SLC 缓存/pSLC、Placement/FDP/Streams、NAND 器件/干扰/保持力等六大方向的专利查询 Starter URL 与关键词扩展建议。
tags:
  - patent
  - query-template
  - ssd
timestamp: "2026-08-16T05:50:25.629Z"
---


# SSD 技术领域专利查询模板

本页面整理了针对 SSD 控制器固件、FTL、NAND 可靠性和数据放置等领域的专利查询起点。包括检索工具入口、CPC 分类锚点、可复用查询模板和摄取标签约定，适用于 FTL 元数据格式与恢复约定 和 ECC、LDPC 与可靠性管理 等方向的专利态势分析。^[research-nand-controller-patent-notes-53079fdd.md]

## 检索工具入口

| 工具 | 适用场景 | 入口地址 | 注意事项 |
|---|---|---|---|
| Google Patents 高级检索 | 快速发现、 assignee 过滤、CPC 过滤、引用追踪、机器翻译 | https://www.google.com/advanced_patent_search | 非法定系统记录地；需要法律状态时通过 USPTO Patent Center 或对应专利局核实 |
| USPTO Patent Public Search | 权威美国专利和公开申请检索 | https://www.uspto.gov/patets/search/patent-public-search | 仅覆盖美国；CN/EP/WO 同族成员需通过 Google Patents 同族链接或官方区域专利局检索 |
| USPTO Patent Center | 按申请号、专利号、PCT 号或公开号查询申请状态 | https://patentcenter.uspto.gov | 不便于宽泛关键词发现；适合候选专利确认，不适合初筛 |
| CPC 官方表 | 保持知识库分类术语与最新 CPC 版本对齐 | https://www.cooperativepatentclassification.org/cpcSchemeAndDefinitions/table | CPC 符号频繁修订；摄取时记录 CPC 版本和日期 |

CPC 由 USPTO 和 EPO 联合管理，是本知识库专利分类的主要词汇表。^[research-nand-controller-patent-notes-53079fdd.md:41-44]

## CPC 分类锚点

以下 CPC 分类覆盖 SSD 控制器专利的核心领域，查询时应与关键词组合使用以减少无关结果。^[research-nand-controller-patent-notes-53079fdd.md:45-50]

| 领域 | CPC 分类 | 说明 | 搭配关键词 |
|---|---|---|---|
| SSD 控制器 / FTL / GC / 放置 / RAID | **G06F 3/06** | 数字输入/输出至记录载体的主类，包含 RAID、仿真记录载体和网络化记录载体 | "solid state drive", "flash translation layer", "garbage collection", "wear leveling", "write amplification", "namespace", "stream", "FDP" |
| 内存寻址 / 分配 | **G06F 12/00** | 内存系统或架构内的访问、寻址或分配子类的辅助分类 | "NAND", "SSD", "FTL", "non-volatile memory" |
| 错误检测 / 纠正 / 监控 | **G06F 11/00** | 计算系统错误检测与纠正，含静态存储和记录载体相关引用 | LDPC 码结构本身常归入 H03M 13；NAND 器件测试/修复可能归入 G11C 29/00 |
| NAND 器件物理 / 电路 / 阈值 / 保持 / 磨损 | **G11C 16/00** | 可擦除可编程只读存储器，含 NAND program/read/erase、disturb、sensing、阈值、保持和磨损机制 | 器件内部发明多于 SSD 固件策略发明；需与 G06F 3/06 组合检索 |
| NAND 器件结构 / 3D NAND | **H10B** | 半导体/固态存储器件结构，包含 NAND string、core region、peripheral region、3D NAND staircase | 器件结构导向，会遗漏固件、主机接口和系统级 SSD 专利 |
| LDPC / BCH / RS / 软解码 / 迭代解码 | **H03M 13** | LDPC 特定分支如 QC-LDPC、LDPC 卷积码、迭代解码、速率兼容 LDPC | 非存储专用；需组合 "NAND", "flash memory", "SSD controller", "read retry", "soft bit", "LLR", "decoder latency" |

## 可复用查询模板

以下模板为常见 SSD 技术方向提供起点式查询组合，可直接复制到 Google Patents 使用。^[research-nand-controller-patent-notes-53079fdd.md:58-68]

### FTL / 垃圾回收 / 磨损均衡

```
"flash translation layer" SSD "garbage collection" "wear leveling"
```

覆盖 FTL 映射、GC、压缩和磨损均衡专利的常用控制器-固件词汇表。查询可能过度匹配恰好使用 "FTL" 术语的文档，应补充 "logical to physical"、"mapping table"、"valid page"、"block compaction" 等变体。^[research-nand-controller-patent-notes-53079fdd.md:61-63]

### PLP / 掉电保护

```
"solid state drive" "power loss protection" capacitor flush
```

直接针对 SSD PLP 实现，组合硬件能量储备和固件 flush/shutdown 行为。需注意部分厂商使用 "sudden power off recovery"、"SPOR"、"power fail"、"backup power"、"supercapacitor" 等替代术语，建议运行变体查询。^[research-nand-controller-patent-notes-53079fdd.md:64-66]

### LDPC / 软解码 / 读重试

```
NAND LDPC "soft decoding" "read retry"
```

针对 NAND 可靠性、ECC 和控制器读恢复管道的交叉领域。可能在未加约束时检索到通信编码专利，需组合 NAND、flash memory、SSD controller 或 G06F/G11C 类过滤。^[research-nand-controller-patent-notes-53079fdd.md:67-69]

### SLC Cache / pSLC

```
"SLC cache" SSD TLC QLC "pseudo-SLC"
```

针对通过以 SLC 模式编程多比特单元换取写入性能的控制器策略。大量专利可能避免使用 "SLC cache" 短语，应补充 "single level mode"、"folding"、"hybrid cache"、"multi-level memory" 等同义表达。^[research-nand-controller-patent-notes-53079fdd.md:70-72]

### 放置 / FDP / 流

```
"flexible data placement" SSD "reclaim unit" "placement identifier"
```

针对与内部 GC 和写放大交互的现代主机定向放置和类 FDP 接口。更早的发明可能使用 "write stream"、"data temperature"、"hot/cold data"、"host hint" 而非 FDP 术语。^[research-nand-controller-patent-notes-53079fdd.md:73-75]

### NAND 器件 / Disturb / 保持

```
"NAND flash" "threshold voltage" disturb retention "read retry"
```

针对控制器固件必须补偿的底层器件行为。可能在未加约束时检索到器件/电路专利，需组合 G11C/H10B 与 G06F 来筛选控制器相关内容。^[research-nand-controller-patent-notes-53079fdd.md:76-78]

## 种子专利参考

以下种子专利从公开资料中识别，可用于收获关键词、 assignee、CPC 符号、后向引用和同族链接。^[research-nand-controller-patent-notes-53079fdd.md:51-56]

| 领域 | 种子专利 | 说明 |
|---|---|---|
| FTL / 块压缩 / 磨损均衡 | US20120317377A1 | 文本明确讨论 FTL 行为、块压缩、动态磨损均衡、静态磨损均衡和逻辑到物理重映射 |
| PLP / 掉电保护 / 超级电容 | US20170185335A1 | 明确描述 SSD 掉电保护框架和备用电源上下文 |
| SLC Cache / 混合级存储 | US20220129168A1 | 明确覆盖 SLC 存储单元作为 MLC 容量权衡的高速缓存 |
| LDPC / 纠错统计 | US8413029B2 | 明确讨论 LDPC 解码、纠正错误统计和存储设备误码率观察 |
| FDP / 放置 / 回收单元 | US12405729B2 | 明确引用灵活数据放置、回收单元、句柄和设备级 GC 影响 |

## 摄取标签约定

摄取结果应标记以下标签，以便跨页面追溯和分类。^[research-nand-controller-patent-notes-53079fdd.md:69-84]

### 厂商标签

| 标签 | 适用内容 | 典型来源 |
|---|---|---|
| `vendor/micron/nand` | Micron NAND 落地页、代际页、数据表、技术说明和下载门户记录 | https://www.micron.com/products/storage/nand-flash |
| `vendor/kioxia/bics` | BiCS FLASH 代际、Kioxia 内存页面和 Kioxia/Sandisk 联合 BiCS 发布 | https://www.kioxia.com/en-jp/business/memory/bics.html |
| `vendor/samsung/v-nand` | V-NAND 术语表、V-NAND 代际发布和 Samsung SSD/FDP 技术上下文 | https://semiconductor.samsung.com |
| `vendor/skhynix/4d-nand` | 4D NAND 发布、238 层/321 层说明和 SK hynix 存储方案里程碑 | https://news.skhynix.com/en/tag/4d-nand/ |
| `vendor/ymtc/xtacking` | Xtacking 架构、X 系列 NAND 和提及 HMB/SLC/混合缓存的 YMTC SSD 页面 | https://www.ymtc.com/en/technicalintroduction.html |
| `vendor/wd-sandisk/bics` | 历史 WD BiCS 说明和分离后当前 Sandisk BiCS 说明 | https://www.sandisk.com |

### 专利主题标签

| 标签 | 覆盖范围 |
|---|---|
| `patent/cpc/g06f-3-06` | SSD 控制器、主机接口、存储虚拟化、FTL、GC、放置和 RAID 类存储专利 |
| `patent/cpc/g11c-16` | NAND program/read/erase、sensing、disturb、保持、磨损和存储单元行为专利 |
| `patent/cpc/h03m-13` | LDPC/BCH/RS 编码、迭代解码、软解码和 ECC 硬件实现专利 |
| `patent/topic/plp` | 掉电保护、突发断电报恢复、电容备份 flush 和元数据保留专利 |
| `patent/topic/slc-cache` | SLC 缓存、pseudo-SLC、混合缓存、折叠和动态单级/多级配置专利 |
| `patent/topic/fdp-placement` | FDP、流、主机提示、放置标识符、回收单元、热/冷数据分离和 WAF 降低专利 |

## 常见误区

- 将 marketing feature list 当成可实现接口：专利公开的机制描述不等于产品化阈值或固件启发式算法。
- 把公开专利的模块名称直接当成 RTL 模块边界：专利文本使用控制器固件词汇，不等于硬件实现切分。
- 把 "enterprise" 或 "client" 当成统一功能集合：不同代际之间的能力差异需逐件核实。
- 把公开专利的术语误写成已验证实现细节：专利检索应与 控制器硬件模块边界 和 控制器 RTL / IP 参考 的验证工作分开。
- 未记录版本和 sha256 导致后续无法追溯：每次摄取应保留 source URL、access date 和 document version。^[research-nand-controller-patent-notes-53079fdd.md]

## 与知识库其他页面的关系

本页面为专利态势分析提供入口模板，具体技术方向可结合以下页面深化检索：

- 控制器硬件模块边界：提供模块级术语对照表，补充专利检索的硬件视角关键词。
- 控制器 RTL / IP 参考：提供 RTL 接口词汇，补充 FPGA/ASIC 实现相关的专利发现路径。
- ECC、LDPC 与可靠性管理：LDPC pipeline、read retry 和元数据 ECC 保护的详细技术背景。
- DRAM-less SSD 与 Host Memory Buffer：HMB 设计中的安全隔离和掉电恢复背景。
- 掉电保护与恢复：PLP 路径、journal 和 checkpoint 的技术上下文。

## Sources

- [research-nand-controller-patent-notes-53079fdd.md](research-nand-controller-patent-notes-53079fdd.md) — NAND Controller and Patent Research Notes，包含检索工具入口、CPC 分类锚点、查询模板和摄取标签约定的完整源表。

# Citations

1. [research-nand-controller-patent-notes-53079fdd.md](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
2. [research-nand-controller-patent-notes-53079fdd.md:41-44](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
3. [research-nand-controller-patent-notes-53079fdd.md:45-50](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
4. [research-nand-controller-patent-notes-53079fdd.md:58-68](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
5. [research-nand-controller-patent-notes-53079fdd.md:61-63](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
6. [research-nand-controller-patent-notes-53079fdd.md:64-66](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
7. [research-nand-controller-patent-notes-53079fdd.md:67-69](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
8. [research-nand-controller-patent-notes-53079fdd.md:70-72](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
9. [research-nand-controller-patent-notes-53079fdd.md:73-75](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
10. [research-nand-controller-patent-notes-53079fdd.md:76-78](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
11. [research-nand-controller-patent-notes-53079fdd.md:51-56](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
12. [research-nand-controller-patent-notes-53079fdd.md:69-84](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
