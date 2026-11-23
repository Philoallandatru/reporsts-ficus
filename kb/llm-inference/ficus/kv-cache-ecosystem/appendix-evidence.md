---
type: Reference
title: 附录：关键源码位置与测试契约
description: 每个结论的 file:line 入口与对应测试断言
summary: 每个结论的 file:line 入口与对应测试断言
tags:
- llm
- kv-cache
- evidence
sources:
- session: 2026-11-18 KV Cache 生态研究与文档重构
- C:/Users/Administrator/Documents/Code/my-code/lm-llama/research/kv-cache-ecosystem/appendix-evidence.md
createdAt: '2026-11-18'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 附录：关键源码位置与测试契约

> 每个结论的 file:line 入口，以及仓库里对应的测试断言。

## 速览

```text
  每个结论 -> 一个 file:line 入口 + 仓库里对应的测试断言

  Strata   12 个关键位置（QSA 布局 / kv_stream 契约 / 会话身份 / 原子发布）
  KVMem    20 个（WorkingSetPlan / 状态机 / LRFU / 摘要键 / apply_plan_to_kv）
  Mooncake 15 个（TransferRequest / Lease / 淘汰三层 / 客户端本地 SSD）
  LMCache  23 个（CacheEngineKey / 前缀哈希 / 后端契约 / MP 三段式）

  边界：全部为「已读测试源码」，不是运行结果；本轮未构建、未跑测试、未跑基准
```

## 1. 关键证据位置

### Strata（新增，固定 f33c8c30）

| 位置 | 职责 |
|---|---|
| qsa.hpp:119（strata/include/strata/kernels/qsa.hpp:119） | 模型专用四 token 页赋值；同文件 :63 说明布局 |
| layer.hpp:209（strata/include/strata/core/layer.hpp:209） | 每层 QsaState、数值 planes、三种驻留模式 |
| kv_stream.hpp:3（strata/include/strata/kernels/kv_stream.hpp:3） | 权威 host、页表与 write-through 的契约 |
| kv_stream.cu:89（strata/src/kernels/cuda/kv_stream.cu:89） | protect/claim/CLOCK/remap/copy 的实际执行 |
| layer.cpp:1264（strata/src/core/layer.cpp:1264） | QSA scoring/select 与纯驻留 resolve 的衔接 |
| conversation_cache.hpp:225（strata/include/strata/core/conversation_cache.hpp:225） | token/图片前缀与可恢复候选；parked KV 的生命周期 |
| conv_cache.hpp:35（strata/include/strata/program/conv_cache.hpp:35） | 活动 checkpoint root/tail/pin 淘汰 |
| conversation_memory.hpp:70（strata/include/strata/core/conversation_memory.hpp:70） | 自动 RAM 预算和真实内存准入 |
| conversation_state.cpp:284（strata/src/core/conversation_state.cpp:284） | checkpoint 运行状态保存；不是完整 KV 导出 |
| conversation_snapshot.cpp:455（strata/src/core/conversation_snapshot.cpp:455） | 完整 KV 恢复、prefix restore 和驻留刷新 |
| conversation_file.cpp:878（strata/src/core/conversation_file.cpp:878） | 配置/模型指纹与 session 文件身份 |
| conversation_file.hpp:143（strata/include/strata/core/conversation_file.hpp:143） | 临时文件、flush、发布及失败语义 |

### KVMem
| 位置 | 职责 |
|---|---|
| `kvmem/kvmem/include/kvmem/memory_contract.hpp:127` | `WorkingSetPlan`——纯计划的换出/换入集合与字节需求 |
| `kvmem/kvmem/include/kvmem/memory_contract.hpp:200` | `MemorySession` 状态机（Idle→Prepared→Spilling→Restoring→Ready→Published） |
| `kvmem/kvmem/include/kvmem/memory_contract.hpp:41-67` | `PayloadPlaneKind` / `PayloadLayout`——量化 scale 作为独立 plane |
| `kvmem/kvmem/include/kvmem/lrfu.hpp:76` | LRFU 更新公式 `lambda*prev + gated_score` |
| `kvmem/kvmem/include/kvmem/lrfu.hpp:72-74` | 负分保护：置零会反转相关性 |
| `kvmem/kvmem/include/kvmem/mean_key_retrieval.hpp:8` | `GqaScoreAggregation{Mean,Max}` |
| `kvmem/kvmem/include/kvmem/graph_recall.hpp:112-121` | 注意力图传播与一跳 score 传播 |
| `kvmem/kvmem/include/kvmem/host_kv_storage.hpp:16-56` | `HostKvLease`（钉住容量）vs `HostKvSource`（延迟读，不钉 RAM 层） |
| `kvmem/kvmem/include/kvmem/content_cache.hpp:225-250` | 内容摘要键与碰撞处理策略 |
| `kvmem/src/adapter/llama-memory-kvmem.cpp:909-951` | 工厂 + 所有模型/几何拒绝点（SWA / 纯 recurrent / n_seq_max>1） |
| `kvmem/src/adapter/llama-memory-kvmem.cpp:2185` | `apply_plan_to_kv`——stage_out → seq_rm_logical → stage_in |
| `kvmem/src/adapter/llama-memory-kvmem.cpp:2332` | `layout_gpu_slots_by_orig_pos`——按原始位置重排 GPU slot |
| `kvmem/src/adapter/llama-memory-kvmem.cpp:4604` | `score_retrieval`——Query 打分 + 图传播 |
| `kvmem/src/host/graph_recall.cpp:322` | `page_softmax_scores`——GQA mean/max 聚合实现 |
| `kvmem/src/host/host_kv_storage.cpp:99-144` | `evict_batch`——host→SSD 批量换出（≤64 条、≤256 KiB） |
| `kvmem/backends/patches/llamacpp-kvmem.patch` | llama.cpp 集成补丁（50 文件） |
| `kvmem/docs/memory-backend-contract.md:77-91` | 三种坐标的权威定义 |
| `kvmem/docs/architecture.md:72-145` | `gen_reserve` 硬上限与环形缓冲后续设计 |
| `kvmem/tests/mean_key_retrieval_test.cpp:19-22` | GQA max 行为测试（oracle） |

