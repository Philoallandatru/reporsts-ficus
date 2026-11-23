---
type: Concept
title: FTL 元数据格式与恢复约定
description: 本页给出教学/原型 SSD 可采用的 FTL 元数据布局与恢复约定。真实产品会更复杂，但这一版已经足够把“哪些状态必须持久化、哪些状态可以重建、掉电后怎么恢复”讲清楚。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# FTL 元数据格式与恢复约定

本页给出教学/原型 SSD 可采用的 FTL 元数据布局与恢复约定。真实产品会更复杂，但这一版已经足够把“哪些状态必须持久化、哪些状态可以重建、掉电后怎么恢复”讲清楚。

## 元数据区域

| 区域 | 持久化 | 用途 |
|---|---|---|
| Superblock | 是，多副本 | 记录 metadata layout、generation、当前 checkpoint、journal head/tail、recoverable layout 范围 |
| Checkpoint | 是，多代 | 保存 L2P 摘要、block table、free pool 摘要、open block 摘要 |
| Journal | 是，顺序追加 | 记录最近映射变化、block 状态变化、GC move 和 namespace 事件 |
| Block table | 是，可 checkpoint | 记录 erase count、valid count、state、bad flag、last sequence |
| L2P cache | 否 | 运行时快速查找，掉电后允许重建 |
| P2L page metadata | 是，随数据页或 metadata page | GC 和恢复时反查 LPN、版本号和来源 block |

一个实用原则是：只要恢复时需要证明“这页确实是最新且完整的”，它就不应该只存在于易失缓存里。

## Superblock 字段

| 字段 | 说明 |
|---|---|
| magic | 固定签名 |
| format_version | 元数据格式版本 |
| firmware_min_version | 兼容的最低固件版本 |
| generation | 单调递增代号 |
| device_uuid | 设备或 namespace 身份 |
| geometry_hash | NAND geometry/config hash |
| active_checkpoint_id | 当前 checkpoint |
| journal_start / journal_tail | 可重放日志范围 |
| crc | Superblock 校验 |

Superblock 至少保留两个副本，写新副本成功后再切换 active generation。通常还会保留一个只读的 factory 或 rescue 入口，用来处理 layout migration 失败后的最小恢复。

## Journal Entry 字段

| 字段 | 说明 |
|---|---|
| entry_magic | Entry 签名 |
| sequence | 单调递增序号 |
| type | mapping_update、block_state、gc_move、namespace_event |
| lpn | 受影响逻辑页 |
| new_ppn | 新物理页 |
| old_ppn | 旧物理页 |
| version | LPN 版本号，防止旧数据复活 |
| block_delta | valid/free/erase count 变化 |
| data_crc | 可选数据校验或摘要 |
| entry_crc | Entry 校验 |
| commit_marker | 完整写入标记 |

恢复时只重放 CRC 正确且 commit marker 完整的 entry。

建议把 journal 设计成幂等重放：

- mapping update 重放多次，结果应相同。
- block state 变化重放多次，结果应相同。
- GC move 必须带 version 或 sequence，避免旧页复活。
- namespace 级事件要能区分“设备内状态变化”和“主机可见配置变化”。

## Block State

| 状态 | 含义 |
|---|---|
| FREE | 已擦除，可写 |
| OPEN | 当前正在写入 |
| CLOSED | 写满，等待读或 GC |
| VICTIM | 被 GC 选中，正在搬迁 |
| ERASE_PENDING | 搬迁完成，等待 erase |
| BAD | 不再使用 |
| META | 存放元数据 |

状态转换必须能在掉电后重放。`VICTIM` 和 `ERASE_PENDING` 是恢复中最容易出错的状态。

## 恢复算法

1. 找到 generation 最大且 CRC 正确的 superblock。
2. 加载 active checkpoint。
3. 按 sequence 扫描 journal。
4. 忽略不完整或 CRC 错误 entry。
5. 对 mapping_update 检查 new_ppn 的 page metadata。
6. 用 version 解决并发 overwrite 与 GC 搬迁冲突。
7. 重建 free pool 和 open block。
8. 对异常 block state 做保守修复：不确定时宁可少释放 free block。

### 恢复顺序为什么这样排

- 先 superblock，再 checkpoint，是为了先确定“该信哪一代布局”。
- 先 checkpoint，再 journal，是为了避免全量扫描。
- 先校验 page metadata，再接受 mapping_update，是为了防止 L2P 指向未完成 program 的页。
- 先恢复 block table，再恢复 free pool，是为了避免把坏块或未完成迁移的块放回可写池。
- 对不确定状态保守处理，是为了让恢复结果稳定，而不是在几次上电之间摇摆。

## 设计约束

- 元数据写入必须自身 wear-leveling。
- Metadata journal 不应和用户数据共享同一个无法区分的 free pool。
- 每个 metadata page 都应有 checksum、generation 和 copy id。
- 格式升级要支持新旧固件兼容或明确禁止回滚。
- Recovery 时间要有上限，journal 不能无限增长。
- 任意一条恢复路径都应能在重复上电后保持幂等。
- Block table 和 journal 的语义不能互相替代：前者表示当前态，后者表示变化历史。
- 只有在 checkpoint 和 journal 都不足以恢复时，才允许退化到更慢的扫描式重建。

## 与固件边界的关系

这一页和 [FTL 与固件职责](firmware-ftl.md) 是一组：

- `firmware-ftl.md` 讲 FTL 要管什么。
- 本页讲 FTL 的状态怎样落盘、怎样重放、怎样从掉电或 reset 中回来。

如果你在设计原型控制器，先把本页里的 superblock、checkpoint、journal、block table、P2L metadata 这五个对象的责任边界定死，再去写代码，后续会少很多恢复分歧。

## 实现时的最小状态机

一个可落地的原型通常只需要以下几个恢复态：

| 状态 | 进入条件 | 退出条件 |
|---|---|---|
| cold_boot | 上电或 controller reset | 读到完整 superblock 并确认 layout 版本 |
| load_checkpoint | 选定 active generation | checkpoint 校验通过 |
| replay_journal | checkpoint 之后的 journal 存在 | 扫到最后一个完整 commit marker |
| rebuild_tables | journal replay 完成 | L2P、P2L、block table、free pool 重建完成 |
| sanitize_inconsistent | 发现不一致或半写入 entry | 保守修复完成 |
| ready_for_io | 恢复完成并可接受 host 命令 | NVMe ready |

这组状态的意义在于：它足够小，适合原型实现；又足够明确，能把恢复过程拆成可测试的阶段。

## 和掉电恢复的分工

本页偏“数据布局”和“恢复格式”；[掉电保护与恢复](power-loss-recovery.md) 偏“注入窗口”和“恢复语义”。

- 本页回答 journal、checkpoint、superblock 应该长什么样。
- 掉电恢复页回答在 DMA、program、journal、checkpoint 这些窗口掉电时应该怎么解释结果。

两页合起来，才能把 FTL 的持久化边界说完整。

## 关键来源

- SPDK FTL: https://spdk.io/doc/ftl.html
- DFTL: https://dl.acm.org/doi/10.1145/1508244.1508271
- Cosmos+ OpenSSD documentation: https://cosmos-plus-openssd-doc.readthedocs.io/
- [掉电保护与恢复](power-loss-recovery.md)
- [FTL 设计深水区](ftl-design-deep-dive.md)
- [FTL 与固件职责](firmware-ftl.md)
