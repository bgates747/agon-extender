/* Host registers stand in for ESP-IDF 5.5.5 and DMA writeback. The test runs the
 * device code itself. No host value models display timing or FIFO lookahead. */
#include <assert.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../mode0/mode0_pattern.h"

enum { LINE = 848 * 3, HEIGHT = 480, FRAME = LINE * HEIGHT };
#define HOST_VALID (UINT32_C(1) << 31)
#define HOST_LAST  (UINT32_C(1) << 30)
#define HOST_IRQ   (UINT32_C(1) << 26)
#define HOST_DONE  (UINT32_C(1) << 30)
#define HOST_END   (UINT32_C(1) << 31)

typedef union {
    uint32_t val, sar0, block_ts, tt_fc;
    struct { uint32_t dsi_dma_flow_controller:1, :3, dma_flow_multiblk_num:4; };
    struct { uint32_t dma_multiblk_en:1; };
} fake_reg;
typedef struct {
    fake_reg sar_lo, sar_hi, dar_lo, dar_hi, block_ts_lo, reserved, llp_lo, llp_hi;
    fake_reg ctrl_lo, ctrl_hi, sstat, dstat, status_lo, status_hi, pad[2];
} __attribute__((aligned(64))) dw_gdma_link_list_item_t;
typedef dw_gdma_link_list_item_t *dw_gdma_link_list_handle_t;
typedef dw_gdma_link_list_item_t *dw_gdma_lli_handle_t;
typedef void *dw_gdma_channel_handle_t;
typedef void dw_gdma_trans_done_event_data_t, dw_gdma_break_event_data_t;
typedef struct { fake_reg chen0; struct { fake_reg cfg1; } ch[1]; } dw_gdma_dev_t;
typedef struct {
    fake_reg dma_flow_ctrl, dma_frame_interval, int_raw;
} dsi_brg_dev_t;
typedef struct { struct { dsi_brg_dev_t *bridge; } hal; } fake_bus;
typedef int esp_lcd_panel_t;
typedef esp_lcd_panel_t *esp_lcd_panel_handle_t;
typedef struct {
    esp_lcd_panel_t base;
    int h_pixels, v_pixels, bits_per_pixel, num_fbs, cur_fb_index;
    size_t fb_size;
    void *fbcpy_handle;
    uint8_t *fbs[1];
    dw_gdma_link_list_handle_t link_lists[1];
    dw_gdma_channel_handle_t dma_chan;
    fake_bus *bus;
} esp_lcd_dpi_panel_t;
typedef int esp_err_t, portMUX_TYPE;
typedef struct { int num_items, link_type; } dw_gdma_link_list_config_t;
typedef struct { uint32_t addr; int burst_mode, burst_items, burst_len, width; } fake_endpoint;
typedef struct { fake_endpoint src, dst; size_t size; } dw_gdma_block_transfer_config_t;

