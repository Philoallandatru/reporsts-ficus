---
type: Concept
title: 启动验签、TPM 和磁盘解锁
description: 解释 BIOS、UEFI、ESP、Secure Boot、TPM、BitLocker、LUKS 和 Opal 在首次读到明文之前各做什么。
summary: 看清启动程序在哪读、由谁验签、最后由谁解密
tags:
- storage
- uefi
- tpm
- encryption
- opal
sources:
- 'session: 2026-11-22 将 BIOS、验签、TPM、软件加密和 Opal 放进开机图'
- nvme-power-cycle/src/content/report.md
- https://uefi.org/specs/UEFI/2.11/32_Secure_Boot_and_Driver_Signing.html
- https://www.trustedcomputinggroup.org/resources/documents/pc-client-specific-platform-firmware-profile-specification
- https://learn.microsoft.com/en-us/windows/security/hardware-security/tpm/how-windows-uses-the-tpm
- https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/faq
- https://gitlab.com/cryptsetup/cryptsetup/-/wikis/FrequentlyAskedQuestions
- https://trustedcomputinggroup.org/wp-content/uploads/TCG-Storage-Opal-SSC-v2.30_pub.pdf
createdAt: '2026-11-22'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 启动验签、TPM 和磁盘解锁

**开机时，先要找到允许执行的启动程序，再按电脑的加密方式取得系统卷的数据。软件加密由电脑解密，Opal 由盘先放行。**

## 启动文件从哪里来

| 词 | 简单解释 | 谁来做 |
| --- | --- | --- |
| 固件 / BIOS / UEFI | 固件是按电源键后最早运行的程序。现在普通 PC 多用 UEFI，大家仍常把它叫 BIOS。 | 电脑先运行主板上的固件，再认盘、挑选启动项。 |
| ESP / EFI 系统分区 | 放启动程序的一小块盘上空间。常见 UEFI 启动从这里找到 `.efi` 文件。 | UEFI 发普通的 NVMe Read，从 SSD 读来文件内容。 |
| 引导程序 / Bootloader | 把操作系统带起来的小程序。 | UEFI 交给它继续工作，由它或随后启动的环境准备运行系统。 |
| 系统卷 | 放操作系统主要文件的逻辑空间。 | 启动环境或操作系统要能够读取这个卷，才能继续使用系统里的文件。 |
| 明文 / 密文 | 明文是解密后能按原格式使用的数据。密文要用密钥才能恢复原内容。 | 软件加密时，SSD 返回受保护扇区的密文，由主机解开。 |

