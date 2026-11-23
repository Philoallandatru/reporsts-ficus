---
type: Concept
title: Terminal-Bench 对 llama.cpp 缓存研究的用途
description: Terminal-Bench 提供公开、版本化的终端任务和独立判分器。对本工作区，它的价值是补充一批可复核的 Agent 工作负载，并用实际任务结果检查缓存改动有没有引入回归。缓存收益仍由固定请求轨迹和同机对照测量。
tags:
- agents
- benchmark
- swe-bench
sources:
- c:/Users/Administrator/Documents/Code/my-code/lm-llama/research/agent-bench-ecosystem/07-implications-for-this-workspace.md
createdAt: '2026-11-23'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# Terminal-Bench 对 llama.cpp 缓存研究的用途

Terminal-Bench 提供公开、版本化的终端任务和独立判分器。对本工作区，它的价值是补充一批可复核的 Agent 工作负载，并用实际任务结果检查缓存改动有没有引入回归。缓存收益仍由固定请求轨迹和同机对照测量。

本文给出的是可执行方案，不是原则清单：先判断 Terminal-Bench 4.1 在本机是否适用，再给出接线、容量设计和 Stop/Go 门槛。

## 三个问题对应三种证据

| 问题 | 实验 | 如何下结论 |
|---|---|---|
| 恢复的状态是否正确 | 用 `prefix-state-bench` 对照冷计算和恢复后的 logits，保留 hybrid/recurrent 检查点 | 结论限定在所测模型、引擎和恢复路径 |
| 缓存是否让同一批请求更快 | 用 `pi-cache-bench` 的录制与回放方法，保留请求体、顺序与会话依赖，只切换缓存配置 | 报告 TTFT、实际 prefill token、缓存命中、请求耗时和回放总耗时 |
| 真实 Agent 是否仍能完成任务 | 选固定版本的公开任务，让同一 Agent 在各配置下独立完成，由任务自带 verifier 判分 | 报告每项结果、失败类型和真实任务墙钟时间。小样本可暴露明显回归，无法证明通过率等效 |

现有 Pi 试验覆盖 2 个 SWE-bench Lite dev 任务和 21 个关联请求。请求回放不会重新执行工具，回放总耗时只描述固定输入轨迹。原生双槽位校准优于单槽位加 RAM 的配置，正式比较应纳入调优后的原生槽位基线。见 Pi 实验协议 (`../pi-cache-bench/README.md`)、前缀状态实验 (`../prefix-state-bench/README.md`)和三级缓存设计 (`../llamacpp-tiered-cache-evaluation-and-implementation.md`)。

## 先判断 Terminal-Bench 4.1 在本机是否适用

这一步不能跳过。官方 4.1 榜的尾部数据说明，本地小模型在这个任务集上很可能整体接近零。

| 榜内模型 | Agent | 4.1 通过率 |
|---|---|---:|
| Qwen3.8-Max-0902 | Claude Code | 26.97% |
| MiMo V2.6 Pro | mini-swe-agent | 26.97% |
| MiMo V2.6 Flash | mini-swe-agent | 16.06% |
| Inkling Small 2 | mini-swe-agent | 13.03% |
| Inkling Small | mini-swe-agent | 0.91% |
| Nemotron 3.5 Super VL | mini-swe-agent | 0.30% |
| Inkling | mini-swe-agent | 0.00% |

本机是 `Qwen3.8-27B-UD-IQ3_XXS`（IQ3 量化、24,576 token 上下文、单张 RTX 5080）。它的能力与上表最小的一档不在一个量级，24K 上下文也低于多数任务的工作量。**如果候选任务全部 0 分（地板效应），缓存引入的功能回归就测不出来**——0% 到 0% 没有信息量。

因此采用顺序是：先在候选任务上跑通 oracle 与 Agent，**连续两题全 0 才降级**。降级选项按成本从低到高：扩充现有 SWE-bench Lite 任务数（无需 Docker，已在本机跑通）、Terminal-Bench 2.1 的 89 题子集（难度低于 4.x）、TerminalWorld 的日常终端任务。

### 候选任务（v4.1.0 实测）

从 66 题中筛出低资源、软件与数据处理向的题。资源取自各题 `task.toml` 的 `[environment]`，题面长度是 `instruction.md` 的字符数，可作上下文规模的粗略上限。

