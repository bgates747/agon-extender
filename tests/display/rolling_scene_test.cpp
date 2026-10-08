// Snapshot lifetime and stock-pixel comparison; no hardware timing claim.
#include "extender/display/rolling/scene.hpp"
#include <cassert>
#include <array>
#include <vector>
#include <iostream>
#define IRAM_ATTR
namespace agon_scanout {
#include "../../vdp/dsi-strip-test/main/stock_sprite_body.inc"
}
using namespace agon_scanout;
int main() {
  SceneMailbox box;
  assert(box.reserve()==0);box.commit();assert(box.latch()==0);
  assert(box.reserve()==1);box.commit();assert(box.reserve()==2);
  assert(box.published==1 && box.leased==0);box.cancel();
  assert(box.latch()==1);assert(box.reserve()==0);box.commit();
  assert(box.leased==1 && box.published==0);
  for(const auto geometry : {std::array<unsigned,4>{STRIP_WIDTH,STRIP_HEIGHT,512,384},
      std::array<unsigned,4>{STRIP_WIDTH,STRIP_HEIGHT,STRIP_WIDTH,STRIP_HEIGHT},
      std::array<unsigned,4>{684,384,512,384}}) {
    const unsigned W=geometry[0],H=geometry[1],LW=geometry[2],LH=geometry[3];
    if(W>STRIP_WIDTH || H>STRIP_HEIGHT)continue;
  Scene scene;scene.reset(1,LW,LH,W,H);
  std::vector<uint8_t> image(W*H*3),expected;
  for(unsigned i=0;i<image.size();++i)image[i]=((i*19)%4)*85;
  expected=image;
  auto add=[&](int sx,int sy,int w,int h,bool rgba,bool xorMode) {
    std::vector<uint8_t> data(w*h*(rgba?4:1));
    for(unsigned i=0;i<data.size();++i)data[i]=(i*73+219)&255;
    assert(scene.append(sx,sy,w,h,rgba?PixelFormat::RGBA8888:PixelFormat::RGBA2222,xorMode,data.data()));
    for(int y=std::max(0,sy);y<std::min(int(LH),sy+h);++y)
      for(int x=std::max(0,sx);x<std::min(int(LW),sx+w);++x) {
        auto offset=((y-sy)*w+x-sx)*(rgba?4:1);
        unsigned color=rgba?((data[offset]>>6)|((data[offset+1]>>6)<<2)|((data[offset+2]>>6)<<4)):data[offset]&63;
        bool opaque=rgba?data[offset+3]!=0:(data[offset]&192)!=0;
        if(!opaque)continue;
        unsigned p=((y+(H-LH)/2)*W+x+(W-LW)/2)*3;
        if(xorMode && !rgba)color^=(expected[p]>>6)<<4|(expected[p+1]>>6)<<2|(expected[p+2]>>6);
        expected[p]=((color>>4)&3)*85;expected[p+1]=((color>>2)&3)*85;expected[p+2]=(color&3)*85;
      }
    // Destroy/mutate the source before composition: the scene must own its bytes.
    std::fill(data.begin(),data.end(),0);
  };
  add(0,0,1,1,false,false); // unaligned next pixel arena position
  add(-3,-2,16,16,true,false);
  add(LW-13,LH-14,25,24,false,false);
  add(12,28,30,60,false,false); // crosses strip boundary
  add(19,35,25,62,false,true); // overlapping cursor-style XOR
  add(20,40,18,50,true,true); // stock ignores XOR for RGBA8888
  add(160,119,127,128,false,false); // forces several arena reallocations
  auto original=image;
  for(unsigned rows:{32u,40u}) {
    image=original;
    for(unsigned y=0;y<H;y+=rows)scene.compose(image.data()+y*W*3,y,std::min(rows,H-y));
    assert(image==expected);
  }
  // A later empty frame removes overlays; no stale entries survive reuse.
  scene.reset(0,320,240,W,H);auto copy=image;scene.compose(image.data(),0,H);assert(image==copy);
  }
  std::cout<<"mailbox ownership, deep-copy lifetime, arena relocation, clipping, overlap, RGBA8888, XOR, strip boundaries and empty scene pass\n";
}
