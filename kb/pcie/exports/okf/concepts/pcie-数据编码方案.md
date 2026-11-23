---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 03e2b9bb3121bfdbd6c6bb0f5e6027596c37dad9e542c1351e23f13ada71a06a
  pageDirectory: concepts
  sources:
    - pcie-layering.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - pcie-数据编码方案
  citations:
    - file: pcie-layering.md
      start: 284
      end: 289
    - file: pcie-layering.md
      start: 317
      end: 321
    - file: pcie-layering.md
      start: 320
      end: 321
    - file: pcie-layering.md
      start: 322
      end: 323
    - file: pcie-layering.md
      start: 323
      end: 324
    - file: pcie-layering.md
      start: 325
      end: 329
    - file: pcie-layering.md
      start: 330
      end: 336
    - file: pcie-layering.md
      start: 332
      end: 335
    - file: pcie-layering.md
      start: 334
      end: 336
    - file: pcie-layering.md
      start: 337
      end: 342
    - file: pcie-layering.md
      start: 417
      end: 424
    - file: pcie-layering.md
      start: 461
      end: 467
    - file: pcie-layering.md
      start: 480
      end: 486
title: PCIe 数据编码方案
description: PCIe使用8b/10b编码(Gen1/2)和128b/130b编码(Gen3+)，后者效率更高达到98.5%
tags:
  - pcie
  - physical-layer
  - encoding
timestamp: "2026-08-16T06:40:31.794Z"
---


# PCIe 数据编码方案

PCIe 在物理层采用数据编码方案将上层交付的数据转换为适合在高速串行链路上传输的信号格式。编码的核心目标是实现 **直流平衡（DC Balance）**、提供足够的信号跳变以支持**时钟恢复**，以及尽可能提高有效数据的传输效率。^[pcie-layering.md:284-289]

## 8b/10b 编码（PCIe 1.0/2.0）

8b/10b 编码是 PCIe 早期世代（Gen 1 和 Gen 2）采用的编码方案。其工作原理是将每 **8 位原始数据**编码为 **10 位符号**进行传输。^[pcie-layering.md:317-321]

### 编码效率

该方案的编码效率为 **80%**（即 8/10），这意味着每传输 10 位符号中仅有 8 位代表有效数据，其余 2 位用于编码开销。^[pcie-layering.md:320-321]

### 技术特性

8b/10b 编码通过精心设计的映射规则实现两项关键技术目标：

- **直流平衡**：编码确保在较长的数据序列中 0 和 1 的数量接近相等，避免直流分量积累，便于交流耦合传输。^[pcie-layering.md:322-323]
- **时钟嵌入**：编码后的比特流包含足够的跳变沿，使接收端能够从数据流中恢复时钟信号，无需独立的时钟线。^[pcie-layering.md:323-324]

### 特殊控制符号

8b/10b 编码定义了一系列特殊符号用于链路控制和管理：^[pcie-layering.md:325-329]

| 符号 | 名称 | 用途 |
|------|------|------|
| **COM** (K28.5) | 对齐符号 | 链路训练时的符号对齐和检测 |
| **SKP** | 时钟补偿符号 | 补偿发送端与接收端之间的时钟频率差异 |
| **EDB** | 错误结束标记 | 标识无效或错误的数据块结束 |

## 128b/130b 编码（PCIe 3.0 及更高版本）

从 PCIe Gen 3 开始，协议采用了更高效的 **128b/130b 编码**方案，以满足更高数据传输速率的需求。^[pcie-layering.md:330-336]

### 编码结构

128b/130b 编码为每 **128 位数据**添加 **2 位同步头（Sync Header）**，因此一个数据块的总长度为 130 位。这种设计大幅减少了编码开销。^[pcie-layering.md:332-335]

### 编码效率

该方案的编码效率提升至 **98.5%**（即 128/130），显著高于 8b/10b 的 80%。这一改进使得在相同的信号速率下，Gen 3 及更高版本的**有效数据吞吐量**大幅提升。^[pcie-layering.md:334-336]

