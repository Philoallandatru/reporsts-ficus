#!/usr/bin/env python3
"""
Knowledge Base MCP Server exposing `kb_search`, `kb_read`, and `kb_status`.

Environment variables:
  KB_ROOT : Root directory of the OKF/Markdown knowledge base (default: parent of tools/)
  KB_DB   : Path to SQLite FTS5 index (default: <KB_ROOT>/.kb_index/kb_index.sqlite)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# Ensure sibling module `kb_govern` is importable regardless of CWD
TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import kb_govern  # noqa: E402

KB_ROOT = Path(os.environ.get("KB_ROOT", str(TOOLS_DIR.parent))).resolve()
KB_DB = Path(os.environ.get("KB_DB", str(KB_ROOT / ".kb_index" / "kb_index.sqlite"))).resolve()

mcp = FastMCP("ficus-kb-governance")


def _ensure_index_ready() -> None:
    if not KB_DB.exists():
        print(f"[kb-mcp] Index not found at {KB_DB}, running initial sync...", file=sys.stderr)
        stats = kb_govern.run_sync(KB_ROOT, KB_DB)
        print(f"[kb-mcp] Initial sync complete: {stats}", file=sys.stderr)


@mcp.tool()
def kb_search(
    query: str,
    kb: str | None = None,
    doc_type: str | None = None,
    top_k: int = 8,
    mode: str = "hybrid",
) -> dict[str, Any]:
    """
    Search the knowledge base using Contextual BM25 + link-graph PPR + RRF fusion.

    Args:
        query: Search query (supports English/Chinese mixed terms and exact hardware symbols like PERST#, MCFG, sm_120a).
        kb: Optional sub-KB prefix filter (e.g. "kb/nvme", "kb/pci-firmware", "benchmarks/reports").
        doc_type: Optional OKF type filter (e.g. "Concept", "Report", "Specification").
        top_k: Number of documents to return (1..20, default 8).
        mode: "hybrid" (Contextual BM25 + PPR graph RRF) or "exact" (pure FTS5 BM25).
    """
    _ensure_index_ready()
    search_mode = mode if mode in ("hybrid", "exact") else "hybrid"
    hits = kb_govern.hybrid_search(
        db_path=KB_DB,
        query=query,
        kb_filter=kb,
        type_filter=doc_type,
        top_k=top_k,
        mode=search_mode,
    )
    return {
        "query": query,
        "mode": search_mode,
        "count": len(hits),
        "results": hits,
    }


@mcp.tool()
def kb_read(
    doc_id: str,
    section: str | None = None,
    include_links: bool = True,
    max_chars: int = 12000,
) -> dict[str, Any]:
    """
    Read a knowledge base document or a specific Markdown section by `doc_id`.

    Args:
        doc_id: Canonical relative path returned by `kb_search` (e.g. "kb/pci-firmware/concepts/perst-assertion-delay.md").
        section: Optional heading name (exact or substring match) to read only that section and its subsections.
        include_links: Include outbound and inbound 1-hop document links from the index.
        max_chars: Maximum characters to return before truncating with TOC guidance.
    """
    _ensure_index_ready()
    return kb_govern.read_doc(
        root=KB_ROOT,
        db_path=KB_DB,
        doc_id=doc_id,
        section=section,
        include_links=include_links,
        max_chars=max_chars,
    )


@mcp.tool()
def kb_status(
    include_audit: bool = False,
    kb: str | None = None,
) -> dict[str, Any]:
    """
    Inspect knowledge base index health, freshness (`needs_sync`), per-KB counts, and optional governance audit.

    Args:
        include_audit: If True, run full OKF governance audit (frontmatter, orphans, dead links, duplicates).
        kb: Optional sub-KB prefix filter (e.g. "kb/nvme", "benchmarks/reports").
    """
    return kb_govern.get_status(
        root=KB_ROOT,
        db_path=KB_DB,
        include_audit=include_audit,
        kb_filter=kb,
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
