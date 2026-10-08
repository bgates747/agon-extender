// Host-only SDK surface for the actual HdmiOutput implementation. Calls can
// fail before acquiring their resource; live-resource assertions detect unwind
// errors. Real driver IRQ/DMA/cache behavior is deliberately not simulated.
#pragma once
#include <atomic>
#include <cassert>
#include <chrono>
#include <condition_variable>
#include <cstdarg>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <mutex>
#include <string>
#include <thread>
#include <unordered_set>
#include <vector>

using esp_err_t = int;
constexpr int ESP_OK=0, ESP_ERR_NO_MEM=0x101, ESP_ERR_INVALID_STATE=0x103, ESP_FAIL=-1;
constexpr int MALLOC_CAP_SPIRAM=1, MALLOC_CAP_8BIT=2, MALLOC_CAP_INTERNAL=4;
constexpr int I2C_NUM_0=0, GPIO_NUM_7=7, GPIO_NUM_8=8, I2C_CLK_SRC_DEFAULT=0;
constexpr int MIPI_DSI_PHY_CLK_SRC_DEFAULT=0, MIPI_DSI_DPI_CLK_SRC_PLL_F240M=0;
constexpr int LCD_COLOR_FMT_RGB888=0, LCD_RGB_ELEMENT_ORDER_RGB=0;
constexpr int LT8912B_ASPECT_RATION_4_3=1, LT8912B_ASPECT_RATION_16_9=2;
#define IRAM_ATTR
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define ESP_LOGI(...) ((void)0)
inline const char *esp_err_to_name(int) { return "host failure"; }
using portMUX_TYPE = std::recursive_mutex;
#define portMUX_INITIALIZER_UNLOCKED {}
#define portENTER_CRITICAL(p) (p)->lock()
#define portEXIT_CRITICAL(p) (p)->unlock()
#define portENTER_CRITICAL_ISR(p) (p)->lock()
#define portEXIT_CRITICAL_ISR(p) (p)->unlock()
using BaseType_t=int;
using UBaseType_t=unsigned;
using TaskFunction_t=void (*)(void *);
constexpr int pdTRUE=1, pdPASS=1;
constexpr unsigned portMAX_DELAY=~0u;
struct HostTask {
  std::mutex mutex;
  std::condition_variable cv;
  unsigned notifications{};
  bool stop{};
  std::thread thread;
};
using TaskHandle_t=HostTask *;
namespace hdmi_host {
inline thread_local int core=1;
inline thread_local HostTask *task{};
struct Stop {};
inline std::string fail_operation;
inline int fail_count{}, fail_error=ESP_FAIL;
inline std::unordered_set<void *> live;
inline std::atomic<unsigned> draws{}, faults{}, front{};
inline unsigned staged{};
inline bool suppress_start_frame{};
inline std::function<void()> after_draw;
inline int operation(const char *name) {
  if (fail_count && fail_operation==name) { --fail_count; return fail_error; }
  return ESP_OK;
}
inline void *acquire() { auto p=std::malloc(1); assert(p); assert(live.insert(p).second); return p; }
inline void release(void *p) { assert(p && live.erase(p)==1); std::free(p); }
inline void inject(const char *name,int count=1,int error=ESP_FAIL) {
  fail_operation=name; fail_count=count; fail_error=error;
}
}
inline int xPortGetCoreID() { return hdmi_host::core; }
inline void vTaskDelay(unsigned) { std::this_thread::sleep_for(std::chrono::milliseconds(1)); }
inline int64_t esp_timer_get_time() {
  return std::chrono::duration_cast<std::chrono::microseconds>(
      std::chrono::steady_clock::now().time_since_epoch()).count();
}
inline unsigned ulTaskNotifyTake(int,unsigned) {
  auto *t=hdmi_host::task; assert(t);
  std::unique_lock lock(t->mutex);
  t->cv.wait(lock,[&]{return t->stop || t->notifications;});
  if(t->stop) throw hdmi_host::Stop{};
  auto n=t->notifications;t->notifications=0;return n;
}
inline void xTaskNotifyGive(HostTask *t) {
  assert(t);std::lock_guard lock(t->mutex);++t->notifications;t->cv.notify_one();
}
inline int xTaskCreatePinnedToCoreWithCaps(TaskFunction_t fn,const char *,uint32_t,
    void *ctx,unsigned,HostTask **out,int core,int) {
  if(hdmi_host::operation("task")!=ESP_OK)return 0;
  auto *t=new HostTask;*out=t;
  t->thread=std::thread([=]{hdmi_host::core=core;hdmi_host::task=t;
    try {fn(ctx);} catch(hdmi_host::Stop const &) {}});
  return pdPASS;
}
inline void vTaskDeleteWithCaps(HostTask *t) {
  {std::lock_guard lock(t->mutex);t->stop=true;t->cv.notify_one();}
  t->thread.join();delete t;
}
inline size_t heap_caps_get_free_size(int) {return 12345;}
inline void heap_caps_free(void *p) {std::free(p);}
inline void *heap_caps_aligned_calloc(size_t,size_t n,size_t size,int) {return std::calloc(n,size);}
using esp_ldo_channel_handle_t=void *;
using i2c_master_bus_handle_t=void *;
using esp_lcd_panel_io_handle_t=void *;
using esp_lcd_dsi_bus_handle_t=void *;
struct esp_ldo_channel_config_t {int chan_id,voltage_mv;};
struct i2c_master_bus_config_t {
  int i2c_port,sda_io_num,scl_io_num,clk_source;
  struct {bool enable_internal_pullup;} flags;
};
struct esp_lcd_panel_io_i2c_config_t {
  int scl_speed_hz,dev_addr,control_phase_bytes,lcd_cmd_bits,lcd_param_bits;
  struct {bool disable_control_phase;} flags;
};
struct esp_lcd_dsi_bus_config_t {int bus_id,num_data_lanes,phy_clk_src;unsigned lane_bit_rate_mbps;};
struct esp_lcd_dpi_panel_config_t {
  int virtual_channel,dpi_clk_src;float dpi_clock_freq_mhz;
  int in_color_format,out_color_format;unsigned num_fbs;
  struct {int h_size,v_size,hsync_pulse_width,hsync_back_porch,hsync_front_porch,
    vsync_pulse_width,vsync_back_porch,vsync_front_porch;} video_timing;
  struct {bool disable_lp,use_dma2d;} flags;
};
struct lt8912b_vendor_config_t {
  struct {int hfp,hs,hbp,hact,htotal,vfp,vs,vbp,vact,vtotal,h_polarity,v_polarity,vic,aspect_ratio;unsigned pclk_mhz;} video_timing;
  struct {esp_lcd_dsi_bus_handle_t dsi_bus;esp_lcd_dpi_panel_config_t *dpi_config;int lane_num;} mipi_config;
};
struct esp_lcd_panel_dev_config_t {int bits_per_pixel,rgb_ele_order,reset_gpio_num;void *vendor_config;};
struct esp_lcd_panel_lt8912b_io_t {void *a,*b,*c;};
struct HostPanel;
using esp_lcd_panel_handle_t=HostPanel *;
struct esp_lcd_dpi_panel_event_data_t {};
struct esp_lcd_dpi_panel_event_callbacks_t {
  bool (*on_frame_buf_complete)(HostPanel *,esp_lcd_dpi_panel_event_data_t *,void *);
};
struct HostPanel {
  void *resource{};int w{},h{};unsigned count{},selected{};
  std::vector<uint8_t> pixels[2];
  esp_lcd_dpi_panel_event_callbacks_t callback{};void *context{};
};
inline esp_err_t host_acquire(const char *name,void **out) {
  int error=hdmi_host::operation(name);if(error==ESP_OK)*out=hdmi_host::acquire();return error;
}
inline int esp_ldo_acquire_channel(esp_ldo_channel_config_t *,void **p){return host_acquire("power",p);}
inline int i2c_new_master_bus(i2c_master_bus_config_t *,void **p){return host_acquire("i2c",p);}
inline int esp_lcd_new_panel_io_i2c(void *,esp_lcd_panel_io_i2c_config_t *c,void **p){
  auto n="io"+std::to_string(c->dev_addr-0x48);return host_acquire(n.c_str(),p);
}
inline int esp_lcd_new_dsi_bus(esp_lcd_dsi_bus_config_t *,void **p){return host_acquire("dsi",p);}
inline int esp_ldo_release_channel(void *p){hdmi_host::release(p);return ESP_OK;}
inline int i2c_del_master_bus(void *p){hdmi_host::release(p);return ESP_OK;}
inline int esp_lcd_panel_io_del(void *p){hdmi_host::release(p);return ESP_OK;}
inline int esp_lcd_del_dsi_bus(void *p){hdmi_host::release(p);return ESP_OK;}
inline int esp_lcd_new_panel_lt8912b(esp_lcd_panel_lt8912b_io_t *,esp_lcd_panel_dev_config_t *c,HostPanel **out) {
  int e=hdmi_host::operation("panel");if(e!=ESP_OK)return e;
  auto *dpi=static_cast<lt8912b_vendor_config_t *>(c->vendor_config)->mipi_config.dpi_config;
  auto *p=new HostPanel;p->resource=hdmi_host::acquire();
  p->w=dpi->video_timing.h_size;p->h=dpi->video_timing.v_size;p->count=dpi->num_fbs;
  for(unsigned i=0;i<p->count;++i)p->pixels[i].resize(size_t(p->w)*p->h*3);
  *out=p;return ESP_OK;
}
inline int esp_lcd_panel_del(HostPanel *p){hdmi_host::release(p->resource);delete p;return ESP_OK;}
inline int esp_lcd_dpi_panel_get_frame_buffer(HostPanel *p,unsigned n,void **first,...) {
  int e=hdmi_host::operation("buffers");if(e!=ESP_OK)return e;
  assert(n==p->count);*first=p->pixels[0].data();
  if(n>1){va_list args;va_start(args,first);*va_arg(args,void **)=p->pixels[1].data();va_end(args);}
  return ESP_OK;
}
inline int esp_lcd_panel_reset(HostPanel *){return hdmi_host::operation("reset");}
inline int esp_lcd_dpi_panel_register_event_callbacks(HostPanel *p,esp_lcd_dpi_panel_event_callbacks_t *c,void *ctx) {
  int e=hdmi_host::operation("callback");if(e==ESP_OK){p->callback=*c;p->context=ctx;}return e;
}
inline void host_frame(HostPanel *p) {
  int old=hdmi_host::core;hdmi_host::core=1;hdmi_host::front=p->selected;
  p->callback.on_frame_buf_complete(p,nullptr,p->context);hdmi_host::core=old;
}
inline int esp_lcd_panel_init(HostPanel *p) {
  int e=hdmi_host::operation("init");if(e!=ESP_OK)return e;
  hdmi_host::faults=0;hdmi_host::front=0;
  if(!hdmi_host::suppress_start_frame)host_frame(p);
  return ESP_OK;
}
inline int esp_lcd_panel_draw_bitmap(HostPanel *p,int,int,int,int,const void *pixels) {
  int e=hdmi_host::operation("draw");if(e!=ESP_OK)return e;
  assert(hdmi_host::live.count(p->resource));
  p->selected=pixels==p->pixels[0].data()?0:1;assert(p->selected<p->count);
  ++hdmi_host::draws;if(hdmi_host::after_draw)hdmi_host::after_draw();return ESP_OK;
}

// Renderer substitution only supplies the surfaces called by the real sink;
// the service/controller integration is covered by hdmi_frame_scheduling_test.
namespace fabgl {
struct P4Rgb888Controller {
  int w=848,h=480;bool doubled{};
  int getViewPortWidth(){return w;}int getViewPortHeight(){return h;}
  bool isDoubleBuffered(){return doubled;}
};
}
#define AGON_STOCK_NATIVE_GUARD ((void)0)
namespace agon::extender::display {
constexpr int kPresentationSnapshotMaximumWidth=1024;
inline unsigned visible_generation{};
inline unsigned stockVisibleGeneration(){return visible_generation;}
inline std::function<void(int)> on_row;
class StockRuntimeController {
 public:
  fabgl::P4Rgb888Controller controller;bool direct{};
  fabgl::P4Rgb888Controller &display(){return controller;}
  fabgl::P4Rgb888Controller &paletted(){return controller;}
  bool panelStorage(){return direct;}bool rgb888Storage(){return false;}
  unsigned preparePanelFrame(int &){return 0;}
  void prepareRow(int y,uint8_t *p){std::memset(p,0,controller.w);if(on_row)on_row(y); }
  void prepareRgb888Row(int,uint8_t *,uint8_t *){}
};
}
