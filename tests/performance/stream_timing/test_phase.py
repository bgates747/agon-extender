import unittest
from phase_analyze import sample,BLOCK,BLOCK_FORMAT4,SCOPES,block_phases
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
 def test_format4_has_no_fabricated_completion(self):
  r,e,s=self.fixture();s={k:v for k,v in s.items() if v in BLOCK_FORMAT4}
  e=[x for x in e if str(x['return_pc']) in s]
  for i,x in enumerate(e):x['index']=i;x['raw_prt']=65535-i-1
  a=sample(r,e,s)
  self.assertEqual(a['block_schema'],'format4')
  self.assertEqual(a['block_total_ticks'],21)
  self.assertFalse(any('completion_' in k for k in a['phase_totals_ticks']))
 def test_partial_completion_and_unknown_schema_refused(self):
  for dropped in ('completion_begin','completion_end','payload_end','reserve_end'):
   r,e,s=self.fixture();s={k:v for k,v in s.items() if v!=dropped}
   with self.assertRaises(ValueError,msg=dropped):sample(r,e,s)
  with self.assertRaises(ValueError):block_phases({'1':'unknown'})
 def test_linked_format4_schema(self):
  names=BLOCK_FORMAT4+tuple(sorted(SCOPES));s={str(i):v for i,v in enumerate(names)}
  self.assertEqual(len(s),14);self.assertEqual(block_phases(s),BLOCK_FORMAT4)
if __name__=='__main__':unittest.main()
