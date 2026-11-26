import evidence_mcp as evidence
import evidence_fast_conditions_mcp
from decision_checks import DOORBELL_PAGES, doorbell_layout


@evidence.mcp.tool()
async def check_doorbell_layout(cc_mps: int, cap_dstrd: int, nsqa: int, ncqa: int,
                               max_sqid: int | None = None, max_cqid: int | None = None) -> dict:
    """Compute NVMe 2.1 Doorbell Buffer Config bounds in each page. Supply raw CC.MPS, CAP.DSTRD and zero-based NSQA/NCQA encodings. Optional max_sqid and max_cqid are the actual largest queue IDs accessed in the plan. Separate the printed size condition, Figure 486 range and proposed slots."""
    with evidence.request("check_doorbell_layout", "nvme", pages=DOORBELL_PAGES):
        if evidence.SCOPE not in ("both", "nvme"):
            raise ValueError(f"This session is restricted to {evidence.SCOPE}")
        return {"spec": evidence.SPEC["nvme"], "pdf_pages": DOORBELL_PAGES,
                **doorbell_layout(cc_mps, cap_dstrd, nsqa, ncqa, max_sqid, max_cqid),
                "scope": "Byte offsets within each buffer only. Check buffer addresses, queue validity and command completion separately."}


if __name__ == "__main__":
    try:
        evidence.mcp.run(transport="stdio")
    finally:
        if evidence.engine:
            evidence.engine.close()
