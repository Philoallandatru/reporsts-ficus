# 使用 llm-wiki-compiler 构建本知识库

本仓库已在 `tmp/llm-wiki-compiler` 克隆了 `atomicstrata/llm-wiki-compiler` 用于参考。该工具会把 `sources/` 中的资料编译成带引用的 `wiki/` Markdown 页面。

## 快速结论

- 先用 `llmwiki ingest` 固定 4 个 canonical 来源，再跑 `llmwiki compile --review --lang zh-CN`。
- 如果你拿到的是原生 Anthropic key，优先走 `LLMWIKI_PROVIDER=anthropic` + `ANTHROPIC_API_KEY=...` 或 `ANTHROPIC_AUTH_TOKEN=...`，这条路会被识别成 `anthropic-native`。
- 如果你拿到的是 Anthropic-compatible 网关，再额外加 `ANTHROPIC_BASE_URL=https://api.minimaxi.com/anthropic`，这条路会被识别成 `anthropic-compatible`；`https://api.minimax.io/anthropic` 可作为国际区备用地址。
- 如果你拿到的是 MiniMax 原生 key，或者兼容网关不通，再切 `LLMWIKI_PROVIDER=minimax`，走 `https://api.minimax.io/v1`。
- 先跑 `python tools/check_llmwiki_setup.py --self-test` 看本地预检，再跑 `python tools/check_llmwiki_setup.py` 看当前 provider、网关和缺失项。
- 当前仓库已经验证过 Anthropic-compatible 和原生 MiniMax 两条路径都能到达远端接口，实际卡点在 key / 账号权限，而不是输入文件或脚本结构。

## 本机检查结果

- Node.js：已满足 `llmwiki` 要求，当前为 Node 24。
- npm：已可用。
- `llmwiki` CLI：通过 `npx -p llm-wiki-compiler llmwiki --version` 验证为 1.1.0。
- 摄取状态：`llmwiki ingest` 已可正常处理 `sources/source-catalog.md`、`sources/seed.md`、`sources/research-source-catalog.md` 和 `sources/research-nand-controller-patent-notes.md`，并生成带 hash 后缀的 `sources/*.md` 摄取副本。
- 编译状态：截至 2026-08-12，`llmwiki status --json` 仍显示 `stateStatus: missing`，且 compile 尚未成功落地；当前阻塞点已经从“输入文件缺失”收敛到“provider/compile 未完成”。

因此目前已经搭好可摄取资料结构；真正自动编译需要先修复 LLM provider 授权，或显式切换到可用 provider。

如果你手头拿到的是原生 Anthropic key，可以先按下面这条路径接：

```powershell
$env:LLMWIKI_PROVIDER="anthropic"
$env:ANTHROPIC_API_KEY="sk-..."
$env:LLMWIKI_OUTPUT_LANG="zh-CN"
```

这条路径会被识别成 `anthropic-native`。如果 key 没有权限，预检和编译都会直接给出 401，方便快速判断是接口问题还是账号权限问题。

如果你拿到的是 Anthropic-compatible 网关，再加上：

```powershell
$env:ANTHROPIC_BASE_URL="https://api.minimaxi.com/anthropic"
$env:LLMWIKI_MODEL="MiniMax-M2.7"
```

这条路径会被识别成 `anthropic-compatible`，适合需要走 MiniMax 兼容网关的场景。

如果你的账号侧只发放了 Anthropic 风格的授权令牌，也可以用：

```powershell
$env:LLMWIKI_PROVIDER="anthropic"
$env:ANTHROPIC_AUTH_TOKEN="sk-..."
$env:LLMWIKI_OUTPUT_LANG="zh-CN"
```

这两种写法走的是同一条 Anthropic-native 路径，区别只在于具体发放的是 API key 还是 auth token。

## 怎么选 provider

| 场景 | 先选什么 | 关键配置 | 先跑什么 |
| --- | --- | --- | --- |
| 你拿到的是原生 Anthropic key | `anthropic` | `LLMWIKI_PROVIDER=anthropic` + `ANTHROPIC_API_KEY=...` 或 `ANTHROPIC_AUTH_TOKEN=...` | `python tools/check_llmwiki_setup.py --self-test` |
| 你拿到的是 Anthropic-compatible 网关 | `anthropic` | `LLMWIKI_PROVIDER=anthropic` + `ANTHROPIC_BASE_URL=https://api.minimaxi.com/anthropic` + `LLMWIKI_MODEL=MiniMax-M2.7` | `python tools/check_llmwiki_setup.py --self-test` |
| 你拿到的是 MiniMax 原生 key，或兼容网关不通 | `minimax` | `LLMWIKI_PROVIDER=minimax` + `MINIMAX_API_KEY=...` + `https://api.minimax.io/v1` | `python tools/check_llmwiki_setup.py --self-test` |
| 你只想确认当前 shell 是否配对正确 | 还是按目标 provider 填 | 保持当前环境变量不变 | `python tools/check_llmwiki_setup.py --self-test` |
| 你想确认某个 key 到底能不能打通远端 | 先按上面两条之一 | 再看摘要里的 `anthropic_gateway`、`ready_for_compile` 和 `missing_provider_requirements` | `python tools/check_llmwiki_setup.py` |

