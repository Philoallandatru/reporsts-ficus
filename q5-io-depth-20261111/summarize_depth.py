"""Audit the depth sweep and summarize request shape without omitting slow samples."""
from collections import Counter
import hashlib
from pathlib import Path
import re
from statistics import median

import numpy as np

from run_depth import ART, HERE, bench

NAMES = ['frozen-d2','r1-d2','r1-d4','r1-d1','r1-d8','r2-d8','r2-d4','r2-d2','r2-d1-retry']


def io_shape(directory, record):
    etw = record['etw']
    origin = etw['trace_start']
    times = [t for t,_ in record['tokens']]
    first, last = times[0], times[-1]
    slowest = sorted(range(1,len(times)),key=lambda i:times[i]-times[i-1],reverse=True)[:5]
    slow_reads = {i:[] for i in slowest}
    reqs, counts, sizes, qd, durations = Counter(), Counter(), [], [], []
    for line in (directory/'diskio.txt').open(encoding='utf-8-sig',errors='replace'):
        if not re.search(r'-0000[456]-of-\d+\.gguf\s*$',line,re.I):
            continue
        fields = [s.strip() for s in line.split(',',15)]
        if len(fields) != 16 or fields[0] != 'DiskRead' or fields[14] != '2':
            continue
        started, ended = [origin + int(fields[i])/1e6 for i in (1,2)]
        if not first < ended <= last:
            continue
        size = int(fields[5],16)
        key = (Path(fields[15]).name.lower(),int(fields[6],16),size)
        reqs[key] += 1
        counts['bytes'] += size
        sizes.append(size/1024)
        qd.append(int(fields[8]))
        durations.append((int(fields[2])-int(fields[1]))/1000)
        for i in slowest:
            if ended > times[i-1] and started < times[i]:
                slow_reads[i].append((max(started,times[i-1]),min(ended,times[i]),durations[-1]))
    d = etw['phases']['decode']
    assert len(sizes) == d['expert_shard_reads'] and counts['bytes'] == d['expert_shard_bytes']
    assert d['q5_shard_bytes'] == d['target_q5_shard_bytes']
    fingerprint = hashlib.sha256()
    for key,n in sorted(reqs.items()):
        fingerprint.update(f'{key}:{n}\n'.encode('ascii'))
    slow = []
    for i in slowest:
        stop = times[i-1]
        busy = 0.
        for begin,end,_ in sorted(slow_reads[i]):
            if end > stop:
                busy += end - max(begin,stop)
                stop = end
        slow.append(dict(output_token=i+1,gap_s=times[i]-times[i-1],expert_disk_busy_s=busy,
                         overlapping_expert_reads=len(slow_reads[i]),
                         max_overlapping_expert_disk_read_ms=max((ms for _,_,ms in slow_reads[i]),default=0.)))
    return dict(qd_p50_p95=np.percentile(qd,[50,95]).tolist(), size_kib_p50=float(np.median(sizes)),
                io_ms_p50_p95_p99=np.percentile(durations,[50,95,99]).tolist(), expert_reads_per_step=len(sizes)/127,
                expert_disk_read_max_ms=max(durations), expert_disk_reads_ge_100ms=sum(ms>=100 for ms in durations),
                slowest_output_steps=slow,
                q5_mib_per_step=d['q5_shard_bytes']/2**20/127,
                q5_gib_s=d['q5_shard_bytes']/2**30/record['decode_s'],
                expert_disk_extent_multiset_sha256=fingerprint.hexdigest())


