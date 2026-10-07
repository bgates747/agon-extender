"""Stage a standalone experimental project from a pinned clean Olimex checkout.
Never build inside or modify the upstream reference. Run with project Python.
"""
import datetime
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from display_experiment import stage_scanout_override, replace_once

UPSTREAM = '04032d68e5c727870f9d40beb9e37b7ab3a66916'
parser = argparse.ArgumentParser()
parser.add_argument('--upstream', required=True, type=Path)
parser.add_argument('--output', required=True, type=Path)
parser.add_argument('--revision', required=True,
                    help='Author-approved experimental revision, e.g. r06')
parser.add_argument('--resolution', choices=('1280x720','640x480'), default='1280x720')
parser.add_argument('--vga-clock', choices=('pll','apll'), default='pll',
                    help='Native VGA: known PLL path; APLL retains the failed r10 control')
args = parser.parse_args()
import re
if not re.fullmatch(r'r(?:0[1-9]|[1-9][0-9]+)', args.revision):
    parser.error('Revision must follow the project rNN identity policy')
ref = args.upstream.resolve()
if subprocess.check_output(['git','-C',str(ref),'rev-parse','HEAD'],text=True).strip()!=UPSTREAM:
    raise SystemExit('Wrong upstream commit')
if subprocess.check_output(['git','-C',str(ref),'status','--porcelain']):
    raise SystemExit('Upstream checkout is not clean')
out = args.output.resolve()
if out.exists():
    raise SystemExit('Choose a fresh output directory')
base=ref/'SOFTWARE/ESP-IDF/p4_production_test'
shutil.copytree(base,out)
local=Path(__file__).resolve().parent
shutil.copyfile(local/'CMakeLists.txt',out/'CMakeLists.txt')
shutil.copyfile(local/'main/main.c',out/'main/main.c')
for name in ('render_reference.c','render_reference.h'):
    shutil.copyfile(local/'main'/name,out/'main'/name)
shutil.copyfile(local/'main/CMakeLists.txt',out/'main/CMakeLists.txt')
# Remove unused factory test components, including its BOOT pin initializer.
for name in ('pt_display','usb_flash_test','audio_loopback_test'):
    shutil.rmtree(out/'components'/name)
# Use BSP dependency graph only; don't pull USB mass storage for a serial demo.
versions=json.loads((local/'dependency-versions.json').read_text())
manifest_text='dependencies:\n  idf: ">=5.5,<5.6"\n'
for name,version in versions.items():
    manifest_text+=f'  {name}: "=={version}"\n'
(out/'main/idf_component.yml').write_text(manifest_text)
# Task-local diagnostic access to the existing DPI panel. The upstream BSP
# exposes creation but not the handle owned by bsp_display_start(). Keep this
# adapter out of the read-only upstream checkout; remove with this experiment.
bsp=out/'components/esp-bsp/bsp/esp32_p4_function_ev_board/esp32_p4_function_ev_board.c'
with bsp.open('a') as f:
    f.write('\n/* P4PC-001: task-local diagnostic accessor for the active DPI panel. */\n'
            'esp_lcd_panel_handle_t playground_panel(void) { return disp_handles.panel; }\n')
# P4PC-001: accepted WLED timing comparison, source commit
# 4d27fd45946a4cf101f67dda4c827bba9b440bc5, wled00/wled_hdmi.cpp.
# Olimex's 64 MHz request and IDF 5.5.5 clock rounding yield an invalid
# compensated horizontal total. Match P4 and LT8912B to WLED's exact 60 MHz
# divider and 1350x741 totals (59.979 Hz), two 720 Mbps DSI lanes, HS-only.
# Adapt numeric configuration only; keep Olimex drivers and PC wiring.
# This is custom blanking, not universal CEA/monitor qualification. Revisit
# when the project adopts a validated timing contract beyond this experiment.
text=bsp.read_text()
needle='vendor_config.mipi_config.dpi_config = &dpi_configs[2];'
if text.count(needle)!=1:
    raise SystemExit('Unexpected upstream 720p DPI configuration')
