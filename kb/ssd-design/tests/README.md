# SSD 测试资产

本目录把 [TEST_PLAN.md](../TEST_PLAN.md) 拆成更接近可执行的测试资产。

## 目录结构

- `profiles/fio/`：fio workload 模板。
- `profiles/nvme-cli/`：nvme-cli 命令清单。
- `evidence/`：验证证据 JSONL 样例，当前包含 PLP、LDPC/read-retry 和 nvme-cli 只读 host command 路径。
- `evidence/raw/`：host-side 工具原始 stdout/stderr 样例；JSONL 中的 raw 路径必须指向这里或 `tests/evidence/` 内部文件。
- `requirements/requirements.yml`：机器可读需求和测试映射。
- `requirements/gc-policy-matrix.yml`：GC victim selection、watermark 和 wear leveling 策略矩阵。
- `requirements/slc-cache-policy-matrix.yml`：SLC cache admission、destage、write cliff 和恢复策略矩阵。
- `requirements/placement-policy-matrix.yml`：FDP、streams、placement hint、fallback 和恢复策略矩阵。
- `requirements/firmware-update-policy-matrix.yml`：firmware download/commit/activation、metadata compatibility 和 rollback 策略矩阵。
- `requirements/reset-boot-power-state-matrix.yml`：controller reset、FLR、PERST#、power cycle、shutdown、firmware activation 与平台启动/电源态边界矩阵。
- `requirements/platform-compatibility-security-matrix.yml`：BIOS/UEFI、Windows、Linux、热插拔、sanitize、crypto erase、TCG/Opal 与 firmware signing 语义矩阵。
- `requirements/telemetry-field-debug-matrix.yml`：runtime counter、persistent event log、crash dump 和 field debug package 语义矩阵。
- `requirements/open-source-reading-smoke-map.yml`：开源实现阅读重点到最小 smoke goal 的映射矩阵。
- `requirements/hmb-policy-matrix.yml`：DRAM-less/HMB mapping cache、DMA fault fallback、miss storm 和安全隔离策略矩阵。
- `requirements/flash-scheduler-policy-matrix.yml`：flash scheduler arbitration、read priority、suspend/resume 和 timeout recovery 策略矩阵。
- `requirements/ldpc-pipeline-policy-matrix.yml`：LDPC hard/soft decode、read retry、scrub/refresh 和 uncorrectable escalation 策略矩阵。
- `requirements/emulator-hook-matrix.yml`：把 PLP、LDPC、flash scheduler、HMB、firmware update 测试绑定到 emulator/source hook 的矩阵。
- `requirements/verification-evidence-schema.yml`：统一 run header、hook event、fault injection event 和 pass/fail decision 的证据字段。
- `requirements/nvme-command-spec-map.yml`：把 nvme-cli 命令、测试 ID、需求 ID、PDF artifact 和主题候选页连接起来。
- `requirements/nvme-cli-output-field-map.yml`：登记 host command evidence 中允许出现的 nvme-cli 输出字段及其测试/规范含义。
- `concepts/verification-evidence-and-fault-bridge.md`：把验证矩阵、证据 schema、故障注入目录和 host command evidence 串成闭环。
- `faults/fault-injection.yml`：机器可读故障注入目录。
- `faults/power-loss-state-table.yml`：机器可读掉电窗口和恢复规则。
- `faults/firmware-update-state-table.yml`：机器可读固件升级掉电窗口和回滚规则。

## 证据日志校验

单个样例日志：

```powershell
python ../tools/validate_evidence_log.py tests/evidence/sample-plp-pass.jsonl
python ../tools/validate_evidence_log.py tests/evidence/sample-ldpc-pass.jsonl
python ../tools/validate_evidence_log.py tests/evidence/sample-nvme-cli-readonly-pass.jsonl
```

从仓库根目录运行时：

```powershell
python tools/validate_evidence_log.py ssd-design-wiki/tests/evidence/sample-plp-pass.jsonl
python tools/validate_evidence_log.py ssd-design-wiki/tests/evidence/sample-ldpc-pass.jsonl
python tools/validate_evidence_log.py ssd-design-wiki/tests/evidence/sample-nvme-cli-readonly-pass.jsonl
```

`tools/check_ssd_wiki.py` 会自动校验 `tests/evidence/*.jsonl` 下的全部样例，包括 emulator hook 与 host command evidence；host command evidence 还会检查 raw stdout/stderr 文件是否存在、路径是否安全，并从 raw stdout 中解析 `field_name : value` 行，确认 JSONL 的 `observed_fields` 逐项来自原始输出。

## 安全约定

