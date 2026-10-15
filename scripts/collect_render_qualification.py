#!/usr/bin/env python3
"""Validate an operator-copied Agon card tree, entirely offline.

--card-root names the copied card root containing agents/extender/results.
Execution receipts and transient P4 sidecars remain in the host run directory.
This command neither accesses the bench nor displays a completion notification.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from qualification.render_modes import validate_records, sha, dump, utc
from scripts.run_render_qualification import validate_plan


def collect(run, card):
    read = lambda path: json.loads(path.read_text())
    plan = read(run/'plan.json')
    validate_plan(plan)
    if plan['collection']['package_plan'] not in plan['inputs']:
        raise ValueError('Frozen package plan must be hash-pinned')
    summary = read(run/'summary.json')
    if summary['state'] != 'awaiting_collection' or summary.get('park_returncode') != 0:
        raise ValueError('Require completed execution and verified collection handback')
    output = run/'collection'
    output.mkdir(exist_ok=False)
    controls = {}
    results = []
    package = read(Path(plan['collection']['package_plan']))
    # Prepare all validation products before replacing any execution receipts.
    for job in plan['jobs']:
        folder = run/job['id']
        receipt = read(folder/'receipt.json')
        binding = {k: job[k] for k in ('id','renderer','mode','case','repeat')}
        if any(receipt.get(k) != v for k,v in binding.items()):
            raise ValueError('Mismatched receipt: '+job['id'])
        if not receipt.get('collection_pending') or not receipt.get('bench_idle'):
            raise ValueError('Require pending, safely returned execution: '+job['id'])
        row=next(r for r in summary['jobs'] if r['id']==job['id'])
        if row['receipt_sha256']!=sha((folder/'receipt.json').read_bytes()):
            raise ValueError('Execution receipt changed: '+job['id'])
        for name in ('invocation.json','windows.json','before-display.json','after-display.json'):
            if receipt['sidecar_sha256'].get(name)!=sha((folder/name).read_bytes()):
                raise ValueError('Execution sidecar changed: '+job['id']+'/'+name)
        invocation = read(folder/'invocation.json')
        if invocation['job']['id'] != job['id'] or invocation['identity'] != receipt['identity']:
            raise ValueError('Invocation identity differs: '+job['id'])
        source = card/receipt['result_remote'].lstrip('/')
        spec = next(j for j in package['jobs'] if j['id']==job['id'])
        if invocation['job']!=spec or receipt['result_remote']!=spec['result']:
            raise ValueError('Frozen job or result path differs: '+job['id'])
        key = (job['mode'],job['case'],job['repeat'])
        raw=None
        report=None
        try:
            raw=source.read_bytes()
            report=validate_records(package,spec,raw,read(folder/'windows.json'),
                                    read(folder/'before-display.json'),read(folder/'after-display.json'))
            if job['renderer']=='rgb888':
                controls[key]=report['trajectory_sha256']
            elif controls.get(key)!=report['trajectory_sha256']:
                raise ValueError('Control failed or deterministic trajectories differ')
            receipt.update(validated=True,trajectory_sha256=report['trajectory_sha256'])
        except (ValueError,RuntimeError,OSError,KeyError) as error:
            receipt.update(validated=False,error=str(error))
        target = output/job['id']
        target.mkdir()
        (target/'execution-receipt.json').write_bytes((folder/'receipt.json').read_bytes())
        if raw is not None:
            (target/'records.bin').write_bytes(raw)
            receipt['raw_sha256']=sha(raw)
        if report is not None:dump(target/'summary.json',report)
        receipt.update(collection_pending=False,collected_utc=utc())
        dump(target/'receipt.json',receipt)
        results.append((folder,target))
    for folder,target in results:
        for name in ('records.bin','summary.json','receipt.json'):
            if (target/name).exists():(folder/name).write_bytes((target/name).read_bytes())
    passed=0
    for row in summary['jobs']:
        receipt=read(run/row['id']/'receipt.json')
        passed+=bool(receipt['validated'])
        row.update(state='passed' if receipt['validated'] else 'failed',
                   receipt_sha256=sha((run/row['id']/'receipt.json').read_bytes()))
        if receipt['renderer']=='indexed':
            row['matched_control_trajectory']=receipt['validated']
    summary.update(state='validated_awaiting_notification' if passed==len(results) else 'collected_with_errors_awaiting_notification',
                   passed=passed,failed=len(results)-passed,
                   pending_collection=0,collected_utc=utc())
    dump(run/'summary.json',summary)
    return len(results)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path)
    parser.add_argument('--card-root',type=Path,required=True)
    args=parser.parse_args()
    print('Processed',collect(args.run,args.card_root),'runs; bench untouched; notification pending')


if __name__=='__main__':
    main()
