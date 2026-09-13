#pragma once
#include <cstddef>
#include <cstdint>
#define UART_NUM_1 1
#define pdMS_TO_TICKS(n) (n)
int uart_read_bytes(int,void*,uint32_t,unsigned);
int uart_get_buffered_data_len(int,size_t*);
