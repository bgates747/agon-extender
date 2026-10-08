// RGB-001 golden comparison against the retained VGA64 CPU rasterizers.
#include <array>
#include <cassert>
#include <cstring>
#include <cstdio>
#include <vector>
#include <mutex>
#include <condition_variable>
#include <thread>
#include "canvas.h"
#include "extender/display/stock_runtime_controller.hpp"
#include "extender/display/hdmi_geometry.hpp"
using namespace agon::extender::display;
using namespace fabgl;
constexpr int W=64,H=32;
template<class Depth> struct TestController : StockBoundController<Depth> {
  void swap() { this->swapBuffers(); }
  volatile uint8_t *visibleRow(int y) { return this->m_viewPortVisible[y]; }
};
using Native=TestController<VGA64Controller>;
using Direct=TestController<P4Rgb888Controller>;

struct Panel {
#ifdef AGON_EXTENDER_HDMI_848X480
  static constexpr int PW=848,PH=480,Stride=PW*3,Guard=64;
#elif defined(AGON_EXTENDER_HDMI_684X384)
  static constexpr int PW=684,PH=384,Stride=PW*3,Guard=64;
#else
  static constexpr int PW=96,PH=48,Stride=PW*3,Guard=64;
#endif
  std::vector<uint8_t> pixels[2] {std::vector<uint8_t>(Guard+Stride*PH+Guard,0x5a),std::vector<uint8_t>(Guard+Stride*PH+Guard,0x5a)};
  std::mutex mutex;std::condition_variable changed;
  bool hold{},requested{},released{};unsigned target{};
  uint8_t *buffer(unsigned i){return pixels[i].data()+Guard;}
  static bool swap(void *context,unsigned target) {
    auto &p=*static_cast<Panel*>(context);std::unique_lock lock(p.mutex);
    p.target=target;p.requested=true;p.changed.notify_all();
    p.changed.wait(lock,[&]{return !p.hold || p.released;});return true;
  }
  Rgb888PanelStorage binding(unsigned front){return {{buffer(0),buffer(1)},2,front,PW,PH,Stride,this,swap};}
  void guards() {
    for(auto &v:pixels)for(int i=0;i<Guard;++i)assert(v[i]==0x5a && v[v.size()-1-i]==0x5a);
  }
  void margins(unsigned front,bool doubled) {
    const int left=(PW-W)/2,top=(PH-H)/2;
    for(unsigned i=0;i<2;++i)for(int y=0;y<PH;++y)for(int x=0;x<PW;++x) {
      if(x>=left && x<left+W && y>=top && y<top+H)continue;
      for(int c=0;c<3;++c)assert(buffer(i)[y*Stride+x*3+c]==(doubled || i==front ? 0 : 0x5a));
    }
  }
};

