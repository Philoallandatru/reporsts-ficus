---
type: Concept
title: 命名空间 Reservation 生命周期（Namespace Reservation Lifecycle）
description: Reservation 让多个 host 协调对同一命名空间的访问。host 用自己持有的 64 位 key 注册身份；其中一个注册者可成为
  reservation holder，并按 reservation type 决定谁能读写。 [PDF pp. 489-495](../_source/pages/page-489.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 命名空间 Reservation 生命周期（Namespace Reservation Lifecycle）

Reservation 让多个 host 协调对同一命名空间的访问。host 用自己持有的 64 位 key 注册身份；其中一个注册者可成为 reservation holder，并按 reservation type 决定谁能读写。 [PDF pp. 489-495](../_source/pages/page-489.md)

## 把它当作带钥匙的共享会议室

```text
[未注册]
    | Register key
    v
[注册者] -- Acquire(type) --> [Reservation Holder]
    |              |                  |
    | 换 key       | Preempt          | Release
    | 注销         | Preempt+Abort    v
    v              v             [注册者]
[未注册]      竞争 key 被移除
                       |
                     Clear -> Reservation 与全部注册清空
```

状态图归纳 Register、Acquire、Preempt、Release 与 Clear。key 属于 host，Reservation 则属于 namespace。 [PDF pp. 489-493](../_source/pages/page-489.md)

## 一个双主机故障切换案例

主机 A 与 B 都注册到共享 namespace，A Acquire 成为 holder。A 故障时，B 用 Preempt 取代 A 的 key；若还要尽快清理 A 的未完成 I/O，则使用 Preempt and Abort。B 不应仅看自己的 Preempt CQE 就假定所有 A 的命令都立刻停止，仍需按目标命令的最终完成语义处理。 [PDF pp. 489-493](../_source/pages/page-489.md)

## 注册与掉电保留

Reservation Register 可注册、注销或替换提交 host 的 key。`IEKEY` 在适用操作中允许跳过当前 key 校验；同一命令也可保持、清除或设置 PTPL。Feature 可保存时，这个副作用同时更新当前和保存值。 [PDF pp. 490-492](../_source/pages/page-490.md)

```text
PTPL=0 -- 掉电 --> Reservation 释放，注册者清空
PTPL=1 -- 掉电 --> Reservation 与注册者保留
```

[PDF pp. 491, 494-495](../_source/pages/page-491.md)

## Acquire、Preempt、Release、Clear 的差别

| 操作 | 效果 |
|---|---|
| Acquire | 以一种 reservation type 取得/变更 reservation，校验当前 key |
| Preempt | 指定并注销竞争 key，同时取得/变更 Reservation |
| Preempt and Abort | Preempt 外加请求中止该 namespace 的未完成命令 |
| Release | 释放当前 Reservation，但保留注册信息；类型必须匹配 |
| Clear | 同时清除 Reservation 和全部注册状态 |

Acquire 有六种 type：write-exclusive 或 exclusive-access，再按 holder、仅 registrant 或所有 registrant 的访问范围区分。Acquire、Release、Clear 中 `IEKEY=1` 无效。 [PDF pp. 489-493](../_source/pages/page-489.md)

## 分散命名空间的额外握手

host 启用 Host Dispersed Namespace Support 后，每条 Reservation 命令用 `DISNSRS` 表明能理解跨参与者 controller 的哨兵 `FFFDh`。在 dispersed namespace 上清除该位会以 Namespace Is Dispersed 失败。 [PDF pp. 490-494](../_source/pages/page-490.md)

## Reservation Report 怎样读

Report 是一个带回绕 generation 的快照，包含 reservation type、注册者数量、PTPL 状态与每个 registrant 的记录。host 选择的 64 位或 128 位 Host Identifier 宽度必须与 basic/extended report 格式匹配。 [PDF pp. 493-495](../_source/pages/page-493.md)

| 内容 | 说明 |
|---|---|
| generation | 注册变更、Clear、Preempt/Preempt-and-Abort 成功后递增 |
| `CNTLID=FFFFh` | 该注册者在本子系统无 controller association |
| `CNTLID=FFFDh` | dispersed namespace 中，controller 位于其他参与子系统 |
| basic record | 24 字节，64 位 Host Identifier |
| extended record | 64 字节，128 位 Host Identifier |

两种记录都会说明 controller association、该 host 是否持有 Reservation 以及其 key。 [PDF pp. 494-496](../_source/pages/page-494.md)

## 规范依据

- [Acquire、key、分散支持和 reservation type，PDF 第 489-490 页](../_source/pages/page-489.md)
- [Register、PTPL、Release 与 Clear，PDF 第 490-493 页](../_source/pages/page-490.md)
- [Reservation Report 与 registrant 记录，PDF 第 493-496 页](../_source/pages/page-493.md)
