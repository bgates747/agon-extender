"""Task-only Pi modem diagram; reuses existing BYTE Pi5 header artwork.

Source header is read-only. Archive WROOM assignments are deliberately omitted;
the new proposal overlays only modem pins and the retained reset circuit.
"""
from pathlib import Path
from xml.etree import ElementTree as E
from copy import deepcopy
import hashlib,json
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[3]/'agon-hardware/first_steps/byte/pi5-wroom-wiring-diagram.svg'
NS='http://www.w3.org/2000/svg';E.register_namespace('',NS)
def node(tag,**attrs):return E.Element('{'+NS+'}'+tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})
r=node('svg',viewBox='0 0 1700 1180',font_family='sans-serif');r.append(node('rect',width=1700,height=1180,fill='#fafafa'))
b=E.parse(BASE).getroot();r.append(deepcopy(b.find('{'+NS+'}defs')))
def text(x,y,s,size=19,color='#202428',**a):
 e=node('text',x=x,y=y,font_size=size,fill=color,**a);e.text=s;r.append(e);return e
def rect(x,y,w,h,fill='#fff',stroke='#63707a'):
 e=node('rect',x=x,y=y,width=w,height=h,rx=8,fill=fill,stroke=stroke,stroke_width=2);r.append(e)
def line(points,color,width=4,dash=None):
 e=node('polyline',points=' '.join(f'{x},{y}' for x,y in points),fill='none',stroke=color,stroke_width=width,stroke_linejoin='round');
 if dash:e.set('stroke-dasharray',dash)
 r.append(e)
text(42,40,'NET-009 — Pi5-powered ESP8266 UART comparison',29,font_weight='bold')
text(42,72,'Proposed wiring • preserve the existing Olimex reset circuit • physical pin numbers shown',19)
pi=deepcopy(b.find(".//*[@id='pi5']"));pi.remove(pi.find(".//*[@id='pi-used-pins']"))
rows=pi.find(".//*[@id='pi-header-rows']")
for parent in rows.iter():
 for child in list(parent):
  if child.tag=='{'+NS+'}text':parent.remove(child)
