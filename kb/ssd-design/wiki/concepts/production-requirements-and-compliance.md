---
type: Concept
title: 量产需求与合规
description: 工程原型能读写不代表 SSD 产品可发布。量产 SSD 需要在规范合规、互操作、可靠性、可制造性、可维护性和现场诊断上闭环。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 量产需求与合规

工程原型能读写不代表 SSD 产品可发布。量产 SSD 需要在规范合规、互操作、可靠性、可制造性、可维护性和现场诊断上闭环。

## 需求来源

| 来源 | 典型要求 |
|---|---|
| NVMe | 命令、队列、features、logs、reset、firmware update、sanitize、power state |
| PCIe | 链路训练、配置空间、AER、低功耗状态、信号完整性 |
| ONFI/JESD/vendor datasheet | NAND command/timing、坏块、可靠性、电源条件 |
| JEDEC JESD218/JESD219 | Endurance rating、workload、UBER/TBW 口径 |
| OCP Data Center NVMe SSD | 数据中心 telemetry、power、thermal、fault reporting、管理要求 |
| SNIA/PTSI | 存储性能测试方法和行业术语 |
| 客户平台 | BIOS/UEFI、Linux/Windows、热插拔、固件更新、供应链安全 |

## 合规维度

- NVMe command behavior：合法字段、非法字段、状态码、命令影响范围。
- Reset behavior：controller reset、subsystem reset、FLR、PERST#、power cycle。
- Firmware lifecycle：download、commit、activation、rollback、slot 管理。
- Sanitize/format/security：数据销毁、crypto erase、状态日志。
- SMART/health/telemetry：温度、寿命、错误、persistent event。
- Power management：APST、non-operational power state、shutdown。
- Namespace management：format、attach、resize、multi-path 或 sharing 视产品而定。

更细的工程边界见 [平台兼容与安全擦除](platform-compatibility-security.md) 和 [Firmware Update、Metadata Compatibility 与 Rollback](firmware-update-rollback.md)。

遥测、日志和现场调试细节见 [遥测、日志与现场调试](telemetry-logging-field-debug.md)。

## 量产固件必须有的“可观测性”

- Build ID、版本、git hash 或等价标识。
- Feature flags 和 SKU capability table。
- Crash dump 或 panic reason。
- Persistent event log。
- Power-loss recovery counters。
- NAND bad block、P/E、RBER、retry、uncorrectable 统计。
- GC/WAF/free block/thermal throttle 统计。
- Firmware update history。

## 制造与校准

量产流程通常需要：

1. NAND 扫描和初始 bad block table。
2. 容量 binning 和 over-provisioning 配置。
3. Controller/NAND 绑定信息。
4. Firmware image、配置表、密钥或证书烧录。
5. 短测、老化、性能分档。
6. SMART 初始值和日志清理。
7. 序列号、model number、FRU/label 信息。

## 现场升级风险

- 同型号不同硬件 BOM 使用不同 firmware branch。
- Firmware activation 期间掉电。
- 新固件改变 metadata layout。
- 回滚路径和安全版本计数冲突。
- 客户平台对 reset timing 或 power state 有隐性依赖。

详细状态机见 [Firmware Update、Metadata Compatibility 与 Rollback](firmware-update-rollback.md)。机器可读策略和掉电窗口见 [Firmware Update Policy Matrix](../../tests/requirements/firmware-update-policy-matrix.yml) 与 [Firmware Update State Table](../../tests/faults/firmware-update-state-table.yml)。

## 验收清单

| 类别 | 必查项 |
|---|---|
| 协议 | NVMe compliance、PCIe compliance、OS interoperability |
| 数据 | Power-fail、flush/FUA、format/sanitize、metadata recovery |
| 可靠性 | Endurance、retention、read disturb、temperature、UBER |
| 性能 | Fresh/steady state、QoS、thermal、SLC cache full、low OP |
| 可维护 | Firmware update、logs、telemetry、field debug |
| 安全 | Secure boot、signed firmware、crypto erase、key management |

## 关键来源

- NVM Express Specifications: https://nvmexpress.org/specifications/
- PCI-SIG Specifications: https://pcisig.com/specifications
- OCP Documents: https://www.opencompute.org/documents
- JEDEC JESD218: https://www.jedec.org/standards-documents/docs/jesd218b02
- JEDEC JESD219: https://www.jedec.org/standards-documents/docs/jesd219a
- SNIA: https://www.snia.org/
