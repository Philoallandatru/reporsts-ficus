# LLM

## 新手入门导读
* [大模型推理入门：Prefill、Decode、TTFT 与 KV Cache](llm-inference-basics-and-kv-cache.md) - 推理两阶段、速度指标定义、KV Cache 增长手算与显存瓶颈。
* [电脑硬件与推理数据流入门：SSD、内存、PCIe 与显存](memory-hierarchy-and-pcie-offloading.md) - 四层存储厨房类比、`mmap`/缺页中断与 Nsight Profiling 指标入门。
* [Dense 稠密模型 vs MoE 专家模型 & 思考强度与投机解码入门](moe-vs-dense-and-reasoning-models.md) - 总参数与激活参数、MoE 热专家缓存、`<think>` 思考强度与 MTP 原理。

## 架构、实测与生态深入

* [C++ KV Cache、vLLM 与 SGLang 学习路线](kv-cache-vllm-sglang-learning.md) - 从实现、索引、调度和指标学习 KV Cache 复用。
* [KV Cache 分层的五条原理](kv-cache-tiering-principles.md) - 容量、搬运收支、粒度取舍、可见历史与恢复条件的五个独立判断。
* [KV Cache 开源生态四家框架对比](kv-cache-ecosystem-framework-comparison.md) - Strata / KVMem / LMCache / Mooncake 的层次分工、交换对象与接入核验。
* [llama.cpp 的 KV 缓存上游最小缺口](llamacpp-kv-cache-upstream-gaps.md) - 外部 KV 缓存落地缺的几个原语与上游不会要的改动。
* [KV Cache 生态研究系列（12 篇原文）](kv-cache-ecosystem/README.md) - 四家框架的架构对比、原理、缺口清单与生态核验，含证据附录。
* [llama.cpp、Strata 与缓存研究归档（28 篇 + 2 HTML）](llamacpp-research/README.md) - 从 `lm-llama/research/` 归档的架构导读、参数手册、多级缓存、文件专家缓存与 Strata 源码对比。
* [Strata 与 llama.cpp 多场景实测、Nsight Profiling 与模块学习路线](strata-vs-llamacpp-profiling-and-scenarios.md) - RTX 5080 全链路数据流、CUDA 同步/Graph 显微对比与各项目源码学习路线。
* [KVMem 在 27B Dense 与 MoE 下的上下文、并发与极限思考实测](kvmem-dense-vs-moe-and-extreme-thinking.md) - 27B Dense vs MoE 矩阵、256K/193K 多轮覆盖与思考强度分化实验、PCIe 变慢与稀疏召回原理。
* [千问 3.8 的 GDN 与 QSA 混合注意力原理解析](qwen38-gdn-qsa-hybrid-architecture.md) - 3:1 GDN + QSA 分工机制，以及 120B+ MoE 大上下文高吞吐的底层原因。
