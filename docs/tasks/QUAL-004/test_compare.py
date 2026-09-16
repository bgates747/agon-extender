import struct,tempfile,unittest
from compare import evf,compare

def frame():return b'EVF1'+bytes([1,32,2,3])+struct.pack('<IHHIIII',1,2,1,2,2,16667,0)+b'\x03\x0c'
class ImageTests(unittest.TestCase):
 def test_exact_and_one_pixel_difference(self):
  a=evf(frame())
  with tempfile.TemporaryDirectory() as d:
   self.assertTrue(compare(a,a,d)['match'])
   r=compare(a,dict(a,pixels=b'\x03\x30'),d)
   self.assertEqual(r['mismatches'],1);self.assertEqual(r['bounds'],[1,0,1,0])
 def test_bad_length(self):
  for data in (frame()[:-1],frame()+b'\0'):
   with self.assertRaises(ValueError):evf(data)
 def test_invalid_colour(self):
  with self.assertRaises(ValueError):evf(frame()[:-1]+b'\xff')
 def test_dimensions_never_resized(self):
  a=evf(frame())
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):compare(a,dict(a,width=1,height=2),d)
if __name__=='__main__':unittest.main()
