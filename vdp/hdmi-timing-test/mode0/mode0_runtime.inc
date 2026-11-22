// Standalone diagnostic included in the IDF 5.5.5 DPI driver's translation
// unit. The shipped driver still owns the immutable preview. Only the one
// live frame uses this prelinked list. The panel and its interrupts are on
// the command task's pinned core. Keep the one-shot evidence until reset.
#ifndef MODE0_HOST_TEST
#include <inttypes.h>
#include <stdatomic.h>
#include <stdio.h>
#include <string.h>
#include "hal/cache_ll.h"
#include "hal/dw_gdma_ll.h"
#include "esp_cpu.h"
#include "esp_timer.h"
#include "mode0_driver.h"
#define MODE0_DMA_FENCE() asm volatile("fence iorw,iorw" ::: "memory")
#endif

enum { M0_ROWS = 480, M0_BYTES = 848 * 3, M0_MARGIN = 104 * 3,
       M0_PIXELS = 640 * 3, M0_SLOT_BYTES = 2560, M0_WORDS = M0_BYTES / 8,
       M0_MIDDLE_WORDS = (M0_ROWS - 2) * M0_WORDS };
_Static_assert(M0_BYTES == 2 * M0_MARGIN + M0_PIXELS && M0_WORDS == 318,
               "one complete 848-pixel RGB888 row");
_Static_assert(M0_SLOT_BYTES >= M0_BYTES && M0_SLOT_BYTES % 128 == 0,
               "cache clean must stay inside the private allocation");

// TRM v1.3, figure 5.5-6: bits 62/63 are the last LLI writeback fields.
#define M0_DONE (UINT32_C(1) << 30)
#define M0_FRAME (UINT32_C(1) << 31)
#define M0_VALID (UINT32_C(1) << 31)
#define M0_LAST (UINT32_C(1) << 30)
// v1.3 DMAC_CHn_INTSTATUS fields: data/LLI access (5..12), multiblock
// type (14), slave register access (16..21), parity (25), abort (31).
// INVALID (13) has its own diagnostic.
#define M0_BUS_ERRORS UINT32_C(0x823f5fe0)

enum mode0_phase { M0_REF, M0_DRAIN, M0_QUIET, M0_LIVE, M0_FINISHED,
                   M0_FAILED, M0_RESTORING };
enum mode0_fault { M0_OK, M0_SETUP, M0_REF_STOP, M0_FLOW, M0_DMA_ERROR,
                   M0_INVALID, M0_UNDERRUN, M0_IRQ_CONTEXT, M0_ORDER,
                   M0_WRITEBACK, M0_ADDRESS, M0_SYNC, M0_TIMEOUT, M0_STOP };
static const char *const mode0_fault_names[] = {
    "none", "setup", "reference_stop", "flow", "dma_error",
    "invalid_descriptor", "underrun", "outside_interrupt", "order",
    "writeback", "address", "cache", "timeout", "channel_stop"
};

struct mode0_lli_snapshot {
    uint32_t source, block_size, control, status, count;
};

static struct {
    esp_lcd_dpi_panel_t *panel;
    dw_gdma_link_list_handle_t list;
    volatile dw_gdma_link_list_item_t *items;
    int id;
    uint8_t *slot;
    uint8_t before[M0_BYTES];     // immutable copy of the DMA-visible initial bytes
    uint8_t bottom[M0_PIXELS];    // internal, read-only after setup
    _Atomic enum mode0_phase phase;
    enum mode0_fault fault;
    enum mode0_phase fault_phase;
    bool invoked, primed, stopped, restored, in_irq, published;
    bool started, frame_ok;
    uint32_t dispatcher_entry, irq_entry, retired_at, first_store_at, published_at, frame_at;
    uint32_t fills, raw, underruns;
    struct mode0_lli_snapshot armed[3], old_reader, new_reader_before, frozen[3];
} m0;
static portMUX_TYPE mode0_control = portMUX_INITIALIZER_UNLOCKED;

