---
type: Guide
title: NVMe SSD 开关机读图指南
description: 从通电到读出明文，再从最后一笔写入看到断电，按图查懂硬件、存储和加密术语。
summary: 用供电、通信、读盘和加密串起开机与关机
tags:
- storage
- nvme
- pcie
- beginner
sources:
- 'session: 2026-11-22 NVMe 开关机图解与 REFCLK、PERST# 讨论'
- nvme-power-cycle/src/content/report.md
- nvme-power-cycle/src/content/beginner-flow.js
createdAt: '2026-11-22'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# NVMe SSD 开关机读图指南

**开机时，电脑先给 SSD 通电、连通线路，然后才能读文件或解锁。关机时，电脑先收尾，主板才在需要时切电。**

## 读图先认四样东西

| 图上的词 | 先这么理解 | 往下读 |
| --- | --- | --- |
| SSD / M.2 | SSD 是存东西的盘。这里的 M.2 是盘插到主板上的接口形式。 | [供电、时钟和复位](../specs/m2-power-clock-reset.md) |
| 3.3 V / REFCLK / PERST# | 给电、给节拍、让盘退出复位。 | [供电、时钟和复位](../specs/m2-power-clock-reset.md) |
| PCIe / NVMe | PCIe 像传东西的通道。NVMe 规定如何请求盘读、写或报告状态。 | [从 PCIe 建链到 NVMe 读盘](../specs/pcie-nvme-queues-and-packets.md) |
| BIOS / UEFI / ESP / Secure Boot | 固件先运行，从一块小分区找到启动程序。启用 Secure Boot 时，还要检查这段程序能不能被信任。 | [启动验签、TPM 和磁盘解锁](nvme-boot-trust-and-unlock.md) |
| TPM / BitLocker / LUKS / Opal | TPM 可帮电脑保护取得密钥的条件。软件加密由电脑解密，Opal 由盘控制访问。 | [启动验签、TPM 和磁盘解锁](nvme-boot-trust-and-unlock.md) |
| Flush / SHN / SHST | Flush 问的是相关写入有没有存稳。SHN 是关停通知，SHST 是关停进度。 | [保存、上锁、关停和断电](nvme-shutdown-and-power-loss.md) |

## 两张图怎么顺着读

这是一台采用常见 M.2 NVMe 启动盘、执行冷启动和有序关机的示意。横线表示先后。等到某一步可以花多久，要看该机型的记录。

```text
开机
主板给电和节拍 → 松开复位 → 连通 PCIe → 初始化 NVMe
                                               |
                      如果 Opal 锁住启动分区，先放行这块区域
                                               |
                UEFI 读启动文件 → 按设置验签 → 准备读系统卷
                                               |
         软件加密：电脑取密钥          Opal：SSD 放行受锁范围
                        \                 /
                         读到系统卷的明文

关机
停止新访问，完成最后写入 → 必要时 Flush（等相关数据存稳）
              ↓
卷收尾（软件结束用密钥，或按策略发 Opal 上锁命令）
              ↓
主机发关停通知 → SSD 报告完成 → 主板按设计收链、复位、断电
                               └→ 适用的复位事件可触发 Opal 自动上锁
```

### 为什么图上箭头有时会倒着走

「电脑读 SSD」说的是电脑想拿数据。在 PCIe 线上，盘把结果写进主机内存，所以返回的数据箭头是 **SSD → 主机**。图上的箭头按当下这一个动作判断，先问「这一箭是谁发的，谁接收」。箭头有时标的是物理信号，比如主板控制的复位引脚。那些电压变化无需形成 PCIe 包。

### 怎么找具体名词

- 展开图里的寄存器时遇到 `CC.EN`、`CSTS.RDY`、`AQA`、`ASQ`、`ACQ`、`SQE`、`CQE`、`MWr`、`MRd` 或 `CplD`，查[队列与发包对照](../specs/pcie-nvme-queues-and-packets.md)。
- 想知道为什么有的盘先读 ESP、有的盘先解锁，查[两条解锁路线](nvme-boot-trust-and-unlock.md)。
- 想知道关机画面消失与插槽掉电之间还发生什么，查[关机与断电](nvme-shutdown-and-power-loss.md)。
- 遇到毫秒和秒数，先问它从哪一刻起算。公开日志的例子在[怎样读开关机实测](nvme-power-timing-evidence.md)。

## 关键要点

- 电源、PCIe、NVMe、文件系统和加密各有自己的状态。理解一条记录时先认它属于哪一层。
- 链路连通后，主机还要让控制器就绪。盘被识别后，系统卷也可能仍需解锁。
- 软件可以报告关机完成。要确认 M.2 真的断电，观测点应放在盘端的 3.3 V 电源轨。

## 相关

- [PC 上电与下电时，一块 NVMe SSD 经历了什么](http://127.0.0.1:4317/index.html) · 本地预览运行时可查完整时序、寄存器和公开资料。
- [开关机简明图解](http://127.0.0.1:4317/beginner.html) · 本地预览运行时可沿流程逐步展开。
