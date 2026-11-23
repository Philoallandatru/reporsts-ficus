# SSD 知识库覆盖缺口清单

本页回答“还有哪些内容需要补充”。它不是普通待办列表，而是用来判断知识库是否足以支撑 SSD 控制器设计、固件实现、硬件分解和验证计划。

## 当前状态

截至 2026-08-12，知识库已经覆盖：

- 顶层架构、NVMe 命令生命周期、FTL、元数据、NAND 接口、ECC/LDPC、掉电恢复、QoS、验证平台和量产合规。
- 现有概念页、需求和测试项已覆盖核心路径，且还在持续扩展。
- fio、nvme-cli、机器可读需求映射、NVMe 命令到规范映射、nvme-cli 输出字段映射、故障注入清单、emulator hook 矩阵、验证证据 schema、PLP/LDPC/nvme-cli 样例 evidence log、raw stdout/stderr 样例和本地 evidence 校验器。
- 资料来源目录、版本化来源清单、规范版本 pins、source artifact/hash manifest、PDF artifact 结构索引、PDF 主题定位索引、NAND 参数采集矩阵、开源实现 commit pins、Backlog、模板和本地检查脚本。

主要缺口已经从“没有框架”转为“需要把资料固定到具体版本、把关键算法拆细、把硬件和实验参数落到可复现级别”。

## P0：必须补齐，才能作为可复现实验基础

| 缺口 | 为什么重要 | 当前入口 | 完成标准 |
|---|---|---|---|
| 固定规范版本 | 已建立 NVMe、ONFI、JEDEC、PCI-SIG、OCP、SNIA 的目标版本、访问条件、公开审计记录、artifact/hash manifest、PDF 结构索引、主题定位索引和 NVMe 命令到规范映射；NVMe Base 2.4、NVM Command Set 1.3、ZNS 1.5 与 NVMe-MI 2.2 已完成本地 PDF/hash/页数固定；Boot 1.4 官方 PDF 链接解析成功但脚本下载返回 525 | [版本化来源清单](VERSIONED_SOURCES.md), [Standards Version Pins](sources/standards-version-pins.yml), [公开标准版本审计](sources/standards-public-audit-2026-08-12.yml), [来源 Artifact 下载与哈希清单](sources/source-artifact-manifest.yml), [PDF Artifact 结构索引](sources/pdf-artifact-index.yml), [PDF 主题定位索引](sources/pdf-topic-locator.yml), [NVMe Command Spec Map](tests/requirements/nvme-command-spec-map.yml) | 每个可下载规范记录文件名和 sha256；受限规范记录访问条件；Boot/OCP v2.7、ONFI、JEDEC 通过浏览器/账户人工复核；为已下载 PDF 抽取关键字段表 |
| 固定开源实现 commit | 已固定 FEMU、SimpleSSD、MQSim、SPDK、Cosmos+、Linux NVMe、nvme-cli、libnvme 等远端 HEAD，并新增 smoke-test 验收矩阵；后续仍需实际 clone/build/run | [源码导读](wiki/concepts/source-code-reading-guide.md), [Open-source Implementation Pins](sources/open-source-implementation-pins.yml), [Implementation Smoke-test Matrix](sources/implementation-smoke-test-matrix.yml) | 每个项目补构建环境、关键入口文件、可运行 smoke test 和本地/CI 验证记录 |
| 掉电恢复状态表 | 已新增 `PLP-WIN-*` 状态表，并在 emulator hook 矩阵、证据 schema 和样例 JSONL 中绑定到写路径/GC/checkpoint 插桩点；host-side nvme-cli evidence 也已纳入同一 schema；后续需要实现真实 emulator 触发和日志解析 | [掉电保护与恢复](wiki/concepts/power-loss-recovery.md), [掉电恢复状态表](tests/faults/power-loss-state-table.yml), [Emulator Hook Matrix](tests/requirements/emulator-hook-matrix.yml), [Verification Evidence Schema](tests/requirements/verification-evidence-schema.yml), [Sample PLP Evidence Log](tests/evidence/sample-plp-pass.jsonl), [Sample nvme-cli Evidence Log](tests/evidence/sample-nvme-cli-readonly-pass.jsonl) | 为每个 PLP-WIN 补实际注入代码、真实日志 parser 和自动化判定脚本 |
| llmwiki 编译状态 | 目前已有源材料，但自动编译状态缺失 | [llmwiki 使用说明](LLMWIKI.md) | 解决 provider access 后生成 compiled pages，并记录输入、输出和审阅结果 |
| 验证证据闭环落地 | 已有 evidence schema、hook matrix、fault matrix、样例日志和桥接页；还需把真实 emulator/host parser 接进自动判定 | [验证证据与故障注入闭环](wiki/concepts/verification-evidence-and-fault-bridge.md), [Verification Evidence Schema](tests/requirements/verification-evidence-schema.yml), [Emulator Hook Matrix](tests/requirements/emulator-hook-matrix.yml) | 为 PLP/LDPC/host command/fault 注入补真实运行管线和 CI 判定 |

