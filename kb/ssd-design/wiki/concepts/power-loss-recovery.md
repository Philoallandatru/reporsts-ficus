---
type: Concept
title: 掉电保护与恢复
description: 掉电保护不是单独的电容问题，而是硬件能量、固件持久化协议、FTL 元数据顺序和 NVMe 可见语义共同组成的系统设计。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 掉电保护与恢复

掉电保护不是单独的电容问题，而是硬件能量、固件持久化协议、FTL 元数据顺序和 NVMe 可见语义共同组成的系统设计。

## 设计目标

- 已向 host 报告成功的数据，在规范和设备声明的持久性范围内必须可恢复。
- 未报告成功的数据可以丢弃，但不能破坏已成功数据或元数据。
- 恢复过程必须能区分“完整写入”“部分写入”“旧版本仍有效”“需要重放日志”。
- 恢复时间要受控，不能每次上电都全盘扫描。

## FTL 持久化边界

掉电恢复真正依赖的不是“把所有状态都写一遍”，而是明确哪些对象必须跨重启存在：

- superblock：告诉恢复流程应该信哪一代 layout。
- checkpoint：给出一个可接受的全局快照。
- journal：记录 checkpoint 之后的增量变化。
- block table：记录 block 的当前状态、计数和坏块标记。
- page metadata：证明某个 physical page 是否真的是最新可恢复版本。

详细格式见 [FTL 元数据格式与恢复约定](ftl-metadata-format-and-recovery-conventions.md)。

## 硬件路径

| 模块 | 职责 | 关键问题 |
|---|---|---|
| Power fail detector | 检测输入电压下降，通知固件/硬件进入 emergency flow | 阈值、去抖、误触发、通知延迟 |
| Hold-up capacitor | 给控制器、DRAM、NAND 留出紧急写入能量 | 容量老化、温度、最坏功耗、写入预算 |
| Power domain control | 关闭非必要模块，把能量留给 metadata commit | 哪些模块必须保留：CPU、SRAM、NAND、DRAM refresh |
| Emergency flush engine | 把关键 buffer、journal、mapping delta 写入 NAND 或非易失区域 | 时间预算、失败处理、优先级 |

## 固件持久化模型

FTL 需要定义可恢复边界。一个常见模型是：

1. 用户数据先写入新 physical page。
2. 写入 journal entry，记录 LPN、新物理地址、旧物理地址、版本号。
3. journal entry 带 checksum、sequence number、commit marker。
4. 周期性 checkpoint 把完整 L2P/P2L 摘要落盘。
5. 恢复时加载最近 checkpoint，再按 sequence 重放 journal。

关键是不要只保存“最新 L2P”，还要能证明该 L2P 指向的数据页本身已经成功 program 并通过校验。

## NVMe 语义交界

需要特别核对：

- Volatile Write Cache Feature 是否启用。
- Flush 命令要求哪些缓存内容变为非易失。
- FUA 或等价语义是否绕过易失缓存。
- Shutdown notification 下，控制器应完成哪些内部收尾。
- Firmware activation、format、sanitize 期间掉电的恢复状态。
- Controller reset 与真实 power loss 的处理边界不同，不能混为一谈。

## 恢复流程

1. 上电初始化最小硬件，读取 superblock 和 checkpoint。
2. 校验 checkpoint generation、版本、CRC、介质位置。
3. 扫描 journal tail，按 sequence number 找到最后完整 entry。
4. 对每条 entry 检查数据页 program 状态和 metadata checksum。
5. 重建 L2P、P2L、block state、free pool。
6. 处理 interrupted GC、wear leveling、namespace operation、firmware update。
7. 进入 NVMe ready 前完成必要的介质一致性检查。

## 测试矩阵

| 注入点 | 预期 |
|---|---|
| DMA 完成前掉电 | 命令不可恢复为成功写入 |
| DMA 完成后、NAND program 前掉电 | 旧数据仍有效 |
| NAND program 中掉电 | 新页可能无效，旧映射必须保留 |
| NAND program 完成后、journal 前掉电 | 恢复策略必须明确选择旧版本或校验后接受新版本 |
| journal entry 写一半掉电 | 忽略不完整 entry |
| checkpoint 写一半掉电 | 使用上一个完整 checkpoint |
| GC 搬迁中掉电 | 不得丢失被搬迁 LBA，也不得复活旧版本 |
| firmware commit 中掉电 | 必须回到旧固件或进入可恢复的新固件状态 |

## 状态转换表

机器可读版本见 [Power-loss State Table](../../tests/faults/power-loss-state-table.yml)。该表把写路径和 GC 路径拆成 10 个掉电窗口，绑定 `REQ-PLP-001` 和 `T4-*` 测试。

| ID | 掉电窗口 | 恢复动作 | 验证 |
|---|---|---|---|
| PLP-WIN-001 | host DMA 完成前 | 丢弃未完成 command context，旧 L2P 保持权威 | T4-001 |
| PLP-WIN-002 | DMA 完成后、NAND program 前 | 丢弃 volatile buffer，除非存在完整 PLP emergency flush record | T4-001 |
| PLP-WIN-003 | NAND program 过程中 | 校验 page metadata、LPN、sequence 和 program 状态；否则保留旧映射 | T4-002 |
| PLP-WIN-004 | program 完成后、journal 前 | 显式选择旧映射或在 P2L scan 后接受 orphan page，不允许未提交 L2P 成为权威 | T4-002, T4-003 |
| PLP-WIN-005 | journal entry 半写入 | 在第一个 CRC/commit marker 不完整的 entry 处停止 replay | T4-003 |
| PLP-WIN-006 | journal 已提交、checkpoint 未包含 | 加载旧 checkpoint，再按 sequence 重放完整 journal | T4-003 |
| PLP-WIN-007 | checkpoint 或 superblock 半写入 | 选择最高的完整 generation；失败则回退上一代 | T4-004 |
| PLP-WIN-008 | GC copy 完成、L2P 未切换 | 旧 PPA 保持权威，未提交 copy 可丢弃或 retire | T4-005 |
| PLP-WIN-009 | GC L2P 已切换、旧页未 retire | 重放 mapping update，标记旧 PPA stale，修复 valid count | T4-005 |
| PLP-WIN-010 | GC erase boundary | retire record 不完整时保守扫描；完整时归还 free pool | T4-005 |

每个状态必须满足幂等性：同一介质状态重复上电恢复多次，不能在旧版本和新版本之间摇摆，也不能重复计数 valid page。

## 关键来源

- NVM Express Specifications: https://nvmexpress.org/specifications/
- SPDK FTL: https://spdk.io/doc/ftl.html
- Cosmos+ OpenSSD documentation: https://cosmos-plus-openssd-doc.readthedocs.io/
- OCP Documents: https://www.opencompute.org/documents
- JEDEC JESD218: https://www.jedec.org/standards-documents/docs/jesd218b02
