#include "extender/storage/spool/store.hpp"
#include <cassert>
#include <filesystem>
#include <fstream>
#include <vector>
#include <iostream>
using namespace agon::extender::spool;
namespace fs=std::filesystem;
struct Faults:Posix {
  static inline long bytes=-1;
  static inline bool failSync=false,failRemove=false;
  static inline const char *removeName="";
  static ssize_t write(int f,const void *p,size_t n){
    if(bytes==0){errno=ENOSPC;return -1;}
    if(bytes>0&&n>size_t(bytes))n=bytes;
    auto r=Posix::write(f,p,n);if(bytes>=0&&r>0)bytes-=r;return r;
  }
  static int sync(int f){if(failSync){errno=EIO;return -1;}return Posix::sync(f);}
  static int remove(const char *p){if(failRemove&&std::strstr(p,removeName)){errno=EIO;return -1;}return Posix::remove(p);}
  static void clear(){bytes=-1;failSync=failRemove=false;removeName="";}
};
using Spool=Store<Faults>;
static Job job(size_t n){
  Job j;j.size=n;auto *b=j.binding.data();b[0]=1;b[8]=2;b[12]=3;b[16]=4;b[24]=2;b[25]=3;
  std::string a="/source.bin",z="/destination.bin";auto *d=j.descriptor.data();d[0]=3;
  sd_put16(d+2,a.size());sd_put16(d+4,z.size());std::memcpy(d+8,a.data(),a.size());std::memcpy(d+8+a.size(),z.data(),z.size());j.descriptorSize=8+a.size()+z.size();return j;
}
static std::string contents(const fs::path &p){std::ifstream f(p,std::ios::binary);return {std::istreambuf_iterator<char>(f),{}};}
int main(){
 char tmp[]="/tmp/extender-spool-XXXXXX";auto *base=mkdtemp(tmp);assert(base);std::string dir=std::string(base)+"/slot";fs::create_directory(dir);
 auto fresh=[&](){Faults::clear();fs::remove_all(dir);fs::create_directory(dir);};
 for(size_t n:{0,1,211,212,213,4096,8193}){
  fresh();std::vector<unsigned char> data(n);for(size_t i=0;i<n;++i)data[i]=(i*17+3)&255;
  auto j=job(n);j.checkCrc=true;j.crc=crc(data.data(),n);Spool s(dir,9000);assert(s.begin(j)==Result::ok);
  Info info;assert(s.inspect(info)==Result::busy);assert(s.begin(j)==Result::busy);
  unsigned char out[4096];size_t got=9;assert(s.read(j.binding,0,out,sizeof out,got)==Result::incomplete&&got==0);
  auto wrong=j.binding;wrong[8]++;assert(s.append(wrong,0,"x",1)==Result::stale);
  size_t offset=0;while(offset<n){auto k=std::min(n-offset,chunkLimit);assert(s.append(j.binding,offset,data.data()+offset,k)==Result::ok);offset+=k;}
  assert(s.seal(j.binding)==Result::ok);
  std::vector<unsigned char> result;offset=0;
  do{assert(s.read(j.binding,offset,out,sizeof out,got)==Result::ok);result.insert(result.end(),out,out+got);offset+=got;}while(got);
  assert(result==data);assert(s.activationStarted(j.binding)==Result::ok);assert(s.discard(j.binding)==Result::recovery);
  assert(s.confirmed(j.binding)==Result::ok);assert(s.discard(j.binding)==Result::ok);assert(fs::is_empty(dir));
 }
 fresh();auto j=job(3);Spool s(dir,3);assert(s.begin(job(4))==Result::quota);
 auto invalid=j;invalid.binding[0]=0;assert(s.begin(invalid)==Result::invalid);
 invalid=j;invalid.descriptorSize=249;assert(s.begin(invalid)==Result::invalid);
 assert(s.begin(j)==Result::ok);assert(s.append(j.binding,1,"abc",3)==Result::invalid);
 assert(s.append(j.binding,0,"ab",2)==Result::ok);assert(s.seal(j.binding)==Result::incomplete);
 s.invalidate();assert(s.append(j.binding,2,"c",1)==Result::stale);
 {Spool restart(dir,3);Info i;assert(restart.inspect(i)==Result::ok&&i.state==State::partial);
  size_t got;char out[3];assert(restart.read(j.binding,0,out,3,got)==Result::stale);assert(restart.begin(j)==Result::recovery);
  auto wrong=j.binding;wrong[12]++;assert(restart.discard(wrong)==Result::stale);assert(contents(dir+"/payload")=="ab");
  assert(restart.discard(j.binding)==Result::ok);}
 // A sealed snapshot survives reset, but does not re-admit its old owner.
 fresh();{Spool a(dir,3);assert(a.begin(j)==Result::ok);assert(a.append(j.binding,0,"abc",3)==Result::ok);assert(a.seal(j.binding)==Result::ok);}
 {Spool a(dir,3);Info i;assert(a.inspect(i)==Result::ok&&i.state==State::sealed&&i.verifiedCrc==crc("abc",3));assert(a.confirmed(j.binding)==Result::stale);assert(a.discard(j.binding)==Result::ok);}
 // Remote ACK loss: neither reset nor explicit abandon deletes the uncertain copy.
 fresh();{Spool a(dir,3);assert(a.begin(j)==Result::ok);assert(a.append(j.binding,0,"abc",3)==Result::ok);assert(a.seal(j.binding)==Result::ok);assert(a.activationStarted(j.binding)==Result::ok);}
 {Spool a(dir,3);Info i;assert(a.inspect(i)==Result::ok&&i.state==State::uncertain);assert(a.discard(j.binding)==Result::recovery);assert(contents(dir+"/payload")=="abc");}
 // Confirmed commit survives reset and permits explicit cleanup.
 fresh();{Spool a(dir,3);assert(a.begin(j)==Result::ok);assert(a.append(j.binding,0,"abc",3)==Result::ok);assert(a.seal(j.binding)==Result::ok);assert(a.activationStarted(j.binding)==Result::ok);assert(a.confirmed(j.binding)==Result::ok);}
 {Spool a(dir,3);Info i;assert(a.inspect(i)==Result::ok&&i.state==State::committed);assert(a.discard(j.binding)==Result::ok);}
 // Disk-full after a short write: preserve exact partial bytes, never seal/read.
 fresh();{Spool a(dir,3);assert(a.begin(j)==Result::ok);Faults::bytes=2;assert(a.append(j.binding,0,"abc",3)==Result::full);Faults::clear();assert(contents(dir+"/payload")=="ab");assert(a.seal(j.binding)==Result::stale);assert(a.discard(j.binding)==Result::ok);}
 // Failed sync leaves partial state, not a complete snapshot.
 fresh();{Spool a(dir,3);assert(a.begin(j)==Result::ok);assert(a.append(j.binding,0,"abc",3)==Result::ok);Faults::failSync=true;assert(a.seal(j.binding)==Result::io);Faults::clear();Info i;assert(a.inspect(i)==Result::ok&&i.state==State::partial);assert(a.discard(j.binding)==Result::ok);}
 // Torn manifest, complete marker, or altered payload must block automatic use.
 fresh();{Spool a(dir,3);Faults::bytes=50;assert(a.begin(j)==Result::full);Faults::clear();Info i;assert(a.inspect(i)==Result::recovery);assert(a.discard(j.binding)==Result::recovery);}
 fresh();{Spool a(dir,3);assert(a.begin(j)==Result::ok);assert(a.append(j.binding,0,"abc",3)==Result::ok);Faults::bytes=50;assert(a.seal(j.binding)==Result::full);Faults::clear();Info i;assert(a.inspect(i)==Result::recovery);assert(contents(dir+"/payload")=="abc");}
 fresh();{Spool a(dir,3);assert(a.begin(j)==Result::ok);assert(a.append(j.binding,0,"abc",3)==Result::ok);assert(a.seal(j.binding)==Result::ok);}
 {std::ofstream f(dir+"/payload",std::ios::binary);f<<"abd";}
 {Spool a(dir,3);Info i;assert(a.inspect(i)==Result::integrity);assert(a.discard(j.binding)==Result::integrity);}
 // Every cleanup interruption can finish after restart, even with manifest gone.
 for(auto name:{"payload","complete","inflight","committed","manifest","retired"}){
  fresh();{Spool a(dir,3);assert(a.begin(j)==Result::ok);assert(a.append(j.binding,0,"abc",3)==Result::ok);assert(a.seal(j.binding)==Result::ok);assert(a.activationStarted(j.binding)==Result::ok);assert(a.confirmed(j.binding)==Result::ok);Faults::failRemove=true;Faults::removeName=name;assert(a.discard(j.binding)==Result::io);}
  Faults::clear();Spool a(dir,3);Info i;assert(a.inspect(i)==Result::ok&&i.state==State::retiring);assert(a.discard(j.binding)==Result::ok);assert(fs::is_empty(dir));
 }
 // Unknown files are never swept; no missing-card RAM fallback or auto-mkdir.
 fresh();{std::ofstream f(dir+"/user.txt");f<<"keep";}
 {Spool a(dir,3);Info i;assert(a.begin(j)==Result::recovery);assert(a.inspect(i)==Result::recovery);assert(contents(dir+"/user.txt")=="keep");}
 {Spool a(std::string(base)+"/missing",3);assert(a.begin(j)==Result::unavailable);assert(!fs::exists(std::string(base)+"/missing"));}
 fresh();j.checkCrc=true;j.crc=0;
 {Spool a(dir,3);assert(a.begin(j)==Result::ok);assert(a.append(j.binding,0,"abc",3)==Result::ok);assert(a.seal(j.binding)==Result::integrity);assert(!fs::exists(dir+"/complete"));}
 
 // Invalid descriptors, per-field stale owners and the target seek-size bound.
 fresh();j=job(3);
 {Spool a(dir,0xffffffffU);auto huge=j;huge.size=0x80000000U;assert(a.begin(huge)==Result::quota);}
 for(auto bad:{"/../x","/x/","/x//y","/a%2fb","/x/..","/x\\y","/x.","relative"})assert(!path(reinterpret_cast<const std::uint8_t *>(bad),std::strlen(bad)));
 {Spool a(dir,3);assert(a.begin(j)==Result::ok);
  for(unsigned index=0;index<28;++index){auto b=j.binding;b[index]^=1;assert(a.append(b,0,"abc",3)==Result::stale);}
  assert(a.discard(j.binding)==Result::ok);}
 for(unsigned damage=0;damage<3;++damage){
  fresh();{Spool a(dir,3);assert(a.begin(j)==Result::ok);assert(a.append(j.binding,0,"abc",3)==Result::ok);assert(a.seal(j.binding)==Result::ok);}
  if(damage==0)fs::resize_file(dir+"/payload",2);
  else if(damage==1){std::ofstream f(dir+"/payload",std::ios::app);f<<"extra";}
  else fs::remove(dir+"/payload");
  Spool a(dir,3);Info i;auto r=a.inspect(i);assert(r==Result::integrity || r==Result::recovery);assert(fs::exists(dir+"/manifest"));
 }
 // Interrupted activation/commit markers conservatively preserve the payload.
 for(bool commit:{false,true}){
  fresh();Spool a(dir,3);assert(a.begin(j)==Result::ok);assert(a.append(j.binding,0,"abc",3)==Result::ok);assert(a.seal(j.binding)==Result::ok);
  if(commit)assert(a.activationStarted(j.binding)==Result::ok);
  Faults::bytes=40;assert((commit?a.confirmed(j.binding):a.activationStarted(j.binding))==Result::full);Faults::clear();
  Info i;assert(a.inspect(i)==Result::recovery);assert(a.discard(j.binding)==Result::recovery);assert(contents(dir+"/payload")=="abc");
 }
 fs::remove_all(base);std::cout<<"P4 spool lifecycle and fault tests PASS\n";
}
