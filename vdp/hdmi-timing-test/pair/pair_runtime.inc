// One-shot bench diagnostic inside the pinned DPI translation unit. All
// control calls and both interrupts run on the panel's allocating CPU.
// DW writeback is read through uncached internal descriptor aliases. The
// descriptor's written-back channel-status bits 62/63 are documented in
// the P4 v1.3 TRM, section 5.5.4.2, but unnamed in IDF's status1 union.
#include <stdio.h>
#include <inttypes.h>
#include <stdatomic.h>
#include "hal/dw_gdma_ll.h"
#include "esp_cpu.h"
#include "esp_timer.h"
#include "pair_driver.h"
#include "pair_pattern.h"

enum { PAIRS_PER_FRAME = 240, LIVE_FRAMES = 300, TOTAL_PAIRS = 72000,
       WORDS_PER_PAIR = 636, SLOT_BYTES = 5120 };
#define PAIR_VALID (UINT32_C(1) << 31)
#define PAIR_BLOCK_DONE (UINT32_C(1) << 30)
#define PAIR_FRAME_DONE (UINT32_C(1) << 31)
_Static_assert(WORDS_PER_PAIR * 8 == 848 * 2 * 3, "pair payload size");
_Static_assert(TOTAL_PAIRS == PAIRS_PER_FRAME * LIVE_FRAMES, "finite run");

enum pair_phase { REF, DRAIN_REF, QUIET, LIVE, FINISHED, FAILED, RESTORING };
enum pair_fault { CLEAN, SETUP, REF_STOP, DMA_ERROR, INVALID_LLI, UNDERRUN,
                  WRONG_TAG, NO_WRITEBACK, BAD_SIZE, BAD_FRAME_DONE, COALESCED,
                  OUTSIDE_IRQ, CACHE_ERROR, ALREADY_VALID, WRONG_EOF,
                  TOP_MISSING, STALLED, RESTORE_ERROR, STOP_TIMEOUT };
static const char *const pair_fault_name[] = {
    "none","setup","reference_stop","dma_error","invalid_descriptor","underrun",
    "wrong_tag","missing_writeback","wrong_word_count","wrong_dma_done","coalesced",
    "outside_interrupt","cache","already_valid","frame_order",
    "top_not_ready","no_progress","reference_restore","channel_stop_timeout"
};

typedef struct {
    uint32_t valid_cycles, handler_cycles, min_spacing, max_spacing, min_lead;
} pair_timing;
typedef struct {
    uint32_t ordinal, entered, status_hi, words, published, published_at, rearmed_at;
} pair_wrap_sample;
static struct {
    esp_lcd_dpi_panel_t *panel;
    int id;
    dw_gdma_link_list_handle_t list;
    volatile dw_gdma_link_list_item_t *items;
    uint8_t *slot[2];
    unsigned generation[2];
    uint32_t ready_at[2];
    _Atomic enum pair_phase phase;
    _Atomic uint32_t retired, fault;
    enum pair_phase fault_phase;
    uint32_t fault_hi, fault_lo, fault_ctrl, fault_ordinal, fault_raw, fault_hw, fault_lli;
    uint32_t frames, wraps, irq_publications, primed, raw, previous_entry, irq_band;
    uint32_t ref_frames, timings_over, underruns;
    bool in_isr, quiet_verified, restored;
    bool invoked;
    pair_timing timing[3]; // first frame, second frame, remaining frames
    pair_wrap_sample seam[4]; // frame 0 pairs 238/239; frame 1 pairs 0/1
    uint32_t old_flow, old_req, old_credit, old_block, old_frame, old_spacing;
    uint32_t flow, req, credit, block, frame, spacing, reload, dw_cfg, dw_cfg0;
} pair;
static portMUX_TYPE pair_control = portMUX_INITIALIZER_UNLOCKED;

static void pair_note_max(uint32_t *out, uint32_t value) { if (value > *out) *out = value; }
static void pair_note_min(uint32_t *out, uint32_t value) { if (value < *out) *out = value; }

