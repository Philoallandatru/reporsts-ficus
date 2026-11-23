---
type: Concept
title: 控制器数据队列（Controller Data Queues，CDQ）
description: CDQ 是位于主机内存、由控制器向其中投递某类数据的队列。主机通过 Controller Data Queue 管理命令创建或删除它；Base
  定义的一种队列类型是 User Data Migration Queue。 [PDF pp. 206-210](../_source/pages/page-206.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 控制器数据队列（Controller Data Queues，CDQ）

CDQ 是位于主机内存、由控制器向其中投递某类数据的队列。主机通过 Controller Data Queue 管理命令创建或删除它；Base 定义的一种队列类型是 User Data Migration Queue。 [PDF pp. 206-210](../_source/pages/page-206.md)

## 把它当作控制器写给主机的“专用收件箱”

```text
主机分配内存页
  |-- 连续：PRP1 -> 一个缓冲区
  `-- 非连续：PRP1 -> 稳定的 PRP List -> 多个页
          |
          v
创建 CDQ（类型、大小、目标控制器）
          |
控制器 ------ 将该类型的数据投递到 CDQ ------> 主机读取
          |
删除 CDQ 或控制器重置后，主机才可释放/修改映射
```

CDQ 使用的 PRP List 在删除或 reset 前必须始终位于同一主机内存位置且内容不变；提前修改属于未定义行为。 [PDF pp. 207-209](../_source/pages/page-207.md)

## 一个迁移场景

控制器迁移期间，系统要记录目标控制器修改过的用户数据。主机先为该控制器创建 User Data Migration Queue；控制器随后把迁移所需的数据条目投递进去，主机读取后再进行迁移或同步。 [PDF p. 209](../_source/pages/page-209.md)

## 创建 CDQ 时要填什么

| 输入 | 含义 |
|---|---|
| `SEL=0h` | 创建；`SEL=1h` 删除；`C0h..FFh` 为厂商操作 |
| `PRP1` | 页对齐的主机内存缓冲区或 PRP List，偏移为零 |
| `PC` | 指明连续缓冲区还是 PRP List |
| `CDQSIZE` | 队列大小，以 dword 计，必须是该队列类型条目大小的倍数 |
| `QT` | 队列数据类型；Base 的 `0h` 是 User Data Migration Queue |

CDQ 必须放在主机内存，不能放在 CMB 或 PMR。每命令/子系统内存范围、每控制器/子系统队列数量都会限制创建。 [PDF pp. 207-208](../_source/pages/page-207.md)

## UDMQ 的绑定和删除

同一个目标控制器最多关联一个 User Data Migration Queue；队列数量耗尽时返回 Not Enough Resources。创建成功后 CQE 返回在处理控制器范围内唯一的 `CDQID`；删除不存在的 ID 会返回 Invalid Controller Data Queue。 [PDF pp. 209-210](../_source/pages/page-209.md)

```text
Create UDMQ(CNTLID) --> CQE.CDQID（仅在处理控制器内唯一）
                              |
Delete CDQ(CDQID) ------------+
```

## 主机怎样消费队列

Controller Data Queue Feature（`21h`）推进主机拥有的 head pointer，也可设置一次性 tail-slot 触发器。Set 成功会清除待处理 tail 事件；触发后使能位自行清零。由于旧 trigger 槽位可能在重新配置完成前被投递，主机应在完成后检查队列，再重新 arm 或禁用。 [PDF pp. 415-416](../_source/pages/page-415.md)

一次性 AER 可报告 CDQ tail 投递或队列已满，并携带 `CDQID`。 [PDF p. 202](../_source/pages/page-202.md)

## 规范依据

- [CDQ 创建、内存约束与布局，PDF 第 207-208 页](../_source/pages/page-207.md)
- [UDMQ、删除与完成 ID，PDF 第 209-210 页](../_source/pages/page-209.md)
- [CDQ Feature 与 head/tail 触发，PDF 第 415-416 页](../_source/pages/page-415.md)
