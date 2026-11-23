---
type: Concept
title: llama.cpp 架构导读（从一次前向传播看懂整个仓库）
description: ┌─────────────────────────────────────────────────┐
tags:
- llm
- llamacpp
- kv-cache
sources:
- c:/Users/Administrator/Documents/Code/my-code/lm-llama/research/llama-cpp-architecture.md
createdAt: '2026-11-23'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# llama.cpp 架构导读（从一次前向传播看懂整个仓库）

> 基于仓库内 `llama.cpp`（commit `f5e85d43a`）。第二次读源码时请带着这张图：
> **token 进来 → vocab 编码 → batch 切分 → memory（KV）排座位 → graph 建图 → backend 执行 → sampler 选词 → decode 循环。**
> server 只是把这个循环包上“排队 + 分桌（slot） + HTTP”。

---

## 1. 总览：五层楼

```
┌─────────────────────────────────────────────────┐
│  tools/（门面）：cli / serve / bench / quantize… │  ← 用户摸到的都是 common_params
├─────────────────────────────────────────────────┤
│  common/（胶水）：arg 解析 / sampling 组装 /     │  ← arg.cpp, sampling.cpp, chat.cpp, common.cpp
│        chat 模板 / multimodal / speculative      │
├─────────────────────────────────────────────────┤
│  lib llama（核心）：model / context / memory /   │  ← src/llama-*.cpp, include/llama.h
│        graph / sampler / vocab / quant           │
├─────────────────────────────────────────────────┤
│  ggml（算子与后端）：tensor / graph 执行 /       │  ← ggml/src/ggml*.cpp, ggml-cpu/cuda/metal/…
│        CPU·CUDA·Metal·Vulkan…                   │
├─────────────────────────────────────────────────┤
│  GGUF 文件（硬盘上的模型）：权重 + 元数据/分词器  │  ← convert_*.py, gguf-py, llama-model-loader
└─────────────────────────────────────────────────┘
```

- 跨层约定只有两个 C API 面：`include/llama.h`（模型/上下文/采样/批全在这声明，~1638 行）
  与 `common/common.h` 的 `common_params`（CLI 参数的结构体镜像）。
- 目录与源码行数（`wc -l` 实测）：`src/llama-context.cpp` 4298、`llama-graph.cpp` 3849、
  `llama-model.cpp` 3220、`llama-kv-cache.cpp` 2852、`llama-sampler.cpp` 4385、
  `llama-vocab.cpp` 4440、`common/common.cpp` 2362。

---

## 2. 数据流：一个 token 的旅行

```
prompt 文本
  │ common_chat_apply_template + llama-vocab 编码
  ▼
llama_batch（逻辑批：n_batch, 逻辑上限）
  │ llama_memory_i::init_batch 切成 llama_ubatch（物理批：n_ubatch）
  ▼
memory 排座位（KV cache 选 seq/pos，必要时 shift/defrag/存档）
  │ llama_memory_context_i::apply()
  ▼
llama_graph 建图（按 arch 选 attention/FFN/norm，决定 fuse flash-attn）
  │ ggml_backend_sched 执行（CPU/GPU 按 -ngl/-dev/-ts 分布）
  ▼
logits → sampler 链（penalties→…→temperature→dist，见 sampling.cpp）
  │ 贪心 temp=0 走捷径分支
  ▼
新 token → 写回 memory → 若 speculate 则 draft 验证/回滚 → 循环直到 EOS/-n
```

关键文件：批 `src/llama-batch.*`，内存接口 `src/llama-memory.h`（`init_batch/init_update/seq_*`），
建图 `src/llama-graph.*`，调度 `ggml/src/ggml-backend*.cpp`，采样 `src/llama-sampler.cpp` + `common/sampling.cpp`。

---

## 3. GGUF 与模型加载（`llama-model`）

- GGUF = 自描述容器：张量权重 + `general.*`/`tokenizer.*` 元数据 + 量化类型（`Q4_K_M` 等）。
  `llama-model-loader.cpp`（1744 行）负责 mmap/分片拼接（`model-00001-of-…`）、
  `--override-kv` 改元数据、`--check-tensors` 校验。
- `llama-arch.cpp/h`（1149/786 行）是“方言翻译官”：Llama/Qwen/Gemma/MoE/encoder-decoder（T5/Whisper 式）各有
  attention/FFN/norm 组合（见 `llama-graph.h` 的 `LLM_FFN_*`、`LLM_NORM_*` 枚举）。
