---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: c934f9464620add953b845fdf487b0e14824d5db435104c8bd89ab22a4e04a76
  pageDirectory: concepts
  sources:
    - research-nand-controller-patent-notes-53079fdd.md
  confidence: 0.9
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - wd-与-sandisk-企业分离后的闪存资料归属
    - W与S企
  citations:
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 33
      end: 33
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 34
      end: 34
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 35
      end: 35
    - file: research-nand-controller-patent-notes-53079fdd.md
      start: 78
      end: 78
title: WD 与 Sandisk 企业分离后的闪存资料归属
description: Western Digital 于 2025-02-24 完成闪存业务分离，BiCS 技术资料的历史归属与当前归属变化，以及对此后 NAND 资料采集来源的影响。
tags:
  - vendor
  - sandisk
  - western-digital
timestamp: "2026-08-16T05:50:30.833Z"
---


# WD 与 Sandisk 企业分离后的闪存资料归属

Western Digital（以下简称 WD）与 Sandisk 的企业分离于 2025 年 2 月 24 日正式完成。此次分离明确了 Western Digital 与 Sandisk 在闪存资料上的各自归属，对知识库的资料采集、来源追溯和版本管理具有直接影响。

## 分离背景

Western Digital 与 Sandisk 的合作关系可追溯至 Sandisk 被 WD 收购期间。在合并期间，Sandisk 的闪存业务（包括 NAND 技术开发、BiCS FLASH 代际演进、与 Kioxia 的联合开发等）统一以 Western Digital 主体对外发布。2025 年分离完成后，闪存业务独立为 Sandisk 公司，原 WD 主体保留 HDD 业务。 ^[research-nand-controller-patent-notes-53079fdd.md:33]

## 资料归属原则

### 当前闪存资料

2025 年 2 月 24 日之后发布的闪存相关资料，包括但不限于 BiCS 代际更新、NAND 产品发布、技术白皮书、新闻稿等，应归属 **Sandisk**。采集时应优先查找 Sandisk 官方页面，例如 Sandisk 新闻室（press releases）和 Sandisk 分离 FAQ 页面。 ^[research-nand-controller-patent-notes-53079fdd.md:33]

### 历史闪存资料

2025 年 2 月 24 日之前的 Western Digital 官方发布的闪存资料仍具有历史参考价值，可作为 BiCS 代际演进、Kioxia/WD 联合开发上下文的重要来源。例如 WD 于 2020 年发布的 BiCS5 相关公告可用于追溯 3D NAND 技术路线图的早期阶段。 ^[research-nand-controller-patent-notes-53079fdd.md:34]

### 注意事项

- **不得混用**：分离后不应将 WD 的 HDD 相关资料与 Sandisk 的闪存资料混淆。
- **来源区分**：记录资料发布时的公司主体名称和日期，作为来源归属的关键标识。
- **产品线核实**：部分 WD 页面在分离前后可能存在过渡期遗留内容，采集时应核对发布主体。

## 典型资料归属示例

| 资料类型 | 归属主体 | 判定依据 |
|---|---|---|
| BiCS10 发布（2026-07-02） | Sandisk | Sandisk 官方新闻稿，明确归属 Sandisk ^[research-nand-controller-patent-notes-53079fdd.md:35] |
| BiCS5 发布（2020-01-30） | Western Digital（历史） | 发布于分离前，保留为历史参考 ^[research-nand-controller-patent-notes-53079fdd.md:34] |
| Sandisk 分离 FAQ | Sandisk | Sandisk 官方页面，明确说明分离后资料归属 ^[research-nand-controller-patent-notes-53079fdd.md:78] |
| WD HDD 产品页面 | Western Digital | 属于分离后 WD 保留业务，与闪存无关 |

## 对资料采集的建议

1. **建立来源时间戳机制**：每条资料记录应包含发布主体和日期，以便在分离后准确定位归属。
2. **分离后优先查 Sandisk**：当需要当前 NAND/闪存资料时，首先访问 Sandisk 官方页面。
3. **历史资料保留索引**：WD 历史闪存资料仍具有参考价值，不应丢弃，但需标注为"historical"或"pre-separation"状态。
4. **核对 sha256 与版本**：由于部分页面在分离过渡期可能更新，采集时应记录文件 sha256 和页面版本信息。

## 相关概念

- BiCS FLASH — Sandisk（原 WD）与 Kioxia 联合开发的 3D NAND 技术品牌
- 闪存控制器资料采集 — 更通用的控制器厂商公开资料采集流程
- Kioxia 与 Sandisk 的 BiCS 合作 — Kioxia/Sandisk 在 3D NAND 领域的联合开发背景

## Sources

- [research-nand-controller-patent-notes-53079fdd.md](https://github.com/your-repo/sources/research/research-nand-controller-patent-notes-53079fdd.md) — 包含 WD/Sandisk 分离相关的 vendor intake 结论（第 33–35、78 行）

# Citations

1. [research-nand-controller-patent-notes-53079fdd.md:33-33](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
2. [research-nand-controller-patent-notes-53079fdd.md:34-34](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
3. [research-nand-controller-patent-notes-53079fdd.md:35-35](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
4. [research-nand-controller-patent-notes-53079fdd.md:78-78](/references/research-nand-controller-patent-notes-53079fdd-e52ba439.md)
