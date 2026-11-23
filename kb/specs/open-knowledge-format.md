---
type: Specification
title: Open Knowledge Format (OKF)
description: 面向人类与 AI Agent 的开放、厂商中立的知识表示规范，将 LLM-Wiki 模式标准化为带 YAML frontmatter 的
  Markdown 目录树。
tags:
- okf
- knowledge-base
- agents
- markdown
- spec
status: stable
generated:
  by: antigravity/2026-11
  at: '2026-11-17T02:23:00Z'
sources:
- id: gcp-blog
  resource: https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
  title: Introducing the Open Knowledge Format (Google Cloud Blog)
- id: okf-spec
  resource: https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md
  title: Open Knowledge Format (OKF) Specification v0.2
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 概述

**Open Knowledge Format (OKF)** 是 Google Cloud 发布的开放知识表示规范，将 Andrej Karpathy 提出的 **LLM Wiki** 模式标准化为可移植、可互操作的文件格式。[^gcp-blog]

它不需要专有数据库、SDK 或运行时：一个 OKF Bundle 就是一个由 **Markdown 文件 + YAML Frontmatter** 组成的普通目录树，人类可直接阅读，Git 可直接做版本控制，AI Agent 可直接遍历检索。[^okf-spec]

# 核心设计原则

1. **Minimally opinionated（最小化约束）**：每篇概念文档（Concept）唯一强制要求的字段只有 `type`，其余字段与正文结构由生产者自行决定。
2. **Producer / Consumer independence（生产与消费解耦）**：人类手写的笔记、数据导出脚本生成的元数据、LLM 整理的知识库，都可以用同一套格式被任意 Agent 或可视化工具消费。
3. **Format, not platform（格式而非平台）**：不绑定特定云厂商、数据库、模型或 Agent 框架。

# 目录结构与保留文件名

```text
bundle-root/
├── index.md          # 保留文件名：目录索引，支持 Agent 渐进式披露（§8）
├── log.md            # 保留文件名：按日期倒序记录变更历史（§9）
└── <subdir>/
    ├── index.md
    └── <concept>.md  # 概念文档：文件名（去 .md）即 Concept ID
```

- `index.md`：不应包含 frontmatter（唯一例外是根目录 `index.md` 可携带 `okf_version: "0.2"`）。
- `log.md`：使用 ISO 8601 日期标题（`## YYYY-MM-DD`），最新日期在前。
- 除 `index.md` 与 `log.md` 外的所有 `.md` 文件均为概念文档，必须包含带非空 `type` 字段的 YAML frontmatter。[^okf-spec]

# Frontmatter 常用字段

| 字段 | 必要性 | 说明 |
|---|---|---|
| `type` | **必需** | 概念类型（如 `Specification`、`Architecture`、`Metric`、`Playbook` 等） |
| `title` | 推荐 | 人类可读的展示标题 |
| `description` | 推荐 | 一句话摘要，供 `index.md` 索引与检索预览使用 |
| `tags` | 可选 | 跨目录分类标签列表 |
| `resource` | 可选 | 所描述底层资产的规范 URI |
| `sources` | 可选 | 溯源列表（含 `id`、`resource`、`title` 等） |
| `generated` | 可选 | `{ by, at }`，记录生成者与 ISO 8601 UTC 时间戳 |
| `verified` | 可选 | `{ by, at }`，区分未校验、机器校验与人类审核（`human:<id>`） |
| `status` / `stale_after` | 可选 | 生命周期状态与过期时间 |

[^gcp-blog]: Introducing the Open Knowledge Format, Google Cloud Blog
[^okf-spec]: Open Knowledge Format (OKF) Specification v0.2
