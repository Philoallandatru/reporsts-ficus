# SSD 知识库测试计划模板

本测试计划把 [需求到验证追踪矩阵](TRACEABILITY_MATRIX.md) 转成可执行测试分组。它可以作为后续实现 SSD emulator、教学控制器或 FPGA 原型时的测试计划起点。

配套机器可读资产：

- [需求映射 YAML](tests/requirements/requirements.yml)
- [GC Policy Matrix](tests/requirements/gc-policy-matrix.yml)
- [SLC Cache Policy Matrix](tests/requirements/slc-cache-policy-matrix.yml)
- [Placement Policy Matrix](tests/requirements/placement-policy-matrix.yml)
- [Firmware Update Policy Matrix](tests/requirements/firmware-update-policy-matrix.yml)
- [HMB Policy Matrix](tests/requirements/hmb-policy-matrix.yml)
- [Flash Scheduler Policy Matrix](tests/requirements/flash-scheduler-policy-matrix.yml)
- [LDPC Pipeline Policy Matrix](tests/requirements/ldpc-pipeline-policy-matrix.yml)
- [Emulator Hook Matrix](tests/requirements/emulator-hook-matrix.yml)
- [Verification Evidence Schema](tests/requirements/verification-evidence-schema.yml)
- [NVMe Command Spec Map](tests/requirements/nvme-command-spec-map.yml)
- [nvme-cli Output Field Map](tests/requirements/nvme-cli-output-field-map.yml)
- [故障注入 YAML](tests/faults/fault-injection.yml)
- [fio profiles](tests/profiles/fio/)
- [nvme-cli 命令清单](tests/profiles/nvme-cli/basic-admin-commands.md)

## 测试环境记录

| 字段 | 示例 |
|---|---|
| DUT | FEMU fork / Cosmos+ board / FPGA prototype / software model |
| Firmware build | version, git hash, build time |
| Host OS | Linux kernel version, distro |
| Tools | nvme-cli, fio, xNVMe, SPDK, libnvme versions |
| Workload config | block size, QD, jobs, runtime, verify mode |
| NAND model | channel, die, plane, page size, timing, error model |

## T0: Smoke

| Test ID | Requirement | Steps | Pass criteria |
|---|---|---|---|
| T0-001 | REQ-NVME-001 | Enumerate PCIe device and run `nvme id-ctrl` | Device visible, fields consistent, no kernel error |
| T0-002 | REQ-NVME-002 | Create I/O queue and run small read/write | CQE status success, phase tag correct |
| T0-003 | REQ-DATA-001 | Run 1 GiB fio verify write/read | No verify mismatch |

## T1: Protocol and Reset

| Test ID | Requirement | Steps | Pass criteria |
|---|---|---|---|
| T1-001 | REQ-NVME-001 | Controller disable/enable loop | Re-enable succeeds, queues rebuilt |
| T1-002 | REQ-NVME-002 | Multi-queue random read/write | No lost CQE, no timeout |
| T1-003 | REQ-NVME-002 | Invalid opcode and invalid field tests | Correct status code, controller remains usable |
| T1-004 | REQ-NVME-001 | FLR or equivalent reset during outstanding I/O | Driver recovers or receives expected failures |

## T2: Data Consistency and FTL

| Test ID | Requirement | Steps | Pass criteria |
|---|---|---|---|
| T2-001 | REQ-DATA-001 | Random overwrite with verify | Latest data returned |
| T2-002 | REQ-FTL-001 | Fill device, then low-OP random writes | Free block watermark maintained |
| T2-003 | REQ-FTL-002 | Inject GC while overwriting same hotset | No old data resurrection |
| T2-004 | REQ-DATA-002 | Flush/FUA write then reset/power cut | Flushed data survives |

## T3: NAND Errors and Reliability

| Test ID | Requirement | Steps | Pass criteria |
|---|---|---|---|
| T3-001 | REQ-REL-001 | Inject correctable bit errors | Data correct, LDPC correction count and retry state logged |
| T3-002 | REQ-REL-002 | Inject uncorrectable read | Retry, soft decode and recovery attempted within [LDPC Pipeline Policy Matrix](tests/requirements/ldpc-pipeline-policy-matrix.yml) budget; correct NVMe error if failed |
| T3-003 | REQ-REL-001 | Trigger high read count / disturb | Scrub or refresh scheduled with reason and source block recorded |
| T3-004 | REQ-NAND-001 | Review geometry/timing config | Matches fixed NAND parameter source |

## T4: Power Loss Recovery

| Test ID | Requirement | Steps | Pass criteria |
|---|---|---|---|
| T4-001 | REQ-PLP-001 | Power cut before NAND program | Old data valid |
| T4-002 | REQ-PLP-001 | Power cut during program | Recovery does not accept partial page blindly |
| T4-003 | REQ-PLP-001 | Power cut during journal append | Incomplete entry ignored |
| T4-004 | REQ-PLP-001 | Power cut during checkpoint write | Previous checkpoint used |
| T4-005 | REQ-PLP-001 | Power cut during GC erase boundary | No valid data erased |

## T5: Performance and QoS

| Test ID | Requirement | Steps | Pass criteria |
|---|---|---|---|
| T5-001 | REQ-PERF-001 | Fresh vs steady-state fio profile | p99/p999 and WAF recorded |
| T5-002 | REQ-QOS-001 | Mixed read/write while GC/HMB miss pressure is active | Read p999 within budget or documented throttle |
| T5-003 | REQ-PERF-001 | Run [SLC cache write cliff profile](tests/profiles/fio/slc-cache-write-cliff.fio) or equivalent low free block run | Write cliff point, destage backlog and forward progress recorded |
| T5-004 | REQ-QOS-001 | ECC retry storm | LDPC retry/soft decode concurrency bounded; no global starvation |

## T6: Production Observability

| Test ID | Requirement | Steps | Pass criteria |
|---|---|---|---|
| T6-001 | REQ-PROD-001 | Read SMART/health/log pages | Key counters exposed |
| T6-002 | REQ-PROD-001 | Exercise firmware download/commit/activation/rollback states from [Firmware Update Policy Matrix](tests/requirements/firmware-update-policy-matrix.yml) | Version, slot table, migration status and update history explainable |
| T6-003 | REQ-PROD-001 | Trigger persistent error | Telemetry or event log contains failed PPA/LBA scope, recovery attempts and final status |

## T7: Coverage Audit

| Test ID | Requirement | Steps | Pass criteria |
|---|---|---|---|
| T7-001 | REQ-TEST-001 | Review protocol, data consistency, FTL, NAND error, power loss, performance and production test groups | Each required category has at least one planned or deferred test |
| T7-002 | REQ-TEST-001 | Run `python tools/check_ssd_wiki.py` | Link, index and requirement coverage checks pass |

## Coverage Rules

1. Every `REQ-*` row in `TRACEABILITY_MATRIX.md` should have at least one `T*` test.
2. Every fault in [故障注入目录](wiki/concepts/fault-injection-catalog.md) should map to a test or be explicitly deferred.
3. Test reports should record tool versions and workload configuration.
4. Performance claims must state fresh/steady-state, OP level, temperature state, QD, block size and runtime.
