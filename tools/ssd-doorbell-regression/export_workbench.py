"""Build a portable OpenKnowledge evaluation report from planned questions, Pi runs and reviews."""
import argparse
import json
from pathlib import Path
from statistics import median

from benchmark import LABELS
from scenario_eval import blind, keyed, load_lines, score, select, validate_design


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def iteration_history(catalog_path, current_id, current):
    archives = catalog_path.resolve().parents[1] / "reports"
    history = []
    for entry in read_json(catalog_path):
        iteration = entry["id"]
        source = (current if iteration == current_id else
                  read_json(archives / f"{iteration}.json"))
        arms = {arm["id"]: arm["results"] for arm in source["rounds"]}
        summary = {}
        for key in ("baseline", "candidate"):
            results = arms[key]
            verdicts = [(r["review"] or {}).get("usability") for r in results]
            summary[key] = {"planned": len(results), "completed": sum(r["status"] == "completed" for r in results),
                            "ready": verdicts.count("ready"), "misleading": verdicts.count("misleading")}
        timings = [{r["caseId"]: r["seconds"] for r in arms[key] if r["status"] == "completed" and r["seconds"] is not None}
                   for key in ("baseline", "candidate")]
        baseline, candidate = timings
        deltas = [candidate[key] - baseline[key] for key in baseline.keys() & candidate.keys()]
        history.append({**entry, **summary, "timedPairs": len(deltas),
                        "medianDelta": round(median(deltas), 3) if deltas else None})
        if iteration == current_id:
            return history
    raise ValueError(f"Missing history entry for {current_id}")


def case_key(case_id, form):
    if type(form) is not int or form < 0:
        raise ValueError(f"{case_id}: invalid follow-up form {form!r}")
    return f"{case_id}:branch-{form}" if form else case_id


def plan_cases(directory, config, bank):
    if ("plan" in config) == ("caseIds" in config):
        raise ValueError(f"{config['id']}: supply exactly one blind plan or caseIds list")
    if "plan" in config:
        plan = load_lines(directory / config["plan"])
    else:
        plan = [blind(bank[case_id]) for case_id in config["caseIds"]]
    planned = {}
    for row in plan:
        item = bank[row["id"]]
        form = row.get("form", 0)
        key = case_key(item["id"], form)
        expected = blind(item, form or None)
        if any(row.get(field) != expected[field] for field in ("id", "spec", "question", "protocol")):
            raise ValueError(f"{key}: blind plan differs from current case, observations or specification")
        if key in planned:
            raise ValueError(f"{key}: duplicate planned case")
        planned[key] = (item, form)
    if not planned:
        raise ValueError(f"{config['id']}: no planned questions")
    return planned


def public_case(item, form):
    key = case_key(item["id"], form)
    data = {k: item[k] for k in ("family", "split", "question", "observations", "criteria", "reject")}
    data.update(id=key, referenceAnswer=item["reference_answer"])
    data["evidence"] = [
        {"id": e["id"], "source": LABELS[e["protocol"]], "page": e["pdf_page"],
         "section": e["section"], "anchor": e["anchor"]} for e in item["evidence"]]
    if form:
        branch = item["followup"]["branches"][form - 1]
        data.update(observations=[*item["observations"], branch["observation"]],
                    question=item["question"] + " 现在如何更新决定？", referenceAnswer=branch["expected_decision"],
                    blindFollowup={"caseId": item["id"], "form": form, "question": blind(item, form)["question"]},
                    criteria=[{"id": "update", "text": branch["expected_decision"],
                               "weight": 1, "critical": True, "evidence": []}])
    return data


def indexed_records(records, form_field, planned):
    indexed = {}
    for row in records:
        key = case_key(row["id"], row.get(form_field, 0))
        if key not in planned or key in indexed:
            raise ValueError(f"{key}: duplicate or unplanned record")
        indexed[key] = row
    return indexed


def read_pages(events):
    pages = {}
    for entry in events:
        if entry.get("status") != "ok":
            continue
        if entry["tool"] == "read_spec_page":
            pages[entry["protocol"], entry["pdf_page"]] = None
        if entry["tool"] in {"read_spec_context", "read_spec_transition", "read_spec_conditions"}:
            for page, _, _ in entry["matching_ranges"]:
                pages[entry["protocol"], page] = None
        if entry["tool"] == "prefetch_spec":
            for page, _, _ in entry.get("matching_ranges", ()):
                pages[entry["protocol"], page] = None
        if entry["tool"] == "find_spec_conditions":
            for page in entry["pages"]:
                pages[entry["protocol"], page] = None
    return [{"source": LABELS[source], "page": page} for source, page in pages]


def read_run(path):
    run = read_json(path)
    audit = path.with_name("calls.jsonl")
    if audit.is_file():
        run["readPages"] = read_pages(load_lines(audit))
    return run


