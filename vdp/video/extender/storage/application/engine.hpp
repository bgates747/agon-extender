#pragma once
// Application-origin service. Called ONLY by the storage worker, never UART/ISR.
// Reuses the durable spool and local FAT replacement idiom. Failed/uncertain
// jobs retain staging evidence; no replay or speculative recovery is performed.
#include "../spool/store.hpp"
#include "../local/files.hpp"
#include <memory>
namespace agon::extender::storage::application {
class Engine {
  std::string root_, directory_, source_, destination_;
  std::unique_ptr<spool::Store<>> store_;
  spool::Job job_{};
  std::uint8_t nonce_[8]{}, last_[240]{}, cached_[240]{}, descriptor_[248]{};
  unsigned lastN_=0, cachedN_=0, total_=0, offset_=0;
  std::uint32_t session_=0, sequence_=0, fileSequence_=0, fileSession_=0,
                descriptorCrc_=0, transfer_=0, written_=0;
  bool claimed_=false, ready_=false, staged_=false, sealed_=false,
       committed_=false, finished_=false, success_=false;
  static bool valid(const std::uint8_t *p,unsigned n) {
    if(n<20||n>240||p[0]!='S'||p[1]!='D'||p[2]!=1||sd_u16(p+14)!=n-20)return false;
    auto c=sd_crc_update(0xffffffffU,p,16);
    return (sd_crc_update(c,p+20,n-20)^0xffffffffU)==sd_u32(p+16);
  }
  bool equalPath(const std::uint8_t *p,unsigned n,const std::string &s) {
    return n==s.size()+1 && p[0]==s.size() && !std::memcmp(p+1,s.data(),s.size());
  }
  bool snapshot() {
    struct stat st{};
    auto path=root_+source_;
    if(stat(path.c_str(),&st)||!S_ISREG(st.st_mode)||st.st_size<0||st.st_size>32*1024*1024)return false;
    job_.size=st.st_size;
    if(store_->begin(job_)!=spool::Result::ok)return false;
    staged_=true;
    FILE *f=fopen(path.c_str(),"rb");if(!f)return false;
    std::uint8_t buf[4096];unsigned at=0;bool ok=true;
    while(at<job_.size) {
      unsigned n=std::min<unsigned>(sizeof buf,job_.size-at);
      if(fread(buf,1,n,f)!=n || store_->append(job_.binding,at,buf,n)!=spool::Result::ok){ok=false;break;}
      at+=n;
    }
    if(ok && fgetc(f)!=EOF)ok=false;
    if(ferror(f))ok=false;
    if(fclose(f))ok=false;
    if(ok)ok=store_->seal(job_.binding)==spool::Result::ok;
    sealed_=ok;return ok;
  }
  bool descriptorOK() {
    if(total_<12 || offset_!=total_ || sd_crc(descriptor_,total_)!=descriptorCrc_)return false;
    unsigned a=sd_u16(descriptor_+2),b=sd_u16(descriptor_+4);
    if(a+b+8!=total_||descriptor_[0]!=job_.binding[25]||descriptor_[1]>1||descriptor_[6]||descriptor_[7])return false;
    if(!spool::path(descriptor_+8,a)||!spool::path(descriptor_+8+a,b))return false;
    source_.assign(reinterpret_cast<char*>(descriptor_+8),a);
    destination_.assign(reinterpret_cast<char*>(descriptor_+8+a),b);
    std::string decoded;
    const auto &remote=descriptor_[0]==3?source_:destination_;
    if(!local_sd::decodePath(remote,decoded)||decoded!=remote)return false;
    job_.descriptorSize=total_;std::memcpy(job_.descriptor.data(),descriptor_,total_);
    return spool::valid(job_);
  }
  unsigned file(const std::uint8_t *p,unsigned n,std::uint8_t *out) {
    const auto *q=p+20;unsigned count=n-20,body=0;auto op=p[12];
    out[3]=SD_RESPONSE;out[13]=SD_BAD_REQUEST;sd_put16(out+14,0);
    if(!ready_||finished_||sd_u32(p+4)!=fileSession_||sd_u32(p+8)!=fileSequence_+1)return 20;
    ++fileSequence_;
    auto put=job_.binding[25]==4;
    if(op==SD_HELLO&&!count) {
      sd_put32(out+20,session_);sd_put16(out+24,212);sd_put16(out+26,15);body=8;out[13]=0;
    } else if(op==SD_STAT&&put&&equalPath(q,count,destination_)) {
      struct stat st{};
      if(!stat((root_+destination_).c_str(),&st)) {
        sd_put32(out+20,st.st_size);out[24]=S_ISDIR(st.st_mode)?16:0;body=5;out[13]=0;
      } else {out[13]=SD_FILE_ERROR;out[20]=errno==ENOENT?4:1;body=1;}
    } else if(op==SD_READ&&!put&&count>=7&&equalPath(q+6,count-6,source_)) {
      auto at=sd_u32(q);auto take=sd_u16(q+4);size_t got=0;
      if(take && take<=212 && store_->read(job_.binding,at,out+24,take,got)==spool::Result::ok) {
        sd_put32(out+20,job_.size);body=4+got;out[13]=0;
      }
    } else if(op==SD_BEGIN&&put&&!staged_&&count>=13&&equalPath(q+12,count-12,destination_)&&sd_u32(q)) {
      transfer_=sd_u32(q);job_.size=sd_u32(q+4);job_.crc=sd_u32(q+8);job_.checkCrc=true;
      if(store_->begin(job_)==spool::Result::ok) {
        staged_=true;written_=0;sd_put32(out+20,transfer_);sd_put32(out+24,0);body=8;out[13]=0;
      }
    } else if(op==SD_WRITE&&put&&staged_&&!sealed_&&count>8&&sd_u32(q)==transfer_&&sd_u32(q+4)==written_) {
      if(store_->append(job_.binding,written_,q+8,count-8)==spool::Result::ok) {
        written_+=count-8;sd_put32(out+20,transfer_);sd_put32(out+24,written_);body=8;out[13]=0;
      }
    } else if(op==SD_FINISH&&put&&staged_&&!sealed_&&count==4&&sd_u32(q)==transfer_) {
      if(store_->seal(job_.binding)==spool::Result::ok) {
        sealed_=true;sd_put32(out+20,job_.size);sd_put32(out+24,job_.crc);body=8;out[13]=0;
      }
    } else if(op==SD_ACTIVATE&&put&&sealed_&&!committed_&&count==4&&sd_u32(q)==transfer_) {
      local_sd::Upload upload(root_+destination_,descriptor_[1]!=0);
      bool ok=upload.open();std::uint8_t buf[4096];unsigned at=0;
      while(ok&&at<job_.size) {
        size_t got=0;ok=store_->read(job_.binding,at,buf,sizeof buf,got)==spool::Result::ok && got;
        if(ok){ok=upload.write(reinterpret_cast<char*>(buf),got);at+=got;}
      }
      // Journal uncertainty before the FAT rename. A lost ACK never replays it.
      if(ok)ok=store_->activationStarted(job_.binding)==spool::Result::ok;
      if(ok)ok=upload.finish();
      if(ok)ok=store_->confirmed(job_.binding)==spool::Result::ok;
      if(ok){committed_=true;out[13]=0;}
    }
    sd_put16(out+14,body);return 20+body;
  }
public:
  bool closed=false;
  Engine(std::string root,std::string directory,std::uint32_t a,std::uint32_t b):root_(std::move(root)),directory_(std::move(directory)) {
    sd_put32(nonce_,a?a:1);sd_put32(nonce_+4,b?b:1);
    store_=std::make_unique<spool::Store<>>(directory_,32U*1024U*1024U);
  }
  unsigned process(const std::uint8_t *p,unsigned n,std::uint8_t *out) {
    if(!valid(p,n)||closed||!sd_u32(p+4)||!sd_u32(p+8))return 0;
    if(lastN_ && n==lastN_ && !std::memcmp(p,last_,n)){std::memcpy(out,cached_,cachedN_);return cachedN_;}
    std::memcpy(out,p,n);unsigned size=48;
    if(p[3]==SD_REQUEST) {
      if(p[13])return 0;
      size=file(p,n,out);
    } else if(p[3]==4&&n>=48) {
      out[3]=5;out[13]=6;sd_put16(out+14,28);
      auto op=p[12];auto seq=sd_u32(p+8);
      if(op==1&&!session_&&n==48&&p[44]==2&&p[46]==1) {
        bool empty=true;for(unsigned i=20;i<44;++i)if(p[i])empty=false;
        if(!empty||p[13]||p[45]||p[47])return 0;
        session_=sd_u32(p+4);sequence_=seq;
        std::memset(out+20,0,28);std::memcpy(out+20,nonce_,8);out[46]=11;out[13]=0;
      } else {
        if(sd_u32(p+4)!=session_||seq<=sequence_||std::memcmp(p+20,nonce_,8)||p[44]!=2||p[46]||p[47])return 0;
        sequence_=seq;
        if(op==5 && !ready_ && n>56) {
          unsigned total=sd_u16(p+48),at=sd_u16(p+50),count=n-56;
          if(!claimed_) {
            if(at||total>248||total<12||sd_u32(p+32)||!sd_u32(p+28)||!sd_u32(p+36)||!sd_u32(p+40)||(p[45]!=3&&p[45]!=4))return 0;
            std::memcpy(job_.binding.data(),p+20,28);sd_put32(job_.binding.data()+12,1);
            claimed_=true;total_=total;descriptorCrc_=sd_u32(p+52);
          } else if(std::memcmp(p+20,job_.binding.data(),28))return 0;
          if(at!=offset_||total!=total_||sd_u32(p+52)!=descriptorCrc_||count>total_-offset_)return 0;
          std::memcpy(descriptor_+offset_,p+56,count);offset_+=count;
          sd_put32(out+32,1);out[13]=0;
        } else if(claimed_&&!std::memcmp(p+20,job_.binding.data(),28)) {
          if(op==4&&!ready_&&n==48&&descriptorOK()) {
            if(job_.binding[25]==4||snapshot()) {
              fileSession_=sd_crc(job_.binding.data(),28);if(!fileSession_)fileSession_=1;
              ready_=true;out[13]=0;
            }
          } else if(op==8&&n==48){success_=false;out[13]=9;}
          else if(op==9&&n==49&&p[48]<=3) {
            finished_=true;success_=!p[13] && p[48]==1 && (job_.binding[25]==3?sealed_:committed_);out[13]=0;
          } else if(op==10&&n==48) {
            out[13]=0;
            if(success_&&staged_&&store_->discard(job_.binding)!=spool::Result::ok)out[13]=7;
            closed=true;
          }
        }
      }
    } else return 0;
    sd_seal(out);std::memcpy(last_,p,n);lastN_=n;std::memcpy(cached_,out,size);cachedN_=size;return size;
  }
};
}
