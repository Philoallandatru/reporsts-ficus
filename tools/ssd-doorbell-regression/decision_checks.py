import re


DOORBELL_PAGES = (445, 446)
CHECK_PASSAGES = {
    "nvme": (
        (r"doorbell buffer|shadow doorbell|\beventidx\b|影子门铃|门铃缓冲", ((445, 21, 59), (446, 9, 29), (702, 4, 27))),
        (r"\bfused\b|\bfuse\b|融合命令|融合操作", ((120, 30, 50), (121, 4, 14), (160, 36, 49))),
    ),
    "pcie": (
        (r"steering tag|\bst table\b|\btph\b|转向标签", ((607, 12, 20), (607, 38, 45), (608, 1, 15), (789, 11, 28))),
    ),
}


def verification_passages(index, protocol, question):
    return [
        {"pdf_page": page, "lines": [first, last],
         "passage": "\n".join(index.read_page(protocol, page).splitlines()[first - 1:last])}
        for pattern, spans in CHECK_PASSAGES[protocol] if re.search(pattern, question, re.IGNORECASE)
        for page, first, last in spans
    ]


def doorbell_layout(cc_mps, cap_dstrd, nsqa, ncqa, max_sqid=None, max_cqid=None):
    for name, value, limit in (("cc_mps", cc_mps, 15), ("cap_dstrd", cap_dstrd, 15),
                               ("nsqa", nsqa, 65535), ("ncqa", ncqa, 65535),
                               ("max_sqid", max_sqid, 65535), ("max_cqid", max_cqid, 65535)):
        if value is None and name in ("max_sqid", "max_cqid"):
            continue
        if type(value) is not int or not 0 <= value <= limit:
            raise ValueError(f"{name} must be an integer from 0 to {limit}")

    page_bytes = 1 << (12 + cc_mps)
    stride_bytes = 4 << cap_dstrd
    y = max(nsqa, ncqa)
    formula_bytes = (y + 1) * stride_bytes

    def slot(queue_id, direction):
        if queue_id is None:
            return None
        first = (2 * queue_id + direction) * stride_bytes
        return {"queue_id": queue_id, "first_byte": first, "last_byte": first + 3,
                "fits_in_page": first + 3 < page_bytes}

    return {"page_bytes": page_bytes, "stride_bytes": stride_bytes, "figure_y": y,
            "printed_condition": {"bytes": formula_bytes, "fits_in_page": formula_bytes <= page_bytes},
            "figure_486": {"sq_tail": slot(y, 0), "cq_head": slot(y, 1)},
            "proposed_slots": {"sq_tail": slot(max_sqid, 0), "cq_head": slot(max_cqid, 1)}}
