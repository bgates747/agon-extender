"""Exercise actual ESP-DSP matrix source before/after the P4 lifetime recipe.

Host stubs disable ESP logging and provide error/config declarations only;
matrix methods and arithmetic are the real selected library. ASan must catch
the original leak and accept the generated correction. No managed file changes.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
    out = (args.output or ROOT / 'agents/video-throughput' / ('matrix-lifetime-' + stamp)).resolve()
    out.mkdir(parents=True, exist_ok=False)
    dsp = ROOT / 'vdp/managed_components/espressif__esp-dsp'
    source = dsp / 'modules/matrix/mat/mat.cpp'
    original = source.read_bytes()
    stubs = out / 'stubs'
    stubs.mkdir()
    (stubs / 'esp_log.h').write_text('#pragma once\n' + ''.join(
        f'#define ESP_LOG{x}(...) ((void)0)\n' for x in 'DWE'))
    (stubs / 'esp_err.h').write_text('#pragma once\ntypedef int esp_err_t;\n#define ESP_OK 0\n#define ESP_FAIL -1\n')
    (stubs / 'sdkconfig.h').write_text('#pragma once\n')
    recipe = ROOT / 'vdp/pio/dsp_matrix_lifetime.cmake'

    def generate(input_path, output_path):
        return subprocess.run(['cmake', f'-DDSP_SOURCE={input_path}',
                               f'-DDSP_OUTPUT={output_path}', '-P', str(recipe)],
                              capture_output=True, text=True)

    generated = out / 'mat.cpp'
    result = generate(source, generated)
    (out / 'generate.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stderr
    altered = out / 'unknown-source.cpp'
    altered.write_bytes(original + b'\n// unreviewed dependency\n')
    rejected = generate(altered, out / 'must-not-exist.cpp')
    assert rejected.returncode != 0 and not (out / 'must-not-exist.cpp').exists()

    includes = [str(p) for p in dsp.rglob('include') if p.is_dir()]
    base = ['g++', '-std=c++17', '-g', '-O1', '-fsanitize=address',
            '-fno-omit-frame-pointer', '-ffunction-sections', '-fdata-sections',
            '-Wl,--gc-sections', '-I', str(stubs)]
    base += [item for p in includes for item in ('-I', p)]
    results = {}
    for label, selected in [('baseline', source), ('corrected', generated)]:
        command = base + [str(selected), str(ROOT / 'tests/dsp_matrix_lifetime_test.cpp'), '-o', str(out / label)]
        with (out / (label + '-build.log')).open('w') as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
        env = dict(os.environ, ASAN_OPTIONS='detect_leaks=1:exitcode=23')
        run = subprocess.run([str(out / label)], env=env, capture_output=True, text=True)
        (out / (label + '.log')).write_text(run.stdout + run.stderr)
        results[label] = {'exit': run.returncode, 'source_sha256': hashlib.sha256(selected.read_bytes()).hexdigest()}
        if label == 'baseline':
            assert run.returncode == 23 and 'LeakSanitizer: detected memory leaks' in run.stderr, run.stderr
        else:
            assert run.returncode == 0 and 'checks passed' in run.stdout, run.stderr
    assert source.read_bytes() == original, 'Managed dependency was modified'
    results['unknown_dependency_rejected'] = True
    results['managed_source_unchanged'] = True
    (out / 'result.json').write_text(json.dumps(results, indent=2) + '\n')
    print('Original leak reproduced; corrected arithmetic/lifetimes pass; unknown source refused:', out)


if __name__ == '__main__':
    main()
