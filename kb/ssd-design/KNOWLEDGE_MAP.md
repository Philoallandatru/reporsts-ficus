# SSD 设计知识地图

## 顶层分解

SSD 设备可以按四个面向来理解：

1. 主机接口面：PCIe、NVMe controller properties、Admin/I/O queue、interrupt、DMA、reset、power management。
2. 闪存介质面：NAND page/block/plane/die/LUN/channel、ONFI/Toggle 接口、program/read/erase、坏块、读干扰、保持期、温度。
3. 固件控制面：FTL、映射表、日志/检查点、垃圾回收、磨损均衡、后台扫描、QoS、错误恢复、固件更新、遥测。
4. 数据保护面：ECC/LDPC、RAID-like parity、end-to-end protection information、元数据校验、掉电保护、电容放电流程。

## 设计问题索引

| 问题 | 先读 | 关键来源 |
|---|---|---|
| SSD 控制器里面有哪些模块？ | [SSD 系统架构](wiki/concepts/ssd-system-architecture.md) | NVM Express, ONFI, Cosmos+ |
| 主机是怎样看见并初始化控制器的？ | [NVMe 寄存器、队列与状态机](wiki/concepts/nvme-register-queue-state.md) | NVM Express, Linux NVMe, Cosmos+ |
| 如果要从零做教学控制器，先实现什么？ | [最小 SSD 控制器实现路线](wiki/concepts/minimal-ssd-controller-roadmap.md) | NVMe, Linux, FEMU, Cosmos+ |
| NVMe 命令在 SSD 内部如何流转？ | [SSD 内部的 NVMe 命令生命周期](wiki/concepts/nvme-command-lifecycle-in-ssd.md) | NVMe, Linux, SPDK, FEMU |
| FTL 为什么是 SSD 固件核心？ | [FTL 与固件职责](wiki/concepts/firmware-ftl.md) | SimpleSSD, FEMU, MQSim, OpenSSD |
| FTL 具体要设计哪些数据结构和状态机？ | [FTL 设计深水区](wiki/concepts/ftl-design-deep-dive.md) | DFTL, FAST, SPDK FTL |
| FTL 元数据和掉电恢复边界怎么定？ | [FTL 元数据格式与恢复约定](wiki/concepts/ftl-metadata-format-and-recovery-conventions.md), [掉电保护与恢复](wiki/concepts/power-loss-recovery.md) | SPDK FTL, Cosmos+, 本地状态表 |
| Page mapping 怎么实现？ | [FTL Page Mapping](wiki/concepts/ftl-page-mapping.md) | DFTL, SPDK FTL, SimpleSSD |
| Hybrid/log-block mapping 怎么合并？ | [FTL Hybrid / Log-block Mapping](wiki/concepts/ftl-hybrid-log-block-mapping.md) | FAST, FlashSim |
| DRAM 受限时如何做 demand-based mapping？ | [DFTL / Demand-based Mapping](wiki/concepts/ftl-dftl-demand-based-mapping.md) | DFTL, SPDK FTL |
| GC victim 和 wear leveling 如何选策略？ | [GC Victim Selection 与 Wear Leveling 策略](wiki/concepts/gc-wear-leveling-policy.md), [GC Policy Matrix](tests/requirements/gc-policy-matrix.yml) | MQSim, SimpleSSD, SPDK FTL |
| SLC cache 写满后为什么会 write cliff？ | [SLC Cache、Write Cliff 与 Destage 策略](wiki/concepts/slc-cache-write-cliff-destage.md), [SLC Cache Policy Matrix](tests/requirements/slc-cache-policy-matrix.yml) | fio, FAST papers, patents |
| FDP/streams/placement hint 如何影响内部 FTL？ | [FDP、Streams、Placement Hint 与内部 FTL](wiki/concepts/fdp-streams-placement-hints.md), [Placement Policy Matrix](tests/requirements/placement-policy-matrix.yml) | NVM Express, FDP, ZNS |
| 固件升级和回滚如何避免变砖？ | [Firmware Update、Metadata Compatibility 与 Rollback](wiki/concepts/firmware-update-rollback.md), [Firmware Update Policy Matrix](tests/requirements/firmware-update-policy-matrix.yml), [Firmware Update State Table](tests/faults/firmware-update-state-table.yml) | NVMe, OCP, 本地状态表 |
| Reset、boot 和 power state 怎么分边界？ | [Reset、Boot 与 Power State 边界](wiki/concepts/reset-boot-power-state.md), [NVMe 寄存器、队列与状态机](wiki/concepts/nvme-register-queue-state.md) | NVMe, Linux NVMe, PCI-SIG |
| FTL 元数据如何落盘和恢复？ | [FTL 元数据格式与恢复约定](wiki/concepts/ftl-metadata-format-and-recovery-conventions.md) | SPDK FTL, DFTL, Cosmos+ |
| NAND channel 和 die 怎么影响性能？ | [控制器硬件与 NAND 接口](wiki/concepts/hardware-controller-and-nand.md) | ONFI, Cosmos+, SimpleSSD |
| 拿到 NAND datasheet 后应抽取哪些参数？ | [NAND 介质参数手册](wiki/concepts/nand-media-parameter-guide.md), [NAND Parameter Extraction Matrix](sources/vendor-intake/nand-parameter-extraction-matrix.yml), [Micron NAND Flash Guide 抽取记录](sources/vendor-intake/micron-nand-flash-guide-intake.md) | ONFI, JEDEC, Micron, Kioxia |
| NAND 数据怎么抽取并落到模型？ | [NAND 数据采集与建模](wiki/concepts/nand-data-acquisition-and-modeling.md), [NAND Vendor Intake](sources/vendor-intake/nand-vendor-public-materials.md) | ONFI, JEDEC, vendor datasheet |
| 控制器厂商数据怎么抽取并落到模型？ | [控制器厂商数据采集与建模](wiki/concepts/controller-vendor-data-acquisition.md), [Controller Vendor Intake](sources/vendor-intake/controller-vendor-public-materials.md), [Controller Vendor Extraction Matrix](sources/vendor-intake/controller-vendor-extraction-matrix.yml), [Controller Vendor Sample Registry](sources/vendor-intake/controller-vendor-sample-registry.yml) | vendor brief, guide, white paper |
| 控制器硬件模块边界怎么划？ | [控制器硬件模块边界](wiki/concepts/controller-hardware-module-boundaries.md) | NVMe, AMD PG329, Cosmos+ |
| 控制器 RTL / IP 设计参考看什么？ | [控制器 RTL / IP 参考](wiki/concepts/controller-rtl-ip-reference.md) | AMD PG329, Cosmos+, FPGA NVMe target |
| Flash scheduler 如何做 channel/die/plane arbitration？ | [Flash Scheduler、Channel/Die/Plane Arbitration 与 Read Priority](wiki/concepts/flash-scheduler-arbitration.md), [Flash Scheduler Policy Matrix](tests/requirements/flash-scheduler-policy-matrix.yml) | ONFI, Cosmos+, 本地策略矩阵 |
| DRAM-less/HMB SSD 怎么设计才安全？ | [DRAM-less SSD 与 Host Memory Buffer](wiki/concepts/dram-less-hmb-ssd.md), [HMB Policy Matrix](tests/requirements/hmb-policy-matrix.yml) | NVMe, DFTL, 本地策略矩阵 |
| ECC/LDPC 和可靠性如何协同？ | [ECC、LDPC 与可靠性管理](wiki/concepts/ecc-ldpc-reliability.md), [LDPC Pipeline Policy Matrix](tests/requirements/ldpc-pipeline-policy-matrix.yml) | LDPC-in-SSD, ONFI, JEDEC |
| LDPC hard/soft decode、read retry 和 QoS budget 怎么设计？ | [ECC、LDPC 与可靠性管理](wiki/concepts/ecc-ldpc-reliability.md), [Flash Scheduler、Channel/Die/Plane Arbitration 与 Read Priority](wiki/concepts/flash-scheduler-arbitration.md), [LDPC Pipeline Policy Matrix](tests/requirements/ldpc-pipeline-policy-matrix.yml) | LDPC-in-SSD, WD ECC/DSP, 本地策略矩阵 |
| 掉电后如何保证数据和映射一致？ | [掉电保护与恢复](wiki/concepts/power-loss-recovery.md) | NVMe, SPDK FTL, OCP |
| 掉电注入窗口如何追踪？ | [掉电恢复状态表](tests/faults/power-loss-state-table.yml), [故障注入清单](tests/faults/fault-injection.yml), [Emulator Hook Matrix](tests/requirements/emulator-hook-matrix.yml) | 本地 PLP 状态表 |
| 如何理解 QoS、稳态性能和写放大？ | [性能、QoS 与写放大](wiki/concepts/performance-qos-write-amplification.md) | MQSim, SimpleSSD, fio, JESD219 |
| 如何做软件仿真和固件验证？ | [仿真、验证与测试平台](wiki/concepts/verification-and-emulation.md), [Emulator Hook Matrix](tests/requirements/emulator-hook-matrix.yml) | FEMU, SimpleSSD, MQSim, SPDK, Linux |
| SSD 验证应该覆盖哪些场景？ | [SSD 验证矩阵](wiki/concepts/ssd-verification-matrix.md) | nvme-cli, fio, SPDK, FEMU |
| 测试通过需要哪些证据？ | [验证证据与故障注入闭环](wiki/concepts/verification-evidence-and-fault-bridge.md), [Verification Evidence Schema](tests/requirements/verification-evidence-schema.yml), [验证报告模板](templates/verification-report-template.md), [Emulator Hook Matrix](tests/requirements/emulator-hook-matrix.yml) | 本地证据 schema |
| 应该注入哪些故障？ | [故障注入目录](wiki/concepts/fault-injection-catalog.md), [验证证据与故障注入闭环](wiki/concepts/verification-evidence-and-fault-bridge.md) | FEMU, fio, xNVMe |
| 从原型到量产还缺哪些要求？ | [量产需求与合规](wiki/concepts/production-requirements-and-compliance.md) | NVMe, PCIe, OCP, JEDEC, SNIA |
| 平台兼容、sanitize 和安全擦除怎么一起看？ | [平台兼容与安全擦除](wiki/concepts/platform-compatibility-security.md), [量产需求与合规](wiki/concepts/production-requirements-and-compliance.md) | NVMe, Linux NVMe, Windows, TCG/Opal |
| 遥测、日志和现场调试看什么？ | [遥测、日志与现场调试](wiki/concepts/telemetry-logging-field-debug.md), [量产需求与合规](wiki/concepts/production-requirements-and-compliance.md) | NVMe, OCP, linux/nvme-cli |
| 哪些开源项目值得读代码？ | [开源实现索引](wiki/concepts/opensource-implementation-index.md), [Open-source Implementation Pins](sources/open-source-implementation-pins.yml) | GitHub repositories |
| 每个开源项目该从哪里读起？ | [源码导读](wiki/concepts/source-code-reading-guide.md), [Open-source Implementation Pins](sources/open-source-implementation-pins.yml) | Cosmos+, FEMU, SimpleSSD, MQSim, SPDK, Linux |
| 开源实现固定到哪个 commit？ | [Open-source Implementation Pins](sources/open-source-implementation-pins.yml), [开源实现 Smoke-test 矩阵](sources/implementation-smoke-test-matrix.yml), [版本化来源清单](VERSIONED_SOURCES.md) | git ls-remote, GitHub repositories |
| 规范资料从哪里拿？ | [资料来源目录](SOURCES.md), [规范版本 Pins](sources/standards-version-pins.yml), [公开标准版本审计](sources/standards-public-audit-2026-08-12.yml), [来源 Artifact 下载与哈希清单](sources/source-artifact-manifest.yml), [PDF Artifact 结构索引](sources/pdf-artifact-index.yml), [PDF 主题定位索引](sources/pdf-topic-locator.yml) | NVM Express, ONFI, JEDEC, PCI-SIG, OCP |
| nvme-cli 命令对应哪些规范页？ | [nvme-cli 命令清单](tests/profiles/nvme-cli/basic-admin-commands.md), [NVMe Command Spec Map](tests/requirements/nvme-command-spec-map.yml), [nvme-cli Output Field Map](tests/requirements/nvme-cli-output-field-map.yml), [PDF 主题定位索引](sources/pdf-topic-locator.yml) | NVM Express, nvme-cli |
| 论文采集怎么开始？ | [SSD 设计论文与 BibTeX 种子](BIBLIOGRAPHY.md), [论文采集矩阵](sources/paper-intake-matrix.yml) | USENIX, ACM, Springer, arXiv |
| 专利资料从哪里开始？ | [SSD 专利检索索引](PATENT_INDEX.md), [专利采集矩阵](sources/patent-intake-matrix.yml), [Patent Intake Template](sources/patents/patent-intake-template.md) | Google Patents, USPTO |
| NAND/控制器厂商资料如何采集？ | [NAND Vendor Intake](sources/vendor-intake/nand-vendor-public-materials.md), [NAND Parameter Extraction Matrix](sources/vendor-intake/nand-parameter-extraction-matrix.yml), [Micron NAND Flash Guide 抽取记录](sources/vendor-intake/micron-nand-flash-guide-intake.md), [Controller Vendor Intake](sources/vendor-intake/controller-vendor-public-materials.md) | Vendor public pages |
| 术语和需求如何追踪？ | [SSD 设计术语表](GLOSSARY.md), [需求到验证追踪矩阵](TRACEABILITY_MATRIX.md) | 本地工程索引 |
| 架构和流程图在哪里？ | [SSD 控制器架构总览](maps/architecture-overview.md), [读写路径图](maps/write-read-path.md), [掉电恢复流程图](maps/recovery-flow.md) | 本地 Mermaid 图 |
| 测试计划从哪里开始？ | [SSD 知识库测试计划模板](TEST_PLAN.md) | 本地工程索引 |
| 还有哪些内容需要补充？ | [覆盖缺口清单](COVERAGE_GAPS.md) | 本地维护索引 |
| 后续采集优先级在哪里？ | [采集 Backlog](BACKLOG.md), [版本化来源清单](VERSIONED_SOURCES.md), [规范版本 Pins](sources/standards-version-pins.yml) | 本地维护索引 |
| 新资料和新页面用什么格式？ | [资料采集模板](templates/source-intake-template.md), [概念页模板](templates/concept-page-template.md), [测试需求模板](templates/test-requirement-template.md), [验证报告模板](templates/verification-report-template.md) | 本地模板 |
| LLM/Agent 应该从哪里读？ | [LLM/Agent 入口](llms.txt) | 本地入口 |
| 可执行测试资产在哪里？ | [测试资产目录](tests/README.md), [机器可读需求映射](tests/requirements/requirements.yml), [GC Policy Matrix](tests/requirements/gc-policy-matrix.yml), [SLC Cache Policy Matrix](tests/requirements/slc-cache-policy-matrix.yml), [Placement Policy Matrix](tests/requirements/placement-policy-matrix.yml), [Firmware Update Policy Matrix](tests/requirements/firmware-update-policy-matrix.yml), [HMB Policy Matrix](tests/requirements/hmb-policy-matrix.yml), [Flash Scheduler Policy Matrix](tests/requirements/flash-scheduler-policy-matrix.yml), [LDPC Pipeline Policy Matrix](tests/requirements/ldpc-pipeline-policy-matrix.yml), [Emulator Hook Matrix](tests/requirements/emulator-hook-matrix.yml), [Verification Evidence Schema](tests/requirements/verification-evidence-schema.yml), [机器可读故障注入清单](tests/faults/fault-injection.yml), [掉电恢复状态表](tests/faults/power-loss-state-table.yml), [Firmware Update State Table](tests/faults/firmware-update-state-table.yml) | 本地测试资产 |

