"""Read-only specification evidence server for retrieval and Pi experiments."""
import os
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP

from benchmark import PAGE_COUNTS, ROOT
from retrieval_trial import PageRetriever, WORD, page_outcomes

Protocol = Literal["nvme", "pcie"]
SPEC = {"nvme": "NVM Express Base Specification, Revision 2.1",
        "pcie": "PCI Express Base Specification, Revision 5.0 Version 1.0"}
MODE = os.getenv("SPEC_EVAL_MODE", "domain")
VIEW = os.getenv("SPEC_EVAL_EVIDENCE_VIEW", "classic")
if VIEW not in {"classic", "bounded", "outcomes", "decision"}:
    raise ValueError("SPEC_EVAL_EVIDENCE_VIEW must be classic, bounded, outcomes or decision")
SCOPE = os.getenv("SPEC_EVAL_PROTOCOL", "both")
LIMIT = int(os.getenv("SPEC_EVAL_CALL_LIMIT", "0"))
AUDIT = os.getenv("SPEC_EVAL_AUDIT")
mcp = FastMCP("spec-evidence")
engine = None
attempts = 0


@contextmanager
def request(tool, protocol, **fields):
    global attempts
    attempts += 1
    event = {"attempt": attempts, "tool": tool, "protocol": protocol, **fields}
    try:
        if LIMIT and attempts > LIMIT:
            raise ValueError("Evidence call budget exhausted; answer from evidence already returned")
        yield event
        event["status"] = "ok"
    except Exception as error:
        event["status"] = "error"
        event["error"] = str(error)
        raise
    finally:
        if AUDIT:
            with Path(AUDIT).open("a", encoding="utf-8") as out:
                out.write(json.dumps(event, ensure_ascii=False) + "\n")


def retriever(protocol):
    global engine
    if SCOPE not in ("both", protocol):
        raise ValueError(f"This session is restricted to {SCOPE}")
    if engine is None:
        engine = PageRetriever(ROOT)
    return engine


@mcp.tool()
async def search_spec(protocol: Protocol, query: str, top_k: int = 3) -> dict:
    """Search NVMe Base 2.1 or PCIe Base 5.0 v1.0. Returns original passages with 1-based PDF file page numbers."""
    with request("search_spec", protocol, query=query) as event:
        if not query.strip() or len(query) > 1200 or not 1 <= top_k <= 5:
            raise ValueError("Provide a nonempty query under 1201 characters and top_k in 1..5")
        index = retriever(protocol)
        hits = index.search(protocol, query, MODE, k=top_k)
        if VIEW in {"bounded", "outcomes", "decision"}:
            passage = index.scoped_passage if VIEW == "bounded" else index.outcome_passage
            results = [{**hit, **passage(protocol, hit["pdf_page"], query)} for hit in hits]
            event["passage_lines"] = [r["lines"] for r in results]
        else:
            results = [{**hit, "passage": index.preview(protocol, hit["pdf_page"], query)} for hit in hits]
        event["pages"] = [h["pdf_page"] for h in hits]
        response = {"spec": SPEC[protocol], "results": results}
        if VIEW in {"outcomes", "decision"}:
            response["coverage"] = "Value-table rows are [encoding, first line, last line] on one PDF page. Check the field and original definitions before grouping outcomes. Unlisted codes or observations have no implied disposition."
        return response


@mcp.tool()
async def read_spec_page(protocol: Protocol, pdf_page: int) -> dict:
    """Read the full original text of a 1-based PDF page, including continuation pages and tables."""
    with request("read_spec_page", protocol, pdf_page=pdf_page):
        index = retriever(protocol)
        body = index.read_page(protocol, pdf_page)
        result = {"spec": SPEC[protocol], "pdf_page": pdf_page, "text": body}
        if VIEW in {"bounded", "outcomes", "decision"}:
            result["section_bookmarks"] = index.page_bookmarks(protocol, pdf_page, body)
        if VIEW in {"outcomes", "decision"}:
            result["page_outcomes"] = page_outcomes(body, result["section_bookmarks"])
            result["coverage"] = "Original text above; 1-based inclusive line numbers. Each row is [encoding, first line, last line]. This page-local index recognizes some layouts only. At page boundaries inspect adjacent pages. Unlisted outcomes do not imply a default action."
        return result


def literal_passages(body, terms):
    lines = body.splitlines()
    located = [(word, i) for i, line in enumerate(lines) for word in WORD.findall(line.lower())]
    words = [word for word, _ in located]
    passages = []
    covered = -1
    for pos in range(len(words) - len(terms) + 1):
        first = located[pos][1]
        if first <= covered or words[pos:pos + len(terms)] != terms:
            continue
        last = located[pos + len(terms) - 1][1]
        start, end = max(0, first - 4), min(len(lines), last + 10)
        passages.append({"match_lines": [first + 1, last + 1], "lines": [start + 1, end],
                         "text": "\n".join(lines[start:end])})
        covered = end - 1
        if len(passages) == 2:
            break
    return passages


async def read_spec_context(protocol: Protocol, pdf_page: int, cue: str) -> dict:
    """Verify an exact field name or short original English phrase on a candidate PDF page and its neighbors. Returns matching lines with surrounding source text. A miss does not mean the rule is absent."""
    with request("read_spec_context", protocol, pdf_page=pdf_page, cue=cue) as event:
        terms = WORD.findall(cue.lower())
        if len(cue) > 120 or not 2 <= len(terms) <= 14:
            raise ValueError("Use two to fourteen words from one field name or original phrase")
        if not 1 <= pdf_page <= PAGE_COUNTS[protocol]:
            raise ValueError("PDF page outside the source")
        index = retriever(protocol)
        passages = []
        examined = []
        for page in (pdf_page, pdf_page - 1, pdf_page + 1):
            if not 1 <= page <= PAGE_COUNTS[protocol]:
                continue
            body = index.read_page(protocol, page)
            examined.append(page)
            matches = literal_passages(body, terms)
            if matches:
                bookmarks = index.page_bookmarks(protocol, page, body)
                for match in matches:
                    headings = [b for b in bookmarks if b["pdf_page"] < page
                                or 0 < b.get("line", 0) <= match["match_lines"][0]]
                    passages.append({"pdf_page": page, "section": headings[-1] if headings else None, **match})
        event["pages_examined"] = examined
        event["matching_ranges"] = [[match["pdf_page"], *match["lines"]] for match in passages]
        return {"spec": SPEC[protocol], "cue": cue, "pages_examined": examined, "matches": passages,
                "coverage": "Original wording around literal matches only. Verify which register, field or subject owns the rule. No match does not establish absence."}


if VIEW == "decision":
    mcp.tool()(read_spec_context)


if __name__ == "__main__":
    try:
        mcp.run(transport="stdio")
    finally:
        if engine:
            engine.close()
