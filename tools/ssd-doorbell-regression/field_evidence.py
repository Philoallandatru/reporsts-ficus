import re

from concise_review import concise_passages
from decision_checks import DOORBELL_PAGES


NVME_WINDOWS = (
    (r"\b(?:IDLP|IPS)\b", 352, 13, 27),
    (r"\b(?:DNR|Do Not Retry)\b", 162, 7, 14),
    (r"\bFlush\b", 485, 22, 33),
)
SLOT_ACCEPTANCE = re.compile(r"槽位|条目边界|最远|最高(?:合法|编号)|\b(?:SQ Tail|CQ Head)\b", re.IGNORECASE)
NOTIFICATION_ACCEPTANCE = re.compile(
    r"\bMMIO\b|通知|跨(?:过|越)?阈值|回绕|漏写|写不写|(?:要|需|该|未|补|省).{0,3}写.{0,5}(?:门铃|doorbell)",
    re.IGNORECASE,
)


def field_passages(index, protocol, question):
    passages = []
    if protocol == "nvme":
        for term, page, first, last in NVME_WINDOWS:
            if re.search(term, question, re.IGNORECASE):
                text = index.read_page(protocol, page)
                passages.append({"pdf_page": page, "lines": [first, last],
                                 "passage": "\n".join(text.splitlines()[first - 1:last])})
    if passages:
        return passages
    passages = concise_passages(index, protocol, question)
    request = question.partition("\n\n现场观测\n")[0]
    if (protocol == "nvme" and SLOT_ACCEPTANCE.search(request)
            and not NOTIFICATION_ACCEPTANCE.search(request)
            and set(DOORBELL_PAGES).issubset(entry["pdf_page"] for entry in passages)):
        return [entry for entry in passages if entry["pdf_page"] != 702]
    return passages
