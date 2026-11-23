---
title: Fabrics发现与认证
summary: IP fabric上通过DNS-SD PTR/SRV/TXT记录引导控制器地址，Discover Service在连接前指明可达子系统路径，secure-channel与in-band-authentication门控命令接受
sources:
- nvme-architecture-map.md
kind: concept
createdAt: '2026-08-16T06:18:22.804Z'
updatedAt: '2026-08-16T06:18:22.804Z'
tags:
- NVMe-Fabrics
- 网络存储
- 安全认证
aliases:
- fabrics发现与认证
confidence: 0.89
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: Fabrics 发现与认证（Fabrics Discovery and Authentication）是 [[nvme-over-fabrics|NVMe
  over Fabrics]] 协议栈中两个相互独立但协同工作的安全入口，共同确保远端子系统访问的可控性与身份可信性。
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Fabrics 发现与认证

Fabrics 发现与认证（Fabrics Discovery and Authentication）是 [[nvme-over-fabrics|NVMe over Fabrics]] 协议栈中两个相互独立但协同工作的安全入口，共同确保远端子系统访问的可控性与身份可信性。

## 发现服务

在 message-based transport（如 Fabrics）上，Discovery Service 在 host 连接前指明可达子系统的路径。发现服务通过集中化的注册与访问控制机制，将 host 与 NVM 子系统的可达性信息汇集到一条控制链中。^[nvme-architecture-map.md:20]

IP-fabric 上的 Fabrics Discovery and Authentication 在 Connect 命令执行之前，通过 DNS-SD 的 PTR、SRV、TXT、A 以及 AAAA 记录 bootstrap 控制器地址。`_cdc` 查询用于协调 DDC（Discovery Controller）到 CDC（Centralized Discovery Controller）的注册行为。^[nvme-architecture-map.md:112]

### 发现日志

Discovery log 协商 host 过滤的、port 局的、包含全部 subsystem 的以及带扩展条目的视图。Multi-command 读取是一个经过 generation 校验的快照。每条记录既可以是一条 referral、一个具备 namespace 能力的 subsystem 路径，也可以是回到当前 Discovery Service 的另一路径。^[nvme-architecture-map.md:222]

同一个 discovery 平面还暴露已注册 host 与 AVE（Access Validation Engine）清单，以及一个 pull-model DDC-to-CDC 请求通道。^[nvme-architecture-map.md:224]

### 集中化发现

IP-based centralized discovery 把注册与访问控制接成一条控制链：host/DDC 通过 push 或 pull 向 CDC 汇集记录，CDC 返回经过 [[Fabric Zoning]] 过滤的 Discovery log；变更再由 AER（Asynchronous Event Request）驱动 host 重读。Pull 模式由 CDC 反向 Connect 到 DDC 并用 `Get Log Page(LID=70h)` 替换该 DDC 的旧快照。^[nvme-architecture-map.md:148]

## 安全入口

Fabrics 安全入口有两个独立门：transport-specific secure channel 必须在 TREQ（Transport Requirements）要求时先于 capsule 传输建立；Connect 后的 NVMe in-band authentication 则通过 Authentication Send/Receive 命令完成。二者可以同时存在，并使用不同的 transport 与 NVMe 身份。^[nvme-architecture-map.md:156]

### 安全通道

Transport-specific secure channel 提供传输层的安全保障，其建立先于任何 NVMe 命令胶囊的交换。

### 带内认证

带内认证是 queue-local 的 soft-state transaction。Discovery well-known NQN 只适合单向认证，而 unique Discovery Service NQN 才能绑定双向身份。认证可以在不安全 Admin connection 上派生 TLS PSK（Pre-Shared Key），随后必须断开旧连接并以该 PSK 建立新的安全 Admin/I/O queue；重认证超时不会撤销先前认证。^[nvme-architecture-map.md:158]

## 认证协议

### DH-HMAC-CHAP

DH-HMAC-CHAP 在同一 `T_ID` 下把参数协商、controller challenge、host proof 与可选的反向 proof 串成严格状态机。NULL DH 会降级为 HMAC-CHAP，且不能与 secure-channel concatenation 同用；任何消息顺序、payload 或 proof 错误都以有方向的 AUTH_Failure 结束并断开连接。^[nvme-architecture-map.md:160]

### Access Validation Engine

AVE（Access Validation Engine）把 verification 从 NVMe entity 委托给按 NQN 索引 key 的服务。Entity 通过 TLS 1.3 + `PSKea` 发送携带交易上下文的 Access-Request，AVE 回传匹配 ID 的 Access-Result。AVE 地址可配置或经 Discovery [[controller|Controller]] 发现。^[nvme-architecture-map.md:162]

## 认证与连接的交互

在 Controller initialization 过程中，Fabrics [[controller|Controller]] 建立连接、Connect Admin queue pair，并在被请求时执行认证，两者随后选择合法的 capability 配置、enable、Identify、枚举 namespace 并创建 I/O queue。^[nvme-architecture-map.md:52]

带内认证完成后，得到的 [[queue-pair|Queue Pair]] 可被认证门控；SQ 容量通过有序的 `SQHD` 更新释放，或者当 SQ flow control 被禁用时由 host 自行管理；Completion Queue 不存在 NVMe 层面的指针流控。^[nvme-architecture-map.md:48]

---

## Sources

^[nvme-architecture-map.md]

