---
type: Concept
title: 控制器内存窗口（Controller Memory Windows）
description: NVMe 可选提供两类与控制器关联的内存：CMB（Controller Memory Buffer）主要用于低延迟的队列、列表或数据放置；PMR（Persistent
  Memory Region）则额外承诺持久性、就绪状态和健康状态。 [PDF pp. 86-94](../_source/pages/page-086.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 控制器内存窗口（Controller Memory Windows）

NVMe 可选提供两类与控制器关联的内存：CMB（Controller Memory Buffer）主要用于低延迟的队列、列表或数据放置；PMR（Persistent Memory Region）则额外承诺持久性、就绪状态和健康状态。 [PDF pp. 86-94](../_source/pages/page-086.md)

## CMB：控制器旁边的一小块工作台

```text
选定的 PCI BAR
+---------------------------------------------------+
| BAR 基址 + CMBLOC.OFST * CMBSZ.SizeUnit           |
|   `-- CMB：可放队列 / PRP-SGL 列表 / 命令数据     |
+---------------------------------------------------+
```

图为地址模型的解释性重述。可用大小是 `CMBSZ.SZ * SizeUnit`，但如果偏移加大小超出选定 BAR，会被 BAR 边界截断；BAR 地址按 4 KiB 对齐。 [PDF pp. 86-89](../_source/pages/page-086.md)

## CMB 不是“有了就能放任何东西”

| 想放入 CMB 的对象 | 必须查看的能力位 |
|---|---|
| 提交/完成队列 | `CMBSZ.SQS`、`CMBSZ.CQS` |
| PRP 或 SGL 列表 | `CMBSZ.LISTS` |
| 主机到控制器 / 控制器到主机数据 | `CMBSZ.WDS`、`CMBSZ.RDS` |
| 非连续或混合内存队列 | `CMBLOC.CQPDS`、`CMBLOC.CQMMS` |

能力位为零表示相应放置限制仍有效。不能只因设备“有 CMB”就假设队列和数据都能放进去。 [PDF pp. 86-88](../_source/pages/page-086.md)

**案例：**驱动想把 I/O 队列放进 CMB 来减少访问延迟，必须先确认控制器允许 SQ/CQ 放置，并确认连续性、对齐与混合内存条件；否则仍应在主机内存创建队列。 [PDF pp. 86-88](../_source/pages/page-086.md)

## PMR：可以持久化的工作区

```text
[PMR 禁用 / NRDY=1]
          | PMRCTL.EN=1
          v
[等待 PMRCAP.PMRTO * PMRTU]
          | PMRSTS.NRDY=0
          v
[PMR 可读写] -- 读取屏障或 PMRSTS --> [之前写入已持久化]
```

这张流程图是解释性示意。PMR 只有在 `PMRCTL.EN=1` 且 `PMRSTS.NRDY=0` 时才就绪；时间单位为 500 ms 或分钟，并且至少支持一种写入屏障方式。 [PDF pp. 92-94](../_source/pages/page-092.md)

## 一个需要保证落盘的案例

主机向 PMR 写入日志或元数据后，不能只凭“写请求已送出”就认为数据持久。它必须使用所报告的屏障机制（内存读取完成和/或读取 `PMRSTS` 完成）来建立此前写入已持久化的顺序点。 [PDF pp. 92-94](../_source/pages/page-092.md)

## PMR 健康状态

| `PMRSTS.HSTS` | 主机应理解为 |
|---|---|
| `000b` | 正常运行 |
| `001b` | 已持久且可运行，但恢复结果可能不正确 |
| `010b` | 只读 |
| `011b` | 不可靠，数据或持久性可能无效 |

非零 `PMRSTS.ERR` 表示此前发生过写错误，并一直保留到 PCI Function reset。 [PDF p. 94](../_source/pages/page-094.md)

## CMB 与 PMR 的选择

| 关注点 | CMB | PMR |
|---|---|---|
| 主要目的 | 控制器附近的低延迟工作内存 | 可管理持久性的控制器内存 |
| 是否在此处承诺持久化 | 否 | 是，需按屏障与健康规则判断 |
| 典型对象 | 队列、列表、命令数据 | 支持能力允许的读写数据 |
| 关键状态 | 地址/能力位与 `CBAI` | `EN`、`NRDY`、`HSTS`、`ERR` |

`CBAI=1` 表示配置的 controller-address base 无效。PMR 的 controller-address 范围还不能溢出 64 位地址空间或与已启用 CMB 范围重叠。 [PDF pp. 89-96](../_source/pages/page-089.md)

## 规范依据

- [CMB 位置、容量与放置能力，PDF 第 86-91 页](../_source/pages/page-086.md)
- [PMR 能力、控制、状态与持久化屏障，PDF 第 92-94 页](../_source/pages/page-092.md)
- [PMR 地址与吞吐报告，PDF 第 95-96 页](../_source/pages/page-095.md)
