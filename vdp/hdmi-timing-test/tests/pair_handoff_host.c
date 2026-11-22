/* Host surrogate for the pinned peripheral registers, not a simulation of
 * bridge-controlled flow or its timing. Compile through verify_pair_handoff.py. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>
#include "pair_pattern.h"

typedef union { uint32_t val; struct { uint32_t cmpltd_blk_tfr_size:22; }; } reg_t;
typedef struct { reg_t ctrl_hi, status_hi, status_lo, block_ts_lo; } dw_gdma_link_list_item_t;
typedef dw_gdma_link_list_item_t *dw_gdma_link_list_handle_t;
typedef void *dw_gdma_channel_handle_t;
typedef void dw_gdma_trans_done_event_data_t;
typedef void dw_gdma_break_event_data_t;
typedef struct { reg_t chen0; } dw_gdma_dev_t;
typedef struct {
    reg_t dma_req_cfg, dma_flow_ctrl, raw_buf_credit_ctl, blk_raw_num_cfg;
    reg_t dma_frame_interval, dma_block_interval;
} dsi_brg_dev_t;
typedef struct { struct { dsi_brg_dev_t *bridge; } hal; } fake_bus;
typedef struct {
    fake_bus *bus;
    dw_gdma_channel_handle_t dma_chan;
    unsigned cur_fb_index;
    dw_gdma_link_list_handle_t link_lists[1];
} esp_lcd_dpi_panel_t;
typedef unsigned portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
#define portENTER_CRITICAL_ISR(x) ((void)(x))
#define portEXIT_CRITICAL_ISR(x) ((void)(x))
#define portENTER_CRITICAL(x) ((void)(x))
#define portEXIT_CRITICAL(x) ((void)(x))
#define DW_GDMA_LL_GET_HW(n) (&fake_gdma)
#define CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ 360
#define ESP_CACHE_MSYNC_FLAG_DIR_C2M 1
#define ESP_OK 0
#define DW_GDMA_ROLE_MEM 0
#define DW_GDMA_ROLE_PERIPH_DSI 1
#define DW_GDMA_FLOW_CTRL_SELF 0
#define MIPI_DSI_BRG_LL_EVENT_UNDERRUN 1
static dw_gdma_dev_t fake_gdma;
static uint32_t cycles;
static bool interrupt_context = true, output_enabled;
static dw_gdma_link_list_handle_t selected;
static unsigned clean_counts[2], restored_flow;
static _Alignas(64) uint8_t storage[2][5120];
static uint32_t esp_cpu_get_cycle_count(void) { return ++cycles; }
static bool xPortInIsrContext(void) { return interrupt_context; }
static void mipi_dsi_brg_ll_enable_dpi_output(dsi_brg_dev_t *brg, bool on)
{ assert(brg); output_enabled = on; }
static void mipi_dsi_brg_ll_update_dpi_config(dsi_brg_dev_t *brg) { assert(brg); }
static void mipi_dsi_brg_ll_clear_interrupt_status(dsi_brg_dev_t *b, unsigned bits)
{ assert(b && bits == 1); }
static unsigned dw_gdma_ll_channel_get_intr_status(dw_gdma_dev_t *d, int id)
{ assert(d && !id); return 0; }
static uint32_t dw_gdma_ll_channel_get_current_link_list_item_addr(dw_gdma_dev_t *d, int id)
{ assert(d && !id); return 0; }
static void dw_gdma_ll_channel_enable(dw_gdma_dev_t *d, int id, bool on)
{ assert(!id); d->chen0.val = on; }
static void dw_gdma_ll_channel_set_trans_flow(dw_gdma_dev_t *d, int id, int src, int dst, int flow)
{ assert(!d->chen0.val && !id && !src && dst == 1 && !flow); ++restored_flow; }
static dw_gdma_link_list_item_t *dw_gdma_link_list_get_item(dw_gdma_link_list_handle_t list, int i)
{ return list + i; }
static void dw_gdma_ll_lli_set_block_markers(dw_gdma_link_list_item_t *i, bool irq, bool last, bool valid)
{ assert(!irq && last && valid); i->ctrl_hi.val = 3u << 30; }
static void dw_gdma_channel_use_link_list(dw_gdma_channel_handle_t ch, dw_gdma_link_list_handle_t list)
{ assert(ch && !fake_gdma.chen0.val); selected = list; }
static int esp_cache_msync(void *p, unsigned bytes, unsigned flags)
{
    assert(bytes == 5120 && flags == ESP_CACHE_MSYNC_FLAG_DIR_C2M);
    assert(p == storage[0] || p == storage[1]);
    ++clean_counts[p == storage[1]];
    return ESP_OK;
}
#include "device_callbacks.inc"

int main(int argc, char **argv)
{
    assert(argc == 2);
    const char *scenario = argv[1];
    dsi_brg_dev_t brg = {0};
    fake_bus bus = {.hal = {.bridge = &brg}};
    dw_gdma_link_list_item_t reference = {0}, items[PAIRS_PER_FRAME] = {0};
    esp_lcd_dpi_panel_t panel = {.bus=&bus,.dma_chan=&fake_gdma,.link_lists={&reference}};
    pair.panel = &panel;
    pair.slot[0] = storage[0]; pair.slot[1] = storage[1];
    pair.list = items; pair.items = items;
    // Reference EOF must suppress its normal rearm before the flow switch.
    const uint32_t reference_size = PAIRS_PER_FRAME * WORDS_PER_PAIR;
    // Preserve either observed encoding without correcting the hardware sample.
    const uint32_t reference_status = reference_size - (!strcmp(scenario, "long") ? 1u : 0u);
    const uint32_t reference_flags = PAIR_FRAME_DONE | PAIR_BLOCK_DONE;
    reference.block_ts_lo.val = reference_size - 1;
    reference.status_lo.val = reference_status;
    reference.status_hi.val = reference_flags;
    reference.ctrl_hi.val = 1u << 30; // LAST set, VALID clear
    pair.phase = DRAIN_REF;
    assert(pair_on_frame(&panel));
    assert(pair.phase == QUIET && pair_channel_stopped() && !output_enabled);
    assert(!pair.reference_count.captured);
    pair_capture_reference_count(&panel);
    memset(&reference, 0, sizeof(reference));
    assert(pair_publish(0,true) && pair_publish(1,true));
    pair.phase = LIVE;
    fake_gdma.chen0.val = 1;
    if (!strcmp(scenario,"invalid")) {
        pair_on_invalid(&fake_gdma,NULL,&panel);
        assert(pair.fault == INVALID_LLI);
    } else if (!strcmp(scenario,"underrun")) {
        assert(pair_on_underrun());
        assert(pair.fault == UNDERRUN);
    } else if (!strcmp(scenario,"early-eof")) {
        assert(pair_on_frame(&panel));
        assert(pair.fault == WRONG_EOF);
    } else for (unsigned n=0; n<TOTAL_PAIRS; ++n) {
        unsigned p = n%PAIRS_PER_FRAME;
        assert(pair.generation[p&1] == n && (items[p].ctrl_hi.val & PAIR_VALID));
        // Before reuse even the previous generation's DONE must be clear.
        assert(!items[p].status_hi.val && !items[p].status_lo.val);
        bool end = p == PAIRS_PER_FRAME-1;
        items[p].status_lo.val = WORDS_PER_PAIR;
        items[p].status_hi.val = PAIR_BLOCK_DONE | (end ? PAIR_FRAME_DONE : 0);
        items[p].ctrl_hi.val &= ~PAIR_VALID;
        if (!strcmp(scenario,"stale") && n == PAIRS_PER_FRAME) {
            // Old DONE survived, but new VALID is still set: zero fresh consumption.
            items[p].ctrl_hi.val |= PAIR_VALID;
        }
        if (!strcmp(scenario,"short") && !n) --items[p].status_lo.val;
        if (!strcmp(scenario,"long") && !n) items[p].status_lo.val = 639;
        if (!strcmp(scenario,"coalesced") && !n) items[p+1].status_hi.val = PAIR_BLOCK_DONE;
        if (!strcmp(scenario,"task")) interrupt_context = false;
        if (end) fake_gdma.chen0.val = 0;
        uint32_t entered = pair_irq_enter(&fake_gdma);
        assert(entered);
        pair_irq_status(end ? 3 : 1);
        pair_on_block(&fake_gdma,NULL,&panel);
        if (end) {
            if (!strcmp(scenario,"withheld")) items[0].ctrl_hi.val &= ~PAIR_VALID;
            assert(pair_on_frame(&panel));
        }
        pair_irq_leave(entered);
        if (pair.phase == FAILED) break;
        assert(pair.retired == n+1);
    }
    if (!strcmp(scenario,"normal")) {
        assert(pair.phase == FINISHED && pair_channel_stopped());
        assert(pair.primed == 2 && pair.irq_publications == 71998 &&
               pair.frames == 300 && pair.wraps == 299 && pair.retired == 72000);
        assert(pair.generation[0] == 71998 && pair.generation[1] == 71999);
        assert(clean_counts[0] == 36000 && clean_counts[1] == 36000 && pair.in_isr);
        for (unsigned i=0; i<4; ++i) assert(pair.seam[i].ordinal == 238+i && pair.seam[i].words == 636);
        assert(pair.seam[1].rearmed_at);
        pair_restore(&panel);
        assert(restored_flow == 1 && selected == &reference && output_enabled);
        assert(pair.phase == RESTORING && !pair_on_frame(&panel) && pair.restored);
    } else {
        if (!strcmp(scenario,"stale")) assert(pair.fault == NO_WRITEBACK && pair.retired == 240);
        if (!strcmp(scenario,"withheld")) assert(pair.fault == TOP_MISSING && !pair.wraps);
        if (!strcmp(scenario,"coalesced")) assert(pair.fault == COALESCED);
        if (!strcmp(scenario,"short")) assert(pair.fault == BAD_SIZE);
        if (!strcmp(scenario,"long"))
            assert(pair.fault == BAD_SIZE && pair.fault_lo == 639 && !pair.retired && !pair.irq_publications);
        if (!strcmp(scenario,"task")) assert(pair.fault == OUTSIDE_IRQ);
        assert(pair.phase == FAILED && pair_channel_stopped());
        unsigned frozen = pair.fault;
        pair_on_underrun(); pair_on_frame(&panel);
        assert(pair.fault == frozen && pair_channel_stopped());
    }
    assert(pair.reference_count.captured && pair.reference_count.block_ts == reference_size - 1);
    assert(pair.reference_count.status_lo == reference_status && pair.reference_count.status_hi == reference_flags);
    assert(pair.reference_count.ctrl_hi == (1u << 30));
    printf("PASS %s, retired %u, fault %s\n", scenario, (unsigned)pair.retired, pair_fault_name[pair.fault]);
}