text=text.replace(needle,
    '/* P4PC-001: WLED matched 59.979 Hz timing; see prepare.py. */\n'
    '        dpi_configs[2].dpi_clock_freq_mhz = 60;\n'
    '        dpi_configs[2].num_fbs = 2; /* r08: direct double buffering */\n'
    '        dpi_configs[2].video_timing.hsync_front_porch = 10;\n'
    '        dpi_configs[2].video_timing.hsync_back_porch = 28;\n'
    '        dpi_configs[2].out_color_format = LCD_COLOR_FMT_RGB888;\n'
    '        dpi_configs[2].flags.disable_lp = true;\n'
    '        ESP_LOGI(TAG, "Experimental HDMI: 60 MHz, 1350x741 total, 59.979 Hz calculated");\n'
    '        '+needle)
needle='memcpy(&vendor_config.video_timing, &video_timings[2], sizeof(esp_lcd_panel_lt8912b_video_timing_t));'
if text.count(needle)!=1:raise SystemExit('Unexpected upstream bridge timing')
text=text.replace(needle,needle+'\n'
    '        vendor_config.video_timing.hfp = 10;\n'
    '        vendor_config.video_timing.hbp = 28;\n'
    '        vendor_config.video_timing.htotal = 1350;\n'
    '        vendor_config.video_timing.pclk_mhz = 60;\n'
    '        vendor_config.video_timing.vic = 4;\n')
needle='.lane_bit_rate_mbps = config->dsi_bus.lane_bit_rate_mbps,'
if text.count(needle)!=1:raise SystemExit('Unexpected upstream DSI bus configuration')
text=text.replace(needle,'/* P4PC-001: 60 MHz RGB888 / two lanes = 720 Mbps per lane. */\n'
    '        .lane_bit_rate_mbps = 720,')
# P4PC-001 r08: replace the inherited small partial buffer/copy path with
# direct dirty-area rendering into two panel-owned framebuffers. The existing
# port waits on its refresh completion semaphore before reusing a buffer.
# HDMI Kconfig hides these LCD options, so select them explicitly here.
# Retain r06/r07 as controls; this changes rendering, not the accepted timings.
render_flags='''#if CONFIG_BSP_DISPLAY_LVGL_FULL_REFRESH
            .full_refresh = true,
#elif CONFIG_BSP_DISPLAY_LVGL_DIRECT_MODE
            .direct_mode = true,
#endif'''
if text.count(render_flags)!=1:raise SystemExit('Unexpected render mode block')
text=text.replace(render_flags,'/* P4PC-001 r08: dirty areas, direct double buffering. */\n'
    '            .direct_mode = true,')
for before,after in [('.buffer_size = cfg->buffer_size,','.buffer_size = display_hres * display_vres,'),
                     ('.double_buffer = cfg->double_buffer,','.double_buffer = true,'),
                     ('.sw_rotate = cfg->flags.sw_rotate,','.sw_rotate = false,'),
                     ('.avoid_tearing = false,','.avoid_tearing = true,')]:
    if text.count(before)!=1:raise SystemExit('Unexpected display buffer configuration')
    text=text.replace(before,after)
