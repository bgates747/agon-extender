"""NET-001 bounded two-viewer hardware test; user authorizes displacement."""
from pathlib import Path
import sys,json,time,datetime
sys.path.insert(0,'scripts');from measure_video import OBSERVER
from playwright.sync_api import sync_playwright
import argparse
p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
r=a.output;r.mkdir(parents=True,exist_ok=False);start=time.monotonic();results=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader'])
  try:
   pages=[browser.new_page() for _ in range(2)]
   for p in pages:
    p.add_init_script(OBSERVER);p.goto(a.url,wait_until='domcontentloaded')
   for turn in range(6):
    current=pages[turn%2];previous=pages[(turn+1)%2]
    count=current.evaluate('__videoObservation.frames.length');oldcloses=previous.evaluate('__videoObservation.closes.length')
    current.click('#connect');current.wait_for_function(f'__videoObservation.frames.length > {count}',timeout=15000)
    if turn:
     previous.wait_for_function(f'__videoObservation.closes.length > {oldcloses}',timeout=10000)
     closed=previous.evaluate('__videoObservation.closes.slice(-1)[0]')
     assert closed['code']==1000 and closed['reason']=='Viewer replaced',closed
    else:closed=None
    current.wait_for_timeout(1000)
    frame=current.evaluate('__videoObservation.frames.slice(-1)[0]');assert frame['width']==320 and frame['height']==240 and frame['payload']==frame['height']*frame['stride'] and frame['bytes']==32+frame['payload'],frame
    results.append(dict(turn=turn,viewer='AB'[turn%2],previous_close=closed,frame=frame))
   pages[1].screenshot(path=str(r/'browser.png'))
   (r/'last.evf').write_bytes(bytes(pages[1].evaluate('Array.from(new Uint8Array(__videoObservation.last))')))
  finally:browser.close()
 (r/'result.json').write_text(json.dumps(dict(status='pass',handovers=5,connections=6,results=results,elapsed_seconds=time.monotonic()-start,ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')
 print('PASS: six connections, five replacements, explicit reconnect in both directions, valid320x240 frames',flush=True)
except Exception as e:
 (r/'result.json').write_text(json.dumps(dict(status='fail',error=str(e),results=results),indent=2)+'\n');raise
