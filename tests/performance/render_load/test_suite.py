import importlib.util,json,sys,tempfile,unittest,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import generate
from packing import pack_rle_stream,unpack_rle_stream,unrle
from codec import plan,decode
class Suite(unittest.TestCase):
 def test_frozen_determinism_bounds_pairs(self):
  with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
   a,b=Path(a),Path(b);ma=generate.generate(a);mb=generate.generate(b)
   self.assertEqual(ma,mb)
   for mode,item in ma['modes'].items():
    data=(a/item['file']).read_bytes();self.assertEqual(data,(b/item['file']).read_bytes())
    self.assertEqual(unpack_rle_stream(pack_rle_stream(data)),data)
    off=13+int.from_bytes(data[11:13],'little');ids=[]
    while True:
     n=int.from_bytes(data[off:off+2],'little');off+=2
     if not n:break
     self.assertLessEqual(n,65535);case=data[off:off+n];off+=n
     ids.append(int.from_bytes(case[:2],'little'));pos=6+int.from_bytes(case[4:6],'little')
     for f in range(40):
      size=int.from_bytes(case[pos:pos+2],'little');pos+=2;frame=case[pos:pos+size];pos+=size
      self.assertTrue(frame.endswith(bytes([23,0,195])) if item['double_buffered'] else not frame.endswith(bytes([23,0,195])))
     self.assertEqual(pos,n)
    self.assertEqual(ids,list(range(94)));self.assertEqual(off,len(data))
   self.assertEqual([c['family'] for c in ma['modes']['8']['cases']],[c['family'] for c in ma['modes']['136']['cases']])
 def test_plan_and_incomplete_checkpoint_rejected(self):
  p=plan('/extender/data.bin','/agents/results.bin',20,generate.MODES[20],123)
  self.assertEqual(len(p),256);self.assertEqual(p[235],20)
  with self.assertRaises(ValueError):decode(b'B9R1\1'+bytes(127))
  for bad in (b'\x80',b'\x02AB'):
   with self.assertRaises(ValueError):unrle(bad)
 def test_continuous_records_exceed_32_and_validate_cycles(self):
  header=bytearray(128);header[:5]=b'B9R2\2';header[22:26]=b'test'
  case=bytearray(24);case[:4]=b'B9C2';case[14:17]=(256).to_bytes(3,'little');case[17:20]=(256).to_bytes(3,'little');case[20]=1
  frames=b''.join(bytes([(i+8)%40,0])+bytes(10) for i in range(256))
  data=header+case+frames;r=decode(data)
  self.assertEqual(r['cases'][0]['total_frames'],256)
  self.assertEqual(len(r['cases'][0]['frames']),256)
  with self.assertRaises(ValueError):decode(data[:-1])
  bad=bytearray(data);bad[152]=7
  with self.assertRaises(ValueError):decode(bad)
 def test_common_agon_ram_layout(self):
  contract=json.loads((Path(__file__).parent/'contract-r04.json').read_text());m=contract['memory_layout']
  self.assertEqual(m['first_records']+m['second_records'],contract['record_capacity_frames'])
  self.assertLessEqual(int(m['samples_first'],16)+12*m['first_records'],int(m['payload'],16))
  self.assertLessEqual(int(m['samples_second'],16)+12*m['second_records'],int(m['user_ram_end_exclusive'],16))
 def test_kind_and_paint_apply_to_each_selected_sprite(self):
  # Model the official selected-sprite API, including inherited reset defaults.
  # This fails the r03 once-before-the-loop type selection for count>1.
  for hardware in (False,True):
   for inherited in (False,True):
    stream=generate.sprite_setup(64,hardware);i=0;selected=0;kinds=[inherited]*64;paint=[3]*64;shown=set()
    while i<len(stream):
     self.assertEqual(stream[i],23);group,op=stream[i+1:i+3];i+=3
     if group==0:
      self.assertEqual(op,248);self.assertEqual(stream[i:i+4],bytes((2,0,1,0)));i+=4;continue
     self.assertEqual(group,27)
     if op in (4,6,7,18):
      value=stream[i];i+=1
      if op==4:selected=value
      elif op==18:paint[selected]=value
     elif op in (19,20):kinds[selected]=op==19
     elif op==11:shown.add(selected)
     else:self.assertIn(op,(5,17))
    self.assertEqual(shown,set(range(64)));self.assertEqual(kinds,[hardware]*64);self.assertEqual(paint,[0]*64)
if __name__=='__main__':unittest.main()
