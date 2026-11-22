#pragma once

#include "esp_err.h"
#include "esp_lcd_types.h"

// One standalone trial on the same pinned core that created the reference
// panel. The reference must be scanning before this call. It is restarted
// after successful completion. Diagnostic state lives until the next boot.
esp_err_t pair_driver_run(esp_lcd_panel_handle_t panel);
void pair_driver_report(void);
