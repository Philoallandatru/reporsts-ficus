---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 292e90d44e387c491b1156c1b98a4a6e514669b7a754bd3ce6e4b03b63257e89
  pageDirectory: concepts
  sources:
    - nvme-queue-pair.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - fabrics队列生命周期
  citations:
    - file: nvme-queue-pair.md
      start: 31
      end: 34
    - file: nvme-queue-pair.md
      start: 147
      end: 164
    - file: nvme-queue-pair.md
      start: 166
      end: 171
    - file: nvme-queue-pair.md
      start: 51
      end: 58
    - file: nvme-queue-pair.md
      start: 176
      end: 179
    - file: nvme-queue-pair.md
      start: 180
      end: 184
    - file: nvme-queue-pair.md
      start: 188
      end: 191
    - file: nvme-queue-pair.md
      start: 192
      end: 195
    - file: nvme-queue-pair.md
      start: 199
      end: 204
    - file: nvme-queue-pair.md
      start: 205
      end: 209
    - file: nvme-queue-pair.md
      start: 233
      end: 238
    - file: nvme-queue-pair.md
      start: 240
      end: 244
    - file: nvme-queue-pair.md
      start: 249
      end: 256
    - file: nvme-queue-pair.md
      start: 258
      end: 262
    - file: nvme-queue-pair.md
      start: 216
      end: 221
    - file: nvme-queue-pair.md
      start: 224
      end: 227
title: Fabrics队列生命周期
description: 基于消息的队列通过Connect/Disconnect命令创建和删除，需协商流量控制，支持认证隔离删除
tags:
  - nvme
  - fabrics
  - 队列管理
timestamp: "2026-08-16T06:25:08.439Z"
---


# Fabrics 队列生命周期

Fabrics（NVMe over Fabrics）采用基于消息的传输模型，其队列生命周期与基于内存的 PCIe 模型有显著区别。在 Fabrics 模式下，每个 I/O 提交队列必须与一个 I/O 完成队列一对一映射，不支持多对一的 I/O 队列映射，这与基于内存的传输模型不同。^[nvme-queue-pair.md:31-34]

## 队列创建流程

Fabrics 队列的创建通过 Connect 命令完成，流程如下：

```text
[传输连接已建立]
       |
    发送 Connect 命令到正在创建的队列
       v
[队列对已创建] -- 需要认证？ --> [仅限认证命令]
       |                              |
       | 无需认证                      | 认证成功
       `---------------+---------------'
                       v
         管理队列：CC.EN=0 时仅 Fabrics 命令
         管理队列：RDY=1 时 Fabrics + 管理命令
         I/O 队列：控制器启用时的 I/O 命令
                       |
         在该 I/O 提交队列上发送 Disconnect（最后一条命令）
                       v
         [最终 Disconnect 响应] → [队列已删除]
```

^[nvme-queue-pair.md:147-164]

Connect 命令具有以下关键特性：
- 在预先建立的传输连接上仅发送一次
- 仅在成功时创建提交队列和完成队列
- 重复的队列 ID 会导致"命令序列错误"
- 不使用内存模型中的 `AQA`、`ASQ`、`ACQ` 或创建/删除 I/O 队列的管理命令 ^[nvme-queue-pair.md:166-171]

### 与基于内存模型的对比

| 事件 | 基于内存的模型 | 基于消息的模型 |
|---|---|---|
| **命令提交** | 写入尾部门铃寄存器，推进到已占用的提交队列槽位之后 | 主机向提交队列添加一个命令胶囊（capsule） |
| **提交完成通知** | 主机可以立即修改槽位，或等待完成队列条目（通过阶段标签翻转检测） | 传输层投递胶囊并接收对应的响应胶囊；不在提交队列中写入状态翻转 |
| **流量控制** | 通过尾部/头部门铃寄存器驱动；Fabrics 模式下不存在完成队列流量控制 | 不使用内存门铃，由传输层的胶囊投递和容量预留驱动；提交队列流量控制可通过协商禁用 |
| **完成关联** | 完成队列条目包含提交队列标识符 + 命令标识符；阶段标签翻转表示新发布 | 相同——关联仍由提交队列ID/命令ID对承担，阶段标签不适用 |

^[nvme-queue-pair.md:51-58]

## 队列删除的隔离性

**单独 I/O 队列删除**仅当两端都公布支持时才是隔离的；否则，删除一条 I/O 队列或丢失其传输连接会终止整个关联。 ^[nvme-queue-pair.md:176-179]

**Disconnect 命令的特性：**
- 成功的 Disconnect 是该提交队列上最后被处理的命令
- 其响应是该队列对上被消费的最后一个完成队列条目
- 此前的命令可以完成或中止，但不能在该完成发布之后再被处理 ^[nvme-queue-pair.md:180-184]

## 流量控制协商

Connect 命令为每个队列对协商提交队列流量控制。^[nvme-queue-pair.md:188-191]

| 状态 | 说明 |
|---|---|
| **启用** | 默认状态，后续响应胶囊携带有效的提交队列头部进度 |
| **禁用** | 仅当主机设置 `DISSQFC=1` 且控制器返回 `SQHD=FFFFh` 时才禁用 |

^[nvme-queue-pair.md:192-195]

## 容量管理规则

| 容量规则 | 必需行为 |
|---|---|
| **提交队列流量控制启用** | 控制器通过 `SQHD` 报告已消费槽位；满意味着头部在尾部之后一位，因此可用容量为大小减一 |
| **提交队列流量控制禁用** | 主机保持未完成命令数低于提交队列大小；连接后 `SQHD` 为零/保留 |
| **完成队列容量** | 无完成队列头/尾流量控制；主机必须为所有可能的未完成响应预留尺寸 |

^[nvme-queue-pair.md:199-204]

### 致命错误条件

- 提交到满的提交队列时，控制器停止命令处理，设置 `CSTS.CFS`，终止传输连接并结束关联
- 禁用流量控制时，未完成命令数达到或超过提交队列大小也会导致同样的致命结果
- 完成队列过小时，响应到达满的完成队列会导致未定义结果 ^[nvme-queue-pair.md:205-209]

## 传输层保证

```text
普通胶囊：传输层可以重排已可靠交付的胶囊
融合对：  第一条 → 第二条，同一提交队列中没有胶囊插入其间
携带 SQHD 的完成条目：更新 1 → 更新 2 → 更新 3（按顺序交付）
传输失败：删除受影响的 I/O 队列/连接，或结束关联
```

^[nvme-queue-pair.md:233-238]

**关键要点：**
- 传输层可以通过命令状态和错误信息日志上报已检测到的错误
- 不可恢复的丢失必须导致队列/连接删除或关联终止
- 在控制器提交之后、主机投递之前修改响应胶囊属于未定义行为 ^[nvme-queue-pair.md:240-244]

## [队列级别重置](/concepts/队列级别重置.md)

当需要对 Fabrics 队列进行重置时，流程如下：

```text
静止受影响的提交队列
        |
