"""Physical encoder RPC checks; native browser decoding, no concurrent video client."""
from pathlib import Path
import argparse,json,urllib.request,urllib.error,time,io,hashlib,base64,statistics,math
from PIL import Image
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--corpus',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--modes',default='80,90,95');a=p.parse_args();a.out.mkdir(exist_ok=True);rows=json.loads((a.out/'results.json').read_text()) if (a.out/'results.json').exists() else [];started=time.time()
manifest=json.loads((a.corpus/'manifest.json').read_text())
# 8x8 solid blocks separately expose channel ordering without edge-loss confounding.
manifest.append(dict(name='primary-patches',width=64,height=64))
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader']);page=b.new_page();page.goto(a.url)
 for item in manifest:
  name=item['name'];w=item['width'];h=item['height']
  if name=='primary-patches':raw=bytes((x//8)+(y//8)*8 for y in range(64) for x in range(64))
  else:raw=(a.corpus/name/'raw.bin').read_bytes()
  im=Image.frombytes('L',(w,h),raw);w=(w+7)//8*8;h=(h+7)//8*8
  padded=Image.new('L',(w,h));padded.paste(im,(0,0));raw=padded.tobytes()
  expected=bytes(c for x in raw for c in ((x&3)*85,((x>>2)&3)*85,((x>>4)&3)*85))
  dest=a.out/name;dest.mkdir(exist_ok=True);Image.frombytes('RGB',(w,h),expected).save(dest/'reference.png')
  for mode in map(int,a.modes.split(',')):
   if any(x['case']==name and x['mode']==mode for x in rows):continue
   samples=[]
   for repeat in range(4):
    req=urllib.request.Request(a.url+f'/diagnostics/image?mode={mode}&w={w}&h={h}',data=raw,headers={'Content-Type':'application/octet-stream'})
    for attempt in range(2):
     try:
      with urllib.request.urlopen(req,timeout=30) as f:enc=f.read();samples.append(dict(convert_us=int(f.headers['X-Convert-Us']),encode_us=int(f.headers['X-Encode-Us'])))
      break
     except urllib.error.HTTPError as e:
      body=e.read().decode();record=dict(case=name,mode=mode,repeat=repeat,attempt=attempt,status=e.code,body=body)
      with (a.out/'request-errors.jsonl').open('a') as log:log.write(json.dumps(record)+'\n')
      if attempt or e.code!=400 or body!='Incomplete body':raise RuntimeError(record)
      time.sleep(.2)
   suffix='jpg' if mode>3 else 'png';(dest/f'{mode}.{suffix}').write_bytes(enc)
   result=page.evaluate('''async ({b64,type,w,h})=>{const data=Uint8Array.from(atob(b64),c=>c.charCodeAt(0)),t=performance.now();const bm=await createImageBitmap(new Blob([data],{type}),{colorSpaceConversion:'none',premultiplyAlpha:'none'});const ms=performance.now()-t;if(bm.width!==w||bm.height!==h)throw Error('geometry');let c=new OffscreenCanvas(w,h),x=c.getContext('2d');x.drawImage(bm,0,0);bm.close();let a=x.getImageData(0,0,w,h).data,r=new Uint8Array(w*h*3);for(let i=0,j=0;i<a.length;i+=4){r[j++]=a[i];r[j++]=a[i+1];r[j++]=a[i+2];}let s='';for(let i=0;i<r.length;i+=8192)s+=String.fromCharCode(...r.subarray(i,i+8192));return {ms,rgb:btoa(s)};}''',dict(b64=base64.b64encode(enc).decode(),type='image/jpeg' if mode>3 else 'image/png',w=w,h=h))
   decoded=base64.b64decode(result['rgb']);diff=[abs(x-y) for x,y in zip(expected,decoded)];mse=sum(x*x for x in diff)/len(diff)
   if mode<=3:assert expected==decoded,'PNG pixel mismatch'
   if name=='primary-patches' and mode>3:assert max(diff)<=6,('JPEG channel-order/solid colour check failed',mode,max(diff))
   Image.frombytes('RGB',(w,h),decoded).save(dest/f'{mode}-decoded.png')
   row=dict(case=name,mode=mode,width=w,height=h,input_sha256=hashlib.sha256(raw).hexdigest(),bytes=len(enc),sha256=hashlib.sha256(enc).hexdigest(),convert_ms=statistics.mean(x['convert_us'] for x in samples[1:])/1000,encode_ms=statistics.mean(x['encode_us'] for x in samples[1:])/1000,samples=samples,browser_decode_ms=result['ms'],mae=statistics.mean(diff),max_error=max(diff),psnr_db=10*math.log10(255**2/mse) if mse else None,exact=expected==decoded)
   rows.append(row);(a.out/'results.json').write_text(json.dumps(rows,indent=2));print(name,mode,row['encode_ms'],'ms',len(enc),'bytes',flush=True)
 b.close()
# Invalid dimensions, unsupported mode and illegal pixel; then healthy request.
checks=[]
for query,data in [('mode=90&w=513&h=8',bytes(4104)),('mode=90&w=8&h=8',bytes(63)),('mode=2&w=8&h=8',bytes(64)),('mode=90&w=8&h=8',bytes([255])*64)]:
 try:urllib.request.urlopen(urllib.request.Request(a.url+'/diagnostics/image?'+query,data=data),timeout=20);raise AssertionError('Malformed request accepted')
 except urllib.error.HTTPError as e:assert e.code==400;checks.append(dict(query=query,status=e.code))
with urllib.request.urlopen(urllib.request.Request(a.url+'/diagnostics/image?mode=90&w=8&h=8',data=bytes(64)),timeout=20) as f:assert f.read().startswith(b'\xff\xd8')
(a.out/'complete.json').write_text(json.dumps(dict(seconds=time.time()-started,checks=checks,healthy_after=True,cases=len(rows)),indent=2))
