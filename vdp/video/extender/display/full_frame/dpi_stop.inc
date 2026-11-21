// IDF 5.5.5, ESP32-P4: the stock single-descriptor EOF handler rearms the
// channel before notifying the panel user. Drain one complete frame here,
// before rearm. Keep the clock, IRQ, descriptors and pixel buffers alive
// until the hardware channel enable bit also clears. Use only with the
// core-1-owned full-frame panel. Retire when upstream provides a joined stop.
enum { DPI_IDLE, DPI_RUNNING, DPI_DRAINING, DPI_EOF };

esp_err_t agon_dpi_stop(esp_lcd_panel_handle_t panel)
{
    esp_lcd_dpi_panel_t *dpi = __containerof(panel, esp_lcd_dpi_panel_t, base);
    unsigned expected = DPI_RUNNING;
    atomic_compare_exchange_strong(&dpi->stop_state, &expected, DPI_DRAINING);
    if (expected == DPI_IDLE) return ESP_OK; // construction failed before DMA start

    int channel;
    ESP_RETURN_ON_ERROR(dw_gdma_channel_get_id(dpi->dma_chan, &channel), TAG, "DMA channel");
    const TickType_t start = xTaskGetTickCount();
    do {
        if (atomic_load(&dpi->stop_state) == DPI_EOF &&
            !(DW_GDMA_LL_GET_HW(0)->chen0.val & (1U << channel))) {
            return ESP_OK;
        }
        vTaskDelay(1);
    } while (xTaskGetTickCount() - start < pdMS_TO_TICKS(100));
    // Timeout retains the complete old panel. It never grants permission to free.
    return ESP_ERR_TIMEOUT;
}