### Mooncake
| 位置 | 职责 |
|---|---|
| `mooncake-transfer-engine/include/transport/transport.h:65-89` | `TransferRequest`——一次搬运的最小描述 |
| `mooncake-transfer-engine/include/transport/transport.h:620-729` | `BatchDesc`——批量完成聚合与回调 pin |
| `mooncake-transfer-engine/include/transfer_metadata.h:44-54` | `GetResult{kFound,kNotFound,kUnavailable}`——区分权威缺失与瞬时故障 |
| `mooncake-transfer-engine/include/transfer_metadata.h:120-185` | `SegmentDesc`——远端地址空间快照 + 派生索引 rebuild 契约 |
| `mooncake-transfer-engine/src/multi_transport.cpp:1391-1441` | `selectTransport`——按可用性/位置/拓扑选路 |
| `mooncake-transfer-engine/include/transport/rdma_transport/rdma_context.h:107-125` | `DmabufExport`——单 fd 多 NIC 的 GPUDirect 导出 |
| `mooncake-store/include/object_metadata.h:48-167` | `ObjectMetadata`——身份 + 权威租约 + 软/硬 pin + 副本集 |
| `mooncake-store/include/lease.h:14-78` | `Lease`——共享读租约，注释记录了 honor now+ttl 的正确性约束 |
| `mooncake-store/include/eviction/evictor.h:3-35` | 淘汰三层职责划分与不可覆盖的底线 |
| `mooncake-store/include/metadata/group_index.h:39-159` | `StripedGroupIndex<64>`——group 共享租约 |
| `mooncake-store/include/local_ssd/manager.h:20-148` | `LocalSsdManager`——客户端本地 SSD offload/promotion |
| `mooncake-conductor/src/prefixindex/hash_strategy.cpp:32-47` | vLLM v1 哈希链复刻的规格说明 |
| `mooncake-conductor/include/conductor/prefixindex/prefix_indexer.h:26-92` | `BlockPresence` / `CacheHitResult`——分介质分实例分 rank 的存在性矩阵 |
| `mooncake-conductor/src/kvevent/event_manager.h:44-147` | 多引擎事件归一化；源失效时全量作废 |
| `mooncake-wheel/mooncake/mooncake_connector_v1.py:647-691` | 连续块合并 + `batch_transfer_sync_write` |

