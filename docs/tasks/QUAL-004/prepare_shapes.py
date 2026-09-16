from pathlib import Path
import argparse,hashlib,json
TASK=Path(__file__).resolve().parent;ROOT=TASK.parents[2]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=False)
b=ROOT/'docs/tasks/QUAL-003/suite/build';clean=(b/'bitmaps-cleanup.vdu').read_bytes()+b'\x0c';rows=[]
for f in sorted(b.glob('shp*.vdu')):
 if f.stem in ('shp20','shp23'):continue
 data=clean+f.read_bytes();name=f.stem.upper();(out/(name+'.vdu')).write_bytes(data)
 rows.append(dict(name=name,file=name+'.vdu',bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),source_sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
(out/'manifest.json').write_text(json.dumps(dict(cases=rows),indent=2)+'\n');print(len(rows),sum(x['bytes'] for x in rows))
