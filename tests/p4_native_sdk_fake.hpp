// Narrow IDF boundary model. Target compilation separately checks real headers.
#pragma once
#include <cstddef>
#include <cstdint>
using gpio_num_t=int;using esp_err_t=int;
constexpr int ESP_OK=0,ESP_FAIL=1,ESP_ERR_INVALID_STATE=2,GPIO_NUM_NC=-1;
constexpr int GPIO_MODE_INPUT=1,GPIO_INTR_ANYEDGE=3;
constexpr int MALLOC_CAP_INTERNAL=1,MALLOC_CAP_DMA=2,MALLOC_CAP_8BIT=4;
constexpr int PARLIO_CLK_SRC_EXTERNAL=1,PARLIO_SHIFT_EDGE_NEG=2;
constexpr int PARLIO_SAMPLE_EDGE_NEG=2,PARLIO_BIT_PACK_ORDER_LSB=0,PARLIO_RX_UNIT_MAX_DATA_WIDTH=16;
#define IRAM_ATTR
using parlio_rx_unit_handle_t=void*;using parlio_tx_unit_handle_t=void*;
using parlio_rx_delimiter_handle_t=void*;
struct parlio_rx_event_data_t {void*delimiter;void*data;std::size_t recv_bytes;};
struct parlio_tx_done_event_data_t {};
struct parlio_rx_event_callbacks_t {bool(*on_receive_done)(void*,parlio_rx_event_data_t const*,void*);};
struct parlio_tx_event_callbacks_t {bool(*on_trans_done)(void*,parlio_tx_done_event_data_t const*,void*);};
struct parlio_tx_unit_config_t {
 int data_gpio_nums[16],clk_src,clk_in_gpio_num,clk_out_gpio_num,valid_gpio_num;
 std::uint32_t input_clk_src_freq_hz,output_clk_freq_hz;
 std::size_t data_width,trans_queue_depth,max_transfer_size;
 int shift_edge,bit_pack_order;
};
struct parlio_transmit_config_t {std::uint32_t idle_value;struct{bool queue_nonblocking;}flags;};
struct parlio_rx_unit_config_t {
 int data_gpio_nums[16],clk_src,clk_in_gpio_num,clk_out_gpio_num,valid_gpio_num;
 std::uint32_t ext_clk_freq_hz,exp_clk_freq_hz;
 std::size_t data_width,trans_queue_depth,max_recv_size,dma_burst_size;
 struct{bool free_clk;}flags;
};
struct parlio_rx_level_delimiter_config_t {
 unsigned valid_sig_line_id;int sample_edge,bit_pack_order;
 struct{bool active_low_en;}flags;
};
struct parlio_receive_config_t {void*delimiter;};
int xPortGetCoreID();int gpio_get_level(int);
int gpio_set_level(int,int);int gpio_install_isr_service(int);
int gpio_set_intr_type(int,int);int gpio_isr_handler_add(int,void(*)(void*),void*);
int gpio_isr_handler_remove(int);int gpio_reset_pin(int);int gpio_set_direction(int,int);
int gpio_pullup_dis(int);int gpio_pulldown_dis(int);
void* heap_caps_aligned_alloc(std::size_t,std::size_t,int);void heap_caps_free(void*);
int parlio_new_tx_unit(parlio_tx_unit_config_t const*,void**);
int parlio_tx_unit_register_event_callbacks(void*,parlio_tx_event_callbacks_t const*,void*);
int parlio_tx_unit_enable(void*);int parlio_tx_unit_disable(void*);int parlio_del_tx_unit(void*);
int parlio_tx_unit_transmit(void*,void const*,std::size_t,parlio_transmit_config_t const*);
int parlio_new_rx_unit(parlio_rx_unit_config_t const*,void**);
int parlio_new_rx_level_delimiter(parlio_rx_level_delimiter_config_t const*,void**);
int parlio_rx_unit_register_event_callbacks(void*,parlio_rx_event_callbacks_t const*,void*);
int parlio_rx_unit_enable(void*,bool);int parlio_rx_unit_disable(void*);int parlio_del_rx_unit(void*);
int parlio_del_rx_delimiter(void*);int parlio_rx_unit_receive(void*,void*,std::size_t,parlio_receive_config_t const*);
