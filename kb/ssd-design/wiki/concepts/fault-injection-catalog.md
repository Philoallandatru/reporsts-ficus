---
type: Concept
title: 故障注入目录
description: SSD 的危险 bug 通常出现在“命令、DMA、FTL、NAND、掉电、reset、GC、ECC”交叠处。故障注入目录用于把这些交叠系统化。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 故障注入目录

SSD 的危险 bug 通常出现在“命令、DMA、FTL、NAND、掉电、reset、GC、ECC”交叠处。故障注入目录用于把这些交叠系统化。

## Host Interface 注入

| ID | 注入点 | 预期 |
|---|---|---|
| FI-HOST-001 | Invalid PRP address | 返回正确 NVMe status，不写错 host memory |
| FI-HOST-002 | PRP 跨越非法边界 | 命令失败，controller 不死锁 |
| FI-HOST-003 | SQE opcode 非法 | 返回 invalid opcode |
| FI-HOST-004 | Doorbell 快速乱序更新 | queue manager 保持一致 |
| FI-HOST-005 | MSI-X 丢失或延迟 | Polling 仍可回收 CQE |
| FI-HOST-006 | Controller reset during outstanding I/O | outstanding context 被清理或安全隔离 |

## FTL 注入

| ID | 注入点 | 预期 |
|---|---|---|
| FI-FTL-001 | L2P cache miss storm | 延迟可观测，不返回错数据 |
| FI-FTL-002 | Free block pool 低于 watermark | 触发 GC 或 host throttle |
| FI-FTL-003 | GC 搬迁页后 host overwrite 同一 LPN | 版本号防止旧数据复活 |
| FI-FTL-004 | Victim block valid count 错误 | 校验或恢复阻止误擦有效数据 |
| FI-FTL-005 | Journal entry CRC 错误 | 恢复时忽略 |
| FI-FTL-006 | Checkpoint 写一半 | 使用上一完整 checkpoint |

## NAND 注入

| ID | 注入点 | 预期 |
|---|---|---|
| FI-NAND-001 | Program fail | 换页/换块，旧映射保持有效 |
| FI-NAND-002 | Erase fail | block retire，bad block table 更新 |
| FI-NAND-003 | Read correctable high bit error | 上报 correction count，触发 refresh |
| FI-NAND-004 | Read uncorrectable | retry/parity/recovery，失败返回错误 |
| FI-NAND-005 | Channel timeout | request abort/retry，不拖死所有 channel |
| FI-NAND-006 | Bad block marker 异常 | 不把未知坏块加入 free pool |

## Power Loss 注入

| ID | 注入点 | 预期 |
|---|---|---|
| FI-PLP-001 | DMA in 之前掉电 | 不产生新写入 |
| FI-PLP-002 | DMA in 后、program 前掉电 | 旧数据仍有效 |
| FI-PLP-003 | Program 中掉电 | 新页不可假定有效 |
| FI-PLP-004 | Program 后、journal 前掉电 | 恢复策略可解释，不破坏旧数据 |
| FI-PLP-005 | Journal entry 半写入 | 忽略半 entry |
| FI-PLP-006 | Superblock 切换中掉电 | 找到上一完整 generation |
| FI-PLP-007 | GC erase 前掉电 | 不误释放 victim block |
| FI-PLP-008 | Firmware activation 中掉电 | 旧/新固件选择可重复 |

## Performance/QoS 注入

| ID | 注入点 | 预期 |
|---|---|---|
| FI-QOS-001 | 强制 GC active | 前台读 p999 在预算内或触发节流 |
| FI-QOS-002 | ECC soft decode storm | Read retry 不导致全系统饥饿 |
| FI-QOS-003 | Thermal throttle asserted | 性能下降可观测且不破坏数据 |
| FI-QOS-004 | SLC cache full | 写 cliff 可测，GC/destage 前向进展 |
| FI-QOS-005 | DRAM/HMB mapping cache pressure | Miss 统计和延迟可解释 |

## 工具建议

- Emulator：FEMU、SimpleSSD、MQSim。
- Host command：nvme-cli、libnvme、xNVMe、SPDK。
- Workload：fio、SPDK perf。
- Fault harness：自研 hook，至少支持按命令序号、LBA、PPN、channel/die、metadata sequence 注入。

## 关键来源

- [SSD 验证矩阵](ssd-verification-matrix.md)
- [验证证据与故障注入闭环](verification-evidence-and-fault-bridge.md)
- [掉电保护与恢复](power-loss-recovery.md)
- [ECC、LDPC 与可靠性管理](ecc-ldpc-reliability.md)
- FEMU: https://github.com/MoatLab/FEMU
- fio: https://github.com/axboe/fio
