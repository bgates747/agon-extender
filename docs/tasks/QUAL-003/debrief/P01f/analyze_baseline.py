from pathlib import Path
import json,re,gzip,hashlib,shutil
import argparse
p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);args=p.parse_args()
r=args.input;d=args.output;e=d/'evidence';e.mkdir(parents=True,exist_ok=True)
text=(r/'refresh-final.log').read_text(errors='replace');rows=[]
for n in sorted(r.glob('p01f-*-nonce.txt')):
 name=n.name[:-10];nonce=n.read_text().strip()
 t=json.loads((r/(name+'-trace.json')).read_text());o=json.loads((r/(name+'-output.json')).read_text());g=json.loads((r/(name+'-game.json')).read_text())[0]
 block=text.split('NPTRACE begin '+nonce+' ')[1].split('NPTRACE end '+nonce)[0]
 samples=[tuple(map(int,x)) for x in re.findall(r'NPTRACE row (\d+) (\d+) (\d+)',block)]
 values=sorted(((samples[i][2]-samples[i-1][2])&0xffffffff)/1000 for i in range(121,len(samples)))
 q=lambda p:values[(len(values)*p+99)//100-1]
 t['completion_intervals'].update(p50_ms=q(50),p99_ms=q(99))
 (e/(name+'-trace.json')).write_text(json.dumps(t,indent=2)+'\n')
 for suffix in ['game.json','output.json','duration.json','nonce.txt']:
  shutil.copy2(r/(name+'-'+suffix),e/(name+'-'+suffix))
 rows.append(dict(name=name,trace=t,output=o))
for p in r.glob('P1F*.BIN'):shutil.copy2(p,e/p.name)
with gzip.open(e/'trace.log.gz','wb') as f:f.write(('\n'.join(line for line in text.splitlines() if line.startswith(('NPTRACE ', 'NPOUT ')))+'\n').encode())
(e/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
(e/'sha256.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(e.iterdir()) if p.name!='sha256.json'},indent=2)+'\n')
for a in rows:
 t,o=a['trace'],a['output'];print(a['name'],round(t['completed_fps'],3),t['completion_intervals'],o['phases'])

for p in r.glob('p01f-*/result.json'):
 b=json.loads(p.read_text());assert not b['page_errors'] and not b['overflow']
 selected={k:b[k] for k in ['label','scope','seconds_requested','started_utc','observer_sha256','assets','browser_version','observed_wall_seconds','summary','page_errors','overflow']}
 (e/(p.parent.name+'-browser.json')).write_text(json.dumps(selected,indent=2)+'\n')
(e/'sha256.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(e.iterdir()) if p.name!='sha256.json'},indent=2)+'\n')
