"""Authorized SHP-03..24 command fixtures; all pixels are drawn by the VDP."""
import struct

BITMAP, CAPTURE, MATRIX, MOTIF = range(60000, 60004)
OWNED_BUFFERS = (BITMAP, CAPTURE, MATRIX, MOTIF)


def words(*values):
    return struct.pack('<' + 'H' * len(values), *(v & 65535 for v in values))


def buffered(p, ident, command, data=b''):
    p.data.extend(bytes((23, 0, 0xA0)) + words(ident) + bytes((command,)) + data)


def upload(p, ident, data):
    buffered(p, ident, 2)
    buffered(p, ident, 0, words(len(data)) + data)
    p.resources.add(ident)


def select_bitmap(p, ident):
    p.data.extend(bytes((23, 27, 0x20)) + words(ident))


def matrix(p, operation, *args):
    p.data.extend(bytes((23, 0, 0xF8)) + words(1, 1))
    buffered(p, MATRIX, 32, bytes((operation,)) +
             (b'\x00' + struct.pack('<' + 'f' * len(args), *args) if args else b''))
    p.resources.add(MATRIX)
    p.transformed = True


def transform(p, ident=MATRIX):
    p.data.extend(bytes((23, 0, 0x96, 1)) + words(ident))


def enlarge(p, bounds, target, scale=8):
    p.plot(4, *bounds[:2]); p.plot(4, *bounds[2:])
    p.data.extend(bytes((23, 27, 0x21)) + words(CAPTURE, 0))
    p.resources.add(CAPTURE)
    select_bitmap(p, CAPTURE)
    matrix(p, 0); matrix(p, 5, scale, scale); transform(p)
    p.plot(0xED, *target)
    p.flush()
    transform(p, 65535)


def bitmap(p):
    # Asymmetric 24x24 arrow, transparent corners, white shaft and coloured tip.
    data = bytearray()
    for y in range(24):
        for x in range(24):
            opaque = (2 <= x < 13 and 9 <= y < 15) or (9 <= x <= 21 and abs(y-12) <= 21-x)
            data.append((0xFF if x < 13 else 0xCC) if opaque else 0)
    upload(p, BITMAP, data)
    select_bitmap(p, BITMAP)
    p.data.extend(bytes((23, 27, 0x21)) + words(24, 24) + b'\x01')


