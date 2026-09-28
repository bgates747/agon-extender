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
  assert(!agon::extender::display::lcd::expand(in.data(),0,240,320,out.data()));
}