#define MIN(a,b) ((a) < (b) ? (a) : (b))
#define IRAM_ATTR
#define DRAM_ATTR
#define __containerof(p,t,f) ((t *)((char *)(p) - offsetof(t,f)))
#define portMUX_INITIALIZER_UNLOCKED 0
#define portENTER_CRITICAL(x) ((void)(x))
#define portEXIT_CRITICAL(x) ((void)(x))
#define portENTER_CRITICAL_ISR(x) ((void)(x))
#define portEXIT_CRITICAL_ISR(x) ((void)(x))
#define DW_GDMA_LL_GET_HW(unit) (&gdma)
#define CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ 360
enum {
    ESP_OK = 0, ESP_FAIL = -1, ESP_ERR_INVALID_STATE = 1, ESP_ERR_NOT_SUPPORTED,
    ESP_ERR_NO_MEM, ESP_ERR_TIMEOUT, ESP_ERR_INVALID_ARG, ESP_CACHE_MSYNC_FLAG_DIR_C2M,
    MALLOC_CAP_INTERNAL = 1, MALLOC_CAP_DMA = 2, MALLOC_CAP_8BIT = 4,
    DW_GDMA_LINKED_LIST_TYPE_SINGLY, DW_GDMA_TRANS_WIDTH_64,
    DW_GDMA_BURST_ITEMS_512, DW_GDMA_BURST_ITEMS_256, DW_GDMA_BURST_MODE_INCREMENT,
    DW_GDMA_BURST_MODE_FIXED, MIPI_DSI_BRG_MEM_BASE, MIPI_DSI_BRG_LL_EVENT_UNDERRUN,
    DW_GDMA_LL_FLOW_M2P_DMAC = 1, MIPI_DSI_LL_FLOW_CONTROLLER_DMA = 0,
};
static _Alignas(64) uint8_t guarded_frame[FRAME + 256], expected[FRAME], fetched[FRAME], visible_slot[LINE];
#define reference (guarded_frame + 128)
static _Alignas(128) uint8_t arena[16384];
static size_t used;
static uint8_t *slot_addr;
static const char *scenario;
static bool is_isr, live, retired, output_on;
static unsigned cycle, current_time, copies, cleans, fence_count, guard_fence, fetch_bytes;
static dw_gdma_dev_t gdma;
static dsi_brg_dev_t bridge;
static fake_bus bus = {.hal.bridge = &bridge};
static dw_gdma_link_list_item_t reference_lli, live_lli[3];
static dw_gdma_link_list_handle_t selected;
static esp_lcd_dpi_panel_t panel = {
    .h_pixels = 848, .v_pixels = 480, .bits_per_pixel = 24, .num_fbs = 1, .fb_size = FRAME,
    .fbs = {reference}, .link_lists = {&reference_lli}, .dma_chan = &gdma, .bus = &bus,
};
static bool testing(const char *name) { return strcmp(scenario, name) == 0; }
static uint32_t addr(const void *p) { assert((uintptr_t)p <= UINT32_MAX); return (uint32_t)(uintptr_t)p; }
static unsigned esp_cpu_get_cycle_count(void) { return ++cycle; }
static int64_t esp_timer_get_time(void) { return current_time; }
static int xPortGetCoreID(void) { return 1; }
static bool xPortInIsrContext(void) { return is_isr; }
static void vTaskDelay(unsigned ticks);
static void *heap_caps_aligned_calloc(size_t alignment, size_t n, size_t size, unsigned caps)
{
    (void)caps;
    assert(alignment && (alignment & (alignment - 1)) == 0);
    uintptr_t base = (uintptr_t)arena;
    uintptr_t next = (base + used + alignment - 1) & ~(uintptr_t)(alignment - 1);
    used = (size_t)(next - base);
    assert(used + n * size <= sizeof arena);
    uint8_t *p = arena + used;
    assert(((uintptr_t)p & (alignment - 1)) == 0);
    used += n * size;
    memset(p, 0, n * size);
    return p;
}
static int dw_gdma_channel_get_id(void *ch, int *id) { assert(ch == &gdma); *id = 0; return ESP_OK; }
static int dw_gdma_new_link_list(const dw_gdma_link_list_config_t *cfg, dw_gdma_link_list_handle_t *list)
{
    assert(cfg->num_items == 3 && cfg->link_type == DW_GDMA_LINKED_LIST_TYPE_SINGLY);
    *list = live_lli;
    for (int i = 0; i < 3; ++i) {
        live_lli[i].status_hi.val = HOST_DONE;
        live_lli[i].status_lo.val = 77;
    }
    for (unsigned i=0; i<2; ++i) live_lli[i].llp_lo.val = addr(&live_lli[i+1]);
    return ESP_OK;
}
static dw_gdma_lli_handle_t dw_gdma_link_list_get_item(dw_gdma_link_list_handle_t list, int i)
{ return list+i; }
static int dw_gdma_channel_use_link_list(void *ch, dw_gdma_link_list_handle_t list)
{
    assert(ch == &gdma && !gdma.chen0.val);
    selected = list;
    return ESP_OK;
}
static int dw_gdma_lli_config_transfer(dw_gdma_lli_handle_t item, const dw_gdma_block_transfer_config_t *cfg)
{
    assert(cfg->src.width == DW_GDMA_TRANS_WIDTH_64 && cfg->dst.width == DW_GDMA_TRANS_WIDTH_64);
    item->sar_lo.val = cfg->src.addr;
    item->dar_lo.val = cfg->dst.addr;
    item->block_ts_lo.val = cfg->size - 1;
    return ESP_OK;
}
static void dw_gdma_ll_lli_set_block_markers(dw_gdma_lli_handle_t item, bool irq, bool last, bool valid)
{
    uint32_t markers = (irq ? HOST_IRQ : 0) | (last ? HOST_LAST : 0) | (valid ? HOST_VALID : 0);
    item->ctrl_hi.val = (item->ctrl_hi.val & ~(HOST_IRQ|HOST_LAST|HOST_VALID)) | markers;
}
static void dw_gdma_ll_channel_enable(dw_gdma_dev_t *d, int id, bool enable)
{
    assert(d == &gdma && id == 0);
    d->chen0.val = enable;
    if (enable) live = selected == live_lli;
}
static void mipi_dsi_brg_ll_set_multi_block_number(dsi_brg_dev_t *b, unsigned num)
{
    b->dma_flow_ctrl.dma_flow_multiblk_num = num;
    b->dma_frame_interval.dma_multiblk_en = num > 1;
}
static void mipi_dsi_brg_ll_enable_dpi_output(dsi_brg_dev_t *b,bool enable)
{ assert(b == &bridge); output_on = enable; }
static void mipi_dsi_brg_ll_update_dpi_config(dsi_brg_dev_t *b) { assert(b == &bridge); }
static void mipi_dsi_brg_ll_clear_interrupt_status(dsi_brg_dev_t *b,unsigned raw)
{ assert(b == &bridge); b->int_raw.val &= ~raw; }
#define DW_GDMA_LL_CHANNEL_EVENT_BLOCK_TFR_DONE 1u
#define DW_GDMA_LL_CHANNEL_EVENT_DMA_TFR_DONE 2u
#define DW_GDMA_LL_CHANNEL_EVENT_SHADOWREG_OR_LLI_INVALID_ERR (1u << 13)
static void dw_gdma_ll_channel_enable_intr_propagation(dw_gdma_dev_t *d, int id, unsigned mask, bool enable)
{ assert(d == &gdma && !id && mask); (void)enable; }
static void dw_gdma_ll_channel_clear_intr(dw_gdma_dev_t *d, int id, unsigned mask)
{ assert(d == &gdma && !id && mask); }
static uint32_t mipi_dsi_brg_ll_get_interrupt_status(dsi_brg_dev_t *b) { return b->int_raw.val; }
static void *dma_view(const void *cpu)
{
    assert(cpu == slot_addr);
    return visible_slot;
}
#define CACHE_LL_L2MEM_NON_CACHE_ADDR(p) ((uintptr_t)dma_view(p))

