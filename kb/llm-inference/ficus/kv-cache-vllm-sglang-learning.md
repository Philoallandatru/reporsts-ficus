---
type: Learning Guide
title: C++ KV Cache、vLLM 与 SGLang 学习路线
description: 从实现、索引、调度和指标学习 KV Cache 复用。
summary: 从实现、索引、调度和指标学习 KV Cache 复用
tags:
- llm
- kv-cache
- inference
- vllm
- sglang
sources:
- session: 2026-09-02 C++ KV Cache、vLLM 与 SGLang 学习资料整理
- C:/Users/Administrator/Documents/Code/my-code/lm-llama/research/kv-cache-vllm-sglang.md
- https://arxiv.org/abs/2309.06180
- https://arxiv.org/abs/2312.07104
- https://github.com/vllm-project/vllm/blob/main/docs/design/prefix_caching.md
- https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/radix_cache.py
createdAt: '2026-09-02'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# C++ KV Cache、vLLM 与 SGLang 学习路线

**学习 KV Cache 要从 prefill/decode 语义开始，再进入 C++ 内存布局、vLLM 的分页块复用、SGLang 的 radix tree 复用，最后用 TTFT 和命中 token 数验证收益。**

## 背景 / 为什么

这次会话要解决的问题是：如果想学习 C++ 层面的 KV Cache 处理、KV cache 命中率/复用率优化，并关联到 vLLM 和 SGLang，应该从哪些方向收集资料和安排学习。

最终产物是一份研究笔记：`lm-llama/research/kv-cache-vllm-sglang.md`。它只采用一手来源，包括 vLLM 官方文档/源码/论文、SGLang 官方文档/源码/论文、PagedAttention、RadixAttention、FlashAttention、CUDA/NVIDIA 文档、Hugging Face Transformers 文档，以及本仓库 `llama.cpp` 源码。

## 核心内容

KV cache 的基础直觉是：自回归模型生成每个新 token 时都需要访问历史 token 的 attention key/value。prefill 阶段把输入 prompt 写成 KV cache，decode 阶段读取历史 KV 并追加新 token 的 KV。前缀缓存主要减少重复 prefill，所以最直接改善的是 TTFT，而不是长输出阶段每个 decode token 的速度。

C++ 学习入口建议放在 `llama.cpp`：`llama-kv-cache.*` 展示 KV cache 的 cell/sequence 管理、slot 准备、K/V storage 访问、copy、shift、state save/read；server 层的 `cache_prompt`、`--cache-reuse`、`--slot-save-path` 展示了 request 级复用、非开头 chunk 复用尝试、slot KV 保存/恢复等机制。

vLLM 的主线是 PagedAttention 和 hash-based automatic prefix caching。PagedAttention 把每个请求的 KV cache 切成固定大小块，逻辑块映射到物理块。prefix caching 用 `parent hash + block tokens + extra hashes` 标识完整 KV block；extra hashes 可以包含 LoRA ID、多模态输入 hash、cache salt 等。vLLM 只缓存 full blocks，所以 block size 会影响可复用边界。

SGLang 的主线是 RadixAttention 和 HiCache。RadixAttention 用 radix tree 对 token 前缀做最长前缀匹配，适合结构化程序、多轮调用、共享 prompt 的复用。HiCache 把 L1/L2/L3 分别映射到 GPU memory、host memory、storage backend，用更大容量提高复用机会，但必须付出搬运和预取成本。

命中率优化要拆成几个问题看：prompt 是否稳定、block/page size 是否适合 workload、请求是否被路由到有缓存的 worker、cache pressure 下可复用 KV 是否被驱逐、分层缓存搬运是否比重算便宜、VLM/LoRA/prompt embedding 的 cache identity 是否安全。

## ASCII 图表

```text
KV Cache 学习路线

[模型语义]
  prefill -> write K/V
  decode  -> read old K/V + append new K/V
        |
        v
[C++ runtime]
  llama.cpp: llama_kv_cache, sequence state, slot cache
        |
        v
[块化 KV]
  vLLM: PagedAttention, block table, full-block hash
        |
        v
[前缀索引]
  SGLang: RadixAttention, radix tree, longest prefix match
        |
        v
[生产优化]
  routing + eviction + hierarchy + metrics + security
```

```text
命中率不等于收益

cache_hit_value = saved_prefill_time
                - lookup_time
                - transfer_time
                - restore/dequant_time
                - sync_wait

只有结果明显为正，cache hit 才是真正的性能收益。
```

## 关键要点

- KV cache 复用主要减少 prefill 和 TTFT；decode 很长时，总延迟收益会被稀释。
- vLLM 适合学习 block/page allocator、block table、full-block hash、ref count、free queue、LRU eviction、cache salt。
- SGLang 适合学习 radix tree 前缀匹配、session-aware retention、UnifiedRadixCache、HiCache 分层缓存。
- C++ 实现方向先从 `llama.cpp/src/llama-kv-cache.*` 和 `llama.cpp/include/llama.h` 的 state API 入手。
- 提高命中率的最高 ROI 往往在应用层：稳定 system prompt、tool schema、RAG 文档顺序、chat template 和多轮历史序列化。
- 对 VLM 和 LoRA 场景，cache key 必须包含非 token 身份信息，例如 media hash、LoRA id、cache salt，否则可能错误共享 KV。
- 指标不要只看 hit rate；至少要同时看 cached tokens、TTFT、prefill tokens/sec、decode tokens/sec、KV usage、eviction 和 offload/prefetch latency。

## 相关

- [[kv-cache-vllm-sglang-learning]] — 本知识点的完整学习路线总结
- `lm-llama/research/kv-cache-vllm-sglang.md` — 会话中生成的完整资料收集文档
- `lm-llama/research/lmcache-llamacpp-kv-cache.md` — 相关的 LMCache 与 llama.cpp KV cache 类比研究
