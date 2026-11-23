# SSD 需求到验证追踪矩阵

本矩阵把 SSD 控制器/固件设计需求连接到设计页面和验证证据。它不是完整产品需求，只是知识库当前覆盖范围的工程化索引。

| ID | 需求 | 设计依据 | 验证证据 | 主要来源 |
|---|---|---|---|---|
| REQ-NVME-001 | 设备应能被 host 枚举并完成 NVMe controller enable | [最小 SSD 控制器实现路线](wiki/concepts/minimal-ssd-controller-roadmap.md), [控制器硬件模块边界](wiki/concepts/controller-hardware-module-boundaries.md) | PCIe enumeration、`nvme id-ctrl`、reset/re-enable 测试 | NVMe, PCI-SIG, Linux NVMe |
| REQ-NVME-002 | I/O queue 应正确处理 SQE fetch、CQE writeback、phase tag 和 doorbell | [NVMe 命令生命周期](wiki/concepts/nvme-command-lifecycle-in-ssd.md) | 多队列、多 QD、lost interrupt、polling 测试 | NVMe, SPDK, Linux |
| REQ-DATA-001 | 已完成写入后读应返回最新数据，不得复活旧版本 | [FTL 与固件职责](wiki/concepts/firmware-ftl.md), [FTL 设计深水区](wiki/concepts/ftl-design-deep-dive.md) | fio verify、随机覆盖写、GC 并发读写 | DFTL, FAST, SimpleSSD |
| REQ-DATA-002 | Flush/FUA 或设备声明的持久性语义应与 VWC/PLP 能力一致 | [掉电保护与恢复](wiki/concepts/power-loss-recovery.md) | Flush 后掉电注入、VWC feature 测试 | NVMe, OCP |
| REQ-FTL-001 | FTL 应维护 L2P/P2L、block table、free block pool，并保证 GC 前向进展 | [FTL 设计深水区](wiki/concepts/ftl-design-deep-dive.md), [FTL 元数据格式与恢复约定](wiki/concepts/ftl-metadata-format-and-recovery-conventions.md) | 低 OP 随机写、free block watermark、WAF 统计 | DFTL, SPDK FTL |
| REQ-FTL-002 | GC 搬迁与 host overwrite 同一 LBA 时应以版本号或等价机制避免旧数据复活 | [FTL 设计深水区](wiki/concepts/ftl-design-deep-dive.md) | GC 中并发 overwrite fault injection | FTL papers, Cosmos+ |
| REQ-NAND-001 | NAND 参数应从 datasheet/ONFI parameter page 提取并固定 | [NAND 介质参数手册](wiki/concepts/nand-media-parameter-guide.md) | Geometry/timing 配置审查、model 参数快照 | ONFI, JEDEC, vendor datasheet |
| REQ-REL-001 | ECC/LDPC 应处理 correctable read，并暴露 correction count 供 refresh/scrub 使用 | [ECC、LDPC 与可靠性管理](wiki/concepts/ecc-ldpc-reliability.md) | bit error injection、correction count histogram | LDPC-in-SSD, WD ECC/DSP |
| REQ-REL-002 | Uncorrectable read 应触发 retry/parity/recovery，失败时返回正确 NVMe status 并记录日志 | [ECC、LDPC 与可靠性管理](wiki/concepts/ecc-ldpc-reliability.md), [故障注入目录](wiki/concepts/fault-injection-catalog.md) | uncorrectable read injection、log/telemetry 检查 | NVMe, ONFI |
| REQ-PLP-001 | 掉电恢复应从 superblock/checkpoint/journal 重建一致 L2P 和 block state | [掉电保护与恢复](wiki/concepts/power-loss-recovery.md), [FTL 元数据格式与恢复约定](wiki/concepts/ftl-metadata-format-and-recovery-conventions.md) | 每个写路径阶段 power cut、journal 半写入 | NVMe, SPDK FTL |
| REQ-PERF-001 | 性能测试应区分 fresh 与 steady state，并记录 p99/p999 和 WAF | [性能、QoS 与写放大](wiki/concepts/performance-qos-write-amplification.md) | fio steady-state profile、latency histogram、WAF counters | MQSim, JESD219, fio |
| REQ-QOS-001 | 后台 GC/scrub/refresh 不应无限阻塞前台读 | [性能、QoS 与写放大](wiki/concepts/performance-qos-write-amplification.md), [SSD 验证矩阵](wiki/concepts/ssd-verification-matrix.md) | 混合读写、GC active、read p999 | MQSim, SimpleSSD |
| REQ-PROD-001 | 量产固件应具备版本、日志、telemetry、升级历史和错误计数等可观测性 | [量产需求与合规](wiki/concepts/production-requirements-and-compliance.md) | SMART/log/telemetry 审查、field dump 测试 | NVMe, OCP |
| REQ-TEST-001 | 验证应覆盖协议、数据一致性、FTL、NAND 错误、掉电、性能、量产可维护性 | [SSD 验证矩阵](wiki/concepts/ssd-verification-matrix.md), [故障注入目录](wiki/concepts/fault-injection-catalog.md) | 测试计划和覆盖报告 | nvme-cli, fio, xNVMe, SPDK |

## 使用方式

1. 新增页面时，如果它承载设计要求，应补一行 `REQ-*`。
2. 新增测试时，必须能追到至少一个需求 ID。
3. 对外发布文档或实验报告时，记录来源版本和测试工具版本。
4. `llmwiki` 编译后，可把本矩阵作为 query/context 的入口，追溯设计和证据。
