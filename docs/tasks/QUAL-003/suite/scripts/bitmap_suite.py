"""BSP-01..32: stage programs with raw VDU, audited API calls, and SD loads."""
import json
import math
import struct
import textwrap
from pathlib import Path
from PIL import Image
from bitmap_assets import build, ROOT, TARGET

BUILD = ROOT / 'build'
ASSETS = {}
PAGES = []
BUFFERS = set()
A, B, C, D, M, N, TMP, MAP = range(61000,61008)
CALLS = [
    'vdu_buff_select','vdu_bmp_create','vdu_consolidate_buffer',
    'vdu_sprite_select','vdu_sprite_clear_frames','vdu_sprite_add_bmp',
    'vdu_sprite_activate','vdu_sprite_next_frame','vdu_sprite_prev_frame',
    'vdu_sprite_select_frame','vdu_sprite_show','vdu_sprite_hide',
    'vdu_sprite_move_abs','vdu_sprite_move_rel','vdu_sprite_update',
    'vdu_sprite_bmp_reset','vdu_sprite_reset','vdu_sprite_set_gcol',
    'vdu_sprite_add_buff','vdu_sprite_move_abs168','vdu_sprite_move_rel168',
    'ext_sprite_hardware','ext_sprite_software','ext_sprite_replace8',
    'ext_sprite_replace16',
]


def w(*args): return struct.pack('<'+'H'*len(args), *(x&65535 for x in args))
def u24(x): return (x&0xffffff).to_bytes(3,'little')
def buf(ident,op,data=b''):
    assert ident != 65535
    BUFFERS.add(ident)
    return bytes((23,0,0xa0))+w(ident)+bytes((op,))+data


class Stage:
    def __init__(self, page, caption, draw_heading=True):
        self.page=page; self.caption=caption; self.actions=[]; self.probes=[]
        self.draw_heading=draw_heading
        self.data=bytearray()
        page.stages.append(self)
        if draw_heading:
            self.raw(4,26,23,0,0xc0,0,18,0,128)
            # CLS deactivates every sprite, even in a small text viewport.
            # Clear with vector rectangles while retaining active sprite state.
            self.rect(0,0,511,55,0);self.rect(0,360,511,383,0);self.gcol()
            self.label(2,0,f'BITMAPS / BSP-{page.number:02} - {page.title}',15)
            self.label(2,2,page.commands,14)
            self.label(2,4,caption,15)
            self.label(2,46,f'Stage {len(page.stages):02}. Key: next. ESC: clear and return to MOS.',15)

    def raw(self,*values): self.data.extend(values)
    def bytes(self,data): self.data.extend(data)
    def drain(self):
        if self.data:
            self.actions.append(dict(op='vdu',hex=self.data.hex()))
            self.data.clear()
    def call(self,name,a=0,bc=0,de=0,hl=0):
        self.drain()
        assert name in CALLS
        self.actions.append(dict(op='call',name=name,a=a,bc=bc,de=de,hl=hl))
    def label(self,x,y,text,col=15):
        assert 0<=x<64 and 0<=y<48,(x,y,text)
        for offset,line in enumerate(textwrap.wrap(text,64-x)):
            assert y+offset<48,(x,y,text)
            self.raw(17,col,31,x,y+offset); self.bytes(line.encode('ascii'))
    def gcol(self,col=15,mode=0): self.raw(18,mode,col)
    def plot(self,code,x,y): self.bytes(bytes((25,code))+w(x,y))
    def rect(self,x,y,r,b,col=15):
        self.gcol(col); self.plot(4,x,y); self.plot(0x65,r,b)
    def line(self,x,y,r,b,col=15):
        self.gcol(col); self.plot(4,x,y); self.plot(5,r,b)
    def outline(self,x,y,r,b,col=7):
        self.line(x,y,r,y,col); self.line(r,y,r,b,col)
        self.line(r,b,x,b,col); self.line(x,b,x,y,col)
    def marker(self,x,y):
        self.line(x-3,y,x+3,y,11); self.line(x,y-3,x,y+3,11)
    def clear_art(self): self.rect(0,56,511,359,0)
    def load(self,name,ident,mode=0):
        self.drain(); BUFFERS.add(ident)
        self.actions.append(dict(op='load',asset=name,ident=ident,mode=mode))
    def select(self,ident,literal=False):
        if literal: self.bytes(bytes((23,27,32))+w(ident))
        else: self.call('vdu_buff_select',hl=ident)
    def create(self,ident,width=34,height=34,fmt=1):
        self.select(ident); self.call('vdu_bmp_create',a=fmt,bc=width,de=height)
    def bmp(self,ident,x,y,code=0xed,mode=0):
        self.select(ident); self.gcol(15,mode); self.plot(code,x,y)
    def direct(self,ident,x,y):
        self.select(ident); self.bytes(bytes((23,27,3))+w(x,y))
    def upload(self,ident,data):
        self.bytes(buf(ident,2)); self.bytes(buf(ident,0,w(len(data))+data))
    def copy(self,dst,src): self.bytes(buf(dst,13,w(src,65535)))
    def checker(self,x,y,width=112,height=80,pattern='checker'):
        self.load(pattern,TMP)
        self.direct(TMP,x,y)
    def matrix(self,op=0,*args,ident=M,fmt=0,raw=None,bitmap=None):
        self.bytes(bytes((23,0,0xf8))+w(1,1))
        packet=bytes((op,))
        if bitmap is not None: packet+=w(bitmap)
        if args or raw is not None:
            packet+=bytes((fmt,))+(raw if raw is not None else struct.pack('<'+'f'*len(args),*args))
        self.bytes(buf(ident,32,packet))
    def transform(self,ident=65535): self.bytes(bytes((23,0,0x96,1))+w(ident))
    def bake(self,src,dst,options=5,size=None):
        self.bytes(buf(dst,40,bytes((options,))+w(M,src)+(w(*size) if size else b'')))
    def sprite(self,n,frames,x,y,hw=False,mode=0):
        self.call('vdu_sprite_select',a=n); self.call('vdu_sprite_clear_frames')
        for frame in frames: self.call('vdu_sprite_add_buff',hl=frame)
        self.call('vdu_sprite_set_gcol',a=mode)
        self.call('ext_sprite_hardware' if hw else 'ext_sprite_software')
        self.call('vdu_sprite_move_abs',bc=x,de=y); self.call('vdu_sprite_show')
    def activate(self,n): self.call('vdu_sprite_activate',a=n); self.call('vdu_sprite_update')
    def hardware(self): self.bytes(bytes((23,0,0xf8))+w(2,1))
    def probe(self,name,x,y,rgb):
        self.probes.append(dict(name=name,x=x,y=y,expected=list(rgb)))
    def sample(self,name,ident_name,x,y,px=8,py=8):
        asset=ASSETS[ident_name]; raw=(TARGET/asset['filename']).read_bytes()
        off=py*asset['width']+px
        if asset['format']==1:
            value=raw[off]; rgb=[((value>>(2*i))&3)*85 for i in range(3)]
        else: rgb=list(raw[off*4:off*4+3])
        self.probe(name,x+px,y+py,rgb)


