#!/usr/bin/env python3
"""Build an offline interactive review of already analysed rendering measurements.

This tool reads local analysis only. It cannot invoke fixtures or contact a bench.
Paired passes stay paired; absent/failing measurements are never replaced by zero.
"""
import argparse
import datetime
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path(__file__).with_name('render_load_web')
MODES = {20: (512, 384, 64, False), 8: (320, 240, 64, False),
         136: (320, 240, 64, True), 21: (512, 384, 16, False),
         149: (512, 384, 16, True)}
INPUTS = ('comparison.json', 'cases.json', 'coverage.json', 'execution-audit.json',
          'zero-submissions.json', 'excluded.json')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_payload(analysis):
    """Keep matched comparisons and matching raw-derived run references together."""
    objects, hashes = {}, {}
    snapshot = analysis / 'pause-manifest.json'
    expected = json.loads(snapshot.read_text())['analysis_files_sha256'] if snapshot.exists() else {}
    for name in INPUTS:
        data = (analysis / name).read_bytes()
        hashes[name] = digest(data)
        if expected and hashes[name] != expected.get(name):
            raise ValueError(f'Snapshot hash mismatch: {name}')
        objects[name] = json.loads(data)
    audit = objects['execution-audit.json']
    if not audit['raw_provenance_complete']:
        raise ValueError('Raw provenance audit has unresolved issues')
    contract = json.loads((ROOT / 'tests/performance/render_load/contract-r04.json').read_text())
    if objects['coverage.json']['suite'] != contract['identity'] or audit['suite'] != contract['identity']:
        raise ValueError('Analysis does not describe the frozen r04 suite')
    allowed = {w['family']: w['variants'] for w in contract['workloads']}
    rows, seen = [], set()
    for original in objects['comparison.json']:
        row = dict(original)
        key = row['mode'], row['case']
        if key in seen:
            raise ValueError(f'Duplicate paired comparison: {key}')
        seen.add(key)
        if row['mode'] not in MODES or row['style'] not in ('paced', 'throughput'):
            raise ValueError(f'Unsupported comparison scope: {key}')
        if row['family'] not in allowed or row['variant'] not in allowed[row['family']]:
            raise ValueError(f'Unknown workload: {key}')
        for field in ('mainboard_completion_median_ms', 'p4_completion_median_ms',
                      'mainboard_p95_ms', 'p4_p95_ms'):
            if not isinstance(row[field], (int, float)) or not math.isfinite(row[field]) or row[field] <= 0:
                raise ValueError(f'Invalid completion time: {key} {field}')
        passes = row['paired_passes']
        if not passes or sorted(set(passes)) != passes or not set(passes) <= {1, 2, 3}:
            raise ValueError(f'Invalid paired passes: {key}')
        references = {}
        for endpoint in ('mainboard', 'p4'):
            found = [r for r in objects['cases.json'] if
                     (r['mode'], r['case'], r['endpoint'], r['output']) ==
                     (row['mode'], row['case'], endpoint, 'normal') and
                     r['pass'] in passes and r['timing_enabled'] and not r['disable_timing']]
            if sorted(r['pass'] for r in found) != passes:
                raise ValueError(f'Missing or duplicate matching run reference: {key} {endpoint}')
            references[endpoint] = [r['run'] for r in sorted(found, key=lambda r: r['pass'])]
        row['runs'] = references
        rows.append(row)
    summaries = {k: audit[k] for k in ('expected_case_executions', 'executions_accounted',
                 'valid_measurements', 'failed_or_invalid_executions', 'execution_coverage_complete',
                 'raw_provenance_complete')}
    return dict(rows=rows, modes={str(k): dict(width=v[0], height=v[1], colours=v[2],
                double_buffered=v[3]) for k, v in MODES.items()},
                level_meanings={w['family']: w.get('level_meaning', 'static control')
                                for w in contract['workloads']},
                levels=contract['levels'], audit=summaries, coverage=objects['coverage.json'],
                zero_submission_windows=len(objects['zero-submissions.json']),
                exclusions=len(objects['excluded.json']), source_hashes=hashes,
                snapshot_hashes_verified=bool(expected), source_label=analysis.name,
                contract=contract['identity'])


def build_page(analysis, output):
    import plotly
    from plotly.offline import get_plotlyjs
    payload = load_payload(analysis)
    output = output.resolve()
    if output.is_relative_to(analysis.resolve()):
        raise ValueError('Keep the generated page outside the retained analysis snapshot')
    provenance = output.with_suffix('.provenance.json')
    if output.exists() or provenance.exists():
        raise FileExistsError('Choose a new output path; existing pages are preserved')
    runtime = get_plotlyjs()
    sources = {p.name: digest(p.read_bytes()) for p in ASSETS.iterdir() if p.is_file()}
    generated = datetime.datetime.now(datetime.timezone.utc).isoformat()
    payload['generated_utc'] = generated
    text = (ASSETS / 'index.html').read_text()
    # Escaped '<' prevents embedded source data from closing the JSON script tag.
    replacements = {'__STYLE__': (ASSETS / 'style.css').read_text(),
                    '__PLOTLY__': runtime,
                    '__DATA__': json.dumps(payload, allow_nan=False).replace('<', '\\u003c'),
                    '__APP__': (ASSETS / 'app.js').read_text()}
    for token, value in replacements.items():
        text = text.replace(token, value)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text)
    receipt = dict(generated_utc=generated, html_sha256=digest(text.encode()),
                   generator_sha256=digest(Path(__file__).read_bytes()),
                   template_sha256=sources, input_sha256=payload['source_hashes'],
                   plotly_python_version=plotly.__version__, plotly_js_sha256=digest(runtime.encode()),
                   paired_comparisons=len(payload['rows']), snapshot_hashes_verified=payload['snapshot_hashes_verified'],
                   execution_audit=payload['audit'], scope='Offline review; no bench operations')
    provenance.write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--analysis', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='New standalone HTML file')
    args = parser.parse_args()
    result = build_page(args.analysis, args.output)
    print(json.dumps(dict(output=str(args.output.resolve()), paired_comparisons=result['paired_comparisons'],
                          html_sha256=result['html_sha256'])))


if __name__ == '__main__':
    main()
