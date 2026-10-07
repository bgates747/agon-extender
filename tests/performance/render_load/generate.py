#!/usr/bin/env python3
"""Render-load-r04 deterministic payloads. Mode changes belong to autoexec only."""
import argparse, hashlib, json, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CONTRACT=json.loads((ROOT/'contract.json').read_text())
MODES={20:(512,384,64,False),8:(320,240,64,False),136:(320,240,64,True),21:(512,384,16,False),149:(512,384,16,True)}
def u16(n): return struct.pack('<H',n&65535)
def cmd(*xs): return bytes(xs)
def plot(op,x,y): return cmd(25,op)+u16(x)+u16(y)
def colour(n): return cmd(18,0,n)
def bitmap(i,x,y): return cmd(23,27,0,i,23,27,3)+u16(x)+u16(y)
def asset(i,w,h,pixels):
    b=64000+i
    return cmd(23,0,160)+u16(b)+cmd(2)+cmd(23,0,160)+u16(b)+cmd(0)+u16(len(pixels))+pixels+cmd(23,27,0,i,23,27,33)+u16(w)+u16(h)+cmd(1)
def assets():
    out=b''
    for i,size in ((0,16),(1,32),(2,16)):
        pix=bytes((0 if i==2 and ((x-7)**2+(y-7)**2)>49 else 192|((x//4+y//4)%4)*21) for y in range(size) for x in range(size))
        out+=asset(i,size,size,pix)
    for f in range(40):
        bits=[1,0]+[(f>>i)&1 for i in range(8)]+[((f^255)>>i)&1 for i in range(8)]+[0,1]
        out+=asset(8+f,20,4,bytes(255 if bit else 192 for _ in range(4) for bit in bits))
    return out

def point(i,f,w,h):
    # Local bounded movement in a stable grid; a fixed seed permutes colours.
    cols=w//32
    return (i%cols)*32+(f*3+i*5+CONTRACT['seed'])%16,8+(i//cols)*32+(f*2+i*3)%16

def sprite_setup(count,hardware):
    out=cmd(23,27,7,0,23,27,17,23,0,248,2,0,1,0)
    # VDP2.16's kind/paint APIs affect only the selected sprite. Attach its
    # RGBA frame first, then explicitly establish both properties for EVERY
    # active sprite; reset defaults and earlier applications are insufficient.
    for i in range(count): out+=cmd(23,27,4,i,23,27,5,23,27,6,2,23,27,18,0,23,27,19 if hardware else 20,23,27,11)
    return out+cmd(23,27,7,count)

def frame(family,variant,level,f,w,h,cols,db,marker=True):
    out=b''
    if family=='fills':
        d={1:8,4:4,16:2,64:1}[level]
        out=colour(1+f%(cols-1))+plot(4,0,8)+plot(101,w//d-1,8+(h-8)//d-1)
    elif family in ('primitives','bitmaps','mixed'):
        for i in range(level):
            x,y=point(i,f,w,h); c=1+(i*7+f)%(cols-1)
            kind=variant if family=='primitives' else ('bitmap' if family=='bitmaps' else ('lines','circles','bitmap','sprite')[i%4])
            if kind=='lines': out+=colour(c)+plot(4,x,y)+plot(5,x+15,y+15)
            elif kind=='circles': out+=colour(c)+plot(4,x+8,y+8)+plot(149,x+15,y+8)
            elif kind=='bitmap': out+=bitmap(int(variant=='32'),x,y)
            else: out+=cmd(23,27,4,i//4,23,27,13)+u16(x)+u16(y)
        if family=='mixed': out+=cmd(23,27,15)
    elif family in ('sprites','overlap'):
        count=64 if family=='overlap' else level
        for i in range(count):
            j=i//level if family=='overlap' else i
            x,y=point(j,f,w,h)
            if family=='overlap': x+=i%level%3; y+=i%level%3
            out+=cmd(23,27,4,i,23,27,13)+u16(x)+u16(y)
        out+=cmd(23,27,15)
    elif family=='text_scroll':
        out+=cmd(31,0,1)+bytes(65+(i+f)%26 for i in range(level))
        out+=cmd(23,7,0,3,1)*level
    if marker: out+=bitmap(8+f,0,0)
    if db: out+=cmd(23,0,195)
    return out

def cases():
    n=0
    for family in CONTRACT['workloads']:
        for variant in family['variants']:
            for level in family.get('levels',CONTRACT['levels']):
                for style in CONTRACT['styles']:
                    yield dict(id=n,family=family['family'],variant=variant,level=level,style=style,timing=True,marker=True)
                    n+=1
    for control in CONTRACT['controls']:
        for style in CONTRACT['styles']:
            yield dict(id=n,family='static',variant=control,level=0,style=style,timing=False,marker=control=='marker_no_timing'); n+=1

def generate(output):
    output.mkdir(parents=True,exist_ok=True)
    manifest={'identity':'render-load-r04','contract_sha256':hashlib.sha256((ROOT/'contract-r04.json').read_bytes()).hexdigest(),'modes':{}}
    for mode,(w,h,col,db) in MODES.items():
        a=assets(); entries=[]; data=b'B9D1'+bytes((mode,))+u16(w)+u16(h)+bytes((col,db))+u16(len(a))+a
        for c in cases():
            # Deactivate before clearing frame lists; resetSprites itself queues
            # a hide refresh before clearing frames in the upstream lifecycle.
            setup=cmd(23,27,7,0,23,27,17,20,26,23,0,192,0,18,0,0,12,16,23,1,0)
            if db: setup+=cmd(23,0,195,12,16,23,0,195)
            # Text viewport starts below the reserved marker band.
            setup+=cmd(28,0,h//8-1,w//8-1,1)
            if c['family'] in ('sprites','overlap','mixed'):
                count=64 if c['family']=='overlap' else (c['level']//4 if c['family']=='mixed' else c['level'])
                setup+=sprite_setup(count,c['variant']=='hardware')
            payload=u16(c['id'])+bytes((int(c['style']=='paced'),int(c['timing'])|int(c['marker'])<<1))+u16(len(setup))+setup
            frames=[frame(c['family'],c['variant'],c['level'],f,w,h,col,db,c['marker']) for f in range(40)]
            payload+=b''.join(u16(len(fr))+fr for fr in frames)
            assert len(payload)<=CONTRACT['payload_limit_bytes']
            entries.append(c|{'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest(),'frame_bytes':[len(x) for x in frames]})
            data+=u16(len(payload))+payload
        data+=b'\0\0'
        name=f'data{mode}.bin'; (output/name).write_bytes(data)
        manifest['modes'][str(mode)]={'width':w,'height':h,'colours':col,'double_buffered':db,'file':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'cases':entries}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('output',type=Path); args=p.parse_args(); m=generate(args.output)
    print(json.dumps({k:(v['bytes'],len(v['cases'])) for k,v in m['modes'].items()}))
