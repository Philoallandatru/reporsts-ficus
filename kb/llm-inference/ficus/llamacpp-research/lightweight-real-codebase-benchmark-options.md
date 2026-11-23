---
type: Concept
title: 轻量级真实代码库基准测试选项
description: 日期：2026-09-01
tags:
- llm
- llamacpp
- kv-cache
sources:
- c:/Users/Administrator/Documents/Code/my-code/lm-llama/research/lightweight-real-codebase-benchmark-options.md
createdAt: '2026-11-23'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 轻量级真实代码库基准测试选项

日期：2026-09-01

更新：如果时效性是硬性要求，RepoBench 不再是首选。本地 llama.cpp 评估时优先选择 LiveCodeBench 加上 GenAI-Perf/自定义 OpenAI-compatible 延迟回放，当端到端代码编辑能力很重要时再加上 Aider Polyglot。

## 目标

为验证 llama.cpp prompt-cache 收益选择一个标准的真实代码库基准测试，且不需要 Docker。该基准测试是为了延迟/缓存行为，而不是完整的 patch 正确性。

## 建议

把 LiveCodeBench 作为第一个现代代码能力基准测试，把 GenAI-Perf 或自定义 OpenAI-compatible 回放框架作为第一个针对 llama.cpp 的性能/缓存基准。

如果要回答"这个本地模型能否编辑代码并端到端通过测试？"，使用 Aider Polyglot。
如果要回答"缓存参数是否真的降低了 TTFT？"，不要使用 Aider Polyglot。

RepoBench 和 CrossCodeEval 仅作为 repo 上下文 prompt 来源或遗留基线保留。

## 类 Aider Polyglot 的套件

这些比 RepoBench/LiveCodeBench 更接近 Aider Polyglot，因为它们评估的是编辑已有代码或 agent 工作，而不只是独立代码生成。

### Aider Refactoring Benchmark

来源：

- 排行榜页面：https://aider.chat/docs/leaderboards/

为什么合适：

- 与 Aider Polyglot 同一生态。
- 直接针对编辑/重构行为。
- 如果本地模型已经通过 Aider 的 OpenAI-compatible API 路径接入，这是很好的首个兄弟基准。

主要限制：

- 它仍然是 Aider 专属，所以对实际 Aider 使用很出色，但学术基准度不如。

### CanItEdit

来源：

- GitHub：https://github.com/nuprl/CanItEdit
- 论文：https://arxiv.org/abs/2312.12450

为什么合适：

- 教学型代码编辑基准：给定已有代码和自然语言指令，产生编辑后的代码。
- 包含 105 个手工构造的 Python 问题，含前后代码、描述型和惰性指令，以及隐藏测试。
- 足够轻量，可以适配到本地 OpenAI-compatible 端点。

主要限制：

- 仅 Python 且单文件导向，因此无法完全代表现代多文件 coding-agent 工作。

### EDIT-Bench

来源：

- 论文：https://arxiv.org/abs/2511.04486
- ICLR 2026 论文页面：
  https://proceedings.iclr.cc/paper_files/paper/2026/hash/98ddf59eb1c622132a1cf04cb5f59ac7-Abstract-Conference.html

为什么合适：

- 基于真实用户使用的现代指令式代码编辑基准。
- 包含从真实用户指令和代码上下文收集的 545 个问题。
- 包含上下文相关的信息，如当前代码、高亮代码和光标位置。
- 涵盖多种自然语言和 Python/JavaScript 代码。

主要限制：

- 更真实，但对本地端到端评估而言可能不如 Aider 那样即插即用。它可能需要一个小适配器才能在 `llama-server` 上运行。

### CodeEditorBench

来源：

- GitHub：https://github.com/CodeEditorBench/CodeEditorBench
- 项目站点：https://codeeditorbench.github.io/
- 论文：https://arxiv.org/abs/2404.03543

为什么合适：

- 更大的代码编辑基准，覆盖调试、转换、打磨和需求切换。
- 涵盖多种编程语言和基于执行/测试的指标。
- 当我们需要比 Aider Polyglot 更广的编辑类别时很有用。

主要限制：

- 比 Aider 更大、更像基准框架；更适合计划的运行，而不是 10 分钟冒烟。

### Terminal-Bench

来源：

