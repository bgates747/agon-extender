#include "extender/display/rgb222_bgr_lut.hpp"
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdio>
#include <vector>
#include <sys/mman.h>
#include <unistd.h>
using agon::extender::display::storeRgb222Bgr;
using agon::extender::display::storeRgba2222BgrSpan;
using agon::extender::display::storeNativeRgb222BgrSpan;
void reference(std::uint8_t *d,const std::uint8_t *s,std::size_t n) {
  for(;n;--n,++s,d+=3) {
    const auto p=*s;
    d[0]=((p>>4)&3)*85;d[1]=((p>>2)&3)*85;d[2]=(p&3)*85;
  }
}
void rgbaReference(std::uint8_t *d,const std::uint8_t *s,std::size_t n) {
  for(;n;--n,++s,d+=3)
    if(*s & 0xc0) reference(d,s,1);
}
int main() {
  unsigned checked=0;
  for(unsigned colour=0;colour<256;++colour) {
    std::array<std::uint8_t,5> got{{19,0,0,0,31}},want=got;
    auto c=std::uint8_t(colour);reference(want.data()+1,&c,1);
    storeRgb222Bgr(got.data()+1,c);assert(got==want);++checked;
  }
  for(unsigned sa=0;sa<16;++sa)for(unsigned da=0;da<16;++da)
    for(unsigned n=0;n<=1024;++n) {
      std::vector<std::uint8_t> input(32+sa+n+32),output(32+da+3*n+32,0xad);
      for(unsigned i=0;i<input.size();++i)input[i]=i*37+sa*13+n;
      const auto unchanged=input;auto want=output;
      reference(want.data()+32+da,input.data()+32+sa,n);
      storeNativeRgb222BgrSpan(output.data()+32+da,input.data()+32+sa,n);
      assert(output==want && input==unchanged);++checked;
      std::fill(output.begin(),output.end(),0xad);want=output;
      rgbaReference(want.data()+32+da,input.data()+32+sa,n);
      storeRgba2222BgrSpan(output.data()+32+da,input.data()+32+sa,n);
      assert(output==want && input==unchanged);++checked;
    }
  // Every four-pixel alpha combination must preserve binary alpha, including
  // opaque groups mixing classes1/2/3. Heads/tails and raw non-quantized bytes
  // make an accidental transparent-pixel rewrite visible.
  for(unsigned alpha=0;alpha<256;++alpha)for(unsigned sa=0;sa<4;++sa)
    for(unsigned da=0;da<4;++da) {
      alignas(16)std::array<std::uint8_t,64> input{},output{};
      for(unsigned i=0;i<input.size();++i)input[i]=i*37+alpha;
      for(unsigned i=0;i<4;++i)
        input[16+sa+da+i]=((alpha>>(i*2))&3)*64+((alpha+i*17)&63);
      output.fill(0xad);auto want=output;
      const auto unchanged=input;const unsigned n=da+7;
      rgbaReference(want.data()+16+da,input.data()+16+sa,n);
      storeRgba2222BgrSpan(output.data()+16+da,input.data()+16+sa,n);
      assert(output==want && input==unchanged);++checked;
    }
  // Compare to the original incremental getter/setter when the user's Native
  // source aliases destination in either direction. Must not prefetch 4 pixels.
  for(unsigned n=1;n<=80;++n)for(int delta=-32;delta<=32;++delta) {
    std::vector<std::uint8_t> got(512);
    for(unsigned i=0;i<got.size();++i)got[i]=i*37+n*19+delta;
    auto want=got;
    reference(want.data()+80+delta,want.data()+80,n);
    storeNativeRgb222BgrSpan(got.data()+80+delta,got.data()+80,n);
    assert(got==want);++checked;
    for(unsigned i=0;i<got.size();++i)got[i]=i*37+n*19+delta;
    want=got;
    rgbaReference(want.data()+80+delta,want.data()+80,n);
    storeRgba2222BgrSpan(got.data()+80+delta,got.data()+80,n);
    assert(got==want);++checked;
  }
  // End-of-page guards expose accidental source read-ahead and output overrun.
  const auto page=std::size_t(sysconf(_SC_PAGESIZE));
  auto *src=(std::uint8_t*)mmap(nullptr,3*page,PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
  auto *dst=(std::uint8_t*)mmap(nullptr,3*page,PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
  assert(src!=MAP_FAILED && dst!=MAP_FAILED);
  assert(mprotect(src+page,page,PROT_READ|PROT_WRITE)==0);
  assert(mprotect(dst+page,page,PROT_READ|PROT_WRITE)==0);
  for(unsigned n=1;n<=512;++n) {
    auto *s=src+2*page-n;auto *d=dst+2*page-3*n;
    for(unsigned i=0;i<n;++i)s[i]=i*37+n;
    std::vector<std::uint8_t> want(3*n);reference(want.data(),s,n);
    storeNativeRgb222BgrSpan(d,s,n);assert(std::equal(want.begin(),want.end(),d));++checked;
    std::fill(dst+page,dst+2*page,0xad);std::fill(want.begin(),want.end(),0xad);
    rgbaReference(want.data(),s,n);
    storeRgba2222BgrSpan(d,s,n);assert(std::equal(want.begin(),want.end(),d));++checked;
  }
  munmap(src,3*page);munmap(dst,3*page);
  std::printf("PASS: %u RGB222 LUT/Native/RGBA cases, alpha groups, byte ABI, alias order and guard pages\n",checked);
}
