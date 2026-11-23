---
type: Concept
title: 命名空间访问模型（Namespace Access Models）
description: 命名空间的分配、控制器挂接、子系统范围和某条命令选中的 NSID 是不同维度。要判断“谁能访问这块存储”，不能只看一个 NSID。 [PDF
  pp. 30, 33-35](../_source/pages/page-030.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 命名空间访问模型（Namespace Access Models）

命名空间的分配、控制器挂接、子系统范围和某条命令选中的 NSID 是不同维度。要判断“谁能访问这块存储”，不能只看一个 NSID。 [PDF pp. 30, 33-35](../_source/pages/page-030.md)

## 三种访问形态与两个容易混淆的概念

```text
私有 namespace    --> 同一时刻至多挂接一个 controller
共享 namespace    --> 一个子系统内并发挂接到两个或更多 controller
分散 namespace    --> 两个或更多参与子系统中的 controller 可并发访问

一台 host -- 多条独立路径 --> 同一 namespace = 多路径 I/O
多台 host -- 不同 controller --> 同一 namespace = namespace 共享
```

多路径描述“一台 host 怎么到达”，共享描述“多台 host 是否共同访问”，它们是两条不同轴。两者都需要子系统中至少有两个 controller；多 host 并发的顺序协调由 host 软件或应用负责，Base Specification 不提供协调协议。 [PDF pp. 54-56](../_source/pages/page-054.md)

## 一个双端口共享盘案例

数据库集群的两台服务器分别通过 controller A 和 B 访问同一共享 namespace。两台控制器上该 namespace 的 NSID 必须相同，Identify Namespace 返回相同的数据；应用仍要借助 Reservation 或集群协议协调并发写入，而不能期待 NVMe 自动跨 controller 排序。 [PDF pp. 55-56](../_source/pages/page-055.md)

## 关键术语边界

| 术语 | 规则 |
|---|---|
| Private namespace | 同时最多一个 attached controller |
| Shared namespace | 一个子系统内至少两个并发 controller attachment |
| Dispersed namespace | 至少两个参与子系统中的 controller 并发访问 |
| Specified namespace | 当前命令 SQE.NSID 选中的 namespace |
| NSID | controller 用来提供 namespace 访问的标识，也就是 SQE 中的选择字段 |

共享 namespace 对所有可访问 controller 使用相同 NSID 和相同 Identify Namespace 数据，但软件仍应以全局唯一 namespace identity 识别多路径，而不只靠 NSID。 [PDF pp. 33, 55-56](../_source/pages/page-033.md)

```text
Controller A -- NSID 2 --+
                          +--> 同一共享 namespace（全局 ID G）
Controller B -- NSID 2 --+
```

该映射根据 Figures 20-21 整理。 [PDF pp. 55-56](../_source/pages/page-055.md)

## Port reset 和 ANA

独立 port 让 reset 隔离在该 port 的 controller，不会重置另一 controller、共享 namespace 或另一 controller 上的操作。SR-IOV 也可实现类似模型：每个 PF/VF 代表一个 controller，共享一个 namespace。 [PDF pp. 56-57](../_source/pages/page-056.md)

某些子系统会因内部布局或所选 controller 不同而显示不对称访问特征，并通过 ANA Reporting 说明每条 controller 路径的状态。 [PDF p. 57](../_source/pages/page-057.md)

## ANA：同一 namespace 在不同路径上未必状态相同

```text
                 内部/路径重配置
[Optimized] <----------------------> [Non-Optimized]
     |                                      |
     +--------------> [Change] <-----------+
                            |
                            v
                     [Inaccessible] -- 恢复 --> 可访问状态
                            |
                            `--> [Persistent Loss]（终态）
```

ANA 描述的是一个 controller 与一个 ANA Group 的关系，不是 namespace 的全局属性。每个支持 ANA 的 controller 上、已挂接的 namespace 属于一个有效 ANA Group；同组 namespace 共享状态转换且必须在同一 Domain。分散 namespace 在每个参与子系统都有 ANA Group，但 group ID 不必相同。 [PDF pp. 497-502](../_source/pages/page-497.md)

| ANA 状态 | 主机应理解为 |
|---|---|
| Optimized | 所有支持操作以优化方式访问 |
| Non-Optimized | 所有支持操作仍可做，但可能较慢/效率较低 |
| Inaccessible | 用户数据暂不可访问，未来可能恢复 |
| Persistent Loss | 此 controller/group 关系永久不可访问，不会再转换 |
| Change | 转换进行中，多数命令以 Asymmetric Access Transition 中止 |

Inaccessible/Persistent Loss 时 Identify 可能清空 namespace 容量字段；应改用 Optimized/Non-Optimized 路径。Inaccessible 或 Change 时，主机可选择另一可访问路径，或至少按 `ANATT` 等待后重试。 [PDF pp. 500-502](../_source/pages/page-500.md)

## ANA 日志怎样读

```text
ANA log header：全局 change count
 `-- 按升序 AGID 的 ANA Group 描述符
      |-- 组内 change count
      |-- 该 controller 上的一个 ANA state
      `-- 已挂接 NSID（RGO=1 时可省略）
```

日志仅列出处理 Get Log Page 的 controller 上有已挂接 namespace 的 group。描述符变长，支持索引 offset 时应使用：0 是头部，1 是第一个描述符。分段读取后重读头部，只有全局 change count 未变才接受快照。 [PDF pp. 250-252](../_source/pages/page-250.md)

## 通知与管理命令

启用时，controller 在 ANA Group ID 改变、转换失败或进入各 ANA 状态后报告 ANA Change Notice，因 namespace attachment 进入状态除外。ANA 不会一律禁用所有 Admin 命令，但 Get/Set Features、Get Log Page 和 Identify 有明确例外，例如容量可能为零、保存 Feature 可能禁止，或广播 Set Features 因任一 namespace 状态不佳而失败。 [PDF pp. 502-503](../_source/pages/page-502.md)

## 规范依据

- [命名空间、NSID、私有/共享/分散访问，PDF 第 30-35、54-57 页](../_source/pages/page-030.md)
- [ANA log，PDF 第 250-252 页](../_source/pages/page-250.md)
- [ANA Group、状态与命令影响，PDF 第 497-503 页](../_source/pages/page-497.md)
