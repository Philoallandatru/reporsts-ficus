---
type: Concept
title: Domain 与分裂（Domains and Divisions）
description: Domain 是 NVM 子系统中最小、不能再拆分的协作单元。它共享电源状态、容量信息等状态；多 Domain 子系统中，Domain 之间既是通信边界，也是故障与管理边界。
  [PDF pp. 104-105](../_source/pages/page-104.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Domain 与分裂（Domains and Divisions）

Domain 是 NVM 子系统中最小、不能再拆分的协作单元。它共享电源状态、容量信息等状态；多 Domain 子系统中，Domain 之间既是通信边界，也是故障与管理边界。 [PDF pp. 104-105](../_source/pages/page-104.md)

## 把 Domain 想成同一园区内的独立楼宇

```text
一个 NVM 子系统
+----------------------+   +----------------------+
| Domain 1             |   | Domain 2             |
| 控制器、存储资源…    |<->| 控制器、存储资源…    |
+----------------------+   +----------------------+
       正常通信               通信中断 = division
```

这是根据 Figures 71-72 的解释性示意。一个 Domain 可以有控制器、存储、两者都有或都没有；命名空间仍可能跨 Domain 共享。 [PDF pp. 105-106](../_source/pages/page-105.md)

## 一个机箱局部故障案例

双机箱存储有两个 Domain。两机箱之间的链路断开后，各自仍可能继续运行，但对方的控制器状态、容量和 Reservation 状态可能变成不完整信息。此时发生的是 division，不应把它简单当作“单条主机路径故障”。 [PDF pp. 104, 106-107](../_source/pages/page-104.md)

## 必须满足的表示规则

| 情况 | 控制器和数据应如何报告 |
|---|---|
| 支持多个 Domain | 所有控制器设置 `CTRATT.MDS`；controller 与受支持 Endurance Group 的 Domain ID 非零 |
| 单 Domain 子系统 | Domain ID 字段为零 |
| Domain ID | 仅在同一 NVM 子系统内唯一 |
| 多 Domain | 必须支持 ANA Reporting |

[PDF pp. 104-105](../_source/pages/page-104.md)

## 分裂后 Reservation 为什么危险

```text
[发生 division]
       |
       v
[通信恢复]
       |
       +-- 同步持久 Reservation 成功 --> [可访问]
       |
       `-- 尚不能同步 --> [ANA Inaccessible]
                            |-- 永久失败 --> ANA Persistent Loss
                            `-- 或控制器停止处理，CFS=1
```

该状态图在本地渲染页 106 核对。未同步时不能假设 Reservation 权利仍然可靠，因此命名空间所属 ANA Group 保持不可访问。 [PDF p. 106](../_source/pages/page-106.md)

## 规范依据

- [Domain 与 division 语义，PDF 第 104 页](../_source/pages/page-104.md)
- [组成、标识符和拓扑示例，PDF 第 105 页](../_source/pages/page-105.md)
- [division 后 Reservation 恢复，PDF 第 106-107 页](../_source/pages/page-106.md)
