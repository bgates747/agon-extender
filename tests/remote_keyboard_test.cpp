#include <cassert>
#include <cstdio>
#include <vector>
#include "extender/input/remote_keyboard.hpp"
using namespace agon::extender::input;
void put32(uint8_t *p,uint32_t v){for(unsigned i=0;i<4;++i)p[i]=v>>(8*i);}
std::vector<uint8_t> request(unsigned op,unsigned seq,std::initializer_list<uint8_t> events={},unsigned boot=42,unsigned sid=77) {
 std::vector<uint8_t> p(REMOTE_HEADER+events.size());p[0]='K';p[1]='Y';p[2]=1;p[3]=op;
 put32(p.data()+4,boot);put32(p.data()+8,sid);put32(p.data()+12,seq);p[16]=events.size();
 std::copy(events.begin(),events.end(),p.begin()+REMOTE_HEADER);put32(p.data()+20,remoteCrc(p.data(),p.size()));return p;
}
unsigned send(RemoteKeyboard &r,const std::vector<uint8_t> &p,uint32_t now=0){return r.post(p.data(),p.size(),now);}
RemoteKeyboard ready(unsigned locale=1){RemoteKeyboard r;r.begin(42);r.admit(locale);assert(send(r,request(1,1))==200);return r;}
int main(){
 ProcessedKey key;
 {auto r=ready();auto p=request(2,2,{225,1,4,1,4,0,225,0});assert(send(r,p)==200);
  assert(send(r,p)==200);assert(r.take(key,0)&&key.virtual_key==117);
  assert(!r.take(key,19));assert(r.take(key,20)&&key.keycode=='A'&&key.down);
  assert(r.take(key,40)&&key.keycode=='A'&&!key.down);
  assert(r.take(key,60)&&!key.down);assert(!r.take(key,80));
  assert(send(r,p,80)==200);assert(!r.take(key,100));assert(r.status(100).emitted==4);
  auto bad=request(2,2,{5,1});assert(send(r,bad,100)==409);
 }
 {auto r=ready();auto p=request(2,2,{4,1,4,0,250,1});assert(send(r,p)==400);assert(!r.take(key,0));
  assert(send(r,request(2,2,{4,0}))==400);assert(send(r,request(2,2,{4,1,4,1}))==400);
  assert(send(r,request(2,2,{4,1,5,1,6,1,7,1,8,1,9,1,10,1}))==400);
  p=request(2,2,{4,1});p.back()^=1;assert(send(r,p)==400);
 }
 {auto r=ready();assert(send(r,request(2,2,{225,1,4,1,4,0,225,0}))==200);
  assert(r.take(key,0));assert(r.take(key,20));
  auto physical=mapUsbCliKey(4,0,1);r.physicalKey(physical);
  std::vector<ProcessedKey> releases;while(r.release(key))releases.push_back(key);
  assert(releases.size()==2&&!releases[0].down&&!releases[1].down);
  assert(!r.status(21).physical_neutral&&r.status(21).reason==RemoteKeyboard::physical);
  assert(!r.take(key,40));assert(send(r,request(1,1,{},42,88),40)==503);
  assert(r.status(40).accepted==4 && r.status(40).emitted==2 && r.status(40).discarded==2);
  physical.down=0;r.physicalKey(physical);r.physicalNeutral(true);
  assert(send(r,request(1,1,{},42,88),40)==200);
 }
 {auto r=ready();assert(send(r,request(2,2,{4,1}),0)==200);assert(r.take(key,0));
  assert(r.take(key,5000)&&!key.down);assert(r.status(5000).reason==RemoteKeyboard::expired);
  assert(send(r,request(4,3),5001)==409);
 }
 {auto r=ready();assert(send(r,request(2,2,{4,1}),0)==200);assert(r.take(key,0));
  r.boundary();assert(r.take(key,20)&&!key.down);assert(send(r,request(4,3),20)==409);
  assert(!r.status(20).ready);r.admit(1);assert(!r.take(key,20));
  assert(send(r,request(1,1,{},43,88),20)==200);
 }
 {RemoteKeyboard r;r.begin(42);r.admit(1);assert(send(r,request(1,1),0xfffffff0)==200);
  assert(send(r,request(2,2,{4,1,4,0}),0xfffffff0)==200);assert(r.take(key,0xfffffff0));
  assert(!r.take(key,3));assert(r.take(key,4)&&!key.down);
  assert(r.status(4900).reason==RemoteKeyboard::none);assert(r.status(5100).reason==RemoteKeyboard::expired);
 }
 {auto r=ready(0);assert(send(r,request(2,2,{225,1,31,1,31,0,225,0}))==200);
  assert(r.take(key,0));assert(r.take(key,20)&&key.keycode=='"');
 }
 {auto r=ready();assert(send(r,request(2,2,{4,1,4,0}))==200);assert(r.take(key,0));
  assert(send(r,request(3,3),1)==200);assert(send(r,request(3,3),1)==200);
  assert(r.take(key,1)&&!key.down);assert(!r.take(key,40));assert(r.status(40).reason==RemoteKeyboard::cancelled);
 }
 {auto r=ready();assert(send(r,request(4,2),100)==200);
  // Console captured now at loop entry, then HTTP renewed under the shared
  // lock before console acquired it. A one-ms-old timestamp is not 49 days.
  r.tick(99);assert(r.status(100).reason==RemoteKeyboard::none);
  assert(r.status(5099).reason==RemoteKeyboard::none);
  assert(r.status(5100).reason==RemoteKeyboard::expired);
 }
 {auto r=ready();assert(send(r,request(2,2,{4,1,4,0}),0)==200);
  assert(r.take(key,0));assert(r.take(key,20));
  assert(send(r,request(2,3,{5,1,5,0}),21)==200);
  assert(!r.take(key,21));assert(r.take(key,40));assert(r.take(key,60));
 }
 std::puts("PASS: bounded input, mapping, idempotence, takeover, timeout, admission, timer wrap and cancellation");
}
