---
type: Concept
title: 保存、上锁、关停和断电
description: 按正常关机顺序解释 Flush、FUA、软件卷密钥、Opal 重新上锁、CC.SHN、CSTS.SHST 和 3.3 V 掉电。
summary: 分清保存数据、锁回卷、控制器关停和撤掉供电
tags:
- storage
- nvme
- shutdown
- flush
- opal
sources:
- 'session: 2026-11-22 NVMe 下电流程与加密收尾'
- nvme-power-cycle/src/content/report.md
- https://nvmexpress.org/wp-content/uploads/NVM-Express-Base-Specification-Revision-2.1-2024.08.05-Ratified.pdf
- https://nvmexpress.org/wp-content/uploads/NVM-Express-NVM-Command-Set-Specification-Revision-1.1-2024.08.05-Ratified.pdf
- https://github.com/torvalds/linux/blob/v6.12/drivers/md/dm-crypt.c#L2783-L2834
- https://www.man7.org/linux/man-pages/man8/cryptsetup-close.8.html
- https://trustedcomputinggroup.org/wp-content/uploads/TCG-Storage-Opal-SSC-v2.30_pub.pdf
- https://trustedcomputinggroup.org/wp-content/uploads/TCG-Storage-Interface-Interactions-Specification-SIIS_V1.0_R20_pub.pdf#page=49
- https://pcisig.com/section-5323-following-error-scenario-valid-rc-sends-pmeturnoff-message-ep-ep-doesnt-respond-ack-due
createdAt: '2026-11-22'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 保存、上锁、关停和断电

**保存是让写入断了电也能留下，关停是让 SSD 报告已经收尾，断电则是主板撤掉盘的供电。加密卷还要在合适的位置结束访问。**

## 第一步 · 把最后的写入存稳

应用停下来后，操作系统可能还要写文件、目录和其他记录。数据可能暂存在内存或 SSD 的**易失缓存**里，意思是一旦断电就可能消失。**持久化**是让约定范围内的数据在掉电后还能保留。