Fabrics：断开 I/O [[队列对|队列对]] → 用非零队列 ID 再次连接
        |
        └─→ 队列属性可以改变
```

^[nvme-queue-pair.md:249-256]

**重要说明：**
- 队列级别重置是删除后重建，不是单独的线上操作
- 主机应先让受影响队列静止，因为删除会中止待处理命令，而这些中止可能产生完成队列条目，也可能不产生 ^[nvme-queue-pair.md:258-262]

## 队列属性

| 属性 | 约定 |
|---|---|
| **大小** | 16 位从零开始的槽位计数；最少两个槽位 |
| **I/O 队列标识符** | `1` 到 `65535`；管理队列使用标识符 `0` |
| **优先级** | 紧急、高、中、低优先级仅在加权轮询加紧急优先级模式下有效 |

^[nvme-queue-pair.md:216-221]

**队列大小限制：**
- I/O 队列最多可包含 65,536 个槽位，受 `CAP.MQES` 约束
- 基于消息的管理提交队列进一步受发现日志页条目 `ASQSZ` 限制 ^[nvme-queue-pair.md:224-227]

## 相关概念

[队列对](/concepts/队列对.md) - 队列对由提交队列和完成队列组成的基本概念

[NVMe over Fabrics](/concepts/nvme-over-fabrics.md) - Fabrics 传输的完整规范

Connect 命令 - 用于建立 Fabrics 队列连接的命令

Disconnect 命令 - 用于删除 Fabrics 队列的命令

流量控制 - Fabrics 队列中的提交队列流量控制机制

## Sources

- [nvme-queue-pair.md - 队列对（Queue Pair）](nvme-queue-pair.md)

# Citations

1. [nvme-queue-pair.md:31-34](/references/nvme-queue-pair-300af9df.md)
2. [nvme-queue-pair.md:147-164](/references/nvme-queue-pair-300af9df.md)
3. [nvme-queue-pair.md:166-171](/references/nvme-queue-pair-300af9df.md)
4. [nvme-queue-pair.md:51-58](/references/nvme-queue-pair-300af9df.md)
5. [nvme-queue-pair.md:176-179](/references/nvme-queue-pair-300af9df.md)
6. [nvme-queue-pair.md:180-184](/references/nvme-queue-pair-300af9df.md)
7. [nvme-queue-pair.md:188-191](/references/nvme-queue-pair-300af9df.md)
8. [nvme-queue-pair.md:192-195](/references/nvme-queue-pair-300af9df.md)
9. [nvme-queue-pair.md:199-204](/references/nvme-queue-pair-300af9df.md)
10. [nvme-queue-pair.md:205-209](/references/nvme-queue-pair-300af9df.md)
11. [nvme-queue-pair.md:233-238](/references/nvme-queue-pair-300af9df.md)
12. [nvme-queue-pair.md:240-244](/references/nvme-queue-pair-300af9df.md)
13. [nvme-queue-pair.md:249-256](/references/nvme-queue-pair-300af9df.md)
14. [nvme-queue-pair.md:258-262](/references/nvme-queue-pair-300af9df.md)
15. [nvme-queue-pair.md:216-221](/references/nvme-queue-pair-300af9df.md)
16. [nvme-queue-pair.md:224-227](/references/nvme-queue-pair-300af9df.md)
