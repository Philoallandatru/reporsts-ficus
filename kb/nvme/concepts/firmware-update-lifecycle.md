---
type: Concept
title: 固件更新生命周期（Firmware Update Lifecycle）
description: NVMe 固件更新不是“上传一个文件就立即生效”。它是一条串行的下载、提交、校验和激活流程；命令通过一个控制器或 Management Endpoint
  发出，而激活影响的是整个 Domain。 [PDF pp. 152-154](../_source/pages/page-152.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 固件更新生命周期（Firmware Update Lifecycle）

NVMe 固件更新不是“上传一个文件就立即生效”。它是一条串行的下载、提交、校验和激活流程；命令通过一个控制器或 Management Endpoint 发出，而激活影响的是整个 Domain。 [PDF pp. 152-154](../_source/pages/page-152.md)

## 最短流程：先存进去，再决定何时切换

```text
[分段下载固件] --> [Commit + 厂商校验] --> 选择激活方式
                                            |-- 立即激活
                                            `-- 下次 reset 激活
                                                     |
                                                     v
                                           重新初始化控制器和 I/O 队列
```

图同时覆盖 reset 激活与立即激活。若无法立即激活，命令状态会告诉主机需要哪个级别的 reset。 [PDF pp. 152-153](../_source/pages/page-152.md)

## 一个安全更新案例

运维程序选定同一 Management Endpoint，按 offset 下载固件的各个分段；全部完成后 Commit 到非活动 slot，并要求下次 Controller Level Reset 激活。reset 后，驱动重新建立管理路径、重新 Identify 并创建 I/O 队列。

不要在多个控制器或端点同时发起相同 Domain 的更新，也不要把下载完成误认为已经激活。 [PDF pp. 152, 154](../_source/pages/page-152.md)

## 下载时的边界

| 规则 | 原因 |
|---|---|
| 每个更新序列通过同一控制器/Management Endpoint | 保持序列一致 |
| 不重叠多个更新序列 | 避免交叉覆盖 |
| 映像从 offset 0 开始，无间隙、无重叠 | 才是有效完整映像 |
| 按 `FWUG` 粒度处理 | 符合控制器要求 |
| reset 发生在 Commit 前 | 已下载内容全部丢弃 |

Firmware Image Download 的长度和 offset 都按从零开始的 dword 编码。下载分段可乱序到达；Boot Partition 分段例外，必须有序。 [PDF pp. 154, 216-217](../_source/pages/page-154.md)

## Commit Action 在做什么

| Action | 效果 |
|---|---|
| `000b` | 放入 slot，不激活 |
| `001b` | 放入 slot，下次 Controller Level Reset 激活 |
| `010b` | 下次 Controller Level Reset 激活已有 slot |
| `011b` | 放入已下载映像后立即激活；Commit 保持未完成直到结果确定 |
| `110b` | 替换选定 Boot Partition |
| `111b` | 标记选定 Boot Partition 为活动分区 |

slot `0h` 可让控制器在适用时从 slot 1 到 7 中选择。固件 slot 和映像由 Domain 内所有控制器共享。 [PDF pp. 214-215](../_source/pages/page-214.md)

## 立即激活的风险与恢复

若激活超过 `MTFA`，映像仍已提交，主机可改用 `010b` 在下一次 Controller Level Reset 激活。加载失败时，控制器回退到最近激活的 slot 或可用只读基线映像，并报告 Firmware Image Load Error。

Sanitize 期间改变固件会导致 sanitize 失败；待 reset 激活时，新 Sanitize 命令会被中止。 [PDF p. 153](../_source/pages/page-153.md)

## 怎样确认当前到底运行了什么

```text
slot revisions：[1] [2] [3] [4] [5] [6] [7]
                  ^ 当前激活       ^ 可选：下次 reset 激活
```

Firmware Slot Information log 报告当前 slot、可选的下次 reset slot，以及七个 slot 的 8 字节 ASCII 修订字符串。未支持或为空的 slot 使用全零修订字段。 [PDF p. 235](../_source/pages/page-235.md)

## 容易踩坑的地方

- 覆盖活动 slot 可能移除当前映像，并把激活留到后续 reset。
- 可能引入 host 不兼容行为的“立即激活”必须返回 Firmware Activation Requires Conventional Reset。
- 更具体的 reset 要求出现时，先做更窄的 reset 不会激活新映像。 [PDF pp. 153, 214-216](../_source/pages/page-153.md)

## 规范依据

- [基于 reset 的更新与立即激活，PDF 第 152-154 页](../_source/pages/page-152.md)
- [Firmware Commit、slot 和状态，PDF 第 214-216 页](../_source/pages/page-214.md)
- [Firmware Image Download，PDF 第 217 页](../_source/pages/page-217.md)
- [Firmware Slot Information log，PDF 第 235 页](../_source/pages/page-235.md)
