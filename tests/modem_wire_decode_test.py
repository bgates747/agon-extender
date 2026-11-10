"""Synthetic waveforms exercise packed channels, gaps and decode failures."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from modem_wire_decode import decode
class Wire(unittest.TestCase):
 def waveform(self,data,bit=0,bad=False):
  rate=24000000;baud=1152000;period=rate/baud;levels=[1]*30
  for byte in data:
   start=len(levels);bits=[0]+[(byte>>i)&1 for i in range(8)]+[0 if bad else 1]
   for k in range(round(10*period)):levels.append(bits[min(9,int(k/period))])
   levels.extend([1]*23)
  levels.extend([1]*100)
  return bytes((x<<bit)|(1<<(1-bit)) for x in levels),rate,baud
 def test_exact_bytes_both_channels(self):
  for bit in [0,1]:
   raw,r,b=self.waveform(bytes(range(256)),bit);data,_,errors=decode(raw,bit,r,b);self.assertEqual(data,bytes(range(256)));self.assertEqual(errors,[])
 def test_stop_error_retained(self):
  raw,r,b=self.waveform(b'x',bad=True);_,_,errors=decode(raw,0,r,b);self.assertTrue(errors)
 def test_idle(self):self.assertEqual(decode(b'\3'*1000,0,24000000,576000)[0],b'')
if __name__=='__main__':unittest.main()
