---
type: Concept
title: 仿真、验证与测试平台
description: SSD 设计验证需要分层：协议互操作、固件状态机、FTL 策略、NAND 错误模型、性能/QoS 和掉电恢复无法靠单一工具覆盖。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 仿真、验证与测试平台

SSD 设计验证需要分层：协议互操作、固件状态机、FTL 策略、NAND 错误模型、性能/QoS 和掉电恢复无法靠单一工具覆盖。

## 平台对比

| 平台 | 最适合 | 不适合 |
|---|---|---|
| FEMU | Linux/QEMU 环境下跑 NVMe SSD emulation、ZNS/OpenChannel/whitebox 实验 | 精确 NAND 电气时序或产品级固件验证 |
| SimpleSSD | Full-system SSD architecture simulation、FTL/latency 模型 | 与真实 NVMe 设备互操作 |
| MQSim | 参数化 SSD 架构和 multi-queue 行为研究 | 直接复用为固件代码 |
| Cosmos+ OpenSSD | 阅读固件/硬件如何协作、FPGA SSD controller 教学 | 现代商用 SSD 全功能覆盖 |
| SPDK | 主机侧高性能 NVMe 命令生成、队列与 latency 实验 | 设备内部 NAND/FTL 验证 |
| Linux NVMe | 互操作、reset、quirk、kernel behavior | 产品内部策略建模 |

## 验证维度

- 协议：Identify、queue create/delete、doorbell、interrupt、reset、shutdown、firmware download/commit、format、sanitize、log。
- 数据一致性：写后读、flush/fua、write zeroes、discard/deallocate、metadata/protection information。
- FTL：映射更新、GC、wear leveling、over-provisioning、hot/cold separation、SLC cache。
- NAND 错误：program fail、erase fail、uncorrectable read、read retry、retention、read disturb。
- 掉电：随机插入 power fail，检查恢复后 mapping、journal、data durability。
- 性能：队列深度、随机/顺序、混合读写、尾延迟、后台任务干扰。

## 推荐工作流

1. 用 SPDK 或 nvme-cli 生成可复现命令序列。
2. 在 FEMU 或 Linux NVMe target 中观察主机侧协议路径。
3. 在 SimpleSSD/MQSim 中扫架构参数和 FTL 策略。
4. 在 Cosmos+ 中对照固件 request scheduler、buffer manager、NAND request lifecycle。
5. 把关键异常变成测试矩阵：触发条件、预期状态、恢复路径、可观测日志。

## 关键来源

- FEMU: https://github.com/MoatLab/FEMU
- SimpleSSD: https://github.com/SimpleSSD/SimpleSSD
- MQSim: https://github.com/CMU-SAFARI/MQSim
- SPDK NVMe documentation: https://spdk.io/doc/nvme.html
- Linux Kernel NVMe documentation: https://docs.kernel.org/nvme/index.html
- nvme-cli: https://github.com/linux-nvme/nvme-cli
