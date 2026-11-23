---
type: Concept
title: 性能、QoS 与写放大
description: SSD 性能不是一个 IOPS 数字。真正需要管理的是前端队列、后端 NAND 并行、FTL 后台写、ECC retry、热/电源限制共同作用下的延迟分布和写放大。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 性能、QoS 与写放大

SSD 性能不是一个 IOPS 数字。真正需要管理的是前端队列、后端 NAND 并行、FTL 后台写、ECC retry、热/电源限制共同作用下的延迟分布和写放大。

## 性能路径

Host I/O 延迟可以拆成：

```text
host queue wait
  + PCIe / doorbell / command fetch
  + firmware dispatch
  + mapping lookup
  + NAND or buffer service time
  + ECC / crypto / metadata
  + DMA completion
  + CQE / interrupt / polling
```

读路径的尾延迟常来自 mapping cache miss、NAND queueing、read retry、ECC soft decode、被 GC 写占用 channel。写路径的尾延迟常来自 SLC cache 写满、free block watermark 降低、GC 搬迁、metadata flush、thermal throttling。

## 写放大

WAF = NAND 实际写入量 / Host 写入量。

会提高 WAF 的因素：

- 随机覆盖写。
- 低 over-provisioning。
- GC victim 中 valid page 多。
- Static wear leveling 搬迁冷数据。
- SLC cache destage。
- Metadata journal/checkpoint。
- RAID-like parity。
- Small write coalescing 不充分。

需要分开统计：

- Host writes。
- GC relocation writes。
- Wear leveling writes。
- Metadata writes。
- Parity/ECC-related writes。
- SLC cache destage writes。

## QoS 控制点

| 控制点 | 目标 | 风险 |
|---|---|---|
| Read priority | 降低读尾延迟 | 写入和 GC 饥饿 |
| GC budget | 限制后台任务干扰 | Free block pool 过低 |
| Write throttling | 保证 GC 前向进展 | Host 看到写 cliff |
| Channel-aware placement | 提高并行度 | 未来 GC 复杂 |
| Hot/cold separation | 降低 GC 搬迁 | 分类错误导致碎片 |
| Thermal throttling | 控制温度 | 延迟和带宽突降 |
| Interrupt coalescing | 降低 CPU 开销 | 增加小 I/O 延迟 |

GC 策略、watermark 和 wear leveling 的详细对比见 [GC Victim Selection 与 Wear Leveling 策略](gc-wear-leveling-policy.md)。机器可读策略矩阵见 [GC Policy Matrix](../../tests/requirements/gc-policy-matrix.yml)。

SLC cache、write cliff 和 destage 的详细策略见 [SLC Cache、Write Cliff 与 Destage 策略](slc-cache-write-cliff-destage.md)。机器可读策略矩阵见 [SLC Cache Policy Matrix](../../tests/requirements/slc-cache-policy-matrix.yml)。

DRAM-less/HMB 下的 mapping cache miss、HMB fault fallback 和 miss storm QoS 见 [DRAM-less SSD 与 Host Memory Buffer](dram-less-hmb-ssd.md)。机器可读策略矩阵见 [HMB Policy Matrix](../../tests/requirements/hmb-policy-matrix.yml)。

NAND 后端 read priority、channel/die fairness、program/erase suspend 和 ECC retry storm 限流见 [Flash Scheduler、Channel/Die/Plane Arbitration 与 Read Priority](flash-scheduler-arbitration.md)。机器可读策略矩阵见 [Flash Scheduler Policy Matrix](../../tests/requirements/flash-scheduler-policy-matrix.yml)。

## 稳态测试

SSD 刚开始写通常处于 fresh-out-of-box 状态，性能过于乐观。应测试 steady state：

1. 全盘顺序预填充。
2. 用目标 workload 随机写到性能收敛。
3. 记录 p50/p99/p999/p9999、WAF、free block、GC 活动。
4. 改变 OP、QD、读写比例、block size、hotset size。
5. 比较 fresh、steady、SLC cache full、thermal throttled 状态。

## 关键指标

- IOPS / bandwidth。
- Average latency。
- p99/p999/p9999。
- WAF。
- GC duty cycle。
- Free block watermark。
- Read retry rate。
- ECC correction count distribution。
- Thermal throttling time。
- Queue occupancy。
- Channel/die utilization。

## 设计陷阱

- 只优化平均延迟，忽略 p999。
- 把 GC write 算进 host write，误判 WAF。
- 只测空盘，不测 steady state。
- 忽略 flush/FUA 对写延迟的影响。
- DRAM-less/HMB 场景没有测 mapping cache miss。
- 温度模型和功耗模型缺失，性能目标不可量产。

## 关键来源

- MQSim: https://github.com/CMU-SAFARI/MQSim
- MQSim FAST'18: https://www.usenix.org/conference/fast18/presentation/tavakkol
- SimpleSSD: https://github.com/SimpleSSD/SimpleSSD
- fio: https://github.com/axboe/fio
- SPDK NVMe Driver: https://spdk.io/doc/nvme.html
- JEDEC JESD219: https://www.jedec.org/standards-documents/docs/jesd219a
