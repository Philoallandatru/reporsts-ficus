---
title: Mermaid 流程图模板
summary: NVMe 规范解释性重绘所采用的标准 Mermaid 语法模板及其适用场景
sources:
- visualization-guidelines.md
kind: concept
createdAt: '2026-08-16T06:27:19.638Z'
updatedAt: '2026-08-16T06:27:19.638Z'
tags:
- visualization
- mermaid
- diagramming
aliases:
- mermaid-流程图模板
confidence: 0.9
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: Mermaid 流程图模板是一套用于在 Wiki 页面中可视化复杂系统关系的标准化图表规范。模板采用 `flowchart LR`（从左到右布局），以简洁的结构呈现核心组件及其交互关系
  ^[visualization-guidelines.md:7-14]。
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Mermaid 流程图模板

Mermaid 流程图模板是一套用于在 Wiki 页面中可视化复杂系统关系的标准化图表规范。模板采用 `flowchart LR`（从左到右布局），以简洁的结构呈现核心组件及其交互关系 ^[visualization-guidelines.md:7-14]。

## 基础模板

```mermaid
flowchart LR
    Host[Host software] --> SQ[Submission Queue]
    SQ --> CController]
    C --> CQ[Completion Queue]
    C --> NS[Namespace]
    C --> T[Transport binding]
```

该模板定义了 NVMe 架构中的五个核心概念：Host software（主机软件）、Submission Queue（提交队列）、Controller（控制器）、Completion Queue（完成队列）、Namespace（命名空间）以及 Transport binding（传输绑定）^[visualization-guidelines.md:7-14]。

## 适用场景

适合使用流程图表达的内容包括：Controller 初始化流程、SQ/CQ 命令生命周期、namespace 资源层级、transport 边界、reset/shutdown 状态转换以及错误恢复路径。流程图擅长展示组件之间的关联和状态变化 ^[visualization-guidelines.md:18]。

相比之下，以下内容更适合使用表格表达：协议字段定义、状态码说明、命令分类、能力位（capability bits）以及版本差异对比 ^[visualization-guidelines.md:18]。

## 使用规范

### 概念前置

在图表之前应先定义相关概念，确保读者理解基础术语后再进入可视化内容。同时，图表之后需要解释读者应观察的边界和关键要点 ^[visualization-guidelines.md:22]。

### 来源标注

每张图表必须注明其性质：若为自行绘制的示意图，应标注"解释性重绘"；若引用自外部规范，需标明来源文件与规范页码。引用只能指向 `sources/` 目录中实际存在的文件；当页码不确定时，引用文件级来源并明确说明"不确定页码" ^[visualization-guidelines.md:23-24]。

### 规范边界

不应将特定传输层（如 PCIe）的实现细节错误地描述为通用行为。例如，不应将 PCIe transport 的特性写入 NVMe Base 规范的通用描述中 ^[visualization-guidelines.md:25]。

## 扩展应用

该模板可扩展用于表示其他具有层次结构的系统。在绘制扩展模板时，应保持组件命名的准确性，并确保新增连接关系经过来源确认。扩展时需避免引入未被来源验证的时序信息或内部实现细节 ^[visualization-guidelines.md:16]。

---

## Sources

- visualization-guidelines.md

