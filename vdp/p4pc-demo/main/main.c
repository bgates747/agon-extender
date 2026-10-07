/* Standalone P4-PC experiment, P4PC-001. Board setup is the Olimex BSP
 * pinned by prepare.py; this is not Extender firmware. In particular, never
 * configure BOOT/GPIO35 as a button: it is also Ethernet RMII TXD1.
 * Audio uses one synchronous owner and finite sample counts; no detached
 * playback task can retain a deleted codec handle. SD commands only list. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdatomic.h>
#include <dirent.h>
#include <sys/stat.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/usb_serial_jtag.h"
#include "driver/usb_serial_jtag_vfs.h"
#include "esp_app_desc.h"
#include "esp_system.h"
#include "esp_lcd_mipi_dsi.h"
#include "esp_lcd_panel_ops.h"
#include "esp_cache.h"
#include "esp_chip_info.h"
#include "esp_timer.h"
#include "esp_heap_caps.h"
#include "esp_netif.h"
#include "esp_codec_dev.h"
#include "bsp/esp32_p4_function_ev_board.h"
#include "lvgl.h"
#include "render_reference.h"
#include "lv_demos.h"
#include "lan_test.h"
#include "sd_card_test.h"

#define DOTS 24
#define PI_F 3.14159265358979323846f
static lv_obj_t *stage, *title, *status, *dots[DOTS];

static esp_netif_t *netif;
static esp_codec_dev_handle_t speaker;
static bool sd_ready;
static _Atomic bool paused=true, widgets_active, scanout_active=true, presentation_bypass, capacity_mode, capacity_owned;
static _Atomic unsigned animation_period_ms=16;
static float capacity_phase;
static int volume=65;
static unsigned flushes;
static lv_display_flush_cb_t original_flush;
extern esp_lcd_panel_handle_t playground_panel(void);
extern esp_err_t playground_bridge_relock(esp_lcd_panel_handle_t panel);
extern esp_err_t playground_scanout_enable(esp_lcd_panel_handle_t panel, bool enable);
static int scene; /* 0 orbit, 1 bounce, 2 bars */
static int width, height;
static unsigned ticks;
static unsigned render_passes;
static uint64_t render_us, render_max_us;
static int64_t render_started;
static volatile unsigned scanout_frames;
static unsigned submitted_frames;
static portMUX_TYPE metrics_lock=portMUX_INITIALIZER_UNLOCKED;
static bool benchmark_active, render_measured, refresh_measured, refresh_rendered;
static uint64_t frame_flush_us, frame_cache_us, frame_wait_us;
static int64_t refresh_started;
static uint64_t benchmark_render_us,benchmark_render_max_us, benchmark_flush_us;
static uint64_t benchmark_cache_us, benchmark_wait_us, benchmark_refresh_us;
static unsigned benchmark_renders, benchmark_refreshes;
void playground_scanout_event(void)
{
    /* ISR: no allocation/logging. Repeated pixels count as scanout, not rendering. */
    portENTER_CRITICAL_ISR(&metrics_lock);scanout_frames++;portEXIT_CRITICAL_ISR(&metrics_lock);
}
void playground_cache_event(uint64_t elapsed) { frame_cache_us+=elapsed; }
void playground_wait_event(uint64_t elapsed) { frame_wait_us+=elapsed; }
static void render_event(lv_event_t *event)
{
    lv_event_code_t code=lv_event_get_code(event);
    if(code==LV_EVENT_REFR_START) {
        refresh_started=esp_timer_get_time();refresh_rendered=false;
        portENTER_CRITICAL(&metrics_lock);refresh_measured=benchmark_active;portEXIT_CRITICAL(&metrics_lock);
    } else if(code==LV_EVENT_RENDER_START) {
        render_started=esp_timer_get_time();
        frame_flush_us=frame_cache_us=frame_wait_us=0;refresh_rendered=true;
        portENTER_CRITICAL(&metrics_lock);render_measured=benchmark_active;portEXIT_CRITICAL(&metrics_lock);
    } else if(code==LV_EVENT_RENDER_READY) {
        uint64_t elapsed=esp_timer_get_time()-render_started;
        portENTER_CRITICAL(&metrics_lock);
        render_passes++;render_us+=elapsed;
        if(elapsed>render_max_us)render_max_us=elapsed;
        if(benchmark_active && render_measured) {
            benchmark_renders++;benchmark_render_us+=elapsed;
            benchmark_flush_us+=frame_flush_us;benchmark_cache_us+=frame_cache_us;
            benchmark_wait_us+=frame_wait_us;
            if(elapsed>benchmark_render_max_us)benchmark_render_max_us=elapsed;
        }
        portEXIT_CRITICAL(&metrics_lock);
    } else if(code==LV_EVENT_REFR_READY && refresh_rendered) {
        uint64_t elapsed=esp_timer_get_time()-refresh_started;
        portENTER_CRITICAL(&metrics_lock);
        if(benchmark_active && refresh_measured) {benchmark_refreshes++;benchmark_refresh_us+=elapsed;}
        portEXIT_CRITICAL(&metrics_lock);
    }
}
static const uint32_t palette[] = {0x42e8e0,0xff637d,0xffcc66,0x9980ff,0x6cf09e,0x64aeff};

