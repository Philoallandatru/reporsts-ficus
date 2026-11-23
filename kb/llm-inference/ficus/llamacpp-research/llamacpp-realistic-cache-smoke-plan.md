---
type: Concept
title: 真实场景 llama.cpp 缓存冒烟测试方案
description: 日期：2026-08-29
tags:
- llm
- llamacpp
- kv-cache
sources:
- c:/Users/Administrator/Documents/Code/my-code/lm-llama/research/llamacpp-realistic-cache-smoke-plan.md
createdAt: '2026-11-23'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 真实场景 llama.cpp 缓存冒烟测试方案

日期：2026-08-29

更新：2026-09-01，把 `kv-cache-tester` 换成更权威的 SWE-bench 家族和 NVIDIA trajectory 数据源。

## 已确定决策

- 主要目标：coding-agent 加速 + 缓存压力/工作集转折点。
- 数据标准：语义负载与 trace 形状负载结合。
- 第一次运行规模：10 分钟冒烟测试，不是完整基准套件。
- 运行时目标：`C:\Users\Administrator\Documents\models\llama\llama-server.exe`
- 模型目标：`C:\Users\Administrator\Documents\models\Qwen3.8-27B-UD-IQ3_XXS.gguf`
- GPU 目标：通过 `CUDA_VISIBLE_DEVICES=0` 使用单张 RTX 5080

## 为什么选这些负载

之前的合成冒烟测试已经证明，当相同的长前缀重复出现时 llama.cpp prompt cache 是工作的。下一个冒烟测试需要回答一个更严苛的问题：当 prompt 看起来像真实 agent 工作时，同样的参数集还能不能帮忙？

用于负载设计的实用公开来源：

- SWE-bench 定义了真实的 GitHub issue 解决任务，模型接收代码库和 issue 并产出 patch。这对语义化 coding-agent prompt 是最佳指南：https://www.swebench.com/
- `SWE-bench/SWE-smith-trajectories` 是本项目首选的 trace 形状数据源。它在 SWE-bench 组织下发布，包含使用 SWE-agent 生成的 agent 轨迹，比小型个人 trace 仓库更接近我们关心的 coding-agent 负载：https://huggingface.co/datasets/SWE-bench/SWE-smith-trajectories
- NVIDIA Open-SWE-Traces 是一个更大的后期选项。它描述了 207,489 条 agent 轨迹，覆盖 9 种编程语言，源自 20,000 个真实 PR，使用 OpenHands 和 SWE-agent harness。它更适合完整基准测试，而不是 10 分钟冒烟：https://huggingface.co/datasets/nvidia/Open-SWE-Traces
- LMSYS-Chat-1M 是真实聊天流量最佳的备用方案。它包含 100 万条真实 LLM 对话，但不是 coding-agent 专属，prompt 也比 agentic coding session 更短，所以主要用作负向/对照分布：https://huggingface.co/datasets/lmsys/lmsys-chat-1m
- LongBench v2 包含真实世界长上下文类别，包括代码仓库理解、单文档 QA、多文档 QA、长对话历史理解和结构化数据。
- LoCoMo 提供带 session、标注 QA、观察和摘要的长期对话样本。这对后续的多轮聊天跟踪很有用。

被拒的来源：

- `kv-cache-tester` 不再作为主要来源使用。它作为 KV cache 回放的想法草图是有用的，但相比 SWE-bench 家族的轨迹数据集，它的采用情况和出处更弱。

## 10 分钟冒烟测试场景

### 1. 真实 coding-agent 同前缀

使用真实本地项目文件作为稳定上下文：

- `llama.cpp/tools/server/README-dev.md`
- `llama.cpp/common/arg.cpp`
- `llama.cpp/tools/server/server-context.cpp`
- `LMCache/README.md`
- `LMCache/docs/source/mp/index.rst`

请求模式：