static inline struct mode0_lli_snapshot mode0_observe(unsigned index)
{
    volatile dw_gdma_link_list_item_t *item = &m0.items[index];
    const uint32_t status = item->status_hi.val;
    MODE0_DMA_FENCE();
    return (struct mode0_lli_snapshot){
        .source = item->sar_lo.val, .block_size = item->block_ts_lo.val,
        .control = item->ctrl_hi.val, .status = status, .count = item->status_lo.val
    };
}

static void mode0_snapshot(struct mode0_lli_snapshot out[3])
{
    for (unsigned i = 0; i < 3; ++i) out[i] = mode0_observe(i);
}

static inline bool mode0_stopped(void)
{
    return !(DW_GDMA_LL_GET_HW(0)->chen0.val & (1u << m0.id));
}

static void mode0_output(bool enabled)
{
    dsi_brg_dev_t *brg = m0.panel->bus->hal.bridge;
    mipi_dsi_brg_ll_enable_dpi_output(brg, enabled);
    mipi_dsi_brg_ll_update_dpi_config(brg);
}

static bool mode0_bridge_underrun(void)
{
    return mipi_dsi_brg_ll_get_interrupt_status(m0.panel->bus->hal.bridge) &
           MIPI_DSI_BRG_LL_EVENT_UNDERRUN;
}

// Called by the allocating core, with interrupts excluded in task context.
// Preserve the first fault before requesting stop. Never free a live source.
static void mode0_fail(enum mode0_fault reason)
{
    // The bridge and DMA have separate interrupt sources. Claim the first
    // fault before touching its snapshot, even if one interrupts the other.
    enum mode0_phase interrupted = atomic_exchange(&m0.phase, M0_FAILED);
    if (interrupted == M0_FAILED) return;
    m0.fault_phase = interrupted;
    m0.fault = reason;
    if (m0.items && !m0.frame_ok) mode0_snapshot(m0.frozen);
    dw_gdma_ll_channel_enable(DW_GDMA_LL_GET_HW(0), m0.id, false);
    mode0_output(false);
}

uint32_t mode0_irq_enter(void *channel)
{
    if (m0.phase != M0_LIVE || channel != m0.panel->dma_chan) return 0;
    // The selector returned to the IDF hook is independent of counter wrap.
    m0.dispatcher_entry = esp_cpu_get_cycle_count();
    return 1;
}

void mode0_irq_status(uint32_t status)
{
    if (m0.phase != M0_LIVE) return;
    m0.raw = status;
    if (status & DW_GDMA_LL_CHANNEL_EVENT_SHADOWREG_OR_LLI_INVALID_ERR) mode0_fail(M0_INVALID);
    else if (status & M0_BUS_ERRORS) mode0_fail(M0_DMA_ERROR);
}

void mode0_irq_leave(uint32_t selector)
{
    (void)selector;
}

static bool mode0_on_underrun(void)
{
    if (m0.phase == M0_LIVE) {
        ++m0.underruns;
        mode0_fail(M0_UNDERRUN);
        return true;
    }
    return m0.phase != M0_REF && m0.phase != M0_RESTORING;
}

static bool mode0_on_invalid(dw_gdma_channel_handle_t ch,
                             const dw_gdma_break_event_data_t *event, void *ctx)
{
    (void)event;
    (void)ctx;
    if (m0.phase == M0_LIVE && ch == m0.panel->dma_chan) mode0_fail(M0_INVALID);
    return false;
}

