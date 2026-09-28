#include "extender/display/lcd/pixels.hpp"
#include <vector>
#include <cassert>
int main() {
  std::vector<unsigned char> in(320*240),out(640*480*3);
  for(unsigned y=0;y<240;++y)for(unsigned x=0;x<320;++x)in[y*320+x]=(x+y)%64;
  assert(agon::extender::display::lcd::expand(in.data(),320,240,320,out.data()));
  for(unsigned y=0;y<480;++y)for(unsigned x=0;x<640;++x) {
    auto v=in[(y/2)*320+x/2];auto p=&out[(y*640+x)*3];
    assert(p[0]==((v>>4)&3)*85 && p[1]==((v>>2)&3)*85 && p[2]==(v&3)*85);
  }
  std::vector<unsigned char> wide(640*240,3);
  assert(agon::extender::display::lcd::expand(wide.data(),640,240,640,out.data()));
  assert(out[0]==0 && out[(120*640)*3+2]==255 && out[(360*640)*3+2]==0);
  const unsigned char primaries[]={3,12,48,15,51,60,63};
  const unsigned char packed[][3]={{0,0,255},{0,255,0},{255,0,0},
    {0,255,255},{255,0,255},{255,255,0},{255,255,255}};
  for(unsigned i=0;i<7;++i) {
    std::vector<unsigned char> pixel(1,primaries[i]), converted(640*480*3);
    assert(agon::extender::display::lcd::expand(pixel.data(),1,1,1,converted.data()));
    auto center=&converted[(240*640+320)*3];
    assert(center[0]==packed[i][0] && center[1]==packed[i][1] && center[2]==packed[i][2]);
  }
  assert(!agon::extender::display::lcd::expand(in.data(),0,240,320,out.data()));
}
