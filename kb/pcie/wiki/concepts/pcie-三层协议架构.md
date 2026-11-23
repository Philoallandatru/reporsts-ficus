---
title: PCIe 三层协议架构
summary: PCIe协议采用事务层、数据链路层、物理层的三层分层架构，每层负责特定功能并通过标准化接口通信
sources:
- pcie-layering.md
kind: concept
createdAt: '2026-08-16T06:39:36.640Z'
updatedAt: '2026-08-16T06:39:36.640Z'
tags:
- pcie
- protocol-architecture
- layering
aliases:
- pcie-三层协议架构
confidence: 0.95
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: PCIe 采用**分层架构**，将复杂的通信协议分解为三个独立的层次，自上而下分别是**事务层（Transaction Layer）**、**数据链路层（Data
  Link Layer）** 和 **物理层（Physical Layer）**。每层负责特定的功能，层与层之间通过定义良好的接口通信。这种设计将协议复杂性模块化，便于硬件实现和协议理解。
  ^...
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCIe 三层协议架构

PCIe 采用**分层架构**，将复杂的通信协议分解为三个独立的层次，自上而下分别是**事务层（Transaction Layer）**、**数据链路层（Data Link Layer）** 和 **物理层（Physical Layer）**。每层负责特定的功能，层与层之间通过定义良好的接口通信。这种设计将协议复杂性模块化，便于硬件实现和协议理解。 ^[pcie-layering.md:5]

## 架构概览

```
┌─────────────────────────────────────────────────────────┐
│          Software Layer (软件层)                        │
│        操作系统、驱动程序                                │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│     Transaction Layer (事务层 - TL)                     │
│  • 生成和处理 TLP (Transaction Layer Packet)            │
│  • 流控制（Flow Control）                               │
│  • 排序规则（Ordering Rules）                           │
│  • 虚拟通道（Virtual Channels）                         │
└────────────────┬────────────────────────────────────────┘
                 │ TLP
┌────────────────▼────────────────────────────────────────┐
│     Data Link Layer (数据链路层 - DLL)                  │
│  • 可靠传输（ACK/NAK 协议）                             │
│  • 重试机制（Retry Buffer）                             │
│  • CRC 错误检测（LCRC）                                 │
│  • 流控制初始化（InitFC DLLPs）                         │
└────────────────┬────────────────────────────────────────┘
                 │ DLLP + TLP
┌────────────────▼────────────────────────────────────────┐
│     Physical Layer (物理层 - PHY)                       │
│  • 数据编码/解码（8b/10b, 128b/130b）                   │
│  • 串行化/解串行化                                      │
│  • 链路训练（LTSSM）                                    │
│  • 电气信号传输                                         │
└────────────────┬────────────────────────────────────────┘
                 │ Electrical Signals
                 ▼
              物理连接 (Lane)
```

数据在各层之间逐层封装：事务层将数据封装为 TLP（事务层数据包）；数据链路层为 TLP 添加序列号和 LCRC 校验，生成 DLLP（数据链路层数据包）用于链路控制；物理层将数据编码后串行发送。 ^[pcie-layering.md:5-39]

---

## 1. 事务层（Transaction Layer）

事务层是 PCIe 协议栈的**最高层**，负责处理所有的事务请求和响应。它直接面向软件层，为上层软件提供统一的传输接口。 ^[pcie-layering.md:47]

### 主要职责

- 构建和解析 TLP（Transaction Layer Packet）
- 管理**内存、IO、配置空间**的读写事务
- 实现**排序规则**保证数据一致性
- 管理**流控制**防止缓冲区溢出
- 支持**虚拟通道**实现 QoS（服务质量） ^[pcie-layering.md:47-52]

### TLP 类型

PCIe 定义了多种 TLP 类型用于不同的通信场景： ^[pcie-layering.md:56]

| 类型 | 说明 | 示例 |
|------|------|------|
| **Memory Request** | 内存读写请求，支持 64 位地址 | Memory Read (MRd), Memory Write (MWr) |
| **IO Request** | IO 读写请求，32 位地址兼容传统设备 | IO Read (IORd), IO Write (IOWr) |
| **Configuration Request** | 配置读写，用于设备枚举 | Configuration Read/Write |
| **Message Request** | 消息请求，用于中断、电源管理、错误报告 | MSI/MSI-X 中断 |
| **Completion** | 完成响应，用于 Non-Posted 请求的应答 | Completion (Cpl), Completion with Data (CplD) |

