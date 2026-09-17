"""Stored-block, capacity and asset-alpha controls against original szip CLI."""
from pathlib import Path
import argparse,ctypes as C,subprocess,json
p=argparse.ArgumentParser();p.add_argument('library',type=Path);p.add_argument('reference',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(exist_ok=False)
lib=C.CDLL(str(a.library.resolve()));u=C.POINTER(C.c_ubyte);lib.p4_szip.argtypes=[C.c_int,u,C.c_size_t,u,C.c_size_t,C.POINTER(C.c_size_t)]
def call(mode,data,cap):
 src=(C.c_ubyte*len(data)).from_buffer_copy(data);dst=(C.c_ubyte*(cap+16))();dst[cap:]=[165]*16;n=C.c_size_t();status=lib.p4_szip(mode,src,len(data),dst,cap,C.byref(n));assert bytes(dst[cap:])==b'\xa5'*16;return status,bytes(dst[:n.value])
rows=[]
for n in range(1,6):
 raw=bytes(range(n));(a.out/'in.bin').write_bytes(raw);subprocess.run([str(a.reference.resolve()),'-b41o3',str((a.out/'in.bin').resolve()),str((a.out/'encoded.bin').resolve())],check=True,timeout=10)
 enc=(a.out/'encoded.bin').read_bytes();assert call(0,raw,100)==(0,enc);assert call(1,enc,n)==(0,raw);assert call(1,enc,n-1)[0]!=0;rows.append(dict(case=f'stored-{n}',passed=True))
# SRLE2 carrying transparent/partial-alpha RLE2 bytes is an asset-level valid outer layer.
raw=b'Cmpr\x03\0\0\0RLE2\x01\0\0\x41';status,enc=call(0,raw,100);assert status==0 and call(1,enc,len(raw))==(0,raw)
(a.out/'alpha.srle2').write_bytes(enc);rows.append(dict(case='asset-alpha-preserved-outer-layer',passed=True))
# Every truncation of this valid small stream must reject; output guard stays intact.
for i in range(len(enc)):assert call(1,enc[:i],len(raw))[0]!=0,i
rows.append(dict(case='all-truncations',count=len(enc),passed=True));(a.out/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
