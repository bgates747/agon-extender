"""Retained dispatcher + actual P4 backend, with deterministic stream/reply fakes."""
from pathlib import Path
import subprocess,tempfile,re
from processed_keyboard_test import function
ROOT=Path(__file__).resolve().parents[1]
src=(ROOT/'vdp/video/vdu_audio.h').read_text()
constants='\n'.join(x for x in (ROOT/'vdp/video/agon.h').read_text().splitlines() if re.match(r'#define (AUDIO_|BUFFERED_SAMPLE_BASEID|PACKET_AUDIO|CALLBACK_SENDING_VDPP)',x))
parts=[function(src,s) for s in ('void VDUStreamProcessor::vdu_sys_audio(', 'void VDUStreamProcessor::sendAudioStatus(')]
fake=r'''
#include <cassert>
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <vector>
#include <array>
#include <algorithm>
#define AGON_EXTENDER_P4_BOOT 1
#define debug_log(...) ((void)0)
void vTaskDelay(int){}
std::vector<std::array<unsigned,2>> replies;unsigned callbacks=0;
void send_packet(unsigned code,unsigned size,uint8_t *p){assert(code==PACKET_AUDIO&&size==2);replies.push_back({p[0],p[1]});}
class VDUStreamProcessor {
public:
 std::vector<uint8_t> bytes;size_t at=0,chunk=64,max_sink=0;
 int16_t readByte_t(){return at<bytes.size()?bytes[at++]:-1;}
 int32_t readWord_t(){auto l=readByte_t();if(l<0)return -1;auto h=readByte_t();return h<0?-1:l|(h<<8);}
 int32_t read24_t(){auto l=readByte_t();if(l<0)return -1;auto m=readByte_t();if(m<0)return -1;auto h=readByte_t();return h<0?-1:l|(m<<8)|(h<<16);}
 uint32_t readIntoBuffer(uint8_t *p,uint32_t n){max_sink=std::max(max_sink,size_t(n));unsigned left=n;while(left&&at<bytes.size()){auto take=std::min({chunk,size_t(left),bytes.size()-at});memcpy(p,bytes.data()+at,take);p+=take;at+=take;left-=take;}return left;}
 void bufferCallCallbacks(unsigned id){assert(id==(CALLBACK_SENDING_VDPP|PACKET_AUDIO));++callbacks;}
 void vdu_sys_audio();void sendAudioStatus(uint8_t,uint8_t);
 uint8_t loadSample(uint16_t,uint32_t);uint8_t createSampleFromBuffer(uint16_t,uint8_t,uint16_t);
 uint8_t setVolumeEnvelope(uint8_t,uint8_t);uint8_t setFrequencyEnvelope(uint8_t,uint8_t);
 uint8_t setSampleFrequency(uint16_t,uint16_t);uint8_t setSampleRepeatStart(uint16_t,uint32_t);uint8_t setSampleRepeatLength(uint16_t,uint32_t);uint8_t setParameter(uint8_t,uint8_t,uint16_t);
};
#include "extender/audio/unavailable_audio_adapter.hpp"
'''
checks=r'''
struct Case{std::vector<uint8_t> bytes;int status;};
unsigned cases_run=0;
void check(const Case &c,size_t chunk){
 VDUStreamProcessor p;p.chunk=chunk;p.bytes=c.bytes;const auto n=p.bytes.size();p.bytes.insert(p.bytes.end(),{'S','A','F','E'});
 replies.clear();callbacks=0;p.vdu_sys_audio();assert(p.at==n&&p.readByte_t()=='S'&&p.readByte_t()=='A'&&p.readByte_t()=='F'&&p.readByte_t()=='E');
 assert(p.max_sink<=64);assert(callbacks==replies.size());
 if(c.status<0)assert(replies.empty());else{assert(replies.size()==1);assert(replies[0][0]==c.bytes[0]&&replies[0][1]==unsigned(c.status));}
 ++cases_run;
 // Every truncated prefix of short commands: no overread or guessed marker.
 if(n<4096)for(size_t end=0;end<n;++end){VDUStreamProcessor t;t.chunk=chunk;t.bytes.assign(c.bytes.begin(),c.bytes.begin()+end);replies.clear();callbacks=0;t.vdu_sys_audio();assert(t.at<=end&&t.max_sink<=64);++cases_run;}
}
int main(){
 std::vector<Case> cases={
 {{0,0,12,12,16,23,0},0},{{0,1},255},{{0,2,12},255},{{0,3,12,1},0},
 {{0,4,3},0},{{0,4,255},0},{{0,4,8,12,16},0},
 {{255,5,1},0},{{255,5,2,12,16,0},0},{{255,5,2,12,16,8,23,0},0},
 {{255,5,3,12,16},0},{{255,5,4,12,16,23,0},0},
 {{255,5,5,12,16,23},0},{{255,5,6,12,16,23,0,133},0},
 {{255,5,7,12,16,23},0},{{255,5,8,12,16,23,0,133},0},
 {{255,5,16,12,16},-1},{{255,5,255},0},
 {{0,6,0},0},{{0,6,1,12,16,23,0,133,12,16},0},{{0,6,255},0},
 {{0,7,0},0},{{0,7,255},0},{{0,8},0},{{0,9},0},{{0,10},0},
 {{0,11,12,16,23},0},{{0,12,12,16,23},0},{{0,13,12,16},0},
 {{0,14,3,12},0},{{0,14,131,12,16},0},{{0,255},-1}};
 for(unsigned count:{0,1,255}){
  Case v{{0,6,2},0};for(int group=0;group<3;++group){v.bytes.push_back(count);for(unsigned i=0;i<count;++i)v.bytes.insert(v.bytes.end(),{12,16,23});}cases.push_back(v);
  Case f{{0,7,1,uint8_t(count),12,16,23},0};for(unsigned i=0;i<count;++i)f.bytes.insert(f.bytes.end(),{12,16,23,133});cases.push_back(f);
 }
 for(unsigned size:{0,1,63,64,65,4096,16777215}){
  Case sample{{255,5,0,uint8_t(size),uint8_t(size>>8),uint8_t(size>>16)},0};for(unsigned i=0;i<size;++i)sample.bytes.push_back(uint8_t(i));cases.push_back(std::move(sample));
 }
 for(auto &c:cases)for(size_t chunk:{1,3,17,64})check(c,chunk);
 // Back-to-back Wolf3D-style enable, sample selection and play: no gap or marker search.
 VDUStreamProcessor stream;std::vector<Case> wolf={{{0,8},0},{{0,4,8,12,16},0},{{0,0,64,12,16,1,0},0}};
 for(auto &c:wolf)stream.bytes.insert(stream.bytes.end(),c.bytes.begin(),c.bytes.end());stream.bytes.push_back('Z');replies.clear();callbacks=0;
 for(size_t i=0;i<wolf.size();++i)stream.vdu_sys_audio();assert(stream.readByte_t()=='Z'&&replies.size()==3);
 printf("PASS: %u framing/truncation cases, all branches, split reads, 24-bit sample maximum, bounded sink, replies and Wolf3D sequence\n",cases_run);
}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td);(p/'test.cpp').write_text('#include <cstdint>\n'+constants+'\n'+fake+'\n'.join(parts)+checks)
 subprocess.run(['c++','-std=c++17','-O1','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-Wno-error=sign-compare','-fsanitize=address,undefined','-I'+str(ROOT/'vdp/video'),str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
