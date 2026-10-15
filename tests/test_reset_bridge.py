import importlib.util,json,threading,time,unittest,urllib.request,urllib.error,uuid
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('reset_bridge',Path(__file__).parents[1]/'scripts/reset_bridge.py');bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)
class ResetTest(unittest.TestCase):
 def test_explicit_origin_and_duplicate(self):
  with patch.object(bridge.subprocess,'run') as run:
   server=bridge.server(dict(bind='127.0.0.1',port=0,origins=['http://p4.test'],command=['fixed-helper']))
   thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
   url=f'http://127.0.0.1:{server.server_port}/reset';body=json.dumps({'id':str(uuid.uuid4())}).encode()
   try:
    for index,(method,origin,header,code) in enumerate([('GET','http://p4.test','1',405),('POST','http://wrong.test','1',403),('POST','http://p4.test','0',403),('POST','http://p4.test','1',200),('POST','http://p4.test','1',200)]):
     req=urllib.request.Request(url,data=body if method=='POST' else None,method=method,headers={'Origin':origin,'X-Agon-Reset':header})
     deadline=time.monotonic()+1
     while True:
      try:response=urllib.request.urlopen(req)
      except urllib.error.HTTPError as e:response=e
      with response:
       status=response.status;response.read()
      # The preceding HTTP response can arrive before its handler releases
      # the operation lock. A duplicate in that window is correctly busy.
      if index==4 and status==409 and time.monotonic()<deadline:
       self.assertEqual(run.call_count,1);time.sleep(.005);continue
      self.assertEqual(status,code);break
    self.assertEqual(run.call_count,1)
   finally:server.shutdown();server.server_close();thread.join()

class P4ResetTest(unittest.TestCase):
 def test_targets_are_separate_and_duplicates_do_not_reset_twice(self):
  with patch.object(bridge.subprocess,'run') as run:
   server=bridge.server(dict(bind='127.0.0.1',port=0,origins=['http://p4.test'],command=['agon-helper'],p4_command=['p4-helper']))
   thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
   body=json.dumps({'id':str(uuid.uuid4())}).encode()
   try:
    for path in ('/reset-p4','/reset-p4','/reset'):
     req=urllib.request.Request(f'http://127.0.0.1:{server.server_port}'+path,data=body,headers={'Origin':'http://p4.test','X-Agon-Reset':'1'})
     with urllib.request.urlopen(req) as response:
      result=json.load(response)
      self.assertEqual(result['target'],'p4' if path.endswith('p4') else 'agon')
     time.sleep(.01)
    self.assertEqual([call.args[0] for call in run.call_args_list],[['p4-helper'],['agon-helper']])
   finally:server.shutdown();server.server_close();thread.join()
 def test_p4_unconfigured_does_not_call_agon_helper(self):
  with patch.object(bridge.subprocess,'run') as run:
   server=bridge.server(dict(bind='127.0.0.1',port=0,origins=['http://p4.test'],command=['agon-helper']))
   thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
   try:
    req=urllib.request.Request(f'http://127.0.0.1:{server.server_port}/reset-p4',data=json.dumps({'id':str(uuid.uuid4())}).encode(),headers={'Origin':'http://p4.test','X-Agon-Reset':'1'})
    with self.assertRaises(urllib.error.HTTPError) as error:urllib.request.urlopen(req)
    self.assertEqual(error.exception.code,503);error.exception.close();run.assert_not_called()
   finally:server.shutdown();server.server_close();thread.join()

if __name__=='__main__':unittest.main()
