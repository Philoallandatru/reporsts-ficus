---
type: Concept
title: NAND 数据采集与建模
description: NAND 相关资料最容易出现的问题，不是没有信息，而是信息分散在技术说明、产品 brief、datasheet、规范和白皮书里。要把这些材料变成可用的
  SSD 模型，最好用一套固定的采集与建模流程。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# NAND 数据采集与建模

NAND 相关资料最容易出现的问题，不是没有信息，而是信息分散在技术说明、产品 brief、datasheet、规范和白皮书里。要把这些材料变成可用的 SSD 模型，最好用一套固定的采集与建模流程。

## 采集目标

这页的目标不是复述 NAND 教科书，而是让你知道：

- 哪些字段必须从具体 part number datasheet 来。
- 哪些字段可以从公开 family brief 或技术说明里先建立初值。
- 哪些字段只是接口规范的默认值，不能当作某颗 NAND 的真值。
- 采集结果如何落到 FTL、flash scheduler、ECC 和验证资产里。

## 采集顺序

### 1. 固定资料身份

先记录这些元数据：

- vendor。
- part number 或 family name。
- document version。
- source URL。
- access date。
- 本地文件名。
- sha256。
- 访问条件。

没有这一步，后续字段很容易混掉代际和来源。

### 2. 先看公开 family 资料

公开 technical note、white paper、product brief 先用来回答：

- 这个 vendor 的 NAND 代际是什么。
- cell type 是 SLC、MLC、TLC 还是 QLC。
- 它强调的是可靠性、接口、还是产品定位。
- 有没有公开提到 read retry、ECC、endurance 或 temperature.

这一步的任务是建词汇和边界，不是填最终模型参数。

### 3. 再找具体 datasheet

具体 part number datasheet 才能稳定抽出：

- page size。
- OOB/spare size。
- pages per block。
- planes per die。
- dies per package。
- ONFI / Toggle version。
- bus width。
- timing mode。
- tR、tPROG、tBERS。
- bad block marker。
- ECC requirement。
- read retry support。

### 4. 再落到模型

抽到的字段一般进入三种模型：

| 模型 | 使用字段 | 影响 |
|---|---|---|
| Geometry model | page/block/plane/die/package/channel | FTL mapping、GC、metadata layout |
| Timing model | tR、tPROG、tBERS、bus width、interface rate | flash scheduler、QoS、PLP budget |
| Reliability model | endurance、retention、read disturb、ECC、retry | LDPC、scrub、wear leveling |

## 可信度分层

| 级别 | 说明 | 用途 |
|---|---|---|
| direct_datasheet | 具体 part number datasheet 明确给出 | 可以进入可执行模型 |
| official_family | 只给产品族或代际级描述 | 用于架构估算和采集队列 |
| standards_default | 来自 ONFI/JESD 这类规范 | 用于 parser 和接口框架 |
| inferred | 从论文、白皮书或产品语言推断 | 只能做教学或敏感性分析 |

## 典型字段到子系统

| 字段组 | 典型字段 | 影响子系统 |
|---|---|---|
| Geometry | page size、OOB、pages/block、planes/die | FTL、GC、metadata |
| Interface/timing | ONFI/Toggle、bus width、timing mode、tR、tPROG、tBERS | flash scheduler、QoS |
| Reliability | P/E cycle、retention、read disturb、temperature | wear leveling、refresh |
| ECC/read retry | ECC bits/KB、retry support、status bits | LDPC pipeline、fault handling |
| Vendor command/status | get/set feature、unique ID、OTP、fail bits | factory test、field diagnosis |

## 采集模板

每条记录至少应该有：

- vendor。
- part number 或 family。
- document version。
- source URL / 本地文件。
- sha256。
- access date。
- confidence。
- 是否公开。

如果已经下载了 PDF，还应补页数和关联 artifact id。

## 常见错误

- 把 family brief 当成具体 datasheet。
- 把标准接口默认值当成某颗 NAND 的 timing 真值。
- 把营销白皮书里的 reliability 语言当作可执行参数。
- 把不同代际、温度和 cell type 的值混成一张表。
- 没记录文档版本和 sha256，后面无法追溯。

## 输出去向

采集结果最终要进入：

- [NAND 介质参数手册](nand-media-parameter-guide.md)
- [NAND Vendor 公开资料 Intake](../../sources/vendor-intake/nand-vendor-public-materials.md)
- [NAND Parameter Extraction Matrix](../../sources/vendor-intake/nand-parameter-extraction-matrix.yml)
- [Flash Scheduler、Channel/Die/Plane Arbitration 与 Read Priority](flash-scheduler-arbitration.md)
- [ECC、LDPC 与可靠性管理](ecc-ldpc-reliability.md)

## 关键来源

- [NAND 介质参数手册](nand-media-parameter-guide.md)
- [NAND Vendor 公开资料 Intake](../../sources/vendor-intake/nand-vendor-public-materials.md)
- [NAND Parameter Extraction Matrix](../../sources/vendor-intake/nand-parameter-extraction-matrix.yml)
- ONFI Specifications: https://onfi.org/specs.html
- JEDEC standards search: https://www.jedec.org/standards-documents
