---
type: Concept
title: 身份、名称与列表格式（Identity, Name, and List Formats）
description: NVMe 中的“编号”用途不同：有些告诉你厂商是谁，有些给人看，有些在全球范围唯一，还有些只是当前子系统里的临时操作句柄。把它们混在一起，是资产管理和多路径排障的常见错误。
  [PDF pp. 183-189](../_source/pages/page-183.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 身份、名称与列表格式（Identity, Name, and List Formats）

NVMe 中的“编号”用途不同：有些告诉你厂商是谁，有些给人看，有些在全球范围唯一，还有些只是当前子系统里的临时操作句柄。把它们混在一起，是资产管理和多路径排障的常见错误。 [PDF pp. 183-189](../_source/pages/page-183.md)

## 一张图分清各种 ID

```text
全局身份
|-- NVM 子系统：NQN
|-- 命名空间：EUI64、NGUID、UUID（至少一个）
`-- 控制器：NQN + 子系统内 CNTLID

展示/归属信息
|-- VID、SSVID、IEEE OUI
`-- Serial Number、Model Number

枚举句柄
|-- Controller List：升序 CNTLID
`-- Namespace List：升序 NSID
```

这张图将耐久身份、显示信息和枚举编号分开。`CNTLID` 单独只在一个子系统内唯一，和 NQN 合在一起才可全球区分控制器。 [PDF pp. 183-188](../_source/pages/page-183.md)

## 一个多路径排障案例

服务器通过两条路径看到同一个存储。两条路径报告的 NSID 都是 `1`，并不证明它们一定指向同一命名空间；管理员应比对 NGUID、EUI64 或 UUID。NSID 只用于在命令中选取当前子系统里的命名空间。 [PDF pp. 188-189](../_source/pages/page-188.md)

## 常见格式和字节顺序

| 标识符 | 形式 | 顺序 | 用途 |
|---|---|---|---|
| `VID`、`SSVID` | 各 16 位 | 小端 | PCI 分配的厂商归属 |
| 序列号、型号 | 固定 ASCII | 字符顺序、右补空格 | 厂商给人看的描述 |
| IEEE OUI | 24 位 | 小端 | Identify Controller 中的归属值 |
| `EUI64` | 8 octets | 大端 | 全局命名空间标识 |
| `NGUID` | 16 octets | 大端 | OUI 加厂商/扩展命名空间身份 |
| UUID | 16 octets | RFC 9562 顺序 | 全局命名空间身份或 UUID 型 NQN 组件 |

三字节 OUI 在 Identify 中是小端，但嵌入 EUI64/NGUID 的 OUI 属于大端 octet 字符串；把两者互换会导致字节倒置。 [PDF pp. 183-186](../_source/pages/page-183.md)

## 命名空间的耐久身份

新建命名空间必须通过非零 `EUI64`、非零 `NGUID` 或 Namespace Identification Descriptor 中的 UUID 至少提供一个全局唯一标识。若 EUI64 和 NGUID 都是零，则有效 Namespace UUID 是强制项。 [PDF pp. 188-189](../_source/pages/page-188.md)

`UIDREUSE=0` 时，删除后的非零 EUI64/NGUID 可被未来命名空间复用；`UIDREUSE=1` 时禁止复用。这和 NSID 完全不同：NSID 是命令选择器，作用域只有子系统，且挂接状态对控制器而言是相对的。 [PDF p. 189](../_source/pages/page-189.md)

## NQN：主机和子系统的全局名字

```text
域名授权形式：
nqn.yyyy-mm.<反向域名>:<授权方自定义后缀>

UUID 形式：
nqn.2014-08.org.nvmexpress:uuid:<RFC-9562 UUID 文本>
```

NQN 是最长 223 字节、以空字节终止的 UTF-8 字符串，在 host 或 NVM 子系统整个生命周期内保持不变。域名形式的日期必须落在授权方拥有该域名的期间，反向域名不能是 `org.nvmexpress`。 [PDF pp. 187-188](../_source/pages/page-187.md)

## 列表不是集合类型，而是按编号排好的数组

| 列表 | 结构 | 空/未使用表示 |
|---|---|---|
| Controller List | 16 位 `NUMCIDS`，最多 2,047 个升序 controller ID | 计数为零，未用项为零 |
| Namespace List | 升序 32 位 NSID | 首项/其余未用项为零 |

图表依据 Figures 137-138 简化。零是填充或“不存在”，不是有效的列表内控制器或命名空间身份。 [PDF pp. 186-187](../_source/pages/page-186.md)

## UTF-8 字符串怎样比较

```text
本地配置输入 --> 可做本地文本处理 --> Host / NVM 子系统
Host / NVM 子系统之间 ------ 原始 NVMe UTF-8 字节 ------>
接收协议字符串：不做归一化、区域比较或 UTF-8 重校验
```

该边界是 Figure 140 的教学性重述。文本归一化或本地化比较只能在本地配置输入边界进行；通过 NVMe 接收的字符串按二进制字符串保存和比较。 [PDF pp. 189-190](../_source/pages/page-189.md)

## 还要认识 Host Identifier 与命名空间标签

Host Identifier（Feature `81h`）注册 host 身份，用于控制器关联和 Reservation 权利。零代表不与其他控制器关联，Fabrics 强制 128 位形式；非零当前值不能被直接覆盖。 [PDF pp. 422-424](../_source/pages/page-422.md)

Namespace Admin Label（Feature `1Fh`）是 256 字节、空终止的 UTF-8 人类标签。它必须保存，Set 时必须带 `SV=1`，成功 Sanitize 后恢复为全零。 [PDF pp. 414-415](../_source/pages/page-414.md)

## 规范依据

- [标识符字节布局，PDF 第 183-186 页](../_source/pages/page-183.md)
- [控制器/命名空间列表与 NQN，PDF 第 186-188 页](../_source/pages/page-186.md)
- [命名空间身份与 UTF-8 边界，PDF 第 188-190 页](../_source/pages/page-188.md)
- [Host Identifier，PDF 第 422-424 页](../_source/pages/page-422.md)
- [Namespace Admin Label，PDF 第 414-415 页](../_source/pages/page-414.md)
