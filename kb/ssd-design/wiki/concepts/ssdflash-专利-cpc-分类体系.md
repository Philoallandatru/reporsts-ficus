---
title: SSD/Flash 专利 CPC 分类体系
summary: G06F 3/06（SSD控制器/FTL/GC）、G11C 16/00（NAND 器件物理）、H03M 13（LDPC/ECC）、H10B（3D
  NAND 结构）等关键 CPC 分类代码及用途
sources:
- research-nand-controller-patent-notes.md
kind: concept
createdAt: '2026-08-16T05:51:36.373Z'
updatedAt: '2026-08-16T05:51:36.373Z'
tags:
- patent
- classification
- cpc
- ssd
aliases:
- ssdflash-专利-cpc-分类体系
- S专C分
confidence: 0.95
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: CPC（Cooperative Patent Classification）是美国专利商标局（USPTO）与欧洲专利局（EPO）联合管理的专利分类体系。对于
  SSD 和 NAND Flash 相关专利，CPC 提供了一套层次化的分类词汇，用于定位控制器、固件、介质、纠错和数据放置等不同技术方向的发明。
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# SSD/Flash 专利 CPC 分类体系

CPC（Cooperative Patent Classification）是美国专利商标局（USPTO）与欧洲专利局（EPO）联合管理的专利分类体系。对于 SSD 和 NAND Flash 相关专利，CPC 提供了一套层次化的分类词汇，用于定位控制器、固件、介质、纠错和数据放置等不同技术方向的发明。

本文档整理了 SSD/Flash 领域专利检索中使用的主要 CPC 类别、搜索工具入口和可复用的查询模板。

## 分类体系概览

CPC 分类在 SSD/Flash 专利检索中的核心价值在于将分散在 G06F、G11C、H03M、H10B 等大类下的技术术语组织为可查询的层级结构。不同类别覆盖了从主机接口到底层器件的完整技术栈 ^[research-nand-controller-patent-notes.md:37-38]。

主要分类节点包括：

- **G06F 3/06**：数字输入/输出到记录载体的操作，涵盖 SSD 控制器、FTL、垃圾回收、命名空间和流数据放置等上层发明。
- **G06F 12/00**：内存系统或架构内的访问、寻址或分配，通常与 FTL 映射表、缓存和放置策略重叠。
- **G06F 11/00**：错误检测、纠错和监控，覆盖 SSD 控制器的可靠性机制。
- **G11C 16/00**：可擦除可编程只读存储器及其子组，覆盖 NAND 编程/读取/擦除、干扰、保持和磨损机制。
- **H10B**：固态电子存储器器件结构，特别涉及 3D NAND 核心/外围/阶梯结构概念。
- **H03M 13**：LDPC、BCH、Reed-Solomon、迭代解码和软解码等信道编码技术。

## 核心 CPC 类别详解

### G06F 3/06 — SSD 控制器与存储接口

G06F 3/06 是 SSD 专利分类的核心锚点。USPTO 的 CPC 方案将其定义为数字输入/输出到记录载体的操作，包括 RAID、模拟记录载体和网络化记录载体 ^[research-nand-controller-patent-notes.md:38-39]。

该类别覆盖的技术领域包括：

- SSD 控制器架构与主机接口（PCIe、NVMe）
- 闪存转换层（FTL）与逻辑到物理地址映射
- 垃圾回收（GC）与块 compaction
- 磨损均衡（wear leveling）
- 写放大（write amplification）控制
- 命名空间（namespace）管理
- 流（stream）和灵活数据放置（FDP）

搜索时建议搭配关键词 `solid state drive`、`flash translation layer`、`garbage collection`、`wear leveling`、`write amplification`、`namespace`、`stream` 和 `FDP` 使用 ^[research-nand-controller-patent-notes.md:38-39]。

### G06F 12/00 — 内存寻址与分配

G06F 12/00 作为辅助类别，覆盖内存系统或架构内的访问、寻址或分配行为 ^[research-nand-controller-patent-notes.md:39-40]。

在 SSD 场景下，该类别常与 FTL 映射表、缓存管理和数据放置重叠。需要注意的是，G06F 12/00 并非 SSD 专用类别，搜索时应搭配 `NAND`、`SSD`、`FTL` 或 `non-volatile memory` 等限定词以减少不相关结果。

### G06F 11/00 — 错误检测与纠正

G06F 11/00 及其子分支（G06F 11/07、G06F 11/08）覆盖计算系统的错误检测、纠错和监控行为 ^[research-nand-controller-patent-notes.md:40-41]。

