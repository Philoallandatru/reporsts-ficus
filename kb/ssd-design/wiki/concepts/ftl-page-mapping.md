---
type: Concept
title: FTL Page Mapping
description: Page mapping 是最直接、随机写最友好的 FTL 映射策略：每个 logical page number 都独立映射到一个 physical
  page。主机覆盖写不会原地改 NAND，而是写入新 physical page，再把旧 physical page 标记为 invalid。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# FTL Page Mapping

Page mapping 是最直接、随机写最友好的 FTL 映射策略：每个 logical page number 都独立映射到一个 physical page。主机覆盖写不会原地改 NAND，而是写入新 physical page，再把旧 physical page 标记为 invalid。

## 设计目标

- 让随机写接近 append-only 写入，避免 block-level overwrite amplification。
- 让读路径只需要一次 L2P lookup 就能定位 physical page。
- 支持 overwrite、trim/deallocate、GC 搬迁、掉电恢复和坏块替换。
- 在 DRAM/SRAM 元数据开销、checkpoint 成本和恢复时间之间取平衡。

## 核心数据结构

| 数据结构 | 内容 | 设计关注点 |
|---|---|---|
| L2P table | `LPN -> PPA` | 常驻 DRAM、压缩、分片、热区缓存、checkpoint |
| P2L metadata | `PPA -> LPN + version` | GC 搬迁、scan rebuild、掉电恢复 |
| Block table | erase count、valid count、invalid count、free/closed/victim/bad | victim selection、wear leveling、前向进展 |
| Write frontier | 当前可写 block/page 指针 | 按 channel/die/plane 分组，保证并行度 |
| Mapping journal | 映射变更、block 状态变更、sequence number | 原子性、重放顺序、日志截断 |

PPA 通常至少包含 channel、die/LUN、plane、block、page。产品实现还会把 superblock、line、zone、reclaim unit 或 RAID stripe 编码进去。

## 写路径

1. 将 LBA 切分成 LPN。
2. 为每个 LPN 选择可写 physical page。
3. 写 NAND page，同时写入 spare/OOB 或 metadata page 中的 LPN、sequence number、CRC。
4. 在 mapping journal 中记录 `LPN -> new PPA`。
5. 更新 volatile L2P。
6. 将 old PPA 标记 invalid，并更新 block valid count。
7. 满足 flush/FUA/PLP 语义后返回完成。

关键点是“host completion 的承诺”。如果设备声明 volatile write cache 且没有 PLP，普通 write 可以在数据仍处于 volatile buffer 时完成；如果 FUA/flush 或 PLP 语义要求数据持久，必须明确完成点和恢复证据。

## 读路径

1. 将 LBA 切分成 LPN。
2. 查 L2P，得到 PPA。
3. 下发 NAND read。
4. ECC hard decode；失败时进入 read retry / soft decode。
5. 校验 metadata 中的 LPN/version，防止 stale page 被误读。
6. 返回数据；必要时触发 read reclaim 或 scrub。

metadata 中的 LPN/version 是 page mapping 的保险丝。它能在 journal 重放、GC 并发、掉电恢复或 mapping corruption 后发现 L2P 指向了旧页。

## GC 影响

Page mapping 的 GC 可以只搬迁 victim block 中仍有效的 page，不需要整块逻辑搬迁。GC 需要：

- 读取 victim block 的 P2L metadata。
- 对每个 valid page 检查当前 L2P 是否仍指向该 PPA。
- 把有效数据写到新位置。
- 用新 PPA 更新 L2P 和 journal。
- 擦除 victim block 并归还 free pool。

危险并发：

- GC 搬迁某个 LPN 时，host 同时覆盖写同一 LPN。
- GC 读 victim page 遇到 correctable/uncorrectable error。
- free block pool 太低，GC 无法搬出 victim 中的有效页。
- journal 写入顺序让掉电恢复后旧 PPA 复活。

## 元数据持久化

Page mapping 的主要成本是 L2P 表很大。常见策略：

- 周期性 checkpoint 全量或分片 L2P。
- 顺序 journal 记录增量更新。
- 每个 physical page 或 metadata page 保留 P2L。
- 恢复时先加载 checkpoint，再按 sequence number 重放 journal，最后必要时 scan flash。

恢复时必须处理：

- journal entry 写了一半。
- data page program 成功但 journal 未持久化。
- journal 持久化但 L2P checkpoint 尚未更新。
- GC 搬迁和 host overwrite 的 sequence 冲突。

## 适用场景

| 场景 | 适配度 | 说明 |
|---|---|---|
| DRAM 充足的 enterprise SSD | 高 | 随机写和低延迟读收益明显 |
| 小容量教学控制器 | 高 | 最容易实现和验证 |
| DRAM-less client SSD | 中 | 需要 HMB、mapping cache 或压缩映射 |
| 极大容量 QLC SSD | 中 | L2P 开销大，常与 segment/zone/reclaim unit 结合 |

## 验证点

- 随机覆盖写后读取最新数据。
- GC 搬迁期间 host overwrite 同一 LPN。
- 掉电发生在 data page program 完成后、journal 持久化前。
- 掉电发生在 journal 持久化后、checkpoint 前。
- P2L 与 L2P 不一致时拒绝 stale page。
- free block watermark 低于阈值时仍能保证 GC 前向进展。

## 关键来源

- [FTL 设计深水区](ftl-design-deep-dive.md)
- [FTL 元数据格式与恢复约定](ftl-metadata-format-and-recovery-conventions.md)
- [DFTL paper](https://dl.acm.org/doi/10.1145/1508244.1508271)
- [SPDK FTL](https://spdk.io/doc/ftl.html)
- [SimpleSSD](https://github.com/SimpleSSD/SimpleSSD)
