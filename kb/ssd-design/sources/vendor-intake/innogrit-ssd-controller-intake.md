# InnoGrit SSD Controller Intake

调研日期：2026-08-12。

## 基本信息

| 字段 | 内容 |
|---|---|
| 标题 | InnoGrit SSD Controllers |
| URL / 本地路径 | https://www.innogritcorp.com/ ; https://www.innogritcorp.com/ssdcontrollers/client/ ; https://www.innogritcorp.com/ssdcontrollers/enterprise/ ; https://www.innogritcorp.com/downloadcat/product-documentation/ssd-controllers/ |
| 来源类型 | 厂商资料 |
| 发布组织 | InnoGrit |
| 版本 / 日期 | 官方产品页和 product brief；页面状态随时可变 |
| 访问日期 | 2026-08-12 |
| License / 使用限制 | 官方产品页与 PDF；仅用于工程阅读 |
| 是否需要账户/会员 | 否 |

## 覆盖主题

- Host interface: PCIe Gen4 / Gen5 NVMe 2.0 or NVMe 1.4 controller family positioning.
- Firmware / FTL: product brief points to turnkey controller/firmware products but not internals.
- NAND media: capacity claims and support for SSD controller families.
- ECC / reliability: data security, end-to-end protection, and low-latency positioning.
- Power loss: not a detailed PLP source.
- Performance / QoS: public brief includes throughput and IOPS claims.
- Verification: controller family and product brief taxonomy.
- Production / compliance: data center and client SSD product segmentation.

## 可抽取事实

| Fact ID | 摘要 | 原文定位 | 可用于页面 |
|---|---|---|
| FACT-INGRIT-001 | InnoGrit positions itself as a PCIe Gen5 SSD controller vendor with low-latency claims. | company homepage | `controller-vendor-data-acquisition.md` |
| FACT-INGRIT-002 | The download category page lists controller briefs such as IG5222 and IG5636. | download category page | `controller-vendor-data-acquisition.md` |
| FACT-INGRIT-003 | IG5222 brief shows a PCIe Gen4 x4 NVMe 2.0 controller with capacity up to 8TB. | IG5222 product brief | `controller-vendor-data-acquisition.md`, `performance-qos-write-amplification.md` |
| FACT-INGRIT-004 | IG5636 brief shows PCIe Gen4 x4 NVMe 1.4 data center positioning and capacity up to 16TB. | IG5636 product brief | `production-requirements-and-compliance.md`, `controller-hardware-module-boundaries.md` |

## 使用注意

- InnoGrit 的公开资料常以 product brief 形式出现，适合作为 family-level ingress。
- 如果要进入可执行模型，必须补具体 brief 版本号和更细的字段抽取。
- FAQ 已明确说 detailed documentation 可能需要销售联系，因此不能把公开页想象成完整 spec。

## 后续动作

- [ ] 加入 `SOURCES.md`
- [ ] 加入 `VERSIONED_SOURCES.md`
- [ ] 摄取到 `llmwiki sources/`
- [ ] 新增或更新概念页
- [ ] 更新 `TRACEABILITY_MATRIX.md`
- [ ] 更新 `TEST_PLAN.md`