static void pair_output(bool enabled)
{
    dsi_brg_dev_t *brg = pair.panel->bus->hal.bridge;
    mipi_dsi_brg_ll_enable_dpi_output(brg, enabled);
    mipi_dsi_brg_ll_update_dpi_config(brg);
}

static bool pair_channel_stopped(void)
{
    return !(DW_GDMA_LL_GET_HW(0)->chen0.val & (1u << pair.id));
}

// Called on the allocating core, from an ISR or with that core's scheduling
// excluded for timeout handling. Keep the first fault before disabling DMA.
static void pair_fail(enum pair_fault fault)
{
    unsigned clear = CLEAN;
    if (!atomic_compare_exchange_strong(&pair.fault, &clear, fault)) return;
    pair.fault_phase = pair.phase;
    pair.phase = FAILED;
    unsigned n = pair.retired;
    pair.fault_ordinal = n;
    pair.fault_raw = pair.raw;
    if (pair.items) {
        volatile dw_gdma_link_list_item_t *item = &pair.items[n % PAIRS_PER_FRAME];
        pair.fault_hi = item->status_hi.val;
        pair.fault_lo = item->status_lo.val;
        pair.fault_ctrl = item->ctrl_hi.val;
    }
    if (pair.panel) {
        dw_gdma_dev_t *hw = DW_GDMA_LL_GET_HW(0);
        pair.fault_hw = dw_gdma_ll_channel_get_intr_status(hw, pair.id);
        pair.fault_lli = dw_gdma_ll_channel_get_current_link_list_item_addr(hw, pair.id);
        dw_gdma_ll_channel_enable(hw, pair.id, false);
        pair_output(false);
    }
}

static inline unsigned pair_band(unsigned ordinal)
{
    unsigned f = ordinal / PAIRS_PER_FRAME;
    return f < 2 ? f : 2;
}

// These hooks bracket the *dispatcher*, including the full-frame callback on
// the final block. Cycle counters wrap safely for individual short intervals.
uint32_t pair_irq_enter(void *channel)
{
    uint32_t entry = esp_cpu_get_cycle_count();
    if (pair.phase != LIVE || channel != pair.panel->dma_chan) return 0;
    unsigned n = pair.retired;
    pair.irq_band = pair_band(n);
    return entry ? entry : UINT32_MAX;
}
void pair_irq_status(uint32_t status)
{
    pair.raw = status;
    // Bits 5..12 are AXI/LLI access faults. INVALID is handled separately
    // by the pinned driver so that the hardware's invalid LLP is available.
    if (status & 0x1fe0u) pair_fail(DMA_ERROR);
}
void pair_irq_leave(uint32_t entry)
{
    uint32_t duration = esp_cpu_get_cycle_count() - entry;
    pair_note_max(&pair.timing[pair.irq_band].handler_cycles, duration);
    if ((uint64_t)duration * 10 > (uint64_t)CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ * 644)
        ++pair.timings_over;
}

static bool pair_on_invalid(dw_gdma_channel_handle_t ch, const dw_gdma_break_event_data_t *event, void *ctx)
{
    (void)ch; (void)event; (void)ctx;
    if (pair.phase == LIVE) pair_fail(INVALID_LLI);
    return false;
}
static bool pair_on_underrun(void)
{
    enum pair_phase phase = pair.phase;
    if (phase == LIVE) {
        ++pair.underruns;
        pair_fail(UNDERRUN);
    }
    return phase != REF && phase != RESTORING;
}

