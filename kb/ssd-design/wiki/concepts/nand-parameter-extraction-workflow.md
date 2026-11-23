---
type: Concept
title: NAND 参数抽取与建模流程
description: NAND 参数不是“有个 datasheet 就行”。要把它变成 SSD 控制器、FTL、flash scheduler 和 ECC 可用的输入，需要先抽字段，再分级，再落入模型。这个流程页就是给这件事定一个可重复的工作流。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# NAND 参数抽取与建模流程

NAND 参数不是“有个 datasheet 就行”。要把它变成 SSD 控制器、FTL、flash scheduler 和 ECC 可用的输入，需要先抽字段，再分级，再落入模型。这个流程页就是给这件事定一个可重复的工作流。

## 输入来源

常见输入分三类：

| 来源 | 例子 | 可得到什么 |
|---|---|---|
| 公开技术资料 | technical note、white paper、product family brief | 术语、代际、可靠性语言、架构边界 |
| 具体 part datasheet | device ID、parameter page、timing、geometry、bad block 规则 | 可直接用于模型的参数 |
| 授权或受限资料 | vendor app note、渠道 datasheet、内部测试记录 | 更细的 timing table、retry table、command sequence |

公开材料主要帮助我们确定“该去找什么”，part datasheet 才真正决定“模型里填什么”。

## 抽取顺序

1. 先固定文档身份：vendor、part number 或 family、document version、访问日期、sha256、来源 URL。
2. 再抽物理几何：page size、OOB/spare、pages per block、planes per die、dies per package。
3. 再抽接口时序：ONFI/Toggle version、bus width、timing mode、tR、tPROG、tBERS。
4. 再抽可靠性：P/E、retention、read disturb、temperature、bad block policy。
5. 再抽 ECC/read-retry：是否支持 read retry、纠错要求、状态位、feature register。
6. 最后才把这些值落到 emulator、RTL timing budget 或 flash scheduler 参数里。

## 参数可信度分级

| 级别 | 判断标准 | 能否进入可执行模型 |
|---|---|---|
| direct_datasheet | 具体 part number datasheet 明确给出 | 可以 |
| official_family | 只有产品族或代际级描述 | 可用于架构估算，不可直接当 timing 真值 |
| standards_default | 规范定义的 parameter page 或接口格式 | 可作为 parser / register 框架 |
| inferred | 从论文、白皮书或实现例子推断 | 只能做教学或敏感性分析 |

## 建模路径

抽出来的参数通常进入三类模型：

| 模型 | 使用哪些字段 | 典型用途 |
|---|---|---|
| Geometry model | page/block/plane/die/channel | FTL、GC、metadata 布局 |
| Timing model | tR/tPROG/tBERS、bus width、interface rate | flash scheduler、QoS、PLP 预算 |
| Reliability model | endurance、retention、read disturb、ECC/retry | LDPC、scrub、wear leveling |

## 抽取模板

每个条目至少记录：

- vendor。
- part number 或 family。
- document version。
- source URL 或本地文件名。
- sha256。
- access date。
- confidence level。
- 是否允许公开。

如果是已下载 PDF，还要补页数和 artifact 关联。

## 典型陷阱

- 把 family brief 当成具体 part datasheet。
- 把 interface 规范当成 NAND timing 真值。
- 把 marketing white paper 当成坏块或 retry 规则来源。
- 把不同 cell type、不同代际、不同温度区间的值混成一张表。
- 把公开模型里的 inferred 值误写成 direct_datasheet。

## 输出去向

抽取结果最终应分别进入：

- [NAND 介质参数手册](nand-media-parameter-guide.md)。
- [NAND Vendor 公开资料 Intake](../../sources/vendor-intake/nand-vendor-public-materials.md)。
- [NAND Parameter Extraction Matrix](../../sources/vendor-intake/nand-parameter-extraction-matrix.yml)。
- [Flash Scheduler、Channel/Die/Plane Arbitration 与 Read Priority](flash-scheduler-arbitration.md)。
- [ECC、LDPC 与可靠性管理](ecc-ldpc-reliability.md)。

## 和控制器设计的关系

这个流程不是文书工作，而是为了把 NAND 变成控制器能用的输入：

- flash scheduler 需要 timing 和并行度。
- ECC/LDPC 需要纠错和 retry 能力。
- FTL 需要 geometry 和坏块语义。
- 掉电恢复需要知道写入完成边界。
- 量产和 field debug 需要可靠性和状态字段。

## 关键来源

- NAND 介质参数手册: [nand-media-parameter-guide.md](nand-media-parameter-guide.md)
- NAND Vendor 公开资料 Intake: [nand-vendor-public-materials.md](../../sources/vendor-intake/nand-vendor-public-materials.md)
- NAND Parameter Extraction Matrix: [nand-parameter-extraction-matrix.yml](../../sources/vendor-intake/nand-parameter-extraction-matrix.yml)
- ONFI Specifications: https://onfi.org/specs.html
- JEDEC standards search: https://www.jedec.org/standards-documents
