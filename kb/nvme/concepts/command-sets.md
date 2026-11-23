---
type: Concept
title: 命令集（Command Sets）
description: 命令集规定“某类命令能做什么、应该走哪条队列、怎样解释数据”。可以把它理解为一套工作语言：管理人员说管理语言，读写数据说 I/O 语言，Fabrics
  连接使用专门的网络语言。 [PDF p. 41](../_source/pages/page-041.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 命令集（Command Sets）

命令集规定“某类命令能做什么、应该走哪条队列、怎样解释数据”。可以把它理解为一套工作语言：管理人员说管理语言，读写数据说 I/O 语言，Fabrics 连接使用专门的网络语言。 [PDF p. 41](../_source/pages/page-041.md)

## 命令该去哪里

```text
管理配置、识别、日志  --> Admin 命令集 --> 管理提交队列
读、写等数据操作      --> I/O 命令集   --> I/O 提交队列
建立/维护 Fabrics 连接 --> Fabrics 命令集 --> 规范规定的相应队列
```

该图根据规范图 5 作了学习用重述。命令的类别不只影响名称，更影响它能否在当前控制器状态下处理。 [PDF p. 41](../_source/pages/page-041.md)

## 一个常见案例

主机先通过管理队列发送 Identify，确认控制器能力；随后在 I/O 队列发送 Read。若使用 NVMe-oF，还要先用 Fabrics 命令建立队列连接。

把 Read 误放到管理提交队列，或在尚未具备条件时发送 I/O 命令，都不是“换一个通道也能完成”的用法。 [PDF p. 41](../_source/pages/page-041.md)

## 三类命令的分工

| 类别 | 主要用途 | 初学者例子 |
|---|---|---|
| Admin | 发现、配置、管理控制器和命名空间 | Identify、获取日志、创建队列 |
| I/O | 操作命名空间中的用户数据 | Read、Write |
| Fabrics | 建立并维护基于消息的 NVMe 连接 | Connect、Disconnect |

Fabrics 命令有特殊启动作用：即使控制器尚未启用，规范仍允许处理这类命令以完成连接等基础操作。 [PDF p. 41](../_source/pages/page-041.md)

## 命名空间为什么要绑定 I/O 命令集

```text
创建命名空间
      |
      +--> 选择一个 I/O 命令集
                 |
                 +--> 此绑定保持到命名空间生命周期结束
```

绑定决定数据模型。例如，NVM 命令集把数据当作逻辑块；其他 I/O 命令集可以使用不同的数据模型。控制器必须支持并启用该命令集，命名空间才可挂接到它。 [PDF p. 52](../_source/pages/page-052.md)

## 进阶：命令集组合

当 `CC.CSS=110b` 选择“所有支持的 I/O 命令集”模式时，主机可用 Feature ID `19h` 选择控制器已声明的某个命令集组合。组合不能排除仍被已挂接命名空间使用的命令集。 [PDF pp. 410-411](../_source/pages/page-410.md)

## 容易混淆的地方

- Admin 命令“管理”设备，不等于它可以替代 I/O 命令读写用户数据。
- I/O 命令集绑定的是命名空间，不是某次单独 I/O 请求的临时选项。
- Fabrics 是连接和传输环境中的命令类别；它不等于所有 NVMe 命令。 [PDF pp. 41, 52](../_source/pages/page-041.md)

## 规范依据

- [命令集分类与队列路由，PDF 第 41 页](../_source/pages/page-041.md)
- [命名空间与 I/O 命令集绑定，PDF 第 52 页](../_source/pages/page-052.md)
- [I/O 命令集配置，PDF 第 410-411 页](../_source/pages/page-410.md)
