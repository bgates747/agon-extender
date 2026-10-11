import unittest
from phase_analyze import sample,BLOCK
class PhaseContract(unittest.TestCase):
 def fixture(self):
  sites={str(i+1):n for i,n in enumerate(BLOCK)};records=[]
  for length,reverse in ((256,0),(7,0),(9,1)):
   for i,_ in enumerate(BLOCK):
    records.append(dict(wire_bytes=256,repeat=1,index=len(records),return_pc=i+1,raw_prt=65535-len(records)-1,offer_bytes=length,reverse=reverse))
  row=dict(route='exext',wire_bytes=256,repeat=1,reply_prt=40,receipt_prt=10,submit_prt=2,wire_prt=0,flags=0,divider=256)
  return row,records,sites
 def test_conserved_and_gap(self):
  r,e,s=self.fixture();a=sample(r,e,s);self.assertEqual(a['block_total_ticks'],27);self.assertEqual(a['outside_block_ticks'],13)
 def test_refuse_integrity(self):
  for change in ('unknown','order','timer','missing','payload','offer','fault'):
   r,e,s=self.fixture()
   if change=='unknown':e[0]['return_pc']=99
   if change=='order':e[1]['index']=9
   if change=='timer':e[0]['raw_prt']=0
   if change=='missing':e.pop()
   if change=='payload':e[2]['offer_bytes']=255
   if change=='offer':e[3]['offer_bytes']=255
   if change=='fault':r['flags']=32
   with self.assertRaises(ValueError,msg=change):sample(r,e,s)
 def test_nested_publication_not_added_to_blocks(self):
  r,e,s=self.fixture();s.update({'98':'publish_begin','99':'publish_end'})
  begin=dict(e[4],return_pc=98);end=dict(e[4],return_pc=99)
  e[4:4]=[begin,end]
  for i,x in enumerate(e):x['index']=i;x['raw_prt']=65535-i-1
  a=sample(r,e,s);self.assertEqual(a['inclusive_scope_ticks']['publish'],1);self.assertEqual(a['block_total_ticks'],29)
if __name__=='__main__':unittest.main()
