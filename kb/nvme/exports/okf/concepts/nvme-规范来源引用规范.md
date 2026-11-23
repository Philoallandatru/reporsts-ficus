---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: e88f92afec84702221b5d289b7972f4276101d04ef84b183e5bd6291d9d24757
  pageDirectory: concepts
  sources:
    - visualization-guidelines.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - nvme-规范来源引用规范
  citations:
    - file: visualization-guidelines.md
      start: 1
      end: 3
    - file: visualization-guidelines.md
      start: 24
      end: 24
    - file: visualization-guidelines.md
      start: 25
      end: 25
    - file: visualization-guidelines.md
      start: 18
      end: 18
    - file: visualization-guidelines.md
      start: 7
      end: 14
    - file: visualization-guidelines.md
      start: 22
      end: 23
    - file: visualization-guidelines.md
      start: 16
      end: 16
title: NVMe 规范来源引用规范
description: NVMe 页面编译时必须遵守的页码引用、文件级来源标注及 transport 细节边界规则
tags:
  - documentation
  - citation-rules
  - provenance
timestamp: "2026-08-16T06:27:18.996Z"
---


# NVMe 规范来源引用规范

本文档定义了 llmwiki 编译 NVMe 相关页面时必须遵守的**来源引用规范**，涵盖视觉呈现、引用规则及质量要求。

## 规范目的

NVMe 技术涉及复杂的协议层次、状态机和多维度概念（如 命令队列、传输绑定、命名空间管理等）。为确保 wiki 页面的准确性与可验证性，所有内容必须遵循统一的引用与可视化标准。^[visualization-guidelines.md:1-3]

## 页面引用规则

### 引用层级

来源引用应遵循以下精度层级：

- **文件级引用**：当页码不确定时，引用到文件层面，并明确标注"不确定页码"
- **行级引用**：当可确定具体规范位置时，引用文件与行范围

引用只能指向 `sources/` 目录下已存在的文件，不得引用未收录的外部来源。^[visualization-guidelines.md:24]

### 禁止行为

- **禁止混用传输层细节**：不得将 PCIe transport 的实现细节描述为 NVMe Base 规范的通用行为
- **禁止无来源引用**：所有实质性主张均需标注来源，不可凭空推断 ^[visualization-guidelines.md:25]

## 页面图表规范

### 图表类型选择

不同内容适合不同表达形式：^[visualization-guidelines.md:18]

| 适合用图表达 | 适合用表表达 |
|-------------|-------------|
| [Controller](/concepts/controller.md) 初始化流程 | 字段定义 |
| SQ/CQ 命令生命周期 | 状态码 |
| Namespace 资源层级 | 命令分类 |
| Transport 边界关系 | 能力位 |
| Reset/Shutdown 状态转换 | 版本差异 |
| 错误恢复路径 | |

### 标准模板

llmwiki 为 NVMe 页面提供了标准流程图模板（使用 Mermaid 语法）：

```mermaid
flowchart LR
    Host[Host software] --> SQ[Submission Queue]
    SQ --> CController]
    C --> CQ[Completion Queue]
    C --> NS[Namespace]
    C --> T[Transport binding]
```

该图展示 NVMe 架构 中的核心组件关系：Host 软件通过提交队列与控制器交互，控制器管理完成队列、命名空间及传输绑定。^[visualization-guidelines.md:7-14]

### 图表使用原则

1. **先定义后图示**：在展示图表之前，必须先定义相关概念
2. **图后说明**：图表展示后应解释读者应关注的边界与要点
3. **来源标注**：每张图表均需注明来源文件与规范页码；若为解释性重绘而非原图复制，需明确标注"解释性重绘" ^[visualization-guidelines.md:22-23]

### 图表性质说明

所有流程图均为**解释性重绘**，仅用于表达组件间的关系，不代表规范原文图示，且不提供未被来源确认的时序信息。^[visualization-guidelines.md:16]

## 质量检查清单

撰写 NVMe 规范页面时，应逐项确认：

- [ ] 所有引用指向 `sources/` 中存在的文件
- [ ] 图表已标注"解释性重绘"或来源页码
- [ ] PCIe transport 特性与 NVMe Base 通用行为未混淆
- [ ] 概念在使用图表前已定义
- [ ] 表格形式用于字段、状态码等结构化数据

## 参见

- NVMe 技术概览
- 命令队列机制
- PCIe Transport
- Namespace 管理
- Controller 初始化

## Sources

- [visualization-guidelines.md](visualization-guidelines.md) — NVMe 图文并茂页面规范（llmwiki 编译规则）

# Citations

1. [visualization-guidelines.md:1-3](/references/visualization-guidelines-0dacfb19.md)
2. [visualization-guidelines.md:24-24](/references/visualization-guidelines-0dacfb19.md)
3. [visualization-guidelines.md:25-25](/references/visualization-guidelines-0dacfb19.md)
4. [visualization-guidelines.md:18-18](/references/visualization-guidelines-0dacfb19.md)
5. [visualization-guidelines.md:7-14](/references/visualization-guidelines-0dacfb19.md)
6. [visualization-guidelines.md:22-23](/references/visualization-guidelines-0dacfb19.md)
7. [visualization-guidelines.md:16-16](/references/visualization-guidelines-0dacfb19.md)
