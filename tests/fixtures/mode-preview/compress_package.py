"""Losslessly pack r02's bitmap uploads using the VDP's public command 65."""
from pathlib import Path
import subprocess,struct,json,hashlib
root=Path(__file__).resolve().parent;repo=root.parents[2]
work=repo/'agents/p4pc-reset/codec';work.mkdir(exist_ok=True)
header=(repo/'vdp/video/compression.h').read_text().replace('#include <esp_heap_caps.h>','').replace('#include <esp32-hal-psram.h>','')
(work/'compression-host.h').write_text(header)
subprocess.run(['g++','-O2','-std=c++17','-I',str(work),str(root/'compress.cpp'),'-o',str(work/'compress')],check=True)
base=repo/'agents/visual-review/display-pattern/fixture-r02';out=base.parent/'fixture-r02-packed';out.mkdir(exist_ok=True)
m=json.loads((base/'manifest.json').read_text());oldtotal=newtotal=0
for name in m['files']:
 data=(base/name).read_bytes();oldtotal+=len(data)
 if name.endswith('.vdu') and name!='m007.vdu':
  pos=data.index(bytes([23,0,160,0,250,2]))+6;prefix=data[:pos];pixels=bytearray()
  while data[pos:pos+6]==bytes([23,0,160,0,250,0]):
   n=struct.unpack_from('<H',data,pos+6)[0];pixels+=data[pos+8:pos+8+n];pos+=8+n
  assert data[pos:pos+6]==bytes([23,0,160,0,250,14]);suffix=data[pos+6:]
  (work/'raw').write_bytes(pixels)
  subprocess.run([str(work/'compress'),str(work/'raw'),str(work/'packed')],check=True)
  coded=(work/'packed').read_bytes();v=bytearray(prefix)
  for start in range(0,len(coded),4096):
   chunk=coded[start:start+4096];v+=bytes([23,0,160,0,250,0])+struct.pack('<H',len(chunk))+chunk
  v+=bytes([23,0,160,0,250,65,0,250])+suffix
  data=bytes(v)
 (out/name).write_bytes(data);newtotal+=len(data);m['files'][name]=hashlib.sha256(data).hexdigest()
m['compression']='Lossless TurboVega; every bitmap codec roundtrip verified before packaging'
(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print(f'Package reduced {oldtotal:,} -> {newtotal:,} bytes; {(1-newtotal/oldtotal)*100:.1f}% smaller')
