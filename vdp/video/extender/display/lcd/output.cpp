// LCD-001 output adapter. Renderer snapshots remain immutable and renderer locks
// are never held during PPA or panel waits. Vendor timing is unchanged.
#include "output.hpp"
#if AGON_EXTENDER_LCD
#include "pixels.hpp"
#include <atomic>
#include "driver/ppa.h"
#include "esp_lcd_mipi_dsi.h"
#include "esp_lcd_panel_ops.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
extern "C" esp_lcd_panel_handle_t extender_lcd_panel_create(void);
namespace agon::extender::display {
namespace {
constexpr size_t bytes=640*480*3;
std::atomic<unsigned> boundaries{0};
bool frameDone(esp_lcd_panel_handle_t, esp_lcd_dpi_panel_event_data_t*, void*) {
  boundaries.fetch_add(1,std::memory_order_relaxed); return false;
}
void worker(void *arg) {
  auto &pool=*static_cast<PresentationSnapshotPool*>(arg);
  auto source=static_cast<uint8_t*>(heap_caps_aligned_alloc(64,bytes,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
  if (!source) { ESP_LOGE("lcd","RGB output allocation failed"); vTaskDelete(nullptr); return; }
  auto panel=extender_lcd_panel_create();
#if AGON_EXTENDER_LCD_PATTERN
  // TRM 42.4.2.3.1: native top-to-bottom W,Y,C,G,M,R,B,K.
  // With ribbon at left these are landscape left-to-right vertical bars.
  ESP_ERROR_CHECK(esp_lcd_dpi_panel_set_pattern(panel,MIPI_DSI_PATTERN_BAR_HORIZONTAL));
  ESP_LOGI("lcd","DSI hardware pattern: ribbon-left order white yellow cyan green magenta red blue black");
  heap_caps_free(source);
  vTaskDelete(nullptr); return;
#endif
  void *fb[2];
  ESP_ERROR_CHECK(esp_lcd_dpi_panel_get_frame_buffer(panel,2,&fb[0],&fb[1]));
  esp_lcd_dpi_panel_event_callbacks_t callbacks{};
  callbacks.on_frame_buf_complete=frameDone;
  ESP_ERROR_CHECK(esp_lcd_dpi_panel_register_event_callbacks(panel,&callbacks,nullptr));
  ppa_client_config_t client{}; client.oper_type=PPA_OPERATION_SRM;
  ppa_client_handle_t ppa;
  ESP_ERROR_CHECK(ppa_register_client(&client,&ppa));
  ppa_srm_oper_config_t op{};
  op.in.buffer=source; op.in.pic_w=640;op.in.pic_h=480;
  op.in.block_w=640;op.in.block_h=480;op.in.srm_cm=PPA_SRM_COLOR_MODE_RGB888;
  op.out.buffer_size=bytes;op.out.pic_w=480;op.out.pic_h=640;
  op.out.srm_cm=PPA_SRM_COLOR_MODE_RGB888;
  // Native top is the ribbon edge. Source LEFT maps to native TOP:
  // native(x,y)=(479-source_y,source_x), i.e. 270deg CCW into native RAM.
  op.rotation_angle=PPA_SRM_ROTATION_ANGLE_270;
  op.scale_x=1;op.scale_y=1;op.mode=PPA_TRANS_MODE_BLOCKING;
  // Diagnostic: exercise every byte with an asymmetric pattern before using
  // renderer data. Uniform boot-screen corners cannot detect channel/row shifts.
  for (unsigned y=0;y<480;++y) for(unsigned x=0;x<640;++x) {
    auto a=source+(y*640+x)*3;
    a[0]=uint8_t(x+3*y); a[1]=uint8_t(5*x+y+71); a[2]=uint8_t(x+7*y+139);
  }
  op.out.buffer=fb[1];
  ESP_ERROR_CHECK(ppa_do_scale_rotate_mirror(ppa,&op));
  unsigned mismatches=0;
  auto diagnostic=static_cast<uint8_t*>(fb[1]);
  for (unsigned y=0;y<480;++y) for(unsigned x=0;x<640;++x) {
    auto a=source+(y*640+x)*3;
    auto b=diagnostic+(x*480+479-y)*3;
    if(std::memcmp(a,b,3)) {
      if(!mismatches) ESP_LOGE("lcd","PPA first mismatch source(%u,%u): expected %02x %02x %02x got %02x %02x %02x",x,y,a[0],a[1],a[2],b[0],b[1],b[2]);
      ++mismatches;
    }
  }
  ESP_LOGI("lcd","PPA full asymmetric check: %u / 307200 pixels mismatched",mismatches);
  if(mismatches) { vTaskDelete(nullptr); return; }
  unsigned next=1, count=0; uint64_t generation=0;
  int64_t last=esp_timer_get_time();
  ESP_LOGI("lcd","Landscape output ready: ribbon-left, 640x480, PPA rotation; browser optional");
  for (;;) {
    PresentationSnapshotLease lease;
    if (!pool.tryAcquireLatest(generation,lease)) { vTaskDelay(pdMS_TO_TICKS(2)); continue; }
    auto view=lease.view(); generation=view.generation;
    bool valid=view.pixel_format==SnapshotPixelFormat::RGB222 &&
      view.payload_bytes>=view.stride_bytes*view.height &&
      lcd::expand(view.data,view.width,view.height,view.stride_bytes,source);
    lease.release(); // Never retain producer storage while awaiting hardware.
    if (!valid) { vTaskDelay(pdMS_TO_TICKS(10)); continue; }
    op.out.buffer=fb[next];
    esp_err_t err=ppa_do_scale_rotate_mirror(ppa,&op);
    if(err!=ESP_OK) { ESP_LOGE("lcd","PPA error %s",esp_err_to_name(err)); break; }
    // Verify four transformed corner pixels before publishing the first image.
    static bool checked=false;
    if (!checked) {
      auto out=static_cast<uint8_t*>(fb[next]);
      const unsigned sx[4]={0,639,0,639}, sy[4]={0,0,479,479};
      for(unsigned i=0;i<4;++i) {
        auto a=source+(sy[i]*640+sx[i])*3;
        auto b=out+(sx[i]*480+479-sy[i])*3;
        if(std::memcmp(a,b,3)) {
          ESP_LOGE("lcd","PPA corner mapping mismatch; not publishing");
          vTaskDelete(nullptr); return;
        }
      }
      checked=true; ESP_LOGI("lcd","PPA corner mapping verified");
    }
    ESP_ERROR_CHECK(esp_lcd_panel_draw_bitmap(panel,0,0,480,640,fb[next]));
    // IDF5.5.5 selects cur_fb_index at DMA completion, before its callback.
    // Wait TWO subsequent completions so even a callback racing the request
    // cannot license reuse of the still-scanned old buffer. No render lock held.
    unsigned start=boundaries.load(std::memory_order_relaxed);
    int64_t deadline=esp_timer_get_time()+500000;
    while(unsigned(boundaries.load(std::memory_order_relaxed)-start)<2 && esp_timer_get_time()<deadline)
      vTaskDelay(pdMS_TO_TICKS(1));
    if(unsigned(boundaries.load(std::memory_order_relaxed)-start)<2) {
      ESP_LOGE("lcd","DSI completion timeout; output stopped without reusing scanout buffer"); break;
    }
    next^=1; ++count;
    if(esp_timer_get_time()-last>=5000000) {
      ESP_LOGI("lcd","%u completed updates in %lld us",count,(long long)(esp_timer_get_time()-last));
      count=0;last=esp_timer_get_time();
    }
  }
  // On hardware failure retain resources: freeing a DMA target would be unsafe.
  vTaskDelete(nullptr);
}
}
bool startLcdOutput(PresentationSnapshotPool &pool) {
  return xTaskCreate(worker,"lcd_output",6144,&pool,2,nullptr)==pdPASS;
}
}
#endif