| 任务 | CPU | 内存 | GPU | Agent 超时 | 题面字符 |
|---|---:|---:|---:|---:|---:|
| `mvcc-lsm-compaction` | 2 | 4096 MiB | 0 | 28800 s | 846 |
| `heat-pump-warranty` | 2 | 4096 MiB | 0 | 28800 s | 574 |
| `session-window-debug` | 2 | 4096 MiB | 0 | 28800 s | 1003 |
| `nextjs-performance` | 2 | 4096 MiB | 0 | 28800 s | 1068 |
| `freight-dispatch-shift` | 2 | 4096 MiB | 0 | 28800 s | 1634 |
| `production-planning` | 2 | 4096 MiB | 0 | 28800 s | 2909 |
| `wal-recovery-ordering` | 2 | 4096 MiB | 0 | 28800 s | 3345 |
| `legacy-utility-triage` | 2 | 8192 MiB | 0 | 28800 s | 566 |
| `payments-pipeline-fix` | 4 | 8192 MiB | 0 | 28800 s | 483 |
| `data-anonymization` | 2 | 8192 MiB | 0 | 28800 s | 1060 |
| `intrastat-meldung` | 2 | 8192 MiB | 0 | 28800 s | 1710 |

`mvcc-lsm-compaction`、`wal-recovery-ordering` 与本工作区的 KV/LSM 主题最接近，优先试这三题。**官方 Agent 超时是 28800 s（8 小时），对本地实验没有意义**，须自行设上限并在报告里标明这已偏离官方协议。

## 选哪个基准下载到本地

「最权威」和「最适合本机部署测试」不是一回事。前者是 TB 4.1，后者要看五条判据：

1. **时限与本地推理速度是否相容**——本地 27B IQ3 在非独占 5080 上比云端前沿模型慢一到两个数量级，时限设短会把「能做完」变成「超时截断」。
2. **本机模型是否有解题信号**——全 0 分的地板效应下，功能回归测不出来。
3. **判分是否需要外部 API**——LLM judge 引入成本与噪声，破坏严格对照。
4. **轨迹形态是否产生前缀重叠**——缓存收益的前提是 agent 反复读写同一批文件。
5. **部署摩擦**——资产是否预构建、是否需要额外下载、镜像大小。

按这五条排序：

| 基准 | 形态与规模 | 本机适配 | 判断 |
|---|---|---|---|
| **TUA-Bench** | Harbor 原生，`tasks/` 下 **120** 个任务目录；许可 **CC BY-NC 4.0**；官网 tuabench.ai | 时限 **150–2400 s**（TB 4.1 是 28800 s）；纯执行式判分，容器内 verifier 查最终状态，**不需要 judge API**；任务以读写表格、文档、EPW 能源模型、PARQUET 等文件为主，前缀重叠高 | **首选下载目标** |
| **SWE-bench Lite** | 300 实例，官方 test patch 判分，MIT | 本工作区**已在用**：两个 marshmallow 任务独立评分 76/77 与 25/25，本地 27B 有真实解题信号；`pi-cache-bench` 已有录制与回放链路 | **保留为回归护栏**，但 issue→patch 轨迹短且同质，不适合当 L2 容量实验的主要负载 |
| **TerminalWorld** | `terminalworld/TerminalWorld`（NeurIPS 2026 Evals & Datasets）；从 80,870 段真实终端录制自动生成 **1,530** 题，18 类；数据集在 HF `terminalworld/TerminalWorld` | 任务形态最贴近真实日常终端操作（与 TB 相关性仅 r=0.20，测的是另一件事）；但仓库只提供**数据引擎**（`data_retrieval` / `environment_building` / `task_synthesis` / `test_generation`），任务本身在 HF，部署路径比 TUA-Bench 重 | **扩量阶段的次选**，先摸清资产与镜像获取方式 |
| **Terminal-Bench 4.1**（含 63 题 CPU-only） | 66 题，Harbor 官方任务集，Apache-2.0 | 官方榜尾部模型通过率已在 0.00%–26.97%，本机 27B IQ3 有**地板效应**风险；Agent 时限 28800 s 对本地无意义 | **不建议作为本机主基准**，保留作外部锚点与口径参照 |
| **Harbor Index** | 80 题，从 20+ 家基准蒸馏；`harbor-framework/harbor-index` | 部分任务用 **LLM judge 集成**（需 judge API 成本）；官方把 agent 预算从统一 3 小时改为 task-specific | **不适合做严格对照** |

