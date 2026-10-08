// SPRITE-001: immutable scanout scene. No live FabGL pointers reach an ISR.
#pragma once
#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include "strip_config.h"
#ifdef ESP_PLATFORM
#include "esp_heap_caps.h"
#endif

namespace agon_scanout {
enum class PixelFormat { RGBA8888, RGBA2222 };
enum class PaintMode { SET, XOR };
struct Bitmap { int width{}, height{}; PixelFormat format{}; const uint8_t *data{}; };
struct Sprite {
  int x{}, y{}; Bitmap image;
  struct { PaintMode mode = PaintMode::SET; } paintOptions;
  Bitmap *getFrame() { return &image; }
};
class VGAPalettedController {
  uint8_t m_HVSync = 0;
 public:
  void rawDrawSpriteScanline(uint8_t *, Sprite *, int, int, int);
};

// A writer cannot reserve the currently published or ISR-leased slot. Callers
// serialize only these tiny transitions; copying/composition stays outside.
struct SceneMailbox {
  int published{-1}, leased{-1}, writing{-1};
  int reserve() {
    if (writing >= 0) return -1;
    for (int n=0;n<3;++n) if(n!=published && n!=leased) return writing=n;
    return -1;
  }
  void commit() { if(writing>=0) {published=writing;writing=-1;} }
  void cancel() {writing=-1;}
  int latch() {return leased=published;}
};

struct Scene {
  static constexpr unsigned maximumSprites=258;
  Sprite sprites[maximumSprites];
  unsigned count{}, background{};
  size_t offsets[maximumSprites]{};
  int left{}, top{}, width{}, height{}, outputWidth{STRIP_WIDTH}, outputHeight{STRIP_HEIGHT};
  uint8_t *pixels{};
  size_t capacity{}, used{};
  ~Scene() {std::free(pixels);}
  void reset(unsigned index,int w,int h,int ow=STRIP_WIDTH,int oh=STRIP_HEIGHT) {
    count=0;used=0;background=index;width=w;height=h;
    outputWidth=ow;outputHeight=oh;
    left=(ow-w)/2;top=(oh-h)/2;
  }
  bool append(int x,int y,int w,int h,PixelFormat format,bool xorMode,const void *data) {
    if(w<=0 || h<=0 || !data || x>=width || y>=height || x+w<=0 || y+h<=0) return true;
    if(count==maximumSprites) return false;
    const size_t bytes=size_t(w)*h*(format==PixelFormat::RGBA8888?4:1);
    const size_t offset=(used+3)&~size_t(3); // RGBA8888 is read as uint32_t upstream
    if(bytes>SIZE_MAX-offset) return false;
    if(offset+bytes>capacity) {
      const size_t next=std::max(offset+bytes,capacity*2);
#ifdef ESP_PLATFORM
      auto p=static_cast<uint8_t *>(heap_caps_realloc(pixels,next,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
#else
      auto p=static_cast<uint8_t *>(std::realloc(pixels,next));
#endif
      if(!p)return false;
      // Existing entries retain offsets if realloc moves the arena.
      for(unsigned i=0;i<count;++i)
        sprites[i].image.data=p+offsets[i];
      pixels=p;capacity=next;
    }
    std::memcpy(pixels+offset,data,bytes);
    offsets[count]=offset;auto &s=sprites[count++];s.x=x;s.y=y;s.image={w,h,format,pixels+offset};
    s.paintOptions.mode=xorMode?PaintMode::XOR:PaintMode::SET;
    used=offset+bytes;return true;
  }
  void compose(uint8_t *strip,unsigned firstY,unsigned rows) {
    if(!count)return;
    alignas(8)uint8_t signal[STRIP_WIDTH];
    VGAPalettedController painter;
    for(unsigned row=0;row<rows;++row) {
      int y=int(firstY+row)-top;if(y<0 || y>=height)continue;
      auto pixelsRow=strip+row*outputWidth*3+left*3;
      auto span=[&](Sprite &s,auto fn) {
        if(y<s.y || y>=s.y+s.image.height)return;
        for(int x=std::max(0,s.x);x<std::min(width,s.x+s.image.width);++x) fn(x);
      };
      // Populate all background spans before painting, preserving overlap/XOR.
      for(unsigned i=0;i<count;++i)span(sprites[i],[&](int x){
        signal[x^2]=(pixelsRow[x*3]>>6<<4)|(pixelsRow[x*3+1]>>6<<2)|(pixelsRow[x*3+2]>>6);
      });
      for(unsigned i=0;i<count;++i)painter.rawDrawSpriteScanline(signal,&sprites[i],y,width,height);
      for(unsigned i=0;i<count;++i)span(sprites[i],[&](int x){
        auto p=signal[x^2];pixelsRow[x*3]=((p>>4)&3)*85;
        pixelsRow[x*3+1]=((p>>2)&3)*85;pixelsRow[x*3+2]=(p&3)*85;
      });
    }
  }
};
} // namespace agon_scanout
