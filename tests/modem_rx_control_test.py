"""Qualification-oracle controls using synthetic endpoint records only."""
import importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('rx',Path(__file__).resolve().parents[1]/'scripts/modem_rx_control.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ReceiverQualification(unittest.TestCase):
 def setUp(self):self.good=dict(pass_=True,uart_retired=True,tx_frames=7000,rx_frames=7000,uart_errors=0,crc_errors=0,frame_errors=0,fifo_errors=0,ring_errors=0,queue_peak=4,rx_elapsed_us=62000000);self.good['pass']=self.good.pop('pass_')
 def test_full_minute(self):self.assertTrue(m.accepted(self.good,60))
 def test_each_fault_rejects(self):
  for key in ['uart_errors','crc_errors','frame_errors','fifo_errors','ring_errors']:
   with self.subTest(key=key):self.assertFalse(m.accepted(dict(self.good,**{key:1}),60))
 def test_lost_or_empty_frames(self):
  for value in [6999,0]:self.assertFalse(m.accepted(dict(self.good,rx_frames=value),60))
 def test_short_or_unretired_or_queue_saturated(self):
  for changed in [dict(rx_elapsed_us=59999999),dict(uart_retired=False),dict(queue_peak=128),dict(pass_=False)]:
   if 'pass_'in changed:changed={'pass':changed['pass_']}
   self.assertFalse(m.accepted(dict(self.good,**changed),60))
 def test_missing_diagnostic_refuses(self):
  for key in ['fifo_errors','ring_errors','queue_peak','uart_retired']:
   x=dict(self.good);del x[key];self.assertFalse(m.accepted(x,60))
if __name__=='__main__':unittest.main()
