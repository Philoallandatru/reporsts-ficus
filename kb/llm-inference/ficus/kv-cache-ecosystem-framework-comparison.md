---
type: Reference
title: KV Cache 开源生态四家框架对比
description: Strata、KVMem、LMCache、Mooncake 的层次分工、交换对象与关键取舍，以及生态接入的核验结果。
summary: 四家不在同一层，不是竞品；Strata 是引擎，KVMem 管可见历史，LMCache 管跨请求复用，Mooncake 只搬字节
tags:
- llm
- kv-cache
- open-source
- inference
sources:
- session: 2026-11-18 KV Cache 生态研究与文档重构
- C:/Users/Administrator/Documents/Code/my-code/lm-llama/research/kv-cache-ecosystem/README.md
- C:/Users/Administrator/Documents/Code/my-code/lm-llama/research/kv-cache-ecosystem/01-architecture-axis.md
- C:/Users/Administrator/Documents/Code/my-code/lm-llama/research/kv-cache-ecosystem/08-ecosystem-map.md
- C:/Users/Administrator/Documents/Code/my-code/lm-llama/research/kv-cache-ecosystem/09-project-profiles.md
createdAt: '2026-11-18'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# KV Cache 开源生态四家框架对比

**Strata、KVMem、LMCache、Mooncake 不在同一层，不是竞品：Strata 自己执行推理，KVMem 决定模型这一步能看见什么，LMCache 管跨请求复用，Mooncake 只搬字节。**

## 背景 / 为什么

想了解 KV cache 有哪些开源方案时，最快的误判是把它们当成同一件事的四个实现，直接比「谁更快」。它们其实站在一条请求路径的不同环节上——搞清层次之后，才能理解为什么 LMCache 可以用 Mooncake 当后端，也能判断自己要做的是哪一层。

这份对比来自对四个仓库的源码静态阅读（本地快照，未 fetch/pull），并对下游接入关系做了 API 级核验。

## 核心内容

### 层次分工

```text
+---------------------------------------------------+
| ① 引擎与模型：自己执行推理                        |
| Strata            完整引擎，模型原生选页 + 页驻留 |
| vLLM / llama.cpp  本系列不深入，作为宿主          |
+---------------------------------------------------+
                          |
+-------------------------------------------------------+
| ② 工作集管理：决定模型这一步能看见什么                |
| KVMem             在引擎内加一层，额外召回 + 预算裁剪 |
+-------------------------------------------------------+
                          |
+-----------------------------------------------------+
| ③ 跨请求复用：管键、分层、淘汰                      |
| LMCache           引擎外中间层，前缀哈希 + 插件后端 |
+-----------------------------------------------------+
                          |
+------------------------------------------------------+
| ④ 对象存储与传输：只搬字节，不解释语义               |
| Mooncake          Store 分布式对象池 + TE 节点间传输 |
+------------------------------------------------------+

已核实的接入关系：
  vLLM --KVConnector--> LMCache --Store 后端--> Mooncake Store
  vLLM --PD 解耦时直接传 KV--> Mooncake TE
  KVMem -.补丁进引擎（50 个文件）-.-> llama.cpp
```

②③④ 可以叠在同一条请求路径上，这一点决定了它们是互补关系。

### 横向速查

| 维度 | Strata（Flash-Next） | KVMem（llama.cpp 路径） | LMCache（普通前缀复用） | Mooncake Store / TE |
|---|---|---|---|---|
| **目标场景** | 单机长上下文推理 | 有限显存下的长会话 | 相同前缀的跨请求复用 | 多节点共享和搬运推理状态 |
| **介入层次** | 完整推理引擎 | 引擎内工作集管理 | 引擎 connector 接入的缓存中间层 | 分布式对象存储与传输底座 |
| **交换对象** | 活动 KV 按页搬运，会话按快照停放 | KV 块，递归状态另存 | 可匹配的前缀块 | 任意字节，粒度由调用方决定 |
| **谁决定可见历史** | 模型原生选页，驻留器补齐所选页 | KVMem 按预算额外召回 | 模型与引擎决定，复用层恢复匹配前缀 | 调用方决定，读取对象不参与选页 |
| **主要代价** | 主机 RAM 承载完整历史，显存缺页可能拖慢生成 | 深度引擎适配 + 召回遗漏关键信息的风险 | 查找/传输/恢复必须抵得过重算 | 网络与分布式开销，调用方承担状态兼容 |
| **许可证** | MIT | **主仓未声明** | Apache-2.0 | Apache-2.0 |
| **平台** | CUDA/HIP/SYCL/Metal | Windows / ROCm | Linux 为主 | Linux-only，依赖 RDMA |

### 每家的关键事实

