# SSD 知识库采集 Backlog

本 backlog 用于持续扩展资料和页面。优先级从 `P0` 到 `P2`。

## P0：把现有知识库变成可复现实验基础

| ID | 任务 | 产出 |
|---|---|---|
| BL-P0-001 | 部分完成：已建立 NVMe、ONFI、JEDEC、PCI-SIG、OCP、SNIA 的版本/访问条件 pins、公开审计记录、artifact/hash manifest、PDF 结构索引、主题定位索引和 NVMe 命令到规范映射，并完成 NVMe Base 2.4、NVM Command Set 1.3、ZNS 1.5、NVMe-MI 2.2 本地 PDF/hash/页数固定；下一步人工复核 Boot 1.4 下载失败、OCP v2.7、ONFI/JEDEC，并开始抽取关键字段表 | [Standards Version Pins](sources/standards-version-pins.yml), [公开标准版本审计](sources/standards-public-audit-2026-08-12.yml), [来源 Artifact 下载与哈希清单](sources/source-artifact-manifest.yml), [PDF Artifact 结构索引](sources/pdf-artifact-index.yml), [PDF 主题定位索引](sources/pdf-topic-locator.yml), [NVMe Command Spec Map](tests/requirements/nvme-command-spec-map.yml), [版本化来源清单](VERSIONED_SOURCES.md) |
| BL-P0-002 | 部分完成：已固定 FEMU、SimpleSSD、MQSim、SPDK、Cosmos+、Linux NVMe、nvme-cli、libnvme 等远端 HEAD commit，并建立 smoke-test 验收矩阵；下一步实际 clone/build/run 并归档日志 | [Open-source Implementation Pins](sources/open-source-implementation-pins.yml), [Implementation Smoke-test Matrix](sources/implementation-smoke-test-matrix.yml), [源码导读](wiki/concepts/source-code-reading-guide.md) |
| BL-P0-003 | 已完成：建立 `fio` 和 `nvme-cli` 基础测试配置目录 | [测试资产目录](tests/README.md) |
| BL-P0-004 | 已完成：把 [TEST_PLAN.md](TEST_PLAN.md) 拆成机器可读测试需求文件 | [机器可读需求映射](tests/requirements/requirements.yml) |
| BL-P0-005 | 已完成：为掉电恢复图补状态转换表 | [掉电保护与恢复](wiki/concepts/power-loss-recovery.md), [掉电恢复状态表](tests/faults/power-loss-state-table.yml) |
| BL-P0-006 | 部分完成：建立 emulator/source hook 矩阵；下一步在 FEMU/SimpleSSD/MQSim/Cosmos+ 中实现确定性触发、日志解析和 pass/fail 判定 | [Emulator Hook Matrix](tests/requirements/emulator-hook-matrix.yml), [Open-source Implementation Pins](sources/open-source-implementation-pins.yml) |
| BL-P0-007 | 部分完成：建立验证证据 schema、报告模板、PLP/LDPC/nvme-cli 样例 evidence log、raw stdout/stderr 样例、nvme-cli 输出字段映射、本地校验器和样例 raw stdout 字段对账；下一步实现真实 emulator/host 日志 parser 并产出实际测试报告 | [Verification Evidence Schema](tests/requirements/verification-evidence-schema.yml), [nvme-cli Output Field Map](tests/requirements/nvme-cli-output-field-map.yml), [验证报告模板](templates/verification-report-template.md), [Sample PLP Evidence Log](tests/evidence/sample-plp-pass.jsonl), [Sample LDPC Evidence Log](tests/evidence/sample-ldpc-pass.jsonl), [Sample nvme-cli Evidence Log](tests/evidence/sample-nvme-cli-readonly-pass.jsonl) |

## P1：补 NAND 和控制器硬件深度

| ID | 任务 | 产出 |
|---|---|---|
| BL-P1-001 | 部分完成：建立 NAND 参数采集矩阵，固定 Micron NOR and NAND Flash Guide 的官方 PDF/hash/页数，并新增 family-level 抽取记录；下一步优先固定 Micron、Western Digital 或 Kioxia 的具体 part datasheet，并按“身份 -> geometry -> timing -> reliability -> retry”顺序抽取 | [NAND 介质参数手册](wiki/concepts/nand-media-parameter-guide.md), [NAND Parameter Extraction Matrix](sources/vendor-intake/nand-parameter-extraction-matrix.yml), [Micron NAND Flash Guide 抽取记录](sources/vendor-intake/micron-nand-flash-guide-intake.md), [NAND Vendor 公开资料 Intake](sources/vendor-intake/nand-vendor-public-materials.md) |
| BL-P1-002 | 部分完成：建立 Kioxia/Samsung/SK hynix/YMTC 公开资料入口；下一步固定具体公开 PDF 或受限 datasheet 访问条件 | [NAND Vendor Intake](sources/vendor-intake/nand-vendor-public-materials.md), [版本化来源清单](VERSIONED_SOURCES.md) |
| BL-P1-003 | 已完成：细化 ECC/LDPC pipeline，包括 hard/soft decode、retry budget、scrub/refresh 和 telemetry | [ECC、LDPC 与可靠性管理](wiki/concepts/ecc-ldpc-reliability.md), [LDPC Pipeline Policy Matrix](tests/requirements/ldpc-pipeline-policy-matrix.yml) |
| BL-P1-004 | 已完成：细化 flash scheduler：channel/die/plane arbitration 和 read-priority | [Flash Scheduler、Channel/Die/Plane Arbitration 与 Read Priority](wiki/concepts/flash-scheduler-arbitration.md), [Flash Scheduler Policy Matrix](tests/requirements/flash-scheduler-policy-matrix.yml) |
| BL-P1-005 | 已完成：细化 DRAM-less/HMB SSD 设计 | [DRAM-less SSD 与 Host Memory Buffer](wiki/concepts/dram-less-hmb-ssd.md), [HMB Policy Matrix](tests/requirements/hmb-policy-matrix.yml) |

