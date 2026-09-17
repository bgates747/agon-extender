from pathlib import Path
import argparse,ctypes as C,json
p=argparse.ArgumentParser();p.add_argument('library',type=Path);p.add_argument('corpus',type=Path);p.add_argument('output',type=Path);a=p.parse_args();lib=C.CDLL(str(a.library.resolve()));u=C.POINTER(C.c_ubyte);lib.p4_szip.argtypes=[C.c_int,u,C.c_size_t,u,C.c_size_t,C.POINTER(C.c_size_t)]
def call(mode,data,cap):
 src=(C.c_ubyte*len(data)).from_buffer_copy(data);dst=(C.c_ubyte*(cap+16))();dst[cap:]=[165]*16;n=C.c_size_t();status=lib.p4_szip(mode,src,len(data),dst,cap,C.byref(n));assert bytes(dst[cap:])==bytes([165])*16;return status,bytes(dst[:n.value])
rows=[]
for case in json.loads((a.corpus/'manifest.json').read_text()):
 d=a.corpus/case['name'];r=(d/'rle2.bin').read_bytes();s=(d/'srle2.bin').read_bytes();status,decoded=call(1,s,len(r));assert status==0 and decoded==r,(case['name'],status,len(decoded))
 status,encoded=call(0,r,len(r)*2+4096);assert status==0 and encoded==s,(case['name'],'encode',status)
 rows.append(dict(case=case['name'],decode_exact=True,encode_exact=True));a.output.write_text(json.dumps(rows,indent=2)+'\n');print(case['name'],'native PASS',flush=True)
