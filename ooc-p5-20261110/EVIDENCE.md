# P5 evidence tables

Generated from per-run summaries and analysis.json; individual failures are retained. Execution status describes process completion only; numerical acceptance is recorded in comparison files and the final report.

| Run | Execution | GPU/RAM MiB; actual ubatch | Startup ready s | Prefill t/s | Decode t/s | Request wall s | Peak private GiB | Min commit margin GiB |
|---|---|---|---:|---:|---:|---:|---:|---:|
| boundary-file-default | completed | 4096/256; 512 | 2.46 | 2.43 | 1.49 | 27.04 | 13.67 | 26.13 |
| boundary-native-default | failed | 4096/256; None | — | — | — | — | 0.96 | 3.37 |
| boundary-native-default-mapped-primed | failed | 4096/256; None | — | — | — | — | 0.96 | 3.08 |
| boundary-native-default-noprefetch | completed | 4096/256; 512 | 3.68 | 1.89 | 0.91 | 36.90 | 13.33 | 26.02 |
| boundary-native-default-primed | failed | 4096/256; None | — | — | — | — | 0.87 | 2.63 |
| boundary-native-gpu | completed | 4096/256; 512 | 26.04 | 1.09 | 0.70 | 59.55 | 13.32 | 16.53 |
| boundary-native-gpu-noprefetch | completed | 4096/256; 512 | 2.49 | 5.24 | 2.83 | 12.92 | 13.32 | 26.57 |
| context-file | completed | 4096/8192; 512 | 2.42 | 14.71 | 1.59 | 70.73 | 20.15 | 21.29 |
| context-native | completed | 4096/8192; 512 | 2.47 | 9.31 | 2.50 | 110.54 | 11.97 | 30.26 |
| control-sync-no-ram | completed | 4096/0; 512 | 2.58 | 4.43 | 1.23 | 132.39 | 13.38 | 25.10 |
| iq2-file-r1 | completed | 4096/16384; 512 | 1.80 | 8.97 | 6.03 | 35.49 | 26.81 | 15.40 |
| iq2-file-r2 | completed | 4096/16384; 512 | 1.92 | 9.23 | 6.28 | 34.26 | 26.81 | 14.54 |
| iq2-file-r3 | completed | 4096/16384; 512 | 2.02 | 9.17 | 6.23 | 34.50 | 26.81 | 13.53 |
| iq2-file-r4 | completed | 4096/16384; 512 | 2.01 | 10.01 | 5.86 | 34.65 | 26.81 | 13.34 |
| iq2-file-r5 | completed | 4096/16384; 512 | 1.88 | 9.65 | 6.15 | 34.10 | 26.81 | 13.97 |
| iq2-file-r6 | completed | 4096/16384; 512 | 2.05 | 9.95 | 6.10 | 33.86 | 26.81 | 10.36 |
| iq2-native-r1 | completed | 4096/0; 512 | 15.23 | 26.11 | 18.59 | 11.91 | 10.69 | 5.57 |
| iq2-native-r2 | completed | 4096/0; 512 | 4.79 | 25.48 | 18.35 | 12.12 | 10.69 | 30.67 |
| iq2-native-r3 | completed | 4096/0; 512 | 4.66 | 26.38 | 19.20 | 11.64 | 10.69 | 31.42 |
| iq2-native-r4 | completed | 4096/0; 512 | 5.23 | 22.21 | 15.24 | 14.28 | 10.69 | 27.87 |
| iq2-native-r5 | completed | 4096/0; 512 | 4.82 | 26.05 | 18.70 | 11.88 | 10.69 | 31.03 |
| iq2-native-r6 | completed | 4096/0; 512 | 4.86 | 25.22 | 18.70 | 12.04 | 10.69 | 30.69 |
| iq2-off-r1 | completed | 4096/0; 512 | 4.39 | 26.35 | 17.65 | 12.23 | 10.69 | 31.62 |
| iq2-off-r2 | completed | 4096/0; 512 | 4.80 | 24.95 | 18.17 | 12.29 | 10.69 | 30.72 |
| iq2-off-r3 | completed | 4096/0; 512 | 4.83 | 23.67 | 17.22 | 12.95 | 10.69 | 29.82 |
| iq2-off-r4 | completed | 4096/0; 512 | 4.97 | 25.30 | 18.57 | 12.07 | 10.69 | 31.77 |
| iq2-off-r5 | completed | 4096/0; 512 | 4.79 | 24.71 | 18.55 | 12.19 | 10.68 | 30.97 |
| iq2-off-r6 | completed | 4096/0; 512 | 5.24 | 21.09 | 14.05 | 15.30 | 10.68 | 27.80 |
| matched-file-r1 | completed | 4096/16384; 512 | 2.40 | 5.15 | 2.30 | 80.19 | 29.45 | 13.49 |
| matched-file-r2 | completed | 4096/16384; 512 | 2.40 | 4.64 | 2.31 | 82.72 | 29.45 | 13.55 |
| matched-file-r3 | completed | 4096/16384; 512 | 2.37 | 5.16 | 2.21 | 82.57 | 29.45 | 13.56 |
| matched-file-r4 | completed | 4096/16384; 512 | 2.40 | 4.78 | 2.32 | 81.69 | 29.45 | 13.61 |
| matched-file-r5 | completed | 4096/16384; 512 | 2.36 | 5.18 | 2.18 | 83.19 | 29.45 | 13.51 |
| matched-file-r6 | completed | 4096/16384; 512 | 2.36 | 5.20 | 2.22 | 82.14 | 29.45 | 11.57 |
| matched-native-r1 | completed | 4096/0; 512 | 2.36 | 8.47 | 5.16 | 39.89 | 13.32 | 29.03 |
| matched-native-r2 | completed | 4096/0; 512 | 2.35 | 5.18 | 4.18 | 55.23 | 13.28 | 29.63 |
| matched-native-r3 | completed | 4096/0; 512 | 2.32 | 5.62 | 4.38 | 51.94 | 13.28 | 29.58 |
| matched-native-r4 | completed | 4096/0; 512 | 2.33 | 5.80 | 4.51 | 50.42 | 13.29 | 29.68 |
| matched-native-r5 | completed | 4096/0; 512 | 2.35 | 5.81 | 4.50 | 50.47 | 13.28 | 29.69 |
| matched-native-r6 | completed | 4096/0; 512 | 2.51 | 4.99 | 3.53 | 61.85 | 13.28 | 25.91 |
| matched-sync-r1 | completed | 4096/16384; 512 | 2.39 | 4.71 | 1.97 | 91.83 | 29.45 | 13.55 |
| matched-sync-r2 | completed | 4096/16384; 512 | 2.37 | 4.66 | 2.04 | 89.86 | 29.45 | 12.69 |
| matched-sync-r3 | completed | 4096/16384; 512 | 2.35 | 4.63 | 2.02 | 90.75 | 29.45 | 13.57 |
| matched-sync-r4 | completed | 4096/16384; 512 | 2.35 | 4.66 | 1.99 | 91.49 | 29.45 | 13.49 |
| matched-sync-r5 | completed | 4096/16384; 512 | 2.37 | 4.56 | 2.01 | 91.33 | 29.45 | 13.59 |
| matched-sync-r6 | completed | 4096/16384; 512 | 2.58 | 4.45 | 1.92 | 95.24 | 29.45 | 11.77 |
| perf-file-r1 | completed | 4096/16384; 512 | 2.59 | 4.55 | 2.18 | 86.60 | 29.45 | 13.47 |
| perf-file-r2 | completed | 4096/16384; 512 | 2.46 | 5.02 | 2.24 | 82.42 | 29.45 | 14.21 |
| perf-file-r3 | completed | 4096/16384; 512 | 2.49 | 5.02 | 2.26 | 81.91 | 29.45 | 13.61 |
| perf-file-r4 | completed | 4096/16384; 512 | 2.45 | 4.98 | 2.25 | 82.31 | 29.45 | 13.57 |
| perf-file-r5 | completed | 4096/16384; 512 | 2.37 | 5.20 | 2.31 | 79.88 | 29.45 | 13.59 |
| perf-file-r6 | completed | 4096/16384; 512 | 2.37 | 5.20 | 2.31 | 79.72 | 29.45 | 13.67 |
| perf-native-r1 | completed | 8192/0; 512 | 2.48 | 4.06 | 4.14 | 62.35 | 17.33 | 26.41 |
| perf-native-r2 | completed | 8192/0; 512 | 2.47 | 8.34 | 6.33 | 35.53 | 17.33 | 26.37 |
| perf-native-r3 | completed | 8192/0; 512 | 2.71 | 7.74 | 5.00 | 42.10 | 17.33 | 24.25 |
| perf-native-r4 | completed | 8192/0; 512 | 2.45 | 4.94 | 4.76 | 52.71 | 17.29 | 24.90 |
| perf-native-r5 | completed | 8192/0; 512 | 2.46 | 8.91 | 6.22 | 34.96 | 17.33 | 24.58 |
| perf-native-r6 | completed | 8192/0; 512 | 2.42 | 4.92 | 5.25 | 50.37 | 17.29 | 25.79 |
| perf-off-r1 | completed | 8192/0; 512 | 2.49 | 8.29 | 5.67 | 37.98 | 17.33 | 26.37 |
| perf-off-r2 | completed | 8192/0; 512 | 2.42 | 5.24 | 5.21 | 48.94 | 17.29 | 26.36 |
| perf-off-r3 | completed | 8192/0; 512 | 2.49 | 8.26 | 5.73 | 37.81 | 17.33 | 24.32 |
| perf-off-r4 | completed | 8192/0; 512 | 2.41 | 8.37 | 5.92 | 36.87 | 17.33 | 23.36 |
| perf-off-r5 | completed | 8192/0; 512 | 2.42 | 5.59 | 5.14 | 47.79 | 17.33 | 25.75 |
| perf-off-r6 | completed | 8192/0; 512 | 2.39 | 8.78 | 5.71 | 36.99 | 17.33 | 25.74 |
| q5-long-file | completed | 4096/8192; 512 | 2.53 | 11.93 | 2.05 | 4480.12 | 21.44 | 15.28 |
| q5-long-native | failed | 4096/0; 512 | 2.51 | — | — | — | 13.22 | 28.11 |
| q5-long-native-ws48 | completed | 4096/0; 512 | 2.63 | 9.82 | 3.66 | 2987.02 | 13.33 | 25.69 |
| q5-ppl-file | completed | 4096/16384; 512 | 2.54 | 1.77 | 2.51 | 79.45 | 29.38 | 11.38 |
| q5-ppl-native | completed | 4096/0; 512 | 2.43 | 2.31 | 2.97 | 66.37 | 13.25 | 26.32 |
| quiet-native-r1 | completed | 4096/0; 512 | 5.07 | 23.32 | 16.93 | 13.17 | 10.69 | 27.45 |
| quiet-native-r2 | completed | 4096/0; 512 | 4.69 | 25.80 | 18.41 | 12.04 | 10.69 | 31.87 |
| quiet-native-r3 | completed | 4096/0; 512 | 4.72 | 25.83 | 18.35 | 12.05 | 10.69 | 31.91 |
| quiet-native-r4 | completed | 4096/0; 512 | 4.74 | 25.80 | 18.77 | 11.90 | 10.69 | 31.78 |
| quiet-native-r5 | completed | 4096/0; 512 | 4.73 | 25.86 | 18.58 | 11.96 | 10.69 | 31.77 |
| quiet-native-r6 | completed | 4096/0; 512 | 4.70 | 25.60 | 18.55 | 12.02 | 10.69 | 31.79 |
| quiet-off-r1 | completed | 4096/0; 512 | 5.03 | 24.58 | 17.09 | 12.82 | 10.69 | 28.68 |
| quiet-off-r2 | completed | 4096/0; 512 | 4.88 | 25.07 | 18.04 | 12.31 | 10.69 | 31.24 |
| quiet-off-r3 | completed | 4096/0; 512 | 4.74 | 25.80 | 18.74 | 11.91 | 10.69 | 31.83 |
| quiet-off-r4 | completed | 4096/0; 512 | 4.79 | 25.65 | 18.36 | 12.08 | 10.69 | 31.85 |
| quiet-off-r5 | completed | 4096/0; 512 | 4.74 | 25.70 | 18.96 | 11.85 | 10.69 | 31.80 |
| quiet-off-r6 | completed | 4096/0; 512 | 4.70 | 25.82 | 18.80 | 11.89 | 10.69 | 31.83 |
| smoke-q5 | failed | 4096/8192; 512 | 2.52 | — | — | — | 5.48 | 37.07 |
| smoke-q5-fixed | failed | 4096/8192; 512 | 2.47 | — | — | — | 5.48 | 37.38 |
| smoke-q5-fixed2 | completed | 4096/8192; 512 | 2.55 | 1.97 | 1.53 | 14.26 | 21.44 | 21.26 |
| tune-file-g2048-r16384 | completed | 2048/16384; 512 | 2.48 | 5.58 | 2.03 | 85.63 | 27.45 | 15.43 |
| tune-file-g2048-r32768 | skipped | 2048/32768; None | — | — | — | — | — | — |
| tune-file-g2048-r8192 | completed | 2048/8192; 512 | 2.49 | 5.06 | 1.41 | 115.69 | 19.43 | 23.20 |
| tune-file-g4096-r16384 | completed | 4096/16384; 512 | 2.47 | 5.76 | 2.28 | 78.07 | 29.45 | 11.88 |
| tune-file-g4096-r32768 | skipped | 4096/32768; None | — | — | — | — | — | — |
| tune-file-g4096-r8192 | completed | 4096/8192; 512 | 2.65 | 5.74 | 1.83 | 91.70 | 21.43 | 20.05 |
| tune-file-g8192-r16384 | completed | 8192/16384; 4 | 2.64 | 3.37 | 3.04 | 79.98 | 31.68 | 8.88 |
| tune-file-g8192-r32768 | skipped | 8192/32768; None | — | — | — | — | — | — |
| tune-file-g8192-r8192 | completed | 8192/8192; 4 | 2.56 | 2.28 | 2.55 | 106.23 | 23.67 | 19.10 |
| tune-file-staging32-depth1 | completed | 4096/16384; 512 | 2.56 | 6.17 | 1.99 | 84.74 | 29.45 | 11.76 |
| tune-file-staging8-depth1 | completed | 4096/16384; 512 | 2.54 | 5.87 | 1.94 | 87.49 | 29.43 | 11.87 |
| tune-file-staging8-depth2 | completed | 4096/16384; 512 | 2.55 | 5.72 | 2.25 | 78.91 | 29.43 | 11.83 |
| tune-native-g2048-r0 | failed | 2048/0; None | — | — | — | — | 0.87 | 0.82 |
| tune-native-g2048-r0-u1 | failed | 2048/0; None | — | — | — | — | — | — |
| tune-native-g2048-r0-u1-retry1 | failed | 2048/0; None | — | — | — | — | 0.96 | 1.76 |
| tune-native-g4096-r0 | completed | 4096/0; 512 | 30.78 | 1.86 | 1.82 | 139.02 | 13.28 | 27.77 |
| tune-native-g4096-r0-u2 | failed | 4096/0; None | — | — | — | — | 0.87 | 1.09 |
| tune-native-g8192-r0 | completed | 8192/0; 512 | 27.98 | 1.27 | 1.85 | 169.98 | 17.29 | 20.54 |
| tune-native-g8192-r0-u4 | completed | 8192/0; 4 | 27.27 | 2.14 | 2.59 | 109.04 | 15.55 | 12.49 |
| tune-native-noprefetch-g2048-u1 | completed | 2048/0; 1 | 2.41 | 3.35 | 3.40 | 75.66 | 9.27 | 34.37 |
| tune-native-noprefetch-g2048-u512 | completed | 2048/0; 512 | 5.39 | 2.30 | 1.86 | 124.16 | 11.28 | 31.33 |
| tune-native-noprefetch-g4096-u2 | completed | 4096/0; 2 | 2.42 | 4.12 | 4.81 | 57.60 | 11.28 | 32.37 |
| tune-native-noprefetch-g4096-u512 | completed | 4096/0; 512 | 2.45 | 7.73 | 4.39 | 45.64 | 13.32 | 30.23 |
| tune-native-noprefetch-g8192-u4 | completed | 8192/0; 4 | 2.45 | 5.22 | 6.04 | 45.70 | 15.56 | 28.10 |
| tune-native-noprefetch-g8192-u512 | completed | 8192/0; 512 | 2.47 | 7.86 | 5.65 | 38.93 | 17.33 | 26.33 |

