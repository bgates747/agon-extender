"""Independent decoding of BSP VM/VDU packets, descriptors and asset contracts."""
import hashlib
import json
from pathlib import Path
import re
import struct
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'build'
seen_sprite=set(); seen_matrix=set(); seen_buffer=set(); seen_calls=set()


class Reader:
    def __init__(self,data): self.data=data;self.pos=0
    def take(self,n):
        assert 0<=n<=len(self.data)-self.pos,('truncated',self.pos,n,len(self.data))
        result=self.data[self.pos:self.pos+n];self.pos+=n;return result
    def byte(self): return self.take(1)[0]
    def word(self): return int.from_bytes(self.take(2),'little')
    def done(self): return self.pos==len(self.data)


def decode_vdu(data,owned):
    r=Reader(data)
    while not r.done():
        cmd=r.byte()
        if cmd>=32:continue
        if cmd in (0,4,12,16,20,26):continue
        if cmd in (17,18,24,28,29,31):
            r.take({17:1,18:2,24:8,28:4,29:4,31:2}[cmd]);continue
        if cmd==25:
            assert r.byte() in (4,5,0x65,*range(0xe8,0xf0))
            r.take(4);continue
        assert cmd==23,('VDU',cmd,r.pos)
        sub=r.byte()
        if sub==1:r.byte();continue
        if sub==27:
            op=r.byte();seen_sprite.add(op)
            if op in (0,4,6,7,10,18,21):r.byte()
            elif op in (3,13,14):r.take(4)
            elif op in (32,38,53):r.word()
            elif op==33:
                width,height=r.word(),r.word()
                if height:assert width and r.byte() in (0,1,2)
            elif op in (1,2):
                width,height=r.word(),r.word()
                if height:r.take(width*height*4 if op==1 else 4)
            else:assert op in (5,8,9,11,12,15,16,17,19,20),('sprite',op)
            continue
        assert sub==0,('VDU23',sub)
        op=r.byte()
        if op in (0xc0,):r.byte();continue
        if op==0xca:continue
        if op==0xc8:assert r.byte() in (3,4);continue
        if op==0xf8:r.take(4);continue
        if op==0x96:assert r.byte()==1;r.word();continue
        assert op==0xa0,('system',op)
        ident=r.word();assert ident in owned and ident!=65535
        op=r.byte();seen_buffer.add(op)
        if op==0:r.take(r.word())
        elif op in (1,2,14):pass
        elif op==13:
            while r.word()!=65535:pass
        elif op==5:
            adjust=r.byte();base=adjust&15;assert base in (0,5,6,7)
            assert not adjust&16 # all current fixtures use ordinary offsets
            r.word();count=r.word() if adjust&0xc0 else 1
            if base:
                if adjust&32:r.take(4)
                else:r.take(count if adjust&128 else 1)
        elif op==32:
            operation=r.byte();base=operation&15;seen_matrix.add(base)
            argc={0:0,1:0,2:1,3:1,4:1,5:2,6:2,7:2,8:2,9:2,10:2,11:6,12:2}[base]
            if base==12:r.word()
            if argc:
                fmt=r.byte();assert not fmt&32
                if operation&32:r.take(4)
                else:
                    for i in range(argc):
                        if i and operation&64:fmt=r.byte();assert not fmt&32
                        r.take(2 if fmt&128 else 4)
        elif op==40:
            flags=r.byte();assert flags<8;r.take(4)
            if flags&2:r.take(4)
        elif op==72:
            flags=r.byte();bits=flags&7;assert bits in (1,2,4);r.word()
            if flags&8:r.word()
            r.take(2 if flags&16 else 1<<bits)
        else:raise AssertionError(('buffer',op))


