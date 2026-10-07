"""Bounded render-load r01 plan and durable binary-result codec."""
import struct

def plan(data_path,result_path,mode,geometry,tag,first=0,end=94,disable_timing=False):
    def name(s,n):
        b=s.encode('ascii');assert len(b)<n and s.startswith('/');return b+b'\0'*(n-len(b))
    w,h,c,_=geometry
    out=b'B9P1'+tag.to_bytes(3,'little')+struct.pack('<HH',first,end)+name(data_path,96)+name(result_path,128)+struct.pack('<BHHB',mode,w,h,c)
    assert len(out)==241
    return out+bytes([bool(disable_timing)])+b'\0'*14

def decode(data):
    if len(data)<128 or data[:5] not in (b'B9R1\1',b'B9R2\2'):raise ValueError('missing result header')
    continuous=data[:5]==b'B9R2\2'
    if not continuous and (len(data)-128)%400:raise ValueError('incomplete case checkpoint')
    def u24(p):return int.from_bytes(p,'little')
    result={'mode':data[5],'width':int.from_bytes(data[6:8],'little'),'height':int.from_bytes(data[8:10],'little'),'colours':data[10],'tag':u24(data[12:15]),'clock_start':u24(data[16:19]),'immediate_prt_counts':int.from_bytes(data[20:22],'little'),'calibration_counts':int.from_bytes(data[100:102],'little'),'calibration_raw_units':u24(data[102:105]),'build_id':data[22:128].split(b'\xff')[0].split(b'\0')[0].decode('ascii'),'cases':[]}
    seen=set()
    off=128
    while off<len(data):
        if continuous:
            d=data[off:off+24]
            if len(d)!=24 or d[:4]!=b'B9C2':raise ValueError('invalid continuous case header')
            frames=u24(d[17:20]);total=u24(d[14:17]);head=24;size=head+12*frames
            if frames>65535 or frames>total or total!=frames and not d[21]:raise ValueError('invalid sample count')
            if off+size>len(data):raise ValueError('incomplete case checkpoint')
            d=data[off:off+size]
        else:
            d=data[off:off+400];frames=total=32;head=16;size=400
            if d[:4]!=b'B9C1' or d[14]!=32:raise ValueError('invalid case header')
        id=int.from_bytes(d[4:6],'little')
        if id in seen:raise ValueError('duplicate case')
        seen.add(id)
        case={'id':id,'paced':bool(d[6]),'flags':d[7],'raw_start':u24(d[8:11]),'raw_end':u24(d[11:14]),'error':d[22] if continuous else d[15],'total_frames':total,'truncated':bool(d[21]) if continuous else False,'exit_reason':d[20] if continuous else 0,'frames':[]}
        for i in range(frames):
            f=d[head+i*12:head+(i+1)*12]
            if f[0]!=((i+8)%40 if continuous else i):raise ValueError('frame order')
            case['frames'].append({'index':i,'status':f[1],'submit_counts':int.from_bytes(f[2:4],'little'),'complete_counts':int.from_bytes(f[4:6],'little'),'total_counts':int.from_bytes(f[6:8],'little'),'raw_delta':u24(f[8:11])})
        result['cases'].append(case)
        off+=size
    return result