r.append(pi)
labels=['3V3','5V','GPIO2','5V','GPIO3','GND','GPIO4','GPIO14 TX','GND reset','GPIO15 RX','GPIO17 reset','GPIO18','GPIO27','GND','GPIO22','GPIO23','3V3','GPIO24','GPIO10','GND','GPIO9','GPIO25','GPIO11','GPIO8','GND','GPIO7','GPIO0','GPIO1','GPIO5','GND','GPIO6','GPIO12','GPIO13','GND','GPIO19','GPIO16','GPIO26','GPIO20','GND','GPIO21']
for pin,label in enumerate(labels,1):
 y=218+30*((pin-1)//2);odd=pin%2
 text(180 if odd else 420,y+4,str(pin),12,text_anchor='end' if odd else 'start')
 text(210 if odd else 390,y+4,label,11,text_anchor='start' if odd else 'end')
 if pin in [1,6,8,10,9,11]:
  colour={1:'#c62828',6:'#111',8:'#238b45',10:'#ef7d00',9:'#111',11:'#546e7a'}[pin];r.append(node('circle',cx=193 if odd else 407,cy=y,r=8,fill='white',stroke=colour,stroke_width=3))
rect(840,185,735,345,fill='#e9f2e7')
text(862,222,'Olimex MOD-WIFI-ESP8266',25,font_weight='bold')
text(862,260,'UEXT 1: 3.3 V',18,'#b71c1c')
text(862,299,'UEXT 2: GND',18)
text(862,358,'UEXT 3: modem RX',18,'#1b6b36')
text(862,408,'UEXT 4: modem TX',18,'#a44b00')
text(1068,260,'Look straight into the modem socket',20,font_weight='bold')
text(1068,285,'Key notch at the bottom; use the molded pin-1 mark.',17)
# Olimex UEXT face drawing with the notch down: even contacts above odd.
# The modem is a peripheral: its pins 3/4 are RX/TX, unlike the host legend.
line([(1280,449),(1068,449),(1068,310),(1532,310),(1532,449),(1320,449)],'#334238',3)
for row,y in [(2,343),(1,405)]:
 for col in range(5):
  pin=row+2*col;x=1118+90*col
  color={1:'#b71c1c',2:'#111',3:'#1b6b36',4:'#a44b00'}.get(pin,'#64726b')
  rect(x-29,y-20,58,39,'white',color)
  text(x,y+6,str(pin),20,color,text_anchor='middle',font_weight='bold')
  text(x,y+34,{1:'3.3 V',2:'GND',3:'RXD',4:'TXD'}.get(pin,'—'),14,color,text_anchor='middle')
text(1118,478,'▲ Pin 1',17,'#b71c1c',text_anchor='middle',font_weight='bold')
text(1300,478,'↑ Key notch',17,text_anchor='middle')
text(862,508,'Pins 5–10: leave open. The rear / wire-entry view is mirrored.',17)
line([(193,218),(105,218),(105,106),(770,106),(770,250),(840,250)],'#c62828',dash='10 6')
line([(407,278),(610,278),(610,290),(840,290)],'#111')
line([(407,308),(670,308),(670,350),(840,350)],'#238b45')
line([(840,400),(720,400),(720,338),(407,338)],'#ef7d00')
text(470,240,'Pin 1: proposed 3V3 supply',18,'#b71c1c');text(470,266,'Pin 6: new modem ground',16)
text(470,325,'Pin 8: Pi TX → modem RX',17,'#1b6b36');text(470,370,'Pin 10: Pi RX ← modem TX',17,'#a44b00')
rect(815,560,760,210,fill='#fff6df',stroke='#b8860b');text(840,594,'Power check before energizing',23,font_weight='bold');text(840,627,'Pi has 3V3 supply pins 1 and 17. Proposed modem feed: pin 1.',18);text(840,658,'Confirm ≥500 mA-capable spare 3V3 supply and module polarity.',18);text(840,689,'If unverified: draw a Pi-5V-fed regulator alternative first.',18);text(840,720,'Disconnect all four old P4 modem wires; never join supplies.',18)
rect(800,820,800,270,fill='#edf0f2');text(825,855,'Existing Olimex reset circuit — leave intact',24,font_weight='bold')
line([(193,368),(128,368),(128,910),(860,910)],'#546e7a',3)
rect(860,892,100,34,fill='white');text(910,915,'10 kΩ',18,text_anchor='middle');line([(960,910),(1050,910)],'#546e7a',3)
text(825,884,'Physical 11 / GPIO17',17,'#455a64');text(1070,915,'Existing transistor base',18)
line([(193,338),(72,338),(72,1000),(1080,1000)],'#111',3);text(825,1033,'Physical 9 / GND → existing emitter + common ground',18)
text(1070,953,'Collector → Olimex RST/EN',18);text(825,1070,'Neither pin 9 nor pin 11 is borrowed for the modem.',18,font_weight='bold')
text(160,875,'Header view reused from BYTE Pi5/WROOM artwork.',16);text(160,900,'Old WROOM bus wires are archival, not current wiring.',16);text(160,935,'USB / Ethernet end ↓',22,font_weight='bold');text(160,967,'Check physical pin 1; underside/socket views mirror.',17)
text(42,1140,'Only the shown connections are proposed/retained. Other header pins are not declared free. No hardware was changed.',17)
E.ElementTree(r).write(HERE/'PI5-ESP8266-WIRING.svg',encoding='unicode',xml_declaration=True)
(HERE/'DIAGRAM-SOURCE.json').write_text(json.dumps({'source':'agon-hardware/first_steps/byte/pi5-wroom-wiring-diagram.svg','sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'reused':'Pi5 header geometry, orientation and full row positions; archival WROOM assignments omitted','modem_connector_orientation':'https://www.olimex.com/Products/Modules/UEXT/images/UEXT-PINS.jpg','modem_signal_reference':'https://www.olimex.com/Products/IoT/ESP8266/MOD-WIFI-ESP8266/open-source-hardware','reset_reference':'docs/bench-reset.md','status':'proposal; power and host pin ownership checks pending'},indent=2)+'\n')