在 SSD 专利检索中，该类别适用于：

- LDPC 码构造以外的存储设备纠错机制
- 错误率监控与统计上报
- 读重试策略与阈值调整

需要注意的是，LDPC 码的构造本身通常归入 H03M 13，而 NAND 器件测试与修复可能归入 G11C 29/00 ^[research-nand-controller-patent-notes.md:40-41]。

### G11C 16/00 — NAND 器件物理层

G11C 16/00 是器件层面的核心类别，覆盖可擦除可编程只读存储器的操作方法 ^[research-nand-controller-patent-notes.md:41-42]。

该类别覆盖的具体技术点包括：

- NAND 编程/读取/擦除时序与命令
- 阈值电压分布与感知
- 干扰（disturb）机制与防护
- 数据保持（retention）特性
- 单元磨损（wearout）行为

该类别更偏向存储器器件内部原理，而非 SSD 固件策略。控制器相关发明通常需要与 G06F 3/06 联合查询。

### H10B — NAND 器件结构

H10B 作为交叉核对类别，覆盖固态电子存储器器件结构，尤其适用于 3D NAND 核心/外围/阶梯结构概念的专利 ^[research-nand-controller-patent-notes.md:42-43]。

该类别以器件结构为主，会遗漏大量固件、主机接口和系统级 SSD 专利。

### H03M 13 — LDPC 与信道编码

H03M 13 是纠错编码的核心类别，覆盖 LDPC、BCH、Reed-Solomon、迭代解码、软判决解码和速率兼容 LDPC 等技术 ^[research-nand-controller-patent-notes.md:43-44]。

在 SSD 专利检索中，该类别适用于：

- LDPC 解码器架构与实现
- 软判决信息生成与 LLR（对数似然比）计算
- 读阈值调整与重试策略
- 解码器延迟与吞吐率优化

由于 H03M 13 并非存储专用类别，搜索时应搭配 `NAND`、`flash memory`、`SSD controller`、`read retry`、`soft bit`、`LLR`、`decoder latency` 等限定词。

## 搜索工具

| 工具 | 用途 | 特点 |
|---|---|---|
| Google Patents 高级搜索 | 快速发现、 assignee 过滤、CPC 过滤、引用链追踪、机器翻译 | 适合 broad SSD/FTL/LDPC 查询探索 ^[research-nand-controller-patent-notes.md:34] |
| USPTO Patent Public Search | 美国专利与已公开申请的权威检索入口 | 提供基础和高级搜索功能 ^[research-nand-controller-patent-notes.md:35] |
| USPTO Patent Center | 按申请号、专利号、PCT 号或公开号查询申请状态 | 适合确认已发现专利的法律状态 ^[research-nand-controller-patent-notes.md:36] |
| 官方 CPC 表格 | 获取最新 CPC 分类版本 | CPC 符号频繁修订，检索时应记录版本和日期 ^[research-nand-controller-patent-notes.md:37] |

## 可复用查询模板

### FTL / 垃圾回收 / 磨损均衡

查询入口：`"flash translation layer" SSD "garbage collection" "wear leveling"`

该查询针对最常见的控制器固件词汇集，应能检索到 FTL 映射、GC、compaction 和磨损均衡相关专利。需要注意部分专利可能使用 `logical to physical`、`mapping table`、`valid page` 或 `block compaction` 等替代术语 ^[research-nand-controller-patent-notes.md:53-56]。

### PLP / 掉电保护

查询入口：`"solid state drive" "power loss protection" capacitor flush`

该查询直接针对 SSD 掉电保护的硬件能量储备与固件 flush/shutdown 行为的组合实现。厂商术语可能包括 `sudden power off recovery`、`SPOR`、`power fail`、`backup power` 或 `supercapacitor`，需要运行变体查询以覆盖完整 ^[research-nand-controller-patent-notes.md:56-57]。

### LDPC / 软解码

查询入口：`NAND LDPC "soft decoding" "read retry"`

该查询针对 NAND 可靠性、ECC 和控制器读恢复管道的交叉领域。需要注意可能检索到通信编码专利，除非使用 NAND、flash memory、SSD controller 或 G06F/G11C 类别加以约束 ^[research-nand-controller-patent-notes.md:57-58]。

### SLC 缓存 / 伪 SLC

查询入口：`"SLC cache" SSD TLC QLC "pseudo-SLC"`

