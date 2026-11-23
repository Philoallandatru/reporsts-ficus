---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 3ea98fddd7ddf473f59ce2fe3d938eeafec5a5b2f08bea2a516579669480dd8f
  pageDirectory: concepts
  sources:
    - nvme-controller-initialization.md
  confidence: 0.9
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - nvme-of-fabrics-初始化
    - NF初
  citations:
    - file: nvme-controller-initialization.md
      start: 1
      end: 9
    - file: nvme-controller-initialization.md
      start: 82
      end: 89
    - file: nvme-controller-initialization.md
      start: 22
      end: 33
    - file: nvme-controller-initialization.md
      start: 78
      end: 89
    - file: nvme-controller-initialization.md
      start: 59
      end: 74
    - file: nvme-controller-initialization.md
      start: 91
      end: 123
    - file: nvme-controller-initialization.md
      start: 22
      end: 89
title: NVMe-oF Fabrics 初始化
description: 基于消息传输的控制器初始化方式，通过建立传输层连接、执行 Connect 命令创建 Admin 队列对、使用 Property Get/Set 访问属性，并在需要时执行身份认证。
tags:
  - Fabrics
  - NVMe-oF
  - 消息传输
timestamp: "2026-08-16T06:21:33.860Z"
---


# NVMe-oF Fabrics 初始化

NVMe-oF Fabrics 初始化是一个基于消息传输的启动过程，用于在 [NVMe over Fabrics](/concepts/nvme-over-fabrics.md) 网络中建立主机与控制器之间的连接并完成必要的配置。与基于内存的 PCIe 传输不同，Fabrics 初始化通过消息队列和远程过程调用实现控制器的发现与配置。 ^[nvme-controller-initialization.md:1-9]

## 初始化流程概述

NVMe-oF Fabrics 初始化主要完成以下工作：

- 建立传输层连接
- 通过 Connect 命令创建 Admin 队列并建立关联（Association）
- 在需要时执行带内身份认证（in-band authentication）
- 使用 Property Get/Set 命令访问控制器能力与配置寄存器
- 使能控制器并等待就绪信号
- 发现控制器支持的命令集与命名空间配置
- 创建 I/O 队列对（Queue Pair）
- 配置异步事件通知 ^[nvme-controller-initialization.md:1-9, nvme-controller-initialization.md:82-89]

## 与 PCIe 初始化的区别

Fabrics 初始化与基于 PCIe 的控制器初始化在概念上相似，但实现细节存在显著差异：

| 初始化阶段 | PCIe（基于内存） | Fabrics（基于消息） |
|-----------|----------------|-------------------|
| 建立管理路径 | 通过寄存器编程 AQA、ASQ、ACQ | 执行 Connect 命令创建 Admin [队列对](/concepts/队列对.md) |
| 属性访问 | 直接读写 PCI 配置空间寄存器 | 使用 Fabrics Property Get/Set 命令 |
| 身份认证 | 不属于初始化序列 | 当 AUTHREQ ≠ 0 时必须先完成认证 |
| I/O 队列创建 | Set Features → 配置中断 → Create CQ → Create SQ | 对每个队列对执行 Connect 命令 |
| 超时处理 | 依赖本地硬件 | 2 分钟内未设置 CC.EN=1，控制器可能移除关联 |

 ^[nvme-controller-initialization.md:22-33, nvme-controller-initialization.md:78-89]

## 详细初始化步骤

### 1. 建立传输层连接

主机首先通过 Fabrics 传输层建立与控制器的物理连接。这是后续所有操作的前提条件。 ^[nvme-controller-initialization.md:22-33]

### 2. 执行 Connect 命令

Connect 命令用于创建 Admin 队列对并建立主机与控制器之间的关联。如果控制器设置 `AUTHREQ ≠ 0`，则必须在创建队列之前完成身份认证流程。 ^[nvme-controller-initialization.md:82-89]

### 3. 配置控制器寄存器

通过 Fabrics Property Get 和 Property Set 命令访问并配置控制器寄存器：

- 获取控制器能力寄存器（CAP）
- 设置控制器配置寄存器（CC），包括选择命令集（CSS）和仲裁机制（AMS）
- 设置 `CC.EN=1` 使能控制器
- 轮询等待 `CSTS.RDY=1`（就绪信号） ^[nvme-controller-initialization.md:22-33, nvme-controller-initialization.md:82-89]

### 4. 识别控制器与命令集

