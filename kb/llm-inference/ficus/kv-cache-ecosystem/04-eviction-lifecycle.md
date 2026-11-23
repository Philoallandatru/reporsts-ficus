---
type: Reference
title: 淘汰、租约与生命周期
description: 先说清淘汰的是谁，再比较算法；hybrid recurrent 另算
summary: 先说清淘汰的是谁，再比较算法；hybrid recurrent 另算
tags:
- llm
- kv-cache
- eviction
sources:
- session: 2026-11-18 KV Cache 生态研究与文档重构
- C:/Users/Administrator/Documents/Code/my-code/lm-llama/research/kv-cache-ecosystem/04-eviction-lifecycle.md
createdAt: '2026-11-18'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 淘汰、租约与生命周期

> 先说清被淘汰的是什么对象，再比较算法；hybrid 的 recurrent 另算。

## 速览

```text
  被管理的对象        Strata                  KVMem         LMCache     Mooncake
  活动 GPU 页/工作集  CLOCK                   工作集策略    引擎管      不参与
  活动 checkpoint 链  root/tail/pin 谱系管理  引擎适配      不参与
  停放会话/host 对象  bytes+slots             FIFO/LRU      CPU+Disk    lease-age
  SSD                 session 文件            spill extent  分 backend  副本四类
  容量不足的含义      拒绝腾空间              失败保留源    回退重算    租户内淘汰

  hybrid recurrent 另算：KVMem 独立快照通道 / Mooncake 仅 shim 层
                        LMCache 有 object_group 机制
```

## 1. 淘汰与生命周期（租约 / pin）

三者在这层的抽象差异很大，值得单列：

- **KVMem**：三套独立策略。GPU 侧是语义选择（top-k + sink/recent + `gpu_high_watermark` 0.95 / `gpu_low_watermark` 0.85）；公共 Host store 是 FIFO/LRU 链表（`kvmem/src/host/host_kv_storage.cpp:99-144`）；遗留 CPU tier 才有 heat-aware 准入（`effective_heat = 衰减频次 + 0.25*连续命中`，`kvmem/kvmem/include/kvmem/pinned_kv_tier.hpp:250-258`）。**LRFU 不是淘汰策略，是召回评分的历史衰减**——这两件事在代码里是分开的，很容易看混。
- **Mooncake**：**租约 + 软/硬 pin 三档**。读租约是共享的 CAS 单调截止时间，且有一个正确性约束——「读路径向客户端播报完整 TTL，服务端就必须 honor now+ttl 而不是保留更早的 deadline，否则会在客户端持有的租约到期前就淘汰它」（`mooncake-store/include/lease.h:16-30`）。硬 pin 创建后不可变、永不淘汰；软 pin 是带 TTL 的截止时间。另有 group 共享租约（全有或全无）。
- **LMCache**：`pin` 语义最轻——`contains(key, pin=True)` 直接把键钉在 backend 里；`MemoryObj.pin_count` 做计数，`PinMonitor`（`v1/pin_monitor.py`）做超时跟踪。MP 模式有 fleet 级按 `cache_salt` 配额的 L2 淘汰，pins 被豁免。

## 2. 持久化

- **KVMem**：SSD 是**进程内**文件，**不跨进程、不跨重启**。三处独立证据：`kvmem/kvmem/include/kvmem/spill_io.hpp:37-40`（"process-local backing storage, with **no crash/restart durability guarantee**"）、`kvmem/docs/legacy-ssd-retirement-20261019.md:31`、`kvmem/docs/session-disk-cache.md:15-16`。旧的 `--kvmem-nvme-*` 参数已退役并显式报错（`kvmem/kvmem/include/kvmem/cli_options.h:13-20`）。
- **Mooncake**：Master 默认单副本、元数据纯内存，「master 崩溃后系统无法继续服务直到恢复」（`mooncake/docs/source/design/store/mooncake-store.md:46`）。HA 模式用 standby 生成的 OpLog 快照恢复（`:58-65`）。**租约与软 pin 明确不持久化**（`mooncake-store/include/metadata_store.h:32-37`）——恢复后重新开始。
- **LMCache**：持久性需逐 backend 确认。classic `LocalDiskBackend` 虽写裸字节文件，但初始化建立的是空的进程内索引（`local_disk_backend.py:118`），`contains` 先查该索引（`:210`）；不能由“.pt 文件还在”推出重启后自动可查。远端对象及 MP 的持久化/恢复依其元数据协议，不能统一承诺跨重启命中。

