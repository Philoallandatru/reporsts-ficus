# Long-run slow I/O window

The first P6 long request showed a temporary slowdown around outputs 448-512. The run was not stopped, restarted, reconfigured or excluded. It continued into the second request without a source change.

The feedback loop is the existing 0.5-second resource sampling plus 32-output session-counter checkpoints and per-token durations. A replay of those recorded windows distinguishes increased work from increased wait. No extra model workload or disk benchmark was run alongside inference. This narrows the observed wait boundary; it is not a deterministic reproduction of an underlying device or OS defect.

Ranked checks were: (1) direct-read completion waits, (2) GPU upload/compute waits, (3) increased cache misses or lease backpressure. Results are saved in `long-slow-window.json`:

| Outputs | Wall s | Logical MiB | Read wait s | Upload wait s |
|---|---:|---:|---:|---:|
| 384-416 | 12.491 | 16133.032 | 7.107 | 1.168 |
| 416-448 | 19.967 | 22202.112 | 13.710 | 1.367 |
| 448-480 | 111.340 | 18541.602 | 98.382 | 4.282 |
| 480-512 | 106.057 | 18583.789 | 93.425 | 4.403 |

At elapsed 600-640 seconds the process read rate was about 1399 MiB/s; at 850-890 seconds it was about 55 MiB/s. Whole-model-disk read deltas tracked process reads closely in these windows. Sampled GPU temperature stayed about 46-50 C, with low utilization during the slow period. Available RAM and commit headroom remained well above the guards, and all listed checkpoint in-flight/lease values were zero. The last saved token timings then returned from roughly 8-18 seconds to roughly 0.2-0.8 seconds in the same process.

The excess time is concentrated in waiting for direct reads to complete, not a proportional rise in cache miss bytes or outstanding cache leases. That measured wait also includes host scheduling; these samples do not establish an SSD, driver, monitoring-tool or external-process root cause. No ETW window was active at that early point; the planned steady-state ETW window begins after 4096 outputs. Do not invent physical-cause attribution from the available counters.

There is no source fix or deterministic unit regression test for this unresolved transient. The original trace and all slow token timings remain in the final latency, wall-time and memory analysis. The short six-pair performance matrix had already completed and is unchanged. No debug instrumentation was added to production code.

Further slow intervals appeared in subsequent requests. A separate 120-second `early-slow-raw.etl` diagnostic window was captured with the same bounded ETW flags; it was stopped cleanly, and merge/export completed after inference ended. It does not replace the predeclared post-4096 steady-state window. Long-run timing includes the observer overhead and all slow intervals.

The complete run finished normally with 7680 outputs in 7843.34 seconds of inference (130.72 minutes), including 4210.87 seconds after the first 4096 outputs. The fresh final audit matched 1,907,097,600 logits bitwise and the full GPU route trace matched the historical P5 file trajectory. All budgets passed. Historical P5 inference took 74.71 minutes; this is not a fresh paired timing comparison, and the short-run speed gain does not establish a long-run speed gain.

All 7665 timed decode calls are retained: 422 exceeded one second, 314 exceeded five seconds, and the maximum was 29.065 seconds. The slowest checkpoint window was request 15, outputs 480-512: 31 actual decode calls took 240.54 seconds, including 219.25 seconds waiting for reads and 7.30 seconds waiting for uploads. Logical reads in that window were 16641.199 MiB. The full `long-slow-summary.json` includes every checkpoint window. Across matched post-warmup windows, P5/P6 logical reads were 664.084/596.881 MiB per decode, a 10.12% reduction in work despite the longer elapsed time. This does not identify the underlying wait cause.

ETW retention limits are explicit in the final analysis. The steady capture ran 182.04 seconds, but its 1 GiB circular file retains DiskIO events only around seconds 107.774-182.028 (74.25 seconds of timestamp span). The raw trace mode is recorded in `etw-raw-tracestats.txt`. Lost-event/buffer counters are both zero, which does not exclude intentional circular overwrite. Retained events contain 18.692 GiB of target expert reads and zero target pagefile hard-fault bytes; they do not establish full-window totals or absence of pagefile faults in unretained intervals. The separate early capture spans 121.16 seconds, with DiskIO timestamps spanning 121.14 seconds, 158.455 GiB of expert reads and zero target pagefile hard-fault bytes in retained records. The system-wide Pages Output/sec sampled integral is about 15752 pages and cannot be attributed to the target process. No trace or slow interval was deleted or replaced to hide these limits.

Read-only Windows storage inspection reported the model disk (PhysicalDrive2, ZHITAI Ti600 1TB) as Healthy/OK, at 53 C. The reliability provider returned `ReadLatencyMax=10665`, `WriteLatencyMax=6126`, and unavailable (null) read-error counters; its reporting interval was not established, so these are not attributed to one test window. System logs contained corrected WHEA event 17 entries for root port `8086:7F3C`, bus 128/device 28/function 4. PnP parent/child queries map that port to the RTX 5060 Ti and its audio controller. The model disk instead maps to root port `8086:7F44`, bus 128/device 27/function 4; inference uses the RTX 5080. These events cannot be presented as proven errors on the model-disk or selected-GPU link, nor as the established cause of the slowdown. No device, power, storage or other-task setting was changed. Raw evidence is retained in `model-disk-pnp-chain.json`, `corrected-port-children.json`, `model-disk-reliability.json` and `system-storage-events.json`.
