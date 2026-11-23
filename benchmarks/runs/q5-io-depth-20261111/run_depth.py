"""Run the unchanged Q5 replay and ETW collector with a shadow expert-store DLL."""
import argparse
import json
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'q5-strata-compare-20261111'))
import run_compare as bench

ART = Path('D:/q5-io-depth-20261111')
FROZEN = Path('D:/llama-ooc-p6-20261110/file-bin')


def validation(out, record, depth):
    p = out/'logits.f32'
    assert p.stat().st_size == 128*248320*4, 'incomplete logits'
    record['logits_sha256'] = bench.digest(p)
    record['requested_depth'] = depth
    log = (out/'engine.log').read_text(encoding='utf-8', errors='replace')
    startup = re.search(r'llama_expert_session: RAM = ([\d.]+) MiB .*staging = ([\d.]+) MiB, depth = (\d+)', log)
    ple = re.search(r'llama_ple_session: RAM = ([\d.]+) MiB .*staging = ([\d.]+) MiB, depth = (\d+)', log)
    assert startup and startup[1] == '16383.047' and startup[2] == '32.000' and int(startup[3]) == depth
    assert ple and float(ple[1]) <= 64 and ple[2] == '1.000' and ple[3] == '2'
    lines = [line for line in log.splitlines() if line.startswith('llama_expert_session: RAM = ') and ', live/peak = ' in line]
    s = lines[-1]
    d = re.search(r'reads = (\d+) \((\d+) pending\), logical/direct = ([\d.]+)/([\d.]+) MiB, uploads = (\d+), overlap = (\d+), '
                  r'peak in-flight = (\d+), in-flight = (\d+), leases = (\d+), read/upload wait = ([\d.]+)/([\d.]+) ms, failures = (\d+), cancelled = (\d+)', s)
    assert d and int(d[7]) == depth and all(int(d[i]) == 0 for i in (8,9,12,13)), s
    assert record['greedy_match'] == 128
    record['session'] = dict(reads=int(d[1]), pending=int(d[2]), logical_mib=float(d[3]), direct_mib=float(d[4]),
                             uploads=int(d[5]), overlap=int(d[6]), peak_slots=int(d[7]),
                             read_wait_ms=float(d[10]), upload_wait_ms=float(d[11]))
    record['phase_scope_session'] = 'expert session: entire one request including prefill, not decode-only'
    assert record['etw']['trace_start'] <= record['request_time'] <= record['tokens'][0][0]
    assert record['peak_rss_gib'] < 24.01
    assert min(record['min_available_gib'],record['min_commit_headroom_gib']) >= 4


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trace-cap-mib',type=int,choices=(1536,3072),default=1536,
                        help='max ETW file size, increased only after a recorded trace overflow')
    parser.add_argument('runs', nargs='+', help='name:depth (use frozen-d2:2 for the archived DLL)')
    args = parser.parse_args()
    if args.trace_cap_mib != 1536:
        invoke = bench.invoke

        def larger_trace(args_, log):
            if args_[:2] == ['xperf','-on']:
                args_ = list(args_)
                args_[args_.index('-MaxFile')+1] = str(args.trace_cap_mib)
                (log.parent/'trace-command.json').write_text(json.dumps(args_),encoding='utf-8')
            return invoke(args_,log)

        bench.invoke = larger_trace
    identities = json.loads((HERE/'build-identity.json').read_text(encoding='utf-8'))
    traj, models = bench.trajectory(), bench.model_identity()
    bench.ART = ART
    bench.write(ART/'trajectory.json',traj)
    bench.write(ART/'model-identity.json',models)
    for spec in args.runs:
        name, depth_text = spec.split(':', 1)
        depth = int(depth_text)
        assert re.fullmatch(r'[a-z0-9_-]+',name) and depth in (1,2,4,8)
        frozen = name == 'frozen-d2'
        assert not frozen or depth == 2
        pkg = ART/('baseline' if frozen else 'candidate')
        dll_hash = identities['frozen_llama_sha256' if frozen else 'candidate_llama_sha256']

        def prepare(mode, out, tokens):
            exe = pkg/'q5_depth_probe.exe'
            h = {f.name:bench.digest(f) for f in pkg.glob('*.dll')}
            assert h['llama.dll'] == dll_hash
            assert all(bench.digest(FROZEN/k) == v for k,v in h.items() if k != 'llama.dll')
            h[exe.name] = bench.digest(exe)
            assert h[exe.name] == identities['probe_sha256']
            env = {k:v for k,v in os.environ.items() if not k.startswith(('LLAMA_','GGML_','STRATA_'))}
            env.update(CUDA_VISIBLE_DEVICES=bench.GPU, LLAMA_EXPERT_STORE='file', LLAMA_EXPERT_RAM_MIB='16384',
                       LLAMA_EXPERT_STAGING_MIB='32', LLAMA_EXPERT_IO_DEPTH=str(depth), LLAMA_PLE_RAM_MIB='64',
                       LLAMA_EXPERT_GRAPH_MIB='4096', GGML_OP_OFFLOAD_MIN_BATCH='1', LLAMA_MMAP_PREFETCH='on')
            return [str(exe),str(bench.MODEL),str(out/'logits.f32')], pkg, env, h

        bench.prepare = prepare
        r = bench.run(name,'p6',traj,models)
        if r.get('monitor_errors') or r.get('error') or r.get('trace_error'):
            raise SystemExit(1)
        out = ART/'runs'/name
        validation(out,r,depth)
        r['frozen'] = frozen
        bench.write(out/'summary.json',r)
        baseline = ART/'runs/frozen-d2/summary.json'
        if baseline.exists():
            ref = bench.read(baseline)
            assert r['logits_sha256'] == ref['logits_sha256'], name
        print(name, 'AUDITED', flush=True)


if __name__ == '__main__':
    main()
