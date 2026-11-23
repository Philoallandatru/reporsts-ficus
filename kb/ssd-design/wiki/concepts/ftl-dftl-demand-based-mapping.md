---
type: Concept
title: DFTL / Demand-based Mapping
description: DFTL 将 page-level mapping 保留为逻辑模型，但不要求整张 L2P 表常驻 DRAM。它把 mapping table
  拆成 translation pages 存在 flash 上，在 DRAM 中只缓存热的 mapping entries 或 translation pages。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# DFTL / Demand-based Mapping

DFTL 将 page-level mapping 保留为逻辑模型，但不要求整张 L2P 表常驻 DRAM。它把 mapping table 拆成 translation pages 存在 flash 上，在 DRAM 中只缓存热的 mapping entries 或 translation pages。

## 设计目标

- 保留 page mapping 对随机写友好的特性。
- 降低大容量 SSD 的 DRAM/SRAM 映射开销。
- 让热 working set 常驻，冷 mapping 按需加载。
- 在 mapping cache miss、translation page 写回、GC 和掉电恢复之间保持一致性。

## 核心数据结构

| 数据结构 | 内容 | 设计关注点 |
|---|---|---|
| Global translation directory | `translation page id -> physical translation page` | 常驻或高度可靠持久化 |
| Cached mapping table | 热 LPN 的 `LPN -> PPA` entry | 替换策略、dirty tracking、锁粒度 |
| Translation page | 一组连续 LPN 的 mapping entries | flash 上的映射页，需 journal/checkpoint |
| Dirty map | cache entry 或 translation page 是否已修改 | eviction 和 flush |
| Mapping request queue | translation page read/write 请求 | 避免阻塞高优先级 host read |

DFTL 的关键不是“少放一点映射表”，而是把 mapping cache miss 变成可调度、可恢复、可观测的内部 I/O。

## 读路径

1. 将 LBA 切分成 LPN。
2. 查 cached mapping table。
3. 命中时直接读 data PPA。
4. miss 时根据 translation directory 找到 translation page。
5. 读取 translation page，填充 cache。
6. 再读 data PPA。

read miss 会多一次 flash read，并可能与 host read、GC read、read retry 争抢 channel。实现上应统计 mapping miss latency，并把 mapping read 与用户 read 区分。

## 写路径

1. 将 LBA 切分成 LPN。
2. 若 mapping entry 不在 cache，加载 translation page 或分配新 entry。
3. 写用户数据到新 data PPA。
4. 更新 cached mapping entry，并标记 dirty。
5. 将旧 PPA 标记 invalid。
6. 在 checkpoint、flush、cache eviction 或后台刷写时持久化 translation page / journal。

写路径上的难点是 dirty mapping 的持久化顺序。设备不能让掉电恢复后 L2P 指向未成功写入的数据，也不能让新数据已经可见但 mapping 丢失。

## Cache 替换

常见策略：

- LRU：简单，但可能被顺序扫描污染。
- CFLRU / dirty-aware eviction：优先淘汰 clean entry，降低 translation page 写回。
- Hot/cold separation：保护热点映射。
- Pinning：flush/FUA、GC victim、metadata recovery 期间固定关键 entry。

需要避免的情况：

- cache miss storm：高 QD 随机读导致大量 translation page read。
- dirty eviction storm：随机写使 translation page 频繁写回。
- GC 搬迁 translation page 与 host write 更新同一 mapping entry。

## Translation Page GC

DFTL 不只回收用户 data block，也要管理 translation pages。translation page 自身也在 flash 上追加写入，旧 translation page 失效后需要 GC。

设计关注点：

- translation page 的 PPA 更新必须反映到 global directory。
- directory update 要有 journal 或双副本保护。
- translation page GC 不能和 data GC 互相饿死。
- mapping metadata 的写放大要单独统计。

## 掉电恢复

恢复流程通常包括：

1. 加载 superblock / root metadata。
2. 加载 global translation directory 或其 checkpoint。
3. 重放 mapping journal。
4. 校验 dirty translation page 的 sequence。
5. 必要时扫描 data page 的 P2L metadata 修补缺口。

危险窗口：

- 用户 data page 写入成功，dirty mapping entry 未刷写。
- translation page 写入成功，directory 未更新。
- directory 更新成功，旧 translation page 尚未 retire。
- cache eviction 和 host overwrite 同时作用于同一 LPN。

## 适用场景

| 场景 | 适配度 | 说明 |
|---|---|---|
| 大容量 DRAM 受限 SSD | 高 | DFTL 的核心目标 |
| DRAM-less/HMB SSD | 高 | 可与 [HMB mapping cache](dram-less-hmb-ssd.md) 组合 |
| 热点明显 workload | 高 | cache 命中率可控 |
| 完全随机大 working set | 中 | miss 放大和 translation I/O 压力明显 |
| 最小教学控制器第一版 | 低 | 状态机比 page mapping 复杂，建议第二阶段实现 |

## 验证点

- mapping cache 命中和 miss 的读延迟分离统计。
- 高随机读下 translation page read 不饿死用户 read。
- dirty mapping eviction 后掉电，恢复能读到最新数据。
- translation page 写入后、directory 更新前掉电。
- directory 更新后、旧 translation page retire 前掉电。
- data GC 与 translation page GC 同时运行时保持前向进展。

## 关键来源

- [DFTL paper](https://dl.acm.org/doi/10.1145/1508244.1508271)
- [SSD 设计论文与 BibTeX 种子](../../BIBLIOGRAPHY.md)
- [FTL Page Mapping](ftl-page-mapping.md)
- [FTL 元数据格式与恢复约定](ftl-metadata-format-and-recovery-conventions.md)
- [SPDK FTL](https://spdk.io/doc/ftl.html)
