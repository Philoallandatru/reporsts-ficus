---
type: Concept
title: llama.cpp 在单卡 RTX 5080 上对 Qwen3.8-27B 的缓存基准测试方案
description: 日期：2026-08-29
tags:
- llm
- llamacpp
- kv-cache
sources:
- c:/Users/Administrator/Documents/Code/my-code/lm-llama/research/llamacpp-cache-benchmark-plan.md
createdAt: '2026-11-23'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# llama.cpp 在单卡 RTX 5080 上对 Qwen3.8-27B 的缓存基准测试方案

日期：2026-08-29

## 本地目标

- llama.cpp 运行时：`C:\Users\Administrator\Documents\models\llama`
- 服务二进制：`C:\Users\Administrator\Documents\models\llama\llama-server.exe`
- 模型：`C:\Users\Administrator\Documents\models\Qwen3.8-27B-UD-IQ3_XXS.gguf`
- 目标 GPU：通过 `CUDA_VISIBLE_DEVICES=0` 使用单张 RTX 5080
- 需保留的基线启动脚本：`C:\Users\Administrator\Documents\models\27-ud-single.ps1`

## 目标

衡量哪些 llama.cpp 缓存机制在这个本地模型上真正降低了重复 prefill 成本：

- 每个请求的 `cache_prompt`
- 通过 `--cache-ram` 启用的服务 RAM prompt cache
- 通过 `--cache-idle-slots` 实现的空闲 slot 保存/恢复行为
- 通过 `--slot-save-path` 的手动 slot 保存/恢复
- 可选的、通过 `--cache-reuse` 实现的非开头 chunk 复用

这还不是完整的 LMCache 集成。它验证的是第一个实用的构建模块：llama.cpp 现有的 state/prompt cache 能否在重复长前缀流量下产生有意义的 TTFT/prompt 处理收益。

## 服务变体

### A. 基线：关闭缓存

保持现有单卡部署形态并关闭 prompt cache：

- `-ngl 99`
- `-c 8192`
- `-b 2048`
- `-ub 512`
- `-np 1`
- `--flash-attn on`
- `--jinja`
- `--split-mode none`
- `--kv-unified`
- `--kv-offload`
- `--no-mmap`
- `--cache-ram 0`
- `--no-cache-prompt`
- `--ctx-checkpoints 0`
- `--checkpoint-every-n-tokens -1`
- `-ctk q4_0`
- `-ctv q4_0`

### B. 启用 RAM Prompt Cache

保持相同部署形态但启用 prompt/state 复用：

- `--cache-prompt`
- `--cache-ram 4096`
- `--cache-idle-slots`
- `--ctx-checkpoints 8`
- `--checkpoint-every-n-tokens 2048`

### C. Chunk-Reuse 变体

与 B 相同，外加：

- `--cache-reuse 256`

用于测试 llama.cpp 自带的非开头 chunk 复用路径。它应与纯前缀缓存分开评估。

### D. Slot Save/Restore 变体

与 B 相同，外加：

- `--slot-save-path C:\Users\Administrator\Documents\models\slot-cache\`

用于验证持久化 state blob。这是最接近未来 prefix-state-blob cache 的本地类比。

## 场景

### 1. 完全重复

发送同一个长 prompt 两次。

预期结果：

- 基线：两次调用都正常处理 prompt。
- 启用缓存：第二次调用应报告更高的缓存 token 数和显著更低的 prompt 处理时间。

### 2. 共享文档，不同问题

发送一个长静态文档和问题 A，然后用同一文档和问题 B。

预期结果：

- 启用缓存应能复用文档前缀，只处理变化的问题后缀。

### 3. Agentic 共享前置内容

使用一个大的固定"系统/工具/文件"前置内容，只变化最后一轮用户输入。

预期结果：

- 启用缓存时应表现为本地版本的 agentic 前缀复用：重复出现的工具/系统/文件上下文应变得很便宜。

### 4. 不断增长的对话

发送第 1 轮，然后发送包含第 1 轮历史的第 2 轮，再发送带更多历史的第 3 轮。

预期结果：

- 只有在格式化后的 prompt 是真正的前缀扩展时缓存才有帮助。chat 模板和推理模式可能影响这一点。

### 5. 每个请求关闭缓存

在启用缓存的服务上用 `cache_prompt=false` 运行相同的 prompt。

预期结果：

- 这能区分服务启动期效果与请求级 prompt cache 效果。

### 6. Slot Save/Restore

在一个长 prompt 之后保存一个 slot，清空/替换该 slot，然后恢复它并问一个后缀问题。

预期结果：

- 当保存的 state 足够大时，恢复成本应低于重新计算整个 prompt。

## 需要记录的指标

- wall-clock 延迟
- `timings.prompt_ms`
- `timings.prompt_n`
- `timings.predicted_ms`
- `timings.predicted_n`
- `usage.prompt_tokens_details.cached_tokens`
- 输出文本的健全性抽样
- prompt-cache load/save 附近的服务日志片段

最重要的对比是：

`saved_prefill_time = baseline_prompt_ms - cached_prompt_ms`

对于未来的类 LMCache 设计，还需要估算：

`net_gain = saved_prefill_time - lookup_time - restore_io_time`

## 第一轮建议

先用 `research/run_llamacpp_cache_bench.py` 中的短自动基准，ctx 设为 8192、生成少量 token。如果显示出明显的 prompt-cache 命中，再加大：

- 上下文到 32768
- 前缀长度到 8k-16k tokens
- 如果主机 RAM 允许，把 `--cache-ram` 调到 8192 或 12288 MiB
- 场景中加入 slot save/restore 和 `--cache-reuse`