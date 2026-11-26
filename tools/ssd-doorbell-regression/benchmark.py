"""Validate the two specification banks and compare retrieval on original user wordings."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import ExitStack
import hashlib
import json
import math
import os
from pathlib import Path
import re
import statistics
import time
import unicodedata

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("SPEC_EVAL_ROOT", HERE / ".local/corpus")).resolve()
PROTOCOLS = ("pcie", "nvme")
MODES = ("bm25", "expanded", "domain", "fusion", "refined")
PCIE = "kb/pcie/PCI Express Base Specification.pdf"
NVME = "kb/nvme/_source/pages/page-{:03}.md"
PAGE_COUNTS = {"pcie": 1299, "nvme": 707}
LABELS = {"pcie": "PCI Express Base Specification Revision 5.0 Version 1.0",
          "nvme": "NVM Express Base Specification, Revision 2.1 (2024-08-05)"}


def load_bank():
    rows = []
    for protocol in PROTOCOLS:
        path = HERE / "bank" / f"{protocol}.jsonl"
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if line.strip():
                item = json.loads(line)
                if item["protocol"] != protocol:
                    raise ValueError(f"Wrong protocol in {path.name}: {item['id']}")
                rows.append(item)
    return rows


def fingerprint(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def norm(text):
    return " ".join(re.findall(r"[^\W_]+", unicodedata.normalize("NFKC", text).casefold()))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate(rows, nvme_pdf):
    import pymupdf
    seen_ids, seen_wordings, families = set(), set(), {}
    pages = defaultdict(set)
    counts = Counter()
    specs = defaultdict(set)
    problems = []
    with ExitStack() as stack:
        pci = stack.enter_context(pymupdf.open(ROOT / PCIE))
        nvm = stack.enter_context(pymupdf.open(nvme_pdf)) if nvme_pdf else None
        if len(pci) != PAGE_COUNTS["pcie"] or (nvm is not None and len(nvm) != PAGE_COUNTS["nvme"]):
            raise ValueError("PDF page count differs from the registered edition")
        if "revision 5 0 version 1 0" not in norm(pci[0].get_text()):
            raise ValueError("PCIe cover version differs from the registered edition")
        if nvm is not None and "revision 2 1" not in norm(nvm[0].get_text()):
            raise ValueError("NVMe cover version differs from the registered edition")
        for r in rows:
            rid, p, split = r["id"], r["protocol"], r["split"]
            evidence = r["evidence"]
            def check(ok, message):
                if not ok:
                    problems.append(f"{rid}: {message}")
            check(rid not in seen_ids, "duplicate ID")
            seen_ids.add(rid)
            check(split in ("dev", "test"), "invalid split")
            check(r["kind"] in ("abstain", "lookup", "boundary", "conditional", "synthesis"), "invalid kind")
            check(bool(r["family"].strip() and r["spec"].strip() and r["answer"].strip()), "empty family/spec/answer")
            specs[p].add(r["spec"])
            check(r["spec"] == LABELS[p], "wrong edition label")
            check(bool(r["claims"]) and all(isinstance(c, str) and c.strip() for c in r["claims"]), "missing claims")
            check(r["kind"] == "abstain" or evidence, "answerable without evidence")
            check(len(r["variants"]) >= 1, "missing variant")
            key = (p, r["family"])
            check(families.setdefault(key, split) == split, "family appears in both splits")
            for q in [r["question"], *r["variants"]]:
                wording = (p, norm(q))
                check(bool(wording[1]) and wording not in seen_wordings, "duplicate or empty wording")
                seen_wordings.add(wording)
            counts[p, split, r["kind"]] += 1
            for e in evidence:
                page = e["pdf_page"]
                if type(page) is not int or not 1 <= page <= PAGE_COUNTS[p]:
                    problems.append(f"{rid}: invalid PDF page {page}")
                    continue
                check(e["path"] == (PCIE if p == "pcie" else NVME.format(page)), "source path/edition mismatch")
                check(bool(e["section"].strip()), "missing section")
                anchor = norm(e["anchor"])
                check(bool(anchor), "empty anchor")

                def contains(text):
                    return f" {anchor} " in f" {norm(text)} "
                if p == "pcie":
                    check(contains(pci[page - 1].get_text()), f"anchor absent from PCIe PDF p{page}: {e['anchor']}")
                else:
                    md = (ROOT / NVME.format(page)).read_text(encoding="utf-8")
                    check(contains(md.partition(f"# Source page {page}")[2]), f"anchor absent from NVMe extract p{page}: {e['anchor']}")
                    if nvm is not None:
                        check(contains(nvm[page - 1].get_text()), f"anchor absent from official NVMe PDF p{page}: {e['anchor']}")
                pages[p, split].add(page)
    for p in PROTOCOLS:
        if len(specs[p]) != 1:
            problems.append(f"{p}: mixed edition labels {specs[p]}")
        if pages[p, "dev"] & pages[p, "test"]:
            problems.append(f"{p}: dev/test evidence pages overlap")
    if problems:
        raise ValueError("\n".join(problems))
    return {"questions": len(rows), "wordings": len(seen_wordings), "families": len(families),
            "anchors": sum(len(r["evidence"]) for r in rows),
            "original_nvme_pdf_verified": bool(nvme_pdf),
            "counts": {"/".join(k): v for k, v in sorted(counts.items())},
            "shared_pages_across_splits": {p: sorted(pages[p, "dev"] & pages[p, "test"]) for p in PROTOCOLS},
            "source_pdf_sha256": {"pcie": fingerprint(ROOT / PCIE), **({"nvme": fingerprint(nvme_pdf)} if nvme_pdf else {})}}


def trial(engine, rows, modes, k):
    observations = []
    for r in rows:
        if r["kind"] == "abstain":
            continue
        gold = {e["pdf_page"] for e in r["evidence"]}
        for i, query in enumerate([r["question"], *r["variants"]]):
            for mode in modes:
                start = time.perf_counter()
                hits = engine.search(r["protocol"], query, mode, k=k)
                elapsed = (time.perf_counter() - start) * 1000
                predicted = [h["pdf_page"] for h in hits]
                if len(predicted) > k or len(set(predicted)) != len(predicted):
                    raise ValueError(f"Invalid ranked list for {mode}: {predicted}")
                for h in hits:
                    if h["path"] != (PCIE if r["protocol"] == "pcie" else NVME.format(h["pdf_page"])):
                        raise ValueError(f"Candidate from a different edition: {h}")
                ranks = [i for i, p in enumerate(predicted, start=1) if p in gold]
                observations.append(dict(id=r["id"], protocol=r["protocol"], family=r["family"],
                    split=r["split"], kind=r["kind"], form=i, mode=mode, query=query, gold=sorted(gold),
                    pages=predicted, hit=int(bool(ranks)), first=int(1 in ranks),
                    complete=int(gold.issubset(predicted)), recall=len(ranks)/len(gold),
                    rr=1/ranks[0] if ranks else 0, ms=round(elapsed, 3)))
    return observations


def metrics(obs):
    def avg(field):
        return round(statistics.mean(o[field] for o in obs), 4)
    timings = sorted(o["ms"] for o in obs)
    forms = defaultdict(list)
    for o in obs:
        forms[o["id"]].append(o["complete"])
    return {"queries": len(obs), "questions": len(forms), "hit": sum(o["hit"] for o in obs),
            "complete": sum(o["complete"] for o in obs), "top1": sum(o["first"] for o in obs),
            "mrr": avg("rr"), "mean_page_recall": avg("recall"),
            "all_forms_complete": sum(all(v) for v in forms.values()),
            "ms_p50": round(statistics.median(timings), 2),
            "ms_p95": round(timings[math.ceil(0.95 * len(timings)) - 1], 2)}


def summarize(observations):
    groups = defaultdict(list)
    for o in observations:
        for p in ("all", o["protocol"]):
            for form in ("all", "primary" if o["form"] == 0 else "rewrite"):
                groups[o["mode"], p, form].append(o)
    return {"/".join(key): metrics(obs) for key, obs in sorted(groups.items())}


def inspect_passages(result_dir, rows, mode):
    from retrieval_trial import PageRetriever
    summary = json.loads((result_dir / "summary.json").read_text(encoding="utf-8"))
    bank_hashes = {p: fingerprint(HERE / "bank" / f"{p}.jsonl") for p in PROTOCOLS}
    if summary["bank_sha256"] != bank_hashes or summary["retriever_sha256"] != fingerprint(HERE / "retrieval_trial.py"):
        raise ValueError("Run the benchmark with this bank and retriever before checking passages")
    if mode not in summary["modes"]:
        raise ValueError(f"{mode} was not run in {result_dir}")
    by_id = {r["id"]: r for r in rows}
    totals = defaultdict(Counter)
    with PageRetriever(ROOT) as retriever:
        for line in (result_dir / "queries.jsonl").read_text(encoding="utf-8").splitlines():
            o = json.loads(line)
            if o["mode"] != mode:
                continue
            r = by_id[o["id"]]
            pages = {e["pdf_page"] for e in r["evidence"]} & set(o["pages"])
            snippets = {p: " " + norm(retriever.preview(r["protocol"], p, o["query"])) + " " for p in pages}
            matches = [f" {norm(e['anchor'])} " in snippets.get(e["pdf_page"], "") for e in r["evidence"]]
            for key in (r["protocol"], "all"):
                totals[key].update({"queries": 1, "all_pages": o["complete"], "all_anchors_in_previews": int(all(matches))})
    return dict(totals)


def regression_snapshot(result_dir, mode):
    summary = json.loads((result_dir / "summary.json").read_text(encoding="utf-8"))
    if mode not in summary["modes"]:
        raise ValueError(f"{mode} was not run in {result_dir}")
    observed = defaultdict(list)
    for line in (result_dir / "queries.jsonl").read_text(encoding="utf-8").splitlines():
        o = json.loads(line)
        if o["mode"] == mode:
            observed[o["id"]].append((o["form"], o["query"], o["gold"], o["complete"]))
    cases = {}
    for rid, forms in sorted(observed.items()):
        forms.sort()
        signature = json.dumps([f[:3] for f in forms], ensure_ascii=False)
        cases[rid] = [hashlib.sha256(signature.encode()).hexdigest()[:20], all(f[3] for f in forms)]
    return {k: summary[k] for k in ("split", "k", "bank_sha256", "retriever_sha256")} | {"mode": mode, "cases": cases}


def compare(reference, current):
    if (reference["split"], reference["k"]) != (current["split"], current["k"]):
        raise ValueError("Compare the same split and k")
    a, b = reference["cases"], current["cases"]
    common = a.keys() & b.keys()
    same = {key for key in common if a[key][0] == b[key][0]}
    return {"comparable": len(same), "gained": sorted(key for key in same if b[key][1] and not a[key][1]),
            "lost": sorted(key for key in same if a[key][1] and not b[key][1]),
            "wordings_or_gold_changed": sorted(common - same),
            "added": sorted(b.keys() - a.keys()), "removed": sorted(a.keys() - b.keys())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    check = sub.add_parser("validate")
    original_nvme = ROOT / ".kb_index/spec_eval/nvme-official-full.pdf"
    check.add_argument("--nvme-pdf", type=Path, default=original_nvme if original_nvme.is_file() else None,
                       help="Official Base 2.1 PDF for independent verification")
    export = sub.add_parser("blind")
    export.add_argument("--split", choices=("dev", "test"), default="dev")
    export.add_argument("--rewrites", action="store_true")
    snippets = sub.add_parser("passages")
    snippets.add_argument("--results", type=Path, required=True, help="Existing benchmark run directory")
    snippets.add_argument("--mode", choices=MODES, default="domain")
    snapshot = sub.add_parser("snapshot")
    snapshot.add_argument("--results", type=Path, required=True)
    snapshot.add_argument("--mode", choices=MODES, default="domain")
    snapshot.add_argument("--output", type=Path, required=True)
    diff = sub.add_parser("compare")
    diff.add_argument("--reference", type=Path, required=True)
    diff.add_argument("--results", type=Path, required=True)
    diff.add_argument("--mode", choices=MODES, default="domain")
    run = sub.add_parser("run")
    run.add_argument("--split", choices=("dev", "test"), default="dev")
    run.add_argument("--modes", nargs="+", choices=MODES, default=MODES)
    run.add_argument("--k", type=int, choices=range(1, 21), default=5)
    run.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = load_bank()
    if args.action == "validate":
        print(json.dumps(validate(rows, args.nvme_pdf), ensure_ascii=False, indent=2))
        return
    if args.action == "passages":
        print(json.dumps(inspect_passages(args.results, rows, args.mode), indent=2))
        return
    if args.action in ("snapshot", "compare"):
        current = regression_snapshot(args.results, args.mode)
        if args.action == "snapshot":
            write_json(args.output, current)
        else:
            previous = json.loads(args.reference.read_text(encoding="utf-8"))
            print(json.dumps(compare(previous, current), ensure_ascii=False, indent=2))
        return
    selected = [r for r in rows if r["split"] == args.split]
    if args.action == "blind":
        for r in selected:
            questions = [r["question"], *r["variants"]] if args.rewrites else [r["question"]]
            for i, q in enumerate(questions):
                print(json.dumps({"id": r["id"], "form": i, "protocol": r["protocol"], "spec": r["spec"],
                                  "question": q}, ensure_ascii=False))
        return
    from retrieval_trial import PageRetriever
    with PageRetriever(ROOT) as engine:
        obs = trial(engine, selected, args.modes, args.k)
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / "queries.jsonl").open("w", encoding="utf-8") as out:
        for o in obs:
            out.write(json.dumps(o, ensure_ascii=False) + "\n")
    summary = {"split": args.split, "k": args.k, "modes": args.modes,
               "bank_sha256": {p: fingerprint(HERE / "bank" / f"{p}.jsonl") for p in PROTOCOLS},
               "retriever_sha256": fingerprint(HERE / "retrieval_trial.py"),
               "evaluator_sha256": fingerprint(Path(__file__)),
               "excluded_abstain": sum(r["kind"] == "abstain" for r in selected),
               "scores": summarize(obs)}
    write_json(args.output / "summary.json", summary)
    for mode in args.modes:
        print(mode, summary["scores"][f"{mode}/all/all"])


if __name__ == "__main__":
    main()
