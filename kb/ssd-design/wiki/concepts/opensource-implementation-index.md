---
type: Concept
title: 开源实现索引
description: 机器可读 commit 固定清单见 [Open-source Implementation Pins](../../sources/open-source-implementation-pins.yml)。构建和冒烟验证口径见
  [Implementation Smoke-test Matrix](../../sources/implementation...
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 开源实现索引

机器可读 commit 固定清单见 [Open-source Implementation Pins](../../sources/open-source-implementation-pins.yml)。构建和冒烟验证口径见 [Implementation Smoke-test Matrix](../../sources/implementation-smoke-test-matrix.yml)。本页用于阅读导向；具体版本、分支和 query date 以 pin 文件为准。

## Cosmos+ OpenSSD

- URL: https://cosmos-plus-openssd-doc.readthedocs.io/
- Source: https://github.com/Cosmos-OpenSSD/Cosmos-plus-OpenSSD
- Pinned: [78601486bb5581e40628ec7e841dea8e97eff034](https://github.com/Cosmos-OpenSSD/Cosmos-plus-OpenSSD/tree/78601486bb5581e40628ec7e841dea8e97eff034)
- 重点阅读：固件 request 队列、NAND request、buffer management、scheduler、flash controller register。
- 适合回答：一个可运行的教学 SSD 控制器如何划分固件与硬件职责。

## FEMU

- URL: https://github.com/MoatLab/FEMU
- Pinned: [46e4261f997e39a6184febe8148a6c3449719119](https://github.com/MoatLab/FEMU/tree/46e4261f997e39a6184febe8148a6c3449719119)
- 重点阅读：NVMe emulation、不同 SSD mode、timing model、ZNS/OpenChannel support。
- 适合回答：如何在系统级实验中控制 SSD 行为并观察主机栈。

## SimpleSSD

- URL: https://github.com/SimpleSSD/SimpleSSD
- Pinned: [2be371619a6533821741540ee2d8ce742c2dad2d](https://github.com/SimpleSSD/SimpleSSD/tree/2be371619a6533821741540ee2d8ce742c2dad2d)
- 重点阅读：controller、FTL、PAL/NAND model、latency model。
- 适合回答：FTL 和 NAND 并行结构如何影响性能。

## MQSim

- URL: https://github.com/CMU-SAFARI/MQSim
- Pinned: [51f0f2d3fed92d88ef4a0fa61a38024b07bf9d16](https://github.com/CMU-SAFARI/MQSim/tree/51f0f2d3fed92d88ef4a0fa61a38024b07bf9d16)
- 重点阅读：SSD configuration、flash channel/package/die/plane model、I/O scheduler、FTL model。
- 适合回答：多队列 SSD 的架构参数和工作负载如何影响 QoS。

## SPDK

- URL: https://github.com/spdk/spdk
- Docs: https://spdk.io/doc/nvme.html
- Pinned: [804a8090b158cbaef613431711afbaefbc76e2ee](https://github.com/spdk/spdk/tree/804a8090b158cbaef613431711afbaefbc76e2ee)
- 重点阅读：NVMe controller attach、queue pair、polling、bdev、FTL module。
- 适合回答：高性能主机侧如何驱动 NVMe 设备。

## Linux NVMe

- Docs: https://docs.kernel.org/nvme/index.html
- Source: https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/nvme
- Pinned mirror ref: [f5bbbfec59b4e2fb7520a91de3df8a6174325d6a](https://github.com/torvalds/linux/tree/f5bbbfec59b4e2fb7520a91de3df8a6174325d6a/drivers/nvme)
- 重点阅读：host driver、target、PCI transport、fabrics、feature/quirk policy。
- 适合回答：真实操作系统如何处理 NVMe 设备、兼容性和异常。

## nvme-cli

- URL: https://github.com/linux-nvme/nvme-cli
- Pinned: [0a77a7d326e509ad1464bcf49ed130df82312871](https://github.com/linux-nvme/nvme-cli/tree/0a77a7d326e509ad1464bcf49ed130df82312871)
- 重点阅读：identify、get-log、fw-download、fw-commit、format、sanitize、self-test。
- 适合回答：如何生成标准 NVMe 管理命令验证设备行为。

## Open-Channel SSD / LightNVM

- Docs: https://openchannelssd.readthedocs.io/
- Historical qemu-nvme pinned ref: [b6fb7eb1e9d708b920f24b559c503e68d0eb0329](https://github.com/OpenChannelSSD/qemu-nvme/tree/b6fb7eb1e9d708b920f24b559c503e68d0eb0329)
- 重点阅读：host-managed FTL、pblk、geometry、bad block、chunk/line abstraction。
- 适合回答：如果把部分 FTL 暴露给 host，设备/主机边界如何变化。