static bool pair_publish(unsigned ordinal, bool primed)
{
    unsigned p = ordinal % PAIRS_PER_FRAME, s = p & 1;
    volatile dw_gdma_link_list_item_t *item = &pair.items[p];
    if (item->ctrl_hi.val & PAIR_VALID) {
        pair_fail(ALREADY_VALID);
        return false;
    }
    pair_pattern_fill(pair.slot[s], ordinal / PAIRS_PER_FRAME, p, primed);
    if (esp_cache_msync(pair.slot[s], SLOT_BYTES, ESP_CACHE_MSYNC_FLAG_DIR_C2M) != ESP_OK) {
        pair_fail(CACHE_ERROR);
        return false;
    }
    if (pair.phase == FAILED) return false;
    item->status_lo.val = 0;
    item->status_hi.val = 0;
    pair.generation[s] = ordinal;
    asm volatile("fence iorw,iorw" ::: "memory");
    item->ctrl_hi.val |= PAIR_VALID;
    asm volatile("fence iorw,iorw" ::: "memory");
    pair.ready_at[s] = esp_cpu_get_cycle_count();
    if (primed) ++pair.primed;
    else ++pair.irq_publications;
    return true;
}

static bool pair_on_block(dw_gdma_channel_handle_t ch, const dw_gdma_trans_done_event_data_t *event, void *ctx)
{
    (void)ch; (void)event; (void)ctx;
    uint32_t entry = esp_cpu_get_cycle_count();
    if (pair.phase != LIVE) return false;
    unsigned n = pair.retired;
    if (n >= TOTAL_PAIRS || n / PAIRS_PER_FRAME != pair.frames) {
        pair_fail(WRONG_EOF);
        return false;
    }
    unsigned p = n % PAIRS_PER_FRAME, slot = p & 1;
    pair_timing *timing = &pair.timing[pair_band(n)];
    if (n && p) {
        uint32_t since = entry - pair.previous_entry;
        pair_note_min(&timing->min_spacing, since);
        pair_note_max(&timing->max_spacing, since);
    }
    pair.previous_entry = entry;
    // Hardware may already be fetching the successor. This is only an
    // observed software lead ending at the predecessor's completion IRQ.
    if (p + 1 < PAIRS_PER_FRAME) pair_note_min(&timing->min_lead, entry - pair.ready_at[slot ^ 1]);
    volatile dw_gdma_link_list_item_t *item = &pair.items[p];
    uint32_t done = item->status_hi.val;
    asm volatile("fence iorw,iorw" ::: "memory");
    unsigned words = item->status_lo.cmpltd_blk_tfr_size;
    bool last = p == PAIRS_PER_FRAME - 1;
    if (pair.generation[slot] != n) { pair_fail(WRONG_TAG); return false; }
    if (!(done & PAIR_BLOCK_DONE) || (item->ctrl_hi.val & PAIR_VALID)) {
        pair_fail(NO_WRITEBACK);
        return false;
    }
    if (words != WORDS_PER_PAIR) { pair_fail(BAD_SIZE); return false; }
    if (((done & PAIR_FRAME_DONE) != 0) != last) {
        pair_fail(BAD_FRAME_DONE);
        return false;
    }
    if (!last && (pair.items[p + 1].status_hi.val & PAIR_BLOCK_DONE)) {
        pair_fail(COALESCED);
        return false;
    }
    pair_wrap_sample *sample = n >= 238 && n <= 241 ? &pair.seam[n - 238] : NULL;
    if (sample) {
        sample->ordinal = n;
        sample->entered = entry;
        sample->status_hi = done;
        sample->words = words;
    }
    if (n + 2 < TOTAL_PAIRS) {
        if (!n) {
            pair.in_isr = xPortInIsrContext();
            if (!pair.in_isr) { pair_fail(OUTSIDE_IRQ); return false; }
        }
        if (!pair_publish(n + 2, false)) return false;
        uint32_t at = pair.ready_at[slot];
        pair_note_max(&timing->valid_cycles, at - entry);
        if (sample) { sample->published = n + 2; sample->published_at = at; }
    }
    pair.retired = n + 1;
    return false;
}

