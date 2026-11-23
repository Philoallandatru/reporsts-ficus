---
type: Concept
title: 证据索引
description: 收录支撑全系列结论的入口。快照时间 **2026-11-19**。各专题保留自己的完整证据表与查证边界；本表负责跨篇的来源分级与版本锁定。
tags:
- agents
- benchmark
- swe-bench
sources:
- c:/Users/Administrator/Documents/Code/my-code/lm-llama/research/agent-bench-ecosystem/appendix-evidence.md
createdAt: '2026-11-23'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 证据索引

收录支撑全系列结论的入口。快照时间 **2026-11-19**。各专题保留自己的完整证据表与查证边界；本表负责跨篇的来源分级与版本锁定。

## 快照版本锁

带行号的 `main` 链接会随上游推送漂移。引用本系列结论时按下表锁定：

| 仓库 | 快照 | commit | 日期 |
|---|---|---|---|
| `harbor-framework/terminal-bench` | tag `v4.1.0` | `4070d6cef56a7d20cb5dc98d5e10ada88a6b9440` | 2026-11-03 |
| 同上 | tag `v4.0.0` | `452bf305c6daa62fc59061d22133a7cbc7c1572e` | 2026-08-26 |
| 同上 | tag `v3.0.0` | `2b0442c3c583b710ca8da14c8e601b99f2f1f244` | 2026-07-23 |
| `harbor-framework/harbor` | `main` | `a215bfa03ccc026d22a0f11d5d6c51a8a46f0510` | 2026-11-19 |
| `harbor-framework/terminal-bench-2-1` | `main` | `12b7565…` | 2026-11-05 |
| `harbor-framework/terminal-bench-science` | `main` | `d4f6c91…` | 2026-11-19 |
| `harbor-framework/harbor-index` | `main` | `5399ea1…` | 2026-08-03 |
| `harbor-framework/terminal-bench-1` | `main` | `d28711d…` | 2026-07-11 |

## 来源分级

本系列统一使用四档。同一事实若有多档来源，取最高档并注明其余。

| 等级 | 含义 | 本系列中的实例 |
|---|---|---|
| **官方一手** | 基准维护方自己发布的源码、文档、榜单、公告 | Harbor 与 Terminal-Bench 仓库、`docs.harborframework.com`、tbench.ai 公告、Harbor Hub 榜单 API |
| **第三方审计** | 独立机构对基准质量的复核 | Epoch AI 对 4.0 的 Flawed 判定、Tokenless 与 Preference Model 的审计 |
| **第三方独立评测** | 用自己协议重跑官方任务集 | Artificial Analysis Coding Agent Index v2.1（TB 4.1，每题 3 次）、DeepMind 方法 PDF（TB-Science、SEC-bench 等自测项） |
| **厂商自述** | 模型厂自己公布的数字 | Anthropic 的 Sonnet 5.5 70.6%、Google 的 Gemini 4 Neon 发布表 |
| **二手汇总** | 只见到转述，未从原站读到 | Lab Index、Tensor.news 关于 AA 权重与榜单的记载 |

## 核心问题 → 一手入口

