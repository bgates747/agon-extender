"""Independent structural checks; full glyph correctness uses stock image parity."""
def check(image):
 w,h=image['width'],image['height'];p=image['pixels']
 assert (w,h)==(640,480)
 def area(x1,y1,x2,y2):return [p[y*w+x] for y in range(y1,y2) for x in range(x1,x2)]
 full=area(16,11*19,32,12*19);separated=area(32,12*19,48,13*19)
 colours=(3,12,15,48,51,60,63)
 text=[colour in area(16,(i+2)*19,600,(i+3)*19) for i,colour in enumerate(colours)]
 halves=[15 in area(32,y*19,400,(y+1)*19) for y in (17,18)]
 checks={'contiguous_white_cell':set(full)=={63},'separated_white_and_black':set(separated)=={0,63},'seven_text_colours':all(text),'double_height_both_halves_nonempty':all(halves),'unused_bottom_rows_black':set(area(0,475,640,480))=={0}}
 return {'passed':all(checks.values()),'checks':checks,'scope':'Structural/palette sanity; not an independent font rasterizer'}
