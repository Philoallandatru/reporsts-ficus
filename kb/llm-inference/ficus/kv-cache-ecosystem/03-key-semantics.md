---
type: Reference
title: 键语义与复用契约
description: 前缀哈希链 vs 内容摘要；精确复用 vs 相似度召回
summary: 前缀哈希链 vs 内容摘要；精确复用 vs 相似度召回
tags:
- llm
- kv-cache
- cache-key
sources:
- session: 2026-11-18 KV Cache 生态研究与文档重构
- C:/Users/Administrator/Documents/Code/my-code/lm-llama/research/kv-cache-ecosystem/03-key-semantics.md
createdAt: '2026-11-18'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 键语义与复用契约

> 「键相同」不等于「状态可恢复」；精确前缀与相似度召回的分野。

## 速览

```text
  键语义要分三层看
    1 找候选    Strata 最长精确前缀 / KVMem 内容摘要谱系
                LMCache 前缀哈希链 / Mooncake 不参与
    2 能否恢复  token LCP + 媒体与模式 + 磁盘身份校验
                Mooncake 由调用方保证
    3 选哪些历史 Strata 模型选页 / KVMem 额外策略召回
                LMCache 前缀键查找 / Mooncake 不参与

  精确复用 != 相似度召回：后者会改变本轮可见历史
```

## 1. KV 寻址与缓存键

**KVMem — 内容摘要 + 原生证明**
缓存键是内容摘要，不是客户端给的 key：

```
struct ContentPrefixKey {                     // kvmem/kvmem/include/kvmem/content_cache.hpp:243
    uint64_t domain = 0, frontier = 0;
    ContentPrefixDigest digest{};
};
```

摘要算法对每个 token 做显式整数混合（splitmix64 变体），注释写明「显式整数混合避免 padding、字节序与文本编码依赖。**碰撞由后续的原生证明处理**」（`content_cache.hpp:225-239`）——即哈希只做索引，正确性靠 token/media/position/KV/统计的联合证明兜底。

客户端 key 被**明确降级为兼容元数据**：`kvmem.conversation_id`、`prompt_cache_key`、`promptCacheKey` 都不用于选择或拥有缓存谱系（`kvmem/docs/multi-conversation-kv-cache.md:9`）。

**Mooncake — 扁平不透明键**
`mooncake-store/include/replica.h:126-130` 注释：*"Object routing is always hash(tenant, key) and is decoupled with groups."* Store 侧完全没有「块链」「token 对齐」的概念，`ExistKey`/`GetReplicaList`/`BatchGetReplicaList` 全是 `key + TenantId` 维度。

前缀哈希在两处：引擎侧（vLLM 自己算）+ Conductor 侧（`mooncake-conductor/src/prefixindex/hash_strategy.cpp:32-47` 复刻 vLLM v1 哈希链）。Conductor 的复刻做得很硬：complete-block 选择、32 字节 parent 推进、SHA-256 摘要、low64_be 投影，逐字节对齐，并提供 golden vector 测试夹具（`mooncake-conductor/tests/fixtures/hash_golden_vectors*.json`）。

**LMCache — 前缀哈希链**
键的定义（`LMCache/lmcache/utils.py:413-420`）：

```python
@dataclass(slots=True)
class CacheEngineKey:
    model_name: str
    world_size: int
    worker_id: int
    chunk_hash: int
    dtype: torch.dtype
    request_configs: Optional[dict] = ...
```

字符串格式是 `model_name@world_size@worker_id@chunk_hash_hex@dtype[@tag%value...]`（`utils.py:463`）。

哈希是**滚动前缀链**而非逐 chunk 独立哈希（`LMCache/lmcache/v1/token_database.py:358-365`）：

```python
def _prefix_hash(self, token_chunks):
    prefix_hash = self._get_init_hash()          # NONE_HASH
    for token_chunk in token_chunks:
        prefix_hash = self._hash_tokens(token_chunk, prefix_hash)   # 滚动链式
        yield prefix_hash
# _hash_tokens: hash((canon_prefix, canon_tokens, canon_extra))
```