## P1：固件设计深度

| 缺口 | 为什么重要 | 当前入口 | 完成标准 |
|---|---|---|---|
| Page mapping、hybrid mapping、DFTL 独立页 | 已新增拆分页；后续需要绑定实现代码和实验 profile | [FTL Page Mapping](wiki/concepts/ftl-page-mapping.md), [FTL Hybrid / Log-block Mapping](wiki/concepts/ftl-hybrid-log-block-mapping.md), [DFTL / Demand-based Mapping](wiki/concepts/ftl-dftl-demand-based-mapping.md) | 每页补 FEMU/SimpleSSD/MQSim/Cosmos+ 对应源码入口和可运行实验 |
| GC victim selection 对比 | 已新增策略页和机器可读矩阵；后续需要绑定 simulator/source code 实现点 | [GC Victim Selection 与 Wear Leveling 策略](wiki/concepts/gc-wear-leveling-policy.md), [GC Policy Matrix](tests/requirements/gc-policy-matrix.yml) | 为每个 `GC-POL-*` 补 FEMU/SimpleSSD/MQSim/SPDK 对应源码入口和实验参数 |
| Wear leveling 和 refresh 策略 | 已覆盖 dynamic/static wear leveling，并在 LDPC pipeline/hook 矩阵、证据 schema 和 LDPC 样例日志中补 read-retry/recovery 触发；后续需要接真实 emulator hook | [GC Victim Selection 与 Wear Leveling 策略](wiki/concepts/gc-wear-leveling-policy.md), [ECC、LDPC 与可靠性管理](wiki/concepts/ecc-ldpc-reliability.md), [LDPC Pipeline Policy Matrix](tests/requirements/ldpc-pipeline-policy-matrix.yml), [Emulator Hook Matrix](tests/requirements/emulator-hook-matrix.yml), [Verification Evidence Schema](tests/requirements/verification-evidence-schema.yml), [Sample LDPC Evidence Log](tests/evidence/sample-ldpc-pass.jsonl) | 为 retention refresh、read disturb scrub 补注入脚本、日志 parser 和 block health counters |
| SLC cache 与 write cliff | 已新增策略页、机器可读矩阵和 fio profile；后续需要绑定 emulator counters | [SLC Cache、Write Cliff 与 Destage 策略](wiki/concepts/slc-cache-write-cliff-destage.md), [SLC Cache Policy Matrix](tests/requirements/slc-cache-policy-matrix.yml), [fio SLC cache write cliff](tests/profiles/fio/slc-cache-write-cliff.fio) | 为每个 `SLC-POL-*` 补实现计数器、日志字段和自动判定脚本 |
| FDP、streams、placement hint | 已新增概念页和机器可读矩阵；后续需要绑定 NVMe 字段和实验 workload | [FDP、Streams、Placement Hint 与内部 FTL](wiki/concepts/fdp-streams-placement-hints.md), [Placement Policy Matrix](tests/requirements/placement-policy-matrix.yml) | 为每个 `PLC-POL-*` 补 NVMe 字段、主机工具命令、emulator hook 和 telemetry |
| Firmware update 回滚 | 已新增概念页、策略矩阵和状态表；后续需要绑定 nvme-cli/SPDK 命令脚本 | [Firmware Update、Metadata Compatibility 与 Rollback](wiki/concepts/firmware-update-rollback.md), [Firmware Update Policy Matrix](tests/requirements/firmware-update-policy-matrix.yml), [Firmware Update State Table](tests/faults/firmware-update-state-table.yml) | 为每个 `FW-POL-*` 和 `FWUP-WIN-*` 补 host 命令、emulator hook、event log 字段和自动判定 |

## P1：硬件与 NAND 深度

