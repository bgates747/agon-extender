// Host qualification of the bounded adapter, with a model of the P4 kernel's
// aligned read/splice contract. This is not execution of the PIE instructions.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <sys/mman.h>
#include <unistd.h>
#include <vector>
#include "extender/display/scroll_copy.hpp"
#include "extender/display/scroll_copy_selftest.hpp"

using namespace agon::extender::display;

struct CheckedBody {
  const std::uint8_t *source;
  std::uint8_t *destination;
  std::size_t bytes;
  unsigned *calls;

  void operator()(std::uint8_t *dst, const std::uint8_t *alignedSrc,
                  std::size_t body, unsigned shift) const
  {
    ++*calls;
    assert((reinterpret_cast<std::uintptr_t>(dst) & 15) == 0);
    assert((reinterpret_cast<std::uintptr_t>(alignedSrc) & 15) == 0);
    assert(body && (body & 31) == 0 && shift < 16);
    assert(alignedSrc >= source);
    assert(alignedSrc + body + (shift ? 16 : 0) <= source + bytes);
    assert(dst >= destination && dst + body <= destination + bytes);
    // Exercise the furthest actual aligned vector read even when its final
    // bytes are not selected by the splice (and a compiler would omit them).
    volatile auto lastRead = alignedSrc[body + (shift ? 16 : 0) - 1];
    (void)lastRead;
    for (std::size_t offset = 0; offset < body; offset += 32) {
      std::array<std::uint8_t,48> vectorReads{};
      std::memcpy(vectorReads.data(), alignedSrc + offset, shift ? 48 : 32);
      std::memcpy(dst + offset, vectorReads.data() + shift, 32);
    }
  }
};

void exercise(std::uint8_t *dst, const std::uint8_t *src, std::size_t bytes)
{
  unsigned calls = 0;
  copyScrollRowBounded(dst, src, bytes, CheckedBody{src, dst, bytes, &calls});
  assert(std::memcmp(dst, src, bytes) == 0);
  assert(calls == unsigned(bytes >= 96));
}

void allAlignments()
{
  alignas(16) std::array<std::uint8_t,4096> source{}, destination{}, expected{};
  for (std::size_t n=0; n<source.size(); ++n) source[n]=(n*73+n/17)&255;
  std::vector<std::size_t> lengths;
  for (std::size_t n=0; n<=192; ++n) lengths.push_back(n);
  for (auto n : {255,256,257,383,384,385,511,512,513,767,768,769,1024,1536,2052}) lengths.push_back(n);
  for (unsigned srcOffset=0; srcOffset<16; ++srcOffset)
    for (unsigned dstOffset=0; dstOffset<16; ++dstOffset)
      for (const auto n : lengths) {
        destination.fill(0xa5); expected.fill(0xa5);
        auto *dst=destination.data()+32+dstOffset;
        const auto *src=source.data()+32+srcOffset;
        std::memcpy(expected.data()+32+dstOffset,src,n);
        exercise(dst,src,n);
        assert(destination==expected);
        // This translation unit is deliberately a host: even when the
        // experimental option is defined, the public entry retains libc.
        destination.fill(0xa5);
        copyScrollRow(dst,src,n);
        assert(destination==expected);
        destination.fill(0xa5);
        copyIndexedSnapshotRow(dst,src,n);
        assert(destination==expected);
      }
}

struct GuardPage {
  std::size_t page=std::size_t(sysconf(_SC_PAGESIZE));
  std::uint8_t *mapping=static_cast<std::uint8_t *>(
      mmap(nullptr,page*3,PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0));
  GuardPage() {
    assert(mapping!=MAP_FAILED);
    assert(mprotect(mapping+page,page,PROT_READ|PROT_WRITE)==0);
  }
  ~GuardPage(){munmap(mapping,page*3);}
  std::uint8_t *begin(){return mapping+page;}
  std::uint8_t *end(){return mapping+page*2;}
};

void pageEdges()
{
  GuardPage source,destination;
  for (const auto n : {1u,31u,64u,95u,96u,97u,127u,128u,129u,768u,1536u,2052u})
    for (unsigned srcOffset=0;srcOffset<16;++srcOffset)
      for (unsigned dstOffset=0;dstOffset<16;++dstOffset)
       for (bool atEnd : {false,true}) {
        auto *src=atEnd?source.end()-n-srcOffset:source.begin()+srcOffset;
        auto *dst=atEnd?destination.end()-n-dstOffset:destination.begin()+dstOffset;
        std::fill(source.begin(),source.end(),0x49);
        std::fill(destination.begin(),destination.end(),0xa5);
        exercise(dst,src,n);
        for(auto *p=destination.begin();p<dst;++p)assert(*p==0xa5);
        for(auto *p=dst+n;p<destination.end();++p)assert(*p==0xa5);
      }
}

void partialViewport()
{
  // Current Nurples geometry:512 logical pixels centred in684 carrier pixels,
  // with a256-pixel field starting at logical x128, below48 top lines.
  constexpr int stride=684*3,height=384,x=(86+128)*3,width=256*3,y1=48;
  constexpr int fieldHeight=height-y1;
  const std::uint8_t clear=0x12;
  for (const int scroll : {1,-1,7,-7,fieldHeight-1,1-fieldHeight,fieldHeight,-fieldHeight}) {
    std::vector<std::uint8_t> actual(stride*height),expected;
    for(std::size_t i=0;i<actual.size();++i)actual[i]=(i*7+i/stride*37)&255;
    expected=actual;
    const auto before=actual;
    const auto amount=std::abs(scroll);
    unsigned calls=0;
    auto copyRow=[&](int srcY,int dstY) {
      auto *dst=actual.data()+dstY*stride+x;
      const auto *src=actual.data()+srcY*stride+x;
      copyScrollRowBounded(dst,src,width,CheckedBody{src,dst,width,&calls});
    };
    if(scroll>0) {
      for(int y=height-amount-1;y>=y1;--y)copyRow(y,y+amount);
    } else {
      for(int y=y1;y<height-amount;++y)copyRow(y+amount,y);
    }
    for(int y=y1;y<height;++y) {
      const auto srcY=y-scroll;
      auto *want=expected.data()+y*stride+x;
      if(srcY>=y1 && srcY<height)std::memcpy(want,before.data()+srcY*stride+x,width);
      else {
        std::memset(want,clear,width);
        std::memset(actual.data()+y*stride+x,clear,width);
      }
    }
    assert(actual==expected);
    assert(calls==unsigned(fieldHeight-amount));
  }
}

int main()
{
  allAlignments();pageEdges();partialViewport();
  assert(scrollCopySelfTest());
  assert(scrollCopySelfTest(copyIndexedSnapshotRow));
  std::puts("PASS: bounded vector-copy model and libc fallback; all16×16 alignments, guard pages,2052-byte stride and exact partial-viewport up/down scrolling");
}