### TUA-Bench 的本地部署步骤

任务在仓库里（不是需要额外拉取的远程数据集），资产由脚本下载：

```bash
git clone https://github.com/facebookresearch/TUA-Bench.git
cd TUA-Bench
uv run setup-env            # 下载/生成任务资产；--reset 可清回干净状态
harbor run -p tasks -a oracle -n 2      # 先验证任务可解、环境可用
harbor run -p tasks -a pi -m <本地模型端点> -o jobs/local-run --yes
```

三点提示：`tasks/` 下是 120 个任务目录，另有 `task_name_mapping.txt`；任务用 Harbor 格式，与 TB 4.x 同源，所以 [02](02-task-and-verifier.md) 里那套 verifier 契约、regrade 规则和 [附录](appendix-evidence.md) 的来源分级都直接适用；**用 `pi` 而不是官方示例里的 `terminus-2`**，才能和现有 `pi-cache-bench` 的 Agent、录制格式对齐。许可为 CC BY-NC（非商业），本工作区的研究用途不受限，但若后续要用于商业部署必须换基准。

未核实：`pi` 适配器能否直接指向本机 `llama-server` 的 OpenAI 兼容端点（需在 Harbor 里配置 base URL），以及 120 题各自的实际上下文长度是否都在本机 24K 之内。

## 接线：Harbor → 录制代理 → llama-server

本机当前状态（2026-11-19 实测）：Docker Desktop 已安装但 Linux engine 未连；`uv` 0.11.14；PATH 中无 `harbor`。

接线前必须先解决三个事实性问题：

- **`uv` 版本不满足要求。** Harbor 源码的依赖锁定要求 `uv 0.13.5+`，本机 0.11.14 低于下限。先升级 `uv`，否则安装会失败或行为不一致。
- **Harbor 内建了 `pi` 适配器。** `harbor-framework/harbor` 的 `src/harbor/agents/installed/` 下有 `pi.py`、`mini_swe_agent.py`、`claude_code.py`、`codex.py`、`swe_agent.py`、`openhands.py`、`goose.py` 等。本工作区 `pi-cache-bench` 用的正是 `@earendil-works/pi-coding-agent`，**同一 Agent 可直接用于录制阶段**，省掉一层适配。
- **Agent 需要访问宿主的 `llama-server`。** `harbor run` 有 `--allow-agent-host` 选项；容器内访问宿主需用 `host.docker.internal`，且 `llama-server` 必须监听容器可达的地址，并确认该地址不被本地防火墙挡住。

最小冒烟顺序：装 Harbor（`uv tool install harbor`）→ 启动 Docker Desktop → 选一题跑 `oracle`（验证任务可解、环境可用）→ 选一题跑 `pi`（Agent 能连上宿主模型）→ 再接录流代理。**前两步失败就不要继续**，它们分别决定环境和任务是否可用。

## 容量设计：怎样才会真的触发 L1 与 L2

这是本工作区最容易走空的一段。**单会话、单槽位的运行全程命中 L0，不会产生任何 L1 淘汰或 L2 读回**，因此测不出 SSD 层的价值。

本机模型的尺寸公式（来自三级缓存设计 §7 (`../llamacpp-tiered-cache-evaluation-and-implementation.md`)）：

```text
固定前缀边界完整快照 ≈ N × 18 KiB + 149.626 MiB + metadata
加 C 个历史检查点      ≈ N × 18 KiB + (C+1) × 149.626 MiB + metadata
```

8K tokens 边界约 294 MiB；带 4 个历史检查点约 892 MiB。实测 `pi-cache-bench` 的 2 会话 21 请求，RAM prompt cache 条目峰值约 **1.47 GiB**（日志报告值），低于 4096 MiB 配额——**所以现有实验根本没有触及 RAM 淘汰，更谈不上 SSD**。

触发条件是两条同时成立：并发/交错会话数 **K 大于槽位数 `np`**，且 **K × 单会话状态字节超过 L1 预算**。落到本机：

| L1 预算 | 需要的交错轨迹数（按每条约 0.7 GiB 估） | 备注 |
|---|---:|---|
| 4096 MiB（现用） | 至少 6 条 | 需把 `pi-cache-bench` 从 2 任务扩到 6 条以上同规模轨迹 |
| 2048 MiB | 至少 3 条 | 扩容成本最低，且不改变被测模型 |
| 1024 MiB | 至少 2 条 | 现有 2 任务即可开始，但额度偏紧，波动大 |