**Strata** — 唯一把 KV 工作集管理做进引擎本体的一家。host pinned/UVA 内存是权威 K/V，VRAM 只放 `n_slots` 个页，page table 退化成 residency map。写者不变式保证槽位永不变陈旧，淘汰用 CLOCK 二次机会。**但 host pool 按完整上下文分配，RAM 是终点**——天然只有两级，拿不到 L2。

**KVMem** — 唯一做相似度召回的一家。mean-K / page-softmax 打分 + GQA max 聚合 + LRFU 历史 + 注意力图传播，构造当前请求的 GPU 工作集。它的 llama.cpp 补丁只有 2 处进 public `llama.h`（`llama_batch.logical_pos` 破坏 C ABI，加 `llama_batch_ext_set_logical_pos()`）。**召回会改变本轮可见历史**：项目自记过 needle 召不回，也自记过相对 compaction 的成功率提升，所以任务质量可升可降——不能写成「必然损失精度」。

**LMCache** — 策略层，负责键、索引、分层编排、淘汰、序列化，搬运交给后端插件。**没有 llama.cpp 集成**，也不存在「v0 的 llama.cpp 路径」（v0 于 2025-12 至 2026-04 三轮删除，`lmcache/v0/` 从未存在）。LocalDisk 的索引只在进程内，重启后文件还在但索引没了，看起来全 miss，且这些文件再也不会被淘汰。

**Mooncake** — 集群级基础设施，**不解释 KV 语义**：键是扁平不透明字符串，值是任意字节，粒度和布局全由调用方决定。这正是它能同时被 LMCache（块级）和 vLLM（引擎侧定粒度）当远端池用的原因。真正的实现是 C++（`mooncake-store/src/master_service.cpp` 等），Go 只是 CGo 绑定。

### 生态核验结论

用 GitHub API 三层核验（仓库元数据 / PR 的 merged_at / 代码是否仍在默认分支）：

- Mooncake 被点名的 **15 个集成 PR 全部 MERGED**，20 个下游仓库默认分支里仍有相关文件（命中 21–364 个不等）。**唯一例外是 `alibaba/ROLL`**——只有论文合作，仓库里没有集成代码，引用时要降级表述。
- KVMem 生态**最薄**，因为它的前提是必须控制 KV 分配、召回、位置恢复与分层移动，无法透明叠在黑盒 API 之上。「延伸」主要表现为引擎后端多样化。
- Radiance 后端**在 Codeberg 而非 GitHub**；`kvmem/kvmem-llama.cpp` 旧仓库名已 302 重定向到主仓；PolyStrata、xLLM、TorchSpec 均已迁仓。
- LMCache 上游的 CacheGen（约 2 年未更新）、CacheBlend（约 1.4 年未更新）都是自维护副本。

### 未深入的相邻项目

| 项目 | 位置 |
|---|---|
| SGLang HiCache | SGLang 内置分层前缀缓存，可对照 LMCache 的复用职责 |
| vLLM Hybrid KV Cache Manager | vLLM 内部 KV 管理，与 KVMem 同类 |
| NIXL | 传输库，可对照 Mooncake TE |
| Tutti（arXiv 2605.03375） | 研究 SSD I/O 控制路径的论文，未找到公开实现 |
| FlexGen | 推理卸载系统，仓库已归档 |
| NVIDIA kvpress | KV 压缩工具，减少每份 KV 占用 |

## 关键要点

- 先按层次分类再比较。「谁更快」是个错误的问题，正确的是「我缺的是哪一层」。
- Mooncake 不在「粒度 × 可见性」这类坐标系里，它是字节容器，放进任何一格都会误导。
- 交换粒度分两派：整存（依赖关系一起走，但公共前缀重复存）vs 切块（前缀可共享，但索引和小 I/O 成本上来）。
- 谁决定模型可见历史，是质量判断的关键分水岭：模型原生选页 vs 额外策略裁剪。
- **能读到源码 ≠ 已确认开源许可**。KVMem 主仓没有根 LICENSE 文件，只有「各后端保留上游许可」的说明，框架自身代码的许可状态未声明。
- 生态规模要用 PR 合并状态和默认分支代码命中数判断，不要采信项目自述或宣传稿。
- 本系列是纯静态阅读：Strata 约 1.3%、KVMem 约 13%（补丁逐 hunk）、LMCache 约 1.7%、Mooncake 不足 0.1% 的源码被逐行读过；没有构建、跑测试或跑基准。结论的性质是契约级，不是性能验收。

## 相关

- [[kv-cache-tiering-principles]] — 四家分歧背后的五条原理
- [[llamacpp-kv-cache-upstream-gaps]] — llama.cpp 要支持这些外部缓存还缺哪些原语
- [[kv-cache-vllm-sglang-learning]] — vLLM/SGLang 侧的 KV 复用与前缀索引基础
