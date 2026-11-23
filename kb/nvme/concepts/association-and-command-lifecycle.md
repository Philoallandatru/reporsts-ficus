---
type: Concept
title: 关联与命令生命周期（Association and Command Lifecycle）
description: 关联（association）是一个 host 与一个 controller 之间的独占通信关系。它包括该控制器的一对管理队列和全部 I/O
  队列；命令则在其中经历提交、可处理、执行和完成。 [PDF pp. 28-29](../_source/pages/page-028.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 关联与命令生命周期（Association and Command Lifecycle）

关联（association）是一个 host 与一个 controller 之间的独占通信关系。它包括该控制器的一对管理队列和全部 I/O 队列；命令则在其中经历提交、可处理、执行和完成。 [PDF pp. 28-29](../_source/pages/page-028.md)

## 把关联当作“一个专属会话”

```text
主机 H
`-- 与控制器 C 的唯一关联
    |-- 管理队列对（ID 0）
    `-- 一条或多条 I/O 队列对

命令：提交 --> 传输并就绪 --> 可处理 --> 执行 --> CQE 发布 --> 完成
```

该图是解释性生命周期。完成不只是控制器做完内部工作，还要求状态已写入并且 CQE 已发布到关联的完成队列。 [PDF pp. 28-29](../_source/pages/page-028.md)

## Fabrics 中怎样建立关联

```text
传输连接已存在
       |
Admin Queue Connect 成功
       v
关联建立（一个主机 <-> 一个控制器）
       |
同一身份再 Connect I/O Queue
       v
可以建立 I/O 队列
```

后续 I/O Queue Connect 必须与管理关联匹配：subsystem port、传输类型/地址、Host NQN、Subsystem NQN、Controller ID 和兼容的 Host Identifier 都不能随意改变。 [PDF pp. 58, 473-477](../_source/pages/page-058.md)

## 一个多路径案例

主机先成功连接管理队列，再尝试创建 I/O 队列。如果第二次 Connect 使用了不同的 Host NQN 或错误的 controller ID，它不是“另一条普通路径”，而会被身份/序列规则拒绝，或被路由到不同子系统。 [PDF p. 474](../_source/pages/page-474.md)

## 关联会在何时结束

| 情况 | 结果 |
|---|---|
| shutdown、Controller Level Reset、管理连接丢失 | 关联结束 |
| 单条 I/O 队列 Disconnect，且两端支持独立删除 | 只删除该队列对 |
| I/O 连接丢失但不支持独立删除 | 关联结束 |

NVMe 没有“直接结束关联”的专门命令；Disconnect 的对象是 I/O 队列。通信丢失时不得盲目重新提交仍可能正在处理的命令。 [PDF pp. 58-59, 115-117](../_source/pages/page-058.md)

## 动态与静态控制器的分配

动态分配通过 Fabrics Connect 中 `CNTLID=FFFFh` 请求。静态子系统可接受特定 controller ID 或 `FFFEh` 请求任一可用控制器，但会拒绝 `FFFFh`。成功分配不会返回 `FFF0h` 到 `FFFFh` 的保留哨兵值。 [PDF pp. 59, 473-474](../_source/pages/page-473.md)

## 重试前必须问的问题

只有幂等命令在没有中间命令时重发，才会得到相同的子系统最终状态和结果。这个“没有中间命令”的条件是定义的一部分；通信丢失后尤其不能省略。 [PDF p. 31](../_source/pages/page-031.md)

## 规范依据

- [关联、命令候选与完成定义，PDF 第 28-29 页](../_source/pages/page-028.md)
- [幂等命令定义，PDF 第 31 页](../_source/pages/page-031.md)
- [Fabrics 关联与终止条件，PDF 第 58-59 页](../_source/pages/page-058.md)
- [Connect 身份校验、认证与 I/O 队列删除，PDF 第 114-117、473-477 页](../_source/pages/page-114.md)