默认 chunk 长度 **256 token**（`v1/config.py:90`），非 layerwise 模式下**一个 chunk 打包全部层**（`v1/metadata.py:87-115`）。

**这里有一个反直觉的点值得强调**：LMCache **不复用 vLLM 的 block hash**。vLLM 的 `block_size` 通常是 16，LMCache 的 chunk 是 256，两套粒度独立，对接点只有 **token 数**（`get_num_new_matched_tokens` 返回最长命中前缀的 token 数，vLLM 按自己的 block 粒度去分配）。**耦合点在哈希函数与哈希输入结构，不在块表。**

另外两处容易踩的键语义：
- `world_size` 与 `worker_id` **进了 key**（`utils.py:414`），所以不同 TP 规模之间不共享缓存；只有 MLA + `save_only_first_rank` 时才把 world_size 折叠为 1（`token_database.py:241-243`）。
- MP 默认 `ObjectKey`（`v1/distributed/api.py:83`）与 **blake3**（`v1/multiprocess/token_hasher.py:62`）；classic 的本地配置默认哈希算法是 **builtin**（`v1/config.py:131`），可选择 vLLM 兼容的 SHA 系列。MP 也提供其他算法选择；两条路径的默认 hash 与键格式不同，不能假定默认互通。

> **对比要点（本次修正）**：KVMem 的 `ContentPrefixKey` 用于筛选可复用的前缀谱系，仍需精确 token/媒体/状态证明；它**不是** mean-K/page-softmax 召回的输入。召回使用模型 Q/K 统计。Strata 的 token/图片前缀判等与 QSA indexer 也分别负责身份和计算选页。LMCache 用前缀哈希及模型/rank 等命名空间定位对象；Mooncake Store 接收不透明 key。四者都不能凭“同一 hash”推出跨引擎数值状态可互读。

## 2. 召回 vs 精确复用 —— 最核心的分水岭

这里比较的是 KVMem 额外的历史召回策略，与 Strata 模型原生的 QSA indexer 不同。Strata 也会按当前 query 选择模型规定的历史页，但 `kv_stream_resolve` 只负责把该集合搬入显存，不能为满足较小驻留预算再丢掉一部分。

**KVMem 的评分链**（`kvmem/kvmem/include/kvmem/graph_recall.hpp`、`mean_key_retrieval.hpp`、`lrfu.hpp`）：

1. **Query = 最后一个 `role=user` span**（`kvmem/docs/architecture.md:25-26`），回退 `--kvmem-query-last`（默认 64）。
2. **打分**：mean-K 余弦（post-RMSNorm / pre-RoPE 的 F32 K 均值）或 page-softmax 质量。
3. **GQA 聚合**：`GqaScoreAggregation{Mean, Max}`（`mean_key_retrieval.hpp:8`）。Max 模式对每个 GQA group 的每个 query head 单独算分母再取 group 内最大值（`kvmem/src/host/graph_recall.cpp:363-380`）。理由是 Mean 会把「某个头强匹配」的信号稀释掉——`kvmem/tests/mean_key_retrieval_test.cpp:19-22` 的用例注释直接写着 *"GQA max lost matching head"*。
4. **LRFU 历史衰减**：`next = lambda*prev + gated_score`（`kvmem/kvmem/include/kvmem/lrfu.hpp:76-77`）。`lambda` 默认 0.5，`top_fraction` 默认 0.9 只门控**正向强化**——把未选中的负分置零会「相对于命中但分数没那么负的块，反而奖励了它，在没有历史时反转相关性」（`lrfu.hpp:72-74`）。这是一个很隐蔽但重要的坑。
5. **图传播**：`propagate_query_scores()` 在当前 query 的正向注意力质量上做一跳传播，负残差留在源处（`graph_recall.hpp:116-121`）。
6. **选块**：`pick_topk_blocks()` 强制保留 sink 块与 recent 块，mandatory 优先，其余按分数 top-k（`kvmem/src/host/kvmem_store.cpp:578-640`）。

