# Silicon Motion SSD Controller Intake

调研日期：2026-08-12。

## 基本信息

| 字段 | 内容 |
|---|---|
| 标题 | Silicon Motion SSD Controllers |
| URL / 本地路径 | https://www.siliconmotion.com/products/client/detail ; https://www.siliconmotion.com/cht/products/enterprise/detail |
| 来源类型 | 厂商资料 |
| 发布组织 | Silicon Motion |
| 版本 / 日期 | 官方产品页；页面状态随时可变 |
| 访问日期 | 2026-08-12 |
| License / 使用限制 | 官方产品页；仅用于工程阅读 |
| 是否需要账户/会员 | 否 |

## 覆盖主题

- Host interface: PCIe Gen5 x4, NVMe 2.0 product positioning; dual-ported enterprise Gen5 and client Gen5 variants.
- Firmware / FTL: public product pages mention controller and firmware family, but not internals.
- NAND media: support for high-speed NAND; enterprise page cites 8 NAND channels and up to 2400 MT/s.
- ECC / reliability: product-family level reliability and efficiency claims.
- Power loss: not a detailed PLP source.
- Performance / QoS: high-performance low-power client and enterprise storage.
- Verification: product family taxonomy and channel count.
- Production / compliance: client versus enterprise SSD positioning.

## 可抽取事实

| Fact ID | 摘要 | 原文定位 | 可用于页面 |
|---|---|---|
| FACT-SMI-001 | Client page shows SM2508 as a PCIe Gen5 x4 NVMe 2.0 SSD controller. | client product page | `controller-vendor-data-acquisition.md` |
| FACT-SMI-002 | Enterprise page shows a dual-ported PCIe Gen5 x4 NVMe controller aimed at enterprise storage and data center computing. | enterprise product page | `controller-hardware-module-boundaries.md`, `production-requirements-and-compliance.md` |
| FACT-SMI-003 | Enterprise page states 8 NAND channels and DDR4-3200 or DDR5-4800 memory interface support. | enterprise product page | `nand-data-acquisition-and-modeling.md`, `flash-scheduler-arbitration.md` |
| FACT-SMI-004 | Silicon Motion positions itself as a NAND flash controller supplier for solid state storage devices. | company/product overview | `controller-vendor-data-acquisition.md` |

## 使用注意

- 公开页适合作为 controller family 和 feature boundary 的入口。
- 这里不能直接推出内部 FTL、ECC pipeline 或命令级行为。
- 如果要进入参数层，需要补 product brief / PDF / version pin。

## 后续动作

- [ ] 加入 `SOURCES.md`
- [ ] 加入 `VERSIONED_SOURCES.md`
- [ ] 摄取到 `llmwiki sources/`
- [ ] 新增或更新概念页
- [ ] 更新 `TRACEABILITY_MATRIX.md`
- [ ] 更新 `TEST_PLAN.md`