static bool pair_on_frame(esp_lcd_dpi_panel_t *panel)
{
    enum pair_phase phase = pair.phase;
    if (phase == RESTORING) {
        pair.restored = true;
        pair.phase = REF;
        return false; // let the IDF reference callback continue
    }
    if (phase == REF) return false;
    if (phase == DRAIN_REF) {
        pair_output(false);
        pair.phase = QUIET;
        return true; // no reference rearm
    }
    if (phase != LIVE) return true;
    unsigned next = (pair.frames + 1) * PAIRS_PER_FRAME;
    if (pair.retired != next) {
        pair_fail(WRONG_EOF);
        return true;
    }
    ++pair.frames;
    if (next == TOTAL_PAIRS) {
        pair_output(false);
        pair.phase = FINISHED;
        return true;
    }
    for (unsigned i = 0; i < 2; ++i) {
        if (pair.generation[i] != next + i ||
            !(pair.items[i].ctrl_hi.val & PAIR_VALID) || pair.items[i].status_hi.val) {
            pair_fail(TOP_MISSING);
            return true;
        }
    }
    // An underrun must never be followed by a successful-path rearm.
    portENTER_CRITICAL_ISR(&pair_control);
    if (pair.phase == LIVE) {
        dw_gdma_channel_use_link_list(panel->dma_chan, pair.list);
        dw_gdma_ll_channel_enable(DW_GDMA_LL_GET_HW(0), pair.id, true);
        ++pair.wraps;
        if (next == PAIRS_PER_FRAME) pair.seam[1].rearmed_at = esp_cpu_get_cycle_count();
    }
    portEXIT_CRITICAL_ISR(&pair_control);
    return true;
}

static bool pair_wait_stop(void)
{
    int64_t deadline = esp_timer_get_time() + 100000;
    while (!pair_channel_stopped() && esp_timer_get_time() < deadline) vTaskDelay(1);
    return pair_channel_stopped();
}

static esp_err_t pair_allocate(void)
{
    for (unsigned i = 0; i < 2; ++i) {
        pair.slot[i] = heap_caps_aligned_calloc(64, 1, SLOT_BYTES, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA | MALLOC_CAP_8BIT);
        if (!pair.slot[i]) return ESP_ERR_NO_MEM;
    }
    dw_gdma_link_list_config_t list = {.num_items = PAIRS_PER_FRAME, .link_type = DW_GDMA_LINKED_LIST_TYPE_SINGLY};
    esp_err_t err = dw_gdma_new_link_list(&list, &pair.list);
    if (err != ESP_OK) return err;
    pair.items = dw_gdma_link_list_get_item(pair.list, 0);
    dw_gdma_block_transfer_config_t transfer = {
        .src = {.burst_mode = DW_GDMA_BURST_MODE_INCREMENT, .burst_items = DW_GDMA_BURST_ITEMS_4,
                .burst_len = 4, .width = DW_GDMA_TRANS_WIDTH_64},
        .dst = {.addr = MIPI_DSI_BRG_MEM_BASE, .burst_mode = DW_GDMA_BURST_MODE_FIXED,
                .burst_items = DW_GDMA_BURST_ITEMS_4, .burst_len = 4, .width = DW_GDMA_TRANS_WIDTH_64},
        .size = WORDS_PER_PAIR,
    };
    for (unsigned p = 0; p < PAIRS_PER_FRAME; ++p) {
        dw_gdma_lli_handle_t item = dw_gdma_link_list_get_item(pair.list, p);
        transfer.src.addr = (uint32_t)pair.slot[p & 1];
        err = dw_gdma_lli_config_transfer(item, &transfer);
        if (err != ESP_OK) return err;
        dw_gdma_ll_lli_set_block_markers(item, true, p == PAIRS_PER_FRAME - 1, false);
    }
    for (unsigned i = 0; i < 3; ++i) {
        pair.timing[i].min_spacing = UINT32_MAX;
        pair.timing[i].min_lead = UINT32_MAX;
    }
    return ESP_OK;
}

