---
type: Concept
title: 从 PCIe 建链到 NVMe 读盘
description: 看懂 PCIe 链路、寄存器、NVMe 队列和数据包，并用一次读盘对照谁发给谁。
summary: 从接通线路、按门铃到 SSD 把数据写回内存
tags:
- specs
- pcie
- nvme
- dma
sources:
- 'session: 2026-11-22 NVMe 开关机图解与发包方向'
- nvme-power-cycle/src/content/beginner-flow.js
- nvme-power-cycle/src/content/report.md
- https://pcisig.com/sites/default/files/files/02_01_Troubleshooting_PCI_Express_Link_Training_and_Protocol_Issues_FROZEN.pdf
- https://nvmexpress.org/wp-content/uploads/NVM-Express-PCI-Express-Transport-Specification-Revision-1.1-2024.08.05-Ratified.pdf
- https://nvmexpress.org/wp-content/uploads/NVM-Express-Base-Specification-Revision-2.1-2024.08.05-Ratified.pdf
- https://learn.microsoft.com/en-us/windows-hardware/drivers/storage/stornvme-command-set-support
createdAt: '2026-11-22'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 从 PCIe 建链到 NVMe 读盘

**PCIe 提供电脑和 SSD 之间的通信通道，NVMe 规定读写的做法。电脑向 SSD 发读盘请求，SSD 再把结果写回电脑的内存。**

## 先让双方联系上

