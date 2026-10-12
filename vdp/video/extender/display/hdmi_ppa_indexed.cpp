// RESEARCH-007: public, upstream-derived PPA CLUT calls benchmarked separately.
// The output task owns this client/CLUT and waits for completion before reuse.
// No mutable logical framebuffer pointers or native mutex cross the DMA wait.
#include "extender/display/hdmi_ppa_indexed.hpp"
#include "driver/ppa.h"
#include "esp_cache.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include <cstring>

namespace agon::extender::display {
namespace { constexpr std::size_t maximumPixels=848*480, alignment=64; }
bool HdmiPpaIndexed::initialize() {
  if(client_)return true;
  source_=static_cast<std::uint8_t *>(heap_caps_aligned_alloc(alignment,maximumPixels,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
  transparent_=static_cast<std::uint8_t *>(heap_caps_aligned_calloc(alignment,1,maximumPixels,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
  if(!source_ || !transparent_){reset();return false;}
  if(esp_cache_msync(transparent_,maximumPixels,ESP_CACHE_MSYNC_FLAG_DIR_C2M)!=ESP_OK){reset();return false;}
  ppa_client_config_t config{};config.oper_type=PPA_OPERATION_BLEND;config.max_pending_trans_num=1;
  ppa_client_handle_t client{};
  if(ppa_register_client(&config,&client)!=ESP_OK){reset();return false;}
  client_=client;
  // These are physical RGB222 colours, not logical palette slots. Stock64
  // logical remapping changes subsequent drawing, never existing pixels.
  // Sync bits are ignored: all four aliases map to the same physical colour.
  color_pixel_argb8888_data_t palette[256]{};
  for(unsigned i=0;i<256;++i) {
    palette[i].r=(i&3)*85;palette[i].g=((i>>2)&3)*85;
    palette[i].b=((i>>4)&3)*85;palette[i].a=255;
  }
  if(ppa_set_color_lookup_table(PPA_CLUT_BLEND_BG,palette,256)!=ESP_OK){reset();return false;}
  return true;
}
void HdmiPpaIndexed::reset() {
  if(client_)ppa_unregister_client(static_cast<ppa_client_handle_t>(client_));
  client_=nullptr;heap_caps_free(source_);heap_caps_free(transparent_);
  source_=transparent_=nullptr;
}
bool HdmiPpaIndexed::expand(std::uint8_t *output,std::size_t bytes,int ow,int oh,int w,int h,int left,int top) {
  if(!client_ || w<=0 || h<=0 || std::size_t(w)*h>maximumPixels || left<0 || top<0 ||
     left+w>ow || top+h>oh || bytes!=std::size_t(ow)*oh*3 || bytes%alignment)return false;
  // Preserve CPU-cleared borders before driver invalidation; publish private
  // snapshot input. BLEND requires a second input: an all-transparent A8 mask.
  if(esp_cache_msync(output,bytes,ESP_CACHE_MSYNC_FLAG_DIR_C2M)!=ESP_OK)return false;
  ppa_blend_oper_config_t op{};
  op.in_bg.buffer=source_;op.in_bg.pic_w=op.in_bg.block_w=w;
  op.in_bg.pic_h=op.in_bg.block_h=h;op.in_bg.blend_cm=PPA_BLEND_COLOR_MODE_L8;
  op.in_fg.buffer=transparent_;op.in_fg.pic_w=op.in_fg.block_w=w;
  op.in_fg.pic_h=op.in_fg.block_h=h;op.in_fg.blend_cm=PPA_BLEND_COLOR_MODE_A8;
  op.out.buffer=output;op.out.buffer_size=bytes;op.out.pic_w=ow;op.out.pic_h=oh;
  op.out.block_offset_x=left;op.out.block_offset_y=top;op.out.blend_cm=PPA_BLEND_COLOR_MODE_RGB888;
  op.bg_alpha_update_mode=op.fg_alpha_update_mode=PPA_ALPHA_NO_CHANGE;
  op.mode=PPA_TRANS_MODE_BLOCKING;
  const auto error=ppa_do_blend(static_cast<ppa_client_handle_t>(client_),&op);
  if(error!=ESP_OK){ESP_LOGE("ext-ppa-indexed","BLEND %dx%d into %dx%d+%d+%d: %s",w,h,ow,oh,left,top,esp_err_to_name(error));return false;}
  return esp_cache_msync(output,bytes,ESP_CACHE_MSYNC_FLAG_DIR_M2C)==ESP_OK;
}
}
