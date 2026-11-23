---
type: Concept
title: DRAM-less SSD 与 Host Memory Buffer
description: DRAM-less SSD 通过减少外部 DRAM 降低成本、功耗和封装复杂度，但代价是 FTL mapping、write buffer、read
  cache、GC buffer 和 telemetry buffer 都要重新设计。Host Memory Buffer 是一种把部分主机内存借给 NVMe controller
  使用的机制，但 HMB...
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# DRAM-less SSD 与 Host Memory Buffer

DRAM-less SSD 通过减少外部 DRAM 降低成本、功耗和封装复杂度，但代价是 FTL mapping、write buffer、read cache、GC buffer 和 telemetry buffer 都要重新设计。Host Memory Buffer 是一种把部分主机内存借给 NVMe controller 使用的机制，但 HMB 不是掉电后的可靠来源，也不应被当作安全边界内的可信持久存储。

## 设计目标

- 在没有外部 DRAM 的情况下控制 mapping cache miss、translation page read 和尾延迟。
- 明确 HMB 中哪些内容可缓存、可丢弃、可重建，哪些内容绝不能只存在 HMB。
- 在 reset、controller disable、host memory revoke、power loss 后可恢复。
- 避免 HMB DMA、地址失效、IOMMU、安全隔离和主机内存污染导致数据错误。
- 将 HMB hit/miss、mapping read、dirty eviction、fallback-to-SRAM/NAND 行为纳入 telemetry。

## HMB 可放什么

| 数据 | 是否适合 HMB | 原因 | 持久化要求 |
|---|---|---|---|
| Clean L2P mapping cache | 高 | 可从 translation page 或 checkpoint 重建 | 不需要持久化 |
| Dirty mapping delta | 低 | 掉电/重置丢失会破坏最新映射 | 必须先 journal/checkpoint |
| Translation page cache | 高 | 可重读 flash | 需要版本校验 |
| Read cache | 中 | 可提升热点读 | 不能作为唯一数据来源 |
| Write buffer | 低 | host-completed write 不能只在 HMB | 需要 PLP 或 NAND 持久证据 |
| GC scratch buffer | 中 | 可降低 SRAM 压力 | reset 后丢弃并重启 GC |
| Telemetry staging | 中 | 批量日志可暂存 | persistent event 必须落盘 |
| Secret/key material | 低 | 主机内存不可作为设备安全边界 | 不应放 HMB |

原则：HMB 里所有关键状态都必须能从 NAND metadata、journal、checkpoint 或重新扫描中恢复。

## 初始化与生命周期

| 阶段 | 内部动作 | 风险 |
|---|---|---|
| Capability advertise | Identify / feature 中声明 HMB 能力和大小约束 | 过度承诺导致 host 分配不足 |
| Host enable | host 提供 memory descriptors | 地址无效、对齐/大小错误 |
| Validation | PRP/SGL/DMA/IOMMU 检查 | 越界 DMA、安全隔离 |
| Warmup | 预取 translation pages 或建立 cache index | 启动延迟 |
| Runtime | HMB hit/miss、eviction、prefetch | miss storm、dirty eviction |
| Reset / disable | 停止使用 HMB，清理 DMA state | outstanding DMA 写坏主机内存 |
| Re-enable | 重新验证 descriptors，重建 cache | stale descriptor |
| Power loss | HMB 内容全部视为丢失 | 必须从持久元数据恢复 |

## 与 DFTL 的关系

HMB 最适合和 demand-based mapping 组合：

- SRAM 保存 global translation directory、hot locks、small emergency cache。
- HMB 保存 clean translation pages 和 hot L2P entries。
- NAND 保存 authoritative translation pages、journal 和 checkpoint。
- cache miss 时先查 SRAM，再查 HMB，最后读 NAND translation page。

危险点：

- HMB 中 cached mapping 的 version 低于 NAND translation page。
- host reset 后 HMB 内容可能还在物理内存里，但设备不能信任它。
- HMB dirty entry 未落盘就返回 flush/FUA 成功。
- mapping cache miss storm 和 foreground read 争抢 NAND channel。

## QoS 与性能

HMB 主要影响：

- mapping cache hit rate。
- translation page read latency。
- random read p99/p999。
- random write dirty mapping eviction。
- GC relocation 查 P2L/L2P 的开销。
- controller SRAM pressure。

需要区分三种延迟：

1. HMB hit：host memory DMA latency。
2. HMB miss but translation page cached in SRAM。
3. HMB/SRAM miss，需要读 NAND translation page。

如果 HMB miss 发生在高 QD 随机读或 GC 活动期间，尾延迟会被明显放大。

## 安全与隔离

HMB 设计必须防御：

- Host 提供无效或恶意 memory descriptors。
- IOMMU remap 或 memory revoke 后 controller 继续 DMA。
- 多 namespace / tenant 场景下缓存泄漏。
- HMB 中旧数据被新 host 或新 VM 观察。
- 设备把 HMB 当作可信配置来源。

建议：

- 每次 enable 都重新验证 descriptor。
- HMB cache line 带 generation 和 checksum。
- HMB 只缓存可重建数据。
- namespace/tenant context 参与 cache tag。
- reset/disable 后停止所有 HMB DMA，并丢弃 HMB cache state。

## 掉电与恢复

掉电恢复时：

1. 不加载或信任 HMB 内容。
2. 从 superblock/checkpoint/journal 重建 authoritative mapping。
3. 清空 HMB cache generation。
4. host 重新 enable HMB 后再 warmup。
5. 对比 HMB disabled/enabled 的 telemetry，确认恢复路径不依赖 HMB。

与 [掉电恢复状态表](../../tests/faults/power-loss-state-table.yml) 的关系：HMB 只能降低运行时 miss cost，不能改变 PLP-WIN 中的持久证据要求。

## 验证点

- HMB disabled 与 enabled 的随机读/写 p99/p999 对比。
- HMB descriptor 无效、大小不足、alignment 错误时返回正确状态。
- Controller reset / FLR / disable-enable 后 HMB cache 不被错误复用。
- HMB revoke 或 DMA fault 时 fallback 到 SRAM/NAND，不产生错误数据。
- dirty mapping 不只存在 HMB；flush/FUA 后掉电可恢复。
- HMB miss storm 与 GC 活动叠加时 foreground read 不饥饿。
- namespace/tenant 切换后 HMB cache tag 不泄漏数据。

## 关键来源

- NVM Express Specifications: https://nvmexpress.org/specifications/
- [DFTL / Demand-based Mapping](ftl-dftl-demand-based-mapping.md)
- [控制器硬件模块边界](controller-hardware-module-boundaries.md)
- [性能、QoS 与写放大](performance-qos-write-amplification.md)
- [掉电保护与恢复](power-loss-recovery.md)