- **主机（Host）**是电脑这一侧，包含运行软件的处理器、内存和连向 SSD 的 PCIe 端口。抓线上的包时，「主机发」一般指 PCIe 根端口这一侧发包。**端点（Endpoint）**是这条链路的另一端，这里是 SSD。
- **链路（Link）**是两端建立起来的连接，**Lane** 是其中一条全双工通道。`×4` 表示配置了四条通道。**链路训练**像先约定用几条通道、用多快的速率通信。**LTSSM** 是控制这些阶段的状态机，也就是按条件从一站走到下一站的规则。常见路径是 Detect（找对端）→ Polling（交换训练序列）→ Configuration（配置通道）→ L0（正常传输）。升速或重训时可经过 Recovery。
- **枚举（Enumeration）**像点名。固件在链路可用后读取设备身份和类型，配置访问地址。**BAR** 是地址窗口的配置。对 NVMe 寄存器对应的 BAR，知道基址和偏移就能找到要读写的寄存器。 [PCI-SIG 链路训练资料](https://pcisig.com/sites/default/files/files/02_01_Troubleshooting_PCI_Express_Link_Training_and_Protocol_Issues_FROZEN.pdf) · [NVMe PCIe Transport 1.1](https://nvmexpress.org/wp-content/uploads/NVM-Express-PCI-Express-Transport-Specification-Revision-1.1-2024.08.05-Ratified.pdf)

展开第 2 步时，`TS1/TS2` 是双方交换的训练序列，帮助建立和配置链路。`CfgRd0/CfgWr0` 是主机发给端点的 Type 0 配置读写，带数据的读回用 `CplD`，普通配置写完成用 `Cpl`。开 `Memory Space Enable` 让设备响应分配给它的内存地址窗口，开 `Bus Master Enable` 才允许设备发起相应的内存事务，例如对主机内存做 DMA。 [PCI-SIG 链路训练资料](https://pcisig.com/sites/default/files/files/02_01_Troubleshooting_PCI_Express_Link_Training_and_Protocol_Issues_FROZEN.pdf) · [NVMe Base 2.1 的 PCI 配置空间](https://nvmexpress.org/wp-content/uploads/NVM-Express-Base-Specification-Revision-2.1-2024.08.05-Ratified.pdf)

## 寄存器、队列和门铃

**寄存器**像设备的控制面板，有的格子让主机写设定，有的让主机读状态。在 PCIe 上，主机访问映射出来的寄存器，称为 **MMIO**，也就是用内存地址的读写方式操作设备。队列更像主机内存里的一摞订单和回执。 [NVMe Base 2.1](https://nvmexpress.org/wp-content/uploads/NVM-Express-Base-Specification-Revision-2.1-2024.08.05-Ratified.pdf)

| 名词 | 一句话 | 在开机图里 |
| --- | --- | --- |
| `CAP` / `VS` | 控制器的能力和接口版本信息 | 并非所有盘都支持相同的设置，主机会先查。 |
| `AQA` / `ASQ` / `ACQ` | 管理队列多大，订单和回执各放在哪 | 主机准备好内存，再把尺寸和地址告诉盘。 |
| `CC.EN` | 主机写的启用开关 | 主机置 1，请盘开始工作。 |
| `CSTS.RDY` | SSD 的控制器就绪状态 | 主机读到 1，知道控制器已就绪。这项信息本身没有说明目标数据能否读出。 |
| Admin Queue / I/O Queue | 管理用的队列和搬数据用的队列 | 先建立编号 0 的管理队列，再用管理命令建立普通读写用的 I/O 队列。 |
| SQ / SQE | 提交队列 / 里面的一份订单 | SQE 里有操作码、命令编号，以及这次指定的地址等。 |
| CQ / CQE | 完成队列 / 里面的一张回执 | CQE 报告是哪条 NVMe 命令完成了，或发生了什么错误。 |
| Doorbell 门铃 | 告诉对方这摞订单或回执处理到哪 | 主机写 SQ 尾门铃通知盘新增订单。收完回执后再写 CQ 头门铃。 |
| Namespace / NSID / LBA | 盘暴露的一片逻辑存储空间 / 它的编号 / 里面的块地址 | 读盘时先用 NSID 选空间，再用 LBA 定位想读的数据块。 |

展开第 3 步时，`Identify 06h` 像问「你是哪款盘、有哪些能力」。`Create I/O CQ 05h` 先建接回执的队列，`Create I/O SQ 01h` 再建提交订单的队列并关联它。有的驱动先用 `Set Features 09h` 的 `FID 07h` 商量有几组队列。固件把控制权交给系统后，系统的驱动可能重新设置自己的队列，再看到一次初始化。 [NVMe Base 2.1 初始化和管理命令](https://nvmexpress.org/wp-content/uploads/NVM-Express-Base-Specification-Revision-2.1-2024.08.05-Ratified.pdf)

展开最后的 Read 时，`SLBA` 指从哪块开始，`NLB` 是块数减一。比如 `SLBA=100、NLB=3` 表示从第 100 块开始读 4 块。SSD 写完回执后，线路上还可能看到另发的 **MSI-X** 中断消息，提醒主机查看回执。驱动也可以定期主动查看完成队列。 [NVM 命令集 1.1](https://nvmexpress.org/wp-content/uploads/NVM-Express-NVM-Command-Set-Specification-Revision-1.1-2024.08.05-Ratified.pdf) · [NVMe PCIe Transport 1.1](https://nvmexpress.org/wp-content/uploads/NVM-Express-PCI-Express-Transport-Specification-Revision-1.1-2024.08.05-Ratified.pdf)

## 把一次读盘拆成发包方向

**TLP** 是 PCIe 传送事务的包。图里用 `MRd` 表示「向对面读一段地址」，`CplD` 表示「带数据回答这次读」，`MWr` 表示「往对面的地址写」。**DMA** 是设备直接读写主机内存。CPU 做好安排后，实际搬运可由 SSD 发起。

```text
主机 / 主机内存                                SSD
       把 Read 订单写进主机内存里的 SQ
       -------- MWr：敲 SQ 门铃 ------------->
       <------- MRd：来取订单 ----------------
       -------- CplD：把订单交过去 ---------->
       <------- MWr：把读到的数据写进内存 -----
       <------- MWr：写入 NVMe 完成项 CQE ------
       -------- MWr：更新 CQ 头门铃 --------->
```

回答 `MRd` 的 `CplD` 和 SSD 后续写入的 `CQE` 在回答不同问题。前者只完成那一笔 PCIe 内存读，后者才给出 NVMe 命令的执行结果。图是常见的主机内存队列示意。实际一笔命令的数据可拆成多个包，一次门铃也可以通知多条命令。 [NVMe PCIe Transport 1.1 §3.4](https://nvmexpress.org/wp-content/uploads/NVM-Express-PCI-Express-Transport-Specification-Revision-1.1-2024.08.05-Ratified.pdf#page=12)

写盘时方向反过来。电脑下单以后，SSD 发 `MRd` 来取待写内容，主机用 `CplD` 带回内容。判断命令还要看队列。比如 `02h` 的 `h` 表示十六进制，`02h` 在 NVM 的 I/O 队列上是 Read，在管理队列上则是 Get Log Page。 [StorNVMe 操作码对照](https://learn.microsoft.com/en-us/windows-hardware/drivers/storage/stornvme-command-set-support)

## 关键要点

- 看见 `L0` 说明链路已经到正常传输阶段。看见 `CSTS.RDY=1` 说明控制器已就绪。要确认系统卷真能读，还要看针对目标块的实际成功读。
- 看箭头先认动作。敲门铃、取订单、送数据、写回执各有自己的发起方。
- 分辨 `MWr` 的用途要一起看方向和地址。写到盘的门铃地址、写到内存的数据缓冲区和写到完成队列的含义各不相同。

## 相关

- [NVMe SSD 开关机读图指南](../storage/nvme-power-cycle-guide.md)
- [M.2 的 3.3 V、REFCLK 和 PERST#](m2-power-clock-reset.md)
- [启动验签、TPM 和磁盘解锁](../storage/nvme-boot-trust-and-unlock.md)
