---
type: Reference
title: 缓存布局与数值格式
description: 页、块、chunk、整序列状态的区别与权威副本位置
summary: 页、块、chunk、整序列状态的区别与权威副本位置
tags:
- llm
- kv-cache
- memory-layout
sources:
- session: 2026-11-18 KV Cache 生态研究与文档重构
- C:/Users/Administrator/Documents/Code/my-code/lm-llama/research/kv-cache-ecosystem/02-cache-layout.md
createdAt: '2026-11-18'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 缓存布局与数值格式

> 页、块、chunk、整序列状态不是同一个对象；权威副本放在哪。

## 速览

```text
  基本单位（四家不是同一个东西）
    Strata   页 = 4 cells（模型专用）
    KVMem    逻辑 block = 32 / 128 token
    LMCache  chunk = 256 token
    Mooncake 不规定 —— 粒度完全由调用方决定

  权威副本放哪
    Strata   mode1 = host pinned/UVA 池权威，VRAM 只是驻留副本
    KVMem    引擎原生 KV 权威，harvest 后才有 host 副本
    LMCache  引擎张量与外部 MemoryObj 生命周期分离
    Mooncake Master 只管元数据，字节直写目标 segment
```

## 1. 分层模型与容量语义

**KVMem** 是三段式且预算正交：

| 段 | 参数 | 语义 |
|---|---|---|
| GPU 工作集 | `--kvmem-budget` B + `--kvmem-gen-reserve` R | 选中的历史 + 本轮生成追加空间。池大小 = B + R |
| Host RAM | `--kvmem-host-mib` H | **原生 K/V 驻留字节配额**，覆盖活跃 + 非活跃历史 |
| SSD | `--kvmem-disk-path` + `--kvmem-disk-mib` D | **仍被持有的文件区间**配额 |

关键纪律：**H 不是进程 RSS 限制**——mean-K 统计、状态、传输暂存、元数据、OS 文件缓存都另计（`kvmem/docs/active-kv-tiering.md:25`）。这套「配额 ≠ RSS」的措辞纪律值得直接照抄。

**Mooncake** 的层更多，且每层有独立的账号体系：集群 DRAM（Store client 注册的 global segment）、客户端本地 `LocalHotCache`（LRU 链表 + 16MB 块，可选 shm 跨进程）、`LOCAL_DISK` 副本（客户端本地盘 + 统一记账）、Master 侧 `DISK`/`NOF_SSD`/`DFS`、对象存储。淘汰主路径**不是 LRU，而是 lease-age 优先**（`mooncake-store/include/eviction/evictor.h:16-35`）。注意 `include/eviction_strategy.h` 里另有 `LRUEvictionStrategy`/`FIFOEvictionStrategy`，但那是被新框架取代的旧路径，实际生效路径需逐处确认。

**LMCache** 的层由插件决定：`LocalCPUBackend`（L1，pinned DRAM）、`LocalDiskBackend`（L2 文件）、`RemoteBackend`（包装 30+ 个 connector：S3、Redis、Valkey、Mooncake、NIXL、Azure、Bigtable、HF3FS、InfiniStore…）。

**注意 LMCache 没有 L0 显存层**——显存始终由推理引擎自己管，LMCache 只做「引擎显存 ↔ CPU DRAM」的 offload/onload。这与你 `try-out/llama.cpp` 的 `server-tier-store.{h,cpp}` 定位重合。

classic 淘汰策略位于 `cache_policy/{lru,lfu,fifo,mru}.py`，**CPU 和本地磁盘后端都会使用**。本地磁盘构造时创建策略和索引（`local_disk_backend.py:118`），容量不足时调用 `get_evict_candidates`（`:346`），命中后可 `touch_cache`（`:220`）。远端介质和 MP L1/L2 则需分别看后端及控制器实现。原文“只有 CPU 后端做 LRU”的结论已撤回。

## 2. 缓存布局：页、块、chunk 和完整状态不是同一对象

