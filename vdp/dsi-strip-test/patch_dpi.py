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
s=s.replace('DPI_PANEL_MIN_DMA_NODES_PER_LINK','STRIP_BLOCKS')
replace('''    dw_gdma_block_markers_t markers = {
        .is_valid = true,
        .is_last = true,
    };
    dw_gdma_lli_set_block_markers(dw_gdma_link_list_get_item(link_list, 0), markers);''', '''    if (atomic_load(&strip_faults)) { dw_gdma_channel_enable_ctrl(chan, false); return false; }
    if (strip_ordinal != STRIP_BLOCKS) atomic_fetch_add(&strip_sequence_errors, 1);
    strip_ordinal = 0;
    atomic_fetch_add(&strip_frames_done, 1);
    for (unsigned n = 0; n < STRIP_BLOCKS; ++n) {
        dw_gdma_block_markers_t markers = {
            .is_valid = true, .is_last = n == STRIP_BLOCKS - 1,
            .en_trans_done_intr = true,
        };
        dw_gdma_lli_set_block_markers(dw_gdma_link_list_get_item(link_list, n), markers);
    }''')
replace('    dw_gdma_channel_enable_ctrl(chan, true);\n\n    if (dpi_panel->on_frame_buf_complete)', '    dw_gdma_channel_enable_ctrl(chan, true);\n    if (strip_last_pending) {\n        strip_last_pending = false;\n        strip_fill(STRIP_SLOTS - 1, STRIP_SLOTS - 1, atomic_load(&strip_frames_done));\n    }\n\n    if (dpi_panel->on_frame_buf_complete)')
replace('''    if (intr_status & MIPI_DSI_BRG_LL_EVENT_UNDERRUN) {''', '''    if (intr_status & MIPI_DSI_BRG_LL_EVENT_UNDERRUN) {
        atomic_fetch_add(&strip_underruns, 1);''')
replace('''        .on_full_trans_done = mipi_dsi_dma_trans_done_cb,''','''        .on_full_trans_done = mipi_dsi_dma_trans_done_cb,
        .on_block_trans_done = strip_block_done,
        .on_invalid_block = strip_invalid_block,''')
replace('''    dw_gdma_block_transfer_config_t dma_transfer_config = {''', '''    strip_configure(dpi_panel->fbs[0], dpi_panel->fb_size);
    ESP_RETURN_ON_ERROR(strip_prime_and_check(), TAG, "strip DMA2D preflight failed");
    dw_gdma_block_transfer_config_t dma_transfer_config = {''')
replace('''        .size = dpi_panel->fb_size * 8 / 64,''','''        .size = dpi_panel->fb_size / STRIP_BLOCKS / 8,''')
replace('''        dma_transfer_config.src.addr = (uint32_t)(dpi_panel->fbs[i]);
        dw_gdma_lli_config_transfer(dw_gdma_link_list_get_item(link_list, 0), &dma_transfer_config);
        dw_gdma_block_markers_t markers = {
            .is_valid = true,
            .is_last = true,
        };
        dw_gdma_lli_set_block_markers(dw_gdma_link_list_get_item(link_list, 0), markers);''','''        assert(dpi_panel->fb_size % (STRIP_BLOCKS * 64) == 0);
        for (unsigned n = 0; n < STRIP_BLOCKS; ++n) {
            dma_transfer_config.src.addr = strip_address(n, dpi_panel->fbs[i]);
            dw_gdma_lli_config_transfer(dw_gdma_link_list_get_item(link_list, n), &dma_transfer_config);
            dw_gdma_block_markers_t markers = {
                .is_valid = true, .is_last = n == STRIP_BLOCKS - 1,
                .en_trans_done_intr = true,
            };
            dw_gdma_lli_set_block_markers(dw_gdma_link_list_get_item(link_list, n), markers);
        }''')
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(s)