def main():
    rows, incomplete = {}, []
    for name in NAMES:
        directory = ART/'runs'/name
        path = directory/'summary.json'
        if not path.exists():
            incomplete.append(dict(name=name, reason='not complete'))
            continue
        r = bench.read(path)
        if 'logits_sha256' not in r:
            incomplete.append(dict(name=name,error=r.get('error'),trace_error=r.get('trace_error'),monitor_errors=r.get('monitor_errors')))
            continue
        assert r['exit_code'] == 0 and not r['monitor_errors'] and not r.get('trace_error')
        assert not r['etw']['lost_events'] and not r['etw']['lost_buffers']
        gaps = np.diff([t[0] for t in r['tokens']])*1000
        assert len(gaps) == 127 and min(gaps) >= 0
        rows[name.removesuffix('-retry')] = dict(name=name, depth=r['requested_depth'], frozen=r['frozen'], logits_sha256=r['logits_sha256'],
                          decode_tps=r['decode_tps'],ttft_s=r['ttft_s'],latency_ms_p50_p95_p99=np.percentile(gaps,[50,95,99]).tolist(),
                          longest_token_s=float(max(gaps)/1000),peak_rss_gib=r['peak_rss_gib'],peak_private_gib=r['peak_private_gib'],
                          min_commit_headroom_gib=r['min_commit_headroom_gib'],session=r['session'],**io_shape(directory,r))
    if 'frozen-d2' in rows:
        f = rows['frozen-d2']
        assert all(r['logits_sha256'] == f['logits_sha256'] for r in rows.values())
        control = ART/'runs/frozen-d2/logits.f32'
        archived = Path('D:/llama-ooc-p6-20261110/runs/q5-p6-r1/logits-0.f32')
        assert bench.digest(control) == f['logits_sha256'] == bench.digest(archived)
    decisions = {}
    if 'frozen-d2' in rows and all(f'r{i}-d2' in rows for i in (1,2)):
        baseline = [rows[f'r{i}-d2'] for i in (1,2)]
        for depth in (1,2,4,8):
            if not all(f'r{i}-d{depth}' in rows for i in (1,2)):
                continue
            v = [rows[f'r{i}-d{depth}'] for i in (1,2)]
            rate = [r['decode_tps']/b['decode_tps'] for r,b in zip(v,baseline)]
            tail = [r['latency_ms_p50_p95_p99'][2]/b['latency_ms_p50_p95_p99'][2] for r,b in zip(v,baseline)]
            reads = [r['q5_mib_per_step']/b['q5_mib_per_step'] for r,b in zip(v,baseline)]
            logical = [r['session']['logical_mib']/b['session']['logical_mib'] for r,b in zip(v,baseline)]
            aligned = [r['session']['direct_mib']/b['session']['direct_mib'] for r,b in zip(v,baseline)]
            d = dict(decode_tps_median=median(r['decode_tps'] for r in v), ttft_s_median=median(r['ttft_s'] for r in v),
                     qd_p50_p95=[median(r['qd_p50_p95'][i] for r in v) for i in (0,1)],
                     io_p95_ms_median=median(r['io_ms_p50_p95_p99'][1] for r in v),
                     q5_gib_s_median=median(r['q5_gib_s'] for r in v), q5_mib_per_step_median=median(r['q5_mib_per_step'] for r in v),
                     paired_decode_ratios=rate, paired_p99_ratios=tail, paired_read_ratios=reads,
                     paired_logical_read_ratios=logical,paired_aligned_read_ratios=aligned,
                     matched_expert_disk_extents=[r['expert_disk_extent_multiset_sha256']==b['expert_disk_extent_multiset_sha256'] for r,b in zip(v,baseline)],
                     gain_over_d2_median_pct=100*(median(r['decode_tps'] for r in v)/median(r['decode_tps'] for r in baseline)-1))
            d['screen_pass'] = depth in (4,8) and min(rate)>1 and d['gain_over_d2_median_pct']>=10 and max(tail)<=1.1 and max(reads+logical+aligned)<=1.01
            decisions[str(depth)] = d
    # Keep the timing-only observation. The kernel logger reached its sequential
    # cap and disappeared before STOP; this sample has no full ETW or logits.
    original = ART/'runs/r2-d1'
    log = (original/'protocol.log').read_text(encoding='utf-8')
    t = [(float(s),int(token)) for s,token in re.findall(r'^(\d+\.\d+) T (\d+)$',log,re.M)]
    assert [token for _,token in t] == bench.trajectory()['tokens'] and 'GREEDY_MATCH 128' in log
    assert (original/'raw.etl').stat().st_size == 1536*2**20
    assert b'0x1069' in (original/'trace-stop.log').read_bytes()
    gaps = np.diff([s for s,_ in t])*1000
    excluded = dict(name='r2-d1',depth=1,decode_tps=127/(t[-1][0]-t[0][0]),
                    latency_ms_p50_p95_p99=np.percentile(gaps,[50,95,99]).tolist(),longest_token_s=float(max(gaps)/1000),
                    trace_cap_mib=1536,reason='sequential ETW file hit cap, STOP 0x1069, missing full ETW and written logits')
    bench.write(HERE/'measurements.json',dict(rows=list(rows.values()),incomplete=incomplete,decisions=decisions,
                                             retained_timing_only=[excluded]))
    for r in rows.values():
        print(f"{r['name']}: {r['decode_tps']:.3f} tok/s, TTFT {r['ttft_s']:.2f} s, p99 {r['latency_ms_p50_p95_p99'][2]:.0f} ms, QD {r['qd_p50_p95']}, read {r['q5_gib_s']:.3f} GiB/s")
    for k,v in decisions.items():
        print(k,v)
    print('Timing-only:',excluded)
    if incomplete:
        print('Incomplete:',incomplete)


if __name__ == '__main__':
    main()