- 量化/蒸馏工具链：`tools/quantize`、`tools/imatrix`（重要性矩阵）、`tools/export-lora`；
  适配器：`src/llama-adapter.cpp`（LoRA）、control-vector。
- 内存放置：`-ngl/-dev/-sm/-ts/-mg/-ot/-cmoe/-ncmoe/-ncffn` 最终都落到
  `llama_model_params.tensor_buft_overrides` + 后端 buffer 类型选择；
  `--fit`（默认开）按各设备空闲显存自动压缩未显式设置的值。

---

## 4. 上下文与内存：KV cache 家族（`llama-memory` / `llama-kv-cache*`）

`llama-memory.h` 只暴露接口 `llama_memory_i`（`seq_rm/cp/keep/add/div` + `init_batch/init_update`），
实现按注意力类型分家（各有 `.cpp`，最长的 dsv4 达 2253 行）：

| 实现 | 给谁用 |
|---|---|
| `llama-kv-cache`（MSA，多头标准） | Llama/Qwen 主流 decoder |
| `llama-kv-cache-iswa` / `dsa-iswa` / `hybrid-iswa` | 滑动窗口（SWA，如 Gemma）：`--swa-full` 切全尺寸 |
| `llama-kv-cache-dsa/dsv4` | 稀疏/混合注意力新架构 |
| `llama-memory-recurrent/hybrid` | Mamba/RWKV 式循环+混合状态 |

- server 的 `--cache-prompt/--cache-reuse/-ctxcp/--slot-save-path` 都是对这层的操作：
  缓存 prompt 的 KV、按前缀相似度平移复用（`seq_add` shift）、存档点回滚、落盘。
- 精度 `-ctk/-ctv`（`f16/q8_0/q4_0`）即 `llama_memory_params.type_k/type_v`；
  `-fa` 是否 fuse flash attention 由 graph 层的 `LLM_FUSED_OP_FLASH_ATTN` 决定。

---

## 5. 计算图与后端（`llama-graph` + `ggml`）

- `llama-graph.cpp`（3849 行）按 batch 中每个 ubatch 为每层搭子图：norm → QKV proj → attention
 （MHA/GQA/SWA/DSA 按 arch 切换）→ O proj → FFN（SwiGLU/GeGLU/…) → norm。
  `LLM_GRAPH_TYPE_{DEFAULT,ENCODER,DECODER,DECODER_MTP}` 区分编码器/解码器/MTP 草稿图。
- `ggml/` 是独立张量库：`ggml.c/cpp`（算子）、`ggml-alloc`（图内存规划）、
  `ggml-backend*.cpp`（设备抽象 + scheduler）、`ggml-cpu/cuda/metal/vulkan/…`（各硬件实现，
  如 Metal FA vec 调优、SYCL 量化 KV decode）。
- 线程模型：`-t/-tb` 进 `common_cpu_params`，再进 ggml 线程池；`-C/-Cr/--prio/--poll/--numa`
  控制绑核与忙等。decode 是内存带宽敏感（batch=1），prefill 是计算敏感（batch 大），
  这就是 `-b/-ub` 分开的原因。

---

## 6. 采样器链（`llama-sampler` + `common/sampling`）

- `llama-sampler.cpp`（4385 行）每个采样器是独立 `llama_sampler`（`init_top_k/top_p/min_p/temp/xtc/dry/penalties/mirostat/grammar/logit_bias/…`，
  声明见 `llama.h:1367-1524`），用 `llama_sampler_chain_add` 串成链。
- `common/sampling.cpp:common_sampler_init()` 负责“按 `--samplers` 顺序组装 + 把 grammar/DRY/logit-bias 前置合并”，
  默认链 `penalties→dry→top_n_sigma→top_k→typical→top_p→min_p→xtc→temperature`（`common.h:261`）。
- 约束解码：`--grammar/--json-schema` 经 `common/json-schema-to-grammar` 转 GBNF，
  再进 `llama_sampler_init_grammar*`（lazy patterns 按触发器延迟生效，省性能）。