class Page:
    def __init__(self,title,commands):
        self.number=len(PAGES)+1; self.title=title; self.commands=commands; self.stages=[]
        PAGES.append(self)
    def stage(self,caption,draw_heading=True): return Stage(self,caption,draw_heading)


def basics():
    p=Page('LOAD AND PLOT','BUFFER 0/14; BITMAP &20/&21; PLOT &ED')
    s=p.stage('Original 34x34 images and independent 2x controls.')
    for col,tag in enumerate(('2','8')):
        x=48+col*248; s.label(x//8,10,'RGBA2222' if tag=='2' else 'RGBA8888',11)
        for row,chunked in enumerate((False,True)):
            y=128+row*112; ident=A+col*2+row
            s.load('axes'+tag,ident,int(chunked)); s.bmp(ident,x,y)
            s.sample('original '+tag+' chunk '+str(row),'axes'+tag,x,y)
        s.load('large'+tag,TMP); s.bmp(TMP,x+80,128)
        s.label(x//8,38,'TOP: single / BELOW: chunks',14)
    s.label(2,43,'2222: 1156 bytes. 8888: 4624 bytes. Both: 64 colours.')

    p=Page('BITMAP ADDRESSING','SELECT 0/&20; LOAD 1; SOLID BITMAP 2')
    s=p.stage('8-bit bitmap 0 aliases buffer 64000; high IDs are separate.')
    s.load('axes8',64000,2); s.load('axes8',A)
    for x,ident,legacy in ((48,64000,True),(208,64000,False),(368,A,False)):
        s.label(x//8,11,('8-BIT 0' if legacy else str(ident)),11)
        if legacy:s.raw(23,27,0,0)
        else:s.select(ident)
        s.plot(0xed,x,136); s.sample('address alias','axes8',x,136)
    s.select(B); s.bytes(bytes((23,27,2))+w(96,48)+bytes((85,170,255,255)))
    BUFFERS.add(B); s.bmp(B,48,256); s.probe('solid rectangle',80,280,(85,170,255))
    s.label(22,33,'Command 2 creates a solid RGBA rectangle.')

    p=Page('ALPHA AND CUTOUTS','RGBA2222 / RGBA8888: ZERO TRANSPARENT, NONZERO OPAQUE')
    s=p.stage('Opaque original, geometric cutout, then alpha-value bands.')
    for row,tag in enumerate(('2','8')):
        y=112+row*136; s.label(2,y//8-3,'RGBA'+('2222' if tag=='2' else '8888'),11)
        for col,name in enumerate(('axes','cut','alpha')):
            x=40+col*160; s.checker(x,y); s.load(name+tag,A+col); s.bmp(A+col,x+16,y+16)
        s.probe('zero alpha reveals checker '+tag,376,y+20,(170,85,0))
        s.probe('nonzero alpha visible '+tag,388,y+20,(255,255,0))
    s.label(2,43,'2222 alpha: 0/1/2/3/3; 8888 alpha: 0/1/64/128/255.')

    p=Page('BITMAP PLOT VARIANTS','PLOT &E8-&EF; ABSOLUTE / SIGNED RELATIVE')
    s=p.stage('FG colours / inverse / BG silhouette; empty move controls.')
    s.load('cut2',A); s.load('cut8',B)
    for row,ident in enumerate((A,B)):
        y=128+row*128
        for col,code in enumerate((0xed,0xee,0xef,0xe9,0xea,0xeb)):
            x=16+col*82; s.rect(x,y,x+64,y+64,7); s.select(ident)
            s.raw(18,0,128+11); s.gcol(15)
            if not code&4:s.plot(4,x+28,y+4); s.plot(code,-12,12)
            else:s.plot(code,x+16,y+16)
            s.label(x//8,(y-24)//8,f'&{code:02X}',11)
        s.select(ident); s.plot(0xe8,0,0); s.plot(0xec,480,y+80)
    s.label(2,43,'Relative panels use (-12,+12). &E8/&EC move only.')

    p=Page('EIGHT BITMAP PAINT MODES','GCOL 0..7 / PLOT &ED; RGB BITWISE OPERATIONS')
    for tag in ('2','8'):
        s=p.stage('RGBA'+('2222' if tag=='2' else '8888')+' over a known two-colour checker.')
        s.load('cut'+tag,A)
        for mode,caption in enumerate(('SET','OR','AND','XOR','INV','NO-OP','AND INV','OR INV')):
            x=16+(mode%4)*124; y=112+(mode//4)*128
            s.checker(x,y); s.label(x//8,(y-24)//8,f'{mode} {caption}',11)
            s.bmp(A,x+16,y+16,mode=mode)
            src=(0,255,0); dst=(170,85,0)
            funcs=(lambda a,b:a,lambda a,b:a|b,lambda a,b:a&b,lambda a,b:a^b,
                   lambda a,b:b^255,lambda a,b:b,lambda a,b:b&(~a&255),lambda a,b:b|(~a&255))
            s.probe('GCOL '+caption,x+24,y+24,tuple(funcs[mode](a,b) for a,b in zip(src,dst)))
        s.gcol(); s.label(2,43,'Each source has transparent holes; mode applies only to ink.')
        s=p.stage('XOR and inverse drawn twice restore; no-op preserves.')
        for i,mode in enumerate((3,4,5)):
            x=40+i*160; s.checker(x,144)
            s.bmp(A,x+16,160,mode=mode); s.bmp(A,x+16,160,mode=mode)
            s.probe('twice mode '+str(mode),x+24,168,(170,85,0))
        s.gcol()

    p=Page('BITMAP COMPOSITING','BITMAP OVER BITMAP: OR / AND / XOR; MANUAL BLITS')
    s=p.stage('Overlapping axes bitmaps on stripes; upper/lower order differs.')
    s.load('axes2',A); s.load('frame0_8',B)
    for row,reverse in enumerate((False,True)):
        for col,mode in enumerate((1,2,3)):
            x=32+col*160; y=112+row*128; s.checker(x,y,pattern='stripes')
            order=[(A,x+16,y+16),(B,x+28,y+24)]
            for ident,xx,yy in (order[::-1] if reverse else order):s.bmp(ident,xx,yy,mode=mode)
            s.label(x//8,(y-24)//8,('REV ' if reverse else '')+('OR','AND','XOR')[col],11)
    s=p.stage('Manual XOR blit drawn twice restores its background.')
    s.clear_art();s.checker(192,144); s.bmp(A,224,176,mode=3)
    s=p.stage('Second XOR removes it; then a SET blit at a new position.')
    s.bmp(A,224,176,mode=3); s.bmp(A,272,192)
    s.probe('XOR removed',232,184,(170,85,0))
    s=p.stage('Redrawing the background removes the manual SET blit.')
    s.checker(192,144); s.probe('manual underlay restored',280,200,(170,85,0))

    p=Page('DIRECT DRAW VERSUS PLOT','BITMAP 3 / PLOT &ED; CLIP, ORIGIN, GCOL, MATRIX')
    s=p.stage('DOC: direct draw bypasses clip. Stock VDP may retain it.')
    s.load('large2',A); s.load('cut8',B)
    for i,direct in enumerate((False,True)):
        x=48+i*248; s.outline(x,112,x+96,216); s.label(x//8,10,'DIRECT 3' if direct else 'PLOT ED',11)
        s.bytes(bytes((24,))+w(x,216,x+96,112))
        (s.direct if direct else s.bmp)(A,x+64,144)
        s.raw(26); s.probe('clip outside '+str(direct),x+104,160,(255,255,255) if direct else (0,0,0))
    s=p.stage('Direct drawing bypasses origin, logical units, XOR and scale.')
    s.clear_art()
    s.matrix(0); s.matrix(5,2,2); s.transform(M)
    s.raw(23,0,0xc0,1); s.bytes(bytes((29,))+w(300,200)); s.gcol(15,3)
    s.direct(B,80,144); s.select(B); s.plot(0xed,600,200)
    s.transform(); s.raw(26,23,0,0xc0,0); s.gcol()
    s=p.stage('Four screen edges; top/bottom samples occupy the right corners.')
    s.clear_art()
    s.raw(23,27,17)
    for x,y in ((-18,176),(496,176),(496,-18),(496,368)):s.direct(B,x,y)
    s.sample('top edge remains visible','cut8',496,-18,px=8,py=22)
    s.sample('bottom edge remains visible','cut8',496,368)

    p=Page('CAPTURE AND REPLOT','CAPTURE 1,n,0,0; / &21,id;0; INCLUSIVE CORNERS')
    s=p.stage('Capture the axes-plus-stripes rectangle through both ID forms.')
    s.checker(48,112); s.load('cut2',A); s.bmp(A,80,144)
    for x,ident,legacy in ((224,64001,True),(384,B,False)):
        s.plot(4,80,144); s.plot(4,113,177)
        if legacy:s.bytes(bytes((23,27,1,1,0,0,0)))
        else:s.bytes(bytes((23,27,33))+w(ident,0))
        BUFFERS.add(ident); s.bmp(ident,x,144)
        s.sample('capture interior','cut2',x,144)
    s.rect(80,272,80,272,15); s.plot(4,80,272); s.plot(4,80,272)
    s.bytes(bytes((23,27,33))+w(C,0)); BUFFERS.add(C); s.bmp(C,224,272)
    s.probe('one pixel capture',224,272,(255,255,255));s.probe('one pixel outside',225,272,(0,0,0))
    s.label(2,40,'The lower capture is exactly one pixel, not zero-by-zero.')

    p=Page('ADJUST STORED PIXEL BYTES','BUFFER 5: NOT / AND / OR / XOR; COPY 13')
    s=p.stage('Top: alpha preserved. Bottom: alpha deliberately modified.')
    s.load('axes2',A,3)
    for row in range(2):
        for col,op in enumerate((0,5,6,7)):
            ident=61020+row*4+col; x=24+col*124; y=120+row*128
            s.copy(ident,A)
            operand=bytes((0x3f if row else 0xcf,)) if op in (5,6) else bytes((0xc3 if row else 0x03,))
            s.bytes(buf(ident,5,bytes((op|0x40,))+w(0,1156)+(operand if op else b'')))
            if not row:s.bytes(buf(ident,5,b'\x46'+w(0,1156)+b'\xc0'))
            s.create(ident); s.checker(x,y); s.bmp(ident,x+16,y+16)
            s.label(x//8,(y-24)//8,('NOT','AND','OR','XOR')[col],11)
    s=p.stage('XOR each byte with a second buffer, twice: original returns.')
    s.upload(B,bytes([0x33])*1156); s.copy(C,A)
    for _ in range(2):s.bytes(buf(C,5,b'\xe7'+w(0,1156,B,0)))
    s.create(C); s.bmp(C,192,160); s.sample('buffer XOR round trip','axes2',192,160)

    p=Page('MASKS AND PACKED EXPANSION','FORMAT 2; BUFFER 72: 1/2/4 BPP, ROWS, MAPPINGS')
    s=p.stage('34-pixel masks use 5 bytes/row. Colour is captured at creation.')
    for i,col in enumerate((11,14)):
        s.gcol(col); s.load('mask',A+i); s.gcol(15); s.bmp(A+i,80+i*248,144)
    s.label(2,32,'Changing foreground to white does not recolour the mask.')
    s=p.stage('Expand packed pixels to RGBA2222, then explicitly create bitmap.')
    for i,bits in enumerate((1,2,4)):
        source=61030+i; target=61034+i; x=56+i*160
        s.load('packed'+str(bits),source,3)
        mapping=bytes((0 if k==0 else 0xc0|((k*7)&63)) for k in range(1<<bits))
        s.upload(MAP,mapping)
        s.bytes(buf(target,72,bytes((bits|8|(16 if i==1 else 0),))+w(source,34)+
                    (w(MAP) if i==1 else mapping)))
        s.create(target);s.checker(x,144);s.bmp(target,x+16,160)
        s.label(x//8,12,f'{bits} BPP '+('MAP BUFFER' if i==1 else 'INLINE MAP'),11)
    s.label(2,35,'Byte padding is discarded at width 34; index zero is clear.')


def matrices():
    p=Page('MATRIX IDENTITY AND SELECTION','BUFFER 32 OP 0/5; SYSTEM &96 BITMAP TRANSFORM')
    s=p.stage('Identity equals no transform; both source formats are paired.')
    s.load('axes2',A);s.load('axes8',B)
    for y,ident in ((128,A),(256,B)):
        s.transform();s.bmp(ident,64,y)
        s.matrix();s.transform(M);s.bmp(ident,224,y)
        s.sample('identity '+str(ident),'axes2',224,y)
    s=p.stage('Edit selected matrix to 2x; clear selection for original size.')
    s.clear_art();s.matrix(5,2,2)
    for y,ident in ((112,A),(248,B)):
        s.transform(M);s.bmp(ident,80,y);s.transform();s.bmp(ident,320,y)
    s.label(8,10,'SELECTED MATRIX',11);s.label(38,10,'SELECTION CLEARED',11)

    p=Page('SCALE AND REFLECT','MATRIX OP 5 XY SCALE / OP 4 COEFFICIENT MULTIPLY')
    for tag in ('2','8'):
        s=p.stage('RGBA'+('2222' if tag=='2' else '8888')+': 2x, half, stretched, X/Y/both reflections.')
        s.clear_art();s.load('axes'+tag,A)
        for i,(sx,sy,caption) in enumerate(((2,2,'2X'),(.5,.5,'HALF'),(2,1,'STRETCH'),
                                           (-2,2,'FLIP X'),(2,-2,'FLIP Y'),(-2,-2,'BOTH'))):
            left=24+(i%3)*168;top=128+(i//3)*136
            x=left+(68 if sx<0 else 0);y=top+(68 if sy<0 else 0)
            s.label(left//8,(top-24)//8,caption,11)
            s.matrix();s.matrix(5,sx,sy);s.transform(M);s.bmp(A,x,y)
            s.transform();s.marker(x,y)
    s=p.stage('OP 4 and uniform OP 5 both scale the existing translation.')
    s.clear_art()
    for i,op in enumerate((4,5)):
        s.matrix();s.matrix(6,20,12);s.matrix(op,*((2,) if op==4 else (2,2)))
        s.transform(M);s.bmp(A,80+i*248,160);s.transform();s.marker(80+i*248,160)
        s.label(8+i*31,12,'OP '+str(op),11)

    p=Page('DEGREES AND RADIANS','MATRIX OP 2 DEGREES / OP 3 RADIANS')
    for tag in ('2','8'):
        s=p.stage('RGBA'+('2222' if tag=='2' else '8888')+': degree row above equivalent radian row.')
        s.clear_art();s.load('axes'+tag,A)
        for row,op in enumerate((2,3)):
            for i,angle in enumerate((0,90,180,270,30)):
                x=64+i*96;y=152+row*152
                s.matrix();s.matrix(op,angle if op==2 else math.radians(angle));s.transform(M)
                s.bmp(A,x,y);s.transform();s.marker(x,y);s.label((x-24)//8,(y-64)//8,str(angle)+' DEG',11)
                if angle==0:s.sample('zero rotation','axes'+tag,x,y)
        s.label(2,43,'Yellow + is the plot anchor. Oblique edges are rasterized.')

    p=Page('TRANSLATION AND PIVOTS','MATRIX OP 6 PIXELS / 7 COORD UNITS / 12 BITMAP SIZE')
    s=p.stage('Top-left pivot at left; centred pivot via pixels / bitmap size.')
    s.load('axes2',A);s.load('axes8',B)
    for row,ident in enumerate((A,B)):
        for i,kind in enumerate(('TOP LEFT','PIXEL CENTRE','SIZE CENTRE')):
            x=88+i*168;y=144+row*144
            s.matrix()
            if i==1:s.matrix(6,-17,-17)
            if i==2:s.matrix(12,-.5,-.5,bitmap=ident)
            s.matrix(2,30);s.matrix(5,2,2)
            s.transform(M);s.bmp(ident,x,y);s.transform();s.marker(x,y)
            s.label((x-64)//8,(y-64)//8,kind,11)
    s=p.stage('Logical-coordinate translation differs from pixel translation.')
    s.clear_art();s.raw(23,0,0xc0,1)
    for i,op in enumerate((6,7)):
        s.matrix();s.matrix(op,80,80);s.transform(M);s.bmp(A,160+i*640,512)
    s.transform();s.raw(26,23,0,0xc0,0)
    s.label(4,12,'OP 6: 80 PIXELS',11);s.label(35,12,'OP 7: 80 LOGICAL UNITS',11)

    p=Page('SHEAR AND SKEW','MATRIX OP 8 SHEAR / 9 DEGREES / 10 RADIANS')
    for tag in ('2','8'):
        s=p.stage('RGBA'+('2222' if tag=='2' else '8888')+': X / Y / combined; positive and negative.')
        s.clear_art();s.load('large'+tag,A)
        for row,sign in enumerate((1,-1)):
            for col,(op,args,caption) in enumerate(((8,(.5,0),'SHEAR X'),(9,(0,20),'SKEW Y DEG'),
                                                   (10,(math.radians(20),math.radians(10)),'XY RAD'))):
                x=64+col*168;y=128+row*144
                s.outline(x-24,y-24,x+100,y+88)
                s.matrix();s.matrix(op,*(sign*v for v in args));s.transform(M);s.bmp(A,x,y)
                s.transform();s.marker(x,y);s.label((x-40)//8,(y-56)//8,caption,11)

    p=Page('COMPOSITION AND INVERSE','MATRIX OP 11 SIX COEFFICIENTS / OP 1 INVERSE')
    s=p.stage('Order matters: translate/rotate and scale/rotate pairs.')
    s.load('axes2',A);s.load('axes8',B)
    for row,ident in enumerate((A,B)):
        for i,ops in enumerate((((6,30,0),(2,30)),((2,30),(6,30,0)),
                                ((5,2,1),(2,30)),((2,30),(5,2,1)))):
            x=48+i*124;y=152+row*144
            s.matrix()
            for op,*args in ops:s.matrix(op,*args)
            s.transform(M);s.bmp(ident,x,y);s.transform();s.marker(x,y)
            s.label((x-24)//8,(y-64)//8,('T THEN R','R THEN T','S THEN R','R THEN S')[i],11)
    s=p.stage('Explicit coefficients equal composition; inverse pair is identity.')
    s.clear_art()
    s.matrix();s.matrix(6,24,12);s.matrix(5,2,2);s.transform(M);s.bmp(A,48,144)
    s.matrix(ident=N);s.matrix(11,2,0,48,0,2,24,ident=N);s.transform(N);s.bmp(B,208,144)
    s.matrix(ident=M);s.matrix(11,2,0,48,0,2,24);s.matrix(1)
    s.matrix(11,2,0,48,0,2,24);s.transform(M);s.bmp(A,400,144);s.transform()
    s.probe('composed translated sample',112,184,(0,255,0))
    s.probe('explicit translated sample',272,184,(0,255,0))
    s.sample('inverse round trip','axes2',400,144)
    for x,text in ((32,'COMPOSED'),(200,'EXPLICIT 6'),(368,'INVERSE PAIR')):s.label(x//8,12,text,11)

    p=Page('MATRIX PARAMETER FORMATS','FLOAT32 / FLOAT16 / FIXED32 / FIXED16; BUFFER ARGS')
    s=p.stage('The same exactly representable scale in four numeric formats.')
    s.load('axes2',A);s.load('axes8',B)
    formats=((0,struct.pack('<ff',1.5,.5),'FLOAT32'),(0x80,struct.pack('<ee',1.5,.5),'FLOAT16'),
             (0x48,struct.pack('<ii',384,128),'FIXED32'),(0xc8,struct.pack('<hh',384,128),'FIXED16'))
    for row,ident in enumerate((A,B)):
        for i,(fmt,raw,caption) in enumerate(formats):
            x=32+i*124;y=136+row*128;s.matrix();s.matrix(5,fmt=fmt,raw=raw)
            s.transform(M);s.bmp(ident,x,y);s.transform();s.label(x//8,(y-32)//8,caption,11)
    s=p.stage('Buffer-fetched args / separate formats / signed negative shift.')
    s.clear_art();s.upload(TMP,struct.pack('<ff',1.5,.5))
    s.matrix();s.matrix(5|0x20,fmt=0,raw=w(TMP,0));s.transform(M);s.bmp(A,56,160)
    s.matrix();s.bytes(buf(M,32,bytes((5|0x40,0))+struct.pack('<f',1.5)+bytes((0xc8,))+struct.pack('<h',128)))
    s.transform(M);s.bmp(B,224,160)
    s.matrix();s.matrix(6,fmt=0xdf,raw=struct.pack('<hh',-8,8));s.transform(M);s.bmp(A,408,160)
    s.transform();s.marker(408,160)
    s.label(4,12,'BUFFER FETCH',11);s.label(26,12,'MIXED FORMATS',11);s.label(48,12,'SHIFT -1',11)

    p=Page('BAKE TRANSFORMED BITMAPS','BUFFER 40: FIXED / AUTO / EXPLICIT / AUTOTRANSLATE')
    for tag in ('2','8'):
        s=p.stage('Source RGBA'+('2222' if tag=='2' else '8888')+'; every baked result is RGBA2222.')
        s.clear_art();s.load('axes'+tag,A)
        for i,(options,caption) in enumerate(((0,'FIXED 34'),(1,'AUTO SIZE'),(5,'AUTO + SHIFT'),(6,'EXPLICIT 72'))):
            ident=61040+i;x=24+i*124
            s.matrix();s.matrix(2,30);s.matrix(5,1.5,1.5)
            s.bake(A,ident,options,(72,72) if options&2 else None)
            s.transform();s.bmp(ident,x+16,144);s.label(x//8,12,caption,11)
        s.matrix();s.matrix(5,-2,2);s.bake(A,61044,5);s.bmp(61044,96,256)
        s.transform(M);s.bmp(A,352,256);s.transform()
        s.label(4,29,'BAKED REFLECTION',11);s.label(34,29,'LIVE REFLECTION',11)

    p=Page('REUSE AND CONTEXT RESTORE','BUFFER CALL 1; CONTEXT &C8 SAVE/RESTORE; GLOBAL DATA')
    s=p.stage('Direct / buffered / restored context should draw the same motif.')
    s.load('axes2',A);s.load('axes8',B);s.matrix();s.matrix(5,2,2);s.transform(M);s.select(A)
    motif=bytes((25,0xed))+w(0,0)
    s.upload(C,motif)
    for i in range(3):
        s.bytes(bytes((29,))+w(48+i*168,144))
        if i==0:s.plot(0xed,0,0)
        if i==1:s.bytes(buf(C,1))
        if i==2:
            s.raw(23,0,0xc8,3);s.select(B);s.transform();s.gcol(11,3)
            s.bytes(bytes((29,))+w(0,0));s.bytes(bytes((24,))+w(0,350,32,300))
            s.raw(23,0,0xc8,4);s.plot(0xed,0,0)
    s.transform();s.raw(26)
    s.label(4,12,'DIRECT',11);s.label(24,12,'BUFFER CALL',11);s.label(44,12,'RESTORED',11)
    s=p.stage('Matrix bytes are global: restoring context does not undo edits.')
    s.clear_art();s.select(A);s.transform(M);s.raw(23,0,0xc8,3)
    s.matrix();s.matrix(5,3,1);s.raw(23,0,0xc8,4);s.bmp(A,192,176);s.transform()
    s.label(2,34,'Expected: wide 3x1 axes, not the old 2x2 matrix.')


def sprites():
    p=Page('SOFTWARE SPRITE LIFECYCLE','SPRITE 4/5/6/7/11/12/20/&26; RGBA AND MASK FRAMES')
    s=p.stage('API: RGBA2222 / RGBA8888 / mask. RAW: RGBA8888 control.')
    s.load('cut2',64000);s.load('cut8',B);s.gcol(14);s.load('mask',C)
    for n,caption in enumerate(('API 2222','API 8888','API MASK','RAW 8888')):
        s.checker(16+n*124,144);s.label((16+n*124)//8,12,caption,11)
    s.sprite(0,[],32,176);s.call('vdu_sprite_add_bmp',a=0)
    s.sprite(1,[B],156,176);s.sprite(2,[C],280,176)
    s.raw(23,27,4,3,23,27,5,23,27,38);s.bytes(w(B))
    s.raw(23,27,18,0,23,27,20,23,27,13);s.bytes(w(404,176));s.raw(23,27,11)
    s.activate(4)
    s.sample('wrapper software frame','cut8',156,176)
    s.sample('literal software frame','cut8',404,176)
    s=p.stage('Hide the middle sprite; its definition and frame remain.')
    s.call('vdu_sprite_select',a=1);s.call('vdu_sprite_hide');s.call('vdu_sprite_update')
    s.probe('hidden middle background',164,184,(170,85,0))
    s=p.stage('Show middle again; clear all frames of the left sprite.')
    s.call('vdu_sprite_show');s.call('vdu_sprite_select',a=0);s.call('vdu_sprite_clear_frames');s.call('vdu_sprite_update')

    p=Page('SPRITE POSITION HELPERS','MOVE 13 ABS / 14 REL; LIBRARY FIXED 16.8 ADAPTERS')
    s=p.stage('Absolute / relative / fixed16.8 controls start in one row.')
    s.load('cut2',A);s.load('cut8',B)
    for n,ident in enumerate((A,B,A)):
        s.checker(32+n*168,144);s.sprite(n,[ident],64+n*168,160)
    s.activate(3)
    for step,(dx,dy) in enumerate(((24,32),(-40,16),(0,0),(16,-48))):
        s=p.stage(f'Movement step {step+1}: delta ({dx:+d},{dy:+d}); all paths match.')
        # Absolute control accumulates the same signed path.
        if step==0:absx,absy=64,160
        absx+=dx;absy+=dy
        s.call('vdu_sprite_select',a=0);s.call('vdu_sprite_move_abs',bc=absx,de=absy)
        s.call('vdu_sprite_select',a=1);s.call('vdu_sprite_move_rel',bc=dx,de=dy)
        s.call('vdu_sprite_select',a=2)
        if step==0:s.call('vdu_sprite_move_abs168',bc=(absx+336)*256+128,de=absy*256+192)
        else:s.call('vdu_sprite_move_rel168',bc=dx*256,de=dy*256)
        s.call('vdu_sprite_update')
    s=p.stage('Sprite positions ignore logical graphics coordinates and origin.')
    s.raw(23,0,0xc0,1);s.bytes(bytes((29,))+w(400,300))
    for n,(x,y) in enumerate(((-16,192),(496,192),(496,352))):
        s.call('vdu_sprite_select',a=n);s.call('vdu_sprite_move_abs',bc=x,de=y)
    s.call('vdu_sprite_update');s.raw(26,23,0,0xc0,0)

    p=Page('DEFERRED SOFTWARE UPDATE','MOVE 13/14; EXPLICIT UPDATE 15; DRAWING TRIGGER')
    s=p.stage('Key 1: stage move / key 2: update / key 3: move+draw / key 4: hide.')
    s.load('cut2',A);s.checker(80,144);s.checker(208,144)
    s.sprite(0,[A],112,176);s.activate(1)
    s.label(10,12,'OLD X=112',11);s.label(30,12,'NEW X=240',11)
    s=p.stage('Move submitted, no drawing or explicit update.',False)
    s.call('vdu_sprite_select',a=0);s.call('vdu_sprite_move_abs',bc=240,de=176)
    s=p.stage('Explicit command 15 reveals the pending move.',False)
    s.call('vdu_sprite_update')
    s=p.stage('Move to old position; a line draw triggers refresh.',False)
    s.call('vdu_sprite_move_abs',bc=112,de=176);s.line(80,280,336,280,11)
    s=p.stage('Hide and update restore the complete underlay.',False)
    s.call('vdu_sprite_hide');s.call('vdu_sprite_update')
    s.probe('old underlay',120,184,(170,85,0));s.probe('new underlay',248,184,(170,85,0))

    p=Page('FRAME NAVIGATION AND REPLACEMENT','FRAME 8/9/10 / REPLACE 21/&35 / ADD 6/&26')
    s=p.stage('Frame zero; two sprites mix RGBA formats and frame dimensions.')
    for name,ident in (('cut2',A),('frame0_8',B),('wide2',C),('frame2_8',64001)):
        s.load(name,ident)
    s.sprite(0,[A,B,C],96,176);s.sprite(1,[A,B,C],320,176);s.activate(2)
    for caption,name,arg in (('Next -> frame one','vdu_sprite_next_frame',0),
                              ('Next -> wider frame two','vdu_sprite_next_frame',0),
                              ('Next wraps to frame zero','vdu_sprite_next_frame',0),
                              ('Previous wraps to frame two','vdu_sprite_prev_frame',0),
                              ('Select frame one explicitly','vdu_sprite_select_frame',1)):
        s=p.stage(caption)
        for n in (0,1):s.call('vdu_sprite_select',a=n);s.call(name,a=arg)
        s.call('vdu_sprite_update')
    s=p.stage('Replace left with legacy bitmap 1; right with high-ID bitmap A.')
    s.call('vdu_sprite_select',a=0);s.call('ext_sprite_replace8',a=1)
    s.call('vdu_sprite_select',a=1);s.call('ext_sprite_replace16',hl=A);s.call('vdu_sprite_update')
    s=p.stage('Invalid frame 99 and undefined bitmap are ignored; then next.')
    s.call('vdu_sprite_select_frame',a=99);s.call('vdu_sprite_add_buff',hl=61999)
    s.call('vdu_sprite_next_frame');s.call('vdu_sprite_update')

    p=Page('SOFTWARE SPRITE PAINT MODES','SPRITE 18 GCOL 0..7 / REFRESH / HIDE RESTORES')
    for tag in ('2','8'):
        s=p.stage('RGBA'+('2222' if tag=='2' else '8888')+': eight paint modes, checker underlay.')
        s.call('vdu_sprite_reset');s.clear_art();s.load('cut'+tag,A)
        for mode,name in enumerate(('SET','OR','AND','XOR','INV','NO-OP','AND INV','OR INV')):
            x=16+(mode%4)*124;y=112+(mode//4)*128
            s.checker(x,y);s.label(x//8,(y-24)//8,f'{mode} {name}',11)
            s.sprite(mode,[A],x+16,y+16,mode=mode)
        s.activate(8)
        funcs=(lambda a,b:a,lambda a,b:a|b,lambda a,b:a&b,lambda a,b:a^b,
               lambda a,b:b^255,lambda a,b:b,lambda a,b:b&(~a&255),lambda a,b:b|(~a&255))
        for mode in range(8):
            x=16+(mode%4)*124;y=112+(mode//4)*128
            s.probe('visible sprite GCOL '+str(mode),x+24,y+24,
                    tuple(funcs[mode](a,b) for a,b in zip((0,255,0),(170,85,0))))
        s=p.stage('Repeated update should leave all stationary sprite pixels stable.')
        for _ in range(3):s.call('vdu_sprite_update')
        s=p.stage('Move all eight together; old positions recover without trails.')
        for n in range(8):
            s.call('vdu_sprite_select',a=n);s.call('vdu_sprite_move_rel',bc=40,de=16)
        s.call('vdu_sprite_update')
        s=p.stage('Hide all sprites; each checkerboard must be completely restored.')
        for n in range(8):s.call('vdu_sprite_select',a=n);s.call('vdu_sprite_hide')
        s.call('vdu_sprite_update')
        for n in range(8):
            x=16+(n%4)*124;y=112+(n//4)*128
            s.probe('restored GCOL '+str(n),x+24,y+24,(170,85,0))

    p=Page('SOFTWARE OVERLAP AND ACTIVATION','ACTIVE PREFIX 7; OVERLAP / HIDE / BACKGROUND REDRAW')
    s=p.stage('Four overlapping software sprites; higher IDs appear above.')
    for n,name in enumerate(('large2','large8','frame0_2','wide8')):
        s.load(name,A+n);s.sprite(n,[A+n],160+n*24,144+n*24)
    s.activate(4)
    s=p.stage('Activate only IDs 0..1; the other two leave the active prefix.')
    s.activate(2)
    s=p.stage('Activate four again; hide ID 1 within the active prefix.')
    s.activate(4);s.call('vdu_sprite_select',a=1);s.call('vdu_sprite_hide');s.call('vdu_sprite_update')
    s=p.stage('Show ID 1; move front sprite and draw a stripe under the group.')
    s.call('vdu_sprite_show');s.call('vdu_sprite_select',a=3);s.call('vdu_sprite_move_rel',bc=-72,de=24)
    s.rect(128,176,336,184,14);s.call('vdu_sprite_update')
    s=p.stage('Hide group: the newly drawn background stripe remains intact.')
    s.activate(0);s.probe('new underlay stripe',200,180,(0,255,255))

    p=Page('HARDWARE SPRITE BASICS','FLAG &F8,2;1; / HARDWARE 19 / SOFTWARE 20')
    s=p.stage('Hardware RGBA2222 and RGBA8888: opaque then cutout frames.')
    s.hardware()
    for n,name in enumerate(('axes2','axes8','cut2','cut8')):
        s.load(name,A+n);s.checker(16+n*124,144);s.sprite(n,[A+n],40+n*124,176,hw=True)
    s.call('vdu_sprite_activate',a=4)
    s=p.stage('Move without command 15: hardware positions update immediately.')
    for n in range(4):s.call('vdu_sprite_select',a=n);s.call('vdu_sprite_move_rel',bc=16,de=40)
    s=p.stage('Hide then show hardware IDs 0 and 1; no explicit refresh.')
    for n in (0,1):s.call('vdu_sprite_select',a=n);s.call('vdu_sprite_hide')
    s=p.stage('Show them; deactivate/convert/re-activate ID 3 as software.')
    s.call('vdu_sprite_activate',a=0)
    for n in (0,1):s.call('vdu_sprite_select',a=n);s.call('vdu_sprite_show')
    s.call('vdu_sprite_select',a=3);s.call('ext_sprite_software');s.call('vdu_sprite_move_abs',bc=400,de=272)
    s.activate(4)

    p=Page('MIXED SPRITE LAYERS','HARDWARE ABOVE SOFTWARE AND GRAPHICS; HIGH HW ID ON TOP')
    s=p.stage('HW 0 and HW 2 overlap SW 1. Transparent holes reveal lower layers.')
    s.hardware();s.load('large2',A);s.load('large8',B);s.load('cut2',C)
    s.checker(160,144);s.checker(288,144)
    s.sprite(0,[A],184,160,hw=True);s.sprite(1,[B],208,184);s.sprite(2,[C],232,208,hw=True);s.activate(3)
    s=p.stage('Draw a cyan stripe now: both hardware sprites remain above it.')
    s.rect(128,208,384,224,14)
    s=p.stage('Hide top hardware ID 2 to reveal the next layer.')
    s.call('vdu_sprite_select',a=2);s.call('vdu_sprite_hide')
    s=p.stage('Deactivate/convert/re-activate: IDs 0 and 2 become software.')
    s.call('vdu_sprite_activate',a=0)
    s.call('ext_sprite_software');s.call('vdu_sprite_show')
    s.call('vdu_sprite_select',a=0);s.call('ext_sprite_software');s.activate(3)

    p=Page('HARDWARE PAINT EXCEPTIONS','GCOL 18 DEMOTES TO SW; 18,3 THEN 19 = HW XOR (2222)')
    s=p.stage('Top row: RGBA2222. Bottom: RGBA8888. HW modes SET/XOR/AND/OR.')
    s.hardware();s.load('cut2',A);s.load('cut8',B)
    for row,ident in enumerate((A,B)):
        for col,mode in enumerate((0,3,2,1)):
            x=16+col*124;y=112+row*128;n=row*4+col
            s.checker(x,y);s.label(x//8,(y-24)//8,('SET','XOR','AND->SET','OR->SET')[col],11)
            s.sprite(n,[ident],x+16,y+16,hw=True,mode=mode)
    s.call('vdu_sprite_activate',a=8)
    s=p.stage('Command 18 alone demotes all sprites to software paint modes.')
    s.call('vdu_sprite_activate',a=0)
    for n in range(8):s.call('vdu_sprite_select',a=n);s.call('vdu_sprite_set_gcol',a=(0,3,2,1)[n%4])
    s.activate(8)
    s=p.stage('Select hardware again: only RGBA2222 XOR retains non-SET mode.')
    s.call('vdu_sprite_activate',a=0)
    for n in range(8):s.call('vdu_sprite_select',a=n);s.call('ext_sprite_hardware')
    s.activate(8)

    p=Page('TRANSFORMED SPRITE FRAMES','BUFFER 40 BAKED RGBA2222 FRAMES / HW AND SW ANIMATION')
    s=p.stage('Fixed 72x72 canvas / fitted frames / independent RGBA8888 control.')
    s.hardware();s.load('axes2',A);s.load('axes8',B)
    fixed=[];tight=[];host=[]
    for i,angle in enumerate((0,90,180,270)):
        s.matrix();s.matrix(6,-17,-17);s.matrix(2,angle);s.matrix(6,36,36)
        f=61050+i;t=61054+i;h=61058+i
        s.bake(A,f,2,(72,72));fixed.append(f)
        s.matrix();s.matrix(2,angle);s.bake(B,t,5);tight.append(t)
        s.load('frame'+str(i)+'_8',h);host.append(h)
    for n,(frames,x,y,hw) in enumerate(((fixed,64,112,False),(tight,248,128,False),(host,416,128,False),
                                       (fixed,64,248,True),(tight,248,264,True),(host,416,264,True))):
        s.sprite(n,frames,x,y,hw=hw)
    s.activate(6);s.matrix();s.matrix(5,3,3);s.transform(M)
    s.label(2,43,'Live PLOT scale 3x is selected; sprite frames keep their sizes.')
    for i in range(1,5):
        s=p.stage(f'Next frame {i}: fixed pivot / fitted dimensions / host control.')
        for n in range(6):s.call('vdu_sprite_select',a=n);s.call('vdu_sprite_next_frame')
        s.call('vdu_sprite_update')
    s.transform()

    p=Page('BOUNDED SPRITE POPULATION','1 / 2 / 4 / 8 / 16 SPRITES; FORMAT / BACKEND / SCANLINES')
    for hw,tag in ((False,'2'),(False,'8'),(True,'2'),(True,'8')):
        s=p.stage(('HARDWARE' if hw else 'SOFTWARE')+' RGBA'+('2222' if tag=='2' else '8888')+': shared frames; step population.')
        s.call('vdu_sprite_reset');s.clear_art();s.hardware();s.load('axes'+tag,A)
        for n in range(16):s.sprite(n,[A],32+(n%8)*60,128+(n//8)*112,hw=hw)
        s.activate(1)
        for count in (2,4,8,16):
            s=p.stage(f'{count} active; two aligned scanline groups.')
            s.activate(count)
        s=p.stage('Sixteen staggered sprites; move all then refresh once.')
        for n in range(16):
            s.call('vdu_sprite_select',a=n);s.call('vdu_sprite_move_abs',bc=24+(n%8)*60,de=88+n*15)
        s.call('vdu_sprite_update')
    s=p.stage('Distinct frames and four modest 68x68 hardware sprites.')
    s.call('vdu_sprite_reset');s.clear_art()
    for n in range(4):
        s.load('large'+('2' if n%2==0 else '8'),61070+n)
        s.sprite(n,[61070+n],40+n*120,176,hw=True)
    s.activate(4)

    p=Page('SHARED FRAME LIFECYCLE','SHARE / REPLACE / HIDE-DETACH / RELOAD / REBIND')
    s=p.stage('Two software and two hardware sprites share one axes bitmap.')
    s.hardware();s.load('cut2',A);s.load('frame1_8',B)
    for n in range(4):s.checker(16+n*124,144);s.sprite(n,[A],40+n*124,176,hw=n>=2)
    s.activate(4)
    s=p.stage('Replace only sprite 0 frame; three other bindings stay unchanged.')
    s.call('vdu_sprite_select',a=0);s.call('ext_sprite_replace16',hl=B);s.call('vdu_sprite_update')
    s=p.stage('Hide and detach all frames before recreating the shared bitmap.')
    for n in range(4):
        s.call('vdu_sprite_select',a=n);s.call('vdu_sprite_hide');s.call('vdu_sprite_clear_frames')
    s.call('vdu_sprite_update');s.load('frame2_2',A)
    s=p.stage('Rebind shared replacement and show all four sprites.')
    for n in range(4):s.sprite(n,[A],40+n*124,176,hw=n>=2)
    s.activate(4)
    s=p.stage('Reload original safely; compare four original bindings again.')
    s.call('vdu_sprite_reset');s.load('cut2',A)
    for n in range(4):s.sprite(n,[A],40+n*124,176,hw=n>=2)
    s.activate(4)

    p=Page('RESET AND RERUN','SPRITE RESET 17 / BITMAP+SPRITE RESET 16 / OWNED CLEANUP')
    s=p.stage('Two sprites and a static bitmap before reset.')
    s.hardware();s.load('cut2',A);s.load('cut8',B)
    s.sprite(0,[A],96,176);s.sprite(1,[B],320,176,hw=True);s.activate(2);s.bmp(A,224,288)
    s=p.stage('Sprite-only reset: sprites disappear; bitmap definitions remain.')
    s.call('vdu_sprite_reset');s.bmp(A,96,176);s.bmp(B,320,176)
    s.sample('bitmap retained after reset17','cut2',96,176)
    s=p.stage('Reset 16 clears definitions/screen; recreate from retained bytes.')
    s.call('vdu_sprite_bmp_reset')
    s.label(2,0,'BITMAPS / BSP-32 - RESET AND RERUN',15)
    s.label(2,2,'RESET 16 RETAINS BUFFER BYTES',14)
    s.label(2,4,'Recreated bitmaps below were not reloaded from SD.',15)
    s.label(2,46,'Key: finish. ESC: clear and return to MOS.',15)
    s.create(A,34,34,1);s.create(B,34,34,0);s.bmp(A,96,176);s.bmp(B,320,176)
    s.sample('bitmap recreated after reset16','cut2',96,176)
    s.sample('rgba8 recreated after reset16','cut8',320,176)
    s.label(2,36,'Suite complete. Rendering observations are separate from PASS.')
    s.label(2,39,'A second launch must start cleanly with no stale sprites.')


def emit():
    assert len(PAGES)==32
    lines=['; Generated, packed descriptors; see bitmap_suite.py and validate_bitmaps.py.',
           'bitmap_calls:']
    lines += ['    dl '+name for name in CALLS]
    lines += ['asset_table:']
    for asset in ASSETS.values():
        lines += [f'    dl asset_path_{asset["index"]},{asset["length"]}',
                  f'    dw {asset["width"]},{asset["height"]}',f'    db {asset["format"]}']
    for asset in ASSETS.values():
        lines += [f'asset_path_{asset["index"]}:',f'    asciz "assets/bitmaps/{asset["filename"]}"']
    lines += ['page_table:']
    for page in PAGES:lines += [f'    dl bsp{page.number:02}_stages',f'    db {len(page.stages)}']
    catalog=[]
    for page in PAGES:
        lines += [f'bsp{page.number:02}_stages:']
        for i,s in enumerate(page.stages,1):
            name=f'bsp{page.number:02}_{i:02}'
            lines += [f'    dl {name}_program,{name}_probes',f'    db {len(s.probes)}']
        entry=dict(page=page.number,title=page.title,commands=page.commands,stages=[])
        for i,s in enumerate(page.stages,1):
            if s.draw_heading:s.raw(23,0,0xca)
            s.drain();name=f'bsp{page.number:02}_{i:02}';data=bytearray()
            for action in s.actions:
                if action['op']=='vdu':
                    raw=bytes.fromhex(action['hex']);data+=b'\x01'+w(len(raw))+raw
                elif action['op']=='call':
                    data+=bytes((2,CALLS.index(action['name']),action['a']))
                    data+=u24(action['bc'])+u24(action['de'])+u24(action['hl'])
                else:
                    data+=bytes((3,ASSETS[action['asset']]['index']))+w(action['ident'])+bytes((action['mode'],))
            data+=b'\x00'
            probes=b''.join(bytes((23,0,0x84))+w(p['x'],p['y'])+bytes(p['expected']) for p in s.probes)
            (BUILD/f'{name}.vm').write_bytes(data);(BUILD/f'{name}.probes').write_bytes(probes)
            lines += [f'{name}_program:',f'    incbin "{name}.vm"',
                      f'{name}_probes:',f'    incbin "{name}.probes"']
            entry['stages'].append(dict(name=name,caption=s.caption,actions=s.actions,probes=s.probes,
                                        quiet=not s.draw_heading))
        catalog.append(entry)
    cleanup=bytes((23,27,7,0,23,27,17,23,0,0x96,1))+w(65535)
    for ident in sorted(BUFFERS):cleanup+=buf(ident,2)
    cleanup+=bytes((23,0,0xf8))+w(1,0)+bytes((23,0,0xf8))+w(2,0)
    cleanup+=bytes((4,20,26,23,0,0xc0,0,23,1,0,18,0,128))
    (BUILD/'bitmaps-cleanup.vdu').write_bytes(cleanup)
    lines += ['cleanup_commands:','    incbin "bitmaps-cleanup.vdu"','cleanup_commands_end:']
    (BUILD/'bitmaps-data.inc').write_text('\n'.join(lines)+'\n')
    (BUILD/'bitmaps-catalog.json').write_text(json.dumps(dict(pages=catalog,calls=CALLS,
        buffers=sorted(BUFFERS),assets=list(ASSETS.values())),indent=2)+'\n')
    print(f'Generated 32 pages / {sum(len(p.stages) for p in PAGES)} keypress stages.')


def main():
    global ASSETS
    ASSETS=build(); BUILD.mkdir(exist_ok=True)
    basics(); matrices(); sprites(); emit()


if __name__ == '__main__': main()
