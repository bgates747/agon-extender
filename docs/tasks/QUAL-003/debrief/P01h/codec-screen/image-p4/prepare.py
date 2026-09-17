from pathlib import Path
import shutil,sys,json
base=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();png=Path(sys.argv[3]).resolve();root=Path(__file__).resolve().parent
out.mkdir();shutil.copytree(base/'source',out/'source',symlinks=True,ignore=shutil.ignore_patterns('.git','.pio','__pycache__'))
v=out/'source/vdp';(v/'.pio').mkdir();(v/'.pio/packages').symlink_to((base/'source/vdp/.pio/packages').resolve(),target_is_directory=True)
s=(base/'platformio.ini').read_text().replace(str(base),str(out))
f=v/'pio/p4-console-source-selection.json';m=json.loads(f.read_text());m['project_translation_units'] += ['video/extender/diagnostics/image/PNGenc/'+x.name for x in (png/'src').iterdir() if x.suffix in ('.cpp','.c')];f.write_text(json.dumps(m,indent=2))
s=s.replace('-D AGON_EXTENDER_CANARY=1','-D AGON_EXTENDER_CANARY=1\n\t-I video/extender/diagnostics/image/PNGenc')
(out/'platformio.ini').write_text(s)
c=v/'video/extender/diagnostics/image';c.mkdir();shutil.copytree(png/'src',c/'PNGenc');shutil.copy2(png/'LICENSE',c/'PNGenc/LICENSE');shutil.copy2(root/'image_codec.hpp',c/'image_codec.hpp')
f=v/'video/extender/network/wired_network_service.cpp';s=f.read_text();s='#include "extender/diagnostics/image/image_codec.hpp"\n'+s
s=s.replace('  if(!rle2_scratch)', '  imagecodec::init();\n  if(!rle2_scratch)',1)
s=s.replace('  httpd_uri_t srle{};', '  httpd_uri_t img{};img.uri="/diagnostics/image";img.method=HTTP_POST;img.handler=&imagecodec::handler;httpd_register_uri_handler(server,&img);\n  httpd_uri_t srle{};')
# Match existing server member used by other handlers.
s=s.replace('httpd_register_uri_handler(server,&img)', 'httpd_register_uri_handler(server,&img)')
s=s.replace('  srle2_order4=', '  imagecodec::selected=!strcmp(query,"jpeg=80")?80:!strcmp(query,"jpeg=90")?90:!strcmp(query,"jpeg=95")?95:!strcmp(query,"png=1")?1:!strcmp(query,"png=3")?3:0;\n  srle2_order4=',1)
anchor='  esp_err_t result = ESP_OK;\n  for(size_t index=0;index<count;++index)'
code='''  if(imagecodec::selected && count==2 && segments[0].size==32){
    auto h=segments[0].data;unsigned w=h[12]|(h[13]<<8),height=h[14]|(h[15]<<8);size_t n=0;
    if(!memcmp(h,"EVF1",4)&&h[6]==2&&segments[1].size==size_t(w)*height&&imagecodec::encode(segments[1].data,w,height,imagecodec::selected,n)){
      memcpy(compressed_header,h,32);compressed_header[2]=imagecodec::selected>3?'J':'P';
      compressed[0]={compressed_header,32};compressed[1]={imagecodec::output,n};segments=compressed.data();count=2;transmitted=32+n;++imagecodec::frames;
    }
  }
'''
assert anchor in s;s=s.replace(anchor,code+anchor)
# Separate stats endpoint avoids changing old counter meaning.
anchor='  httpd_uri_t srle{};'
s=s.replace(anchor,'''  httpd_uri_t ims{};ims.uri="/diagnostics/image-stats";ims.method=HTTP_GET;ims.handler=[](httpd_req_t*r){char b[256];snprintf(b,sizeof b,"{\\"convert_us\\":%llu,\\"encode_us\\":%llu,\\"attempts\\":%llu,\\"failures\\":%llu,\\"frames\\":%llu}",(unsigned long long)imagecodec::convert_us,(unsigned long long)imagecodec::encode_us,(unsigned long long)imagecodec::attempts,(unsigned long long)imagecodec::failures,(unsigned long long)imagecodec::frames);return httpd_resp_send(r,b,HTTPD_RESP_USE_STRLEN);};httpd_register_uri_handler(server,&ims);
'''+anchor)
f.write_text(s)
# Browser decode emits native bitmap, avoiding GPU readback in timing runs.
f=v/'video/extender/web/decoder.js';s=f.read_text();s=s.replace('  if(this.pending)throw', '  if(this.pending)throw')
s=s.replace('  if(buffer.byteLength<4', '''  if(buffer.byteLength>=32){const a=new Uint8Array(buffer),magic=String.fromCharCode(...a.subarray(0,4));if(magic==='EVJ1'||magic==='EVP1'){
   const t=performance.now(),v=new DataView(buffer),w=v.getUint16(12,true),h=v.getUint16(14,true);
   if(a[4]!==1||a[5]!==32||a[6]!==2||!w||!h||w>512||h>384||v.getUint32(16,true)!==w||v.getUint32(20,true)!==w*h||buffer.byteLength>1048576)throw Error('Invalid image envelope');
   const bitmap=await createImageBitmap(new Blob([a.subarray(32)],{type:magic==='EVJ1'?'image/jpeg':'image/png'}),{colorSpaceConversion:'none',premultiplyAlpha:'none'});
   if(bitmap.width!==w||bitmap.height!==h){bitmap.close();throw Error('Image dimensions mismatch');}
   return {frame:{width:w,height:h,strideBytes:w*3,pixelFormat:1,pixels:bitmap,bitmap,sequence:v.getUint32(8,true),presentPeriodUs:v.getUint32(24,true),flags:a[7]},metrics:{totalMs:performance.now()-t}};
  }}
  if(buffer.byteLength<4''');f.write_text(s)
f=v/'video/extender/web/app.js';s=f.read_text().replace('const frame=parseFrame(decoded.buffer);','const frame=decoded.frame||parseFrame(decoded.buffer);');s=s.replace('  pendingFrame = { frame, usesCredit };','  if(pendingFrame?.frame.bitmap)pendingFrame.frame.bitmap.close();\n  pendingFrame = { frame, usesCredit };').replace('  pendingFrame = null;\n  credit.disconnected();','  if(pendingFrame?.frame.bitmap)pendingFrame.frame.bitmap.close();\n  pendingFrame = null;\n  credit.disconnected();');f.write_text(s)
f=v/'video/extender/web/webgl2_presenter.js';s=f.read_text();start=s.index('    gl.texSubImage2D(');end=s.index('    gl.useProgram',start);old=s[start:end];s=s[:start]+'''    if(frame.bitmap){gl.texSubImage2D(gl.TEXTURE_2D,0,0,0,uploadFormat,gl.UNSIGNED_BYTE,frame.bitmap);frame.bitmap.close();}else{
'''+old+'    }\n'+s[end:];f.write_text(s)
