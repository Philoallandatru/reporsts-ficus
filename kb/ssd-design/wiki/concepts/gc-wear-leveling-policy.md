---
type: Concept
title: GC Victim Selection 与 Wear Leveling 策略
description: GC 的核心问题不是“找一个 invalid page 多的 block 擦掉”这么简单。真实控制器要同时管理 free block 前向进展、写放大、读尾延迟、erase
  count 分布、冷热数据隔离、后台任务预算和掉电恢复边界。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# GC Victim Selection 与 Wear Leveling 策略

GC 的核心问题不是“找一个 invalid page 多的 block 擦掉”这么简单。真实控制器要同时管理 free block 前向进展、写放大、读尾延迟、erase count 分布、冷热数据隔离、后台任务预算和掉电恢复边界。

## 设计目标

- 在低 free block watermark 时仍能保证 host write 前向进展。
- 尽量选择 valid page 少、搬迁成本低、不会破坏 QoS 的 victim。
- 避免少数 block 过度磨损，同时避免为了 wear leveling 过度搬迁冷数据。
- 把 GC relocation write、wear leveling write、metadata write 与 host write 分开统计。
- 让 GC、wear leveling、refresh、scrub 的后台预算可配置、可观测、可测试。

## Victim Selection 对比

| 策略 | 选择依据 | 优点 | 风险 | 适用场景 | 绑定指标 |
|---|---|---|---|---|---|
| Greedy | valid page count 最少 | 实现简单，短期 WAF 低 | 忽略 block age、冷热和 erase count，可能磨损不均 | 教学 FTL、早期原型 | valid page count、WAF |
| Cost-benefit | invalid ratio、age、erase cost 综合评分 | 比 greedy 更能兼顾搬迁收益和数据年龄 | 参数调得不好会震荡 | 稳态随机写、混合 workload | WAF、GC duty cycle、victim age |
| Hot/cold aware | 按数据温度分区选择 victim | 降低冷热混合导致的未来搬迁 | 温度分类错误会造成碎片或热点 | 有 stream/namespace/hotset 线索的 SSD | hot/cold misclassification、future relocation |
| Wear-aware | erase count 偏差进入评分 | 控制寿命分布 | 可能牺牲短期性能和 WAF | 寿命压力高、企业盘 | min/max/avg P/E、erase skew |
| QoS-aware | GC 只在预算内运行，读优先 | 控制 p99/p999 | free block 太低时需要 host throttling | 读敏感 workload | read p999、GC budget debt |
| Emergency GC | free block 低于硬阈值时强制回收 | 保证前向进展 | 延迟尖峰明显 | 极端随机写、低 OP | emergency events、write throttle time |

推荐实现不是单一策略，而是分层决策：

1. 先按 channel/die/plane 的 free block watermark 找到必须回收的区域。
2. 排除 bad、open、erase-in-progress、PLP 不安全或 metadata 未提交的 block。
3. 在候选集中按 valid count、age、temperature、erase count、QoS budget 评分。
4. 如果进入 emergency watermark，允许更激进的 victim 选择和 host write throttling。

## Watermark 状态机

| 状态 | 触发条件 | 行为 | Host 影响 |
|---|---|---|---|
| Normal | free blocks 高于 soft watermark | 后台 proactive GC，低优先级运行 | 无明显影响 |
| Pressure | free blocks 低于 soft watermark | 增加 GC budget，限制低优先级后台任务 | 写延迟可能上升 |
| Critical | free blocks 低于 hard watermark | foreground-assisted GC，必要时写节流 | 写 cliff，可观测 |
| Emergency | free blocks 接近保留块 | 停止非必要写，优先搬迁最低成本 victim | host write 可能被强制限速 |

每个 channel/die 都需要自己的 watermark。全局 free block 足够不代表局部 NAND die 不会饥饿。

## Dynamic Wear Leveling

Dynamic wear leveling 通过写分配和 GC victim 选择影响正在活动的 block：

- 优先把新写入分配到 erase count 较低的 free block。
- victim selection 中加入 erase count 偏差。
- 对高 erase count block 降低再次写入概率。

优点是额外搬迁少，缺点是无法处理长期冷数据占据低 erase count block 的情况。

## Static Wear Leveling

Static wear leveling 会主动搬迁冷数据，让低 erase count block 重新进入 free pool。它适合在 erase count skew 超过阈值时运行。

触发条件示例：

- `max_erase_count - min_erase_count` 超过阈值。
- 冷 block 年龄超过阈值且 erase count 明显低于平均。
- 预计寿命不均衡影响 DWPD/保修目标。

风险：

- 主动搬迁冷数据会提高 WAF。
- 如果和 foreground write 或 GC 争抢 channel，会放大读尾延迟。
- 搬迁冷数据时必须使用和 GC 相同的版本检查，避免 host overwrite race。

## Refresh / Scrub 与 GC 的关系

Refresh 和 scrub 不是 GC，但会使用相似的数据搬迁路径：

- Read disturb：高读计数 block 触发 scrub。
- Retention：冷数据长时间未迁移，按 age/temperature 触发 refresh。
- ECC margin：corrected bit count 接近阈值时提前搬迁。

调度上应把它们记为独立后台任务，避免把 refresh write 混进 GC relocation write。

## 并发和掉电边界

GC/wear leveling 必须和写路径使用同一套版本规则：

- 搬迁前读取 victim page 的 P2L。
- 搬迁提交前确认当前 L2P 仍指向 victim PPA。
- 提交 relocation journal 后再让新 PPA 成为权威。
- old PPA retire 和 victim erase 必须可重放、可幂等。

对应掉电窗口见 [掉电恢复状态表](../../tests/faults/power-loss-state-table.yml) 的 `PLP-WIN-008` 到 `PLP-WIN-010`。

## 观测指标

| 指标 | 说明 | 相关测试 |
|---|---|---|
| WAF | NAND writes / host writes | T5-001, T5-003 |
| GC relocation writes | GC 搬迁写，不含 host write | T2-002, T5-001 |
| Wear leveling writes | static/dynamic wear leveling 搬迁写 | T2-002 |
| GC duty cycle | GC active 时间占比 | T5-002 |
| Free block watermark | 每个 channel/die 的 free block 水位 | T2-002 |
| Emergency GC count | 进入 emergency 状态次数 | T2-002, T5-003 |
| Read p999 during GC | GC 活动期间读尾延迟 | T5-002 |
| Erase skew | max/min/avg erase count 差异 | T2-002 |

## 验证点

- 低 OP 随机写下 free block pool 不跌破 emergency reserve。
- Greedy 与 cost-benefit victim selection 的 WAF 对比。
- hot/cold 分离对未来 GC 搬迁量的影响。
- foreground read 与 GC relocation 争抢 channel 时 p999 是否受控。
- static wear leveling 启动后 erase skew 收敛，但 WAF 增量可解释。
- GC 搬迁与 host overwrite 同一 LPN 时不会复活旧数据。
- 掉电发生在 GC copy、mapping switch、victim erase 边界时仍能恢复。

## 关键来源

- [FTL 设计深水区](ftl-design-deep-dive.md)
- [性能、QoS 与写放大](performance-qos-write-amplification.md)
- [掉电恢复状态表](../../tests/faults/power-loss-state-table.yml)
- [MQSim](https://github.com/CMU-SAFARI/MQSim)
- [SimpleSSD](https://github.com/SimpleSSD/SimpleSSD)
- [SPDK FTL](https://spdk.io/doc/ftl.html)
