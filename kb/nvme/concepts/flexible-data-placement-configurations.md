---
type: Concept
title: 灵活数据放置配置（Flexible Data Placement，FDP）
description: FDP 让 host 不只“写到一个 namespace”，还可通过 Placement Handle 提示控制器把数据放进哪个 Reclaim
  Unit 资源组。FDP Configurations log 是一个 Endurance Group 范围的目录，列出当前可以应用的静态放置配置。 [PDF
  pp. 294-295](../_source/...
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 灵活数据放置配置（Flexible Data Placement，FDP）

FDP 让 host 不只“写到一个 namespace”，还可通过 Placement Handle 提示控制器把数据放进哪个 Reclaim Unit 资源组。FDP Configurations log 是一个 Endurance Group 范围的目录，列出当前可以应用的静态放置配置。 [PDF pp. 294-295](../_source/pages/page-294.md)

## 把它当作“给不同数据挑不同回收仓位”

```text
选定 ENDGID 的 Endurance Group
`-- FDP 配置（现在可用吗？）
    |-- Reclaim Group 数量 + Placement Identifier 划分
    |-- Reclaim Unit Handle 数量与有序类型
    |-- namespace / placement 上限
    `-- 标称 RU 大小 + 预计 handle 重新指向时间
```

图总结 Figures 279-281，并已对照本地渲染页 294-295。 [PDF pp. 294-295](../_source/pages/page-294.md)

## 一个冷热数据分离案例

数据库把短寿命日志写入一个 Placement Handle，把长期索引写入另一个。FDP 配置可让它们在同一 Reclaim Group 内先放到不同 Reclaim Unit，帮助控制回收和写放大；但“Initially Isolated”不是永久物理隔离，控制器后续垃圾回收仍可能把同类型 handle 的数据合并。 [PDF p. 295](../_source/pages/page-295.md)

若需要更强保证，应选择 `Persistently Isolated`：即使控制器内部搬迁，数据仍与同一 Reclaim Unit Handle 关联。 [PDF p. 296](../_source/pages/page-296.md)

## 配置目录中最重要的限制

| 字段/限制 | 初学者解释 |
|---|---|
| `NUMFDPC` | 从零开始编码的配置描述符数量 |
| `FDPCV=0` | 该条目当前不可用，host 应忽略 |
| `NRG`、`NRUH` | Reclaim Group 和每组 handle 数，都非零 |
| `RGIF` | 多个 Reclaim Group 时非零；决定 Placement Identifier 的高位如何变成 RGID |
| `MAXPIDS` | 从零开始编码的最大 Placement Identifier 数，且小于 `NRG * NRUH` |
| `NNS` | namespace 上限；有 `MNAN` 时受其限制，否则受 `NN` 限制 |
| Handle 列表 | 按 Reclaim Unit Handle Identifier 有序 |

创建 Endurance Group 或在其中启用 FDP 都可能改变目录条目的可用性。描述符可变长，但用 vendor size 和零填充保持下一项 8 字节对齐。 [PDF pp. 294-295](../_source/pages/page-294.md)

`FDPVWC=1` 表示该配置带 volatile write cache，并强制 Identify Controller `VWCP=1`，包括兼容不知道 FDP 的旧 host 的情形。每个 Reclaim Unit 使用同一标称 RU 大小；`ERUTL` 限制一个 handle 指向 unit 多久后 controller 可重定向，零表示未报告估计。 [PDF pp. 294-295](../_source/pages/page-294.md)

## 启用后要观察什么

FDP Feature（`1Dh`）是 mandatory-save 更新：它为 Endurance Group 选择一个有效配置索引并启用/禁用 FDP。配置变化可能影响 Identify 报告的 User Data Format，所以 host 应重新读取相关 Identify 视图。 [PDF p. 412](../_source/pages/page-412.md)

```text
静态配置                           运行时视图
NRG + NRUH + RGIF --------+------> RU Handle Usage（LID 21h）
                         +------> FDP Statistics（LID 22h）
每个 RUH 的事件掩码 ----+------> FDP Events（LID 23h）
                                      |-- host 事件
                                      `-- controller 事件
```

这是配置目录与三个 Endurance Group 范围运行日志的关系图。 [PDF pp. 296-299](../_source/pages/page-296.md)

| 运行视图 | 稳定规则 |
|---|---|
| RU Handle Usage | 每个配置 handle 一个描述符：未使用、host 显式选择，或唯一的 controller 选择；至多一个为 controller 选择 |
| FDP Statistics | 128 位饱和的 host-written/media-written/media-erased 字节计数；FDP Feature 改变会清零，固件更新不会 |
| FDP Events | 固定 4 KiB、最旧在前的历史；只有影响的 handle 启用该事件时才记录 |

启用 FDP 后，这些日志保留 command `NSID` 并在 FDP 禁用时以 FDP Disabled 失败。统计覆盖自上次启用 FDP 后该 Endurance Group 内曾存在的所有 namespace。 [PDF pp. 296-298](../_source/pages/page-296.md)

## 事件为什么不能只按时间戳排序

事件历史满时，新启用事件会丢弃最旧项；FDP 从禁用转为启用时事件计数复位。事件按发生顺序排列，不一定按 timestamp 值排列，因为 Timestamp 配置可跨 Controller Level Reset 改变。 [PDF pp. 298-299](../_source/pages/page-298.md)

每个事件分别标记 Placement Identifier、NSID、Reclaim Group/RU Handle 位置是否有效。host 事件包括提前 retarget、超时、reset 引发 retarget、无效放置；controller 事件包括介质重分配和隐式 retarget。 [PDF pp. 299-301](../_source/pages/page-299.md)

## 规范依据

- [FDP 配置目录与限制，PDF 第 294-296 页](../_source/pages/page-294.md)
- [Usage、Statistics 与 Events 日志，PDF 第 296-299 页](../_source/pages/page-296.md)
- [FDP 事件类型和有效性字段，PDF 第 299-301 页](../_source/pages/page-299.md)
- [FDP Feature，PDF 第 412 页](../_source/pages/page-412.md)
