#!/usr/bin/env python3
"""Build one immutable timestamped render-load-r04 MOS executable."""
import argparse,datetime,hashlib,json,shutil,subprocess
from pathlib import Path
from generate import cases
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--assembler',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 a.output.mkdir(parents=True,exist_ok=False)
 id='render-load-r04-b'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
 shutil.copyfile(ROOT/'benchmark-r04.asm',a.output/'benchmark.asm')
 labels=list(cases());text='label_table:\n'
 for i in range(0,len(labels),12):text+=' dl '+','.join('label'+str(c['id']) for c in labels[i:i+12])+'\n'
 for c in labels:
  name=f"{c['id']:02} {c['family'][:7]} {c['variant'][:3]} {c['level']} {c['style'][0].upper()}"
  text+=f'label{c["id"]}: db "{name}",0\n'
 (a.output/'labels.inc').write_text(text)
 (a.output/'identity.inc').write_text(f'db "{id}"\nds {106-len(id)}\n')
 subprocess.run([str(a.assembler.resolve()),'benchmark.asm',id+'.bin','-l','-s','-c'],cwd=a.output,check=True)
 assert (a.output/(id+'.bin')).stat().st_size<8192, 'code overlaps plan RAM'
 record={'build_id':id,'status':'experimental','binary':id+'.bin','binary_sha256':sha(a.output/(id+'.bin')),'source_sha256':sha(ROOT/'benchmark-r04.asm'),'labels_sha256':sha(a.output/'labels.inc'),'assembler_sha256':sha(a.assembler),'assembler_commit':'5dc733c286b7864e3eb05ef93462c7e1637ba51e','contract_sha256':sha(ROOT/'contract-r04.json')}
 (a.output/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
if __name__=='__main__':main()
