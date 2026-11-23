---
type: Reference
title: 传输路径
description: 缺页调入、工作集切换、chunk 恢复与网络数据面
summary: 缺页调入、工作集切换、chunk 恢复与网络数据面
tags:
- llm
- kv-cache
- data-transfer
sources:
- session: 2026-11-18 KV Cache 生态研究与文档重构
- C:/Users/Administrator/Documents/Code/my-code/lm-llama/research/kv-cache-ecosystem/05-transfer-paths.md
createdAt: '2026-11-18'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 传输路径

> 缺页调入、工作集切换、chunk 恢复，以及网络数据面。

## 速览

```text
  KVMem    同机 memcpy：stage_out -> seq_rm_logical -> stage_in
           原始位置不变，物理槽按原始位置重排 -> 纯 memcpy，无需 re-RoPE
  Strata   qsa_scores -> topk -> qsa_kv_resolve -> copy_kernel -> attention
           GPU kernel 读 mapped pinned host，把 miss 页搬进 slot
  Mooncake TransferRequest -> 连续块合并 -> submitTransfer -> RDMA/TCP/SHM/...
           TE 是纯数据面，不保留源、不管生命周期
  LMCache  三套接口并存：StorageBackendInterface / RemoteConnector
                            / L2AdapterInterface（submit -> eventfd -> query）
```

## 1. 传输与数据通路

**KVMem** 的传输是**同机进程内的 memcpy**，没有网络抽象：

```
stage_out → seq_rm_logical → stage_in
  ↑ 严格顺序，先换出后换入（kvmem/src/adapter/llama-memory-kvmem.cpp:2185-2231）
```

关键在「恢复到原逻辑位置」的物理实现（`llama-memory-kvmem.cpp:2332` `layout_gpu_slots_by_orig_pos`）：**逻辑位置（原始 token 位置）不变**——决定 RoPE 坐标与 causal 边界；**物理位置（GPU slot）按原始位置重排**——保证 `seq_rm_logical` 能精确删除逻辑块。恢复是 packed GPU 格式的 memcpy，**不重旋转 K、不 re-RoPE**（`kvmem/docs/memory-backend-contract.md:77-91` 定义的三种坐标：原始位置 / 紧凑 attention 地址 / 物理槽）。

**Mooncake** 的传输是一整套网络数据面：`TransferRequest{opcode, source, target_id, target_offset, length, priority, intent_type, task_group_id}` → 连续块合并 → `submitTransfer(batch_id, entries)` → RDMA one-sided（`ibv_reg_mr` 得 lkey/rkey，网卡 DMA 直写，零用户态拷贝）/ TCP / POSIX SHM / NVMe-oF / CXL / NVLink / IBGDA 等 20+ transport，由 `MultiTransport::selectTransport` 按「构建可用性 + 内存位置 + 拓扑」选路（`mooncake-transfer-engine/src/multi_transport.cpp:1391-1441`）。

批量形状值得抄：Python 绑定把 (src, dst, len) 拍平成**三个平行数组**（`mooncake-wheel/mooncake/mooncake_connector_v1.py:682-684`），且**相邻块 id 会被合并成一次大传输**（`group_concurrent_contiguous`，`:647-663`）——对 SSD 场景收益尤其大。

**LMCache** 有三套形状不同的接口并存，是本仓库最容易被误读的地方：

| 接口 | 位置 | 形状 |
|---|---|---|
| `StorageBackendInterface`（classic 编排层） | `v1/storage_backend/abstract_backend.py:27` | `contains(key, pin)` / `exists_in_put_tasks` / `batched_submit_put_task(keys, objs, transfer_spec, on_complete_callback)` / `get_blocking` / `get_non_blocking` / `pin` / `unpin` / `remove` |
| `RemoteConnector`（classic 网络 L2） | `v1/storage_backend/connector/base_connector.py:31` | `exists` / `get` / `put` / `list` / `close` / `ping` + 一组 `support_*` 能力探测位 |
| `L2AdapterInterface`（MP 模式） | `v1/distributed/l2_adapters/base.py:80` | **submit → eventfd → query 的非阻塞三段式**：`submit_store_task` / `pop_completed_store_tasks`；`submit_lookup_and_lock_task` / `query_lookup_and_lock_result`；`submit_load_task` / `query_load_result` |

> 注意：`StorageBackendInterface` 上**没有 `list` 和 `clear`**，也没有叫 `get`/`put`/`delete` 的方法。`list()` 只在 `RemoteConnector`（`base_connector.py:202`），`clear()` 只在 `StorageManager.clear()`（`storage_manager.py:1121`）。

