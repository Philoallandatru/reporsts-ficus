# Marvell SSD Controllers Intake

调研日期：2026-08-12。

## 基本信息

| 字段 | 内容 |
|---|---|
| 标题 | SSD Controllers |
| URL / 本地路径 | https://www.marvell.com/products/ssd-controllers.html |
| 来源类型 | 厂商资料 |
| 发布组织 | Marvell |
| 版本 / 日期 | 官方产品页；页面状态随时可变 |
| 访问日期 | 2026-08-12 |
| License / 使用限制 | 官方产品页；仅用于工程阅读 |
| 是否需要账户/会员 | 否 |

## 覆盖主题

- Host interface: PCIe and NVMe generation / controller portfolio positioning.
- Firmware / FTL: 公开页强调 technology leadership in IP and firmware, but does not disclose internals.
- NAND media: product family supports high-speed NAND and controller portfolios for SSD categories.
- ECC / reliability: public materials mention advanced error correction and data protection themes.
- Power loss: not a detailed PLP source, but power efficiency and data protection are visible claims.
- Performance / QoS: performance-optimized, efficient, feature-rich controller positioning.
- Verification: product family taxonomy and generation claims.
- Production / compliance: data center flash storage positioning.

## 可抽取事实

| Fact ID | 摘要 | 原文定位 | 可用于页面 |
|---|---|---|---|
| FACT-MRVL-001 | Marvell 把 SSD controllers 定位为 high-performance、cost-efficient 存储方案。 | product page summary | `controller-vendor-data-acquisition.md` |
| FACT-MRVL-002 | 公开页强调 Bravera SSD controllers 和 scalable embedded processors。 | product page summary | `controller-hardware-module-boundaries.md` |
| FACT-MRVL-003 | Marvell 公开材料把 technology leadership in IP and firmware 作为卖点。 | product page / related release | `controller-rtl-ip-reference.md`, `controller-vendor-data-acquisition.md` |
| FACT-MRVL-004 | 公开页面和新闻稿显示其 SSD controller 线覆盖 data center、PCIe Gen5/Gen6 和 security/data protection 叙事。 | product page / press release / blog | `platform-compatibility-security.md`, `production-requirements-and-compliance.md` |

## 使用注意

- 该资料适合作为 controller family 和 market positioning 入口。
- 页面内容偏产品叙事，不能直接映射成可实现的模块边界。
- 如果后续要做具体 controller family 记录，需要补具体 family 页面或 PDF。

## 后续动作

- [ ] 加入 `SOURCES.md`
- [ ] 加入 `VERSIONED_SOURCES.md`
- [ ] 摄取到 `llmwiki sources/`
- [ ] 新增或更新概念页
- [ ] 更新 `TRACEABILITY_MATRIX.md`
- [ ] 更新 `TEST_PLAN.md`

