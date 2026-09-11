#!/usr/bin/env python3
"""Preload exact finite stage traffic, preserving page dependencies.

The existing VM actions are serialized as their audited vendored assembly APIs
serialize them. RAM preloading excludes all Agon SD reads from the interval;
asset uploads remain part of the original stage traffic and are counted apart
from native primitive execution. No mode commands or additional sprite refresh.
"""
from pathlib import Path
import hashlib,json,struct,subprocess,sys
TASK=Path(__file__).resolve().parents[2]; SUITE=TASK/'suite'; OUT=TASK/'timing/fixture'
def word(*v): return struct.pack('<'+'H'*len(v),*(x&65535 for x in v))
def buffer(n,op,data=b''):return bytes((23,0,160))+word(n)+bytes((op,))+data
def call(a):
    name=a['name']; n=a['a']; x=a['bc']; y=a['de']; ident=a['hl']; prefix=bytes((23,27))
    single={'vdu_sprite_clear_frames':5,'vdu_sprite_next_frame':8,'vdu_sprite_prev_frame':9,
            'vdu_sprite_show':11,'vdu_sprite_hide':12,'vdu_sprite_update':15,
            'vdu_sprite_bmp_reset':16,'vdu_sprite_reset':17,
            'ext_sprite_hardware':19,'ext_sprite_software':20}
    one={'vdu_sprite_select':4,'vdu_sprite_add_bmp':6,'vdu_sprite_activate':7,
         'vdu_sprite_select_frame':10,'vdu_sprite_set_gcol':18,'ext_sprite_replace8':21}
    if name in single:return prefix+bytes((single[name],))
    if name in one:return prefix+bytes((one[name],n&255))
    if name=='vdu_buff_select':return prefix+b'\x20'+word(ident)
    if name=='vdu_bmp_create':return prefix+b'\x21'+word(x,y)+bytes((n&255,))
    if name=='vdu_consolidate_buffer':return buffer(ident,14)
    if name=='vdu_sprite_add_buff':return prefix+b'\x26'+word(ident)
    if name=='ext_sprite_replace16':return prefix+b'\x35'+word(ident)
    if name.startswith('vdu_sprite_move_'):
        if name.endswith('168'):x>>=8;y>>=8
        return prefix+bytes((13 if '_abs' in name else 14,))+word(x,y)
    raise ValueError(name)
