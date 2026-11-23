# Maxio SSD Controller Intake

调研日期：2026-08-12。

## 基本信息

| 字段 | 内容 |
|---|---|
| 标题 | Maxio SSD Controllers |
| URL / 本地路径 | https://www.maxio-tech.com/product/11628/11631/ ; https://www.maxio-tech.com/product/11628/11631/11753/ ; https://www.maxio-tech.com/product/11628/11631/11753/11733/ ; https://www.maxio-tech.com/product/ |
| 来源类型 | 厂商资料 |
| 发布组织 | Maxio / 联芸科技 |
| 版本 / 日期 | 官方产品页；页面状态随时可变 |
| 访问日期 | 2026-08-12 |
| License / 使用限制 | 官方产品页；仅用于工程阅读 |
| 是否需要账户/会员 | 否 |

## 覆盖主题

- Host interface: PCIe / NVMe controller family positioning, including DRAM-less PCIe NVMe controllers.
- Firmware / FTL: public solution pages mention DRAM-less firmware, SmartCache and customized firmware.
- NAND media: supports MLC/TLC/QLC on main product pages and solutions pages.
- ECC / reliability: Agile ECC, hardware ECC and bad block / wear leveling claims.
- Power loss: public solution pages mention power-loss protection and low power management.
- Performance / QoS: performance, cost, low power, and stability positioning.
- Verification: product-family taxonomy and solution page wording.
- Production / compliance: consumer, industrial and SATA/PCIe solution segmentation.

## 可抽取事实

| Fact ID | 摘要 | 原文定位 | 可用于页面 |
|---|---|---|---|
| FACT-MAXIO-001 | Maxio's home/product pages position the company as a supplier of SATA and PCIe SSD controllers and solutions. | company homepage / product page | `controller-vendor-data-acquisition.md` |
| FACT-MAXIO-002 | The PCIe SSD controller page states support for MLC/TLC/QLC NAND and emphasizes reliability, stability, performance and security. | PCIe SSD controller page | `controller-vendor-data-acquisition.md`, `production-requirements-and-compliance.md` |
| FACT-MAXIO-003 | The DRAM-less PCIe NVMe page states NVMe 1.3/1.4/2.0 support and references Agile ECC plus Smart Cache architecture. | DRAM-less PCIe NVMe page | `dram-less-hmb-ssd.md`, `ecc-ldpc-reliability.md` |
| FACT-MAXIO-004 | The PCIe SSD solution page mentions DRAM-less architecture firmware, SmartCache and power-loss protection. | PCIe SSD solution page | `dram-less-hmb-ssd.md`, `power-loss-recovery.md` |

## 使用注意

- Maxio 的公开资料偏产品解决方案，不是内部 controller spec。
- 页面是中文营销页，后续进入参数层必须补版本号、PDF 或本地固定文件。
- 不要把“支持 MLC/TLC/QLC”和具体 NAND timing 混为一谈。

## 后续动作

- [ ] 加入 `SOURCES.md`
- [ ] 加入 `VERSIONED_SOURCES.md`
- [ ] 摄取到 `llmwiki sources/`
- [ ] 新增或更新概念页
- [ ] 更新 `TRACEABILITY_MATRIX.md`
- [ ] 更新 `TEST_PLAN.md`

