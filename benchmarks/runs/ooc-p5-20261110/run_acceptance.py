"""Run after tuning; failures stop the sequence with all evidence retained."""
import json
import subprocess
import sys
from run_probe import HERE, run
from compare_logits import compare, replay


def checked(name, model, mode, config, chosen, timeout=14400):
    path = HERE / "runs" / name / "summary.json"
    if path.exists():
        record = json.loads(path.read_text(encoding="utf-8"))
    else:
        record = run(name, model, mode, config, ram=chosen["ram_mib"], staging=chosen["staging_mib"], depth=chosen["depth"], timeout=timeout)
    if record.get("exit_code") != 0 or record.get("result", {}).get("phase") != "complete":
        raise RuntimeError("run failed or skipped: " + name)
    return record


selected = json.loads((HERE / "selected.json").read_text(encoding="utf-8"))
subprocess.run([sys.executable, str(HERE / "run_boundary.py")], check=True)
file = selected["file"]
native = selected["native"]
long = json.loads((HERE / "long.json").read_text(encoding="utf-8"))
capacity = dict(ram_mib=8192, gpu_mib=4096, staging_mib=32, depth=2)
long["gpu_mib"] = capacity["gpu_mib"]
record = checked("q5-long-file", "q5", "file", long, capacity, timeout=21600)
assert record["result"]["total_outputs"] >= 4096
assert record["result"]["soak_elapsed_s"] >= 1800
long_replay = replay("q5-long-file", long)
long_replay["ubatch"] = record["result"]["actual_ubatch"]
long_replay["mmap_prefetch"] = "off"
long_replay["working_set_mib"] = 49152
checked("q5-long-native-ws48", "q5", "native_np", long_replay, native, timeout=21600)
assert compare("q5-long-native-ws48", "q5-long-file")["exact"]

subprocess.run([sys.executable, str(HERE / "run_native_np_scan.py")], check=True)
native = json.loads((HERE / "selected.json").read_text(encoding="utf-8"))["native"]
formal = json.loads((HERE / "formal.json").read_text(encoding="utf-8"))
formal["mmap_prefetch"] = "off"
formal["working_set_mib"] = 49152
canonical = dict(formal, gpu_mib=native["gpu_mib"], ubatch=native["ubatch"])
checked("perf-native-r1", "q5", "native_np", canonical, native)
forced = replay("perf-native-r1", canonical)
for index, order in enumerate((("off", "file"), ("file", "off", "native"), ("off", "native", "file"),
                               ("file", "native", "off"), ("native", "file", "off"), ("off", "file", "native")), 1):
    for mode in order:
        chosen = file if mode == "file" else native
        config = dict(forced, gpu_mib=chosen["gpu_mib"], ubatch=chosen["ubatch"])
        name = f"perf-{mode}-r{index}"
        checked(name, "q5", "native_np" if mode == "native" else mode, config, chosen)
        assert compare("perf-native-r1", name)["tolerance_pass"]
    assert compare("perf-native-r1", f"perf-off-r{index}")["exact"]

same = dict(forced, gpu_mib=file["gpu_mib"], ubatch=file["ubatch"])
for index, order in enumerate((("native", "file", "sync"), ("sync", "file", "native"), ("file", "native", "sync"),
                               ("sync", "native", "file"), ("native", "sync", "file"), ("file", "sync", "native")), 1):
    for mode in order:
        chosen = dict(file, depth=1) if mode == "sync" else (file if mode == "file" else native)
        name = f"matched-{mode}-r{index}"
        checked(name, "q5", "native_np" if mode == "native" else "file", same, chosen)
        assert compare("perf-native-r1", name)["tolerance_pass"]
    assert compare(f"matched-native-r{index}", f"matched-file-r{index}")["exact"]
    assert compare(f"matched-native-r{index}", f"matched-sync-r{index}")["exact"]

checked("control-sync-no-ram", "q5", "file", same, dict(file, ram_mib=0, depth=1))
assert compare("matched-native-r1", "control-sync-no-ram")["exact"]

evaluation = json.loads((HERE / "evaluation.json").read_text(encoding="utf-8"))
evaluation["mmap_prefetch"] = "off"
evaluation["working_set_mib"] = 49152
evaluation["gpu_mib"] = file["gpu_mib"]
evaluation["ubatch"] = file["ubatch"]
checked("q5-ppl-native", "q5", "native_np", evaluation, native)
checked("q5-ppl-file", "q5", "file", evaluation, file)
assert compare("q5-ppl-native", "q5-ppl-file")["exact"]

iq2 = dict(formal, gpu_mib=4096, mmap_prefetch="on")
checked("iq2-native-r1", "iq2", "native", iq2, native)
iq2 = replay("iq2-native-r1", iq2)
for index, order in enumerate((("off", "file"), ("file", "native", "off"), ("off", "file", "native")), 1):
    for mode in order:
        name = f"iq2-{mode}-r{index}"
        checked(name, "iq2", mode, iq2, file if mode == "file" else native)
        assert compare("iq2-native-r1", name)["exact"]
print("ACCEPTANCE RUNS FINISHED", flush=True)
