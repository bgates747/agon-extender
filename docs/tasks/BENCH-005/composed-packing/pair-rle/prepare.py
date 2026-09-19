"""Build on preserved W09; old packet negotiation and codecs remain intact."""
from pathlib import Path
import shutil
T=Path('docs/tasks/BENCH-005/composed-packing/pair-rle');P=T.parent/'sixbit';R=Path('agents/pair-rle');src=Path('agents/rle2-execution/candidate02/source/vdp');web=src/'video/extender/web';net=src/'video/extender/network/wired_network_service.cpp'
s=(P/'network-candidate.cpp').read_text();s='#include "pair_rle.hpp"\n'+s
s=s.replace('static uint8_t *packed_scratch=nullptr;','static uint8_t *packed_scratch=nullptr, *pair_scratch=nullptr;\nstatic bool pair_requested=false;')
s=s.replace('  if(!packed_scratch)', '  if(!pair_scratch)pair_scratch=(uint8_t*)heap_caps_malloc(786432,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);\n  if(!packed_scratch)',1)
s=s.replace('std::strcmp(query,"rle2=1&packed=2")==0','(std::strcmp(query,"rle2=1&packed=2")==0 || std::strcmp(query,"rle2=1&packed=2&pair=1")==0)')
s=s.replace('  sixbit_requested=', '  pair_requested=std::strcmp(query,"pair=1")==0 || std::strcmp(query,"rle2=1&packed=2&pair=1")==0;\n  sixbit_requested=',1)
needle='  esp_err_t result = ESP_OK;\n  for(size_t index=0;index<count;++index)'
code='''  if(pair_requested && pair_scratch && view.segment_count==2 && view.segments[0].size==32) {
    auto h=view.segments[0].data;auto pixels=view.segments[1];
    const size_t w=size_t(h[12])|(size_t(h[13])<<8),hh=size_t(h[14])|(size_t(h[15])<<8);
    if(std::memcmp(h,"EVF1",4)==0 && h[6]==2 && pixels.size==w*hh && rle2::get32(h+16)==w && rle2::get32(h+20)==pixels.size){
      const size_t limit=(!rle2_requested && !packed_requested)?pixels.size+1:transmitted-32;
      auto bytes=pair_rle::encode(pixels.data,pixels.size,pair_scratch,786432,limit);
      if(bytes){std::memcpy(compressed_header,h,32);compressed_header[2]='Q';
        compressed[0]={compressed_header,32};compressed[1]={pair_scratch,bytes};
        segments=compressed.data();count=2;transmitted=32+bytes;}
    }
  }
'''+needle
assert needle in s;s=s.replace(needle,code);net.write_text(s);(T/'network-candidate.cpp').write_text(s)
shutil.copy2(T/'pair.hpp',net.parent/'pair_rle.hpp');shutil.copy2(P/'packed.hpp',net.parent/'packed_frame.hpp')
(R/'web').mkdir(exist_ok=True)
for n in ['app.js','index.html','style.css','frame_protocol.js']:
 s=(Path('agents/sixbit/web')/n).read_text()
 # Retain prior default: the Nurples experiment did not justify an extra encoder pass.
 if n=='frame_protocol.js':s=(T/'decoder.js').read_text()+'\n'+s.replace('buffer=unpackRLE2Frame(unpackPackedFrame(buffer));','buffer=unpackRLE2Frame(unpackPackedFrame(unpackPairFrame(buffer)));')
 (web/n).write_text(s);(R/'web'/n).write_text(s)
