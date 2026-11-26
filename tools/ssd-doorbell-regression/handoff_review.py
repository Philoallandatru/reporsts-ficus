import json
from pathlib import Path
import re
import subprocess


PROMPT = """你为 SSD 工单签发最终交接答复。收到的材料是题面事实、规范返回的原文、以及待审草稿。
先在内部给每项关键事实定作用对象、来源和时间。出现历史窗口、复位前后或一次事务归因时，要求同一对象当时的记录或可证明不中断的覆盖关系。后读的状态、锁存位和当前计数，按规范类型只说能证实的范围。恢复后无报错不能抹掉早期故障。一次明确记录到的完成、清除和自动转换仍可按条款给出其确定的直接后果。
只交付题面要求的动作、直接成立的条件与证据。已确认的事实可以直接用。撤掉草稿中越权的诊断、时刻、下界、其他字段、重新配置和泛化分支。拒绝执行时，如同一动作存在明确的最早恢复条件就写出来；缺历史证据时只交代当时哪一条记录能补足，复测只产生下一轮证据。不要把规范页当作现场采样记录。
只输出 JSON 对象，三个字符串字段 decision、evidence、next_check。证据引用已有规范原文的文件页，确实缺证就写明。next_check 在无需补证时填空。三项合计尽量在 240 个汉字内。"""


def messages(path):
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "message_end":
            yield event.get("message", {})


def message_text(message):
    content = message.get("content", [])
    return content if isinstance(content, str) else "\n".join(item.get("text", "") for item in content)


def original_excerpts(events, prefetch):
    tools = [message_text(m) for m in messages(events) if m.get("role") == "toolResult" and not m.get("isError")]
    records = [*reversed([entry[:3000] for entry in tools]), prefetch[:3000]]
    return "\n\n".join(records)[:13500]


def format_handoff(raw):
    try:
        entry = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip()))
    except ValueError:
        return ""
    keys = {"decision", "evidence", "next_check"}
    if (not isinstance(entry, dict) or entry.keys() != keys or any(not isinstance(entry[k], str) for k in keys)
            or not entry["decision"].strip() or not entry["evidence"].strip()):
        return ""
    return "\n\n".join(f"**{label}** {entry[key].strip()}" for key, label in
                       [("decision", "处置"), ("evidence", "依据"), ("next_check", "必要核验")]
                       if entry[key].strip())


def sign_handoff(command_start, args, env, session, outdir, row, draft, excerpts, timeout,
                 prompt=PROMPT, formatter=format_handoff):
    if timeout <= 0:
        return "", "timeout"
    packet = json.dumps({"工单": row["question"], "草稿": draft[:3500], "规范原文": excerpts}, ensure_ascii=False)
    command = [*command_start, "-ne", "--no-tools", "--no-mcp", "-nc", "-ns", "-np", "--offline",
               "--no-session", "--no-approve", "--provider", args.provider, "--model", args.review_model or args.model,
               "--thinking", "off", "--mode", "json", "-p", prompt + "\n\n" + packet]
    output = outdir / "handoff-events.jsonl"
    with output.open("wb") as stdout, (outdir / "handoff-stderr.log").open("wb") as stderr:
        try:
            reply = subprocess.run(command, cwd=session, env=env, stdout=stdout, stderr=stderr, timeout=timeout)
        except subprocess.TimeoutExpired:
            return "", "timeout"
    if reply.returncode:
        return "", "error"
    final = [message_text(m) for m in messages(output) if m.get("role") == "assistant" and m.get("stopReason") == "stop"]
    answer = formatter(final[-1]) if final else ""
    return answer, "ok" if answer else "invalid"
