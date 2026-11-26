import evidence_mcp as evidence
import evidence_conditions_mcp


@evidence.mcp.tool()
async def find_spec_conditions(protocol: evidence.Protocol, query: str) -> dict:
    """Find original condition windows on the two best pages for distinct English field or event names. Returns neighboring conditions and file page numbers in one call."""
    with evidence.request("find_spec_conditions", protocol, query=query) as event:
        if not query.strip() or len(query) > 240:
            raise ValueError("Provide field or event names in a nonempty query of up to 240 characters")
        index = evidence.retriever(protocol)
        hits = index.search(protocol, query, evidence.MODE, k=2)
        results = []
        seen = set()
        for hit in hits:
            page = hit["pdf_page"]
            excerpt = index.outcome_passage(protocol, page, query)
            if not excerpt["lines"]:
                continue
            lines = index.read_page(protocol, page).splitlines()
            first, last = excerpt["lines"]
            start, end = max(1, first - 6), min(len(lines), last + 12)
            for neighbor, begin, finish, body in (
                (page, start, end, lines),
                (page - 1, -15, -1, index.read_page(protocol, page - 1).splitlines() if start == 1 and page > 1 else []),
                (page + 1, 1, 16, index.read_page(protocol, page + 1).splitlines()
                 if end == len(lines) and page < evidence.PAGE_COUNTS[protocol] else []),
            ):
                if not body:
                    continue
                begin = max(1, len(body) + begin + 1) if begin < 0 else begin
                finish = len(body) if finish < 0 else min(finish, len(body))
                key = (neighbor, begin, finish)
                if key not in seen:
                    seen.add(key)
                    results.append({"pdf_page": neighbor, "lines": [begin, finish], "text": "\n".join(body[begin - 1:finish])})
        event["pages"] = list(dict.fromkeys(r["pdf_page"] for r in results))
        return {"spec": evidence.SPEC[protocol], "results": results,
                "coverage": "Candidate windows can contain unrelated fields. Inspect the exact field, scope and any missing continuation before deciding."}


if __name__ == "__main__":
    try:
        evidence.mcp.run(transport="stdio")
    finally:
        if evidence.engine:
            evidence.engine.close()
