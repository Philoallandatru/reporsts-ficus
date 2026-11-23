---
type: Concept
title: Reset、Boot 与 Power State 边界
description: SSD 设计里最容易混乱的地方之一，不是正常 I/O，而是 reset、boot、power state、firmware activation、sanitize
  和掉电恢复交叠时到底谁该负责什么。这个页面把这些边界单独拆开，方便做控制器状态机、主机互操作和异常恢复设计。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Reset、Boot 与 Power State 边界

SSD 设计里最容易混乱的地方之一，不是正常 I/O，而是 reset、boot、power state、firmware activation、sanitize 和掉电恢复交叠时到底谁该负责什么。这个页面把这些边界单独拆开，方便做控制器状态机、主机互操作和异常恢复设计。

## 为什么要单独拆开

- `controller reset`、`FLR`、`subsystem reset`、`PERST#`、`power cycle` 不是同一件事。
- `boot` 关注控制器从复位到可枚举、可接受命令的过程。
- `power state` 关注设备在运行、低功耗、非运行和关机路径中的可见语义。
- `firmware activation` 和 `power loss recovery` 都可能在 reset 前后切换可用镜像，但它们不是同一种恢复机制。

如果这些边界不拆清楚，常见后果是：

- 队列上下文在 reset 后残留，导致 host 看到不一致的 completion。
- HMB、映射缓存或 DMA 描述符在 disable 之后被错误复用。
- 固件激活中断后，设备无法判断应该回滚还是继续启动。
- 低功耗状态与真正的 shutdown 混在一起，测试结果在不同平台上不一致。

## 设计对象

| 对象 | 作用 | 是否必须持久化 |
|---|---|---|
| NVMe register block | host 看到的控制器状态、enable/ready/shutdown 语义 | 部分状态必须保持可解释 |
| Queue manager | SQ/CQ 上下文、doorbell shadow、fetch progress | 通常在 reset 后重建 |
| Boot loader / bring-up flow | 从 reset 到 ready 的初始化序列 | 固件镜像本身是持久化的 |
| Power state manager | 运行、低功耗、非运行、关机之间的切换 | 状态机必须可恢复 |
| Firmware slot table | 当前镜像、备用镜像、pending activation 状态 | 必须跨重启存在 |
| Telemetry / event log | reset、boot failure、power transition、activation 记录 | 建议保留 |

## 常见动作的边界

| 动作 | 典型触发 | 主要职责 | 不能做什么 |
|---|---|---|---|
| Controller reset | host 发起 reset、driver reload | 清理 volatile queue/context，重建可运行状态 | 不能把非易失元数据当成已丢失 |
| FLR | function-level reset | 重置单功能视图和 host-visible 状态 | 不能跨 function 污染全局状态 |
| Subsystem reset | 更广域的控制器/子系统复位 | 清理共享上下文，进入更深层恢复 | 不能把安全状态和 boot 状态混为一谈 |
| PERST# | PCIe 级复位 | 清理链路和 endpoint 可见状态 | 不能默认清除所有内部 NAND 元数据 |
| Power cycle | 真正断电再上电 | 触发完整 boot + recovery 流程 | 不能假设 volatile cache 还在 |
| Shutdown | host 正常关机 | 收尾、flush、标记 power-loss context | 不能替代掉电保护 |
| Firmware activation | 切换新镜像 | 选择 slot、执行 self-test、记录 pending | 不能在未完成验证时把新镜像永久标记为 good |

## 启动序列

一个可解释的 boot 流程通常包括：

1. 最小硬件上电。
2. 读取 reset reason、power-loss marker、firmware slot 状态。
3. 恢复必要的非易失 metadata。
4. 选择 boot slot 或 fallback slot。
5. 重建 NVMe register block 的 host-visible 语义。
6. 重新初始化 queue manager、DMA、flash scheduler 和必要的缓存。
7. 进入 ready，允许 host 重新发命令。

这条路径和掉电恢复有关，但不是同一个页面的重复。这里关注的是“设备怎样重新可用”；掉电恢复更关注“数据和元数据怎样不丢”。

## Power state 语义

| 状态 | 设计意图 | 风险 |
|---|---|---|
| Active / operational | 正常处理 I/O | 后台任务和前台 I/O 抢占带宽 |
| Idle / low power | 降低功耗但保持可恢复 | 唤醒延迟和队列状态耦合 |
| Standby / non-operational | 更深层省电 | host 以为还能快速恢复，但内部状态已经收缩 |
| Shutdown preparation | 准备离开运行态 | 若和 flush、journal commit 重叠，容易出现边界错误 |
| D3cold / external power loss | 设备可能失去大部分易失状态 | 如果把它误认为普通 reset，会高估恢复能力 |

设备必须为每个 power state 说明：

- 哪些 register 或 cache state 保留。
- 哪些队列上下文会失效。
- 哪些后台任务必须暂停。
- 恢复后 host 应该看到什么错误或延迟。

## Firmware activation 与 boot 的关系

Firmware activation 不是单纯的镜像替换，它会穿过 boot 边界：

- `download` 通常是 staging。
- `commit` 可能只是写入 activation record。
- `activate` 或 `reset required` 之后，新的 slot 才真正参与 boot。
- 如果 self-test 失败，bootloader 需要能回到 previous-good slot。

因此，firmware slot table 至少要记录：

- current slot。
- pending slot。
- previous-good slot。
- activation status。
- panic / reset counter。

## 推荐状态字段

| 字段 | 用途 | 备注 |
|---|---|---|
| reset_reason | 区分 controller reset、FLR、PERST#、power loss | 便于现场排障 |
| power_transition_reason | 区分 idle、standby、shutdown、wake | 便于验证功耗路径 |
| boot_generation | 标记一次 boot 尝试 | 便于判定是否回滚 |
| firmware_slot_active | 当前运行镜像 | 必须能在 telemetry 中读到 |
| firmware_slot_pending | 待激活镜像 | 需要和 reset 语义配对 |
| init_stage | bring-up 所处阶段 | 用于精确定位 boot 卡点 |
| queue_recovery_state | queue 是否已重建 | 避免 host 误判 |

## 验证点

- controller reset、FLR、PERST# 和 power cycle 的 host-visible 结果不同，但都能解释。
- reset 后 volatile queue/context 不被错误复用。
- boot 失败时能自动回退到 previous-good firmware slot。
- power state 切换不会破坏掉电恢复的非易失元数据。
- shutdown、firmware activation 和 sanitize 的事件顺序可以在 telemetry 中重建。

## 与本库其他页面的关系

- 主机侧 reset / queue 语义见 [NVMe 寄存器、队列与状态机](nvme-register-queue-state.md)。
- 固件更新和回滚见 [Firmware Update、Metadata Compatibility 与 Rollback](firmware-update-rollback.md)。
- 真正的掉电恢复边界见 [掉电保护与恢复](power-loss-recovery.md)。
- 平台兼容和安全擦除见 [平台兼容与安全擦除](platform-compatibility-security.md)。
- 现场调试和 reset / power 事件记录见 [遥测、日志与现场调试](telemetry-logging-field-debug.md)。

## 关键来源

- NVM Express Specifications: https://nvmexpress.org/specifications/
- Linux Kernel NVMe documentation: https://docs.kernel.org/nvme/index.html
- PCI-SIG Specifications: https://pcisig.com/specifications
- OCP Documents: https://www.opencompute.org/documents
- [Firmware Update、Metadata Compatibility 与 Rollback](firmware-update-rollback.md)
- [掉电保护与恢复](power-loss-recovery.md)