static int esp_cache_msync(void *ptr, size_t bytes, unsigned flags)
{
    assert(bytes == 2560 && flags == ESP_CACHE_MSYNC_FLAG_DIR_C2M);
    if (!slot_addr) slot_addr = ptr;
    assert(ptr == slot_addr);
    if (is_isr) {
        assert(retired && copies == 1 && !(live_lli[2].ctrl_hi.val & HOST_VALID));
        assert(!memcmp(ptr, expected + FRAME - LINE, LINE));
        if (testing("cache-error")) return ESP_FAIL;
        guard_fence = fence_count;
    }
    memcpy(visible_slot, ptr, LINE);
    ++cleans;
    return ESP_OK;
}
static void *observe_copy(void *dest, const void *source, size_t len)
{
    if (live && slot_addr && (uintptr_t)dest >= (uintptr_t)slot_addr &&
        (uintptr_t)dest < (uintptr_t)slot_addr + LINE) {
        assert(is_isr && retired && copies == 0);
        assert(live_lli[0].status_hi.val == HOST_DONE && !(live_lli[0].ctrl_hi.val & HOST_VALID));
        assert(!(live_lli[2].ctrl_hi.val & HOST_VALID) && !live_lli[2].status_hi.val);
        assert(dest == slot_addr + 104 * 3 && len == 640 * 3);
        assert(!memcmp(visible_slot, expected, LINE));
        ++copies;
    }
    return memcpy(dest, source, len);
}
static void host_fence(void)
{
    atomic_thread_fence(memory_order_seq_cst);
    if (copies && guard_fence && (live_lli[2].ctrl_hi.val & HOST_VALID)) {
        // A cache clean and at least one ordering fence must precede VALID.
        assert(cleans == 2 && guard_fence < fence_count);
    }
    ++fence_count;
}
#define MODE0_DMA_FENCE() host_fence()
#define MODE0_HOST_TEST
#define memcpy observe_copy
#include "../mode0/mode0_runtime.inc"
#undef memcpy

