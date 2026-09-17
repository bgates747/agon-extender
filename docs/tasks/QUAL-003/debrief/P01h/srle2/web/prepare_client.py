"""Reuse real candidate page/presenter; insert reusable SRLE2 decoder boundary."""
from pathlib import Path
import argparse,shutil,json,hashlib
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('decoder',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(exist_ok=False);root=Path(__file__).resolve().parent
for n in ['index.html','style.css','app.js','frame_protocol.js','webgl2_presenter.js']:shutil.copy2(a.source/n,a.out/n)
for n in ['decoder.js','decoder-worker.js']:shutil.copy2(root/n,a.out/n)
shutil.copy2(root.parents[1]/'codec/web_decode.js',a.out/'web_decode.js')
for n in ['szip.js','szip.wasm']:shutil.copy2(a.decoder/n,a.out/n)
shutil.copy2(root.parent/'vendor/COPYING.GPL-2',a.out/'COPYING.GPL-2')
shutil.copy2(root.parent/'SOURCE.json',a.out/'codec-source.json')
p=a.out/'app.js';s=p.read_text();assert s.count('    acceptFrame(parseFrame(event.data), true);')==1
s='import {FrameDecoder} from "./decoder.js";\nconst frameDecoder=new FrameDecoder();\n'+s
s=s.replace('function onSocketMessage(event) {','async function onSocketMessage(event) {\n  const owner=socket;')
s=s.replace('    acceptFrame(parseFrame(event.data), true);','''    const decoded=await frameDecoder.decode(event.data);
    if(socket!==owner)return;
    const parseStart=performance.now();
    const frame=parseFrame(decoded.buffer);
    decoded.metrics.parseMs=performance.now()-parseStart;
    window.dispatchEvent(new CustomEvent('agon-frame-decoded',{detail:{buffer:decoded.buffer,pixels:frame.pixels,metrics:decoded.metrics}}));
    acceptFrame(frame, true);''')
s=s.replace('    closeForProtocol(error);','    if(socket===owner)closeForProtocol(error);')
s=s.replace('function disconnect() {','function disconnect() {\n  frameDecoder.reset();')
s=s.replace('?rle2=1','?srle2=1')
# Browser close() forbids reserved protocol code 1002; use private application code.
s=s.replace('socket.close(1002, "invalid EVF1 frame")','socket.close(4002, "invalid video frame")')
s=s.replace('      presenter.present(accepted.frame);',"      const submitStart=performance.now();\n      presenter.present(accepted.frame);\n      window.dispatchEvent(new CustomEvent('agon-frame-submitted',{detail:{ms:performance.now()-submitStart}}));")
p.write_text(s)
(a.out/'source-hashes.json').write_text(json.dumps({n:hashlib.sha256((a.source/n).read_bytes()).hexdigest() for n in ['app.js','frame_protocol.js','webgl2_presenter.js']},indent=2)+'\n')
