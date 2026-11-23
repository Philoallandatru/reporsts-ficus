---
type: Concept
title: FTL 与固件职责
description: FTL 是 SSD 固件中最核心的抽象层。主机以连续 LBA 访问设备，但 NAND 只能以 page program、block erase
  的方式工作，并且 page 不能原地覆盖。FTL 负责把 overwrite-heavy 的块接口转成 append-style 的 flash 写入。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# FTL 与固件职责

FTL 是 SSD 固件中最核心的抽象层。主机以连续 LBA 访问设备，但 NAND 只能以 page program、block erase 的方式工作，并且 page 不能原地覆盖。FTL 负责把 overwrite-heavy 的块接口转成 append-style 的 flash 写入。

## FTL 的核心职责

- 地址映射：维护 LBA 到 physical page/block 的映射。
- 写分配：选择 channel、die、plane、block、page，决定并行度与冷热数据布局。
- 垃圾回收：挑选 victim block，迁移仍有效 page，擦除 block 并归还 free block pool。
- 磨损均衡：让 P/E cycle 在 block 间尽量均匀，必要时迁移冷数据。
- 元数据持久化：维护 mapping table、journal、checkpoint、block state，并支持掉电恢复。
- 错误恢复：处理 program fail、erase fail、read retry、uncorrectable error、坏块替换。
- 后台任务调度：把 GC、scrub、refresh、telemetry 与 host I/O 做 QoS 协调。

## 映射粒度

| 策略 | 优点 | 代价 |
|---|---|---|
| Block mapping | 映射表小 | 小随机写放大严重 |
| Page mapping | 随机写友好 | DRAM/SRAM 元数据开销大 |
| Hybrid/log-block | 折中 | 合并逻辑复杂 |
| Demand-based mapping | 降低 DRAM 常驻需求 | 映射缓存 miss 会增加延迟 |

真实产品通常不会只采用教材中的单一映射。它们会按 workload、namespace、stream、temperature、SLC cache、OP 空间和 QoS 目标组合策略。

映射算法拆分页：

- [FTL Page Mapping](ftl-page-mapping.md)
- [FTL Hybrid / Log-block Mapping](ftl-hybrid-log-block-mapping.md)
- [DFTL / Demand-based Mapping](ftl-dftl-demand-based-mapping.md)
- [FDP、Streams、Placement Hint 与内部 FTL](fdp-streams-placement-hints.md)

## 固件边界

固件通常不直接 bit-bang NAND timing，而是向 flash controller 下发 NAND request。硬件负责精确时序、ECC pipeline、DMA 和 channel arbitration；固件负责策略、状态机、错误分支和可恢复性。

## 验证点

- 掉电发生在 host data DMA 之后、NAND program 之前。
- 掉电发生在 NAND program 完成之后、mapping journal 刷新之前。
- GC 迁移 page 期间遇到读错误。
- Wear leveling 迁移冷数据时 host 写入同一 LBA。
- Firmware update 与 reset、shutdown、sanitize、format 交叠。
- 映射表缓存 miss 与高队列深度随机读交叠。

## 元数据与恢复

FTL 的持久化边界细节见 [FTL 元数据格式与恢复约定](ftl-metadata-format-and-recovery-conventions.md)，掉电窗口和恢复语义见 [掉电保护与恢复](power-loss-recovery.md)。如果没有把 superblock、checkpoint、journal、block table 和 P2L page metadata 的责任边界写清楚，FTL 再多的映射策略也很难真正恢复。

## 关键来源

- Cosmos+ OpenSSD documentation: https://cosmos-plus-openssd-doc.readthedocs.io/
- FEMU: https://github.com/MoatLab/FEMU
- SimpleSSD: https://github.com/SimpleSSD/SimpleSSD
- MQSim: https://github.com/CMU-SAFARI/MQSim
- SPDK source: https://github.com/spdk/spdk