bsp.write_text(text)
# Native VGA experiment: the copied BSP's selected HDMI slot is deliberately
# repurposed, including the LVGL geometry (not a 640x480 window in a 720p buffer).
# IDF 5.5.5 supports APLL as a DPI clock source on this v1.3 P4. Hold an APLL
# reference for the lifetime of this standalone display; peripherals stay idle.
if args.resolution == '640x480':
    text=replace_once(text,'#include "bsp/esp32_p4_function_ev_board.h"',
                     '#include "bsp/esp32_p4_function_ev_board.h"\n#include "clk_ctrl_os.h"')
    text=replace_once(text,'dpi_configs[2].dpi_clock_freq_mhz = 60;',
        'periph_rtc_apll_acquire();\n'
        '        uint32_t actual_apll_hz = 0;\n'
        '        ESP_ERROR_CHECK(periph_rtc_apll_freq_set(25200000, &actual_apll_hz));\n'
        '        ESP_LOGI(TAG, "VGA APLL actual %lu Hz", (unsigned long)actual_apll_hz);\n'
        '        dpi_configs[2].dpi_clk_src = MIPI_DSI_DPI_CLK_SRC_APLL;\n'
        '        dpi_configs[2].dpi_clock_freq_mhz = 25.2;\n'
        '        dpi_configs[2].video_timing.h_size = 640;\n'
        '        dpi_configs[2].video_timing.v_size = 480;\n'
        '        dpi_configs[2].video_timing.hsync_pulse_width = 96;\n'
        '        dpi_configs[2].video_timing.vsync_front_porch = 10;\n'
        '        dpi_configs[2].video_timing.vsync_pulse_width = 2;\n'
        '        dpi_configs[2].video_timing.vsync_back_porch = 33;')
    text=replace_once(text,'dpi_configs[2].video_timing.hsync_front_porch = 10;',
                          'dpi_configs[2].video_timing.hsync_front_porch = 16;')
    text=replace_once(text,'dpi_configs[2].video_timing.hsync_back_porch = 28;',
                          'dpi_configs[2].video_timing.hsync_back_porch = 48;')
    text=replace_once(text,'Experimental HDMI: 60 MHz, 1350x741 total, 59.979 Hz calculated',
                          'Experimental HDMI: 640x480, 25.2 MHz APLL, 800x525 total, 60 Hz calculated')
    text=text.replace('HDMI configuration for 1280x720@60HZ','HDMI configuration for native 640x480 experiment')
    text=replace_once(text,'display_hres = 1280;\n        display_vres = 720;',
                          '/* P4PC-001: selected slot carries native VGA. */\n'
                          '        display_hres = 640;\n        display_vres = 480;')
    start=text.index('        vendor_config.video_timing.hfp = 10;')
    end=text.index('\n        break;',start)
    text=text[:start]+'''        vendor_config.video_timing = (esp_lcd_panel_lt8912b_video_timing_t){
            .hact=640, .hfp=16, .hs=96, .hbp=48, .htotal=800,
            .vact=480, .vfp=10, .vs=2, .vbp=33, .vtotal=525,
            .h_polarity=false, .v_polarity=false, .vic=1, .aspect_ratio=1,
            .pclk_mhz=25, /* Integer field is used only by disabled bridge test pattern. */
        };'''+text[end:]
    if args.vga_clock=='pll':
        start=text.index('periph_rtc_apll_acquire();')
        end=text.index('        dpi_configs[2].video_timing.h_size = 640;',start)
        text=text[:start]+'''/* P4PC-001: r10 APLL had no DMA completions. Keep the
         * proven 240 MHz source / 8, with matched RGB888 lane rate and
         * custom near-60 Hz blanking. r11 had DMA but no usable HDMI picture.
         * This is a diagnostic monitor mode, not universal VGA qualification. */
        dpi_configs[2].dpi_clk_src = MIPI_DSI_DPI_CLK_SRC_PLL_F240M;
        dpi_configs[2].dpi_clock_freq_mhz = 30;
'''+text[end:]
        text=replace_once(text,'dpi_configs[2].video_timing.hsync_front_porch = 16;',
                              'dpi_configs[2].video_timing.hsync_front_porch = 168;')
        text=replace_once(text,'.hact=640, .hfp=16, .hs=96, .hbp=48, .htotal=800,',
                              '.hact=640, .hfp=168, .hs=96, .hbp=48, .htotal=952,')
        text=replace_once(text,'640x480, 25.2 MHz APLL, 800x525 total, 60 Hz calculated',
                              '640x480, 30 MHz PLL, 952x525 total, 60.0240 Hz calculated')
        text=replace_once(text,'.lane_bit_rate_mbps = 720,','.lane_bit_rate_mbps = 360,')
        text=replace_once(text,'.pclk_mhz=25,','.pclk_mhz=30,')
    bsp.write_text(text)
