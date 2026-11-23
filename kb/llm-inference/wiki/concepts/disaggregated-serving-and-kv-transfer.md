---
type: Concept
title: Disaggregated Serving 与 KV Transfer
description: Disaggregated serving 把 prefill 和 decode 拆到不同 worker 或不同 GPU 池中。它的动机很直接：prefill
  是大矩阵并行、吞吐型计算；decode 是每步小 batch、读 KV cache、延迟敏感计算。把二者混在同一调度器里，长 prompt 容易拖慢短 decode；拆开后可以分别扩容。
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Disaggregated Serving 与 KV Transfer

Disaggregated serving 把 prefill 和 decode 拆到不同 worker 或不同 GPU 池中。它的动机很直接：prefill 是大矩阵并行、吞吐型计算；decode 是每步小 batch、读 KV cache、延迟敏感计算。把二者混在同一调度器里，长 prompt 容易拖慢短 decode；拆开后可以分别扩容。

## 为什么要分离 prefill 和 decode

| 阶段 | 计算形态 | 资源压力 | 对用户体验的影响 |
|---|---|---|---|
| Prefill | 一次处理 prompt token | 算力、activation、长输入 batch | 决定 TTFT 的大头 |
| Decode | 每步生成新 token | KV cache 读、scheduler、kernel launch | 决定 TPOT / ITL |

在混合服务中，大 prompt prefill 会占用调度周期，让已经开始生成的请求等待。分离后，prefill worker 负责产出 prompt 的 KV cache，decode worker 接收 KV 后继续生成。

## KV transfer 是核心成本

Prefill/decode 分离不是免费午餐。系统必须把 KV cache 从 prefill 侧传到 decode 侧：

```text
transfer bytes ~= prompt_tokens * layers * kv_heads * head_dim * 2 * bytes_per_element
```

这和 [KV cache 与 PagedAttention](kv-cache-and-paged-attention.md) 的单请求 KV 公式一样，只是把“存在显存里”变成“跨进程或跨节点传输”。prompt 越长、层数越多、KV dtype 越大，传输越贵。跨节点时，网络和 RDMA/NVLink/PCIe 拓扑会成为第一等级约束。

## 架构组件

| 组件 | 职责 | 常见参数/配置 |
|---|---|---|
| Prefill worker | 处理 prompt，生成 KV | prefill 并行、chunked prefill、context parallel |
| Decode worker | 接收 KV，逐 token 生成 | decode batch、KV role、KV load failure policy |
| KV connector | KV 传输与加载 | NIXL、LMCache、Mooncake、connector extra config |
| Router / proxy | 选择 prefill/decode worker | 负载均衡、prefix-aware routing、失败重试 |
| KV store | 跨 worker 复用或持久化 | CPU RAM、local SSD、remote KV store、eviction |

## 框架实现对照

| 框架 | 能力 | 相关入口 |
|---|---|---|
| vLLM | experimental disaggregated prefilling、NIXL connector、LMCache/Mooncake examples、KV load failure policy | `kv_transfer_config`、NixlConnector、LMCache connector、proxy examples |
| SGLang | PD disaggregation，把 prefill 和 decode 服务器分离 | `--disaggregation-mode`、prefill/decode launch 参数、router 配置 |
| TensorRT-LLM | disaggregated serving 与 KV cache transfer | `trtllm-serve` YAML、KV cache connector、leader/orchestrator/worker 拓扑 |
| LMCache | 独立 KV cache 管理层，可让多个 engine 共享和复用 KV | `LMCacheMPConnector`、L1/L2 storage、CPU RAM/local storage/remote KV |
| NVIDIA Dynamo / NIXL | Dynamo 是上层编排框架；NIXL 是低延迟数据传输库 | vLLM/SGLang/TensorRT-LLM backend、KV-aware routing、multi-tier KV cache、NIXL transport |

## 调参判断

### 什么时候适合分离

- prompt 很长、输出相对短，例如 RAG、代码库问答、长文档抽取。
- TTFT 被 prefill 长尾拖慢，但 TPOT 本身可接受。
- GPU 池可以按 prefill/decode 不同形态分别扩容。
- 公共前缀和多轮对话有明显 KV 复用空间。

### 什么时候不适合

- prompt 很短，KV transfer 的固定成本吃掉收益。
- 网络拓扑弱，跨节点 KV 传输比本地 prefill 更慢。
- 请求高度随机，没有 prefix reuse，且输出很长。
- 系统还没有稳定的 admission control、metrics 和失败恢复。

### 排障信号

| 症状 | 可能原因 | 处理 |
|---|---|---|
| TTFT 没降反升 | KV transfer 慢、prefill chunk 太碎、router 排队 | 检查 transfer bandwidth、分桶长 prompt、减少跨节点跳转 |
| decode 中断或 fallback | KV load failure、connector 配置不一致 | 检查 KV role、failure policy、连接器兼容矩阵 |
| cache 命中率低 | tokenizer/template 或 hash key 不一致 | 固定 template、revision、tokenizer，记录 prefix hash |
| 多轮对话收益不稳定 | KV 只单向传输，decode 产生的新 KV 没回写 | 检查 bidirectional KV transfer 支持和限制 |

## 与其他机制的关系

- [Offload 与内存层级](offload-and-memory-hierarchy.md)：KV transfer 常和 CPU/SSD/远端 KV store 组成层级。
- [生产服务与运维控制面](production-serving-operations.md)：没有 router、metrics、失败策略，分离式服务很难稳定。
- [长上下文推理](long-context-inference.md)：上下文越长，prefill/decode 分离越有吸引力，但 KV transfer 也越贵。
- [容量规划公式](capacity-planning-formulas.md)：先算 KV bytes，再判断网络和显存是否能承受。

## 关键来源

- vLLM Disaggregated Prefilling: https://docs.vllm.ai/en/stable/features/disagg_prefill/
- vLLM NixlConnector Usage Guide: https://docs.vllm.ai/en/stable/features/nixl_connector_usage/
- vLLM NixlConnector Compatibility Matrix: https://docs.vllm.ai/en/stable/features/nixl_connector_compatibility/
- vLLM NVIDIA Dynamo integration: https://docs.vllm.ai/en/stable/deployment/integrations/dynamo/
- SGLang PD Disaggregation: https://docs.sglang.io/docs/advanced_features/pd_disaggregation
- TensorRT-LLM Disaggregated Serving: https://nvidia.github.io/TensorRT-LLM/features/disagg-serving.html
- LMCache documentation: https://docs.lmcache.ai/
- LMCache Dynamic Connector: https://docs.lmcache.ai/api_reference/dynamic_connector.html
- LMCache CPU RAM backend: https://docs.lmcache.ai/kv_cache/cpu_ram.html
- LMCache disaggregated prefill quickstart: https://docs.lmcache.ai/getting_started/quickstart/disaggregated_prefill.html
- NVIDIA Dynamo: https://developer.nvidia.com/dynamo
- NVIDIA Dynamo documentation: https://docs.nvidia.com/dynamo/latest/
- Dynamo GitHub: https://github.com/ai-dynamo/dynamo
- NIXL GitHub: https://github.com/ai-dynamo/nixl
- NIXL docs: https://github.com/ai-dynamo/nixl/blob/main/docs/nixl.md
- DistServe paper: https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin
