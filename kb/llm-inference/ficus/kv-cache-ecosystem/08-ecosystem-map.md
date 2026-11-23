---
type: Reference
title: 生态与衍生项目地图
description: 谁被谁接入、哪些仓库已改名或迁移
summary: 谁被谁接入、哪些仓库已改名或迁移
tags:
- llm
- kv-cache
- ecosystem
sources:
- session: 2026-11-18 KV Cache 生态研究与文档重构
- C:/Users/Administrator/Documents/Code/my-code/lm-llama/research/kv-cache-ecosystem/08-ecosystem-map.md
createdAt: '2026-11-18'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 生态与衍生项目地图

> API 级核验的生态快照，记录接入关系、仓库迁移及公开实现。初次了解项目分工可先读 [首页生态职责图](README.md#先看这张图) 和 [相邻项目索引](README.md#本系列没深入的相邻项目)。

## 速览

```text
  KVMem     生态最薄：延伸 = 引擎后端多样化（Radiance 在 Codeberg）
  Mooncake  15 个集成 PR 全部 MERGED，20 个仓库默认分支仍有代码
            唯一例外 alibaba/ROLL（只有论文合作，命中 0）
  LMCache   策略层 + 30+ 后端插件；上游 CacheGen/CacheBlend 已停更
  Strata    独立推理引擎，MIT

  核验口径：仓库元数据 + PR merged_at + 默认分支代码命中数
```

## 1. 生态与衍生项目地图（2026-11-17 核验版）

本节每一项都经过实测核验，核验口径如下：

- **仓库活跃度**：`gh api repos/{owner}/{repo}` 读 stars / pushed_at / created_at / archived（核验时间 2026-11-17）。
- **集成 PR 状态**：`gh api repos/{repo}/pulls/{n}` 读 state 与 merged_at。
- **代码是否仍在默认分支**：`gh api search/code?q=mooncake+repo:{repo}` 统计默认分支命中文件数。**这一步比「PR 已合并」更强——它证明集成代码今天仍然存在于上游默认分支里**，而不是合并后又被移除。
- **非 GitHub 项目**：Codeberg 走其 REST API（`codeberg.org/api/v1/repos/...`）。

### 9.1 KVMem 生态 —— 最年轻，生态最薄，延伸体现为「后端引擎多样化」

| 项目 | 仓库（核验后） | ★ | 最后 push | 建仓 | 状态 |
|---|---|---|---|---|---|
| KVMem 主仓 | `kvmem/kvmem` | 1,346 | 2026-11-16 | 2026-09-14 | live |
| QW3 原生运行时 | `kvmem/kvmem-qw3` | 28 | 2026-11-16 | 2026-05-25 | live |
| ~~kvmem-llama.cpp~~ | **→ 302 重定向到 `kvmem/kvmem`** | — | — | — | **旧仓库名已消失** |
| NInfer（当前上游） | `iamwavecut/ninfer-all` | 227 | 2026-11-17 | 2026-08-20 | live |
| NInfer（原始引擎） | `Neroued/ninfer` | 3,357 | 2026-11-17 | 2026-06-26 | live |
| PolyStrata | `VecSzn/PolyStrata` → **`simplexai-labs/PolyStrata`** | 1,124 | 2026-11-16 | — | live |
| Radiance | **Codeberg** `StillDeadcode/radiance` | 113（62 fork） | 2026-11-16 | 2026-09-25 | live，C++；24 open issue + 20 open PR；**无 release** |
| kvmem-actkv | `melis2023/kvmem-actkv` | 9 | 2026-10-11 | **2026-10-10** | live，但**只活跃了 1 天** |
| fastllm（第三方移植） | `ztxz16/fastllm` | 5,128 | 2026-11-17 | 2023-05-13 | live |
| llama.cpp 上游 | `ggml-org/llama.cpp` | 135,376 | 2026-11-17 | — | live |

**核验结论**：

1. **后端上游仓库地址全部来自 `kvmem/backends/versions.json` 的一手记录**（`llamacpp` → `ggml-org/llama.cpp.git`、`ninfer` → `iamwavecut/ninfer-all.git`、`polystrata` → `VecSzn/PolyStrata.git`；Radiance 不在 versions.json 而在 `backends/radiance/upstream.json`）。
2. **Radiance 不在 GitHub，而在 Codeberg**（`codeberg.org/StillDeadcode/radiance.git`），其模型权重仓库 `StillDeadcode/qwen3.8-27b-iqr-v4` 同样只在 Codeberg。**按 GitHub 生态去搜会完全找不到这条线。**
3. **`kvmem/kvmem-llama.cpp` 这个仓库名已经不存在**——GitHub 302 重定向到 `kvmem/kvmem`，说明早期单后端线已并入多后端主仓。引用旧名会得到 404。
4. **`kvmem-actkv` 只是一个一天的快照**（建仓 2026-10-10，最后 push 2026-10-11，9★），不是活跃项目。把它当「参考实现」读是可以的，当「上游依赖」则不合适。
5. **`kvmem-qw3` 只有 28★**，是全文生态里最小的自有仓库。但它才是 arXiv:2609.04852 的「Source code」指向。

**KVMem 生态的判读**：它没有像 Mooncake/LMCache 那样形成「被众多引擎接入」的生态——因为它的前提是**必须控制 KV 分配、召回、位置恢复与分层移动**，无法透明地叠在黑盒 API 之上（论文 §7 明确写了这条限制）。所以它的「延伸」主要表现为**引擎后端的多样化**，而不是下游集成。

### 9.2 Mooncake 生态 —— 最庞大，15 个集成 PR 全部已合并，且代码仍在默认分支

**自家衍生**

| 项目 | 仓库 | ★ | 最后 push | 说明 |
|---|---|---|---|---|
| Mooncake | `kvcache-ai/Mooncake` | 7,055 | 2026-11-17 | 建仓 2024-06-25 |
| checkpoint-engine | `MoonshotAI/checkpoint-engine` | 1,025 | 2026-10-22 | P2P Store 官方开源化身；近 2 个月无更新 |
| TENT | **无独立仓库**，在 `Mooncake/mooncake-transfer-engine/tent/` | — | — | 编译开关 `USE_TENT` / `WITH_TENT`（`Mooncake/CMakeLists.txt:150-158`）；另有 `Mooncake/docs/source/design/tent/` 设计文档 |
| store-rs / conductor-rs | 同仓库内 `mooncake-store-rs/`、`mooncake-conductor/rust/` | — | — | 独立演进 |
| KVCache.AI | `kvcache.ai`（博客站） | — | — | 取代原 `kvcache-ai.github.io/Mooncake` 文档站 |

**引擎与框架侧集成 —— PR 状态核验（15/15 全部 MERGED）**

| 集成方 | 仓库（★ / 最后 push） | 关键 PR | PR 合并日 | 默认分支 mooncake 命中文件数 |
|---|---|---|---|---|
| vLLM | `vllm-project/vllm`（97,059 / 2026-11-17） | #41567 ECMooncakeConnector | 2026-09-07 | **133** |
| vLLM | 同上 | #56242 cross-encoder caching | 2026-09-17 | 同上 |
| SGLang | `sgl-project/sglang`（38,957 / 2026-11-17） | #10423 Mooncake Backend + EP | 2025-10-15 | **317** |
| SGLang | 同上 | #16137 Encoder Global Cache Manager | 2026-02-25 | 同上 |
| TensorRT-LLM | `NVIDIA/TensorRT-LLM`（15,084 / 2026-11-17） | #19171 集成进 KVCMv2 | 2026-10-10 | **78** |
| LMDeploy | `InternLM/lmdeploy`（8,148 / 2026-11-16） | #4903 mooncake store | 2026-08-28 | **63** |
| NVIDIA Dynamo | `ai-dynamo/dynamo`（8,509 / 2026-11-17） | #11239 索引 Mooncake KV 事件 | 2026-07-31 | **364** |
| vLLM-Ascend | `vllm-project/vllm-ascend`（3,086 / 2026-11-17） | — | — | **307** |
| vLLM-Omni | `vllm-project/vllm-omni`（7,801 / 2026-11-17） | — | — | **98** |
| LightX2V | `ModelTC/LightX2V`（3,010 / 2026-11-16） | #893 disaggregation | 2026-03-05 | **21** |
| FastDeploy | `PaddlePaddle/FastDeploy`（3,722 / **2026-09-24**） | #6768 PD cache storage | 2026-03-16 | **27** |
| xLLM | `jd-opensource/xllm` → **`xLLM-AI/xllm`**（1,623 / 2026-11-16） | — | — | **81** |
| llm-d | `llm-d/llm-d`（5,285 / 2026-11-17） | #1511 / #1826 部署与分层卸载指南 | 2026-08-05 / 2026-06-24 | **54** |
| FlexKV | `taco-project/FlexKV`（389 / 2026-11-16） | #231 REMOTE tier | 2026-07-24 | **98** |
| RBG | `sgl-project/rbg`（315 / 2026-11-17） | — | — | **24** |
| AMD ATOM | `ROCm/ATOM`（207 / 2026-11-17） | — | — | **145** |
| TokenSpeed | `lightseekorg/tokenspeed`（2,930 / 2026-11-17） | v0.1.1 | 2026-10-06 | **94** |

**训练 / RL 侧**

| 项目 | 仓库（★ / 最后 push） | 状态 |
|---|---|---|
| verl | `verl-project/verl`（24,247 / 2026-11-16） | PR #5176 checkpoint-engine 后端，**MERGED 2026-03-03**；代码命中 0（verl 侧未以 "mooncake" 命名） |
| Miles | `radixark/miles`（3,323 / 2026-11-17） | 代码命中 **115**，含 `miles/backends/training_utils/weight_update/protocols/transports/mooncake.py` |
| Speculators | `vllm-project/speculators`（958 / 2026-11-16） | 代码命中 **27**（`hs_connectors/src/hs_connectors/mooncake_store.py`） |
| TorchSpec | `torchspec-project/TorchSpec` → **`lightseekorg/TorchSpec`**（268 / 2026-11-14） | 归属已变 |
| ROLL | `alibaba/ROLL`（3,455 / 2026-11-17） | **代码命中 0 —— 只有论文合作，无代码集成** |
| TransferQueue | `Ascend/TransferQueue`（175 / 2026-11-13） | PR #131 GDR，**MERGED 2026-07-12**；代码命中 **30** |

**传输层枢纽**：`ai-dynamo/nixl`（1,368★ / 2026-11-17）把 Mooncake TE 收为 backend plugin——这是 Mooncake 影响面最广的一处。

**核验结论**：Mooncake 的集成**不是「宣传稿」而是真代码**。15 个被点名的 PR 全部处于 MERGED 状态，且 20 个下游仓库的默认分支里都仍有 mooncake 相关文件（命中数 21–364 不等）。**唯一的例外是 `alibaba/ROLL`——它只有论文合作，仓库里没有集成代码**，引用时应降级表述。

### 9.3 LMCache 生态 —— 策略层 + 插件后端

| 项目 | 仓库（★ / 最后 push） | 状态 |
|---|---|---|
| LMCache 本体 | `LMCache/LMCache`（12,376 / 2026-11-17） | live，建仓 2024-05-28 |
| LMCache → Mooncake | 同上 PR #2911 `[MP] Introduce l2 mooncake adapter` | **MERGED 2026-04-03** |
| NVIDIA Dynamo 集成 | `ai-dynamo/dynamo` | lmcache 命中 **90** 文件，含 `examples/backends/vllm/launch/agg_lmcache.sh` 与 `agg_lmcache_mp.sh` |
| vLLM production stack | `vllm-project/production-stack`（2,731 / 2026-11-07） | lmcache 命中 **106** 文件（GKE 本地盘部署教程 + dashboard）；**mooncake 命中 0** |
| InfiniStore（字节） | `bytedance/InfiniStore`（456 / **2026-09-16**） | live，但**近 2 个月无更新** |

**存储后端全景**（一手：LMCache 源码目录 + `docs/source/mp/l2_storage/supported_storages.rst`）

- classic connector（30+）：CPU RAM、Local Disk、S3、Redis/Valkey、HF3FS、HF Bucket、Bigtable、SageMaker HyperPod、InfiniStore（字节）、Mooncake Store、NIXL、GDS、DAX（Device-DAX）、Aerospike、Maru、EIC（Elastic GDS）、Blackhole/Mock（测试）、External、Plugin
- MP L2 adapter：`nixl_store` / `nixl_store_dynamic` / `fs` / `fs_native` / `raw_block`（Rust）/ `bigtable` / `sagemaker-hyperpod` / `s3` / `hfbucket` / `mooncake_store` / `resp` / `valkey` / `aerospike` / `dax` / `mock` / `fault_inject` / `plugin` / `native_plugin`

**学术衍生**（LMCache 内置的编解码器直接来自这些工作）——**注意其中两项已停更**：

| 工作 | 仓库（★ / 最后 push） | 状态 |
|---|---|---|
| CacheGen（SIGCOMM 2024） | `UChi-JCL/CacheGen`（176 / **2024-10-09**） | **约 2 年未更新**；LMCache 内置 `naive_serde/cachegen_*` |
| CacheBlend（EuroSys 2025） | `YaoJiayi/CacheBlend`（207 / **2025-07-15**） | **约 1.4 年未更新**；LMCache 内置 MP 侧 blend 模块（144 KB 单文件） |
| KIVI 量化 | — | LMCache 内置 `naive_serde/kivi_serde.py` |
| LMCache 论文 | arXiv:2510.09665 | — |
| LMCache Operator | 未见独立仓库 | 官方规划的重构（KV 管理彻底拆出引擎进程独立成容器），**目前是计划而非可依赖的发布物** |

### 9.4 同一问题域的平行延伸

| 项目 | 仓库 / 出处 | ★ / 最后 push | 核验结论 |
|---|---|---|---|
| **Strata** | `Niko1221/Strata` | **44,964** / 2026-11-16 | 上一轮 API 快照为 live；MIT 独立推理引擎。工作区 `strata/` 的 `f33c8c30` 已在 四维对齐系列（02–05） 作四维对齐；不与同名分层缓存论文混用 |
| **Tutti**（arXiv:2605.03375） | **无仓库** | — | **复核确认：论文 v1 与 TeX 源码均未给出 repo URL，代码未开源** |
| **SolidAttention**（FAST'26） | 无官方仓库 | — | 只找到个人复现：`IseRrat/SolidAttention`（0★，无描述）、`ZjuXxxc/solidattention-repro`（1★）。**官方实现未公开** |
| **KVSwap** | `hwhwz23/KVSWAP-CODE` | 8 / 2026-03-28 | 官方代码释出，规模很小 |
| **IndexMem** | `Chooovy/IndexMem` | 3 / 2026-11-09 | 「The Gating Mechanism of KV Cache Eviction」，KVMem 论文自列的未来方向 |
| **FlexGen** | `FMInference/FlexGen` → **`FMInference/FlexLLMGen`** | 9,336 / **2024-10-28** | **已 ARCHIVED**（GitHub 归档标记），近 2 年无更新 |
| **NVIDIA kvpress** | `NVIDIA/kvpress` | 1,255 / 2026-11-16 | live。是 **KV cache 压缩**库，注意与 KVPR 是不同项目，别混 |
| **FastServe** | — | — | 论文工作，未核到活跃仓库 |
| **CHEOPS 2025** | — | — | VU Amsterdam / IBM Research 的 I/O 刻画测量工作 |

**Tutti 的技术主张仍然成立**（二手：arXiv 摘要与论文解读）：瓶颈不在 SSD 原始带宽，而在 **I/O 控制路径留在 CPU 上**——GDS 只解决了数据路径。三件套是 GPU-native object store、GPU io_uring、slack-aware I/O scheduler，CPU 控制开销从 `O(layer × blocks)` 降到 `O(layer)`。它以 **GDS 版 LMCache 为基线**，自述严格 SLO 下 TTFT 降 78.3%、可达请求率 2×、服务成本降 27%，并把 compute-bound↔I/O-bound crossover 推到 98.3% 命中率。已集成 vLLM（vLLM KVConnector 插件，不改调度器与 attention kernel）。与 Mooncake 是 **local data plane + global control plane** 的分层。

### 9.5 本次核验纠正的事实

| 原表述 | 核验后 |
|---|---|
| `kvmem/kvmem-llama.cpp` 是独立早期仓库 | **仓库名已消失**，302 重定向到 `kvmem/kvmem`（该主仓 2026-09-14 建仓） |
| Radiance 属于 KVMem 的 GitHub 后端生态 | **Radiance 在 Codeberg**（`StillDeadcode/radiance`，113★），GitHub 上搜不到 |
| PolyStrata 是 `VecSzn/PolyStrata` | 仓库已迁至 **`simplexai-labs/PolyStrata`**（旧名重定向） |
| xLLM 在 `jd-opensource/xllm` | 已迁至 **`xLLM-AI/xllm`** |
| TorchSpec 在 `torchspec-project/TorchSpec` | 已迁至 **`lightseekorg/TorchSpec`** |
| FlexGen 是活跃项目 | **已 ARCHIVED**，最后 push 2024-10-28 |
| TENT 是独立开源项目 | **无独立仓库**，是 `Mooncake/mooncake-transfer-engine/tent/` 内的目录 + `USE_TENT` 开关 |
| ROLL 集成了 Mooncake | **只有论文合作，仓库内无集成代码**（命中 0） |
| SolidAttention / Tutti 可直接参考其实现 | **两者都没有可依赖的官方公开仓库** |
| LMCache 的 CacheGen/CacheBlend 上游活跃 | 两者分别**约 2 年 / 1.4 年未更新**，LMCache 内的实现是自维护副本 |
| Mooncake 生态「大量集成」是宣传 | **15 个 PR 全部 MERGED + 20 个仓库默认分支仍有代码**，属实（唯一例外 ROLL） |

### 9.6 生态给本工作区的四点提示

1. **单机 + SSD 方向上，最新的系统论文是 Tutti，不是这三家中的任何一家。** 核心洞察「GDS 已解决数据路径，瓶颈在控制路径」对你的 L2 层直接适用：如果你现在是从 CPU 线程发起 SSD 读，瓶颈很可能也在控制路径而非 NVMe 带宽。**但 Tutti 代码未开源**，目前只能借鉴设计。
2. **社区分工已收敛**：「策略层」（LMCache / SGLang HiCache）+「存储与传输层」（Mooncake / NIXL / Tutti）是两个可独立替换的层。这印证了 07 §1.4 的判断——你的 L1/L2 应该按这个分工切，而不是造一个大一统。
3. **Moonshot 自己在往「统一数据面」走**（TENT + Conductor + Indexer API 标准化 #1403 + KV Events API 标准化 #1527）。跨引擎共享 KV 的协议层正在收敛——如果你的 llama.cpp tier store 将来想接入这类共享池，**现在就要把「键 + 字节布局 + 事件」三件事标准化**，而不是只做单机内部格式。Mooncake Conductor 的 vLLM 哈希链复刻 + golden vector 测试夹具，是现成的对齐参照。
4. **Niko1221/Strata 已在本轮纳入四维源码对齐（四维对齐系列（02–05））**。分析固定本地 `f33c8c30`，未 fetch/pull；上一轮的 star 数只是其核验时间的关注度指标，不用于证明缓存质量、性能、模型支持范围，也不用于宣称它是整个赛道体量最大者。

---
