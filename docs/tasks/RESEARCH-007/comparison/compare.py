#!/usr/bin/env python3
"""Validate and compare collected local SCAN records; no bench access.

Timing comes from the existing records/window_results codecs. Publication,
scanout and application rates remain separate; this cannot grant visual/input
acceptance. Each collection's run.json must bind it to the verified P4 bytes.
"""
import argparse
import json
from pathlib import Path
import sys


def compare(root, plan_path, baseline, candidate):
    sys.path.insert(0, str(root/'tests/performance/scan'))
    from records import decode
    from window_results import analyse
    plan = json.loads(plan_path.read_text())
    result = {'scope': 'matched finite fixtures; visual/input acceptance separate',
              'campaign': plan['campaign'], 'clock': plan['clock'], 'variants': {}, 'deltas': []}
    for label, directory in (('baseline', baseline), ('candidate', candidate)):
        meta = json.loads((directory/'run.json').read_text())
        identity = plan['firmware'][label]
        app = next(s for s in identity['segments'] if s['path']=='agon_extender.bin')
        if (meta['installed_build_id'], meta['application_sha256']) != (identity['build_id'], app['sha256']):
            raise ValueError(label+' installed firmware identity does not match the campaign')
        windows = json.loads((directory/'windows.json').read_text())
        if windows['open'] or windows['overflow']:
            raise ValueError('open or overflowed windows: '+label)
        cases = {}
        for e in (e for e in plan['cases'] if e['variant']==label):
            raw = (directory/f't{e["case"]:02}.bin').read_bytes()
            d = decode(raw)
            wanted = (e['case'], e['frames'], e['frames'], e['warmup'], plan['fixture_build'], e['window_tag'])
            actual = (d['case'], d['count'], d['expected'], d['warmup'], d['build_id'], d['window_tag'])
            if actual != wanted or d['abort'] or any(r['flags']&11 for r in d['rows']):
                raise ValueError('incomplete/mismatched/faulted record: '+label+f'/T{e["case"]:02}')
            matching = [w for w in windows['windows'] if w['tag']==e['window_tag'] and w['id']==e['case']]
            if len(matching)!=1 or matching[0]['updates']<=0 or matching[0]['scanouts']<=0:
                raise ValueError('missing/nonunique/inactive HDMI window')
            cases[e['case']] = analyse(raw, matching[0])
        result['variants'][label] = {'firmware': meta, 'cases': cases}
    a = result['variants']['baseline']['cases']
    b = result['variants']['candidate']['cases']
    if set(a)!={3,7,8,9} or set(b)!=set(a):
        raise ValueError('require all four agreed cases')
    for case in a:
        if a[case]['trajectory_sha256'] != b[case]['trajectory_sha256']:
            raise ValueError(f'T{case:02}: deterministic workloads differ; timing comparison rejected')
        def delta(x, y, higher=False):
            return ((y-x) if higher else (x-y))*100/x if x else None
        metrics = {}
        for metric in ('active', 'complete', 'total', 'wait'):
            if metric not in a[case]:
                continue
            metrics[metric] = {kind+'_cost_reduction_percent': delta(a[case][metric][kind+'_counts'], b[case][metric][kind+'_counts'])
                               for kind in ('median', 'p95', 'max')}
        for metric in ('nominal_updates_per_second',):
            metrics[metric+'_increase_percent'] = delta(a[case][metric], b[case][metric], True)
        for metric in ('submissions_per_second', 'scanouts_per_second'):
            metrics[metric+'_increase_percent'] = delta(a[case]['p4'][metric], b[case]['p4'][metric], True)
        result['deltas'].append({'case':case, 'metrics':metrics})
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    value = compare(a.root.resolve(), a.plan, a.baseline, a.candidate)
    with a.output.open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')
    print('All four records, installed identities, tagged windows and deterministic trajectories match; comparison saved. Visual review remains separate.')


if __name__=='__main__':
    main()
