---
type: Concept
title: Terminal-Bench 如何出分，又如何演化
description: Terminal-Bench 的分数表示一个 Agent 系统在指定题集、工具、沙箱和预算下完成任务的比例。判断两个分数能否相减，先看求解时看到的题目和环境有没有变，再看验收规则与分母有没有变。4.0
  到 4.1 的存档重评可以观察同一产物
tags:
- agents
- benchmark
- swe-bench
sources:
- c:/Users/Administrator/Documents/Code/my-code/lm-llama/research/agent-bench-ecosystem/08-benchmark-mechanics-and-evolution.md
createdAt: '2026-11-23'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# Terminal-Bench 如何出分，又如何演化

Terminal-Bench 的分数表示一个 Agent 系统在指定题集、工具、沙箱和预算下完成任务的比例。判断两个分数能否相减，先看求解时看到的题目和环境有没有变，再看验收规则与分母有没有变。4.0 到 4.1 的存档重评可以观察同一产物被判得有何不同。2.1 到 3.0 换了大部分任务，跨版分差反映的是两套测试条件下的表现。

## 一道题经过哪些环节

| 环节 | 4.1 的实际合同 | 最容易改变结论的地方 |
|---|---|---|
| 固定起点 | `instruction.md` 定义目标。`task.toml` 记录资源、时限与要交接的产物。环境镜像提供初始文件和工具 | 同一镜像标签可能随时间指向不同内容。本地硬上限与云平台的资源保障语义也可能不同 |
| Agent 求解 | 每个 trial 从任务初态开始，Agent 多轮调用模型和工具，按配置结束或超时 | Agent 版本、工具接口、推理预算、自动重试和最大输出量都会影响最终产物 |
| 交接 | Harbor 将声明的 artifacts 交给独立 verifier 沙箱，保留原始结果与必要元数据 | 文件容易归档，运行中的服务需要快照或由 verifier 重建。采集不全会让过去结果无法重评 |
| 验收 | verifier 执行程序化检查，输出 reward。需要执行候选程序时，候选程序和可信断言应处于不同权限边界 | 测试漏掉错误解会产生假阳性，测试绑定某个实现方式会产生假阴性。独立沙箱改善评分隔离，对测试覆盖率还要另行核验 |
| 聚合 | 按所选口径汇总 trial，保留超时、基础设施故障、验收失败和取消资格的记录 | Harbor Job 的默认均值与 Terminal-Bench 榜单可以对同一批传入记录给出不同数字 |

