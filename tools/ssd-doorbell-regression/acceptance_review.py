import json
import re

from condition_review import format_conditions
from decision_checks import verification_passages


PROMPT = """按题面证据与规范原文签发 SSD 工单。说明当前处置、所有改变决定的前提和例外。历史归因只用同一对象同期或连续覆盖证据。每条规范规则附实际核对的 PDF 文件页。
只输出 JSON。decision 是当前处置；conditions 是 1–5 条短依据；checks 是必要的核验行，每行包含三个非空字符串 target（测什么）、record（读哪个字段或哪条现场记录）、pass（什么结果才能签）。建议替代路径时，把其放行条件也落实为核验行。工单只要求解释或限定了范围时按题面回答。缺记录就待验，试验要求与规范条款分别表述。"""


def acceptance_passages(index, protocol, question):
    passages = verification_passages(index, protocol, question)
    if (protocol == "pcie" and re.search(r"\bMSI-X\b", question, re.IGNORECASE)
            and re.search(r"Message Address|Message Data|Address\s*/\s*Data|地址|消息载荷", question, re.IGNORECASE)):
        for page, first, last in ((500, 1, 4), (500, 14, 31), (501, 1, 4)):
            lines = index.read_page(protocol, page).splitlines()
            passages.append({"pdf_page": page, "lines": [first, last], "passage": "\n".join(lines[first - 1:last])})
    return passages


def format_acceptance(raw):
    raw = raw.strip()
    try:
        start = raw.index("{")
        entry, end = json.JSONDecoder().raw_decode(raw, start)
    except ValueError:
        return ""
    if raw[end:].strip() not in ("", "```") or entry.keys() != {"decision", "conditions", "checks"}:
        return ""
    checks = entry["checks"]
    if not isinstance(checks, list) or len(checks) > 5:
        return ""
    lines = []
    for check in checks:
        if (not isinstance(check, dict) or check.keys() != {"target", "record", "pass"}
                or any(not isinstance(value, str) or not value.strip() for value in check.values())):
            return ""
        target, record, passed = (check[key].strip().rstrip("。") for key in ("target", "record", "pass"))
        if not (target and record and passed):
            return ""
        lines.append(f"- **{target}**。记录为{record}。通过条件为{passed}。")
    answer = format_conditions(json.dumps({"decision": entry["decision"], "conditions": entry["conditions"], "next_check": ""}))
    if not answer or not lines:
        return answer
    return answer + "\n\n**现场验收**\n" + "\n".join(lines)
