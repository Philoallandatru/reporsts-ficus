---
type: Concept
title: Fabrics 发现与认证（Fabrics Discovery and Authentication）
description: NVMe over Fabrics 先解决“哪些子系统路径可访问”，再解决“已连接 controller 是否允许命令流量”。Discovery
  Service 只暴露 Discovery controller，并告诉 host 可用的 NVM 子系统与路径；它不替代正常 I/O controller。
  [PDF p. 45](../_source/p...
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Fabrics 发现与认证（Fabrics Discovery and Authentication）

NVMe over Fabrics 先解决“哪些子系统路径可访问”，再解决“已连接 controller 是否允许命令流量”。Discovery Service 只暴露 Discovery controller，并告诉 host 可用的 NVM 子系统与路径；它不替代正常 I/O controller。 [PDF p. 45](../_source/pages/page-045.md)

## 从找到设备到开始 I/O

```text
实现定义的启动信息
        |
        v
[Discovery Service]
        |
        +--> 可访问的 subsystem path + 安全要求
        |
        v
Connect 到 controller
        |
        +-- secure channel? 先建立，才允许任何命令
        `-- in-band auth? 新队列上仅允许认证命令
        |
        v
正常 Admin / I/O 命令流量
```

一个 NVM 子系统可要求 secure channel、NVMe 带内认证或两者都要求。 [PDF pp. 45-46](../_source/pages/page-045.md)

## 一个初次连接案例

host 从操作系统配置或其他实现定义方式获知 Discovery Service。它读取 Discovery Log，选出同一 subsystem 的两个不同 Port ID 路径以获得端口故障独立性，再对选定路径 Connect。若 Connect 响应要求认证，新建队列在认证完成前只能发 Authentication Send/Receive，不能先抢跑 Read 或 Identify。 [PDF pp. 45-46, 63, 477-478](../_source/pages/page-045.md)

## Discovery controller 是什么，不是什么

Discovery controller 永远是消息型且动态分配。它只实现发现相关 Feature：没有 I/O Queue、I/O command 或 namespace。若 Discovery subsystem 宣告唯一的 Discovery Service NQN，Connect 必须同时接受该 NQN 与 well-known NQN；否则接受 well-known NQN。 [PDF pp. 58, 62](../_source/pages/page-058.md)

## 两道安全门

| 门 | 信号 | 限制 |
|---|---|---|
| Fabric secure channel | Discovery Service 表示必需 | channel 建立前 controller 不接受 Fabrics/Admin/I/O 命令 |
| NVMe 带内认证 | Connect 响应表示必需 | Connect 创建的队列上，认证成功前仅接受认证命令 |

Authentication Send 把 security-protocol 命令或参数交给 controller；Authentication Receive 取回与此前 Send 关联的协议状态/数据。所选 SPC-5 security protocol 定义 payload 和关联，NVMe 只提供 FCTYPE、SGL、protocol selector 和传输长度。保留 protocol 值以 Invalid Parameter 失败。 [PDF pp. 471-473](../_source/pages/page-471.md)

认证接收数据在通信丢失或 Controller Level Reset 后失效。两条认证命令都可走 Admin 或 I/O Queue；Connect 失败使用 Connect 专用状态/参数位置，而不是 Invalid Field 或 Error Information Log。 [PDF pp. 471-473, 477-478](../_source/pages/page-471.md)

## Discovery Log 如何选路径

```text
Discovery Log
|-- subsystem X，Port A ---- 独立端口故障域 A
|-- subsystem X，Port B ---- 独立端口故障域 B
`-- referral -------------> 另一个 Discovery Service

一个 association：选择一个适用 entry
多个 association：优先不同 Port ID，以提高路径独立性
```

entry 不要求排序；同一 subsystem 的多条 entry 可能是多条 fabric path，也可能是共享一条 path 的多个 static controller。不同 Port ID 表示对端口硬件故障独立的 transport connection。 [PDF p. 63](../_source/pages/page-063.md)

Discovery Log（`LID 70h`）只存在于 Discovery controller，且跨 reset 保留。它可返回请求 host 的过滤子集、port-local 记录，或在支持/请求时不按 `HOSTNQN` 过滤的全部注册 subsystem port；仅 Direct Discovery Controller 可支持 port-local-only。 [PDF pp. 306-308](../_source/pages/page-306.md)

```text
能力                 请求位                  返回标志
EXTDLPES ---------> EXTDLPE -------------> EXTEND
PLEOS（仅 DDC） ---> PLEO ----------------> PORTLCL
ALLSUBES ---------> ALLSUBE -------------> ALLSUB
```

[PDF pp. 306-308](../_source/pages/page-306.md)

## 多次读取 Discovery Log 时必须校验快照

```text
按递增 offset 读 header + entries
              |
              v
        重读 Generation Counter
          /                    \
      未变化                   已变化
        |                        |
    接受数据                丢弃并重读
```

单命令读取是原子的。多命令读取应使用上述 generation 协议；内容变化时 controller 也可返回 Discover Restart。支持 index offset 时，0 指向 header，1 从 Entry 0 开始。 [PDF p. 307](../_source/pages/page-307.md)

## Entry 中最重要的语义

| 信号 | 含义 |
|---|---|
| `SUBTYPE=01h` | referral 到另一 Discovery Service |
| `SUBTYPE=02h` | 可暴露 namespace 的 NVM subsystem |
| `SUBTYPE=03h` | 当前 Discovery Service 的另一访问路径 |
| `DUPRETINFO=1` | 当前 service entry 返回重复发现信息，一条路径可代表该组 |

固定 1,024 字节 entry 载有 transport/address family、subsystem type、安全要求、Port ID、Controller ID、最大 Admin SQ、NQN 和 transport address。动态模型使用 `CNTLID=FFFFh`；静态模型可给具体 ID，或以 `FFFEh` 请求分配并保存返回 ID 供重连。扩展 entry 在该固定头后以总长度和 attribute count 框住可变属性列表。 [PDF pp. 307-311](../_source/pages/page-307.md)

## Discovery Information Management：管理发现记录

```text
实体头（Host / DDC / CDC）
      |
      +-- Register：1..N 条；同 key 替换，新 key 新增
      +-- De-register：1..N 个 entry key
      `-- Update：恰好 2 条；第一条找旧 key，第二条原子替换
```

Host/CDC 提交 host extended entry；DDC 提交 basic 或 extended NVM-subsystem entry，且只有 DDC 可标记 port-local。entry key 对 host 必须基于 transport address；对 subsystem 可基于 port ID。 [PDF pp. 449-453](../_source/pages/page-449.md)

| 任务 | 条目数量 | 效果 |
|---|---:|---|
| Register | 一个或更多 | 同 key 替换或新建记录 |
| De-register | 一个或更多 | 删除匹配记录 |
| Update | 恰好两个 | 原子替换旧记录 |

注册容量不足会使整个 Register 失败。extended host entry 至少含一个 Host Identifier attribute；subsystem entry 可没有。`TRADDR` 首字节为空时选连接对端 IP，此类注册/注销每条命令限一个 entry。 [PDF pp. 450-456](../_source/pages/page-450.md)

## 发现平面的其他库存

```text
Discovery controller
|-- LID 70h：subsystem path / referral
|-- LID 71h：已注册 host
|-- LID 72h：Authentication Verification Entity（AVE）
`-- LID 73h：pull-model DDC 对 CDC 的请求
```

Host Discovery entry 是可变长结构，含 Host NQN、transport address 和至少一个 Host Identifier attribute；多命令读取使用与 Discovery Log 相同的 generation 验证。AVE Discovery entry 则列出 AVE NQN 与可选 TCP transport record。 [PDF pp. 312-317](../_source/pages/page-312.md)

显式持久 Discovery connection 通过非零 Keep Alive Timer 请求；这要求 controller 支持 Keep Alive、AER 和 Discovery Log change notification。Discovery controller 永远不支持 Disconnect。 [PDF pp. 63-65](../_source/pages/page-063.md)

## ID 哨兵与变更通知

| Controller ID | 发现/Connect 中的含义 |
|---|---|
| `FFF0h`-`FFFCh` | 保留，Connect 无效 |
| `FFFDh` | 分散 namespace 的 controller 在另一参与子系统；Connect 无效 |
| `FFFEh` | 分配任一可用 static controller |
| `FFFFh` | 分配任一可用 dynamic controller |

静态分配得到 `FFFEh` 后，host 应记住真实返回 ID 并用于以后 association。Discovery/Host Discovery log 变化可通过 Notice AER 上报：LID `70h` + `F0h` 表示 Discovery 变化，LID `71h` + `F1h` 表示 Host Discovery 变化。 [PDF pp. 64-65](../_source/pages/page-064.md)

## Pull 模式下 CDC 推送日志

```text
pull-model DDC 向 CDC 请求日志
         |
CDC -- SDLP（status、LID、offset、dword count、data） --> DDC
         |
         `-- CQE.LPUR=1：注册一次重发；下一条 SDLP 后消耗
```

Send Discovery Log Page 传输与 Get Log Page 相同的内容，只允许 Discovery（`70h`）、Host Discovery（`71h`）和 AVE Discovery（`72h`）；其他 LID 无数据并返回 Not Allowed。若要持续收到更新，DDC 必须在每次 CDC 发出 SDLP 后重新注册。 [PDF pp. 469-470](../_source/pages/page-469.md)

## 规范依据

- [Discovery Service 与安全门，PDF 第 45-46 页](../_source/pages/page-045.md)
- [Discovery controller、路径与通知，PDF 第 58-65 页](../_source/pages/page-058.md)
- [Discovery Log 与扩展 entry，PDF 第 306-311 页](../_source/pages/page-306.md)
- [Host/AVE/pull-model 发现日志，PDF 第 312-317 页](../_source/pages/page-312.md)
- [Discovery Information Management，PDF 第 449-456 页](../_source/pages/page-449.md)
- [SDLP、Authentication Send/Receive、Connect 认证，PDF 第 469-478 页](../_source/pages/page-469.md)
