---
type: Concept
title: Flash Scheduler、Channel/Die/Plane Arbitration 与 Read Priority
description: Flash scheduler 是 SSD 后端的调度中枢。它把 FTL、GC、SLC destage、read retry、refresh/scrub
  和 host I/O 产生的 NAND request 排到 channel、die/LUN、plane 和 ECC pipeline 上执行。好的 scheduler
  不是只追求吞吐，而是在并行度、...
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Flash Scheduler、Channel/Die/Plane Arbitration 与 Read Priority

Flash scheduler 是 SSD 后端的调度中枢。它把 FTL、GC、SLC destage、read retry、refresh/scrub 和 host I/O 产生的 NAND request 排到 channel、die/LUN、plane 和 ECC pipeline 上执行。好的 scheduler 不是只追求吞吐，而是在并行度、尾延迟、前向进展、磨损、错误恢复和掉电边界之间取平衡。

## 设计目标

- 利用 channel/die/plane 并行度，同时避免某个 die 或 request class 饥饿。
- 前台 read 和 read retry 有足够优先级，控制 p99/p999。
- GC、destage、wear leveling、refresh 和 scrub 有预算，不破坏 free block 前向进展。
- 尊重 NAND timing、multi-plane 约束、program/erase suspend/resume 限制。
- 对 timeout、program fail、erase fail、uncorrectable read 和 ECC retry storm 有可恢复路径。
- 暴露 channel utilization、queue depth、busy time、retry count、suspend count 等 telemetry。

## 调度输入

| Request class | 来源 | 典型优先级 | 风险 |
|---|---|---|---|
| Foreground read | host read | 最高 | 被 program/GC 占 channel 造成尾延迟 |
| Read retry / soft decode | ECC failure path | 最高或紧急 | retry storm 饿死其他请求 |
| Foreground write program | host write / SLC admission | 高 | free block low 时阻塞 |
| Flush/FUA metadata | persistence path | 高 | 完成点错误会破坏语义 |
| GC relocation read/write | GC policy | 中 | 抢读、抢写、WAF 上升 |
| SLC destage | cache policy | 中 | cache full 时变成紧急 |
| Wear leveling / refresh / scrub | 后台可靠性 | 低到中 | 长期不运行会增加可靠性风险 |
| Erase | GC / free pool | 低到中 | erase busy 长，且失败要 retire block |

## 资源模型

| 资源 | 共享关系 | 调度关注点 |
|---|---|---|
| Channel bus | 同 channel 下 package/die 共享数据总线 | 数据传输阶段不能冲突 |
| Die/LUN | 有独立 busy 状态 | program/read/erase timing、suspend 能力 |
| Plane | multi-plane 操作受地址/block 条件限制 | pairing、block alignment、bad block mismatch |
| ECC/LDPC engine | 多 channel 可能共享 decoder | soft decode storm、硬件瓶颈 |
| SRAM/DRAM buffer | read/write/GC/destage 共享 | buffer deadlock |
| Metadata engine | journal/checksum/parity | flush/FUA、checkpoint |

## Arbitration 策略

| 策略 | 说明 | 优点 | 风险 |
|---|---|---|---|
| FIFO per channel | 每个 channel 独立 FIFO | 简单、硬件友好 | read tail latency 差 |
| Read-priority | read/read retry 优先于 program/erase | 降低读尾延迟 | 写入、GC 或 erase 饥饿 |
| Weighted round-robin | 按 class/channel 权重轮转 | 可控公平性 | 权重调参复杂 |
| Deadline-aware | request 带 deadline 或 age | 防饥饿 | 需要计时和 aging |
| Die-aware placement | 分散 hot die，平衡 busy time | 提升并行度 | 与 FTL placement/GC 冲突 |
| QoS budgeted background | GC/destage/scrub 消耗预算 | 前台延迟可控 | free block pressure 下需升级优先级 |

推荐实现：read-priority + aging + background budget + emergency override。读优先不能无限制，否则写路径和 free block 会死锁。

## Program / Erase Suspend

部分 NAND 支持 program suspend、erase suspend 或 read while busy 变体。使用时要明确：

- suspend/resume 是否影响 program disturb 或可靠性。
- suspend 次数是否有限制。
- suspend 后 read latency 和 program completion 如何计数。
- 是否允许在同 die/plane 上插入 read。
- timeout 后如何 abort、retry 或 retire block。

调度策略：

| 场景 | 建议 |
|---|---|
| Foreground read 等待被 program 占用的 die | 如果 NAND 支持且预算允许，触发 program suspend |
| GC program 正在占用 die | 更容易 suspend，优先释放读路径 |
| Erase 长时间阻塞 read | 允许 erase suspend 或选择其他 die |
| Soft decode storm | 限制 retry 并发，防止 ECC engine 饱和 |

## Multi-plane 与并行度

Multi-plane 可以提高 throughput，但要求：

- plane 地址、block pairing 满足 NAND datasheet。
- 两个 plane 都不是 bad block，且 erase count/状态匹配。
- metadata、P2L、ECC codeword 和 retry 信息能区分 plane。
- program fail 时能定位失败 plane 并修复 mapping。

风险：

- 为了凑 multi-plane 导致写入分组变差，未来 GC 成本升高。
- 某个 plane bad block 破坏 superblock/line 对齐。
- read priority 与 multi-plane batch 冲突。

## 错误路径

| 错误 | Scheduler 行为 | 上层影响 |
|---|---|---|
| Program fail | 停止使用目标 page/block，通知 FTL remap | 旧映射保持有效 |
| Erase fail | retire block，更新 bad block table | free pool 减少 |
| Read timeout | retry、reset die/channel 或 isolate | 可能返回 NVMe error |
| Correctable high count | 上报 ECC count，触发 refresh/scrub | 后台任务增加 |
| Uncorrectable read | read retry/soft decode/parity/recovery | 失败时返回正确 status |
| Channel timeout | abort outstanding，恢复 channel state | 避免全控制器死锁 |

## Telemetry

| 指标 | 说明 | 相关测试 |
|---|---|---|
| Channel utilization | 每个 channel busy ratio | T5-001 |
| Die busy histogram | die/LUN busy 分布 | T5-002 |
| Read p999 under GC | GC 活动时读尾延迟 | T5-002 |
| Program/erase suspend count | suspend/resume 次数 | T5-002 |
| ECC retry queue depth | retry storm 指标 | T5-004 |
| Background budget debt | GC/destage/scrub 欠账 | T5-002 |
| Program/erase fail count | NAND fail 统计 | T3-001 |
| Channel timeout count | 后端死锁/恢复风险 | T3-002 |

## 验证点

- mixed read/write + GC active 时 read p999 是否受控。
- read-priority 开启后 foreground write 和 GC 是否仍有前向进展。
- program/erase suspend 后数据、metadata 和 timing 统计一致。
- multi-plane bad block mismatch 时不会写错 plane。
- ECC soft decode storm 不饿死普通 read/write。
- channel timeout 后能隔离或恢复，不拖死全控制器。
- 掉电发生在 program/erase/suspend 边界时，FTL recovery 仍能解释状态。

## 关键来源

- [控制器硬件与 NAND 接口](hardware-controller-and-nand.md)
- [控制器硬件模块边界](controller-hardware-module-boundaries.md)
- [GC Victim Selection 与 Wear Leveling 策略](gc-wear-leveling-policy.md)
- [性能、QoS 与写放大](performance-qos-write-amplification.md)
- ONFI Specifications: https://onfi.org/specs.html
- Cosmos+ OpenSSD documentation: https://cosmos-plus-openssd-doc.readthedocs.io/
