#pragma once

#include "esp_err.h"
#include "esp_lcd_types.h"

// The standalone command task runs this once on the reference panel's core.
// The transfer reads two different pattern rows from a single DMA address.
esp_err_t mode0_driver_run(esp_lcd_panel_handle_t panel);
void mode0_driver_report(void);
