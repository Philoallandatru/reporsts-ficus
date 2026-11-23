---
type: Concept
title: M.2 的 3.3 V、REFCLK 和 PERST#
description: 用供电、节拍和复位键解释 M.2 NVMe SSD 得电后怎样开始建立 PCIe 连接。
summary: 看懂供电、参考时钟和低有效复位三条信号
tags:
- specs
- pcie
- m2
- power
sources:
- 'session: 2026-11-22 REFCLK 与 PERST# 低到高'
- nvme-power-cycle/src/content/report.md
- https://pcisig.com/PCIExpress/ECN/M.2/Power-uprequirementsforPCIesidebandsPERST_etc.
- https://pcisig.com/blog/seamless-transition-pcie%C2%AE-50-technology-system-implementations-webinar-qa
- https://www.intel.com/content/dam/www/public/us/en/documents/technical-specifications/pci-express-gen4-retimer-supplemental-features.pdf
- https://www.intel.com/programmable/technical-pdfs/683059.pdf
createdAt: '2026-11-22'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# M.2 的 3.3 V、REFCLK 和 PERST#

**3.3 V 给 SSD 电，REFCLK 给通信打节拍，PERST# 像主板替 SSD 按住的复位键。线从低变高，就是松开复位键。**

## 图上这三个名字怎么读

| 名字 | 用生活里的话讲 | 在硬件里具体是什么 |
| --- | --- | --- |
| M.2 | 盘插进去的位置和插接形式 | 模块与插槽的规格。还要看产品是否接的是 PCIe，以及盘用什么协议。 |
| 3.3 V | 让盘有电可用 | 盘端主电源的标称电压。V 是伏特，是电压的单位。图中这条供电线从主板到盘。 |
| REFCLK | 通信的节拍器 | Reference Clock，参考时钟。在共同时钟设计里，同一个时钟源给主机端和设备端提供参考，通常是 100 MHz。 |
| PERST# | 按住或松开复位键 | 主板控制的 PCIe 复位信号。低电平让盘处于复位状态，高电平释放复位。 |
| PCIe 数据线 | 双方开始说话的线路 | 复位释放后，PCIe 两端在高速线上训练，再交换配置和数据。 |

REFCLK 的「时钟」是电信号稳定重复的节拍。100 MHz 表示每秒约一亿个周期。通信电路以它为参考，实际的数据传输速率取决于链路协商结果。 [PCI-SIG 共同时钟说明](https://pcisig.com/blog/seamless-transition-pcie%C2%AE-50-technology-system-implementations-webinar-qa)

## PERST# 的「低 → 高」是什么意思

把硬件的一根控制线想成两档开关。SSD 能把较低和较高的两种电压范围识别为逻辑 `0` 和 `1`。PERST 后面的 `#` 提醒你这根线是**低有效**的，所以 `0` 对应复位正在生效，`1` 对应复位解除。这里的「高」指控制线被识别为逻辑 `1`，其电压由接口设计定义。图里的 `3.3 V` 单列为 SSD 的主电源。 [Intel 信号定义](https://www.intel.com/content/dam/www/public/us/en/documents/technical-specifications/pci-express-gen4-retimer-supplemental-features.pdf)

## ASCII 时序图

```text
常见共同时钟路径示意，时间从左往右 →

3.3 V   ____/----------------------------------  稳定供电
REFCLK  _________/¯\_/¯\_/¯\_/¯\_/¯\_/¯\_/¯\_  稳定重复
PERST#  ___________________/-------------------  放开复位
        低：按住复位        ↑ 高：释放
                               └→ PCIe 两端开始建立连接
```

图里先画电和节拍就绪，再画 PERST# 释放，横线长度只表示先后。实际板子何时打开时钟、等待多久，要看这一块主板的时钟方案和 M.2 实现。正常关机时平台可把 PERST# 从高拉到低，再撤掉电。要分辨「盘正在复位」和「盘已经没电」，需要分别看复位线和盘端 3.3 V。 [PCI-SIG M.2 上电要求修订](https://pcisig.com/PCIExpress/ECN/M.2/Power-uprequirementsforPCIesidebandsPERST_etc.) · [Intel 时钟稳定与释放复位示例](https://www.intel.com/programmable/technical-pdfs/683059.pdf)

## 关键要点

- `REFCLK` 和 `PERST#` 是两个词。原图的「低 → 高」只修饰 `PERST#`。
- 主板给盘供电、给参考时钟和控制复位，属于插槽引脚、电压和时钟层面的动作。
- PCIe 链路训练是接下来的事。图里先认出复位释放，再往下找数据线路上的活动。

## 相关

- [NVMe SSD 开关机读图指南](../storage/nvme-power-cycle-guide.md)
- [从 PCIe 建链到 NVMe 读盘](pcie-nvme-queues-and-packets.md)
- [保存、上锁、关停和断电](../storage/nvme-shutdown-and-power-loss.md)