这几个场景里，`anthropic` 和 `minimax` 的区别主要在于网关形态和 key 类型，不是整个编译流程的逻辑分叉。

## 2026-08-12 本机复测

在当前工作区再次执行：

```powershell
npx -p llm-wiki-compiler llmwiki compile --review --lang zh-CN
```

实际结果：

- `compile` 能识别并列出 8 个 pending 输入。
- `compile` 能进入 `Extracting` 阶段，说明 `sources/` 输入和 `.llmwiki/config.json` 本身没有缺失。
- 在提取阶段失败，错误为 `403 No active subscription found for this group`。
- 当前 shell 中未发现显式的 `LLMWIKI_*`、`OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`GITHUB_*`、`COPILOT_*` 或 `OLLAMA_*` 环境变量。

这说明当前阻塞点不是源文件路径，也不是 `ingest`；而是 `compile` 运行时选中的 provider/账号上下文不可用。

## 推荐命令

在 `ssd-design-wiki` 目录下执行：

```powershell
npm install -g llm-wiki-compiler

# OpenAI-compatible 示例
$env:LLMWIKI_PROVIDER="openai"
$env:OPENAI_API_KEY="sk-..."
$env:LLMWIKI_OUTPUT_LANG="zh-CN"

# 或 Anthropic / Anthropic-compatible 示例
$env:LLMWIKI_PROVIDER="anthropic"
$env:ANTHROPIC_BASE_URL="https://api.minimaxi.com/anthropic"
$env:ANTHROPIC_API_KEY="sk-ant-..."
$env:LLMWIKI_MODEL="MiniMax-M2.7"
$env:LLMWIKI_OUTPUT_LANG="zh-CN"

