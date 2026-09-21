#!/usr/bin/env python3
"""Bench-only, fixed-command reset bridge. Configuration stays outside Git.
No GET side effects, retries, arbitrary command arguments, or automatic reset.
"""
import argparse,json,subprocess,threading,uuid
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer

def server(config):
    lock=threading.Lock();seen={}
    class Handler(BaseHTTPRequestHandler):
        def allowed(self):return self.headers.get('Origin') in config['origins']
        def reply(self,code,body):
            data=json.dumps(body).encode();self.send_response(code)
            if self.allowed():
                self.send_header('Access-Control-Allow-Origin',self.headers['Origin'])
                self.send_header('Vary','Origin')
            self.send_header('Cache-Control','no-store');self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        def do_OPTIONS(self):
            if self.path!='/reset' or not self.allowed():return self.reply(403,{'error':'origin/path'})
            self.send_response(204);self.send_header('Access-Control-Allow-Origin',self.headers['Origin'])
            self.send_header('Access-Control-Allow-Methods','POST');self.send_header('Access-Control-Allow-Headers','Content-Type, X-Agon-Reset')
            self.send_header('Access-Control-Allow-Private-Network','true');self.end_headers()
        def do_GET(self):self.reply(405,{'error':'POST required'})
        def do_POST(self):
            if self.path!='/reset' or not self.allowed() or self.headers.get('X-Agon-Reset')!='1':return self.reply(403,{'error':'request rejected'})
            try:
                n=int(self.headers.get('Content-Length','0'))
                if not 1<=n<=128:raise ValueError()
                self.connection.settimeout(2)
                request=json.loads(self.rfile.read(n));key=str(uuid.UUID(request['id']))
            except (ValueError,KeyError,TypeError,TimeoutError):return self.reply(400,{'error':'invalid request'})
            if not lock.acquire(False):return self.reply(409,{'error':'reset already in progress'})
            try:
                if key in seen:code,result=seen[key]
                else:
                    # Refuse once full rather than evict IDs and risk duplicate pulses.
                    if len(seen)>=1024:return self.reply(503,{'error':'restart bridge to renew request history'})
                    seen[key]=(500,{'error':'outcome uncertain; do not retry'})
                    try:
                        subprocess.run(config['command'],check=True,timeout=5,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                        code,result=200,{'pulse':'released','boot_verified':False}
                    except (subprocess.SubprocessError,OSError):code,result=500,{'error':'outcome uncertain; check Agon before another request'}
                    seen[key]=(code,result)
                self.reply(code,result)
            finally:lock.release()
    return ThreadingHTTPServer((config['bind'],config['port']),Handler)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);a=p.parse_args()
    with open(a.config) as f:config=json.load(f)
    server(config).serve_forever()
