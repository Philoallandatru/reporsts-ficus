"""Validate, blind and score SSD field scenarios using explicit engineering judgments."""
import argparse
from collections import Counter
from contextlib import ExitStack
import json
from pathlib import Path

from benchmark import HERE, ROOT, LABELS, NVME, PCIE, PAGE_COUNTS, norm

PILOT_BANKS = {"startup", "shutdown"}
DECISION_STATES = {"decidable", "conditional", "need_observation"}
CAUSE_STATES = {"established", "undetermined", "not_applicable"}

def load_lines(path):
    records = []
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if line.strip():
            try:
                records.append(json.loads(line))
            except ValueError as e:
                raise ValueError(f"{path}:{number}: {e}") from e
    return records


def keyed(records, label):
    result = {}
    for item in records:
        key = item["id"]
        if not isinstance(key, str) or not key.strip() or key in result:
            raise ValueError(f"{label}: duplicate or invalid ID {key!r}")
        result[key] = item
    return result


def select(args):
    cases = []
    directory = HERE / "scenarios"
    paths = [directory / f"{name}.jsonl" for name in ("startup", "shutdown")] if args.suite != "extended" else []
    if args.suite != "pilot":
        paths.extend(p for p in sorted(directory.glob("*.jsonl")) if p.stem not in PILOT_BANKS)
    for path in paths:
        bank = load_lines(path)
        if path.stem not in PILOT_BANKS:
            for case in bank:
                validate_design(case)
        cases.extend(bank)
    all_cases = keyed(cases, "scenario bank")
    family_splits = {}
    inputs = set()
    for case in cases:
        family = case["family"]
        if family_splits.setdefault(family, case["split"]) != case["split"]:
            raise ValueError(f"Family {family!r} crosses dev/challenge")
        initial = (norm(case["question"]), tuple(norm(o) for o in case["observations"]))
        if initial in inputs:
            raise ValueError(f"{case['id']}: duplicate question and initial observations")
        inputs.add(initial)
    rows = [c for c in all_cases.values() if (not args.split or args.split == c["split"])
            and (not args.id or c["id"] in args.id)]
    missing = set(args.id or []) - {c["id"] for c in rows}
    if not rows or missing:
        raise ValueError(f"No matching cases or requested IDs outside this selection: {sorted(missing)}")
    return rows


def validate_design(case):
    rid = case["id"]
    def require(ok, message):
        if not ok:
            raise ValueError(f"{rid}: {message}")
    require(case.get("origin") in ("synthetic", "reconstructed", "field"), "missing or unknown origin")
    if case["origin"] != "synthetic":
        require(isinstance(case.get("source_ref"), str) and case["source_ref"].strip(), "supply a deidentified source_ref")
    require(isinstance(case.get("decision"), str) and case["decision"].strip(), "missing decision")
    require(case.get("decision_sufficiency") in DECISION_STATES, "invalid decision_sufficiency")
    require(case.get("root_cause_sufficiency") in CAUSE_STATES, "invalid root_cause_sufficiency")
    criteria = case["criteria"]
    require(all(type(c.get("weight")) is int and c["weight"] > 0 for c in criteria)
            and sum(c["weight"] for c in criteria) in (10, 100), "weights must be positive and total 10 or 100")
    for item in case["evidence"]:
        require(isinstance(item.get("anchor"), str) and 3 <= len(item["anchor"].split()) <= 9,
                "supply a short source anchor of 3 to 9 words")
    followup = case.get("followup")
    if followup is not None:
        require(isinstance(followup, dict) and isinstance(followup.get("ask_for"), str) and followup["ask_for"].strip(), "missing follow-up measurement")
        branches = followup.get("branches")
        require(isinstance(branches, list) and len(branches) >= 2, "supply at least two possible outcomes")
        for branch in branches:
            require(isinstance(branch, dict) and all(isinstance(branch.get(k), str) and branch[k].strip()
                    for k in ("observation", "expected_decision")), "incomplete follow-up branch")
        for k in ("observation", "expected_decision"):
            require(len({b[k].strip() for b in branches}) == len(branches), "duplicate branch " + k)


