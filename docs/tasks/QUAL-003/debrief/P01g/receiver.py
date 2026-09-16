"""Wired diagnostic receiver; validates every LDR1 byte without rendering."""
import argparse,asyncio,json,struct,time,zlib
from pathlib import Path

def validate(data,nonce,previous):
 assert len(data)>=32 and data[:4]==b'LDR1'
 version=struct.unpack_from('<I',data,4)[0]
 seq,size,timestamp,crc=struct.unpack_from('<IIII',data,16)
 assert version==1 and data[8:16]==nonce and seq==previous+1
 assert 0<size<=196608 and size%12288==0 and len(data)==32+size
 payload=data[32:];assert zlib.crc32(payload)==crc
 assert payload==bytes(range(256))*(size//256)
 return seq,size,timestamp

async def run(a):
 import websockets
 out=Path(a.output);out.mkdir(exist_ok=True,parents=True)
 rows=[];error=None;began=time.monotonic();previous=0;ignored=0
 try:
  async with websockets.connect(a.url,max_size=1000000,compression=None,ping_interval=None,max_queue=1) as ws:
   await ws.send('frame');(out/'ready.json').write_text(json.dumps({'connected':True})+'\n')
   while time.monotonic()-began<a.seconds and not (out/'stop').exists():
    try:data=await asyncio.wait_for(ws.recv(),timeout=0.5)
    except asyncio.TimeoutError:continue
    now=time.monotonic()
    if data[:4]==b'LDR1':
     previous,size,timestamp=validate(data,bytes.fromhex(a.nonce),previous)
     rows.append({'sequence':previous,'bytes':size,'received_s':now-began,'sender_us':timestamp})
    else:
     assert data[:3]==b'EVF',data[:32];ignored+=1
    await ws.send('frame')
 except Exception as e:error=repr(e)
 result={'rows':rows,'error':error,'ignored_normal_frames':ignored,'duration_s':time.monotonic()-began,'receiver':'wired Python; no presentation','validation':'all payload bytes, CRC32, nonce, consecutive send IDs'}
 (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 if error:raise RuntimeError(error)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--nonce',required=True);p.add_argument('--output',required=True);p.add_argument('--seconds',type=float,default=180);a=p.parse_args();asyncio.run(run(a))
