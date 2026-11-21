// Host substitutes for HW enable status, the tick clock and the ISR scheduler.
// The Python runner inserts the generated driver's pre-rearm gate here.
#include <stdatomic.h>
#include <stdbool.h>
#include <stdio.h>
#include <assert.h>
typedef unsigned TickType_t;
typedef int esp_err_t;
typedef struct { atomic_uint stop_state; int dma_chan; } esp_lcd_dpi_panel_t;
typedef esp_lcd_dpi_panel_t *esp_lcd_panel_handle_t;
#define __containerof(p,t,f) (p)
#define ESP_OK 0
#define ESP_ERR_TIMEOUT (-1)
#define pdMS_TO_TICKS(n) (n)
#define ESP_RETURN_ON_ERROR(code,tag,msg) do { if ((code) != 0) return -2; } while (0)
static struct { struct { unsigned val; } chen0; } hw;
#define DW_GDMA_LL_GET_HW(id) (&hw)
static esp_lcd_dpi_panel_t panel;
static unsigned tick, eof_at, idle_at, rearms;
static int dw_gdma_channel_get_id(int ch, int *id) { *id = ch; return 0; }
static TickType_t xTaskGetTickCount(void) { return tick; }
static void vTaskDelay(unsigned ticks);
#include "dpi_stop.inc"

static bool completion(esp_lcd_dpi_panel_t *dpi_panel) {
    (void)dpi_panel;
    /* actual EOF gate */
    ++rearms;
    return true;
}
static void vTaskDelay(unsigned ticks) {
    tick += ticks;
    if (tick == eof_at) completion(&panel);
    if (tick == idle_at) hw.chen0.val &= ~(1U << panel.dma_chan);
}
int main(void) {
    panel.dma_chan = 2;
    assert(agon_dpi_stop(&panel) == ESP_OK && tick == 0);
    atomic_store(&panel.stop_state, DPI_RUNNING);
    assert(completion(&panel) && rearms == 1);
    hw.chen0.val = (1U << 2) | (1U << 1);
    eof_at = 2;
    idle_at = 8;
    if (agon_dpi_stop(&panel) != ESP_OK) return 1;
    assert(tick == idle_at && hw.chen0.val == (1U << 1));
    assert(!completion(&panel) && rearms == 1);
    // A stale/clear enable bit alone cannot establish end of transfer.
    atomic_store(&panel.stop_state, DPI_RUNNING);
    assert(agon_dpi_stop(&panel) == ESP_ERR_TIMEOUT);
    // EOF alone cannot release a channel which still reports enabled.
    hw.chen0.val |= 1U << panel.dma_chan;
    eof_at = tick + 1;
    assert(agon_dpi_stop(&panel) == ESP_ERR_TIMEOUT);
    idle_at = tick + 1;
    assert(agon_dpi_stop(&panel) == ESP_OK);
    puts("PASS idle construction, delayed EOF and HW idle, both missing signals, late IRQ, retry");
    return 0;
}
