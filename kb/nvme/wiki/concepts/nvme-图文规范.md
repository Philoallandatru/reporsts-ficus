---
title: NVMe 图文规范
summary: llmwiki 编译 NVMe 页面时关于图表类型选择、模板格式及来源标注的质量要求
sources:
- visualization-guidelines.md
kind: concept
createdAt: '2026-08-16T06:27:00.240Z'
updatedAt: '2026-08-16T06:27:00.240Z'
tags:
- documentation
- wiki-style-guide
- visualization
aliases:
- nvme-图文规范
confidence: 0.95
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: 本文档定义了 NVMe 相关页面在图文呈现方面的规范要求，旨在确保页面内容准确、易读且引用规范。
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# NVMe 图文规范

本文档定义了 NVMe 相关页面在图文呈现方面的规范要求，旨在确保页面内容准确、易读且引用规范。

## 页面图表模板

为清晰展示 NVMe 架构的核心组件及其关系，建议使用以下 Mermaid 流程图模板：

```mermaid
flowchart LR
    Host[Host software] --> SQ[Submission Queue]
    SQ --> CController]
    C --> CQ[Completion Queue]
    C --> NS[Namespace]
    C --> T[Transport binding]
```

该图是 **解释性重绘**，仅用于表达 Host、Controller、Queue、Namespace 与 Transport 之间的关系，不代表 NVMe 规范原图，且不提供未被来源确认的时序信息。^[visualization-guidelines.md:8-16]

## 图表与表格的适用场景

根据内容的性质选择合适的呈现方式：

**适合用图表表达的内容：**

- [[controller|Controller]] 初始化流程
- Submission Queue / Completion Queue 命令生命周期
- Namespace 资源层级结构
- Transport 边界与绑定关系
- Reset / Shutdown 状态转换
- 错误恢复路径

**适合用表格表达的内容：**

- 寄存器字段定义
- 状态码与错误码
- 命令分类与功能描述
- 能力位（Capability Bits）
- 版本差异对比

## 质量要求

图表创作与引用应遵循以下原则：

- **概念先行**：图表前必须先定义相关概念，图表后应解释读者应观察的边界和要点。^[visualization-guidelines.md:22]
- **明确标注**：每张图都应注明来源类型，区分"解释性重绘"与"规范原图引用"。
- **精确引用**：引用只能指向 `sources/` 中存在的文件；页码不确定时引用文件级来源，并明确标注"不确定页码"。^[visualization-guidelines.md:24]
- **避免混淆**：不应将特定 Transport（如 PCIe）的实现细节描述为 NVMe Base 规范的通用行为。^[visualization-guidelines.md:25]

## 相关信息

- [[NVMe 命令队列机制]]
- NVMe Controller
- NVMe Namespace
- NVMe Transport

## Sources

- [visualization-guidelines.md](../../sources/visualization-guidelines.md)

