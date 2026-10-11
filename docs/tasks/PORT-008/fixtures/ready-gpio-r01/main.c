/* PORT-008 temporary GPIO20 readback probe, not the historical receiver.
 * r04: GPIO20 input-only, sleep off; compare weak internal pull-up off/on/off.
 * Preserve external bias; output stays released/disabled throughout.
 * No PARLIO, transfer, drive-low command, or other GPIO setup.
 * USB s prints live state; all other commands are rejected.
 */
#include <inttypes.h>
#include <stdio.h>
#include "driver/gpio.h"
#include "esp_err.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "soc/soc.h"
#include "soc/gpio_reg.h"
#include "soc/io_mux_reg.h"
#include "soc/hp_system_reg.h"
#include "soc/hp_sys_clkrst_reg.h"
#include "soc/pmu_reg.h"

static const gpio_num_t READY_PIN = GPIO_NUM_20;
static void configure_ready(void)
{
    ESP_ERROR_CHECK(gpio_set_level(READY_PIN, 1));
    const gpio_config_t config = {
        .pin_bit_mask = UINT64_C(1) << READY_PIN,
        .mode = GPIO_MODE_INPUT_OUTPUT_OD,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&config));
    ESP_ERROR_CHECK(gpio_set_level(READY_PIN, 1));
}
static void report(void)
{
    printf("READY_EXTRA hold0=%08"PRIx32" clock_gate=%08"PRIx32
           " iomux_clock=%08"PRIx32" pmu_active=%08"PRIx32"\n",
           REG_READ(HP_SYSTEM_GPIO_O_HOLD_CTRL0_REG),
           REG_READ(GPIO_CLOCK_GATE_REG),
           REG_READ(HP_SYS_CLKRST_PERI_CLK_CTRL26_REG),
           REG_READ(PMU_HP_ACTIVE_HP_SYS_CNTL_REG));
    ESP_ERROR_CHECK(gpio_dump_io_configuration(stdout, UINT64_C(1) << READY_PIN));
    for (int i=0; i<3; ++i) {
        uint32_t mux=REG_READ(IO_MUX_GPIO20_REG);
        uint32_t in=REG_READ(GPIO_IN_REG);
        uint32_t out=REG_READ(GPIO_OUT_REG);
        uint32_t en=REG_READ(GPIO_ENABLE_REG);
        uint32_t pin=REG_READ(GPIO_PIN20_REG);
        uint32_t route=REG_READ(GPIO_FUNC20_OUT_SEL_CFG_REG);
        printf("READY_PROBE sample=%d api=%d raw_in=%08"PRIx32
               " bit20=%"PRIu32" mux=%08"PRIx32" ie=%"PRIu32
               " function=%"PRIu32" sleep_sel=%"PRIu32
               " out=%08"PRIx32" enable=%08"PRIx32
               " pin=%08"PRIx32" route=%08"PRIx32"\n",
               i,gpio_get_level(READY_PIN),in,(in>>20)&1,
               mux,(mux>>FUN_IE_S)&1,(mux>>MCU_SEL_S)&MCU_SEL,
               (mux>>SLP_SEL_S)&1,out,en,pin,route);
        fflush(stdout);
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
void app_main(void)
{
    configure_ready();
    ESP_ERROR_CHECK(gpio_set_direction(READY_PIN, GPIO_MODE_INPUT));
    ESP_ERROR_CHECK(gpio_sleep_sel_dis(READY_PIN));
    puts("READY_PROBE r04: input-only pull-up comparison; s=status; no arm command");
    puts("READY_PHASE internal-pull-up-off-before");
    report();
    ESP_ERROR_CHECK(gpio_pullup_en(READY_PIN));
    vTaskDelay(pdMS_TO_TICKS(20));
    puts("READY_PHASE internal-pull-up-on");
    report();
    ESP_ERROR_CHECK(gpio_pullup_dis(READY_PIN));
    vTaskDelay(pdMS_TO_TICKS(20));
    puts("READY_PHASE internal-pull-up-off-after");
    report();
    while (1) {
        int c=getchar();
        if (c=='s' || c=='S') report();
        else if (c==EOF) vTaskDelay(pdMS_TO_TICKS(10));
        else if (c!='\r' && c!='\n') puts("Command rejected; READY remains input-only");
    }
}
