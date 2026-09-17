import {Decoder} from './decoder.js';
import {parseFrame} from './frame_protocol.js';
import {WebGL2Presenter} from './webgl2_presenter.js';
const decoder=new Decoder(),presenter=new WebGL2Presenter(document.querySelector('canvas'));
function bitmapPresent(b){const p=presenter,g=p.gl,w=b.width,h=b.height;if(p.canvas.width!==w)p.canvas.width=w;if(p.canvas.height!==h)p.canvas.height=h;
 if(p.pixelFormat!=='png'||p.textureWidth!==w||p.textureHeight!==h){g.deleteTexture(p.texture);p.texture=g.createTexture();p.configureTexture();g.texImage2D(g.TEXTURE_2D,0,g.RGBA8,w,h,0,g.RGBA,g.UNSIGNED_BYTE,null);p.pixelFormat='png';p.textureWidth=w;p.textureHeight=h;}
 g.bindTexture(g.TEXTURE_2D,p.texture);g.texSubImage2D(g.TEXTURE_2D,0,0,0,g.RGBA,g.UNSIGNED_BYTE,b);g.viewport(0,0,w,h);g.useProgram(p.program);g.uniform1i(p.formatUniform,0);g.bindVertexArray(p.vao);g.drawArrays(g.TRIANGLES,0,3);b.close();}
window.run=async(config)=>{const expected={};if(config.verify)for(const name of config.cases)expected[name]=new Uint8Array(await(await fetch('/raw/'+name)).arrayBuffer());
 return new Promise((resolve,reject)=>{let rows=[],busy=false;const ws=new WebSocket(`ws://${location.host}/video`);ws.binaryType='arraybuffer';const timer=setTimeout(()=>{ws.close();reject(Error('Run timeout'));},60000);
 ws.onopen=()=>ws.send('frame');ws.onerror=()=>{clearTimeout(timer);reject(Error('Socket error'));};ws.onmessage=async e=>{if(busy){reject(Error('Multiple outstanding frames'));return;}busy=true;try{const start=performance.now(),seq=new DataView(e.data).getUint32(8,true),name=config.cases[seq%config.cases.length],d=await decoder.decode(e.data,config.verify),decodeWallMs=performance.now()-start;let frame=d.buffer?parseFrame(d.buffer):null;
 let mismatch=-1;if(config.verify){const pixels=d.pixels||frame.pixels,want=expected[name];if(pixels.length!==want.length)mismatch=0;for(let i=0;mismatch<0&&i<want.length;i++)if(pixels[i]!==want[i])mismatch=i;}
 await new Promise(requestAnimationFrame);const t=performance.now();if(d.bitmap)bitmapPresent(d.bitmap);else presenter.present(frame);const submitMs=performance.now()-t;
 rows.push({seq,name,at:performance.now(),decodeWallMs,submitMs,mismatch,...d.metrics});busy=false;if(rows.length>=config.count){clearTimeout(timer);ws.close();resolve(rows);}else ws.send('frame');
 }catch(e){clearTimeout(timer);ws.close();reject(e);}};});};
window.edge=async(buffer)=>{try{await decoder.decode(new Uint8Array(buffer).buffer,true);return 'accepted';}catch(e){return String(e.message);}};
window.ready=true;

window.timeoutEdge=async(buffer)=>{const url=URL.createObjectURL(new Blob(['self.onmessage=()=>{}'],{type:'text/javascript'})),d=new Decoder(50,url);try{await d.decode(new Uint8Array(buffer).buffer);throw Error('Timeout was not enforced');}catch(e){if(e.message!=='Decoder timeout')throw e;return e.message;}finally{d.reset();URL.revokeObjectURL(url);}};