| 要核对的问题 | 一手材料及位置 | 专题 |
|---|---|---|
| 每版到底发布了哪些任务 | [GitHub Releases](https://github.com/harbor-framework/terminal-bench/releases) 和 [v4.1.0 的任务树](https://github.com/harbor-framework/terminal-bench/tree/v4.1.0/tasks)，目录数排除顶层说明和数据集配置。4.1 保留 66 题，另有 63 题 CPU-only 变体 | [官方栈](01-official-stack.md) / [任务与判分](02-task-and-verifier.md) |
| 2.0 论文说明了什么 | [arXiv 正文](https://arxiv.org/html/2601.11868v1) 的评测设置、Table 2、Limitations。89 题和参考 Agent 对照均属于 2.0 | [方法学](05-methodology-and-audits.md) |
| 任务应该怎样设计 | [Task Guidelines](https://github.com/harbor-framework/terminal-bench/blob/main/docs/task-guidelines.md) 的 Verifiable、Well-specified、Solvable、Difficult、Outcome-verified，以及 [CONTRIBUTING](https://github.com/harbor-framework/terminal-bench/blob/main/CONTRIBUTING.md) 的 Task Quality 和版本约定 | [任务与判分](02-task-and-verifier.md) |
| Agent、环境、verifier 分别负责什么 | [Harbor 任务概览](https://docs.harborframework.com/tasks/overview.md)、[Verifier](https://docs.harborframework.com/tasks/verifier.md)、[独立判分沙箱](https://docs.harborframework.com/tasks/separate-verifier.md)、[RewardKit](https://docs.harborframework.com/rewardkit/motivation-and-design.md) | [官方栈](01-official-stack.md) / [任务与判分](02-task-and-verifier.md) |
| 官方榜的提交要求、均值和区间如何核查 | 官方仓 [SUBMIT.md](https://github.com/harbor-framework/terminal-bench/blob/main/leaderboard/SUBMIT.md)（顶部 NOTE：社区提交关闭）和 [metrics.py](https://github.com/harbor-framework/terminal-bench/blob/v4.1.0/leaderboard/src/leaderboard/core/metrics.py)，对照 [Harbor 默认聚合](https://docs.harborframework.com/datasets/metrics.md) | [方法学](05-methodology-and-audits.md) |
| 公网访问与查题目答案如何区分 | [CONTRIBUTING 的 Task Difficulty](https://github.com/harbor-framework/terminal-bench/blob/main/CONTRIBUTING.md#task-difficulty) 和 [Task Guidelines](https://github.com/harbor-framework/terminal-bench/blob/main/docs/task-guidelines.md) 的防答案检索要求 | [方法学](05-methodology-and-audits.md) |
| 4.0 到 4.1 改了什么 | [4.1 发布公告](https://www.tbench.ai/news/terminal-bench-4-1)、[4.1.0 Release](https://github.com/harbor-framework/terminal-bench/releases/tag/v4.1.0) 与 [Harbor Regrade](https://docs.harborframework.com/jobs/regrade.md) | [任务与判分](02-task-and-verifier.md) / [方法学](05-methodology-and-audits.md) |
| 哪个榜有多少行，能追到什么粒度 | [tbench.ai](https://www.tbench.ai/)、[Harbor Hub 4.1](https://hub.harborframework.com/datasets/terminal-bench/terminal-bench/5?tab=leaderboard&leaderboard=4-1-0) 和 [Hub Leaderboards 契约](https://docs.harborframework.com/harbor-hub/leaderboards.md)。网站折叠展示与 Hub 完整榜分别记录 | [榜单与采用](06-leaderboards-and-adopters.md) |
| 厂商发布表里的数字各来自哪里 | [DeepMind 方法 PDF](https://deepmind.google/models/evals-methodology/gemini-4-neon)、[AA 编码 Agent 索引方法](https://artificialanalysis.ai/methodology/coding-agents-benchmarking)、[AA 对照页](https://artificialanalysis.ai/agents/coding-agents/comparisons/antigravity-cli-vs-codex)、[Google 发布页](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon/) | [出分机制与演化](08-benchmark-mechanics-and-evolution.md) |
| 哪些版本或扩展可以沿用 Harbor | [适配器文档](https://docs.harborframework.com/agents/pre-integrated-agents.md)、[沙箱文档](https://docs.harborframework.com/sandboxes/pre-integrated-sandboxes.md)、[TB-Science](https://github.com/harbor-framework/terminal-bench-science)、[Harbor Index](https://github.com/harbor-framework/harbor-index)、[官方生态索引](https://github.com/harbor-framework/awesome-harbor) | [衍生与复现](03-derivatives-and-replicas.md) |
| 相邻基准测量什么 | [SWE-bench](https://www.swebench.com/)、[TerminalWorld](https://arxiv.org/abs/2605.22535)、[TUA-Bench](https://arxiv.org/abs/2606.28480)。其他项目的官方论文、仓库及榜单见专题 | [相邻基准](04-alternatives-landscape.md) |
| 哪些现象实际在本地测过 | Pi 缓存实验 (`../pi-cache-bench/README.md`)、前缀状态实验 (`../prefix-state-bench/README.md`)、三级缓存收益方案 (`../llamacpp-tiered-cache-evaluation-and-implementation.md`) 和 2026-11-19 的工具链探测 | [本工作区应用](07-implications-for-this-workspace.md) |

## 第三方审计

三份审计独立给出，各自适用版本不同，不要混用：

| 审计方 | 结论 | 适用版本 | 入口 |
|---|---|---|---|
| Epoch AI | **Flawed**：66 题中 30 题含公开记录的评分缺陷 | Terminal-Bench 4.0.0 | [review](https://epoch.ai/benchmarks/terminal-bench-4/review) |
| Tokenless | 110 条 reward hack 与判分缺陷（跨 TB 4.0 / DeepSWE 1.1 / BFCL v4 三个基准合计） | 多基准 | [envcheck](https://usetokenless.com/blog/envcheck/) |
| Preference Model | 242 条发现，逐任务复审并做移植对照 | Terminal-Bench 4 | [blog](https://preferencemodel.com/blog/terminal-bench-4-is-saturated/) |

官方 4.1 公告确认采纳了这三家的意见并做了判分器修订，同时说明多数被报告的利用方式在榜单上并未实际出现。Epoch 对 4.0 的 Flawed 判定**不等于**对 4.1 的判定，后者未找到同口径复审。

## 复核用的命令

```bash
# 官方榜全部行（公开、无需鉴权）
curl -sS -X POST https://api.harborframework.com/functions/v1/leaderboard-read \
  -H "Content-Type: application/json" \
  -d '{"package":"terminal-bench/terminal-bench","name":"4-1-0","page":1,"page_size":100}'

# 任务集版本与数量
gh api "repos/harbor-framework/terminal-bench/contents/tasks?ref=v4.1.0" --jq '.[].name'
gh api "repos/harbor-framework/terminal-bench/git/trees/v4.1.0?recursive=1" --jq '.tree[].path'

# 榜单统计实现
gh api repos/harbor-framework/terminal-bench/contents/leaderboard/src/leaderboard/core/metrics.py \
  -H "Accept: application/vnd.github.raw"
```