static void animate(void)
{
    if (paused || widgets_active || scene == 2) return;
    portENTER_CRITICAL(&metrics_lock);ticks++;portEXIT_CRITICAL(&metrics_lock);
    /* Capacity windows replay prescribed 1/60 s steps, independent of throughput.
     * Ordinary motion remains tied to elapsed time; this is not an n-body simulation. */
    float t;
    if(capacity_mode) {capacity_phase+=1.0f/60.0f;t=capacity_phase;}
    else t=esp_timer_get_time()/1000000.0f;
    int area_h = height - 190;
    for (int i=0;i<DOTS;i++) {
        int size = 14 + (i%4)*10;
        float x, y;
        if (!scene) {
            float a = t*(0.35f + (i%3)*0.15f) + i*(2*PI_F/DOTS);
            float r = 0.3f + (i%4)*0.17f;
            x = width/2 + cosf(a)*width*0.40f*r - size/2;
            y = area_h/2 + sinf(a*1.5f)*area_h*0.41f*r - size/2;
        } else {
            float bx = fmodf(t*(65+i*5)+i*47, 2*(width-size));
            float by = fmodf(t*(40+i*3)+i*31, 2*(area_h-size));
            x = bx > width-size ? 2*(width-size)-bx : bx;
            y = by > area_h-size ? 2*(area_h-size)-by : by;
        }
        lv_obj_set_pos(dots[i], (int)x, (int)y);
    }
}

static void set_scene(int selected)
{
    bool was_paused=atomic_exchange(&paused,true);
    if (!bsp_display_lock(5000)) {paused=was_paused;puts("ERR display busy");return;}
    scene=selected;
    portENTER_CRITICAL(&metrics_lock);ticks=0;portEXIT_CRITICAL(&metrics_lock);
    lv_obj_clean(stage);
    const char *names[]={"Orbital motion", "Bouncing shapes", "Colour bars"};
    lv_label_set_text_fmt(title,"P4-PC playground  |  %s",names[scene]);
    if (scene==2) {
        const uint32_t bars[]={0xffffff,0xffff00,0x00ffff,0x00ff00,0xff00ff,0xff0000,0x0000ff,0x000000};
        for (int i=0;i<8;i++) {
            lv_obj_t *o=lv_obj_create(stage); lv_obj_remove_style_all(o);
            lv_obj_set_pos(o,i*width/8,0);
            lv_obj_set_size(o,(i+1)*width/8-i*width/8,height-190);
            lv_obj_set_style_bg_color(o,lv_color_hex(bars[i]),0);
            lv_obj_set_style_bg_opa(o,LV_OPA_COVER,0);
        }
    } else {
        for (int i=0;i<DOTS;i++) {
            dots[i]=lv_obj_create(stage); lv_obj_remove_style_all(dots[i]);
            int size=14+(i%4)*10;
            lv_obj_set_size(dots[i],size,size);
            lv_obj_set_style_radius(dots[i],scene?6:LV_RADIUS_CIRCLE,0);
            lv_obj_set_style_bg_color(dots[i],lv_color_hex(palette[i%6]),0);
            lv_obj_set_style_bg_opa(dots[i],LV_OPA_COVER,0);
        }
        animate();
    }
    bsp_display_unlock();
    paused=was_paused;
    printf("OK demo %s\n",names[scene]);
}

static void update_status(void)
{
    esp_netif_ip_info_t ip={0};
    if (netif) esp_netif_get_ip_info(netif,&ip);
    if (bsp_display_lock(1000)) {
        lv_label_set_text_fmt(status,"Ethernet: " IPSTR "   |   SD: %s   |   360 MHz   |   USB serial: help",
                             IP2STR(&ip.ip),sd_ready?"mounted":"not mounted");
        bsp_display_unlock();
    }
}

/* Keep animation pacing outside lv_timer_handler. At 720p software drawing,
 * a perpetually overdue animation timer can keep that handler busy and starve
 * main/idle work. Invalidate only between completed LVGL handler passes and
 * always sleep after the update. Never disable the watchdog to mask overload. */
static void animation_task(void *arg)
{
    (void)arg;
    TickType_t wake=xTaskGetTickCount();
    for (;;) {
        if (!paused && !widgets_active && !capacity_owned && bsp_display_lock(100)) { animate(); bsp_display_unlock(); }
        /* Nominal 60 Hz source; scanout is independently counted. Do not
         * infer presentation FPS from ticks or from LVGL flush fragments. */
        if(!xTaskDelayUntil(&wake,pdMS_TO_TICKS(animation_period_ms))) {
            wake=xTaskGetTickCount();vTaskDelay(1);
        }
    }
}

