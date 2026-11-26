"""Run isolated Pi sessions with a page-evidence MCP and a server-side call budget."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

from benchmark import ROOT
from acceptance_review import PROMPT as ACCEPTANCE_PROMPT, acceptance_passages, format_acceptance
from concise_review import PROMPT as CONCISE_PROMPT, concise_passages
from condition_review import PROMPT as CONDITION_PROMPT, condition_excerpts, format_conditions
from decision_checks import verification_passages
from field_evidence import field_passages
from handoff_review import original_excerpts, sign_handoff
from trial_timing import phases, tool_wait_seconds

HERE = Path(__file__).resolve().parent


def prefetch_pages(row, mode, audit, view="classic", *, verified=False, acceptance=False, concise=False, field=False):
    from retrieval_trial import PageRetriever

    protocols = ("nvme", "pcie") if row["protocol"] == "both" else (row["protocol"],)
    passages = []
    picker = (field_passages if field else concise_passages if concise else acceptance_passages if acceptance else
              verification_passages if verified else None)
    with PageRetriever(ROOT) as index, audit.open("a", encoding="utf-8") as log:
        for protocol in protocols:
            checks = picker(index, protocol, row["question"]) if picker else []
            if checks:
                ranges = [[entry["pdf_page"], *entry["lines"]] for entry in checks]
                pages = list(dict.fromkeys(page for page, _, _ in ranges))
                for entry in checks:
                    passages.append(f"{protocol.upper()} PDF p.{entry['pdf_page']}\n{entry['passage']}")
                log.write(json.dumps({"tool": "prefetch_spec", "protocol": protocol, "pages": pages,
                                      "matching_ranges": ranges, "status": "ok"}) + "\n")
                continue
            hits = index.search(protocol, row["question"], mode, k=2)
            pages = [hit["pdf_page"] for hit in hits]
            evidence_call = {"tool": "prefetch_spec", "protocol": protocol, "pages": pages, "status": "ok"}
            for page in pages:
                if view in ("bounded", "outcomes", "decision"):
                    get_passage = index.scoped_passage if view == "bounded" else index.outcome_passage
                    excerpt = get_passage(protocol, page, row["question"])
                    evidence_call.setdefault("passage_lines", []).append(excerpt["lines"])
                    passage = json.dumps(excerpt, ensure_ascii=False)
                else:
                    passage = index.preview(protocol, page, row["question"])
                passages.append(f"{protocol.upper()} PDF p.{page}\n{passage}")
            log.write(json.dumps(evidence_call, ensure_ascii=False) + "\n")
    return "\n\n".join(passages), len(protocols)


def run_one(args, row):
    key = row["id"] + "-" + str(row.get("form", 0))
    if not re.fullmatch(r"[\w.-]+", key) or row["protocol"] not in ("pcie", "nvme", "both"):
        raise ValueError(f"Unexpected question identifier or protocol: {key}")
    outdir = args.output.resolve() / key
    outdir.mkdir(parents=True, exist_ok=False)
    audit = outdir / "calls.jsonl"
    audit.touch()
    env = dict(os.environ, PI_MCP_CONFIG_MODE="exclusive", PYTHONUTF8="1")
    started = time.monotonic()
    view = getattr(args, "evidence_view", "classic")
    field = args.answer_style == "field-acceptance"
    concise = args.answer_style == "concise-acceptance" or field
    acceptance = args.answer_style == "acceptance" or concise
    verified = args.answer_style == "verified-conditions" or acceptance
    fast = args.answer_style == "fast-conditions" or verified
    conditions = args.answer_style == "conditions" or fast
    handoff = args.answer_style in {"timeline", "conditions"}
    server = ("evidence_verification_mcp.py" if verified else "evidence_fast_conditions_mcp.py" if fast else
              "evidence_conditions_mcp.py" if conditions else
              "evidence_timeline_mcp.py" if handoff else "evidence_mcp.py")
    skill = getattr(args, "skill", None)
    skill_name = skill.resolve().parent.name if skill else None
    skill_body = skill.read_text(encoding="utf-8-sig").split("\n---\n", 1)[-1].strip() if skill else ""
    stage_start = time.monotonic()
    excerpts, automatic_calls = (prefetch_pages(row, args.mode, audit, view, verified=verified,
                                               acceptance=acceptance, concise=concise, field=field)
                                 if getattr(args, "prefetch", False) else ("", 0))
    prefetch_seconds = time.monotonic() - stage_start
    with tempfile.TemporaryDirectory(prefix="spec-pi-") as session:
        config = Path(session) / "mcp.json"
        config.write_text(json.dumps({
            "settings": {"scriptMode": False},
            "mcpServers": {"spec": {
                "command": sys.executable, "args": [str(HERE / server)],
                "lifecycle": "eager", "directTools": True,
                "env": {"SPEC_EVAL_MODE": args.mode, "SPEC_EVAL_CALL_LIMIT": str(args.calls - automatic_calls),
                        "SPEC_EVAL_ROOT": str(ROOT), "SPEC_EVAL_AUDIT": str(audit), "SPEC_EVAL_PROTOCOL": row["protocol"], "SPEC_EVAL_EVIDENCE_VIEW": view,
                        "PYTHONUTF8": "1"}}}}), encoding="utf-8")
        prompt = (f"请用 spec 的 search_spec 和 read_spec_page 核查。版本为 {row['spec']}。"
                  f"服务端预算为 {args.calls} 次检索或读页，每次检索最多 5 条。"
                  "优先检索问题中的关键概念，原文足够就作答。回答问题所问的事实和条件，"
                  "标明实际用到的 PDF 文件页；证据有缺口则说明缺什么。\n" + row["question"])
        if row["protocol"] == "both" or args.without_mcp:
            prompt = (f"请直接答复提出问题的工程同事。适用规范为 {row['spec']}。"
                      "优先给出对当前记录的判断、理由和最有区分力的下一步，交代什么仍待确认。"
                      "若引用资料请标明可核对的位置。尽量控制在 400 个汉字内。\n" + row["question"])
        if args.answer_style == "handoff":
            prompt = ("以现场交接单形式作答。第一句给决定，然后给最少的机制解释和一次能验证决定的检查。"
                      "逐项核对建议所依据的条款是否适用于题面给出的设备、传输和状态。"
                      "保留观测未能区分的原因，删去对本次处置没有影响的扩展结论。\n" + prompt)
        if args.answer_style == "decision-audit":
            prompt = ("先定位哪条观测能改变现场动作，再用对应协议的英文寄存器名或命令字段查原文；"
                      "搜索片段不能证明关键前提时才读整页，找到直接证据就结束检索。"
                      "答复给出当前可以作的决定、尚不能认定的原因，以及一次区分它们的检查和各结果对应的动作。"
                      "提交前默查全文：每条新增时限、复位、重试和归责是否由本传输和状态支持？"
                      "删去无法证实且不影响当前处置的说法。页码只用实际核实过的文件页。\n" + prompt)
        if args.answer_style in {"scoped", "timeline", "conditions"}:
            prompt = (f"只回答这张工单要求签字或采取的动作。规范范围为 {row['spec']}。"
                      f"取证预算 {args.calls} 次，先针对直接决定处置的英文术语查证。"
                      "最终答复最多三项：当前处置、直接依据（用核实的文件页）、必要的只读核验。"
                      "前两项已经能交接时，用两项结案。第三项只写确实缺少的一条观测及它解决的问题。"
                      + ("必要条件要完整。" if conditions else "总共不超过 220 字。")
                      + "把可选诊断、假设性结果和没有被问到的处置留给后续工单。\n" + row["question"])
        if fast:
            prompt = (f"规范 {row['spec']}\n{CONCISE_PROMPT}\n\n工单\n{row['question']}" if concise else
                      f"核对 {row['spec']} 并直接签发这份工单。"
                      "先看候选原文。缺影响处置的条款时，用 find_spec_conditions 合并定位和读原文，"
                      "再针对仍缺的条件补证。规范证据足够后自行逐项复核并签发。\n"
                      + (ACCEPTANCE_PROMPT if acceptance else CONDITION_PROMPT.replace("，草稿需要重新核对", ""))
                      + "\n\n工单\n" + row["question"])
        elif conditions:
            prompt = ("草稿交复核前，用 read_spec_conditions 核对最直接的英文字段。"
                      "列出决定动作的门槛、适用范围及会改变处置的备选路径。写全必要条件，避免添加无关操作。\n" + prompt)
        elif handoff:
            prompt = ("草稿将经过一次交接复核。引用必要的同期观测、初始状态或明确恢复门槛。"
                      "规范解释状态或转换，工单事实给出发生时间。取到决定性条款就结束取证。\n" + prompt)
        if excerpts:
            prompt += (f"\n\n以下是按完整问题自动检索的候选片段，可能包含无关内容。"
                       f"需要补证时还可调用规范工具 {args.calls - automatic_calls} 次。"
                       "已有足够依据时直接作答。\n\n" + excerpts)
        access = (["--no-tools", "--no-mcp"] if args.without_mcp else
                  ["-e", str(args.adapter.resolve()), "-nbt", "--mcp-config", str(config)])
        launcher = [shutil.which("node") or "node", str(args.pi_entry.resolve())]
        signing_model = (args.review_model or args.model) if handoff or fast else None
        initial_model = signing_model if fast else args.model
        command = [*launcher,
                   "-ne", *access, "-nc", "-ns", *(["--skill", str(skill.resolve())] if skill else []), "-np",
                   "--offline", "--no-session", "--no-approve", "--provider", args.provider,
                   "--model", initial_model, "--thinking", "off", "--mode", "json", "-p",
                   f"/skill:{skill_name} {prompt}" if skill else prompt]
        events = outdir / "events.jsonl"
        with events.open("wb") as stdout, (outdir / "stderr.log").open("wb") as stderr:
            stage_start = time.monotonic()
            with subprocess.Popen(command, cwd=session, env=env, stdout=stdout, stderr=stderr) as proc:
                try:
                    reserve = min(40, args.timeout / 3) if handoff else 0
                    rc = proc.wait(timeout=max(0, args.timeout - reserve - (time.monotonic() - started)))
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                    rc = "timeout"
            draft_seconds = time.monotonic() - stage_start
    answer = ""
    last_reason = None
    model = None
    skill_expanded = False
    event_lines = events.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in event_lines:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        m = e.get("message", {})
        if skill and m.get("role") == "user" and e.get("type") == "message_end":
            content = m.get("content", "")
            body = content if isinstance(content, str) else "".join(c.get("text", "") for c in content)
            skill_expanded |= (f'<skill name="{skill_name}"' in body and skill_body in body.replace("\r\n", "\n"))
        if e.get("type") == "message_end" and m.get("role") == "assistant":
            model = m.get("model") or model
            last_reason = m.get("stopReason")
            if last_reason == "stop":
                answer = "".join(c.get("text", "") for c in m.get("content", []) if c.get("type") == "text")
    handoff_status = None
    review_seconds = 0.0
    if fast:
        formatter = format_acceptance if acceptance else format_conditions
        answer = formatter(answer) if rc == 0 else ""
        handoff_status = "ok" if answer else "invalid" if rc == 0 else "timeout" if rc == "timeout" else "error"
        if not answer:
            rc = handoff_status
    if handoff:
        handoff_status = "no_draft"
        if answer and rc == 0:
            (outdir / "draft.txt").write_text(answer, encoding="utf-8")
            context = condition_excerpts(events, excerpts) if conditions else original_excerpts(events, excerpts)
            options = {"prompt": CONDITION_PROMPT, "formatter": format_conditions} if conditions else {}
            with tempfile.TemporaryDirectory(prefix="spec-pi-handoff-") as session:
                stage_start = time.monotonic()
                answer, handoff_status = sign_handoff(launcher, args, env, session, outdir, row, answer, context,
                                                      args.timeout - (time.monotonic() - started), **options)
                review_seconds = time.monotonic() - stage_start
            if handoff_status != "ok":
                rc = handoff_status
        else:
            answer = ""
    elapsed = time.monotonic() - started
    seconds = round(elapsed, 2)
    calls = [json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines()]
    stderr_text = (outdir / "stderr.log").read_text(encoding="utf-8", errors="replace")
    result = {"id": row["id"], "form": row.get("form", 0), "protocol": row["protocol"], "spec": row["spec"],
              "question": row["question"], "mode": args.mode, "provider": args.provider, "model": model or initial_model,
              "arm": "without_mcp" if args.without_mcp else "with_mcp",
              "answer_style": args.answer_style,
              "evidence_view": view, "skill_name": skill_name, "skill_expanded": skill_expanded,
              "skill_sha256": hashlib.sha256(skill.read_bytes()).hexdigest() if skill else None,
              "prefetch_calls": automatic_calls,
              "mcp_initialization_failed": not args.without_mcp and "MCP initialization failed" in stderr_text,
              "call_limit": 0 if args.without_mcp else args.calls, "timeout": args.timeout, "exit": rc, "seconds": seconds,
              "phaseSeconds": phases(elapsed, draft_seconds, review_seconds, prefetch_seconds,
                                     tool_wait_seconds(event_lines), direct_signoff=fast),
              "attempts": len(calls), "successful_evidence_calls": sum(c["status"] == "ok" for c in calls),
              "completion_reason": last_reason, "handoff_status": handoff_status,
              "review_model": signing_model, "answer": answer}
    (outdir / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(key, rc, seconds, len(calls), "answered" if answer else "no final answer", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Blind JSONL with id, spec, protocol and question")
    parser.add_argument("--id", action="append", help="Run only these IDs")
    parser.add_argument("--output", required=True, type=Path, help="New output directory per run")
    parser.add_argument("--pi-entry", required=True, type=Path, help="Installed Pi Node CLI entrypoint")
    parser.add_argument("--adapter", type=Path, help="Installed pi-mcp-adapter index.ts for runs with MCP")
    parser.add_argument("--without-mcp", action="store_true", help="Run a paired baseline with all tools disabled")
    parser.add_argument("--prefetch", action="store_true", help="Spend one evidence call per allowed protocol on initial passages")
    parser.add_argument("--evidence-view", choices=("classic", "bounded", "outcomes", "decision"), default="classic")
    parser.add_argument("--skill", type=Path, help="Explicit Pi skill file, invoked with its native slash command")
    parser.add_argument("--answer-style", choices=("standard", "handoff", "decision-audit", "scoped", "timeline", "conditions", "fast-conditions", "verified-conditions", "acceptance", "concise-acceptance", "field-acceptance"), default="standard")
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--review-model", help="Optional model for the final timeline handoff review on the same provider")
    parser.add_argument("--mode", default="domain")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--calls", type=int, default=6)
    args = parser.parse_args()
    if (args.calls < 1 or args.timeout < 1 or not args.pi_entry.is_file()
            or (not args.without_mcp and (not args.adapter or not args.adapter.is_file()))):
        parser.error("Provide installed Pi and adapter files, and positive time and call budgets")
    if args.prefetch and (args.without_mcp or args.calls < 3):
        parser.error("Prefetch requires MCP and at least three total evidence calls")
    reviewed = args.answer_style in {"timeline", "conditions", "fast-conditions", "verified-conditions", "acceptance", "concise-acceptance", "field-acceptance"}
    if reviewed and (args.without_mcp or args.evidence_view != "decision"):
        parser.error("Reviewed handoffs require the decision evidence view")
    if args.review_model and not reviewed:
        parser.error("A separate review model requires a reviewed handoff")
    if args.skill and (args.skill.name != "SKILL.md" or not args.skill.is_file()):
        parser.error("Provide a readable SKILL.md inside its named skill directory")
    selected = []
    for line in args.input.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            row = json.loads(line)
            if not args.id or row["id"] in args.id:
                selected.append(row)
    if not selected or set(args.id or []) - {r["id"] for r in selected}:
        parser.error("No matching inputs for one or more requested IDs")
    for r in selected:
        run_one(args, r)


if __name__ == "__main__":
    main()