def main():
    subprocess.run(['make','all','check',f'PYTHON={sys.executable}'],cwd=SUITE,check=True)
    build=OUT/'build';media=OUT/'media';build.mkdir(exist_ok=True);media.mkdir(exist_ok=True)
    corpus=json.loads((SUITE/'build/bitmaps-catalog.json').read_text());assets={a['name']:a for a in corpus['assets']}
    inventory=json.loads((TASK/'curated-timing-cases.json').read_text())
    for name,digest in inventory['generator_sha256'].items():
        if hashlib.sha256((TASK/name).read_bytes()).hexdigest()!=digest:raise ValueError('Curated source changed: '+name)
    rows=[]
    def emit(name,group,data,probes,quiet=False,uploads=0,setup=b''):
        assert len(data)<196608,(name,len(data))
        rawprobes=b''.join(word(p['x'],p['y'])+bytes(p['expected']) for p in probes)
        (media/(name+'.DAT')).write_bytes(setup+data+rawprobes)
        rows.append(dict(name=name,group=group,bytes=len(data),setup_bytes=len(setup),probes=len(probes),quiet=quiet,upload_bytes=uploads,
                         sha256=hashlib.sha256(setup+data+rawprobes).hexdigest()))
    clean=(SUITE/'build/bitmaps-cleanup.vdu').read_bytes()+b'\x0c'
    emit('EMPTY',0,b'',[],setup=clean)
    for p in inventory['shapes_pages']:
        stem=f"shp{p['page']:02}";raw=(SUITE/'build'/f'{stem}.probes').read_bytes()
        # Existing shape probes are query7 + expected RGB3, like bitmap probes.
        assert len(raw)%10==0
        probes=[dict(x=int.from_bytes(raw[i+3:i+5],'little'),y=int.from_bytes(raw[i+5:i+7],'little'),expected=list(raw[i+7:i+10])) for i in range(0,len(raw),10)]
        emit(stem.upper(),p['page'],(SUITE/'build'/f'{stem}.vdu').read_bytes(),probes,setup=clean)
    chosen={p['page'] for p in inventory['bitmap_pages']}
    for p in corpus['pages']:
        if p['page'] not in chosen:continue
        for index,s in enumerate(p['stages']):
            data=bytearray();upload_bytes=0
            for a in s['actions']:
                if a['op']=='vdu':data+=bytes.fromhex(a['hex'])
                elif a['op']=='call':data+=call(a)
                else:
                    assert a['op']=='load' and a['mode']==0
                    asset=assets[a['asset']];raw=(SUITE/'tgt/assets/bitmaps'/asset['filename']).read_bytes()
                    assert len(raw)==asset['length'];n=a['ident'];upload_bytes+=len(raw)
                    data+=buffer(n,2)+buffer(n,0,word(len(raw))+raw)+buffer(n,14)
                    data+=bytes((23,27,32))+word(n)+bytes((23,27,33))+word(asset['width'],asset['height'])+bytes((asset['format'],))
            emit(s['name'].upper(),100+p['page'],bytes(data),s['probes'],s['quiet'],upload_bytes,clean if index==0 else b'')
    # Partial-width one-pixel scroll and clipped oversized bitmaps, fixed 64 batches.
    def viewport(x,y,r,b):return b'\x18'+word(x,y,r,b)
    def rect(x,y,r,b,c):return bytes((18,0,c,25,4))+word(x,y)+bytes((25,101))+word(r,b)
    setup=clean+rect(0,0,511,383,0)+viewport(32,24,287,359)+rect(32,24,287,359,2)
    scroll=bytes((23,7,2,2,1)) # downward one pixel, graphics viewport
    raw=bytes((0xC0|0x3f,))*256*16
    setup+=buffer(62000,2)+buffer(62000,0,word(len(raw))+raw)+buffer(62000,14)
    setup+=bytes((23,27,32))+word(62000)+bytes((23,27,33))+word(256,16)+b'\x01'
    strip=viewport(32,24,287,24)+bytes((25,0xED))+word(32,9)
    bounds=viewport(32,24,287,359)
    emit('SCROLL',201,scroll*64,[dict(x=16,y=100,expected=[0,0,0])],setup=setup)
    emit('CLIPROW',202,strip*64,[dict(x=40,y=24,expected=[255,255,255]),dict(x=16,y=24,expected=[0,0,0])],setup=setup)
    emit('COMBINED',203,(bounds+scroll+strip)*64,[dict(x=40,y=24,expected=[255,255,255]),dict(x=16,y=24,expected=[0,0,0])],setup=setup)
    header='// Generated immutable stage layout; no pointers into received packets.\n'
    header+='typedef struct { const char *name; unsigned group,setup,bytes,probes,uploads; } Case;\n'
    header+='static const Case cases[]={\n'+''.join(f'{{"{r["name"]}",{r["group"]},{r["setup_bytes"]},{r["bytes"]},{r["probes"]},{r["upload_bytes"]}}},\n' for r in rows)+'};\n'
    header+=f'#define CASE_COUNT {len(rows)}\n#define MAX_CASE_BYTES {max(r["setup_bytes"]+r["bytes"]+r["probes"]*7 for r in rows)+1}\n'
    (build/'cases.h').write_text(header)
    (media/'CLEAN.DAT').write_bytes(clean)
    (build/'corpus.json').write_text(json.dumps(dict(cases=rows,total=len(rows),cleanup_size=len(clean)),indent=2)+'\n')
    print(f'Prepared {len(rows)} finite cases; largest RAM preload {max(r["setup_bytes"]+r["bytes"] for r in rows)} bytes.')
if __name__=='__main__':main()