控制器就绪后，主机执行 Identify [Controller](/concepts/controller.md) 命令获取控制器基本信息，并根据需要识别支持的 I/O 命令集组合。 ^[nvme-controller-initialization.md:59-74]

### 5. 枚举命名空间

遍历活动的命名空间标识符（NSID），识别可用的存储逻辑单元。 ^[nvme-controller-initialization.md:59-74]

### 6. 创建 I/O 队列

Fabrics 传输通过 Connect 命令为每个 I/O 队列对建立连接，查询队列数量限制（MQES）以确保不超过控制器能力。 ^[nvme-controller-initialization.md:59-74, nvme-controller-initialization.md:82-89]

### 7. 配置异步事件通知

在控制器就绪后的任意时刻，主机可提交 Asynchronous Event Request（AER）以启用异步事件通知机制。 ^[nvme-controller-initialization.md:59-74]

## Discovery 控制器的初始化

Discovery 控制器是 NVMe-oF 架构中的特殊控制器，专门用于发现网络中的可用存储目标。其初始化流程根据是否请求变更通知而有所不同： ^[nvme-controller-initialization.md:91-123]

### 支持变更通知的情况

如果主机请求变更通知且 Keep Alive Timeout（KATO）非零：
1. 控制器可调整 KATO 值
2. 预分配 AER/AEN 资源
3. Connect 成功
4. 主机提交 AER 命令
5. 执行身份认证（如需要）
6. 读取控制器能力
7. 写入 CC 寄存器并设置 EN=1
8. 等待 RDY=1
9. 读取 Discovery Log Page ^[nvme-controller-initialization.md:91-123]

### 不支持变更通知的情况

如果未请求变更通知或 KATO 为零：
- 使用固定的 KATO 值
- 或返回 Connect 错误
- 主机完成连接后不提交 AER ^[nvme-controller-initialization.md:91-123]

## 关键概念

- NVMe-oF：NVMe over Fabrics，一种通过网络传输 NVMe 协议的扩展
- [控制器初始化](/concepts/控制器初始化.md)：控制器启动的一般过程，Fabrics 初始化是其特定实现
- Discovery 控制器：专门用于发现存储资源的特殊控制器
- [队列对](/concepts/队列对.md)：由提交队列（SQ）和完成队列（CQ）组成的 I/O 单元
- 身份认证：Fabrics 传输中的安全机制，当 AUTHREQ ≠ 0 时必须执行

## 关键术语对照

| 中文术语 | 英文术语 | 缩写 | 说明 |
|---------|---------|-----|------|
| 关联 | Association | - | Fabrics 中主机与控制器的连接关系 |
| [队列对](/concepts/队列对.md) | [Queue Pair](/concepts/queue-pair.md) | QP | 一对提交队列和完成队列 |
| 身份认证 | Authentication | - | 验证通信双方身份的机制 |
| 发现日志页 | Discovery Log Page | DLP | 记录可用存储目标信息的结构 |
| 保持活跃超时 | Keep Alive Timeout | KATO | 连接保活超时时间 |

## 规范参考

以下页面提供了初始化流程的详细规范说明：

- [基于内存的初始化起点，PDF p. 124](../_source/pages/page-124.md)
- [基于内存的完成流程与 Fabrics 启动，PDF p. 125](../_source/pages/page-125.md)
- [Figure 82 时序图与 Fabrics 初始化起点，PDF p. 126](../_source/pages/page-126.md)
- [Fabrics 初始化延续与超时处理，PDF p. 127](../_source/pages/page-127.md)
- [Figure 83 时序图与 Discovery 初始化序列，PDF p. 128](../_source/pages/page-128.md)

## Sources

^[nvme-controller-initialization.md:1-9, nvme-controller-initialization.md:22-89, nvme-controller-initialization.md:91-123]

# Citations

1. [nvme-controller-initialization.md:1-9](/references/nvme-controller-initialization-1b5c7c04.md)
2. [nvme-controller-initialization.md:82-89](/references/nvme-controller-initialization-1b5c7c04.md)
3. [nvme-controller-initialization.md:22-33](/references/nvme-controller-initialization-1b5c7c04.md)
4. [nvme-controller-initialization.md:78-89](/references/nvme-controller-initialization-1b5c7c04.md)
5. [nvme-controller-initialization.md:59-74](/references/nvme-controller-initialization-1b5c7c04.md)
6. [nvme-controller-initialization.md:91-123](/references/nvme-controller-initialization-1b5c7c04.md)
7. [nvme-controller-initialization.md:22-89](/references/nvme-controller-initialization-1b5c7c04.md)
