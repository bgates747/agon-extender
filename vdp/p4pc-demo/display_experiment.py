"""P4PC-001 task-local IDF 5.5.5 override; never edits the SDK checkout.

The public LT8912B display-off operation is unsupported and blanking its HDMI
output would not remove P4 DMA traffic. This bounded diagnostic stops rearming
DMA after a complete frame, retains its buffers, and resumes existing resources.
Remove this override when the SDK supplies an admitted scanout control API.
"""
import shutil


def replace_once(text, before, after):
    if text.count(before) != 1:
        raise SystemExit(f'Unexpected pinned source: {before[:90]}')
    return text.replace(before, after)


def stage_scanout_override(project, idf):
    target = project / 'components/esp_lcd'
    shutil.copytree(idf / 'components/esp_lcd', target)
    cmake=target/'CMakeLists.txt'
    cmake.write_text(replace_once(cmake.read_text(),
        'set(priv_requires "esp_mm" "esp_psram" "esp_pm" "esp_driver_i2s")',
        'set(priv_requires "esp_mm" "esp_psram" "esp_pm" "esp_driver_i2s" "esp_timer")'))
    source = target / 'dsi/esp_lcd_panel_dpi.c'
    text = source.read_text()
    text = '/* P4PC-001: generated task-local scanout override; see display_experiment.py. */\n' + text
    text = replace_once(text, '#include "hal/color_hal.h"',
                        '#include "hal/color_hal.h"\n#include "esp_timer.h"\n#include <stdatomic.h>')
    text = replace_once(text, '    void *user_ctx; // User context for the callback',
                        '    _Atomic bool scanout_enabled;\n    SemaphoreHandle_t scanout_idle_sem;\n'
                        '    void *user_ctx; // User context for the callback')
    begin = text.index('    // restart the DMA transfer, keep refreshing the LCD')
    end = text.index('\n    if (dpi_panel->on_frame_buf_complete)', begin)
    text = text[:begin] + '''    if (dpi_panel->scanout_enabled) {
        // Normal SDK rearm, unchanged while scanout is active.
        dw_gdma_block_markers_t markers = {.is_valid = true, .is_last = true};
        dw_gdma_lli_set_block_markers(dw_gdma_link_list_get_item(link_list, 0), markers);
        dw_gdma_channel_use_link_list(chan, link_list);
        dw_gdma_channel_enable_ctrl(chan, true);
    } else {
        // A whole frame completed: DMA is idle. Disable the downstream demand
        // before acknowledging stop; never abort a live AXI transaction.
        mipi_dsi_hal_context_t *hal = &dpi_panel->bus->hal;
        mipi_dsi_brg_ll_enable_interrupt(hal->bridge, MIPI_DSI_BRG_LL_EVENT_UNDERRUN, false);
        mipi_dsi_host_ll_enable_video_mode(hal->host, false);
        mipi_dsi_brg_ll_enable_dpi_output(hal->bridge, false);
        mipi_dsi_brg_ll_update_dpi_config(hal->bridge);
        BaseType_t woken = pdFALSE;
        xSemaphoreGiveFromISR(dpi_panel->scanout_idle_sem, &woken);
        yield_needed = woken == pdTRUE;
    }
''' + text[end:]
    text = replace_once(text, '    dpi_panel->num_fbs = num_fbs;',
                        '    dpi_panel->num_fbs = num_fbs;\n'
                        '    dpi_panel->scanout_enabled = true;\n'
                        '    dpi_panel->scanout_idle_sem = xSemaphoreCreateBinaryWithCaps(DSI_MEM_ALLOC_CAPS);\n'
                        '    ESP_GOTO_ON_FALSE(dpi_panel->scanout_idle_sem, ESP_ERR_NO_MEM, err, TAG, "no scanout semaphore");')
    text = replace_once(text, '    if (dpi_panel->draw_sem) {',
                        '    if (dpi_panel->scanout_idle_sem) vSemaphoreDeleteWithCaps(dpi_panel->scanout_idle_sem);\n'
                        '    if (dpi_panel->draw_sem) {')
    # The normal direct-buffer path writes back exactly these full-width lines.
    needle = '        esp_cache_msync(cache_sync_start, cache_sync_size, ESP_CACHE_MSYNC_FLAG_DIR_C2M | ESP_CACHE_MSYNC_FLAG_UNALIGNED);'
    # This occurs twice (direct and CPU-copy); instrument only the direct branch.
    location = text.index(needle, text.index('    if (!do_copy)'))
    text = text[:location] + '''        int64_t cache_started = esp_timer_get_time();
''' + text[location:location + len(needle)] + '''
        extern void playground_cache_event(uint64_t elapsed);
        playground_cache_event(esp_timer_get_time() - cache_started);''' + text[location + len(needle):]
    text += '''
/* Main holds the LVGL mutex and pauses animation around this task-local API.
 * It operates on the retained DPI base even though LT8912B wraps base.init.
 * Timeout restores rearming and reports failure; no false headless acceptance. */
esp_err_t playground_scanout_enable(esp_lcd_panel_handle_t panel, bool enable)
{
    ESP_RETURN_ON_FALSE(panel, ESP_ERR_INVALID_ARG, TAG, "missing panel");
    esp_lcd_dpi_panel_t *dpi_panel = __containerof(panel, esp_lcd_dpi_panel_t, base);
    if (enable == dpi_panel->scanout_enabled) return ESP_OK;
    if (enable) {
        dpi_panel->scanout_enabled = true;
        return dpi_panel_init(panel);
    }
    xSemaphoreTake(dpi_panel->scanout_idle_sem, 0);
    dpi_panel->scanout_enabled = false;
    if (xSemaphoreTake(dpi_panel->scanout_idle_sem, pdMS_TO_TICKS(1000)) != pdTRUE) {
        dpi_panel->scanout_enabled = true;
        return ESP_ERR_TIMEOUT;
    }
    return ESP_OK;
}
'''
    source.write_text(text)