## Formal medians

Default-off throughput regression limit is 3%; incomplete groups are not judged.

### perf

```json
{
  "native": {
    "rounds": 6,
    "decode_tps": 5.122077917077657,
    "prefill_tps": 6.343168414144552,
    "request_wall_s": 46.23434935,
    "startup_ready_s": 2.46314695,
    "first_ttft_s": 21.21082725,
    "pooled_decode_p50_p95_p99_ms": [
      171.6009000000014,
      358.6137349999994,
      481.4414929999958
    ],
    "decode_tps_range": [
      4.13961888849688,
      6.33404972266938
    ],
    "prefill_tps_range": [
      4.059235188652337,
      8.906913140993833
    ],
    "request_wall_s_range": [
      34.9552817,
      62.347218
    ],
    "peak_rss_gib": 48.000003814697266,
    "peak_private_gib": 17.331558227539062,
    "min_available_ram_gib": 13.933837890625,
    "min_commit_headroom_gib": 24.254100799560547,
    "run_names": [
      "perf-native-r1",
      "perf-native-r2",
      "perf-native-r3",
      "perf-native-r4",
      "perf-native-r5",
      "perf-native-r6"
    ]
  },
  "off": {
    "rounds": 6,
    "decode_tps": 5.689581270746496,
    "prefill_tps": 8.273708369796212,
    "request_wall_s": 37.891975900000006,
    "startup_ready_s": 2.4185997500000003,
    "first_ttft_s": 15.4711076,
    "pooled_decode_p50_p95_p99_ms": [
      159.83049999999997,
      330.4470550000005,
      467.4356419999993
    ],
    "decode_tps_range": [
      5.13576911134938,
      5.923574130524138
    ],
    "prefill_tps_range": [
      5.2423009949846335,
      8.781303830292906
    ],
    "request_wall_s_range": [
      36.8697677,
      48.9393655
    ],
    "peak_rss_gib": 48.000003814697266,
    "peak_private_gib": 17.33167266845703,
    "min_available_ram_gib": 13.82217025756836,
    "min_commit_headroom_gib": 23.363971710205078,
    "run_names": [
      "perf-off-r1",
      "perf-off-r2",
      "perf-off-r3",
      "perf-off-r4",
      "perf-off-r5",
      "perf-off-r6"
    ]
  },
  "file": {
    "rounds": 6,
    "decode_tps": 2.2537524044965096,
    "prefill_tps": 5.017254577208709,
    "request_wall_s": 82.1105079,
    "startup_ready_s": 2.4544707,
    "first_ttft_s": 25.5123687,
    "pooled_decode_p50_p95_p99_ms": [
      390.0056499999955,
      777.5211699999976,
      1147.3169640000006
    ],
    "decode_tps_range": [
      2.1759011437190887,
      2.3117213874357643
    ],
    "prefill_tps_range": [
      4.554857041737283,
      5.202006004057792
    ],
    "request_wall_s_range": [
      79.7156903,
      86.604719
    ],
    "peak_rss_gib": 20.787097930908203,
    "peak_private_gib": 29.450397491455078,
    "min_available_ram_gib": 41.596073150634766,
    "min_commit_headroom_gib": 13.46657943725586,
    "run_names": [
      "perf-file-r1",
      "perf-file-r2",
      "perf-file-r3",
      "perf-file-r4",
      "perf-file-r5",
      "perf-file-r6"
    ]
  },
  "default_off_regression": {
    "decode_ratio": 1.110795533152026,
    "prefill_ratio": 1.304349471684651,
    "request_wall_ratio": 0.8195632994238299,
    "decode_pass_limit_3_percent": true,
    "prefill_pass_limit_3_percent": true,
    "both_throughputs_pass_limit_3_percent": true
  }
}
```

