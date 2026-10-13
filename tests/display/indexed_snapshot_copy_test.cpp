// Actual controller/row descriptors and stock scroll execution on the host.
// PIE instructions require target qualification; scroll_copy_test separately
// proves the unchanged kernel adapter's vector-read bounds with a host model.
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include "canvas.h"
#include "extender/display/indexed_snapshot_copy.hpp"
#include "extender/display/stock_runtime_controller.hpp"

using namespace agon::extender::display;

class Controller : public StockBoundController<fabgl::P4Color64Controller> {
 public:
  ~Controller() override {end();delete mouseCursor();}
  std::uint8_t *row(int y) {return (std::uint8_t *)m_viewPortVisible[y];}
  void row(int y,std::uint8_t *p) {m_viewPortVisible[y]=p;}
};

void exercise(int width,int height,bool doubled,bool decorate)
{
  Controller c;c.begin();
  const auto timings="\"snapshot\" 1 "+std::to_string(width)+" "+std::to_string(width+4)+
      " "+std::to_string(width+8)+" "+std::to_string(width+16)+" "+std::to_string(height)+
      " "+std::to_string(height+2)+" "+std::to_string(height+4)+" "+std::to_string(height+8)+" -HSync -VSync";
  c.setResolution(timings.c_str(),width,height,doubled);
  c.resumeBackgroundPrimitiveExecution();c.bindNativeAliases();c.drain();
  assert(c.isViewPortAllocated()&&c.getViewPortWidth()==width&&c.getViewPortHeight()==height);
  assert(c.isDoubleBuffered()==doubled);
  assert(c.linearStorage());
  constexpr std::size_t guard=64;
  const auto stride=std::size_t(width)+2*guard+16;
  std::vector<std::uint8_t> storage(stride*height,0xa7),expected(width*height);
  std::vector<std::uint8_t *> original(height),physical(height);
  for(int y=0;y<height;++y) {
    original[y]=c.row(y);
    // Deliberately fragmented/misaligned logical rows with canaries around
    // every span, so no flat-allocation or source-alignment assumption can pass.
    physical[y]=storage.data()+y*stride+guard+(y*7&15);
    for(int x=0;x<width;++x)physical[y][x]=(y*13+x*5)&63;
  }
  const auto pristine=storage;
  std::atomic<bool> stopping{};
  auto capture=[&](std::uint8_t *destination) {
    AGON_STOCK_NATIVE_GUARD;
    return c.copyLinearFrameUnderNativeGuard(destination,decorate,stopping);
  };
  for(int permutation=0;permutation<3;++permutation) {
    for(int y=0;y<height;++y) {
      const auto index=permutation==0?y:(permutation==1?(y+23)%height:height-1-y);
      c.row(y,physical[index]);
      std::memcpy(expected.data()+std::size_t(y)*width,physical[index],width);
    }
    for(unsigned alignment=0;alignment<16;++alignment) {
      std::vector<std::uint8_t> output(expected.size()+2*guard+16,0xd3);
      auto *destination=output.data()+guard+alignment;
      assert(capture(destination));
      assert(std::memcmp(destination,expected.data(),expected.size())==0);
      assert(storage==pristine);
      assert(std::all_of(output.begin(),output.begin()+guard+alignment,[](auto x){return x==0xd3;}));
      assert(std::all_of(output.begin()+guard+alignment+expected.size(),output.end(),[](auto x){return x==0xd3;}));
      stopping=true;std::fill(output.begin(),output.end(),0xd3);
      assert(!capture(destination));
      assert(std::all_of(output.begin(),output.end(),[](auto x){return x==0xd3;}));
      stopping=false;
    }
  }
  if(width==512&&height==384&&!doubled&&!decorate) {
    // Execute the real partial copy-scroll through fragmented/permuted rows.
    // 256 is Nurples's byte width; odd bounds and the95/96-byte cutoff exercise
    // kernel heads/tails. Every non-field pixel and allocation canary survives.
    fabgl::Canvas canvas(&c);canvas.setBrushColor(0,0,0);
    std::vector<std::uint8_t> output(expected.size());
    for(int permutation=0;permutation<3;++permutation)
      for(const auto &region : {fabgl::Rect(128,48,383,383),fabgl::Rect(129,49,383,382),
                                fabgl::Rect(5,48,99,383),fabgl::Rect(7,48,102,383),
                                fabgl::Rect(3,48,259,383),fabgl::Rect(1,48,511,383)}) {
        const auto fieldHeight=region.Y2-region.Y1+1;
        for(int amount : {1,-1,7,-7,fieldHeight-1,1-fieldHeight,fieldHeight,-fieldHeight}) {
          std::copy(pristine.begin(),pristine.end(),storage.begin());
          std::vector<std::uint8_t *> rows(height);
          for(int y=0;y<height;++y) {
            const auto index=permutation==0?y:(permutation==1?(y+23)%height:height-1-y);
            c.row(y,physical[index]);rows[y]=c.row(y);
            std::memcpy(expected.data()+std::size_t(y)*width,rows[y],width);
          }
          const auto before=expected;
          canvas.setScrollingRegion(region.X1,region.Y1,region.X2,region.Y2);c.drain();
          canvas.scroll(0,amount);c.drain();
          for(int y=region.Y1;y<=region.Y2;++y)
            for(int x=region.X1;x<=region.X2;++x) {
              const auto sourceY=y-amount;
              expected[std::size_t(y)*width+x]=sourceY>=region.Y1&&sourceY<=region.Y2
                  ? before[std::size_t(sourceY)*width+x] : c.createBlankRawPixel();
            }
          assert(capture(output.data()));assert(output==expected);
          for(int y=0;y<height;++y) {
            assert(c.row(y)==rows[y]); // partial scroll never rotates descriptors
            const auto start=storage.data()+std::size_t(y)*stride;
            const auto offset=std::size_t(physical[y]-storage.data());
            assert(std::equal(start,physical[y],pristine.data()+std::size_t(y)*stride));
            assert(std::equal(physical[y]+width,start+stride,pristine.data()+offset+width));
          }
        }
      }
    // A full-width scroll can rotate row pointers. Capture still follows the
    // descriptors rather than copying a guessed contiguous plane.
    const auto before=expected;
    const auto seventhRow=c.row(7);
    canvas.setScrollingRegion(0,0,width-1,height-1);c.drain();
    canvas.scroll(0,-7);c.drain();
    assert(c.row(0)==seventhRow);
    for(int y=0;y<height;++y)for(int x=0;x<width;++x)
      expected[std::size_t(y)*width+x]=y+7<height
          ? before[std::size_t(y+7)*width+x] : c.createBlankRawPixel();
    const auto source_before=storage;
    assert(capture(output.data()));assert(output==expected);assert(storage==source_before);
  }
  for(int y=0;y<height;++y)c.row(y,original[y]);
  c.bindNativeAliases();
}

int main()
{
  static_assert(indexedSnapshotPieGeometry(512,384,false,false));
  static_assert(!indexedSnapshotPieGeometry(320,240,false,false));
  static_assert(!indexedSnapshotPieGeometry(640,480,false,false));
  static_assert(!indexedSnapshotPieGeometry(512,384,true,false));
  static_assert(!indexedSnapshotPieGeometry(512,384,false,true));
  exercise(512,384,false,false);
  exercise(320,240,false,false);exercise(320,240,true,true);
  exercise(640,480,false,false);exercise(512,384,true,false);
  exercise(512,384,false,true);
  std::puts("PASS: actual controller snapshots and partial scrolls; fragmented/permuted rows, +/-amounts, odd widths, fixed borders/canaries, full-width pointer rotation, all16 snapshot alignments, cancellation and geometry/DB/decorated fallbacks");
}
