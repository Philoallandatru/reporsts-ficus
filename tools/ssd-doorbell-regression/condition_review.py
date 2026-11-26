import json
import re

from handoff_review import message_text, messages


PROMPT = """你为 SSD 工单签发最终交接。题面提供现场事实，规范逐页摘录提供可核对的规则，草稿需要重新核对。
先查其它路径或门槛会不会改变同一动作。拒绝签署时写下导致拒绝的规范条件、任何会改变判断的另一种路径，以及对应的放行条件。允许执行时交代已满足的关键前提。把 AND、OR、例外、初始态、清除、完成和超时条件在输出中保留下来，包括草稿已写、原文已支持的条件。不要仅留下结论或状态名，把规范原句与题面的证据明确对应。
历史判断须同一对象、同一时点或能覆盖历史区间的记录。规范给出规则，事后读数只用于其实际时点。若条件只支持一种可能，不要说已发生。只写会影响本次判断或执行的条件，删除无关行为、未授权动作和出处不明的精确值。引用对应摘录的 PDF 文件页。
只输出 JSON 对象。decision 是当前处置的短字符串。conditions 是 1 到 5 个短字符串，每条说明一个关键条件、作用域或备选路径，附已有文件页。next_check 是必要核验或恢复门槛，无需核验时填空字符串。不要删掉必要条件来缩短文字。"""


def source_parts(response):
    if not isinstance(response, dict) or "spec" not in response:
        return
    standard = "NVMe" if response["spec"].startswith("NVM") else "PCIe"
    matches = response.get("matches")
    if isinstance(matches, dict):
        matches = [match for group in matches.values() for match in group]
    for item in response.get("results") or matches or [response]:
        content = item.get("text") or item.get("passage")
        if content and type(item.get("pdf_page")) is int:
            yield standard, item["pdf_page"], content


def condition_excerpts(events, prefetch, limit=13800):
    blocks = []
    parts = re.split(r"(?:^|\n\n)(NVME|PCIE) PDF p\.(\d+)\n", prefetch)
    for protocol, page, raw in zip(parts[1::3], parts[2::3], parts[3::3]):
        try:
            excerpt = json.loads(raw)
        except ValueError:
            excerpt = {"passage": raw}
        if excerpt.get("passage"):
            blocks.append((2, "NVMe" if protocol == "NVME" else "PCIe", int(page), excerpt["passage"]))
    for m in messages(events):
        if m.get("role") != "toolResult" or m.get("isError"):
            continue
        try:
            entry = json.loads(message_text(m))
        except ValueError:
            continue
        tool = m.get("toolName", "")
        priority = 0 if tool.endswith(("read_spec_conditions", "read_spec_transition", "read_spec_context")) else 1
        blocks.extend((priority, protocol, page, content) for protocol, page, content in source_parts(entry))
    seen = set()
    output = []
    for _, protocol, page, content in sorted(blocks, key=lambda block: block[0]):
        descriptor = (protocol, page, " ".join(content.split()))
        if descriptor in seen:
            continue
        seen.add(descriptor)
        block = f"{protocol} PDF p.{page}\n{content.strip()}\n\n"
        if len(block) <= limit:
            output.append(block)
            limit -= len(block)
    return "".join(output).rstrip()


def format_conditions(raw):
    try:
        entry = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip()))
    except ValueError:
        return ""
    if not isinstance(entry, dict) or entry.keys() != {"decision", "conditions", "next_check"}:
        return ""
    conditions = entry["conditions"]
    if (not isinstance(entry["decision"], str) or not entry["decision"].strip()
            or not isinstance(entry["next_check"], str) or not isinstance(conditions, list)
            or not 1 <= len(conditions) <= 5 or any(not isinstance(x, str) or not x.strip() for x in conditions)):
        return ""
    basis = "\n".join(f"- {item.strip()}" for item in conditions)
    next_step = f"\n\n**必要核验** {entry['next_check'].strip()}" if entry["next_check"].strip() else ""
    return f"**处置** {entry['decision'].strip()}\n\n**判定条件**\n{basis}{next_step}"