### matched

```json
{
  "native": {
    "rounds": 6,
    "decode_tps": 4.441733909186361,
    "prefill_tps": 5.707351113103219,
    "request_wall_s": 51.203136900000004,
    "startup_ready_s": 2.3453695999999997,
    "first_ttft_s": 22.4331467,
    "pooled_decode_p50_p95_p99_ms": [
      205.11219999999852,
      405.5957049999987,
      567.1742569999972
    ],
    "decode_tps_range": [
      3.526072079587852,
      5.161073990075138
    ],
    "prefill_tps_range": [
      4.989329111342251,
      8.466494143768994
    ],
    "request_wall_s_range": [
      39.8901287,
      61.84673539999999
    ],
    "peak_rss_gib": 48.000003814697266,
    "peak_private_gib": 13.323772430419922,
    "min_available_ram_gib": 12.40884780883789,
    "min_commit_headroom_gib": 25.908794403076172,
    "run_names": [
      "matched-native-r1",
      "matched-native-r2",
      "matched-native-r3",
      "matched-native-r4",
      "matched-native-r5",
      "matched-native-r6"
    ]
  },
  "file": {
    "rounds": 6,
    "decode_tps": 2.2590574879763947,
    "prefill_tps": 5.152021746776466,
    "request_wall_s": 82.35216855,
    "startup_ready_s": 2.38417215,
    "first_ttft_s": 24.845053550000003,
    "pooled_decode_p50_p95_p99_ms": [
      397.11019999999667,
      762.1395700000025,
      1097.985839000001
    ],
    "decode_tps_range": [
      2.1790626885725666,
      2.3208534925195665
    ],
    "prefill_tps_range": [
      4.643114292880954,
      5.1976279455404235
    ],
    "request_wall_s_range": [
      80.1927208,
      83.18634709999999
    ],
    "peak_rss_gib": 20.780399322509766,
    "peak_private_gib": 29.450237274169922,
    "min_available_ram_gib": 40.873897552490234,
    "min_commit_headroom_gib": 11.565746307373047,
    "run_names": [
      "matched-file-r1",
      "matched-file-r2",
      "matched-file-r3",
      "matched-file-r4",
      "matched-file-r5",
      "matched-file-r6"
    ]
  },
  "sync": {
    "rounds": 6,
    "decode_tps": 2.001177248525943,
    "prefill_tps": 4.643891168216549,
    "request_wall_s": 91.4109986,
    "startup_ready_s": 2.3705385999999997,
    "first_ttft_s": 27.5638073,
    "pooled_decode_p50_p95_p99_ms": [
      435.3560500000029,
      884.1036399999962,
      1504.2636470000004
    ],
    "decode_tps_range": [
      1.9165764523818256,
      2.0412131642170124
    ],
    "prefill_tps_range": [
      4.4452736268906605,
      4.714764449152595
    ],
    "request_wall_s_range": [
      89.8627752,
      95.2377798
    ],
    "peak_rss_gib": 20.786087036132812,
    "peak_private_gib": 29.450340270996094,
    "min_available_ram_gib": 40.143638610839844,
    "min_commit_headroom_gib": 11.772266387939453,
    "run_names": [
      "matched-sync-r1",
      "matched-sync-r2",
      "matched-sync-r3",
      "matched-sync-r4",
      "matched-sync-r5",
      "matched-sync-r6"
    ]
  }
}
```