def page_three(P):
    p = P('SHAPES / SHP-03 - LINE ENDPOINTS',
          'PLOT &05 / &0D / &25 / &2D; CAPTURE + SCALE',
          'Right: an 8x capture of the actual nine-pixel line.')
    for i, (code, caption, first, last) in enumerate((
        (5, 'BOTH ENDS', True, True), (13, 'OMIT FINAL', True, False),
        (37, 'OMIT FIRST', False, True), (45, 'OMIT BOTH', False, False))):
        y = 96 + i * 48
        p.label(2, y//8, f'&{code:02X} {caption}', 11)
        p.colour(15); p.plot(4, 200, y); p.plot(code, 208, y)
        p.probe(caption+' first', 200, y, first)
        p.probe(caption+' last', 208, y, last)
        p.probe(caption+' middle', 204, y, True)
        enlarge(p, (198, y-1, 210, y+1), (320, y-8))
    p.label(2, 36, 'XOR JOINS: both ends / omit first', 14)
    for y, code in ((312, 5), (332, 37)):
        p.colour(15, 3); p.line((200,y),(240,y))
        p.plot(code,280,y)
        p.probe('XOR shared vertex '+str(code),240,y,code==37)
    p.label(2, 39, 'BOTH: gap'); p.label(2, 41, 'OMIT: joined')
    p.save('shp03')


def page_four(P):
    p = P('SHAPES / SHP-04 - DOTS AND DASHES',
          'VDU 23,6 PATTERN; &F2 LENGTH; PLOT &10-&3F',
          'Compare one line with two joined segments at right.')
    for i,(code,length,caption) in enumerate(((0x15,8,'BOTH / RESTART'),
            (0x1D,12,'OMIT END / RESTART'),(0x35,5,'OMIT FIRST / CONTINUE'),
            (0x3D,0,'OMIT BOTH / CONTINUE'))):
        y=104+i*64
        p.label(2,y//8-3,f'&{code:02X} {caption}, LEN {length}',11)
        p.data.extend((23,6,0xF0,0xAA,0xCC,0x33,0xF0,0x0F,0xAA,0x55))
        p.data.extend((23,0,0xF2,length))
        p.colour(15); p.plot(4,32,y); p.plot(code,224,y)
        p.plot(4,280,y); p.plot(code,317,y); p.plot(code,480,y)
        p.colour(7); p.line((317,y+8),(317,y+15))
        if i==0:
            p.probe('first dash on',33,y,True); p.probe('first dash off',37,y,False)
    p.label(2,42,'Length 0 restores the default alternating-dot pattern.',14)
    p.save('shp04')


def page_five(P):
    p=P('SHAPES / SHP-05 - LINE THICKNESS','VDU 23,23,n; SOLID LINE, CIRCLE, FILLED RECTANGLE',
        'Widths 1, 2, 4, 8. Filled controls keep the same size.')
    for i,width in enumerate((1,2,4,8)):
        x=24+i*124
        p.label(x//8,9,f'WIDTH {width}',11)
        p.data.extend((23,23,width)); p.colour(11)
        p.line((x+8,120),(x+80,176))
        p.colour(14); p.circle((x+44,236),32)
        p.colour(15); p.rect(x+20,300,x+68,324)
        p.probe('filled control '+str(width),x+44,310,True)
        p.probe('control exterior '+str(width),x+19,310,False)
    p.save('shp05')


def page_six(P):
    p=P('SHAPES / SHP-06 - TRIANGLES','PLOT &55 TRIANGLE FILL; LINES; GCOL 3 XOR FAN',
        'Compare outlines and fills; the XOR fan has no cracks.')
    for shift,filled,reverse in ((0,False,False),(160,True,False),(320,True,True)):
        p.label((16+shift)//8,9,('OUTLINE','FILL CW','FILL CCW')[shift//160],11)
        pts=[(32+shift,192),(144+shift,192),(88+shift,96)]
        if reverse: pts.reverse()
        p.colour(14 if filled else 15); p.polygon(pts,0x55 if filled else None)
    p.label(2,28,'THIN TRIANGLE',11); p.colour(11)
    p.polygon([(32,300),(184,304),(112,310)],0x55)
    p.label(34,28,'XOR FAN',11); p.colour(15,3)
    corners=[(288,248),(464,248),(464,336),(288,336)]
    for a,b in zip(corners,corners[1:]+corners[:1]): p.polygon([(376,292),a,b],0x55)
    p.probe('XOR fan interior',350,280,True)
    p.probe('XOR fan outside',280,280,False)
    p.save('shp06')


def page_seven(P):
    p=P('SHAPES / SHP-07 - RECTANGLES','PLOT &65 / &61 FILLED RECTANGLE; LINE OUTLINES',
        'Opposite-corner order and relative endpoints agree.')
    for i,(code,reverse,caption) in enumerate(((None,False,'OUTLINE'),(0x65,False,'ABS FILL'),
            (0x65,True,'REVERSED'),(0x61,False,'REL FILL'))):
        x=24+i*124; p.label(x//8,10,caption,11); p.colour(15)
        if code is None: p.outline(x,112,x+88,216)
        else:
            a,b=(x,112),(x+88,216)
            if reverse:a,b=b,a
            p.plot(4,*a); p.plot(code,*(b if code&4 else (b[0]-a[0],b[1]-a[1])))
        p.probe(caption+' interior',x+44,164,code is not None)
        p.probe(caption+' corner',x,112,True)
    p.label(2,32,'ONE PIXEL WIDE / ONE PIXEL HIGH',14); p.colour(15)
    p.rect(96,280,96,328); p.rect(224,304,464,304)
    for x,y,v in ((96,300,True),(95,300,False),(340,304,True),(340,303,False)):
        p.probe('degenerate rectangle',x,y,v)
    p.save('shp07')


def page_eight(P):
    p=P('SHAPES / SHP-08 - PARALLELOGRAMS','PLOT &75 / &71: THREE CORNERS; FIRST/THIRD OPPOSE',
        'Filled shapes match the outlined four-corner references.')
    for row,lean in enumerate((32,-32)):
        y=128+row*136
        pts=[(48,y+64),(160,y+64),(160+lean,y),(48+lean,y)]
        p.colour(15); p.polygon(pts)
        p.label(2,(y-40)//8,'OUTLINE',11)
        p.label(34,(y-40)//8,'ABS FILL' if row==0 else 'REL FILL',11)
        a,b,c=[(x+248,yy) for x,yy in pts[:3]]
        p.colour(14); p.plot(4,*a); p.plot(4,*b)
        p.plot(0x75 if row==0 else 0x71,*(c if row==0 else (c[0]-b[0],c[1]-b[1])))
        p.probe('outlined interior',104,y+32,False)
    p.save('shp08')


def page_nine(P):
    p=P('SHAPES / SHP-09 - CIRCLES','PLOT &95 / &9D / &99: CENTRE + CIRCUMFERENCE',
        'Outline and fill pairs use identical radii.')
    for i,radius in enumerate((12,24,40)):
        x=96+i*160; p.label((x-40)//8,9,f'RADIUS {radius}',11)
        p.colour(15); p.circle((x,152),radius)
        p.circle((x,272),radius,True,relative=i==1)
        p.probe('outline centre '+str(radius),x,152,False)
        p.probe('fill centre '+str(radius),x,272,True)
        p.probe('circle outside '+str(radius),x+radius+2,272,False)
    p.label(2,42,'Small pair at left: off-axis radius point (0.6r,0.8r).',14)
    # A separate off-axis radius of exactly 10 beside the small pair.
    p.plot(4,32,208); p.plot(0x95,38,216)
    p.plot(4,64,208); p.plot(0x99,6,8)
    p.save('shp09')


def page_ten(P):
    p=P('SHAPES / SHP-10 - ELLIPSES','PLOT &C5 / &CD: CENTRE, SIDE, TOP/BOTTOM',
        'Wide, tall, and sheared outlines above matching fills.')
    for i,(rx,ry,shear,caption) in enumerate(((60,28,0,'WIDE'),(28,52,0,'TALL'),(44,36,28,'SHEARED'))):
        x=88+i*168; p.label((x-32)//8,9,caption,11)
        for y,filled in ((148,False),(280,True)):
            p.colour(15); p.plot(4,x,y); p.plot(4,x+rx,y)
            p.plot(0xCD if filled else 0xC5,x+shear,y-ry)
            p.probe(caption+' centre '+str(filled),x,y,filled)
    p.save('shp10')


def arc(p,code,cx,cy,r,end,reference=False):
    a,b=(cx+r,cy),(cx,cy)
    if reference:a,b=b,a
    p.plot(4,*a);p.plot(4,*b);p.plot(code,cx+end[0],cy+end[1])


def page_eleven(P):
    p=P('SHAPES / SHP-11 - ARCS AND POINT ORDER',
        'PLOT &A5: DOCUMENTED AND REFERENCE POINT ORDER',
        'Quarter / half / major arcs; compare the two point orders.')
    for row,reference in enumerate((False,True)):
        y=160+row*144
        p.label(2,8+row*18,('DOC: START, CENTRE, END' if not reference else
                           'REFERENCE: CENTRE, START, END'),14)
        for i,(end,caption) in enumerate((((0,-60),'QUARTER'),((-60,0),'HALF'),((0,60),'MAJOR'))):
            x=80+i*168;p.label((x-32)//8,11+row*18,caption,11)
            p.colour(15);arc(p,0xA5,x,y,36,end,reference)
            p.probe(('reference' if reference else 'documented')+' arc top '+caption,x,y-36,True)
            p.colour(11);p.cross(x,y,2)
    p.label(2,43,'Yellow + marks intended centre. End points lie beyond radius.')
    p.save('shp11')


def page_twelve(P):
    p=P('SHAPES / SHP-12 - SEGMENTS AND SECTORS',
        'PLOT &AD SEGMENT / &B5 SECTOR; POINT-ORDER COMPARISON',
        'Segments close by chord; sectors by centre. Compare orders.')
    p.label(18,8,'SEGMENT',11);p.label(44,8,'SECTOR',11)
    for row,(reference,major) in enumerate(((False,False),(False,True),(True,False),(True,True))):
        y=112+row*64;end=(0,40 if major else -40)
        p.label(2,(y-4)//8,('REF ' if reference else 'DOC ')+('MAJOR' if major else 'MINOR'),11)
        for x,code in ((176,0xAD),(384,0xB5)):
            p.colour(14);arc(p,code,x,y,24,end,reference)
            dx,dy=((6,-6) if major or code==0xB5 else (15,-15))
            p.probe(('reference' if reference else 'documented')+' filled arc '+str((major,code)),
                    x+dx,y+dy,(0,255,255))
        p.colour(7);p.line((264,y),(288,y));p.line((264,y),(264,y+(-24 if not major else 24)))
    p.label(2,43,'DOC: start,centre,end. REF: centre,start,end.',14)
    p.save('shp12')


def page_thirteen(P):
    p=P('SHAPES / SHP-13 - HORIZONTAL FILLS','PLOT &4D / &5D / &6D / &7D + RELATIVE LINE',
        'Yellow stroke starts at the updated right edge of each fill.')
    for i,(code,caption) in enumerate(((0x4D,'TO NON-BACKGROUND'),(0x5D,'RIGHT TO BACKGROUND'),
            (0x6D,'TO FOREGROUND'),(0x7D,'RIGHT TO NON-FOREGROUND'))):
        y=112+i*64; p.label(2,(y-24)//8,f'&{code:02X} {caption}',11)
        p.colour(14); p.rect(232,y-5,264,y+5)
        p.colour(15)
        if code==0x4D:
            p.line((192,y-8),(192,y+8));p.line((448,y-8),(448,y+8)); seed=320
        elif code==0x5D:
            p.colour(14);p.line((280,y),(448,y));p.colour(15);seed=320
        elif code==0x6D:
            p.line((192,y-8),(192,y+8));p.line((448,y-8),(448,y+8));seed=320
        else:
            p.line((280,y),(448,y));seed=320
        p.plot(code,seed,y)
        p.colour(11); p.plot(1,0,16)
        p.probe(caption+' filled seed',seed+8,y,True)
    p.save('shp13')


def page_fourteen(P):
    p=P('SHAPES / SHP-14 - FLOOD FILLS','PLOT &85 UNTIL NON-BG / &8D UNTIL FG; VIEWPORT',
        'Left keeps the cyan island. Right paints over the island.')
    for x,code in ((32,0x85),(280,0x8D)):
        p.colour(15);p.outline(x,96,x+184,216)
        p.colour(14);p.rect(x+64,128,x+112,176)
        p.colour(15);p.plot(code,x+16,112)
        p.probe('flood interior '+str(code),x+24,144,True)
        p.probe('flood outside '+str(code),x-2,144,False)
        p.probe('island '+str(code),x+80,144,(0,255,255) if code==0x85 else True)
    p.label(2,30,'OPEN ENCLOSURE: fill escapes, but stays in viewport.',14)
    p.viewport(48,272,464,336);p.colour(7);p.outline(80,288,160,320)
    p.colour(0);p.line((104,288),(128,288));p.colour(11);p.plot(0x85,112,304)
    p.reset_position();p.save('shp14')


def page_fifteen(P):
    p=P('SHAPES / SHP-15 - FILLED PATHS (EXPERIMENTAL)',
        'PLOT &DD / &D9; FOLLOWING MOVE CLOSES EACH PATH',
        'Uninterrupted convex and concave paths, >3 vertices.')
    for pts,relative in (([(48,144),(104,96),(176,120),(208,192),(144,256),(56,224)],False),
            ([(288,96),(464,96),(464,152),(376,152),(376,208),(464,208),(464,272),(288,272)],True)):
        p.colour(14 if relative else 11)
        p.plot(4,*pts[0]);p.plot(4,*pts[1]);previous=pts[1]
        for i,point in enumerate(pts[2:]):
            rel=relative and i%2==0
            p.plot(0xD9 if rel else 0xDD,*( (point[0]-previous[0],point[1]-previous[1]) if rel else point))
            previous=point
        p.plot(4,0,0)
    p.label(2,38,'CONVEX / ABSOLUTE',11);p.label(34,38,'CONCAVE / MIXED',14)
    p.probe('concave notch empty',420,180,False)
    p.probe('concave interior',320,180,(0,255,255))
    p.save('shp15')


def page_sixteen(P):
    p=P('SHAPES / SHP-16 - PLOT PAINT VARIANTS','LOW BITS 1/2/3 + 5/6/7: FG, INVERSE, BACKGROUND',
        'Top: absolute. Bottom: relative. Inverse twice restores.')
    for row,relative in enumerate((False,True)):
        y=104+row*136
        for col,(low,name) in enumerate(((1,'FOREGROUND'),(3,'BACKGROUND'),(2,'INVERSE'))):
            x=24+col*168;p.label(x//8,(y-24)//8,name,11)
            p.colour(7);p.rect(x,y,x+128,y+88)
            p.colour(15);p.colour(128,0)
            a,b=(x+16,y+16),(x+112,y+16)
            p.plot(4,*a);p.plot(low if relative else low+4,*( (96,0) if relative else b))
            p.plot(4,x+16,y+40);p.plot(0x60+low+(0 if relative else 4),*( (64,32) if relative else (x+80,y+72)))
            if low==2:
                p.plot(4,x+96,y+48);p.plot(0x60+low+(0 if relative else 4),*((16,24) if relative else (x+112,y+72)))
                p.plot(4,x+96,y+48);p.plot(0x60+low+(0 if relative else 4),*((16,24) if relative else (x+112,y+72)))
            if low!=2:p.probe(name+' line '+str(row),x+48,y+16,low==1)
            else:p.probe('inverse twice restores '+str(row),x+104,y+60,(170,170,170))
    p.save('shp16')


def page_seventeen(P):
    p=P('SHAPES / SHP-17 - ALL EIGHT GCOL OPERATIONS','VDU 18,0..7; FG/BG RECTANGLES + EXPECTED RGB SWATCH',
        'Each pair: foreground / background. Bar below is expected.')
    base=(170,85,0);target=(85,170,255)
    names=('SET','OR','AND','XOR','INVERT','NO-OP','AND NOT','OR NOT')
    p.palette(32,*base);p.palette(33,*target)
    for mode,name in enumerate(names):
        x=16+(mode%4)*124;y=104+(mode//4)*136
        p.label(x//8,(y-24)//8,f'{mode} {name}',11)
        expected=tuple((t,b|t,b&t,b^t,255-b,b,b&(255-t),b|(255-t))[mode] for b,t in zip(base,target))
        for dx,bg in ((0,False),(56,True)):
            p.colour(32);p.rect(x+dx,y,x+dx+48,y+56)
            p.colour(33+(128 if bg else 0),mode)
            p.plot(4,x+dx+8,y+8);p.plot(0x67 if bg else 0x65,x+dx+40,y+48)
            p.probe(name+(' background' if bg else ' foreground'),x+dx+24,y+24,expected)
        p.palette(34,*expected);p.colour(34);p.rect(x,y+72,x+104,y+80)
    p.data.append(20);p.save('shp17')


def page_eighteen(P):
    p=P('SHAPES / SHP-18 - COLOUR MAPPING','ALL 64 COLOURS; VDU 19 PHYSICAL/RGB; VDU 20 RESET',
        'Remapping changes new drawing; earlier swatches stay put.')
    for i in range(64):
        x=16+(i%16)*30;y=80+(i//16)*36
        p.colour(i);p.rect(x,y,x+26,y+24)
    p.label(2,29,'LOGICAL 32: ORIGINAL / PHYSICAL / RGB / RESET',11)
    p.colour(32);p.rect(24,256,112,304)
    p.data.extend((19,32,48,0,0,0));p.colour(32);p.rect(148,256,236,304)
    p.palette(32,0,255,0);p.colour(32);p.rect(272,256,360,304)
    p.data.append(20);p.colour(32);p.rect(396,256,484,304)
    p.probe('physical RRGGBB red',180,280,(255,0,0))
    p.probe('explicit RGB green',304,280,(0,255,0))
    p.label(2,40,'Physical mapping: red. Explicit RGB: green.',14)
    p.save('shp18')


def page_nineteen(P):
    p=P('SHAPES / SHP-19 - ORIGIN AND COORDINATES','VDU 29 ORIGIN; VDU 23,0,&C0 PIXEL / LOGICAL',
        'Same motif at two origins; lower pair compares scaling.')
    for ox,oy in ((104,152),(360,152)):
        p.origin(ox,oy);p.colour(15);p.polygon([(-56,32),(56,32),(0,-48)])
        p.colour(11);p.cross(0,0,3)
    p.reset_position();p.label(2,9,'PIXEL ORIGIN (104,152)',11);p.label(34,9,'ORIGIN (360,152)',11)
    p.label(2,27,'PIXELS: Y DOWN',14);p.label(34,27,'LOGICAL: Y UP',14)
    p.colour(15);p.outline(48,248,208,328)
    p.data.extend((23,0,0xC0,1));p.origin(0,0)
    # Exact screen-space equivalent; rounding is intentionally observable.
    p.outline(740,147,1140,360)
    p.reset_position();p.probe('pixel rectangle top',120,248,True)
    p.label(2,42,'Logical grid is 1280 x 1024; pixel grid is 512 x 384.')
    p.save('shp19')


def page_twenty(P):
    p=P('SHAPES / SHP-20 - VIEWPORTS AND CLEARS','VDU 24 / 28 / 16 CLG / 12 CLS / 26 RESET',
        'Drawing clips at all four edges; clears affect subwindows.')
    p.colour(7);p.outline(30,94,226,218)
    p.viewport(48,112,208,200);p.colour(15)
    p.line((0,156),(256,156));p.line((128,64),(128,232));p.circle((128,156),72)
    p.reset_position()
    for x,y,v in ((48,156,True),(208,156,True),(128,112,True),(128,200,True),(47,156,False)):
        p.probe('clipping edge',x,y,v)
    p.label(2,9,'CLIP ALL FOUR EDGES',11);p.label(34,9,'CLG / CLS SUBWINDOWS',11)
    p.colour(14);p.rect(280,104,472,208)
    p.viewport(296,120,360,192);p.data.append(16);p.reset_position()
    p.data.extend((28,48,23,56,15,12));p.data.append(26)
    p.probe('CLG cleared',320,160,False);p.probe('CLS cleared',416,160,False)
    p.probe('clear preserved border',288,160,(0,255,255))
    p.label(2,30,'ONE PIXEL WIDE / HIGH VIEWPORTS',14)
    p.viewport(104,264,104,328);p.colour(15);p.rect(32,248,216,336)
    p.reset_position();p.viewport(264,296,464,296);p.rect(248,248,480,336);p.reset_position()
    p.probe('one-wide viewport',104,280,True);p.probe('one-wide outside',103,280,False)
    p.probe('one-high viewport',340,296,True);p.probe('one-high outside',340,295,False)
    p.save('shp20')


def page_twenty_one(P):
    p=P('SHAPES / SHP-21 - VIEWPORTS FROM CURSOR HISTORY',
        'VDU 23,0,&9C / &9D / &9E / &9F',
        'Cursor-defined windows clip; moving origin moves both windows.')
    p.plot(4,32,104);p.plot(4,192,192);p.data.extend((23,0,0x9D,23,0,0x9C))
    p.colour(14);p.rect(0,80,224,216)
    p.data.extend((31,1,1));p.data.extend(b'WINDOW A')
    p.plot(4,232,0);p.data.extend((23,0,0x9F))
    p.colour(11);p.rect(0,80,224,216)
    p.data.extend((31,1,1));p.data.extend(b'MOVED B')
    p.reset_position();p.label(2,9,'FROM TWO MOVES',11);p.label(34,9,'ORIGIN + WINDOWS MOVED',11)
    p.plot(4,104,280);p.data.extend((23,0,0x9E));p.colour(15)
    p.polygon([(-48,32),(48,32),(0,-40)])
    p.reset_position();p.label(2,42,'&9E ORIGIN',11)
    p.plot(4,288,248);p.plot(4,560,320);p.data.extend((23,0,0x9D))
    p.colour(14);p.rect(256,224,600,344);p.reset_position()
    p.label(34,42,'&9D CLIPPED AT SCREEN EDGE',11)
    p.probe('cursor window outside',24,160,False)
    p.probe('offscreen viewport clipped',500,280,(0,255,255))
    p.save('shp21')


def stamp(p,x,y):
    p.colour(15);p.rect(x,y,x+23,y+23)
    p.colour(14);p.rect(x+2,y+2,x+9,y+17)
    p.colour(11);p.rect(x+10,y+14,x+21,y+21)


def page_twenty_two(P):
    p=P('SHAPES / SHP-22 - COPY, MOVE AND SCROLL','PLOT &B9/&BA/&BB/&BD/&BE/&BF; VDU 23,7',
        'Copies keep sources. Moves erase vacated source pixels.')
    for i,code in enumerate((0xB9,0xBA,0xBB,0xBD,0xBE,0xBF)):
        col=i%3;row=i//3;x=24+col*168;y=96+row*88
        p.label(x//8,(y-24)//8,f'&{code:02X} '+('MOVE' if code in (0xB9,0xBD) else 'COPY'),11)
        stamp(p,x,y)
        dx=16 if row else 80 # second row deliberately overlaps
        p.plot(4,x,y);p.plot(4,x+23,y+23)
        p.plot(code,*( (x+dx,y+23) if code&4 else (dx-23,0)))
        p.probe('copy/move source '+str(code),x,y,code not in (0xB9,0xBD))
        p.probe('copy/move destination '+str(code),x+dx,y,True)
    p.label(2,31,'SCROLL: RIGHT 8 / LEFT 8 / DOWN 8 / UP 8 / RIGHT 0',14)
    for i,(direction,movement) in enumerate(((0,8),(1,8),(2,8),(3,8),(0,0))):
        x=24+i*96;p.colour(7);p.outline(x-2,270,x+74,334)
        p.viewport(x,272,x+72,332);stamp(p,x+24,288)
        p.data.extend((23,7,2,direction,movement));p.reset_position()
    p.label(2,43,'Copy/move destination is bottom-left; lower row overlaps.')
    p.save('shp22')


def page_twenty_three(P):
    p=P('SHAPES / SHP-23 - BITMAP PLOTS AND GRAPHICS TEXT',
        'RGBA2222 BUFFER; PLOT &E9-&EF; VDU 23,27,3; VDU 5',
        'Transparent corners survive; direct draw ignores clipping.')
    bitmap(p)
    for row,relative in enumerate((False,True)):
        y=112+row*88
        for col,(low,caption) in enumerate(((1,'FG'),(3,'BG'),(2,'INV'))):
            x=48+col*168;p.label(x//8,(y-24)//8,('REL ' if relative else 'ABS ')+caption,11)
            p.colour(7);p.rect(x-8,y-8,x+64,y+40);p.colour(128)
            p.plot(4,x-12,y+8);p.plot(0xE8+low+(0 if relative else 4),*((12,-8) if relative else (x,y)))
    p.viewport(32,272,80,312);p.plot(0xED,64,280)
    p.data.extend(bytes((23,27,3))+words(192,280));p.reset_position()
    p.label(2,40,'PLOT CLIPPED',14);p.label(22,40,'DIRECT',14)
    p.colour(15);p.plot(4,344,288);p.data.append(5);p.data.extend(b'VDU 5 TEXT');p.data.append(4)
    p.probe('bitmap clip outside',84,292,False)
    p.probe('direct bitmap ignores clip',196,292,True)
    # An unclipped control proves the uploaded bitmap and direct call work.
    p.data.extend(bytes((23,27,3))+words(272,280))
    p.label(32,40,'CONTROL',11)
    p.label(2,43,'DIRECT OUTSIDE VIEW: expected arrow; reference may clip it.')
    p.probe('direct bitmap control',276,292,True)
    p.save('shp23')


def page_twenty_four(P):
    p=P('SHAPES / SHP-24 - BUFFERS, CONTEXTS AND TRANSFORMS',
        'BUFFER CALL; CONTEXT &C8,3/4; MATRIX 32; BITMAP &96',
        'Motifs match; restore recovers colour, origin and viewport.')
    # Absolute coordinates inside the reusable command buffer use each origin.
    motif=bytearray()
    for code,x,y in ((4,0,32),(5,24,0),(5,48,32),(5,0,32)):
        motif.extend(bytes((25,code))+struct.pack('<hh',x,y))
    upload(p,MOTIF,motif)
    for x in (48,192,336):
        p.origin(x,104);p.colour(15)
        if x==48:p.data.extend(motif)
        else:buffered(p,MOTIF,1)
    p.reset_position();p.label(2,9,'DIRECT',11);p.label(24,9,'CALL',11);p.label(42,9,'CALL',11)
    p.colour(15);p.origin(64,208);p.viewport(0,-32,392,32)
    p.data.extend((23,0,0xC8,3))
    p.origin(288,208);p.viewport(0,-24,56,24);p.colour(14);p.rect(0,0,48,16)
    p.data.extend((23,0,0xC8,4));p.rect(0,0,112,16)
    p.reset_position();p.label(2,23,'RESTORED WHITE',11);p.label(34,23,'TEMPORARY CYAN',11)
    p.probe('restored colour and origin',100,216,True)
    p.probe('temporary context',312,216,(0,255,255))
    bitmap(p)
    for i,(op,args,caption) in enumerate(((0,(),'IDENTITY'),(5,(2,2),'SCALE 2X'),
            (2,(90,),'ROTATE 90'),(8,(0.75,0),'SHEAR X'))):
        x=32+i*124;p.label(x//8,31,caption,11)
        matrix(p,0)
        if op:matrix(p,op,*args)
        transform(p);p.colour(15);p.plot(0xED,x+32,296)
        if i==0:p.probe('identity bitmap shaft',x+36,308,True)
        if i==1:p.probe('scaled bitmap beyond original bounds',x+40,320,True)
        if i==3:p.probe('sheared bitmap shaft',x+48,308,True)
    p.flush();transform(p,65535)
    p.save('shp24')


PAGES=(page_three,page_four,page_five,page_six,page_seven,page_eight,page_nine,
       page_ten,page_eleven,page_twelve,page_thirteen,page_fourteen,page_fifteen,
       page_sixteen,page_seventeen,page_eighteen,page_nineteen,page_twenty,
       page_twenty_one,page_twenty_two,page_twenty_three,page_twenty_four)
