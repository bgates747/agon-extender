"""Independently decode generated VDU packets and their compiled descriptors."""
import json
from pathlib import Path
import re
import struct

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'build'
FAMILIES=set(range(0,0xD0,8)) | {0xD8,0xE8}
plot_codes=set()
system_codes=set()


def decode(data):
    pos=0
    def take(size):
        nonlocal pos
        assert pos+size<=len(data),f'Truncated packet at {pos}'
        value=data[pos:pos+size];pos+=size;return value
    def byte():return take(1)[0]
    def word():return int.from_bytes(take(2),'little')
    while pos<len(data):
        command=byte()
        if command>=32:continue
        if command in (4,5,6,12,15,16,20,26):continue
        if command in (17,18,19,24,28,29,31):
            take({17:1,18:2,19:5,24:8,28:4,29:4,31:2}[command]);continue
        if command==25:
            code=byte();assert code&0xF8 in FAMILIES,hex(code)
            plot_codes.add(code);struct.unpack('<hh',take(4));continue
        assert command==23,f'Unexpected VDU {command} at {pos-1}'
        sub=byte()
        if sub in (1,6,7,23):take({1:1,6:8,7:3,23:1}[sub]);continue
        if sub==27:
            op=byte()
            if op==0x20:word()
            elif op==3:take(4)
            elif op==0x21:
                width,height=word(),word()
                if height:assert width>0 and byte() in (0,1,2)
            else:raise AssertionError(f'Unexpected bitmap command {op}')
            continue
        assert sub==0,f'Unexpected VDU 23,{sub}'
        op=byte();system_codes.add(op)
        if op in (0x9C,0x9D,0x9E,0x9F,0xCA):continue
        if op in (0xC0,0xF2):byte();continue
        if op==0xC8:assert byte() in (3,4);continue
        if op==0xF8:take(4);continue
        if op==0xF9:take(2);continue
        if op==0x96:assert byte()==1;word();continue
        assert op==0xA0,f'Unexpected system command {op:02x}'
        ident=word();operation=byte()
        assert 60000<=ident<=60003,f'Non-owned buffer {ident}'
        if operation==0:
            payload=take(word())
            if ident==60003:decode(payload)
        elif operation in (1,2):pass
        elif operation==32:
            operation=byte();argc={0:0,2:1,5:2,8:2}[operation]
            if argc:
                assert byte()==0 # explicit IEEE-754 single precision
                struct.unpack('<'+'f'*argc,take(argc*4))
        else:raise AssertionError(f'Unexpected buffer operation {operation}')
    assert pos==len(data)


def main():
    binary=(ROOT/'tgt/shapes.bin').read_bytes()
    symbols={k:int(v,16) for k,v in re.findall(r'^(\S+) \$([0-9a-fA-F]+)',
                 (BUILD/'shapes.symbols').read_text(),re.M)}
    assert binary[64:69]==b'MOS\x00\x01'
    assert len(binary)==symbols['app_end']-0x40000
    catalog=json.loads((BUILD/'catalog.json').read_text())
    assert len(catalog)==24
    for i,(name,length,count) in enumerate(catalog):
        data=(BUILD/f'{name}.vdu').read_bytes();decode(data)
        probes=(BUILD/f'{name}.probes').read_bytes()
        manifest=json.loads((BUILD/f'{name}.json').read_text())
        assert len(probes)==count*10 and len(data)==length
        for j,(_,x,y,rgb) in enumerate(manifest['probes']):
            assert probes[j*10:(j+1)*10]==bytes((23,0,0x84))+struct.pack('<hh',x,y)+bytes(rgb)
        start=symbols['page_table']-0x40000+i*10
        row=binary[start:start+10]
        stream,size,query=(int.from_bytes(row[o:o+3],'little') for o in (0,3,6))
        assert (stream,size,query,row[9])==(symbols[name+'_stream'],length,symbols[name+'_probes'],count)
        assert binary[stream-0x40000:stream-0x40000+length]==data
        assert binary[query-0x40000:query-0x40000+len(probes)]==probes
    assert {p&0xF8 for p in plot_codes}==FAMILIES
    assert {0x9C,0x9D,0x9E,0x9F,0x96,0xC8,0xA0,0xF2}<=system_codes
    print(f'24 pages, {len(FAMILIES)} PLOT families, exact packets and compiled descriptors verified.')


if __name__=='__main__':main()