1. 请求服务端缓存机制总结。
2. 用同一上下文请求风险清单。
3. 用同一上下文请求测试方案。

预期缓存行为：

- 步骤 1 是冷启动。
- 步骤 2 和 3 应能复用稳定的代码/文档前缀。
- 这验证了常见的 coding-agent 形态：同一 repo 上下文，不同推理任务。

通过条件：

- 步骤 2 或 3 有明显的缓存 token 计数，并且 prompt 处理时间比基线低至少 25-30%。

### 2. SWE 轨迹形状的 agent session

使用相同的真实代码上下文，但回放简化的类 SWE-agent/OpenHands 推进：

1. 大型固定 system/tool/project 前置。
2. 加入 issue 描述。
3. 加入 tool result 块。
4. 加入第二个 tool result 块。
5. 用相同前缀和不同最终指令再次提问。

预期缓存行为：

- 重复前缀应被复用。
- 根据 chat template 稳定性，增长的步骤可能只能部分复用。
- 这直接重测了第一次冒烟的弱点：增长对话并不是很强。

通过条件：

- revisit 步骤显示出强命中。
- 增长步骤应不弱于无缓存基线。

### 3. 工作集压力迷你测试

从真实文件创建 4 个伪 session：

- Session A：llama.cpp server 源码
- Session B：llama.cpp common args/源码
- Session C：LMCache MP docs/源码
- Session D：LMCache storage/backend docs/源码

请求模式：

1. warm A, B, C, D。
2. revisit A。
3. revisit B。

使用以下配置跑：

- `--cache-ram 1024`
- `--cache-ram 4096`

预期缓存行为：

- 4096 MiB 应该比 1024 MiB 保留更多有用的热前缀。
- 如果两者表现相同，则冒烟测试还没有制造足够的压力。

通过条件：

- 至少一个 revisit 在 4096 MiB 下相对 1024 MiB 有改善。
- 无缓存基线保持接近 0 缓存 token。

### 4. 负对照

在启用缓存的服务上用请求级 `cache_prompt=false` 跑相同的真实 coding-agent prompt。

预期缓存行为：

- 缓存 token 应为 0。
- prompt 时间应类似于冷处理。

通过条件：

- 确认我们在衡量的是缓存行为，而不是普通进程预热。

## 变体

最小 10 分钟运行：

1. `baseline_no_cache`：当前无缓存对照。
2. `cache_ram_4096`：推荐的当前参数集。

如果有时间可选：

3. `cache_ram_1024`：压力对比。
4. `cache_ram_reuse256`：仅当包含非开头重复块场景时才有意义。

## 指标

- wall-clock 请求延迟
- 流式 TTFT（如果用流式请求）
- `timings.prompt_ms`
- `timings.prompt_n`
- `timings.predicted_ms`
- `timings.predicted_n`
- `usage.prompt_tokens_details.cached_tokens`
- 缓存 token 比例
- 每个场景的 p50 和 p95
- 服务日志证据：prompt cache save/load/checkpoint 消息
- 每个变体前后的进程内存和 GPU 内存快照

## Grilling 通过准则

本次冒烟只有能证伪参数选择时才有意义。在以下任一情况下应视为成功：

- 对真实 coding-agent 前缀有明确收益，或
- 明确限制显示之前的合成收益在真实 prompt 形态下不成立。

不要仅凭"完全重复"就声称生产价值。完全重复只能证明机制工作。生产相关性需要 trace 形状和工作集场景。

## 建议的下一步命令

编写第二个基准脚本，从上面列出的真实本地文件构建 prompt，并运行：

```powershell
python research\run_llamacpp_realistic_cache_smoke.py --variants baseline,cache --cache-ram-mib 4096 --max-minutes 10
```

如果通过，再用以下方式扩展同一脚本：

```powershell
python research\run_llamacpp_realistic_cache_smoke.py --variants baseline,cache1024,cache4096 --max-minutes 30
```