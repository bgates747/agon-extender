"""Build a stopped, interactive MOS fixture from the approved source rasters."""
from pathlib import Path
from PIL import Image
from palette import default_palette, quantize
import json,struct,subprocess,hashlib
root=Path(__file__).resolve().parent
repo=root.parents[2]
assets=repo/'agents/visual-review/display-pattern'
manifest=json.loads((assets/'rasters/manifest.json').read_text())
out=assets/'fixture-r02';out.mkdir(exist_ok=True)
previews=assets/'palette-previews-r02';previews.mkdir(exist_ok=True)
palette_records={}
rows=manifest['modes']+[dict(mode=m,mode_width=848,mode_height=480,colours=c) for m,c in zip(range(96,100),(64,16,4,2))]
rows.sort(key=lambda r:r['mode'])
entries=[];paths=[];hashes={}
for r in rows:
 m,w,h,c=(r[k] for k in ('mode','mode_width','mode_height','colours'))
 if m in range(96,100):
  im=Image.open(assets/'rasters/mode-000-wide-854x480.png').convert('RGB').resize((848,480),Image.Resampling.NEAREST)
  # Replace mode identification using a readable native font on the raster.
  from PIL import ImageDraw,ImageFont
  d=ImageDraw.Draw(im);d.rectangle((106,37,742,64),fill='black')
  font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
  d.text((424,40),f'MODE {m} / 848 x 480 / {c} COLOURS',anchor='mt',font=font,fill='white')
 else:
  im=Image.open(assets/'rasters'/r['file']).convert('RGB')
  x=(im.width-w)//2;im=im.crop((x,0,x+w,h))
 palette=default_palette(repo,c)
 im=quantize(im,palette)
 im.save(previews/f'mode-{m:03d}.png')
 im.resize((round(h*3*(16/9 if m in range(96,100) else 4/3)),h*3),Image.Resampling.NEAREST).save(previews/f'mode-{m:03d}-display-3x.png')
 palette_records[str(m)]={'palette_rgb':palette,'unique_colours':len(set(im.get_flattened_data()))}
 # Public RGBA2222 byte order is AABBGGRR, unlike the RGB222 swatch ordering.
 pixels=bytes(0xc0 | round(red/85) | (round(green/85)<<2) | (round(blue/85)<<4) for red,green,blue in im.get_flattened_data())
 v=bytearray([22,m,23,1,0,23,0,192,0,12])
 v+=f'Mode {m}: {w}x{h}, {c} colours. Loading pattern...'.encode()
 v+=bytes([23,0,160])+struct.pack('<H',64000)+bytes([2])
 for pos in range(0,len(pixels),4096):
  block=pixels[pos:pos+4096]
  v+=bytes([23,0,160])+struct.pack('<H',64000)+bytes([0])+struct.pack('<H',len(block))+block
 v+=bytes([23,0,160])+struct.pack('<H',64000)+bytes([14])
 v+=bytes([23,27,32])+struct.pack('<H',64000)
 v+=bytes([23,27,33])+struct.pack('<HHB',w,h,1)
 v+=bytes([23,27,3])+struct.pack('<HH',0,0)
 if m>=128:v+=bytes([23,0,195])
 name=f'm{m:03d}.vdu';(out/name).write_bytes(v)
 entries.append(f' db {m}\n dl path_{m}')
 paths.append(f'path_{m}: db "/extender/mode-preview-r02/{name}",0')
 hashes[name]=hashlib.sha256(v).hexdigest()
# Teletext has a separate text-based sample; bitmap APIs are not its contract.
tele=bytes([22,7,12])+b'MODE 7 - TELETEXT\r\nText-only control; no bitmap geometry.\r\nABCDEFGHIJKLMNOPQRSTUVWXYZ\r\n0123456789\r\nPress Escape for the mode menu.'
(out/'m007.vdu').write_bytes(tele);hashes['m007.vdu']=hashlib.sha256(tele).hexdigest()
entries.append(' db 7\n dl path_7');paths.append('path_7: db "/extender/mode-preview-r02/m007.vdu",0')
labels=[f"{r['mode']:3} {r['mode_width']:4}x{r['mode_height']:<3} {r['colours']:2}c" for r in rows]+['  7 Teletext']
lines=['Extender mode preview - HDMI-004 r02','Selectable modes; visual qualification pending.','Mode  width x height  colours (128+ = double buffer)','']
for i in range(0,len(labels),3):lines.append(' | '.join(labels[i:i+3]))
lines+=['','Type mode number then Enter. Escape exits to Legacy mode 0.','After loading: Esc returns to the menu, even with no picture.','Compare circles, squares, colour swatches and clipping.','Mode: ']
text='\r\n'.join(lines).encode()
inc=f'ENTRY_COUNT: equ {len(entries)}\nentries:\n'+'\n'.join(entries+paths)+'\nmenu_vdu:\n db 22,0,23,1,1,12\n'
inc+=''.join(' db '+','.join(str(b) for b in text[i:i+32])+'\n' for i in range(0,len(text),32))+'menu_end:\n'
(root/'generated.inc').write_text(inc)
asm='/Agon/mystuff/agon-fsim/utilities/flight-model/agon-cockpit/build-benchmark/ez80asm'
subprocess.run([asm,'preview.asm','preview.bin'],cwd=root,check=True)
(out/'preview.bin').write_bytes((root/'preview.bin').read_bytes())
(root/'preview.bin').unlink()
hashes['preview.bin']=hashlib.sha256((out/'preview.bin').read_bytes()).hexdigest()
(out/'manifest.json').write_text(json.dumps({'fixture':'mode-preview-r02','files':hashes,'modes':len(entries),'hardware_validation':'pending','quantization':'Nearest RGB, no dithering; Agon default palette','palettes':palette_records},indent=2)+'\n')
print(out)
