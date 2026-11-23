---
type: Concept
title: 控制器属性（Controller Properties）
description: 控制器属性可以理解为 NVMe 控制器的“配置面板”。主机读取能力、设置运行参数、查询状态，都是在读写这些 4 或 8 字节的属性；传输方式只改变访问方法，不改变属性含义。
  [PDF p. 71](../_source/pages/page-071.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 控制器属性（Controller Properties）

控制器属性可以理解为 NVMe 控制器的“配置面板”。主机读取能力、设置运行参数、查询状态，都是在读写这些 4 或 8 字节的属性；传输方式只改变访问方法，不改变属性含义。 [PDF p. 71](../_source/pages/page-071.md)

## 先把属性当作一排固定尺寸的抽屉

```text
主机
 | 在属性起始偏移处，按声明宽度读/写一次
 v
+--------------------------------------------------+
| CAP | VS | INTMS | INTMC | CC | CSTS | 其他属性 |
+--------------------------------------------------+
    能力   版本    屏蔽   解除    配置   状态
```

该图是解释性布局。一次访问不能跨越两个属性；主机也不应把保留位或保留属性当作可用空间。 [PDF pp. 71-73](../_source/pages/page-071.md)

## 一个初始化案例

驱动先读取 `CAP`，得知支持哪些页大小、仲裁方式、命令集和队列上限；随后在 `CC` 中选择这些能力允许的值，配置好队列条目大小，最后才设置 `CC.EN=1`。

如果不先读 `CAP` 就随意写 `CC`，就像给插座接了不兼容电压：写入值可能不受控制器支持。 [PDF pp. 74-79](../_source/pages/page-074.md)

## 访问时必须遵守的规则

| 规则 | 初学者解释 |
|---|---|
| 从属性起始偏移访问 | 不能从属性中间切入 |
| 使用声明的 4 或 8 字节宽度 | 不能随意拆成或合并访问 |
| 不跨越两个属性 | 一次读写不能碰到相邻抽屉 |
| 保留位写零 | 为未来扩展留出空间 |
| 保留位读零 | 但不应依赖“不支持访问也会返回零” |

消息型控制器通过 Property Get/Set 读写，内存型控制器依所属传输绑定访问。 [PDF pp. 71-73](../_source/pages/page-071.md)

## 最常见的几个属性

| 属性 | 用途 | 例子 |
|---|---|---|
| `CAP` | 报告限制和能力 | 最大队列、页大小、就绪模式 |
| `VS` | 报告规范版本 | Revision 2.1 为 `2.1.0` 编码 |
| `CC` | 选择配置并启用控制器 | `CC.EN=1` 开始就绪转换 |
| `CSTS` | 报告当前状态 | `CSTS.RDY=1` 表示达到相应就绪契约 |
| `INTMS` / `INTMC` | 屏蔽/解除中断向量 | 写 `1` 才改变对应位 |

`INTMS` 和 `INTMC` 仅适用于引脚中断和 MSI；配置 MSI-X 时不得访问它们，因为 MSI-X 有自己的屏蔽表。 [PDF pp. 77-79](../_source/pages/page-077.md)

## CAP 中几个容易读错的编码

| 字段 | 正确解读 |
|---|---|
| `MPSMIN` / `MPSMAX` | 页大小为 `2^(12 + value)` 字节 |
| `DSTRD` | doorbell 间距为 `2^(2 + value)` 字节；`0h` 是 4 字节 |
| `TO` | 最坏就绪等待，单位 500 ms；`FFh` 为 127.5 秒 |
| `MQES` | 从零开始的单队列最大条目数；`1h` 表示 2 个条目 |

`CAP.CQR=1` 时队列必须物理连续；对消息型传输它总是置位。PCIe 的 `MQES` 限制主机创建的 I/O SQ 和 CQ，Fabrics 中则限制 I/O SQ。 [PDF pp. 75-77](../_source/pages/page-075.md)

## PCIe 与 Fabrics 的访问差异

```text
内存型主机：MMIO / 传输绑定定义的属性访问 --> 控制器属性
消息型主机：Property Get / Property Set 胶囊 --> 同一属性语义
```

Fabrics 的 Get/Set 选择单个偏移处的 4 或 8 字节访问。偏移、属性或宽度不合法时，命令以 Invalid Field in Command 失败。 [PDF pp. 479-481](../_source/pages/page-479.md)

## 规范依据

- [属性访问规则与属性空间，PDF 第 71-73 页](../_source/pages/page-071.md)
- [CAP 字段与限制，PDF 第 74-77 页](../_source/pages/page-074.md)
- [版本、中断与 CC 前置条件，PDF 第 77-79 页](../_source/pages/page-077.md)
- [Fabrics Property Get/Set，PDF 第 479-481 页](../_source/pages/page-479.md)
