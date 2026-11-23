---
type: Concept
title: 控制器厂商数据采集与建模
description: 控制器厂商公开资料往往不是一份完整规格书，而是一组分散的产品页、brief、guide、white paper 和应用说明。要把这些材料变成
  SSD 控制器知识库能用的输入，需要一套稳定的采集流程。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 控制器厂商数据采集与建模

控制器厂商公开资料往往不是一份完整规格书，而是一组分散的产品页、brief、guide、white paper 和应用说明。要把这些材料变成 SSD 控制器知识库能用的输入，需要一套稳定的采集流程。

## 采集目标

这页的目标不是替代私有 datasheet，而是把公开资料变成可比较、可追溯的字段：

- 这家 vendor 的控制器公开承诺了什么。
- 它公开使用了哪些模块名和术语。
- 哪些能力只停留在 marketing 层。
- 哪些内容可以进入硬件边界、平台兼容、遥测和量产页面。

## 输入来源

| 来源 | 例子 | 主要作用 |
|---|---|---|
| 产品页 / brief | Microchip、Marvell、Silicon Motion、Phison、Innogrit、Maxio | 功能边界、代际、目标市场 |
| 产品指南 / guide | AMD PG329、NVMe target guide | 接口、模块边界、参考实现 |
| White paper / app note | security、telemetry、power、enterprise feature 白皮书 | 术语、风险点、产品能力语言 |
| 源码或公开项目 | Cosmos+、Linux NVMe、nvme-cli、SPDK | 交叉验证 vendor 语义是否合理 |

## 采集顺序

### 1. 固定资料身份

先记录：

- vendor。
- product family。
- document version。
- source URL。
- access date。
- 本地文件名。
- sha256。
- 是否公开。

如果是网页而不是 PDF，也应保留 URL 和访问日期。

### 2. 先抽功能边界

优先抽这些：

- PCIe generation。
- NVMe version。
- lane 数。
- DRAM-less / HMB 支持。
- enterprise / client 定位。
- telemetry / power / security 卖点。
- firmware download / commit / rollback 的公开表述。

这一步决定“厂商愿意公开承诺什么”。

### 3. 再抽接口和模块名

从 guide 或更详细资料里抽：

- register / queue / doorbell 名称。
- PRP / SGL / DMA 边界。
- NAND support 术语。
- ECC / LDPC / RAID-like 术语。
- host interface、controller front end、flash scheduler、memory controller 这些模块名。

这些词汇会影响知识库里的模块边界和验证表述。

### 4. 再抽生命周期语义

重点看：

- firmware download / commit / activation / rollback。
- secure boot / signed firmware。
- telemetry / health log / persistent event。
- factory test / diagnostics / recovery mode。
- platform compatibility 相关说明。

这些内容会直接影响量产、平台兼容和现场调试。

## 可信度分级

| 级别 | 说明 | 用途 |
|---|---|---|
| explicit product brief | 页面或 PDF 明确说出 | 可进入 vendor intake |
| guide / product guide | 更细但仍属公开参考 | 可用于接口和模块边界 |
| marketing language | 只有定位或卖点 | 只用于术语和 backlog |
| inferred | 从产品命名、市场定位或对标项目推断 | 仅供探索，不作事实 |

## 字段模板

每条记录至少包括：

- vendor。
- product family。
- source URL / file。
- access date。
- document version。
- sha256（如果可下载）。
- host interface。
- NAND interface（如果公开）。
- memory architecture。
- reliability / ECC。
- security。
- firmware lifecycle。
- telemetry / diagnostics。

## 常见误区

- 把 marketing feature list 当成可实现接口。
- 把 guide 里的模块名称直接当成 RTL 模块边界。
- 把“enterprise”或“client”当成统一功能集合，不区分具体代际。
- 把公开资料的术语误写成已验证实现细节。
- 没记录版本和 sha256，后面无法追溯。

## 输出去向

采集结果应进入：

- [Controller Vendor 公开资料 Intake](../../sources/vendor-intake/controller-vendor-public-materials.md)
- [控制器硬件模块边界](controller-hardware-module-boundaries.md)
- [控制器 RTL / IP 参考](controller-rtl-ip-reference.md)
- [量产需求与合规](production-requirements-and-compliance.md)
- [遥测、日志与现场调试](telemetry-logging-field-debug.md)

## 关键来源

- [Controller Vendor 公开资料 Intake](../../sources/vendor-intake/controller-vendor-public-materials.md)
- [控制器硬件模块边界](controller-hardware-module-boundaries.md)
- [控制器 RTL / IP 参考](controller-rtl-ip-reference.md)
- AMD PG329 NVMe Target Controller: https://docs.amd.com/r/en-US/pg329-nvme-target-controller
- Cosmos+ OpenSSD repository: https://github.com/Cosmos-OpenSSD/Cosmos-plus-OpenSSD
