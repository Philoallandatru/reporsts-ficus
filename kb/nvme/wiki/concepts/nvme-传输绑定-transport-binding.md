---
title: NVMe 传输绑定 (Transport Binding)
summary: NVMe 规范中定义的不同传输层实现（如 PCIe）与协议语义解耦的抽象机制
sources:
- visualization-guidelines.md
kind: concept
createdAt: '2026-08-16T06:26:42.524Z'
updatedAt: '2026-08-16T06:26:42.524Z'
tags:
- nvme
- transport-layer
- pcie
aliases:
- nvme-传输绑定-transport-binding
- N传(B
confidence: 0.9
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: 传输绑定（Transport Binding）是 NVMe 架构中连接NVMe 主机与 [[NVMe 控制器]] 的通信层协议。它定义了命令和数据如何在主机软件与控制器之间传输，是
  NVMe 实现多种物理介质和网络拓扑的基础。
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# NVMe 传输绑定 (Transport Binding)

传输绑定（Transport Binding）是 NVMe 架构中连接NVMe 主机与 [[NVMe 控制器]] 的通信层协议。它定义了命令和数据如何在主机软件与控制器之间传输，是 NVMe 实现多种物理介质和网络拓扑的基础。

## 架构位置

根据 NVMe 页面规范的可视化模板，传输绑定位于整个 NVMe 体系结构的边缘位置：^[visualization-guidelines.md:7-14]

```mermaid
flowmap LR
    Host[Host software] --> SQ[Submission Queue]
    SQ --> CController]
    C --> CQ[Completion Queue]
    C --> NS[Namespace]
    C --> T[Transport binding]
```

该图仅为解释性重绘，用于表达 主机、控制器、队列对与传输绑定之间的逻辑关系，不代表任何规范原图的时序或物理拓扑。^[visualization-guidelines.md:16]

## 规范编写注意事项

编写涉及传输绑定的规范页面时，应注意以下质量要求：

- **区分传输层与通用行为**：不应将 PCIe 传输的实现细节描述为 NVMe Base 规范的通用行为。传输绑定是可插拔的，不同传输协议具有各自独特的特性。^[visualization-guidelines.md:25]
- **图表与表格的选用**：适合用图表表达的内容包括 transport 边界；适合用表格表达的内容包括字段、状态码等结构化数据。^[visualization-guidelines.md:18]
- **引用准确性**：引用只能指向 `sources/` 中存在的文件；页码不确定时应引用文件级来源，并明确标注"不确定页码"。^[visualization-guidelines.md:24]

## 常见传输绑定类型

虽然源文档未列出具体传输协议，但 NVMe 规范通常涉及以下传输绑定：

- PCIe：本地高速直连
- [[NVMe over Fabrics]]：通过网络结构扩展

---

## Sources

- visualization-guidelines.md (不确定页码)