static void count_flush(lv_display_t *display,const lv_area_t *area,uint8_t *pixels)
{
    int64_t started=esp_timer_get_time();
    bool last=lv_display_flush_is_last(display);
    bool bypass=presentation_bypass || !scanout_active;
    portENTER_CRITICAL(&metrics_lock);
    flushes++;
    if(last && !bypass)submitted_frames++;
    portEXIT_CRITICAL(&metrics_lock);
    if(bypass) {
        /* Match the normal port's final full-frame writeback, including its
         * cost in both capacity windows. No panel flip or VSYNC semaphore wait.
         * The two retained LVGL buffers still receive dirty-area synchronization.
         * Active scanout repeats one buffer; these are drawing-capacity counts,
         * not safe presented frames (the diagnostic may overwrite a scanned FB). */
        if(last) {
            int64_t cache_started=esp_timer_get_time();
            ESP_ERROR_CHECK(esp_cache_msync(pixels,(size_t)width*height*3,
                ESP_CACHE_MSYNC_FLAG_DIR_C2M|ESP_CACHE_MSYNC_FLAG_UNALIGNED));
            playground_cache_event(esp_timer_get_time()-cache_started);
        }
        lv_display_flush_ready(display);
    } else original_flush(display,area,pixels);
    frame_flush_us+=esp_timer_get_time()-started;
}

static bool set_scanout(bool enabled)
{
    bool was_paused=atomic_exchange(&paused,true);
    if(!bsp_display_lock(5000)) {paused=was_paused;puts("ERR display busy");return false;}
    esp_err_t error=playground_scanout_enable(playground_panel(),enabled);
    if(error==ESP_OK) {
        scanout_active=enabled;
        if(enabled) {
            vTaskDelay(pdMS_TO_TICKS(50));
            error=playground_bridge_relock(playground_panel());
            lv_obj_invalidate(lv_screen_active());
        }
    }
    bsp_display_unlock();paused=was_paused;
    printf("%s scanout %s: %s; framebuffers retained\n",error==ESP_OK?"OK":"ERR",
           enabled?"on":"off",esp_err_to_name(error));
    return error==ESP_OK;
}

/* Finite windows use the P4 monotonic clock. Instrument complete intervals
 * beginning inside the window; boundary counts may differ by one render.
 * 'draw' owns sequential updates/refreshes and bypasses presentation in BOTH
 * scanout states. Keep its cache writeback
 * and fixed-step workload identical; it is not a presented FPS claim. */
static void benchmark(int seconds,bool capacity)
{
    bool was_paused=paused;
    if(capacity) {
        paused=true;
        if(!bsp_display_lock(5000)) {paused=was_paused;puts("ERR display busy");return;}
        if(widgets_active || scene==2) {bsp_display_unlock();paused=was_paused;puts("ERR draw benchmark requires orbit or bounce");return;}
        /* One owner advances exactly one prescribed step then renders it.
         * r11's two independently scheduled tasks inserted polling gaps and
         * occasionally merged updates; its draw-only throughput was not a
         * drawing-capacity ceiling. Hold the LVGL mutex for this finite test,
         * with a one-tick yield after each complete refresh for idle/watchdog.
         * Ordinary visible animation/port scheduling is unchanged. */
        capacity_owned=true;capacity_phase=0;capacity_mode=true;presentation_bypass=true;
        lv_timer_pause(lv_display_get_refr_timer(lv_display_get_default()));
        paused=false;
        int64_t warmup=esp_timer_get_time();
        while(esp_timer_get_time()-warmup<500000) {
            animate();lv_refr_now(lv_display_get_default());vTaskDelay(1);
        }
    }
    unsigned start_updates,start_renders,start_submitted,start_scanouts;
    portENTER_CRITICAL(&metrics_lock);
    start_updates=ticks;start_renders=render_passes;
    start_submitted=submitted_frames;start_scanouts=scanout_frames;
    benchmark_render_us=benchmark_render_max_us=benchmark_flush_us=0;
    benchmark_cache_us=benchmark_wait_us=benchmark_refresh_us=0;
    benchmark_renders=benchmark_refreshes=0;benchmark_active=true;
    int64_t started=esp_timer_get_time();
    portEXIT_CRITICAL(&metrics_lock);
    printf("BENCH START seconds=%d mode=%s scanout=%s geometry=%dx%d\n",seconds,
           capacity?"draw":"paced",scanout_active?"on":"off",width,height);
    while(esp_timer_get_time()-started<(int64_t)seconds*1000000) {
        if(capacity) {animate();lv_refr_now(lv_display_get_default());vTaskDelay(1);}
        else vTaskDelay(pdMS_TO_TICKS(20));
    }
    portENTER_CRITICAL(&metrics_lock);
    int64_t elapsed=esp_timer_get_time()-started;
    unsigned updates=ticks-start_updates,renders=render_passes-start_renders;
    unsigned submitted=submitted_frames-start_submitted,scanouts=scanout_frames-start_scanouts;
    uint64_t total=benchmark_render_us,maximum=benchmark_render_max_us,flushing=benchmark_flush_us;
    uint64_t cache=benchmark_cache_us,waiting=benchmark_wait_us,refresh=benchmark_refresh_us;
    unsigned measured=benchmark_renders,refreshes=benchmark_refreshes;
    benchmark_active=false;
    portEXIT_CRITICAL(&metrics_lock);
    double duration=elapsed/1000000.0,divisor=measured?1000.0*measured:1.0;
    printf("BENCH END elapsed_us=%lld updates=%u update_hz=%.3f renders=%u render_hz=%.3f "
           "submitted=%u submitted_hz=%.3f scanouts=%u scanout_hz=%.3f "
           "measured=%u render_mean_ms=%.3f render_max_ms=%.3f "
           "draw_mean_ms=%.3f flush_mean_ms=%.3f cache_mean_ms=%.3f wait_mean_ms=%.3f "
           "refreshes=%u refresh_mean_ms=%.3f\n",
           (long long)elapsed,updates,updates/duration,renders,renders/duration,
           submitted,submitted/duration,scanouts,scanouts/duration,
           measured,total/divisor,maximum/1000.0,
           (total-flushing)/divisor,flushing/divisor,cache/divisor,waiting/divisor,
           refreshes,refreshes?refresh/(1000.0*refreshes):0.0);
    if(capacity) {
        paused=true;
        capacity_mode=presentation_bypass=false;
        lv_timer_resume(lv_display_get_refr_timer(lv_display_get_default()));
        lv_obj_invalidate(lv_screen_active());
        bsp_display_unlock();capacity_owned=false;paused=was_paused;
    }
}

