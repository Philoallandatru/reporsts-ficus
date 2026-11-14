# P5 static review

Baseline: `D:/llama-ooc-p4-20261110/p4-source`; current production delta in `p5-review.patch`, with current files checked. Repository HEAD remains `7d7f0287530bc8981690f361d8c1627dbae1c99a`; no P5 commits. Two independent read-only reviewers followed the code-review skill. Neither ran GPU work during timing.

## Standards

No documented-standard violations or significant defects found in the P5 production diff, reviewed against AGENTS.md, CONTRIBUTING.md and the repository review checklist. Explicit GPU assignments survive measurement and are reapplied after graph reconstruction. File mode validates a single GPU. Residency accounting correctly distinguishes cumulative routes from current cached payload.

One optional low-priority Duplicated Code heuristic: `test_sched_measure_assigned` repeats part of the graph/backend fixture in `test_sched_copy_status`. This is a maintenance suggestion, not a standards violation. The fixtures remain local and short; no unrelated refactor was made during acceptance.

## Spec

One missing verification was identified: plan §8.2 requires the actual context boundary, while the long test uses 8192+512 in a 32K context. The original probe's conservative request guard also leaves its last context position unused. An independent short-context variant and `run_context_boundary.py` were added to fill position 511, require overflow position 512 to return no-slot status 1, clear/reuse the same context, and compare native/file logits. Its outcome is recorded separately; it does not alter performance probes or inference DLLs.

P4 already covers cancellation and context recreation. No other confirmed production implementation errors or scope creep were found. Pending formal measurements were correctly excluded from the draft's passing claims. The original-loader and CPU/GPU numeric limitations remain disclosed.

The added boundary run passed: actual capacity 512, successful last position 511, overflow status 1, clear/refill reuse, and 993,280 native/file float logits bitwise equal. Both processes exited normally. The Spec verification gap is closed.

Counts: Standards 0 violations / 1 optional heuristic; Spec 1 verification gap, now closed by the recorded boundary run.
