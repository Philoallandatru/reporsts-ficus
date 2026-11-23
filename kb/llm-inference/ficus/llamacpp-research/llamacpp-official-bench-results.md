---
type: Concept
title: llama.cpp 官方基准测试结果
description: 日期：2026-09-01
tags:
- llm
- llamacpp
- kv-cache
sources:
- c:/Users/Administrator/Documents/Code/my-code/lm-llama/research/llamacpp-official-bench-results.md
createdAt: '2026-11-23'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# llama.cpp 官方基准测试结果

日期：2026-09-01

## 目标

- 运行时：`C:\Users\Administrator\Documents\models\llama`
- 模型：`C:\Users\Administrator\Documents\models\Qwen3.8-27B-UD-IQ3_XXS.gguf`
- llama.cpp 报告的模型类型：`qwen35 27B IQ3_XXS - 3.0625 bpw`
- 构建版本：`0caf2a1d4`，构建号 `9209`
- GPU：单张 `NVIDIA GeForce RTX 5080`
- 后端：CUDA
- CPU：`Intel(R) Core(TM) Ultra 7 270K Plus`

## 说明

`llama-bench` 在开启 mmap 时可以正常工作，但本地的这个构建在执行 `llama-bench -mmp 0` 时报 `GGML_ASSERT(buffer)` 失败。线上服务部署仍然使用 `--no-mmap`，但下面的官方基准结果应理解为开启了 mmap 的官方工具基线。

所有基准测试命令都通过 `CUDA_VISIBLE_DEVICES=0` 强制使用单张 5080。

## llama-bench

命令模板：

```powershell
llama-bench.exe --no-warmup `
  -m C:\Users\Administrator\Documents\models\Qwen3.8-27B-UD-IQ3_XXS.gguf `
  -ngl 99 -p 512,2048 -n 128 -b 2048 -ub 512 `
  -ctk q4_0 -ctv q4_0 -fa 1 -sm none -r 3 -o json
```

结果：

| 测试 | 平均速度 | 平均耗时 | 样本 |
|---|---:|---:|---|
| Prompt 处理，512 tokens | `1753.84 tok/s` | `306.84 ms` | `1251.32`, `1933.52`, `2076.66 tok/s` |
| Prompt 处理，2048 tokens | `2045.10 tok/s` | `1001.43 ms` | `2036.87`, `2053.05`, `2045.39 tok/s` |
| 文本生成，128 tokens | `58.20 tok/s` | `2200.03 ms` | `56.77`, `58.91`, `58.92 tok/s` |

解读：

- prompt 足够大时，prompt 处理速度稳定在约 `2k tok/s`。
- decode 约 `58 tok/s`，与之前 API 冒烟测试推导出的 decode TPS 一致。
- 缓存参数的调优应主要着眼于减少 prompt 处理量，而不应预期显著改变 `58 tok/s` 的 decode 速度。

## llama-batched-bench

命令模板：

```powershell
llama-batched-bench.exe `
  -m C:\Users\Administrator\Documents\models\Qwen3.8-27B-UD-IQ3_XXS.gguf `
  -ngl 99 -c 8192 -b 2048 -ub 512 `
  -ctk q4_0 -ctv q4_0 -fa on -sm none -kvu `
  -npp 512,2048 -ntg 128 -npl 1,2 --output-format jsonl
```

结果：

| Prompt tokens | 生成 tokens | 并发 prompt 数 | PP 速度 | TG 速度 | 总速度 |
|---:|---:|---:|---:|---:|---:|
| 512 | 128 | 1 | `1934.16 tok/s` | `58.33 tok/s` | `260.25 tok/s` |
| 512 | 128 | 2 | `2038.82 tok/s` | `100.09 tok/s` | `418.31 tok/s` |
| 2048 | 128 | 1 | `2035.52 tok/s` | `58.28 tok/s` | `679.46 tok/s` |
| 2048 | 128 | 2 | `2028.34 tok/s` | `99.49 tok/s` | `947.64 tok/s` |

解读：

- 批量 prompt 处理速度仍接近 `2k tok/s`。
- 两个并发 prompt 把总体 decode 从约 `58 tok/s` 提升到约 `99-100 tok/s`，但没有达到完美的 2x。
- 这是独立于 prompt-cache 测试的一个有用的服务吞吐基线。

## 实际使用建议

调优模型/运行时原始参数时使用 `llama-bench`：

- `-p`：prompt 处理长度
- `-n`：生成长度
- `-b` / `-ub`：批大小和微批大小
- `-ctk` / `-ctv`：KV cache dtype
- `-fa`：flash attention
- `-ngl`：GPU 卸载层数

调优服务类并发度时使用 `llama-batched-bench`：

- `-npp`：每个 prompt 的 prompt tokens
- `-ntg`：每个 prompt 的生成 tokens
- `-npl`：并发 prompt 数
- `-c`：上下文大小
- `-kvu`：unified KV

评估 prompt-cache 收益时请使用自定义缓存冒烟脚本，因为官方 bench 工具衡量的是原始计算吞吐，并不会回放多请求 prompt 复用模式。