static void mode0_refill(void)
{
    if (!xPortInIsrContext()) { mode0_fail(M0_IRQ_CONTEXT); return; }
    if (m0.published || !m0.primed || !(m0.raw & DW_GDMA_LL_CHANNEL_EVENT_BLOCK_TFR_DONE) ||
        (m0.raw & DW_GDMA_LL_CHANNEL_EVENT_DMA_TFR_DONE)) {
        mode0_fail(M0_ORDER);
        return;
    }
    struct mode0_lli_snapshot old = mode0_observe(0);
    struct mode0_lli_snapshot next = mode0_observe(2);
    m0.old_reader = old;
    m0.new_reader_before = next;
    if ((old.status & (M0_DONE | M0_FRAME)) != M0_DONE || (old.control & (M0_LAST | M0_VALID)) ||
        (next.control & (M0_LAST | M0_VALID)) != M0_LAST || next.status) {
        mode0_fail(M0_WRITEBACK);
        return;
    }
    // A fresh DONE observed *after* arm transfers ownership only for the
    // exact programmed source. The middle descriptor reads immutable memory.
    if (old.source != (uint32_t)(uintptr_t)m0.slot || next.source != old.source ||
        old.block_size != M0_WORDS - 1 || next.block_size != old.block_size) {
        mode0_fail(M0_ADDRESS);
        return;
    }
    if (mode0_bridge_underrun()) { mode0_on_underrun(); return; }
    m0.irq_entry = m0.dispatcher_entry;
    m0.in_irq = true;
    m0.retired_at = esp_cpu_get_cycle_count();
    MODE0_DMA_FENCE();
    m0.first_store_at = esp_cpu_get_cycle_count();
    memcpy(m0.slot + M0_MARGIN, m0.bottom, M0_PIXELS);
    ++m0.fills;
    if (esp_cache_msync(m0.slot, M0_SLOT_BYTES, ESP_CACHE_MSYNC_FLAG_DIR_C2M) != ESP_OK) {
        mode0_fail(M0_SYNC);
        return;
    }
    // HW may have prefetched an invalid last LLI. Its valid re-fetch must
    // see all the new pixel bytes. A real INVALID interrupt fails the trial.
    MODE0_DMA_FENCE();
    m0.items[2].ctrl_hi.val = next.control | M0_VALID;
    MODE0_DMA_FENCE();
    m0.published_at = esp_cpu_get_cycle_count();
    m0.published = true;
}

static bool mode0_on_block(dw_gdma_channel_handle_t ch,
                           const dw_gdma_trans_done_event_data_t *event, void *ctx)
{
    (void)event;
    (void)ctx;
    if (m0.phase != M0_LIVE || ch != m0.panel->dma_chan) return false;
    portENTER_CRITICAL_ISR(&mode0_control);
    if (m0.phase == M0_LIVE) mode0_refill();
    portEXIT_CRITICAL_ISR(&mode0_control);
    return false;
}

static esp_err_t mode0_prepare(esp_lcd_dpi_panel_t *panel)
{
    const uint8_t *fb = panel->fbs[panel->cur_fb_index];
    m0.slot = heap_caps_aligned_calloc(128, 1, M0_SLOT_BYTES,
                                       MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA | MALLOC_CAP_8BIT);
    if (!m0.slot) return ESP_ERR_NO_MEM;
    memcpy(m0.slot, fb, M0_BYTES);
    memcpy(m0.bottom, fb + (M0_ROWS - 1) * M0_BYTES + M0_MARGIN, M0_PIXELS);
    esp_err_t err = esp_cache_msync(m0.slot, M0_SLOT_BYTES, ESP_CACHE_MSYNC_FLAG_DIR_C2M);
    if (err != ESP_OK) return err;
    // Capture what DMA can read, without relying on the CPU's cached alias.
    MODE0_DMA_FENCE();
    memcpy(m0.before, (const void *)CACHE_LL_L2MEM_NON_CACHE_ADDR(m0.slot), M0_BYTES);

    dw_gdma_link_list_config_t list = {.num_items = 3, .link_type = DW_GDMA_LINKED_LIST_TYPE_SINGLY};
    err = dw_gdma_new_link_list(&list, &m0.list);
    if (err != ESP_OK) return err;
    m0.items = dw_gdma_link_list_get_item(m0.list, 0);
    // Match esp_lcd_panel_dpi.c's existing DMA-controlled RGB888 transfer.
    // Only lengths, sources, and end/interrupt/ownership markers differ.
    dw_gdma_block_transfer_config_t cfg = {
        .src = {.burst_mode = DW_GDMA_BURST_MODE_INCREMENT, .burst_items = DW_GDMA_BURST_ITEMS_512,
                .burst_len = 16, .width = DW_GDMA_TRANS_WIDTH_64},
        .dst = {.addr = MIPI_DSI_BRG_MEM_BASE, .burst_mode = DW_GDMA_BURST_MODE_FIXED,
                .burst_items = DW_GDMA_BURST_ITEMS_256, .burst_len = 16, .width = DW_GDMA_TRANS_WIDTH_64},
    };
    for (unsigned i = 0; i < 3; ++i) {
        dw_gdma_lli_handle_t item = dw_gdma_link_list_get_item(m0.list, i);
        cfg.src.addr = (uint32_t)(uintptr_t)(i == 1 ? fb + M0_BYTES : m0.slot);
        cfg.size = i == 1 ? M0_MIDDLE_WORDS : M0_WORDS;
        err = dw_gdma_lli_config_transfer(item, &cfg);
        if (err != ESP_OK) return err;
        m0.items[i].status_hi.val = 0;
        m0.items[i].status_lo.val = 0;
        dw_gdma_ll_lli_set_block_markers(item, i == 0, i == 2, i != 2);
    }
    MODE0_DMA_FENCE();
    mode0_snapshot(m0.armed);
    for (unsigned i = 0; i < 3; ++i) {
        const struct mode0_lli_snapshot *s = &m0.armed[i];
        uint32_t source = (uint32_t)(uintptr_t)(i == 1 ? fb + M0_BYTES : m0.slot);
        if (s->source != source || s->block_size != (i == 1 ? M0_MIDDLE_WORDS : M0_WORDS) - 1 ||
            s->status || s->count || (s->control & (M0_LAST | M0_VALID)) != (i == 2 ? M0_LAST : M0_VALID))
            return ESP_ERR_INVALID_STATE;
    }
    m0.primed = true;
    return ESP_OK;
}