### TLP 结构

TLP 由三部分组成：

- **Header（3 或 4 个双字）**：包含格式/类型、长度、请求者 ID、标签、地址等字段
- **Data Payload（0-1024 双字）**：实际数据负载，最大 4096 字节，可选
- **ECRC（4 字节）**：端到端 CRC校验，可选 ^[pcie-layering.md:94-113]

### 流控制（Flow Control）

流控制基于**信用机制（Credit-based）**防止发送方发送超过接收方缓冲区容量的数据。接收方定期向发送方通告可用缓冲区空间，发送方根据信用情况决定是否可以发送数据。 ^[pcie-layering.md:116-123]

PCIe 将事务分为三类：

| 类型 | 说明 | 示例 |
|------|------|------|
| **Posted (P)** | 无需响应的请求 | Memory Write, Message |
| **Non-Poested (NP)** | 需要 Completion 响应 | Memory Read, IO R/W, Config R/W |
| **Completion (Cpl)** | 对 NP 请求的响应 | Completion, Completion with Data |

### 排序规则（Ordering Rules）

PCIe 定义了严格的排序规则保证数据一致性。基本原则是**同类型 TLP 保持顺序，不同类型 TLP 可能允许乱序**。Posted Write 之间必须保序，而 Read Request 与 Posted Write 之间可以乱序。 ^[pcie-layering.md:155-163]

### 虚拟通道（Virtual Channels）

虚拟通道机制允许在单个物理链路上实现流量分类和 QoS。每个 TLP 携带 **TC（Traffic Class）** 标签，映射到不同的 **VC（Virtual Channel）**，每个 VC 有独立的流控制缓冲区。所有设备必须支持 VC0，VC1-VC7 为可选配置。 ^[pcie-layering.md:185-197]

---

## 2. 数据链路层（Data Link Layer）

数据链路层负责**可靠传输**，确保事务层产生的 TLP 正确到达对端设备。该层通过确认机制和错误恢复保证链路级数据的完整性。 ^[pcie-layering.md:207-209]

### 主要职责

- 添加 **Sequence Number（序列号）** 用于包序管理
- 添加 **LCRC（Link CRC）** 用于错误检测
- 实现 **ACK/NAK 协议** 进行可靠传输
- 管理 **Retry Buffer（重试缓冲区）** 存储待确认数据包
- 发送 DLLP（Data Link Layer Packet）控制包 ^[pcie-layering.md:210-214]

### DLLP 类型

DLLP 是数据链路层的控制包，**不携带用户数据**，仅用于链路管理和控制： ^[pcie-layering.md:218-227]

| DLLP 类型 | 功能 |
|-----------|------|
| **Ack** | 确认收到 TLP |
| **Nak** | 请求重传 TLP |
| **InitFC1/InitFC2** | 流控制初始化 |
| **UpdateFC** | 运行时更新流控制信用 |
| **PM_Enter_L1/L23** | 电源管理状态转换 |

### [[acknak-协议|ACK/NAK 协议]]

ACK/NAK 协议是数据链路层可靠传输的核心机制。发送方为每个 TLP 分配 12 位序列号（0-4095 循环使用），接收方验证 LCRC 后返回 Ack 或 Nak 确认。如果发送方超时未收到 ACK 或收到 NAK，会从 Retry Buffer 重传相关数据包。 ^[pcie-layering.md:229-258]

### LCRC 与 ECRC 的区别

数据链路层的 LCRC 与事务层的 ECRC 保护范围不同：

| 特性 | LCRC | ECRC |
|------|------|------|
| **覆盖范围** | 每一跳（逐跳保护） | 端到端（整个传输路径） |
| **添加位置** | 数据链路层 | 事务层 |
| **保护对象** | 链路传输错误 | Switch 内部错误、内存错误 |
| **强制性** | 必须 | 可选 | ^[pcie-layering.md:260-277]

---

## 3. 物理层（Physical Layer）

物理层是 PCIe 协议栈的**最底层**，负责将数据转换为可在物理介质上传输的信号。它处理编码、串行化、链路训练和电气信号传输等任务。 ^[pcie-layering.md:282-284]