std::vector<RGB888> read(StockRuntimeController &r);
void commands(Canvas &c,StockRuntimeController &r,std::vector<std::vector<RGB888>> &stages) {
  auto checkpoint=[&](){stages.push_back(read(r));};
  c.setBrushColor(0,0,0);c.clear();
  for(int colour=0;colour<64;++colour) {
    c.setBrushColor((colour&3)*85,((colour>>2)&3)*85,((colour>>4)&3)*85);
    c.fillRectangle(colour,0,colour,31);
  }
  checkpoint();
  for(auto mode : {PaintMode::Set,PaintMode::OR,PaintMode::AND,PaintMode::XOR,
                  PaintMode::ORNOT,PaintMode::ANDNOT,PaintMode::Invert}) {
    PaintOptions options;options.mode=mode;c.setPaintOptions(options);
    c.setPenColor(87,139,230);c.drawLine(-5,3,62,29);
    c.setBrushColor(170,85,255);c.fillRectangle(3,6,20,12);
  }
  checkpoint();
  c.resetPaintOptions();
  c.setClippingRect(Rect(2,2,60,30));
  const std::uint8_t pixels[]={0xc1,0x02,0xc3,0xc4,0x85,0x46,0x07,0xc8};
  Bitmap bitmap(4,2,pixels,PixelFormat::RGBA2222);
  c.drawBitmap(0,8,&bitmap);c.drawBitmap(58,29,&bitmap);
  const std::uint32_t rgba[]={0xff203040,0x00203040,0x012080ff,0x404080c0};
  Bitmap bitmap8888(2,2,rgba,PixelFormat::RGBA8888);
  c.drawBitmap(16,20,&bitmap8888);
  checkpoint();
  c.copyRect(3,3,7,5,24,16);c.copyRect(7,5,2,1,24,16);
  checkpoint();
  c.setClippingRect(Rect(0,0,W-1,H-1));
  c.setScrollingRegion(0,0,W-1,H-1);c.scroll(5,-3);c.scroll(-7,2);
  checkpoint();
  c.setScrollingRegion(5,4,48,28);c.scroll(3,2);c.scroll(-2,-4);checkpoint();

  // SCAN-001 copy-scroll remedy: compare the actual stock rasterizer with
  // fixed RGB888 rows. Unequal rows expose wrong overlap direction; odd X
  // bounds expose byte-offset/length errors. Oversized stock scrolls are out
  // of scope (the upstream helper itself does not clamp them).
  for(const auto &region : {Rect(5,4,48,28),Rect(0,0,W-1,H-1),
                            Rect(7,5,7,25),Rect(2,6,60,6)}) {
    for(int y=0;y<H;++y)for(int x=0;x<W;++x) {
      const int v=(x+7*y)&63;
      c.setPenColor((v&3)*85,((v>>2)&3)*85,((v>>4)&3)*85);c.setPixel(x,y);
    }
    c.setBrushColor(85,170,255);
    c.setScrollingRegion(region.X1,region.Y1,region.X2,region.Y2);
    for(int amount : {1,-1,region.Y2-region.Y1+1,-(region.Y2-region.Y1+1)}) {
      c.scroll(0,amount);checkpoint();
    }
  }
}

std::vector<RGB888> read(StockRuntimeController &r) {
  std::vector<RGB888> image(W*H);r.display().readScreen(Rect(0,0,W-1,H-1),image.data());return image;
}
void same(const std::vector<RGB888>&a,const std::vector<RGB888>&b) {
  assert(a.size()==b.size());
  for(unsigned i=0;i<a.size();++i) {
    if(a[i].R!=b[i].R || a[i].G!=b[i].G || a[i].B!=b[i].B) {
      fprintf(stderr,"pixel (%u,%u) native=%u,%u,%u direct=%u,%u,%u\n",i%W,i/W,a[i].R,a[i].G,a[i].B,b[i].R,b[i].G,b[i].B);
      assert(false);
    }
  }
}