更省事的做法是**压低 L1 配额**而不是加轨迹数：把 `--cache-ram` 降到 1–2 GiB，让同样的 2–3 条轨迹就能把缓存顶出。注意 `--cache-ram` 的单位是 MiB，且配额只约束 RAM prompt cache 条目，不等于进程 RSS。

无论走哪条路，都要能从日志里看到 **`L0 miss → L1 miss → L2 hit`** 的完整路径。只看到 L1 hit 说明还没到 SSD。

## 两阶段隔离

本机只有一台非独占的 Windows 工作站。Docker/WSL2 里的容器构建会同时抢宿主机 RAM（`vmmem`）、CPU 和 SSD I/O，污染 L1 配额与 L2 计时。因此分成两阶段：

1. **阶段一（开 Docker/Harbor）**：只做两件事——live 任务正确性验收，以及录制 HTTP/SSE 轨迹。不在本阶段测任何缓存时间指标。
2. **阶段二（关掉 Docker/WSL2）**：在干净宿主机上跑固定轨迹的多会话回放，测 TTFT、实际 prefill、命中率和 L2 读回延迟。

两个阶段都要记录宿主机当时的负载背景（GPU 占用、其他应用），本机不是专用性能测试机。

## 实验方案

1. **先校准环境。** 固定数据集版本、Harbor 版本、任务清单、模型与量化、引擎提交、Agent 与工具链、资源及超时。对选定任务跑 oracle 检查任务可解和环境可用。官方 README 的五次 oracle 是环境校准示例，榜单每任务至少五次 Agent trial 是另一个要求。见 [官方方法学](05-methodology-and-audits.md)和[官方仓库](https://github.com/harbor-framework/terminal-bench#running-the-benchmark)。
2. **先测轨迹再决定工作负载。** 记录轮数、最长共同前缀、跨会话重访间隔和可恢复状态的累计字节数，避免从题名或任务时长直接推断前缀重叠。把选择条件、任务 ID 和未通过环境校准的任务写入报告。
3. **成对回放比较缓存。** 固定硬件、模型、引擎和服务预算，保留现有 `no_cache` 组作为机制诊断对照，以调优后的原生配置衡量真实增益。不同配置使用相同的冷启动和预热时点，按轮切换执行顺序，报告逐轨迹差值以及 TTFT 和 prefill 分布。独立的 live 运行记录任务结果和真实墙钟时间。
4. **专门设计 L2 容量实验。** 按上节的触发条件配置 K 与 L1 预算，比较相同 RAM 上限下有无 L2 的配置。验证基线确实发生淘汰，L2 确实恢复了对应对象。计入落盘、读回、队列争用和首次保存成本。公开任务的轨迹可作输入，多会话交错和 RAM 预算仍须单独设计。见三级缓存设计 §4 (`../llamacpp-tiered-cache-evaluation-and-implementation.md#4-第二个实验证明新增-ssd-层的增量价值`)。

## 阶段与 Stop/Go 门槛

| 阶段 | 产出 | 继续的条件 | 止损条件 |
|---|---|---|---|
| 0 环境 | Docker 可用、Harbor 装好、oracle 通过 | 至少 1 题 oracle 通过 | Docker 或 `uv` 装不上 → 停在阶段一 |
| 1 轨迹 | 一题的完整 HTTP/SSE 录制 + 任务结果 | Agent 能连上宿主模型且任务被判分 | 连续 2 题全 0 → 降级到 SWE-bench Lite / TB 2.1 / TerminalWorld |
| 2 容量 | 多会话回放中出现 `L0 miss → L1 miss → L2 hit` | 日志能看到完整回落路径 | 只能稳定看到 L1 hit → 先压低 L1 配额或加轨迹数，仍不出现则 L2 收益无法在本机证明 |
| 3 验收 | 缓存组 vs 对照组的任务结果差异 | 任务结果无回归 | 出现回归 → 先查状态恢复正确性，不查缓存收益 |

**时间预算**：官方论文记录单题最长约 2 小时、近 1 亿 token。本机 27B IQ3 在非独占 5080 上更慢，每题应先设 20–30 分钟上限，超时即记为失败。阶段 0 与阶段 1 应在半天内完成，否则说明接线方案有问题。

## 如何报告

报告把任务成功率、Agent 真实任务耗时、固定轨迹回放性能和 Prefix State Blob 恢复正确性作为独立观察值。附任务与轨迹标识、引擎与模型配置、预热与资源限制、逐次结果和失败记录。若只跑固定子集，注明本地子集、任务数和每题试次数。若采用同一任务集的不同 Agent 配置，需要重新说明比较对象。若自行缩短了 Agent 超时或改了资源上限，须明确标出——这些是偏离官方协议的地方。第三方审计对 4.0 的结论及其对 4.1 的适用性见[方法学篇](05-methodology-and-audits.md#44-第三方审计三家结论各自独立)。

## 本机探测与验证边界

2026-11-19 的本机探测确认 Docker CLI 存在，但当时无法连接 Docker Desktop 的 Linux engine。WSL 默认发行版为 Ubuntu-24.04，默认版本为 2，uv 0.11.14，当前 PowerShell 的 PATH 中未找到 `harbor`。本次没有安装 Harbor、启动容器或执行基准，本地 Agent 访问 llama-server 的端到端链路尚未验证。63 题 CPU-only 变体约束的是**任务环境**，本地 GGUF 推理仍会使用相同的推理硬件。见 [4.1 发行说明](https://github.com/harbor-framework/terminal-bench/releases/tag/v4.1.0)。

## 未核实与存疑

1. **候选任务能否被本地模型解出，未实测。** 上表只给了资源与题面规模，实际通过率未知，需阶段 1 验证。
2. **24K 上下文是否够用，未核算。** 题面字符数只是题面本身，agent 轨迹会读文件、跑命令，实际上下文占用远大于题面。需要在阶段 1 从录制的请求体里读 `prompt_tokens` 分布来确认。
3. **`host.docker.internal` 到 `llama-server` 的连通性未验证**，包括监听地址与本地防火墙。
4. **每条轨迹 0.7 GiB 是按现有 2 任务实测值外推的**，换任务集后需重测。
5. **官方 8 小时 Agent 超时下的行为特征不适用于本机**，缩短超时可能改变任务结果（有的任务需要长时间运行才能通过验证）。
6. **TB 4.1 在 63 题 CPU-only 变体上的行为是否与全量集一致，未核实**；该变体的任务构成与全量不同。

## 证据表

| 结论 | 证据 | 来源等级 |
|---|---|---|
| 4.1 榜尾部模型通过率 0.00%–26.97% | Harbor Hub `4-1-0` API 逐行读取（2026-11-19） | 官方一手 |
| 候选任务 CPU / 内存 / GPU / Agent 超时 / 题面长度 | `gh api repos/harbor-framework/terminal-bench/contents/tasks/<task>/task.toml?ref=v4.1.0` 与 `instruction.md` | 官方一手 |
| 全部候选题 Agent 超时为 28800 s | 同上，`[agent] timeout_sec` | 官方一手 |
| Harbor 内建 pi / mini-swe-agent / claude-code / codex 适配器 | `gh api repos/harbor-framework/harbor/contents/src/harbor/agents/installed` | 官方一手 |
| `--allow-agent-host` 是 Harbor run 选项 | `docs.harborframework.com/jobs/run-a-job.md` | 官方一手 |
| Harbor 依赖要求 `uv 0.13.5+` | `harbor-framework/harbor` `CONTRIBUTING.md` §Source dependency setup | 官方一手 |
| KV 尺寸公式 N × 18 KiB + 149.626 MiB；8K + 4 检查点 ≈ 892 MiB | 本工作区 `research/llamacpp-tiered-cache-evaluation-and-implementation.md` §7 | 本工作区一手 |
| 2 会话 21 请求 RAM 条目峰值 ≈ 1.47 GiB，未触及 4096 MiB 配额 | `research/pi-cache-bench/results/summary.json`、`report.py` 结论段 | 本工作区一手 |
| 官方榜每任务 ≥5 trial、oracle 五次为校准示例 | `terminal-bench` README、2.1 仓 README | 官方一手 |
| 单题最长约 2 小时、近 1 亿 token | TB 2.0 论文 §4.1（arXiv 2601.11868） | 论文自述 |
| 本机 Docker 未连、uv 0.11.14、无 harbor | 2026-11-19 本机命令探测 | 本机实测 |
