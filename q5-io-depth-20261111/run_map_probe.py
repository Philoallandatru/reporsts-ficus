"""Separate, fixed-offset Windows direct-I/O diagnostic; run after the model sweep."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

import numpy as np
import psutil

from run_depth import ART, HERE, bench
from build_shadow import VS


def main():
    root = ART/'map-probe'
    root.mkdir(exist_ok=False)
    exe = root/'map_probe.exe'
    bat = root/'build.cmd'
    bat.write_text('\n'.join(['@echo off',f'call "{VS / "VC/Auxiliary/Build/vcvars64.bat"}" -vcvars_ver=14.44 >nul',
                             'if errorlevel 1 exit /b 1',
                             f'cl /nologo /std:c++17 /EHsc /O2 /MD /utf-8 "{HERE / "map_probe.cpp"}" /Fe:"{exe}"',
                             'exit /b %errorlevel%','']),encoding='utf-8')
    subprocess.run([os.environ['ComSpec'],'/d','/c',str(bat)],cwd=root,check=True)
    shard = bench.MODEL.with_name(bench.MODEL.name.replace('00001-of','00004-of'))
    records = []
    for i, mapped in enumerate([0,1,1,0], 1):
        if min(bench.p6.p4.sample(psutil.Process())['ram_available'], psutil.disk_usage('D:/').free) < 8*2**30:
            raise RuntimeError('resource reserve not met')
        out = root / f'map-{i}-{mapped}'
        out.mkdir()
        raw, merged = out/'raw.etl', out/'merged.etl'
        active = bench.invoke(['xperf','-loggers'],out/'loggers-before.log').decode(errors='replace')
        assert not re.search(r'Logger Name\s*:\s*NT Kernel Logger',active)
        bench.invoke(['xperf','-on','PROC_THREAD+LOADER+DISK_IO+DISK_IO_INIT+FILE_IO+FILE_IO_INIT',
                      '-f',str(raw),'-BufferSize','1024','-MinBuffers','32','-MaxBuffers','64','-MaxFile','256','-FileMode','Sequential'],out/'start.log')
        try:
            stdout = bench.invoke([str(exe),str(shard),str(mapped)],out/'probe.log')
        finally:
            bench.invoke(['xperf','-stop','NT Kernel Logger'],out/'stop.log')
        r = json.loads(stdout)
        assert r['requests'] == 1536 and r['bytes'] == 1956*2**20 and r['mapped'] == mapped
        bench.invoke(['xperf','-merge',str(raw),str(merged)],out/'merge.log')
        for action, opts in [('tracestats',[]),('diskio',['-detail'])]:
            bench.invoke(['xperf','-i',str(merged),'-o',str(out/f'{action}.txt'),'-a',action,*opts],out/f'{action}.log')
        stats = (out/'tracestats.txt').read_text(encoding='utf-8-sig',errors='replace')
        assert not any(int(re.search(rf'Total # Lost {x}\s+: (\d+)',stats)[1]) for x in ('Events','Buffers'))
        qd, events, disk_bytes = [], [], 0
        for line in (out/'diskio.txt').open(encoding='utf-8-sig',errors='replace'):
            fields = [x.strip() for x in line.split(',',15)]
            if len(fields) != 16 or fields[0] != 'DiskRead' or fields[14] != bench.DISK.removeprefix('PhysicalDrive'): continue
            p = re.search(r'\(\s*(\d+)\s*\)$',fields[13])
            if not p or int(p[1]) != r['pid'] or Path(fields[15]).name.lower() != shard.name.lower(): continue
            qd.append(int(fields[8]))
            size = int(fields[5],16)
            disk_bytes += size
            events.append((int(fields[6],16),size))
        assert disk_bytes == r['bytes'], (disk_bytes,r['bytes'])
        extent_hash = hashlib.sha256(repr(sorted(events)).encode('ascii')).hexdigest()
        r.update(run=i, etw_reads=len(qd), physical_mib=disk_bytes/2**20, qd_p50_p95=np.percentile(qd,[50,95]).tolist(),
                 gib_s=disk_bytes/2**30/r['elapsed_s'],physical_extent_hash=extent_hash)
        bench.write(out/'summary.json',r)
        records.append(r)
        print('MAP PROBE',r,flush=True)
    assert len({r['physical_extent_hash'] for r in records}) == 1
    paired_unmapped_over_mapped = [records[i]['gib_s']/records[j]['gib_s'] for i,j in ((0,1),(3,2))]
    bench.write(HERE/'map-probe-results.json',dict(shard=str(shard),slots=8,staging_mib=32,records=records,
        paired_unmapped_over_mapped=paired_unmapped_over_mapped,
        scope='isolated same-shard aligned reads, no GPU, same held normal handle, only mapping presence changes'))


if __name__ == '__main__':
    main()
