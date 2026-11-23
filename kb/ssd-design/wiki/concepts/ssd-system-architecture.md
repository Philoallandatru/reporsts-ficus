---
type: Concept
title: SSD 系统架构
description: SSD 可以看成一个嵌入式存储系统：前端接受主机命令，后端管理 NAND 介质，中间由固件把块接口转换成可恢复、可磨损均衡、可并行执行的
  flash 操作。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# SSD 系统架构

SSD 可以看成一个嵌入式存储系统：前端接受主机命令，后端管理 NAND 介质，中间由固件把块接口转换成可恢复、可磨损均衡、可并行执行的 flash 操作。

## 主要模块

| 模块 | 职责 | 典型实现 |
|---|---|---|
| Host interface | PCIe endpoint、NVMe register、doorbell、MSI-X、中断聚合 | ASIC/FPGA 硬件加速，固件处理 Admin 与异常路径 |
| Command engine | 拉取 SQE、解析 opcode、维护 command context、写 CQE | 硬件队列 + firmware scheduler |
| DMA/data path | Host memory 与内部 SRAM/DRAM/NAND pipeline 之间搬运数据 | PCIe DMA、scatter-gather、metadata path |
| FTL | LBA 到物理页映射、写分配、GC、wear leveling、日志 | firmware + DRAM/SRAM metadata |
| Flash controller | NAND command/address/data phase、channel arbitration、timing | 多 channel/way 控制器 |
| ECC/LDPC | 编码、解码、soft read、read retry、uncorrectable 处理 | 硬件 pipeline + firmware policy |
| Reliability manager | 坏块、读干扰、保持期、温度、scrub、refresh | 固件后台任务 |
| Power-loss protection | 掉电检测、hold-up energy、emergency metadata commit | 模拟/数字电源管理 + 固件恢复协议 |

主机最先接触到的是 [NVMe 寄存器、队列与状态机](nvme-register-queue-state.md)：控制器能否枚举、enable、收发队列、reset 后重新进入可解释状态，决定后面的 FTL、NAND 和恢复机制是不是能真正落地。

## 数据路径

写请求通常经历：NVMe SQE 拉取、host buffer DMA、数据校验/加密/ECC、FTL 分配物理页、NAND program、映射表与日志更新、CQE 返回。为了降低尾延迟，很多 SSD 会在“数据与必要元数据达到可恢复条件”后完成命令，而不是等待全部后台整理完成。

读请求通常经历：NVMe SQE 拉取、查映射、调度 NAND read、ECC/LDPC 解码、必要时 read retry 或 RAID-like recovery、DMA 回 host、CQE 返回。

## 设计冲突

- 性能与写放大：更积极的并行写入可能增加未来 GC 成本。
- DRAM 成本与映射粒度：细粒度 page mapping 性能好但映射表大。
- 延迟与可靠性：强同步元数据更安全，但影响写延迟。
- QoS 与后台任务：GC、scrub、wear leveling 都会抢占 channel 和 die。
- 规范合规与内部自由度：NVMe 定义主机可见行为，内部 FTL 与 NAND 策略仍是实现选择。

## 关键来源

- NVM Express Specifications: https://nvmexpress.org/specifications/
- ONFI Specifications: https://onfi.org/specs.html
- Cosmos+ OpenSSD documentation: https://cosmos-plus-openssd-doc.readthedocs.io/
- SimpleSSD: https://github.com/SimpleSSD/SimpleSSD
