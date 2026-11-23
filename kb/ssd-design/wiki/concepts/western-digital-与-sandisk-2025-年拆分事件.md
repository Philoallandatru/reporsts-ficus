---
title: Western Digital 与 Sandisk 2025 年拆分事件
summary: Western Digital 于 2025-02-24 完成闪存业务拆分，后续 NAND/Flash 资料应追溯至 Sandisk，WD 历史页面仅作存档参考
sources:
- research-nand-controller-patent-notes.md
kind: concept
createdAt: '2026-08-16T05:52:41.512Z'
updatedAt: '2026-08-16T05:52:41.512Z'
tags:
- wd-sandisk
- corporate-separation
- flash-business
aliases:
- western-digital-与-sandisk-2025-年拆分事件
- WD与S2年
confidence: 0.95
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: Western Digital 与 Sandisk 的企业拆分（spin-off）是指 Western Digital 将其闪存业务正式分拆为独立上市公司的过程。2025
  年 2 月 24 日，Western Digital 宣布拆分完成，闪存业务以 **Sandisk** 品牌独立运营。^[research-nand-controller-paten...
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Western Digital 与 Sandisk 2025 年拆分事件

Western Digital 与 Sandisk 的企业拆分（spin-off）是指 Western Digital 将其闪存业务正式分拆为独立上市公司的过程。2025 年 2 月 24 日，Western Digital 宣布拆分完成，闪存业务以 **Sandisk** 品牌独立运营。^[research-nand-controller-patent-notes.md:26]

## 背景

Western Digital 于 2016 年完成对 Sandisk 的收购，此后 Sandisk 作为 Western Digital 内部的闪存业务部门运营。双方在 BiCS 3D NAND 技术上与 Kioxia 保持联合开发关系。^[research-nand-controller-patent-notes.md:27]

## 时间线

| 时间 | 事件 |
|---|---|
| 2025-02-24 | Western Digital 官方宣布完成闪存业务拆分，Sandisk 作为独立公司正式成立 ^[research-nand-controller-patent-notes.md:26] |
| 2026 年后 | Sandisk 以独立公司身份发布 BiCS10 等新一代闪存产品 ^[research-nand-controller-patent-notes.md:28-29] |

## 对知识库采集的影响

拆分完成后，公开资料的来源归属发生了根本性变化。知识库在采集闪存相关资料时须遵循以下原则：

- **2025 年 2 月 24 日之前**的 Western Digital 闪存/NAND 页面视为历史资料，仅供参考。^[research-nand-controller-patent-notes.md:26]
- **2025 年 2 月 24 日之后**，闪存相关新产品公告、技术白皮书和产品文档应优先查阅 Sandisk 官方页面。^[research-nand-controller-patent-notes.md:26]
- **不可混用**：Western Digital 拆分后主攻 HDD 领域，Sandisk 主攻 NAND/闪存领域，不应将 WD 的 HDD 相关内容与 Sandisk 的闪存资料混为一谈。^[research-nand-controller-patent-notes.md:26]
- BiCS 系列技术的历史渊源（BiCS3/BiCS5/BiCS8）仍可参考 Western Digital 历史发布，因为这些属于双方联合开发阶段的产物。^[research-nand-controller-patent-notes.md:27]

## 当前闪存资料入口

| 品牌 | 定位 | 采集建议 |
|---|---|---|
| Sandisk（独立后） | 闪存/NAND 技术与产品 | 作为当前闪存资料的首要来源 ^[research-nand-controller-patent-notes.md:26] |
| Western Digital（独立后） | HDD 与企业存储 | 闪存资料不再从 WD 更新 ^[research-nand-controller-patent-notes.md:26] |
| Kioxia/Sandisk 联合发布 | BiCS FLASH 技术 | BiCS10 等新一代技术由 Sandisk 独立或与 Kioxia 联合发布 ^[research-nand-controller-patent-notes.md:28-29] |

## 采集标签约定

知识库使用标签 `vendor/wd-sandisk/bics` 统一记录 Western Digital 与 Sandisk 在 BiCS NAND 技术上的历史渊源与当前进展，以拆分完成日期为分界点区分来源归属。^[research-nand-controller-patent-notes.md:71]

## 相关概念

- NAND 控制器与专利研究笔记 — 包含本拆分事件的详细来源梳理
- BiCS FLASH — Sandisk 与 Kioxia 联合开发的 3D NAND 技术路线
- 控制器厂商数据采集与建模 — 拆分后厂商资料采集的通用流程

## 来源

- Western Digital 官方新闻稿（2025-02-24）：https://www.westerndigital.com/company/newsroom/press-releases/2025/2025-02-24-western-digital-completes-planned-company-separation
- Sandisk 拆分常见问题：https://www.sandisk.com/sandisk-separation-faqs
- Sandisk BiCS10 公告（2026-07-02）：https://www.sandisk.com/company/newsroom/press-releases/2026/2026-07-02-sandisk-announces-bics10-1tb-tlc
- Western Digital BiCS5 公告（2020-01-30）：https://www.westerndigital.com/company/newsroom/press-releases/2020/2020-01-30-western-digital-extends-storage-leadership-with-bics5-3d-nand-technology

