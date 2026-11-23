# Microchip Flashtec NVMe Controller Intake

调研日期：2026-08-12。

## 基本信息

| 字段 | 内容 |
|---|---|
| 标题 | Flashtec NVMe Controllers |
| URL / 本地路径 | https://www.microchip.com/en-us/products/storage/flashtec-nvme-controllers |
| 来源类型 | 厂商资料 |
| 发布组织 | Microchip Technology |
| 版本 / 日期 | 官方产品页；页面状态随时可变 |
| 访问日期 | 2026-08-12 |
| License / 使用限制 | 官方产品页；仅用于工程阅读 |
| 是否需要账户/会员 | 否 |

## 覆盖主题

- Host interface: standard NVMe host interface, form factor support, PCIe generation claims.
- Firmware / FTL: 公开页强调 on-chip flash management，但不披露内部实现。
- NAND media: next-generation NAND technologies, ONFI support in product family materials.
- ECC / reliability: reliability、security、flexibility 是公开卖点。
- Power loss: evaluation / reference design materials may mention power-sensitive use cases.
- Performance / QoS: performance, random read/write, enterprise and data center positioning.
- Verification: product family and reference design terminology.
- Production / compliance: enterprise / data-center SSD context.

## 可抽取事实

| Fact ID | 摘要 | 原文定位 | 可用于页面 |
|---|---|---|---|
| FACT-MCHP-001 | Flashtec NVMe controllers 面向 enterprise 和 data center SSD。 | product page summary | `controller-vendor-data-acquisition.md`, `production-requirements-and-compliance.md` |
| FACT-MCHP-002 | 官方产品页明确强调 standard NVMe host interface。 | product page | `controller-hardware-module-boundaries.md` |
| FACT-MCHP-003 | 产品家族公开材料强调 minimal host processing and memory resources。 | product page summary | `dram-less-hmb-ssd.md`, `controller-vendor-data-acquisition.md` |
| FACT-MCHP-004 | 公开资料与新闻稿显示 Flashtec NVMe 3108 / 5016 等家族覆盖 PCIe Gen4 / Gen5 方向。 | product page / news release / reference design | `controller-vendor-data-acquisition.md` |

## 使用注意

- 该资料适合作为产品族和功能边界入口，不适合直接当成 RTL 或 FTL 设计说明。
- 产品页会随时间变化；后续如果要固化字段，需要补对应 PDF、版本号和 sha256。
- 这里强调的 security、flexibility 和 reliability 是公开卖点，不是内部实现细节。

## 后续动作

- [ ] 加入 `SOURCES.md`
- [ ] 加入 `VERSIONED_SOURCES.md`
- [ ] 摄取到 `llmwiki sources/`
- [ ] 新增或更新概念页
- [ ] 更新 `TRACEABILITY_MATRIX.md`
- [ ] 更新 `TEST_PLAN.md`