**LMCache 的 GPU 搬运是自己做的**，这是它与引擎耦合最深的一层：`gpu_connector.batched_from_gpu`（`v1/cache_engine.py:558`）从引擎的 paged GPU buffer 直接拷到 `MemoryObj`，**不是引擎侧预先 offload 过**。LMCache 直接持有引擎 KV tensor 的 device pointer。

**插件发现机制**：classic 用 URL schema 匹配——`ConnectorManager`（`connector/__init__.py:214`）自动加载包内所有 `*_adapter` 子类，每个 adapter 声明 `schema` 前缀，`CreateConnector(url)` 按 URL 选第一个 `can_parse` 命中的（`:358`）。已声明的 schema：`redis://`、`rediss://`、`redis-sentinel://`、`lm://`、`infinistore://`、`mooncakestore://`、`blackhole://`、`audit://`、`fs://`、`s3://`、`mock://`、`external://`、`plugin://`。MP 模式则是工厂注册表 `register_l2_adapter_factory`（`v1/distributed/l2_adapters/factory.py:62`），CLI 入口 `--l2-adapter <type>`。

**序列化格式**：classic 走 `v1/storage_backend/naive_serde/`（`NaiveSerializer` identity、`cachegen_*` 压缩编解码、`kivi_serde.py`）；MP 走 `v1/distributed/serde/`（`Serializer.serialize(src, dst, key) -> int` 原地写 dst，另有 fp8 / aesgcm / asym_k16_v8 / turboquant）。**但磁盘路径是个例外**：`LocalDiskBackend` 直接写 `memory_obj.byte_array` 裸字节（`local_disk_backend.py:633-643`），文件后缀却是 `.pt`——**不能用 `torch.load` 读**。

## 2. 传输路径：缺页调入、工作集切换、chunk 恢复分别展开

| 路径 | Strata | KVMem | LMCache | Mooncake |
|---|---|---|---|---|
| **GPU/host 热路径** | `qsa_*scores → topk ids → qsa_kv_resolve → resolve_kernel → copy_kernel → attention`；GPU kernel 读取 mapped pinned host，把 miss 页移到 slot | `apply_plan_to_kv → harvest/spill outgoing → seq_rm_logical → admit incoming → write_block_to_gpu`；恢复 packed K/V 到 slot/cell | classic `store → process_tokens → allocate → batched_from_gpu → batched_put`；`retrieve → get_block_mapping/batched_get → batched_to_gpu` | 引擎 connector → TE `submitTransfer(batch_id, entries)` → 目标 segment buffer；TE 是纯数据面，不管理生命周期 |
| **触发和粒度** | decode 只搬本次 miss 页，每页包含所有 KV heads 及相应 scales；prefill 则可按层 DMA staging 连续前缀 | 计划的 block 差集；按层获取 packed token rows，再 H2D slab/后端写入。只搬工作集变化不等于只搬一整个会话 | keyed chunk/layer/group；connector 用引擎 page/slot mapping gather/scatter，存储粒度独立于引擎页 | `TransferRequest{opcode,source,target_id,target_offset,length,priority,intent_type,task_group_id}`；批次 → 切片两级，相邻块由调用方合并 |
| **写回与源保留** | 默认 decode 的 mode 1 append write-through；HIP 可选 prefill 先写 staging 再 DMA 到 host。完成同步后替换干净驻留副本，无需 victim 回写 | 新/脏原生 KV 需先 harvest 为有效 host copy；SSD 转移先 reserve/write，再发布 destination 并释放 RAM | 对象 pin/refcount、backend 完成结果、引擎 load/save 时机必须配合；MP L2 的 buffer 生命周期归调用方 | **由调用方决定**。TE 只搬字节，不保留源、不管理副本生命周期；副本与租约由 Store 记账 |
| **host/SSD** | `conversation_kv_source → session writer → 16 MiB 顺序缓冲 → 临时文件 → flush/rename`；读取完整 `SavedConversation` 后再恢复状态 | `HostKvStorage → SpillExtent`；相邻 extent 可通过 `write_batch` 合并，冷 source 支持区间读，不要求整 record 提升回 RAM | LocalDisk 以对象文件存裸字节；后端有 async worker。MP L2 为 submit→通知→查询完成结果；文件、GDS、remote 的数据面不同 | TE 支持 20+ transport（RDMA/TCP/SHM/NVMe-oF/CXL/…）；Store 用 TE 直写 segment，Master 不经手字节 |
| **重叠与同步** | resolve/copy/attention 在计算依赖链内；prefill 可选独立 stream 预取下一层并用 events 围住 staging。checkpoint/parking 可选 D2D 冻结后后台 D2H，消费/复用前 join | 异步 harvest 和 stage-in 最终仍需引擎安全边界、有效版本及显式完成后 publish；abort 需先排空/取消传输 | classic 用 backend async loop/Future；MP 完成通知不等于自动持有 buffer，调用方要保活；成功按任务或 bitmap 解释 | `BatchDesc` 聚合完成状态 + 完成队列（`drainCompletions`）；批量完成按 batch 判，task 级状态可单独查 |
| **网络/直连存储** | 本次 QSA/session 路径未找到 RDMA、GDS 或按需 SSD→attention 页故障协议；Python 服务 IPC 不等于 KV 网络传输协议 | 本次 llama/HostKvStorage 路径是本地 GPU/host/文件，不是远端对象池 | 可通过 Mooncake/NIXL/GDS 等 adapter 使用网络或设备路径，但不是所有部署都自动启用 | **主场**：RDMA one-sided 零拷贝、GPUDirect（`DmabufExport` 单 fd 多 NIC）、NVMe-oF、CXL、NVLink/IBGDA |