def result_for(item, form, run, assessment):
    key = case_key(item["id"], form)
    expected = blind(item, form or None)
    archived_prompt = assessment if assessment is not None and "question" in assessment else None
    for record in (run, archived_prompt):
        if record is not None and any(record.get(k) != expected[k] for k in ("question", "spec", "protocol")):
            raise ValueError(f"{key}: executed prompt differs from the plan")
    if run is not None:
        if assessment is not None and "answer" in assessment and assessment["answer"] != run["answer"]:
            raise ValueError(f"{key}: review contains a different answer")
    record = run if run is not None else assessment
    answer = None
    seconds = None
    calls = None
    status = "pending"
    if record is not None:
        if not isinstance(record.get("answer"), str):
            raise ValueError(f"{key}: supply Pi output or an archived review containing its answer")
        answer = record["answer"] if record["answer"].strip() else None
        seconds, calls = record.get("seconds"), record.get("attempts")
        status = "completed" if answer is not None else "incomplete"
    grade = None
    if assessment is not None:
        if assessment["completed"] != (status == "completed"):
            raise ValueError(f"{key}: completion differs between run and review")
        scored_case = {"id": key, "criteria": public_case(item, form)["criteria"], "reject": item["reject"]}
        scored = score([scored_case], [dict(assessment, id=key)])["cases"][0]
        grade = {"usability": scored["usability"], "reason": scored["reason"],
                 "otherError": scored["other_error"], "credits": scored["criteria"],
                 "rejectHits": scored["reject_hits"], "score": scored["score"],
                 "passed": scored["status"] == "pass"}
    result = {"caseId": key, "status": status, "answer": answer, "seconds": seconds, "toolCalls": calls, "review": grade}
    if record is not None and "phaseSeconds" in record:
        result["phaseSeconds"] = record["phaseSeconds"]
    if run is not None and "readPages" in run:
        result["readPages"] = run["readPages"]
    elif assessment is not None and "calls" in assessment:
        result["readPages"] = read_pages(assessment["calls"])
    if assessment is not None and "totalTokens" in assessment.get("observed_usage", {}):
        result["tokens"] = assessment["observed_usage"]["totalTokens"]
    return result


def build(manifest_path):
    manifest = read_json(manifest_path)
    directory = manifest_path.parent
    rounds = keyed(manifest["rounds"], "manifest rounds")
    if not rounds:
        raise ValueError("At least one round is required")
    if "caseBank" in manifest:
        bank = keyed(load_lines(directory / manifest["caseBank"]), "cases")
        for item in bank.values():
            validate_design(item)
    else:
        bank = keyed(select(argparse.Namespace(suite="all", split=None, id=None)), "cases")
    cases = {}
    output = []
    contexts = set()
    for name, config in rounds.items():
        planned = plan_cases(directory, config, bank)
        reviews = indexed_records(load_lines(directory / config["reviews"]), "branch", planned) if "reviews" in config else {}
        runs = {}
        if "runs" in config:
            folder = directory / config["runs"]
            if not folder.is_dir():
                raise ValueError(f"{name}: run directory does not exist")
            runs = indexed_records((read_run(p) for p in sorted(folder.glob("*/result.json"))), "form", planned)
        results = []
        for key, (item, form) in planned.items():
            cases.setdefault(key, public_case(item, form))
            blind_row = blind(item, form or None)
            contexts.add((blind_row["spec"], blind_row["protocol"]))
            results.append(result_for(item, form, runs.get(key), reviews.get(key)))
        output.append({"id": name, "label": config["label"], "config": config["config"], "results": results})
    report = {"schemaVersion": 1, "title": manifest["title"], "cases": list(cases.values()), "rounds": output}
    for name, label in (("conditionMetric", "condition"), ("acceptanceMetric", "acceptance")):
        if name in manifest:
            metric = manifest[name]
            if any(metric["criterionId"] not in {c["id"] for c in item["criteria"]} for item in cases.values()):
                raise ValueError(f"Missing {label} metric criterion")
            report[name] = metric
    if "latencyMetric" in manifest:
        report["latencyMetric"] = manifest["latencyMetric"]
    if "pairedLatencyLimit" in manifest:
        report["pairedLatencyLimit"] = manifest["pairedLatencyLimit"]
    if "history" in manifest:
        report["iterationHistory"] = iteration_history(directory / manifest["history"], manifest["iteration"], report)
    if len(contexts) == 1:
        spec, protocol = next(iter(contexts))
        report["blindContext"] = {"spec": spec, "protocol": protocol, "observationHeading": "现场观测"}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="JSON manifest; input paths are relative to this file")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.dumps(build(args.manifest), ensure_ascii=False, allow_nan=False, indent=2) + "\n"
    if len(data.encode("utf-8")) > 8 * 1024 * 1024:
        parser.error("Report exceeds the workbench's 8 MiB limit; split it into smaller cohorts")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data.encode("utf-8"))
    print(args.output)


if __name__ == "__main__":
    main()
