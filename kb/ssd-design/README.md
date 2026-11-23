# SSD 固件与硬件设计知识库

本知识库面向想理解或实现 SSD 控制器、固件和验证平台的工程读者。它把资料分成三层：

- `wiki/`：已经整理过的中文知识页，可直接阅读。
- `sources/`：可被 `llmwiki` 摄取的原始资料清单和种子文档。
- `SOURCES.md`：持续扩展的权威资料索引，优先收录规范、官方文档、源码仓库和论文主页。

本库与已有 `nvme-wiki`、`pcie-wiki` 互补：NVMe/PCIe 负责主机接口和传输协议，本库聚焦 SSD 设备内部的控制器、FTL、NAND、ECC、掉电保护、固件流程和硬件实现。

如果你想快速找路：

- 看 SSD 内部怎么分层：先读 [SSD 系统架构](wiki/concepts/ssd-system-architecture.md)
- 追一条 host 命令怎么进 SSD：先读 [SSD 内部的 NVMe 命令生命周期](wiki/concepts/nvme-command-lifecycle-in-ssd.md)
- 看 FTL 怎么落盘和恢复：先读 [FTL 与固件职责](wiki/concepts/firmware-ftl.md) 和 [FTL 元数据格式与恢复约定](wiki/concepts/ftl-metadata-format-and-recovery-conventions.md)
- 看验证和证据怎么闭环：先读 [SSD 验证矩阵](wiki/concepts/ssd-verification-matrix.md) 和 [验证证据与故障注入闭环](wiki/concepts/verification-evidence-and-fault-bridge.md)

## 快速入口

### 阅读入口

- [知识地图](KNOWLEDGE_MAP.md)
- [SSD 设计术语表](GLOSSARY.md)
- [需求到验证追踪矩阵](TRACEABILITY_MATRIX.md)
- [SSD 知识库测试计划模板](TEST_PLAN.md)
- [资料来源目录](SOURCES.md)
- [版本化来源清单](VERSIONED_SOURCES.md)
- [SSD 设计论文与 BibTeX 种子](BIBLIOGRAPHY.md)
- [SSD 专利检索索引](PATENT_INDEX.md)
- [覆盖缺口清单](COVERAGE_GAPS.md)
- [Wiki 首页](wiki/index.md)
- [SSD 控制器架构总览](maps/architecture-overview.md)
- [读写路径图](maps/write-read-path.md)
- [掉电恢复流程图](maps/recovery-flow.md)
- [SSD 系统架构](wiki/concepts/ssd-system-architecture.md)
- [最小 SSD 控制器实现路线](wiki/concepts/minimal-ssd-controller-roadmap.md)
- [NVMe 寄存器、队列与状态机](wiki/concepts/nvme-register-queue-state.md)
- [SSD 内部的 NVMe 命令生命周期](wiki/concepts/nvme-command-lifecycle-in-ssd.md)
- [FTL 与固件职责](wiki/concepts/firmware-ftl.md)
- [FTL 设计深水区](wiki/concepts/ftl-design-deep-dive.md)
- [FTL Page Mapping](wiki/concepts/ftl-page-mapping.md)
- [FTL Hybrid / Log-block Mapping](wiki/concepts/ftl-hybrid-log-block-mapping.md)
- [DFTL / Demand-based Mapping](wiki/concepts/ftl-dftl-demand-based-mapping.md)
- [FTL 元数据格式与恢复约定](wiki/concepts/ftl-metadata-format-and-recovery-conventions.md)
- [控制器 RTL / IP 参考](wiki/concepts/controller-rtl-ip-reference.md)
- [GC Victim Selection 与 Wear Leveling 策略](wiki/concepts/gc-wear-leveling-policy.md)
- [SLC Cache、Write Cliff 与 Destage 策略](wiki/concepts/slc-cache-write-cliff-destage.md)
- [FDP、Streams、Placement Hint 与内部 FTL](wiki/concepts/fdp-streams-placement-hints.md)
- [Firmware Update、Metadata Compatibility 与 Rollback](wiki/concepts/firmware-update-rollback.md)
- [控制器硬件与 NAND 接口](wiki/concepts/hardware-controller-and-nand.md)
- [NAND 介质参数手册](wiki/concepts/nand-media-parameter-guide.md)
- [NAND 数据采集与建模](wiki/concepts/nand-data-acquisition-and-modeling.md)
- [NAND 参数抽取与建模流程](wiki/concepts/nand-parameter-extraction-workflow.md)
- [控制器厂商数据采集与建模](wiki/concepts/controller-vendor-data-acquisition.md)
- [控制器硬件模块边界](wiki/concepts/controller-hardware-module-boundaries.md)
- [Flash Scheduler、Channel/Die/Plane Arbitration 与 Read Priority](wiki/concepts/flash-scheduler-arbitration.md)
- [DRAM-less SSD 与 Host Memory Buffer](wiki/concepts/dram-less-hmb-ssd.md)
- [ECC、LDPC 与可靠性管理](wiki/concepts/ecc-ldpc-reliability.md)
- [掉电保护与恢复](wiki/concepts/power-loss-recovery.md)
- [平台兼容与安全擦除](wiki/concepts/platform-compatibility-security.md)
- [遥测、日志与现场调试](wiki/concepts/telemetry-logging-field-debug.md)
- [性能、QoS 与写放大](wiki/concepts/performance-qos-write-amplification.md)
- [仿真、验证与测试平台](wiki/concepts/verification-and-emulation.md)
- [SSD 验证矩阵](wiki/concepts/ssd-verification-matrix.md)
- [故障注入目录](wiki/concepts/fault-injection-catalog.md)
- [验证证据与故障注入闭环](wiki/concepts/verification-evidence-and-fault-bridge.md)
- [量产需求与合规](wiki/concepts/production-requirements-and-compliance.md)
- [开源实现索引](wiki/concepts/opensource-implementation-index.md)
- [源码导读](wiki/concepts/source-code-reading-guide.md)