### iq2

```json
{
  "native": {
    "rounds": 6,
    "decode_tps": 18.64258298124911,
    "prefill_tps": 25.764277979234173,
    "request_wall_s": 11.97425835,
    "startup_ready_s": 4.8417416,
    "first_ttft_s": 4.96917455,
    "pooled_decode_p50_p95_p99_ms": [
      48.468850000000785,
      102.12617000000088,
      154.1753940000004
    ],
    "decode_tps_range": [
      15.238110961860253,
      19.19500211719365
    ],
    "prefill_tps_range": [
      22.209452558162827,
      26.382353387954833
    ],
    "request_wall_s_range": [
      11.640295,
      14.2817271
    ],
    "peak_rss_gib": 19.970687866210938,
    "peak_private_gib": 10.687259674072266,
    "min_available_ram_gib": 24.989280700683594,
    "min_commit_headroom_gib": 5.567325592041016,
    "run_names": [
      "iq2-native-r1",
      "iq2-native-r2",
      "iq2-native-r3",
      "iq2-native-r4",
      "iq2-native-r5",
      "iq2-native-r6"
    ]
  },
  "off": {
    "rounds": 6,
    "decode_tps": 17.907827946198793,
    "prefill_tps": 24.829862087366738,
    "request_wall_s": 12.259766950000001,
    "startup_ready_s": 4.8152151,
    "first_ttft_s": 5.155587250000001,
    "pooled_decode_p50_p95_p99_ms": [
      50.80404999999999,
      113.167754999999,
      168.46172999999962
    ],
    "decode_tps_range": [
      14.051706429270876,
      18.572621773588263
    ],
    "prefill_tps_range": [
      21.089726256836062,
      26.352274696440837
    ],
    "request_wall_s_range": [
      12.066970400000002,
      15.295196699999998
    ],
    "peak_rss_gib": 19.970661163330078,
    "peak_private_gib": 10.687206268310547,
    "min_available_ram_gib": 39.96217727661133,
    "min_commit_headroom_gib": 27.799861907958984,
    "run_names": [
      "iq2-off-r1",
      "iq2-off-r2",
      "iq2-off-r3",
      "iq2-off-r4",
      "iq2-off-r5",
      "iq2-off-r6"
    ]
  },
  "file": {
    "rounds": 6,
    "decode_tps": 6.125387996530476,
    "prefill_tps": 9.439138002242593,
    "request_wall_s": 34.379606700000004,
    "startup_ready_s": 1.9605294,
    "first_ttft_s": 13.567696950000002,
    "pooled_decode_p50_p95_p99_ms": [
      125.93374999999973,
      360.8706450000001,
      804.6544049999995
    ],
    "decode_tps_range": [
      5.862924962113033,
      6.281971991338172
    ],
    "prefill_tps_range": [
      8.973943929452236,
      10.005380080470145
    ],
    "request_wall_s_range": [
      33.857405,
      35.487961000000006
    ],
    "peak_rss_gib": 17.11248016357422,
    "peak_private_gib": 26.812679290771484,
    "min_available_ram_gib": 42.02772903442383,
    "min_commit_headroom_gib": 10.35616683959961,
    "run_names": [
      "iq2-file-r1",
      "iq2-file-r2",
      "iq2-file-r3",
      "iq2-file-r4",
      "iq2-file-r5",
      "iq2-file-r6"
    ]
  },
  "default_off_regression": {
    "decode_ratio": 0.960587272922999,
    "prefill_ratio": 0.9637321141845866,
    "request_wall_ratio": 1.0238435309857834,
    "decode_pass_limit_3_percent": false,
    "prefill_pass_limit_3_percent": false,
    "both_throughputs_pass_limit_3_percent": false
  }
}
```

