---
type: Concept
title: C++ KV Cache、vLLM 与 SGLang 学习方向
description: 'Date: 2026-09-02'
tags:
- llm
- llamacpp
- kv-cache
sources:
- c:/Users/Administrator/Documents/Code/my-code/lm-llama/research/kv-cache-vllm-sglang.md
createdAt: '2026-11-23'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# C++ KV Cache、vLLM 与 SGLang 学习方向

Date: 2026-09-02

本笔记只依赖一手资料：vLLM 官方文档/源码/论文、SGLang 官方文档/源码/论文、FlashAttention/PagedAttention/RadixAttention 相关论文或官方仓库、NVIDIA/CUDA 官方资料、Hugging Face Transformers 官方文档/源码，以及本仓库 `llama.cpp` 源码。

## 学习路线

1. 先建立 KV cache 的基础心智模型：自回归解码会重复使用历史 token 的 key/value；cache 的核心收益是减少重复 prefill 计算，而不是直接加速长输出阶段的每个 decode token。[Hugging Face Transformers KV cache docs](https://huggingface.co/docs/transformers/main/en/kv_cache), [vLLM Automatic Prefix Caching docs](https://github.com/vllm-project/vllm/blob/main/docs/features/automatic_prefix_caching.md)

2. 再学习“连续 KV”到“分页/块化 KV”的转变：PagedAttention 把每个请求的 KV cache 切成固定大小的块，逻辑块映射到非连续物理块，从而降低碎片并允许共享前缀块。[PagedAttention paper](https://arxiv.org/abs/2309.06180), [vLLM Paged Attention kernel doc](https://docs.vllm.ai/en/v0.21.0/design/paged_attention/), [vLLM prefix caching design](https://github.com/vllm-project/vllm/blob/main/docs/design/prefix_caching.md)

3. 接着对比两种主流复用索引：vLLM 的哈希块索引和 SGLang 的 radix tree 索引。vLLM 用 `parent hash + block tokens + extra hashes` 标识完整 KV 块；SGLang/RadixAttention 用 radix tree 在请求 token 序列上做最长前缀匹配。[vLLM prefix caching design](https://github.com/vllm-project/vllm/blob/main/docs/design/prefix_caching.md), [SGLang paper](https://arxiv.org/abs/2312.07104), [SGLang RadixCache source](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/radix_cache.py)

4. 然后进入实现层：读 vLLM `KVCacheManager`、`BlockPool`、`kv_cache_utils`，读 SGLang `RadixCache`、`UnifiedRadixCache`、`memory_pool`，再读本仓库 `llama.cpp/src/llama-kv-cache.*`。这些源码分别代表“服务端 Python 调度 + CUDA kernel”、“radix 前缀树 + memory pool”、“C++/ggml 本地推理 KV 管理”三类实现路径。[vLLM KV cache manager source](https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/kv_cache_manager.py), [vLLM block pool source](https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/block_pool.py), [vLLM kv cache utils source](https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/kv_cache_utils.py), [SGLang memory pool source](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/memory_pool.py), llama.cpp KV cache header (`../llama.cpp/src/llama-kv-cache.h`), llama.cpp KV cache implementation (`../llama.cpp/src/llama-kv-cache.cpp`)

5. 最后学习命中率/复用率优化：请求路由、系统 prompt 稳定化、块大小、完整块比例、eviction、session-aware retention、分层缓存、host/offload、quantized KV、metrics 和安全隔离都影响最终收益。[vLLM prefix caching design](https://github.com/vllm-project/vllm/blob/main/docs/design/prefix_caching.md), [SGLang Session-Aware Radix Cache](https://docs.sglang.io/docs/advanced_features/session_radix_cache), [SGLang HiCache design](https://docs.sglang.io/docs/advanced_features/hicache_design), [TensorRT-LLM KV cache reuse](https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html)

## 核心概念

KV cache 是 Transformer attention 中历史 token 的 key/value 张量缓存。自回归生成每一步都依赖此前 token；缓存这些 key/value 可以避免每一步重新计算历史 token 的 attention 输入。[Hugging Face Transformers KV cache docs](https://huggingface.co/docs/transformers/main/en/kv_cache)

Prefill 是把输入 prompt 变成 KV cache 的阶段；decode 是逐 token 生成新输出的阶段。前缀缓存主要减少 shared prefix 的 prefill 计算；如果请求不共享前缀，或延迟主要来自很长的输出 decode，收益会明显下降。[vLLM Automatic Prefix Caching docs](https://github.com/vllm-project/vllm/blob/main/docs/features/automatic_prefix_caching.md), [TensorRT-LLM KV cache reuse](https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html)

Paged/block KV cache 把 token 序列切成固定大小块，服务端维护逻辑块到物理块的映射；attention kernel 根据 block table 读取非连续 KV。PagedAttention 论文把这个设计类比为操作系统分页，vLLM 的 kernel 文档也明确其 attention kernel 适配 paged KV cache。[PagedAttention paper](https://arxiv.org/abs/2309.06180), [vLLM Paged Attention kernel doc](https://docs.vllm.ai/en/v0.21.0/design/paged_attention/)

Prefix caching 的关键是“可判定同一前缀是否产生同一 KV”。vLLM 用哈希标识完整块；SGLang 用 radix tree 保存 token 前缀路径；TensorRT-LLM 也要求请求以相同 partial prompt 开始时才复用 KV cache state。[vLLM prefix caching design](https://github.com/vllm-project/vllm/blob/main/docs/design/prefix_caching.md), [SGLang paper](https://arxiv.org/abs/2312.07104), [TensorRT-LLM KV cache reuse](https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html)

命中率不等于收益。有效收益取决于命中的 token 长度、被跳过的 prefill 成本、缓存查找/搬运/反量化成本、GPU/CPU/网络带宽、eviction 造成的失效率，以及输出 decode 是否成为主导瓶颈。[vLLM Automatic Prefix Caching docs](https://github.com/vllm-project/vllm/blob/main/docs/features/automatic_prefix_caching.md), [Hugging Face cache offloading docs](https://huggingface.co/docs/transformers/main/en/kv_cache), [TensorRT-LLM KV cache reuse](https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html)

## vLLM 方向

vLLM 的第一条主线是 PagedAttention。PagedAttention 把 KV cache 组织成固定 token 数的块，按需分配物理块，减少为最大长度预留连续 KV 空间带来的浪费，并使多个请求可以共享相同前缀的物理块。[PagedAttention paper](https://arxiv.org/abs/2309.06180), [vLLM Paged Attention kernel doc](https://docs.vllm.ai/en/v0.21.0/design/paged_attention/)

vLLM 的第二条主线是 hash-based automatic prefix caching。官方设计文档说明：每个完整 KV block 的 hash 由 parent hash、block token tuple 和 extra hashes 组成；extra hashes 可包含 LoRA ID、多模态输入 hash、cache salt 等，且 vLLM 只缓存 full blocks。[vLLM prefix caching design](https://github.com/vllm-project/vllm/blob/main/docs/design/prefix_caching.md)

vLLM 的第三条主线是 KV cache manager 的数据结构和调度接口。官方设计文档把 V1 prefix caching 放在 `KVCacheManager` 中，核心对象包括 `KVCacheBlock`、block pool、free block queue、hash 到 block ID 的 cache blocks、request 到 block ID 的 request blocks；新请求先通过 `get_computed_blocks()` 找可复用块，再通过 `allocate_slots()` touch 命中块并分配新块。[vLLM prefix caching design](https://github.com/vllm-project/vllm/blob/main/docs/design/prefix_caching.md), [vLLM KVCacheManager source](https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/kv_cache_manager.py), [vLLM BlockPool source](https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/block_pool.py)

vLLM 的第四条主线是 hybrid KV cache。对 full attention、sliding window attention、Mamba 等混合模型，vLLM 会按 KV cache group 管理缓存，并在 prefix caching 时对不同 group 的命中前缀取交集；这意味着“命中多少 token”不是只看一种 attention 层，还要看模型结构和 group 管理策略。[vLLM Hybrid KV Cache Manager](https://github.com/vllm-project/vllm/blob/main/docs/design/hybrid_kv_cache_manager.md)

vLLM 的第五条主线是可观测性。vLLM metrics 设计文档说明 prefix cache hit rate 已经转成 queries/hits counters，而不是单个 hit-rate gauge；做命中率优化时应保存原始 counters、TTFT、prefill tokens、decode tokens，而不是只看百分比。[vLLM metrics design](https://github.com/vllm-project/vllm/blob/main/docs/design/metrics.md), [vLLM per-request metrics docs](https://docs.vllm.ai/en/latest/features/per_request_metrics/)

建议读源码顺序：

- `vllm/v1/core/kv_cache_utils.py`：理解 `BlockHash`、哈希组成、cache salt、extra hash 与完整块边界。[source](https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/kv_cache_utils.py)
- `vllm/v1/core/block_pool.py`：理解 block 生命周期、free queue、LRU eviction 与 ref count。[source](https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/block_pool.py)
- `vllm/v1/core/kv_cache_manager.py`：理解 scheduler 如何查询 computed blocks、分配 slots、释放 blocks。[source](https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/kv_cache_manager.py)
- `docs/design/prefix_caching.md` 与 `docs/design/hybrid_kv_cache_manager.md`：把源码行为映射回设计约束。[prefix caching](https://github.com/vllm-project/vllm/blob/main/docs/design/prefix_caching.md), [hybrid KV cache](https://github.com/vllm-project/vllm/blob/main/docs/design/hybrid_kv_cache_manager.md)

## SGLang 方向

SGLang 的核心学习点是 RadixAttention。SGLang 论文把 RadixAttention 描述为自动复用 KV cache 的机制：运行时维护 radix tree，用 prompt/token 前缀做匹配，从而在多调用、结构化程序、多轮场景里复用 shared prefix。[SGLang paper](https://arxiv.org/abs/2312.07104), [SGLang RadixCache source](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/radix_cache.py)

SGLang 的基础内存模型分两层：`ReqToTokenPool` 把请求映射到 token 位置，`TokenToKVPoolAllocator` 管理 KV cache 物理索引，实际 KV cache 持有物理 key/value 张量。这适合用来学习“请求级逻辑 token 表”和“物理 KV pool”如何分离。[SGLang memory_pool.py](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/memory_pool.py)

SGLang 的现代方向是 `UnifiedRadixCache`。官方组件 README 说明它用一个 radix tree 统一 Full attention、SWA 和 Mamba/SSM 缓存；各组件负责物理资源、锁引用、evictable/protected size 和 cascade eviction。[SGLang Unified Radix Cache README](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/unified_cache/components/README.md), [SGLang UnifiedRadixCache source](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/unified_radix_cache.py)

SGLang 的 session-aware radix cache 适合研究“长生命周期会话下如何提高命中率”。官方文档说明它只由 `UnifiedRadixCache` 实现；应用必须在同一会话的请求里传相同 `session_id`；session 引用是 soft protection 而不是 pin，eviction 会先驱逐未引用 KV，再考虑被 active session 引用较少的 KV。[SGLang Session-Aware Radix Cache](https://docs.sglang.io/docs/advanced_features/session_radix_cache)

SGLang 的 HiCache 适合研究“缓存容量如何影响复用率”。官方设计把 L1 定义为 GPU memory，L2 定义为 host memory，L3 定义为 storage backend；L1/L2 是单个 inference instance 私有，跨实例共享只能通过配置为共享范围的 L3 backend。[SGLang HiCache design](https://docs.sglang.io/docs/advanced_features/hicache_design), [SGLang HiCache best practices](https://docs.sglang.io/docs/advanced_features/hicache_best_practices)

SGLang 的 quantized KV cache 适合研究“更大容量和 kernel 支持之间的 trade-off”。官方文档说明 FP8/FP4 KV cache 可以增加可缓存 token 数，但如果 attention backend 不能 fused dequantize，吞吐可能严重下降，抵消内存收益。[SGLang Quantized KV Cache](https://docs.sglang.io/docs/advanced_features/quantized_kv_cache)

SGLang 暴露 `sglang:cache_hit_rate`、`sglang:prompt_tokens_total`、`sglang:token_usage`、TTFT histogram 等 Prometheus metrics；命中率优化必须同时观察 cache hit、token usage 和 TTFT，而不能只看某一项。[SGLang Production Metrics](https://docs.sglang.io/docs/references/production_metrics)

建议读源码顺序：

- `python/sglang/srt/mem_cache/base_prefix_cache.py`：先看 prefix cache 的抽象输入输出，如 `MatchPrefixParams`、`MatchResult`、`EvictParams`。[source](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/base_prefix_cache.py)
- `python/sglang/srt/mem_cache/radix_cache.py`：看 radix tree 节点、最长前缀匹配、引用计数和 eviction。[source](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/radix_cache.py)
- `python/sglang/srt/mem_cache/memory_pool.py`：看请求到 token、token 到 KV 物理池的映射。[source](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/memory_pool.py)
- `python/sglang/srt/mem_cache/unified_radix_cache.py` 与 `unified_cache/components/README.md`：看 Full/SWA/Mamba 多组件统一缓存。[source](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/unified_radix_cache.py), [README](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/unified_cache/components/README.md)
- `python/sglang/srt/mem_cache/storage/lmcache/lmc_radix_cache.py`：看外部 KV cache connector 如何挂到 radix cache 的 match/store/retrieve 流程上。[source](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/storage/lmcache/lmc_radix_cache.py)

## C++/CUDA 实现方向

C++ 侧先读本仓库的 `llama.cpp`。`llama_kv_cache` 实现了 KV cache 的 cell/sequence 管理、slot 准备、K/V storage 访问、K/V copy、shift、state save/read 等；它是学习 C++ 层 KV cache 生命周期的直接入口。llama.cpp KV cache header (`../llama.cpp/src/llama-kv-cache.h`), llama.cpp KV cache implementation (`../llama.cpp/src/llama-kv-cache.cpp`)

`llama.cpp` 的 server 层展示了面向请求的复用接口：`cache_prompt` 表示复用上一请求 KV cache 的公共前缀，`--cache-reuse` 可尝试复用非开头 chunks 并通过 KV shifting 调整位置，`--slot-save-path` 提供 slot KV cache 的保存/恢复路径，`--kv-unified` 提供多 sequence 共享 KV buffer 的模式。llama.cpp server README (`../llama.cpp/tools/server/README.md`), llama.cpp server context (`../llama.cpp/tools/server/server-context.cpp`), llama.cpp CLI args (`../llama.cpp/common/arg.cpp`)

`llama.cpp` 的 public state API 可保存/恢复完整 context 或单个 sequence state；这对学习“原始 KV tensor chunk 协议”和“opaque state blob 协议”的差异很有价值。前者要求外部系统理解每层 K/V 布局，后者只要求同一 engine 能解释序列化状态。llama.cpp public API (`../llama.cpp/include/llama.h`), llama.cpp state implementation (`../llama.cpp/src/llama-context.cpp`)

CUDA 侧要先补 GPU memory model。CUDA 官方文档说明线程可访问寄存器、local、shared、global、constant、texture 等内存空间；CUDA Best Practices 强调 global memory coalescing，且对 compute capability 6.0+ 可按 32-byte transaction 理解 warp 访问合并。这直接影响 paged KV kernel 的物理布局和读取方式。[CUDA C++ Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/), [CUDA C++ Best Practices Guide](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)

FlashAttention 侧重点是 attention kernel 如何减少 HBM 读写。FlashAttention 官方 repo 对应 IO-aware exact attention 论文；其 `flash_attn_with_kvcache` 接口支持在同一个 kernel 里原地更新 K/V cache 并对更新后的 cache 做 attention，还暴露 `block_table` 参数用于 paged KV cache 场景。[FlashAttention paper](https://arxiv.org/abs/2205.14135), [FlashAttention README](https://github.com/Dao-AILab/flash-attention/blob/main/README.md), [FlashAttention interface source](https://github.com/Dao-AILab/flash-attention/blob/main/flash_attn/flash_attn_interface.py)

NVIDIA TensorRT-LLM 是另一个官方 C++/GPU 系统参照。其 KV cache reuse 文档明确：KV cache pages 可被相同 prompt 开头的请求共享；reuse 需要 paged context attention；只有完整 blocks 可共享；block size 是 kernel 效率和复用概率之间的权衡；host offloading 可延长可复用块寿命但有 CPU/GPU copy 成本。[TensorRT-LLM KV cache reuse](https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html)

实现练习建议：

- 写一个最小 C++ `PagedKVCache`：固定 `block_size`、free list、logical-to-physical table、append、gather、evict；用 CPU tensor 或普通数组验证输出不变。设计参考来自 PagedAttention 和 vLLM/TensorRT-LLM 的 block table 思路。[PagedAttention paper](https://arxiv.org/abs/2309.06180), [vLLM Paged Attention kernel doc](https://docs.vllm.ai/en/v0.21.0/design/paged_attention/), [TensorRT-LLM KV cache reuse](https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html)
- 在 C++ 中加 block hash：`parent_hash + token_ids + extra_key`，只在 block full 后进入 hash table；验证 partial block 不命中。这直接对应 vLLM 设计和 TensorRT-LLM 对 full blocks 的要求。[vLLM prefix caching design](https://github.com/vllm-project/vllm/blob/main/docs/design/prefix_caching.md), [TensorRT-LLM KV cache reuse](https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html)
- 加 radix tree 版本：支持最长前缀匹配、split node、lock/ref count、LRU eviction；对照 SGLang `RadixCache` 与 `UnifiedRadixCache`。[SGLang RadixCache source](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/radix_cache.py), [SGLang UnifiedRadixCache source](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/unified_radix_cache.py)
- 加 CUDA kernel 读取练习：把 K/V cache 布局成 `[block, head, token_in_block, head_dim]` 或 page-first 布局，测 coalesced load、shared memory staging、`cudaMemcpyAsync`/pinned host memory 的影响。[CUDA Best Practices Guide](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html), [CUDA async execution](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/asynchronous-execution.html)

## 命中率/复用率优化方向

稳定 prompt 前缀是最高 ROI 的应用层优化。系统 prompt、工具描述、RAG 文档模板、few-shot 示例、chat template 应尽量固定顺序和 tokenization；vLLM 和 TensorRT-LLM 都要求请求共享相同开头才能复用 prefix KV。[vLLM Automatic Prefix Caching docs](https://github.com/vllm-project/vllm/blob/main/docs/features/automatic_prefix_caching.md), [TensorRT-LLM KV cache reuse](https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html)

调块大小时要同时看 kernel 效率和命中概率。块越大，kernel 和 metadata 开销可能更低，但只有完整块能复用，较大的 block size 会降低 partial prefix 的可复用比例；TensorRT-LLM 明确把 tokens per block 描述为效率与复用概率的 trade-off，vLLM 也只缓存 full blocks。[TensorRT-LLM KV cache reuse](https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html), [vLLM prefix caching design](https://github.com/vllm-project/vllm/blob/main/docs/design/prefix_caching.md)

路由和调度会影响命中率。多副本部署中，请求如果被随机打散，L1/GPU 私有缓存命中率会下降；SGLang HiCache 明确 L1/L2 是 instance-private，跨实例共享必须依赖 L3 storage backend；TensorRT-LLM 也指出共享 prompt 的第二个请求只有在第一个请求完成并留下可复用状态后才会复用。[SGLang HiCache design](https://docs.sglang.io/docs/advanced_features/hicache_design), [TensorRT-LLM KV cache reuse](https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html)

Session-aware retention 适合多轮 agent/chat。SGLang 文档说明 session-aware radix cache 会把 reusable KV 注册到 `session_id`，eviction 优先驱逐未引用 KV；这可以在内存压力下提高长生命周期会话的命中概率，但不是硬 pin，内存不足时仍可驱逐。[SGLang Session-Aware Radix Cache](https://docs.sglang.io/docs/advanced_features/session_radix_cache)

分层缓存提升复用率的前提是搬运成本低于重算成本。SGLang HiCache 把 L1/L2/L3 分别映射到 GPU/host/storage；TensorRT-LLM host offloading 会延长 reusable blocks 生命周期，但也明确存在 CPU/GPU copy 成本；Hugging Face offloaded cache 也说明吞吐可能因 K/V 搬运下降。[SGLang HiCache design](https://docs.sglang.io/docs/advanced_features/hicache_design), [TensorRT-LLM KV cache reuse](https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html), [Hugging Face KV cache docs](https://huggingface.co/docs/transformers/main/en/kv_cache)

KV quantization 是容量优化，不是无条件提速。SGLang 官方文档警告：如果 chosen attention backend 不支持 fused quantized KV，反量化可能非常慢；Hugging Face 也提示短上下文或 GPU 内存足够时，quantized cache 可能伤害 latency。[SGLang Quantized KV Cache](https://docs.sglang.io/docs/advanced_features/quantized_kv_cache), [Hugging Face KV cache docs](https://huggingface.co/docs/transformers/main/en/kv_cache)

安全隔离也属于复用策略。vLLM 的设计文档说明 `cache_salt` 会注入第一个 block hash，使只有相同 salt 的请求共享缓存，用于减少多租户环境中通过 latency 观察推断缓存内容的风险。[vLLM prefix caching design](https://github.com/vllm-project/vllm/blob/main/docs/design/prefix_caching.md)

指标应至少包含：prefix cache queries、prefix cache hits、命中 token 数或可跳过 prefill token 数、TTFT、prefill tokens/sec、decode tokens/sec、KV cache usage、eviction 次数、offload/prefetch latency。vLLM 指标设计强调 counters，SGLang 暴露 cache hit rate、prompt tokens、token usage 和 TTFT histogram。[vLLM metrics design](https://github.com/vllm-project/vllm/blob/main/docs/design/metrics.md), [SGLang Production Metrics](https://docs.sglang.io/docs/references/production_metrics)

## 推荐阅读顺序

1. Hugging Face `Cache strategies`：先理解 Dynamic/Static/Offloaded/Quantized cache，以及 cache 对 generation 的基本作用。[docs](https://huggingface.co/docs/transformers/main/en/kv_cache), [cache_utils.py](https://github.com/huggingface/transformers/blob/main/src/transformers/cache_utils.py)

2. PagedAttention 论文：理解为什么 KV cache 需要块化、分页、共享和按需分配。[paper](https://arxiv.org/abs/2309.06180)

3. vLLM prefix caching design：理解 hash-based block reuse、full block、extra hash、LRU/free queue、cache salt。[docs](https://github.com/vllm-project/vllm/blob/main/docs/design/prefix_caching.md)

4. vLLM V1 KV cache 源码：`kv_cache_utils.py` -> `block_pool.py` -> `kv_cache_manager.py`。[utils](https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/kv_cache_utils.py), [block pool](https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/block_pool.py), [manager](https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/kv_cache_manager.py)

5. SGLang 论文与 `RadixCache`：理解 RadixAttention、最长前缀匹配、树结构复用。[paper](https://arxiv.org/abs/2312.07104), [source](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/radix_cache.py)

6. SGLang `UnifiedRadixCache`、Session-Aware Radix Cache、HiCache：理解混合 attention/state、session retention、L1/L2/L3 层级。[Unified README](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/unified_cache/components/README.md), [session docs](https://docs.sglang.io/docs/advanced_features/session_radix_cache), [HiCache design](https://docs.sglang.io/docs/advanced_features/hicache_design)

7. FlashAttention repo 与 CUDA Best Practices：理解 kernel 层 IO、paged KV 的 `block_table`、coalescing、shared memory、async copy。[FlashAttention README](https://github.com/Dao-AILab/flash-attention/blob/main/README.md), [CUDA Best Practices](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)

8. 本仓库 `llama.cpp` KV cache：从 C++ 角度读 `llama-kv-cache.*`、server prompt cache、slot save/restore、state API。llama-kv-cache.h (`../llama.cpp/src/llama-kv-cache.h`), llama-kv-cache.cpp (`../llama.cpp/src/llama-kv-cache.cpp`), server README (`../llama.cpp/tools/server/README.md`), llama.h (`../llama.cpp/include/llama.h`)

9. TensorRT-LLM KV cache reuse：用 NVIDIA 官方系统复核 block size、full block、host offload、paged context attention 等工程 trade-off。[docs](https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html)

## 术语表

- KV cache：历史 token 的 key/value 张量缓存，用于避免重复 attention 计算。[Hugging Face docs](https://huggingface.co/docs/transformers/main/en/kv_cache)
- Prefill：处理输入 prompt 并生成初始 KV cache 的阶段；prefix caching 主要减少这个阶段的重复工作。[vLLM APC docs](https://github.com/vllm-project/vllm/blob/main/docs/features/automatic_prefix_caching.md)
- Decode：逐 token 生成输出的阶段；长输出时 prefix cache 对总时延的相对收益会下降。[vLLM APC docs](https://github.com/vllm-project/vllm/blob/main/docs/features/automatic_prefix_caching.md)
- PagedAttention：把 KV cache 分页/块化并通过 block table 间接访问的 attention serving 设计。[PagedAttention paper](https://arxiv.org/abs/2309.06180)
- KV block/page：固定数量 token 的 K/V 存储单元；通常只有完整块才能进入 prefix cache。[vLLM prefix caching design](https://github.com/vllm-project/vllm/blob/main/docs/design/prefix_caching.md), [TensorRT-LLM KV cache reuse](https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html)
- Block table：逻辑 KV 块到物理 KV 块的映射；attention kernel 根据该映射读取非连续 KV。[vLLM Paged Attention kernel doc](https://docs.vllm.ai/en/v0.21.0/design/paged_attention/), [FlashAttention README](https://github.com/Dao-AILab/flash-attention/blob/main/README.md)
- Prefix caching：复用相同 prompt 前缀产生的 KV cache，跳过共享部分的 prefill。[vLLM APC docs](https://github.com/vllm-project/vllm/blob/main/docs/features/automatic_prefix_caching.md)
- RadixAttention：SGLang 用 radix tree 自动管理和复用 KV cache 的机制。[SGLang paper](https://arxiv.org/abs/2312.07104), [SGLang RadixCache source](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/radix_cache.py)
- `UnifiedRadixCache`：SGLang 统一 Full attention、SWA、Mamba/SSM 缓存的组件化 radix cache。[SGLang Unified README](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/unified_cache/components/README.md)
- HiCache：SGLang 的分层 KV cache；L1=GPU memory，L2=host memory，L3=storage backend。[SGLang HiCache design](https://docs.sglang.io/docs/advanced_features/hicache_design)
- Cache salt：vLLM 用于隔离 prefix cache 复用范围的 per-request salt，会进入首个 block hash。[vLLM prefix caching design](https://github.com/vllm-project/vllm/blob/main/docs/design/prefix_caching.md)
- TTFT：time to first token；prefix/KV cache 复用通常最直接改善这个指标。[TensorRT-LLM KV cache reuse](https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html)
- KV quantization：用 FP8/FP4/int 低精度存储 KV cache 以节省容量；必须关注 fused dequantize/kernel 支持和精度影响。[SGLang Quantized KV Cache](https://docs.sglang.io/docs/advanced_features/quantized_kv_cache), [Hugging Face KV cache docs](https://huggingface.co/docs/transformers/main/en/kv_cache)

## 参考资料

### vLLM

- vLLM Automatic Prefix Caching feature docs: https://github.com/vllm-project/vllm/blob/main/docs/features/automatic_prefix_caching.md
- vLLM Prefix Caching design: https://github.com/vllm-project/vllm/blob/main/docs/design/prefix_caching.md
- vLLM Hybrid KV Cache Manager design: https://github.com/vllm-project/vllm/blob/main/docs/design/hybrid_kv_cache_manager.md
- vLLM Paged Attention kernel doc: https://docs.vllm.ai/en/v0.21.0/design/paged_attention/
- vLLM Metrics design: https://github.com/vllm-project/vllm/blob/main/docs/design/metrics.md
- vLLM `kv_cache_utils.py`: https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/kv_cache_utils.py
- vLLM `block_pool.py`: https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/block_pool.py
- vLLM `kv_cache_manager.py`: https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/kv_cache_manager.py
- PagedAttention paper: https://arxiv.org/abs/2309.06180

### SGLang

- SGLang paper: https://arxiv.org/abs/2312.07104
- SGLang RadixCache source: https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/radix_cache.py
- SGLang BasePrefixCache source: https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/base_prefix_cache.py
- SGLang memory pool source: https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/memory_pool.py
- SGLang UnifiedRadixCache source: https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/unified_radix_cache.py
- SGLang Unified Radix Cache component README: https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/unified_cache/components/README.md
- SGLang Session-Aware Radix Cache: https://docs.sglang.io/docs/advanced_features/session_radix_cache
- SGLang HiCache design: https://docs.sglang.io/docs/advanced_features/hicache_design
- SGLang HiCache best practices: https://docs.sglang.io/docs/advanced_features/hicache_best_practices
- SGLang Quantized KV Cache: https://docs.sglang.io/docs/advanced_features/quantized_kv_cache
- SGLang Production Metrics: https://docs.sglang.io/docs/references/production_metrics

### FlashAttention / CUDA / NVIDIA

- FlashAttention paper: https://arxiv.org/abs/2205.14135
- FlashAttention official repo README: https://github.com/Dao-AILab/flash-attention/blob/main/README.md
- FlashAttention interface source: https://github.com/Dao-AILab/flash-attention/blob/main/flash_attn/flash_attn_interface.py
- CUDA C++ Programming Guide: https://docs.nvidia.com/cuda/cuda-programming-guide/
- CUDA C++ Best Practices Guide: https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html
- CUDA async execution: https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/asynchronous-execution.html
- TensorRT-LLM KV cache reuse: https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html
- TensorRT-LLM GPT attention: https://nvidia.github.io/TensorRT-LLM/advanced/gpt-attention.html

### llama.cpp / Hugging Face

- 本仓库 `llama.cpp/src/llama-kv-cache.h`: ../llama.cpp/src/llama-kv-cache.h (`../llama.cpp/src/llama-kv-cache.h`)
- 本仓库 `llama.cpp/src/llama-kv-cache.cpp`: ../llama.cpp/src/llama-kv-cache.cpp (`../llama.cpp/src/llama-kv-cache.cpp`)
- 本仓库 `llama.cpp/include/llama.h`: ../llama.cpp/include/llama.h (`../llama.cpp/include/llama.h`)
- 本仓库 `llama.cpp/src/llama-context.cpp`: ../llama.cpp/src/llama-context.cpp (`../llama.cpp/src/llama-context.cpp`)
- 本仓库 `llama.cpp/tools/server/README.md`: ../llama.cpp/tools/server/README.md (`../llama.cpp/tools/server/README.md`)
- 本仓库 `llama.cpp/tools/server/server-context.cpp`: ../llama.cpp/tools/server/server-context.cpp (`../llama.cpp/tools/server/server-context.cpp`)
- Hugging Face Transformers KV cache docs: https://huggingface.co/docs/transformers/main/en/kv_cache
- Hugging Face Transformers `cache_utils.py`: https://github.com/huggingface/transformers/blob/main/src/transformers/cache_utils.py
