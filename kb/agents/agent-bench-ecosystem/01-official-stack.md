---
type: Concept
title: Terminal-Bench 官方栈全景
description: '`harbor-framework` 组织共 **21 个公开仓库**（`gh api orgs/harbor-framework/repos
  --paginate`，21 条，无分页遗漏）。下表按角色分组，license 列的 `—` 表'
tags:
- agents
- benchmark
- swe-bench
sources:
- c:/Users/Administrator/Documents/Code/my-code/lm-llama/research/agent-bench-ecosystem/01-official-stack.md
createdAt: '2026-11-23'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# Terminal-Bench 官方栈全景

> **一句话定位**：Terminal-Bench 已经从一个 Python 评测脚本仓库，演化成一套由 **`harbor-framework` 组织**统辖的官方栈——`terminal-bench`（现行基准本体）+ `harbor`（运行框架）+ `harbor-rewardkit`（判分库）+ Harbor Hub（榜与产物托管），全部 Apache-2.0，文档独立成站 `docs.harborframework.com`。
>
> **证据口径**：仓库状态与任务数来自 2026-11-19 的 GitHub API 快照，文档查阅 Harbor 官网和官方仓库。本篇没有运行基准或测试。第三方来源在相应条目标注。

---

## 1. 官方组件清单

`harbor-framework` 组织共 **21 个公开仓库**（`gh api orgs/harbor-framework/repos --paginate`，21 条，无分页遗漏）。下表按角色分组，license 列的 `—` 表示该仓库**没有可识别的 license 对象**（`license.spdx_id` 返回 `null`，即仓库根目录无 LICENSE 文件），不是 `NOASSERTION`。

### 1.1 基准本体

| 组件 | URL | 作用 | stars | 最后推送 | 许可 | 状态 |
|---|---|---|---|---|---|---|
| `terminal-bench` | github.com/harbor-framework/terminal-bench | 现行基准本体：v3.0.0+ 的 66 个任务、`docs/` 治理文件、`leaderboard/` 提交流水线 | 1088 | 2026-11-19 | Apache-2.0 | live |
| `terminal-bench-1` | github.com/harbor-framework/terminal-bench-1 | TB 1.0 时代的老 harness（`terminal_bench/` Python 包 + `original-tasks/`），**历史遗产** | 2623 | 2026-07-11 | Apache-2.0 | live（事实上冻结） |
| `terminal-bench-2` | github.com/harbor-framework/terminal-bench-2 | TB 2.0 任务集，根目录 89 个任务目录（顶层 92 项含 LICENSE / README / .gitignore） | 450 | 2026-04-30 | Apache-2.0 | live（事实上冻结） |
| `terminal-bench-2-1` | github.com/harbor-framework/terminal-bench-2-1 | TB 2.1「verified」迭代：26 个任务被修 bug / 调超时 / 加固 anti-reward-hacking | 140 | 2026-11-05 | Apache-2.0 | live |

### 1.2 运行框架与 SDK

| 组件 | URL | 作用 | stars | 最后推送 | 许可 | 状态 |
|---|---|---|---|---|---|---|
| `harbor` | github.com/harbor-framework/harbor | **官方 harness**：`harbor run` CLI、task 格式、sandbox/agent 插件、Registry、`packages/rewardkit`、`packages/harbor-atif2otel`、`packages/harbor-langsmith` | 7224 | 2026-11-19 | Apache-2.0 | live |
| `harbor-client` | github.com/harbor-framework/harbor-client | Harbor API 的 Typed Python SDK（Fern 生成 + native Replay） | 1 | 2026-11-19 | Apache-2.0 | live |
| `adapters` | github.com/harbor-framework/adapters | **扩展点**：把外部基准（SWE-Bench、Aider Polyglot、GPQA、AIME 等 80+）转成 Harbor task 格式；已从 harbor monorepo 拆出独立版本化 | 14 | 2026-11-17 | Apache-2.0 | live |
| `harbor-cookbook` | github.com/harbor-framework/harbor-cookbook | 官方配方集：10 个 task recipe + 6 个 RL/优化示例（cortex-rl / harbor-rl / gepa / tinker-rl / prime-rl / sky-rl） | 281 | 2026-10-31 | Apache-2.0 | live |

### 1.3 同组织的独立基准（不是 TB 本体）

| 组件 | URL | 作用 | stars | 最后推送 | 许可 | 状态 |
|---|---|---|---|---|---|---|
| `terminal-bench-science` | github.com/harbor-framework/terminal-bench-science | **独立基准**：科学研究工作流，README 称 96 个专家编纂任务、5 大科学域；Stanford + Laude Institute 主办，官网 terminal-bench-science.ai | 944 | 2026-11-19 | Apache-2.0 | live |
| `harbor-index` | github.com/harbor-framework/harbor-index | **独立基准**：从 6000+ 候选中蒸馏的「高信号」元基准（README 称 80 任务），Harbor 生态自己的 meta-benchmark | 49 | 2026-08-03 | — | live |
| `terminal-bench-challenges` | github.com/harbor-framework/terminal-bench-challenges | **单任务长时挑战**（非重复跑的任务集）：token 密集、长时、单任务、程序化验证 | 26 | 2026-11-06 | — | live |
| `harbor-datasets` | github.com/harbor-framework/harbor-datasets | 把热门基准移植成 Harbor 可跑数据集。README 只是 17 字节的存根（`# harbor-datasets`），实际内容在 `datasets/`：**102 个**已移植基准目录，含 `swebench-verified` `swebenchpro` `swesmith` `aider_polyglot` `gpqa-diamond` `aime` `hle` `gaia2` `arc_agi_1/2` `bixbench` `featurebench` `financeagent` `medagentbench` `paperbench` `skillsbench` `theagentcompany` 等 | 47 | 2026-05-16 | — | live |

### 1.4 扩展点与生态索引

| 组件 | URL | 作用 | stars | 最后推送 | 许可 | 状态 |
|---|---|---|---|---|---|---|
| `awesome-harbor` | github.com/harbor-framework/awesome-harbor | **官方 curated list**：28 个官方认可的周边项目（benchmark / 训练集 / RL / 工具） | 62 | 2026-05-29 | — | live |
| `skills` | github.com/harbor-framework/skills | **扩展点**：Harbor 的 agent skills 目录（`harbor-task-creator` / `harbor-adapter-creator` / `harbor-cli`），供 Claude Code / Codex / Cursor 安装 | 15 | 2026-05-12 | Apache-2.0 | live |
| `harbor-adapters-experiments` | github.com/harbor-framework/harbor-adapters-experiments | adapter 的实验性工作区，非稳定产物 | 9 | 2026-06-28 | Apache-2.0 | live |

### 1.5 站点与文档