/* Direct packed-format reference; same rasterizer/opaque circle spans and
 * full-frame clear for both formats, independently of LVGL's AA/labels/dirty
 * areas. RGB332 is NOT a native path in the selected LVGL software renderer.
 * Both buffers remain in PSRAM; DMA is stopped before any one-byte writes. */
static void benchmark_reference(int seconds,int cpp)
{
    if(width!=640 || height!=480) {puts("ERR reference benchmark requires native 640x480");return;}
    bool was_paused=atomic_exchange(&paused,true),was_scanning=scanout_active;
    if(!bsp_display_lock(5000)) {paused=was_paused;puts("ERR display busy");return;}
    if(widgets_active) {bsp_display_unlock();paused=was_paused;puts("ERR reference benchmark requires playground");return;}
    esp_err_t error=playground_scanout_enable(playground_panel(),false);
    if(error!=ESP_OK) {bsp_display_unlock();paused=was_paused;printf("ERR DMA stop: %s\n",esp_err_to_name(error));return;}
    scanout_active=false;
    uint8_t *buffers[2];
    ESP_ERROR_CHECK(esp_lcd_dpi_panel_get_frame_buffer(playground_panel(),2,(void **)&buffers[0],(void **)&buffers[1],NULL));
    lv_timer_pause(lv_display_get_refr_timer(lv_display_get_default()));
    struct reference_dot objects[DOTS];
    for(int i=0;i<DOTS;i++)objects[i]=(struct reference_dot){0,0,14+10*(i%4),palette[i%6]};
    /* Initialize spans/cache outside the measured window. */
    reference_render(buffers[0],width,height,cpp,objects,DOTS);
    reference_render(buffers[1],width,height,cpp,objects,DOTS);
    size_t bytes=(size_t)width*height*cpp;
    unsigned frames=0,start_scanouts;
    uint64_t drawing=0,cache=0,motion=0,maximum=0;
    portENTER_CRITICAL(&metrics_lock);start_scanouts=scanout_frames;portEXIT_CRITICAL(&metrics_lock);
    printf("REFBENCH START seconds=%d format=%s width=%d height=%d frame_bytes=%u DMA=off AA=off labels=off full_clear=yes\n",
           seconds,cpp==1?"RGB332":"RGB888",width,height,(unsigned)bytes);
    int64_t started=esp_timer_get_time();
    while(esp_timer_get_time()-started<(int64_t)seconds*1000000) {
        int64_t step=esp_timer_get_time();float t=frames/60.0f;
        int area_h=height-190;
        for(int i=0;i<DOTS;i++) {
            float a=t*(0.35f+(i%3)*0.15f)+i*(2*PI_F/DOTS),r=0.3f+(i%4)*0.17f;
            objects[i].x=(int)(width/2+cosf(a)*width*0.40f*r-objects[i].size/2);
            objects[i].y=85+(int)(area_h/2+sinf(a*1.5f)*area_h*0.41f*r-objects[i].size/2);
        }
        motion+=esp_timer_get_time()-step;
        uint8_t *buffer=buffers[frames%2];step=esp_timer_get_time();
        reference_render(buffer,width,height,cpp,objects,DOTS);
        uint64_t draw=esp_timer_get_time()-step;drawing+=draw;if(draw>maximum)maximum=draw;
        step=esp_timer_get_time();
        ESP_ERROR_CHECK(esp_cache_msync(buffer,bytes,ESP_CACHE_MSYNC_FLAG_DIR_C2M|ESP_CACHE_MSYNC_FLAG_UNALIGNED));
        cache+=esp_timer_get_time()-step;frames++;
        vTaskDelay(1); /* Bounded CPU run with idle/watchdog opportunity. */
    }
    int64_t elapsed=esp_timer_get_time()-started;unsigned scanouts;
    portENTER_CRITICAL(&metrics_lock);scanouts=scanout_frames-start_scanouts;portEXIT_CRITICAL(&metrics_lock);
    uint32_t checksum=2166136261u;uint8_t *last=buffers[(frames-1)%2];
    for(size_t i=0;i<bytes;i++)checksum=(checksum^last[i])*16777619u;
    printf("REFBENCH END elapsed_us=%lld frames=%u frame_hz=%.3f scanouts=%u "
           "draw_mean_ms=%.3f draw_max_ms=%.3f cache_mean_ms=%.3f motion_mean_ms=%.3f checksum=%08lx\n",
           (long long)elapsed,frames,frames/(elapsed/1000000.0),scanouts,
           drawing/(1000.0*frames),maximum/1000.0,cache/(1000.0*frames),motion/(1000.0*frames),(unsigned long)checksum);
    if(scanouts)puts("ERR reference window had DMA completions");
    /* Restore RGB888 GUI pixels after the diagnostic overwrote panel buffers.
     * Benchmark measurements end before this recovery; no one-byte scanout. */
    lv_obj_invalidate(lv_screen_active());lv_timer_resume(lv_display_get_refr_timer(lv_display_get_default()));
    if(was_scanning) {
        error=playground_scanout_enable(playground_panel(),true);scanout_active=error==ESP_OK;
        if(error==ESP_OK) {vTaskDelay(pdMS_TO_TICKS(50));error=playground_bridge_relock(playground_panel());}
        if(error!=ESP_OK)printf("ERR scanout recovery: %s\n",esp_err_to_name(error));
    }
    bsp_display_unlock();paused=was_paused;
}

