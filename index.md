---
okf_version: "0.2"
---

# reporsts-ficus 知识与评测总库

按**持久知识（`kb/`）**与**时效实测（`benchmarks/`）**严格分离的统一治理仓库。

## 1. 领域知识库（`kb/`）

- [kb/index.md](kb/index.md) — 领域知识库总索引（NVMe / PCIe / PCI Firmware / SSD / Storage / Specs / LLM 推理 / Agents / Engineering / Wikipedia）

## 2. 实验评测与运行产物（`benchmarks/`）

- [benchmarks/index.md](benchmarks/index.md) — LLM 推理评测报告（Strata / KVMem / llama.cpp）、运行产物与图表索引

## 3. 个人创作与日记（`personal/`，默认隔离在技术检索外）

- `personal/design/` — 人物设定与设计草稿（来自 Ficus-KB）
- `personal/diary/` — 个人日记记录（来自 Ficus-KB）

## 3. 治理与检索工具

- [GOVERNANCE.md](GOVERNANCE.md) — 知识治理、OKF 规范、生命周期与增量更新闭环
- [tools/kb_govern.py](tools/kb_govern.py) — 统一治理体检（`audit`）、增量结构化同步（`sync`）与混合检索（`search`）
- [log.md](log.md) — 仓库结构与治理变更日志