## 3. 混合模型（recurrent state）的处理

这一维对用户持有的 Qwen hybrid 模型直接相关，三者做法完全不同：

- **KVMem**：recurrent（GDN）状态**完全不参与 KV 分层**，走原生 `llama_memory_recurrent`，用**独立的字节快照通道**（`kvmem/src/adapter/llama-memory-kvmem-hybrid.h:14-16`：「attention half is a KVMem slot-pool and whose recurrent half is stock `llama_memory_recurrent`」）。换会话时**不切换** recurrent 半边（`llama-kvmem-hooks.h:157-159`）。GDN replay 有很窄的几何门槛（`llama-memory-kvmem-hybrid.cpp:14-40`）：必须 `LLAMA_ARCH_QWEN35` + `n_seq_max==1` + `1<=n_rs_seq<=5` + `ssm_d_state==128` + `ssm_d_conv==4`，不满足直接抛异常。
- **Mooncake**：vLLM connector 的 HMA 路径只做到 shim 层——`request_finished_all_groups`（`mooncake_connector_v1.py:176-196`）注释明说「cross-node fidelity for non-attention SSM/Mamba state is not asserted by this method and remains a follow-up」。
- **LMCache**：**有对应机制**——`KernelGroupInfo.recurrent_state` 标志（`v1/kv_layer_groups.py:216-219`）明确支持 Mamba/GDN 的 recurrent state 快照，而非 per-token attention KV，并用 `object_group_id` 分组。但这条路较新，成熟度不如 attention KV。

## 4. 淘汰：先指出被淘汰的对象，再比较算法

| 被管理的对象 | Strata | KVMem | LMCache | Mooncake |
|---|---|---|---|---|
| **活动 GPU 页/工作集** | CLOCK second chance，当前 resolve epoch 命中的 slot 受保护；缺失页只选非当前页的 slot 替换，不删除 host 历史 | Query/Pressure 等策略决定工作集与 mandatory 集，再用 residency delta 搬运；LRFU 是召回评分历史，不能等同于 host/SSD 淘汰器 | 一般由推理引擎管理 GPU cache；LMCache 管外部对象和搬运，不接管模型所有 attention 页的选择 | **不参与**——GPU cache 由引擎管；Store 管的只是集群侧的副本集合 |
| **活动 checkpoint 链** | 容量至少 2 时保 root，非 root 按 `used` LRU；非最新 tail 可优先丢；显式 pin 优先保护，但全部 pin 时有保持 cap 的非 root 兜底。另有可选 spread 策略 | recurrent/内容快照按自身保留策略和谱系管理，不能拿 GPU 召回分数直接替代 checkpoint 策略 | hybrid group/state 对象受引擎适配与存储协议约束；没有可直接等同 Strata root 链的通用算法 | **不参与** |
| **停放会话 / host 对象** | `ConversationCache` 同时限制 bytes 与 slots；压力下可先丢 retained KV，再淘汰最久未活动的非 pinned/guarded 会话。借用 donor 受临时 guard 保护 | host record 封存后才允许 spill；跳过 mutable、leased/pinned、relocating 项，写入成功才释放原 RAM；目录冗余版本另有保留规则 | classic CPU **和 LocalDisk** 都实例化 cache policy；pin 防淘汰。MP L1/L2 的 eviction controller/adapter 使用另外的策略接口 | **lease-age 优先**：`EvictionIndex` 定访问顺序、`EvictionPolicy::Decide` 定谁有资格淘汰、`Reclaimer` 执行；软/硬 pin 三档；group 共享租约（全有或全无）。**命名空间之间不共享配额** |
| **SSD** | 显式 session 文件，没有在本次活动 KV 路径找到自动页式 SSD 容量淘汰器 | `SpillFile` 为 native record 预留磁盘 extent；受 D 配额及记录/lease 生命周期约束，当前不保证重启恢复 | classic LocalDisk 的 chunk 容量淘汰与远端 backend/MP adapter 分开；“写到盘”与“重启后对象可发现”也是两件事 | 四类副本 `LOCAL_DISK`（客户端本地盘）/`DISK`（Master 侧文件）/`NOF_SSD`/`DFS`；**客户端本地盘 + Master 统一记账**，不是纯本地文件管理 |
| **容量不足的含义** | 页驻留不足标 overflow，不应把遗漏模型所选页当合法质量降级；停放无法与保护对象共存时可以拒绝腾空间/跳过 parking | 目标预留、源副本保留、版本与转移完成后发布；不允许用未完成副本充当有效 payload | store 分配失败可少存；retrieve 缺失需按前缀与完成结果处理，缓存失败应回退重算而非使用半成品 | `PutStart` 先扣配额；失败则**租户内**定向淘汰并有限重试（至多两次），仍失败返回 `TENANT_QUOTA_EXCEEDED` |

