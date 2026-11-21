"""Generate the native-row P4 DPI derivative against the reviewed IDF 5.5.5 blob.

The panel owns one list of physical RGB888 block descriptors and three internal
DMA slots. It exposes no writable display framebuffer. Keep the ordinary DSI
bus, LT8912B, full-frame event and positively drained channel teardown.
"""
import hashlib
from pathlib import Path
import sys


def derive(data):
    if hashlib.sha256(data).hexdigest() != "a0b13536fec34d3cc4a6324ab64bc9bb62fee4db39dec24133681bc3c17b8373":
        raise ValueError("unreviewed DPI driver")
    source = data.decode()

    def replace(old, new):
        nonlocal source
        if source.count(old) != 1:
            raise ValueError(f"unexpected DPI anchor {old[:100]!r}")
        source = source.replace(old, new)

    def section(start, end, new):
        first = source.index(start)
        last = source.index(end, first + len(start))
        replace(source[first:last], new)

    replace('#include "hal/color_hal.h"', '#include "hal/color_hal.h"\n#include "native_state.h"')
    replace('    uint8_t virtual_channel;', '    native_state native;\n    uint8_t virtual_channel;')
    replace('IRAM_ATTR\nstatic bool async_fbcpy_done_cb', '#include "native_runtime.inc"\n\nIRAM_ATTR\nstatic bool async_fbcpy_done_cb')
    replace('    uint8_t *fbs[DPI_PANEL_MAX_FB_NUM]; // Frame buffers\n', '')
    section('    esp_async_fbcpy_handle_t fbcpy_handle;', '    esp_pm_lock_handle_t pm_lock;', '')
    section('    if (dpi_panel->fbcpy_handle) {', '    if (dpi_panel->brg_intr) {', '')
    section('IRAM_ATTR\nstatic bool async_fbcpy_done_cb(', 'bool mipi_dsi_dma_trans_done_cb(', '')
    replace('    esp_async_fbcpy_handle_t fbcpy_ctx = NULL;\n', '')
    section('#if SOC_DMA2D_SUPPORTED\n    if (panel_config->flags.use_dma2d)', '    // if the clock source', '')
    section('    uint8_t fb_index = dpi_panel->cur_fb_index;', '    dw_gdma_channel_use_link_list(chan, link_list);',
            '''    if (!native_frame(dpi_panel)) return false;
    dw_gdma_link_list_handle_t link_list = dpi_panel->link_lists[0];
''')
    replace('''    if (intr_status & MIPI_DSI_BRG_LL_EVENT_UNDERRUN) {''',
            '''    if (intr_status & MIPI_DSI_BRG_LL_EVENT_UNDERRUN) {
        native_underrun(dpi_panel);''')
    replace('''        .num_items = DPI_PANEL_MIN_DMA_NODES_PER_LINK,''',
            '''        .num_items = dpi_panel->native.ring.count,''')
    replace('''    mipi_dsi_brg_ll_set_multi_block_number(hal->bridge, DPI_PANEL_MIN_DMA_NODES_PER_LINK);''',
            '''    mipi_dsi_brg_ll_set_multi_block_number(hal->bridge, dpi_panel->native.ring.count);''')
    replace('''        .on_full_trans_done = mipi_dsi_dma_trans_done_cb,''',
            '''        .on_full_trans_done = mipi_dsi_dma_trans_done_cb,
        .on_block_trans_done = native_block_done,
        .on_invalid_block = native_invalid,''')
    section('    size_t num_fbs = panel_config->num_fbs;', '    // by default, use RGB888',
            '''    ESP_RETURN_ON_FALSE(panel_config->num_fbs <= 1 && !panel_config->flags.use_dma2d,
                        ESP_ERR_INVALID_ARG, TAG, "native rows own the scanout DMA");
    // num_fbs names descriptor-list count in this derivative. No full frames are allocated.
    const size_t num_fbs = 1;

''')
    section('    // allocate frame buffer from PSRAM','    dpi_panel->bits_per_pixel = bits_per_pixel;',
            '''    dpi_panel->fb_size = panel_config->video_timing.h_size *
                         panel_config->video_timing.v_size * bits_per_pixel / 8;
''')
    replace('    dpi_panel->v_pixels = panel_config->video_timing.v_size;', '''    dpi_panel->v_pixels = panel_config->video_timing.v_size;
    ESP_GOTO_ON_FALSE(bits_per_pixel == 24 &&
                      ((dpi_panel->h_pixels == 684 && dpi_panel->v_pixels == 384) ||
                       (dpi_panel->h_pixels == 848 && dpi_panel->v_pixels == 480)),
                      ESP_ERR_NOT_SUPPORTED, err, TAG, "unsupported native row carrier");
    ESP_GOTO_ON_ERROR(native_allocate(dpi_panel),err,TAG,"native slot allocation");''')
    replace('    // disable the DPI clock','''    ESP_RETURN_ON_ERROR(agon_dpi_stop(panel),TAG,"native shutdown");
    // disable the DPI clock''')
    section('    for (int i = 0; i < DPI_PANEL_MAX_FB_NUM; i++) {\n        if (dpi_panel->fbs[i])', '    for (int i = 0; i < DPI_PANEL_MAX_FB_NUM; i++) {\n        if (dpi_panel->link_lists[i])', '''    native_free(dpi_panel);
''')
    section('    ESP_RETURN_ON_FALSE(panel, ESP_ERR_INVALID_ARG, TAG, "invalid argument");\n    esp_lcd_dpi_panel_t *dpi_panel', 'static esp_err_t dpi_panel_init(esp_lcd_panel_t *panel)\n{', '''    return ESP_ERR_NOT_SUPPORTED; // DMA slots have no application framebuffer contract
}

''')
    replace('        .size = dpi_panel->fb_size * 8 / 64,', '        .size = dpi_panel->h_pixels * NR_ROWS * 3 / 8,')
    section('    for (int i = 0; i < dpi_panel->num_fbs; i++) {\n        link_list = dpi_panel->link_lists[i];','    // by default, we use the fb0',
            '''    link_list = dpi_panel->link_lists[0];
    for (unsigned b = 0; b < dpi_panel->native.ring.count; ++b) {
        dma_transfer_config.src.addr = (uint32_t)dpi_panel->native.pixels[b % NR_SLOTS];
        dw_gdma_lli_config_transfer(dw_gdma_link_list_get_item(link_list,b),&dma_transfer_config);
        nr_mark(dpi_panel,b,b < NR_SLOTS);
    }

''')
    replace('    dw_gdma_channel_enable_ctrl(dma_chan, true);', '''    portENTER_CRITICAL(&nr_mux);
    dpi_panel->native.phase = NR_RUNNING;
    for (unsigned i = 0; i < NR_SLOTS; ++i) dpi_panel->native.ready_at[i] = esp_timer_get_time();
    portEXIT_CRITICAL(&nr_mux);
    dw_gdma_channel_enable_ctrl(dma_chan, true);''')
    sig = 'static esp_err_t dpi_panel_draw_bitmap(esp_lcd_panel_t *panel, int x_start, int y_start, int x_end, int y_end, const void *color_data)\n{'
    start = source.index(sig)
    end = source.index('\n}', start)
    replace(source[start:end], sig + '\n    return ESP_ERR_NOT_SUPPORTED; // Direct native row producer is the pixel owner.')
    return source


if __name__ == "__main__":
    original, target = map(Path, sys.argv[1:])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(derive(original.read_bytes()))
