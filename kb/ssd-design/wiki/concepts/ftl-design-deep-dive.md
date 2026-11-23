---
type: Concept
title: FTL 设计深水区
description: FTL 的难点不是“把 LBA 映射到物理页”这一句话，而是在有限 DRAM、有限空闲块、有限擦写寿命和严格掉电恢复要求下，让随机写、顺序写、读延迟、GC、热管理和固件重启都同时可控。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# FTL 设计深水区

FTL 的难点不是“把 LBA 映射到物理页”这一句话，而是在有限 DRAM、有限空闲块、有限擦写寿命和严格掉电恢复要求下，让随机写、顺序写、读延迟、GC、热管理和固件重启都同时可控。

## 关键数据结构

| 数据结构 | 作用 | 设计关注点 |
|---|---|---|
| L2P mapping | 从 LBA 或 LPN 找到 physical page | 粒度、DRAM 常驻比例、cache miss 延迟、checkpoint 策略 |
| P2L reverse map | 从 physical page 找回逻辑地址 | GC 搬迁、掉电恢复、scan rebuild |
| Block table | 记录 block 的 erase count、valid page count、free/closed/victim/bad 状态 | victim selection、wear leveling、坏块隔离 |
| Segment/line table | 把多个 block 或 die 上的条带作为写入/回收单位 | 并行度、RAID-like parity、恢复粒度 |
| Metadata journal | 顺序记录映射变化和 block 状态变化 | 原子性、重放顺序、日志截断、写放大 |
| Free block pool | 按 channel/die/plane/温度分类的可写 block | 保证 GC 前向进展，避免某个 die 饥饿 |

## 映射策略

Page mapping 随机写性能最好，但映射表大。Block mapping 省 DRAM，但覆盖写会导致严重迁移。Hybrid/log-block 把随机写先写到 log block，再与 data block merge，能省元数据但状态机复杂。Demand-based FTL 用映射缓存降低 DRAM 常驻需求，代价是 miss 时需要读映射页。

拆分页：

- [FTL Page Mapping](ftl-page-mapping.md)
- [FTL Hybrid / Log-block Mapping](ftl-hybrid-log-block-mapping.md)
- [DFTL / Demand-based Mapping](ftl-dftl-demand-based-mapping.md)

工程实现通常会混合多种策略：

- 小容量或 DRAM 足够时用细粒度 mapping。
- 大容量低成本 SSD 用 demand-based mapping 或 compressed mapping。
- SLC cache 区和 TLC/QLC 主存储区使用不同映射和搬迁策略。
- Sequential stream 可以用更粗粒度 extent/segment 记录。
- Namespace、stream、FDP/placement hint 可能影响写入分组。

## 写路径状态机

1. 接收 NVMe write，解析 PRP/SGL，分配 command context。
2. DMA host data 到内部 buffer，计算 CRC/metadata，必要时加密。
3. 为每个 LPN 选择写入位置，预留 physical page。
4. 下发 NAND program，等待完成或进入异步队列。
5. 写入 metadata journal，建立“新数据可恢复”的证据。
6. 更新 volatile L2P cache，把旧 physical page 标记 invalid。
7. 满足持久性策略后返回 CQE。

真正的完成点取决于设备承诺：普通 write、FUA、flush、volatile write cache、PLP 能力都会改变“什么时候可以告诉 host 成功”。

## GC 与前向进展

GC 必须满足两个条件：能找到可回收 victim，也有足够空闲页搬迁 victim 中的有效数据。危险情形是 free block pool 已经太低，GC 需要搬迁的数据又太多，导致写请求和 GC 互相抢资源。

常见控制手段：

- 为每个 channel/die 保留 emergency free blocks。
- 根据 valid page count、erase count、冷热属性和 age 选择 victim。
- 在 host 空闲或低 QD 时做 proactive GC。
- 写放大升高时对 host write 做节流。
- 把用户写和 GC 搬迁写分开统计，避免误判 workload。

详细策略见 [GC Victim Selection 与 Wear Leveling 策略](gc-wear-leveling-policy.md)，机器可读策略矩阵见 [GC Policy Matrix](../../tests/requirements/gc-policy-matrix.yml)。

## Wear leveling

Dynamic wear leveling 只影响正在写入和回收的 block。Static wear leveling 会搬迁长期不变的冷数据，释放低 P/E block 给热数据使用。后者会主动增加写放大，但能避免少数 block 快速老化。

要记录的指标：

- 平均 P/E cycle。
- 最大和最小 P/E cycle。
- block erase count 分布。
- cold data age。
- 每类 NAND region 的剩余寿命。

## 设计风险

- 映射页和用户数据的持久化顺序不清，会导致掉电后 L2P 指向未成功写入的数据。
- GC 搬迁和 host overwrite 同一 LBA 时没有版本号，会把旧数据“复活”。
- Free block watermark 太低，极端随机写下无法保证前向进展。
- Mapping cache miss 与高队列深度读混在一起，会制造长尾延迟。
- Flush/FUA 语义没有与 volatile write cache 和 PLP 能力对齐。

## 关键来源

- DFTL: https://dl.acm.org/doi/10.1145/1508244.1508271
- FAST: https://link.springer.com/chapter/10.1007/11807964_88
- SPDK FTL: https://spdk.io/doc/ftl.html
- Cosmos+ OpenSSD documentation: https://cosmos-plus-openssd-doc.readthedocs.io/
- SimpleSSD: https://github.com/SimpleSSD/SimpleSSD