| 组件 | URL | 作用 | stars | 最后推送 | 许可 | 状态 |
|---|---|---|---|---|---|---|
| `terminal-bench-website` | github.com/harbor-framework/terminal-bench-website | tbench.ai 站点源码（Next.js + Fumadocs） | 6 | 2026-11-16 | — | live |
| `terminal-bench-docs` | github.com/harbor-framework/terminal-bench-docs | TB 文档分仓 | 10 | 2026-08-19 | — | live |
| `terminal-bench-science-docs` | github.com/harbor-framework/terminal-bench-science-docs | TB-Science 文档分仓 | 1 | 2026-08-26 | — | live |
| `docs` | github.com/harbor-framework/docs | 历史文档仓，现行读者入口见 [Harbor 文档](https://docs.harborframework.com/) | 0 | 2026-06-03 | MIT | **ARCHIVED** |
| `harbor-docs` | github.com/harbor-framework/harbor-docs | **归档**：更早一批文档仓 | 5 | 2026-03-31 | — | **ARCHIVED** |
| `benchmark-template` | github.com/harbor-framework/benchmark-template | **归档**：在 Harbor 上建基准的模板（`harbor-framework/benchmark` 现在 302 到这里） | 18 | 2026-08-06 | — | **ARCHIVED** |

> Harbor 面向读者的现行文档在 [docs.harborframework.com](https://docs.harborframework.com/)，站点部署元数据指向 `harbor-framework/harbor` 的 `docs-mintlify`。历史文档仓的 `archived` 和 `pushed_at` 分别记录归档状态与最后推送时间。官方提供机器可读的 [llms.txt](https://docs.harborframework.com/llms.txt)。

### 1.6 `awesome-harbor` 官方认可的周边项目（28 条，官方一手 curated list）

`gh api repos/harbor-framework/awesome-harbor/contents/README.md`（4401 bytes，单文件）。注意该 README **停留在 2026-05-29 的快照**，链接有陈旧/失效条目（见 §6）。

| 分类 | 条目（官方原文描述） |
|---|---|
| Evaluation Benchmarks | `terminal-bench-2`（官方）；`terminal-bench-pro`（Alibaba 扩展）；`skillsbench`；`otel-bench`；`CompileBench`；`harbor-datasets`（SWE-bench verified 等移植）；`RuneBench`；`legacy-bench`（Factory-AI）；`SWE-Atlas`（scaleapi） |
| Training Datasets | `SWE-gen-Java` / `-JS` / `-Rust` / `-Go` / `-Cpp`（各 1000 任务）；`Nemotron-Terminal-Synthetic-Tasks`（NVIDIA）；`seta-env`（camel-ai 全自动 Harbor 任务合成与验证） |
| Training & RL | `OpenThoughts-Agent`；`endless-terminals`；`Ares`（withmartian，基于 Harbor + SkyRL 的在线 RL）；`SkyRL Harbor Integration` 指南 |
| Tools | `harbor-bot`（PR 自动 QA）；`Benchmark Template`（链接已失效，见 §6）；`SWE-gen`；`Oddish`（eval 调度器）；`TerminalBenchTaskGenerator`（桌面应用）；`AutoAgent`；`Meta-Harness`（Stanford IRL）；`ATIF Trajectory Viewer` |

---

## 2. 版本与发布线

### 2.1 发布线时间线

| 线 | 版本 | 发布日期 | 定位 |
|---|---|---|---|
| terminal-bench | `v3.0.0` | 2026-07-23 | 「Added initial 74 Tasks」，首发时仍是 `harbor-framework/frontier-bench` 仓（**formerly Frontier-Bench**）。tag 处 74 个任务目录 |
| terminal-bench | `v4.0.0` | 2026-08-26 | 校准时间、CPU 和内存，官方公告称修复 19 题。撤下 8 题，饱和、拒答、公开解答、未解决的质量或平台兼容性问题各占 2 题。发布任务目录由 74 减至 66。 [4.0 公告](https://www.tbench.ai/news/terminal-bench-4-0) |
| terminal-bench | `v4.1.0` | 2026-11-03 | 「Tasks added or removed: None. **Tasks modified (66)**」+ 新增 **CPU-only 数据集 63 任务**（`terminal-bench/terminal-bench-cpu@4.1.0`）。tag 处 66 个任务目录 |
| harbor | `v0.3.0` → `v0.9.0` | 2026-03-27 → 2026-05-28 | 早期迭代；`v0.3.0` release name 即「The new Harbor registry」 |
| harbor | `v0.13.0` → `v0.18.0` | 2026-05-30 → 2026-07-07 | 稳定化期；`v0.18.0` 引入 personal API key 替代 GoTrue session、`harbor hub leaderboard create/show/list` |
| harbor | `v0.20.0` → `v0.26.0` | 2026-07-18 → **2026-11-13** | 功能期。`v0.21.0` 引入 `harbor job/trial regrade`；`v0.24.0` 引入 `--stream` 与 `harbor run --diff`；`v0.25.0` 引入 `harbor lint`、`.harborignore`、RewardKit `Worker`、**新任务默认 separate verifier**；`v0.26.0` 引入 `harbor serve` |
| terminal-bench-1 | 无 release | 最后提交 2026-07-11 | 冻结的 1.0 harness |
| terminal-bench-2 | 无 release | 最后提交 2026-04-30 | 冻结的 2.0 任务集 |
| terminal-bench-2-1 | 无 release | 最后提交 2026-11-05 | 2.1 verified 任务集 + 自己的 leaderboard 提交流水线 |
| terminal-bench-science | `v0.1.0` | 2026-08-26 | 首个正式 release |
| harbor-index | `harbor-index-1.1` → `-1.4` | 2026-07-11 → 2026-07-28 | 用 `harbor-index-1.x` 而非 `v1.x` 命名 |
| harbor-client | `v0.1.0`, `v0.2.0` | 2026-11-18, 2026-11-19 | SDK 起步 |

### 2.2 改名 / 迁移事实（`gh api` 302 重定向实测）

| 旧 URL | 302 到 | 说明 |
|---|---|---|
| `laude-institute/terminal-bench` | `harbor-framework/terminal-bench-1` | **原始 TB 仓库被重命名为 `-1`**，现行基准另起 `terminal-bench`。这解释了为何 `terminal-bench-1` 有 2623★（历史积累）而 `terminal-bench` 只有 1088★ |
| `laude-institute/harbor` | `harbor-framework/harbor` | Harbor 从 laude-institute 迁到 harbor-framework |
| `laude-institute/terminal-bench-2` | `harbor-framework/terminal-bench-2` | 同上 |
| `laude-institute/harbor-datasets` | `harbor-framework/harbor-datasets` | 同上 |
| `harbor-framework/frontier-bench` | `harbor-framework/terminal-bench` | v3.0.0 的 PR 链接仍指向 `frontier-bench`；官方 news 标题为「Terminal-Bench 3.0 (formerly Frontier-Bench)」 |
| `harbor-framework/benchmark` | `harbor-framework/benchmark-template` | 且目标**已归档**——`awesome-harbor` 里指向它的链接实际失效 |

`laude-institute` 组织现存 8 个仓库：6 个已归档的 TB 遗留（`terminal-bench-datasets`、`terminal-bench-leaderboard`、`terminal-bench-experiments`、`terminal-bench-2-0-sample`、`terminal-bench-lite`、`terminal-bench-2-leaderboard`）+ 2 个 live（`headlong` 1277★、`rev-engine` 29★，均与 TB 无关）。

### 2.3 「66 任务 / 7 域」数字的核验

| 断言 | 核验方式 | 结果 |
|---|---|---|
| v3.0.0 = 74 任务 | `contents/tasks?ref=v3.0.0` 计数 | 74 ✅ 与 release body「Added initial 74 Tasks」一致 |
| v4.0.0 = 66 任务 | 同上 | 66 ✅ = 74 − 8 removed |
| v4.1.0 = 66 任务 | 同上 | 66 ✅ 与「Tasks modified (66)」一致 |
| 7 个领域 | `docs/TAXONOMY.yaml` 顶层 `areas` | 7 ✅ Science / Software / ML / Operations / Security / Hardware / Media |

---

## 3. 官方文档地图

`https://docs.harborframework.com/llms.txt` 共 **105 个页面**（含 6 个 news 页、26 个 API-SDK 页）。下表只列本调研指定的必读页；每页记录「它规定了什么」。

| 页面 | 规定了什么 | 关键命令 / 字段 |
|---|---|---|
| `getting-started/quick-start` | 装 Harbor → 跑第一个 job → 本地看结果 → 上传共享。trial=一次解题尝试，job=trial 集合 | `harbor run -t hello-world/hello-world -a codex -m openai/gpt-5.6-luna`；`harbor view ./jobs`；`harbor upload ./jobs/<job-id>`；默认 Docker sandbox，`--env/-e` 切云沙箱，`--launch` 上 Hub |
| `jobs/run-a-job` | job 的 6 种数据源形态 + CLI 配置面 + config 文件模型 | 本地数据集 `-p` / 本地任务 `-p` / Hub 数据集 `-d "<org/dataset>@<ref>"` / Hub 任务 `-t` / 自定义 registry `--registry-path` \| `--registry-url` / Git 仓库 `--repo`；`-n` 并发 `-k` 尝试 `-r` 重试；`-l` 限任务数 `-i` glob `-x` 排除；`-e` sandbox `--allow-agent-host` `--override-memory-mb`；`--effort` / `--ak` / `--model`；`--print-config`、`harbor job init`、`config.json` |
| `tasks/verifier` | verifier 入口、reward 文件契约、separate/shared 模式、regrade 前提 | `tests/test.sh`（Linux）/ `tests/test.bat`（Windows）；必须产出 `/logs/verifier/reward.txt` 或 `reward.json`（**两者同存时优先 json**）；`[verifier] environment_mode = "shared"\|"separate"`；`[verifier.environment].docker_image` 优先于 `tests/` 构建定义；`[verifier.env]` 用 `${VAR}` 读宿主环境（**需用户确认**） |
| `jobs/custom-verifiers` | 默认 `Verifier` vs 自定义 `BaseVerifier` 的取舍与契约 | 自定义类必须实现 `async verify() -> VerifierResult`；配置 `verifier.import_path` + `verifier.kwargs`；CLI `--verifier custom_verifier:OutputVerifier --verifier-kwarg required_path=/app/output.json`；**自定义 verifier 完整替换默认流程**，上传/命令/算分全自负 |
| `jobs/regrade` | 用新 verifier 对已录制产物重判、**不重跑 agent** | `harbor job regrade "jobs/<job>" -p path/to/updated-task -e modal`；`harbor trial regrade "jobs/<job>/<trial>"`；Hub UUID 形态；前置条件：源 trial 有可读 `result.json` + `artifacts/manifest.json`、更新后任务用 separate verifier、所需 artifact 都已被采集；`--ve` 透传 verifier 环境变量；「no agent credentials, no new agent cost」 |
| `jobs/artifact-collection` | artifact 声明格式、跨沙箱搬运语义、采集清单 | `artifacts = [...]`（task.toml 顶层，须在首个 section 之前）/ `--artifact` / config `artifacts`；对象形式 `source` / `destination` / `exclude` / `service`；落盘 `<trial-dir>/artifacts/<destination>`；`<trial-dir>/artifacts/manifest.json` 记 `ok`/`empty`/`failed`/`skipped`；`/logs/artifacts/` 自动采集**即将移除**（官方 WARNING）；separate verifier 只搬运声明的 artifact；多容器用 `service` + `[[verifier.collect]]` |
| `agents/pre-integrated-agents` | 内置 agent 名单与**能力矩阵** | 47 个 agent（`aider`…`opencode-v2`）；能力位：ATIF / Resume / Load native trajectory / Load ATIF trajectory / Handoff / Native configuration / Windows / ACP bridge / MCP servers / Skills / HTTP MCP headers / Native web tools；`--ak` / `--ae` / `--effort`；`--ak skip_install=true` 复用镜像内已装 agent |
| `sandboxes/pre-integrated-sandboxes` | sandbox 分类、provider 名单、**能力矩阵** | 本地 `docker`(默认) / `podman` / `apple-container` / `singularity` / `sbx`；远端 ~30 个（`modal` `daytona` `e2b` `ec2` `gke` `vercel` `runloop` `sky`…）；`-e/--env`、`--ek/--environment-kwarg`、`-n`（默认 4）、`--force-build`、`--delete`（默认删）、`--cpus/--memory`（auto/limit/request/guarantee/ignore）；能力位：Compose / GPU / TPU / Windows / Host-mounted logs / Stream over SSH / 断网 / 主机名白名单 / CIDR / 运行时策略 |
| `datasets/metrics` | dataset 级聚合指标的自定义方式与默认值 | 默认「averages rewards across tasks and treats missing rewards as 0」；单维 → `{"mean": 0.25}`，多维 → 每维独立聚合，缺失维度计 0；`metric.py` 必须接受 `-i/--input-path`（rewards JSONL）与 `-o/--output-path`；`harbor init --dataset "<org>/<name>" --with-metric`；输出 `{"mean": 0.81, "pass_rate": 0.5}` |
| `harbor-hub/leaderboards` | 榜的定义 schema、行结构、trial 链接、脚本化读取 | `harbor hub leaderboard list/show/init/create/update`；定义字段 `package`\|`package_id` / `name` / `title` / `visibility`(默认 private) / `metadata_schema` / `metrics_schema` / `columns[]` / `rank_by[]` / `dataset_version_refs`；行字段 `metadata` / `metrics` / `status`(display\|hide) / `trial_ids`（1–500 行/次）；`row create/update/delete`、`row trial set/add/remove`；公开读走 `https://api.harborframework.com/functions/v1/leaderboard-read`；「Hub **不**由 linked trials 计算分数」 |
| `rewardkit/quick-start` | RewardKit 的安装、与 Harbor 的接线、评分合并规则、隔离、`Worker` | `uv tool install harbor-rewardkit`（`[all]` 加文档/图片 extra）；`tests/` 下放 `*.py`（程序化 criteria）与 `*.toml`（judge），`rewardkit /tests` 跑，workspace 默认 `/app`，输出 `/logs/verifier/reward.json`；每个 `.py`/`.toml` 出一个分，文件名即分名；`reward.toml` 里 `[scoring.files].aggregation` 与 `[[reward]].aggregation` 两层；聚合模式 `weighted-mean`/`weighted-sum`/`all-pass`/`any-pass`/`threshold`/`required-pass`；子目录 = 多 reward 维度；`isolated=True` 用 overlayfs 只读挂载；`Worker()` 以非特权用户跑提交代码 |
| `rewardkit/motivation-and-design` | 为什么有 RewardKit：verifier 是最烦的部分 | 5 条设计原则：**Simplicity**（目录即定义）/ **Reuse and sharing**（纯文件、git 版本化）/ **Zero boilerplate**（20+ 内置 criteria + 原生 LLM/agent judge）/ **Isolation**（overlayfs 快照互不干扰）/ **Security**（「The agent's code never has to run inside the grader」） |
| `rewardkit/judge-criteria` | judge 的完整 TOML 契约 | `[judge]`: `judge`(默认 `anthropic/claude-opus-5-5`) / `model` / `files` / `mode`(batched\|individual) / `timeout`(300) / `reasoning_effort` / `isolated` / `cwd` / `mcp_servers[]` / `reference` / `atif-trajectory` / `weight`(1.0) / `prompt_template` / `samples`(1) / `guard`(off\|flag\|penalize) / `on-error`(fail\|drop) / `response-format`(json-schema\|json-object\|none)；`[[criterion]]`: `description`(必填) / `type`(binary\|likert\|numeric\|rubric) / `points` / `min`/`max` / `levels` / `weight` / `files` / `negate` / `optional` / `id`；归一化规则（likert `(raw-1)/(points-1)`）；`--judge` / `--model` / `--je` / `--reasoning-effort` 覆盖 |

### 3.1 补充：文档站上另外几页对本调研重要的

| 页面 | 规定了什么 | 关键内容 |
|---|---|---|
| `jobs/error-classification` | **错误→重试/判分/奖励有效性的唯一真源** | `src/harbor/models/trial/error_policy.py` 是 single source of truth；每个异常映射到 `ErrorPolicy{should_retry, should_grade, has_valid_reward}` 三字段；`result.reward_valid` 决定奖励能否进 benchmark/RL 聚合；无效奖励「不进分子也不进分母」 |
| `tasks/separate-verifier` | 独立 verifier 沙箱的完整语义 | `environment_mode="separate"`；`[verifier.environment]` 可配 `network_mode`/`cpus`/`memory_mb`；per-step 用 `[steps.verifier]`；`tests/` 被当作 environment 目录 |
| `changelog` | 稳定版发布说明 | 与 GitHub releases 互链；v0.26.0 明确标注 breaking changes |

---

## 4. 官方口径条款表

> 本节是全文最重要的一节。**每条都是官方原文**，出处给到 URL + 小节标题（GitHub 文件类给出 `file:line`）。后续文档引用「官方口径」时应直接引本表编号。
>
> 简称：**TB** = `github.com/harbor-framework/terminal-bench`；**TBG** = `docs/task-guidelines.md`；**TBC** = `CONTRIBUTING.md`；**TBR** = `docs/REVIEWING.md`；**TBRA** = `docs/TASK_REVIEW_AUTOMATION.md`；**HF** = `docs.harborframework.com`。

| # | 条款 | 原文摘录 | 出处（URL + 小节） |
|---|---|---|---|
| 1 | 任务准入的六条硬性要求 | "All terminal bench tasks must be: 1. **Verifiable**: the task must be checkable with a program that is all-but-guaranteed to detect errors and all-but-guaranteed to return "valid" for correct solutions. 2. **Well specified** … 3. **Solvable** … 4. **Difficult** … 5. **Realistic, valuable, and at least somewhat interesting** … 6. **Outcome-verified**: we are grading outcomes, not the process to get there." | TB → `docs/task-guidelines.md:1-8`（https://github.com/harbor-framework/terminal-bench/blob/main/docs/task-guidelines.md） |
| 2 | 主观题直接拒 | "Reject tasks that there is no way to verify the task has been solved or where grading is subjective (e.g., "make this game more fun")" | TBG §Verifiable（`docs/task-guidelines.md:11`） |
| 3 | verifier 必须几乎完美、且可反复跑不 flaky | "The verification must be efficient and reliable. Tasks that have nondeterminism must always be verified correctly. **Re-running the verifier hundreds of times should show no failures.**" | TBG §Verifiable（`docs/task-guidelines.md:13`） |
| 4 | LLM-as-a-judge 的唯一例外条件 | "Using LLM-as-a-judge is permissible in rare and extraordinary circumstances but only if it can be shown that the verifier essentially never makes a mistake. One way to show this is by showing that multiple different LLMs always make the same determination. **It must be documented what alternate approaches could have substituted for LLM-as-a-judge and why those are insufficient.**" | TBG §Verifiable（`docs/task-guidelines.md:15`） |
| 5 | well-specified 的双盲判据 | "if two reasonable people read the problem description, a well-specified problem should result in both of them writing verification algorithms so that anyone who passed one of the verifiers would also pass the other" | TBG §Well-specified（`docs/task-guidelines.md:21`） |
| 6 | 难度的下限（本科生几天内能解 = 太简单） | "As a general rule, **any task that could be solved by an average undergraduate student in under a few days is too easy.** This means typical problems that feel like course projects are unlikely to be accepted. These projects include tasks like writing simple compilers or operating systems; or implementing simple algorithms or protocols." | TBG §Difficult（`docs/task-guidelines.md:37`） |
| 7 | 冷门事实不构成难度 | "Obscure factual knowledge generally does not make tasks hard. If the solution to a task is knowing a very specific fact it is likely that modern LLMs already know this fact. … **Because TB tasks are open-Internet, tasks that can be solved by looking up an obvious question are not valid.**" | TBG §Difficult（`docs/task-guidelines.md:41`） |
| 8 | 允许查答案但禁止查「本题答案」 | "It is OK if a problem has been solved once, or just a few times, before on the internet. The agent will be instructed not to search for the problem answer online, and **we will run a process grader to verify that the agent did not look up the answer** as part of its solution." | TBG §Difficult（`docs/task-guidelines.md:43`） |
| 9 | 只能判结果，不能判过程 | "Tasks must not be graded based on the approach taken, only the final solution. For example, a task cannot say "use emacs to edit a file". Using vim is allowed. … **Instructions that enumerate a long list of steps or procedures the agent must follow are often overspecified.**" | TBG §Outcome-verified（`docs/task-guidelines.md:55`） |
| 10 | 约束只能是机械性的 | "Constraints can be put in place only if they are mechanistic and prevent the task from being solved by cheating (or similar). **The only exception to this rule is verification that prevents cheating.**" | TBG §Outcome-verified（`docs/task-guidelines.md:57`） |
| 11 | 反「gimmick」与反重复 | "Tasks must not be gimmicks. There shouldn't be a "trick question". … Tasks must be different from all other existing TB tasks." | TBG §Misc. considerations（`docs/task-guidelines.md:63-64`） |
| 12 | 难度必须超出现有模型能力，且不许靠「关网」造难度 | "Contributed tasks should be **well beyond the current frontier of model ability**: tasks which agents cannot solve (reliably or at all) due to meaningful failures." ／ "Terminal-Bench is an open-internet benchmark. We want agents to have their full capabilities available, so **disabling network access is not a valid way to make a task difficult.**" | TBC §Task Difficulty（`CONTRIBUTING.md:32`, `CONTRIBUTING.md:36`） |
| 13 | 任务质量三要件 | "A high quality Terminal-Bench task is: - Something a human would be paid to complete using a computer - A clear instruction and robust verifier such that a solution passes verification **if and only if** it successfully completes the instruction - Robust across time and on hardware that meets the specified resource requirements" | TBC §Task Quality（`CONTRIBUTING.md:76-80`） |
| 14 | 任务 README 四段且必须人写 | "`## Difficulty explanation` / `## Solution explanation` / `## Verification explanation` / `## Relevant experience` … **All of these sections MUST be written completely by a human.**" | TBC §README.md sections（`CONTRIBUTING.md:221-228`） |
| 15 | instruction.md 必须以固定句结尾，且 CI 强制 | "End the file with a blank line followed by this exact sentence and a trailing newline (CI enforces it via `check-instruction-suffix`): `You have N seconds to complete this task. Do not cheat by using online solutions or hints specific to this task.` where N is the integer value of `[agent].timeout_sec`" | TBC §Instruction guidelines（`CONTRIBUTING.md:258-264`） |
| 16 | 任务级语义化版本 = 榜单复用规则 | Major = 改 agent 环境/指令/数据/资源 → "Run the agent again."；Minor = 改 verifier（过严判分、防 reward exploit、judge criteria、算分方式）→ "Grade saved artifacts again."；Patch = 仅元数据维护 → "**Reuse previous results.**" | TBC §Task Versioning and Changelogs（`CONTRIBUTING.md:378-382`） |
| 17 | 全基准强制 separate verifier（5 个机械条件） | 检查项要求：`[verifier] environment_mode="separate"`；`artifacts` 必须在 `task.toml` 顶层；必须有 `tests/Dockerfile`；该 Dockerfile 必须 COPY/ADD 到 `/tests`（separate 模式 `skip_tests_upload=True`）；必须 `RUN mkdir -p` 预建每个 artifact 的父目录。理由原文："**Shared mode is leaky** — the verifier inherits agent-installed packages, mutated filesystem state, and any files the agent wrote — so this check enforces isolation across the benchmark." | TBRA §check-separate-verifier（`docs/TASK_REVIEW_AUTOMATION.md:212-222`） |
| 18 | verifier 禁止 trial 时联网（已知攻击面） | "Trial-time fetches are flaky … and are a known reward-hacking surface (an agent can shim `/usr/bin/curl` in its phase so the verifier's later fetch returns trojaned output — **the RDI/Berkeley 89/89 attack on TB2**). Bake external deps into `tests/Dockerfile`" | TBRA §check-trial-network-fetch（`docs/TASK_REVIEW_AUTOMATION.md:224-230`） |
| 19 | pytest 版本必须锁到全仓统一值 | "As of PR #1313 every task is unified on `pytest==9.1.1` and `pytest-json-ctrf==0.5.2`" | TBRA §check-pytest-version（`docs/TASK_REVIEW_AUTOMATION.md:242`） |
| 20 | 禁止裸 `nproc` | "Inside a Docker container, `nproc` returns the host CPU count, not the configured cpu limit … this is what tb2.1 had to patch in `caffe-cifar-10` and `compile-compcert`." | TBRA §check-nproc（`docs/TASK_REVIEW_AUTOMATION.md:246`） |
| 21 | 任务环境不得用 docker volumes | "Some sandbox providers do not support Docker volumes … This supersedes the former `check-compose-host-binds`" | TBRA §check-compose-volumes（`docs/TASK_REVIEW_AUTOMATION.md:250`） |
| 22 | 自动 rubric 评审只是「第一遍信号」，不是终审 | "This evaluates **30 criteria** covering verifiability, difficulty, anti-cheat robustness, task security, separate-verifier configuration, and more. **Treat it as a first-pass signal, not a final judgment.** You can re-run it anytime by commenting `/review` on the PR." | TBR §Suggested Review Order 第 2 步（`docs/REVIEWING.md:9`） |
| 23 | 合并权限是个人化的 | "Maintainers review task PRs directly — there is no automated reviewer assignment, DRI rotation, or two-pass label lifecycle. … **Only Ryan or Ivan can merge to main.**" | TBR §Review and Merge（`docs/REVIEWING.md:47`, `docs/REVIEWING.md:52`） |
| 24 | 静态 CI 检查清单（口径基线） | Canary string present；Dockerfile 不 copy solution/tests；Dockerfile sanity（不锁 apt 版本、正确清理）；instruction 用绝对路径；test 文件引用与 instruction 一致；`test.sh` 用 uv venv；task.toml 必填元数据 | TBR §Suggested Review Order 第 3 步（`docs/REVIEWING.md:11-18`） |
| 25 | 三类 reward hack 的官方定义 | "**Tampering** — Interferes with and subverts the grading process … **Cheating** — Gets the answer from somewhere it shouldn't … **Loopholes** — Satisfies the tests without solving the problem" | HF `/news/reward-hacking` §What counts as a reward hack（https://docs.harborframework.com/news/reward-hacking.md） |
| 26 | 分三阶段防 reward hacking（写任务时 / 跑时 / 跑完后） | "We've addressed reward hacking in three stages: when a task is written, while it runs, and after it finishes." | HF `/news/reward-hacking` §Three chances to mitigate reward hacking |
| 27 | `harbor lint` 的具体规则集 | `agent-image-test-leak`、`shared-verifier`、`compose-writable-bind-mount`、`compose-privileged`、`compose-additional-capabilities`、`verifier-network-download`、`unpinned-image`（"Images not pinned to a digest, which can change under you"） | HF `/news/reward-hacking` §Catch weak spots with `harbor lint` |
| 28 | `harbor check` 默认用 11 分制 TB 风格 rubric | "`harbor check` drops the agent into a sandbox containing the task source files and has the agent grade the task against a rubric. **By default, an 11-point Terminal-Bench-inspired rubric is used**, but task creators can override the rubric using `--rubric`." | HF `/news/reward-hacking` §Review the whole task with `harbor check` |
| 29 | 评测意识最小化 | "An agent that can tell it's in an eval harness may behave differently. Harbor-branded paths, environment variables, generated agent instructions and identities, and tool directories now use neutral names." | HF `/news/reward-hacking` §Minimizing eval awareness |
| 30 | artifact 搬运时的净化规则 | "Drops symlinks that point outside the artifact … Skips FIFOs, sockets and device files, which could hang the grader … Clears setuid and setgid bits" | HF `/news/reward-hacking` §Sanitize artifacts before the verifier reads them |
| 31 | 榜单必须可审计、可复现 | "**Leaderboards should be *auditable* and *reproducible*.** You can create leaderboards on Harbor Hub, where each row can link to the trials behind it, so anyone reading the leaderboard can view the corresponding trajectories (and the exact config that produced the trial)." | HF `/news/reward-hacking` §Publish leaderboards backed by trajectories |
| 32 | Hub 不替用户算分（构造自由度优先） | "**Harbor Hub intentionally does not calculate row scores from linked trials, to enable maximally flexible leaderboard construction.**" ／ "Prepare your results as rows, **calculating the scores yourself**." | HF `/harbor-hub/leaderboards` §Browse / §General approach |
| 33 | 共享默认私有 | "Job results are private by default, but can be shared with other users or organizations, or made public" ／ "Jobs are private by default. Trust us, it's better than sharing zips on Slack." | HF `/news/job-result-sharing`；HF `/news/reward-hacking` §Share trajectories on Harbor Hub |
| 34 | regrade 的经济性承诺 | "No agent environment is started, so **regrading needs no agent credentials and incurs no new agent cost**." | HF `/jobs/regrade` §How it works |
| 35 | 数据集默认聚合口径 | "By default, Harbor **averages rewards across tasks and treats missing rewards as 0**." ／ "Missing rewards and missing dimensions count as 0." | HF `/datasets/metrics` §Default behavior |
| 36 | 错误分类的唯一真源 | "`error_policy.py` is the **single source of truth** for trial errors. Each exception type maps directly to an `ErrorPolicy` with three independent fields: `should_retry`, `should_grade`, and `has_valid_reward`." | HF `/jobs/error-classification` 开篇 |
| 37 | 「0 和 1 都可能是有效奖励」 | "**Both 0 and 1 can be valid reward signals.** `reward_valid` indicates whether a reward can be used for RL and job reward aggregation, not whether the task succeeded. **Invalid rewards contribute to neither the numerator nor the denominator of the mean.** For example, rewards `0` (valid), `1` (valid), and `1` (invalid) produce `(0 + 1) / 2 = 0.5`." | HF `/jobs/error-classification` §（NOTE 块） |
| 38 | 禁自动挂载输出目录（历史漏洞） | "Local environments like Docker used to bind-mount log and artifact directories to the host automatically, including `/logs/verifier` in the agent's container, so the agent could still write a reward file the verifier would read (#3741). Those mounts are now opt-in" | HF `/news/reward-hacking` §No automatic output mounts |
| 39 | RewardKit 的设计原则（官方原文五条） | "**Simplicity:** Verifiers are defined by directory structure … **Reuse and sharing:** Reward criteria are plain files in a directory … **Zero boilerplate:** 20+ built-in criteria … **Isolation:** Criteria can run in isolated filesystem snapshots … **Security:** **The agent's code never has to run inside the grader.**" | HF `/rewardkit/motivation-and-design` §Design principles |
| 40 | RewardKit 的存在理由 | "When creating new tasks for Harbor, **writing the verifier is often the most tedious part**. We looked at verifier implementations across popular benchmarks and found that they are often complicated scripts that are hard to read, extend, and reuse across tasks. This leads to copy-and-pasting of boilerplate code between tasks, which causes subtle errors in verifiers during evals." | HF `/rewardkit/motivation-and-design` §Motivation |
| 41 | TB 的「持续基准」自我定位 | "Terminal-Bench is a **continuous benchmark**, with **tagged releases** published on the Harbor Hub." | TB → `README.md:8` |
| 42 | TB 3.0 的前身是 Frontier-Bench | 官方 news 标题："## Terminal-Bench 3.0 (formerly Frontier-Bench)" | HF `/news`（2026-07-23 条目）；`gh api repos/harbor-framework/frontier-bench` → 302 到 `terminal-bench` |
| 43 | 评审流程的人工环节不可省 | PR 必须 "pass automated checks and **receive maintainer approval before merge**"；流程为 "automated checks run on every push, a maintainer discusses feedback and triggers further checks, and the task is iterated to a high quality bar" | TB → `README.md:48`；TBR 开篇（`docs/REVIEWING.md:3`） |
| 44 | `/run` 与 `/cheat` 的区别（cheat 不等于 hacking） | "Note that ✅ (reward 1.0) doesn't necessarily mean the agent hacked — it may have solved the task legitimately. The LLM-based analysis determines whether actual hacking occurred." | TBRA §Cheat Trials（`docs/TASK_REVIEW_AUTOMATION.md:340`） |
| 45 | `/fortify` 与 `/cheat` 的区别 | "`/cheat` runs an agent **once** under an adversarial prompt and reports whether it hacked, whereas `/fortify` **iterates** hacker↔fixer and produces hardening." ／ "**The loop does not modify the PR branch.**" | TBRA §Hacker-Fixer Loop（`docs/TASK_REVIEW_AUTOMATION.md:361`, `:363`） |
| 46 | Harbor 的贡献黄金法则 | "We've adopted Ghostty's golden rule: **you must understand the code you contribute**. Feel free to use coding agents liberally, but you are in charge of demonstrating an understanding of your code." | HF 仓 → `CONTRIBUTING.md` §Golden Rule（https://github.com/harbor-framework/harbor/blob/main/CONTRIBUTING.md） |
| 47 | 文档/issue/PR 必须人写 | "**Docs, PR descriptions, issues, and comments should be written by a human with AI assistance.** … you are in charge of the *first* draft and the *last* draft but can use agents in between." | HF 仓 → `CONTRIBUTING.md` §Communication |
| 48 | 接口/核心逻辑变更必须先 RFC | "We are unlikely to change interfaces or core logic without first discussing a design. **This is especially true for Harbor format.**" ／ "The RFC should be **concise** and written by a human with AI assistance. **If an RFC is slop, we will close it.**" | HF 仓 → `CONTRIBUTING.md` §Interfaces and Core Logic |
| 49 | 集成准入门槛（要有人提过） | "We are fairly liberal with integrations. All that we require is that **at least one *user* has asked for the integration** so please provide evidence of that (e.g. by having them leave a comment)." | HF 仓 → `CONTRIBUTING.md` §Agents, Sandboxes, and Plugins |
| 50 | Harbor 是 TB 的重写而非包装 | "We took everything we learned about agent evals and **rewrote the original Terminal-Bench eval harness from the ground up** for improved reliability, observability, scalability, and performance." | TB2 → `README.md` §FAQ（"What is "Harbor" and why do I have to use it?"） |
| 51 | 迁移路径（TB1 harness → Harbor） | "If you'd previously tested your agent or model inside the legacy Terminal-Bench repo then migrating to Harbor should be straight forward. Simply point the same model endpoint to the `--model` arg of `harbor run`. For agents, you'll need to subclass `BaseInstalledAgent` or `BaseAgent`." | TB2 → `README.md` §Migrating from the Terminal-Bench Harness to Harbor |
| 52 | TB-Science 的定位与主办方 | "Terminal-Bench-Science is **an open academic collaboration hosted by Stanford University and the Laude Institute**. As part of the Terminal-Bench franchise, it is built by the Terminal-Bench & Harbor Framework team, and scientific contributors." | TB-Science → `README.md:347` |
| 53 | Harbor 是 Terminal-Bench 的创造者做的框架 | "Harbor is a framework **from the creators of Terminal-Bench** for evaluating and optimizing agents and language models." | HF 仓 → `README.md:10` |
| 54 | 赞助商与托管方（官方一句式声明） | "Compute sponsors: Modal, Anthropic, OpenAI, Google ／ Data partners: ScaleAI, Snorkel Open Benchmarks, Turing, gNucleus AI, Boolean AI, Ellamind ／ **Terminal-Bench is hosted by Harbor and Laude Institute.**" | TB → `README.md:246-248` |

---

## 5. 治理、赞助与贡献流程

### 5.1 治理主体

| 角色 | 名单 | 出处 |
|---|---|---|
| Project Leadership | Ryan Marten、Alex Shaw、Andy Konwinski、Ludwig Schmidt | TB `README.md` §Contributors（Project Leadership 行） |
| Senior Reviewers | Ivan Bercovich、Benedikt Droste、Tommaso Cerruti、Steven Dillmann、Ruiyang Wang、Dariush Wahdany、Allen Hart、Karl Krauth | TB `README.md`（Senior Reviewers 表） |
| Advisors | Mike Merrill、Nicholas Carlini、Gian Segato、Jenia Jitsev、Alex Dimakis | TB `README.md:245` |
| Compute sponsors | Modal、Anthropic、OpenAI、Google | TB `README.md:246` |
| Data partners | ScaleAI、Snorkel Open Benchmarks、Turing、gNucleus AI、Boolean AI、Ellamind | TB `README.md:247` |
| 托管 | Harbor + Laude Institute | TB `README.md:248` |

**Task Authors**（TB `README.md` §Contributors 的 Task Authors 表）共约 80 人/组织，含 6 家机构级作者：**ScaleAI、Snorkel AI、Turing、gNucleus AI、Boolean AI、UniPat AI**；其余为个人（含 Nicholas Carlini、Malte Ubl、Zhuofu Tao、Varun Gangal、Jonas Mueller、Russ Poldrack 等）。**Reviewers** 表另有约 45 人。完整名单以 TB `README.md` 表格为准，本文不逐一转录。

**Senior Reviewer 按领域分配**（TB `docs/REVIEWING.md` §Senior Reviewers by Category，与 `docs/TAXONOMY.yaml` 的 `senior_reviewer` 字段一致）：

| 领域 | 高级评审人 |
|---|---|
| Science / Physics, Math | Allen Graham Hart |
| Science / Chemistry | Aaron Feller |
| Science / Biology | Karl Krauth |
| Science / Earth, other | Steven Dillmann |
| Software / Systems | Ruiyang Wang |
| ML / Kernels | Irakli Salia |
| ML / Training, Inference, Evaluation | Tommaso Cerruti |
| Operations / all | Benedikt Droste |
| Security / all | Dariush Wahdany |
| Hardware / CAD | Karl Krauth |
| Hardware / RTL | Stephen Benjamin |
| Media / Music | Christine Sutcliffe |
| Media / Design | Ryan Marten |

**TB-Science 的研究伙伴**（TB-Science `README.md:333`）：Laude Institute、Stanford AI Lab (SAIL)、Stanford HAI、Stanford AIMS、2077AI Open Source Foundation、NSF AI Institute for Foundations of Machine Learning (IFML)、Allen Institute、Allen Institute for AI (Ai2)。致谢另含 Snorkel AI（Open Benchmarks Grants）、2077AI（PP API credits）、UniPat AI、Modal，以及 Bespoke Labs / Anthropic / Google / Moonshot AI / SpaceXAI / Z.ai 的 API credits。

### 5.2 贡献流程（TB）

```
Calibrate（读 task-guidelines + task-proposal rubric + 已合并任务）
  → Ideate（在自己专业域定义任务提案）
  → Validate（在 Discord #tb-task-spam / 邮件 / 面对面过会）
  → Create（harbor tasks init --include-canary-strings → 写 task 文件）
  → Test（harbor check → harbor run -a oracle → 可选 -a nop / 真 agent → harbor analyze）
  → Submit（开 PR，填 checklist，附 agent 失败分析）
  → 自动检查全绿 → 维护者人工评审（Approve / Request changes）
  → Ryan 或 Ivan 合并
```

关键约束（TBC §Task Difficulty / §Create your Task / §What to Expect After Submitting）：
- 提案先过审再动手："Before investing time in building a full task, share your task idea with maintainers in `#tb-task-spam`"（`CONTRIBUTING.md:110`）
- 提交必须带 agent 失败分析："Run failure analysis on failed trajectories (`harbor analyze`) to confirm the task is **fundamentally hard, not just misspecified**"（`CONTRIBUTING.md:421`）
- 新任务可带 GPU，但"for the current release, GPU-based tasks are limited to a single H100"（`CONTRIBUTING.md:92`）
- 首次贡献可拿 referral 分（`CONTRIBUTING.md:243`）
- 节奏："We will process tasks **first-come-first-serve**"（`CONTRIBUTING.md:84`）

**自动检查矩阵**（TBRA §Pipeline Overview，11 条流水线）：

| 命令 | 作用 | 谁可跑 |
|---|---|---|
| `/overview` | 重新生成任务概览评论 | 任何人 |
| `/validate` | 重跑执行检查（Docker build / oracle / nop） | 维护者（write access） |
| `/run` | 多 agent × model 全量 agent trial | 维护者 |
| `/cheat` | 对抗性 cheat trial | 维护者 |
| `/regrade` | 用 PR 的新 verifier 重判已录制 trial | 维护者 |
| `/fortify` | hacker↔fixer 迭代加固 | 维护者 |

自动跑（无需维护者动作）：Task Overview、Static Checks、Implementation Rubric Review（rubric 条目数见 [02 §6](02-task-and-verifier.md)，需 `ANTHROPIC_API_KEY`）、Docker Build、Oracle Validation、Nop Validation。

### 5.3 Harbor 侧的贡献流程

- 外部 fork PR 必须开 "Allow edits by maintainers"（HF `CONTRIBUTING.md` §PRs）
- 插件比集成更保守："We are slightly less liberal with plugins and only plan to maintain plugins with high demand."（§Agents, Sandboxes, and Plugins）
- 接口/核心逻辑变更先走 RFC，放 `rfcs/`（§Interfaces and Core Logic）
- CHANGELOG 只在 major feature / breaking change 时改（§CHANGELOG.md）
- 依赖锁：`uv 0.13.5+`，`uv sync --locked`；根锁固定 certifi 2026.10.19（§Source dependency setup）

### 5.4 社区与节奏

- TB Discord：`#terminal-bench`（日常）、`#tb-task-spam`（任务想法）；TB-Science 用 `#tb-science`
- 每周会议：**Thursdays 9am PT**（TBC §Contact）
- TB-Science 有公开日历与每周 office hours（TB-Science `README.md:29`）
- 公开路线图：https://github.com/orgs/harbor-framework/projects/1/views/1 （TB `README.md:8`）
- 提交 benchmark 门槛（TB2.1 README）：每任务**至少 5 次 trial**，且必须 **公开**上传到 Harbor Hub，再开 PR 提交到 leaderboard；但 TB2.1 的社区提交**当时已关闭**："***Community submissions are currently closed for Terminal-Bench 2.1. Only submissions run by the maintainers will be added to the leaderboard at this time.***"

---

## 6. 未核实与存疑

1. **本次调研未运行任何代码**：没有 build、没有跑 benchmark、没有跑 test、没有调用 Harbor CLI。文档中的命令、字段、schema 全部是**从官方文档文本中抄录**，未经本机执行验证。
2. **license 字段需区分两种缺省**：部分仓库（`harbor-index` / `awesome-harbor` / `terminal-bench-website` 等）在 `gh api repos/{repo} --jq '.license.spdx_id'` 下返回 **`null`**（整个 `.license` 对象为 null，即根目录无 LICENSE 文件）。这与 SPDX 的 `NOASSERTION`（「有 license 但无法确定」）不等价，引用时按「无 LICENSE 文件」记录。
3. **`harbor-framework/awesome-harbor` 的 README 已过时**（最后推送 2026-05-29）：其中 `terminal-bench-2`、`harbor-datasets` 仍指向 `laude-institute/*`（302 后虽可用，但非现行 URL）；「Benchmark Template」指向 `harbor-framework/benchmark`，该路径 302 到**已归档**的 `benchmark-template`。故该表应视为 2026-05 的快照，不能当作今天的完整生态清单。
4. **Harbor release 号有缺口**：GitHub releases 列表里**没有** v0.1.0 / v0.2.0 / v0.10.0 / v0.11.0 / v0.12.0 / v0.19.0。可能这些版本未在 GitHub 发 release、或被 tag 替代——**未核实**。
5. **TB 4.1 的发布日期有两个口径**：GitHub release `v4.1.0` 的 `published_at` 是 **2026-11-03**，而官方 news 页把 "Terminal-Bench 4.1" 记为 **November 9, 2026**（且链接只指向一条 X 推文，不指向 release）。可能是「发布」与「公告」两个时点，**未核实**。
6. **「66 任务 / 7 域」的适用范围**：66 是 `terminal-bench` 仓 `tasks/` 下目录数，在 `v3.0.0`=74、`v4.0.0`=66、`v4.1.0`=66 三处独立核对一致。但这是**任务目录数**，与 Hub 上发布的 dataset 条目数、CPU-only 数据集的 63 条**不是同一口径**，三者不要混用。
7. **Harbor Index 按快照有两种规模。** 2026-07-08 的官方 news 写 82 题，查阅时主仓 README 和任务树均为 80 题。采样与适配见[衍生与复现](03-derivatives-and-replicas.md)。
8. **TB-Science 按快照有两种规模。** 2026-08-27 的发布新闻写 70 题，查阅时主仓 README 和任务树均为 96 题，覆盖五个科学域。成绩应标注使用哪一版任务集。见[衍生与复现](03-derivatives-and-replicas.md)。
9. **TB-Science「Stanford-led」的表述强度**：news 说 "A Stanford-led Harbor benchmark"；README 原文是 "**an open academic collaboration hosted by Stanford University and the Laude Institute**"，且 README 主体自述为 "a large-scale scientific community effort"。本文采用 README 措辞。
10. **Hub 侧数据未直接核实**：`hub.harborframework.com` 与 `api.harborframework.com` 的实际返回未调用（需鉴权）。Hub 上 `terminal-bench` 的 dataset version 与 release tag 的对应关系（4.0.0 → version `4`，4.1.0 → version `5`）只由 `leaderboard/leaderboard.yaml` 的 `dataset_version_refs: ['4']` 和 v4.1.0 release body 的 URL 推出，未在 Hub 页面二次确认。
11. **Leaderboard 当前实际排名未取**：没有拉取 tbench.ai 或 Hub leaderboard 的行数据，因此本文不对「谁排第几」做任何陈述。`leaderboard/leaderboard.yaml` 只定义了 **TB 4.0** 的榜 schema（`name: 4-0-0`、`visibility: public`、`rank_by: metrics.accuracy desc`），4.1 的榜定义不在该文件中。
12. **`harbor check` 的 11 分制 rubric 与 TB 的 30 条 rubric 是两套东西**：前者来自 HF `/news/reward-hacking`（"11-point Terminal-Bench-inspired rubric"，且 task 作者可用 `--rubric` 覆盖），后者来自 TB `docs/prompts/task-implementation.toml`（30 条）。本文未逐条比对二者，也未读到 `task-implementation.toml` 的实际条文（只从 `docs/REVIEWING.md:9` 读到「30 criteria」这个计数与覆盖范围描述）。
13. **`docs/prompts/` 下的 rubric 原文未逐条抄录**：`task-implementation.toml` / `task-proposal.md` / `trial-analysis.toml` / `hack-trial-prompt.md` / `regrade-analysis.txt` 的正文未读，§4 中相关条款引自 `REVIEWING.md` 与 `TASK_REVIEW_AUTOMATION.md` 的描述性文字。**这是 §4 条款表的主要残余缺口**——条款表要作为「官方口径」被下游引用时，建议再补读这几个 toml。
14. **`terminal-bench-science` / `harbor-index` / `terminal-bench-challenges` 的治理文档未通读**：只读了 TB-Science README 的前 90 行与末尾致谢段，其 `CONTRIBUTING.md` / `REVIEWING.md` / `TASK_REVIEW_AUTOMATION.md` 未读。
15. **`harbor-framework/skills` 与 `adapters` 被标为「扩展点」是我的角色判断**，不是官方原文措辞。官方对 `skills` 的自述是 "Public agent skills catalog for Harbor"，对 `adapters` 的自述是 "the standalone home for Harbor adapters … was split out of the main harbor-framework/harbor monorepo so adapters can be versioned and contributed independently"。
16. **`harbor-datasets` / `terminal-bench-challenges` / `terminal-bench-docs` / `terminal-bench-science-docs` / `terminal-bench-website` 的 description 字段为 `null`**，其作用是依据仓库内容推断的。`harbor-datasets` 的 README 实测只有 **17 字节**（全文即 `# harbor-datasets`），作用依据的是 `datasets/` 下的 102 个基准目录与 `awesome-harbor` 的收录描述 "Popular benchmarks (e.g. SWE-bench verified) ported to run in Harbor"；`terminal-bench-website` 的 README 是 Next.js/Fumadocs 脚手架说明，**未核实**其是否即 tbench.ai 的现行站点源码（仓库名与 `terminal-bench-website` 一致，但站点内容未比对）。
17. **`harbor-datasets` 移植基准清单我未逐一核对可用性**：`datasets/` 下 102 个目录名已列出，但**未验证**每个目录是否含完整 `task.toml`/`instruction.md`/`tests/`，也未验证其在 Hub 上的发布状态。
18. **未读 `docs.harborframework.com` 的全部 105 页**：只读了 22 页（llms.txt 全量清单 + 本调研指定的 13 页 + 9 页补充）。`tasks/overview`、`tasks/instruction`、`tasks/configuration`、`tasks/artifacts`、`datasets/datasets`、`harbor-hub/publish|upload|download|sharing`、`hosted-harbor/*`、`api-sdk/*`、`telemetry/telemetry`、`contributing/release-policy`、`plugins/*` 未读。
19. **tbench.ai 页面与 arXiv 2601.11868 论文正文不在本文范围**：TB2.1 README 给了完整 BibTeX（`@misc{merrill2026terminalbenchbenchmarkingagentshard, … eprint={2601.11868}}`）。论文正文由 [05](05-methodology-and-audits.md) 与 [08](08-benchmark-mechanics-and-evolution.md) 引用，本篇不重复转述其方法学。
20. **`gh api search/code` 未使用**：该接口限流很快，本次结论全部改用 `gh api` 的 repos / contents / releases / commits / orgs 端点直接取得，无需 code search 交叉验证。
21. **时间戳口径**：`pushed_at` 是 GitHub 的仓库 push 时间（含 branch push），`commits[0].commit.author.date` 是最新 commit 的作者日期，二者可能不同（如 `terminal-bench-2` 两者同为 2026-04-30，`terminal-bench` 为 2026-11-19 / 2026-11-18）。本文表格统一用 `pushed_at`。

---

## 证据表

| # | 结论 | 证据 | 来源等级 |
|---|---|---|---|
| E1 | `harbor-framework` 组织共 21 个公开仓库 | `gh api orgs/harbor-framework/repos --paginate --jq '.[]\|.full_name'` 返回 21 行 | 官方一手（GitHub API） |
| E2 | `harbor` 7224★ / 2026-11-19 / Apache-2.0 / live | `gh api repos/harbor-framework/harbor --jq '[.full_name,.stargazers_count,.pushed_at[0:10],.archived,.license.spdx_id] \| join(" \| ")'` | 官方一手 |
| E3 | `terminal-bench` 1088★ / 2026-11-19 / Apache-2.0 | 同上，`repos/harbor-framework/terminal-bench` | 官方一手 |
| E4 | `terminal-bench-1` 2623★ / 2026-07-11 / Apache-2.0 / live | 同上 | 官方一手 |
| E5 | `terminal-bench-2` 450★ / 2026-04-30 / Apache-2.0 | 同上 | 官方一手 |
| E6 | `terminal-bench-2-1` 140★ / 2026-11-05 / Apache-2.0 | 同上 | 官方一手 |
| E7 | `terminal-bench-science` 944★ / 2026-11-19 / Apache-2.0 | 同上；description "Terminal-Bench-Science: Evaluating AI agents on research workflows across scientific domains" | 官方一手 |
| E8 | `harbor-index` 49★ / 2026-08-03 / **无 license 对象** | 同上，`.license` 为 null | 官方一手 |
| E9 | `awesome-harbor` 62★ / 2026-05-29 / **无 license 对象** / description "A curated list of awesome Harbor ecosystem projects" | 同上 | 官方一手 |
| E10 | `harbor-client` 1★ / 2026-11-19 / Apache-2.0 | 同上 | 官方一手 |
| E11 | `adapters` 14★ / 2026-11-17 / Apache-2.0 | 同上 | 官方一手 |
| E12 | `harbor-cookbook` 281★ / 2026-10-31 / Apache-2.0 | 同上 | 官方一手 |
| E13 | `skills` 15★ / 2026-05-12 / Apache-2.0 | 同上 | 官方一手 |
| E14 | `harbor-adapters-experiments` 9★ / 2026-06-28 / Apache-2.0 | 同上 | 官方一手 |
| E15 | `harbor-datasets` 47★ / 2026-05-16 / **无 license 对象** | 同上 | 官方一手 |
| E85 | `harbor-datasets` 含 **102** 个已移植基准目录，README 仅 17 字节存根 | `gh api repos/harbor-framework/harbor-datasets/contents/datasets --jq '[.[]\|select(.type=="dir")]\|length'` → 102；README raw 内容 = `# harbor-datasets` | 官方一手 |
| E16 | `terminal-bench-challenges` 26★ / 2026-11-06 / **无 license 对象** | 同上 | 官方一手 |
| E17 | `terminal-bench-website` 6★ / 2026-11-16 / **无 license 对象** | 同上 | 官方一手 |
| E18 | `terminal-bench-docs` 10★ / 2026-08-19 / **无 license 对象** | 同上 | 官方一手 |
| E19 | `terminal-bench-science-docs` 1★ / 2026-08-26 / **无 license 对象** | 同上 | 官方一手 |
| E20 | `docs` **ARCHIVED** / 0★ / 2026-06-03 / MIT | 同上，`.archived == true` | 官方一手 |
| E21 | `harbor-docs` **ARCHIVED** / 5★ / 2026-03-31 | 同上 | 官方一手 |
| E22 | `benchmark-template` **ARCHIVED** / 18★ / 2026-08-06 | 同上 | 官方一手 |
| E23 | `laude-institute/terminal-bench` 302 → `harbor-framework/terminal-bench-1` | `gh api repos/laude-institute/terminal-bench --jq .full_name` | 官方一手 |
| E24 | `harbor-framework/frontier-bench` 302 → `harbor-framework/terminal-bench` | `gh api repos/harbor-framework/frontier-bench --jq .full_name` | 官方一手 |
| E25 | `harbor-framework/benchmark` 302 → `harbor-framework/benchmark-template`（已归档） | `gh api repos/harbor-framework/benchmark --jq .full_name` | 官方一手 |
| E26 | `laude-institute/harbor` / `terminal-bench-2` / `harbor-datasets` 均 302 到 `harbor-framework/*` | 同上三次调用 | 官方一手 |
| E27 | `laude-institute` 余下 8 仓：6 归档 + `headlong`(1277★) / `rev-engine`(29★) live | `gh api orgs/laude-institute/repos` | 官方一手 |
| E28 | terminal-bench release 仅 3 个：`v3.0.0`(2026-07-23) / `v4.0.0`(2026-08-26) / `v4.1.0`(2026-11-03) | `gh api repos/harbor-framework/terminal-bench/releases?per_page=100` | 官方一手 |
| E29 | v3.0.0 = 74 任务 | release body "Added initial 74 Tasks" + `contents/tasks?ref=v3.0.0` 计数 = 74 | 官方一手 |
| E30 | v4.0.0 移除 8 个任务（饱和、拒答、公开解答、未解决的质量或平台兼容性问题各 2） | release body 的 "Tasks removed:" 列表（cli-2ph-simplex 等）+ [4.0 公告](https://www.tbench.ai/news/terminal-bench-4-0) 的分类说明 | 官方一手 |
| E31 | v4.0.0 = 66 任务 | `contents/tasks?ref=v4.0.0` 计数 = 66 | 官方一手 |
| E32 | v4.1.0「Tasks added or removed: None. Tasks modified (66)」+ CPU-only 数据集 63 任务 | `gh api repos/harbor-framework/terminal-bench/releases/tags/v4.1.0 --jq .body` | 官方一手 |
| E33 | v4.1.0 = 66 任务 | `contents/tasks?ref=v4.1.0` 计数 = 66 | 官方一手 |
| E34 | terminal-bench tag 只有 v3.0.0 / v4.0.0 / v4.1.0 | `gh api repos/harbor-framework/terminal-bench/tags` | 官方一手 |
| E35 | harbor release 覆盖 v0.3.0 → v0.26.0，共 28 个 | `gh api repos/harbor-framework/harbor/releases?per_page=100`；最新 v0.26.0 = 2026-11-13 | 官方一手 |
| E36 | harbor 缺 v0.1.0 / v0.2.0 / v0.10-v0.12 / v0.19 release | 同上 release 列表 | 官方一手 |
| E37 | terminal-bench-science 唯一 release `v0.1.0` (2026-08-26) | `gh api repos/harbor-framework/terminal-bench-science/releases` | 官方一手 |
| E38 | harbor-index release 命名 `harbor-index-1.1` … `-1.4`（2026-07-11 → 2026-07-28） | `gh api repos/harbor-framework/harbor-index/releases` | 官方一手 |
| E39 | harbor-client release `v0.1.0`(2026-11-18) / `v0.2.0`(2026-11-19) | `gh api repos/harbor-framework/harbor-client/releases` | 官方一手 |
| E40 | 数据集仓最后提交：tb-1 = 2026-07-11；tb-2 = 2026-04-30；tb-2-1 = 2026-11-05 | `gh api repos/{repo}/commits --jq '.[0].commit.author.date[0:10]'` | 官方一手 |
| E41 | docs 站索引 `llms.txt` 共 105 个页面 + openapi + Hub/Discord | `https://docs.harborframework.com/llms.txt`（117 行，HTTP 200） | 官方一手（官方文档站） |
| E42 | verifier 入口与 reward 契约：`tests/test.sh`，产出 `/logs/verifier/reward.txt` 或 `.json`，同存时优先 json | https://docs.harborframework.com/tasks/verifier.md | 官方一手 |
| E43 | regrade 三条前置条件 + 「no agent credentials, no new agent cost」 | https://docs.harborframework.com/jobs/regrade.md | 官方一手 |
| E44 | artifact 对象字段 `source`/`destination`/`exclude`/`service`；manifest 状态 `ok`/`empty`/`failed`/`skipped` | https://docs.harborframework.com/jobs/artifact-collection.md | 官方一手 |
| E45 | 默认聚合：均值 + 缺失计 0；`metric.py` 接受 `-i`/`-o` | https://docs.harborframework.com/datasets/metrics.md | 官方一手 |
| E46 | 47 个内置 agent 名单 + 12 项能力矩阵 | https://docs.harborframework.com/agents/pre-integrated-agents.md | 官方一手 |
| E47 | sandbox 本地 5 个 / 远端约 30 个 + 能力矩阵 | https://docs.harborframework.com/sandboxes/pre-integrated-sandboxes.md | 官方一手 |
| E48 | leaderboard schema 字段全集 + 「Hub 不代算分」 | https://docs.harborframework.com/harbor-hub/leaderboards.md | 官方一手 |
| E49 | RewardKit 五条设计原则原文 | https://docs.harborframework.com/rewardkit/motivation-and-design.md | 官方一手 |
| E50 | judge TOML 完整字段参考（`[judge]` 18 项 + `[[criterion]]` 11 项） | https://docs.harborframework.com/rewardkit/judge-criteria.md | 官方一手 |
| E51 | reward hacking 三分类（Tampering/Cheating/Loopholes） | https://docs.harborframework.com/news/reward-hacking.md | 官方一手 |
| E52 | `harbor lint` 7 条规则名 | https://docs.harborframework.com/news/reward-hacking.md | 官方一手 |
| E53 | 独立 verifier 沙箱的收益与代价 | https://docs.harborframework.com/news/separate-verifier-sandboxes.md | 官方一手 |
| E54 | 共享默认私有 + 2.1 榜由 Hub upload 构建 | https://docs.harborframework.com/news/job-result-sharing.md | 官方一手 |
| E55 | news 时间线：TB3.0 (formerly Frontier-Bench) 2026-07-23、Harbor-Index 2026-07-08、TB4.0 2026-08-29、TB-Science 2026-08-27、TB4.1 2026-11-09、Harbor Server 2026-11-13 | https://docs.harborframework.com/news.md | 官方一手 |
| E56 | 错误分类唯一真源 `error_policy.py`；三字段语义 | https://docs.harborframework.com/jobs/error-classification.md | 官方一手 |
| E57 | harbor v0.26.0 changelog（含 breaking changes 与 `harbor serve`） | https://docs.harborframework.com/changelog.md | 官方一手 |
| E58 | 任务准入六条原文 | TB `docs/task-guidelines.md:1-8` | 官方一手（GitHub raw） |
| E59 | 「本科生几天能解 = 太简单」原文 | TB `docs/task-guidelines.md:37` | 官方一手 |
| E60 | LLM-as-a-judge 罕见例外条款 | TB `docs/task-guidelines.md:15` | 官方一手 |
| E61 | 「Only Ryan or Ivan can merge to main」 | TB `docs/REVIEWING.md:52` | 官方一手 |
| E62 | 自动 rubric 评审 = 30 criteria，「first-pass signal, not a final judgment」 | TB `docs/REVIEWING.md:9` | 官方一手 |
| E63 | separate verifier 的 5 条机械检查 + 「Shared mode is leaky」 | TB `docs/TASK_REVIEW_AUTOMATION.md:212-222` | 官方一手 |
| E64 | 「the RDI/Berkeley 89/89 attack on TB2」 | TB `docs/TASK_REVIEW_AUTOMATION.md:228` | 官方一手 |
| E65 | pytest 统一锁 `pytest==9.1.1` / `pytest-json-ctrf==0.5.2` | TB `docs/TASK_REVIEW_AUTOMATION.md:242` | 官方一手 |
| E66 | 11 条评审流水线与 6 条 PR 命令权限表 | TB `docs/TASK_REVIEW_AUTOMATION.md:23-38`, `:369-373` | 官方一手 |
| E67 | 任务版本语义化 → 榜单复用规则（Major/Minor/Patch） | TB `CONTRIBUTING.md:378-382` | 官方一手 |
| E68 | instruction.md 结尾固定句（CI 强制 `check-instruction-suffix`） | TB `CONTRIBUTING.md:258-264` | 官方一手 |
| E69 | 「Terminal-Bench is an open-internet benchmark … disabling network access is not a valid way to make a task difficult」 | TB `CONTRIBUTING.md:36` | 官方一手 |
| E70 | 「well beyond the current frontier of model ability」 | TB `CONTRIBUTING.md:32` | 官方一手 |
| E71 | 赞助商 / 数据伙伴 / 托管方声明 | TB `README.md:246-248` | 官方一手 |
| E72 | 领导层 / 高级评审 / 顾问 / Task Authors / Reviewers 名单 | TB `README.md` §Contributors 表 | 官方一手 |
| E73 | TAXONOMY 7 个一级领域 + 每域 senior_reviewer | TB `docs/TAXONOMY.yaml`（本地读取计数=7） | 官方一手 |
| E74 | TB 4.0 榜定义 schema（`name: 4-0-0`、`dataset_version_refs: ['4']`、`rank_by: metrics.accuracy desc`、metrics 含 `accuracy` / `accuracy_ci95_half_width` / `total_tokens` / `total_cost_usd` / `n_trials` / `pass_at_2..5`） | TB `leaderboard/leaderboard.yaml` | 官方一手 |
| E75 | TB2.1 = 26 个任务被修，且部分改动直接取自 Z.ai 的 TB 2.0 Verified | TB2.1 `README.md:5` | 官方一手 |
| E76 | TB2.1 提交要求：每任务 ≥5 trial + 公开上传 + PR；且社区提交当时已关闭 | TB2.1 `README.md:28-45` | 官方一手 |
| E77 | Harbor 重写 TB harness 的自述 + 迁移路径（`BaseInstalledAgent`/`BaseAgent`） | TB2 `README.md` §Migrating / §FAQ | 官方一手 |
| E78 | awesome-harbor 收录 28 个项目，分 4 类 | `gh api repos/harbor-framework/awesome-harbor/contents/README.md`（4401 bytes） | 官方一手（官方 curated list） |
| E79 | Harbor 贡献黄金法则 + 「Docs, PR descriptions, issues, and comments should be written by a human with AI assistance」+ RFC 要求 | HF 仓 `CONTRIBUTING.md` | 官方一手 |
| E80 | TB-Science 定位「open academic collaboration hosted by Stanford University and the Laude Institute」+ 96 任务 + 研究伙伴名单 | TB-Science `README.md:25`, `:50`, `:333`, `:347` | 官方一手 |
| E81 | Harbor Index 自述「80-task … distilled from more than 6,000 candidate tasks」 | `harbor-index` `README.md:3-5` | 官方一手 |
| E82 | Terminal-Bench Challenges 的定位（单任务、token 密集、程序化验证） | `terminal-bench-challenges` `README.md` §Motivation | 官方一手 |
| E83 | `skills` 仓收录 3 个 skill（harbor-task-creator / harbor-adapter-creator / harbor-cli） | `skills` `README.md` §Skills | 官方一手 |
| E84 | `adapters` 自述：把 SWE-Bench / Aider Polyglot / GPQA / AIME 等 80+ 转成 Harbor task | `adapters` `README.md:14-19` | 官方一手 |