def validate(rows, nvme_pdf):
    import pymupdf
    def nonempty(value):
        return isinstance(value, str) and bool(value.strip())

    counters = Counter()
    with ExitStack() as stack:
        documents = {"pcie": stack.enter_context(pymupdf.open(ROOT / PCIE))}
        if nvme_pdf:
            documents["nvme"] = stack.enter_context(pymupdf.open(nvme_pdf))
        covers = {"pcie": "revision 5 0 version 1 0", "nvme": "revision 2 1"}
        for protocol, pdf in documents.items():
            if len(pdf) != PAGE_COUNTS[protocol] or covers[protocol] not in norm(pdf[0].get_text()):
                raise ValueError(f"Unexpected {protocol} PDF edition")
        for case in rows:
            rid = case["id"]
            def need(condition, message):
                if not condition:
                    raise ValueError(f"{rid}: {message}")
            need(case["split"] in ("dev", "challenge"), "invalid split")
            need(all(nonempty(case[k]) for k in ("family", "question", "reference_answer")), "missing text")
            for field in ("observations", "reject"):
                need(isinstance(case[field], list) and case[field] and all(map(nonempty, case[field])), f"invalid {field}")
            evidence = keyed(case["evidence"], rid + " evidence")
            criteria = keyed(case["criteria"], rid + " criteria")
            need(criteria and evidence, "no evidence or criteria")
            for criterion in criteria.values():
                need(type(criterion["weight"]) is int and criterion["weight"] > 0, "invalid criterion weight")
                need(type(criterion["critical"]) is bool and nonempty(criterion["text"]), "invalid criterion")
                refs = criterion["evidence"]
                need(isinstance(refs, list) and all(k in evidence for k in refs), "unknown or malformed evidence links")
            need(any(c["critical"] for c in criteria.values()), "no critical engineering judgment")
            for e in evidence.values():
                p, page = e["protocol"], e["pdf_page"]
                need(p in LABELS and type(page) is int and 1 <= page <= PAGE_COUNTS[p], "invalid source page")
                need(nonempty(e["section"]) and nonempty(e["anchor"]), "missing section or anchor")
                anchor = " " + norm(e["anchor"]) + " "
                if p == "nvme":
                    text = (ROOT / NVME.format(page)).read_text(encoding="utf-8").partition(f"# Source page {page}")[2]
                    need(anchor in " " + norm(text) + " ", f"{e['id']}: anchor absent from NVMe extraction p{page}")
                if p in documents:
                    need(anchor in " " + norm(documents[p][page-1].get_text()) + " ", f"{e['id']}: anchor absent from {p} PDF p{page}")
                counters[p] += 1
    return {"scenarios": len(rows), "criteria": sum(len(c["criteria"]) for c in rows),
            "anchors": dict(counters), "verified_pdfs": sorted(documents)}


def blind(case, branch=None):
    observations = "\n".join("- " + item for item in case["observations"])
    result = {"id": case["id"], "protocol": "both", "spec": " / ".join(LABELS.values()),
              "question": f"{case['question']}\n\n现场观测\n{observations}"}
    if branch is not None:
        options = case.get("followup", {}).get("branches", [])
        if not 1 <= branch <= len(options):
            raise ValueError(f"{case['id']}: unknown follow-up branch {branch}")
        result["form"] = branch
        result["question"] += "\n\n补充观测\n" + options[branch - 1]["observation"] + "\n现在如何更新决定？"
    return result


def question_book(rows):
    lines = ["# SSD 工程场景盲题册", "", f"共 {len(rows)} 道题。请根据每道题首次提问时已有的观测回答。",
             "本册由评分工具从题库导出，仅包含首问和首轮观测。", ""]
    for case in rows:
        lines.extend([f"## {case['id']}", "", case["question"], ""])
        lines.extend("- " + item for item in case["observations"])
        lines.append("")
    return "\n".join(lines).rstrip()


def score_case(case, review):
    case_id = case["id"]
    if review is None:
        return {"id": case_id, "status": "pending", "score": None}
    credits, hits = review["criteria"], review["reject_hits"]
    criteria = keyed(case["criteria"], case_id + " criteria")
    completed = review["completed"]
    if type(completed) is not bool or not isinstance(review["reason"], str) or not review["reason"].strip():
        raise ValueError(f"{case_id}: supply a boolean completed and a review reason")
    if not isinstance(hits, list) or any(type(i) is not int or not 1 <= i <= len(case["reject"]) for i in hits):
        raise ValueError(f"{case_id}: reject_hits must contain 1-based reject indices")
    if not isinstance(credits, dict) or credits.keys() - criteria.keys() or (completed and credits.keys() != criteria.keys()):
        raise ValueError(f"{case_id}: invalid or missing criterion IDs")
    if any(type(v) not in (int, float) or v not in (0, .5, 1) for v in credits.values()):
        raise ValueError(f"{case_id}: allowed credits are 0, 0.5, 1")
    critical_misses = [k for k, c in criteria.items() if c["critical"] and credits.get(k, 0) != 1]
    total = sum(c["weight"] for c in criteria.values())
    earned = sum(c["weight"] * credits.get(k, 0) for k, c in criteria.items()) if completed else 0
    passed = completed and not critical_misses and not hits and 100 * earned >= 80 * total
    return {"id": case_id, "status": "incomplete" if not completed else ("pass" if passed else "fail"),
            "score": round(100 * earned / total, 2), "earned_weight": earned, "total_weight": total,
            "critical_misses": critical_misses, "reject_hits": hits, "criteria": credits, "reason": review["reason"]}