- **Flush** 像说「把这批符合条件的已写数据存稳」。主机发 NVM `Flush 00h`，看 SSD 写回的成功完成项（CQE）。这条命令有队列提交和回执，没有另行搬运文件数据的缓冲区。
- **FUA（Force Unit Access）**可以跟在一条 Write 命令里，要求这笔写入按相应的持久化语义完成。普通 Write 的完成与 FUA 或 Flush 的保证要按命令和缓存配置分别理解。
- 存储栈决定关机时是否发 Flush 和刷新哪个范围。仍在做最后一笔加密写入时，软件卷还要能加密，Opal 范围还要允许所需的写入。具体 Flush 的位置也可能在软件映射撤掉之后，因为主机可以对底层 namespace 发命令。 [NVM 命令集 1.1](https://nvmexpress.org/wp-content/uploads/NVM-Express-NVM-Command-Set-Specification-Revision-1.1-2024.08.05-Ratified.pdf)

## 第二步 · 结束加密卷的访问

| 方式 | 什么时候、谁来做 | SSD 线上的表现 |
| --- | --- | --- |
| 软件加密 | 主机停止使用卷，撤掉运行时解密路径。以 LUKS 为例，映射实际关闭时会清理它持有的内核密钥。卷仍被使用时，关闭可能失败或推迟。 | 结束用钥和内存清理发生在主机内部。可观察前后的普通 I/O。 |
| Opal 主动上锁 | 如果配置了主动上锁，主机等目标范围的相关 I/O 完成，再在盘仍可通信时认证并设置范围锁。 | 使用管理队列的 `81h/82h` 安全收发。根据方法结果和目标范围状态判定。 |
| Opal 自动上锁 | 盘按 `LockOnReset` 策略在遇到匹配的复位或重新上电条件时恢复锁态。 | 盘内动作本身无需 `81h/82h` 流量。下次可通信时可核对锁状态。 |

清掉电脑这次使用的密钥，与改掉下次启动用的卷保护配置是两个动作。关闭软件解密路径时，磁盘上的加密数据和下次用来解锁的元数据仍然保留。Opal 的电源周期和有电的硬件复位也要分别判断，单独看到链路消失或清 `CC.EN` 无法辨认出自动上锁是否发生。 [cryptsetup-close 手册](https://www.man7.org/linux/man-pages/man8/cryptsetup-close.8.html) · [TCG Opal 2.30](https://trustedcomputinggroup.org/wp-content/uploads/TCG-Storage-Opal-SSC-v2.30_pub.pdf) · [TCG 存储接口复位映射](https://trustedcomputinggroup.org/wp-content/uploads/TCG-Storage-Interface-Interactions-Specification-SIIS_V1.0_R20_pub.pdf#page=49)

## 第三步 · 通知 SSD，等它答复

在正常、有通信的示例路径里，主机等普通 I/O 收尾。有 I/O 队列时，按规范建议先删请求队列再删回执队列。接下来，主机写通知并轮询状态。

| 字段 | 一句话 | 典型包方向 |
| --- | --- | --- |
| `CC.SHN=01b` | 电脑告诉 SSD「开始正常关停」 | 主机 → SSD，`MWr` 写控制寄存器。 |
| `CSTS.SHST` | 电脑问「做到哪了」 | 主机 → SSD 发 `MRd`，SSD → 主机回 `CplD`。 |
| `SHST=00b / 01b / 10b` | 正常运行 / 正在关停 / 已完成 | 状态从上面那笔读返回的寄存器值里取。一次轮询可能直接从正常读到已完成。 |
| `CSTS.ST=0` | 在 NVMe Base 2.1 的这一场景表示控制器级关停 | 与 `SHST=10b` 一起作为 Base 2.1 的控制器级可下电条件。更早的规范和驱动实现按其各自定义核对。 |

后缀 `b` 表示二进制，所以 `10b` 是十进制的 2。`SHN` 和 `SHST` 是控制面板上的两处字段。发关停通知这一步是写寄存器，普通队列里无需再出现一张对应通知的 NVMe 回执。 [NVMe Base 2.1 §3.6.1](https://nvmexpress.org/wp-content/uploads/NVM-Express-Base-Specification-Revision-2.1-2024.08.05-Ratified.pdf#page=133)

```text
操作系统 / 主机                                  SSD
  -------- Write，按需要带 FUA 或随后 Flush ----->
  <------- 成功完成项 --------------------------------
  [完成卷访问。若主动给 Opal 上锁，在还可通信时做]
  -------- 写 CC.SHN，通知正常关停 --------------->
  -------- 读 CSTS，询问完成状态 ---------------->
  <------- 返回 SHST，主机确认完成 -------------------

主板按实现停止通信、拉复位并撤掉 3.3 V
  └─ 匹配已配置的事件时，盘按策略恢复 Opal 锁态
```

## 第四步 · 盘端 3.3 V 消失才是撤电

主板按自己的设计收起链路、控制 PERST# 并在相应路径中撤电。关机画面消失、链路不再活动、PERST# 拉低和盘端 3.3 V 掉电，是可以分别观察的事件。突然失电时，完整的通知和完成读回可能来不及发生。 [PCI-SIG M.2 边带信号](https://pcisig.com/PCIExpress/ECN/M.2/Power-uprequirementsforPCIesidebandsPERST_etc.) · [NVMe Base 2.1 关停](https://nvmexpress.org/wp-content/uploads/NVM-Express-Base-Specification-Revision-2.1-2024.08.05-Ratified.pdf#page=133)

展开这一步时，`PME_Turn_Off` 是主机送出的 PCIe 准备关停消息，`PME_TO_Ack` 是设备回的协议响应。`L2/L3 Ready` 表示链路准备转入深度省电或掉电状态。它描述的是链路准备到哪一步，实际撤电要继续查看物理电源轨。各平台是否走这段握手，取决于电源管理路径。 [PCI-SIG 关停握手说明](https://pcisig.com/section-5323-following-error-scenario-valid-rc-sends-pmeturnoff-message-ep-ep-doesnt-respond-ack-due) · [PCI-SIG 低功耗链路状态](https://pcisig.com/blog/making-most-pcie%C2%AE-low-power-features)

## 关键要点

- Flush 管的是相关数据能不能留住。SHN 发通知，SHST 报进度。它们能在同一次关机中各自出现。
- 软件卷用钥在主机内结束。主动 Opal 上锁发生在盘还在线时，自动 Opal 上锁取决于盘是否遇到配置匹配的事件。
- 看到 SSD 报告关停完成后，还要看主板是否真的撤了盘的 3.3 V。

## 相关

- [NVMe SSD 开关机读图指南](nvme-power-cycle-guide.md)
- [启动验签、TPM 和磁盘解锁](nvme-boot-trust-and-unlock.md)
- [M.2 的 3.3 V、REFCLK 和 PERST#](../specs/m2-power-clock-reset.md)
- [怎样读开关机实测](nvme-power-timing-evidence.md)
