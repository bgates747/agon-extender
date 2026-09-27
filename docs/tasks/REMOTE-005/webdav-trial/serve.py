"""Serve only an explicitly named synthetic sandbox; never a device backend."""
import argparse
from pathlib import Path
from wsgidav.wsgidav_app import WsgiDAVApp
from cheroot.wsgi import Server
p=argparse.ArgumentParser()
p.add_argument('--root',required=True)
p.add_argument('--bind',default='127.0.0.1')
p.add_argument('--port',type=int,default=8766)
a=p.parse_args()
root=Path(a.root).resolve()
if not (root/'.synthetic-webdav-sandbox').is_file():
    raise SystemExit('Refusing directory without synthetic-sandbox marker')
app=WsgiDAVApp({'provider_mapping':{'/':str(root)},'simple_dc':{'user_mapping':{'*':True}},'http_authenticator':{'accept_basic':True,'accept_digest':False,'default_to_digest':False},'verbose':1})
Server((a.bind,a.port),app).start()
