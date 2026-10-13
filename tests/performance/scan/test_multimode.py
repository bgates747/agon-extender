"""Verify bounded streams for every selected mode, including both-bank work."""
import unittest
import struct
import multimode as m


def parse(data):
    offset=0;bitmaps=[];sprites=[];scrolls=swaps=0
    while offset<len(data):
        op=data[offset]
        if op==29: offset+=5
        elif op==24: offset+=9
        elif data[offset:offset+3]==bytes((23,27,32)):
            if data[offset+5:offset+7]!=bytes((25,237)):raise ValueError('Unexpected bitmap plot')
            bitmaps.append(struct.unpack_from('<hh',data,offset+7));offset+=11
        elif data[offset:offset+3]==bytes((23,27,4)):
            if data[offset+4:offset+7]!=bytes((23,27,13)):raise ValueError('Unexpected sprite position')
            sprites.append(struct.unpack_from('<HH',data,offset+7));offset+=11
        elif data[offset:offset+3]==bytes((23,27,15)):offset+=3
        elif data[offset:offset+3]==bytes((23,0,195)):swaps+=1;offset+=3
        elif data[offset:offset+5]==bytes((23,7,2,2,1)):scrolls+=1;offset+=5
        else:raise ValueError((offset,data[offset:offset+12]))
    return bitmaps,sprites,scrolls,swaps


class MultimodeTests(unittest.TestCase):
    def test_all_generated_frames_have_bounded_bitmap_and_sprite_positions(self):
        for mode in m.MODES:
            w,h,c,db,x,y,fh=m.geometry(mode)
            for case in (1,2,3,4,5,7):
                for u in range(256):
                    bitmaps,sprites,scrolls,swaps=parse(m.frame(mode,case,u))
                    self.assertEqual(swaps,int(db))
                    if case in (1,2):
                        self.assertEqual(len(bitmaps),16 if case==1 else 64)
                        self.assertTrue(all(16<=xx and xx+16<=w-16 and 0<=yy and yy+16<=h for xx,yy in bitmaps))
                    if case in (4,5,7):
                        self.assertEqual(len(sprites),16 if case==7 else 32)
                        self.assertTrue(all(x<=xx and xx+16<=x+256 and y<=yy and yy+16<=h for xx,yy in sprites))
                    self.assertEqual(scrolls,(2 if db else 1) if case in (3,5) else 0)
                    if case in (3,5):
                        self.assertEqual(len(bitmaps),17*scrolls)
                        self.assertIn(m.old.viewport(0,0,255,0),m.frame(mode,case,u))

    def test_mode_admission_and_diagnostic_reset_have_no_mode_selection(self):
        for mode in m.MODES:
            text=m.runner(mode)
            self.assertIn(f'    cp {mode}\n',text)
            self.assertIn('    xor a\n    call sc_marker\n    call sc_prepare',text)
            self.assertNotIn('call vdu_set_screen_mode',text)

    def test_diagnostic_ids_match_selected_sampler_admission(self):
        for mode in m.MODES:
            for case in m.NAMES:
                diagnostic=9 if mode==136 else m.DIAGNOSTIC_IDS[case]
                text=m.runner(mode,case)
                self.assertIn(f'"B009",1,0,{diagnostic},0,1,0,0,0',text)
                if mode!=136 and case not in (6,8):
                    self.assertIn(diagnostic,(3,7,8,39,41,54))
                else:self.assertEqual(diagnostic,9)


if __name__=='__main__':unittest.main()
