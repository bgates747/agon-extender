#include "extender/display/hdmi_geometry.hpp"
#include "extender/display/rgb888_pixel.hpp"
#include <array>
#include <cassert>
#include <cstdint>
#include <vector>
using namespace agon::extender::display;

// The oracle walks destination pixels, independently of the producer's
// logical-row loop. Exercise cropped half-row boundaries and decorated colors.
static void check(int w,int h,int ow,int oh) {
  const int repeat=hdmiVerticalRepeat(w,h),stride=ow*3;
  const auto geometry=centeredHdmiGeometry(w,h*repeat,ow,oh);
  std::vector<std::uint8_t> guarded(std::size_t(stride)*oh+2,0);
  guarded.front()=guarded.back()=0xa5;
  auto image=guarded.data()+1;
  std::vector<std::uint8_t> signal(w);
  for(int y=0;y<h;++y) {
    for(int x=0;x<w;++x)signal[x^2]=0xc0|((17*y+x)&63);
    expandRepeatedSignalRowToHdmi(signal.data(),image,stride,geometry,y,repeat);
  }
  for(int y=0;y<oh;++y)for(int x=0;x<ow;++x) {
    const bool visible=x>=geometry.destination_x && x<geometry.destination_x+geometry.width &&
        y>=geometry.destination_y && y<geometry.destination_y+geometry.height;
    unsigned value=0;
    if(visible) {
      const int sx=x-geometry.destination_x+geometry.source_x;
      const int sy=(y-geometry.destination_y+geometry.source_y)/repeat;
      value=(17*sy+sx)&63;
    }
    const auto p=image+y*stride+x*3;
    assert(p[0]==((value>>4)&3)*85);
    assert(p[1]==((value>>2)&3)*85);
    assert(p[2]==(value&3)*85);
  }
  assert(guarded.front()==0xa5 && guarded.back()==0xa5);
}
int main() {
  assert(hdmiVerticalRepeat(640,240)==2);
  for(auto mode:{std::array<int,2>{640,480},{512,384},{320,240},{640,256}})
    assert(hdmiVerticalRepeat(mode[0],mode[1])==1);
  const auto carrier=selectHdmiTiming(640,240);
  assert(carrier.width==848 && carrier.height==480);
  const auto placement=centeredHdmiGeometry(640,480,carrier.width,carrier.height);
  assert(placement.destination_x==104 && placement.destination_y==0);
  // Both comparison variants use native decorated rows for this mode family.
  assert(!rgb888ExperimentGeometry(64,640,240));
  check(640,240,848,480);
  check(640,240,683,383); // odd crop: a partially visible final repeated row
  check(640,240,619,385); // horizontal crop and unequal vertical edge rows
  check(512,384,684,384);
  check(320,240,848,480); // row reader remains unscaled before separate PPA
}
