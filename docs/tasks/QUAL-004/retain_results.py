"""Retain reproducible full-image evidence and generate a scoped case table.

Run only on stopped/completed cohorts. Never reinterpret unfinished acquisition
as a passing image comparison. Output must be new, so evidence is not overwritten.
"""
from pathlib import Path
import argparse, datetime, gzip, hashlib, json, shutil

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('runs',type=Path,nargs='+')
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    rows=[];inventory=[]
    for run in args.runs:
        for src in sorted(run.glob('*/run.json')):
            record=json.loads(src.read_text())
            if record['status']=='running':
                raise ValueError('Unfinished acquisition: '+str(src))
            name=record['case']['name'];dest=args.output/run.name/name
            dest.mkdir(parents=True)
            shutil.copy2(src,dest/'run.json')
            for image in (src.parent/'images').glob('*'):
                if image.suffix in ('.png','.json'):shutil.copy2(image,dest/image.name)
            captures=list(src.parent.glob('mainboard-*.serial'))
            captures+=sorted((src.parent/'web').glob('*.evf'))[-2:]
            for capture in captures:
                (dest/(capture.name+'.gz')).write_bytes(gzip.compress(capture.read_bytes(),mtime=0))
            rows.append((run.name,record))
    for f in sorted(args.output.rglob('*')):
        if f.is_file():inventory.append(dict(file=str(f.relative_to(args.output)),
            bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
    (args.output/'integrity.json').write_text(json.dumps(inventory,indent=2)+'\n')
    valid=[r for _,r in rows if 'comparison' in r]
    passed=sum(r['comparison']['match'] for r in valid)
    text=['# Whole-image comparison case table','', '## Executive summary','',
          f'{passed} exact matches among {len(valid)} completed device comparisons. '
          f'{len(rows)-len(valid)} other records have no valid paired comparison.', '',
          'Every comparison includes all pixels; repeat captures validate stability. '
          'Elapsed seconds cover setup, loading, extraction and host control. '
          'They are **not** rendering-operation times or frame-rate measurements.', '',
          '| Cohort | Case | Outcome | Different / total pixels | Procedure seconds |',
          '|---|---|---|---:|---:|']
    for cohort,r in sorted(rows,key=lambda x:(-x[1].get('comparison',{}).get('mismatches',-1),x[1]['start'])):
        c=r.get('comparison');difference=f"{c['mismatches']} / {c['pixels']}" if c else 'Not comparable'
        elapsed=f"{r['end']-r['start']:.3f}" if 'end' in r else 'Not recorded'
        link=f"{cohort}/{r['case']['name']}/run.json"
        text.append(f"| {cohort} | [{r['case']['name']}]({link}) | {r['status']} | {difference} | {elapsed} |")
    text+=['','## Evidence interpretation','',
           'Mainboard `.serial.gz` contains checksummed composed scanout rows. '
           'P4 `.evf.gz` contains the last two fresh web snapshot generations. '
           'PNGs are lossless decoded views; magenta in a difference image marks '
           'every unequal pixel. `integrity.json` hashes all retained evidence. '
           'Fixture and firmware identities belong to the parent results document.', '']
    (args.output/'TABLES.md').write_text('\n'.join(text))
    print(json.dumps(dict(cases=len(rows),paired=len(valid),passed=passed,
                         retained_bytes=sum(x['bytes'] for x in inventory))))

if __name__=='__main__':main()
