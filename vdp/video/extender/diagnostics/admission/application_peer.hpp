// R05-A05 controlled RAM-only peer. Never production storage: exactly 1027
// synthetic bytes and two fixed paths, no card access or arbitrary file names.
#pragma once
#include <cstdint>
#include <cstring>
#include "../../storage/sd_wire.h"
namespace agon::extender::storage {
struct ApplicationProbe {
  std::uint8_t reply[240]{}, prefix[28]{}, descriptor[248]{}, stage[1027]{};
  unsigned pending=0, offset=0,total=0,size=0,written=0,complete=0,blocked=0;
  std::uint32_t descriptor_crc=0,file_session=0,file_sequence=0,transfer=0,expected_crc=0;
  bool active=false,ready=false,finished=false;
  void reset(){pending=offset=total=size=written=0;active=ready=finished=false;file_sequence=0;}
  unsigned take(std::uint8_t *p){auto n=pending;std::memcpy(p,reply,n);pending=0;return n;}
  bool receive(const std::uint8_t *p,unsigned n,const std::uint8_t *nonce){
    if(n==48 && p[3]==4 && p[12]==1)return false; // shared diagnostic HELLO
    if(n<20 || n>240 || p[0]!='S'||p[1]!='D'||p[2]!=1 || sd_u16(p+14)!=n-20)return false;
    if(p[3]!=1 && !(p[3]==4 && n>=48 && p[44]==2))return false;
    auto crc=sd_crc_update(0xffffffffU,p,16);crc=sd_crc_update(crc,p+20,n-20)^0xffffffffU;
    if(crc!=sd_u32(p+16) || pending)return true;
    std::memcpy(reply,p,20);reply[13]=0;
    if(p[3]==4){
      reply[3]=5;sd_put16(reply+14,28);std::memcpy(reply+20,p+20,28);
      if(std::memcmp(p+20,nonce,8) || (p[45]!=3 && p[45]!=4))return true;
      if(p[12]==5){
        if(n<56)return true;
        auto at=sd_u16(p+50);auto length=sd_u16(p+48);
        if(!active){if(at || !length || length>248)return true;reset();active=true;total=length;descriptor_crc=sd_u32(p+52);std::memcpy(prefix,p+20,28);sd_put32(prefix+12,73);}
        if(at!=offset || length!=total || sd_u32(p+52)!=descriptor_crc || offset+n-56>total)return true;
        std::memcpy(descriptor+offset,p+56,n-56);offset+=n-56;
        if(offset==total && sd_crc(descriptor,total)!=descriptor_crc)return true;
        sd_put32(reply+32,73);
      }else {
        if(!active || std::memcmp(p+20,prefix,28))return true;
        if(p[12]==4){
          if(offset!=total || total<8)return true;
          unsigned a=sd_u16(descriptor+2),b=sd_u16(descriptor+4);
          if(a+b+8!=total || descriptor[0]!=p[45] || descriptor[1]>1 || descriptor[6] || descriptor[7])return true;
          const char *local="/agents/extender/results/a05-in.bin";
          const char *remote=descriptor[0]==3?"/p4/source.bin":"/p4/output.bin";
          const char *src=descriptor[0]==3?remote:local,*dst=descriptor[0]==3?local:remote;
          if(a!=std::strlen(src)||b!=std::strlen(dst)||std::memcmp(descriptor+8,src,a)||std::memcmp(descriptor+8+a,dst,b))return true;
          file_session=sd_crc(prefix,28);if(!file_session)file_session=1;ready=true;
        }else if(p[12]==8){reply[13]=9;}
        else if(p[12]==9){if(n!=49)return true;}
        else if(p[12]==10){active=ready=false;}
        else return true;
      }
      sd_seal(reply);pending=48;return true;
    }
    if(!active || !ready || sd_u32(p+4)!=file_session || sd_u32(p+8)!=file_sequence+1)return true;
    ++file_sequence;reply[3]=2;unsigned len=0;auto q=p+20;auto count=n-20;
    if(p[12]==1 && !count){sd_put32(reply+20,91);sd_put16(reply+24,212);sd_put16(reply+26,15);len=8;}
    else if(p[12]==2 && prefix[25]==4){reply[13]=6;reply[20]=4;len=1;}
    else if(p[12]==4 && prefix[25]==3 && count==21 && q[6]==14 && !std::memcmp(q+7,"/p4/source.bin",14)){
      auto at=sd_u32(q);unsigned take=sd_u16(q+4);if(at>1027 || take>212)return true;
      if(take>1027-at)take=1027-at;sd_put32(reply+20,1027);len=take+4;
      for(unsigned i=0;i<take;++i)reply[24+i]=((at+i)*17+3)&255;
    }else if(p[12]==5 && prefix[25]==4 && count==27 && q[12]==14 && !std::memcmp(q+13,"/p4/output.bin",14)){
      transfer=sd_u32(q);size=sd_u32(q+4);expected_crc=sd_u32(q+8);if(size!=1027 || !transfer)return true;
      written=0;finished=false;sd_put32(reply+20,transfer);sd_put32(reply+24,0);len=8;
    }else if(p[12]==6 && count>=9 && prefix[25]==4 && sd_u32(q)==transfer && sd_u32(q+4)==written && count-8<=size-written){
      std::memcpy(stage+written,q+8,count-8);written+=count-8;sd_put32(reply+20,transfer);sd_put32(reply+24,written);len=8;
    }else if(p[12]==7 && count==4 && prefix[25]==4 && sd_u32(q)==transfer && written==size && sd_crc(stage,size)==expected_crc){
      finished=true;sd_put32(reply+20,size);sd_put32(reply+24,expected_crc);len=8;
    }else if(p[12]==8 && count==4 && prefix[25]==4 && sd_u32(q)==transfer && finished){
      bool equal=true;for(unsigned i=0;i<size;++i)if(stage[i]!=std::uint8_t(i*17+3))equal=false;
      if(equal)++complete;else reply[13]=7;
    }else reply[13]=1;
    sd_put16(reply+14,len);sd_seal(reply);pending=20+len;return true;
  }
};
}
