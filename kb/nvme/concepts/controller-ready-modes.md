---
type: Concept
title: 控制器就绪模式与超时（Controller Ready Modes and Timeouts）
description: '`CSTS.RDY=1` 不总是表示“所有数据盘已经能读写”。它可以表示控制器已全面就绪，也可以只表示不依赖介质的管理工作已可用、命名空间仍在准备。
  [PDF pp. 128-131](../_source/pages/page-128.md)'
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 控制器就绪模式与超时（Controller Ready Modes and Timeouts）

`CSTS.RDY=1` 不总是表示“所有数据盘已经能读写”。它可以表示控制器已全面就绪，也可以只表示不依赖介质的管理工作已可用、命名空间仍在准备。 [PDF pp. 128-131](../_source/pages/page-128.md)

## 两种“就绪”的差别

```text
CC.EN: 0 -> 1
      |
      +-- 带介质就绪（CC.CRIME=0）
      |      `-- 到 CRTO.CRWMT 前：RDY=1，命令与介质均可用
      |
      `-- 独立于介质就绪（CC.CRIME=1）
             |-- 到 CRTO.CRIMT 前：RDY=1，非介质命令可用
             `-- 到 CRTO.CRWMT 前：已挂接命名空间与介质可用
```

这张时间线是解释性重述。`CAP.CRMS` 报告支持哪些模式，控制器同时支持两种模式时，主机在启用前用 `CC.CRIME` 选择。 [PDF pp. 128-131](../_source/pages/page-128.md)

## 一个启动很快但磁盘仍未就绪的案例

服务器启动时，主机选择“独立于介质就绪”。控制器很快报告 `RDY=1`，驱动便能读取 Identify、日志等不依赖命名空间介质的资料；但立即发出的 Read 可能返回可重试的 Namespace Not Ready。

这不是 Read 永久失败，而是提醒主机等到介质准备截止时间前后再试。 [PDF pp. 128-131](../_source/pages/page-128.md)

## 能否选择模式

| `CAP.CRMS` | 控制器能力 | 主机对 `CC.CRIME` 的作用 |
|---|---|---|
| `00b` | 旧式、不可选择；使用 `CAP.TO` 限定等待 | 忽略，读回为 `0` |
| `01b` | 仅支持带介质就绪 | 读回为 `0` |
| `11b` | 同时支持两种模式 | 启用前由主机选择 |

Revision 2.1 控制器支持“带介质就绪”；`00b` 仍用于早于 Revision 2.0 的兼容语义。更改 `CC.CRIME` 不会改写 `CRTO` 的两个数值，但可能影响 `CAP.TO`。 [PDF pp. 130-131](../_source/pages/page-130.md)

## 主机应怎样判断失败

若控制器错过适用的处理或介质截止时间，仍必须在 `CRTO.CRWMT` 前使 `CSTS.RDY=1`。若支持 Persistent Event Log，还要记录 Controller Ready Timeout Exceeded 硬件错误事件。 [PDF pp. 131-132](../_source/pages/page-131.md)

## 容易混淆的地方

- `RDY=1` 不是无条件的“所有 I/O 都能成功”。
- 独立于介质就绪只放宽了不依赖已挂接命名空间或介质的命令。
- 哪些 Admin 命令可以报告 Admin Command Media Not Ready 由跨页 Figure 84 精确定义，不应自行扩大名单。 [PDF pp. 129-130](../_source/pages/page-129.md)

## 规范依据

- [就绪模式定义，PDF 第 128 页](../_source/pages/page-128.md)
- [命令限制与 Figure 84，PDF 第 129-130 页](../_source/pages/page-129.md)
- [模式选择、超时与失败处理，PDF 第 130-132 页](../_source/pages/page-130.md)
