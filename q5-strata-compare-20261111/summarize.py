"""Rebuild comparable request metrics from the archived measured runs."""
import json
from bisect import bisect_left
from statistics import median
import re

import numpy as np

from run_compare import ART, HERE, MIB, N, DISK, read, write


def io_shape(directory, r):
    first, last = r['tokens'][0][0], r['tokens'][-1][0]
    origin = r['etw']['trace_start']
    sizes, durations, queues = [], [], []
    times = [token[0] for token in r['tokens']]
    per_gap = [dict(bytes=0, reads=0, max_io_ms=0.0) for _ in times]
    for line in (directory/'diskio.txt').open(encoding='utf-8-sig', errors='replace'):
        if 'UD-Q5_K_XL-0000' not in line and 'ud-q5_k_xl-0000' not in line:
            continue
        fields = [s.strip() for s in line.split(',', 15)]
        if len(fields) != 16 or fields[0] != 'DiskRead' or fields[14] != DISK.removeprefix('PhysicalDrive'):
            continue
        completed = origin + int(fields[2])/1e6
        if not first < completed <= last:
            continue
        if not re.search(r'-0000[456]-of-\d+\.gguf$', fields[15], re.I):
            continue
        size = int(fields[5], 16)
        duration = (int(fields[2]) - int(fields[1]))/1000
        sizes.append(size/1024)
        durations.append(duration)
        queues.append(int(fields[8]))
        gap = per_gap[bisect_left(times, completed)]
        gap['bytes'] += size
        gap['reads'] += 1
        gap['max_io_ms'] = max(gap['max_io_ms'], duration)
    expected = r['etw']['phases']['decode'].get('expert_shard_reads',0)
    assert len(sizes) == expected, (directory, len(sizes), expected)
    slow = sorted(range(1,len(times)), key=lambda i: times[i]-times[i-1], reverse=True)[:5]
    return dict(expert_request_kib_mean=float(np.mean(sizes)),
                expert_request_kib_p50=float(np.median(sizes)),
                expert_io_ms_p50_p95_p99=np.percentile(durations,[50,95,99]).tolist(),
                drive_outstanding_at_start_p50_p95=np.percentile(queues,[50,95]).tolist(),
                slow_token_gaps=[dict(output_index=i+1, wall_s=times[i]-times[i-1], **per_gap[i]) for i in slow])


def main():
    rows, incomplete = [], []
    for directory in sorted((ART/'runs').iterdir()):
        path = directory/'summary.json'
        if not path.exists():
            incomplete.append(dict(name=directory.name, error='no summary'))
            continue
        r = read(path)
        if r.get('error') or r.get('trace_error') or r.get('monitor_errors') or 'etw' not in r:
            incomplete.append({k: r[k] for k in ('name','mode','error','trace_error','monitor_errors','peak_rss_gib','peak_private_gib','min_commit_headroom_gib') if k in r})
            continue
        d = r['etw']['phases']['decode']
        p = r['etw']['phases']['prefill']
        assert len(r['tokens']) == N and not r['etw']['lost_buffers'] and not r['etw']['lost_events']
        gaps = np.diff([token[0] for token in r['tokens']])*1000
        assert len(gaps) == N-1 and min(gaps) >= 0
        with (directory/'samples.jsonl').open(encoding='utf-8') as source:
            first_sample = json.loads(next(source))
        with (directory/'protocol.log').open(encoding='utf-8') as source:
            ready_time = float(next(line for line in source if ' READY ' in line).split()[0])
        rows.append(dict(**{k:r[k] for k in ('name','mode','decode_tps','decode_s','ttft_s','request_s','peak_rss_gib',
                    'peak_private_gib','peak_gpu_used_mib','min_available_gib','min_commit_headroom_gib','expert_cache_actual')},
                    q5_mib_per_decode=d['q5_shard_bytes']/MIB/(N-1),
                    expert_mib_per_decode=d.get('expert_shard_bytes',0)/MIB/(N-1),
                    physical_q5_gib_s=d['q5_shard_bytes']/2**30/r['decode_s'],
                    decode_disk_mib_s=d['drive_bytes']/MIB/r['decode_s'],
                    drive_mib_per_decode=d['drive_bytes']/MIB/(N-1),
                    expert_reads_per_decode=d.get('expert_shard_reads',0)/(N-1),
                    prefill_q5_gib=p.get('q5_shard_bytes',0)/2**30,
                    startup_s_from_first_sample=ready_time-first_sample['time'],
                    token_gap_ms_p50_p95_p99=np.percentile(gaps,[50,95,99]).tolist(),
                    unattributed_q5_mib=(d['q5_shard_bytes']-d.get('target_q5_shard_bytes',0))/MIB,
                    target_unknown_path_mib=d.get('target_unknown_path_bytes',0)/MIB,
                    idle_mib_per_s=r['idle_disk_delta']/MIB/3,
                    **io_shape(directory, r)))
    metrics = ['decode_tps','ttft_s','request_s','peak_rss_gib','peak_private_gib','peak_gpu_used_mib',
               'q5_mib_per_decode','expert_mib_per_decode','physical_q5_gib_s','expert_reads_per_decode','prefill_q5_gib',
               'startup_s_from_first_sample','expert_request_kib_p50']
    summary = {}
    for mode in ('native','native_np','p6','strata'):
        batch = [r for r in rows if r['mode'] == mode]
        if not batch: continue
        summary[mode] = dict(n=len(batch), **{k:dict(median=median(r[k] for r in batch), min=min(r[k] for r in batch),
                                                      max=max(r[k] for r in batch)) for k in metrics})
    result = dict(rows=rows, incomplete=incomplete, summary=summary)
    write(HERE/'measurements.json', result)
    for row in rows:
        print(json.dumps(row, ensure_ascii=False))
    for row in incomplete:
        print('INCOMPLETE',json.dumps(row, ensure_ascii=False))


if __name__ == '__main__':
    main()