- 网站：https://www.tbench.ai/
- GitHub：https://github.com/harbor-framework/terminal-bench
- 本工作区调研：`agent-bench-ecosystem/` (`agent-bench-ecosystem/README.md`)

为什么合适：

- 在真实终端任务上测试 agent：编译、调试、系统设置、多步工作流。
- 对实际 agent 行为比单 prompt 代码编辑给出更强信号。
- 官方任务自带 verifier，判分可审计；成绩由版本标签、harness、agent、模型和试次数共同定义。

主要限制：

- 比 Aider Polyglot 更重，基于容器/沙箱（Harbor，默认 Docker，可切 Modal/Daytona 等）。它不是"轻量级、不用 Docker"约束的最佳匹配。
- 连续演进基准：任务集与判分器持续改版，引用任何数字都必须带版本标签。
- 第三方审计对 4.0 判 Flawed（66 题中 30 题有公开记录的评分缺陷）；4.1 只加固判分器、不新增任务，是否仍应判 Flawed 未核实。

定位调整：本节原把它列为"轻量候选"。它更适合作为**外部锚点**——为"缓存在真实长时程 agent 工作负载上的收益"提供一个别人也认的坐标系。轻量候选仍是 Aider Polyglot / LiveCodeBench。

仅把 SWE-bench 作为 issue 来源或后续完整 agent 评估保留，因为官方 SWE-bench 评分需要 Docker。

## 选项 0：当前推荐的栈

### LiveCodeBench 用于当前代码能力

来源：

- 网站：https://livecodebench.github.io/
- GitHub：https://github.com/LiveCodeBench/LiveCodeBench

为什么合适：

- 持续用 LeetCode、AtCoder、CodeForces 的代码问题更新。
- 支持 release windows，有助于减少新模型的污染。
- 覆盖范围超出普通代码生成：自修复、测试输出预测和代码执行。
- 可以针对本地/开放模型运行生成，并可以评估保存的自定义生成。

如何用于 llama.cpp：

- 通过 `llama-server` 的 OpenAI-compatible API 提供本地 GGUF 模型。
- 通过小型适配器脚本或其自定义输出路径生成 LiveCodeBench 答案。
- 对保存的完成运行 LiveCodeBench 评估。

主要限制：

- 它不是仓库级 agent 工作。它评估当前代码能力优于 RepoBench，但本身并不能压测重复 repo 上下文 prompt 缓存。

### GenAI-Perf 或 AIPerf 用于本地服务/缓存指标

来源：

- NVIDIA GenAI-Perf 文档：
  https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html
- NVIDIA OpenAI-compatible API 基准指南：
  https://developer.nvidia.com/blog/measuring-generative-ai-model-performance-using-nvidia-genai-perf-and-an-openai-compatible-api/

为什么合适：

- 衡量 LLM 服务指标，例如 TTFT、time-to-second-token、token 间延迟、输出吞吐和请求吞吐。
- 可以面向 OpenAI-compatible 端点，与 `llama-server` 匹配。
- 接受合成或文件定义的数据集和负载模式。

如何用于 llama.cpp 缓存测试：

- 把真实 prompt 回放集合保留为文件定义的数据集。
- 运行 baseline 无缓存和 cache4096 服务。
- 在受控并发下比较 TTFT/p95/吞吐。

主要限制：

- 它衡量的是服务性能，而不是答案正确性。

### Aider Polyglot 用于端到端本地代码编辑

来源：

- Aider 排行榜：https://aider.chat/docs/leaderboards/
- Aider 基准文档：
  https://github.com/Aider-AI/aider/blob/main/benchmark/README.md

为什么合适：

- 当前实用的代码编辑基准，通过真实 coding 工具。
- 使用 225 个有挑战性的 Exercism 任务，覆盖 C++、Go、Java、JavaScript、Python 和 Rust。
- Aider 支持 OpenAI-compatible API，因此本地 `llama-server` 端点可以用作模型后端。

主要限制：

- 它是代码能力基准，而不是缓存基准。缓存收益必须独立于模型的 pass/fail 分数来衡量。

## 选项 1：RepoBench

来源：

- 论文：https://arxiv.org/abs/2306.03091
- GitHub：https://github.com/Leolty/repobench
- Python v1.1 数据集：https://huggingface.co/datasets/tianyang/repobench_python_v1.1
- Java v1.1 数据集：https://huggingface.co/datasets/tianyang/repobench_java_v1.1

