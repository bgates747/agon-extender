#pragma once
#include <cstddef>
#include <cstdint>
using esp_err_t=int; using uart_port_t=int; using gpio_num_t=int; using portMUX_TYPE=int;
constexpr int ESP_OK=0,ESP_ERR_TIMEOUT=1,ESP_FAIL=2,UART_NUM_1=1,GPIO_MODE_INPUT=1;
constexpr int GPIO_MATRIX_CONST_ONE_INPUT=0x38,SOC_UART_RX_PIN_IDX=0,SOC_UART_CTS_PIN_IDX=1;
#define UART_PERIPH_SIGNAL(u,p) ((u)*10+(p))
#define portMUX_INITIALIZER_UNLOCKED 0
struct uart_dev_t {};
extern uart_dev_t hardware;
#define UART_LL_GET_HW(u) (&hardware)
int xPortGetCoreID();
void enterCritical(portMUX_TYPE*);void exitCritical(portMUX_TYPE*);
#define taskENTER_CRITICAL(m) enterCritical(m)
#define taskEXIT_CRITICAL(m) exitCritical(m)
esp_err_t uart_wait_tx_done(uart_port_t,int);
esp_err_t uart_get_buffered_data_len(uart_port_t,std::size_t*);
esp_err_t uart_set_pin(uart_port_t,int,int,int,int);
esp_err_t gpio_set_direction(gpio_num_t,int);
void esp_rom_gpio_connect_in_signal(int,int,bool);
std::uint32_t uart_ll_get_rxfifo_len(uart_dev_t*);
bool uart_ll_is_tx_idle(uart_dev_t*);
