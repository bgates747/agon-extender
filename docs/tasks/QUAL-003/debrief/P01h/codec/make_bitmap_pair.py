"""Reuse retained bitmap transform oracle with an RLE2-upload substitution."""
from pathlib import Path
import argparse,runpy,struct,json
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--assets',type=Path);a=p.parse_args();a.out.mkdir()
ns=runpy.run_path('docs/tasks/PORT-008/bitmap-coverage/make_case.py');ns['make_case'](a.out/'source')
lines=(a.out/'source/bitmaps.txt').read_text().splitlines();prefix='VDU 23 0 160 51001; 0 12; '
line=next(l for l in lines if l.startswith(prefix));pixels=[int(x) for x in line[len(prefix):].split()];pixels=[(x&63)|(192 if x&192 else 0) for x in pixels]
rawline=prefix+' '.join(map(str,pixels));packed=b'Cmpr'+struct.pack('<I',12)+b'RLE2\1\0'+bytes(128|(x&63)|(64 if x&192 else 0) for x in pixels)
compressed='VDU 23 0 160 51006; 2\nVDU 23 0 160 51006; 0 '+str(len(packed))+'; '+' '.join(map(str,packed))+'\nVDU 23 0 160 51001; 65 51006;'
convert=runpy.run_path('docs/tasks/QUAL-004/prepare_modes.py')['binary']
for name,replacement in [('bitmap_raw',rawline),('bitmap_rle',compressed)]:
 text='\n'.join(replacement if l==line else l for l in lines)
 data=convert(text)
 (a.out/(name+'.vdu')).write_bytes(data);(a.out/(name+'.vdu.bar')).write_bytes(b'Q4B1'+len(data).to_bytes(3,'little')+b'\0\0')

if a.assets:
 u=lambda n:struct.pack('<H',n)
 extra=bytes([23,0,248])+u(2)+u(1)+bytes([23,0,248])+u(784)+u(0)
 for i,hw in [(0,False),(1,True)]:extra+=bytes([23,27,4,i,23,27,5,23,27,38])+u(3000)+bytes([23,27,19 if hw else 20,23,27,13])+u(160+i*80)+u(64)+bytes([23,27,11])
 extra+=bytes([23,27,7,2,23,27,15,23,0,202])
 for name in ('raw','rle'):
  data=(a.assets/(name+'.vdu')).read_bytes()+extra
  (a.out/(name+'_sprites.vdu')).write_bytes(data)
  (a.out/(name+'_sprites.vdu.bar')).write_bytes(b'Q4B1'+len(data).to_bytes(3,'little')+b'\0\0')
