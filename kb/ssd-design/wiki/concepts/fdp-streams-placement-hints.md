---
type: Concept
title: FDP、Streams、Placement Hint 与内部 FTL
description: FDP、streams、placement hint、ZNS 和 hot/cold data hint 都在回答同一个工程问题：主机能不能把“哪些数据应该放在一起、哪些数据生命周期相近”告诉
  SSD，从而降低内部 GC 搬迁和写放大。它们的语义强度不同，FTL 不能把 host hint 当成绝对真理。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# FDP、Streams、Placement Hint 与内部 FTL

FDP、streams、placement hint、ZNS 和 hot/cold data hint 都在回答同一个工程问题：主机能不能把“哪些数据应该放在一起、哪些数据生命周期相近”告诉 SSD，从而降低内部 GC 搬迁和写放大。它们的语义强度不同，FTL 不能把 host hint 当成绝对真理。

## 边界声明

| 层级 | 负责内容 | 不负责内容 |
|---|---|---|
| NVMe / 标准接口 | host-visible command、feature、log、namespace 或 placement 语义 | SSD 内部如何布局 NAND、GC 和 wear leveling |
| FTL / firmware | 将 hint 映射到 stream group、reclaim unit、superblock、SLC cache 或 GC policy | 改写规范语义或向 host 承诺未声明能力 |
| 专利 / 厂商资料 | 提供工程术语、placement 设计动机和可能实现族 | 不能作为协议合规或产品实现的规范依据 |

知识库里所有 FDP/streams 相关设计都应同时追踪 host-visible 规范入口、内部 FTL policy、WAF/GC relocation/stream isolation/write cliff/tail latency 指标，以及 hint 缺失或错误时的 fallback 行为。

## 语义强度对比

| 机制 | Host 给出的信息 | Device 自由度 | FTL 影响 | 风险 |
|---|---|---|---|---|
| No hint | 没有生命周期或分组信息 | 最大 | FTL 自己做 hot/cold 分类 | 分类滞后，GC 搬迁多 |
| Streams / write stream | 写入属于某个 stream 或生命周期组 | 中 | 可把 stream 映射到不同 block/line | stream ID 滥用或粒度太粗 |
| FDP / placement handle | host guided data placement / reclaim unit 相关提示 | 中 | 可减少 reclaim unit 内冷热混合 | hint 与内部 free pool/QoS 冲突 |
| ZNS | host 按 zone 顺序写，管理 zone lifecycle | 较小 | FTL 更接近 zone/segment 管理 | host 责任更重，兼容性要求高 |
| Vendor hints | 厂商特定温度、QoS 或 namespace policy | 可变 | 可深度绑定内部策略 | 不可移植，验证难 |

## 内部映射对象

| 内部对象 | 作用 | 适合绑定的 hint |
|---|---|---|
| Write frontier | 当前写入位置 | stream、temperature、namespace |
| Superblock / line | 多 die/channel 条带化写入单位 | FDP placement handle、hot/cold group |
| Reclaim unit | GC 回收单位 | FDP、ZNS zone group、stream group |
| SLC cache partition | cache admission 和 destage 分区 | short-lived data、small random writes、QoS hint |
| GC victim class | victim selection 候选集 | placement group、temperature、age |
| Wear leveling pool | erase count 平衡范围 | namespace / tenant isolation |

设计原则：host hint 可以影响写入分组，但不能破坏 free block 前向进展、PLP recovery、ECC refresh 或 wear leveling。

## Placement-aware 写路径

1. 解析 NVMe command 中的 namespace、directive、stream、placement handle 或 zone 信息。
2. 将 host hint 映射到内部 placement class。
3. 检查该 class 的 free block、SLC cache occupancy、GC pressure 和 QoS budget。
4. 选择 write frontier 或 fallback class。
5. 写入 data page，并在 page metadata 中记录 placement class / stream / sequence。
6. 更新 L2P、P2L、block table 和 placement statistics。

