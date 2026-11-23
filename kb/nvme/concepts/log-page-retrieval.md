---
type: Concept
title: 日志页读取（Get Log Page）
description: Get Log Page 是读取控制器、命名空间、Domain、Endurance Group 或 NVM 子系统信息的管理命令。`LID`（日志页标识符）决定返回哪种数据，也决定数据的作用域。
  [PDF pp. 223, 226-227](../_source/pages/page-223.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 日志页读取（Get Log Page）

Get Log Page 是读取控制器、命名空间、Domain、Endurance Group 或 NVM 子系统信息的管理命令。`LID`（日志页标识符）决定返回哪种数据，也决定数据的作用域。 [PDF pp. 223, 226-227](../_source/pages/page-223.md)

## 把日志页当作“按编号索取的报告”

```text
主机 -- Get Log Page(LID、范围、长度、起点) --> 控制器 --> 对应日志对象
主机 <------------- 指定 dword 范围的数据 -------------------|

成功且 RAE=0：通常同时清除对应的异步事件
```

这是解释性命令流程，不是对编号 Figure 的重绘。未支持的 LID 会以 Invalid Log Page 失败，但规范定义的命令特定例外仍适用。 [PDF pp. 223-225](../_source/pages/page-223.md)

## 一个处理告警的案例

控制器通过 AER 报告健康或错误事件。主机随后发送 Get Log Page，读取细节；如果确认已处理，就用 `RAE=0` 成功完成读取以清除相应事件。若只是想先观察、稍后再处理，则使用 `RAE=1` 保留事件。 [PDF p. 224](../_source/pages/page-224.md)

## 关键参数怎么理解

| 关注点 | 规则 |
|---|---|
| 传输长度 | `NUMDU:NUMDL` 是从零开始的 dword 数；超出日志末尾时，完整日志后面的 dword 未定义 |
| 字节偏移 | `OT=0`，`LPOU:LPOL` 是按 dword 对齐处理的字节偏移；超界失败 |
| 索引偏移 | `OT=1`，偏移是条目索引；只有该 LID 报告 `IOS=1` 时可用 |
| 命令集选择 | `CSI` 只在 LID 支持它且 `CC.CSS=110b` 时有效 |
| UUID 选择 | `UIDX` 只用于该日志支持 UUID 限定的情况 |

命令使用通用 Data Pointer 和 CDW10 到 CDW14；其余命令特定字段保留。 [PDF pp. 223-225](../_source/pages/page-223.md)

## 先问：这个接口支持哪几份报告

`LID=00h` 的 Supported Log Pages 日志有 256 个、每个 4 字节的条目，覆盖当前提交接口上可能的所有 LID。不同 Admin Queue 或管理端点可报告不同的支持集合。 [PDF pp. 227-228](../_source/pages/page-227.md)

```text
Supported Log Pages（1024 字节）
+---------+---------+-----+-----------+
| LID 00h | LID 01h | ... | LID FFh   |
+---------+---------+-----+-----------+
     每个条目：SUP=是否支持；IOS=是否允许索引偏移
```

图根据 Figures 203-204 作了教学性简化。若 `SUP=0`，主机应忽略该条目的其余位；扩展 Get Log Page 不支持时，`IOS` 必须为零。 [PDF p. 228](../_source/pages/page-228.md)

## 范围必须与日志定义相符

| 日志范围 | 数据属于谁 |
|---|---|
| 子系统范围 | 整个 NVM 子系统 |
| Domain 范围 | 指定 Domain |
| 控制器范围 | 处理该命令的控制器 |
| 命名空间范围 | 指定 NSID 的命名空间 |

控制器或子系统范围的日志若使用既非 `0h` 也非 `FFFFFFFFh` 的 NSID，会无效。某些多范围日志还有自己的有效范围规则。 [PDF pp. 226-227](../_source/pages/page-226.md)

## 容易踩坑的地方

- 一个接口报告支持某日志，不代表另一个 Admin 接口也支持。
- `RAE=0` 会影响事件保留；读取前要决定是“确认处理”还是“只查看”。
- 当 `IOS=0` 时不能把偏移当条目编号使用。 [PDF pp. 224-228](../_source/pages/page-224.md)

## 规范依据

- [Get Log Page 命令、长度与事件保留，PDF 第 223-225 页](../_source/pages/page-223.md)
- [日志范围与 LID 注册表，PDF 第 226-227 页](../_source/pages/page-226.md)
- [Supported Log Pages 结构，PDF 第 227-228 页](../_source/pages/page-227.md)
