from pathlib import Path
import re,json,subprocess
T=Path('docs/tasks/BENCH-005/composed-packing')
s=Path('/home/smith/Agon/agon-docs/docs/vdp/Screen-Modes.md').read_text().split('### Legacy modes')[0]
rows=[]
for line in s.splitlines():
 m=re.match(r'\|\s*[*§ ]*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)hz',line)
 if m:
  mode,w,h,c,hz=map(int,m.groups())
  if hz!=50:rows.append(dict(mode=mode,width=w,height=h,colours=c,hz=hz,double=mode>128))
rows.insert(7,dict(mode=7,width=640,height=480,colours=16,hz=60,double=False,special='teletext; separately qualify, not ordinary raster fixture'))
(T/'modes.json').write_text(json.dumps(rows,indent=2)+'\n')
lines=['# Non-50-Hz mode inventory','','Source: official Agon Screen-Modes.md, cross-check installed agon_screen.h. Listed support is not a new hardware qualification. Mode7 is special teletext.','','| Mode | Pixels | Colours | Hz | Double buffered | RGB222 bytes |','|---:|---|---:|---:|---|---:|']
for r in rows:lines.append(f"| {r['mode']} | {r['width']}×{r['height']} | {r['colours']} | {r['hz']} | {r['double']} | {r['width']*r['height']} |")
lines+=['','Historical numbering aliases (VDU23,0,193; unrelated to EMOS Legacy routing): 0→1024×768×2 at60Hz; 1→512×384×16 at60Hz; 2→320×200×64 at75Hz; 3→640×480×16 at60Hz. No extra raster geometry/depth; alias2 has separate timing. No 50Hz modes occur in this installed switch.','', 'All frames are composed first. Palette cardinality after composition determines packing eligibility, not this nominal Colours column. Browser request cap remains60 even for70/75Hz sources.']
(T/'MODES.md').write_text('\n'.join(lines)+'\n')
print(len(rows),'explicit modes')