关键是 fallback：如果目标 placement class 没有空闲 block，设备可以选择 emergency fallback，但必须记录统计，否则后续 GC 会误以为隔离仍然成立。

## 与 GC 的关系

Placement-aware GC 的目标是让 reclaim unit 内的数据生命周期更一致。

| 设计点 | 好处 | 风险 |
|---|---|---|
| 按 placement class 选择 victim | 减少冷热混合搬迁 | class 太小导致 free block 碎片 |
| stream-local free pool | 提升隔离 | 某些 stream 饥饿 |
| fallback class | 保证前向进展 | 降低 hint 有效性 |
| placement-aware cost-benefit | 兼顾 age、valid count 和 stream | 参数更复杂 |
| per-class WAF | 找出坏 hint 或混写 tenant | telemetry 成本上升 |

对应策略可与 [GC Policy Matrix](../../tests/requirements/gc-policy-matrix.yml) 的 hot/cold-aware 和 QoS-aware 项结合。

## 与 SLC Cache 的关系

SLC cache 不能简单地把所有 hinted write 都收进去。placement hint 会影响是否 admit 到 SLC cache、是否为不同 stream 分配独立 SLC budget、destage 时是否保持 placement class、大顺序/冷数据是否 bypass SLC，以及 cache full 时 fallback 是否破坏后续 GC 隔离。

对应策略可与 [SLC Cache Policy Matrix](../../tests/requirements/slc-cache-policy-matrix.yml) 的 size-aware、temperature-aware 和 emergency destage 项结合。

## 错误使用与防御

| 场景 | 风险 | 防御 |
|---|---|---|
| Host 所有写都用同一个 stream | hint 失去分组意义 | 降级为 no-hint policy，记录 low entropy |
| Host 频繁改变 stream | 造成碎片和小 reclaim unit | 合并小 stream 或设置 minimum allocation |
| Tenant 混写同一 placement class | GC isolation 失效 | per-namespace/tenant statistics |
| Hint 与写入大小冲突 | 大顺序写污染 SLC cache | size-aware bypass |
| Free pool 不足 | 强行隔离导致写阻塞 | fallback class + emergency GC |
| 掉电恢复缺少 placement metadata | 恢复后 class 信息丢失 | page metadata / journal 记录 placement class |

## 观测指标

| 指标 | 说明 | 相关测试 |
|---|---|---|
| Per-class WAF | 每个 placement class 的写放大 | T5-001 |
| Stream isolation ratio | 同一 reclaim unit 内同 class page 比例 | T2-002 |
| Fallback rate | hint 无法满足时 fallback 次数 | T5-003 |
| Placement entropy | host hint 分布是否有效 | T7-001 |
| Per-class free blocks | 每类 placement pool 的水位 | T2-002 |
| Read p999 during placement GC | placement-aware GC 期间读尾延迟 | T5-002 |
| SLC per-class occupancy | SLC cache 中不同 class 占用 | T5-003 |

## 验证点

- 无 hint、正确 hot/cold hint、错误 hint 三组 workload 的 WAF 对比。
- stream/FDP class 与 GC victim selection 的隔离效果。
- SLC cache full 时 placement class 是否保持或记录 fallback。
- 低 free block 时 fallback 不导致 host write 无前向进展。
- 掉电恢复后 placement metadata 与 L2P/P2L 一致。
- per-class telemetry 能解释 WAF、write cliff 和 GC duty cycle。

## 关键来源

- NVM Express Specifications: https://nvmexpress.org/specifications/
- NVM Express FDP blog: https://nvmexpress.org/nvmeflexible-data-placement-fdp-blog/
- [GC Victim Selection 与 Wear Leveling 策略](gc-wear-leveling-policy.md)
- [SLC Cache、Write Cliff 与 Destage 策略](slc-cache-write-cliff-destage.md)
- [SSD 专利检索索引](../../PATENT_INDEX.md)