// The IRQ checks CHEN at each frame boundary. In its usual, already-idle
// case it can switch lists immediately. If HW is still stopping, the task
// waits with output gated and makes the same positive observation before
// it can install a new list. Never rearm either list across a live reader.
static void mode0_switch_when_stopped(void)
{
    if (!mode0_stopped()) return;
    esp_lcd_dpi_panel_t *panel = m0.panel;
    dsi_brg_dev_t *brg = panel->bus->hal.bridge;
    dw_gdma_dev_t *hw = DW_GDMA_LL_GET_HW(0);
    bool live = m0.phase == M0_QUIET;
    if (!live && m0.phase != M0_FINISHED) return;
    dw_gdma_link_list_handle_t list = live ? m0.list : panel->link_lists[panel->cur_fb_index];
    if (!live) {
        m0.stopped = true;
        dw_gdma_ll_lli_set_block_markers(dw_gdma_link_list_get_item(list, 0), false, true, true);
    }
    // The reference uses the same DMA-owned channel and bridge flow mode.
    mipi_dsi_brg_ll_set_multi_block_number(brg, live ? 3 : 1);
    mipi_dsi_brg_ll_update_dpi_config(brg);
    if (brg->dma_flow_ctrl.dsi_dma_flow_controller != MIPI_DSI_LL_FLOW_CONTROLLER_DMA ||
        brg->dma_flow_ctrl.dma_flow_multiblk_num != (live ? 3 : 1) ||
        brg->dma_frame_interval.dma_multiblk_en != live ||
        hw->ch[m0.id].cfg1.tt_fc != DW_GDMA_LL_FLOW_M2P_DMAC) {
        mode0_fail(M0_FLOW);
        return;
    }
    uint32_t error_mask = M0_BUS_ERRORS;
    // IDF already enables status generation for all channel events. Signal
    // AXI/LLI faults as well, including one which occurs without a later EOF.
    dw_gdma_ll_channel_enable_intr_propagation(hw, m0.id, error_mask, live);
    if (live) {
        dw_gdma_ll_channel_clear_intr(hw, m0.id, error_mask | DW_GDMA_LL_CHANNEL_EVENT_SHADOWREG_OR_LLI_INVALID_ERR);
        mipi_dsi_brg_ll_clear_interrupt_status(brg, MIPI_DSI_BRG_LL_EVENT_UNDERRUN);
    }
    MODE0_DMA_FENCE();
    if (dw_gdma_channel_use_link_list(panel->dma_chan, list) != ESP_OK) {
        mode0_fail(M0_SETUP);
        return;
    }
    m0.phase = live ? M0_LIVE : M0_RESTORING;
    if (live) m0.started = true;
    dw_gdma_ll_channel_enable(hw, m0.id, true);
    mode0_output(true);
}