| 缺口 | 为什么重要 | 当前入口 | 完成标准 |
|---|---|---|---|
| NAND vendor datasheet 参数抽取 | 已建立公开 vendor intake 和机器可读参数采集矩阵，固定 Micron NOR and NAND Flash Guide 的官方 PDF/hash/页数，并新增 family-level 抽取记录；真实 NAND 的 timing、geometry、read retry 和坏块规则仍需具体 part/PDF 固定 | [NAND 介质参数手册](wiki/concepts/nand-media-parameter-guide.md), [NAND Vendor Intake](sources/vendor-intake/nand-vendor-public-materials.md), [NAND Parameter Extraction Matrix](sources/vendor-intake/nand-parameter-extraction-matrix.yml), [Micron NAND Flash Guide 抽取记录](sources/vendor-intake/micron-nand-flash-guide-intake.md) | 为 Micron、Kioxia、Samsung、SK hynix、YMTC 固定具体 part number、document revision、sha256、geometry、timing、retry、ECC 要求 |
| Flash scheduler 独立页 | 已新增概念页、机器可读矩阵和 hook 矩阵；后续需要绑定 NAND vendor timing 并实现 scheduler trace | [Flash Scheduler、Channel/Die/Plane Arbitration 与 Read Priority](wiki/concepts/flash-scheduler-arbitration.md), [Flash Scheduler Policy Matrix](tests/requirements/flash-scheduler-policy-matrix.yml), [Emulator Hook Matrix](tests/requirements/emulator-hook-matrix.yml) | 为每个 `FSCH-POL-*` 补 ONFI/vendor timing 参数、channel/die telemetry、suspend/timeout 注入 hook |
| DRAM-less 与 HMB | 已新增概念页、机器可读矩阵、HMB miss storm profile 和 hook 矩阵；后续需要绑定 NVMe HMB 字段和 host 命令 | [DRAM-less SSD 与 Host Memory Buffer](wiki/concepts/dram-less-hmb-ssd.md), [HMB Policy Matrix](tests/requirements/hmb-policy-matrix.yml), [fio HMB mapping miss storm](tests/profiles/fio/hmb-mapping-miss-storm.fio), [Emulator Hook Matrix](tests/requirements/emulator-hook-matrix.yml) | 为每个 `HMB-POL-*` 补 NVMe feature 字段、host 命令、DMA fault hook、telemetry 字段和自动判定 |
| LDPC pipeline 细化 | 已新增 hard decode、read retry ladder、soft decode/LLR、QoS guard、scrub/refresh、metadata priority、uncorrectable telemetry、hook 矩阵和可校验样例日志；后续需要绑定 NAND vendor retry table 并实现真实注入点 | [ECC、LDPC 与可靠性管理](wiki/concepts/ecc-ldpc-reliability.md), [LDPC Pipeline Policy Matrix](tests/requirements/ldpc-pipeline-policy-matrix.yml), [Emulator Hook Matrix](tests/requirements/emulator-hook-matrix.yml), [Sample LDPC Evidence Log](tests/evidence/sample-ldpc-pass.jsonl) | 为每个 `LDPC-POL-*` 补 vendor 参数、ECC engine counters、fault hook、真实日志 parser 和自动判定脚本 |
| 控制器 RTL/IP 参考 | 已新增控制器 RTL / IP 参考页，但还需要更细的 register/queue/DMA 交互示意和 vendor brief 摘录 | [控制器 RTL / IP 参考](wiki/concepts/controller-rtl-ip-reference.md), [控制器硬件模块边界](wiki/concepts/controller-hardware-module-boundaries.md) | 抽取 AMD PG329、Cosmos+、FPGA NVMe target 的 interface checklist 和可核对字段 |

## P2：资料库广度

