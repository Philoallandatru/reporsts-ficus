---
type: Concept
title: llama.cpp 缓存基准测试结果：Qwen3.8-27B on 单卡 RTX 5080
description: 日期：2026-08-29
tags:
- llm
- llamacpp
- kv-cache
sources:
- c:/Users/Administrator/Documents/Code/my-code/lm-llama/research/llamacpp-cache-benchmark-results.md
createdAt: '2026-11-23'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# llama.cpp 缓存基准测试结果：Qwen3.8-27B on 单卡 RTX 5080

日期：2026-08-29

## 环境

- 运行时：`C:\Users\Administrator\Documents\models\llama`
- 服务：`C:\Users\Administrator\Documents\models\llama\llama-server.exe`
- 模型：`C:\Users\Administrator\Documents\models\Qwen3.8-27B-UD-IQ3_XXS.gguf`
- GPU：通过 `CUDA_VISIBLE_DEVICES=0` 使用单张 RTX 5080
- 上下文：`-c 8192`
- 共享基础参数：`-ngl 99 -b 2048 -ub 512 -np 1 --flash-attn on --jinja --reasoning off --split-mode none --kv-unified --kv-offload --no-mmap -ctk q4_0 -ctv q4_0`

## 测试过的变体

- `baseline_no_cache`：`--cache-ram 0 --no-cache-prompt --ctx-checkpoints 0 --checkpoint-every-n-tokens -1`
- `cache_ram`：`--cache-prompt --cache-ram 4096 --cache-idle-slots --ctx-checkpoints 8 --checkpoint-every-n-tokens 2048`
- `cache_ram_reuse256`：与 `cache_ram` 相同，外加 `--cache-reuse 256`
- `cache_ram_slot_save`：与 `cache_ram` 相同，外加 `--slot-save-path C:\Users\Administrator\Documents\models\slot-cache\`

运行命令：`research/run_llamacpp_cache_bench.py --profile smoke --ctx 8192 --variants baseline,cache,cache_reuse,slot_save --cache-ram-mib 4096`。

## 概要

这个本地 llama.cpp 构建已经在重复长前缀流量上显示出真实的 prompt-cache 收益。最明显的冒烟结果是"完全重复"：第二次请求的 prompt 处理从无缓存时约 `497 ms` 降到有缓存时的 `52-59 ms`，并报告 `987` 个缓存 token。在这个短输出测试中，这意味着 prompt 处理约快 `8.4x-9.6x`，整个请求 wall time 约快 `2.2x`。

共享长上下文也有收益，但在这次短 8k 上下文冒烟测试中不那么显著。共享文档和 agentic 前置场景下缓存 token 为 `385-475`，prompt 处理相对基线加速约 `1.3x-1.5x`。不断增长的对话没有显示出明显的逐轮递增收益，这意味着在假设多轮聊天会自动改善之前，需要更深入地测试 prompt 形状和 checkpoint 行为。

`--cache-reuse 256` 在这些场景中与普通 RAM prompt cache 接近。这里并没有带来明显收益，因为冒烟 prompt 主要测试的是开头前缀复用，而不是非开头重复 chunk。

手动 slot save/restore 成功写入和恢复了 state，但没有在测试的 OpenAI chat 请求形态中降低 prompt 处理。它保存/恢复了 `993` tokens，写入/读取 `175,221,576` 字节，save 耗时 `90.435 ms`，restore 耗时 `40.088 ms`，但后续同一 prompt 请求仍然完整进行 prompt 处理，缓存 token 为 `0`。服务日志说由于缺乏缓存数据，它强制进行了完整 prompt 重处理，这很可能与 SWA/hybrid/recurrent memory 处理有关。把这个视为已测试路径的负面结果，而不是缓存成功的证据。

## 关键数字

| 变体 | 场景 | 第二次请求缓存 tokens | 第二次 prompt ms | 相对基线第二次请求的 prompt 加速 | 相对基线第二次请求的 wall-time 加速 |
|---|---:|---:|---:|---:|---:|
| `cache_ram` | 完全重复 | 987 | 59.345 | 8.38x | 2.21x |
| `cache_ram` | 共享文档，不同问题 | 475 | 348.239 | 1.43x | 1.23x |
| `cache_ram` | agentic 共享前置 | 385 | 362.058 | 1.30x | 1.15x |
| `cache_ram` | 不断增长的对话 | 385 | 401.678 | 1.18x | 1.09x |
| `cache_ram_reuse256` | 完全重复 | 987 | 57.661 | 8.62x | 2.20x |
| `cache_ram_reuse256` | 共享文档，不同问题 | 475 | 336.638 | 1.48x | 1.26x |
| `cache_ram_reuse256` | agentic 共享前置 | 385 | 354.647 | 1.33x | 1.17x |
| `cache_ram_reuse256` | 不断增长的对话 | 385 | 383.949 | 1.23x | 1.14x |
| `cache_ram_slot_save` | 完全重复 | 987 | 51.788 | 9.60x | 2.25x |
| `cache_ram_slot_save` | 共享文档，不同问题 | 475 | 342.788 | 1.45x | 1.24x |
| `cache_ram_slot_save` | agentic 共享前置 | 385 | 358.975 | 1.31x | 1.16x |
| `cache_ram_slot_save` | 不断增长的对话 | 385 | 380.442 | 1.24x | 1.15x |

## 对照 LMCache 的解读

LMCache 在生产中的价值在于它把 KV cache 从短生命的引擎本地 state 变为可在请求、会话、引擎进程、Pod、节点、存储层之间复用的 state，有时还能跨 prefill/decode 角色复用。它在长上下文 agentic、RAG、多模态、多副本和内存压力负载下报告的收益最大——这些场景下重复 prefill 成本很高，并且是可复用的。

对于本地 llama.cpp 部署，第一个实际目标不是泛泛地说"加缓存"。llama.cpp 已经有有用的进程内 prompt 复用。高价值的下一步是衡量这种本地缓存何时不再够用：

- 8k-32k 稳定前缀的重复 coding-agent/工具前置内容
- RAG：许多问题复用同一批检索到的文档
- 多用户流量，热前缀被驱逐或被发送到不同服务进程
- 非开头重复 chunk，用于 `--cache-reuse`
- 进程重启或跨进程复用，未来类 LMCache 层会需要持久化/分层 state

## 当前的建议

对于当前的单 5080 部署，在服务的负载具有重复长前缀时启用 RAM prompt cache：

```powershell
--cache-prompt --cache-ram 4096 --cache-idle-slots --ctx-checkpoints 8 --checkpoint-every-n-tokens 2048
```

这已经足够在本地验证真实的 TTFT/prefill 收益。保留 `--cache-ram 0 --no-cache-prompt` 作为对照基线，因为首次运行的缓存开销可能让未缓存的一次性 prompt 看起来更干净。

暂不要依赖手动 `--slot-save-path` 作为生产加速路径。API 可以工作，但对 Qwen3.8-27B 的 chat 测试没有产生可用的恢复期 prefill 跳过。

## 后续实验

1. 用更接近 `8k-16k` tokens 的前缀跑 `--profile full`，对比 TTFT 而不只是 prompt 毫秒数。
2. 如果主机 RAM 允许，把 `--cache-ram` 提升到 `8192` 或 `12288` MiB，然后测试更长的热工作集。
3. 加入 `-np 2` 或多个服务进程，测试缓存收益是否在 slot 争抢和路由下存活。
4. 为 `--cache-reuse 256` 增加一个真正的非开头重复 chunk 场景。
5. 除了 `/v1/chat/completions` 还要测试 `/completion` 的 prompt 形态，因为 chat 模板可能打乱严格前缀复用。
6. 把 slot save/restore 留作工程风险跟踪：可用于理解 state blob，但尚未被证明是该模型/请求形态下的加速路径。

原始输出：`research/llamacpp_cache_bench_results.json`

服务日志：`research/llamacpp-cache-logs\`