**精度代价是明确的，项目自己记录了**：

- 紧预算下「埋在中间的 needle **召不回**，输出仍连贯（不是乱码）」（`kvmem/docs/modification-plan.md:342`）。
- 检索能救回来：recency 256 召回失败输出 "no secret code"，retrieval 256 选中 needle block 13 输出含 `BLUEBIRD-42`（`kvmem/docs/kvmem-mtp-plan.md:197-199`）。
- **但不是 bitwise 等价**：多 GPU 强制检索后的 greedy 输出与单 GPU 不同，改变 KV 量化类型（Q8_0 ↔ F16）会反转哪个结果胜出，「bitwise generation parity is not established」（`kvmem/docs/multi-gpu-layer.md:38-40`）。
- **一般召回质量未验收**（`kvmem/docs/checkpoint-policy-validation-20261025.md:87`）。

**Mooncake Store 搬运字节，LMCache 的普通前缀路径复用匹配对象**；在模型、位置、状态、布局均兼容且不启用有损变换时，存储层不应额外改变模型需要的数据。不能把“key 命中”直接写成“数值必然等价”。LMCache 的 CacheBlend、量化/压缩通路需另行评价质量；Strata 的 KVA 近似 prefill 也应单列。KVMem 保留所有 host 历史，但工作集子集可能改变本轮可见历史，任务质量可能改善或退化，不能仅由稀疏性推出每个任务分数必然下降。

> **精确性条件**：冷历史保存在 L2，只证明仍可找回；如果本轮 attention 本来需要它，而 L0 执行时跳过了它，就仍会改变计算。若仅做同一有效前缀的完整 state restore，或保证模型原生选择的每页都到齐，才不因搬运层再引入删减。三种路径的粒度与兼容性条件见 四维对齐系列（02–05）。

## 3. 键语义：前缀命中、模型选页、文件兼容性分三层

