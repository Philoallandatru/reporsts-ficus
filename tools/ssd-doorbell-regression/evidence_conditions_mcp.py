import evidence_mcp as evidence
import evidence_timeline_mcp


@evidence.mcp.tool()
async def read_spec_conditions(protocol: evidence.Protocol, field: str, pdf_page: int, top_k: int = 2) -> dict:
    """Read all nearby lines for an exact English field name on a candidate page and its neighbors. Use this to retain conjunctions, alternative paths, and page continuations."""
    with evidence.request("read_spec_conditions", protocol, pdf_page=pdf_page, field=field) as event:
        terms = evidence.WORD.findall(field.lower())
        if not 2 <= len(terms) <= 14 or len(field) > 120 or top_k not in (1, 2, 3):
            raise ValueError("Use a two to fourteen word field name and one to three matches")
        if not 1 <= pdf_page <= evidence.PAGE_COUNTS[protocol]:
            raise ValueError("PDF page outside the source")
        index = evidence.retriever(protocol)
        pages = [p for p in (pdf_page, pdf_page - 1, pdf_page + 1) if 1 <= p <= evidence.PAGE_COUNTS[protocol]]
        matches = []
        for page in pages:
            body = index.read_page(protocol, page)
            lines = body.splitlines()
            for match in evidence.literal_passages(body, terms):
                first, last = match["match_lines"]
                start, end = max(1, first - 6), min(len(lines), last + 16)
                item = {"pdf_page": page, "lines": [start, end], "text": "\n".join(lines[start-1:end])}
                is_definition = any(":" in line or " - " in line for line in lines[first-1:last])
                matches.append((not is_definition, page != pdf_page, page, first, item))
        result = []
        seen = set()
        for _, _, page, _, item in sorted(matches, key=lambda m: m[:4])[:top_k]:
            tag = (page, *item["lines"])
            if tag not in seen:
                seen.add(tag)
                result.append(item)
            if item["lines"][1] == len(index.read_page(protocol, page).splitlines()) and page < evidence.PAGE_COUNTS[protocol]:
                following = index.read_page(protocol, page + 1).splitlines()[:16]
                tag = (page + 1, 1, len(following))
                if following and tag not in seen:
                    seen.add(tag)
                    result.append({"pdf_page": page + 1, "lines": [1, len(following)], "text": "\n".join(following)})
        event["pages_examined"] = sorted(set(pages) | {m["pdf_page"] for m in result})
        event["matching_ranges"] = [[m["pdf_page"], *m["lines"]] for m in result]
        return {"spec": evidence.SPEC[protocol], "field": field, "matches": result,
                "coverage": "Quoted lines may contain nearby fields. Verify scope before treating a condition or alternative as part of the named field."}


if __name__ == "__main__":
    try:
        evidence.mcp.run(transport="stdio")
    finally:
        if evidence.engine:
            evidence.engine.close()
