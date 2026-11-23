---
type: Concept
title: 资源与管理清单日志（Resource and Management Inventory Logs）
description: 有些日志不是记录某次命令，而是列出资源边界上的“资产清单”：例如 Endurance Group 范围内的旋转介质寿命数据，以及整个 NVM
  子系统可用的管理地址。 [PDF pp. 287-289](../_source/pages/page-287.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 资源与管理清单日志（Resource and Management Inventory Logs）

有些日志不是记录某次命令，而是列出资源边界上的“资产清单”：例如 Endurance Group 范围内的旋转介质寿命数据，以及整个 NVM 子系统可用的管理地址。 [PDF pp. 287-289](../_source/pages/page-287.md)

## 两种清单，回答两个问题

```text
指定 ENDGID 的 Endurance Group
`-- 旋转介质：actuator、RPM、spinup/load 成功/失败累计数

NVM 子系统
`-- 最多 8 个管理地址描述符
    `-- 类型 + 空终止 UTF-8 URI
```

图概括了 Figures 269、271、272，并已对照本地渲染的 PDF 页 287-289。 [PDF pp. 287-289](../_source/pages/page-287.md)

## 一个运维案例

运维工具先读取 Management Address List，发现一个管理代理 URI，于是把设备配置和带外管理交给该地址；这不是另一条 NVMe 队列，也不是 host-controller association。若设备使用旋转介质，工具还可按 Endurance Group 读取旋转信息，观察起转/加载失败趋势。 [PDF pp. 287-289](../_source/pages/page-287.md)

## 两种日志的固定规则

| 日志 | 范围/选择子 | 关键规则 |
|---|---|---|
| Rotational Media Information（`16h`） | 用 Log Specific Identifier 选择 Endurance Group | 跨掉电/reset 保留；报告 actuator 数、Power State 0 RPM 和饱和的 32 位寿命事件计数 |
| Management Address List（`18h`） | NVM 子系统 | 0 到 8 个固定大小描述符；扫描到第 7 项或第一个 `MAT=FFh` 结束 |

旋转计数区分成功与失败：spinup 关心 controller 从非运行到运行，load 关心 actuator 的对应转换。计数达到 `FFFFFFFFh` 后饱和，而不是回绕。没有旋转介质 Endurance Group 的子系统不应支持该日志。 [PDF pp. 287-288](../_source/pages/page-287.md)

## 管理地址类型

| `MAT` | 含义 |
|---|---|
| `1h` | 子系统管理代理 |
| `2h` | fabric 接口管理器 |
| `0h` | 地址字段保留 |
| `FFh` | 有效描述符结束标记 |

地址本身是空终止 UTF-8 URI。 [PDF p. 289](../_source/pages/page-289.md)

## 规范依据

- [旋转介质选择子和字段，PDF 第 287-288 页](../_source/pages/page-287.md)
- [管理地址列表与描述符，PDF 第 289 页](../_source/pages/page-289.md)
