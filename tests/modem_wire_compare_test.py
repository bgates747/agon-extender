import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from modem_wire_compare import compare
from modem_bw_protocol import frame,pattern,UP
class Compare(unittest.TestCase):
 def test_exact_and_destination_gap(self):
  data=frame(1,pattern(1,UP))+frame(2,pattern(2,UP))+frame(3)
  r=compare(b'AT\r\n'+data+b'+++',data,UP,2)
  self.assertEqual(r['valid_payload_frames'],2);self.assertIsNone(r['first_wire_vs_expected_difference']);self.assertTrue(r['endpoint_is_wire_prefix'])
  r=compare(data,data[:1500]+data[1600:],UP,2);self.assertEqual(r['first_wire_vs_endpoint_difference'],1500)
 def test_truncation_not_full_capture(self):
  data=frame(1,pattern(1,UP))+frame(2)
  self.assertFalse(compare(data[:500],None,UP,1)['capture_covers_expected_length'])
if __name__=='__main__':unittest.main()
