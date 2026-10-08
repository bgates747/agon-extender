// SPRITE-001 experimental bridge: tasks own snapshots, ISR leases immutable
// bytes. Stock draw ordering/body retained; no live controller pointer stored.
#include "scene.hpp"
#include "bridge.h"
#include "extender/display/p4_rgb888_controller.hpp"
#include "freertos/FreeRTOS.h"
#include "esp_attr.h"
#include <new>

namespace agon_scanout {
// The same exact function as the standalone proof, with original GPL notice.
#include "../../../../dsi-strip-test/main/stock_sprite_body.inc"
}
namespace {
// Three snapshot arenas are read-only while leased. Metadata belongs in PSRAM
// too: static internal storage displaced ~35KiB of the contiguous SRAM needed
// by scanout and made the initial integrated firmware fail during allocation.
agon_scanout::Scene *scenes;
agon_scanout::SceneMailbox mailbox;
portMUX_TYPE mux=portMUX_INITIALIZER_UNLOCKED;
}
extern "C" void agon_scanout_reset() {
  // Driver callbacks and output task were joined before this task-only call.
  mailbox=agon_scanout::SceneMailbox{};
  if(scenes) for(unsigned i=0;i<3;++i) scenes[i].reset(0,0,0);
}
bool agon_scanout_stage(fabgl::P4Rgb888Controller *controller,unsigned index,int width,int height) {
  if(!scenes) {
    void *storage=heap_caps_malloc(3*sizeof(agon_scanout::Scene),MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);
    if(!storage)return false;
    scenes=static_cast<agon_scanout::Scene *>(storage);
    for(unsigned i=0;i<3;++i)new(scenes+i) agon_scanout::Scene;
  }
  const int outputWidth=agon_scanout_width(),outputHeight=agon_scanout_height();
  if(width<=0 || width>outputWidth || height<=0 || height>outputHeight || (width&3))return false;
  portENTER_CRITICAL(&mux);
  mailbox.cancel(); // a failed/cancelled previous submit owns no ISR lease
  int slot=mailbox.reserve();
  portEXIT_CRITICAL(&mux);
  if(slot<0)return false;
  auto &scene=scenes[slot];scene.reset(index,width,height,outputWidth,outputHeight);
  auto append=[&](fabgl::Sprite *s) {
    if(!s || !s->visible)return true;
    auto b=s->getFrame();if(!b)return true;
    if(b->format!=fabgl::PixelFormat::RGBA2222 && b->format!=fabgl::PixelFormat::RGBA8888)return true;
    return scene.append(s->x,s->y,b->width,b->height,
      b->format==fabgl::PixelFormat::RGBA2222?agon_scanout::PixelFormat::RGBA2222:agon_scanout::PixelFormat::RGBA8888,
      s->paintOptions.mode==fabgl::PaintMode::XOR,b->data);
  };
  bool ok=true;
  if(controller) {
    ok=append(controller->textCursor());
    for(int i=0;ok && i<controller->spritesCount();++i) {
      auto s=controller->getSprite(i);
      if(s->hardware && s->allowDraw)ok=append(s);
    }
    if(ok)ok=append(controller->mouseCursor());
  }
  if(!ok){portENTER_CRITICAL(&mux);mailbox.cancel();portEXIT_CRITICAL(&mux);}
  return ok;
}
void agon_scanout_commit() {portENTER_CRITICAL(&mux);mailbox.commit();portEXIT_CRITICAL(&mux);}
extern "C" agon_scanout_frame agon_scanout_latch() {
  portENTER_CRITICAL_ISR(&mux);int slot=mailbox.latch();portEXIT_CRITICAL_ISR(&mux);
  if(slot<0)return {0,0,0,0,0};
  auto &s=scenes[slot];return {s.background,s.left,s.top,s.width,s.height};
}
extern "C" void agon_scanout_compose(uint8_t *pixels,unsigned y,unsigned rows) {
  // Only the single outstanding copy completion calls this; the lease changes
  // at the first strip of the next prepared frame, after this job has finished.
  int slot=mailbox.leased;if(slot>=0)scenes[slot].compose(pixels,y,rows);
}
