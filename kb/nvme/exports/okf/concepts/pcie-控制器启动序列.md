---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 3851e7664d30e5b66be0200bea363c0276003b6300f218f43e61b103251bcb8a
  pageDirectory: concepts
  sources:
    - nvme-controller-initialization.md
  confidence: 0.9
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - pcie-控制器启动序列
  citations:
    - file: nvme-controller-initialization.md
      start: 3
      end: 3
    - file: nvme-controller-initialization.md
      start: 3
      end: 10
    - file: nvme-controller-initialization.md
      start: 16
      end: 16
    - file: nvme-controller-initialization.md
      start: 20
      end: 33
    - file: nvme-controller-initialization.md
      start: 41
      end: 48
    - file: nvme-controller-initialization.md
      start: 51
      end: 56
    - file: nvme-controller-initialization.md
      start: 61
      end: 73
    - file: nvme-controller-initialization.md
      start: 80
      end: 85
title: PCIe 控制器启动序列
description: 基于内存传输的 NVMe 控制器最小启动流程：等待 RDY=0 → 配置 AQA/ASQ/ACQ → 选择 CSS/AMS/MPS → 设置 EN=1 并等待 RDY=1 → 执行 Identify 和创建 I/O 队列。
tags:
  - PCIe
  - NVMe
  - 内存传输
timestamp: "2026-08-16T06:21:33.353Z"
---


# PCIe 控制器启动序列

PCIe 控制器启动序列是 NVMe 控制器初始化流程中针对 PCIe 传输类型的特定实现，属于一种依赖于传输类型的引导过程（transport-specific bootstrap process）。该序列的核心目标是在主机与 NVMe 设备之间建立通信基础，使控制器从禁用状态过渡到就绪状态，从而支持后续的存储操作。^[nvme-controller-initialization.md:3]

## 概述

PCIe 控制器启动序列主要完成以下工作：

- 建立管理通道（Admin Path）
- 选择控制器支持的配置参数
- 使能控制器（Enable Controller）
- 发现其命令集（Command Set）和命名空间（Namespace）配置
- 创建 I/O 队列（I/O Queue）
- 可选地启用异步事件通知（Asynchronous Events）

这些步骤为主机提供了与 NVMe 设备进行 I/O 操作所必需的前置条件。^[nvme-controller-initialization.md:3-10]

## 最小 PCIe 启动流程

将新控制器接入服务器后，驱动不能立刻创建 I/O 队列。完整的启动流程遵循严格的顺序依赖关系：

1. **等待就绪信号**：首先等待控制器处于禁用状态且 `RDY=0`
2. **读取能力并配置管理队列**：读取控制器能力寄存器，配置管理队列的地址和大小
3. **选择配置参数**：选择合法的 `CC`（Controller Configuration）值
4. **使能控制器**：设置 `CC.EN=1` 并等待 `RDY=1`
5. **执行后续操作**：在控制器就绪后，执行 Identify 命令、命名空间发现和 I/O 队列创建

只有完成上述步骤，后续的 Identify 和 I/O 队列创建才有正确的前提条件。^[nvme-controller-initialization.md:16]

## 概念模型对比

PCIe 作为一种基于内存的传输（Memory-based transport），其启动序列与基于消息的传输（如 NVMe-oF Fabrics）存在差异，但核心步骤相似。以下对比了两者的初始化路径：

```text
[[基于内存的传输|基于内存的传输]] (PCIe)                [[基于消息的传输|基于消息的传输]] (Fabrics)
等待 RDY=0                          建立传输层连接
配置 AQA / ASQ / ACQ                 执行 Connect → 创建 Admin 队列 + 关联
选择 CSS / AMS / MPS                 如果 AUTHREQ != 0 则执行身份认证
设置 EN=1; 等待 RDY=1                Property Get/Set CAP, CC; EN=1; 等待 RDY=1
           \                         /
            +---> 执行 Identify 识别控制器和 I/O 命令集
                  枚举活动的命名空间
                  协商/创建 I/O 队列
                  启用事件监听 + 提交 AER
```

两者在完成初始握手后，都需要执行 Identify 识别控制器、枚举命名空间、创建 I/O 队列等通用步骤。^[nvme-controller-initialization.md:20-33]

## 基于能力寄存器的初始化序列

### 配置命令集选择

主机需要根据控制器能力寄存器 `CAP.CSS`（Controller Capabilities - Command Sets Supported）来决定命令集配置 `CC.CSS`（Controller Configuration - Command Set Selection）：

| CSS 值 | 含义 | 说明 |
|--------|------|------|
| `111b` | 无 I/O 命令集模式 | 仅支持管理命令 |
| `110b` | I/O 命令集组合 | 支持多种命令集的组合 |
| `000b` | NVM 命令集 | 标准块存储命令集，需满足能力条件 |

正确选择命令集是确保控制器与主机之间通信兼容的基础。^[nvme-controller-initialization.md:41-48]

### 初始化前的准备工作

在设置 `CC.EN=1`（使能控制器）之前，主机需要完成以下准备工作：

