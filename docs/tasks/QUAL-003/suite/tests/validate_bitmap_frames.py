"""Independent comparisons of actual SDL presentation, including hardware sprites."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageChops


def validate(root,partial=False):
    root=Path(root);cache={};results=[]
    def frame(stem):
        if stem not in cache:
            path=root/(stem+'.bmp')
            if not path.exists():path=root/('p'+stem[3:5])/(stem+'.bmp')
            if not path.exists():
                if partial:return None
                raise AssertionError(f'Missing presentation frame: {path}')
            cache[stem]=Image.open(path).convert('RGB')
        return cache[stem]
    def pixel(name,stem,x,y,expected):
        im=frame(stem)
        if im is None:return
        actual=im.getpixel((x,y))
        results.append(dict(name=name,frame=stem,point=[x,y],expected=list(expected),
                            actual=list(actual),correct=actual==expected))
    def equal(name,a,box_a,b,box_b):
        ia,ib=frame(a),frame(b)
        if ia is None or ib is None:return
        delta=ImageChops.difference(ia.crop(box_a),ib.crop(box_b))
        wrong=sum(pixel!=(0,0,0) for pixel in delta.get_flattened_data())
        results.append(dict(name=name,frames=[a,b],different_pixels=wrong,correct=wrong==0))
    green=(0,255,0);background=(170,85,0)
    for stage in (1,2):
        pixel('SW remains at old position before update',f'bsp22_{stage:02}',120,184,green)
        pixel('SW new position remains background',f'bsp22_{stage:02}',248,184,background)
    pixel('SW explicit update moves sprite','bsp22_03',248,184,green)
    pixel('SW old position restored','bsp22_03',120,184,background)
    pixel('Drawing triggers SW update','bsp22_04',120,184,green)
    for n in range(4):
        pixel('Hardware initial position '+str(n),'bsp26_01',48+n*124,184,green)
        pixel('Hardware relative move without command 15 '+str(n),'bsp26_02',64+n*124,224,green)
    pixel('Hardware converted to software remains visible','bsp26_04',408,280,green)
    for stem in ('bsp28_01','bsp28_03'):
        pixel('Hardware RGBA2222 XOR',stem,164,136,(170,170,0))
        pixel('Hardware RGBA8888 XOR uses SET',stem,164,264,green)
        pixel('Hardware AND request uses SET',stem,288,136,green)
    pixel('GCOL demotion enables software AND','bsp28_02',288,136,(0,85,0))
    for row in (0,1):
        y=144+row*144
        equal('Pixel and bitmap-relative centred pivot', 'bsp14_01',(198,y-50,298,y+50),
              'bsp14_01',(366,y-50,466,y+50))
    equal('Explicit six coefficients equal composed matrix','bsp16_02',(88,160,168,240),
          'bsp16_02',(248,160,328,240))
    for i in range(5):
        x=64+i*96
        equal('Degrees equal radians '+str(i),'bsp13_01',(x-40,112,x+56,192),
              'bsp13_01',(x-40,264,x+56,344))
    for row in (0,1):
        y=136+row*128
        for col in (1,2,3):
            x=32+col*124
            equal('Equivalent numeric argument formats','bsp17_01',(32,y,88,y+20),
                  'bsp17_01',(x,y,x+56,y+20))
    equal('Next-frame wrap restores frame zero','bsp23_01',(80,160,392,224),
          'bsp23_04',(80,160,392,224))
    for first,next_stage in ((1,2),(5,6)):
        equal('Repeated software sprite refresh is stable',f'bsp24_{first:02}',(0,56,512,359),
              f'bsp24_{next_stage:02}',(0,56,512,359))
    equal('Baked sprite animation wraps on fixed canvas','bsp29_01',(56,104,144,192),
          'bsp29_05',(56,104,144,192))
    (root/'presentation-results.json').write_text(json.dumps(results,indent=2)+'\n')
    wrong=[r for r in results if not r['correct']]
    for result in wrong:print(json.dumps(result))
    print(f'Presentation comparisons: {len(results)-len(wrong)}/{len(results)} correct.')
    return len(wrong)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('--partial',action='store_true')
    args=parser.parse_args()
    raise SystemExit(bool(validate(args.directory,args.partial)))