| 缺口 | 为什么重要 | 当前入口 | 完成标准 |
|---|---|---|---|
| 论文与 BibTeX | 已建立初始索引；还需要逐篇固定 PDF sha256 和阅读摘录 | [SSD 设计论文与 BibTeX 种子](BIBLIOGRAPHY.md) | 每篇论文补本地 PDF 文件名、sha256、关键图表摘录和关联概念页 |
| 专利族索引 | 已建立检索索引；还需要按方向建立 patent family intake | [SSD 专利检索索引](PATENT_INDEX.md) | 每个方向至少 5 个同族专利，记录 assignee、priority date、claim summary |
| Controller vendor 公开资料 | 已建立 controller vendor intake；还需要下载/固定 product brief | [Controller Vendor Intake](sources/vendor-intake/controller-vendor-public-materials.md) | 采集 Microchip、Marvell、Silicon Motion、Phison、Innogrit、Maxio 的公开 brief/app note |
| 平台与安全资料 | 已新增平台兼容与安全擦除页，但仍可继续补 Windows/UEFI 互操作和 TCG/Opal 细节 | [平台兼容与安全擦除](wiki/concepts/platform-compatibility-security.md), [量产需求与合规](wiki/concepts/production-requirements-and-compliance.md) | 继续补 Windows/UEFI 互操作、sanitize 细粒度语义和安全版本策略 |
| Reset / boot / power state | 已新增 reset、boot 与 power state 边界页；后续可继续补 UEFI/BIOS 启动时序、power state 迁移和 telemetry 字段 | [Reset、Boot 与 Power State 边界](wiki/concepts/reset-boot-power-state.md), [NVMe 寄存器、队列与状态机](wiki/concepts/nvme-register-queue-state.md) | 为 controller reset、FLR、PERST#、power cycle、shutdown、firmware activation 补更细的状态表和主机互操作记录 |
| 遥测与现场调试 | 已新增遥测、日志与现场调试页，但仍可继续补 OCP telemetry 语义和 crash dump 字段 | [遥测、日志与现场调试](wiki/concepts/telemetry-logging-field-debug.md), [量产需求与合规](wiki/concepts/production-requirements-and-compliance.md) | 补 persistent event、crash dump、field debug 包和导出格式 |
| Mermaid 图导出 | 部分阅读器不渲染 Mermaid | [架构图](maps/architecture-overview.md) | 生成 PNG/SVG，并在 README 与 MkDocs 中链接 |

## 推荐补充顺序

1. 按 [来源 Artifact 下载与哈希清单](sources/source-artifact-manifest.yml) 继续为允许下载的规范补 PDF 文件名和 sha256；按 [PDF Artifact 结构索引](sources/pdf-artifact-index.yml) 为已下载 PDF 抽取关键字段表。
2. 按 [Implementation Smoke-test Matrix](sources/implementation-smoke-test-matrix.yml) 为 [Open-source Implementation Pins](sources/open-source-implementation-pins.yml) 中的项目补本地 clone、构建环境、关键源码入口和 smoke test。
3. 按 [Emulator Hook Matrix](tests/requirements/emulator-hook-matrix.yml) 和 [Verification Evidence Schema](tests/requirements/verification-evidence-schema.yml) 为 PLP/LDPC/flash scheduler/HMB 补实际注入方式、真实日志 parser 和自动判定脚本；现有 [Sample PLP Evidence Log](tests/evidence/sample-plp-pass.jsonl) 和 [Sample LDPC Evidence Log](tests/evidence/sample-ldpc-pass.jsonl) 只作为格式基准。
4. 为 FTL mapping 拆分页补源码入口和实验 profile。
5. 按 [NAND Parameter Extraction Matrix](sources/vendor-intake/nand-parameter-extraction-matrix.yml) 固定 Micron 或 Western Digital 的公开 PDF，再扩展到 Kioxia、Samsung、SK hynix、YMTC。
6. 把固定后的 NAND geometry/timing/read-retry 参数接入 flash scheduler、LDPC pipeline 和 emulator/FPGA hook。
7. 为 `BIBLIOGRAPHY.md`、[SSD 专利检索索引](PATENT_INDEX.md) 和 vendor intake 补本地文件/hash。
8. 解决 `llmwiki` provider access，生成自动编译页面并人工审阅。

## 维护规则

1. 每补一个缺口，都要更新 [采集 Backlog](BACKLOG.md) 的状态。
2. 每新增资料，都要更新 [版本化来源清单](VERSIONED_SOURCES.md) 或 [资料来源目录](SOURCES.md)。
3. 每新增概念页，都要加入 [Wiki 首页](wiki/index.md)、[知识地图](KNOWLEDGE_MAP.md) 和 `mkdocs.yml`。
4. 每新增需求或测试，都要同步 [需求到验证追踪矩阵](TRACEABILITY_MATRIX.md)、[测试计划](TEST_PLAN.md) 和 `tests/requirements/requirements.yml`。
5. 完成后运行：

```powershell
python tools/check_ssd_wiki.py
```
