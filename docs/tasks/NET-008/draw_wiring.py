#!/usr/bin/env python3
"""Task-only ESP8266 proposal over the unchanged complete P4-PC harness SVG.

No hardware/profile changes. Keep the base drawing's existing wire paths,
pulls, colours and contact geometry. The Author reports the modem wiring complete;
the module's physical terminal order and available power margin are unresolved.
Use librsvg/Cairo for PNG export: ImageMagick's internal SVG renderer omitted
the existing path elements during this task, so it is unsuitable for this file.
"""
from pathlib import Path
import ctypes
import ctypes.util
import hashlib
import json
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / 'hardware/designs/light2-p4pc-harness-draft/wiring-diagram.svg'
PROFILE = ROOT / 'vdp/build/boards/p4-pc.json'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
def tag(n): return '{'+NS+'}'+n
base = ET.parse(BASE).getroot()
old_paths = [dict(e.attrib) for e in base.iter(tag('path'))]
profile = json.loads(PROFILE.read_text())
assert profile['header']['gpio_pins']['47'] == 19
assert profile['header']['gpio_pins']['48'] == 20
assert not {47,48} & (set(profile['transport']['data']) |
                     {profile['transport'][n] for n in ('clock','valid','ready')} |
                     set(profile['reserved_gpios']))
base.set('width','2700'); base.set('viewBox','0 0 2700 1540')
base.find(tag('rect')).set('width','2700')
base.find(tag('title')).text = 'NET-008 wiring record — full existing harness plus ESP8266 UART'
base.find(tag('desc')).text = 'Task-only derivative. All existing harness paths retained. Author-reported GPIO47 TX and orange GPIO48 RX; supply current remains unqualified.'
for e in base.iter(tag('text')):
    if e.get('x')=='40' and e.get('y')=='40':
        e.text = 'Agon Light 2 → P4-PC Rev C + ESP8266 branch'
    elif e.get('x')=='40' and e.get('y')=='69':
        e.text = 'NET-008 task-only record · Author reports wiring complete · Orange RX matches Console8'
    elif e.text and 'GPIO47 / Spare' in e.text:
        e.text = e.text.replace('GPIO47 / Spare','GPIO47 / modem TX')
    elif e.text and 'GPIO48 / Spare' in e.text:
        e.text = e.text.replace('GPIO48 / Spare','GPIO48 / modem RX')
    elif e.get('x')=='40' and e.get('y')=='1414':
        e.text = 'New modem UART uses EXT1-19 / GPIO47 and EXT1-20 / GPIO48; their earlier proposed ZDI use is deferred.'
    elif e.get('x')=='40' and e.get('y')=='1442':
        e.text = 'Agon and P4-PC positive rails stay separate. Modem supply is proposed from P4 EXT1-1, subject to power check.'
    elif e.get('x')=='40' and e.get('y')=='1510':
        e.text = 'Task copy of the existing P4-PC harness; base file and maintained pin profile unchanged. See task PIN-SELECTION.md.'

def el(n, **attrs): return ET.SubElement(base,tag(n),{k.replace('_','-'):str(v) for k,v in attrs.items()})
def text(x,y,s,size=18,colour='#20242b',bold=False):
    e=el('text',x=x,y=y,font_size=size,fill=colour,font_weight='bold' if bold else 'normal');e.text=s
def rect(x,y,w,h,fill='#f5f6f8',stroke='#b8c1cc',**attrs):
    return el('rect',x=x,y=y,width=w,height=h,fill=fill,stroke=stroke,**attrs)
defs=el('defs')
for name,col in [('tx','#008b8b'),('rx','#e07800')]:
    m=ET.SubElement(defs,tag('marker'),{'id':'arrow-'+name,'markerWidth':'9','markerHeight':'9','refX':'8','refY':'4','orient':'auto','markerUnits':'userSpaceOnUse'})
    ET.SubElement(m,tag('path'),{'d':'M 0 0 L 8 4 L 0 8 Z','fill':col})
for pin,col in [(19,'#008b8b'),(20,'#e07800'),(1,'#c62828'),(3,'#111111')]:
    for kind in ['overview','bank']:
        old=base.find(f'.//*[@id="pc-{kind}-pin{pin}"]')
        if old is not None:
            old.set('stroke',col);old.set('stroke-width','3')
            if pin in (19,20):old.set('fill','#e4f6f5' if pin==19 else '#fff0da')

# The drawing keeps the original 1800-wide harness area intact. Branches start
# at actual contact rectangles in its complete physical header view.
el('path',d='M 1820 24 V 1516',stroke='#d3dce5',fill='none',stroke_width=2)
text(1870,50,'ESP8266 modem branch',28,bold=True)
text(1870,84,'P4 UART2 · 115200 baud · 8N1 · TX/RX only',18)
text(1870,113,'Existing mainboard UART1 and all harness wires stay in place.',17)
rect(1998,194,636,374,'#f5fafc','#64788a',rx=14)
text(2030,231,'Real ESP8266 / existing AT firmware',23,bold=True)
for y,label,col in [(260,'VCC / 3.3 V','#c62828'),(340,'RXD  ←  P4 TX','#008b8b'),
                    (420,'TXD  →  P4 RX','#e07800'),(500,'GND','#111111')]:
    el('circle',cx=2010,cy=y,r=5,fill=col)
    text(2040,y+6,label,21,col,True)
text(2030,548,'Logical terminals; module pin order is not assumed.',16)

