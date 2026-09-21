import importlib.util,json,threading,unittest,urllib.request,urllib.error,uuid
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
    for method,origin,header,code in [('GET','http://p4.test','1',405),('POST','http://wrong.test','1',403),('POST','http://p4.test','0',403),('POST','http://p4.test','1',200),('POST','http://p4.test','1',200)]:
     req=urllib.request.Request(url,data=body if method=='POST' else None,method=method,headers={'Origin':origin,'X-Agon-Reset':header})
     try:response=urllib.request.urlopen(req)
     except urllib.error.HTTPError as e:response=e
     with response:self.assertEqual(response.status,code)
    self.assertEqual(run.call_count,1)
   finally:server.shutdown();server.server_close();thread.join()
if __name__=='__main__':unittest.main()