def score(cases, reviews):
    reviews_by_id = keyed(reviews, "reviews")
    unknown = reviews_by_id.keys() - {r["id"] for r in cases}
    if unknown:
        raise ValueError(f"Reviews outside the selected run: {sorted(unknown)}")
    results = [score_case(case, reviews_by_id.get(case["id"])) for case in cases]
    counts = Counter(r["status"] for r in results)
    finished = [r for r in results if r["status"] in ("pass", "fail")]
    mean_completed = round(sum(r["score"] for r in finished) / len(finished), 2) if finished else None
    suitability = Counter()
    for result in results:
        row = reviews_by_id.get(result["id"], {})
        label = row.get("usability")
        if result["status"] == "incomplete":
            if label not in (None, "no_answer"):
                raise ValueError(f"{result['id']}: incomplete run cannot be ready for use")
            label = "no_answer"
        elif label is not None and label not in ("ready", "revise", "misleading"):
            raise ValueError(f"{result['id']}: invalid usability label")
        suitability[label or "unreviewed"] += 1
        result["usability"] = label
        result["other_error"] = row.get("other_error", "")
    return {"planned": len(cases),
            "field_usability": {label: suitability[label] for label in ("ready", "revise", "misleading", "no_answer", "unreviewed")},
            "ready_fraction_of_planned": f"{suitability['ready']}/{len(cases)}" if not suitability["unreviewed"] else None,
            "ready_fraction_of_completed": f"{suitability['ready']}/{len(finished)}" if finished and not suitability["unreviewed"] else None,
            "passed": counts["pass"], "failed": counts["fail"],
            "incomplete": counts["incomplete"], "pending": counts["pending"],
            "completed_answers": len(finished), "mean_score_of_completed_answers": mean_completed,
            "passed_fraction_of_completed": f"{counts['pass']}/{len(finished)}" if finished else None,
            "passed_fraction_of_planned": f"{counts['pass']}/{len(cases)}",
            "final": counts["pending"] == 0, "cases": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("validate", "blind", "book", "score"):
        cmd = sub.add_parser(action)
        cmd.add_argument("--suite", choices=("pilot", "extended", "all"), default="pilot",
                         help="Original eight, new scenario banks, or both (default: pilot)")
        cmd.add_argument("--id", action="append")
        cmd.add_argument("--split", choices=("dev", "challenge"))
        cmd.add_argument("--output", type=Path)
        if action == "validate":
            cached = ROOT / ".kb_index/spec_eval/nvme-official-full.pdf"
            cmd.add_argument("--nvme-pdf", type=Path, default=cached if cached.is_file() else None)
        if action in ("blind", "score"):
            cmd.add_argument("--branch", type=int, help="With one --id, reveal this 1-based follow-up observation")
        if action == "score":
            cmd.add_argument("--reviews", required=True, type=Path)
    args = parser.parse_args()
    rows = select(args)
    branch = getattr(args, "branch", None)
    if branch is not None and len(rows) != 1:
        parser.error("--branch requires a single selected case")
    if args.action == "blind":
        output = "\n".join(json.dumps(blind(row, args.branch), ensure_ascii=False) for row in rows)
    elif args.action == "book":
        output = question_book(rows)
    else:
        if args.action == "validate":
            result = validate(rows, args.nvme_pdf)
        else:
            reviews = load_lines(args.reviews)
            if branch is not None:
                case = rows[0]
                choices = case.get("followup", {}).get("branches", [])
                if not 1 <= branch <= len(choices):
                    parser.error(f"{case['id']}: unknown follow-up branch {branch}")
                if any(review.get("branch") != branch for review in reviews):
                    parser.error("each follow-up review must specify the selected branch")
                criterion = {"id": "update", "weight": 1, "critical": True,
                             "text": choices[branch - 1]["expected_decision"]}
                rows = [dict(case, criteria=[criterion])]
            elif any(review.get("branch") is not None for review in reviews):
                parser.error("use --branch to score follow-up reviews separately")
            result = score(rows, reviews)
            if branch is not None:
                result["branch"] = branch
                result["expected_decision"] = rows[0]["criteria"][0]["text"]
        output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
