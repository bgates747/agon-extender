from pathlib import Path
import argparse,tempfile,shutil,threading,json
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--assets',type=Path,required=True);p.add_argument('--evf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--browser');a=p.parse_args()
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp)
 for n in ('frame_protocol.js','webgl2_presenter.js'):shutil.copy2(a.assets/n,root/n)
 shutil.copy2(a.evf,root/'frame.evf');(root/'index.html').write_text('<canvas id="c"></canvas>')
 class H(SimpleHTTPRequestHandler):
  def __init__(self,*args,**kw):super().__init__(*args,directory=tmp,**kw)
  def log_message(self,*args):pass
 server=ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader'],executable_path=a.browser)
   try:
    page=browser.new_page();page.goto('http://127.0.0.1:'+str(server.server_port))
    result=page.evaluate('''async()=>{
     const {parseFrame}=await import('./frame_protocol.js');const {WebGL2Presenter}=await import('./webgl2_presenter.js');
     const b=await(await fetch('./frame.evf')).arrayBuffer(),frame=parseFrame(b),src=new Uint8Array(b,32);
     const p=new WebGL2Presenter(document.querySelector('#c'));p.present(frame);
     const gl=p.gl, pixels=new Uint8Array(frame.width*frame.height*4);gl.readPixels(0,0,frame.width,frame.height,gl.RGBA,gl.UNSIGNED_BYTE,pixels);
     let differences=0,first=null;
     for(let y=0;y<frame.height;y++)for(let x=0;x<frame.width;x++){
       const v=src[y*frame.strideBytes+x],i=((frame.height-1-y)*frame.width+x)*4;
       const want=[(v&3)*85,((v>>2)&3)*85,((v>>4)&3)*85,255];
       if(want.some((n,k)=>pixels[i+k]!==n)){differences++;if(!first)first={x,y,v,want,got:Array.from(pixels.slice(i,i+4))};}
     }
     return {width:frame.width,height:frame.height,stride:frame.strideBytes,differences,first,gl_error:gl.getError(),renderer:gl.getParameter(gl.RENDERER)};
    }''')
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));assert not result['differences'] and not result['gl_error']
   finally:browser.close()
 finally:server.shutdown();server.server_close()
