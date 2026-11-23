---
type: Concept
title: 管理命令模型（Admin Command Model）
description: 管理命令集是控制器的“运维通道”。命令从管理提交队列进入，用来识别设备、读日志、设置 Feature、管理命名空间和固件；它和用户读写所在的
  I/O 队列分工不同。 [PDF pp. 191-192](../_source/pages/page-191.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 管理命令模型（Admin Command Model）

管理命令集是控制器的“运维通道”。命令从管理提交队列进入，用来识别设备、读日志、设置 Feature、管理命名空间和固件；它和用户读写所在的 I/O 队列分工不同。 [PDF pp. 191-192](../_source/pages/page-191.md)

## 先看管理队列里会出现什么

```text
管理提交队列
|-- 所有传输共用：Identify、Features、日志、固件、命名空间…
|-- 仅内存型传输：创建/删除 I/O 队列、Doorbell Buffer、虚拟化
`-- 仅消息型传输：发现、分区、导出资源管理
        |
        `-- opcode 选择操作；DTD 表示数据方向
```

图根据 Figure 141 作了学习用归纳。Fabrics 命令共同使用 `7Fh` 操作码，并在自己的命令格式中区分具体操作；未列出的管理操作码保留。 [PDF pp. 191-192](../_source/pages/page-191.md)

## 一个驱动初始化案例

驱动先在管理队列发 Identify，确认控制器能力；接着用 Get Features/Set Features 读取或配置策略，再创建 I/O 队列供业务读写。即使 I/O 完成队列暂时拥塞，管理处理也不应因此被阻塞，例如 Delete I/O Submission Queue 不应被满 I/O CQ 卡住。 [PDF p. 191](../_source/pages/page-191.md)

## 读命令表时要看的四件事

| 项目 | 规则 |
|---|---|
| 操作码 | 由 6 位功能和 2 位数据传输方向组成 |
| 未使用 NSID | 主机写 `0h` |
| 使用 NSID | 一般可使用 `FFFFFFFFh`，但命令自身规则可收窄 |
| 厂商范围 | 组合操作码 `C0h..FFh` |

通用、内存型专用和消息型专用命令分别在规范 5.1、5.2、5.3 中定义。只使用内存型传输的子系统中，导出资源管理命令被禁止。 [PDF pp. 191-192](../_source/pages/page-191.md)

## Format 或 Sanitize 正在运行时

```text
普通管理命令
  |-- 命名空间正在 Format，且不在允许名单 --> 可能中止：Format In Progress
  `-- Sanitize 正在运行，且不在允许名单 --> 禁止或受命令特定限制

Format NVM 请求
  `-- 有冲突的非允许管理工作 --> 可能中止：Command Sequence Error
```

图是 Figure 142 的教学性概括。允许名单保留 Abort、AER、部分队列操作、指定日志、Identify、Keep Alive 与部分 Fabrics 操作，但每项仍受表中的额外条件约束。厂商命令仅可在既不影响也不读取用户数据时使用。 [PDF pp. 192-193](../_source/pages/page-192.md)

## 容易混淆的地方

- 操作码已分配，不等于当前控制器类型必须支持它；还要看支持矩阵。
- 管理队列不是更慢的 I/O 队列，而是控制与维护通道。
- Format/Sanitize 期间不是“所有管理命令都禁止”，而是按精确允许名单收窄。 [PDF pp. 65-67, 191-193](../_source/pages/page-065.md)

## 规范依据

- [管理操作码矩阵，PDF 第 191-192 页](../_source/pages/page-191.md)
- [Format/Sanitize 管理命令允许名单，PDF 第 192-193 页](../_source/pages/page-192.md)
