---
type: Concept
title: Fabric Zoning 数据传输（Fabric Zoning Data Transfer）
description: Fabric Zoning 命令让 Direct Discovery Controller（DDC）定位并交换存放在 Centralized
  Discovery Controller（CDC）中的 Zoning 数据结构。先用 Lookup 把查询条件映射成 Zoning Data Key（ZDK），再用
  Receive/Send 分片传输结构。 [P...
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Fabric Zoning 数据传输（Fabric Zoning Data Transfer）

Fabric Zoning 命令让 Direct Discovery Controller（DDC）定位并交换存放在 Centralized Discovery Controller（CDC）中的 Zoning 数据结构。先用 Lookup 把查询条件映射成 Zoning Data Key（ZDK），再用 Receive/Send 分片传输结构。 [PDF pp. 457-460](../_source/pages/page-457.md)

## 先查编号，再分片搬运

```text
DDC 查询条件 -- FZL --> CDC Zoning 数据库
                         |
                         `-- Zoning Data Key（ZDK）
                                  |
              +-------------------+-------------------+
              |                                       |
     FZR：CDC -> DDC 分片                   FZS：DDC -> CDC 分片
     offset + length；CQE 中 LF              offset + length；命令中 LF
```

该图把“找对象”和“搬对象”分开，也保留了最后一片标志所在位置的差异。 [PDF pp. 457-460](../_source/pages/page-457.md)

## 一个同步 ZoneGroup 的案例

DDC 需要取得 CDC 中某个 ZoneGroup。它先发 FZL，CDC 在 CQE Dword 0 返回 ZDK；DDC 再用这个 ZDK 多次 FZR，按 offset 获取片段，直到 controller 在 CQE 里把 `LF=1`。此时 DDC 才可把完整结构交给后续逻辑处理。 [PDF pp. 457-459](../_source/pages/page-457.md)

## 三个操作如何分工

| 操作 | 选择上下文 | 结束标记 |
|---|---|---|
| Lookup（`FZL`） | 命令缓冲区中的 lookup data | 在 CQE Dword 0 返回 `ZDK` |
| Receive（`FZR`） | DDC 用 `ZDK`；CDC 用当前 Transaction ID | controller 在 CQE Dword 0 返回 `LF` |
| Send（`FZS`） | DDC 用 `ZDK`；CDC 用当前 Transaction ID | 发送方在命令 Dword 12 设置 `LF` |

`ZDKC` 位区分当前携带的是 Zoning Data Key 还是 Transaction ID。CDC 接受 key 上下文，DDC 接受 transaction 上下文；相反组合以 Invalid Field in Command 失败。`NUMD` 不得为零。 [PDF pp. 458-459](../_source/pages/page-458.md)

## 分片生命周期

```text
[选定 ZDK / Transaction ID]
            |
            v
[offset + 非零 dword 数] -- 传输 --> [LF=0：继续]
            ^                            |
            `----------------------------'
                                         |
                                  [LF=1：完成]
```

Receive 在完成中报告 `LF`，Send 在命令中携带 `LF`。offset 按 dword 对齐；低位不为零时 controller 可拒绝，若未拒绝则按低位为零处理。Receive 还会拒绝超过目标结构大小的 offset。 [PDF pp. 458-459](../_source/pages/page-458.md)

## 常见失败原因

Lookup、Receive 和 Send 都可能报告结构被锁定、结构不存在、Fabric Zoning 未启用，或 DDC 无权访问该 ZoneGroup。Fabric Zoning 是全 Fabric 的访问控制配置，不等于 Exported NVM Subsystem 的 Allowed Host List。 [PDF pp. 457-460](../_source/pages/page-457.md)

## 规范依据

- [Lookup 与 ZDK，PDF 第 457 页](../_source/pages/page-457.md)
- [Receive 字段和完成状态，PDF 第 458-459 页](../_source/pages/page-458.md)
- [Send 字段和完成状态，PDF 第 459-460 页](../_source/pages/page-459.md)
