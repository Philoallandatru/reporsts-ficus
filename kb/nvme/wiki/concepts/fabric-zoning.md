---
title: Fabric Zoning
summary: NVMe over Fabrics 的访问控制机制，通过 ZoneGroup、Zone、ZoneMember 实现成员间的通信规则强制与网络限制。
sources:
- nvme-context.md
kind: concept
createdAt: '2026-08-16T06:20:52.271Z'
updatedAt: '2026-08-16T06:20:52.271Z'
tags:
- nvme
- fabrics
- access-control
- zoning
aliases:
- fabric-zoning
confidence: 0.95
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: Fabric Zoning 是 [[nvme-over-fabrics|NVMe over Fabrics]] (NVMe-oF) 架构中的一种访问控制机制，用于在共享的存储
  fabric 上隔离不同租户或应用组之间的通信。^[nvme-context.md:695-696]
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Fabric Zoning

Fabric Zoning 是 [[nvme-over-fabrics|NVMe over Fabrics]] (NVMe-oF) 架构中的一种访问控制机制，用于在共享的存储 fabric 上隔离不同租户或应用组之间的通信。^[nvme-context.md:695-696]

## 概述

Fabric Zoning 通过划分逻辑区域（Zone），使得同一 Zone 内的成员可以相互通信，而 Zone 之外的实体则受到访问限制。这一机制由 Centralized Discovery [[controller|Controller]] (CDC) 集中管理，支持基于 NQN、IP 地址、协议类型、服务端口或 PortID 等多种标识符定义访问规则。^[nvme-context.md:698-699]

## 核心概念

### Zone

Zone 是 Fabric Zoning 的访问控制单元，同一 Zone 内的成员按照该 Zone 定义的规则进行通信。Zone 规则通过 Zone Member 来描述，Zone Member 是一个固定 256 字节的类型化匹配项，包含 Role 与 NQN、IP、协议、服务端口或 PortID 的组合。类型未包含的维度不参与强制执行。^[nvme-context.md:695-696, nvme-context.md:698-699]

### ZoneGroup

ZoneGroup 是 Fabric Zoning 的激活单元，由 `{ZoneGroup Name, ZoneGroup Originator}` 唯一标识，并拥有 compact key 与 update generation。ZoneGroup 作为整体被激活或去激活，而非单独操作其中的 Zone。^[nvme-context.md:692-693]

### ZoneAlias

ZoneAlias 是 ZoneDBConfig 中可复用的 NVMe entity 分组。在 ZoneGroup 激活时，alias 引用会被解析为具体的成员。需要注意的是，ZoneAlias 不得包含其他 ZoneAlias 类型的成员。^[nvme-context.md:701-702]

### ZoneMember

ZoneMember 是定义 Zone 成员身份的基本元素。每个 ZoneMember 通过 Role（角色标识）结合 NQN、IP、协议、服务端口或 PortID 等属性来标识 host 或 NVM subsystem。^[nvme-context.md:698-699]

### Fabric Enforced Zone Property

Fabric Enforced Zone Property 是 Zone 上的一个 TLV（Type-Length-Value）提示，请求以逐包网络限制强制执行该 Zone 的规则。启用此属性后，网络设备可对跨 Zone 的流量进行硬件级过滤。该属性不改变 Zone 成员的 host↔subsystem 通信矩阵本身。^[nvme-context.md:704-705]

## 数据管理

### ZoneDBConfig

ZoneDBConfig 是 CDC Zoning database 中保存已配置的 ZoneGroups 与 ZoneAliases 的配置集合。ZoneDBConfig 定义了预期的配置状态，但不代表当前已强制执行的规则。^[nvme-context.md:686-687]

### ZoneDBActive

ZoneDBActive 是 CDC Zoning database 中当前生效的 ZoneGroup 集合。ZoneDBActive 驱动 Discovery-log filtering（发现日志过滤）、change notification（变更通知）以及可选的网络限制执行。^[nvme-context.md:689-690]

### ZoneGroup 操作

**Get Active ZoneGroup (GAZ)**：读取 ZoneDBActive 中完整 ZoneGroup 的操作。在 push model 中使用 lookup key 与 FZR（Fabric Zoning Response），在 pull model 中使用 Transaction ID 与 FZS（Fabric Zoning Status）。接收方在全部 fragment 到达前不得处理结果。^[nvme-context.md:707-708]

**Add/Replace Active ZoneGroup (AAZ)**：对 active ZoneGroup 的带锁原子更新。CDC 只在完整定义到达后更新并递增 generation。在 push model 中，超过 30 秒未收齐全部数据会丢弃数据并解锁。^[nvme-context.md:710-711]

**Remove Active ZoneGroup (RAZ)**：从 ZoneDBActive 删除指定 `{ZoneGroup Originator, ZoneGroup Name}` 的操作。目标缺失、被锁定或 originator 未授权都会导致操作失败。^[nvme-context.md:713-714]

### Fabric Zoning Data Key (ZDK)

ZDK 由 CDC 分配，在 Fabric Zoning Lookup 中返回。DDC（Direct Discovery Controller）据此选择一个 Zoning data 结构进行分片传输。^[nvme-context.md:539-540]

## 与 Centralized Discovery 的集成

Fabric Zoning 机制深度集成于 NVMe-oF 的发现服务体系中。Centralized Discovery [[controller|Controller]] 负责维护 Zoning database，并响应来自 Direct Discovery [[controller|Controller]] 或 host 的 ZoneGroup 查询与更新请求。在 push model 中，CDC 主动将 Zoning 数据推送给 DDC；在 pull model 中，DDC 通过 pull 机制从 CDC 获取 Zoning 数据。^[nvme-context.md:680-682, nvme-context.md:707-711]

## 相关概念

- Centralized Discovery Controller
- Direct Discovery Controller
- [[NVM Subsystem]]
- Discovery Service
- NVMe Qualified Name (NQN)

## Sources

- NVMe Base 2.1 知识上下文 (nvme-context.md) (`nvme-context.md:539-541, 686-714`)

