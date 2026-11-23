---
type: Concept
title: 怎样读 NVMe 开关机实测
description: 用 ThinkPad T14 Gen 1 和 Dell Inspiron 16 7610 的公开记录区分整机时间、软件日志时间与盘端事件。
summary: 读时间先核对机型、起点、终点和观测手段
tags:
- storage
- nvme
- timing
- evidence
sources:
- 'session: 2026-11-22 用公开记录说明 NVMe 启动和关机'
- nvme-power-cycle/src/content/report.md
- https://bbs.archlinux.org/viewtopic.php?id=309678
- https://discussion.fedoraproject.org/t/why-might-sd-sync-hang-during-shutdown/71885
- https://lists.infradead.org/pipermail/linux-nvme/2024-May/047178.html
createdAt: '2026-11-22'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 怎样读 NVMe 开关机实测

**先问秒表从哪儿开始、到哪儿停止。整机启动、输入口令、控制器关停和插槽断电是不同的计时项目。**

## 两个公开例子

### 开机 · ThinkPad T14 Gen 1

硬件为 Samsung 512 GB Gen3 NVMe，使用 LUKS。机主公开的一次 `systemd-analyze` 输出合计 **28.972 秒**。机主还说，「内核」段的大部分时间用来输入磁盘解密口令，并注明没有使用 TPM2 密钥。这里能直接读出各个软件阶段的用时。没有单独记录 SSD 解密、TPM 取钥、PCIe 链路训练或某次 NVMe 读命令的时间。 [ThinkPad 机主原帖](https://bbs.archlinux.org/viewtopic.php?id=309678)

| 记录里的名字 | 大致是哪一段 | 时间 |
| --- | --- | ---: |
| firmware | 主板固件开始准备硬件 | 6.373 秒 |
| loader | 引导器准备启动操作系统 | 0.195 秒 |
| kernel | 内核与这次早期启动的工作，包含等机主输入口令 | 16.527 秒 |
| userspace | 系统开始启动各项服务后的阶段 | 5.877 秒 |

### 关机 · Dell Inspiron 16 7610

Fedora 35，M.2 NVMe 型号未公开。机主贴出的故障日志中，**14:02:34** 报 LUKS 映射还在使用、关闭失败，同一秒开始同步文件系统和块设备，**14:03:24** 报同步超时。两个软件事件相隔约 **50 秒**。这份记录没有测盘端 3.3 V，也没有确认工作密钥在哪一刻清理成功。 [Dell 机主原始日志](https://discussion.fedoraproject.org/t/why-might-sd-sync-hang-during-shutdown/71885)

```text
同一次关机里，三种「什么时候」可以各自计时：

软件日志      开始同步 ---------------- 同步超时 / 完成
PCIe 记录     写 SHN ----------------- 第一次读到 SHST 完成
盘端测点      3.3 V 仍在 -------------↓ 电压降到有效范围以下

Dell 公开日志给了第一行的两端：14:02:34 → 14:03:24。
三行画在一起表示观测层不同，图中间距无时间比例。
```

## 以后看到一个数字，怎样给它写注释

记录 **机型与盘型号、开关机路径、从哪一刻算到哪一刻、用什么资料量到**。比如另一份 Dell XPS 13 / SK hynix PC300 的 Linux 记录里，约 **412.470 毫秒**量的是进入 **S3 睡眠**时一次从写关停通知到轮询读到 SHST 完成的间隔。适用路径和那台机型都应随数字保留。 [Dell XPS 13 内核邮件列表原始记录](https://lists.infradead.org/pipermail/linux-nvme/2024-May/047178.html)

## 关键要点

- 整机启动统计可能包含固件、输入口令、启动服务和其他设备等待。
- 轮询日志第一次读到完成时，盘已经完成该状态转换。精确发生时间通常还在两次观测之间。
- 软件日志和 PCIe 包可以解释不同阶段，盘端电压记录才直接给出这次供电消失的时间。

## 相关

- [NVMe SSD 开关机读图指南](nvme-power-cycle-guide.md)
- [保存、上锁、关停和断电](nvme-shutdown-and-power-loss.md)
- [M.2 的 3.3 V、REFCLK 和 PERST#](../specs/m2-power-clock-reset.md)