branches=[
 ('modem-vcc','M 945 222 H 900 V 177 H 1770 V 260 H 2010','#c62828','',True,1),
 ('modem-tx','M 945 492 H 920 V 538 H 1860 V 340 H 2010','#008b8b','tx',False,19),
 ('modem-rx','M 2010 420 H 1910 V 492 H 1445','#e07800','rx',False,20),
 ('modem-ground','M 945 252 H 875 V 600 H 1940 V 500 H 2010','#111111','',False,3),
]
for name,d,col,arrow,dashed,pin in branches:
    # White underlay makes crossings explicit: no dot means no junction.
    el('path',d=d,fill='none',stroke='white',stroke_width=8)
    e=el('path',id=name,d=d,fill='none',stroke=col,stroke_width=3,
         stroke_linejoin='round',data_pc_pin=pin,data_status='author-reported' if pin != 1 else 'supply-unqualified')
    if dashed:e.set('stroke-dasharray','9 5')
    if arrow:e.set('marker-end','url(#arrow-'+arrow+')')
    if pin in (1,3,19):
        xy={1:(945,222),3:(945,252),19:(945,492)}[pin]
    else:xy=(1445,492)
    el('circle',cx=xy[0],cy=xy[1],r=4,fill=col)
text(1490,483,'EXT1-20 / GPIO48 RX',16,'#e07800',True)
text(1490,529,'EXT1-19 / GPIO47 TX',16,'#008b8b',True)
text(1490,591,'EXT1-3 / common GND',16,'#111111',True)
text(1510,167,'EXT1-1 / P4 +3.3 V',16,'#c62828',True)

text(1870,650,'Find the two new signal pins',23,bold=True)
for y,s in [(686,'At the USB-A end of EXT1: the last pair is pins19/20.'),
            (718,'19: one row beyond brown D6 / EXT1-17.'),
            (750,'20: one row beyond green D7 / EXT1-18.'),
            (782,'In the lower bank drawing, both are immediately above'),
            (810,'those existing brown and green connections.')]:text(1870,y,s,18)
text(1870,866,'Power and allocation notes',23,bold=True)
for y,s in [(902,'Signal levels: 3.3 V. No modem RTS/CTS pins available.'),
            (934,'Dashed red: candidate supply from P4 EXT1-1.'),
            (966,'Check modem current demand and P4 rail margin first.'),
            (998,'EXT1-3 already shares Agon ground; add a modem branch.'),
            (1030,'Do not connect P4 +3.3 V to the Agon +3.3 V rail.'),
            (1062,'GPIO47/48 share the already-required LDO4 3.3 V bank.'),
            (1094,'Earlier ZDI use of these contacts was proposed only.'),
            (1126,'The reported modem wiring occupies that pair.')]:text(1870,y,s,18)
rect(1860,1180,790,225,'#eef4fa','#bbc9d8',rx=10)
text(1880,1217,'Existing wiring is the complete base harness at left.',19,bold=True)
for y,s in [(1254,'All eight data wires, three handshake/clock wires,'),
            (1284,'common ground, pull resistors, rails and full headers remain.'),
            (1320,'Orange RX matches the Author’s Console8 wiring.'),
            (1350,'Wiring completion is Author-reported; firmware is unchanged.'),
            (1380,'No dot at a crossing means the wires are not joined.')]:text(1880,y,s,17)
text(1870,1488,'Base: light2-p4pc-harness-draft · Rev C manufacturer reference',15,'#56606e')
text(1870,1514,'Task: NET-008 · 2026-11-09 · Author-reported wiring',15,'#56606e')

actual_old=[dict(e.attrib) for e in base.iter(tag('path')) if e.attrib in old_paths]
assert actual_old==old_paths,'Existing wire/rail paths must remain identical'
svg=HERE/'ESP8266-WIRING.svg'
ET.indent(base,space='  ')
ET.ElementTree(base).write(svg,encoding='utf-8',xml_declaration=True)

# Render with the installed native SVG library, without installing dependencies.
r=ctypes.CDLL(ctypes.util.find_library('rsvg-2'))
c=ctypes.CDLL(ctypes.util.find_library('cairo'))
g=ctypes.CDLL(ctypes.util.find_library('gobject-2.0'))
r.rsvg_handle_new_from_file.argtypes=[ctypes.c_char_p,ctypes.c_void_p]
r.rsvg_handle_new_from_file.restype=ctypes.c_void_p
r.rsvg_handle_render_cairo.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
r.rsvg_handle_render_cairo.restype=ctypes.c_int
c.cairo_image_surface_create.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_int]
c.cairo_image_surface_create.restype=ctypes.c_void_p
c.cairo_create.argtypes=[ctypes.c_void_p];c.cairo_create.restype=ctypes.c_void_p
c.cairo_surface_write_to_png.argtypes=[ctypes.c_void_p,ctypes.c_char_p]
c.cairo_surface_write_to_png.restype=ctypes.c_int
c.cairo_destroy.argtypes=[ctypes.c_void_p]
c.cairo_surface_destroy.argtypes=[ctypes.c_void_p]
g.g_object_unref.argtypes=[ctypes.c_void_p]
h=r.rsvg_handle_new_from_file(str(svg).encode(),None)
assert h,'SVG load failed'
s=c.cairo_image_surface_create(0,2700,1540);ctx=c.cairo_create(s)
assert r.rsvg_handle_render_cairo(h,ctx),'SVG render failed'
assert c.cairo_surface_write_to_png(s,str(HERE/'ESP8266-WIRING.png').encode())==0
c.cairo_destroy(ctx);c.cairo_surface_destroy(s);g.g_object_unref(h)
print('Wrote task-only SVG/PNG; preserved',len(old_paths),'existing path elements')
print('Base SHA256:',hashlib.sha256(BASE.read_bytes()).hexdigest())
print('Profile SHA256:',hashlib.sha256(PROFILE.read_bytes()).hexdigest())
