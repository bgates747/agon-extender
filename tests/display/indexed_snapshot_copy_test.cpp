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
    // Execute the real partial vertical scroll with fixed bezel/top rows.
    // The snapshot must follow its current descriptors and preserve clipping.
    fabgl::Canvas canvas(&c);canvas.setBrushColor(0,0,0);
    canvas.setScrollingRegion(128,48,383,383);c.drain();
    const auto before=expected;
    canvas.scroll(0,-1);c.drain();
    for(int y=48;y<384;++y)for(int x=128;x<384;++x)
      expected[std::size_t(y)*width+x]=y<383?before[std::size_t(y+1)*width+x]:c.createBlankRawPixel();
    std::vector<std::uint8_t> output(expected.size());
    assert(capture(output.data()));assert(output==expected);
    // A full-width scroll can rotate row pointers. Capture still follows the
    // descriptors rather than copying a guessed contiguous plane.
    canvas.setScrollingRegion(0,0,width-1,height-1);c.drain();
    canvas.scroll(0,-7);c.drain();
    for(int y=0;y<height;++y)
      std::memcpy(expected.data()+std::size_t(y)*width,c.row(y),width);
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
  std::puts("PASS: actual controller frame snapshots; row permutation/rotation, partial-scroll clipping, all16 destination alignments, source/destination canaries, unchanged source, cancellation and geometry/DB/decorated fallbacks");
}