### 验证与维护

- [采集 Backlog](BACKLOG.md)
- [LLM/Agent 入口](llms.txt)
- [llmwiki 使用说明（含 provider 选型）](LLMWIKI.md)

### 验证资产

- [测试资产目录](tests/README.md)
- [机器可读需求映射](tests/requirements/requirements.yml)
- [机器可读 GC 策略矩阵](tests/requirements/gc-policy-matrix.yml)
- [机器可读 SLC Cache 策略矩阵](tests/requirements/slc-cache-policy-matrix.yml)
- [机器可读 Placement 策略矩阵](tests/requirements/placement-policy-matrix.yml)
- [机器可读 Firmware Update 策略矩阵](tests/requirements/firmware-update-policy-matrix.yml)
- [机器可读 HMB 策略矩阵](tests/requirements/hmb-policy-matrix.yml)
- [机器可读 Flash Scheduler 策略矩阵](tests/requirements/flash-scheduler-policy-matrix.yml)
- [机器可读 LDPC Pipeline 策略矩阵](tests/requirements/ldpc-pipeline-policy-matrix.yml)
- [机器可读 Emulator Hook 矩阵](tests/requirements/emulator-hook-matrix.yml)
- [机器可读验证证据 Schema](tests/requirements/verification-evidence-schema.yml)
- [NVMe 命令到规范映射](tests/requirements/nvme-command-spec-map.yml)
- [nvme-cli 输出字段映射](tests/requirements/nvme-cli-output-field-map.yml)
- [nvme-cli 只读命令证据样例 JSONL](tests/evidence/sample-nvme-cli-readonly-pass.jsonl)
- [LDPC 验证证据样例 JSONL](tests/evidence/sample-ldpc-pass.jsonl)
- [PLP 验证证据样例 JSONL](tests/evidence/sample-plp-pass.jsonl)
- [机器可读故障注入清单](tests/faults/fault-injection.yml)
- [掉电恢复状态表](tests/faults/power-loss-state-table.yml)
- [Firmware Update 状态表](tests/faults/firmware-update-state-table.yml)

### 来源追溯

- [开源实现 Commit Pins](sources/open-source-implementation-pins.yml)
- [开源实现 Smoke-test 矩阵](sources/implementation-smoke-test-matrix.yml)
- [规范版本 Pins](sources/standards-version-pins.yml)
- [公开标准版本审计](sources/standards-public-audit-2026-08-12.yml)
- [来源 Artifact 下载与哈希清单](sources/source-artifact-manifest.yml)
- [PDF Artifact 结构索引](sources/pdf-artifact-index.yml)
- [PDF 主题定位索引](sources/pdf-topic-locator.yml)

### 资料采集

- [资料采集模板](templates/source-intake-template.md)
- [概念页模板](templates/concept-page-template.md)
- [测试需求模板](templates/test-requirement-template.md)
- [验证报告模板](templates/verification-report-template.md)
- [NAND 参数采集矩阵](sources/vendor-intake/nand-parameter-extraction-matrix.yml)
- [Micron NAND Flash Guide 抽取记录](sources/vendor-intake/micron-nand-flash-guide-intake.md)
- [llmwiki Source Catalog](sources/source-catalog.md)
- [llmwiki Seed Notes](sources/seed.md)

