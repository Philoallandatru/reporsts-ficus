import evidence_mcp as evidence


@evidence.mcp.tool()
async def read_spec_transition(protocol: evidence.Protocol, pdf_page: int, trigger: str, state: str) -> dict:
    """Find a rule's trigger and its resulting state as separate literal excerpts, including adjacent pages. The result contains spec rules only, with no event timestamps."""
    with evidence.request("read_spec_transition", protocol, pdf_page=pdf_page) as event:
        if not 1 <= pdf_page <= evidence.PAGE_COUNTS[protocol]:
            raise ValueError("PDF page outside the source")
        cues = {"trigger": trigger, "state": state}
        terms = {name: evidence.WORD.findall(cue.lower()) for name, cue in cues.items()}
        if any(not 2 <= len(tokens) <= 14 for tokens in terms.values()) or any(len(cue) > 120 for cue in cues.values()):
            raise ValueError("Use two to fourteen original words for each cue")
        index = evidence.retriever(protocol)
        pages = [p for p in (pdf_page, pdf_page - 1, pdf_page + 1) if 1 <= p <= evidence.PAGE_COUNTS[protocol]]
        matches = {name: [] for name in cues}
        for page in pages:
            body = index.read_page(protocol, page)
            for name, tokens in terms.items():
                matches[name].extend({"pdf_page": page, **m} for m in evidence.literal_passages(body, tokens))
        event["pages_examined"] = pages
        event["matching_ranges"] = sorted({(m["pdf_page"], *m["lines"]) for group in matches.values() for m in group})
        return {"spec": evidence.SPEC[protocol], "cues": cues, "matches": matches, "pages_examined": pages,
                "coverage": "Check that both excerpts describe the same transition and object. A rule does not date a field event or establish that another event did not occur."}


if __name__ == "__main__":
    try:
        evidence.mcp.run(transport="stdio")
    finally:
        if evidence.engine:
            evidence.engine.close()
