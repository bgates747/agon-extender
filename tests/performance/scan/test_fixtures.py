"""Contract checks independent of timings; protect critical payload semantics."""
import unittest,struct
import build
from records import decode

class Fixtures(unittest.TestCase):
    def test_window_correlation_and_controls(self):
        p='/agents/extender/results/scan-r02/check.bin'
        for case in (1,3,7,8,9):
            plan=build.config(case,120,60,p,extra_flags=4,window_tag=0x432109)
            self.assertEqual(plan[11:14],bytes([9,33,67]))
            self.assertEqual(plan[10],5 if case==9 else 4)
            for tag,flags in [(0,4),(1,0)]:
                with self.assertRaises(AssertionError):
                    build.config(case,120,60,p,extra_flags=flags,window_tag=tag)
        # Old files remain decodable; the formerly reserved tag defaults to0.
        h=bytearray(128);h[:8]=b'SCANR01!';h[8]=1;h[9]=24
        self.assertEqual(decode(h)['window_tag'],0)
        h[10:13]=bytes([9,33,67])
        self.assertEqual(decode(h)['window_tag'],0x432109)
    def test_progressive_load_and_clipping(self):
        for u in range(256):
            self.assertEqual(build.frame(1,u),b'')
            self.assertEqual(build.frame(2,u),build.field()+bytes([23,7,2,2,1]))
            f=build.frame(3,u);self.assertIn(build.viewport(0,0,255,0),f)
            # Bitmap command parser walks precise fields, not byte substrings in pixels.
            off=len(build.frame(2,u))+9
            bitmaps=[]
            while f[off:off+3]==bytes([23,27,32]):
                ident=int.from_bytes(f[off+3:off+5],'little')
                self.assertEqual(f[off+5:off+7],bytes([25,237]))
                x,y=struct.unpack_from('<hh',f,off+7);bitmaps.append((ident,x,y));off+=11
            self.assertEqual(len(bitmaps),17)
            self.assertEqual([x for _,x,_ in bitmaps[1:]],list(range(0,256,16)))
            self.assertEqual({y for _,_,y in bitmaps[1:]},{u%16-15})
            self.assertEqual(f[off:],build.field())
            # T07/08 movement is exactly identical, with one refresh per batch.
            movement=build.frame(8,u)
            self.assertEqual(build.frame(7,u),f+movement)
            self.assertEqual(len(movement),32*11+3)
            for i in range(32):
                p=i*11;self.assertEqual(movement[p:p+7],bytes([23,27,4,i,23,27,13]))
                x,y=struct.unpack_from('<HH',movement,p+7)
                self.assertGreaterEqual(x,128);self.assertLessEqual(x+15,383)
                self.assertGreaterEqual(y,48);self.assertLessEqual(y+15,383)
            self.assertEqual(movement[-3:],bytes([23,27,15]))
    def test_selected_sprite_semantics_after_reset(self):
        # Skip actual assets/scene, evaluate only definition tail under hostile defaults.
        data={i:(16,16,bytes(256)) for i in build.ART+[512+t for t in build.TILES]+[1024]}
        tail=build.setup(32,data);off=tail.index(bytes([23,27,4,0,23,27,5]))
        kinds=['hardware']*32;paint=[3]*32;shown=set()
        while off<len(tail)-4:
            self.assertEqual(tail[off:off+3],bytes([23,27,4]));i=tail[off+3];off+=4
            self.assertEqual(tail[off:off+6],bytes([23,27,5,23,27,38]));off+=8
            self.assertEqual(tail[off:off+7],bytes([23,27,18,0,23,27,20]));off+=7
            kinds[i]='software';paint[i]=0
            self.assertEqual(tail[off:off+3],bytes([23,27,11]));off+=3;shown.add(i)
        self.assertEqual(shown,set(range(32)));self.assertEqual(kinds,['software']*32);self.assertEqual(paint,[0]*32)
    def test_incomplete_records_rejected(self):
        for b in [b'',b'SCANR01!'+bytes(120),b'SCANR01!'+bytes([1,24])+bytes(6)+bytes([1])+bytes(111)]:
            with self.assertRaises(ValueError):decode(b)
if __name__=='__main__':unittest.main()