## 当前覆盖范围

第一版覆盖：

- 固件：NVMe 命令处理、队列、FTL 映射、垃圾回收、磨损均衡、读干扰/保持期管理、后台任务调度、固件更新、日志与遥测。
- FTL 算法：提供 page mapping、hybrid/log-block mapping、DFTL/demand-based mapping 的独立设计页。
- GC 与寿命：提供 GC victim selection、watermark、dynamic/static wear leveling 的策略页和机器可读矩阵。
- SLC cache：提供 admission、destage、write cliff、bypass 和 PLP-aware metadata 的策略页、矩阵和 fio profile。
- Placement：提供 FDP、streams、placement hint 与内部 FTL/GC/SLC/fallback 的策略页和机器可读矩阵。
- 固件生命周期：提供 firmware download/commit/activation、metadata compatibility、rollback 和 telemetry 的策略页和状态表。
- DRAM-less/HMB：提供 HMB clean mapping cache、descriptor validation、miss storm、reset invalidation 和安全隔离策略。
- Flash scheduler：提供 channel/die/plane arbitration、read priority、program/erase suspend、ECC retry storm 和 timeout recovery 策略。
- ECC/LDPC：提供 hard decode、read retry ladder、soft-decision decode、ECC retry storm QoS guard、scrub/refresh 和 telemetry 策略矩阵。
- 元数据：Superblock、checkpoint、journal、L2P/P2L、block table、恢复重放和格式升级风险。
- 硬件：PCIe/NVMe 前端、DMA、PRP/SGL walker、queue manager、SRAM/DRAM、flash channel、NAND die/LUN/plane、NAND 时序参数、ONFI Toggle/async 接口、ECC/LDPC、AES、掉电保护、时钟/复位/电源域。
- 性能：稳态测试、QoS、写放大、GC budget、SLC cache write cliff、thermal throttling。
- 验证：FEMU、SimpleSSD、MQSim、SPDK、Linux NVMe、OpenSSD/Cosmos+、fio、xNVMe 等可读实现与实验平台，并提供协议、数据一致性、FTL、NAND 错误、掉电和 QoS 矩阵，以及验证证据闭环。
- 规范：NVM Express、ONFI、JEDEC SSD endurance/workload、PCI-SIG、OCP Data Center NVMe SSD、SNIA 性能测试资料。
- 资料追溯：提供论文/BibTeX 种子、专利检索索引、NAND vendor intake 和 controller vendor intake。
- Vendor 参数采集：提供 NAND geometry、timing、interface、ECC/read-retry 和可靠性字段的机器可读采集矩阵。
- 开源实现追溯：固定 FEMU、SimpleSSD、MQSim、SPDK、Cosmos+、Linux NVMe、nvme-cli 等参考实现的远端 HEAD commit，并定义后续本地构建/冒烟验证口径。
- 规范版本追溯：固定 NVMe、ONFI、JEDEC、PCI-SIG、OCP、SNIA 的目标版本、访问条件、公开审计记录和 artifact/hash 待补状态。
- 已验证 artifact：NVMe Base 2.4、NVM Command Set 1.3、ZNS 1.5 与 NVMe-MI 2.2 已下载官方 PDF，并在 artifact manifest 中记录本地文件和 sha256。
- PDF 结构索引：为已下载 PDF 记录页数、主题路由和后续抽取任务，并由 `tools/validate_source_artifacts.py` 自动校验 PDF 魔数、sha256 和页数。
- PDF 主题定位：提供 Identify Controller、Firmware Commit、Sanitize、FDP、Telemetry、ZNS 等主题的候选页码，并可用 `tools/locate_pdf_topics.py` 重新生成。
- 命令到规范追踪：把 `nvme-cli` 基础命令、测试 ID、需求 ID、PDF artifact 和主题候选页连接到 [NVMe Command Spec Map](tests/requirements/nvme-command-spec-map.yml)。
- Host command evidence：`verification-evidence-schema.yml` 支持 `host_command_event`，可把 `nvme-cli` 输出字段绑定到命令映射、测试、需求和规范 artifact。
- nvme-cli 字段映射：把 `vid`、`mn`、`fr`、`oacs`、`critical_warning`、`media_errors`、`num_err_log_entries` 等样例字段绑定到命令、测试、需求和规范 topic。
- Emulator hook 追踪：把 PLP、LDPC、flash scheduler、HMB、firmware update 的测试资产绑定到 FEMU/SimpleSSD/MQSim/Cosmos+ 等实现 hook。
- 验证证据：提供 run header、hook event、fault injection event、pass/fail decision 的机器可读 schema、报告模板，以及 PLP/LDPC 样例日志。
- 工程追踪：术语表、需求到验证矩阵、故障注入目录，用于把知识页转成测试计划或实现任务。
- 可维护性：提供本地检查脚本 `tools/check_ssd_wiki.py`、`tools/check_llmwiki_setup.py`、证据日志校验脚本 `tools/validate_evidence_log.py` 和来源 artifact 校验脚本 `tools/validate_source_artifacts.py`，覆盖 Markdown 链接、首页概念页覆盖、需求到测试计划映射、全部样例 evidence log、下载资料 hash manifest、PDF 结构索引、NAND 参数矩阵中的固定 artifact 引用，以及 `llmwiki` 输入/ingest 状态诊断。
- 测试资产：提供 fio profile、nvme-cli 命令清单、机器可读需求映射和故障注入清单。
- 掉电恢复：提供 `PLP-WIN-*` 状态表，覆盖写路径、journal、checkpoint 和 GC erase boundary 的掉电窗口。
- 缺口管理：提供 [覆盖缺口清单](COVERAGE_GAPS.md)，用于判断后续还需要补哪些资料、页面和实验资产。
- 发布入口：提供 `mkdocs.yml` 用于 MkDocs Material 预览，提供 `llms.txt` 作为 agent/LLM 快速入口。
- llmwiki 输入：已固定 `sources/source-catalog.md`、`sources/seed.md`、`sources/research-source-catalog.md` 和 `sources/research-nand-controller-patent-notes.md` 作为 `llmwiki` 输入源，并验证 `ingest` 可生成带 hash 后缀的摄取副本。
- 扩展流程：提供资料采集、概念页、测试需求和验证报告模板，配套 `VERSIONED_SOURCES.md` 与 `BACKLOG.md`。