static bool pair_configure_live(esp_lcd_dpi_panel_t *panel)
{
    dw_gdma_dev_t *hw = DW_GDMA_LL_GET_HW(0);
    dsi_brg_dev_t *brg = panel->bus->hal.bridge;
    pair.old_req = brg->dma_req_cfg.val;
    pair.old_flow = brg->dma_flow_ctrl.val;
    pair.old_block = brg->blk_raw_num_cfg.val;
    pair.old_spacing = brg->dma_block_interval.val;
    pair.old_frame = brg->dma_frame_interval.val;
    pair.old_credit = brg->raw_buf_credit_ctl.val;
    // r05 uses DMAC flow. This experiment selects the destination on both
    // sides of the hardware handshake, with 159 four-word bursts per pair.
    dw_gdma_ll_channel_set_trans_flow(hw, pair.id, DW_GDMA_ROLE_MEM,
                                      DW_GDMA_ROLE_PERIPH_DSI, DW_GDMA_FLOW_CTRL_DST);
    mipi_dsi_brg_ll_set_flow_controller(brg, MIPI_DSI_LL_FLOW_CONTROLLER_BRIDGE);
    brg->dma_frame_interval.dma_multiblk_en = 1;
    brg->dma_block_interval.dma_block_interval_en = 0;
    brg->dma_block_interval.raw_num_total_auto_reload = 1;
    mipi_dsi_brg_ll_set_num_pixel_bits(brg, PAIRS_PER_FRAME * WORDS_PER_PAIR * 64);
    brg->blk_raw_num_cfg.blk_raw_num_total = WORDS_PER_PAIR;
    brg->blk_raw_num_cfg.blk_raw_num_total_set = 1;
    mipi_dsi_brg_ll_set_burst_len(brg, 4);
    mipi_dsi_brg_ll_credit_set_threshold(brg, 1024);
    mipi_dsi_brg_ll_credit_set_burst_threshold(brg, 1024 - 4);
    mipi_dsi_brg_ll_credit_reset(brg);
    mipi_dsi_brg_ll_update_dpi_config(brg);
    pair.flow = brg->dma_flow_ctrl.val;
    pair.req = brg->dma_req_cfg.val;
    pair.credit = brg->raw_buf_credit_ctl.val;
    pair.block = brg->blk_raw_num_cfg.val;
    pair.frame = brg->raw_num_cfg.val;
    pair.spacing = brg->dma_frame_interval.val;
    pair.reload = brg->dma_block_interval.val;
    pair.dw_cfg = hw->ch[pair.id].cfg1.val;
    pair.dw_cfg0 = hw->ch[pair.id].cfg0.val;
    return brg->dma_flow_ctrl.dsi_dma_flow_controller == 1 &&
           brg->dma_frame_interval.dma_multiblk_en == 1 &&
           brg->raw_num_cfg.raw_num_total == PAIRS_PER_FRAME * WORDS_PER_PAIR &&
           brg->blk_raw_num_cfg.blk_raw_num_total == WORDS_PER_PAIR &&
           hw->ch[pair.id].cfg1.tt_fc == DW_GDMA_LL_FLOW_M2P_DST;
}

static bool pair_wait_phase(enum pair_phase phase, unsigned timeout_ms)
{
    int64_t deadline = esp_timer_get_time() + timeout_ms * 1000;
    while (pair.phase == phase && esp_timer_get_time() < deadline) vTaskDelay(1);
    return pair.phase != phase;
}

static void pair_restore(esp_lcd_dpi_panel_t *panel)
{
    dw_gdma_dev_t *hw = DW_GDMA_LL_GET_HW(0);
    dsi_brg_dev_t *brg = panel->bus->hal.bridge;
    dw_gdma_ll_channel_set_trans_flow(hw, pair.id, DW_GDMA_ROLE_MEM,
                                      DW_GDMA_ROLE_PERIPH_DSI, DW_GDMA_FLOW_CTRL_SELF);
    brg->dma_req_cfg.val = pair.old_req;
    brg->dma_flow_ctrl.val = pair.old_flow;
    brg->raw_buf_credit_ctl.val = pair.old_credit;
    brg->blk_raw_num_cfg.val = pair.old_block;
    brg->dma_frame_interval.val = pair.old_frame;
    brg->dma_block_interval.val = pair.old_spacing;
    dw_gdma_link_list_handle_t list = panel->link_lists[panel->cur_fb_index];
    dw_gdma_ll_lli_set_block_markers(dw_gdma_link_list_get_item(list, 0), false, true, true);
    asm volatile("fence iorw,iorw" ::: "memory");
    dw_gdma_channel_use_link_list(panel->dma_chan, list);
    portENTER_CRITICAL(&pair_control);
    pair.phase = RESTORING;
    mipi_dsi_brg_ll_clear_interrupt_status(brg, MIPI_DSI_BRG_LL_EVENT_UNDERRUN);
    dw_gdma_ll_channel_enable(hw, pair.id, true);
    pair_output(true);
    portEXIT_CRITICAL(&pair_control);
}