### LMCache
| 位置 | 职责 |
|---|---|
| `LMCache/lmcache/v1/cache_engine.py:83` | `LMCacheEngine`——classic 主类，store/retrieve/lookup/move |
| `LMCache/lmcache/v1/cache_engine.py:388` | `store()`——token→key→分配→GPU→CPU→多后端分发 |
| `LMCache/lmcache/v1/cache_engine.py:780` | `retrieve()`——定位→按后端取→broadcast→CPU→GPU |
| `LMCache/lmcache/v1/cache_engine.py:1130` | `lookup()`——最长命中前缀长度计算与 pin 管理 |
| `LMCache/lmcache/v1/cache_engine.py:944-956` | chunk(256) 与引擎 page(16) 粒度不匹配导致的重叠重算 |
| `LMCache/lmcache/v1/token_database.py:269` | `_hash_tokens()`——`hash((prefix_hash, tokens, extra))` |
| `LMCache/lmcache/v1/token_database.py:358` | `_prefix_hash()`——滚动前缀链哈希 |
| `LMCache/lmcache/utils.py:413-463` | `CacheEngineKey`——`model@ws@wid@hash@dtype` 键结构与字符串格式 |
| `LMCache/lmcache/v1/memory_management.py:77` | `MemoryFormat` 枚举——KV_2LTD / KV_T2D / KV_MLA_FMT / … |
| `LMCache/lmcache/v1/memory_management.py:1286` | `AddressManager`——4096 对齐的虚拟地址空间 + 空闲块合并 |
| `LMCache/lmcache/v1/kv_layer_groups.py:216` | `KernelGroupInfo.recurrent_state`——Mamba/GDN 快照标志 |
| `LMCache/lmcache/v1/storage_backend/storage_manager.py:221` | `StorageManager`——多后端编排 + 独立 asyncio 线程 |
| `LMCache/lmcache/v1/storage_backend/abstract_backend.py:27` | `StorageBackendInterface`——classic 后端插件契约 |
| `LMCache/lmcache/v1/storage_backend/connector/__init__.py:214` | `ConnectorManager`——URL schema → connector 自动发现 |
| `LMCache/lmcache/v1/distributed/l2_adapters/base.py:80` | `L2AdapterInterface`——MP 模式 submit/eventfd/query 契约 |
| `LMCache/lmcache/v1/distributed/l2_adapters/factory.py:62` | `register_l2_adapter_factory()`——MP L2 适配器注册表 |
| `LMCache/lmcache/v1/gpu_connector/gpu_connectors.py:45` | `GPUConnectorInterface`——引擎 paged buffer ↔ MemoryObj 搬运 |
| `LMCache/lmcache/v1/multiprocess/token_hasher.py:54` | `TokenHasher`——MP 服务端 blake3 前缀哈希 |
| `LMCache/lmcache/v1/distributed/api.py:83` | `ObjectKey`——MP 模式键（hash+model+rank+group+salt） |
| `LMCache/lmcache/v1/platform/event_notifier.py:44` | `EventNotifier` 抽象 + eventfd / Windows pipe 实现 |
| `LMCache/lmcache/v1/health_monitor/base.py:146` | `HealthMonitor`——健康巡检与降级开关 |
| `LMCache/lmcache/integration/vllm/vllm_v1_adapter.py:1359` | `get_num_new_matched_tokens()`——与 vLLM 调度器对接点 |
| `LMCache/lmcache/integration/vllm/vllm_multi_process_adapter.py:591 / :1100` | MP scheduler 侧 / worker 侧适配器 |

---

## 2. 已有测试源码与本轮结论的边界

| 要检查的契约 | 仓库中的测试证据 | 本轮状态 |
|---|---|---|
| 同一选页下，streamed/全驻留及 ring 恢复的 attention 输出逐字节一致，映射互逆、无 overflow | kv_stream_parity.cpp（strata/src/kernels/kv_stream_parity.cpp:184） | 已读 attention 输出的 `memcmp` 断言，未运行；未在该测试中直接逐页比对原始 KV planes |
| 同 token、不同范围内图片不能错误命中，范围外图片不污染已验证前缀 | conversation_cache_test.cpp（strata/src/core/conversation_cache_test.cpp:196） | 已查测试源码 |
| root/tail/pin/cap 的 checkpoint 淘汰边界 | conv_cache_test.cpp（strata/src/program/conv_cache_test.cpp:58） | 已查测试源码 |
| 自动预算未知/不足/封顶/取整边界 | conversation_memory_test.cpp（strata/src/core/conversation_memory_test.cpp:52） | 已查测试源码 |
| 文件 config 身份、浮点位差异及字段边界 | conversation_file_test.cpp（strata/src/core/conversation_file_test.cpp:363） | 已查测试源码 |
| prefix KV restore＋checkpoint 与整会话 restore 后 rewind 的状态对照 | conversation_snapshot_test.cpp（strata/src/core/conversation_snapshot_test.cpp:229） | 已查测试源码，未做本机状态往返 |

**覆盖缺口**：所引快照测试在 conversation_snapshot_test.cpp:340（strata/src/core/conversation_snapshot_test.cpp:340） 跳过 K8V4 的 mode 1/2；当前快照实现允许合规的 K8V4 mode 1，显式拒绝 ring 或冲突格式标记（conversation_snapshot.cpp:34（strata/src/core/conversation_snapshot.cpp:34））。因此不能由测试文件存在推出 K8V4 streamed snapshot 已验收；这是测试覆盖边界，不是本轮运行失败。

**对本工作区的可迁移结论**：完整 Prefix State Blob 路线优先借鉴 Strata 的恢复闭包、配置/模型身份、流式 source、准入和原子发布；活动页路线再参考逻辑页/物理 slot 分离与显式同步。Strata mode 1 的权威 host pool 仍按完整活动历史占 RAM，显式 session 文件也不等于活动页的自动 L2，因此本轮没有证明“超过 RAM 后仍可边推理边从 SSD 调页”的容量收益。没有修改实现，也没有作跨引擎性能排序。

---
