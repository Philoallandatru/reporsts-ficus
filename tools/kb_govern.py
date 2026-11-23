#!/usr/bin/env python3
"""
Knowledge Base Governance Linter, Incremental Structure-Aware Indexer & Hybrid Retrieval Engine.

Shared backend for both the CLI (`kb_govern.py`) and the MCP Server (`kb_mcp_server.py`).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

EXCLUDED_DIR_NAMES = {
    ".git",
    ".obsidian",
    ".claude",
    ".llmwiki",
    ".kb_index",
    "node_modules",
    "dist",
    "__pycache__",
    "_source",
    "_meta",
    "_review",
    "sources",
    "exports",
    "maps",
    "templates",
    "tests",
    "tmp",
    "tools",
    "assets",
    "runs",
    "personal",
    "pcie-visual-lab",
    "visual-lab",
    "nvme-power-cycle",
}

META_FILE_NAMES = {
    "index.md",
    "CONCEPT_INDEX.md",
    "README.md",
    "log.md",
    "CONTEXT.md",
    "CONTEXT-MAP.md",
    "GOVERNANCE.md",
    "LLMWIKI.md",
    "SOURCES.md",
    "MOC.md",
    "FINAL_REPORT.md",
    "FINAL_SUMMARY.md",
    "PROGRESS.md",
    "PROJECT_COMPLETE.md",
    "PROJECT_SUMMARY.md",
    "QUICKSTART.md",
    "SPEC_INDEX.md",
    "STATUS.md",
    "TODO.md",
    "BACKLOG.md",
    "BIBLIOGRAPHY.md",
    "COVERAGE_GAPS.md",
    "GLOSSARY.md",
    "KNOWLEDGE_MAP.md",
    "PATENT_INDEX.md",
    "TEST_PLAN.md",
    "TRACEABILITY_MATRIX.md",
    "VERSIONED_SOURCES.md",
    "pcie-deep-analysis.md",
    "pcie-spec-analysis.md",
}

FRONTMATTER_RE = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
WIKI_LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


@dataclass
class ConceptDoc:
    kb_name: str
    rel_path: str
    abs_path: Path
    sha256: str
    schema_style: str  # "okf" | "llmwiki" | "plain"
    frontmatter: dict[str, Any] = field(default_factory=dict)
    title: str = ""
    description: str = ""
    body: str = ""
    md_links: list[str] = field(default_factory=list)
    wiki_links: list[str] = field(default_factory=list)
    resolved_links: list[str] = field(default_factory=list)


def _is_kb_dir(d: Path) -> bool:
    has_concepts = (d / "concepts").is_dir() or (d / "wiki" / "concepts").is_dir()
    has_index = any((d / name).exists() for name in ("index.md", "CONCEPT_INDEX.md"))
    return has_concepts or has_index


def discover_kbs(root: Path) -> list[tuple[str, Path]]:
    """Discover leaf knowledge sub-bases under root."""
    kbs: list[tuple[str, Path]] = []

    def _walk(curr: Path) -> None:
        for child in sorted(curr.iterdir()):
            if not child.is_dir() or child.name in EXCLUDED_DIR_NAMES:
                continue
            has_concepts_dir = (child / "concepts").is_dir() or (child / "wiki" / "concepts").is_dir()
            if has_concepts_dir:
                kbs.append((child.relative_to(root).as_posix(), child))
                continue
            before = len(kbs)
            _walk(child)
            if len(kbs) == before and _is_kb_dir(child):
                kbs.append((child.relative_to(root).as_posix(), child))

    _walk(root)
    return kbs


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text, "llmwiki"
    raw_yaml = m.group(1)
    body = text[m.end():]
    try:
        parsed = yaml.safe_load(raw_yaml)
        if not isinstance(parsed, dict):
            return {}, body, "plain"
        return parsed, body, "okf"
    except yaml.YAMLError:
        return {"_yaml_error": True}, body, "plain"


def extract_title(fm: dict[str, Any], body: str, fallback: str) -> str:
    if isinstance(fm.get("title"), str) and fm["title"].strip():
        return fm["title"].strip()
    for line in body.splitlines():
        hm = HEADING_RE.match(line)
        if hm and len(hm.group(1)) == 1:
            return hm.group(2).strip()
    return fallback


def is_concept_file(path: Path, kb_root: Path) -> bool:
    if path.suffix.lower() != ".md":
        return False
    if path.name in META_FILE_NAMES:
        return False
    rel_parts = path.relative_to(kb_root).parts
    if any(part in EXCLUDED_DIR_NAMES for part in rel_parts):
        return False
    return True


def collect_docs(root: Path) -> tuple[list[tuple[str, Path]], list[ConceptDoc]]:
    kbs = discover_kbs(root)
    docs: list[ConceptDoc] = []
    root_resolved = root.resolve()

    def _add_doc(kb_name: str, md_path: Path) -> None:
        raw = md_path.read_text(encoding="utf-8", errors="replace")
        sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        fm, body, style = parse_frontmatter(raw)
        title = extract_title(fm, body, md_path.stem)
        desc = str(fm.get("description", "")).strip()
        md_links = [
            target.split("#")[0].strip()
            for _, target in MD_LINK_RE.findall(body)
            if not target.startswith(("http://", "https://", "mailto:", "#"))
        ]
        wiki_links = [target.split("#")[0].strip() for target in WIKI_LINK_RE.findall(body)]

        resolved_links: list[str] = []
        for lk in md_links:
            if "_source/" in lk:
                continue
            cand = (md_path.parent / lk).resolve()
            if cand.exists() and cand.is_relative_to(root_resolved):
                resolved_links.append(cand.relative_to(root_resolved).as_posix())

        docs.append(
            ConceptDoc(
                kb_name=kb_name,
                rel_path=md_path.relative_to(root).as_posix(),
                abs_path=md_path,
                sha256=sha,
                schema_style=style,
                frontmatter=fm,
                title=title,
                description=desc,
                body=body,
                md_links=md_links,
                wiki_links=wiki_links,
                resolved_links=sorted(set(resolved_links)),
            )
        )

    for kb_name, kb_path in kbs:
        for md_path in sorted(kb_path.rglob("*.md")):
            if is_concept_file(md_path, kb_path):
                _add_doc(kb_name, md_path)

    root_reports = [p for p in sorted(root.glob("*.md")) if p.name not in META_FILE_NAMES]
    for md_path in root_reports:
        _add_doc("root-reports", md_path)

    return kbs, docs


def collect_index_targets(kb_root: Path, repo_root: Path) -> tuple[set[str], list[str]]:
    referenced: set[str] = set()
    dead_links: list[str] = []
    for idx_name in ("index.md", "CONCEPT_INDEX.md", "wiki/index.md"):
        idx_path = kb_root / idx_name
        if not idx_path.exists():
            continue
        text = idx_path.read_text(encoding="utf-8", errors="replace")
        for _, target in MD_LINK_RE.findall(text):
            clean = target.split("#")[0].strip()
            if not clean or clean.startswith(("http://", "https://")):
                continue
            resolved = (idx_path.parent / clean).resolve()
            if resolved.exists():
                try:
                    referenced.add(resolved.relative_to(repo_root.resolve()).as_posix())
                except ValueError:
                    pass
            else:
                dead_links.append(f"{idx_path.relative_to(repo_root).as_posix()} -> {clean}")
        for target in WIKI_LINK_RE.findall(text):
            referenced.add(target.strip())
    return referenced, dead_links


def run_audit(root: Path, json_out: Path | None = None) -> dict[str, Any]:
    kbs, docs = collect_docs(root)
    by_kb: dict[str, list[ConceptDoc]] = defaultdict(list)
    active_slug_map: dict[str, list[str]] = defaultdict(list)

    for doc in docs:
        by_kb[doc.kb_name].append(doc)
        status = str(doc.frontmatter.get("status", "active")).lower()
        if status not in ("archived", "deprecated"):
            active_slug_map[doc.abs_path.stem].append(doc.rel_path)

    kb_reports: list[dict[str, Any]] = []
    total_orphans = 0
    total_broken_links = 0
    total_missing_fm = 0
    total_unverified = 0
    total_dead_idx = 0
    total_stale = 0
    now = datetime.now(timezone.utc)

    kb_items = list(kbs)
    if "root-reports" in by_kb:
        kb_items.append(("root-reports", root))

    for kb_name, kb_path in kb_items:
        kb_docs = by_kb.get(kb_name, [])
        referenced, dead_index_links = collect_index_targets(kb_path, root)

        okf_count = 0
        llmwiki_count = 0
        orphans: list[str] = []
        broken_links: list[str] = []
        missing_required_fm: list[str] = []
        unverified_count = 0
        stale_count = 0
        archived_count = 0

        for doc in kb_docs:
            status = str(doc.frontmatter.get("status", "active")).lower()
            if status == "archived":
                archived_count += 1

            if doc.schema_style == "okf":
                okf_count += 1
                if not doc.frontmatter.get("type") or not doc.frontmatter.get("description"):
                    missing_required_fm.append(doc.rel_path)
            else:
                llmwiki_count += 1
                missing_required_fm.append(doc.rel_path)

            if not doc.frontmatter.get("verified"):
                unverified_count += 1

            stale_after = doc.frontmatter.get("stale_after")
            if isinstance(stale_after, str):
                try:
                    dt = datetime.fromisoformat(stale_after.replace("Z", "+00:00"))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    if dt < now:
                        stale_count += 1
                except ValueError:
                    pass

            if status not in ("archived", "deprecated"):
                if doc.rel_path not in referenced and doc.abs_path.stem not in referenced:
                    orphans.append(doc.rel_path)

            for target in doc.md_links:
                if "_source/" in target:
                    continue
                resolved = (doc.abs_path.parent / target).resolve()
                if not resolved.exists():
                    broken_links.append(f"{doc.rel_path} -> {target}")

        total_orphans += len(orphans)
        total_broken_links += len(broken_links)
        total_missing_fm += len(missing_required_fm)
        total_unverified += unverified_count
        total_dead_idx += len(dead_index_links)
        total_stale += stale_count

        kb_reports.append(
            {
                "kb": kb_name,
                "doc_count": len(kb_docs),
                "archived_docs": archived_count,
                "schema_breakdown": {"okf": okf_count, "no_frontmatter": llmwiki_count},
                "missing_okf_frontmatter": len(missing_required_fm),
                "unverified_docs": unverified_count,
                "stale_docs": stale_count,
                "orphan_docs": len(orphans),
                "dead_index_links": len(dead_index_links),
                "broken_internal_links": len(broken_links),
                "sample_orphans": orphans[:5],
                "sample_broken_links": (dead_index_links + broken_links)[:5],
            }
        )

    active_duplicates = {
        slug: paths for slug, paths in sorted(active_slug_map.items()) if len(paths) > 1
    }

    report = {
        "repo_root": str(root),
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_kbs": len(kb_items),
            "total_concept_docs": len(docs),
            "missing_okf_frontmatter": total_missing_fm,
            "unverified_docs": total_unverified,
            "stale_docs": total_stale,
            "orphan_docs": total_orphans,
            "dead_index_links": total_dead_idx,
            "broken_internal_links": total_broken_links,
            "active_duplicate_slugs": len(active_duplicates),
        },
        "kbs": kb_reports,
        "active_duplicate_slugs": active_duplicates,
    }

    if json_out:
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    return report


def chunk_markdown(doc: ConceptDoc, max_chars: int = 1200) -> list[tuple[str, str]]:
    lines = doc.body.splitlines()
    stack: list[tuple[int, str]] = []
    chunks: list[tuple[str, str]] = []
    buf: list[str] = []
    in_code = False

    def flush() -> None:
        text = "\n".join(buf).strip()
        if not text:
            return
        breadcrumb = " > ".join(h for _, h in stack) if stack else doc.title
        if len(text) <= max_chars:
            chunks.append((breadcrumb, text))
        else:
            paras = text.split("\n\n")
            cur: list[str] = []
            cur_len = 0
            for p in paras:
                if cur and cur_len + len(p) > max_chars:
                    chunks.append((breadcrumb, "\n\n".join(cur)))
                    cur = [p]
                    cur_len = len(p)
                else:
                    cur.append(p)
                    cur_len += len(p) + 2
            if cur:
                chunks.append((breadcrumb, "\n\n".join(cur)))

    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            buf.append(line)
            continue
        if not in_code:
            hm = HEADING_RE.match(line)
            if hm:
                flush()
                buf.clear()
                level = len(hm.group(1))
                heading_text = hm.group(2).strip()
                while stack and stack[-1][0] >= level:
                    stack.pop()
                stack.append((level, heading_text))
                continue
        buf.append(line)

    flush()
    if not chunks and doc.body.strip():
        chunks.append((doc.title, doc.body.strip()[:max_chars]))
    return chunks


def ensure_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS documents (
            doc_id TEXT PRIMARY KEY,
            kb_name TEXT NOT NULL,
            schema_style TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            doc_type TEXT NOT NULL,
            status TEXT NOT NULL,
            verified_at TEXT NOT NULL DEFAULT '',
            tags_json TEXT NOT NULL,
            links_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id TEXT NOT NULL,
            kb_name TEXT NOT NULL,
            doc_type TEXT NOT NULL,
            status TEXT NOT NULL,
            heading_breadcrumb TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
            doc_id UNINDEXED,
            kb_name UNINDEXED,
            title,
            description,
            heading_breadcrumb,
            tags,
            content,
            tokenize='unicode61'
        );
        """
    )
    # Schema migration guard for existing DBs
    cols = {row[1] for row in conn.execute("PRAGMA table_info(documents)").fetchall()}
    if "description" not in cols or "verified_at" not in cols:
        conn.executescript(
            """
            DROP TABLE IF EXISTS chunks_fts;
            DROP TABLE IF EXISTS chunks;
            DROP TABLE IF EXISTS documents;
            """
        )
        return ensure_db(db_path)
    return conn


