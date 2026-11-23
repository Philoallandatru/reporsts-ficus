---
type: Concept
title: 源码导读
description: 读 SSD 相关开源项目时，先明确“这个项目模拟或实现的是哪一层”。把 host driver、NVMe emulator、SSD simulator、FTL
  library 和 FPGA firmware 混在一起看，很容易得出错误边界。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 源码导读

读 SSD 相关开源项目时，先明确“这个项目模拟或实现的是哪一层”。把 host driver、NVMe emulator、SSD simulator、FTL library 和 FPGA firmware 混在一起看，很容易得出错误边界。

当前阅读版本见 [Open-source Implementation Pins](../../sources/open-source-implementation-pins.yml)。这些 pin 固定了远端 HEAD commit，但还不代表已经完成本地构建或 smoke test。后续复现实验的最小验收口径见 [Implementation Smoke-test Matrix](../../sources/implementation-smoke-test-matrix.yml)。

## Cosmos+ OpenSSD

先读官方文档，再读 firmware。关注：

- Request allocation 和队列结构。
- NVMe manager 如何把 command 转成内部 request。
- Buffer manager 如何管理 data buffer。
- Low-level scheduler 如何下发 NAND request。
- GreedyFTL 的映射、写入和 GC。

适合借鉴：固件模块边界、request lifecycle、FPGA SSD 原型组织。

不宜直接照搬：工具链、性能参数、现代 TLC/QLC/LDPC 细节。

## FEMU

先读 README 和论文，再看 QEMU 设备模型。关注：

- NVMe BAR/register/queue emulation。
- BlackBox、WhiteBox、OpenChannel、ZNS 不同 mode。
- Timing model 如何注入延迟。
- Host OS 如何看到这个虚拟设备。

适合借鉴：系统级实验平台、NVMe 行为改造、host stack interaction。

不宜直接照搬：真实 NAND 时序、硬件 pipeline、产品级 FTL 复杂度。

## SimpleSSD

关注：

- Host interface、controller、FTL、PAL/NAND model 的分层。
- 配置文件如何定义 channel、package、die、plane 和 timing。
- FTL 如何处理 read/write/trim 和 GC。

适合借鉴：架构参数实验、FTL 策略对性能的影响。

不宜直接照搬：具体固件接口和 ASIC 硬件结构。

## MQSim

关注：

- Workload definition。
- SSD configuration。
- Address mapping、transaction scheduling、flash chip model。
- Multi-queue 和 steady-state latency。

适合借鉴：端到端延迟建模、多队列 SSD 参数扫点。

不宜直接照搬：固件代码结构。

## SPDK

关注两个区域：`lib/nvme` 和 `lib/ftl`。

- `lib/nvme`：用户态 queue pair、controller attach、transport、polling。
- `lib/ftl`：L2P、relocation、metadata、recovery。

适合借鉴：高性能主机访问模型和公开工程化 FTL 思路。

不宜直接照搬：把 SPDK FTL 当成 SSD controller firmware；它的运行位置和失败模型不同。

## Linux NVMe

关注：

- Host PCI driver 的 probe/reset/queue setup。
- Core controller lifecycle。
- Namespace 扫描和 block layer 集成。
- Target 和 PCI endpoint target 文档。
- Feature and quirk policy。

适合借鉴：真实 OS 对 NVMe device 的期望、异常路径和兼容性。

不宜直接照搬：Linux host driver 不是设备固件。

## 阅读顺序建议

1. 用 Linux/SPDK/nvme-cli 理解 host 如何发命令。
2. 用 FEMU 看 host-visible NVMe device 行为如何被模拟。
3. 用 Cosmos+ 看真实固件如何组织 request。
4. 用 SimpleSSD/MQSim 分析 FTL 和 NAND 结构的性能影响。
5. 回到规范核对每个 host-visible 行为是否符合 NVMe/PCIe。

## 关键来源

- Cosmos+ OpenSSD: https://github.com/Cosmos-OpenSSD/Cosmos-plus-OpenSSD
- FEMU: https://github.com/MoatLab/FEMU
- SimpleSSD: https://github.com/SimpleSSD/SimpleSSD
- MQSim: https://github.com/CMU-SAFARI/MQSim
- SPDK: https://github.com/spdk/spdk
- Linux NVMe documentation: https://docs.kernel.org/nvme/index.html
- Open-source implementation pins: ../../sources/open-source-implementation-pins.yml
- Implementation smoke-test matrix: ../../sources/implementation-smoke-test-matrix.yml