static void video_diagnostic(const char *mode)
{
    bool was_paused=atomic_exchange(&paused,true);
    if(!width || !bsp_display_lock(5000)) {paused=was_paused;puts("ERR display busy");return;}
    if(!strcmp(mode,"pattern")) {
        /* IDF's host pattern bypasses PSRAM scanout and LVGL pixel data.
         * Retain the same DSI timing and external HDMI bridge for isolation. */
        paused=true;
        lv_timer_pause(lv_display_get_refr_timer(lv_display_get_default()));
        esp_err_t e=esp_lcd_dpi_panel_set_pattern(playground_panel(),MIPI_DSI_PATTERN_BAR_VERTICAL);
        printf("DSI host vertical bars: %s\n",esp_err_to_name(e));
        bsp_display_unlock();return;
    }
    uint8_t *fb=NULL;
    esp_err_t err=esp_lcd_dpi_panel_get_frame_buffer(playground_panel(),1,(void **)&fb);
    if(err!=ESP_OK) {printf("ERR framebuffer %s\n",esp_err_to_name(err));bsp_display_unlock();return;}
    size_t bytes=(size_t)width*height*3;
    if(!strcmp(mode,"raw")) {
        ESP_ERROR_CHECK(esp_lcd_dpi_panel_set_pattern(playground_panel(),MIPI_DSI_PATTERN_NONE));
        paused=true;
        lv_timer_pause(lv_display_get_refr_timer(lv_display_get_default()));
        const uint32_t colours[]={0xffffff,0xffff00,0x00ffff,0x00ff00,0xff00ff,0xff0000,0x0000ff,0};
        for(int y=0;y<height;y++)for(int x=0;x<width;x++) {
            uint32_t c=colours[x*8/width];size_t i=((size_t)y*width+x)*3;
            fb[i]=c&255;fb[i+1]=(c>>8)&255;fb[i+2]=(c>>16)&255;
        }
        err=esp_cache_msync(fb,bytes,ESP_CACHE_MSYNC_FLAG_DIR_C2M|ESP_CACHE_MSYNC_FLAG_UNALIGNED);
        if(err==ESP_OK) {
            /* Select this buffer explicitly: direct double buffering may
             * currently scan the other panel-owned buffer. */
            err=esp_lcd_panel_draw_bitmap(playground_panel(),0,0,width,height,fb);
        }
        printf("Direct framebuffer bars: %s\n",esp_err_to_name(err));
    } else if(!strcmp(mode,"ui")) {
        ESP_ERROR_CHECK(esp_lcd_dpi_panel_set_pattern(playground_panel(),MIPI_DSI_PATTERN_NONE));
        lv_timer_resume(lv_display_get_refr_timer(lv_display_get_default()));
        lv_obj_invalidate(lv_screen_active());paused=false;
    }
    if(strcmp(mode,"raw") && strcmp(mode,"pattern") && strcmp(mode,"ui"))paused=was_paused;
    size_t nonzero=0;uint32_t sum=0;
    for(size_t i=0;i<bytes;i+=97){if(fb[i])nonzero++;sum+=fb[i];}
    printf("Video: %dx%d RGB888, LVGL flushes %u, sampled nonzero %u, sum %u\n",
           width,height,flushes,(unsigned)nonzero,(unsigned)sum);
    bsp_display_unlock();
}