static bool mode0_on_frame(esp_lcd_dpi_panel_t *panel)
{
    enum mode0_phase phase = m0.phase;
    if (phase == M0_REF || panel != m0.panel) return false;
    if (phase == M0_RESTORING) {
        m0.restored = true;
        m0.phase = M0_REF;
        return false;   // IDF can now refresh its original reference normally.
    }
    if (phase != M0_DRAIN && phase != M0_LIVE) return true;
    portENTER_CRITICAL_ISR(&mode0_control);
    if (phase == M0_DRAIN) {
        m0.phase = M0_QUIET; // suppress IDF automatic reference rearm
    } else if (m0.phase == M0_LIVE) {
        mode0_snapshot(m0.frozen);
        const struct mode0_lli_snapshot *bottom = &m0.frozen[2];
        if (mode0_bridge_underrun()) mode0_on_underrun();
        else if (!xPortInIsrContext() || !m0.published || m0.fills != 1 ||
                 !(m0.raw & DW_GDMA_LL_CHANNEL_EVENT_DMA_TFR_DONE)) mode0_fail(M0_ORDER);
        else if ((bottom->status & (M0_DONE | M0_FRAME)) != (M0_DONE | M0_FRAME) ||
                 (bottom->control & (M0_LAST | M0_VALID)) != M0_LAST ||
                 (m0.frozen[1].control & M0_VALID)) mode0_fail(M0_WRITEBACK);
        else if (bottom->source != m0.old_reader.source ||
                 bottom->block_size != M0_WORDS - 1) mode0_fail(M0_ADDRESS);
        else {
            m0.frame_at = esp_cpu_get_cycle_count();
            m0.frame_ok = true;
            m0.phase = M0_FINISHED;
        }
    }
    if (m0.phase == M0_FINISHED || m0.phase == M0_QUIET) {
        if (mode0_stopped()) mode0_switch_when_stopped();
        else mode0_output(false);
    }
    portEXIT_CRITICAL_ISR(&mode0_control);
    return true;
}

esp_err_t mode0_driver_run(esp_lcd_panel_handle_t handle)
{
    if (!handle || xPortGetCoreID() != 1 || m0.invoked) return ESP_ERR_INVALID_STATE;
    esp_lcd_dpi_panel_t *panel = __containerof(handle, esp_lcd_dpi_panel_t, base);
    if (panel->h_pixels != 848 || panel->v_pixels != M0_ROWS || panel->bits_per_pixel != 24 ||
        panel->fb_size != M0_BYTES * M0_ROWS || panel->num_fbs != 1 || panel->fbcpy_handle)
        return ESP_ERR_NOT_SUPPORTED;
    m0.invoked = true;
    m0.panel = panel;
    esp_err_t err = dw_gdma_channel_get_id(panel->dma_chan, &m0.id);
    if (err == ESP_OK) err = mode0_prepare(panel);
    if (err != ESP_OK) {
        m0.fault = M0_SETUP;
        return err; // the normal reference is still refreshing its own buffer
    }
    m0.phase = M0_DRAIN;
    const int64_t deadline = esp_timer_get_time() + 300000;
    while (m0.phase != M0_FAILED && m0.phase != M0_REF) {
        vTaskDelay(1);
        portENTER_CRITICAL(&mode0_control);
        if (m0.phase == M0_QUIET || m0.phase == M0_FINISHED)
            mode0_switch_when_stopped();
        if (m0.phase != M0_REF && m0.phase != M0_FAILED && esp_timer_get_time() >= deadline) {
            enum mode0_fault reason = m0.phase == M0_DRAIN || m0.phase == M0_QUIET ? M0_REF_STOP :
                                      m0.phase == M0_FINISHED ? M0_STOP : M0_TIMEOUT;
            mode0_fail(reason);
        }
        portEXIT_CRITICAL(&mode0_control);
    }
    if (m0.phase == M0_FAILED) {
        const int64_t stop_deadline = esp_timer_get_time() + 100000;
        while (!mode0_stopped() && esp_timer_get_time() < stop_deadline) vTaskDelay(1);
        m0.stopped = mode0_stopped();
        return ESP_FAIL;
    }
    return m0.frame_ok && m0.stopped && m0.restored ? ESP_OK : ESP_ERR_INVALID_STATE;
}