### 主要职责

- **数据编码/解码**：8b/10b（Gen1/2）或 128b/130b（Gen3+）
- **串行化/解串行化**：并行数据与串行比特流的转换
- **链路训练**：速度和宽度协商（LTSSM）
- **时钟恢复**：从数据流中提取时钟
- **电气信号传输**：差分信号驱动 ^[pcie-layering.md:285-289]

### 编码方案

#### 8b/10b 编码（PCIe 1.0/2.0）

每 8 位数据编码为 10 位符号，效率为 80%。该编码保证 DC 平衡和足够的跳变用于时钟恢复。特殊符号包括链路训练时用于对齐的 COM（K28.5）和时钟补偿符号 SKP。 ^[pcie-layering.md:318-328]

#### 128b/130b 编码（PCIe 3.0+）

每 128 位数据添加 2 位同步头，效率提升至 98.5%，显著减少编码开销。同步头标识数据块或 Ordered Set 块类型。 ^[pcie-layering.md:331-341]

### 链路训练（LTSSM）

LTSSM（Link Training and Status State Machine）管理链路的整个生命周期，包括以下关键状态：

- **Detect**：检测链路对端是否存在
- **Polling**：比特锁定和符号锁定，速度协商
- **Configuration**：Lane 宽度协商，分配 Lane 编号
- **L0**：数据传输状态（正常工作）
- **Recovery**：链路恢复和重新训练 ^[pcie-layering.md:375-380]

### Lane（通道）

Lane 是 PCIe 的最小传输单元，由 **4 根信号线**组成（TX+/TX- 发送差分对 + RX+/RX- 接收差分对），支持全双工通信。常见配置包括 x1（1 Lane）、x4（4 Lane）和 x16（16 Lane）。物理层自动支持 Lane 反转和极性翻转以适应布线。 ^[pcie-layering.md:382-404]

### 信号速率与数据率

| PCIe 代际 | 信号速率 | 编码方式 | 每 Lane 数据率 |
|-----------|----------|----------|----------------|
| Gen 1 | 2.5 GHz | 8b/10b | 2.0 Gbps (250 MB/s) |
| Gen 2 | 5.0 GHz | 8b/10b | 4.0 Gbps (500 MB/s) |
| Gen 3 | 8.0 GHz | 128b/130b | 7.877 Gbps (985 MB/s) |
| Gen 4 | 16.0 GHz | 128b/130b | 15.754 Gbps (1969 MB/s) |
| Gen 5 | 32.0 GHz | 128b/130b | 31.508 Gbps (3938 MB/s) | ^[pcie-layering.md:417-424]

---

## 层间交互

### 发送路径（TX）

数据发送时经过以下封装过程：

1. **事务层**：创建 Memory Write TLP（Header + Data），检查流控制信用，添加可选 ECRC
2. **数据链路层**：添加序列号，计算并添加 LCRC，存入 Retry Buffer
3. **物理层**：添加成帧标记（STP/END），加扰，编码（8b/10b 或 128b/130b），串行化发送 ^[pcie-layering.md:429-471]

### 接收路径（RX）

数据接收时经过以下解封装过程：

1. **物理层**：解串行化，解码，解扰，检测成帧标记
2. **数据链路层**：验证 LCRC，发送 Ack/Nak DLLP，检查序列号
3. **事务层**：解析 TLP Header，验证 ECRC（如存在），路由到目标地址，更新流控制信用 ^[pcie-layering.md:475-511]

---

## 总结

PCIe 三层协议架构的关键要点：

| 要点 | 说明 |
|------|------|
| **三层分离** | 事务层、数据链路层、物理层各司其职，接口清晰 |
| **TLP** | 事务层的数据包，携带实际事务请求和响应 |
| **DLLP** | 数据链路层的控制包，用于 ACK/NAK 和流控制 |
| **可靠传输** | 通过序列号、LCRC、重试机制保证 |
| **流控制** | 基于信用机制，防止缓冲区溢出 |
| **链路训练** | LTSSM 管理链路状态和参数协商 |
| **编码效率** | 8b/10b（Gen1/2，80%）→ 128b/130b（Gen3+，98.5%）|

---

## Sources

- [pcie-layering.md - PCIe 三层协议模型详解](../../sources/pcie-layering.md)

