"""Compile a one-file P6 variant and link it in an isolated artifact directory."""
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent / 'llama.cpp'
ART = Path('D:/q5-io-depth-20261111')
BUILD = Path('D:/llama-ooc-p0-p2-20261110/build')
FROZEN = Path('D:/llama-ooc-p6-20261110')
VS = Path('C:/Program Files/Microsoft Visual Studio/18/Community')
NINJA = VS/'Common7/IDE/CommonExtensions/Microsoft/CMake/Ninja/ninja.exe'


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def edit(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


def commands(target):
    return subprocess.check_output([str(NINJA), '-t', 'commands', target], cwd=BUILD, encoding='utf-8').splitlines()


def compile_variant(cmd, source, obj, obj_dir):
    args, previous_source = cmd.rsplit(' -c ', 1)
    assert previous_source.endswith(source.name)
    args = re.sub(r' /Fo\S+', lambda _: f' /Fo{obj}', args)
    args = re.sub(r' /Fd\S+', lambda _: f' /Fd{obj_dir / (obj.stem + ".pdb")}', args)
    return args.replace(' /showIncludes', '') + ' -c ' + str(source)


def link_variant(cmd, output_name, out_dir, obj_dir, replacements):
    for old,new in replacements.items():
        cmd = edit(cmd, old, str(new))
    cmd = re.sub(r'--intdir=\S+', lambda _: f'--intdir={obj_dir}', cmd)
    cmd = re.sub(r' /out:\S+', lambda _: f' /out:{out_dir / output_name}', cmd)
    stem = Path(output_name).stem
    cmd = re.sub(r' /implib:\S+', lambda _: f' /implib:{obj_dir / (stem + ".lib")}', cmd)
    cmd = re.sub(r' /pdb:\S+', lambda _: f' /pdb:{obj_dir / (stem + ".pdb")}', cmd)
    return cmd


def main():
    assert digest(BUILD/'bin/llama.dll') == digest(FROZEN/'file-bin/llama.dll')
    manifest = json.loads((HERE.parent/'ooc-p6-20261110/machine-and-build.json').read_text(encoding='utf-8'))
    for rel, expected in manifest['source_sha256'].items():
        if rel.startswith(('src/','ggml/','tests/')):
            assert digest(REPO/rel) == expected, rel
    obj = ART/'obj'
    generated = ART/'source'
    candidate = ART/'candidate'
    baseline = ART/'baseline'
    assert not (ART/'shadow-build.cmd').exists(), 'do not overwrite an existing build attempt'
    for p in (obj,generated,candidate,baseline):
        p.mkdir(parents=True,exist_ok=True)
    for target in (candidate,baseline):
        for dll in (FROZEN/'file-bin').glob('*.dll'):
            shutil.copy2(dll,target/dll.name)

    store_path = generated/'llama-expert-store.cpp'
    stock = (FROZEN/'p6-source/src/llama-expert-store.cpp').read_text(encoding='utf-8')
    variant = edit(stock, 'static size_t expert_env_size(', 'static constexpr unsigned expert_max_io_depth = 8;\n\nstatic size_t expert_env_size(')
    for old,new in (
        ('opts.io_depth, 1, 2, 1)', 'opts.io_depth, 1, expert_max_io_depth, 1)'),
        ('std::array<slot, 2>', 'std::array<slot, expert_max_io_depth>'),
        ('std::array<ggml_backend_event_ptr, 2>', 'std::array<ggml_backend_event_ptr, expert_max_io_depth>'),
        ('opts.io_depth > 2)', 'opts.io_depth > expert_max_io_depth)'),
    ):
        variant = edit(variant,old,new)
    store_path.write_text(variant,encoding='utf-8')
    (HERE/'depth-only.patch').write_text(''.join(difflib.unified_diff(stock.splitlines(True),variant.splitlines(True),
        fromfile='P6/src/llama-expert-store.cpp',tofile='candidate/src/llama-expert-store.cpp')),encoding='utf-8')

    test_path = generated/'test-expert-store.cpp'
    test = (FROZEN/'p6-source/tests/test-expert-store.cpp').read_text(encoding='utf-8')
    test = edit(test,'std::array<std::promise<void>, 2>','std::array<std::promise<void>, 8>')
    test = edit(test,'std::array<std::future<bool>, 2>','std::array<std::future<bool>, 8>')
    test = edit(test,'size_t ram_budget) {','size_t ram_budget, size_t depth = 2) {')
    test = edit(test,'st.peak_in_flight <= 2','st.peak_in_flight <= depth')
    test = edit(test,'int main() {',(HERE/'depth_test.inc').read_text(encoding='utf-8')+'\nint main() {')
    test = edit(test,'            test_cancel_and_error(index, t, reference);','            test_cancel_and_error(index, t, reference);\n            test_depth_eight(index, t, reference);')
    test_path.write_text(test,encoding='utf-8')

    probe_path = generated/'q5_depth_probe.cpp'
    probe = (HERE.parent/'q5-strata-compare-20261111/q5_probe.cpp').read_text(encoding='utf-8')
    probe = edit(probe,'#include <iostream>','#include <fstream>\n#include <iostream>')
    probe = edit(probe,'if (argc != 2)', 'if (argc != 3)')
    probe = edit(probe,'        const auto start = clock_type::now();','        std::vector<float> captured;\n        captured.reserve(size_t(nv)*count);\n        const auto start = clock_type::now();')
    probe = edit(probe,'            const auto token = forced[i];','            captured.insert(captured.end(), logits, logits + nv);\n            const auto token = forced[i];')
    probe = edit(probe,'        ctx.reset();','        std::ofstream logits_out(argv[2], std::ios::binary);\n        logits_out.write(reinterpret_cast<const char *>(captured.data()), captured.size()*sizeof(float));\n        logits_out.close();\n        if (!logits_out) throw std::runtime_error("logit archive failed");\n        ctx.reset();')
    probe_path.write_text(probe,encoding='utf-8')

    llama_cmds = commands('llama')
    test_cmds = commands('test-expert-store')
    store_obj = r'src\CMakeFiles\llama.dir\llama-expert-store.cpp.obj'
    test_root = r'tests\CMakeFiles\test-expert-store.dir'
    test_obj = test_root+r'\test-expert-store.cpp.obj'
    testing_obj = test_root+r'\__\src\llama-expert-store.cpp.obj'
    llama_link = next(c for c in llama_cmds if '/out:bin\\llama.dll' in c)
    test_link = next(c for c in test_cmds if '/out:bin\\test-expert-store.exe' in c)
    inputs = set(re.findall(r'\S+\.obj(?=\s)', llama_link+' '+test_link)) - {store_obj,test_obj,testing_obj}
    identities = {p: digest(BUILD/p) for p in sorted(inputs)}
    actions = [
        compile_variant(next(c for c in llama_cmds if '/Fo'+store_obj in c),store_path,obj/'store.obj',obj),
        link_variant(llama_link,'llama.dll',candidate,obj,{store_obj:obj/'store.obj'}),
        compile_variant(next(c for c in test_cmds if '/Fo'+testing_obj in c),store_path,obj/'store_test.obj',obj),
        compile_variant(next(c for c in test_cmds if '/Fo'+test_obj in c),test_path,obj/'test.obj',obj),
        link_variant(test_link,'test-expert-store.exe',candidate,obj,{test_obj:obj/'test.obj',testing_obj:obj/'store_test.obj'}),
        f'cl /nologo /std:c++17 /EHsc /O2 /MD /utf-8 /DGGML_SHARED /DLLAMA_SHARED /DNOMINMAX /I{REPO / "include"} /I{REPO / "src"} /I{REPO / "ggml/include"} {probe_path} /Fo{obj/"probe.obj"} /Fe:{candidate/"q5_depth_probe.exe"} /link /LIBPATH:{BUILD/"src"} /LIBPATH:{BUILD/"ggml/src"} llama.lib ggml.lib ggml-base.lib ggml-cpu.lib',
    ]
    bat = ART/'shadow-build.cmd'
    bat.write_text('\n'.join(['@echo off',f'call "{VS / "VC/Auxiliary/Build/vcvars64.bat"}" -vcvars_ver=14.44 >nul','if errorlevel 1 exit /b 1',
                             *(line for action in actions for line in (action,'if errorlevel 1 exit /b 1')),'exit /b 0','']),encoding='utf-8')
    with (HERE/'build.log').open('wb') as log:
        subprocess.run([os.environ['ComSpec'],'/d','/c',str(bat)],cwd=BUILD,stdout=log,stderr=subprocess.STDOUT,check=True)
    shutil.copy2(candidate/'q5_depth_probe.exe',baseline/'q5_depth_probe.exe')
    assert all(digest(BUILD/p) == h for p,h in identities.items())
    assert digest(BUILD/'bin/llama.dll') == digest(FROZEN/'file-bin/llama.dll')
    metadata = dict(generated={p.name:digest(p) for p in generated.iterdir()},reused_objects=identities,
                    frozen_llama_sha256=digest(baseline/'llama.dll'),candidate_llama_sha256=digest(candidate/'llama.dll'),
                    probe_sha256=digest(candidate/'q5_depth_probe.exe'))
    (HERE/'build-identity.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    print('SHADOW BUILD COMPLETE')


if __name__ == '__main__':
    main()
