---
type: Reference
title: 四家速查档案
description: 横向速查与一页一家的定位、许可证、关键文件
summary: 横向速查与一页一家的定位、许可证、关键文件
tags:
- llm
- kv-cache
- reference
sources:
- session: 2026-11-18 KV Cache 生态研究与文档重构
- C:/Users/Administrator/Documents/Code/my-code/lm-llama/research/kv-cache-ecosystem/09-project-profiles.md
createdAt: '2026-11-18'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 四家速查档案

> 先比较四家的架构取舍，再按需查各项目的许可证、源码位置和接入条件。详细论证见 [01–08](README.md#阅读顺序)。

## 速览

```text
                 Strata      KVMem       Mooncake     LMCache
              Strata     KVMem        Mooncake    LMCache
  角色        完整引擎   引擎内框架   集群设施    缓存中间层
  许可证      MIT        未声明       Apache-2.0  Apache-2.0
  交换粒度    4-cell 页  32/128 tok   调用方决定  256 tok
  可见历史    模型选页   额外召回     不参与      精确复用
  本机可跑    是         是           否(Linux)   否(Linux)
  需要改引擎  不适用     是，50 文件  否(插件)    是(写 connector)
```

## 横向速查

| 维度 | Strata（Flash-Next） | KVMem（llama.cpp 路径） | LMCache（普通前缀复用） | Mooncake Store / TE |
|---|---|---|---|---|
| **目标场景** | 单机长上下文推理 | 有限显存下的长会话 | 相同前缀的跨请求复用 | 多节点共享和搬运推理状态 |
| **介入层次** | 完整推理引擎 | 引擎内工作集管理 | 由引擎 connector 接入的缓存中间层 | 分布式对象存储与传输底座 |
| **交换对象** | 活动 KV 按页搬运，会话按快照停放 | KV 块，递归状态另存 | 可匹配的前缀块 | 任意字节，粒度由调用方决定 |
| **谁决定可见历史** | 模型原生选页，驻留器补齐所选页 | KVMem 按预算额外召回，选择结果影响模型可读历史 | 模型与引擎决定，复用层恢复匹配的可用前缀 | 调用方决定，从 Store 读取对象不参与模型选页 |
| **主要代价** | 主机 RAM 承载完整历史，显存缺页可能拖慢生成 | 深度引擎适配，以及召回遗漏关键信息的风险 | 查找、传输和恢复必须抵得过重算，且需匹配引擎布局 | 网络与分布式部署开销，调用方承担状态兼容和索引 |
| **许可证** | MIT | 主仓未声明 | Apache-2.0 | Apache-2.0 |

---

## Strata

| 项 | 值 |
|---|---|
| 仓库 | `github.com/Niko1221/Strata`（**独立推理引擎**，非 llama.cpp 分支） |
| 快照 | `f33c8c30`（2026-11-09） |
| 许可证 | **MIT**（`LICENSE`，Copyright (c) 2026 Niko1221 and the Strata contributors） |
| 活跃度 | 44,964★，最后 push 2026-11-16，live |
| 形态 | 自带模型加载、CUDA 内核、服务端；多后端（CUDA/HIP/SYCL/Metal） |
| 模型族 | Flash-Next（Qwen3.8）走 QSA+GDN；qwen35、dsv41 是独立实现 |

**定位**：唯一把「KV 工作集管理」做进**引擎本体**的一家。host pinned/UVA 内存是权威 K/V，VRAM 只是 n_slots 页的驻留副本，page table 退化成 residency map。

**关键文件**：`include/strata/kernels/kv_stream.hpp`（设计边界）、`src/kernels/cuda/kv_stream.cu`（resolve/CLOCK/copy）、`src/core/layer.cpp`（kv_mode 判定与 host pool 分配）、`src/prefill/prefill.cpp`（staging 与预取）、`src/core/conversation_*.cpp`（会话停放与文件）。

**要注意的**：host pool 按**完整上下文**分配，RAM 是终点——所以它天然只有两级，**拿不到 L2**。

**对本工作区的意义**：机制最值得抄（权威副本 + 驻留映射 + CLOCK + 写者不变式），但页大小（4 cell）和窗口下限（4096 cells，靠 QSA 稀疏选择才够用）在 llama.cpp 都不成立。MIT 许可最友好。

---

## KVMem

| 项 | 值 |
|---|---|
| 仓库 | `github.com/kvmem/kvmem`（多后端 KV 虚拟化框架） |
| 快照 | `2abbd50`（2026-11-16） |
| 许可证 | **主仓无根 LICENSE 文件**。README「Credits and licenses」只声明「各后端保留其上游许可证」——**框架自身代码的许可状态未声明**（`scripts/model_health_ninfer/LICENSE` 是 ninfer 的，不是框架的） |
| 活跃度 | 1,346★，最后 push 2026-11-16，建仓 2026-09-14，live |
| 形态 | 引擎无关核心库 + 每个后端一份 in-process 适配层 |
| 后端 | NInfer、llama.cpp、PolyStrata、Radiance（Codeberg，AMD RDNA4） |

**定位**：唯一做**相似度召回**的一家。mean-K / page-softmax 打分 + GQA max 聚合 + LRFU 历史 + 注意力图传播，构造当前请求的 GPU 工作集。

**关键文件**：`kvmem/include/kvmem/memory_contract.hpp`（引擎无关契约）、`src/adapter/llama-memory-kvmem.cpp`（6,059 行适配层）、`backends/patches/llamacpp-kvmem.patch`（125 KB / 2,768 行 / 50 文件）。

**要注意的**：它的 llama.cpp 补丁**只有 2 处进了 public `llama.h`**（`llama_batch.logical_pos` 字段——破坏 C ABI——与 `llama_batch_ext_set_logical_pos()`），另有 5 项「非侵入不可」的语义改动。**召回会改变本轮模型可见的历史**：项目自记「紧预算下中间的 needle 召不回，输出仍连贯」，也自记相对 compaction-only 的成功率提升（DeepSWE 43.8% → 48.4%）。所以任务质量**可升可降**，不能简单说成「必然损失精度」；但一般召回质量尚未验收。

**对本工作区的意义**：**机制不可直接抄（代价过高），但它是「上游缺什么」的最佳证据来源**。它的 patch 清单就是一份现成的缺口需求单。

---

## Mooncake

| 项 | 值 |
|---|---|
| 仓库 | `github.com/kvcache-ai/Mooncake` |
| 快照 | `8916f63`（2026-11-16） |
| 许可证 | **Apache-2.0**（`LICENSE-APACHE`） |
| 活跃度 | 7,055★，最后 push 2026-11-17，建仓 2024-06-25，live |
| 形态 | Transfer Engine（C++ 数据面）+ Mooncake Store（C++ 分布式对象池）+ Conductor（全局前缀索引） |
| 平台 | **Linux-only**，依赖 RDMA；`completionFd()` 在非 Linux 返回 -1 |

**定位**：集群级基础设施。**它不解释 KV 的语义**——键是扁平不透明字符串，值是任意字节，粒度与布局全由调用方决定。Prefix hashing 在引擎侧与 Conductor 侧。

**关键文件**：`mooncake-transfer-engine/include/transport/transport.h`（TransferRequest/Slice/Batch）、`mooncake-store/include/object_metadata.h`、`lease.h`、`eviction/evictor.h`、`mooncake-conductor/src/prefixindex/hash_strategy.cpp`（vLLM v1 哈希链逐字节复刻）。

**要注意的**：本系列里**读得最浅**的一家（<0.1%），`master_service.cpp`/`real_client.cpp` 两份万行级实现完全没读。两套淘汰框架并存（旧的 LRU/FIFO 与新的 lease-age），实际生效路径需 grep 调用方确认。

**对本工作区的意义**：单机用不了，但它的**抽象切分方式**最值得抄——元数据与内容分离、块级寻址 + 扁平键、批量化传输 API、淘汰三段分离、租约 + 软硬 pin 三档。它也是唯一做了跨引擎协议标准化（Indexer API #1403 / KV Events API #1527）的一家。

---

## LMCache

| 项 | 值 |
|---|---|
| 仓库 | `github.com/LMCache/LMCache` |
| 快照 | `a0e4a4c2`（2026-08-27） |
| 许可证 | **Apache-2.0**（`LICENSE`） |
| 活跃度 | 12,376★，最后 push 2026-11-17，建仓 2024-05-28，live |
| 形态 | 引擎内进程库（classic）／独立守护进程（MP，ZMQ + IPC） |
| 引擎 | vLLM、SGLang、TensorRT-LLM、ATOM；**无 llama.cpp 集成** |
| 后端 | CPU RAM、本地盘、S3、Redis/Valkey、Mooncake、NIXL、GDS、DAX、InfiniStore、Bigtable、SageMaker HyperPod、Aerospike、Maru 等 30+ |

**定位**：策略层。负责键、索引、分层编排、淘汰、序列化；搬运交给后端插件。引擎侧 connector 实现 vLLM 的 `KVConnectorBase_V1`。

**关键文件**：`lmcache/v1/storage_backend/abstract_backend.py`（插件契约）、`cache_engine.py`（store/retrieve/lookup）、`token_database.py`（前缀哈希链）、`kv_layer_groups.py`（layout/group + recurrent_state）、`gpu_connectors/gpu_connectors.py`（引擎 paged buffer 搬运）、`distributed/l2_adapters/base.py`（MP 三段式非阻塞接口）。

**要注意的**：
- **没有 llama.cpp 集成**，也不存在「v0 的 llama.cpp 路径」（v0 已于 2025-12 至 2026-04 三轮删除）。
- LocalDisk 的索引**只在进程内**——重启后文件还在但索引没了，看起来全 miss，且这些文件**再也不会被淘汰，等于永久泄漏**。
- 健康检查失败时 store/retrieve/lookup 静默降级为 no-op，只打 warning——配错 Redis/磁盘不会报错，只会悄悄退化成「没有缓存」。

**对本工作区的意义**：**接口形状可借鉴，代码不可直接用**。它的 backend 插件接口（contains / batched put / blocking+non-blocking get / pin 语义 / 每键独立完成回调）是最好的「可插拔存储层」参考；但它是 Python/torch 风格，与 llama.cpp 的 C++/ggml 需要一层重写。**最务实的定位是「格式与协议对齐」而非「嵌进 llama.cpp」。**

就本工作区的 Windows 单机而言，Strata 和 KVMem 可优先列为本地实测候选。Mooncake 走 Linux，LMCache 需按引擎及后端分别确认部署条件。