## 学习路径

### 固件工程师路径

1. NVMe queue 与命令生命周期：结合本仓库 `nvme-wiki` 阅读。
2. FTL：logical block address 到 physical page/block 的映射。
3. FTL 深水区：L2P/P2L、block table、journal、checkpoint、GC 前向进展。
4. 写路径：host write、buffer、分配物理页、写 NAND、更新映射、返回 CQE。
5. 读路径：查映射、调度 channel/die、ECC 解码、错误重试、返回数据。
6. 后台任务：GC、wear leveling、refresh、scrub、日志 checkpoint。
7. 异常路径：掉电、reset、uncorrectable read、坏块替换、固件下载/激活。

### 硬件工程师路径

1. PCIe endpoint 与 NVMe controller register/interface。
2. DMA、doorbell、MSI-X、中断聚合和队列调度。
3. Flash controller：channel、way、CE、R/B、command/address/data phase。
4. 模块边界：PRP/SGL walker、queue manager、DMA、flash scheduler、metadata engine。
5. ECC/LDPC pipeline、scrambler、AES、CRC/metadata。
6. DRAM/SRAM 带宽分配：映射表、数据缓存、命令上下文、日志。
7. 电源与信号：M.2/U.2/EDSFF、3.3V/12V、PERST#、CLKREQ#、PLP capacitor。