三种保护失败不能混用：活动 checkpoint 候选全部 pinned 时可牺牲非 root pin 保持 cap；停放会话只剩 pinned 时可拒绝 parking；临时 donor guard 导致 `guard_blocked` 时，serve 会解除 guard，把 **borrow 改为 take**，取出完整 donor，再把仍存活的 incoming 字节计入准入后重试停放原活动会话。因此 guard 不保证 donor 永远留在 parked cache。实现见 generate.cpp:16421（strata/src/program/generate.cpp:16421），测试场景见 conversation_cache_test.cpp:452（strata/src/core/conversation_cache_test.cpp:452）。

**Strata 自动 RAM cache 预算是可核查的公式**（单位 MiB）：

```text
U = floor(available_bytes / MiB) - min_free_mib
B = floor(min(floor(2*U/5), 8192) / 256) * 256
U <= 0、B < 1024 或遥测未知时，B = 0
```

它在模型加载后采样并扣除保留余量；保存/恢复还另做实际内存准入，预算不是预留。`--conversation-cache-mib/slots` 管停放会话，`--kv-resident` 管活动显存页，`--resident-budget-gib` 管专家权重 RAM 补集，**不是同一配额**。活动 host pool 按上下文另分配，不能把停放 cache 的上限说成进程 RAM 硬上限。

**注释与实现的冲突**：当前 CUDA/HIP `qsa_kv_resident_min()` 为 4096 cells，而部分帮助和 kernel 注释仍提 20480/5120 slots；Metal 分支保留较大下限。比较以 `layer.cpp` 的实际函数为准，不能仅抄旧帮助值。K8V4 的“只支持 mode 0”旧注释也与当前 streaming 分配/搬运实现不一致。

**源码锚点**：Strata CLOCK、miss 去重与 overflow（strata/src/kernels/cuda/kv_stream.cu:89）、checkpoint 三个策略重载（strata/include/strata/program/conv_cache.hpp:35）、会话准入与淘汰（strata/include/strata/core/conversation_cache.hpp:383）、自动 RAM 预算（strata/include/strata/core/conversation_memory.hpp:70）、显存驻留下限（strata/src/core/layer.cpp:771）。KVMem LRFU 更新（kvmem/kvmem/include/kvmem/lrfu.hpp:75）、安全 host spill（kvmem/kvmem/src/host/host_kv_storage.cpp:99）；LMCache CPU 策略（LMCache/lmcache/v1/storage_backend/local_cpu_backend.py:62）、磁盘策略（LMCache/lmcache/v1/storage_backend/local_disk_backend.py:118）、磁盘容量淘汰（LMCache/lmcache/v1/storage_backend/local_disk_backend.py:346）。