esp_err_t pair_driver_run(esp_lcd_panel_handle_t handle)
{
    if (!handle || xPortGetCoreID() != 1 || pair.invoked) return ESP_ERR_INVALID_STATE;
    esp_lcd_dpi_panel_t *panel = __containerof(handle, esp_lcd_dpi_panel_t, base);
    if (panel->h_pixels != 848 || panel->v_pixels != 480 || panel->bits_per_pixel != 24 ||
        panel->num_fbs != 1 || panel->fbcpy_handle) return ESP_ERR_NOT_SUPPORTED;
    esp_err_t result = dw_gdma_channel_get_id(panel->dma_chan, &pair.id);
    if (result != ESP_OK) return result;
    pair.invoked = true;
    pair.panel = panel;
    result = pair_allocate();
    if (result != ESP_OK) {
        pair.fault = SETUP;
        return result; // reference continues untouched
    }
    pair.phase = DRAIN_REF;
    if (!pair_wait_phase(DRAIN_REF, 100) || pair.phase != QUIET || !pair_wait_stop()) {
        portENTER_CRITICAL(&pair_control);
        pair_fail(REF_STOP);
        portEXIT_CRITICAL(&pair_control);
        pair.quiet_verified = pair_wait_stop();
        return ESP_ERR_TIMEOUT;
    }
    if (!pair_configure_live(panel) || !pair_publish(0, true) || !pair_publish(1, true)) {
        pair_fail(SETUP);
        pair.quiet_verified = pair_wait_stop();
        return ESP_FAIL;
    }
    dw_gdma_channel_use_link_list(panel->dma_chan, pair.list);
    portENTER_CRITICAL(&pair_control);
    mipi_dsi_brg_ll_clear_interrupt_status(panel->bus->hal.bridge, MIPI_DSI_BRG_LL_EVENT_UNDERRUN);
    pair.phase = LIVE;
    dw_gdma_ll_channel_enable(DW_GDMA_LL_GET_HW(0), pair.id, true);
    pair_output(true);
    portEXIT_CRITICAL(&pair_control);

    uint32_t last = 0;
    int64_t began = esp_timer_get_time(), progress = began;
    while (pair.phase == LIVE) {
        vTaskDelay(1);
        unsigned current = pair.retired;
        int64_t now = esp_timer_get_time();
        if (current != last) {
            last = current;
            progress = now;
        }
        if (now - progress > 100000 || now - began > 8000000) {
            portENTER_CRITICAL(&pair_control);
            if (pair.phase == LIVE && (pair.retired == current || now - began > 8000000)) pair_fail(STALLED);
            portEXIT_CRITICAL(&pair_control);
        }
    }
    pair.quiet_verified = pair_wait_stop();
    if (!pair.quiet_verified) {
        pair_fail(STOP_TIMEOUT);
        return ESP_ERR_TIMEOUT;
    }
    if (pair.phase != FINISHED || pair.fault) return ESP_FAIL;
    pair_restore(panel);
    if (!pair_wait_phase(RESTORING, 100) || !pair.restored) {
        portENTER_CRITICAL(&pair_control);
        pair_fail(RESTORE_ERROR);
        portEXIT_CRITICAL(&pair_control);
        return ESP_FAIL;
    }
    return pair.timings_over ? ESP_ERR_TIMEOUT : ESP_OK;
}

