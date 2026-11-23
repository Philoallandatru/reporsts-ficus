# Phison SSD Controller Intake

调研日期：2026-08-12。

## 基本信息

| 字段 | 内容 |
|---|---|
| 标题 | PHISON SSD Controllers |
| URL / 本地路径 | https://www.phison.com/solutions/ssd/ ; https://www.phison.com/e28/ ; https://www.phison.com/e31t/ |
| 来源类型 | 厂商资料 |
| 发布组织 | Phison Electronics |
| 版本 / 日期 | 官方产品页；页面状态随时可变 |
| 访问日期 | 2026-08-12 |
| License / 使用限制 | 官方产品页；仅用于工程阅读 |
| 是否需要账户/会员 | 否 |

## 覆盖主题

- Host interface: PCIe 3.0 / Gen4 / Gen5 SSD controller positioning.
- Firmware / FTL: public pages imply controller plus firmware solutions, but do not expose internals.
- NAND media: product family and capacity range for SSD controller portfolios.
- ECC / reliability: security, reliability, and industrial/automotive positioning.
- Power loss: not a detailed PLP source.
- Performance / QoS: sequence read/write and random IOPS claims on product lines.
- Verification: family taxonomy and product-generation claims.
- Production / compliance: gaming, enterprise, and automotive positioning.

## 可抽取事实

| Fact ID | 摘要 | 原文定位 | 可用于页面 |
|---|---|---|
| FACT-PHISON-001 | Phison presents SSD controllers and storage solutions as a broad controller portfolio. | SSD solutions page | `controller-vendor-data-acquisition.md` |
| FACT-PHISON-002 | The product family page includes controller/interface/form factor/capacity/performance tables. | SSD solutions page | `controller-hardware-module-boundaries.md` |
| FACT-PHISON-003 | The E28 page shows a PCIe Gen5 controller positioned for power users, gamers, and content creators with up to 14.9 GB/s and 3000K-class performance claims. | E28 product page | `controller-vendor-data-acquisition.md`, `performance-qos-write-amplification.md` |
| FACT-PHISON-004 | The E31T page shows a DRAM-less Gen5 controller positioned for maximum efficiency. | E31T product page | `dram-less-hmb-ssd.md`, `performance-qos-write-amplification.md` |

## 使用注意

- 公开页是产品族入口，不是内部 controller spec。
- 性能数字来自产品营销页，后续必须回到 PDF / brief 固定版本。
- 不要把 family page 的容量或速度直接当作 controller hardware limits。

## 后续动作

- [ ] 加入 `SOURCES.md`
- [ ] 加入 `VERSIONED_SOURCES.md`
- [ ] 摄取到 `llmwiki sources/`
- [ ] 新增或更新概念页
- [ ] 更新 `TRACEABILITY_MATRIX.md`
- [ ] 更新 `TEST_PLAN.md`
