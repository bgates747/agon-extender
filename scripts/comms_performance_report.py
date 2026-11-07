#!/usr/bin/env python3
"""Analyse dedicated COMMS-002 matched samples, never accuracy/soak logs."""
import argparse
import json
import math
from pathlib import Path
import re
import statistics

SCOPES = {'source_lifetime', 'transfer', 'setup', 'turnaround', 'vdp_execution',
          'complete_workload', 'ez80_busy', 'ez80_useful_work'}
IDENTITY = ('workload_sha256', 'renderer_sha256', 'logical_configuration_sha256',
            'ez80_hz', 'p4_hz', 'iterations', 'bytes_per_iteration', 'clock_hz', 'timer_bits')


def positive_int(value):
    return type(value) is int and value > 0


def interval(start, end, bits, upper):
    if (not all(type(v) is int for v in (start, end, bits, upper)) or not 8 <= bits <= 32
            or not 0 < upper < (1 << (bits - 1)) or not 0 <= start < (1 << bits)
            or not 0 <= end < (1 << bits)):
        raise ValueError('Invalid timer range/independent upper bound')
    result = (end - start) & ((1 << bits) - 1)
    if not 0 < result <= upper:
        raise ValueError('Zero/sub-tick or out-of-bound interval; batch more work')
    return result


def percentile(values, fraction):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * fraction) - 1)]


def analyse(rows):
    if not rows:
        raise ValueError('No performance samples')
    pairs = {}
    for row in rows:
        if row.get('schema') != 'comms-performance-sample-r01':
            raise ValueError('Dedicated performance sample required')
        if row.get('passed') is not True:
            raise ValueError('Failed/incomplete sample retained; cohort has no clean speed verdict')
        if row.get('arm') not in ('uart1', 'parallel') or row.get('scope') not in SCOPES:
            raise ValueError('Unknown arm/scope')
        for field in ('pair', 'case', 'observer', 'clock'):
            if not isinstance(row.get(field), str) or not row[field] or len(row[field]) > 100:
                raise ValueError('Missing bounded sample identity: ' + field)
        for field in IDENTITY[:3]:
            if not isinstance(row.get(field), str) or not re.fullmatch('[0-9a-f]{64}', row[field]):
                raise ValueError('Missing matched hash: ' + field)
        for field in ('ez80_hz', 'p4_hz', 'iterations', 'clock_hz'):
            if not positive_int(row.get(field)):
                raise ValueError('Invalid nominal rate/iteration count')
        if type(row.get('bytes_per_iteration')) is not int or row['bytes_per_iteration'] < 0:
            raise ValueError('Invalid logical byte count')
        counts = interval(row['start'], row['end'], row['timer_bits'], row['upper_bound_counts'])
        key = tuple(row[field] for field in ('case', 'scope', 'observer', 'clock', 'pair'))
        arms = pairs.setdefault(key, {})
        if row['arm'] in arms:
            raise ValueError('Duplicate arm in matched pair')
        arms[row['arm']] = (row, counts * 1000 / row['clock_hz'])
    groups = {}
    for key, arms in pairs.items():
        if set(arms) != {'uart1', 'parallel'}:
            raise ValueError('Unmatched pair: ' + repr(key))
        a, b = arms['uart1'], arms['parallel']
        identity = tuple(a[0][field] for field in IDENTITY)
        if identity != tuple(b[0][field] for field in IDENTITY):
            raise ValueError('Workload/renderer/configuration/clock mismatch')
        group = groups.setdefault(key[:-1], dict(identity=identity, uart1=[], parallel=[], paired_reduction=[]))
        if group['identity'] != identity:
            raise ValueError('Same case label hides different matched workloads')
        group['uart1'].append(a[1])
        group['parallel'].append(b[1])
        group['paired_reduction'].append((a[1] - b[1]) / a[1] * 100)
    result = []
    for key, group in groups.items():
        a, b = group['uart1'], group['parallel']
        baseline, candidate = statistics.median(a), statistics.median(b)
        row = dict(zip(('case', 'scope', 'observer', 'clock'), key))
        row.update(pairs=len(a), unit='ms per matched batch',
                   uart1_median_ms=baseline, parallel_median_ms=candidate,
                   elapsed_reduction_percent=(baseline - candidate) / baseline * 100,
                   paired_reduction_median_percent=statistics.median(group['paired_reduction']),
                   uart1_p95_ms=percentile(a, .95), parallel_p95_ms=percentile(b, .95),
                   uart1_max_ms=max(a), parallel_max_ms=max(b),
                   iterations=group['identity'][5], bytes_per_iteration=group['identity'][6],
                   timing='nominal endpoint-local clock; no optical/external calibration')
        if key[1] == 'ez80_useful_work':
            # Elapsed reduction alone does not describe useful-work throughput.
            row['interpretation'] = 'Duration of the same counted work; not a CPU utilisation percentage'
        result.append(row)
    return dict(schema='comms-performance-report-r01', passed=True,
                baseline='uart1', cpu_utilisation_percent=None,
                scopes_summed=False, rows=sorted(result, key=lambda x: -x['uart1_median_ms']))


def read_samples(path):
    rows = []
    with Path(path).open() as file:
        while True:
            line = file.readline(8193)
            if not line:
                break
            if len(line) > 8192 or not line.endswith('\n'):
                raise ValueError('Oversized or interrupted sample record')
            rows.append(json.loads(line))
            if len(rows) > 100000:
                raise ValueError('Sample count bound')
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('samples')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    result = analyse(read_samples(args.samples))
    with Path(args.output).open('x') as file:
        json.dump(result, file, indent=2, allow_nan=False)
        file.write('\n')
    print('| Case / scope | UART1 median ms | Parallel median ms | Reduction from UART1 % | Pairs |')
    print('|---|---:|---:|---:|---:|')
    for row in result['rows']:
        print(f"| {row['case']} / {row['scope']} | {row['uart1_median_ms']:.3f} | "
              f"{row['parallel_median_ms']:.3f} | {row['elapsed_reduction_percent']:.2f} | {row['pairs']} |")


if __name__ == '__main__':
    main()
