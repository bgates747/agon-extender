#!/usr/bin/env python3
"""Fast, single-readback deployment of already generated render-load payloads."""
import argparse,hashlib,json,time,sys
from pathlib import Path
from render_load import Bench,ROOT
sys.path.insert(0,str(ROOT/'tests/performance/render_load'))
from packing import unpack_rle_stream

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--packed',type=Path,required=True);p.add_argument('--receipt',type=Path);a=p.parse_args()
 destination=a.receipt or a.evidence/'payload-deployment.json'
 if destination.exists():raise RuntimeError('Deployment receipt already exists; preserve it and choose a fresh receipt path')
 b=Bench(a.config,a.evidence);manifest=json.loads((a.packed/'manifest.json').read_text());t=time.monotonic();receipt=[]
 for mode in (20,8,136,21,149):
  name=f'data{mode}.rle';data=(a.packed/name).read_bytes();item=manifest[name]
  assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
  raw=unpack_rle_stream(data);assert len(raw)==item['decoded_bytes'] and hashlib.sha256(raw).hexdigest()==item['decoded_sha256']
  print(f'DEPLOY mode{mode}, {len(data)} packed bytes, {len(raw)} original bytes',flush=True)
  start=time.monotonic();b.fast_put_new(b.config['fixture_root']+'/'+name,data)
  receipt.append(dict(item,mode=mode,seconds=time.monotonic()-start,verification='one whole-file readback',transport='foreground fast EMOS SD listener'))
  destination.write_text(json.dumps({'total_seconds':time.monotonic()-t,'files':receipt},indent=2)+'\n')
  print(f'VERIFIED mode{mode}, {receipt[-1]["seconds"]:.1f} seconds',flush=True)
 print('Full five-mode deployment verified',flush=True)
if __name__=='__main__':main()
