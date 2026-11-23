---
type: Concept
title: 通用 I/O 控制命令（Common I/O Control Commands）
description: 这些命令和普通 Read/Write 一样走 I/O 队列，但主要解决控制问题：取消已取走的命令、把易失缓存中的写入提交到非易失介质，或交换
  I/O 命令集的管理数据。它们只能在控制器就绪且 I/O 队列已创建后提交。 [PDF pp. 482-486](../_source/pages/page-482.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 通用 I/O 控制命令（Common I/O Control Commands）

这些命令和普通 Read/Write 一样走 I/O 队列，但主要解决控制问题：取消已取走的命令、把易失缓存中的写入提交到非易失介质，或交换 I/O 命令集的管理数据。它们只能在控制器就绪且 I/O 队列已创建后提交。 [PDF pp. 482-486](../_source/pages/page-482.md)

## 先看三种最常见的控制动作

```text
I/O 提交队列
|-- Cancel ----------------> 已取走的匹配命令 -> 立即/延迟中止
|-- Flush -----------------> 已完成写入 -> 非易失介质持久化屏障
`-- I/O Management Receive -> 控制器管理状态 -> 主机缓冲区
```

图把不同效果放在同一 I/O 执行平面中。 [PDF pp. 482-486](../_source/pages/page-482.md)

## Cancel：取消一批同队列命令

Cancel 只能选择与它提交在同一 I/O SQ 的命令。单命令模式按 CID 加一个 NSID 或全部 NSID 选择；多命令模式要求 `CID=FFFFh`，选择该 SQ 上指定 NSID 或全部 NSID 的所有其他命令。编码 SQID 必须等于提交 Cancel 的 SQ。 [PDF pp. 482-484](../_source/pages/page-482.md)

**案例：**应用撤销某个大批量 I/O 时，驱动在同一 SQ 上发多命令 Cancel。但 Cancel 只覆盖处理时已经被控制器取走的匹配命令；还没取走的命令可不受影响。因此仍需逐条查看目标命令自己的 CQE。 [PDF pp. 483-485](../_source/pages/page-483.md)

| Cancel CQE 字段 | 代表什么 |
|---|---|
| `CMDA` | 此次 Cancel 已立即中止的命令数 |
| `CEDA` | 可能以后被延迟中止的匹配命令数，至 `FFFFh` 饱和 |

Cancel 的 CQE 不能证明延迟中止最终发生；`CMDA=0` 或多命令取消时，主机尤其需要看每条目标命令的 CQE 是否报告 Command Abort Requested。 [PDF pp. 484-485](../_source/pages/page-484.md)

## Flush：建立“之前写入已经落盘”的边界

Flush 把提交前已经完成的写命令的数据和 metadata 从 volatile write cache 提交到非易失介质；控制器也可以顺便提交更多命名空间数据。广播 NSID 行为取决于 Identify Controller 的 `FB`，FDP 命名空间还可用 `VWCNP` 独立报告没有易失缓存。 [PDF p. 485](../_source/pages/page-485.md)

**案例：**数据库写入日志后在提交事务前发 Flush。Flush 成功后，提交前已完成的相关写入跨越了持久化边界；它不是“从此所有未来写入自动落盘”。没有启用/不存在 volatile cache 时，Flush 没有效果但通常仍成功。 [PDF p. 485](../_source/pages/page-485.md)

## I/O Management Receive：读取 I/O 命令集的管理状态

该命令选择操作和从零开始编码的 dword 长度，可读取结果前缀，但不会传输超过已定义结构的内容。Base 定义的 Reclaim Unit Handle Status 为每个可访问的 Placement Handle/Reclaim Group 关系返回一个由 I/O Command Set 定义的描述符。 [PDF pp. 486-487](../_source/pages/page-486.md)

状态按描述符逐个采样，可能不反映未完成命令的影响。该操作要求指定一个具体命名空间，且其 Endurance Group 已启用 FDP；读取超过结果结构的部分返回零。 [PDF pp. 486-487](../_source/pages/page-486.md)

## I/O Management Send：更新 Reclaim Unit Handle

Base 定义的 Reclaim Unit Handle Update 接收从零开始编码的 Placement Identifier 数量，并把每个 handle 重新指向一个空 Reclaim Unit。已有用户数据的 unit 必须被替换；已经为空的 unit 也可被替换。 [PDF pp. 487-489](../_source/pages/page-487.md)

数量同时受 `MAXPIDS` 和 `NRG * NRUH` 限制，每个 Placement Identifier 都必须指向有效 Reclaim Group 和 Placement Handle。失败不具原子性：前面的 ID 可能已更新，后面的失败；并发写入使用这些 ID 时，数据可能落到处理前或命令完成时所指的 unit。 [PDF pp. 488-489](../_source/pages/page-488.md)

## 规范依据

- [通用 I/O 操作码与 Cancel，PDF 第 482-485 页](../_source/pages/page-482.md)
- [Flush 持久化边界，PDF 第 485 页](../_source/pages/page-485.md)
- [I/O Management Receive，PDF 第 486-487 页](../_source/pages/page-486.md)
- [I/O Management Send，PDF 第 487-489 页](../_source/pages/page-487.md)
