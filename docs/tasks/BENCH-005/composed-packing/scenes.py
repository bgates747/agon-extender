from pathlib import Path
import runpy,struct,json,shutil
T=Path('docs/tasks/BENCH-005/composed-packing');R=Path('agents/composed-packing');out=R/'scenes';out.mkdir(exist_ok=True)
make=runpy.run_path('docs/tasks/PORT-008/copper-coverage/make_case.py')['make_case']
def binary(s):
 data=bytearray()
 for line in s.splitlines():
  if line.startswith('VDU '):
   for token in line.split()[1:]:data.extend(struct.pack('<H',int(token[:-1])&65535) if token.endswith(';') else bytes([int(token)]))
 return data
for c in [2,4,16]:
 d=out/f'copper{c}'
 if d.exists():shutil.rmtree(d)
 make(d,c);(out/f'c{c}.vdu').write_bytes(binary((d/'setup.txt').read_text()))
# 64-colour control follows QUAL-004 physical-coordinate rectangles.
data=bytearray([23,0,192,0,23,1,0,26,12])
for y in range(8):
 for x in range(8):data+=bytes([18,0,y*8+x,25,4])+struct.pack('<HH',x*40,y*25)+bytes([25,101])+struct.pack('<HH',x*40+39,y*25+24)
(out/'c64.vdu').write_bytes(data)
(out/'c7.vdu').write_bytes(b'\x0cComposed packing teletext control\r\n'+b'0123456789 ABCDEFGHIJKLMNOPQRSTUVWXYZ\r\n'*15)
print('Reused Copper+SW/HW sprite scenes and raster control prepared')