static void display_init(void)
{
    lv_display_t *display=bsp_display_start();
    if (!display) { puts("ERR HDMI initialization"); return; }
    original_flush=lv_display_get_flush_cb(display);
    lv_display_set_flush_cb(display,count_flush);
    lv_display_add_event_cb(display,render_event,LV_EVENT_RENDER_START,NULL);
    lv_display_add_event_cb(display,render_event,LV_EVENT_RENDER_READY,NULL);
    lv_display_add_event_cb(display,render_event,LV_EVENT_REFR_START,NULL);
    lv_display_add_event_cb(display,render_event,LV_EVENT_REFR_READY,NULL);
    width=lv_display_get_horizontal_resolution(display);
    height=lv_display_get_vertical_resolution(display);
    if(width==640 && height==480) {
        /* The copied LT driver configured/reset the receiver before starting
         * DPI. Retry RX/DDS acquisition with a live stream, independently of
         * the pixel-rendering benchmark. No DMA abort or framebuffer change. */
        vTaskDelay(pdMS_TO_TICKS(50));
        printf("Bridge live-stream relock: %s\n",esp_err_to_name(playground_bridge_relock(playground_panel())));
    }
    if (!bsp_display_lock(1000)) return;
    lv_obj_t *screen=lv_screen_active();
    lv_obj_set_style_bg_color(screen,lv_color_hex(0x0b1020),0);
    lv_obj_set_style_text_color(screen,lv_color_hex(0xeaf2ff),0);
    title=lv_label_create(screen);
    lv_obj_set_pos(title,32,22);
    lv_obj_set_style_text_font(title,&lv_font_montserrat_24,0);
    stage=lv_obj_create(screen); lv_obj_remove_style_all(stage);
    lv_obj_set_pos(stage,0,85); lv_obj_set_size(stage,width,height-190);
    lv_obj_remove_flag(stage,LV_OBJ_FLAG_SCROLLABLE);
    status=lv_label_create(screen); lv_obj_set_pos(status,32,height-80);
    lv_obj_t *hint=lv_label_create(screen);
    lv_label_set_text(hint,"demo orbit | bounce | bars     pause / resume     tone 440 3     melody     sd ls");
    lv_obj_set_pos(hint,32,height-45);
    bsp_display_unlock();
    set_scene(0);
}

static bool audio_init(void)
{
    if (speaker) return true;
    speaker=bsp_audio_codec_speaker_init();
    if (!speaker) { puts("ERR codec init"); return false; }
    esp_codec_dev_sample_info_t format={.sample_rate=48000,.channel=2,.bits_per_sample=16};
    int err=esp_codec_dev_open(speaker,&format);
    if (!err) err=esp_codec_dev_set_out_vol(speaker,volume);
    if (err) { printf("ERR codec open/volume %d\n",err); esp_codec_dev_delete(speaker); speaker=NULL; return false; }
    return true;
}

static bool play_note(float hz,int ms)
{
    if (!audio_init()) return false;
    int16_t samples[256*2];
    int total=48*ms;
    for (int offset=0;offset<total;offset+=256) {
        int count=total-offset; if(count>256)count=256;
        for(int i=0;i<count;i++) {
            int n=offset+i;
            /* Five millisecond envelopes avoid discontinuities between notes. */
            float envelope=fminf(1.0f,fminf(n/240.0f,(total-1-n)/240.0f));
            int16_t value=(int16_t)(5000*envelope*sinf(2*PI_F*hz*n/48000.0f));
            samples[i*2]=samples[i*2+1]=value;
        }
        int err=esp_codec_dev_write(speaker,samples,count*4);
        if(err) { printf("ERR audio write %d\n",err); return false; }
    }
    memset(samples,0,sizeof(samples));
    return esp_codec_dev_write(speaker,samples,sizeof(samples))==0;
}