**Secure Boot 像验票。** UEFI 在启动程序运行之前，按策略检查它的签名或摘要。摘要可以理解为用程序字节算出的短指纹。常见的 `db` 是允许库，`dbx` 是禁止库。SSD 把文件送到主机内存，以后怎么判断允不允许运行，由主机里的固件负责。 [UEFI 2.11 第 32 章](https://uefi.org/specs/UEFI/2.11/32_Secure_Boot_and_Driver_Signing.html)

**度量启动（Measured Boot）像登记。** 电脑会把启动代码或策略的摘要交给 **TPM**（可信平台模块）。TPM 中的 **PCR** 像几格专用的累计登记簿。每次加入新摘要时，计算会把旧值和新摘要一起算进去。后续可按这次启动的状态决定是否放行受保护的密钥材料。PC Client 规范中，PCR 4 与启动程序有关，PCR 7 与 Secure Boot 策略有关。验签、登记和取钥都是主机侧的工作，TPM 交互走平台接口。 [TCG 平台固件规范](https://www.trustedcomputinggroup.org/resources/documents/pc-client-specific-platform-firmware-profile-specification) · [微软如何使用 TPM](https://learn.microsoft.com/en-us/windows/security/hardware-security/tpm/how-windows-uses-the-tpm)

## 两条路线怎么走

### 软件加密 · 电脑拿钥匙，电脑解密

常见 Windows 软件 **BitLocker** 先从独立、可读的 ESP 启动引导环境。BitLocker 里，**FVEK** 是实际解密卷数据的密钥，**VMK** 像护住 FVEK 的外层钥匙。配置 TPM 保护器时，满足启动策略可取得解开 VMK 所需的材料，有的配置还要 PIN。

Linux 的 **LUKS** 是管理加密卷及其密钥槽的格式。典型软件路径由启动早期的 **initramfs**（先放进内存的小型启动环境）解锁，随后 **dm-crypt**（内核中的加解密层）按需对数据加解密。解锁凭据可能是口令、密钥文件或按配置受 TPM 保护的材料。“输的口令”和“真正加解密数据的卷密钥”承担不同职责。 [微软 BitLocker FAQ](https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/faq) · [Cryptsetup FAQ](https://gitlab.com/cryptsetup/cryptsetup/-/wikis/FrequentlyAskedQuestions)

### Opal · 盘负责范围的门禁

**SED** 是能在盘内加解密的自加密盘。**TCG Opal** 规定了怎样管理盘上的访问权限。SSD 可以对一段逻辑块地址（**锁定范围**）分别锁住读和写。主机认证并放行目标范围后，SSD 才接受相应访问。对于只用盘端加密的一层，读取时 SSD 在盘内解密并送回原数据块。如果同一范围还叠加了软件卷加密，电脑还要解开那一层。

- **ESP 已可读**。先读启动程序并按策略检查，再在读系统卷之前解锁系统卷所在范围。
- **ESP 也在 Opal 读锁里**。先从固件或其他可读位置运行认证程序并放行这个范围，接着才读 ESP。之后若系统卷在另一个仍被锁住的范围，还要放行那个范围。 [TCG Opal 2.30](https://trustedcomputinggroup.org/wp-content/uploads/TCG-Storage-Opal-SSC-v2.30_pub.pdf)

```text
软件加密                       Opal 范围锁

读 ESP → 验签/启动             ESP 锁住了吗？
          ↓                   ├─ 锁住：先通过可用的启动代码认证，再读 ESP
      主机取得卷密钥           └─ 可读：直接读 ESP
          ↓                           ↓
SSD → 主机内存：系统卷密文       系统卷仍锁住时，主机再认证并请求放行
          ↓                           ↓
      主机解密得明文           SSD 在盘内解密，回传逻辑块
```

### 展开图里的 81h / 82h

两条都是**主机提交的 NVMe 管理命令**。这里看的是盘端链路的数据阶段，提交、取订单、完成项仍按[通用命令路径](../specs/pcie-nvme-queues-and-packets.md)经过各自的门铃和队列。

| 操作码 | 好记的说法 | 数据阶段的方向 |
| --- | --- | --- |
| `81h` Security Send | 主机把安全协议请求交给盘 | SSD → 主机发 `MRd` 取主机内存里的请求。主机 → SSD 回 `CplD` 携带请求内容。 |
| `82h` Security Receive | 主机从盘取回安全协议响应 | SSD → 主机发 `MWr`，把响应写进主机内存。 |

这两个操作码也可用于查询等操作。要确认真的解锁，要看协议响应是否成功、目标范围的读锁是否解除，以及随后读盘的结果。 [NVMe PCIe 传输](https://nvmexpress.org/wp-content/uploads/NVM-Express-PCI-Express-Transport-Specification-Revision-1.1-2024.08.05-Ratified.pdf#page=12) · [StorNVMe 命令表](https://learn.microsoft.com/en-us/windows-hardware/drivers/storage/stornvme-command-set-support)

## 关键要点

- Secure Boot 回答「这段程序可不可以启动」，TPM 可以参与回答「按现在的启动状态能不能使用受保护的材料」，卷加密回答「这些数据怎样恢复成能读的内容」。
- ESP 何时读取取决于它当前能否访问。第一次读到 ESP 文件和第一次读到系统卷明文是两个阶段。
- 读加密系统卷仍用普通读命令。软件加密与 Opal 的区别在于线路上的数据内容和解密发生的位置。

## 相关

- [NVMe SSD 开关机读图指南](nvme-power-cycle-guide.md)
- [从 PCIe 建链到 NVMe 读盘](../specs/pcie-nvme-queues-and-packets.md)
- [保存、上锁、关停和断电](nvme-shutdown-and-power-loss.md)
