---
type: Concept
title: NVM 容量模型（NVM Capacity Model）
description: NVMe 容量模型把“主机可用的逻辑容量”与“底层 Media Unit 如何组织”分开描述。设备可选择在子系统、Domain、Endurance
  Group、NVM Set、格式化命名空间和 Media Unit 各层报告容量。 [PDF pp. 141-142](../_source/pages/page-141.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# NVM 容量模型（NVM Capacity Model）

NVMe 容量模型把“主机可用的逻辑容量”与“底层 Media Unit 如何组织”分开描述。设备可选择在子系统、Domain、Endurance Group、NVM Set、格式化命名空间和 Media Unit 各层报告容量。 [PDF pp. 141-142](../_source/pages/page-141.md)

## 容量归属和数据通道是两条不同的线

```text
NVM 子系统容量
`-- Domain
    `-- Endurance Group（每个 MU 只属于一个）
        `-- NVM Set（支持时每个 MU 只属于一个）
            |-- 格式化 Namespace（完整落在一个 NVM Set 内）
            `-- 未分配容量

Channel(s) <------ 数据传输连接 ------> Media Unit(s)
```

上半部分回答“容量分给谁”，下半部分回答“数据可经哪些 Channel 到达 MU”；它们不是同一层级关系。 [PDF pp. 141-143](../_source/pages/page-141.md)

## 一个容量规划案例

管理员先从某个 Endurance Group 创建 NVM Set，再在这个 Set 中创建数据库命名空间。该命名空间的容量全部来自这个 NVM Set；即使没有分完 Set 的容量，未分配部分仍留在 Set 内，等待以后创建其他命名空间。 [PDF pp. 141-142](../_source/pages/page-141.md)

## 分配必须遵守的归属

| 来源 | 可分配给 | 必须保持的归属 |
|---|---|---|
| Domain 容量 | 一个或多个 Endurance Group | 每个 Endurance Group 只在一个 Domain 内 |
| Endurance Group 容量 | 一个或多个 NVM Set | 每个 NVM Set 只在一个 Endurance Group 内 |
| NVM Set 容量 | 一个或多个格式化命名空间 | 每个命名空间只在一个 NVM Set 内 |
| Media Unit | Endurance Group；支持 NVM Set 时还属于一个 NVM Set | 在每个已支持层级只有一个父对象 |

任何层级都不必分配完。Capacity Management 分配 Endurance Group/NVM Set/MU，Namespace Management 分配格式化命名空间容量。不支持 NVM Set 时 `NVMSETID` 全为零；不支持 Endurance Group 时 `ENDGID` 全为零。 [PDF p. 142](../_source/pages/page-142.md)

## 组织方式如何影响性能与隔离

```text
最大聚合带宽示例：
一个 Endurance Group / 一个 NVM Set
 |-- Channel 0 -> MU MU MU MU
 |-- Channel 1 -> MU MU MU MU
 |-- Channel 2 -> MU MU MU MU
 `-- Channel 3 -> MU MU MU MU

单次操作可利用全部 Channel 上的 MU
```

该图是经本地渲染核对的 Figure 86 教学性重绘。 [PDF pp. 142-143](../_source/pages/page-142.md)

| 组织方式 | 取舍 |
|---|---|
| Simple（Figure 86） | 一个组/Set 跨四条 Channel，追求最大聚合带宽 |
| Vertical（Figure 87） | 每条 Channel 的 MU 自成一组/Set，形成四个隔离集合，但每个受单 Channel 带宽限制 |
| Horizontal dual-NAND（Figure 88） | 每条 Channel 贡献 SLC 与 QLC MU 到不同集合，让较小 SLC 和较大 QLC 集合都跨所有 Channel |

Figure 88 的约 400/100 Capacity Adjustment Factor 只是示例配置，不是 SLC/QLC 的通用比例。 [PDF pp. 143-145](../_source/pages/page-143.md)

## 创建/删除时该看哪层的可用容量

| 正在管理的对象 | 主机用于判断和更新容量的层级 |
|---|---|
| Endurance Group（无 Domain） | NVM 子系统容量字段 |
| Endurance Group（有 Domain） | Domain Attributes Entry |
| NVM Set | Endurance Group Information log |
| 格式化 namespace（无 Endurance Group/Domain） | NVM 子系统 |
| 格式化 namespace（仅 Domain） | Domain Attributes Entry |
| 格式化 namespace（Endurance Group、无 NVM Set） | Endurance Group Information log |
| 格式化 namespace（有 NVM Set） | NVM Set Attributes Entry |

这张表是 Figure 89 的学习用压缩：控制器在创建/删除后更新相应层级的已分配/未分配账目。支持 NVM Set 必然支持 Endurance Group。 [PDF pp. 145-146](../_source/pages/page-145.md)

## 运行时如何观察底层 MU

```text
按 Domain 选择的 Media Unit Status log
`-- 按升序 MUID 的 MU 描述符
    |-- Domain -> Endurance Group -> NVM Set 归属
    |-- capacity adjustment、spare、percentage used
    `-- 升序且无重复的 Channel ID 列表
```

该日志报告所选 Domain 可访问的 MU、可访问 Channel 数和当前容量配置。多 Domain 时 ID 仅在 Domain 内有作用域；选择零表示处理控制器自己的 Domain。 [PDF pp. 276-278](../_source/pages/page-276.md)

未选容量配置时，描述符清空 Endurance Group、NVM Set、capacity adjustment 和 Channel count；spare/percentage used 是 MU 本地测量，与 Endurance Group 指标的关系未规定。 [PDF pp. 277-278](../_source/pages/page-277.md)

## 支持的容量配置清单

```text
Supported Capacity Configuration List
`-- 按升序唯一 CCID 的配置
    `-- 按升序唯一 ENDGID 的 Endurance Group 描述符
        |-- 容量、spare、调整系数、耐久性估计
        |-- 升序唯一 NVM Set ID
        `-- 按升序唯一 CHID 的 Channel
            `-- 按升序唯一 MUID 的 Media Unit
```

各嵌套描述符为可变长度。Endurance Group 描述符报告总/备用字节容量和以十亿字节为单位、向上取整的寿命估计；零表示未报告，全一饱和值表示“该值及以上”。 [PDF pp. 278-281](../_source/pages/page-278.md)

## 规范依据

- [容量层级、归属和 Channel/MU，PDF 第 141-146 页](../_source/pages/page-141.md)
- [Media Unit Status log，PDF 第 276-278 页](../_source/pages/page-276.md)
- [Supported Capacity Configuration 清单，PDF 第 278-281 页](../_source/pages/page-278.md)
