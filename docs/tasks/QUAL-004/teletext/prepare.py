"""Static Mode7 page; mode selection belongs exclusively to autoexec.
Controls use printable high-bit aliases so MOS/VDU transports retain them.
No flash, Copper, timing, emulator or renderer implementation changes.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
b=bytearray([4,26,20,12,23,1,0])
def row(y,data):
 assert len(data)<40
 b.extend([31,0,y]);b.extend(data)
row(0,b'Teletext static qualification')
for c,label in enumerate(('Red','Green','Yellow','Blue','Magenta','Cyan','White'),1):
 row(c+1,bytes([128+c])+label.encode()+b' AaZz 0123456789')
row(10,b'Symbols: # [ \\ ] ^ _ ` { | } ~')
row(11,bytes([0x97,0xff])+b' Contiguous full block')
row(12,bytes([0x97,0x9a,0xff])+b' Separated full block')
row(13,bytes([0x96])+bytes([0xa1,0xa2,0xa4,0xa8,0xb0,0xe0,0xff]))
row(14,bytes([0x93,0xff,0x9e,0x91,0x92,0x94,0x9f])+b' Hold and release')
row(15,bytes([0x84,0x9d,0x87])+b' White on blue '+bytes([0x9c])+b' black')
for y in (17,18):row(y,bytes([0x83,0x8d])+b'Double height 123')
row(21,bytes([0x87,0x8c])+b'Normal height restored')
row(22,bytes([0x98])+b'Hidden'+bytes([0x87])+b'Visible')
b.extend([23,0,202])
(R/'TTSTATIC.vdu').write_bytes(b)
bar=b'Q4B1'+len(b).to_bytes(3,'little')+b'\0\0';(R/'TTSTATIC.vdu.bar').write_bytes(bar)
m={'identity':'teletext-static-probe-r01','name':'TTSTATIC','file':'TTSTATIC.vdu','mode':7,'surface':[640,480],'text_grid':[40,25],'cell':[16,19],'sha256':hashlib.sha256(b).hexdigest(),'barrier_sha256':hashlib.sha256(bar).hexdigest(),'bytes':len(b),'scope':'Static text, colours, mosaics, held graphics, background, double height and conceal; no flashing'}
(R/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
