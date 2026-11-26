# 变更日志（log.md）

## 2026-11-26

- 同步 [NVMe 门铃槽位恢复与通知分支回归](benchmarks/reports/ssd-doorbell-regression.md)，收录三道合成题、原答、工作台报告和可独立运行的 Pi/MCP 工具。真实 SD 工单等待工程师签发记录后单独评估。

## 2026-11-23

- **迁移与治理修理**：将 `Code/my-code/nvmespec` 清洁迁移至 `reporsts/nvmespec/`（排除 `node_modules/`、`dist/`、`tmp/`、`__pycache__/`）。
- **OKF 规范化**：为 319 篇无头文档补齐 OKF YAML Frontmatter，为 209 篇现有文档补齐 `status` 与 `verified` 字段。
- **断链与孤儿修复**：修复 `wikipedia-*-okf/` 中的 22 个文件的 `/concepts/` 绝对路径断链，清理 119 处内部引用/行号链接，补充 285 条索引条目。
- **SSOT 去重**：将 `nvme-wiki/wiki/concepts/` 中 7 篇重复概念及 `wikipedia-okf/` 中 6 篇重叠概念标记为 `status: archived` 并指向唯一真源。
- **根治理工具就位**：部署 [tools/kb_govern.py](tools/kb_govern.py)、[GOVERNANCE.md](GOVERNANCE.md) 与 [index.md](index.md)。
- **根目录整理**：将 10 篇平铺报告与 2 张 SVG 图归入 `reports/`（补齐 OKF Frontmatter、修复相对路径与外部断链、生成 `reports/index.md`），将 4 个原始实验目录归入 `runs/`。
- **语义拆解重构**：废弃混合容器 `nvmespec/`，拆分为 `kb/`（`nvme/`、`pcie/`、`pci-firmware/`、`ssd-design/`、`llm-inference/`、`reference-wikipedia/`）与 `benchmarks/`（`reports/`、`runs/`、`assets/`）两大语义层，并清理冗余 `spec/欢迎.md`。
- **Ficus-KB 整合**：将 `Ficus-KB/wiki/` 的 `agents/`、`engineering/`、`specs/`、`storage/` 合并入 `kb/` 对应领域，将 `wiki/llm/` 归入 `kb/llm-inference/ficus/`，将 `design/` 与 `diary/` 归入 `personal/`（默认隔离于技术检索外）；完成 69 篇文档 `status`/`verified` 规范化、150 处外部路径断链清理与 60 条索引补全。
- **算法与治理文档沉淀**：将 Contextual BM25 + 显式图谱 PPR + RRF 检索算法、渐进式披露 MCP 设计及 OKF 生命周期治理方法写入 [GOVERNANCE.md](GOVERNANCE.md)。