static void help(void)
{
    puts("Commands: help | info | demo orbit|bounce|bars|widgets | pause | resume");
    puts("          tone [50..4000 Hz] [1..10 seconds] | melody | volume 0..90 | sd ls");
    puts("          net start | sd mount (diagnostic deferred peripheral startup)");
    puts("          video | video raw (direct bars) | video pattern (DSI bars) | video ui");
    puts("Audio: analog headset jack, volume adjustable (default 65), finite playback; silent at boot.");
    printf("HDMI: native %dx%d RGB888; see boot clock/timing record.\n",width,height);
    puts("demo widgets starts the LVGL slideshow once; video raw/pattern/ui remain available.");
    puts("bench [5..30 seconds] [draw]: timed stages; draw bypasses presentation and uses fixed-step capacity workload.");
    puts("bench [5..30 seconds] rgb332|rgb888: matched opaque-circle reference, render-only, DMA off.");
    puts("scanout off|on: stops/resumes P4 framebuffer DMA and DSI video; off blanks the monitor.");
}

static void command(char *line)
{
    if(!strncmp(line,"bench",5) && (line[5]==0||line[5]==' ')) {
        int seconds=10;char mode[16]={0},extra;int n=sscanf(line+5,"%d %15s %c",&seconds,mode,&extra);
        if((line[5] && n<1)||n>2||(n==2 && strcmp(mode,"draw") && strcmp(mode,"rgb332") && strcmp(mode,"rgb888"))||seconds<5||seconds>30)puts("ERR bench [5..30 seconds] [draw|rgb332|rgb888]");
        else if(n==2 && (!strcmp(mode,"rgb332")||!strcmp(mode,"rgb888")))benchmark_reference(seconds,!strcmp(mode,"rgb332")?1:3);
        else benchmark(seconds,n==2);
    }
    else if(!strcmp(line,"scanout on")||!strcmp(line,"scanout off"))set_scanout(!strcmp(line+8,"on"));
    else if(!strcmp(line,"video")||!strcmp(line,"video raw")||!strcmp(line,"video ui")||!strcmp(line,"video pattern"))
        video_diagnostic(line[5]?line+6:"");
    else if(!strncmp(line,"volume ",7)) {
        int v;char extra;
        if(sscanf(line+7,"%d %c",&v,&extra)!=1||v<0||v>90)puts("ERR volume 0..90");
        else {volume=v;int err=speaker?esp_codec_dev_set_out_vol(speaker,volume):0;printf("Volume %d: %s\n",volume,err?"ERR":"OK");}
    }
    else if (!strcmp(line,"sd mount")) {
        if (!sd_ready) { esp_err_t e=sd_test_init(); sd_ready=e==ESP_OK;
            printf("SD mount: %s (no write test)\n",esp_err_to_name(e)); }
        else puts("SD already mounted");
    }
    else if (!strcmp(line,"net start")) {
    esp_err_t eth=lan_test_eth_start(&netif);
    printf("Ethernet start: %s\n",esp_err_to_name(eth));
    if(eth==ESP_OK) {
        esp_netif_ip_info_t ip;
        esp_err_t dhcp=lan_test_wait_dhcp(netif,15000,&ip);
        printf("DHCP: %s\n",esp_err_to_name(dhcp));
    } else netif=NULL;
    }
    else if (!strcmp(line,"help")) help();
    else if (!strcmp(line,"info")) {
        esp_netif_ip_info_t ip={0}; if(netif)esp_netif_get_ip_info(netif,&ip);
        printf("P4PC demo %s | IP " IPSTR " | heap %u | SD %s | scene %d\n",
            esp_app_get_description()->version,IP2STR(&ip.ip),
            (unsigned)esp_get_free_heap_size(),sd_ready?"mounted":"absent",scene);
        portENTER_CRITICAL(&metrics_lock);
        unsigned updates=ticks,passes=render_passes,scanouts=scanout_frames;
        uint64_t total=render_us,maximum=render_max_us;
        portEXIT_CRITICAL(&metrics_lock);
        printf("Rendering: %u passes, total %llu us, maximum %llu us | scanout completions %u | scanout %s | %dx%d\n",
               passes,(unsigned long long)total,(unsigned long long)maximum,scanouts,scanout_active?"on":"off",width,height);
        if((title || widgets_active) && bsp_display_lock(1000)) {
            lv_mem_monitor_t memory;
            lv_mem_monitor(&memory);
            printf("LVGL pool: total %u bytes, free %u bytes, largest %u bytes, peak used %u bytes\n",
                   (unsigned)memory.total_size,(unsigned)memory.free_size,
                   (unsigned)memory.free_biggest_size,(unsigned)memory.max_used);
            bsp_display_unlock();
        }
        TaskHandle_t event_task=xTaskGetHandle("sys_evt");
        printf("Uptime %lld ms | animation updates %u (not presented frames) | sys_evt stack free minimum %u bytes\n",
               (long long)(esp_timer_get_time()/1000),updates,
               event_task?(unsigned)uxTaskGetStackHighWaterMark(event_task):0);
    } else if (!strncmp(line,"demo ",5)) {
        if(!strcmp(line+5,"widgets")) {
            if(widgets_active) {puts("ERR widgets already active");return;}
            if(!title || !bsp_display_lock(1000)) {puts("ERR display busy");return;}
            /* Same widgets entry point offered by Olimex's LVGL demo player.
             * Start only after static output review, with no input hardware or
             * audio initialization. Drop playground pointers before deleting
             * their objects; its separate animation task remains idle. */
            paused=true;widgets_active=true;
            title=status=stage=NULL;
            esp_lcd_dpi_panel_set_pattern(playground_panel(),MIPI_DSI_PATTERN_NONE);
            lv_obj_clean(lv_screen_active());
            lv_timer_resume(lv_display_get_refr_timer(lv_display_get_default()));
            lv_demo_widgets();
            lv_demo_widgets_start_slideshow();
            bsp_display_unlock();
            puts("OK LVGL widgets slideshow started");return;
        }
        if (!title) { puts("ERR no display"); return; }
        if(!strcmp(line+5,"orbit"))set_scene(0);
        else if(!strcmp(line+5,"bounce"))set_scene(1);
        else if(!strcmp(line+5,"bars"))set_scene(2);
        else puts("ERR demo orbit|bounce|bars|widgets");
    } else if(!strcmp(line,"pause")||!strcmp(line,"resume")) {
        paused=!strcmp(line,"pause"); /* Atomic: acknowledged state never depends on renderer mutex. */
        puts("OK");
    } else if(!strncmp(line,"tone",4) && (line[4]==0||line[4]==' ')) {
        int hz=440,seconds=3; char extra;
        int n=sscanf(line+4,"%d %d %c",&hz,&seconds,&extra);
        if((line[4] && n<1)||n>2||hz<50||hz>4000||seconds<1||seconds>10) puts("ERR tone [50..4000] [1..10]");
        else { printf("Audio start: %d Hz %d s\n",hz,seconds); puts(play_note(hz,seconds*1000)?"OK tone complete":"ERR tone failed"); }
    } else if(!strcmp(line,"melody")) {
        const float notes[]={261.63f,329.63f,392.0f,523.25f,392.0f,329.63f,293.66f,261.63f};
        bool ok=true; puts("Audio start: C major phrase");
        for(int i=0;i<8&&ok;i++)ok=play_note(notes[i],350);
        puts(ok?"OK melody complete":"ERR melody failed");
    } else if(!strcmp(line,"sd ls")) {
        if(!sd_ready)puts("ERR SD not mounted");
        else {
            DIR *dir=opendir("/sdcard");
            if(!dir) { puts("ERR SD directory"); return; }
            struct dirent *ent; unsigned count=0;
            while((ent=readdir(dir)) && count<128) { printf("%s\n",ent->d_name); count++; }
            closedir(dir); printf("OK SD listing %u entries (limit 128)\n",count);
        }
    } else if(*line) puts("ERR unknown command; type help");
}

