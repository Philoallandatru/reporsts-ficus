# reporsts-ficus 知识治理与检索规范

以 `C:\Users\Administrator\Documents\ChatGPT\reporsts` 为根目录，统一管理实验报告与 `nvmespec/` 知识库。

## 日常命令

```powershell
# 1. 全库治理体检（Frontmatter / 孤儿 / 断链 / SSOT 冲突）
python tools/kb_govern.py --root . audit --json-out .kb_index/audit_report.json

# 2. 增量结构化同步（SHA256 变更检测 + 自动剔除 archived/deprecated）
python tools/kb_govern.py --root . sync

# 3. 混合检索（BM25 + 元数据过滤 + 1-hop 关联展开）
python tools/kb_govern.py --root . search "PERST# D3cold" --top-k 5 --expand-links
python tools/kb_govern.py --root . search "MCFG" --kb nvmespec/wiki --top-k 3
```

## 更新三步闭环

1. **正文与 Frontmatter**：概念文档必须包含 `type`、`title`、`description`、`status`、`verified`。废弃文档标记 `status: deprecated`，重复归档标记 `status: archived`。
2. **索引与日志**：新增或迁移文档需同步更新所属子库 `index.md` / `CONCEPT_INDEX.md` 及根目录 [log.md](log.md)。
3. **体检与同步**：提交前运行 `audit` 与 `sync`，确保 `missing_okf_frontmatter = 0`、`dead_index_links = 0`、`orphan_docs = 0`。

## MCP Server 接入（`kb_search` / `kb_read` / `kb_status`）

`tools/kb_mcp_server.py` 基于 `FastMCP`（`stdio`）提供三个工具：

- `kb_search(query, kb=None, doc_type=None, top_k=8, mode="hybrid")`：Contextual BM25 + 显式链接图谱 PPR + RRF 融合检索（自动过滤 `archived` / `deprecated`）。
- `kb_read(doc_id, section=None, include_links=True, max_chars=12000)`：带路径穿越防护的整篇/按小节精读，附带 TOC 与双向链接。
- `kb_status(include_audit=False, kb=None)`：查看索引健康度、`needs_sync` 新鲜度及可选全库治理审计。

客户端 MCP 配置示例：

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