| 对齐项 | Strata | KVMem | LMCache | Mooncake |
|---|---|---|---|---|
| **跨请求找候选** | `ConversationCache::best` 枚举 live/checkpoint，调用 `conversation_prefix`，取可恢复的最长精确 token 前缀；等长偏向最近停放项，调用方可优先已有 live 状态 | `ContentPrefixKey={domain,frontier,digest}` 先筛相同内容前缀谱系；hash 碰撞和原生可恢复性要通过精确证明处理 | `ChunkedTokenDatabase` 链式 `H(parent,tokens,extra)` 定位；classic `CacheEngineKey` 再包含 model/world_size/worker_id/dtype/tags；MP 则用 `ObjectKey` | **不参与**。Store 路由是 `hash(tenant, key)`（`mooncake-store/include/replica.h:126-130`），不理解 token；前缀哈希由引擎侧或 Conductor 生成 |
| **token LCP 是否总可恢复** | 否。必须有 live 或实际保存的 checkpoint；该 checkpoint 的整段 token 都匹配且长度严格小于 prompt，保留末 token 给后续执行 | 否。内容匹配之外，还要 native checkpoint/版本/执行历史满足恢复条件 | 普通前缀路径按 chunk 连续命中；首个 miss 后不能把更远 chunk 直接当精确连续前缀，末 token/边界还由引擎适配器处理 | **不适用**——Store 不理解 token，是否可恢复由调用方的 key 语义决定 |
| **媒体和模式** | 范围内图片按有序 `(start,hash)` 验证；相同图片占位 token 但图片 hash 不同不能命中。`cvec` 等执行模式也需相符 | adapter 原生证明核对媒体、位置、token 及已接受的执行状态；客户端 ID 不替代这些证明 | 多模态 extra key、salt/tag、model/group 元数据由对应路径处理；这里不推断所有引擎都生成相同 extra key | **不适用**；由调用方把模式编进 key（`ObjectKey` 有 `model_name`/`kv_rank`/`object_group_id`/`cache_salt` 四个命名空间位） |
| **磁盘文件身份** | 除 schema/header/payload 校验外，config fingerprint 包含 engine/backend/KV/RoPE、上下文/驻留参数及显式算术开关；model fingerprint 采样实际加载文件的角色、大小、首尾 MiB，路径不入身份 | native `BackendIdentity` 包括 backend/revision/model/state_schema，并绑定 layout/session/stamp；当前公共 spill 是进程内存储，没有跨重启 manifest 协议 | key 和 layout 元数据共同约束；classic 默认 builtin，MP 默认 blake3，均有配置路径，不能概括为统一 SHA 协议或自动跨引擎互通 | Master 元数据默认**纯内存**；HA 模式用 standby OpLog 快照恢复，但**租约与软 pin 明确不持久化**（`mooncake-store/include/metadata_store.h:32-37`） |
| **query 选历史的层次** | QSA 原生 indexer 计算 score→top-k ids；这是模型计算。`resolve` 只保证这些 ids 涉及的页驻留，不二次裁剪模型所选集合 | 额外 Query/Pressure 机制利用 Q/K 统计及图/LRFU 等信号构造工作集；内容前缀 digest 本身不参与相似度评分 | 普通 lookup 是前缀键查找；CacheBlend 是独立的非前缀复用/重算路径，不是通用 KVMem 式历史召回 | **不参与**。Conductor 提供前缀索引与最长匹配查询，但那是给 gateway/router 用的路由信息，不改变模型看到的历史 |
| **非前缀复用** | 所查 Flash-Next 会话路径未找到 `--cache-reuse` 或 KV shifting 式中间片段复用；prefix borrow 是从共同前缀分支，不等于任意文本片段复用 | 稀疏历史重选可以找回更早逻辑块，但要区分它与会话分支的精确恢复证明 | 普通前缀缓存与 Segment/CacheBlend 的非前缀机制必须分开描述 | **不参与**（存储层无此概念） |

**这里需要区分两种“选中”。** Strata 的 QSA 当前 query 选择历史页，页驻留器必须满足该模型集合；KVMem 的额外工作集策略可以改变本轮有效历史。两者都可能看到稀疏 ids，但它们相对原模型计算的契约不同，不能只按“都 top-k”归为同一语义。

**Strata fingerprint 的边界**：配置 fingerprint 是调用方列出的字段，不是全环境摘要；模型 fingerprint 采样文件首尾，等长修改大型模型文件中部可能漏检。`SavedConversation.geometry` 仅验证运行几何，源码明确不把它当模型权重身份。因此“prefix 命中”“配置相同”“同一组权重”需要分别判断。

**源码锚点**：Strata 前缀验证（strata/include/strata/core/conversation_cache.hpp:225）、最长可恢复候选（strata/include/strata/core/conversation_cache.hpp:305）、prefix borrow（strata/include/strata/core/conversation_cache.hpp:343）、session 配置指纹（strata/src/core/conversation_file.cpp:878）、模型采样指纹（strata/src/core/conversation_file.cpp:943）、score→select→resolve→attention（strata/src/core/layer.cpp:1264）。KVMem digest 只是 shortlist（kvmem/kvmem/include/kvmem/content_cache.hpp:211）、checkpoint compatibility（kvmem/kvmem/include/kvmem/memory_contract.hpp:156）；LMCache classic 键字段/相等性（LMCache/lmcache/utils.py:414）、prefix hash（LMCache/lmcache/v1/token_database.py:358）、MP 键（LMCache/lmcache/v1/distributed/api.py:83）、MP 默认算法与可选算法（LMCache/lmcache/v1/multiprocess/token_hasher.py:62）。
