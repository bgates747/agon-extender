import unittest
from capture import decode,fnv,rgb

def specimen():
 data=bytes(range(8))
 return b'boot noise\nQ4BEGIN 7 4 2\n'+b''.join(f'Q4ROW 7 {y} 4 {fnv(data[y*4:y*4+4]):08x}\n'.encode()+data[y*4:y*4+4]+b'\n' for y in range(2))+b'Q4END 7 1\n'
class CaptureTests(unittest.TestCase):
 def test_valid(self):self.assertEqual(decode(specimen())[0]['pixels'],bytes(range(8)))
 def test_corruption(self):
  raw=specimen().replace(bytes(range(4)),b'\x01\x01\x02\x03')
  with self.assertRaises(ValueError):decode(raw)
 def test_missing_row(self):
  with self.assertRaises(ValueError):decode(specimen().replace(b'Q4ROW 7 1',b'Q4ROW 7 2'))
 def test_truncated(self):
  with self.assertRaises(ValueError):decode(specimen()[:-5])
 def test_colour_order(self):self.assertEqual(rgb(bytes([3,12,48])),bytes([255,0,0,0,255,0,0,0,255]))
if __name__=='__main__':unittest.main()
