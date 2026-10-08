#!/usr/bin/env python3
"""SPRITE-001: generate an isolated derivative; never modify the pinned SDK."""
import hashlib
import sys
from pathlib import Path
source, target = map(Path, sys.argv[1:])
s = source.read_text()
assert hashlib.sha256(source.read_bytes()).hexdigest() == 'a0b13536fec34d3cc4a6324ab64bc9bb62fee4db39dec24133681bc3c17b8373'
def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:100], s.count(old))
    s = s.replace(old, new)
replace('#include "hal/color_hal.h"', '#include "hal/color_hal.h"\n#include "strip_runtime.inc"')
# HDMI02-F: both proven carriers use fixed32-row strips, with12/15 blocks.
s=s.replace('DPI_PANEL_MIN_DMA_NODES_PER_LINK','(STRIP_ACTIVE(dpi_panel) ? STRIP_COUNT(dpi_panel) : 1)')
s=s.replace('#include "strip_runtime.inc"', '#include "strip_runtime.inc"\n#ifdef AGON_EXTENDER_HDMI_AUTO\n#define STRIP_ACTIVE(p) (((p)->h_pixels == 684 && (p)->v_pixels == 384) || ((p)->h_pixels == 848 && (p)->v_pixels == 480))\n#else\n#define STRIP_ACTIVE(p) 1\n#endif\n#define STRIP_COUNT(p) ((p)->v_pixels / STRIP_ROWS)')
replace('''    dw_gdma_block_markers_t markers = {
        .is_valid = true,
        .is_last = true,
    };
    dw_gdma_lli_set_block_markers(dw_gdma_link_list_get_item(link_list, 0), markers);''', '''    if (STRIP_ACTIVE(dpi_panel)) {
    if (atomic_load(&strip_faults)) { dw_gdma_channel_enable_ctrl(chan, false); return false; }
    strip_front_index = strip_scene.background;
    if (strip_ordinal != STRIP_COUNT(dpi_panel)) {
        atomic_fetch_add(&strip_sequence_errors, 1);
        strip_abort(STRIP_FAULT_SEQUENCE, strip_ordinal);
        return false; // lost/coalesced block events cannot safely advance slot ownership
    }
    strip_ordinal = 0;
    atomic_fetch_add(&strip_frames_done, 1);
    for (unsigned n = 0; n < STRIP_COUNT(dpi_panel); ++n) {
        dw_gdma_block_markers_t markers = {
            .is_valid = true, .is_last = n == STRIP_COUNT(dpi_panel) - 1,
            .en_trans_done_intr = true,
        };
        dw_gdma_lli_set_block_markers(dw_gdma_link_list_get_item(link_list, n), markers);
    }
    } else {
    dw_gdma_block_markers_t markers = {
        .is_valid = true,
        .is_last = true,
    };
    dw_gdma_lli_set_block_markers(dw_gdma_link_list_get_item(link_list, 0), markers);
    }''')
replace('    dw_gdma_channel_enable_ctrl(chan, true);\n\n    if (dpi_panel->on_frame_buf_complete)', '    dw_gdma_channel_enable_ctrl(chan, true);\n    if (STRIP_ACTIVE(dpi_panel) && strip_last_pending) {\n        strip_last_pending = false;\n        strip_fill(STRIP_SLOTS - 1, STRIP_SLOTS - 1, atomic_load(&strip_frames_done));\n    }\n\n    if (dpi_panel->on_frame_buf_complete)')
replace('''    if (intr_status & MIPI_DSI_BRG_LL_EVENT_UNDERRUN) {''', '''    if (intr_status & MIPI_DSI_BRG_LL_EVENT_UNDERRUN) {
        strip_note_underrun();''')
replace('''        .on_full_trans_done = mipi_dsi_dma_trans_done_cb,''','''        .on_full_trans_done = mipi_dsi_dma_trans_done_cb,
        .on_block_trans_done = STRIP_ACTIVE(dpi_panel) ? strip_block_done : NULL,
        .on_invalid_block = STRIP_ACTIVE(dpi_panel) ? strip_invalid_block : NULL,''')
