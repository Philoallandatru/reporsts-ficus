---
type: Concept
title: 主机内存缓冲区（Host Memory Buffer，HMB）
description: HMB 是主机划出、专供控制器使用的内存。它仍位于主机内存，但一旦启用完成，主机必须把这块内存的使用权交给控制器；完成禁用后才能安全回收或改写。
  [PDF pp. 429-431](../_source/pages/page-429.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 主机内存缓冲区（Host Memory Buffer，HMB）

HMB 是主机划出、专供控制器使用的内存。它仍位于主机内存，但一旦启用完成，主机必须把这块内存的使用权交给控制器；完成禁用后才能安全回收或改写。 [PDF pp. 429-431](../_source/pages/page-429.md)

## 谁拥有内存，一眼看清

```text
主机分配区域和描述符列表
          |
          | Set Features: EHM=1 成功完成
          v
[控制器拥有 HMB；主机不得写]
          |
          | Set Features: EHM=0 成功完成
          v
[控制器停止访问；主机可回收或修改]
```

这条完成边界是最重要的 HMB 规则。 [PDF pp. 429-430](../_source/pages/page-429.md)

## 一个驱动回收内存的案例

驱动需要释放一块 HMB 给其他用途时，先发送禁用 HMB 的 Set Features，并等待其完成。收到完成前，控制器仍可能读取其中的数据；收到完成后，控制器不得再访问，驱动才可以释放或改写该内存。 [PDF pp. 429-430](../_source/pages/page-429.md)

## 启用、禁用和返回旧内存

| 动作 | 结果 |
|---|---|
| 对已启用 HMB 再启用 | Command Sequence Error |
| 对已禁用 HMB 再禁用 | 成功，但不做动作 |
| `MR=1` 返回旧内存 | 尺寸、描述符地址/内容和缓冲区内容必须与 reset/Runtime D3 前一致 |
| `MR=0` 提供新内存 | 内容可未定义 |

禁用完成前控制器应先取走仍需要的数据；完成后到下一次启用前不得访问 HMB。 [PDF pp. 429-431](../_source/pages/page-429.md)

## HMB 由什么描述

```text
连续的描述符列表（每项 16 字节）
|-- entry 0：BADD（页对齐地址）+ BSIZE（页数）
|-- entry 1：BADD（页对齐地址）+ BSIZE（页数）
`-- entry n：BADD（页对齐地址）+ BSIZE（页数）
```

主机提供以 controller memory page 为单位的总大小、16 字节对齐的连续描述符列表物理地址以及非零条目数。每项描述一段连续缓冲区；长度为零的项被忽略。 [PDF pp. 431-432](../_source/pages/page-431.md)

Get Features 返回 `EHM`、非运行状态限制是否启用（`HMNARE`）及当前是否生效（`HMNAR`）；其 4 KiB 属性结构只是当前状态观察，不会产生新的所有权移交。 [PDF p. 432](../_source/pages/page-432.md)

## 低功耗状态下的限制

控制器支持时，主机可在请求进入非运行电源状态后限制 HMB 访问，管理命令和由管理命令发起的后台操作除外。这个限制独立于 permissive mode，也不改变声明的进入延迟。 [PDF p. 430](../_source/pages/page-430.md)

## 规范依据

- [HMB 所有权与启用/禁用，PDF 第 429-430 页](../_source/pages/page-429.md)
- [返回语义、描述符与 Get Features 属性，PDF 第 430-432 页](../_source/pages/page-430.md)
