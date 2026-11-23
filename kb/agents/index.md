# Agents

* [不依赖特定 Agent 的本地视觉小说制作流程](agent-independent-vn-pipeline.md) - 用项目文件、稳定素材编号和可恢复任务连接生成模型与可玩游戏。
* [单账户持仓以当日截图为准](single-account-holdings-snapshot.md) - 单账户只用一份按日期归档的持仓快照，截图当天即最终持仓。
* [Agent 基准测试生态调研（10 篇）](agent-bench-ecosystem/README.md) - SWE-bench 官方栈、Task/Verifier、衍生版与审计方法调研。

## 补充归档索引（Ficus-KB Synced）

- [Terminal-Bench 官方栈全景](agent-bench-ecosystem/01-official-stack.md) — `harbor-framework` 组织共 **21 个公开仓库**（`gh api orgs/harbor-framework/repos --paginate`，21 条，无分页遗漏）。下表按角色分组，license 列的 `—` 表
- [Terminal-Bench 的任务结构与判分体系](agent-bench-ecosystem/02-task-and-verifier.md) — `v4.1.0` 的 Linux 任务以 `task.toml` 声明配置，`solution/solve.sh` 提供 Oracle 入口，`tests/test.sh` 提供 verifier 入口。发布树中的 66 个目录均有 `ta
- [Terminal-Bench 的衍生实现、复现与学术衍生](agent-bench-ecosystem/03-derivatives-and-replicas.md) — 有三处常见说法与一手证据不符，先钉死，后文全部以此为准。
- [Agent 基准生态：竞品与替代全景](agent-bench-ecosystem/04-alternatives-landscape.md) — **与 TB 的分工**：TB 4.x 的 66 题横跨软件工程 / 系统 / 数据 / 科研杂项；TB-Science 把同一 harness 用在**科研工作流**上（生物信息学、蛋白结构、光子波导、基因组排序等），并引入「领域专家写任
- [Agent 评测方法学：Terminal-Bench 的可信度边界](agent-bench-ecosystem/05-methodology-and-audits.md) — **证据口径声明**
- [榜单、聚合平台与采用方](agent-bench-ecosystem/06-leaderboards-and-adopters.md) — **来源等级标记**：`官方一手` = tbench.ai / Harbor Hub / 官方仓库 / 厂商自己的页面；`厂商自述` = 厂商博客或模型页自报；`第三方聚合` = 独立机构或镜像站的榜单；`二手汇总` = 引用了上述来源但做
- [Terminal-Bench 对 llama.cpp 缓存研究的用途](agent-bench-ecosystem/07-implications-for-this-workspace.md) — Terminal-Bench 提供公开、版本化的终端任务和独立判分器。对本工作区，它的价值是补充一批可复核的 Agent 工作负载，并用实际任务结果检查缓存改动有没有引入回归。缓存收益仍由固定请求轨迹和同机对照测量。
- [Terminal-Bench 如何出分，又如何演化](agent-bench-ecosystem/08-benchmark-mechanics-and-evolution.md) — Terminal-Bench 的分数表示一个 Agent 系统在指定题集、工具、沙箱和预算下完成任务的比例。判断两个分数能否相减，先看求解时看到的题目和环境有没有变，再看验收规则与分母有没有变。4.0 到 4.1 的存档重评可以观察同一产物
- [证据索引](agent-bench-ecosystem/appendix-evidence.md) — 收录支撑全系列结论的入口。快照时间 **2026-11-19**。各专题保留自己的完整证据表与查证边界；本表负责跨篇的来源分级与版本锁定。