### quiet

```json
{
  "native": {
    "rounds": 6,
    "decode_tps": 18.478432754254076,
    "prefill_tps": 25.80015737856168,
    "request_wall_s": 12.028523949999999,
    "startup_ready_s": 4.72223725,
    "first_ttft_s": 4.96167255,
    "pooled_decode_p50_p95_p99_ms": [
      48.28855000000054,
      101.70370000000116,
      143.61780999999962
    ],
    "decode_tps_range": [
      16.93019199264309,
      18.767637700300615
    ],
    "prefill_tps_range": [
      23.323927959383706,
      25.860000583466263
    ],
    "request_wall_s_range": [
      11.900999200000001,
      13.169320800000001
    ],
    "peak_rss_gib": 19.922775268554688,
    "peak_private_gib": 10.687450408935547,
    "min_available_ram_gib": 39.980926513671875,
    "min_commit_headroom_gib": 27.45181655883789,
    "run_names": [
      "quiet-native-r1",
      "quiet-native-r2",
      "quiet-native-r3",
      "quiet-native-r4",
      "quiet-native-r5",
      "quiet-native-r6"
    ]
  },
  "off": {
    "rounds": 6,
    "decode_tps": 18.55113098970921,
    "prefill_tps": 25.676561069384185,
    "request_wall_s": 11.9949661,
    "startup_ready_s": 4.7662071,
    "first_ttft_s": 4.98554485,
    "pooled_decode_p50_p95_p99_ms": [
      48.39309999999841,
      100.80173500000063,
      144.73764500000058
    ],
    "decode_tps_range": [
      17.089603631134388,
      18.96120883051268
    ],
    "prefill_tps_range": [
      24.584640104589205,
      25.81709439776514
    ],
    "request_wall_s_range": [
      11.853637,
      12.816377099999999
    ],
    "peak_rss_gib": 19.933509826660156,
    "peak_private_gib": 10.687568664550781,
    "min_available_ram_gib": 40.096458435058594,
    "min_commit_headroom_gib": 28.68267822265625,
    "run_names": [
      "quiet-off-r1",
      "quiet-off-r2",
      "quiet-off-r3",
      "quiet-off-r4",
      "quiet-off-r5",
      "quiet-off-r6"
    ]
  },
  "default_off_regression": {
    "decode_ratio": 1.0039342208520579,
    "prefill_ratio": 0.9952094746026552,
    "request_wall_ratio": 0.9972101439761444,
    "decode_pass_limit_3_percent": true,
    "prefill_pass_limit_3_percent": true,
    "both_throughputs_pass_limit_3_percent": true
  }
}
```
