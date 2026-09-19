"""Apply reproducible experimental overlay to a preserved source tree."""
from pathlib import Path
import shutil,json,hashlib,re
root=Path.cwd();task=root/'docs/tasks/BENCH-005/composed-packing/sixbit';out=root/'agents/sixbit'
src=root/'agents/rle2-execution/candidate02/source/vdp'
net=src/'video/extender/network/wired_network_service.cpp';web=src/'video/extender/web'
# Save every modified upstream-to-experiment input for reproducible reversal.
backup=out/'original';backup.mkdir(exist_ok=True)
for p in [net,web/'app.js',web/'index.html',web/'style.css',web/'frame_protocol.js']:
 q=backup/p.name
 if not q.exists():q.write_bytes(p.read_bytes())
s=(backup/net.name).read_text()
s='#include "packed_frame.hpp"\n'+s
s=s.replace('static bool rle2_requested=false;', 'static bool rle2_requested=false, packed_requested=false, sixbit_requested=false;\nstatic uint8_t *packed_scratch=nullptr;')
s=s.replace('196622','786446').replace('n<=196608','n<=786432')
s=s.replace('  if(!rle2_scratch)', '  if(!packed_scratch)packed_scratch=(uint8_t*)heap_caps_malloc(589828,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);\n  if(!rle2_scratch)',1)
s=s.replace('std::strcmp(query,"rle2=1")==0', '(std::strcmp(query,"rle2=1")==0 || std::strcmp(query,"rle2=1&packed=1")==0 || std::strcmp(query,"rle2=1&packed=2")==0)')
s=s.replace('  auto const socket = httpd_req_to_sockfd(request);\n  std::lock_guard', '  sixbit_requested=std::strcmp(query,"packed=2")==0 || std::strcmp(query,"rle2=1&packed=2")==0;\n  packed_requested=sixbit_requested || std::strcmp(query,"packed=1")==0 || std::strcmp(query,"rle2=1&packed=1")==0;\n  auto const socket = httpd_req_to_sockfd(request);\n  std::lock_guard',1)
needle='  esp_err_t result = ESP_OK;\n  for(size_t index=0;index<count;++index)'
replacement='''  if(packed_requested && packed_scratch && view.segment_count==2 && view.segments[0].size==32) {
    auto h=view.segments[0].data;auto pixels=view.segments[1];
    size_t w=size_t(h[12])|(size_t(h[13])<<8),hh=size_t(h[14])|(size_t(h[15])<<8);
    if(std::memcmp(h,"EVF1",4)==0 && h[6]==2 && pixels.size==w*hh && rle2::get32(h+16)==w && rle2::get32(h+20)==pixels.size) {
      auto bytes=packed_frame::encode(pixels.data,pixels.size,packed_scratch,589828,transmitted-32,sixbit_requested);
      if(bytes){std::memcpy(compressed_header,h,32);compressed_header[2]='P';
        compressed[0]={compressed_header,32};compressed[1]={packed_scratch,bytes};
        segments=compressed.data();count=2;transmitted=32+bytes;}
    }
  }
  esp_err_t result = ESP_OK;
  for(size_t index=0;index<count;++index)'''
assert needle in s;s=s.replace(needle,replacement)
net.write_text(s);shutil.copy2(task/'packed.hpp',net.parent/'packed_frame.hpp')
for n in ['app.js','index.html','style.css']:
 data=(root/'agents/web60/web'/n).read_text()
 if n=='app.js':data=data.replace('?rle2=1','?rle2=1&packed=2')
 (web/n).write_text(data)
s=(backup/'frame_protocol.js').read_text().replace('n>196608','n>786432')
s=(task/'decoder.js').read_text()+'\n'+s.replace('buffer=unpackRLE2Frame(buffer);','buffer=unpackRLE2Frame(unpackPackedFrame(buffer));')
(web/'frame_protocol.js').write_text(s)
(out/'web').mkdir(exist_ok=True)
for n in ['app.js','index.html','style.css','frame_protocol.js']:shutil.copy2(web/n,out/'web'/n)
# Retain actual overlay, not merely an ignored modified tree.
(task/'network-candidate.cpp').write_text(net.read_text())
print('Prepared composed-packing overlay')
