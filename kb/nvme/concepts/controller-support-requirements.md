---
type: Concept
title: 控制器支持要求（Controller Support Requirements）
description: 不要因为某个功能“叫 NVMe 功能”就假设所有控制器都必须支持它。规范会按 I/O、管理和发现控制器分别标注命令、日志页和 Feature
  是必需（M）、可选（O）还是禁止（P）。 [PDF pp. 65-70](../_source/pages/page-065.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 控制器支持要求（Controller Support Requirements）

不要因为某个功能“叫 NVMe 功能”就假设所有控制器都必须支持它。规范会按 I/O、管理和发现控制器分别标注命令、日志页和 Feature 是必需（M）、可选（O）还是禁止（P）。 [PDF pp. 65-70](../_source/pages/page-065.md)

## 把支持矩阵当作“岗位权限表”

```text
控制器角色          I/O          管理         发现
----------------------------------------------------
用户数据命令       可以          禁止         禁止
管理命令           按矩阵        按矩阵       按矩阵
日志与 Feature     按角色/条件   按角色/条件   按角色/条件
```

图只帮助定位；Figures 28-32 及每个单元格的注释才是精确要求。 [PDF pp. 65-70](../_source/pages/page-065.md)

## 主机如何确认“真的支持”

| 对象 | 用什么确认 | 还要注意什么 |
|---|---|---|
| 命令 | Commands Supported and Effects 日志页 | I/O 命令集自己的规范也可能另有要求 |
| 日志页 | Supported Log Pages 与控制器类型要求 | 作用域、前置条件会改变结论 |
| Feature | Feature Identifiers Supported and Effects 日志页 | 支持任何 Feature 时必须支持 Get/Set Features |

这些日志帮助主机发现实现能力，但不替代规范中对控制器角色的强制要求。 [PDF pp. 65, 67-70](../_source/pages/page-065.md)

## 一个实际案例

同一台存储同时提供 I/O 控制器和发现控制器。业务主机只能把 Read/Write 发给 I/O 控制器；发现控制器只负责让新主机找到服务。即便两者都能通过 Fabrics 连接，也不能把发现控制器当成数据路径。 [PDF pp. 65-68](../_source/pages/page-065.md)

## 传输也会改变答案

```text
PCIe：Fabrics 命令禁止；I/O 控制器必须支持创建/删除 I/O 队列
Fabrics：每类控制器都必须支持 Property Get/Set 与 Connect
发现控制器：发现服务相关命令/日志按角色要求；普通 I/O 禁止
```

[PDF pp. 65-68](../_source/pages/page-065.md)

## “可选”不等于随意省略

有些 `O` 项在特定能力开启后变成必须：例如启用 Reservation、Flexible Data Placement，或维持持久 Discovery 连接时，相关命令、日志、Keep Alive 和异步事件支持都会受到附注约束。 [PDF pp. 66-70](../_source/pages/page-066.md)

## 规范依据

- [管理、Fabrics 与 I/O 命令支持矩阵，PDF 第 65-67 页](../_source/pages/page-065.md)
- [日志页与 Feature 支持矩阵，PDF 第 67-70 页](../_source/pages/page-067.md)
