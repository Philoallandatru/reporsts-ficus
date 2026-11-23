---
type: Concept
title: SLC Cache、Write Cliff 与 Destage 策略
description: 很多 TLC/QLC SSD 会把一部分 NAND 以 SLC 或 pseudo-SLC 模式使用，用来吸收短 burst 写入并降低前台写延迟。SLC
  cache 不是单纯的“高速缓存”；它会改变 FTL 映射、free block pool、GC、wear leveling、PLP 和稳态性能。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# SLC Cache、Write Cliff 与 Destage 策略

很多 TLC/QLC SSD 会把一部分 NAND 以 SLC 或 pseudo-SLC 模式使用，用来吸收短 burst 写入并降低前台写延迟。SLC cache 不是单纯的“高速缓存”；它会改变 FTL 映射、free block pool、GC、wear leveling、PLP 和稳态性能。

## 设计目标

- 在短 burst、小随机写和客户端交互 workload 下提供低写延迟。
- 在 cache full 或 low free block 时保持前向进展，而不是进入不可解释的写入悬崖。
- 控制 SLC-to-TLC/QLC destage 的写放大、读干扰和后台 QoS 影响。
- 确保 SLC cache metadata、host-completed writes 和 flush/FUA 语义可恢复。
- 把 host write、SLC program、destage write、GC relocation write 分开统计。

## Cache 形态

| 形态 | 说明 | 优点 | 风险 |
|---|---|---|---|
| Static SLC cache | 固定 NAND 区域长期以 SLC 模式使用 | 行为稳定、恢复简单 | 容量成本高，长期热写磨损集中 |
| Dynamic SLC cache | 根据空闲空间动态把 TLC/QLC block 临时作为 SLC 使用 | 空盘性能好，容量利用高 | 越接近满盘 cache 越小，性能悬崖明显 |
| Hybrid cache | 固定小 SLC + 动态 SLC | 折中 | 策略和 telemetry 更复杂 |
| Direct-to-TLC/QLC bypass | 大顺序写或 cache full 时绕过 SLC | 避免无意义 destage | 前台写延迟上升，写路径分叉 |

## Admission 策略

| 策略 | 适合写入 | 不适合写入 | 关键指标 |
|---|---|---|---|
| Admit all | 小容量原型、简单 client workload | 大顺序写、长期持续写 | cache fill rate、destage pressure |
| Size-aware | 小写、随机写进入 SLC；大顺序写 bypass | 混合 workload 分类不准时 | bypass ratio、write latency |
| Temperature-aware | 热数据或短生命周期数据进入 SLC | 冷大文件备份 | hot/cold accuracy、future relocation |
| QoS-aware | 读敏感或低 QD 时限制 destage，前台写优先入 SLC | cache 接近满时 | p99/p999、cache occupancy |
| PLP-aware | host-completed data 必须有 cache metadata 和 recovery evidence | PLP 能量不足时继续接收写 | protected bytes、emergency flush time |

Admission 不能只看当前写入大小。它还要看 cache occupancy、TLC/QLC free block、destage backlog、temperature、flush/FUA、namespace/stream/FDP hint 和 host QD。

## Write Cliff 状态机

| 状态 | 触发条件 | 行为 | Host 可见现象 |
|---|---|---|---|
| Burst | cache occupancy 低，destage backlog 低 | 前台写优先进入 SLC | 写延迟低 |
| Destage pressure | cache occupancy 超过 soft threshold | 后台 destage 增加 budget | p99 写延迟上升 |
| Cache full | cache occupancy 接近 hard threshold | bypass 或同步 destage | 明显 write cliff |
| Low TLC/QLC free | 主存储区 free block 不足 | 同时触发 GC 和 destage | WAF 上升，尾延迟变差 |
| Recovery constrained | PLP/flush/FUA 要求强持久化 | 限制 admission，优先提交 metadata | 写延迟变成持久化成本 |

