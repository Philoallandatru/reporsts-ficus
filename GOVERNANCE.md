# reporsts-ficus 知识治理与检索架构规范

以 `C:\Users\Administrator\Documents\ChatGPT\reporsts` 为根目录，统一管理持久领域知识（`kb/`）、时效性实测报告（`benchmarks/`）与个人笔记（`personal/`）。

---

## 一、 仓库语义分层与真源边界（SSOT）

| 层级 | 目录 | 是否入默认检索 | 治理定位 |
|---|---|---|---|
| **持久知识层** | `kb/<domain>/` | **是（高权重）** | 按真实技术领域划分（`nvme`、`pcie`、`pci-firmware`、`ssd-design`、`storage`、`specs`、`llm-inference`、`agents`、`engineering`、`reference-wikipedia`） |
| **实测报告层** | `benchmarks/reports/` | **是（可按 `--kb benchmarks/reports` 过滤）** | 存放带实测结论的评测报告（`type: Report`），与概念知识解耦 |
| **原始运行与静态资源** | `benchmarks/runs/`、`benchmarks/assets/`、`kb/*/sources/`、`kb/*/_source/` | **否** | 只读证据与图表资源，由报告/概念通过相对路径或 `sources` 引用 |
| **个人工作区** | `personal/`（`design/`、`diary/`） | **否** | 默认被索引器排除，不污染技术检索空间 |

---

## 二、 统一 OKF 元数据与生命周期治理

### 1. Frontmatter 最小治理字段
所有概念与报告文档统一采用 [Open Knowledge Format (OKF) v0.2](kb/specs/open-knowledge-format.md) YAML Frontmatter：

```yaml
---
type: Concept          # 受控枚举: Concept | Report | Specification | Architecture | Playbook | Reference
title: "文档标题"
description: "一句话摘要，用于 index.md 渐进式披露与 Contextual BM25 索引"
tags: [nvme, sanitize]
status: active         # draft | active | reviewing | archived | deprecated
verified:
  by: "human:owner"    # 或 "agent:<model>"，区分实测核对与文献整理
  at: "2026-11-23"
stale_after: "2027-05-23"  # 可选：基准评测或快速迭代协议的复核截止期
canonical_ref: "../../concepts/example.md"  # 仅 status: archived 时填写，指向唯一真源
---
```

### 2. 生命周期与 SSOT 去重规则
- **`active`**：唯一真源（SSOT），正常参与检索与图谱扩散。
- **`archived`**：跨库/同库重叠的次级副本（如 `kb/nvme/wiki/concepts/` 中已被 `kb/nvme/concepts/` 取代的旧版），必须标注 `canonical_ref`，**自动从默认检索中剔除**。
- **`deprecated`**：已失效结论或过时规范，保留文件供历史审计，但从 FTS5 索引中**级联清除**，防止“幽灵召回”。

### 3. 更新三步闭环（改一处，动三处）
1. **更新正文与元数据**：更新内容、`status` 与 `verified`；重大结论推翻时保留实验条件或将旧文标为 `deprecated`。
2. **联动索引与日志**：同步更新所属子库 `index.md` / `CONCEPT_INDEX.md`、上级 `kb/index.md` 与根目录 [log.md](log.md)。
3. **执行体检与增量同步**：
   ```powershell
   python tools/kb_govern.py --root . audit --json-out .kb_index/audit_report.json
   python tools/kb_govern.py --root . sync
   ```
   `audit` 门禁要求：`missing_okf_frontmatter = 0`、`orphan_docs = 0`、`dead_index_links = 0`、`broken_internal_links = 0`。

---

## 三、 检索算法与渐进式披露架构

本仓库采用 **“零外部重型数据库、单机 SQLite + 内存图谱”** 的四级检索方案（实现于 [tools/kb_govern.py](tools/kb_govern.py) 与 [tools/kb_mcp_server.py](tools/kb_mcp_server.py)）：