static void consume(unsigned i)
{
    dw_gdma_link_list_item_t *item = &live_lli[i];
    assert(item->ctrl_hi.val & HOST_VALID);
    size_t bytes = 8u * ((size_t)item->block_ts_lo.val + 1);
    assert(fetch_bytes + bytes <= FRAME);
    const void *source = (const void *)(uintptr_t)item->sar_lo.val;
    if (source == slot_addr) {
        assert(bytes == LINE);
        source = visible_slot;   // bus sees the last cleaned generation only
    }
    memcpy(fetched + fetch_bytes, source, bytes);
    fetch_bytes += bytes;
    item->ctrl_hi.val &= ~HOST_VALID;
    item->status_hi.val = HOST_DONE | (i == 2 ? HOST_END : 0);
}
static void irq(unsigned flags, bool block, bool frame)
{
    is_isr = !testing("task-context");
    unsigned selector = mode0_irq_enter(panel.dma_chan);
    if (selector) mode0_irq_status(flags);
    if (flags & DW_GDMA_LL_CHANNEL_EVENT_SHADOWREG_OR_LLI_INVALID_ERR)
        mode0_on_invalid(panel.dma_chan, NULL, &panel);
    if (block) mode0_on_block(panel.dma_chan, NULL, &panel);
    if (frame) {
        bool suppress = mode0_on_frame(&panel);
        assert(suppress || selected == &reference_lli);
    }
    if (selector) mode0_irq_leave(selector);
    is_isr = false;
}
static void drive_trial(void)
{
    assert(selected == live_lli && !fetch_bytes);
    assert(bridge.dma_flow_ctrl.dma_flow_multiblk_num == 3);
    assert((addr(slot_addr) & 127u) == 0);
    assert(live_lli[0].sar_lo.val == addr(slot_addr) && live_lli[2].sar_lo.val == addr(slot_addr));
    assert(live_lli[1].sar_lo.val == addr(reference + LINE));
    assert(live_lli[0].block_ts_lo.val == 317 && live_lli[1].block_ts_lo.val == 152003 &&
           live_lli[2].block_ts_lo.val == 317);
    unsigned flags = HOST_VALID | HOST_IRQ | HOST_LAST;
    assert((live_lli[0].ctrl_hi.val & flags) == (HOST_VALID | HOST_IRQ));
    assert((live_lli[1].ctrl_hi.val & flags) == HOST_VALID);
    assert((live_lli[2].ctrl_hi.val & flags) == HOST_LAST);
    for (int i=0; i<3; ++i) assert(live_lli[i].status_hi.val == 0);
    assert(cleans == 1 && !memcmp(visible_slot, expected, LINE));
    if (testing("cycle-wrap")) cycle = UINT32_MAX - 2;
    if (testing("early-frame")) { irq(2, false, true); return; }
    if (testing("early")) { irq(1, true, false); return; }
    consume(0);
    retired = true;
    if (testing("stale-valid")) live_lli[0].ctrl_hi.val |= HOST_VALID;
    if (testing("early-valid")) live_lli[2].ctrl_hi.val |= HOST_VALID;
    if (testing("wrong-source")) live_lli[2].sar_lo.val = addr(reference);
    if (testing("underrun")) bridge.int_raw.val |= MIPI_DSI_BRG_LL_EVENT_UNDERRUN;
    unsigned raw = 1u;
    if (testing("invalid")) raw |= DW_GDMA_LL_CHANNEL_EVENT_SHADOWREG_OR_LLI_INVALID_ERR;
    if (testing("dma-error")) raw |= 1u << 5;
    if (testing("coalesced")) raw |= DW_GDMA_LL_CHANNEL_EVENT_DMA_TFR_DONE;
    irq(raw, true, false);
    if (m0.phase != M0_LIVE) return;
    assert(m0.fills == 1 && m0.published && copies == 1 && cleans == 2);
    if (testing("duplicate")) { irq(1, true, false); return; }
    consume(1);
    if (!testing("missing-last")) consume(2);
    // A final block need not fire the optional interrupt; the channel EOF is sufficient.
    gdma.chen0.val = testing("delayed-stop");
    cycle += 1000;
    irq(2, false, true);
}

static void vTaskDelay(unsigned ticks)
{
    (void)ticks;
    current_time += 1000;
    switch (m0.phase) {
    case M0_QUIET:
    case M0_FINISHED:
        assert(testing("delayed-stop") && gdma.chen0.val && !output_on);
        gdma.chen0.val = 0;  // software wasn't allowed to install the next list before this
        break;
    case M0_DRAIN:
        gdma.chen0.val = testing("delayed-stop");
        irq(2, false, true);
        break;
    case M0_LIVE:
        drive_trial();
        break;
    case M0_RESTORING:
        assert(selected == &reference_lli && output_on && gdma.chen0.val);
        irq(2, false, true);
        break;
    default:
        break;
    }
}