def main():
    catalog=json.loads((BUILD/'bitmaps-catalog.json').read_text())
    owned=set(catalog['buffers']);assets=catalog['assets']
    original=Image.open(ROOT/'assets/bitmaps/source/blenderaxes.png').convert('RGBA')
    raw=original.tobytes()
    assert (ROOT/'tgt/assets/bitmaps/axes8.rgba8').read_bytes()==raw
    packed=bytes(sum(round(v/85)<<(i*2) for i,v in enumerate(raw[pos:pos+4]))
                 for pos in range(0,len(raw),4))
    assert (ROOT/'tgt/assets/bitmaps/axes2.rgba2').read_bytes()==packed
    assert (ROOT/'assets/bitmaps/source/blenderaxes.rgba2').read_bytes()==packed
    for asset in assets:
        data=(ROOT/'tgt/assets/bitmaps'/asset['filename']).read_bytes()
        assert len(data)==asset['length']<32768
        assert hashlib.sha256(data).hexdigest()==asset['sha256']
        w,h,fmt=asset['width'],asset['height'],asset['format']
        if fmt<3:assert len(data)==h*((w+7)//8 if fmt==2 else w*(4 if fmt==0 else 1))
    binary=(ROOT/'tgt/bitmaps.bin').read_bytes()
    symbols={k:int(v,16) for k,v in re.findall(r'^(\S+) \$([0-9a-fA-F]+)',
                 (BUILD/'bitmaps.symbols').read_text(),re.M)}
    assert binary[64:69]==b'MOS\0\1'
    assert len(binary)==symbols['app_end']-0x40000
    assert symbols['app_end'] < 0xa0000
    assert symbols['app_end']-symbols['asset_staging']==32768
    stage_count=0
    for number,page in enumerate(catalog['pages'],1):
        assert page['page']==number
        row=symbols['page_table']-0x40000+(number-1)*4
        ptr=int.from_bytes(binary[row:row+3],'little')
        assert ptr==symbols[f'bsp{number:02}_stages'] and binary[row+3]==len(page['stages'])
        for i,stage in enumerate(page['stages']):
            stage_count+=1;name=stage['name'];data=(BUILD/(name+'.vm')).read_bytes();r=Reader(data)
            row=ptr-0x40000+i*7
            assert int.from_bytes(binary[row:row+3],'little')==symbols[name+'_program']
            assert int.from_bytes(binary[row+3:row+6],'little')==symbols[name+'_probes']
            assert binary[row+6]==len(stage['probes'])<100
            at=symbols[name+'_program']-0x40000;assert binary[at:at+len(data)]==data
            for action in stage['actions']:
                op=r.byte()
                if op==1:
                    assert action['op']=='vdu';raw=r.take(r.word())
                    assert raw.hex()==action['hex'];decode_vdu(raw,owned)
                elif op==2:
                    assert action['op']=='call';index=r.byte();a=r.byte()
                    name_call=catalog['calls'][index];seen_calls.add(name_call)
                    assert name_call==action['name'] and a==action['a']
                    for reg in ('bc','de','hl'):assert int.from_bytes(r.take(3),'little')==action[reg]&0xffffff
                elif op==3:
                    assert action['op']=='load';asset=assets[r.byte()];ident=r.word();mode=r.byte()
                    assert (asset['name'],ident,mode)==(action['asset'],action['ident'],action['mode'])
                    assert ident in owned and mode in (0,1,2,3)
                    if mode==2:assert asset['format']==0
                    if asset['format']==3:assert mode==3
                else:raise AssertionError(('VM',op))
            assert r.byte()==0 and r.done()
            probes=(BUILD/(stage['name']+'.probes')).read_bytes()
            expected=b''.join(bytes((23,0,0x84))+struct.pack('<HH',p['x'],p['y'])+bytes(p['expected']) for p in stage['probes'])
            assert probes==expected
    decode_vdu((BUILD/'bitmaps-cleanup.vdu').read_bytes(),owned)
    assert len(catalog['pages'])==32 and seen_matrix==set(range(13))
    assert set(catalog['calls'])-{'vdu_consolidate_buffer'}<=seen_calls
    assert {0,1,2,5,13,32,40,72}<=seen_buffer
    print(f'32 pages / {stage_count} stages; {len(assets)} assets; all 13 2D matrix operations.')
    print('VM packets, VDU lengths, compiled descriptors, asset packing and memory extent verified.')


if __name__=='__main__':main()
