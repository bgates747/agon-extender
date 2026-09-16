"""Supplement whole-image parity with retained independent literal pixel oracles.

No resizing/cropping is permitted here. An ideal-oracle failure is reported
separately even when stock and P4 agree with each other.
"""
from pathlib import Path
import argparse, json, runpy
from PIL import Image

TASK=Path(__file__).resolve().parent;ROOT=TASK.parents[2]
check=runpy.run_path(str(ROOT/'docs/tasks/PORT-008/bitmap-coverage/check_pixels.py'))['check']

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--scenes',type=Path,required=True)
 p.add_argument('--runs',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True)
 a=p.parse_args();results=[]
 for manifest in sorted(a.scenes.glob('mode*/manifest.json')):
  mode=int(manifest.parent.name[4:])
  for scene in json.loads(manifest.read_text())['cases']:
   name=scene['name'];images=a.runs/f'mode{mode}-run01'/name/'images'
   for device in ('mainboard','p4'):
    image=images/(device+'.png')
    if not image.exists():
     results.append(dict(case=name,device=device,status='not captured'));continue
    with Image.open(image) as pixels:
     assert pixels.size==(320,240),'No resizing of literal oracle'
     if name.startswith('PAGE_'):
      bg=tuple(scene['expected_background_rgb']);x1,y1,x2,y2=scene['expected_white_rectangle']
      mismatch=sum(pixels.getpixel((x,y))!=((255,255,255) if x1<=x<=x2 and y1<=y<=y2 else bg)
                   for y in range(240) for x in range(320))
      result=dict(passed=mismatch==0,mismatches=mismatch,pixels=76800)
     else:
      oracle=(manifest.parent/'oracle/oracle.json' if name.startswith('PAL') else
              manifest.parent/'copper-oracle'/(scene['stage']+'-oracle.json'))
      result=check(oracle,image)
      result.pop('oracle',None);result.pop('capture',None)
    results.append(dict(case=name,device=device,status='pass' if result['passed'] else 'ideal mismatch',result=result))
 a.output.write_text(json.dumps(results,indent=2)+'\n')
 print(json.dumps({s:sum(r['status']==s for r in results) for s in ('pass','ideal mismatch','not captured')}))

if __name__=='__main__':main()