static void mode0_print_lli(const char *when, unsigned index, struct mode0_lli_snapshot s)
{
    printf("MODE0_LLI {\"when\":\"%s\",\"index\":%u,\"source\":%" PRIu32
           ",\"block_size\":%" PRIu32 ",\"control\":%" PRIu32 ",\"status\":%" PRIu32
           ",\"count\":%" PRIu32 "}\n",
           when, index, s.source, s.block_size, s.control, s.status, s.count);
}

static void mode0_print_slot(const char *when, const uint8_t *bytes)
{
    static const char digits[] = "0123456789abcdef";
    char chunk[129];
    printf("MODE0_SLOT %s ", when);
    for (unsigned pos = 0; pos < M0_BYTES;) {
        unsigned n = MIN(64, M0_BYTES - pos);
        for (unsigned i = 0; i < n; ++i) {
            uint8_t value = bytes[pos++];
            chunk[2 * i] = digits[value >> 4];
            chunk[2 * i + 1] = digits[value & 15];
        }
        chunk[2 * n] = 0;
        fputs(chunk, stdout);
    }
    putchar('\n');
}

void mode0_driver_report(void)
{
    uint32_t elapsed = m0.published ? m0.published_at - m0.irq_entry : 0;
    unsigned mhz = CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ;
    printf("MODE0_RESULT {\"fault\":\"%s\",\"phase_at_fault\":%u,\"primed\":%u,"
           "\"started\":%u,\"in_irq\":%u,\"fills\":%" PRIu32 ",\"published\":%u,"
           "\"frame_ok\":%u,\"live_stopped\":%u,\"reference_restored\":%u,"
           "\"underruns\":%" PRIu32 ",\"raw\":%" PRIu32 ",\"cpu_mhz\":%u,"
           "\"irq_entry\":%" PRIu32 ",\"retired_at\":%" PRIu32 ",\"first_store_at\":%" PRIu32
           ",\"published_at\":%" PRIu32 ",\"frame_at\":%" PRIu32 ",\"refill_cycles\":%" PRIu32
           ",\"refill_us\":%u.%03u}\n",
           mode0_fault_names[m0.fault], (unsigned)m0.fault_phase, (unsigned)m0.primed,
           (unsigned)m0.started, (unsigned)m0.in_irq, m0.fills, (unsigned)m0.published,
           (unsigned)m0.frame_ok, (unsigned)m0.stopped, (unsigned)m0.restored,
           m0.underruns, m0.raw, mhz, m0.irq_entry, m0.retired_at, m0.first_store_at,
           m0.published_at, m0.frame_at, elapsed, (unsigned)(elapsed / mhz),
           (unsigned)((elapsed % mhz) * 1000 / mhz));
    if (m0.items) {
        for (unsigned i = 0; i < 3; ++i) mode0_print_lli("armed", i, m0.armed[i]);
        mode0_print_lli("retire", 0, m0.old_reader);
        mode0_print_lli("before_refill", 2, m0.new_reader_before);
        for (unsigned i = 0; i < 3; ++i) mode0_print_lli("frozen", i, m0.frozen[i]);
    }
    if (m0.primed) mode0_print_slot("before", m0.before);
    if (m0.started && m0.stopped) {
        MODE0_DMA_FENCE();
        mode0_print_slot("after", (const uint8_t *)CACHE_LL_L2MEM_NON_CACHE_ADDR(m0.slot));
    }
    fflush(stdout);
}
