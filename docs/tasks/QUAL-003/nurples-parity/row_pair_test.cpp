#include <array>
#include <cassert>
#include <cstring>
#include "extender/display/stock_p4_service.hpp"
#include "extender/display/rgb222_row.hpp"
using namespace agon::extender::display;
struct Controller : StockBoundController<fabgl::VGA64Controller> {
 void fill() {for(int y=0;y<16;++y)for(int x=0;x<64;++x)m_viewPortVisible[y][x]=1;}
};
int main() {
 Controller c;c.begin();c.setResolution("\"64x16\" 1 64 68 72 80 16 18 20 24 -HSync -VSync",64,16,false);c.enableBackgroundPrimitiveTimeout(false);c.fill();
 std::uint8_t pixels[16];std::memset(pixels,0xc3,16);
 fabgl::Bitmap bitmap(4,4,pixels,fabgl::PixelFormat::RGBA2222);fabgl::Sprite sprite;
 sprite.addBitmap(&bitmap);sprite.hardware=true;sprite.visible=true;sprite.moveTo(1,1);c.setSprites(&sprite,1);c.drain();
 for(unsigned count: {1u,2u})for(int y=0;y<=16-int(count);++y) {
  alignas(8) std::array<std::uint8_t,160> single,pair;single.fill(0xa5);pair.fill(0xa5);
  for(unsigned i=0;i<count;++i)c.prepareRow(y+i,single.data()+80*i);
  c.prepareRows(y,count,pair.data(),80);assert(single==pair);
  for(unsigned i=0;i<count;++i)for(unsigned x=64;x<80;++x)assert(pair[i*80+x]==0xa5);
  if(count==1)for(unsigned x=80;x<160;++x)assert(pair[x]==0xa5);
 }
 alignas(8) std::uint8_t row[64],normal[64];c.prepareRow(2,row);normalizeRgb222Row(row,normal,64);assert(normal[1]==3 && normal[10]==1);
 c.removeSprites();sprite.clearBitmaps();
}