该查询针对控制器策略中以 SLC 模式编程多 bit 单元以换取写入性能的设计。许多专利避免使用 `SLC cache` 短语，应重复使用 `single level mode`、`folding`、`hybrid cache` 和 `multi-level memory` 等变体进行补充查询 ^[research-nand-controller-patent-notes.md:58-59]。

### 数据放置 / FDP / 流

查询入口：`"flexible data placement" SSD "reclaim unit" "placement identifier"`

该查询针对现代主机导向的放置策略和与内部 GC、写放大相互作用的 FDP 类接口。老旧发明可能使用 `write stream`、`data temperature`、`hot/cold data` 或 `host hint` 而非 FDP 术语 ^[research-nand-controller-patent-notes.md:59-60]。

### NAND 器件 / 干扰 / 保持

查询入口：`"NAND flash" "threshold voltage" disturb retention "read retry"`

该查询针对控制器固件必须补偿的底层器件行为。可能检索到 die/电路专利而非 SSD 专利，当控制器含义重要时应将 G11C/H10B 与 G06F 结合使用。

## 特征专利种子

| 主题 | 示例专利 | 覆盖内容 |
|---|---|---|
| FTL | US20120317377A1 | FTL 行为、块压缩、动态磨损均衡、静态磨损均衡、逻辑到物理重映射 ^[research-nand-controller-patent-notes.md:44] |
| PLP | US20170185335A1 | SSD 掉电保护、备用电源、超级电容、易失性缓冲 flush 行为 ^[research-nand-controller-patent-notes.md:45] |
| SLC 缓存 | US20220129168A1 | SLC 存储单元作为 MLC 容量权衡的高速缓存 ^[research-nand-controller-patent-notes.md:46] |
| LDPC | US8413029B2 | LDPC 解码能力调整、错误统计、存储设备 LDPC 监控 ^[research-nand-controller-patent-notes.md:47] |
| 放置/FDP | US12405729B2 | 类 FDP 的 reclaim unit 数据放置、主机控制放置概念 ^[research-nand-controller-patent-notes.md:48] |

## 检索标签建议

| 标签 | 适用范围 |
|---|---|
| `patent/cpc/g06f-3-06` | SSD 控制器、主机接口、存储虚拟化、FTL、GC、放置、RAID 类存储专利 ^[research-nand-controller-patent-notes.md:72] |
| `patent/cpc/g11c-16` | NAND 编程/读取/擦除、感知、干扰、保持、单元行为专利 ^[research-nand-controller-patent-notes.md:73] |
| `patent/cpc/h03m-13` | LDPC/BCH/RS 编码、迭代解码、软解码、ECC 硬件实现专利 ^[research-nand-controller-patent-notes.md:74] |
| `patent/topic/plp` | 掉电保护、突发断电恢复、电容支撑 flush、元数据保留专利 ^[research-nand-controller-patent-notes.md:75] |
| `patent/topic/slc-cache` | SLC 缓存、伪 SLC、混合缓存、折叠、动态单级/多级配置专利 ^[research-nand-controller-patent-notes.md:76] |
| `patent/topic/fdp-placement` | FDP、流、主机提示、放置标识符、reclaim unit、热/冷数据分离、WAF 降低专利 ^[research-nand-controller-patent-notes.md:77] |

## 可信度分级

| 级别 | 说明 | 适用场景 |
|---|---|---|
| explicit product brief | 页面或 PDF 明确说明 | 可进入 vendor intake |
| guide / product guide | 细节更丰富但仍属公开参考 | 可用于接口和模块边界 |
| marketing language | 仅有定位或卖点 | 仅用于术语和 backlog |
| inferred | 从产品命名、市场定位或对标项目推断 | 仅供探索，不作事实 |

## 常见误区

- 把 marketing feature list 当成可实现接口。
- 把 guide 里的模块名称直接当成 RTL 模块边界。
- 把 `enterprise` 或 `client` 当成统一功能集合，不区分具体代际。
- 把公开资料的术语误写成已验证实现细节。
- 没记录版本和 sha256，后面无法追溯。
- 将专利检索结果与 NVMe 规范行为混淆 — 专利描述的是声称的发明实现，而非协议规范本身 ^[research-nand-controller-patent-notes.md:48-49]。

## 相关概念

- 闪存转换层 (FTL)
- LDPC Pipeline Policy Matrix
- 掉电保护与恢复
- SLC 缓存与混合缓存策略
- NVMe 灵活数据放置 (FDP)
- 控制器硬件模块边界

## Sources

- [NAND Controller and Patent Research Notes - research-nand-controller-patent-notes.md](../../sources/research-nand-controller-patent-notes.md)

