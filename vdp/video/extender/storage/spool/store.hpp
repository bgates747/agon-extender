#pragma once
// REMOTE-005 A06: dormant storage primitive, not a UART/HTTP service.
// A single foreground owner supplies an already mounted, private directory and
// serializes all access (including the local-card HTTP service). FAT has no
// general crash-atomic transaction: bad/torn records block reuse for recovery.
// Destruction/invalidation closes files but NEVER deletes staging evidence.
#include "../sd_wire.h"
#include <array>
#include <cstdint>
#include <string>
#include <utility>
#include <cstring>
#include <cerrno>
#include <cstdio>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <dirent.h>

namespace agon::extender::spool {
constexpr size_t chunkLimit = 4096, descriptorLimit = 248, recordSize = 304;
using Binding = std::array<std::uint8_t,28>;
struct Job {
  Binding binding{};
  std::array<std::uint8_t,descriptorLimit> descriptor{};
  std::uint16_t descriptorSize=0;
  std::uint32_t size=0, crc=0;
  bool checkCrc=false;
};
enum class Result { ok, busy, unavailable, invalid, stale, incomplete, integrity, quota, full, io, recovery };
enum class State { empty, partial, sealed, uncertain, committed, retiring };
struct Info { Job job{}; State state=State::empty; std::uint32_t verifiedCrc=0; };
// Syscall seam permits deterministic ENOSPC/sync/unlink fault tests with real
// filesystem bytes. The production defaults are the ESP-IDF POSIX/FatFS idioms.
struct Posix {
  static int open(const char *p,int flags) { return ::open(p,flags,0600); }
  static ssize_t read(int f,void *p,size_t n) { return ::read(f,p,n); }
  static ssize_t write(int f,const void *p,size_t n) { return ::write(f,p,n); }
  static int sync(int f) { return ::fsync(f); }
  static int close(int f) { return ::close(f); }
  static int remove(const char *p) { return ::unlink(p); }
};
inline std::uint32_t crc(const void *p,size_t n) {
  return sd_crc_update(0xffffffffU,static_cast<const std::uint8_t *>(p),n)^0xffffffffU;
}
inline bool path(const std::uint8_t *p,unsigned n) {
  if(n<2 || n>120 || p[0]!='/' || p[n-1]=='/')return false;
  unsigned start=1;
  for(unsigned i=1;i<=n;++i) {
    if(i==n || p[i]=='/') {
      unsigned len=i-start;
      if(!len || (len==1 && p[start]=='.') || (len==2 && p[start]=='.' && p[start+1]=='.') || p[i-1]=='.' || p[i-1]==' ')return false;
      start=i+1;
    } else if(p[i]<32 || p[i]>=127 || std::strchr("\\:%*?\"<>|",p[i]))return false;
  }
  return true;
}
// External COPY (class 7) stages each file under the unchanged parent grant.
// Its descriptor names that file pair; the worker must enforce subtree scope.
inline bool valid(const Job &j) {
  const auto *b=j.binding.data(), *d=j.descriptor.data();
  auto nonzero=[](const std::uint8_t *p,unsigned n){unsigned x=0;while(n--)x|=*p++;return x!=0;};
  if(!nonzero(b,8)||!nonzero(b+8,4)||!nonzero(b+12,4)||!nonzero(b+16,8)||
     (b[24]!=1&&b[24]!=2)||(b[25]!=3&&b[25]!=4&&!(b[25]==7&&b[24]==1))||b[26]||b[27])return false;
  if(j.descriptorSize<8 || j.descriptorSize>descriptorLimit || d[0]!=b[25] || (d[1]&~1U) || d[6] || d[7])return false;
  unsigned a=sd_u16(d+2),z=sd_u16(d+4);
  return 8+a+z==j.descriptorSize && path(d+8,a) && path(d+8+a,z);
}

template<class IO=Posix> class Store {
  using Record=std::array<std::uint8_t,recordSize>;
 public:
  // No default quota or implicit mount/provisioning; integration owns both.
  Store(std::string directory,std::uint32_t quota):root_(std::move(directory)),quota_(quota) {}
  Store(const Store &)=delete; Store &operator=(const Store &)=delete;
  ~Store(){invalidate();}
  void invalidate(){if(fd_>=0){IO::close(fd_);fd_=-1;}active_=false;}
  Result inspect(Info &out) {
    if(active_)return Result::busy;
    bool empty=false;auto r=scan(empty);if(r!=Result::ok)return r;
    if(empty){info_={};out=info_;return Result::ok;}
    Record m{},retired{};bool have=false,ret=false;
    r=load("manifest",m,have);if(r!=Result::ok)return r;
    r=load("retired",retired,ret);if(r!=Result::ok)return r;
    if(!have&&!ret)return Result::recovery;
    if(have&&ret&&!same(m,retired))return Result::recovery;
    record_=have?m:retired;decode(record_,info_.job);info_.verifiedCrc=sd_u32(record_.data()+296);
    info_.state=State::partial;
    if(ret){info_.state=State::retiring;out=info_;return Result::ok;}
    Record sealed{},flight{},committed{};bool s=false,f=false,c=false;
    if((r=load("complete",sealed,s))!=Result::ok || (r=load("inflight",flight,f))!=Result::ok ||
       (r=load("committed",committed,c))!=Result::ok)return r;
    if((s&&!same(m,sealed)) || (f&&(!s||flight!=sealed)) || (c&&(!f||committed!=sealed)))return Result::recovery;
    if(s){
      info_.verifiedCrc=sd_u32(sealed.data()+296);
      r=digest(info_.job.size,info_.verifiedCrc);if(r!=Result::ok)return r;
      record_=sealed;info_.state=c?State::committed:f?State::uncertain:State::sealed;
    }
    out=info_;return Result::ok;
  }
  Result begin(const Job &job) {
    if(active_)return Result::busy;
    if(!valid(job))return Result::invalid;
    // The target POSIX off_t may be signed 32-bit. Keep seekable snapshots
    // within that bound even if a caller configures a larger payload quota.
    if(job.size>quota_ || job.size>0x7fffffffU)return Result::quota;
    bool empty=false;auto r=scan(empty);if(r!=Result::ok)return r;
    if(!empty)return Result::recovery;
    record_=encode(job,0);info_={job,State::partial,0};written_=0;rolling_=0xffffffffU;
    if((r=save("manifest",record_))!=Result::ok)return r;
    fd_=IO::open(file("payload").c_str(),O_WRONLY|O_CREAT|O_EXCL);
    if(fd_<0)return failure(errno);
    active_=true;return Result::ok;
  }
  Result append(const Binding &b,std::uint32_t offset,const void *data,size_t n) {
    auto r=owner(b);if(r!=Result::ok)return r;
    if(info_.state!=State::partial || fd_<0)return Result::invalid;
    if(offset!=written_ || !n || n>chunkLimit || n>info_.job.size-written_ || !data)return Result::invalid;
    if(!writeAll(fd_,data,n)){int error=errno;invalidate();return failure(error);}
    rolling_=sd_crc_update(rolling_,static_cast<const std::uint8_t *>(data),n);
    written_+=n;return Result::ok;
  }
  Result seal(const Binding &b) {
    auto r=owner(b);if(r!=Result::ok)return r;
    if(info_.state!=State::partial || fd_<0)return Result::invalid;
    if(written_!=info_.job.size)return Result::incomplete;
    auto sum=rolling_^0xffffffffU;
    if(info_.job.checkCrc && sum!=info_.job.crc){invalidate();return Result::integrity;}
    bool synced=IO::sync(fd_)==0;int error=errno;int closed=IO::close(fd_);fd_=-1;
    if(!synced||closed){active_=false;return failure(synced?errno:error);}
    if((r=digest(written_,sum))!=Result::ok){active_=false;return r;}
    record_=encode(info_.job,sum);
    if((r=save("complete",record_))!=Result::ok){active_=false;return r;}
    info_.state=State::sealed;info_.verifiedCrc=sum;return Result::ok;
  }
  Result read(const Binding &b,std::uint32_t offset,void *data,size_t capacity,size_t &count) {
    count=0;auto r=owner(b);if(r!=Result::ok)return r;
    if(info_.state!=State::sealed && info_.state!=State::committed)return Result::incomplete;
    if(offset>info_.job.size || !data || !capacity || capacity>chunkLimit)return Result::invalid;
    int f=IO::open(file("payload").c_str(),O_RDONLY);if(f<0)return Result::io;
    size_t n=info_.job.size-offset;if(n>capacity)n=capacity;
    bool ok=::lseek(f,offset,SEEK_SET)>=0 && readAll(f,data,n);
    int closed=IO::close(f);if(!ok||closed)return Result::io;
    count=n;return Result::ok;
  }
  // Persist BEFORE issuing a remote activation. A failed marker means the
  // caller must not send activation. No source/destination file is touched here.
  Result activationStarted(const Binding &b){return transition(b,State::sealed,State::uncertain,"inflight");}
  // Caller may invoke only after an exact matching remote commit confirmation.
  Result confirmed(const Binding &b){return transition(b,State::uncertain,State::committed,"committed");}
  // Explicit release/abandonment; never an automatic destructor/TTL action.
  // Recovered jobs can be discarded, but cannot resume execution or serving.
  Result discard(const Binding &b) {
    if(!active_){Info found;auto r=inspect(found);if(r!=Result::ok)return r;}
    if(info_.state==State::empty || b!=info_.job.binding)return Result::stale;
    if(info_.state==State::uncertain)return Result::recovery;
    bool empty=false;auto r=scan(empty);if(r!=Result::ok)return r;
    invalidate();
    if(info_.state!=State::retiring){
      if((r=save("retired",record_))!=Result::ok)return r;
      info_.state=State::retiring;
    }
    // Retired contains the complete manifest so a crash after manifest removal
    // still identifies cleanup. Remove its proof LAST. Never traverse a tree.
    for(auto name:{"payload","complete","inflight","committed","manifest","retired"})
      if(IO::remove(file(name).c_str()) && errno!=ENOENT)return Result::io;
    info_={};return Result::ok;
  }
 private:
  std::string root_;std::uint32_t quota_,written_=0,rolling_=0xffffffffU;
  int fd_=-1;bool active_=false;Info info_{};Record record_{};
  static Result failure(int error){return error==ENOSPC?Result::full:Result::io;}
  std::string file(const char *name)const{return root_+"/"+name;}
  Result owner(const Binding &b)const{return active_ && b==info_.job.binding?Result::ok:Result::stale;}
  static bool readAll(int f,void *p,size_t n){
    auto *b=static_cast<std::uint8_t *>(p);
    while(n){auto got=IO::read(f,b,n);if(got<0&&errno==EINTR)continue;if(got<=0)return false;b+=got;n-=got;}return true;
  }
  static bool writeAll(int f,const void *p,size_t n){
    auto *b=static_cast<const std::uint8_t *>(p);
    while(n){auto got=IO::write(f,b,n);if(got<0&&errno==EINTR)continue;if(got<=0)return false;b+=got;n-=got;}return true;
  }
  static Record encode(const Job &j,std::uint32_t verified){
    Record r{};auto *p=r.data();std::memcpy(p,"ESP1",4);std::memcpy(p+4,j.binding.data(),28);
    sd_put16(p+32,j.descriptorSize);p[34]=j.checkCrc;sd_put32(p+36,j.size);sd_put32(p+40,j.crc);
    std::memcpy(p+44,j.descriptor.data(),j.descriptorSize);sd_put32(p+292,crc(p,292));
    sd_put32(p+296,verified);sd_put32(p+300,crc(p,300));return r;
  }
  static void decode(const Record &r,Job &j){
    j={};auto *p=r.data();std::memcpy(j.binding.data(),p+4,28);j.descriptorSize=sd_u16(p+32);
    j.checkCrc=p[34];j.size=sd_u32(p+36);j.crc=sd_u32(p+40);
    std::memcpy(j.descriptor.data(),p+44,descriptorLimit);
  }
  static bool same(const Record &a,const Record &b){return std::memcmp(a.data(),b.data(),296)==0;}
  Result load(const char *name,Record &r,bool &have){
    have=false;int f=IO::open(file(name).c_str(),O_RDONLY);
    if(f<0)return errno==ENOENT?Result::ok:Result::io;
    std::uint8_t extra;bool ok=readAll(f,r.data(),r.size()) && IO::read(f,&extra,1)==0;
    int closed=IO::close(f);if(!ok||closed)return Result::recovery;
    Job j;decode(r,j);
    if(!valid(j) || encode(j,sd_u32(r.data()+296))!=r)return Result::recovery;
    have=true;return Result::ok;
  }
  Result save(const char *name,const Record &r){
    int f=IO::open(file(name).c_str(),O_WRONLY|O_CREAT|O_EXCL);if(f<0)return failure(errno);
    bool ok=writeAll(f,r.data(),r.size()) && IO::sync(f)==0;int error=errno;
    int closed=IO::close(f);return ok&&!closed?Result::ok:failure(ok?errno:error);
  }
  Result digest(std::uint32_t size,std::uint32_t expected){
    int f=IO::open(file("payload").c_str(),O_RDONLY);if(f<0)return Result::recovery;
    std::array<std::uint8_t,chunkLimit> buf{};std::uint32_t total=0,sum=0xffffffffU;bool ok=true;
    for(;;){auto n=IO::read(f,buf.data(),buf.size());if(n<0&&errno==EINTR)continue;if(n<0){ok=false;break;}if(!n)break;
      if(static_cast<std::uint32_t>(n)>size-total){ok=false;break;}
      total+=n;sum=sd_crc_update(sum,buf.data(),n);
    }
    int closed=IO::close(f);
    return ok&&!closed&&total==size&&(sum^0xffffffffU)==expected?Result::ok:Result::integrity;
  }
  Result scan(bool &empty){
    empty=true;if(root_.empty()||root_.size()>240||root_.front()!='/'||root_.back()=='/')return Result::invalid;
    DIR *d=opendir(root_.c_str());if(!d)return Result::unavailable;
    Result r=Result::ok;
    for(;;){errno=0;auto *e=readdir(d);if(!e){if(errno)r=Result::io;break;}
      if(!std::strcmp(e->d_name,".")||!std::strcmp(e->d_name,".."))continue;
      bool known=false;for(auto name:{"manifest","payload","complete","inflight","committed","retired"})if(!std::strcmp(e->d_name,name))known=true;
      struct stat st{};
      if(!known || ::stat(file(e->d_name).c_str(),&st) || !S_ISREG(st.st_mode)){r=Result::recovery;break;}
      empty=false;
    }
    closedir(d);return r;
  }
  Result transition(const Binding &b,State from,State to,const char *name){
    auto r=owner(b);if(r!=Result::ok)return r;if(info_.state!=from)return Result::invalid;
    r=save(name,record_);if(r==Result::ok)info_.state=to;else invalidate();return r;
  }
};
} // namespace agon::extender::spool
