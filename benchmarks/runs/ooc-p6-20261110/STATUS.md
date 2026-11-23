# P6 final state - 2026-11-10

Implementation, all inference, final numerical/budget audit and full archival are complete. **The predeclared Q5 +10% decode performance gate failed**: six alternating pairs measured 2.241763 to 2.449459 token/s (+9.264854%). No rounds were discarded or added to change that result. IQ2's +1.07% interval crosses no change.

All 31 model runs completed normally. Related CTest passed 2/2. The fresh strict bit-pattern audit passed all 18 comparisons, including 1,907,097,600 native-reference long-run logits. Paired and long GPU route traces are identical; all recorded RAM/PLE/staging/GPU expert/graph budgets pass. The full long trajectory completed 7680 outputs over 130.72 minutes, including 70.18 minutes after the first 4096 outputs. Its private memory remained stable; read-wait slowdowns are retained, with no established root cause. Historical P5 long inference was 74.71 minutes, so the short-run gain must not be presented as a demonstrated long-run gain.

Steady ETW proves continued expert reads in retained records but has a coverage limitation: the 1 GiB circular capture retains DiskIO timestamps around seconds 108-182 of a 182-second capture. Zero lost-event counters do not exclude ring overwrite or prove absence of paging in unretained intervals. The separate early trace is preserved. See RESULTS.zh-CN.md, DIAGNOSIS.md and acceptance-audit.json for scope.

Full model hashes match P5. Source snapshots and the three-file stage diff are under the documented artifact directories; only llama.dll differs between the frozen inference packages. P5 originals and prior source changes are preserved. The plan and development document are updated. No commit or push was performed.

No inference, observer or ETW capture from this work is active. The driver and archive logs end in their completion markers. `prepare.py`, inference drivers, `finalize_docs.py` and `archive.py` have already run; do not rerun them over these names or snapshots. `verify_archive.py` checks the final small artifacts, manifest and model metadata without repeating full model reads; its result is in final-checks.json. Further optimization should use a new experiment and preserve the failed target and I/O evidence here.

## Historical work log - superseded

The instructions and process/session IDs below describe earlier work and are inactive. They are retained as history, not as pending tasks.

### Original active-work notes

Implementation is complete and frozen for measurement. Production source changes are limited to `llama.cpp/src/llama-expert-store.cpp`; tests and documentation are also updated. Related CTest passed 2/2 in `ctest-r2.log`. Initial fixture failure is retained in `ctest.log`.

Independent artifacts: `D:/llama-ooc-p6-20261110`. P5 snapshots and original binaries remain untouched. `prepare.py` already ran; do not rerun it during inference. P6 uses unchanged P5 probe executables and ggml DLLs; only llama.dll differs. No model hash I/O until all inference finishes.

Active sequence:

1. `run_paired.py` writes `paired-driver.log`: six AB/BA pairs for Q5, then six for IQ2. Each run is new, with no summary reuse. It exits with `PAIRED RUNS COMPLETE`.
2. Already-started `run_validation.py` waits for that marker before touching the GPU, then runs PPL, actual context boundary, zero RAM, synchronous control and `q5-long-p6`. It writes `validation-driver.log`. Long test replays all 15 P5 requests (8192 initial prompt, 7680 output positions) at RAM 8 GiB, with the read-only observer/ETW process. Do not launch duplicate model workloads.
3. Still required: run `summarize.py`, `audit.py` (fresh comparator checks uint32 bit patterns, stronger than early in-process float comparison), analyze route coverage, inspect long resource curves/ETW, archive sources/binaries/full model identities, finish report and update plan/development documentation. Rebuild is unnecessary unless source changes. Final `git diff --check` and script syntax checks are required.

No commit or push. The primary target is Q5 median decode +10% with no key regression; report failure honestly if missed. Full conditions are in PROTOCOL.zh-CN.md. Static grouping does not lend cold-group capacity to hot groups. No prefill, read-coalescing or complementary-residency optimization is included.
## Confirmed intermediate finding

The full six-pair Q5 timing matrix is complete. Median decode is P5 2.2417630712 versus P6 2.4494591549 token/s, ratio 1.0926485436 (+9.264854%). This does NOT meet the predeclared 10% performance gate. Keep all six pairs and report this honestly. Do not silently add rounds or change the threshold. IQ2 and validation continue independently of this failed performance target.
## Long-run progress and diagnostic evidence

All 24 paired runs and six PPL/context/zero-RAM/synchronous validation runs passed inference and the inherited comparison. The full long run is active (`q5-long-p6`, child PID 22792; validation exec session 31017). Do not launch another model workload. `status.py --brief` reports current progress and written logits, including positions newer than the 32-output checkpoint.

Long inference shows intermittent direct-read wait slowdowns that recover without changes. Memory stays around RSS 13.46 GiB / private 21.41 GiB so far. See DIAGNOSIS.md and long-slow-window.json; do not assert an SSD/driver/monitor root cause. Corrected WHEA errors mapped to the OTHER RTX 5060 Ti root port; the model disk has a different parent. No device settings or other jobs were changed.

A separate bounded 120-second early diagnostic ETW capture completed and its logger was STOPPED (trace_early.py, completed exec session 57171). Export deliberately waits until inference ends: run `python trace_early.py --export`, then `python analyze_etw.py q5-long-p6 early`. The normal observe_long.py is still attached and will capture its original 180-second steady window after 4096 outputs. Preserve both traces and any lost-event counts.

The final to-do remains: wait for validation-driver.log VALIDATION COMPLETE; summarize.py; audit.py with strict uint32 bit comparisons; route analysis; export/analyze early trace; report generation and inspection; update plan/development docs with the failed +10% gate and actual long metrics; archive.py (full model hashes only after inference, P6 source snapshot and P6-vs-P5 patch); syntax/diff checks; refresh archive research hashes after final docs. Production source and inference package have stayed frozen since tests. The current header/source does not require another build.