replace('''    dw_gdma_block_transfer_config_t dma_transfer_config = {''', '''#ifdef AGON_EXTENDER_HDMI_AUTO
    ESP_RETURN_ON_ERROR(strip_reserve(), TAG, "persistent strip reserve failed");
#endif
    if (STRIP_ACTIVE(dpi_panel)) {
        ESP_RETURN_ON_ERROR(strip_configure(dpi_panel->fbs[0],dpi_panel->fbs[1], dpi_panel->fb_size, dpi_panel->h_pixels, dpi_panel->v_pixels), TAG, "strip allocation failed");
        ESP_RETURN_ON_ERROR(strip_prime_and_check(), TAG, "strip DMA2D preflight failed");
    }
    dw_gdma_block_transfer_config_t dma_transfer_config = {''')
replace('''        .size = dpi_panel->fb_size * 8 / 64,''','''        .size = dpi_panel->fb_size / (STRIP_ACTIVE(dpi_panel) ? STRIP_COUNT(dpi_panel) : 1) / 8,''')
replace('''        dma_transfer_config.src.addr = (uint32_t)(dpi_panel->fbs[i]);
        dw_gdma_lli_config_transfer(dw_gdma_link_list_get_item(link_list, 0), &dma_transfer_config);
        dw_gdma_block_markers_t markers = {
            .is_valid = true,
            .is_last = true,
        };
        dw_gdma_lli_set_block_markers(dw_gdma_link_list_get_item(link_list, 0), markers);''','''        if (STRIP_ACTIVE(dpi_panel)) {
        assert(dpi_panel->fb_size % (STRIP_COUNT(dpi_panel) * 64) == 0);
        for (unsigned n = 0; n < STRIP_COUNT(dpi_panel); ++n) {
            dma_transfer_config.src.addr = strip_address(n, dpi_panel->fbs[i]);
            dw_gdma_lli_config_transfer(dw_gdma_link_list_get_item(link_list, n), &dma_transfer_config);
            dw_gdma_block_markers_t markers = {
                .is_valid = true, .is_last = n == STRIP_COUNT(dpi_panel) - 1,
                .en_trans_done_intr = true,
            };
            dw_gdma_lli_set_block_markers(dw_gdma_link_list_get_item(link_list, n), markers);
        }
        } else {
        dma_transfer_config.src.addr = (uint32_t)(dpi_panel->fbs[i]);
        dw_gdma_lli_config_transfer(dw_gdma_link_list_get_item(link_list, 0), &dma_transfer_config);
        dw_gdma_block_markers_t markers = {
            .is_valid = true,
            .is_last = true,
        };
        dw_gdma_lli_set_block_markers(dw_gdma_link_list_get_item(link_list, 0), markers);
        }''')
# IDF's channel deletion releases handles/IRQ; explicitly stop the channel
# first. Prevent its completion callback from rearming while deletion starts.
replace('    uint8_t fb_index = dpi_panel->cur_fb_index;', '    if (atomic_load(&strip_stopping)) { dw_gdma_channel_enable_ctrl(chan, false); return false; }\n    uint8_t fb_index = dpi_panel->cur_fb_index;')
replace('static esp_err_t dpi_panel_init(esp_lcd_panel_t *panel)\n{', 'static esp_err_t dpi_panel_init(esp_lcd_panel_t *panel)\n{\n    atomic_store(&strip_stopping, false);')
replace('static esp_err_t dpi_panel_del(esp_lcd_panel_t *panel)\n{', 'static esp_err_t dpi_panel_del(esp_lcd_panel_t *panel)\n{\n    strip_stop();')
# DSI channel deletion joins its callbacks; then join DMA2D before freeing
# either source framebuffers or destination SRAM. Applies also to failed init.
replace('''        dw_gdma_del_channel(dpi_panel->dma_chan);
    }
    for (int i = 0; i < DPI_PANEL_MAX_FB_NUM; i++) {''', '''        dw_gdma_channel_enable_ctrl(dpi_panel->dma_chan, false);
        dw_gdma_del_channel(dpi_panel->dma_chan);
    }
    if (STRIP_ACTIVE(dpi_panel)) ESP_ERROR_CHECK(strip_shutdown());
    for (int i = 0; i < DPI_PANEL_MAX_FB_NUM; i++) {''')
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(s)
