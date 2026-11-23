---
type: Concept
title: Firmware Update、Metadata Compatibility 与 Rollback
description: Firmware update 是 SSD 产品生命周期中最容易把协议、FTL metadata、安全、掉电恢复和现场可维护性缠在一起的路径。一个能执行
  NVMe Firmware Download/Commit 的控制器，不等于有安全的升级和回滚设计。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Firmware Update、Metadata Compatibility 与 Rollback

Firmware update 是 SSD 产品生命周期中最容易把协议、FTL metadata、安全、掉电恢复和现场可维护性缠在一起的路径。一个能执行 NVMe Firmware Download/Commit 的控制器，不等于有安全的升级和回滚设计。

## 设计目标

- 固件镜像下载、校验、暂存、提交、激活和回滚状态可追踪。
- activation 期间掉电或 reset 后，设备能选择一个可启动、可解释的 firmware slot。
- 新旧固件对 FTL metadata layout、journal、checkpoint、telemetry 和 feature flags 的兼容关系明确。
- signed firmware、anti-rollback/security version 和现场救援路径不互相冲突。
- host-visible firmware log、activation status、persistent event log 能解释升级历史。

与平台兼容、sanitize、secure erase 和 TCG/Opal 相关的边界见 [平台兼容与安全擦除](platform-compatibility-security.md)。
升级后的遥测和现场调试需求见 [遥测、日志与现场调试](telemetry-logging-field-debug.md)。

## 核心对象

| 对象 | 内容 | 设计关注点 |
|---|---|---|
| Firmware image | code、config、manifest、signature、hash、build ID | 完整性、来源、SKU/BOM 匹配 |
| Staging area | download 暂存区 | 分片下载、断点、CRC、掉电清理 |
| Slot table | active slot、pending slot、previous-good slot、factory slot | 原子切换、双副本、generation |
| Compatibility manifest | metadata layout version、min/max supported firmware、feature flags | 是否允许升级、是否允许回滚 |
| Security version counter | anti-rollback 计数或 fuse/secure storage | 安全回滚与现场救援冲突 |
| Activation record | commit action、reset required、activation pending、commit marker | reset/power loss 后恢复 |
| Health gate | boot self-test、metadata migration status、panic counter | 决定新固件是否 good |

## NVMe 可见路径

| 阶段 | Host 可见行为 | 内部动作 | 关键风险 |
|---|---|---|---|
| Firmware Download | host 分片写入 image | 写 staging area，校验 offset/range/hash | 分片乱序、掉电、空间不足 |
| Firmware Commit | host 指定 slot/action | 校验 manifest、signature、SKU、compatibility | 错 slot、签名失败、版本不兼容 |
| Activation pending | 可能需要 reset | 写 activation record 和 slot table pending | 记录半写入 |
| Reset / activation | controller reset 后选择 slot | bootloader 选择 pending slot 或 fallback | 新固件无法启动 |
| Post-activation validation | log/telemetry 显示新版本 | health gate、metadata migration、event log | metadata migration 失败 |
| Rollback | 回到 previous-good 或 factory | 检查 rollback eligibility 和 security version | anti-rollback 阻止救援 |

## Metadata Compatibility

固件升级最危险的部分通常不是代码替换，而是新旧固件如何解释已有介质元数据。

| 类型 | 示例 | 风险 | 策略 |
|---|---|---|---|
| Backward compatible | 新固件能读旧 checkpoint/journal | 迁移逻辑 bug | lazy migration + dual-read |
| Forward incompatible | 旧固件不能读新 metadata | 回滚后无法挂载 namespace | activation 前确认 rollback boundary |
| Bidirectional compatible | 新旧都能读同一 layout | 实现成本高 | 保守字段扩展、reserved field |
| One-way migration | 激活后升级 layout | 中途掉电或回滚破坏 | migration journal + explicit commit |
| Feature flag gated | 新固件启用新 FTL/SLC/FDP policy | field data 不一致 | per-feature enable record |

建议在 manifest 中记录：

- `metadata_layout_version`
- `min_supported_layout`
- `max_supported_layout`
- `rollback_safe_until_layout`
- `requires_migration`
- `migration_id`
- `feature_flags_added`
- `feature_flags_removed`

## Activation / Rollback 状态机

| 状态 | 触发 | 行为 | 可回退性 |
|---|---|---|---|
| Idle | 无 pending update | active slot 正常启动 | 保留 previous-good |
| Downloading | Firmware Download 开始 | 写 staging image 和 chunk map | 可丢弃 staging |
| Staged | image 完整并通过 hash/signature | 等待 commit | 可丢弃 staging |
| Commit pending | Firmware Commit 接受 | 写 pending slot、activation record | 可回 active |
| Activating | reset 后尝试 pending slot | boot new image，运行 self-test | 可回 previous-good |
| Migrating metadata | 新固件修改 layout | 写 migration journal | 取决于 migration boundary |
| Active provisional | 新固件运行但未标记 good | 观察 panic/error/telemetry | 可回 previous-good |
| Active good | health gate 通过 | 标记 previous-good 和 history | 回滚受 policy/security 限制 |
| Rollback | 新固件失败或 host 请求 | 回 previous-good/factory | 必须记录原因 |
| Recovery mode | 无 slot 可安全启动 | 暴露最小 admin/debug 能力 | 需要工厂或客户救援 |

## 掉电窗口

固件更新需要独立于普通 FTL 写路径的掉电窗口：

- image chunk 半写入。
- manifest/signature 校验完成前。
- slot table 半写入。
- activation record 半写入。
- pending slot 启动失败。
- metadata migration journal 半写入。
- new layout committed 但 previous-good 尚未更新。
- rollback record 半写入。

机器可读窗口见 [Firmware Update State Table](../../tests/faults/firmware-update-state-table.yml)。

## Rollback Policy

| 条件 | 允许回滚 | 不允许回滚或需特殊路径 |
|---|---|---|
| 只是 code bug，metadata layout 未改 | yes |  |
| 新固件启用 one-way metadata migration | 只在 migration commit 前 | commit 后需旧固件支持新 layout |
| security version 已提升 | 取决于 anti-rollback policy | 回旧版本可能被安全策略阻止 |
| previous-good slot 损坏 | no | 尝试 factory/recovery slot |
| 新固件导致 panic loop | yes, bootloader 自动回滚 | 需 panic counter 和 event log |
| host 显式请求 downgrade | 取决于 policy | 需签名、SKU、security version 检查 |

## 可观测性

至少记录：

- current firmware revision / active slot。
- previous-good slot / factory slot。
- pending activation slot。
- last update result。
- rollback reason。
- metadata layout version。
- migration status。
- signature/hash failure counter。
- panic/reset count after activation。
- update persistent event log。

## 验证点

- 分片 Firmware Download 顺序错误、重复、越界。
- Firmware Commit 到无效 slot 或不兼容 image。
- activation record 写入后掉电，恢复后 pending 状态可解释。
- 新固件启动失败，bootloader 回滚 previous-good。
- metadata migration 中掉电，重复恢复幂等。
- 新固件提升 layout 后，旧固件回滚 eligibility 被正确拒绝或进入 recovery。
- firmware update history 和 telemetry 能解释每次升级/失败/回滚。

## 关键来源

- NVM Express Specifications: https://nvmexpress.org/specifications/
- [SSD 内部的 NVMe 命令生命周期](nvme-command-lifecycle-in-ssd.md)
- [量产需求与合规](production-requirements-and-compliance.md)
- [掉电保护与恢复](power-loss-recovery.md)
- [FTL 元数据格式与恢复约定](ftl-metadata-format-and-recovery-conventions.md)