**Strata resolve 的可复核执行顺序**：先把选中集合中已驻留页标为当前 epoch；missing 页用 `atomicCAS(-1,-2)` 去重；CLOCK 只在非当前 epoch slot 中找 second-chance victim；更新双向映射后，`copy_kernel` 每线程搬 16 B，按格式移动 K/V/scale 的 runs。INT8 的单 miss 复制为一页 4224 B。这里没有把相邻 miss 自动合并成一笔 SSD I/O；prefill 和 ring restore 的连续 DMA 是另一条路径。

**HIP prefill 例外需单列**：`STRATA_KV_HOST_DMA=1` 只在 HIP 构建启用；staged 且非 K8V4 分支把 `host_w` 设为 null，append 写 staging/resident，再由 `kv_unstage_to_host` 把 chunk 覆盖的页 DMA 回权威 host。K8V4 分支仍分两半直接写 host。不能将 decode 的 kernel write-through 描述套在这条预填充路径上；证据见 prefill.cpp:4318（strata/src/prefill/prefill.cpp:4318） 和 kv_stream.cu:264（strata/src/kernels/cuda/kv_stream.cu:264）。

**Strata 的 checkpoint 不能独立复活任意分支。** `checkpoint_save/restore` 不复制完整历史 K/V 或所有已完成 pooled rows。同一 branch rewind 依赖相应 positional KV 仍未覆盖；若池已装入另一会话，只恢复旧 GDN 等运行状态仍不够。完整恢复必须先把该会话的 K/V、scales、pooled rows 与运行状态合并。`conversation_kv_restore` 恢复后会 `refresh_residency`：mode 1 清空驻留图、mode 2 refill ring，防止继续用旧会话的 slot。

**磁盘原子性也有边界。** Strata 默认 durable 写先完成自身临时文件、flush 后发布；rename 前失败保留旧文件，rename 后目录 flush 失败可出现 `published=true` 但名字持久性未确认。Linux 的 O_DIRECT 是尝试并带回退，Windows 是 buffered 路径；不是 GPU Direct Storage。文件的完整性校验也不消除模型采样指纹的盲区。

**源码锚点**：Strata resolve/copy 调用（strata/src/kernels/cuda/kv_stream.cu:214）、连续 staging/ring DMA（strata/src/kernels/cuda/kv_stream.cu:241）、prefill 预取实现（strata/src/prefill/prefill.cpp:3675）、checkpoint save（strata/src/core/conversation_state.cpp:284）、checkpoint restore（strata/src/core/conversation_state.cpp:392）、KV restore 与驻留刷新（strata/src/core/conversation_snapshot.cpp:408）、流式 KV source（strata/src/core/conversation_snapshot.cpp:517）、session 写入与发布契约（strata/include/strata/core/conversation_file.hpp:143）、文件 I/O 实现（strata/src/core/conversation_file.cpp:528）。KVMem packed 恢复（kvmem/src/adapter/llama-memory-kvmem.cpp:4450）、spill 的源保留和发布（kvmem/kvmem/src/host/host_kv_storage.cpp:149）、extent 合并（kvmem/kvmem/include/kvmem/spill_io.hpp:37）；LMCache store 数据面（LMCache/lmcache/v1/cache_engine.py:485）、retrieve 的引擎布局要求（LMCache/lmcache/v1/cache_engine.py:780）、MP L2 完成/保活职责（LMCache/lmcache/v1/distributed/l2_adapters/base.py:80）。
