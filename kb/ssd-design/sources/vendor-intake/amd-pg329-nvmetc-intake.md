# AMD PG329 NVMe Target Controller Intake

调研日期：2026-08-12。

## 基本信息

| 字段 | 内容 |
|---|---|
| 标题 | AMD PG329 NVMe Target Controller |
| URL / 本地路径 | https://docs.amd.com/r/en-US/pg329-nvme-target-controller |
| 来源类型 | 厂商资料 |
| 发布组织 | AMD |
| 版本 / 日期 | PG329 v3.0 English, release date 2021-10-27 |
| 访问日期 | 2026-08-12 |
| License / 使用限制 | 官方文档与产品指南；仅用于工程阅读 |
| 是否需要账户/会员 | 否 |

## 覆盖主题

- Host interface: NVMe target / NVMe device view, queue and doorbell handling.
- Firmware / FTL: 不覆盖 NAND FTL。
- NAND media: 不覆盖。
- ECC / reliability: 不覆盖。
- Power loss: 不覆盖。
- Performance / QoS: 仅作为前端模块参考。
- Verification: register、queue、PRP fetch、work queue 术语。
- Production / compliance: 无直接覆盖。

## 可抽取事实

| Fact ID | 摘要 | 原文定位 | 可用于页面 |
|---|---|---|---|
| FACT-AMD-001 | 该 IP 用于在 FPGA 内实现 NVMe device view。 | PG329 overview / IP facts | `controller-vendor-data-acquisition.md`, `controller-rtl-ip-reference.md` |
| FACT-AMD-002 | 文档提供 control/status register、submission queue arbitration、command validation/decode、PRP fetch manager、work queue manager、completion 等模块视角。 | PG329 documentation / IP facts | `controller-hardware-module-boundaries.md` |
| FACT-AMD-003 | IP 与 AMD QDMA 结合，面向 NVMe target / endpoint 参考设计。 | AMD NVMeTC product page | `controller-hardware-module-boundaries.md`, `controller-rtl-ip-reference.md` |
| FACT-AMD-004 | 页面与文档都明确这是 NVMe 1.3 风格的 device view，而非完整 SSD。 | product page / introduction | `controller-vendor-data-acquisition.md` |

## 使用注意

- 该资料是一手厂商参考设计，不是 SSD 产品 controller datasheet。
- 版本已固定，但这是 2021 年的产品指南，后续如果要写“最新”必须回官方页复核。
- 与 NAND、FTL、PLP、LDPC 相关的能力不能从这里直接推导。

## 后续动作

- [ ] 加入 `SOURCES.md`
- [ ] 加入 `VERSIONED_SOURCES.md`
- [ ] 摄取到 `llmwiki sources/`
- [ ] 新增或更新概念页
- [ ] 更新 `TRACEABILITY_MATRIX.md`
- [ ] 更新 `TEST_PLAN.md`

