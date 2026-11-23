---
type: Concept
title: NAND 介质参数手册
description: SSD 设计需要把 NAND 当成有约束的并行介质，而不是一个慢一点的块设备。做 FTL、调度、ECC、PLP 和性能模型前，应先固定一组介质参数。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# NAND 介质参数手册

SSD 设计需要把 NAND 当成有约束的并行介质，而不是一个慢一点的块设备。做 FTL、调度、ECC、PLP 和性能模型前，应先固定一组介质参数。

配套采集矩阵见 [NAND Parameter Extraction Matrix](../../sources/vendor-intake/nand-parameter-extraction-matrix.yml)。它用于区分哪些字段可以来自公开资料，哪些必须等待具体 part number datasheet 或厂商授权资料。

更完整的抽取与建模流程见 [NAND 数据采集与建模](nand-data-acquisition-and-modeling.md)。

## 物理层级参数

| 参数 | 说明 | 影响 |
|---|---|---|
| Channel count | 独立 NAND 数据通道数 | 后端带宽上限、并行读写 |
| Package per channel | 每通道封装数量 | CE/way 调度、板级布线 |
| Die/LUN per package | 封装内可并行单元 | 并行度、busy hiding |
| Plane per die | die 内 plane 数 | Multi-plane command、地址限制 |
| Block per plane | 擦除单元数量 | 容量、wear leveling 粒度 |
| Page size | program/read 单位 | LBA 聚合、ECC codeword、metadata |
| OOB/spare size | page 附带元数据区域 | ECC parity、LPN、CRC、状态标记 |

## 时序参数

| 参数 | 典型用途 |
|---|---|
| tR | Read latency，用于读延迟模型 |
| tPROG | Program latency，用于写路径和 PLP 预算 |
| tBERS | Block erase latency，用于 GC 预算 |
| Interface transfer rate | Channel 数据传输带宽 |
| Command/address overhead | 小 I/O 下的固定开销 |
| Read retry latency | ECC failure 后的尾延迟 |

不要只用平均值。延迟分布、P/E cycle、温度和 read retry 次数会影响 p99/p999。

## 操作约束

- Page program 通常要求块内按顺序或半顺序写。
- Block erase 前必须保证有效数据已经搬迁。
- Multi-plane 操作要求 plane 地址条件匹配。
- Copyback、cache read/program、multi-LUN interleaving 依赖具体 NAND。
- TLC/QLC 可能有 lower/upper page 或 wordline 相关顺序约束。
- SLC cache 和 TLC/QLC 主存储区的 program 模式不同。

## 介质健康参数

| 参数 | 固件用途 |
|---|---|
| P/E cycle | Wear leveling、寿命估算 |
| RBER | ECC margin、refresh 策略 |
| Retention age | Cold data refresh |
| Read count | Read disturb scrub |
| Temperature | Retention、throttling、refresh priority |
| Program/erase fail count | Block retire |
| Correction count | Early warning、data migration |

## Datasheet 阅读清单

拿到目标 NAND datasheet 后至少抽取：

- Device ID 和 parameter page。
- Geometry：page/block/plane/die/package/channel 相关字段。
- Timing mode 与最大 interface rate。
- Command set：read、program、erase、reset、get/set feature。
- Status register 和 fail bit。
- Bad block marker 位置。
- Read retry 或 vendor-specific feature。
- Power-on reset、ready/busy 行为。
- OOB/spare layout 建议。
- Endurance、retention、temperature 条件。

## 参数可信度分层

| 层级 | 含义 | 可用于 |
|---|---|---|
| Direct datasheet | 具体 part number datasheet、官方 parameter page 或明确版本 PDF 直接给出 | emulator 默认参数、RTL timing budget、验证断言 |
| Official family | 厂商公开资料描述产品族、NAND 代际或 cell technology，但不绑定具体 part number | 架构估算、Backlog、资料采集方向 |
| Standards default | ONFI/JESD 等接口规范定义字段、命令、parameter page 格式 | interface parser、控制器寄存器/时序框架 |
| Inferred | 从论文、白皮书、开源 simulator 或产品定位推断 | 教学模型、早期敏感性分析 |

知识库中的控制器参数不应把这四类混在一起。例如，ONFI 可定义如何读取 parameter page，但不能替代某颗 NAND 的 tR/tPROG；厂商白皮书可说明 LDPC/read retry 的方向，但不能替代具体 read-retry voltage table。

## 抽取字段到子系统映射

| 字段组 | 典型字段 | 影响子系统 | 关联资产 |
|---|---|---|---|
| Geometry | page size、OOB、pages/block、planes/die、dies/package | FTL mapping、GC、metadata layout | [FTL Page Mapping](ftl-page-mapping.md), [FTL 元数据格式与恢复约定](ftl-metadata-format-and-recovery-conventions.md) |
| Interface/timing | ONFI/Toggle version、bus width、timing mode、tR、tPROG、tBERS | flash scheduler、QoS、PLP budget | [Flash Scheduler](flash-scheduler-arbitration.md), [Flash Scheduler Policy Matrix](../../tests/requirements/flash-scheduler-policy-matrix.yml) |
| Reliability | endurance、retention、read disturb、temperature、bad block policy | wear leveling、scrub、block retire | [GC Victim Selection 与 Wear Leveling 策略](gc-wear-leveling-policy.md) |
| ECC/read retry | ECC bits/KB、LDPC expectation、retry support、status bits | LDPC pipeline、uncorrectable escalation | [ECC、LDPC 与可靠性管理](ecc-ldpc-reliability.md), [LDPC Pipeline Policy Matrix](../../tests/requirements/ldpc-pipeline-policy-matrix.yml) |
| Vendor command/status | get/set feature、unique ID、OTP、fail bits、retry hooks | NAND driver、factory test、field diagnosis | [故障注入目录](fault-injection-catalog.md) |

## Read-retry 参数处理规则

Read-retry 往往是最容易被误用的字段。建议规则：

1. 公开知识库只记录是否支持 read retry、需要哪些抽象 hook、哪些状态/计数器要暴露。
2. 具体 voltage table、vendor command sequence、feature address 和 retry ordering 放到受限资料或私有配置，不直接复制到公开页面。
3. emulator 可以先用 `retry_step_count`、`retry_latency_us`、`soft_decode_probability` 这类抽象字段建模。
4. 一旦拿到具体 datasheet，应记录 part number、document revision、sha256、访问条件，并把参数填入私有模型或受限 intake。

## 建模建议

早期原型可用固定延迟模型，但要保留扩展点：

- 每个 die 独立 busy。
- Channel bus 和 die array 分开建模。
- ECC latency 作为独立 pipeline。
- Read retry 作为概率事件或 fault injection。
- Block wear 会改变 error probability。

## 关键来源

- ONFI Specifications: https://onfi.org/specs.html
- JEDEC standards search: https://www.jedec.org/standards-documents
- Micron technical notes: https://www.micron.com/support/technical-notes
- Kioxia technical resources: https://www.kioxia.com/en-jp/business/memory/technical-resources.html
- SimpleSSD: https://github.com/SimpleSSD/SimpleSSD
- MQSim: https://github.com/CMU-SAFARI/MQSim