```text
User / Agent Query
   │
   ▼ [1. 元数据硬过滤] ──> 剔除 status IN ('archived', 'deprecated')；按 kb / doc_type 路由
   │
   ├──► [2a. Contextual BM25]  SQLite FTS5 (unicode61)，切片前缀拼接 title + description + breadcrumb + tags
   ├──► [2b. 显式图谱 PPR]     以 BM25 Top-12 为种子，沿 Markdown 互链邻接表跑 2 轮 Personalized PageRank
   │
   ▼ [3. RRF 无量纲融合] ──> 1/(60 + rank_bm25) + 0.6/(60 + rank_ppr)，按 doc_id 聚合去重
   │
   ▼ [4. 渐进式披露] ──> kb_search 返回摘要与 1-hop 线索 ──> kb_read 按需整篇或按 section 精读
```

### 关键设计细节
1. **结构化切片（Structure-Aware Chunking）**：按 Markdown `H1–H6` 标题层级切分，保持代码块完整，超长段落按自然段边界切分（`max_chars=1200`），并保留完整标题面包屑（`heading_breadcrumb`）。
2. **Contextual BM25（借鉴 Anthropic Contextual Retrieval）**：FTS5 表按字段加权索引：`title (4.0)`、`heading_breadcrumb (2.5)`、`description (2.0)`、`tags (2.0)`、`content (1.0)`，兼顾精确硬件符号（`PERST#`、`MCFG`、`0Bh`、`sm_120a`）与上下文语义。
3. **轻量图谱扩散（借鉴 HippoRAG / LinkedIn GraphRAG）**：不依赖高成本 LLM 实体抽取，直接利用已校验的 Markdown 互链（`links_json`）构建内存有向图，跑 2 轮 PPR（阻尼系数 `alpha=0.25`）拉起多跳关联概念。
4. **增量哈希同步（Incremental Hash Sync）**：`sync` 对每篇文档计算 `SHA256`：未改动跳过，内容变更则按 `doc_id` 先删旧切片再重切，删除或废弃则级联清理 `documents`、`chunks` 与 `chunks_fts`。
5. **并发安全**：SQLite 开启 `WAL` 模式，MCP 查询侧使用只读 URI 连接（`?mode=ro`），读写互不阻塞。

---

## 四、 CLI 与 MCP Server 使用方式

### 1. CLI 命令
```powershell
# 全库治理体检
python tools/kb_govern.py --root . audit --json-out .kb_index/audit_report.json

# 增量结构化同步
python tools/kb_govern.py --root . sync

# 混合检索（Contextual BM25 + PPR + RRF）与精确检索
python tools/kb_govern.py --root . search "PERST# D3cold" --top-k 5 --mode hybrid
python tools/kb_govern.py --root . search "MCFG" --kb kb/pci-firmware --mode exact

# 查看索引健康度与待同步状态
python tools/kb_govern.py --root . status --audit
```

### 2. MCP Server（`kb_search` / `kb_read` / `kb_status`）
[tools/kb_mcp_server.py](tools/kb_mcp_server.py) 基于 `FastMCP`（`stdio`）暴露三个工具：
- `kb_search(query, kb=None, doc_type=None, top_k=8, mode="hybrid")`：返回精简元数据、命中切片与 `related_1hop`。
- `kb_read(doc_id, section=None, include_links=True, max_chars=12000)`：带路径穿越防护的整篇/按 `section` 局部精读，附带 TOC 与双向链接（`outbound_links` / `inbound_links`）。
- `kb_status(include_audit=False, kb=None)`：检查索引数量、`needs_sync` 新鲜度与可选全库治理审计。

客户端配置示例：

```json
{
  "mcpServers": {
    "reporsts-kb": {
      "command": "python",
      "args": ["C:/Users/Administrator/Documents/ChatGPT/reporsts/tools/kb_mcp_server.py"],
      "env": {
        "KB_ROOT": "C:/Users/Administrator/Documents/ChatGPT/reporsts"
      }
    }
  }
}
```

---

## 五、 后续演进路线
- **Phase 2（本地语义向量 + 精排）**：在 `.kb_index/kb_index.sqlite` 中增加本地 Embedding（如 `bge-m3`）作为第三路召回并入 RRF，配合 `bge-reranker-v2-m3` 精排 Top-5。
- **Phase 3（回归评测与知识探索）**：建立 30 题 `eval_queries.jsonl` 固化 `Recall@5` / `MRR` 基线，并在 `kb_govern.py` 中增加 `discover` 子命令挖掘高入度薄弱枢纽概念与跨库盲区。