- 推测解码（`common/speculative.cpp` + `tools/server` 的 draft 上下文）：
  draft 上下文（小模型/ngram）先猜 `n_max` 个 → target 一次验证 → 接受则保留 KV，拒绝则 `seq_rm` 回滚。
  `--spec-type mtp/dflash/eagle3/dspark/ngram-*` 即选择 draft 策略。

---

## 7. common 胶水层：参数如何变成行为

- `common/arg.cpp`（4767 行，357 个 `add_opt`）：CLI/env/config 三源合一，产物是 `common_params`。
- `common/common.cpp`（2362 行）：`common_params_parse` 之后做“翻译”——`common_params → llama_model_params + llama_context_params`，
  含 `--fit` 压缩、`--jinja` 模板选择、mmproj 挂载。
- `common/chat.cpp`（957 行）：Jinja 模板渲染、reasoning 标签提取（`--reasoning-format`）、tool-call 解析；
  `common/chat-*.cpp` 是自动解析器生成器。
- `common/build-info`、`log`、`download`（HF 缓存/断点续传）、`ngram-cache`（lookup 解码的静态/动态缓存文件）。

---

## 8. server：队列 + slot + 连续批（`tools/server`）

```
HTTP（server-http）→ task 队列（server-queue：post/defer/优先级）
  → worker 聚合各 slot 的 batch → llama_decode 一次前向
  → 按 slot 做 sampler（各请求独立 seed/grammar/penalty）
  → SSE/WebSocket 流式回传（server-stream）→ slot 归还/存档
```

- `server-context.h:27 slot_n_ctx`：每个 slot 一份序列状态（token 历史 + 采样器 + KV 位置引用），
  总 KV 池（`-c`）被 `-np` 个 slot 切分（或按 `--kv-unified-per-slot` 估算）。
- `server-queue.h`：`queue_tasks`（待办）/`queue_tasks_deferred`（等空 slot）/`queue_tasks_unhandled`（yield 时暂退），
  `--sleep-idle-seconds` 无任务时休眠，`--slot-prompt-similarity` 做 slot 亲和复用。
- 端点（`server.cpp:194` 起注册）：OpenAI 兼容 `/v1/chat/completions·completions·embeddings`、
  原生 `/completion·embeddings·rerank`、运维 `/health·metrics·props·slots`、模型路由 `/models`（router 模式多模型按需加载）。
- `cli-client.cpp` 让 `llama cli --server-base URL` 复用同一套 HTTP 面：CLI 与 server 共享数据契约。

---

## 9. 给 LMCache 项目的对接启示（为什么你要读这两篇）

1. ** prefix 复用的钩子都在 memory 层**：`seq_cp/add/div/rm` + `slot_save_path` 落盘格式，
   LMCache 若要做 L1/L2，只需在 `server-context` 的 slot 换入换出点拦截 KV（本仓库 `research/` 下
   `lmcache-llamacpp-kv-cache.md`、`llamacpp-tiered-cache-*.md` 已有实测与设计）。
2. **参数调优顺序**：先定 `-c/-np`（容量规划）→ `-b/-ub`（prefill）→ `-ctk/-ctv/-fa`（显存）→
   `--cache-reuse/-sps`（命中率）→ `--spec-*`（decode 加速）→ 采样（口味）。
3. **看源码的入口顺序**：`common/arg.cpp`（参数定义）→ `common/common.h:448`（`common_params` 默认值）
   → `common/sampling.cpp:187`（采样组装）→ `src/llama-memory.h`（KV 接口）→
   `src/llama-graph.cpp`（建图）→ `tools/server/server-queue.h` + `server-context.*`（并发）。

---

## 10. 一页速记

- 选模型：`-m/-hf/-mmproj`；多模型 router：`--models-dir/--models-preset/--models-max`。
- 定容量：`-c`（桌子）`-n`（续菜数）`-np`（几桌）`-ns`（一客多吃）。
- 提速：`-b/-ub`（prefill），`--spec-*`（decode 白嫖），`--cache-prompt/--cache-reuse`（TTFT）。
- 省显存：`-ngl/-dev/-ts`（放哪），`-ctk/-ctv/-fa`（KV 精度/注意力），`--fit`（自动压缩）。
- 定口味：`--temp/--top-k/--top-p/--min-p` + 惩罚项 + `--samplers` 顺序 + `--grammar/-j`。
- 开服务：`--host/--port/--api-key/--tls` + `--metrics/--props/--slots` + `--jinja/--reasoning-*`。