int main(int argc, char **argv)
{
    assert(argc == 3);
    FILE *rows = fopen(argv[1], "rb");
    assert(rows && fread(expected, 1, FRAME, rows) == FRAME && fgetc(rows) == EOF);
    fclose(rows);
    scenario = argv[2];
    memset(guarded_frame, 0xe5, sizeof guarded_frame);
    mode0_render_reference(reference);
    assert(!memcmp(reference, expected, FRAME));
    for (int i = 0; i < 128; ++i)
        assert(guarded_frame[i] == 0xe5 && guarded_frame[128+FRAME+i] == 0xe5);
    memset(fetched, 0xee, sizeof fetched);
    gdma.ch[0].cfg1.tt_fc = DW_GDMA_LL_FLOW_M2P_DMAC;
    bridge.dma_flow_ctrl.dsi_dma_flow_controller = MIPI_DSI_LL_FLOW_CONTROLLER_DMA;
    selected = &reference_lli;
    gdma.chen0.val = 1;
    bool success = testing("normal") || testing("cycle-wrap") || testing("delayed-stop");
    assert(mode0_driver_run(&panel.base) == (success ? ESP_OK : ESP_FAIL));
    if (success) {
        assert(m0.phase == M0_REF && m0.frame_ok && m0.restored && m0.fault == M0_OK);
        assert(m0.in_irq && m0.fills == 1 && m0.published && cleans == 2 && copies == 1);
        assert(fetch_bytes == FRAME && !memcmp(fetched, expected, FRAME));
        assert(m0.old_reader.source == m0.frozen[2].source && m0.old_reader.source == addr(slot_addr));
        assert((m0.old_reader.status & HOST_DONE) && !(m0.old_reader.control & HOST_VALID));
        assert(!(m0.new_reader_before.control & HOST_VALID) && m0.new_reader_before.status == 0);
        assert(m0.frozen[2].status == (HOST_END|HOST_DONE) && !(m0.frozen[2].control & HOST_VALID));
        assert(m0.published_at - m0.irq_entry < 100);
        assert(m0.retired_at - m0.irq_entry > 0 && m0.retired_at - m0.irq_entry < 100);
        assert(m0.first_store_at - m0.retired_at > 0 && m0.first_store_at - m0.retired_at < 100);
        assert(m0.published_at - m0.first_store_at > 0 && m0.published_at - m0.first_store_at < 100);
        assert(m0.frame_at - m0.published_at > 1000);
        if (testing("cycle-wrap")) assert(m0.published_at < m0.irq_entry);
    } else {
        assert(m0.phase == M0_FAILED && !gdma.chen0.val && !output_on && !m0.restored);
        enum mode0_fault want = M0_WRITEBACK;
        if (testing("duplicate") || testing("early-frame") || testing("coalesced")) want = M0_ORDER;
        if (testing("task-context")) want = M0_IRQ_CONTEXT;
        if (testing("wrong-source")) want = M0_ADDRESS;
        if (testing("dma-error")) want = M0_DMA_ERROR;
        if (testing("invalid")) want = M0_INVALID;
        if (testing("underrun")) want = M0_UNDERRUN;
        if (testing("cache-error")) want = M0_SYNC;
        assert(m0.fault == want);
        bool filled = testing("duplicate") || testing("missing-last") || testing("cache-error");
        assert(copies == filled && m0.fills == filled);
        bool published = filled && !testing("cache-error");
        assert(m0.published == published && cleans == 1u + published);
        assert(!memcmp(visible_slot, expected + (published ? FRAME - LINE : 0), LINE));
    }
    assert(m0.stopped && !memcmp(m0.before, expected, LINE));
    unsigned before = m0.fills;
    enum mode0_fault fault = m0.fault;
    struct mode0_lli_snapshot record[3];
    memcpy(record, m0.frozen, sizeof record);
    // Late notifications and a second command must leave the first result frozen.
    irq(3, true, true);
    mode0_on_invalid(panel.dma_chan, NULL, &panel);
    mode0_on_underrun();
    assert(mode0_driver_run(&panel.base) == ESP_ERR_INVALID_STATE);
    assert(m0.fills == before && m0.fault == fault && !memcmp(record,m0.frozen,sizeof record));
    mode0_driver_report();
    printf("PASS %-14s fault=%s stores=%u DMA-visible-refills=%u fetched=%u bytes\n",
           scenario, mode0_fault_names[m0.fault], copies, cleans-1, fetch_bytes);
    return 0;
}
