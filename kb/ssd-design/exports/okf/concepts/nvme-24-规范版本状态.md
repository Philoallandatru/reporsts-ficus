---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 694cb4f270fa7a581357612ab98af70a8fc9aaddd086914e3d7f3a6c60d537b5
  pageDirectory: concepts
  sources:
    - research-source-catalog.md
  confidence: 0.9
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - nvme-24-规范版本状态
    - N2规
  citations:
    - file: research-source-catalog.md
      start: 12
      end: 12
    - file: research-source-catalog.md
      start: 11
      end: 12
    - file: research-source-catalog.md
      start: 11
      end: 11
title: NVMe 2.4 规范版本状态
description: 截至 2026-08-12，NVMe 2.4 已于 2026-08-04 发布，版本迭代速度加快，需固定 PDF 版本进行引用
tags:
  - NVMe规范
  - 版本追踪
  - 规范管理
timestamp: "2026-08-16T05:56:09.613Z"
---


# NVMe 2.4 规范版本状态

## 发布概览

截至 2026-08-12，官方资料明确指出 **NVMe 2.4** 已于 **2026-08-04** 正式发布。^[research-source-catalog.md:12]

NVMe 2.4 归属于 NVM Express Base Specification 规范体系，是 NVMe 标准家族的核心基础规范，负责定义控制器模型、队列机制、命名空间以及 Admin 命令集和 NVM 命令集的行为。^[research-source-catalog.md:11-12]

## 规范层级

NVM Express 规范家族包含多个层次，NVMe Base Specification 是其中最高权威层，负责描述主机可见的 NVMe 行为。^[research-source-catalog.md:11]

| 层级 | 说明 |
|---|---|
| NVMe Base Specification | 核心协议：控制器模型、队列、命名空间、Admin/NVM 命令 |
| Command Set Specifications | 特定命令集扩展（如 ZNS、NVM Command Set） |
| Transport Specifications | 传输层定义（如 NVMe-oF、PCIe Transport） |
| NVMe-MI | 管理接口规范（带外管理） |

## 版本引用原则

引用 NVMe 规范字段时，应**在发布页面固定 PDF 版本号**，避免因规范迭代导致引用失效。^[research-source-catalog.md:12]

建议从以下官方入口获取规范文档：

- 规范索引页：https://nvmexpress.org/specifications/
- Base Specification 专项页：https://nvmexpress.org/specification/nvm-express-base-specification/

## 与本知识库的关联

NVMe 规范是以下各页面的最高权威参考：

- NVMe 寄存器、队列与状态机 — 规范中定义的寄存器、队列门铃和控制器状态机
- 控制器硬件模块边界 — 规范中的前端模块（PCIe endpoint、Queue manager、PRP/SGL walker）
- 控制器 RTL / IP 参考 — AMD PG329 等参考实现对 NVMe Base Specification 的工程映射

## 规范演进方向

NVMe 2.x 系列在 2.0 阶段已引入若干重要更新，包括：

- 新增 NVM Command Set
- 扩展命名空间能力
- 增强错误报告和遥测机制

2.4 版本预计在此基础上继续完善可靠性、功耗管理和多命名空间场景。实际细节需以发布后的正式 PDF 内容为准。

## Sources

- [NVM Express Specifications — 规范索引](https://nvmexpress.org/specifications/)
- [NVM Express Base Specification — 发布页面](https://nvmexpress.org/specification/nvm-express-base-specification/)
- [SSD firmware and hardware design research source catalog](research-source-catalog.md)

# Citations

1. [research-source-catalog.md:12-12](/references/research-source-catalog-b219c498.md)
2. [research-source-catalog.md:11-12](/references/research-source-catalog-b219c498.md)
3. [research-source-catalog.md:11-11](/references/research-source-catalog-b219c498.md)