int main() {
  // Exercise physical BGR order, all64 colours, proxy-to-proxy assignment and
  // fill bounds independently of the golden controller.
  for(unsigned colour=0;colour<64;++colour) {
    std::array<std::uint8_t,27> bytes;bytes.fill(0x5a);
    fillRgb888(bytes.data()+3,7,colour);
    for(int i=1;i<8;++i)assert((std::uint8_t(Rgb888PixelRef(bytes.data()+3*i))&63)==colour);
    assert(bytes[0]==0x5a && bytes[26]==0x5a);
    Rgb888PixelRef(bytes.data())=Rgb888PixelRef(bytes.data()+3);
    assert((std::uint8_t(Rgb888PixelRef(bytes.data()))&63)==colour);
  }
  for(unsigned binding=0;binding<3;++binding) for(bool doubled : {false,true}) {
    Native native;Direct direct;
    Panel panel;if(binding)direct.bindPanelStorage(panel.binding(binding-1));
    std::vector<std::vector<RGB888>> stages[2];int variant=0;
    for(auto *r : {static_cast<StockRuntimeController*>(&native),static_cast<StockRuntimeController*>(&direct)}) {
      r->paletted().begin();
      r->paletted().setResolution("\"64x32\" 1 64 68 72 80 32 34 36 40 -HSync -VSync",W,H,doubled);
      assert(r->display().isViewPortAllocated());
      r->display().enableBackgroundPrimitiveExecution(false);
      r->bindNativeAliases();Canvas c(&r->paletted());
      // Stock initializes only the drawing plane. Clear/swap first so this test
      // compares defined backgrounds, rather than uninitialized native front RAM.
      if(doubled) {c.setBrushColor(0,0,0);c.clear();if(!variant)native.swap();else direct.swap();}
      commands(c,*r,stages[variant++]);
    }
    for(unsigned stage=0;stage<stages[0].size();++stage){same(stages[0][stage],stages[1][stage]);}
    same(read(native),read(direct));
    if(doubled) {native.bindNativeAliases();native.swap();direct.bindNativeAliases();direct.swap();}
    std::uint8_t spritePixels[]={0xc3,0x00,0xc0,0xff};
    Bitmap bitmap(2,2,spritePixels,PixelFormat::RGBA2222);
    Sprite overlay;overlay.addBitmap(&bitmap);overlay.hardware=1;overlay.visible=1;overlay.allowDraw=1;overlay.x=4;overlay.y=8;
    Sprite mouse;mouse.visible=0;
    native.setTextCursor(&overlay);direct.setTextCursor(&overlay);
    if(binding && doubled) {native.bindNativeAliases();native.swap();direct.bindNativeAliases();direct.swap();}
    int marker=-1;if(binding) {direct.bindNativeAliases();direct.preparePanelFrame(marker);}
    alignas(8)std::uint8_t a[W],b[W];std::uint8_t nativeRgb[W*3],directRgb[W*3];
    for(int y=0;y<H;++y) {
      native.bindNativeAliases();native.prepareRow(y,a);expandSignalRowToHdmi(a,nativeRgb,0,W);
      if(binding)assert(!memcmp(nativeRgb,(const void*)direct.visibleRow(y),sizeof(nativeRgb)));
      direct.bindNativeAliases();direct.prepareRgb888Row(y,directRgb,b);
      assert(!memcmp(nativeRgb,directRgb,sizeof(nativeRgb)));
    }
    // Overlay composition must leave persistent background/readback unchanged.
    same(read(native),read(direct));
    native.setTextCursor(nullptr);direct.setTextCursor(nullptr);
    std::vector<std::vector<RGB888>> spriteStages[2];variant=0;
    for(auto *r : {static_cast<StockRuntimeController*>(&native),static_cast<StockRuntimeController*>(&direct)}) {
      r->bindNativeAliases();
      Sprite sprite;sprite.addBitmap(&bitmap);sprite.hardware=0;sprite.visible=1;sprite.allowDraw=1;
      r->display().setSprites(&sprite,1);
      for(int step=0;step<5;++step) {
        sprite.moveTo(3+step*2,9+step);r->display().refreshSprites();
        spriteStages[variant].push_back(read(*r));
      }
      // Nurples-style partial scroll followed by one clipped incoming row.
      // Keep the software sprite live, crossing the edge of that region, so
      // hide/restore must not bake its old pixels into the background.
      Canvas c(&r->paletted());
      const std::uint8_t tilePixels[]={0xc1,0xc2,0xc3,0xc4,0xc5,0xc6,0xc7,0xc8,
                                      0xc9,0xca,0xcb,0xcc,0xcd,0xce,0xcf,0xd0};
      Bitmap tile(4,4,tilePixels,PixelFormat::RGBA2222);
      for(int step=0;step<20;++step) {
        c.setScrollingRegion(5,4,48,28);c.setBrushColor(85,0,170);
        c.scroll(0,step<10?1:-1);
        const int row=step<10?4:28;
        c.setClippingRect(Rect(5,row,48,row));
        for(int x=3;x<49;x+=4)c.drawBitmap(x,row-(step%4),&tile);
        c.setClippingRect(Rect(0,0,W-1,H-1));
        sprite.moveTo(4+step%5,4+step%4);r->display().refreshSprites();
        spriteStages[variant].push_back(read(*r));
      }
      r->display().removeSprites();++variant;
      spriteStages[variant-1].push_back(read(*r));
    }
    for(unsigned i=0;i<spriteStages[0].size();++i)same(spriteStages[0][i],spriteStages[1][i]);
    if(doubled) {
      const auto generation=stockVisibleGeneration();
      direct.bindNativeAliases();
      if(binding) {
        auto *drawing=direct.display().getScanline(0);auto *visible=direct.visibleRow(0);
        {std::lock_guard lock(panel.mutex);panel.hold=true;panel.requested=panel.released=false;}
        std::atomic<bool> finished{};std::thread swapper([&]{direct.swap();finished.store(true);});
        {std::unique_lock lock(panel.mutex);panel.changed.wait(lock,[&]{return panel.requested;});
          // The old scanned front must remain unavailable while DMA still
          // owns it. Merely requesting/selecting a swap is not a release.
          assert(!finished.load());assert(direct.display().getScanline(0)==drawing);
          assert(direct.visibleRow(0)==visible);panel.released=true;panel.changed.notify_all();}
        swapper.join();assert(finished.load());
        assert(direct.display().getScanline(0)==visible && direct.visibleRow(0)==drawing);
      } else direct.swap();
      assert(stockVisibleGeneration()==generation+1);
    }
    if(binding) {
      const auto drawing=direct.display().getScanline(0);
      assert(direct.display().getScanline(1)-drawing==Panel::Stride);
      Canvas c(&direct.paletted());c.setPenColor(255,0,0);c.setPixel(0,0);
      assert(drawing[0]==0 && drawing[1]==0 && drawing[2]==255);
      // The panel owner retains both allocations through renderer teardown.
      panel.guards();
      panel.margins(binding-1,doubled);
    }
    native.end();direct.end();
    if(binding)panel.guards();
  }
#ifdef AGON_EXTENDER_HDMI_848X480
  // HDMI02-F: full-width allocation, edge drawing, partial scrolling and
  // overlay scratch beyond the old512 boundary; compare real stock pixels.
  {
    Native native;Direct direct;Panel panel;direct.bindPanelStorage(panel.binding(0));
    std::vector<RGB888> images[2];unsigned variant=0;
    for(auto *r : {static_cast<StockRuntimeController*>(&native),static_cast<StockRuntimeController*>(&direct)}) {
      r->paletted().begin();
      r->paletted().setResolution("\"848x480\" 34.285714 848 880 992 1104 480 486 494 517 +HSync +VSync",848,480,false);
      assert(r->display().isViewPortAllocated());r->display().enableBackgroundPrimitiveExecution(false);
      r->bindNativeAliases();Canvas c(&r->paletted());c.setBrushColor(0,0,0);c.clear();
      c.setBrushColor(85,170,255);c.fillRectangle(512,450,847,479);
      c.setPenColor(255,0,0);c.drawLine(0,0,847,479);c.setPixel(847,0);
      // Keep a four-pixel right sidebar: retained VGA64 swapRows repeats its
      // tail when the sidebar is only1..3 pixels. That upstream-style edge
      // discrepancy is recorded under HDMI02-F, not fixed by this experiment.
      c.setScrollingRegion(701,459,843,478);c.scroll(0,1);c.scroll(0,-2);
      images[variant].resize(848*480);r->display().readScreen(Rect(0,0,847,479),images[variant++].data());
    }
    same(images[0],images[1]);
    std::uint8_t pixels[]={0xc3,0xc2,0xc1,0xff};Bitmap bitmap(2,2,pixels,PixelFormat::RGBA2222);
    Sprite overlay;overlay.addBitmap(&bitmap);overlay.visible=overlay.allowDraw=overlay.hardware=1;overlay.x=846;overlay.y=478;
    native.setTextCursor(&overlay);direct.setTextCursor(&overlay);direct.bindNativeAliases();int marker;direct.preparePanelFrame(marker);
    alignas(8)std::uint8_t signal[848];std::uint8_t rgb[848*3];
    for(int y=478;y<480;++y) {
      native.bindNativeAliases();native.prepareRow(y,signal);expandSignalRowToHdmi(signal,rgb,0,848);
      assert(!memcmp(rgb,(const void*)direct.visibleRow(y),sizeof(rgb)));
    }
    native.setTextCursor(nullptr);direct.setTextCursor(nullptr);native.end();direct.end();panel.guards();
  }
#endif

}
