# IQ2 default-off performance investigation

This is acceptance evidence, not a claim that a production defect has been fixed. The frozen 128-input/128-output teacher-forcing probe is the reproducible comparison loop. All variants retain exact logits.

## Reproduced symptom

The initial three monitored rounds gave off/native median throughput ratios 0.9493508 (decode) and 0.9553221 (prefill). Completing all six order permutations gave 0.9605873 and 0.9637321, still below the fixed 0.97 gate. Both snapshots are retained: `performance-initial-iq2-three-rounds.json` and `performance-iq2-six-rounds.json`.

## Ranked hypotheses and observations

1. **Short-window observation and shared-machine variation.** Prediction: more balanced repetitions or less intrusive observation changes the apparent gap without changing inference code. The six-round native decode range includes 15.238–19.195 token/s; off includes 14.052–18.573. Runtime GPU observation launches nvidia-smi approximately every two seconds, while IQ2 decode lasts only about seven seconds. A fixed six-pair AB/BA follow-up disables runtime GPU queries, retaining preflight GPU checks and 0.5-second host memory/commit guards. It also uses paired ordering, so a changed result alone cannot identify nvidia-smi as the sole cause. These `quiet-*` runs remain separate from the original failed cohort.
2. **Additional work while the feature is off.** Prediction: changed routing, cache fills, graph rebuilding, or a file-only scan appears in the native/off comparison. Both `iq2-native-r2` and `iq2-off-r2` report 126 graph reuses, zero graph reallocations, 40,951 cache hits / 20,019 misses, and 27,584.45 MiB uploaded. Their 317,492-byte MCT1 traces have identical SHA256 `7382ca7b5ae5c7278bc436a02450322bedd35bd72e5b4fd7c9f08bef7f3c6184`. Source inspection confirms the legacy copy callback is selected when off and file graph checks return immediately. This rules out those forms of extra work, but is not a CPU instruction-level profile.
3. **Build differences.** Prediction: mismatched optimization, ISA or backend choices explain the gap. Initial build commands and current caches confirm the same MSVC 14.44, CUDA 13.3, Release/O2, sm120 and native CPU configuration. The original build used CMake's default exception flags; it must not be described as missing EHsc. Later explicit UTF-8/Zc flags and rebuilt DLL section hashes are retained as build detail. `binary-section-identity.json` records unequal rebuilt PE sections; unequal hashes do not establish a kernel or performance defect. No diagnostic DLL swapping or inference source changes were made.

## Disposition

The six-pair follow-up completed with exact logits. Off/native median ratios are 1.0039342 (decode), 0.9952095 (prefill), and 0.9972101 (request wall), passing the unchanged throughput gate under the recheck conditions. Original monitored six-round failures remain in the report and audit; this is not an assertion that all measurement conditions passed. Runtime GPU observation and ordering both changed, and shared-machine activity was not controlled, so no sole cause is proven.

No stable production-code defect was localized; the fix/regression-test phase was therefore not applied speculatively. The original input and binaries were rechecked using the improved measurement loop. Diagnostic scripts are retained in this research directory for reproducibility; no temporary debug logging was added to production code. Future short GPU benchmarks should quantify observer overhead and use paired runs before interpreting differences of a few percent.
