"""Synthetic unit checks, not measured device performance."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'qualification'),str(ROOT/'scripts')]
from static_conversion import summarize

def telemetry(height,whole_image):
    row_calls=600*height
    phases=[dict(calls=0,us=0,max=0,drops=0) for _ in range(6)]
    phases[1].update(calls=row_calls,us=row_calls)
    phases[2].update(calls=row_calls,us=2*row_calls)
    phases[3].update(calls=600 if whole_image else row_calls,
                     us=600*3000 if whole_image else row_calls*5)
    phases[4].update(calls=600,us=600*100)
    phases[5].update(calls=600,us=600*5000)
    return dict(output='normal',open=0,overflow=False,windows=[
        dict(id=i,tag=123,start_us=1,end_us=10000001,updates=600,
             scanouts=600,phases=phases) for i in range(3)])

class ConversionUnits(unittest.TestCase):
    def test_whole_image_expansion_is_independent_of_height(self):
        for height in (240,384):
            r=summarize(telemetry(height,True),20,height,123,render_storage='linear-rgb222')
            self.assertEqual(r['median_normalized_frame_ms']['rgb888_expand'],3)
            self.assertEqual(r['median_normalized_frame_ms']['row_read_compose'],2*height/1000)
            self.assertEqual(r['median_submissions_per_second'],60)
            self.assertEqual(r['expansion_unit'],'whole-image')
            self.assertIn('driver cache handling',r['scope'])
    def test_legacy_cpu_row_normalization_is_preserved(self):
        r=summarize(telemetry(384,False),20,384,123)
        self.assertEqual(r['median_normalized_frame_ms']['rgb888_expand'],1.92)
        self.assertEqual(r['expansion_unit'],'row')
        self.assertNotIn('whole-image public PPA',r['scope'])

if __name__=='__main__':unittest.main()
