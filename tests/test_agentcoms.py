import importlib.util
from pathlib import Path
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
spec=importlib.util.spec_from_file_location('agentcoms',Path(__file__).resolve().parents[1]/'scripts/agentcoms.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class MailboxTests(unittest.TestCase):
    def test_retry_isolation_and_ack(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);req=dict(author='mac-zork',recipient='linux-extender',request_id='question-one',thread_id='zork',body='Hello\n---\nworld')
            a=m.send(root,req);self.assertTrue(m.send(root,req)['duplicate'])
            with self.assertRaises(ValueError):m.send(root,dict(req,body='changed'))
            self.assertEqual(len(m.read(root,'linux-extender')),1)
            self.assertEqual(m.read(root,'mac-zork'),[])
            with self.assertRaises(ValueError):m.ack(root,'mac-zork',[a['message_id']])
            m.ack(root,'linux-extender',[a['message_id']]);self.assertEqual(m.read(root,'linux-extender'),[])
            self.assertEqual(m.read(root,'linux-extender',True)[0]['body'],req['body'])
            m.send(root,dict(req,author='linux-extender',recipient='mac-zork',request_id='reply-one',in_reply_to=a['message_id']))
            with self.assertRaises(ValueError):m.send(root,dict(req,request_id='bad-parent',in_reply_to='missing'))
    def test_concurrent_identical_sends(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);req=dict(author='mac-zork',recipient='linux-extender',request_id='same',thread_id='zork',body='one')
            with ThreadPoolExecutor(max_workers=8) as pool:rows=list(pool.map(lambda _:m.send(root,req),range(16)))
            self.assertEqual(sum(not r['duplicate'] for r in rows),1)
            self.assertEqual(len(m.read(root,'linux-extender')),1)
    def test_reject_path_and_oversize(self):
        with tempfile.TemporaryDirectory() as d:
            r=dict(author='../bad',recipient='linux',request_id='x',thread_id='x',body='ok')
            with self.assertRaises(ValueError):m.send(Path(d),r)
            with self.assertRaises(ValueError):m.send(Path(d),dict(r,author='mac',body='x'*65537))
if __name__=='__main__':unittest.main()
