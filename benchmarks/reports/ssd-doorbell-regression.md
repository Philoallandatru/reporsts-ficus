---
type: Report
title: NVMe 门铃槽位恢复与通知分支回归
description: 三道可复跑的 NVMe 门铃合成回归题，覆盖槽位恢复签发、无需额外通知和事后读数无法判定通知三种情况。
tags: [nvme, ssd, doorbell, eventidx, mmio, regression, pi]
status: active
verified:
  by: "agent:codex"
  at: "2026-11-26"
---

# NVMe 门铃槽位恢复与通知分支回归

门铃配置与槽位恢复按 NVMe Base 2.1 PDF 第 445–446 页验收。核对本代次原始 Admin SQE 的 PRP1/PRP2、匹配有效的成功 CQE、队列实际槽位是否落页，以及同次访问的地址、条目值和写入方。配置与实测均满足时，按已测范围签发。工单要求判断通知抑制、漏写或阈值跨越时，按第 702 页核对同次比较的旧值、新值、对应 EventIdx、队列回绕和 MMIO 轨迹。

| 回归题 | 现场签发判据 | 已记录结果 |
| --- | --- | --- |
| SSD-F15-08 | 重启后、本代次 QID=9 的最远 SQ Tail 和 CQ Head 均达标。归档本次配置提交、匹配完成和两类槽访问。 | 3 次均签发，未将通知轨迹列作门槛。 |
| SSD-F13-06 | 同一 CQ 的 4→7 未跨过当次比较值 9。该次可省略额外 MMIO。 | 首跑正确签发。 |
| SSD-F12-06 | 事后 EventIdx=12 不足以判断此前有无漏写。复核同一 SQ 的当次比较输入和真实 MMIO 轨迹。 | 首跑正确暂缓。 |

合成回归首跑的代理复核结果为原样可用 3/3、误导 0/3、交卷耗时中位数 10.85 秒。三题已用于开发回归。真实 SD 现场工单单独成批，等有可追溯的工程师签发记录后再计算其成绩。[原答与复核](../runs/ssd-doorbell-regression/reviewed.jsonl) · [另外两次槽位重放](../runs/ssd-doorbell-regression/repeat-slots.jsonl)

## 导入报告或导出盲题

从 reporsts 仓库取下列文件即可使用。

- 在 OpenKnowledge 打开 **设置 → 智能体 → 智能体评估 → 导入报告**。[工作台 JSON](../runs/ssd-doorbell-regression/doorbell-scope-regression.json)
- 逐题测试时仅给模型盲题 JSONL。题库带参考答案、判据及证据页，留到评分时使用。[盲题](../runs/ssd-doorbell-regression/questions.jsonl) · [题库与判据](../runs/ssd-doorbell-regression/case-bank.jsonl)

在 reporsts 根目录运行以下命令可重建工作台报告。只需要 Python 3.11 或更新版本。

```text
python -X utf8 tools/ssd-doorbell-regression/export_workbench.py benchmarks/runs/ssd-doorbell-regression/workbench-manifest.json --output .kb_index/ssd-doorbell-scope.json
```

## 复跑 Pi 和 MCP

准备 Python 3.11+、Node.js、已配置模型提供方的 Pi 及其 `pi-mcp-adapter`。PCIe Base 5.0 Version 1.0 PDF 使用库中已有的文件。另准备 NVMe Base 2.1（2024-08-05）PDF。替换第二行的 NVMe 文件路径，以及第三行的 Pi CLI 和适配器入口路径。以下各行可从 reporsts 根目录在 PowerShell 或 Bash 单独执行。每次复跑使用新的 `--output` 目录。语料已准备时可直接运行第三行。[NVMe 2.1 原件](https://nvmexpress.org/wp-content/uploads/NVM-Express-Base-Specification-Revision-2.1-2024.08.05-Ratified.pdf) · [原始 PDF 校验值](../runs/ssd-doorbell-regression/source-hashes.json)

```text
python -m pip install -r tools/ssd-doorbell-regression/requirements.txt
python -X utf8 tools/ssd-doorbell-regression/prepare_corpus.py --pcie "kb/pcie/PCI Express Base Specification.pdf" --nvme "path/to/NVMe-Base-2.1.pdf"
python -X utf8 tools/ssd-doorbell-regression/pi_trial.py --input benchmarks/runs/ssd-doorbell-regression/questions.jsonl --output .kb_index/ssd-doorbell-run-01 --pi-entry "path/to/pi/dist/bundle/cli.js" --adapter "path/to/pi-mcp-adapter/index.ts" --provider magpie --model codex/gpt-6.2-sol --prefetch --evidence-view decision --answer-style field-acceptance --skill tools/ssd-doorbell-regression/skills/scoped-field-acceptance/ssd-field-decisions/SKILL.md --calls 8 --timeout 120
```

对照上表判处置和验收证据。每题的 `result.json` 保存原答和耗时，`calls.jsonl` 保存取证记录。使用其他提供方或模型时替换 `--provider` 和 `--model`，另记录该配置。规范语料默认写入工具目录下的 `.local/`，复跑产物写入 `.kb_index/`。

在 reporsts 的独立语料与 Python 环境中复跑，三题均正常交卷。新版槽位题答卷没有要求通知轨迹，但把归档 Admin SQE 写成了补证后才能签发的条件。模型复跑可能改变具体签发措辞，需按上表复核。

这套运行器来自 OpenKnowledge fork 的固定提交 `751b4608`，随本库提供源码、版本化依赖和原许可证。[原始回归](https://github.com/Philoallandatru/op/tree/751b4608da5bc9c4830f7d96388ad54a4e32933b/examples/ssd-evaluation/studies/doorbell-scope) · [许可证](../../tools/ssd-doorbell-regression/LICENSE)