### 同步头定义

2 位同步头用于标识后续 128 位数据的类型：^[pcie-layering.md:337-342]

| 同步头值 | 含义 |
|----------|------|
| `00b` | 数据块（Data Block） |
| `01b` | Ordered Set 块（用于链路训练和控制） |
| `10b` | 保留 |
| `11b` | 保留 |

## 各代际编码与速率对比

下表汇总了 PCIe 各代际的信号速率、编码方案及每通道有效数据率：^[pcie-layering.md:417-424]

| PCIe 代际 | 信号速率 | 编码方案 | 每通道数据率 | 实际传输速率 |
|-----------|----------|----------|--------------|--------------|
| Gen 1 | 2.5 GHz | 8b/10b | 2.0 Gbps | 250 MB/s |
| Gen 2 | 5.0 GHz | 8b/10b | 4.0 Gbps | 500 MB/s |
| Gen 3 | 8.0 GHz | 128b/130b | 7.877 Gbps | 985 MB/s |
| Gen 4 | 16.0 GHz | 128b/130b | 15.754 Gbps | 1969 MB/s |
| Gen 5 | 32.0 GHz | 128b/130b | 31.508 Gbps | 3938 MB/s |

从 Gen 1 到 Gen 2，虽然信号速率翻倍，但由于仍采用 8b/10b 编码，实际有效数据率同样翻倍。从 Gen 2 到 Gen 3，信号速率从 5 GHz 提升至 8 GHz（约 1.6 倍），但由于编码方案从 8b/10b 切换至 128b/130b，有效数据率的提升幅度（接近 2 倍）超过了信号速率的提升。^[pcie-layering.md:417-424]

## 编码与物理层的关系

编码是物理层功能的核心组成部分。在发送路径上，物理层首先对数据进行 **加扰（Scrambling）** 以打破长连零或长连一模式，随后进行编码，最后通过 **串行化（Serialization）** 将并行比特流转换为串行信号。^[pcie-layering.md:461-467]

在接收路径上，物理层执行相反的操作：**解串行化（Deserialization）**、**解码（Decoding）**、**解扰（Descrambling）**，最后进行 **成帧检测（Framing Detection）** 以识别数据包边界。^[pcie-layering.md:480-486]

## 相关概念

PCIe 数据编码方案与以下物理层概念紧密相关：

- PCIe 物理层结构：编码所在的物理层组成部分
- PCIe 链路训练（LTSSM）：链路训练过程中进行的符号对齐和编码协商
- PCIe 电气特性：编码对信号传输质量的影响

---

## Sources

- PCIe 三层协议模型](../pcie-layering.md)

# Citations

1. [pcie-layering.md:284-289](/references/pcie-layering-3c12192c.md)
2. [pcie-layering.md:317-321](/references/pcie-layering-3c12192c.md)
3. [pcie-layering.md:320-321](/references/pcie-layering-3c12192c.md)
4. [pcie-layering.md:322-323](/references/pcie-layering-3c12192c.md)
5. [pcie-layering.md:323-324](/references/pcie-layering-3c12192c.md)
6. [pcie-layering.md:325-329](/references/pcie-layering-3c12192c.md)
7. [pcie-layering.md:330-336](/references/pcie-layering-3c12192c.md)
8. [pcie-layering.md:332-335](/references/pcie-layering-3c12192c.md)
9. [pcie-layering.md:334-336](/references/pcie-layering-3c12192c.md)
10. [pcie-layering.md:337-342](/references/pcie-layering-3c12192c.md)
11. [pcie-layering.md:417-424](/references/pcie-layering-3c12192c.md)
12. [pcie-layering.md:461-467](/references/pcie-layering-3c12192c.md)
13. [pcie-layering.md:480-486](/references/pcie-layering-3c12192c.md)