## P1：补固件和 FTL 深度

| ID | 任务 | 产出 |
|---|---|---|
| BL-P1-006 | 已完成：为 page mapping、hybrid mapping、DFTL 分别补独立页面 | [FTL Page Mapping](wiki/concepts/ftl-page-mapping.md), [FTL Hybrid / Log-block Mapping](wiki/concepts/ftl-hybrid-log-block-mapping.md), [DFTL / Demand-based Mapping](wiki/concepts/ftl-dftl-demand-based-mapping.md) |
| BL-P1-007 | 已完成：为 GC victim selection 和 wear leveling 补算法对比表 | [GC Victim Selection 与 Wear Leveling 策略](wiki/concepts/gc-wear-leveling-policy.md), [GC Policy Matrix](tests/requirements/gc-policy-matrix.yml) |
| BL-P1-008 | 已完成：为 SLC cache、write cliff 和 destage 策略补页面 | [SLC Cache、Write Cliff 与 Destage 策略](wiki/concepts/slc-cache-write-cliff-destage.md), [SLC Cache Policy Matrix](tests/requirements/slc-cache-policy-matrix.yml) |
| BL-P1-009 | 已完成：补 FDP/streams/placement hint 与内部 FTL 的关系 | [FDP、Streams、Placement Hint 与内部 FTL](wiki/concepts/fdp-streams-placement-hints.md), [Placement Policy Matrix](tests/requirements/placement-policy-matrix.yml) |
| BL-P1-010 | 已完成：补 firmware update metadata compatibility 和 rollback 风险 | [Firmware Update、Metadata Compatibility 与 Rollback](wiki/concepts/firmware-update-rollback.md), [Firmware Update Policy Matrix](tests/requirements/firmware-update-policy-matrix.yml) |

## P2：研究、专利和产品资料

| ID | 任务 | 产出 |
|---|---|---|
| BL-P2-001 | 部分完成：已建立论文采集矩阵和 BibTeX 种子；下一步按条目固定本地 PDF、sha256 和阅读状态 | [SSD 设计论文与 BibTeX 种子](BIBLIOGRAPHY.md), [论文采集矩阵](sources/paper-intake-matrix.yml) |
| BL-P2-002 | 部分完成：已建立专利采集矩阵和检索索引；下一步按方向补至少 5 个同族专利的 intake | [SSD 专利检索索引](PATENT_INDEX.md), [专利采集矩阵](sources/patent-intake-matrix.yml) |
| BL-P2-003 | 部分完成：已建立 controller vendor 采集矩阵；当前已整理 AMD / Microchip / Marvell / Silicon Motion / Phison / Innogrit / Maxio 的入口和字段提取方向，下一步固定具体 brief / guide / PDF | [Controller Vendor Intake](sources/vendor-intake/controller-vendor-public-materials.md), [Controller Vendor Extraction Matrix](sources/vendor-intake/controller-vendor-extraction-matrix.yml) |
| BL-P2-004 | 部分完成：已补平台兼容与安全擦除页，并新增 reset、boot 与 power state 边界页；下一步继续补 Windows NVMe、UEFI/BIOS boot 互操作和 OPAL/TCG 细节 | [平台兼容与安全擦除](wiki/concepts/platform-compatibility-security.md), [Reset、Boot 与 Power State 边界](wiki/concepts/reset-boot-power-state.md) |
| BL-P2-005 | 把 Mermaid 图导出成 PNG/SVG 供不支持 Mermaid 的阅读器使用 | 新增 `maps/rendered/` |

## 维护规则

1. 完成 backlog 项时，在相关页面写明来源版本。
2. 新增概念页后运行 `python tools/check_ssd_wiki.py`。
3. 新增需求后必须同步 `TRACEABILITY_MATRIX.md` 和 `TEST_PLAN.md`。
4. 新增来源后优先写 `templates/source-intake-template.md` 的 intake 文件。
