---
type: Concept
title: 错误信息与健康日志（Error and Health Logs）
description: NVMe 用两类日志回答不同问题：错误信息日志保存“刚才哪件事出错了”的近期历史；SMART/Health 日志则像体检报告，反映设备寿命、温度、掉电和介质健康的长期状态。
  [PDF pp. 229-230](../_source/pages/page-229.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 错误信息与健康日志（Error and Health Logs）

NVMe 用两类日志回答不同问题：错误信息日志保存“刚才哪件事出错了”的近期历史；SMART/Health 日志则像体检报告，反映设备寿命、温度、掉电和介质健康的长期状态。 [PDF pp. 229-230](../_source/pages/page-229.md)

## 先分清“事故记录”和“健康档案”

```text
命令错误 / 异步错误                         控制器与介质状态
          |                                        |
          v                                        v
 +------------------+                    +------------------+
 | Error Information|                    | SMART / Health   |
 | 最近错误在前      |                    | 当前告警+累计计数 |
 | 每条 64 字节      |                    |                  |
 +--------+---------+                    +--------+---------+
          \-------------- Get Log Page ------------/
```

图是解释性比较，不是编号 Figure 的重绘。 [PDF pp. 229-231](../_source/pages/page-229.md)

## 一个排障案例

应用收到非成功 CQE，且 `M=1`。驱动应随后读取 Error Information log，使用其中的 SQID、CID、状态和相关字段，把扩展错误信息对应回原命令；若控制器先通过 AER 报告错误，流程也是先收事件、再读日志。 [PDF p. 229](../_source/pages/page-229.md)

## 错误信息日志怎么读

日志按最近优先返回 64 字节记录，数量由 `ELPE` 定义。空间满时，控制器应写入新记录并丢弃最旧记录。 [PDF p. 229](../_source/pages/page-229.md)

```text
错误信息条目（64 字节，教学性简化）
+--------+------+------+------+-----+------+-----+-----+--------+
| ECNT   | SQID | CID  | STS  | PEL | NSID | CSI | OPC | 细节   |
+--------+------+------+------+-----+------+-----+-----+--------+
  错误编号   命令关联    状态/错误位置       命令与命名空间上下文
```

布局根据已渲染核对的 Figure 205 作了简化，省略保留字节和专用细节。`SQID=CID=FFFFh` 且 `PEL=FFFFh` 表示该错误不属于某条具体命令。 [PDF pp. 229-230](../_source/pages/page-229.md)

| 字段组 | 初学者理解 |
|---|---|
| `ECNT` | 从 1 开始的持久唯一错误编号；0 表示无效或缺失槽位 |
| `SQID`、`CID` | 找回触发错误的命令；无关联命令时为 `FFFFh` |
| `STS`、`PEL` | 保存完成状态和适用时最靠后的错误字节/位位置 |
| NSID 与命令细节 | 提供命名空间、命令集、操作码、传输或厂商日志上下文 |

Controller Level Reset 或掉电循环后，控制器应删除日志条目，但 `ECNT` 自身跨掉电保留。 [PDF pp. 229-230](../_source/pages/page-229.md)

## SMART / Health：看趋势，不只看一次告警

| 信号 | 正确理解 |
|---|---|
| Critical Warning | 备用空间、温度、可靠性、只读、易失备份或 PMR 状态的当前位图 |
| Composite Temperature | 控制器与关联命名空间的实现定义 Kelvin 值，不一定对应一个物理传感器 |
| Available Spare / Threshold | 剩余备用空间及其 AER 告警阈值 |
| Percentage Used | 厂商估算的寿命消耗；100 表示预计耐久度用尽，不必然等于立即故障 |

SMART 数据通常跨掉电保留。`NSID=0h` 或 `FFFFFFFFh` 请求控制器数据；Revision 2.1 对控制器范围和命名空间请求定义相同内容。 [PDF pp. 230-231](../_source/pages/page-230.md)

## 这些累计数字各自代表什么

```text
瞬时状态                         累计历史
告警位、温度、备用空间  ------>  数据量、命令数、忙碌时间
寿命百分比                       掉电次数、通电小时、不安全关机
                                 介质错误与过温时间
```

该图区分“此刻测到什么”和“长期发生过什么”。 [PDF pp. 231-234](../_source/pages/page-231.md)

| 计数族 | 含义 |
|---|---|
| Data Units Read/Written | 千个 512 字节单位计数，向上取整；不含 metadata |
| Host Read/Write Commands | 主机请求且完成的读/写命令数量 |
| Controller Busy Time | 控制器处理 I/O 命令时累计的分钟数 |
| 电源历史 | 上电次数、通电小时、不安全关机 |
| 错误/热历史 | 介质完整性错误、错误日志数量、阈值以上分钟数与传感器数据 |

不支持的温度传感器返回零。Critical Warning 表示处理 Get Log Page 时的状态，可能不同于先前 AER 到达时的状态。 [PDF pp. 231-234](../_source/pages/page-231.md)

## 容易踩坑的地方

- `ECNT=0` 不是第一个错误，而是无效/缺失条目。
- 命名空间形式的 SMART 请求不意味着字段变成该命名空间专属数据。
- `Percentage Used >100` 可合法存在，直到在 255 饱和；不要把 100 当成设备已不可用。 [PDF pp. 229-231](../_source/pages/page-229.md)

## 规范依据

- [错误历史与 Figure 205，PDF 第 229-230 页](../_source/pages/page-229.md)
- [SMART 范围、告警与字段，PDF 第 230-231 页](../_source/pages/page-230.md)
- [SMART 累计计数、掉电/错误历史和热传感器，PDF 第 232-234 页](../_source/pages/page-232.md)
