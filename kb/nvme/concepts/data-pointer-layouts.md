---
type: Concept
title: 数据指针布局（Data Pointer Layouts）
description: 一条 NVMe 命令要读写数据时，控制器必须知道主机缓冲区在哪里。PRP 用“按内存页编号”的方式描述位置；SGL 用一串带长度和类型的描述符描述位置。
  [PDF pp. 173-175](../_source/pages/page-173.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 数据指针布局（Data Pointer Layouts）

一条 NVMe 命令要读写数据时，控制器必须知道主机缓冲区在哪里。PRP 用“按内存页编号”的方式描述位置；SGL 用一串带长度和类型的描述符描述位置。 [PDF pp. 173-175](../_source/pages/page-173.md)

## 两种地址清单的直觉

```text
PRP：命令
 |-- PRP1 -> 第一页（可带页内偏移）
 `-- PRP2 -> 第二页，或 PRP List
                    `-> 更多页地址

SGL：命令
 `-- SGL1 -> 数据描述符，或段描述符
                    `-> 带长度/类型的更多描述符
```

PRP 的总长度由命令传输长度和页大小推导；SGL 每个描述符显式携带长度和类型。 [PDF pp. 173-175](../_source/pages/page-173.md)

## 一个跨页 Read 的案例

应用需要读 12 KiB，缓冲区从一页中间开始。驱动把起点放入 `PRP1`，若只跨到第二页则在 `PRP2` 放第二页地址；若还会跨更多页，`PRP2` 改为指向 PRP List，列表列出后续页。

这也是为什么驱动不能把任意字节地址填到每个 PRP：只有第一个 PRP 可以有有效的页内偏移。 [PDF pp. 173-174](../_source/pages/page-173.md)

## PRP 的对齐规则

```text
63                         n+1 n                         0
+-----------------------------+--------------------------+
| 页基地址                    | CC.MPS 决定的页内偏移    |
+-----------------------------+--------------------------+
```

该位域依据已渲染核对的 Figures 109-110 重绘。每个 PRP 为 64 位并按 dword 对齐；`CC.MPS` 决定偏移宽度。 [PDF pp. 173-174](../_source/pages/page-173.md)

| PRP 位置 | 偏移规则 | 用途 |
|---|---|---|
| 命令的第一个 PRP | 可非零，但 bits 1:0 必须为 `00b` | 数据起点 |
| 命令的第二个 PRP | 必须为零 | 第二个数据页或首个 PRP List 页 |
| PRP List 中的数据页 | 必须为零 | 一个完整数据页 |
| 下一张 List 的指针 | 页对齐 | 串联下一张列表页 |

页对齐要求的位置出现非零偏移，应报告 PRP Offset Invalid；若控制器未报告低两位非零，它按这两位为零处理。 [PDF p. 174](../_source/pages/page-174.md)

## PRP List 是一页地址簿

```text
一张连续内存页，装满 64 位条目
+-----------------------------+
| 数据页地址 0                |
| 数据页地址 1                |
| ...                         |
| 最后一个数据页地址，或      |
| 下一张 PRP List 页的地址    |
+-----------------------------+
```

列表从第 0 项开始，不重复命令中已给出的 PRP。需要多张列表页时，当前页最后一个可用项用于串联下一页。相邻条目指向的数据页可以物理连续，也可以完全无关。 [PDF p. 174](../_source/pages/page-174.md)

## SGL：更灵活的“快递清单”

SGL 由一个或多个按 qword 对齐的连续 segment 组成，segment 内装有类型化描述符。只有一个 segment 的最后一个描述符才能链接到下一个 Segment 或 Last Segment；最后一个 segment 不得再链接。 [PDF p. 175](../_source/pages/page-175.md)

```text
通用 SGL 描述符（16 字节）
+-----------------------------------------------+------+
| bytes 0:14：类型专用内容                      | ID   |
+-----------------------------------------------+------+
                                                  |  |
                                           类型 7:4  子类型 3:0
```

该字节图依据 Figures 113-116 重绘。Base Specification 定义数据、丢弃、segment 链接、keyed data、transport data 等角色；各类型允许的子类型决定地址/偏移等解释。 [PDF pp. 176-177](../_source/pages/page-176.md)

| 描述符类型 | 作用 | 必须记住的规则 |
|---|---|---|
| Data Block | 描述一段要传输的地址范围 | 零长度合法；地址加长度不能溢出 64 位 |
| Bit Bucket | 丢弃源数据的一部分 | 作为源缓冲区时无效果 |
| Segment | 链接到后续非最终段 | 链接长度非零且为 16 的倍数 |
| Last Segment | 链接到最终段 | 目标段不再含 segment 链接 |
| Keyed Data Block | 带 32 位 key 的地址范围 | 长度用 24 位编码 |
| Transport Data Block | 由传输绑定提供传输机制 | Base 中地址字节保留 |

控制器会报告支持哪些 SGL 形式和 Data Block 的对齐粒度。不支持的描述符类型/子类型或非法 segment 链接，会中止命令。 [PDF pp. 175-179](../_source/pages/page-175.md)

## Bit Bucket 为什么有用

```text
控制器逻辑数据：[3 KiB][4 KiB][丢弃 2 KiB][4 KiB] = 13 KiB
主机目标缓冲区： A      B                 C      = 11 KiB

segment 0：Data(A,3 KiB) -> Segment(1)
segment 1：Data(B,4 KiB), BitBucket(2 KiB) -> LastSegment(2)
segment 2：Data(C,4 KiB)
```

这个 Figure 123 的教学性重述说明：命令访问 13 KiB，但真正写到主机的 Data Block 只接收 11 KiB，另外 2 KiB 被目的端 Bit Bucket 吃掉。 [PDF pp. 179-180](../_source/pages/page-179.md)

## 与命令格式的关系

`CDW0.PSDT` 决定通用命令格式如何解释 metadata 和 data pointer：选择 PRP 还是 SGL。Fabrics 命令使用 SGL 而非 PRP，并可使用传输特定的描述符形式。Metadata Region 的详细含义由所选 I/O Command Set 定义，不在 Base 中统一布局。 [PDF pp. 43, 155-160, 181](../_source/pages/page-043.md)

## 规范依据

- [PRP 地址、偏移与列表，PDF 第 173-174 页](../_source/pages/page-173.md)
- [SGL segment 与描述符契约，PDF 第 175-179 页](../_source/pages/page-175.md)
- [链式 SGL 与 Bit Bucket 示例，PDF 第 179-180 页](../_source/pages/page-179.md)
- [Metadata Region 边界，PDF 第 181 页](../_source/pages/page-181.md)