| 对齐项 | Strata：Flash-Next | KVMem：llama 适配路径 | LMCache：classic / MP | Mooncake：Store / TE |
|---|---|---|---|---|
| **基本单位** | 单个 `QsaState` 属于一层、一个序列；page size=4 cells，每 cell 对应逻辑 token。不是以 token hash 为单位的共享 chunk | 策略选择逻辑 block；llama 适配默认 32 token，配方可能用 128。`PayloadLayout.block_tokens` 和 backend page quantum 都显式描述，不能把所有后端当同一粒度 | 默认 256-token chunk；classic 非 layerwise 可打包全部层，layerwise 分层对象，MP 另有 object groups。chunk 不等于引擎物理 page | **不规定**。Store 的 key 是扁平不透明字符串，值是任意字节；粒度完全由调用方决定 |
| **物理数值排列** | K/V 分离，`[page][kv_head][page_size][head_dim]`；token `t`、head `h` 的行号为 `(page_table[t/4] * H + h) * 4 + t%4` | 原生 packed token rows；`PayloadPlane` 指明 layer/kind/offset/bytes/stride/rank/head range。编码由后端定义，scale 可独立或嵌入 packed row | classic `KV_2LTD=[2,L,T,D]`、layerwise `KV_T2D`、MLA latent 等；MP 通过 group layout 描述对象。物理布局由 connector/元数据约束 | **不解释**。`ObjectPart` 只给长度与校验和；各 `Replica` 类型（MEMORY/DISK/LOCAL_DISK/NOF_SSD/DFS）带自己的描述符。布局约定在引擎侧 connector |
| **权威数据与副本** | mode 0 全驻 VRAM、无 host copy；mode 1 host pinned/UVA pool 是完整权威历史，VRAM `n_slots` 是驻留副本；mode 2 为 drafter ring＋host 恢复历史 | 引擎先产生原生 KV，再 harvest/spill；块以 version、host copy 完成状态及驻留状态区分。`HostKvStorage` 管 RAM/SSD record，不代替引擎的写入/提交边界 | L0 引擎张量与外部 `MemoryObj` 是不同生命周期的对象；classic 自己 gather/scatter，MP 可用已注册 buffer 或 engine-driven 通路 | Master 只管元数据、**不中转对象字节**；客户端经 TE 直写目标 segment。`dynamic_replicas` 是「有几份」的权威，每份内容一致由写入方保证 |
| **副本一致性** | decode/默认路径的 mode 1 append 写 host，已驻留页也写 slot；HIP 可选 prefill 非 K8V4 路径改由 staging DMA 更新 host。完成边界后 host 仍是权威，CLOCK victim 无需额外 D2H 回写；恢复会话后 reset 页表或 refill ring | 未完成/脏块必须先生成有效 host copy，才能释放源；完整原生 K/V 与 `MemoryStamp`/版本共同构成可恢复条件 | store 分配对象并从引擎搬数据，get/retrieve 再注回引擎；pin/ref count 和完成通知控制对象存活，不自动证明任意张量布局可兼容 | `ReplicaStatus{UNDEFINED,INITIALIZED,PROCESSING,COMPLETE,REMOVED,FAILED}`；写模式 `SINGLE/FLEXIBLE_DUAL/RELIABLE_MULTI`。**一致性由写入方保证，Store 只记账** |
| **数值格式** | FP16、INT8＋每 64 值一个 FP16 scale、packed Q4_0、K8V4；Q4/可选 INT8 的 Hadamard 旋转属于数值格式，不能与位置 RoPE 混淆 | 搬运保持 backend-native K/V 编码及 scale，不因进入 SSD 自动重新量化；mean-K/Q 统计是另一类数据 | `MemoryFormat` 与 dtype/group 共同解释布局；可选量化/serde 是独立变换，不能统一宣称逐位无损 | **不规定**。Store 是字节容器；量化与否由引擎决定，Store 照单全收 |
| **恢复闭包** | `ConversationCheckpoint` 只有 token/图片及 GDN、PLE、indexer tail/dead/block_pos；`SavedConversation` 再附上 K/V、scale、pooled rows、geometry/layer range 等 | attention KV payload 与 recurrent/checkpoint、统计及执行历史分别描述，恢复需在兼容边界合并 | chunk 对象与 recurrent state group 分开；`recurrent_state` 字段提供表达能力，不代表所有 hybrid 架构组合都已可用 | `ObjectMetadata` 持有身份 + 权威读租约 + 软/硬 pin + 副本集合；`Lease` 是共享读租约截止时间。**恢复闭包由调用方定义** |

**Strata 的大小示例只适用于本几何。** 两个 KV heads、head_dim=256 时，单层每 token K+V 的 FP16/INT8/Q4/K8V4 分别为 2048/1056/576/816 B；INT8 一页是 4224 B。不包含 pooled indexer、GDN、页表或 staging，不能拿这个数当整模型 KV/RSS。

**源码锚点**：Strata QSA 布局（strata/include/strata/kernels/qsa.hpp:63）、四 token 页赋值（strata/include/strata/kernels/qsa.hpp:119）、QsaState 布局和模式（strata/include/strata/core/layer.hpp:209）、KvHostPools/KvStreamMap（strata/include/strata/kernels/kv_stream.hpp:30）、按格式计算页大小（strata/src/kernels/cuda/kv_stream.cu:199）、FP16 write-through（strata/src/kernels/cuda/qsa.cu:122）、INT8 write-through（strata/src/kernels/cuda/kv_q8.cu:62）、checkpoint 类型（strata/include/strata/core/conversation_cache.hpp:24）、完整快照类型（strata/include/strata/core/conversation_cache.hpp:174）。KVMem native payload/planes（kvmem/kvmem/include/kvmem/memory_contract.hpp:41）、llama 默认块大小（kvmem/src/adapter/llama-memory-kvmem.cpp:726）；LMCache 格式枚举（LMCache/lmcache/v1/memory_management.py:77）、chunk 默认值（LMCache/lmcache/v1/config.py:90）、classic shapes（LMCache/lmcache/v1/metadata.py:87）、recurrent group 描述（LMCache/lmcache/v1/kv_layer_groups.py:216）。