# P4PC-001: bounded LT8912B low-resolution experiment. Linux's bridge driver
# uses receiver settle=0x04 for <=600 active lines. Olimex's pinned driver uses
# fixed 0x10. Retain notices; change only the generated native-VGA candidate.
# https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/bridge/lontium-lt8912b.c
lt=out/'components/esp-bsp/components/lcd/esp_lcd_lt8912b/esp_lcd_lt8912b.c'
text=lt.read_text()
if args.resolution=='640x480':
    text=replace_once(text,'_panel_lt8912b_send_data(io_cec, 0x11, 0x10)',
        '_panel_lt8912b_send_data(io_cec, 0x11, 0x04) /* P4PC-001 low-resolution RX settling control */')
# Original init resets RX/DDS before base DPI init starts the stream. Expose a
# task-local retry with live input, also after diagnostic stop/resume. This is
# an unproven remedy; remove on completion of bounded bridge qualification.
text+=""+"""esp_err_t playground_bridge_relock(esp_lcd_panel_t *panel)
{
    lt8912b_panel_t *bridge = (lt8912b_panel_t *)panel->user_data;
    ESP_RETURN_ON_ERROR(_panel_lt8912b_send_video_setup(panel), TAG, "relock timing failed");
    ESP_RETURN_ON_ERROR(_panel_lt8912b_mipi_rx_logic_reset(bridge->io.main), TAG, "relock reset failed");
    vTaskDelay(pdMS_TO_TICKS(50));
    return _panel_lt8912b_detect_input_mipi(panel);
}
"""
lt.write_text(text)
# Own the diagnostic override in the generated project; pin and preserve its
# provenance. The native SDK reference remains unmodified.
idf=local.parents[1]/'agents/build001/native-tools/esp-idf'
if subprocess.check_output(['git','-C',str(idf),'rev-parse','HEAD'],text=True).strip()!='b774170ff46c393eeb5e495ea37936038d3f4f4f':
    raise SystemExit('Wrong SDK for scanout override')
stage_scanout_override(out,idf)
# Count panel frame completions through the existing port callback. Preserve
# its semaphore and return value; this ISR hook does no logging or allocation.
port=out/'components/esp-bsp/components/esp_lvgl_port/src/lvgl9/esp_lvgl_port_disp.c'
text=port.read_text()
needle='''static bool lvgl_port_flush_dpi_vsync_ready_callback(esp_lcd_panel_handle_t panel_io, esp_lcd_dpi_panel_event_data_t *edata, void *user_ctx)
{
    BaseType_t need_yield = pdFALSE;'''
if text.count(needle)!=1:raise SystemExit('Unexpected frame completion callback')
text=text.replace(needle,needle+'\n    /* P4PC-001 r08: count scanout independently of LVGL rendering. */\n'
    '    extern void playground_scanout_event(void);\n    playground_scanout_event();')
port.write_text(text)
# Time the existing port's blocking frame wait without changing its semantics.
text=replace_once(text,'#include "esp_log.h"','#include "esp_log.h"\n#include "esp_timer.h"')
text=replace_once(text,'            xSemaphoreTake(disp_ctx->trans_sem, 0);\n            xSemaphoreTake(disp_ctx->trans_sem, portMAX_DELAY);',
    '            int64_t wait_started = esp_timer_get_time();\n'
    '            xSemaphoreTake(disp_ctx->trans_sem, 0);\n'
    '            xSemaphoreTake(disp_ctx->trans_sem, portMAX_DELAY);\n'
    '            extern void playground_wait_event(uint64_t elapsed);\n'
    '            playground_wait_event(esp_timer_get_time() - wait_started);')
