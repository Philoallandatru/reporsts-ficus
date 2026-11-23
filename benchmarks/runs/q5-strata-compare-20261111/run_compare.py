"""Same-token Q5 replay on frozen engines, with bounded sequential ETW traces."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import subprocess
import sys
import threading
import time

import psutil

HERE = Path(__file__).resolve().parent
ART = Path('D:/q5-strata-compare-20261111')
LAB = Path.home() / 'Documents/Code/tasks/strata-lab'
sys.path.insert(0, str(HERE.parent / 'ooc-p6-20261110'))
import run_probe as p6

MIB = 2**20
GIB = 2**30
GPU = p6.GPU
MODEL = p6.p4.MODEL['q5']
WORKING_SET_MIB = 24 * 1024
RAM_MIB = 16 * 1024
GPU_SLOTS = 963  # 1070 requested became 1185 physical slots / 4.41 GiB. Recalibrate below 4 GiB.
N = 128
DISK = 'PhysicalDrive2'
AFFINITY = list(range(14)) + [22, 23]
ENGINE = LAB / 'Strata/engine/strata.exe'
CONFIG = LAB / 'runs/outofcore-5080-budget24-01/config.json'


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def trajectory():
    p = read(Path('D:/llama-ooc-p6-20261110/runs/q5-p6-r1/result.json'))['requests'][0]
    p = {k: p[k] for k in ('prompt_tokens', 'tokens', 'eog_count')}
    assert len(p['prompt_tokens']) == len(p['tokens']) == N and 0 not in p['tokens']
    return p


def model_identity():
    a = read(HERE.parent / 'ooc-p6-20261110/machine-and-build.json')['models']['q5']
    b = read(LAB / 'evidence/model-verification.json')['files']
    assert len(a) == len(b) == 6
    assert {Path(r['path']).name: r['sha256'] for r in a} == {Path(r['path']).name: r['sha256'] for r in b}
    for row in a:
        p = MODEL.parent / Path(row['path']).name
        stat = p.stat()
        assert (stat.st_size, stat.st_mtime_ns) == (row['bytes'], row['mtime_ns']), str(p)
    return a


def model_disk():
    d = psutil.disk_io_counters(perdisk=True)[DISK]
    return dict(read_bytes=d.read_bytes, read_count=d.read_count, write_bytes=d.write_bytes)


def resources(proc):
    return dict(**p6.p4.sample(proc), disk=model_disk())


def invoke(args, log):
    p = subprocess.run(args, capture_output=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
    log.write_bytes(p.stdout + p.stderr)
    if p.returncode:
        raise RuntimeError(f'{args[0:2]} returned {p.returncode}; see {log}')
    return p.stdout


def prepare(mode, out, tokens):
    env = {k: v for k, v in os.environ.items() if not k.startswith(('LLAMA_', 'STRATA_', 'GGML_'))}
    env.update(CUDA_VISIBLE_DEVICES=GPU)
    if mode != 'strata':
        exe = ART / mode / 'q5_probe.exe'
        src = {'native': Path('D:/llama-ooc-p5-20261110/native-bin'),
               'native_np': Path('D:/llama-ooc-p5-20261110/native-noprefetch-bin'),
               'p6': Path('D:/llama-ooc-p6-20261110/file-bin')}[mode]
        binaries = {f.name: digest(f) for f in exe.parent.glob('*.dll')}
        assert binaries and all(digest(src / k) == v for k, v in binaries.items())
        binaries[exe.name] = digest(exe)
        env.update(LLAMA_EXPERT_STORE='file' if mode == 'p6' else 'off', LLAMA_EXPERT_RAM_MIB=str(RAM_MIB),
                   LLAMA_EXPERT_STAGING_MIB='32', LLAMA_EXPERT_IO_DEPTH='2', LLAMA_PLE_RAM_MIB='64',
                   LLAMA_EXPERT_GRAPH_MIB='4096', GGML_OP_OFFLOAD_MIN_BATCH='1',
                   LLAMA_MMAP_PREFETCH='off' if mode == 'native_np' else 'on')
        return [str(exe), str(MODEL)], exe.parent, env, binaries
    conf = read(CONFIG)
    follow = out / 'follow.txt'
    follow.write_text(','.join(map(str, tokens)) + '\n', encoding='ascii')
    env.update(STRATA_ROUTE_TAIL_SKIP='0', STRATA_FOLLOW=str(follow), STRATA_MMQ_KQ='1', STRATA_HC_Q8='1')
    env['PATH'] = os.pathsep.join([str(ENGINE.parent), *conf['lib_dirs'], env['PATH']])
    return [str(ENGINE), '--serve', '--pack', conf['args'][conf['args'].index('--pack') + 1], '--native', str(MODEL),
            '--expert-profile', conf['args'][conf['args'].index('--expert-profile') + 1],
            '--expert-cache', str(GPU_SLOTS), '--resident-budget-gib', '16', '--pool-workers', '15',
            '--prefill', '512', '--spec', '2', '--suffix-draft', '0', '--lookup-max-t', '0', '--lookup-chain', '0',
            '--eos-ids', '0', '--max-context', '32768', '--kv', 'int8', '--conversation-cache-mib', '0',
            '--prompt-cache', '0'], Path(conf['cwd']), env, {ENGINE.name: digest(ENGINE)}


def etw_time(stats, label):
    t = re.search(rf'{label} time \(UTC\)\s+: ([\d/:.]+)', stats)[1]
    return datetime.strptime(t[:-1], '%Y/%m/%d:%H:%M:%S.%f').replace(tzinfo=timezone.utc).timestamp()


def actual_budget(mode, engine_log):
    if mode == 'strata':
        ram = re.search(r'resident RAM mode: ([\d.]+) GiB of experts in RAM', engine_log)
        vram = re.search(r'expert cache (\d+) slots, ([\d.]+) GiB of VRAM', engine_log)
        assert ram and vram and 'mapped view of the experts is closed' in engine_log
        assert 'route tail skip:' not in engine_log
        return dict(ram_gib=float(ram[1]), gpu_slots=int(vram[1]), gpu_gib=float(vram[2]))
    vram = re.search(r'MoE cache size =\s+([\d.]+) MiB', engine_log)
    assert vram
    result = dict(gpu_mib=float(vram[1]))
    if mode == 'p6':
        # At READY the startup RAM line reports allocation even before any expert becomes live.
        ram = re.search(r'llama_expert_session: RAM = ([\d.]+) MiB', engine_log)
        assert ram
        result['ram_mib'] = float(ram[1])
    return result


def trace_summary(out, record, model_files):
    raw, merged = out / 'raw.etl', out / 'merged.etl'
    invoke(['xperf', '-merge', str(raw), str(merged)], out / 'merge.log')
    for action, args in [('tracestats', []), ('diskio', ['-detail'])]:
        invoke(['xperf', '-i', str(merged), '-o', str(out / f'{action}.txt'), '-a', action, *args], out / f'{action}.log')
    stats = (out / 'tracestats.txt').read_text(encoding='utf-8-sig', errors='replace')
    start, end = [etw_time(stats, label) for label in ('Start', 'End')]
    loss = [int(re.search(rf'Total # Lost {label}\s+: (\d+)', stats)[1]) for label in ('Buffers', 'Events')]
    first = record['tokens'][0][0]
    last = record['tokens'][-1][0]
    assert not any(loss) and start <= first < last <= end, (loss, start, first, last, end)
    phases = {'prefill': Counter(), 'decode': Counter()}
    initiators = {'prefill': Counter(), 'decode': Counter()}
    files = {Path(row['path']).name.lower() for row in model_files}
    expert = {f for f in files if re.search(r'-0000[456]-of-', f)}
    for line in (out / 'diskio.txt').open(encoding='utf-8-sig', errors='replace'):
        fields = [s.strip() for s in line.split(',', 15)]
        if len(fields) != 16 or fields[0] != 'DiskRead' or fields[14] != DISK.removeprefix('PhysicalDrive'):
            continue
        t = start + int(fields[2]) / 1e6
        if not record['request_time'] <= t <= last:
            continue
        phase = 'decode' if t > first else 'prefill'
        count = phases[phase]
        size = int(fields[5], 16)
        count['drive_bytes'] += size
        m = re.search(r'\(\s*(\d+)\s*\)$', fields[13])
        target = m is not None and int(m[1]) == record['pid']
        name = Path(fields[15]).name.lower()
        if target:
            count['target_pid_bytes'] += size
            if not fields[15]: count['target_unknown_path_bytes'] += size
        if name in files:
            count['q5_shard_bytes'] += size
            initiators[phase][fields[13]] += size
            if target: count['target_q5_shard_bytes'] += size
            if name in expert:
                count['expert_shard_bytes'] += size
                count['expert_shard_reads'] += 1
    output = dict(trace_start=start, trace_end=end, lost_buffers=loss[0], lost_events=loss[1],
                  phases={k: dict(v) for k, v in phases.items()}, initiators={k: dict(v) for k, v in initiators.items()},
                  scope='disk completion time, PhysicalDrive2, Q5 shard by filename, not NAND traffic')
    assert phases['decode']['drive_bytes'] > 0, 'no decode DiskRead records'
    assert phases['decode']['q5_shard_bytes'] > 0, 'Q5 filenames not resolved'
    return output


def run(name, mode, traj, models):
    out = ART / 'runs' / name
    out.mkdir(parents=True, exist_ok=False)
    cmd, cwd, env, binaries = prepare(mode, out, traj['tokens'])
    sys_pre = resources(psutil.Process())
    sys_pre.update(p6.gpu())
    record = dict(name=name, mode=mode, argv=cmd, gpu=GPU, preflight=sys_pre, binaries=binaries,
                  process_working_set_limit_mib=WORKING_SET_MIB, gpu_expert_budget_mib=4096,
                  expert_ram_budget_mib=RAM_MIB if mode in ('p6', 'strata') else None,
                  environment={k:v for k,v in env.items() if k.startswith(('CUDA_VISIBLE', 'LLAMA_', 'GGML_', 'STRATA_'))},
                  tokens=[])
    write(out / 'command.json', record)
    def reserve(row):
        return min(row['ram_available'], row['commit_limit']-row['commit_used'])
    if reserve(sys_pre) < (37 if mode in ('p6', 'strata') else 24)*GIB or sys_pre['gpu_free_mib'] < 11200:
        raise RuntimeError('preflight RAM/commit/GPU reserve not met')
    if psutil.disk_usage('D:/').free < 16*GIB or psutil.disk_usage('C:/').free < 3*GIB:
        raise RuntimeError('artifact/model disk reserve not met')
    print(name, 'LOAD', flush=True)
    trace_active = False
    stop = threading.Event()
    rows, gpu_rows, monitor_errors = [], [], []
    messages = queue.Queue()
    stderr = (out / 'engine.log').open('wb')
    child = subprocess.Popen(cmd, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr,
                             creationflags=subprocess.CREATE_NO_WINDOW)
    record['pid'] = child.pid
    proc = psutil.Process(child.pid)

    def stdout_loop():
        with (out / 'protocol.log').open('w', encoding='utf-8') as f:
            for raw in child.stdout:
                now = time.time()
                line = raw.decode('utf-8', errors='replace').strip()
                f.write(f'{now:.6f} {line}\n')
                f.flush()
                messages.put((now, line))
        messages.put((time.time(), None))

    def host_loop():
        with (out / 'samples.jsonl').open('w', encoding='utf-8') as f:
            while not stop.is_set() and child.poll() is None:
                try:
                    row = resources(proc)
                    rows.append(row)
                    f.write(json.dumps(row)+'\n')
                    f.flush()
                    if reserve(row) < 4*GIB or psutil.disk_usage('D:/').free < 12*GIB or psutil.disk_usage('C:/').free < 2*GIB:
                        monitor_errors.append('runtime resource reserve breached')
                        child.terminate()
                        return
                except psutil.NoSuchProcess:
                    return
                except Exception as exc:
                    monitor_errors.append(str(exc))
                    return
                stop.wait(.5)

    def gpu_loop():
        with (out / 'gpu.jsonl').open('w', encoding='utf-8') as f:
            while not stop.is_set() and child.poll() is None:
                try:
                    row = dict(time=time.time(), **p6.gpu())
                    gpu_rows.append(row)
                    f.write(json.dumps(row)+'\n')
                    f.flush()
                except Exception as exc:
                    f.write(json.dumps(dict(time=time.time(), error=str(exc)))+'\n')
                stop.wait(2)

    def until(prefix, timeout):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                at, line = messages.get(timeout=.5)
            except queue.Empty:
                if monitor_errors: raise RuntimeError(str(monitor_errors))
                continue
            if line is None or line.startswith('ERR '):
                raise RuntimeError(f'{mode} exited or refused request: {line}, {monitor_errors}')
            if line.startswith('T '): record['tokens'].append([at, int(line.split()[1])])
            if line.startswith(prefix): return at, line
        raise TimeoutError(prefix)

    threads = []
    try:
        record['working_set_policy'] = p6.limit_working_set(child.pid, WORKING_SET_MIB)
        proc.cpu_affinity(AFFINITY)
        write(out / 'command.json', record)
        threads = [threading.Thread(target=fn, daemon=True) for fn in (stdout_loop, host_loop, gpu_loop)]
        for th in threads: th.start()
        _, record['ready'] = until('READY ', 360)
        assert int(record['ready'].split()[1]) == 32768
        cache = actual_budget(mode, (out / 'engine.log').read_text(encoding='utf-8', errors='replace'))
        record['expert_cache_actual'] = cache
        if mode == 'strata':
            assert 15.97 <= cache['ram_gib'] <= 16 and 3.94 <= cache['gpu_gib'] < 4.00, cache
        else:
            assert 4060 <= cache['gpu_mib'] <= 4096, cache
            if mode == 'p6': assert 16380 <= cache['ram_mib'] <= RAM_MIB, cache
        time.sleep(3)
        pre_loggers = invoke(['xperf', '-loggers'], out / 'loggers-before.log').decode(errors='replace')
        if re.search(r'Logger Name\s*:\s*NT Kernel Logger', pre_loggers):
            raise RuntimeError('a kernel logger already exists; left it alone')
        invoke(['xperf', '-on', 'PROC_THREAD+LOADER+DISK_IO+DISK_IO_INIT+FILE_IO+FILE_IO_INIT+HARD_FAULTS',
                '-f', str(out/'raw.etl'), '-BufferSize', '1024', '-MinBuffers', '64', '-MaxBuffers', '128',
                '-MaxFile', '1536', '-FileMode', 'Sequential'], out / 'trace-start.log')
        trace_active = True
        idle_disk = model_disk()
        time.sleep(3)
        record['idle_disk_delta'] = model_disk()['read_bytes'] - idle_disk['read_bytes']
        record['disk_before'] = model_disk()
        record['request_time'] = time.time()
        prompt = ','.join(map(str, traj['prompt_tokens']))
        tail = '' if mode == 'strata' else ' ' + ','.join(map(str, traj['tokens']))
        child.stdin.write(f'GEN {N} {prompt}{tail}\n'.encode('ascii'))
        child.stdin.flush()
        print(name, 'REQUEST', flush=True)
        _, done = until('DONE ', 900)
        record['disk_after'] = model_disk()
        record['done'] = done
        fields = done.split()
        assert fields[1:3] == [str(N), str(N)] and fields[5:9] == ['length', '0', '0', '0'], done
        assert [x[1] for x in record['tokens']] == traj['tokens'], 'forced trajectory mismatch'
        if mode != 'strata':
            _, match = until('GREEDY_MATCH ', 10)
            record['greedy_match'] = int(match.split()[1])
        record['ttft_s'] = record['tokens'][0][0] - record['request_time']
        record['decode_s'] = record['tokens'][-1][0] - record['tokens'][0][0]
        record['decode_tps'] = (N - 1) / record['decode_s']
        record['engine_prefill_ms'], record['engine_decode_ms'] = map(float, fields[3:5])
        record['request_s'] = record['tokens'][-1][0] - record['request_time']
        record['done_time'] = time.time()
        invoke(['xperf', '-stop', 'NT Kernel Logger'], out / 'trace-stop.log')
        trace_active = False
        child.stdin.write(b'QUIT\n')
        child.stdin.flush()
        child.wait(timeout=90)
        record['exit_code'] = child.returncode
        assert child.returncode == 0
        assert actual_budget(mode, (out / 'engine.log').read_text(encoding='utf-8', errors='replace')) == cache
    except Exception as exc:
        record['error'] = repr(exc)
    finally:
        try:
            if trace_active:
                invoke(['xperf', '-stop', 'NT Kernel Logger'], out / 'trace-stop.log')
        finally:
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=30)
            stop.set()
            for th in threads: th.join(timeout=12)
            stderr.close()
            record['exit_code'] = child.returncode
    if rows:
        record['peak_rss_gib'] = max(r['rss'] for r in rows)/GIB
        record['peak_private_gib'] = max(r['private'] for r in rows)/GIB
        record['min_available_gib'] = min(r['ram_available'] for r in rows)/GIB
        record['min_commit_headroom_gib'] = min(r['commit_limit']-r['commit_used'] for r in rows)/GIB
    if gpu_rows:
        record['peak_gpu_used_mib'] = max(r['gpu_used_mib'] for r in gpu_rows)
    record['monitor_errors'] = monitor_errors
    if 'error' not in record:
        try:
            record['etw'] = trace_summary(out, record, models)
        except Exception as exc:
            record['trace_error'] = repr(exc)
    write(out / 'summary.json', record)
    print(name, 'END', record.get('decode_tps'), record.get('error'), record.get('trace_error'), flush=True)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('runs', nargs='+', help='name:mode, processed sequentially')
    args = parser.parse_args()
    models = model_identity()
    traj = trajectory()
    write(ART / 'trajectory.json', traj)
    write(ART / 'model-identity.json', models)
    for pair in args.runs:
        name, mode = pair.split(':')
        if mode not in ('native', 'native_np', 'p6', 'strata') or not re.fullmatch(r'[a-z0-9_-]+', name):
            raise ValueError(pair)
        record = run(name, mode, traj, models)
        if record.get('monitor_errors') or record.get('error') or record.get('trace_error'):
            raise SystemExit(1)


if __name__ == '__main__':
    main()