def run_sync(root: Path, db_path: Path) -> dict[str, Any]:
    t0 = time.perf_counter()
    _, docs = collect_docs(root)
    conn = ensure_db(db_path)

    existing = {
        row[0]: row[1] for row in conn.execute("SELECT doc_id, sha256 FROM documents").fetchall()
    }
    current_ids = {d.rel_path for d in docs}

    added = 0
    updated = 0
    skipped = 0
    deleted = 0

    for old_id in set(existing.keys()) - current_ids:
        conn.execute("DELETE FROM chunks_fts WHERE doc_id = ?", (old_id,))
        conn.execute("DELETE FROM chunks WHERE doc_id = ?", (old_id,))
        conn.execute("DELETE FROM documents WHERE doc_id = ?", (old_id,))
        deleted += 1

    now_iso = datetime.now(timezone.utc).isoformat()
    for doc in docs:
        status = str(doc.frontmatter.get("status", "active")).lower()
        if status in ("deprecated", "archived"):
            if doc.rel_path in existing:
                conn.execute("DELETE FROM chunks_fts WHERE doc_id = ?", (doc.rel_path,))
                conn.execute("DELETE FROM chunks WHERE doc_id = ?", (doc.rel_path,))
                conn.execute("DELETE FROM documents WHERE doc_id = ?", (doc.rel_path,))
                deleted += 1
            continue

        if existing.get(doc.rel_path) == doc.sha256:
            skipped += 1
            continue

        if doc.rel_path in existing:
            conn.execute("DELETE FROM chunks_fts WHERE doc_id = ?", (doc.rel_path,))
            conn.execute("DELETE FROM chunks WHERE doc_id = ?", (doc.rel_path,))
            updated += 1
        else:
            added += 1

        doc_type = str(doc.frontmatter.get("type", "Concept"))
        raw_tags = doc.frontmatter.get("tags", [])
        tags = [str(t) for t in raw_tags] if isinstance(raw_tags, list) else []
        verified = doc.frontmatter.get("verified")
        verified_at = str(verified.get("at", "")) if isinstance(verified, dict) else ""

        conn.execute(
            """
            INSERT OR REPLACE INTO documents
            (doc_id, kb_name, schema_style, sha256, title, description, doc_type, status, verified_at, tags_json, links_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doc.rel_path,
                doc.kb_name,
                doc.schema_style,
                doc.sha256,
                doc.title,
                doc.description,
                doc_type,
                status,
                verified_at,
                json.dumps(tags, ensure_ascii=False),
                json.dumps(doc.resolved_links, ensure_ascii=False),
                now_iso,
            ),
        )

        tags_str = " ".join(tags)
        for breadcrumb, chunk_text in chunk_markdown(doc):
            conn.execute(
                """
                INSERT INTO chunks (doc_id, kb_name, doc_type, status, heading_breadcrumb, content)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (doc.rel_path, doc.kb_name, doc_type, status, breadcrumb, chunk_text),
            )
            conn.execute(
                """
                INSERT INTO chunks_fts (doc_id, kb_name, title, description, heading_breadcrumb, tags, content)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (doc.rel_path, doc.kb_name, doc.title, doc.description, breadcrumb, tags_str, chunk_text),
            )

    conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('last_synced_at', ?)", (now_iso,))
    conn.commit()
    total_docs = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    total_chunks = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    conn.close()
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)

    return {
        "added": added,
        "updated": updated,
        "skipped": skipped,
        "deleted": deleted,
        "total_docs_indexed": total_docs,
        "total_chunks": total_chunks,
        "elapsed_ms": elapsed_ms,
    }


def sanitize_fts_query(query: str) -> str:
    tokens = re.findall(r"[A-Za-z0-9_\u4e00-\u9fff]+", query)
    if not tokens:
        return '""'
    return " OR ".join(f'"{tok}"' for tok in tokens)


def _open_ro_db(db_path: Path) -> sqlite3.Connection:
    uri = f"file:{db_path.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def _run_ppr(
    adj: dict[str, list[str]],
    seeds: dict[str, float],
    alpha: float = 0.25,
    iters: int = 2,
) -> dict[str, float]:
    """Lightweight Personalized PageRank over explicit Markdown link graph."""
    total_seed = sum(seeds.values())
    if total_seed <= 0:
        return {}
    personal = {k: v / total_seed for k, v in seeds.items()}
    scores = dict(personal)
    for _ in range(iters):
        nxt: dict[str, float] = {k: alpha * v for k, v in personal.items()}
        for node, rank in scores.items():
            neighbors = adj.get(node, [])
            if not neighbors:
                continue
            share = (1.0 - alpha) * rank / len(neighbors)
            for nb in neighbors:
                nxt[nb] = nxt.get(nb, 0.0) + share
        scores = nxt
    return scores


def hybrid_search(
    db_path: Path,
    query: str,
    kb_filter: str | None = None,
    type_filter: str | None = None,
    top_k: int = 8,
    mode: str = "hybrid",
) -> list[dict[str, Any]]:
    top_k = max(1, min(top_k, 20))
    conn = _open_ro_db(db_path)
    fts_q = sanitize_fts_query(query)

    sql = """
        SELECT
            f.doc_id,
            f.kb_name,
            f.title,
            f.description,
            f.heading_breadcrumb,
            f.content,
            bm25(chunks_fts, 4.0, 2.0, 2.5, 2.0, 1.0) AS bm25_raw,
            d.doc_type,
            d.verified_at,
            d.links_json
        FROM chunks_fts f
        JOIN documents d ON d.doc_id = f.doc_id
        WHERE chunks_fts MATCH ?
          AND d.status NOT IN ('archived', 'deprecated')
    """
    params: list[Any] = [fts_q]
    if kb_filter:
        sql += " AND (f.kb_name = ? OR f.kb_name LIKE ?)"
        params.extend([kb_filter, f"{kb_filter}/%"])
    if type_filter:
        sql += " AND LOWER(d.doc_type) = LOWER(?)"
        params.append(type_filter)

    sql += " ORDER BY bm25_raw LIMIT ?"
    params.append(top_k * 4)

    rows = conn.execute(sql, params).fetchall()

    # Aggregate best chunk per doc_id from BM25
    best_by_doc: dict[str, dict[str, Any]] = {}
    bm25_order: list[str] = []
    for row in rows:
        doc_id, kb_name, title, desc, breadcrumb, content, bm25_raw, doc_type, verified_at, links_json = row
        if doc_id not in best_by_doc:
            bm25_order.append(doc_id)
            best_by_doc[doc_id] = {
                "doc_id": doc_id,
                "kb": kb_name,
                "type": doc_type,
                "title": title,
                "description": desc,
                "verified_at": verified_at,
                "matched_section": breadcrumb,
                "snippet": content[:260].replace("\n", " "),
                "bm25_score": round(float(bm25_raw), 4),
                "related_1hop": json.loads(links_json)[:6],
            }

    if mode == "exact" or not bm25_order:
        conn.close()
        return [best_by_doc[d] for d in bm25_order[:top_k]]

    # Build graph adjacency & run PPR seeded by top BM25 hits
    all_docs_rows = conn.execute(
        "SELECT doc_id, kb_name, title, description, doc_type, verified_at, links_json "
        "FROM documents WHERE status NOT IN ('archived', 'deprecated')"
    ).fetchall()

    adj: dict[str, list[str]] = {}
    doc_meta: dict[str, tuple[str, str, str, str, str, list[str]]] = {}
    for did, kbn, ttl, dsc, dtp, vat, ljson in all_docs_rows:
        links = json.loads(ljson)
        adj[did] = links
        doc_meta[did] = (kbn, ttl, dsc, dtp, vat, links)

    seeds = {did: 1.0 / (idx + 1) for idx, did in enumerate(bm25_order[:12])}
    ppr_scores = _run_ppr(adj, seeds)

    # Filter PPR candidates by kb/type if specified
    ppr_order = sorted(ppr_scores.keys(), key=lambda x: ppr_scores[x], reverse=True)
    filtered_ppr: list[str] = []
    for did in ppr_order:
        if did not in doc_meta:
            continue
        kbn, _, _, dtp, _, _ = doc_meta[did]
        if kb_filter and not (kbn == kb_filter or kbn.startswith(f"{kb_filter}/")):
            continue
        if type_filter and dtp.lower() != type_filter.lower():
            continue
        filtered_ppr.append(did)

    # RRF fusion (k=60)
    rrf_k = 60
    rrf: dict[str, float] = {}
    for rank, did in enumerate(bm25_order, start=1):
        rrf[did] = rrf.get(did, 0.0) + 1.0 / (rrf_k + rank)
    for rank, did in enumerate(filtered_ppr[: top_k * 3], start=1):
        rrf[did] = rrf.get(did, 0.0) + 0.6 / (rrf_k + rank)

    conn.close()
    ranked_ids = sorted(rrf.keys(), key=lambda x: rrf[x], reverse=True)[:top_k]

    results: list[dict[str, Any]] = []
    for did in ranked_ids:
        if did in best_by_doc:
            item = dict(best_by_doc[did])
        else:
            kbn, ttl, dsc, dtp, vat, links = doc_meta[did]
            item = {
                "doc_id": did,
                "kb": kbn,
                "type": dtp,
                "title": ttl,
                "description": dsc,
                "verified_at": vat,
                "matched_section": "(1-hop graph neighbor)",
                "snippet": dsc,
                "bm25_score": None,
                "related_1hop": links[:6],
            }
        item["rrf_score"] = round(rrf[did], 5)
        results.append(item)
    return results


def _extract_toc_and_section(body: str, section: str | None) -> tuple[list[str], str | None]:
    lines = body.splitlines()
    toc: list[str] = []
    headings: list[tuple[int, int, str]] = []  # (line_idx, level, title)
    in_code = False

    for idx, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            hm = HEADING_RE.match(line)
            if hm:
                lvl = len(hm.group(1))
                htitle = hm.group(2).strip()
                if lvl <= 3:
                    toc.append(f"{'#' * lvl} {htitle}")
                headings.append((idx, lvl, htitle))

    if not section:
        return toc, body

    sec_lower = section.strip().lower()
    target_idx = None
    target_lvl = 0
    for i, (line_idx, lvl, htitle) in enumerate(headings):
        if htitle.lower() == sec_lower or sec_lower in htitle.lower():
            target_idx = i
            target_lvl = lvl
            break

    if target_idx is None:
        return toc, None

    start_line = headings[target_idx][0]
    end_line = len(lines)
    for j in range(target_idx + 1, len(headings)):
        if headings[j][1] <= target_lvl:
            end_line = headings[j][0]
            break

    return toc, "\n".join(lines[start_line:end_line]).strip()


def read_doc(
    root: Path,
    db_path: Path,
    doc_id: str,
    section: str | None = None,
    include_links: bool = True,
    max_chars: int = 12000,
) -> dict[str, Any]:
    root_res = root.resolve()
    target = (root_res / doc_id).resolve()
    if not target.is_relative_to(root_res) or not target.is_file():
        return {"error": f"Invalid or missing doc_id: {doc_id}"}

    raw = target.read_text(encoding="utf-8", errors="replace")
    fm, body, style = parse_frontmatter(raw)
    status = str(fm.get("status", "active")).lower()

    toc, content = _extract_toc_and_section(body, section)
    if section and content is None:
        return {
            "doc_id": doc_id,
            "error": f"Section '{section}' not found.",
            "toc": toc,
        }

    truncated = False
    assert content is not None
    if len(content) > max_chars:
        content = content[:max_chars].rstrip() + "\n\n... [TRUNCATED: pass `section` to read specific subsections]"
        truncated = True

    resp: dict[str, Any] = {
        "doc_id": doc_id,
        "schema_style": style,
        "metadata": fm,
        "toc": toc,
        "truncated": truncated,
        "content": content,
    }
    if status in ("archived", "deprecated"):
        resp["warning"] = f"This document is `{status}`."
        if fm.get("canonical_ref"):
            resp["canonical_ref"] = fm["canonical_ref"]

    if include_links and db_path.exists():
        conn = _open_ro_db(db_path)
        row = conn.execute("SELECT links_json FROM documents WHERE doc_id = ?", (doc_id,)).fetchone()
        outbound_ids = json.loads(row[0]) if row else []

        inbound_rows = conn.execute(
            "SELECT doc_id, title FROM documents WHERE links_json LIKE ? AND doc_id != ?",
            (f'%"{doc_id}"%', doc_id),
        ).fetchall()

        outbound_meta = []
        for oid in outbound_ids[:10]:
            orow = conn.execute("SELECT title, description FROM documents WHERE doc_id = ?", (oid,)).fetchone()
            outbound_meta.append(
                {"doc_id": oid, "title": orow[0] if orow else oid, "description": orow[1] if orow else ""}
            )
        conn.close()

        resp["outbound_links"] = outbound_meta
        resp["inbound_links"] = [{"doc_id": r[0], "title": r[1]} for r in inbound_rows[:10]]

    return resp


def get_status(
    root: Path,
    db_path: Path,
    include_audit: bool = False,
    kb_filter: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "kb_root": str(root.resolve()),
        "db_path": str(db_path.resolve()),
        "index_exists": db_path.exists(),
    }

    if db_path.exists():
        conn = _open_ro_db(db_path)
        meta_row = conn.execute("SELECT value FROM meta WHERE key = 'last_synced_at'").fetchone()
        last_synced = meta_row[0] if meta_row else None
        total_docs = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        total_chunks = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]

        if kb_filter:
            kb_rows = conn.execute(
                "SELECT kb_name, COUNT(*) FROM documents WHERE kb_name = ? OR kb_name LIKE ? GROUP BY kb_name ORDER BY kb_name",
                (kb_filter, f"{kb_filter}/%"),
            ).fetchall()
        else:
            kb_rows = conn.execute(
                "SELECT kb_name, COUNT(*) FROM documents GROUP BY kb_name ORDER BY kb_name"
            ).fetchall()
        conn.close()

        needs_sync = False
        if last_synced:
            try:
                sync_ts = datetime.fromisoformat(last_synced.replace("Z", "+00:00")).timestamp()
                for _, kb_path in discover_kbs(root):
                    for md in kb_path.rglob("*.md"):
                        if md.stat().st_mtime > sync_ts:
                            needs_sync = True
                            break
                    if needs_sync:
                        break
            except ValueError:
                pass

        result.update(
            {
                "last_synced_at": last_synced,
                "needs_sync": needs_sync,
                "total_docs_indexed": total_docs,
                "total_chunks": total_chunks,
                "indexed_kbs": {r[0]: r[1] for r in kb_rows},
            }
        )

    if include_audit:
        audit_report = run_audit(root)
        if kb_filter:
            audit_report["kbs"] = [
                k for k in audit_report["kbs"] if k["kb"] == kb_filter or k["kb"].startswith(f"{kb_filter}/")
            ]
        result["audit"] = audit_report

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="KB Governance Linter & Hybrid Retrieval CLI")
    parser.add_argument("--root", type=Path, default=Path("."), help="Knowledge repo root")
    parser.add_argument("--db", type=Path, default=None, help="SQLite index path")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_audit = sub.add_parser("audit", help="Run knowledge governance audit")
    p_audit.add_argument("--json-out", type=Path, default=None)

    sub.add_parser("sync", help="Run incremental structure-aware FTS5 sync")

    p_search = sub.add_parser("search", help="Search the indexed knowledge base")
    p_search.add_argument("query", type=str)
    p_search.add_argument("--kb", type=str, default=None)
    p_search.add_argument("--type", type=str, default=None)
    p_search.add_argument("--top-k", type=int, default=8)
    p_search.add_argument("--mode", choices=["hybrid", "exact"], default="hybrid")

    p_read = sub.add_parser("read", help="Read a document or section by doc_id")
    p_read.add_argument("doc_id", type=str)
    p_read.add_argument("--section", type=str, default=None)

    p_status = sub.add_parser("status", help="Show KB index & optional audit status")
    p_status.add_argument("--audit", action="store_true")
    p_status.add_argument("--kb", type=str, default=None)

    args = parser.parse_args()
    root = args.root.resolve()
    db_path = args.db.resolve() if args.db else root / ".kb_index" / "kb_index.sqlite"

    if args.cmd == "audit":
        print(json.dumps(run_audit(root, args.json_out), indent=2, ensure_ascii=False))
    elif args.cmd == "sync":
        print(json.dumps(run_sync(root, db_path), indent=2, ensure_ascii=False))
    elif args.cmd == "search":
        print(
            json.dumps(
                hybrid_search(db_path, args.query, args.kb, args.type, args.top_k, args.mode),
                indent=2,
                ensure_ascii=False,
            )
        )
    elif args.cmd == "read":
        print(json.dumps(read_doc(root, db_path, args.doc_id, args.section), indent=2, ensure_ascii=False))
    elif args.cmd == "status":
        print(json.dumps(get_status(root, db_path, args.audit, args.kb), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