1. **选择仲裁机制**（Arbitration Mechanism）：从控制器支持的仲裁方式中选择一种
2. **选择内存页大小**（Memory Page Size）：与系统内存管理匹配
3. **等待就绪信号**：设置 `CC.EN=1` 后，轮询等待 `CSTS.RDY=1`（Controller Status - Ready）

这些配置参数必须与控制器的能力匹配，否则可能导致初始化失败。^[nvme-controller-initialization.md:51-56]

### 控制器就绪后的发现流程

控制器进入就绪状态后，主机按以下顺序执行发现操作：

1. **识别控制器**：执行 Identify Controller 命令，获取控制器基本信息
2. **命令集发现**：
   - 如果控制器支持命令集组合，主机识别可用组合并选择合适的配置文件
   - 对每个已使能的 I/O 命令集，执行命令集特定的识别操作
3. **枚举命名空间**：遍历活动的命名空间标识符（Active NSID）
4. **读取标识结构**：获取命令集特定和命令集独立的 Identify 数据结构
5. **创建 I/O 队列**：按照"先完成队列（CQ）后提交队列（SQ）"的顺序创建
6. **配置异步事件**：在控制器就绪后的任意时刻配置异步事件通知

对于 PCIe 传输，I/O 队列的创建需要通过 Set Features 命令设置队列数量，并配置中断设置。^[nvme-controller-initialization.md:61-73]

## PCIe 特定的启动细节

### 管理路径建立

PCIe 控制器通过寄存器编程方式建立管理路径，具体配置以下寄存器：

- **AQA**（Admin Queue Attributes）：定义管理队列属性
- **ASQ**（Admin Submission Queue Address）：管理提交队列基地址
- **ACQ**（Admin Completion Queue Address）：管理完成队列基地址

### 属性访问方式

PCIe 控制器通过绑定定义的寄存器访问（Binding-defined register access）方式访问控制器属性，这与 Fabrics 使用 Property Get/Set 命令的方式不同。

### I/O 队列创建

PCIe 控制器的 I/O 队列创建流程如下：

1. 通过 Set Features 设置队列数量（Number of Queues）
2. 配置中断（Interrupt）设置
3. 先创建完成队列（Create CQ）
4. 后创建提交队列（Create SQ）

这种顺序确保了队列创建的依赖关系得到正确处理。^[nvme-controller-initialization.md:80-85]

## 关键寄存器说明

| 寄存器 | 全称 | 功能 |
|--------|------|------|
| CAP | [Controller](/concepts/controller.md) Capabilities | 报告控制器支持的功能和能力 |
| CC | [Controller](/concepts/controller.md) Configuration | 控制器的配置参数（包含 EN、CSS 等字段） |
| CSTS | [Controller](/concepts/controller.md) Status | 控制器的当前状态（包含 RDY 标志） |
| AQA | Admin Queue Attributes | 管理队列属性配置 |
| ASQ | Admin Submission Queue Base Address | 管理提交队列基地址 |
| ACQ | Admin Completion Queue Base Address | 管理完成队列基地址 |

## 相关概念

- NVMe 控制器初始化：NVMe 控制器初始化的通用流程
- NVMe-oF Fabrics：基于消息的传输类型，与 PCIe 形成对比
- Identify 命令：用于获取控制器和命名空间信息的关键命令
- Set Features：用于配置控制器特性的命令
- I/O 队列：用于承载 I/O 命令的提交和完成队列
- [异步事件通知](/concepts/异步事件通知.md)：控制器向主机报告状态变化的机制

## 来源

- [NVMe [控制器初始化](/concepts/控制器初始化.md) - nvme-controller-initialization.md](../_source/pages/nvme-controller-initialization.md)

## 规范参考

以下页面提供了初始化流程的详细规范说明：

- [基于内存的初始化起点，PDF p. 124](../_source/pages/page-124.md)
- [基于内存的完成流程与 Fabrics 启动，PDF p. 125](../_source/pages/page-125.md)
- [Figure 82 时序图与 Fabrics 初始化起点，PDF p. 126](../_source/pages/page-126.md)
- [Fabrics 初始化延续与超时处理，PDF p. 127](../_source/pages/page-127.md)

# Citations

1. [nvme-controller-initialization.md:3-3](/references/nvme-controller-initialization-1b5c7c04.md)
2. [nvme-controller-initialization.md:3-10](/references/nvme-controller-initialization-1b5c7c04.md)
3. [nvme-controller-initialization.md:16-16](/references/nvme-controller-initialization-1b5c7c04.md)
4. [nvme-controller-initialization.md:20-33](/references/nvme-controller-initialization-1b5c7c04.md)
5. [nvme-controller-initialization.md:41-48](/references/nvme-controller-initialization-1b5c7c04.md)
6. [nvme-controller-initialization.md:51-56](/references/nvme-controller-initialization-1b5c7c04.md)
7. [nvme-controller-initialization.md:61-73](/references/nvme-controller-initialization-1b5c7c04.md)
8. [nvme-controller-initialization.md:80-85](/references/nvme-controller-initialization-1b5c7c04.md)
