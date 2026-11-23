---
type: Concept
title: FTL Hybrid / Log-block Mapping
description: Hybrid mapping 把粗粒度 data block mapping 和细粒度 log block mapping 结合起来。核心思路是：稳定顺序数据保留在
  data block，小随机覆盖写先追加到 log block，之后通过 merge 把 log block 和 data block 合并成新的 data block。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# FTL Hybrid / Log-block Mapping

Hybrid mapping 把粗粒度 data block mapping 和细粒度 log block mapping 结合起来。核心思路是：稳定顺序数据保留在 data block，小随机覆盖写先追加到 log block，之后通过 merge 把 log block 和 data block 合并成新的 data block。

## 设计目标

- 降低 page mapping 的 DRAM 元数据开销。
- 避免纯 block mapping 在小随机写下频繁整块迁移。
- 用 log block 吸收覆盖写和小写。
- 通过 merge 控制写放大、尾延迟和 free block 消耗。

## 核心术语

| 术语 | 含义 | 设计关注点 |
|---|---|---|
| Data block | 主要数据块，按逻辑 block 粒度映射 | 顺序写友好，元数据小 |
| Log block | 接收覆盖写的追加写块 | 数量有限，需要快速查找最新页 |
| Switch merge | log block 刚好覆盖完整逻辑块并顺序排列，可直接变成 data block | 写放大最低 |
| Partial merge | log block 只覆盖部分 page，需要从 old data block 拷贝剩余有效页 | 常见但有搬迁成本 |
| Full merge | 多个 log block 或乱序更新，需要读旧块和日志块重组 | 写放大和尾延迟最高 |

FAST 这类 fully-associative sector translation 进一步允许 log block 与任意 data block 关联，以提高 log block 利用率，但查找和 merge 状态更复杂。

## 映射结构

| 数据结构 | 内容 | 设计关注点 |
|---|---|---|
| Data block map | `Logical block -> physical data block` | 小、可常驻 |
| Log block map | `Logical page/sector -> physical log page` | 必须能找到最新版本 |
| Log association table | log block 与 data block 或 logical page 的关系 | direct-mapped / fully-associative |
| Page validity bitmap | data/log block 中 page 是否有效 | merge 和 recovery |
| Merge journal | merge 开始、搬迁、提交、擦除阶段 | 掉电恢复和幂等性 |

## 写路径

1. 将 LBA 定位到 logical block 和 page offset。
2. 如果是顺序写且可形成整块，直接写 data block 或准备 switch merge。
3. 如果是覆盖写或小写，选择 log block page 追加写入。
4. 更新 log page map，让读路径优先命中新 log page。
5. 当 log block 满、log block 数量不足或 GC watermark 触发时执行 merge。

写入时不能只更新 data block map，因为最新数据可能在 log block。读路径必须先查 log block，再回退到 data block。

## 读路径

1. 查 logical block 对应的 log metadata。
2. 如果目标 page 在 log block 有最新版本，读 log page。
3. 否则读 data block 中对应 offset。
4. 校验 page metadata 中的 logical page / sector / sequence。

读放大来自 log lookup 和 log/data 分散。为了控制读延迟，常见做法是缓存 hot logical block 的 log map，或者限制每个 data block 关联的 log block 数量。

## Merge 状态机

| 阶段 | 动作 | 持久化证据 |
|---|---|---|
| Prepare | 选择 victim data/log block，分配 new block | merge journal prepare record |
| Copy | 把最新版本 page 写入 new block | page metadata + copy progress |
| Commit | 原子切换 data block map | commit record + sequence |
| Retire | old data/log block 标记 stale 并擦除 | block table update |

merge 必须可重入。掉电恢复看到 prepare 但没有 commit 时，可以丢弃 new block 或继续 copy；看到 commit 后必须保证 data block map 指向 new block，并且 old block 不再作为最新数据来源。

## GC 与写放大

Hybrid mapping 的写放大主要来自 merge。需要监控：

- log block 命中率。
- switch/partial/full merge 比例。
- 每次 merge 搬迁 page 数。
- log block starvation 次数。
- host write 被 merge 阻塞的延迟。

设计取舍：

- log block 越多，随机写越容易吸收，但 metadata 和 recovery 更复杂。
- direct-mapped log block 查找简单，但冲突多。
- fully-associative log block 利用率高，但 lookup/merge 成本高。
- hot/cold 分离能降低 full merge 概率。

## 适用场景

| 场景 | 适配度 | 说明 |
|---|---|---|
| DRAM 较小的控制器 | 高 | data block map 小，log metadata 可控 |
| 顺序写为主 workload | 高 | switch merge 可降低写放大 |
| 高随机写 enterprise workload | 中 | log block 容易被打满，full merge 尾延迟明显 |
| 教学 FTL | 高 | 能清楚展示 log-structured overwrite 和 merge 机制 |

## 验证点

- 顺序写触发 switch merge。
- 小随机覆盖写触发 partial merge。
- 多 log block 乱序更新触发 full merge。
- merge commit 前掉电，恢复后不能丢失旧 data block。
- merge commit 后掉电，恢复后不能读到旧 data/log page。
- log block 数量耗尽时仍能完成前向进展。

## 关键来源

- [FAST log-block FTL](https://link.springer.com/chapter/10.1007/11807964_88)
- [SSD 设计论文与 BibTeX 种子](../../BIBLIOGRAPHY.md)
- [FTL 设计深水区](ftl-design-deep-dive.md)
- [FlashSim](https://github.com/flashsim/flashsim)
