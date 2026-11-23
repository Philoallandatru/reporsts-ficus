---
type: Concept
title: Directive 交换（Directive Exchange）
description: Directive Receive 和 Directive Send 是一对管理命令，用于在 host 与 controller 之间传输“由
  Directive Type 决定含义”的数据。通用命令只提供信封；具体 Directive Type 才定义操作、数据结构和状态码。 [PDF pp. 212-214](../_source/pages/pa...
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Directive 交换（Directive Exchange）

Directive Receive 和 Directive Send 是一对管理命令，用于在 host 与 controller 之间传输“由 Directive Type 决定含义”的数据。通用命令只提供信封；具体 Directive Type 才定义操作、数据结构和状态码。 [PDF pp. 212-214](../_source/pages/page-212.md)

## 把它当作带类型标签的收发件

```text
Host                         Controller
 |-- Directive Send --------->|  host -> controller 的类型数据
 |   DTYPE + DOPER + DSPEC    |
 |                            |
 |<-- Directive Receive ------|  controller -> host 的类型数据
     DTYPE + DOPER + DSPEC
```

图根据 Receive/Send 定义整理，展示的是方向而不是某个类型的具体 payload。 [PDF pp. 212-214](../_source/pages/page-212.md)

## 一个理解案例

驱动知道某个 Directive Type，但不必为每种类型新造一套传输命令。它用 `DTYPE` 选中类型、用 `DOPER` 选择该类型内操作、再用 `DSPEC` 传递类型专用选择子。Send 把数据交给控制器，Receive 取回结果。 [PDF pp. 212-214](../_source/pages/page-212.md)

## 通用信封中有哪些字段

| 字段 | 作用 |
|---|---|
| Data Pointer | 传输缓冲区起点 |
| `NUMD` | 从零开始编码的传输 dword 数 |
| `DTYPE` | 选择 Directive Type |
| `DOPER` | 选择该类型内的操作 |
| `DSPEC` | Directive Type 专用值 |
| CDW12-13 | 仅当选定类型/操作定义时使用 |

Receive 和 Send 在 CDW10-11 使用相同字段划分，区别只是传输方向。表是 Figures 175-180 的紧凑归纳。 [PDF pp. 212-213](../_source/pages/page-212.md)

## 长度不匹配时

Receive 请求长度小于结果结构时，只传输其前缀；请求更大时，控制器只传输完整结构，不会补零或附加数据。完成仍通过管理完成队列返回，其命令特定状态由 Directive Type 决定。 [PDF pp. 212-214](../_source/pages/page-212.md)

## 规范依据

- [Directive Receive 缓冲区和长度行为，PDF 第 212 页](../_source/pages/page-212.md)
- [Receive/Send 字段布局，PDF 第 213 页](../_source/pages/page-213.md)
- [Send 完成与类型专用语义边界，PDF 第 214 页](../_source/pages/page-214.md)
