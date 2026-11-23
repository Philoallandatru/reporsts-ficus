---
type: Concept
title: "llama.cpp、Strata 与缓存研究归档（28 篇）"
description: "从 lm-llama/research 归档的 llama.cpp 架构、参数手册、多级缓存、文件专家缓存及 Strata 对比研究文档。"
tags:
  - llm
  - llamacpp
  - strata
createdAt: "2026-11-23"
---

# llama.cpp、Strata 与缓存研究归档

本目录归档自 `lm-llama/research/`（保留原路径以维持实验脚本兼容性）：

## 交互式图解
* [llama.cpp 参数说明与性能图解 (HTML)](llamacpp-parameters-handbook.zh-CN.html)
* [KVMem 架构图解 (HTML)](kvmem-architecture.html)

## 研究文档清单
* [AI Infra、KV Cache 与 llama.cpp Prompt Cache 学习地图](ai-infra-kv-cache-llamacpp-learning.md)
* [C++ KV Cache、vLLM 与 SGLang 学习方向](kv-cache-vllm-sglang.md)
* [轻量级真实代码库基准测试选项](lightweight-real-codebase-benchmark-options.md)
* [llama.cpp 架构导读（从一次前向传播看懂整个仓库）](llama-cpp-architecture.md)
* [llama.cpp 参数完全指南（小白也能看懂）](llama-cpp-params-guide.md)
* [llama.cpp 完整公共参数注册表](llamacpp-all-parameters-catalog.md)
* [llama.cpp 在单卡 RTX 5080 上对 Qwen3.8-27B 的缓存基准测试方案](llamacpp-cache-benchmark-plan.md)
* [llama.cpp 缓存基准测试结果：Qwen3.8-27B on 单卡 RTX 5080](llamacpp-cache-benchmark-results.md)
* [7 天读懂 llama.cpp 文件专家缓存](llamacpp-file-expert-7-day-plan.zh-CN.md)
* [从一次 decode 到 SSD：llama.cpp 文件专家源入门](llamacpp-file-expert-beginner.zh-CN.md)
* [llama.cpp 官方基准测试结果](llamacpp-official-bench-results.md)
* [llama.cpp 推理性能参数：源码证据与调参边界](llamacpp-parameter-performance-evidence.md)
* [llama.cpp 参数说明与性能图解](llamacpp-parameters-handbook.zh-CN.md)
* [llama.cpp 参数说明与性能图解](llamacpp-parameters-performance-guide.md)
* [真实场景 llama.cpp 缓存冒烟测试方案](llamacpp-realistic-cache-smoke-plan.md)
* [llama.cpp 通用 completion 请求参数完整注册表](llamacpp-request-parameters.md)
* [llama.cpp Slot、Prompt Cache 与同文档反复提问图解](llamacpp-slot-cache-visual-guide.md)
* [借鉴 Strata 的 llama.cpp 超内存模型推理实现计划](llamacpp-strata-out-of-core-plan-20261109.zh-CN.md)
* [面向本机 llama.cpp 的工作集驱动多级缓存设计](llamacpp-tiered-cache-design.md)
* [llama.cpp 类三级缓存：收益验证与调度实现](llamacpp-tiered-cache-evaluation-and-implementation.md)
* [llama.cpp 三级缓存方案：独立第二意见审查](llamacpp-tiered-cache-independent-review.zh-CN.md)
* [llama.cpp 多级缓存：源码能力与实现边界审计](llamacpp-tiered-cache-source-audit.md)
* [llama.cpp 独立工具参数补编](llamacpp-tool-parameters.md)
* [llama.cpp 131K TPS 扫描结果](llamacpp_131k_tps_sweep_summary.md)
* [真实场景 llama.cpp 缓存冒烟测试结果](llamacpp_realistic_cache_smoke_summary.md)
* [LMCache 的生产角色及与 llama.cpp 的类比](lmcache-llamacpp-kv-cache.md)
* [Strata 与 llama.cpp 综合源码区别分析](strata-vs-llamacpp-source-analysis-20261112.zh-CN.md)
* [Strata 与 llama.cpp 源码区别图解（新手向）](strata-vs-llamacpp-visual-guide.zh-CN.md)