## 本地检查

从仓库根目录运行：

```powershell
python tools/check_ssd_wiki.py
```

检查项：

- Markdown 内部链接是否存在。
- `wiki/index.md` 是否覆盖全部概念页。
- `TRACEABILITY_MATRIX.md` 中的 `REQ-*` 是否在 `TEST_PLAN.md` 中有测试覆盖。
- 关键维护文件和模板是否存在。
- `tests/requirements/requirements.yml` 中的需求、测试和 profile 路径是否可追踪。
- `python tools/check_llmwiki_setup.py` 可用于单独查看 `llmwiki` 的 canonical 输入、ingest 副本、当前状态摘要、provider 预检结果和 provider 矩阵快照；追加 `--json` 可输出机器可读结果。对应的 `tests/requirements/llmwiki-provider-matrix.yml` 现在还有专门的 validator。
- `python tools/check_llmwiki_setup.py --self-test` 可在不访问外部网络的情况下，回归 anthropic / anthropic-compatible / claude-agent / openai / copilot / minimax 的 provider 预检分支。
- `tests/requirements/llmwiki-provider-matrix.yml` 记录了 `llmwiki` 支持的 provider、默认模型、鉴权变量和本地预检状态，可作为脚本和文档的机器可读依据。

## 可信度约定

- `规范级`：可作为接口、时序、合规要求依据，例如 NVMe、ONFI、JEDEC、PCI-SIG、OCP 规范。
- `实现级`：可作为工程实现参考，例如 Linux、SPDK、FEMU、SimpleSSD、OpenSSD/Cosmos+。
- `研究级`：适合理解设计空间、算法权衡和模拟方法，需要回到实验条件判断是否能用于产品。
- `厂商资料`：适合理解工程趋势和产品约束，但通常省略关键实现细节。

## 后续扩展建议

1. 补齐具体 NAND vendor datasheet、controller vendor app note 和公开 patent 族。
2. 用 `llmwiki ingest` 摄取 `sources/source-catalog.md` 中的 URL，然后用中文输出编译成可查询 wiki。
3. 把每篇概念页拆成“设计目标、关键状态机、数据结构、错误场景、验证点”五段式页面。
4. 把 [需求到验证追踪矩阵](TRACEABILITY_MATRIX.md) 拆成独立测试需求，并为每条需求绑定工具、脚本和预期日志。
5. 按 [采集 Backlog](BACKLOG.md) 固定规范版本、源码 commit 和 vendor datasheet。