void pair_driver_report(void)
{
    printf("PAIR_RESULT {\"fault\":\"%s\",\"at\":%u,\"phase_at_fault\":%u,"
           "\"retired\":%u,\"frames\":%u,\"wraps\":%u,\"primed\":%u,\"irq_fills\":%u,"
           "\"in_irq\":%u,\"timing_misses\":%u,\"cpu_mhz\":%u,\"underruns\":%u,"
           "\"live_stopped\":%u,\"reference_restored\":%u,"
           "\"writeback\":[%u,%u,%u],\"fault_hw\":[%u,%u,%u],"
           "\"flow\":%u,\"request\":%u,\"credit\":%u,\"block_cfg\":%u,\"frame_cfg\":%u,"
           "\"frame_interval\":%u,\"block_interval\":%u,\"dw_cfg\":[%u,%u]}\n",
           pair_fault_name[pair.fault], (unsigned)pair.fault_ordinal, (unsigned)pair.fault_phase,
           (unsigned)pair.retired, (unsigned)pair.frames, (unsigned)pair.wraps, (unsigned)pair.primed,
           (unsigned)pair.irq_publications, (unsigned)pair.in_isr, (unsigned)pair.timings_over,
           (unsigned)CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ, (unsigned)pair.underruns,
           (unsigned)pair.quiet_verified, (unsigned)pair.restored, (unsigned)pair.fault_hi,
           (unsigned)pair.fault_lo, (unsigned)pair.fault_ctrl, (unsigned)pair.fault_raw,
           (unsigned)pair.fault_hw, (unsigned)pair.fault_lli,
           (unsigned)pair.flow, (unsigned)pair.req, (unsigned)pair.credit, (unsigned)pair.block,
           (unsigned)pair.frame, (unsigned)pair.spacing, (unsigned)pair.reload,
           (unsigned)pair.dw_cfg0, (unsigned)pair.dw_cfg);
    for (unsigned i = 0; i < 3; ++i) {
        pair_timing *t = &pair.timing[i];
        printf("PAIR_TIME {\"band\":%u,\"valid_cycles\":%u,\"handler_cycles\":%u,"
               "\"min_spacing_cycles\":%u,\"max_spacing_cycles\":%u,\"min_sw_lead_cycles\":%u}\n",
               i,(unsigned)t->valid_cycles,(unsigned)t->handler_cycles,(unsigned)t->min_spacing,
               (unsigned)t->max_spacing,(unsigned)t->min_lead);
    }
    for (unsigned i = 0; i < 4; ++i) {
        pair_wrap_sample *s = &pair.seam[i];
        if (!s->words) continue;
        printf("PAIR_WRAP {\"ordinal\":%u,\"entry_cycles\":%u,\"done\":%u,\"words\":%u,"
               "\"published\":%u,\"valid_cycles\":%u,\"rearm_cycles\":%u}\n",
               (unsigned)s->ordinal,(unsigned)s->entered,(unsigned)s->status_hi,(unsigned)s->words,
               (unsigned)s->published,(unsigned)s->published_at,(unsigned)s->rearmed_at);
    }
    if (!pair.quiet_verified) return;
    const char digits[] = "0123456789abcdef";
    // The transfer ranges belong to the stopped live channel. The restarted
    // reference only reads the original full framebuffer.
    for (unsigned s = 0; s < 2; ++s) {
        if (!pair.slot[s]) continue;
        printf("PAIR_SLOT %u ", s);
        char chunk[129];
        for (unsigned at = 0; at < WORDS_PER_PAIR * 8;) {
            unsigned count = MIN(64, WORDS_PER_PAIR * 8 - at);
            for (unsigned k = 0; k < count; ++k) {
                uint8_t value = pair.slot[s][at++];
                chunk[k * 2] = digits[value >> 4];
                chunk[k * 2 + 1] = digits[value & 15];
            }
            chunk[2 * count] = 0;
            fputs(chunk, stdout);
        }
        putchar('\n');
    }
    fflush(stdout);
}