llmwiki ingest ./sources/source-catalog.md
llmwiki ingest ./sources/seed.md
llmwiki ingest ./sources/research-source-catalog.md
llmwiki ingest ./sources/research-nand-controller-patent-notes.md
llmwiki compile --review --lang zh-CN
llmwiki lint
llmwiki view --open
```

如果直接运行 `compile` 出现 `403 No active subscription found for this group`，优先检查当前 shell 或工具环境是否隐式使用了不可用的 provider。可显式设置：

```powershell
$env:LLMWIKI_PROVIDER="anthropic"
$env:ANTHROPIC_BASE_URL="https://api.minimaxi.com/anthropic"
$env:ANTHROPIC_API_KEY="sk-..."
$env:LLMWIKI_MODEL="MiniMax-M2.7"
```

如果这条 Anthropic-compatible 路径仍返回 401，再去切换到 OpenAI、Ollama、GitHub Copilot、Claude Agent SDK 等 `llmwiki` 支持的 provider。

## 资料摄取策略

1. 先摄取 `sources/source-catalog.md`、`sources/seed.md`、`sources/research-source-catalog.md` 和 `sources/research-nand-controller-patent-notes.md`。
2. 再逐个摄取规范入口和项目 README，不要一次把大量 PDF 全部塞进去。
3. 对规范 PDF 使用固定版本文件名，例如 `nvm-express-base-2.x.pdf`、`onfi-5.x.pdf`、`jesd218b02.pdf`。
4. 对源码仓库使用固定 commit 或 release tag 的 README、docs、关键源码片段。
5. 编译时优先使用 `--review`，人工确认后再 approve，避免把错误推断写成权威页。
6. 新增外部资料前，先用 `templates/source-intake-template.md` 建立 intake 记录，并同步 `VERSIONED_SOURCES.md`。

## 当前已验证行为

- `ingest` 可正常生成带 hash 后缀的摄取文件，例如 `sources/source-catalog-3e9312b0.md`。
- `.llmwiki/config.json` 已存在，说明工作区初始化过最小配置。
- 因为还没有成功 compile，`llmwiki status --json` 当前会把原始 `sources/*.md` 和 ingest 产物都显示为 `pendingChanges`。
- 这意味着下一步应优先解决 provider/compile，而不是继续排查源文件路径。
- 本地检查脚本当前要求 4 个 canonical 输入文件持续存在，并约束每个 canonical 文件最多只保留一个 `-xxxxxxxx.md` 形式的 ingest 副本。

## 当前排障优先级

1. 先走 Anthropic-compatible 路径，确认 key 是否允许 `https://api.minimaxi.com/anthropic` 这条网关。
2. 如果 Anthropic-compatible 路径返回 401，再确认当前 key 是否真的具备 MiniMax API 调用权限，而不只是控制台或别的产品权限。
3. 如果需要切到原生 MiniMax provider，再确认 key 是否允许 `https://api.minimax.io/v1` 和默认模型 `MiniMax-M2.7`。
4. 在 compile 成功前，不要继续增加 ingest 输入数量，否则 `pendingChanges` 只会继续膨胀。

## MiniMax Anthropic 兼容接口复测

截至 2026-08-12，本机还额外验证了 Anthropic 兼容网关路径：

- 设定 `LLMWIKI_PROVIDER=anthropic`。
- 设定 `ANTHROPIC_BASE_URL=https://api.minimaxi.com/anthropic`。
- 设定 `LLMWIKI_MODEL=MiniMax-M2.7`。
- 分别测试了 `ANTHROPIC_API_KEY` 和 `ANTHROPIC_AUTH_TOKEN` 两种鉴权变量。
- 两次 `compile --review --lang zh-CN` 都能进入 `Extracting` 阶段，但最终都返回 `401 invalid api key`。

这说明：

- Anthropic 兼容 base URL 路径本身是通的。
- 当前失败点已经从默认 provider/group 的 `403` 收敛成 MiniMax 鉴权失败。
- 后续需要优先核对所用 key 是否适用于该 Anthropic 兼容接口、模型名是否被该 key 允许，以及账户侧是否已开通对应能力。

## MiniMax 原生 provider 复测

截至 2026-08-12，本机还按 `llmwiki` 自带的原生 `minimax` provider 再测了一次：

- 设定 `LLMWIKI_PROVIDER=minimax`。
- 设定 `MINIMAX_API_KEY`。
- 不再设置 `ANTHROPIC_BASE_URL`，直接走 `llmwiki` 内置的 `https://api.minimax.io/v1`。
- 使用 provider 默认模型 `MiniMax-M2.7`。

实际结果：

- `compile --review --lang zh-CN` 同样能进入 `Extracting` 阶段。
- 之后返回 `401 invalid api key (2049)`。

这说明：

- MiniMax 原生 provider 和 Anthropic 兼容 provider 都能到达远端接口。
- 当前阻塞点一致落在凭证校验，而不是 provider 适配层、输入文件或 compile 流程本身。
- 在更换 key、账号或权限前，继续尝试不同模型名的收益不高。

## 本地状态守护

- `tools/check_ssd_wiki.py` 当前会检查 4 个 canonical `sources/*.md` 输入是否存在。
- 如果已经做过 `ingest`，每个 canonical 输入最多只允许存在一个 `-xxxxxxxx.md` 形式的 hash 副本。
- 这个规则的目标是避免 `sources/` 目录出现重复 ingest 产物，导致 `pendingChanges` 和排障状态越来越混乱。
- `python tools/check_llmwiki_setup.py` 默认输出适合人读的摘要；追加 `--json` 时会输出当前 `.llmwiki/config.json`、canonical 输入文件、ingest 副本、provider 环境变量是否存在、provider 矩阵快照、静态 provider 预检结果、按 provider 分流的 `next_step`、`next_actions`、`provider_route`、`provider_route_description` 和 `provider_route_description_compatible`，以及 `llmwiki status --json` 的原始结果。这里的 `provider_route` 和 `provider_route_description` 直接来自 `tests/requirements/llmwiki-provider-matrix.yml`；`provider_route_description_compatible` 只会在 `provider_route=anthropic-compatible` 时出现。Anthropic-native / Anthropic-compatible、原生 MiniMax、OpenAI-compatible、Claude Code 本地登录和 Ollama 这些路线都在矩阵里定义；`next_actions` 会跟着 route 走，不再把 native 路线和兼容网关混在一起。`tests/requirements/llmwiki-provider-matrix.yml` 还可以用专门 validator 单独检查。
- `python tools/check_llmwiki_setup.py --provider anthropic --anthropic-base-url https://api.minimaxi.com/anthropic --model MiniMax-M2.7 --anthropic-api-key ...` 可以在不改当前 shell 环境的情况下，直接试 Anthropic-compatible 这条路径的预检结果；如果账号发的是 token，也可以改用 `--anthropic-auth-token ...`。同样可用 `--openai-api-key`、`--minimax-api-key` 等参数快速切换。
- `python tools/validate_llmwiki_provider_matrix.py` 可以单独校验 `tests/requirements/llmwiki-provider-matrix.yml` 的结构，适合在改 provider 说明或自检用例后快速回归。
- `python tools/check_llmwiki_setup.py --self-test` 会本地验证 anthropic / anthropic-compatible / claude-agent / openai / copilot / minimax 的预检分支，不依赖外部网络。

## 建议的 llmwiki 查询

```powershell
llmwiki query "SSD firmware 中 FTL、GC、wear leveling 和 NVMe command processing 的边界是什么？"
llmwiki query "NAND channel/die/plane 结构如何影响 SSD 并行度？"
llmwiki query "FEMU、SimpleSSD、MQSim、Cosmos+ 分别适合验证哪些问题？"
llmwiki context "为一个教学用 NVMe SSD 控制器设计固件模块边界" --json
```
