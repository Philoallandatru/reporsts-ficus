---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: e3c0c8a71306b29cb9554bb14d52f434f20bb2ca6f825788bc850a6435b281bc
  pageDirectory: concepts
  sources:
    - nvme-context.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - dh-hmac-chap-authentication
  citations:
    - file: nvme-context.md
      start: 716
      end: 717
    - file: nvme-context.md
      start: 193
      end: 194
    - file: nvme-context.md
      start: 196
      end: 197
    - file: nvme-context.md
      start: 719
      end: 720
    - file: nvme-context.md
      start: 722
      end: 723
    - file: nvme-context.md
      start: 725
      end: 726
    - file: nvme-context.md
      start: 728
      end: 729
    - file: nvme-context.md
      start: 190
      end: 191
    - file: nvme-context.md
      start: 199
      end: 200
title: DH-HMAC-CHAP Authentication
description: NVMe In-band 认证协议，通过协商 hash/DH 参数、controller challenge、host proof 及可选 subsystem 反向 proof 完成安全认证事务。
tags:
  - nvme
  - security
  - authentication
  - fabrics
timestamp: "2026-08-16T06:20:28.029Z"
---


# DH-HMAC-CHAP 认证

DH-HMAC-CHAP（Diffie-Hellman Hash-based Message Authentication Code Challenge-Handshake Authentication Protocol）是 [NVMe over Fabrics](/concepts/nvme-over-fabrics.md) 协议中用于在 host 与 [Controller](/concepts/controller.md) 之间进行相互身份验证的机制，基于 Diffie-Hellman 密钥交换与 HMAC 挑战-响应协议实现。^[nvme-context.md:716-717]

## 概述

在 NVMe-oF 架构中，DH-HMAC-CHAP 认证位于 NVMe In-band Authentication 层面，作为 Connect 成功之后的一道安全门控。在认证完成之前，新建的所有 queue 只能处理认证相关命令，普通 I/O 命令被阻塞。^[nvme-context.md:193-194]

该认证机制通过 Authentication Transaction 的形式推进，由 `T_ID` 标识的同一事务上下文关联多个消息，参与方在单个 queue 上通过 Authentication Send/Receive 命令序列完成身份验证。^[nvme-context.md:196-197]

## 认证事务流程

DH-HMAC-CHAP 认证事务是一个由同一 `T_ID` 绑定的严格消息序列，包含以下四个阶段：

1. **协商阶段**：host 与 [Controller](/concepts/controller.md) 协商 hash 算法与 DH（Diffie-Hellman）参数
2. **Controller Challenge**：controller 向 host 发起挑战
3. **Host Proof**：host 提供响应证明
4. **可选的 Subsystem 反向证明**：controller 向 host 提供反向证明

整个流程中，顺序错误、payload 异常或 proof 验证失败都会导致连接终止。^[nvme-context.md:716-717]

## NULL DH Exchange

当 `DHgID=00h` 时，DH-HMAC-CHAP 采用 NULL DH Exchange 模式。该模式下不进行 DH exponential 交换，协议退化为纯 HMAC-CHAP 形式。此模式禁止用于 Secure Channel Concatenation 流程。^[nvme-context.md:719-720]

## Secret 表示形式

DH-HMAC-CHAP 使用 `DHHC-1:xx:<Base64>:` 格式的可交换 secret（exchangeable secret）。其中 hash identifier (`xx`) 决定是否将 secret 与 NQN 绑定派生为验证密钥。Base64 payload 末尾附加的 CRC-32 校验码用于配置录入时的数据完整性校验。^[nvme-context.md:722-723]

## Authentication Verification Entity

Authentication Verification Entity (AVE) 是代表 host 或 [Controller](/concepts/controller.md) 验证 DH-HMAC-CHAP 响应的专用服务。AVE 以 NQN 作为标识，通过 TLS 1.3 PSK 连接进行通信，并为每个受验证的实体维护以下信息：

- NQN（实体标识）
- Verification key（验证密钥）
- AVE-connection PSK（PSKea）^[nvme-context.md:725-726]

## AVE Connection PSK

AVE Connection PSK（PSKea）是某一 NVMe entity 与 AVE 之间共享的 TLS 1.3 预共享密钥。其派生上下文绑定 `NQNAVE`（AVE 的 NQN）与 `NQNe`（被验证实体的 NQN）。需要特别注意的是，PSKea 与 host-controller 之间直接认证产生的 TLS PSK 用途不同，前者专用于与 AVE 的通信安全。^[nvme-context.md:728-729]

## 与 Secure Channel 的关系

根据 Fabric Secure Channel 的要求，在控制器接受任何 NVMe Transport 命令之前必须先建立安全通道。Secure Channel Concatenation 流程允许在不可信的 Admin Queue 上通过认证事务生成 PSK，断开连接后，再用该 PSK 为后续的 Admin 与 I/O Queue 建立安全的传输通道。^[nvme-context.md:190-191, nvme-context.md:199-200]

## 重认证行为

初始认证具有门控普通命令的优先级——在认证完成前，queue 只能处理认证命令。重认证则不会先撤销已有的认证状态，允许在保持现有通信能力的同时更新认证凭证。^[nvme-context.md:196-197]

## 相关概念

- NVMe In-band Authentication
- Authentication Transaction
- Fabric Secure Channel
- Secure Channel Concatenation
- Authentication Verification Entity

## Sources

- nvme-context.md（NVM Express Base Specification Revision 2.1 概念词汇表）

# Citations

1. [nvme-context.md:716-717](/references/nvme-context-d9974722.md)
2. [nvme-context.md:193-194](/references/nvme-context-d9974722.md)
3. [nvme-context.md:196-197](/references/nvme-context-d9974722.md)
4. [nvme-context.md:719-720](/references/nvme-context-d9974722.md)
5. [nvme-context.md:722-723](/references/nvme-context-d9974722.md)
6. [nvme-context.md:725-726](/references/nvme-context-d9974722.md)
7. [nvme-context.md:728-729](/references/nvme-context-d9974722.md)
8. [nvme-context.md:190-191](/references/nvme-context-d9974722.md)
9. [nvme-context.md:199-200](/references/nvme-context-d9974722.md)
