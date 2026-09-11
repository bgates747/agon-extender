#!/usr/bin/env python3
"""Offline attribution of a completed timing capture; never contacts hardware."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import statistics


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def analyze(capture, output):
    checks = json.loads((capture/'checksums.json').read_text())
    for name, expected in checks.items():
        assert sha(capture/name) == expected, ('capture checksum', name)
    binding = json.loads((capture/'binding.json').read_text())
    for item in binding['binding_files']:
        assert sha(Path(item['path'])) == item['sha256'], ('binding', item['path'])
    raw = (capture/'records.jsonl').read_bytes()
    rows = [json.loads(line) for line in raw.splitlines()]
    assert rows[0]['kind'] == 'start' and rows[-1]['kind'] == 'end'
    samples = [r for r in rows if r['kind'] == 'sample']
    markers = [r for r in rows if r['kind'] == 'operator_marker']
    assert len(samples) == rows[-1]['samples'] and len(markers) == rows[-1]['markers']
    decoded = [(r, json.loads(r['body'])) for r in samples if r.get('valid')]
    assert len(samples)-len(decoded) == rows[-1]['failed_requests']
    good = [(r, b) for r, b in decoded if b['totals_valid']]
    first, last = good[0][1], good[-1][1]
    by = lambda b: {p['name']: p for p in b['phases']}
    # This observed run has neither wrap nor reset. Refuse to silently process
    # a different run with a discontinuity using these simple subtractions.
    assert all(a[1]['now_us'] <= b[1]['now_us'] for a, b in zip(decoded, decoded[1:]))
    for a, b in zip(good, good[1:]):
        for name, p in by(a[1]).items():
            assert all(by(b[1])[name][k] >= p[k] for k in ('count', 'total_us', 'units'))
    events = {tuple(e[k] for k in ('phase', 'start_us', 'duration_us', 'context', 'units')): e
              for _, b in good for e in b['history']}
    long_drains = sorted((e for e in events.values()
                          if e['phase'] == 'queue' and e['duration_us'] >= 1000000),
                         key=lambda e: e['start_us'])
    longest = max(long_drains, key=lambda e: e['duration_us'])
    inside = [(r, b) for r, b in good if by(b)['queue']['active']['state'] == 2
              and by(b)['queue']['active']['consistent']
              and by(b)['queue']['active']['start_us'] == longest['start_us']]
    assert len(inside) >= 2
    left, right = by(inside[0][1]), by(inside[-1][1])
    progress = {name: {k: right[name][k]-left[name][k] for k in ('count', 'units')}
                for name in left}
    phases = {}
    for name, p in by(last).items():
        phases[name] = {'delta': {k: p[k]-by(first)[name][k] for k in ('count', 'total_us', 'units')},
                        'maximum_completed_us': p['max_us'], 'maximum_started_us': p['max_at_us'],
                        'maximum_context': p['max_context'],
                        'maximum_observed_active_age_us': max(by(b)[name]['active']['age_us']
                            for _, b in decoded if by(b)[name]['active']['consistent']),
                        'last_active': p['active']}
    brackets = []
    for i, marker in enumerate(markers, 1):
        before = [x for x in decoded if x[0]['host_monotonic_ns'] <= marker['host_monotonic_ns']]
        after = [x for x in decoded if x[0]['host_monotonic_ns'] >= marker['host_monotonic_ns']]
        entries = []
        for side, pair in (('before', before[-1] if before else None),
                           ('after', after[0] if after else None)):
            if pair is None: continue
            r, b = pair
            entries.append({'side': side, 'host_at': r['host_at'], 'now_us': b['now_us'],
                            'marker_offset_ms': (r['host_monotonic_ns']-marker['host_monotonic_ns'])/1e6,
                            'totals_valid': b['totals_valid'],
                            'queue_active': by(b)['queue']['active'],
                            'snapshot_count': by(b)['snapshot']['count'] if b['totals_valid'] else None})
        brackets.append({'index': i, 'host_at': marker['host_at'], 'note': marker['note'], 'brackets': entries})
    summary = {
        'run_id': rows[0]['run_id'], 'build_id': binding['build_id'],
        'factory_sha256': binding['factory_sha256'], 'emos_build': binding['emos_build'],
        'nurples_sha256': binding['nurples_sha256'],
        'raw_sha256': checks['records.jsonl'], 'private_binding_sha256': checks['binding.json'],
        'first_sample_at': decoded[0][0]['host_at'], 'last_sample_at': decoded[-1][0]['host_at'],
        'end': rows[-1], 'valid_aggregate_samples': len(good),
        'http_median_ms': statistics.median(r['request_duration_ns']/1e6 for r in samples),
        'http_max_ms': max(r['request_duration_ns']/1e6 for r in samples),
        'monotonic_time_and_totals': True,
        'loss': {'completion_records_before': first['lost_completions'],
                 'completion_records_after': last['lost_completions'],
                 'overlapping_calls': last['overlapping_calls'],
                 'busy_reads': last['busy_reads'],
                 'history_overwritten': last['history_overwritten'],
                 'inconsistent_live_observations': sum(not p['active']['consistent']
                     for _, b in decoded for p in b['phases'])},
        'phases': phases, 'completed_drains_over_one_second': long_drains,
        'longest_drain_observed_interior': {'first_host_at': inside[0][0]['host_at'],
            'last_host_at': inside[-1][0]['host_at'], 'valid_samples': len(inside),
            'duration_us': inside[-1][1]['now_us']-inside[0][1]['now_us'], 'progress': progress},
        'markers': brackets,
    }
    output.mkdir(parents=True, exist_ok=False)
    (output/'records.jsonl.gz').write_bytes(gzip.compress(raw, mtime=0))
    assert gzip.decompress((output/'records.jsonl.gz').read_bytes()) == raw
    summary['compressed_raw_sha256'] = sha(output/'records.jsonl.gz')
    (output/'analysis.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(f'Validated {len(samples)} samples and {len(markers)} markers; longest drain {longest["duration_us"]/1e6:.6f} s.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    analyze(args.capture, args.output)
