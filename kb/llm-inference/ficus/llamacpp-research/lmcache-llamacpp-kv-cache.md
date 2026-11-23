---
type: Concept
title: LMCache 的生产角色及与 llama.cpp 的类比
description: 日期：2026-08-29
tags:
- llm
- llamacpp
- kv-cache
sources:
- c:/Users/Administrator/Documents/Code/my-code/lm-llama/research/lmcache-llamacpp-kv-cache.md
createdAt: '2026-11-23'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# LMCache 的生产角色及与 llama.cpp 的类比

日期：2026-08-29

本笔记仅使用一手资料：LMCache 文档/源码/博客/论文、用以厘清 prefix caching 的 vLLM 文档、用以厘清相邻 KV cache 系统的 SGLang 源码/文档，以及 llama.cpp 文档/源码。工作区没有现有的研究笔记约定，因此本文件放在 `research/` 下。

## 简短回答

LMCache 最好被理解成服务引擎旁边的一个 KV cache 管理层，而不是推理引擎本身。它提取、存储、检索、传输、观测、有时还会变换 KV cache，这样重复或相关的 prompt 就可以在请求、会话、引擎实例、Pod 之间跳过 prefill 工作，在某些模式下甚至能跨节点或跨 prefill/decode 角色共享。LMCache 将这个角色描述为：把 KV cache 从临时性的、每个请求的引擎 state 转换为可复用、可存储的 state，并在长上下文 agentic 流量、多轮聊天、RAG、多模态输入、CPU/远端 offload、对等共享以及 prefill/decode 解耦场景下报告了收益。LMCache README (`../LMCache/README.md`), [LMCache docs home](https://docs.lmcache.ai/), [LMCache integration docs](https://docs.lmcache.ai/developer_guide/integration.html), LMCache MP overview (`../LMCache/docs/source/mp/index.rst`), LMCache MP P2P docs (`../LMCache/docs/source/mp/p2p.rst`), LMCache MP disaggregated-prefill docs (`../LMCache/docs/source/mp/disaggregated_prefill.rst`)

打个比方，当 llama.cpp 的服务工作负载有大段重复前缀或大段跨轮共享上下文，且超出进程内有效缓存容量时，它理论上可以从一个 LMCache 式的层受益。可预期的收益主要在更低的 time to first token 和更低的 prefill 计算，而不是更快的每 token decode，因为 LMCache 和 vLLM 自带的 automatic prefix caching 针对的都是 prefill 复用，而不是 decode 成本。[vLLM automatic prefix caching docs](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html), LMCache README (`../LMCache/README.md`)

不过，llama.cpp 已经在服务进程内部和通过 state 文件支持了若干 prompt/KV 复用机制。因此，一个 LMCache 式的提案不应被包装成泛泛的"添加 prompt cache"。它应该被包装成：在当前每进程 slot 和 state 机制之外，增加跨请求、跨 slot、跨进程、分层的、可观测的，并且可能解耦 prefill 的 KV 复用。llama.cpp server flags (`../llama.cpp/common/arg.cpp`), llama.cpp server context source (`../llama.cpp/tools/server/server-context.cpp`), llama.cpp public state/session API (`../llama.cpp/include/llama.h`), llama-server development docs (`../llama.cpp/tools/server/README-dev.md`)

## 1. LMCache 在生产服务中的角色

### 在栈中的位置

LMCache 处于服务引擎和存储/传输后端之间作为 cache 中间件。它文档化的集成模型是：引擎连接器查找可复用的 prompt KV，检索匹配的 chunk，让引擎把这些 chunk 注入到它的 KV cache 中，并在计算后存储新的 chunk。LMCache 在集成文档中列出 vLLM 和 SGLang 为支持的引擎，而 README 描述了厂商中立的存储和传输支持。[LMCache integration docs](https://docs.lmcache.ai/developer_guide/integration.html), LMCache README (`../LMCache/README.md`)

在多进程模式下，LMCache 作为独立服务运行，vLLM 实例通过 ZMQ 连接到它。MP 文档说明，每个节点一个 LMCache 服务可以服务多个 vLLM pod，并提供进程隔离、跨 pod 共享缓存、独立的资源伸缩、多层存储和内置可观测性。LMCache MP overview (`../LMCache/docs/source/mp/index.rst`), LMCache MP deployment guide (`../LMCache/docs/source/mp/deployment.rst`)

LMCache 的 MP 架构把工作拆分为多种请求类型，例如 `LOOKUP`、`STORE`、`RETRIEVE`、prefetch 状态查询、management、P2P 和 CacheBlend RPC；它管理 L1 对象、异步 L1 到 L2 store、L2 到 L1 prefetch、eviction，以及 Prometheus/OpenTelemetry 可观测性。LMCache MP overview (`../LMCache/docs/source/mp/index.rst`), LMCache MP configuration (`../LMCache/docs/source/mp/configuration.rst`)

LMCache 支持超出 GPU memory 的分层。README 列出了 CPU RAM、本地盘/SSD、Redis/Valkey、Mooncake、InfiniStore、S3 兼容存储、NIXL 和 GDS 作为支持的存储或传输后端，MP 配置文档描述了 L1 由 pinned DRAM、Device-DAX 或 GPUDirect Storage/NVMe slab 文件支撑。LMCache README (`../LMCache/README.md`), LMCache MP configuration (`../LMCache/docs/source/mp/configuration.rst`), LMCache storage backends docs (`../LMCache/docs/source/kv_cache/storage_backends/index.rst`)

LMCache 也支持 P2P cache 共享。P2P 文档说明，每个节点运行一个 LMCache 服务，cache miss 时可以从对等节点的 L1 memory 读取本地前缀，一个协调者跟踪活跃服务但不查看 KV 数据，默认传输引擎是基于 RDMA 的 NIXL。LMCache MP P2P docs (`../LMCache/docs/source/mp/p2p.rst`)

LMCache 支持 vLLM 部署中的 prefill/decode 解耦。MP disaggregated-prefill 文档描述了一个 prefill 实例计算 prompt KV，一个 decode 实例通过 NIXL 拉取 prompt KV，一个路由器协调请求，LMCache 在当前请求的 prefill-to-decode 传输之上增加跨请求 KV 复用。LMCache MP disaggregated-prefill docs (`../LMCache/docs/source/mp/disaggregated_prefill.rst`)

LMCache 通过 CacheBlend 支持非前缀复用，根据 README 和 MP overview。其实现被描述为复用非前缀缓存的 KV 块并选择性重算 token 以恢复质量，并由服务端配置选择一个 `blend` 引擎模块。LMCache README (`../LMCache/README.md`), LMCache MP overview (`../LMCache/docs/source/mp/index.rst`)

### LMCache 针对的工作负载和环境

LMCache 自己的 README 说它特别针对长上下文 agentic、多轮对话和知识增强（如 RAG）工作负载，因为这些工作负载会反复包含大段共享上下文。LMCache README (`../LMCache/README.md`), [LMCache docs home](https://docs.lmcache.ai/)

LMCache 的集成文档报告多轮对话和 RAG 场景下 TTFT 降低 3x 到 10x，并将 LMCache 描述为透明的 cache 复用加上 GPU 周期节省，但这是宽泛的文档声明，而不是对每个工作负载的保证。[LMCache integration docs](https://docs.lmcache.ai/developer_guide/integration.html)

CPU offload 快速入门演示了 vLLM 与本地 CPU 后端的离线和在线集成，其中重复的 prompt 可以从 CPU 加载 KV 而非重算，并给出当总 KV cache 超过 GPU memory 时第二次运行加速 7.43x 的示例。该示例被标记为相对于 MP 模式是 in-process/已弃用的，因此这个数字应视为教程示例，而非当前 MP 生产基准。LMCache CPU offload quickstart (`../LMCache/docs/source/getting_started/quickstart/offload_kv_cache.rst`)

跨实例共享快速入门演示了两个 vLLM 实例之间的中心化服务和对等共享，包括向不同实例的第二个请求检索由第一个实例填充的 cache。该页面也被标记为相对于 MP 模式是 in-process/已弃用的，因此它有助于理解概念，但不是首选部署形式。LMCache cross-instance sharing quickstart (`../LMCache/docs/source/getting_started/quickstart/share_kv_cache.rst`), LMCache MP P2P docs (`../LMCache/docs/source/mp/p2p.rst`)

LMCache 的多模态文档说明 LMCache 可以加速 vLLM 支持的多模态模型，并给出一个音频工作负载示例：首次请求 50.83 秒，缓存后第二次请求 3.34 秒。这同样是一个被标记为相对于 MP 模式是 in-process/已弃用的示例页面。LMCache multimodality docs (`../LMCache/docs/source/api_reference/multimodality.rst`)

LMCache 官方的 2026 年 AMD MI300X 基准测试文章报告，在 32 用户、100k 上下文、基于 Claude Code agent 轨迹的压力测试中，LMCache CPU-DRAM offload 在 MiniMax-M2.5 上平均 TTFT 低 3.0x、p95 TTFT 低 2.1x、最大 TTFT 低 2.6x、完成请求多 2.3x、输入 933 tok/s 对比 HBM-only prefix cache 的 471 tok/s，并在相同 HBM 预算下多保留 36% 的工作集。同篇文章还报告，在负载较低、working set 能放进 HBM 的情况下，vLLM 的 HBM prefix cache 获胜，LMCache 的开销不划算。[LMCache AMD MI300X benchmark](https://blog.lmcache.ai/en/2026/05/12/benchmarking-lmcache-for-multi-turn-agentic-workloads-on-amd-mi300x/)

LMCache 官方的 2026 年 MP 架构文章报告了 8x NVIDIA H100 80GB 基准测试，使用 Qwen3-235B-A22B-Instruct-2507-FP8 与 vLLM 数据并行和 expert 并行。它报告 LMCache MP 模式相比 in-process offload：平均 TTFT 0.29s vs 3.98s、p99 TTFT 1.30s vs 13.55s、平均 decode 速度 37.47 tok/s vs 9.81 tok/s，文章总结为约 13x 平均 TTFT 降低、超过 10x p99 TTFT 降低和近 4x decode 吞吐增加。[LMCache MP architecture benchmark](https://blog.lmcache.ai/en/2026/04/03/lmcaches-new-architecture-boosts-moe-inference-performance-by-10x/)

LMCache 官方的 Cohere/CoreWeave 文章报告了在 Cohere Command A 上使用 vLLM 和 CoreWeave AI Object Storage 的面向生产的 RAG/远程 cache 基准测试。它报告 TTFT 低 22% 到 32%、解码吞吐比完整 prefill 高 41%、相比 S3 Express 冷 cache 检索提升 1.2x、cache 热时比 S3 Express 快 3x。这是合作伙伴博客声明，而不是此 repo 中可复现的公开基准制品。[LMCache Cohere/CoreWeave post](https://blog.lmcache.ai/en/2025/10/29/breaking-the-memory-barrier-how-lmcache-and-coreweave-power-efficient-llm-inference-for-cohere/)

LMCache 论文摘要说明 LMCache 提取和存储由 vLLM 和 SGLang 生成的 KV cache，在引擎和查询之间共享它们，支持 cache offloading 和 prefill-decode 解耦，暴露用于 pinning、lookup、清理、移动和压缩的控制 API，并在不同工作负载下通过 vLLM 实现高达 15x 的吞吐改进。由于这是 arXiv 预印本，摘要使用"高达"措辞，这个数字应视为该论文评估设置下的上限。[LMCache paper](https://arxiv.org/abs/2510.09665)

### LMCache 并不能神奇地改善什么

LMCache 在 prefill 工作量大且可复用时最直接有用。vLLM 的 automatic prefix caching 文档对 APC 明确说明同样的限制：prefix caching 减少 query/prompt 处理，不减少生成新 token 的时间，因此当回答很长或请求不共享前缀时收益很小。除非部署的系统还改变了调度、解耦或内存压力到足以间接影响 decode 吞吐，否则这个限制类比适用于 LMCache 式的复用。[vLLM automatic prefix caching docs](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html), LMCache README (`../LMCache/README.md`)

## 2. llama.cpp 的类比

### llama.cpp 已经支持的行为

llama.cpp 在非服务端示例中已经有 prompt cache：`--prompt-cache` 把 prompt state 保存到文件以便更快启动，`--prompt-cache-all` 也保存用户输入和生成内容，`--prompt-cache-ro` 以只读方式打开该 cache。llama.cpp server/common flags (`../llama.cpp/common/arg.cpp`)

llama.cpp 暴露了 public state/session API，可以序列化和恢复完整的 context state 或单个 sequence state，包括基于文件的 sequence save/load API 以及用于部分 state 或设备驻留 sequence state 的扩展 flags。llama.cpp public state/session API (`../llama.cpp/include/llama.h`)

`llama-server` 在 common 参数中默认启用 prompt caching，具有 RAM cache 大小默认值，并暴露 flags 用于服务端 prompt caching、通过 KV shifting 的 cache 复用、将空闲 slot 保存到 prompt cache、暴露 slots、以及将 slot KV cache 保存到配置路径。llama.cpp common params (`../llama.cpp/common/common.h`), llama.cpp server/common flags (`../llama.cpp/common/arg.cpp`)

`llama-server` 通过 longest common prefix 使用 prompt 相似性选择空闲 slot，然后可以将旧 prompt 保存到 prompt cache 并加载匹配的 prompt token 用于新任务。llama.cpp server context source (`../llama.cpp/tools/server/server-context.cpp`)

启用请求级 prompt caching 时，`llama-server` 会复用与新 prompt 公共的已计算 token，配合 `--cache-reuse`，它可以尝试通过在 memory 实现支持 shifting 且 prompt 不是多模态的情况下 shifting KV 位置来复用匹配的非开头 chunk。llama.cpp server context source (`../llama.cpp/tools/server/server-context.cpp`), llama.cpp server/common flags (`../llama.cpp/common/arg.cpp`)

`llama-server` 通过序列化 `server_tokens`、调用 `llama_state_seq_save_file`、用 `llama_state_seq_load_file` 加载、验证恢复的 token 并将它们放回目标 slot 来实现 slot save 和 restore。llama.cpp server context source (`../llama.cpp/tools/server/server-context.cpp`), llama.cpp public state/session API (`../llama.cpp/include/llama.h`)

llama.cpp 服务端开发文档描述 `server_context` 持有主 `llama_context` 和活跃 slots，`server_slot` 是个体 sequence，`server_prompt_checkpoint` 是一种机制，为 recurrent/SWA 模型存储快照以复用共享 prompt 前缀。llama-server development docs (`../llama.cpp/tools/server/README-dev.md`)

### 一个类 LMCache 层可以在此之上增加什么

当前的 llama.cpp 机制主要绑定到一个进程的 slots、显式 state 文件或服务端管理的 RAM/state 复用。一个 LMCache 式的层会有质的不同，如果它能为 llama.cpp 提供一个稳定的外部 KV/object 协议，具备 chunk lookup、store、retrieve、eviction、metrics，以及超出单个 `llama-server` 进程的存储分层。这镜像了 LMCache MP 的 `LOOKUP`、`STORE`、`RETRIEVE`、L1/L2、eviction 和可观测性设计，但由于 llama.cpp 当前的 state API 暴露的是序列化引擎 state，而不是 LMCache 的 vLLM/SGLang KV-connector 协议，因此需要 llama.cpp 特定的工程工作。LMCache MP overview (`../LMCache/docs/source/mp/index.rst`), LMCache MP configuration (`../LMCache/docs/source/mp/configuration.rst`), llama.cpp public state/session API (`../llama.cpp/include/llama.h`)

对 llama.cpp 的潜在改进 1：降低错过本地 slot cache 或由不同进程服务的重复长 prompt 的 TTFT。这是合理的，因为 vLLM APC 和 llama.cpp slot prompt caching 都在一个引擎内部跳过共享前缀 prefill，而 LMCache 在可复用 KV 存活于原始引擎进程之外或 HBM 之外时报告了额外价值。不确定性很高，需要测量后才能确定，因为 llama.cpp 的常见部署通常运行一个本地模型服务端，slot 亲和性可能已经捕获了大部分复用。[vLLM automatic prefix caching docs](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html), llama.cpp server context source (`../llama.cpp/tools/server/server-context.cpp`), LMCache MP overview (`../LMCache/docs/source/mp/index.rst`)

对 llama.cpp 的潜在改进 2：通过把旧的 prompt/slot state 从 RAM 或设备 memory 溢出到本地 NVMe 或远端存储来扩大有效缓存容量，然后再恢复它们。LMCache 的文档化价值部分来自 CPU、本地盘、GDS/NVMe 和远端存储分层，而 llama.cpp 已经有 save/load state 原语，如果原始 KV 布局集成过于侵入，这些可以作为不透明 state blob 的桥梁。不确定性在于：对于典型 GGUF 模型和硬件，序列化/反序列化成本、mmap/I/O 带宽、模型特定的 state 兼容性以及验证开销是否仍会比重算更便宜。LMCache README (`../LMCache/README.md`), LMCache MP configuration (`../LMCache/docs/source/mp/configuration.rst`), llama.cpp public state/session API (`../llama.cpp/include/llama.h`)

对 llama.cpp 的潜在改进 3：针对 OpenAI-compatible llama.cpp 服务池的多进程或集群级复用。LMCache P2P 展示了架构目标：每节点 cache 成为逻辑 cache，节点可以从对等节点检索前缀而非重算。对于 llama.cpp，当请求在没有严格 sticky 路由的多个 `llama-server` 进程之间负载均衡时，这点最重要。不确定性很大，因为 llama.cpp 源码当前在此工作区中未暴露像 vLLM 那样的生产 KV connector。LMCache MP P2P docs (`../LMCache/docs/source/mp/p2p.rst`), [LMCache integration docs](https://docs.lmcache.ai/developer_guide/integration.html), llama-server development docs (`../llama.cpp/tools/server/README-dev.md`)

对 llama.cpp 的潜在改进 4：面向大型、对延迟敏感的部署的 prefill/decode 分离。LMCache 的 P/D 文档展示了 vLLM 使用 NIXL 进行当前请求的 prefill-to-decode 移交，而 LMCache 在此之上增加跨请求复用。等价的 llama.cpp 实现将是一个相当大的服务架构变更，而不是一个小的 cache 开关，因为服务端需要一种方式在一个进程/设备中计算 prompt KV，并让另一个进程/设备安全地消费它。LMCache MP disaggregated-prefill docs (`../LMCache/docs/source/mp/disaggregated_prefill.rst`), llama-server development docs (`../llama.cpp/tools/server/README-dev.md`)

对 llama.cpp 的潜在改进 5：更强的生产可观测性和 cache 策略控制。LMCache 文档化了 KV cache 专用指标、Prometheus 端点、事件遥测、quota/policy、eviction 阈值和 lookup-hash 日志。llama.cpp 有 timing 和服务端 metrics flags，但一个 LMCache 式的 cache 服务将使 cache hit/miss、每 token 复用和存储分层行为成为一等运维表面。LMCache README (`../LMCache/README.md`), LMCache MP overview (`../LMCache/docs/source/mp/index.rst`), LMCache MP deployment guide (`../LMCache/docs/source/mp/deployment.rst`), llama.cpp server/common flags (`../llama.cpp/common/arg.cpp`)

### llama.cpp 的预期收益形态

合理的收益形态并不是"LMCache 的数字直接套用到 llama.cpp"。一个更安全的预期是：如果 llama.cpp 服务工作负载反复发送长共享前缀；如果 prefill 主导 TTFT；如果活跃的可复用上下文超出本地 slot/RAM/HBM cache；如果 cache 恢复/传输比重算便宜，那么一个 LMCache 式的层可以按命中长度和传输开销的比例降低 TTFT 和 prefill 计算。这个结论来自 vLLM APC、LMCache MP 和 llama.cpp prompt/slot 复用文档化的机制，而不是来自测得的 llama.cpp LMCache 基准测试。[vLLM automatic prefix caching docs](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html), LMCache MP overview (`../LMCache/docs/source/mp/index.rst`), llama.cpp server context source (`../llama.cpp/tools/server/server-context.cpp`)

最可能受益的工作负载是本地或小规模集群的 coding agent、对重复长文档的 RAG、携带大历史的 multi-turn 对话、共享的系统/工具 prompt，以及具有重复模板的多租户服务端。这些正是 LMCache 和 vLLM APC 文档点名的相同工作负载类别，也匹配 llama.cpp 现有的 LCP/slot 复用逻辑。LMCache README (`../LMCache/README.md`), [LMCache integration docs](https://docs.lmcache.ai/developer_guide/integration.html), [vLLM automatic prefix caching docs](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html), llama.cpp server context source (`../llama.cpp/tools/server/server-context.cpp`)

最不可能受益的工作负载是一次性 prompt、低重叠 prompt、解码密集的响应（输出生成主导延迟）、能舒适放入本地 cache 的小上下文，以及 llama.cpp slot prompt caching 已经保留热前缀的单进程部署。vLLM 为 APC 文档化了前三个限制，LMCache 的 MI300X 文章报告了 HBM prefix cache 胜出的低负载场景，而 llama.cpp 已经有进程内复用机制。[vLLM automatic prefix caching docs](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html), [LMCache AMD MI300X benchmark](https://blog.lmcache.ai/en/2026/05/12/benchmarking-lmcache-for-multi-turn-agentic-workloads-on-amd-mi300x/), llama.cpp server context source (`../llama.cpp/tools/server/server-context.cpp`)

## 开放的不确定性

1. 在本工作区或官方 llama.cpp 文档中，没有找到一个集成 llama.cpp 的 LMCache 式外部 KV 层的一手基准。本笔记中关于 llama.cpp 的任何收益都是从机制和外部引擎结果类比而来的，而不是 llama.cpp 的测量结果。llama.cpp source tree (`../llama.cpp/`), [LMCache integration docs](https://docs.lmcache.ai/developer_guide/integration.html)

2. llama.cpp 的 sequence/state API 可以保存和加载 state，但一个生产级 LMCache 风格的 tensor-chunk 协议将需要围绕模型身份、GGUF metadata、量化 KV 类型、RoPE 设置、SWA/recurrent 部分 state、多模态占位符、adapters、sampler state 边界以及设备放置的仔细兼容性规则。这些规则的需求源自 llama.cpp 暴露了 state/session 和 memory API 以及许多与 cache 相关的运行时 flags，而不是来自已完成的设计。llama.cpp public state/session API (`../llama.cpp/include/llama.h`), llama.cpp server/common flags (`../llama.cpp/common/arg.cpp`), llama.cpp server context source (`../llama.cpp/tools/server/server-context.cpp`)

3. 报告的 LMCache 改进取决于工作负载和配置。LMCache 自己的 AMD 文章说 HBM prefix cache 在低负载下获胜，而 LMCache 在 HBM 压力和真实长上下文 agentic 压力下获胜。[LMCache AMD MI300X benchmark](https://blog.lmcache.ai/en/2026/05/12/benchmarking-lmcache-for-multi-turn-agentic-workloads-on-amd-mi300x/)

## 关键发现

1. LMCache 的生产角色是围绕服务引擎进行外部 KV cache 管理：lookup、store、retrieve、传输、分层、eviction、观测，有时还要变换 KV cache。LMCache README (`../LMCache/README.md`), LMCache MP overview (`../LMCache/docs/source/mp/index.rst`)

2. LMCache 在同时存在复用和引擎本地 cache 压力时最有说服力：长上下文、重复前缀、多轮 agent session、RAG、多模态输入、多个副本，或 prefill/decode 分离。LMCache README (`../LMCache/README.md`), [LMCache AMD MI300X benchmark](https://blog.lmcache.ai/en/2026/05/12/benchmarking-lmcache-for-multi-turn-agentic-workloads-on-amd-mi300x/)

3. 报告的改进范围从示例级第二次运行加速（如 CPU offload 复用 7.43x 和多模态音频约 15x 的耗时降低），到论文级"高达 15x 吞吐"，再到生产风格报告，如 LMCache MP 相比 in-process offload 的 13x 平均 TTFT 降低，以及 MI300X 压力下相比 HBM-only 的 3.0x 平均 TTFT 降低。LMCache CPU offload quickstart (`../LMCache/docs/source/getting_started/quickstart/offload_kv_cache.rst`), LMCache multimodality docs (`../LMCache/docs/source/api_reference/multimodality.rst`), [LMCache paper](https://arxiv.org/abs/2510.09665), [LMCache MP architecture benchmark](https://blog.lmcache.ai/en/2026/04/03/lmcaches-new-architecture-boosts-moe-inference-performance-by-10x/), [LMCache AMD MI300X benchmark](https://blog.lmcache.ai/en/2026/05/12/benchmarking-lmcache-for-multi-turn-agentic-workloads-on-amd-mi300x/)

4. Prefix caching 主要针对 prefill 和 TTFT；它不会在生成长度占主导时直接加速 decode。[vLLM automatic prefix caching docs](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html)

5. llama.cpp 已经有 prompt/state/slot 复用：文件 prompt cache、state/session API、服务端 prompt caching、slot save/restore、基于 LCP 的 slot 选择，以及通过 KV shifting 的可选 chunk 复用。llama.cpp server/common flags (`../llama.cpp/common/arg.cpp`), llama.cpp public state/session API (`../llama.cpp/include/llama.h`), llama.cpp server context source (`../llama.cpp/tools/server/server-context.cpp`)

6. llama.cpp 的 LMCache 式机会不是基本 prompt caching；它是外部的、分层的、跨进程、跨 slot、集群感知、可观测的 KV 复用，并可能解耦 prefill。LMCache MP overview (`../LMCache/docs/source/mp/index.rst`), LMCache MP P2P docs (`../LMCache/docs/source/mp/p2p.rst`), LMCache MP disaggregated-prefill docs (`../LMCache/docs/source/mp/disaggregated_prefill.rst`)

7. 最大的不确定性是工程适配性：llama.cpp 有 state 序列化 API，但一个 LMCache 风格的原始 KV connector 需要稳定的 chunk 标识、memory 布局兼容性、传输语义以及当前没有作为文档化生产 connector 的 cache 安全规则。llama.cpp public state/session API (`../llama.cpp/include/llama.h`), [LMCache integration docs](https://docs.lmcache.ai/developer_guide/integration.html)