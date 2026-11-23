---
title: FabricZoningModel网络分域模型
summary: 将配置态ZoneDBConfig与强制态ZoneDBActive分离，ZoneGroup是激活单元，Zone是访问控制单元，支持从NQN-only到NQN/IP/protocol/service/PortID的精确身份维度组合
sources:
- nvme-architecture-map.md
kind: concept
createdAt: '2026-08-16T06:18:41.230Z'
updatedAt: '2026-08-16T06:18:41.230Z'
tags:
- NVMe-Fabrics
- 访问控制
- 网络安全
aliases:
- fabriczoningmodel网络分域模型
confidence: 0.86
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: '[[fabric-zoning|Fabric Zoning]] Model 是 [[nvme-over-fabrics|NVMe over
  Fabrics]] 架构中用于在 IP 网络上实现访问控制的机制。该模型通过在 NVM 子系统和 Host 之间建立逻辑分区，限制特定 Host 只能访问被授权的存储资源，从而实现多租户环境下的安全隔离。'
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# [[fabric-zoning|Fabric Zoning]] Model（网络分域模型）

[[fabric-zoning|Fabric Zoning]] Model 是 [[nvme-over-fabrics|NVMe over Fabrics]] 架构中用于在 IP 网络上实现访问控制的机制。该模型通过在 NVM 子系统和 Host 之间建立逻辑分区，限制特定 Host 只能访问被授权的存储资源，从而实现多租户环境下的安全隔离。

## 核心概念

### 配置态与强制态分离

[[fabric-zoning|Fabric Zoning]] Model 将状态分为两个独立的平面：

- **ZoneDBConfig（配置态）**：存储 Zone 的配置信息，包括成员资格、属性等可变参数。
- **ZoneDBActive（强制态）**：存储实际生效的访问控制决策，用于在运行时执行过滤。

这种分离设计允许管理员先更新配置，待激活后配置态数据才成为强制态约束，实现配置变更与访问控制的解耦。 ^[nvme-architecture-map.md:150] ^[nvme-architecture-map.md:150]

### ZoneGroup 与 Zone

- **ZoneGroup**：作为激活单元（activation unit），管理一组 Zone 的激活状态。
- **Zone**：作为访问控制单元（access-control unit），定义具体的成员资格和属性。

Zone 的可变尾部存放成员信息和属性数据，而实际的 key 查找和片段传输由 网络分域数据传输 负责完成。 ^[nvme-architecture-map.md:150]

## 分域操作模式

Zoning operations 在语义上提供两种控制方向 ^[nvme-architecture-map.md:152]：

### Push 模式（推送模式）

1. DDC（Discovery Controller）以 FZL（Fabric Zoning Key）获得紧凑 key
2. 随后主动执行 FZR（Fabric Zoning Read）和 FZS（Fabric Zoning Synchronize）操作

### Pull 模式（拉取模式）

1. DDC 先通过异步事件和请求日志（request log）交付 Transaction ID
2. 再由 CDC（Central Discovery Controller）主动执行 FZR/FZS
3. Pull-model zoning 使用统一 operation-status 集合结束 GAZ/AAZ/RAZ
4. 并复用 AEN/request-log 通道触发 CDC 以 SDLP 反向投递 Discovery log ^[nvme-architecture-map.md:154]

## 访问控制操作

### 三种边界操作

- **GAZ（Get All Zones）**：以完整快照为读取边界，用于获取所有 Zone 的配置。
- **AAZ（Activate All Zones）**：以锁、全片接收和 generation 递增为提交边界，用于激活配置变更。
- **RAZ（Remove All Zones）**：受相同的存在性、锁定与 originator 授权检查约束，用于清除分区配置。 ^[nvme-architecture-map.md:152]

### 操作约束

所有操作均受以下约束 ^[nvme-architecture-map.md:152]：

- 存在性检查
- 锁定状态检查
- 发起者授权验证

## 成员资格与身份维度

Zone member 类型决定 enforcement 可使用的身份维度 ^[nvme-architecture-map.md:166]：

| 维度 | 说明 |
|------|------|
| NQN-only | 仅基于 NVM Qualified Name 匹配 |
| NQN + IP | NQN 与 IP 地址组合 |
| Protocol | 传输协议类型 |
| Service | 服务类型 |
| PortID | 端口标识符 |

未编码的维度不得参与匹配。这种多维度设计允许管理员根据安全需求选择合适的匹配精度。

## 通信范围限制

Zone 只允许 Host 与 [[nvm-subsystem|NVM Subsystem]] 互通 ^[nvme-architecture-map.md:166]：

- 激活时展开 ZoneAlias
- 可通过 property 请求实现逐包网络级强制

## 相关概念

- 网络发现与认证：Zoning 与 Discovery Service 的集成
- 网络分域数据传输：Zone 数据的 key 查找与片段传输机制
- 导出资源与底层资源：exported-resource management 与 ENSID 关联
- 命名空间管理生命周期：export 管理流程与分域配置的协同

## Sources

^[nvme-architecture-map.md]

