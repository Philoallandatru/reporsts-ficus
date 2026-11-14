# P6 evidence map

The result is scoped to the tested single RTX 5080 GPU execution path. The predeclared Q5 decode target is a median improvement of at least 10%; the measured six-pair ratio is 1.0926485436, so that performance gate fails. Implementation, numerical correctness and capacity checks are separate outcomes.

| Evidence | Location and interpretation |
|---|---|
| Final findings | `RESULTS.zh-CN.md`; complete round tables and limitations |
| Predeclared method | `PROTOCOL.zh-CN.md`; all six pairs remain included |
| Final audit | `acceptance-audit.json`; strict float32 bit patterns, route identity, budgets, context boundary and long-run checks |
| Per-run metrics | `analysis.json`; `performance.json` aggregates six pairs and records all budget checks |
| Model size populations | `size-distribution.json`; derived from inventory and quantized block byte sizes, without changing model data |
| Stage-only source changes | `p6-vs-p5.patch`, comparing the P5 source snapshot rather than the original HEAD |
| Source and build identity | `machine-and-build.json`, `candidate-build-source.json`, `baseline-binaries.json`, `candidate-binaries.json`, `build-CMakeCache.txt` |
| Final archive checks | `final-checks.json`, produced by `verify_archive.py`; source snapshots, preserved baseline, frozen binaries, model metadata, research hashes, whitespace and Python syntax |
| Code review and local tests | `REVIEW.md`, `ctest-r2.log`; the initial fixture failure remains in `ctest.log` |
| Correctness details | `comparison-*.json`; includes each request's float count, error metrics, argmax agreement and fixed-text PPL |
| Run configuration | `runs/<name>/config.json`, `command.json`, `summary.json`, `stdout.log`, `stderr.log`, `samples.jsonl` |
| Cache telemetry | `runs/<name>/telemetry.json`; checkpoints are outside the per-token timer but inside request wall time |
| Route coverage | `runs/{q5-p6-r1,iq2-p6-r1,q5-long-p6}/routes-summary.json`; cache-lookup routes only, including small-batch prefill |
| Long-run residency | `runs/q5-long-p6/working-set.jsonl`; PSAPI snapshots complement RSS/private samples, not a total pinned-memory accounting |
| Planned steady ETW | `runs/q5-long-p6/etw-analysis.json` and `etw-*.txt`; individual DiskIO events summed by initiating PID and file; circular capture retains events only around seconds 108-182, not the full capture |
| Additional diagnostic ETW | `runs/q5-long-p6/early-analysis.json`, `early-*.txt`, `early-observation.json`; does not replace the steady trace |
| Slow-read investigation | `DIAGNOSIS.md`, `long-slow-window.json`, complete `long-slow-summary.json`, storage/PnP JSON files; root cause remains unestablished |

Large artifacts are kept under `D:/llama-ooc-p6-20261110`: frozen `file-bin`, `p6-source`, and per-run logits, MCT1 route traces, result JSON and ETL files. P5 originals remain under `D:/llama-ooc-p5-20261110` and `../ooc-p5-20261110`. Only `llama.dll` differs between the P5 and P6 inference packages.

After all inference completes, run `summarize.py`, export the early trace with `trace_early.py --export`, run `analyze_etw.py q5-long-p6 early`, `analyze_routes.py q5-long-p6`, `slow_windows.py`, then `audit.py` and `render_report.py`. `finalize_docs.py` updates the existing plan/development documentation after that audit. `archive.py` records source and complete model hashes after documentation is finalized. It intentionally refuses an existing `p6-source` directory. Do not rerun `prepare.py`, the documentation updater or any inference driver over an existing measurement set.

The P5 CPU fallback numerical failure and original IQ2 monitored short-test failure retain their original status. Historical native logits are a numerical oracle, not a fresh long-run timing baseline. Process IO, whole-disk traffic, DiskIO completion bytes and NAND traffic are distinct quantities.