## Destage 路径

1. 选择 SLC cache victim：按 age、temperature、namespace/stream、valid ratio。
2. 读取 SLC page，校验 metadata 和 sequence。
3. 选择 TLC/QLC 目标位置，尽量保持冷热和 stream 分组。
4. program TLC/QLC page 或 fold 到目标 block。
5. 写入 destage journal，记录 `LPN -> TLC/QLC PPA`。
6. 原子切换 L2P，标记 SLC page stale。
7. SLC block invalid 足够多时擦除，归还 SLC cache pool。

Destage 和 GC 的区别：destage 是从高性能 cache 区搬到主存储区；GC 是为了回收 victim block。两者都写 NAND，但统计和调度应分开。

## Metadata 与恢复

SLC cache 至少需要记录：

- cache page 的 LPN、sequence、namespace、stream/FDP hint。
- cache page 是否已经 host-completed。
- 是否已经 destaged 到 TLC/QLC。
- destage journal 的 source SLC PPA、target TLC/QLC PPA、commit marker。
- cache block state：open、closed、destaging、retired、bad。

危险掉电窗口：

- host write 已写入 SLC，但 cache metadata 未提交。
- flush/FUA 已完成，但 destage journal 未提交。
- destage target 已写入 TLC/QLC，但 L2P 还指向 SLC。
- L2P 已切换到 TLC/QLC，但 SLC page 尚未 retire。
- cache block erase boundary。

这些窗口应复用 [掉电恢复状态表](../../tests/faults/power-loss-state-table.yml) 的 journal、checkpoint 和 GC relocation 规则，并在实现中增加 SLC-specific evidence。

## QoS 与调度

SLC cache 会把写延迟从前台移动到后台。需要单独调度：

- foreground host writes。
- SLC cache program。
- SLC-to-TLC/QLC destage。
- TLC/QLC GC relocation。
- wear leveling / refresh / scrub。
- metadata checkpoint。

优先级建议：

1. foreground read 和 read retry。
2. flush/FUA required metadata commit。
3. foreground write admission。
4. emergency destage / emergency GC。
5. normal destage。
6. proactive GC / wear leveling / refresh。

## 指标

| 指标 | 说明 | 相关测试 |
|---|---|---|
| SLC occupancy | cache 已用比例 | T5-003 |
| Destage backlog | 待搬迁到 TLC/QLC 的数据量 | T5-003 |
| Bypass ratio | 直接写 TLC/QLC 的 host write 比例 | T5-003 |
| Write cliff point | 写延迟显著上升的 occupancy/free block 点 | T5-003 |
| Destage writes | SLC-to-TLC/QLC 写量 | T5-001, T5-003 |
| Cache metadata writes | cache map、journal、checkpoint 写量 | T5-003 |
| Read p999 during destage | destage 活动期间读尾延迟 | T5-002 |
| Recovery accepted cache pages | 掉电恢复接受的 SLC pages | T4-* |

## 验证点

- 空盘 burst 写入和 steady-state 写入的延迟分布差异。
- SLC cache full 后 write cliff 的位置和持续时间。
- 大顺序写是否 bypass，避免占满 SLC 后再 destage。
- destage 与 foreground read 混合时 p999 是否受控。
- low TLC/QLC free block 时 destage 和 GC 是否互相饿死。
- flush/FUA 后掉电，SLC cache 中已完成写是否可恢复。
- destage 中掉电，不得丢失最新版本，也不得复活 SLC 旧版本。

## 关键来源

- [性能、QoS 与写放大](performance-qos-write-amplification.md)
- [GC Victim Selection 与 Wear Leveling 策略](gc-wear-leveling-policy.md)
- [掉电恢复状态表](../../tests/faults/power-loss-state-table.yml)
- [SSD 设计论文与 BibTeX 种子](../../BIBLIOGRAPHY.md)
- [SLC cache patent search](../../PATENT_INDEX.md)