void app_main(void)
{
    usb_serial_jtag_driver_config_t usb={.rx_buffer_size=512,.tx_buffer_size=2048};
    ESP_ERROR_CHECK(usb_serial_jtag_driver_install(&usb));
    /* Route stdout through the installed USB driver, not competing FIFO writes.
     * IDF/newlib logging also needs the larger event-task stack in prepare.py. */
    usb_serial_jtag_vfs_use_driver();
    setvbuf(stdout,NULL,_IONBF,0);
    puts("\nP4PC playground starting (experimental)");
    display_init();
    /* P4PC-001 diagnosis: start with display only. Factory video is stable;
     * explicit peripheral commands isolate interference before restoring auto-start. */
    set_scene(2);
    paused=true;
    video_diagnostic("raw");
    if (title && xTaskCreate(animation_task,"demo_anim",4096,NULL,2,NULL)!=pdPASS)
        puts("ERR animation task allocation");
    /* Keep Ethernet alive after startup; no factory LAN teardown or button init. */
    help(); puts("READY"); printf("p4pc> ");
    char line[128]; size_t used=0; bool overflow=false;
    int64_t last=0;
    for(;;) {
        unsigned char c;
        int n=usb_serial_jtag_read_bytes(&c,1,pdMS_TO_TICKS(50));
        if(n>0) {
            if(c=='\r'||c=='\n') {
                if(used||overflow) {
                    puts(""); line[used]=0;
                    if(overflow) puts("ERR line too long"); else command(line);
                    used=0; overflow=false; printf("p4pc> ");
                }
            } else if(c==8||c==127) { if(used) {used--;printf("\b \b");} }
            else if(c>=32&&c<127) {
                if(used<sizeof(line)-1&&!overflow) {line[used++]=c;putchar(c);} else overflow=true;
            }
        }
        if(esp_timer_get_time()-last>1000000) {if(status && !paused)update_status();last=esp_timer_get_time();}
    }
}