### 验证路径

1. SPDK/nvme-cli 生成主机侧命令与 trace。
2. FEMU 或 SimpleSSD 观察控制器行为。
3. MQSim 做体系结构参数扫点。
4. Cosmos+/OpenSSD 对照固件流程和硬件寄存器。
5. 用 Linux NVMe target 或 PCI endpoint function 搭建互操作验证。
6. 按 [SSD 验证矩阵](wiki/concepts/ssd-verification-matrix.md) 补协议、数据一致性、FTL、NAND 错误、掉电和 QoS 测试。

### 最小教学控制器路线

详见 [最小 SSD 控制器实现路线](wiki/concepts/minimal-ssd-controller-roadmap.md)。

1. 可枚举 NVMe 设备：Identify、Admin Queue、controller enable。
2. RAM-backed namespace：queue、read/write、PRP、CQE。
3. NVMe 命令生命周期：decode、PRP/SGL、dispatch、DMA、CQE。
4. 简单 page mapping FTL：L2P、free block、顺序写入。
5. GC 和 P2L：支持 overwrite 和低空闲块回收。
6. NAND model：program/read/erase latency、bad block、ECC error count。
7. Checkpoint/journal：支持 reset 和掉电恢复。
8. ECC/LDPC/retry 模型：支持 correctable/uncorrectable 路径。
9. QoS 和后台任务：GC、wear leveling、refresh、thermal throttling。

## 与现有知识库关系

- `nvme-wiki`：主机看到的 NVMe 协议模型。
- `pcie-wiki`：PCIe 传输、配置空间、电气/链路训练。
- `ssd-design-wiki`：SSD 控制器内部如何把 NVMe 请求变成 NAND 操作。

## 维护检查

从仓库根目录运行：

```powershell
python tools/check_ssd_wiki.py
```

该脚本检查内部链接、首页概念页覆盖，以及需求到测试计划的覆盖关系。