为什么合适：

- ICLR 2024 仓库级代码自动补全基准。
- 使用真实多文件仓库上下文。
- 有 Python 和 Java 版本。
- 有检索、补全和流水线任务。
- Hugging Face 数据集已经是 prompt 风格的表格数据，因此可以通过 llama.cpp 的 OpenAI-compatible API 进行测试，而无需克隆/构建每个 repo。
- RepoBench 自己的 README 说如果只使用数据可以跳过依赖项。

用于 llama.cpp 缓存测试的最佳用法：

1. 从 `tianyang/repobench_python_v1.1` 加载一个小切片。
2. 按 `repo_name` 对样例分组。
3. 对每个 repo，在多个补全式 prompt 中复用相同的 `context` 代码片段和 `import_statement`。
4. 对比 baseline 无缓存 vs cache4096。
5. 衡量 `prompt_ms`、wall time、缓存 tokens 和缓存 token 比例。

为什么比之前的临时 trace 选项更好：

- 它是一个有公开论文和数据集的同行评审基准。
- 它已经针对仓库级代码补全，这正是我们需要用于 coding-agent 上下文复用的精确轻量代理。

主要限制：

- 它测试代码补全和跨文件检索/补全，而不是完整的 issue 解决轨迹。它对缓存/延迟和上下文复用很出色，但不足以声称 SWE-agent 任务成功。

## 选项 2：CrossCodeEval

来源：

- 论文：https://arxiv.org/abs/2310.11248
- GitHub：https://github.com/amazon-science/cceval
- 项目站点：https://crosscodeeval.github.io/

为什么合适：

- NeurIPS 2023 Datasets and Benchmarks track。
- 由真实、宽松许可的开源 repo 构建。
- 涵盖 Python、Java、TypeScript 和 C#。
- 明确需要跨文件上下文以实现准确补全。
- 仓库包含数据和推理脚本。

用于 llama.cpp 缓存测试的最佳用法：

1. 直接使用 prompt JSONL 文件。
2. 仅从 Python 开始。
3. 在多个补全请求中复用跨文件上下文块。
4. 对比 baseline 与 cache4096 的 prompt-cache 行为。

主要限制：

- 完整官方评估可能需要额外的 Python 依赖项和 tree-sitter 设置才能计算指标。对于仅缓存/延迟测试，prompt 文件就够用。

## 选项 3：SWE-bench / SWE-bench Lite

来源：

- 网站：https://www.swebench.com/
- Harness 文档：https://www.swebench.com/SWE-bench/reference/harness/
- FAQ：https://www.swebench.com/SWE-bench/faq/

为什么不是这个约束的首选：

- SWE-bench 是权威的，使用真实的 GitHub issue。
- 但官方评估应用生成的 patch 并在 Docker 中运行测试。
- FAQ 说 Docker 是必需的，以保证一致的评估环境。

最佳轻量级用法：

- 仅使用 issue 文本和 repo 元数据作为 prompt 资料。
- 不要声称官方 SWE-bench 分数。

## 选项 4：LMSYS-Chat-1M

来源：

- 数据集：https://huggingface.co/datasets/lmsys/lmsys-chat-1m
- 论文：https://arxiv.org/abs/2309.11998

为什么不是主要代码基准：

- 它是真实世界聊天流量，而不是仓库级代码。
- 它作为低复用普通聊天的负向/对照分布很有用。

## 建议的下一个测试

添加 RepoBench 切片模式：

```powershell
python research\run_llamacpp_repobench_cache_smoke.py --dataset tianyang/repobench_python_v1.1 --split cross_file_first --repos 3 --examples-per-repo 3 --variants baseline,cache --cache-ram-mib 4096
```

预期信号：

- 同一 repo 的第一个样例是冷启动或低命中。
- 同一 `repo_name` 的后续样例复用稳定的跨文件上下文。
- repo 级 revisit 应显示缓存 token 和更低的 prompt/prefill 时间。

通过条件：

- 至少 50% 的同 repo 后续样例命中缓存。
- 同 repo 后续样例的中位数 prompt 加速至少 1.5x。
- 负向/对照混合 repo 或 `cache_prompt=false` 用例不显示虚假缓存收益。