所有 profile 都使用占位设备路径，例如 `/dev/nvmeXnY`。运行前必须替换为目标 emulator、测试盘或 loop/test backend。不要直接对生产盘运行。

## 推荐流程

1. 固定 DUT、固件版本、host OS、工具版本。
2. 从 smoke profile 开始。
3. 再运行数据一致性、steady-state、SLC cache write cliff、HMB mapping miss storm、mixed QoS profile。
4. 对 fault-injection 条目逐项启用 emulator 或测试固件 hook。
5. 先读 `concepts/verification-evidence-and-fault-bridge.md`，再按 `requirements/emulator-hook-matrix.yml` 选择 hook 点，并按 `requirements/verification-evidence-schema.yml` 记录日志字段和 pass/fail 证据。
6. 对 LDPC/read-retry 类测试记录 corrected bits、retry count、soft decode count、ECC engine busy time 和 uncorrectable telemetry。
7. 把结果回填到测试报告，并更新 `TRACEABILITY_MATRIX.md`。

## llmwiki 预检自检

```powershell
python ../tools/check_llmwiki_setup.py --self-test
```

这个命令只验证本地 provider 预检分支，不会发网络请求。它适合在调整 `LLMWIKI_PROVIDER`、`ANTHROPIC_BASE_URL`、`OPENAI_API_KEY` 或 `MINIMAX_API_KEY` 相关逻辑后做快速回归。

## Anthropic quickstart

如果你要直接走原生 Anthropic 协议，最短路径就是把 provider 和 key 放好：

```powershell
$env:LLMWIKI_PROVIDER="anthropic"
$env:ANTHROPIC_API_KEY="sk-..."
$env:LLMWIKI_OUTPUT_LANG="zh-CN"
python ../tools/check_llmwiki_setup.py
```

如果账号侧发的是 token，就把 `ANTHROPIC_API_KEY` 换成 `ANTHROPIC_AUTH_TOKEN`。这两种写法都走同一条 Anthropic-native 路径。

如果你拿到的是 Anthropic-compatible 网关，再加上：

```powershell
$env:ANTHROPIC_BASE_URL="https://api.minimaxi.com/anthropic"
$env:LLMWIKI_MODEL="MiniMax-M2.7"
python ../tools/check_llmwiki_setup.py
```

这条路径会被识别成 `anthropic-compatible`，适合需要走 MiniMax 兼容网关的场景。

## MiniMax quickstart

如果你拿到的是 MiniMax 原生 key，最短路径是：

```powershell
$env:LLMWIKI_PROVIDER="minimax"
$env:MINIMAX_API_KEY="sk-..."
$env:LLMWIKI_OUTPUT_LANG="zh-CN"
python ../tools/check_llmwiki_setup.py
```

这条路径会直接走 `https://api.minimax.io/v1`，适合在 Anthropic-compatible 网关不通，或者账号本身就是原生 MiniMax 授权时使用。

## Reset / boot quickstart

如果你想检查 reset、boot 和 power-state 的边界定义是否还和文档一致，可以直接看机器可读矩阵：

- `tests/requirements/reset-boot-power-state-matrix.yml`
- `wiki/concepts/reset-boot-power-state.md`
- `wiki/concepts/platform-compatibility-security.md`

这套资产主要用来对照 controller reset、FLR、PERST#、power cycle、shutdown 和 firmware activation 的可见行为。

## Platform compatibility quickstart

如果你要检查平台兼容和安全擦除的边界是否一致，可以直接看：

- `tests/requirements/platform-compatibility-security-matrix.yml`
- `wiki/concepts/platform-compatibility-security.md`
- `wiki/concepts/production-requirements-and-compliance.md`

这套资产主要对照 BIOS/UEFI、Windows、Linux、热插拔、sanitize、crypto erase、secure boot、signed firmware 和 TCG/Opal 的可观测行为。

## Telemetry quickstart

如果你想看遥测、日志和现场调试的边界，直接看：

- `tests/requirements/telemetry-field-debug-matrix.yml`
- `wiki/concepts/telemetry-logging-field-debug.md`
- `wiki/concepts/production-requirements-and-compliance.md`

这套资产主要对照 runtime counter、persistent event log、crash dump 和 field debug package 的最小可观测字段。

## Open-source reading quickstart

如果你想直接从开源实现进入阅读和复现，可以看：

- `tests/requirements/open-source-reading-smoke-map.yml`
- `wiki/concepts/opensource-implementation-index.md`
- `wiki/concepts/source-code-reading-guide.md`

这套资产主要把 pinned commit、阅读重点和最小 smoke goal 绑在一起，避免只停留在“知道仓库名”。