在 `wal-recovery-ordering` 这道数据库题里，Agent 交付应用工作树。verifier 在新环境启动候选程序，采集操作分阶段的结果，由外侧测试判断恢复、顺序和并发行为。候选正常跑完但断言失败，可记录一个有效的 `0`。评分设施本身出错时，可没有有效 reward。这两个状态在排障时必须能区分。以 CAD 题为例，验收应检查形状与尺寸，只要题面允许，挤出草图和直接创建 3D 实体都应能通过。4.1 修复的 `freecad-platform-drawing` 正是后者原先被误拒的案例。 [任务结构与判分](02-task-and-verifier.md) · [WAL 题的 4.1 测试入口](https://github.com/harbor-framework/terminal-bench/blob/v4.1.0/tasks/wal-recovery-ordering/tests/test.sh) · [4.1 修订说明](https://www.tbench.ai/news/terminal-bench-4-1)

质量门槛也要分层读。Oracle 通过证明参考解可行，no-op 失败证明初态无法直接过关。两个检查都通过时，仍需独立的合法解法和接近验收边界的错误产物来检验错判。常规 Agent 试跑还能暴露预算和依赖问题。模型辅助审阅任务、事后检查轨迹和 verifier 给最终结果打分，是三种不同用途。 [官方题目审阅流程](https://github.com/harbor-framework/terminal-bench/blob/main/docs/REVIEWING.md) · [题目验收规范](https://github.com/harbor-framework/terminal-bench/blob/main/docs/task-guidelines.md)

## 分数与区间怎样读

**先固定分母。** 4.1 榜单源码对纳入统计的 trial 使用 `reward > 0` 判成功。无分和被取消资格的 trial 按失败计。已核对的 Harbor 默认 Job 路径先筛 `reward_valid`，再计算均值。假设同一批记录为 `1、0、无有效分`，前者得到 `1/3`，后者得到 `1/2`。引用数字时写清哪一条路径，还要披露基础设施失败、重试和替补是否改变了最终纳入的 trial。 [4.1 榜单源码](https://github.com/harbor-framework/terminal-bench/blob/v4.1.0/leaderboard/src/leaderboard/core/metrics.py#L19-L90) · [Harbor Job 聚合](https://github.com/harbor-framework/harbor/blob/e26966a026f872925979d8479b7ace236b68303f/src/harbor/job.py#L1203-L1227)

**区分一次完成率与多次机会。** 每题五次、66 题共 330 trial 时，一次结果翻转改变 **0.303 个百分点**，整题五次全由失败变成功改变 **1.515 个百分点**。若某题五次里成功一次，对主分贡献的题内成功比例是 20%，该题的 pass@5 却是 100%。各题试次数相同，汇总 trial 的成功率等于逐题成功率的平均值。若题 A 为 5/5、题 B 为 0/10，二者分别得到 33.3% 和 50%，所以不平衡重跑时必须披露两种权重的差别。 [榜单算法及 pass@k](https://github.com/harbor-framework/terminal-bench/blob/v4.1.0/leaderboard/src/leaderboard/core/metrics.py#L24-L74)

**置信区间估计同一批题上的重复波动。** 4.1 榜单先按题算 `p_i(1−p_i)/(k_i−1)`，对所有题求和后除以题数的平方，最后用 `1.96 × 标准误` 作半宽。假设各题估计的 `p_i` 保持稳定，每题从 5 次增到 10 次，半宽理论倍率约为 **0.667**，到 17 次才恰好是 **0.5**。在题内方差分布近似不变、试验独立的条件下，题数翻倍的对应倍率约为 **0.707**。若观测到每题都全过或全挂，公式可能给零半宽，结论仍限于这批题和这套配置。比较同批产物在新旧 verifier 下的差异，应该看逐任务、逐 trial 的配对翻转，两个榜单区间是否重叠只能用来描述现象。 [榜单统计实现](https://github.com/harbor-framework/terminal-bench/blob/v4.1.0/leaderboard/src/leaderboard/core/metrics.py) · [方法学与来源](05-methodology-and-audits.md)

资源也是实验变量。Anthropic 在 TB 2.0 固定模型、Agent 和题集，只改容器资源阈值，最严到不限的设置间分数差达 **6 个百分点**。适量余量可减少基础设施故障，更大的资源预算可能让此前不可行的求解策略变得可行。这个量级只适用于该实验。做横向对照时，需要同时记录实际执行后端、CPU/RAM 保留与硬上限的语义，以及超时、输出上限和并发。 [Anthropic 资源对照](https://www.anthropic.com/research/infrastructure-noise)

## 每一版解决了什么

| 阶段 | 实际变化 | 原有成绩怎样读 |
|---|---|---|
| **1.0 → 2.0** | 从旧终端 harness 迁到 Harbor，强化任务筛选与人工、模型辅助验证；2.0 论文使用 89 道题。Harbor 加入可扩展的沙箱与 Agent 适配 | 数据集和运行框架都变了，迁移适配器以后仍要在 2.0 重跑。 [官方公告](https://www.tbench.ai/news/announcement-2-0) · [2.0 论文](https://arxiv.org/abs/2601.11868) |
| **2.0 → 2.1** | 两个任务仓各 89 个目录，名称完全重合。官方发布公告说修了 28 道，2.1 仓库 README 记 26 道改动，两个来源的计数口径尚未逐条对齐。问题集中在外部依赖漂移、资源不足、题意与测试错位 | 题名不变也可能改变作答条件。官方示例中 Opus 4.6 + Claude Code 从 58.0% 到 70.1%，应读成发布版差异。 [2.1 公告](https://www.tbench.ai/news/terminal-bench-2-1) · [2.1 仓](https://github.com/harbor-framework/terminal-bench-2-1) |
| **2.1 → 3.0** | 3.0 重建难题集，首发 74 题、7 个域。对照 2.1 仓与 3.0 标签，任务目录名只重合 1 个。正式发布已将 Agent 沙箱和 verifier 沙箱分离，引入产物归档、评审流水线和结果迁移 | 3.0 首发报道里 Fable 5 + Claude Code 从 83.8% 降到 33.8%，对应不同任务分布。同一工具链不保证分数接续。 [3.0 公告](https://www.tbench.ai/news/terminal-bench-3-0) · [3.0 任务树](https://github.com/harbor-framework/terminal-bench/tree/v3.0.0/tasks) |
| **3.0 → 4.0** | 74→66，撤 8 题且未加新题。饱和、拒答、有公开解答、未解决的质量或兼容性问题各占 2 题。公告说修复 19 题，并把 Agent 时限统一为八小时、重新校准资源 | 题集和求解预算同时改变。要拆出撤题效应，可以先在旧记录上按保留题重算，再对资源或题面改变的任务做受控重跑。 [4.0 公告](https://www.tbench.ai/news/terminal-bench-4-0) · [4.0 Release](https://github.com/harbor-framework/terminal-bench/releases/tag/v4.0.0) |
| **4.0 → 4.1** | 66 题原样保留，题面文本相同。重点是修 verifier 的误判、隔离候选代码和提高可复现性，新增 63 题 CPU-only 平行数据集 | 公告成绩复用已有轨迹并重评对应产物。CPU-only 使用不同分母，需单独标注。 [4.1 公告](https://www.tbench.ai/news/terminal-bench-4-1) · [4.1 Release](https://github.com/harbor-framework/terminal-bench/releases/tag/v4.1.0) |
| **5.0** | 查阅时 GitHub 里程碑仍开放，无截止日，现行发布版仍为 4.1.0 | 最终任务组成、资源和计分变化以发布版为准。 [5.0 里程碑](https://github.com/harbor-framework/terminal-bench/milestone/3) |

4.1 有一处值得特别核对。将 4.0 和 4.1 的保留任务按 Git blob 逐文件比较，**66 题题面没有变化，66 题的 `tests/` 有变化，63 题的 `environment/` 也有文件变化**。文件变了还要检查行为是否变了。比如 `cad-model` 的 Agent 镜像从可移动的 `python:3.12-slim` 标签变成固定 digest，抽查的 CPU、内存、GPU 和 Agent 时限都相同。这个结果支持将固定依赖视作复现维护，但不能用单题的检查外推 63 题的镜像运行行为。4.1 的重评本身使用旧产物，直接回答 verifier 变化带来的影响。 [4.0 树](https://api.github.com/repos/harbor-framework/terminal-bench/git/trees/v4.0.0?recursive=1) · [4.1 树](https://api.github.com/repos/harbor-framework/terminal-bench/git/trees/v4.1.0?recursive=1) · [CAD 环境 4.0](https://github.com/harbor-framework/terminal-bench/blob/v4.0.0/tasks/cad-model/environment/Dockerfile) · [CAD 环境 4.1](https://github.com/harbor-framework/terminal-bench/blob/v4.1.0/tasks/cad-model/environment/Dockerfile)

重评也比单看榜分提供更多信息。官方公告记录 **11,550 次**历史 trial，初步有 **162 次**翻转，经人工复核保留 **134 次**预期变化。89 次由失败改成成功，45 次由成功改成失败。二者抵消后，这批 trial 的净变化仅 **+0.381 个百分点**，实际改判比例约 **1.16%**。汇总稳定与某些题确有修复可以同时成立。官方对测量差异、重评报错或缺少产物的记录沿用旧分，复核时应保留每条记录的分数来源。 [4.1 公告](https://www.tbench.ai/news/terminal-bench-4-1)

## 演化时如何保持可比

官方的操作顺序是复用、重评、重跑。只改文档或不影响行为的元数据，复用旧记录。只改验收逻辑，且新 verifier 所需产物已归档、版本与路径可以对上，才对旧产物重评。改题面、初始文件、工具或求解预算，会改变 Agent 的选择空间，应重跑受影响的任务。换了题集时，可以同时保留一批固定任务作为长期回归对照，再用滚动任务测前沿能力，两组各报一项成绩。发布时按题标明变更、受影响试次、使用了哪一版 verifier，以及复用或重跑的理由。 [官方 Continuous Benchmarks](https://www.tbench.ai/news/continuous-benchmarks) · [Harbor Regrade 前置条件](https://docs.harborframework.com/jobs/regrade.md)

**对本工作区，值得沿用的是固定输入、独立验收与版本迁移规则。** 用固定轨迹隔离缓存配置对 TTFT、实际 prefill 和墙钟时间的影响，用独立 live trial 检查任务结果。用 `prefix-state-bench` 验证缓存恢复后的 logits。L2 单独让可复用状态工作集超过 L1 RAM 预算，并验证淘汰后的重访确实走到了 SSD 恢复路径。Terminal-Bench 提供任务与可审计的判分，其任务名或时长无法证明前缀复用强度，仍要从实际轨迹测量。 [本工作区应用](07-implications-for-this-workspace.md)

## 发布图案例：Gemini 4 Neon 的跨基准对比

下表转录用户提供的发布图。破折号表示图中未列值。各行分别依照自己的评分口径，不能按领先行数合并成能力排序。DeepMind 的方法 PDF 将来源拆为第三方独立评测、官方榜、厂商自测和其他模型的自报值。多数 Neon 成绩按独立尝试的 pass@1 报告，小型评测可多次运行后平均，具体例外见各项方法。 [Google 发布页](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon/) · [DeepMind 方法与结果 PDF](https://deepmind.google/models/evals-methodology/gemini-4-neon)

| 图中项目与口径 | Gemini 4 Neon | Claude Opus 5.5 | GPT-6.2 Sol |
|---|---:|---:|---:|
| AA Index v5.0.1 | 61 | 59 | 57 |
| Vals Index v2.2 | 70.9% | 70.1% | 66.1% |
| CursorBench 4.1 · Score | 65.4% | 58.1% | — |
| Terminal-Bench 4.1 · Cheating adjusted accuracy | 65.2% | 65.8% | 61.5% |
| FrontierCode 2.0 · Main score | 46.2% | 47.3% | 43.8% |
| SWE-sweep · Provider harness | 39.0% | 10.1% | 8.3% |
| SWE-sweep · Mini-SWE harness | 12.8% | 3.6% | 11.6% |
| AutomationBench | 56.3% | 42.5% | 41.3% |
| Agents' Last Exam v1.1 | 75.8% | 71.6% | 73.0% |
| RiemannBench | 84.0% | 80.0% | 80.0% |
| Terminal-Bench-Science 0.1 | 70.5% | 63.3% | 68.0% |
| HLE-Diamond | 71.3% | 67.9% | 64.0% |
| MKA · Climb WSR | 56.5% | 53.0% | 52.7% |
| Chartography | 73.5% | 66.3% | 75.1% |
| LVBench | 89.0% | 83.7% | 87.6% |
| GraphWalks · 256k–1M，BFS F1 | 95.2% | 66.8% | 80.1% |
| CWE-Bench v2 | 70.7% | 67.1% | 66.0% |
| SEC-bench Pro | 90.5% | — | 88.3% |
| WebExploitBench v1.2 | 51.3% | 37.1% | — |

**Terminal-Bench 这行拼接了两种运行协议。** Neon 的 **65.2%** 来自 Artificial Analysis，使用公开 Antigravity CLI 1.5.9，AA 页面标记 `xhigh`。AA 的 Coding Agent Index v2.1 方法规定 66 题、每题 3 次，汇报平均 pass@1。另两列取自 Terminal-Bench 官方榜。2026-11-19 读取 Harbor Hub `4-1-0`，Opus 5.5 + Claude Code（max）为 **65.76% ± 3.11 个百分点**，GPT-6.2 Sol + Codex（max）为 **61.52% ± 2.75 个百分点**，各 330 次 trial，精确值按一位小数四舍五入与图一致。该次查询的官方榜没有 Neon 行。图上的 **0.6 个百分点**只描述所列配置的点估计差，缺少同协议下的配对数据来判断是否有稳定差距。AA 的独立评测页还将 GPT-6.2 Sol + Codex（max）的 TB 4.1 分数显示为约 **58%**，进一步说明图中的 61.5% 来自另一个评测记录。 [AA 方法](https://artificialanalysis.ai/methodology/coding-agents-benchmarking) · [AA 评测页](https://artificialanalysis.ai/agents/coding-agents/comparisons/antigravity-cli-vs-codex) · [官方 4.1 榜](https://hub.harborframework.com/datasets/terminal-bench/terminal-bench/5?tab=leaderboard&leaderboard=4-1-0)

**“Cheating adjusted”描述通过后的轨迹复核。** 判分器先检查产物，随后评审已通过的试验轨迹，确认通过是否来自合法求解，确认违规的 trial 按 0 计。4.1 verifier 修订发生在产物验收这一层，轨迹复核发生在其后。AA 文档说明其按同一原则处理，但发布图没有列三组各自的原始通过率、扣分次数或可配对 trial。 [官方完整性规则](https://www.tbench.ai/news/leaderboard-integrity-update) · [AA 完整性方法](https://artificialanalysis.ai/methodology/coding-agents-benchmarking)

**SWE-sweep 把运行框架的影响变成了可见的数字。** 两行均由 Google 自测，使用按子任务加权的 reward。Provider 行分别用 Antigravity CLI 1.5.9、Claude Code 和 Codex，Mini-SWE 行统一使用 `mini-swe-agent vision` harness。用表面值计算，切到 provider 配置后，Neon **+26.2**、Opus **+6.5**、Sol **−3.3** 个百分点。Neon 对 Sol 的领先从 **1.2** 扩大到 **30.7** 个百分点，Opus 和 Sol 的次序也发生交换。DeepMind 提到 Antigravity CLI 的并行子 Agent 工具有利于分头查代码。该表能说明整套配置有影响，未单独控制子 Agent、工具链和计算预算，不能把 26.2 点全部归因于并行。 [DeepMind 方法 PDF，第 3 个物理页 Agentic Coding](https://deepmind.google/models/evals-methodology/gemini-4-neon) · [Google 发布页](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon/)

**跨类数字还要检查指标与指数版本。** 图首 `AA Index v5.0.1` 是 Intelligence Index，和把 Terminal-Bench 4.1、FrontierCode-AA 2.0、SWE-Atlas-QnA-AA 等权合成的 Coding Agent Index v2.1 是两套指数。图里的 FrontierCode 2.0 取官方榜，Neon 用 high thinking。Terminal-Bench-Science 0.1 的 Neon 70.5% 是 Google 用 Mini-SWE vision 每题重复五次的平均 reward，另两列来自该科学基准的官方榜。GraphWalks 的 95.2% 是长上下文 BFS 的 F1，它支持分析给定长输入下的任务表现，无法充当 prompt cache 的 TTFT、命中率或 SSD 增益指标。 [DeepMind 方法 PDF](https://deepmind.google/models/evals-methodology/gemini-4-neon) · [AA 指数方法](https://artificialanalysis.ai/methodology/coding-agents-benchmarking)

这张图给本地实验的可用参照，是把**固定 harness 的控制比较**和**实际产品配置的系统比较**分开报告。前者可以控制请求和 Agent 配置来定位缓存差值，后者容许编排与工具链变化，但只能把结果归到整个组合。两者分别保留预算、任务版本、失败处理和原始记录。 [本工作区应用](07-implications-for-this-workspace.md)

本文核对了发布标签、源码、官方公告和 Gemini 4 Neon 公开评测方法。仓库比较未启动镜像，厂商与独立评测结果未逐 trial 重算，本次未实跑 Harbor 或 llama.cpp 基准。