port.write_text(text)
config=(out/'sdkconfig').read_text()
changes={
 'CONFIG_ESP_CONSOLE_UART_DEFAULT':None,
 'CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG':'y',
 'CONFIG_ESP_CONSOLE_SECONDARY_USB_SERIAL_JTAG':None,
 'CONFIG_ESP_CONSOLE_SECONDARY_NONE':'y',
 'CONFIG_BSP_SD_FORMAT_ON_MOUNT_FAIL':None,
 'CONFIG_LV_FONT_MONTSERRAT_24':'y',
 'CONFIG_LV_USE_DEMO_WIDGETS':'y',
 'CONFIG_LV_MEM_SIZE':'1048576',
 'CONFIG_LV_MEM_SIZE_KILOBYTES':'0',
 'CONFIG_LV_DEF_REFR_PERIOD':'16',
 # Native IDF 5.5.5/newlib logging overflowed sys_evt's inherited 2304 bytes.
 # Retain 8192 until measured stack headroom supports a smaller allocation.
 'CONFIG_ESP_SYSTEM_EVENT_TASK_STACK_SIZE':'8192',
}
lines=[]
for line in config.splitlines():
    key=line.split('=',1)[0] if line.startswith('CONFIG_') else line[2:].split(' ',1)[0] if line.startswith('# CONFIG_') else ''
    if key not in changes: lines.append(line)
for key,val in changes.items():lines.append(f'{key}={val}' if val else f'# {key} is not set')
(out/'sdkconfig').write_text('\n'.join(lines)+'\n')
manifest={'upstream_commit':UPSTREAM,'status':'experimental','sources':{}}
manifest['display_timing']={'donor_commit':'4d27fd45946a4cf101f67dda4c827bba9b440bc5',
    'pixel_clock_mhz':60,'lane_mbps':720,'h_total':1350,'v_total':741,
    'calculated_hz':60000000/(1350*741),'physical_validation':'pending'}
manifest['rendering']={'mode':'direct','panel_framebuffers':2,'lvgl_pool_bytes':1048576,
    'pool_allocation':'malloc with fixed PSRAM policy','animation_interval_ms':16,
    'refresh_interval_ms':16,'physical_performance':'pending'}
if args.resolution=='640x480':
    manifest['display_timing']={'pixel_clock_mhz':25.2,'clock_source':'APLL','lane_mbps':720,
        'active_width':640,'active_height':480,'h_total':800,'v_total':525,
        'calculated_hz':60,'physical_validation':'pending'}
    if args.vga_clock=='pll':
        manifest['display_timing'].update(pixel_clock_mhz=30,clock_source='PLL_F240M',lane_mbps=360,
            h_total=952,calculated_hz=30000000/(952*525),
            timing_note='custom blanking, physical monitor validation required')
manifest['scanout_control']={'idf_commit':'b774170ff46c393eeb5e495ea37936038d3f4f4f',
    'method':'stop DMA rearm at frame completion and disable DSI video/DPI output',
    'component':'project/components/esp_lcd'}
for name in ('main/main.c','main/render_reference.c','main/render_reference.h','main/CMakeLists.txt','CMakeLists.txt','prepare.py','display_experiment.py','dependency-versions.json'):
    manifest['sources'][name]=hashlib.sha256((local/name).read_bytes()).hexdigest()
for name in ('components/esp-bsp/components/lcd/esp_lcd_lt8912b/esp_lcd_lt8912b.c',
             'components/esp_lcd/dsi/esp_lcd_panel_dpi.c',
             'components/esp_lcd/CMakeLists.txt',
             'components/esp-bsp/components/esp_lvgl_port/src/lvgl9/esp_lvgl_port_disp.c',
             'components/esp-bsp/bsp/esp32_p4_function_ev_board/esp32_p4_function_ev_board.c'):
    manifest['sources'][name]=hashlib.sha256((out/name).read_bytes()).hexdigest()
build_id='p4pc-playground-'+args.revision+'-b'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
(out/'version.txt').write_text(build_id.removeprefix('p4pc-playground-')+'\n')
manifest['build_id']=build_id
(out/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(out)
