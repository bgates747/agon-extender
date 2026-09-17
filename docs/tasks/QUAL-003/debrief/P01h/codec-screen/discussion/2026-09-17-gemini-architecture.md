### Architectural Specification: Agon Light/Console 8 ESP32-P4 Extender Board

This document defines the system architecture, dual-core resource allocation, memory maps, and configuration parameters for using the **Olimex ESP32-P4-DevKit-Rev-D1** as a high-performance Video Display Processor (VDP) network extender for the **Agon Light 2** and **Heber Console 8** (eZ80F92/F91). 

### 1. System Architecture & Dual-Core Topology

To sustain a **512x384 1bpp single-buffered framebuffer** transmission over a 100 Mbps RMII Ethernet link without blocking or lagging real-time command processing from the eZ80, the system relies on strict **Symmetric Multiprocessing (SMP)** segregation. 

                  +---------------------------------------+

                  |         eZ80 Host Computer            |
                  +---------------------------------------+
                                      |
                                      | (UART over Port C Pins)
                                      v
+-------------------------------------------------------------------------+

| Olimex ESP32-P4 Extender Board                                          |
|                                                                         |
|  +-----------------------------------+   +----------------------------+ |
|  | Core 1 (APP_CPU): VDP Emulation   |   | Core 0 (PRO_CPU): Network  | |
|  |-----------------------------------|   |----------------------------| |
|  | * Deep Internal SRAM UART FIFO    |   | * LwIP TCP/IP Stack        | |
|  | * Decodes Agon VDP Packets        |   | * Ethernet MAC/PHY Drivers | |
|  | * Modifies Live Framebuffer       |   | * Lockless Frame Snapshot  | |
|  +-----------------------------------+   +----------------------------+ |
|                    |                                    ^               |
|                    v (Direct Write)                     | (Lockless Copy|
|        +-----------------------+                        |  sub-uS speed)|
|        | vdp_framebuffer       |------------------------+               |
|        | (24 KB Aligned SRAM)  |                                        |
|        +-----------------------+                                        |
|                                                                         |
|  +--------------------------------------------------------------------+ |
|  | GDMA & Network Hardware Layer                                      | |
|  |--------------------------------------------------------------------| |
|  | Outbound Stream Buffer (Internal SRAM)                             | |
|  | LAN8720 RMII Ethernet Controller Interface                         | |
|  +--------------------------------------------------------------------+ |
+-------------------------------------------------------------------------+
                                      |
                                      v
                         +--------------------------+

                         | Network Target / Client  |
                         +--------------------------+

### Core 0 (PRO_CPU): Network and I/O Tasking

* **Responsibilities**: Runs the LwIP TCP/IP protocol stack, processes hardware Ethernet MAC/PHY interrupts, and handles network sockets.
* **Performance Isolation**: Isolates non-deterministic network execution jitter and network frame re-transmissions away from timing-critical bus interactions.

### Core 1 (APP_CPU): VDP Command Processing

* **Responsibilities**: Manages UART/Parallel data ingestion interfaces from the eZ80 host computer, acts as the command packet decoder (VDP parsing loops), and renders changes directly to memory.
* **Performance Isolation**: Operates with maximum deterministic cycle times to avoid UART FIFO overruns or parallel bus clock-stretching.

### 2. Memory Subsystem & Frame Buffering

The **512x384 1bpp** configuration results in a compact memory footprint:

Framebuffer Size=512×3848=24,576 Bytes (24 KB)Framebuffer Size equals the fraction with numerator 512 cross 384 and denominator 8 end-fraction equals 24 comma 576  Bytes  open paren 24  KB close paren
Framebuffer Size=512×3848=24,576 Bytes (24 KB)
 

Because 24 KB fits completely inside the ESP32-P4's **768 KB of internal high-speed SRAM**, external PSRAM is completely bypassed for frame management. This eliminates memory controller bus-contention latencies entirely. 

### Lockless Snapshot Pipeline

To safely share the single buffer across cores without utilizing blocking mechanisms (like FreeRTOS Mutexes or hardware spinlocks) that would cause the eZ80 bus capture to drop cycles, a **lockless memory snapshot pattern** is used. Core 0 instantly snapshots the live frame block to a fast internal heap allocation using memcpy, then streams the snapshot asynchronously. 

### 3. Reference Implementation Snippets

### 3.1 Memory Layout and Network Stream Task (Core 0)

c

#include <string.h>
#include "esp_heap_caps.h"
#include "lwip/api.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define FB_WIDTH  512
#define FB_HEIGHT 384
#define FB_SIZE   ((FB_WIDTH * FB_HEIGHT) / 8) // Exactly 24,576 Bytes

// Live Framebuffer: Core 1 writes to this; Core 0 reads from it.
// Aligned to 32-bytes to ensure optimal caching and DMA safety profiles.
DMA_ATTR uint8_t vdp_framebuffer[FB_SIZE] __attribute__((aligned(32)));

// Network Streaming Task - Pin to Core 0 (PRO_CPU)
void ethernet_stream_task(void *pvParameters) {
    struct netconn *conn, *newconn;
    err_t err;
    
    // Allocate network transmit scratchpad entirely inside high-speed internal DMA-capable SRAM
    uint8_t *net_snapshot = heap_caps_malloc(FB_SIZE, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA);
    if (net_snapshot == NULL) {
        vTaskDelete(NULL);
        return;
    }
    
    conn = netconn_new(NETCONN_TCP);
    netconn_bind(conn, IP_ADDR_ANY, 8080);
    netconn_listen(conn);
    
    while (1) {
        err = netconn_accept(conn, &newconn);
        if (err == ERR_OK) {
            while (1) {
                // Step 1: Instantly copy the active frame. 
                // Execution overhead in internal SRAM is sub-microsecond and will not bottleneck Core 1.
                memcpy(net_snapshot, vdp_framebuffer, FB_SIZE);
                
                // Step 2: Push snapshot out asynchronously.
                // Using NETCONN_NOCOPY safely prevents internal LwIP memory duplications.
                err = netconn_write(newconn, net_snapshot, FB_SIZE, NETCONN_NOCOPY);
                if (err != ERR_OK) {
                    break; 
                }
                
                // Throttle transmission frequency (~60 FPS target maximum)
                vTaskDelay(pdMS_TO_TICKS(16));
            }
            netconn_delete(newconn);
        }
    }
}

Use code with caution.

### 3.2 Inbound UART Driver and Target Hardware Selection (Core 1)

c

#include "driver/uart.h"

#define EX_UART_NUM      UART_NUM_1 
#define BUF_SIZE         2048       

// Hardware Abstraction Profile Toggle
//#define TARGET_OLIMEX_AGON_LIGHT_2
#define TARGET_HEBER_CONSOLE_8

#if defined(TARGET_OLIMEX_AGON_LIGHT_2)
    #define PIN_PORT_C_TX  1  // Replace with physical schematic map
    #define PIN_PORT_C_RX  2  
#elif defined(TARGET_HEBER_CONSOLE_8)
    #define PIN_PORT_C_TX  5  // Replace with physical schematic map
    #define PIN_PORT_C_RX  6  
#endif

void init_agon_uart(void) {
    uart_config_t uart_config = {
        .baud_rate = 1152000, // Sync with eZ80 VDP port speed limits
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };
    
    uart_param_config(EX_UART_NUM, &uart_config);
    
    // Map UART to hardware via the P4 GPIO Matrix
    uart_set_pin(EX_UART_NUM, PIN_PORT_C_TX, PIN_PORT_C_RX, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);
    
    // Install the driver ring buffer explicitly into high-speed internal RAM
    uart_driver_install(EX_UART_NUM, BUF_SIZE * 2, 0, 0, NULL, ESP_ALLOC_CAP_INTERNAL);
}

// Ingestion and Command Parsing Task - Pin to Core 1 (APP_CPU)
void agon_vdp_parser_task(void *pvParameters) {
    uint8_t rx_byte;
    while (1) {
        int len = uart_read_bytes(EX_UART_NUM, &rx_byte, 1, portMAX_DELAY);
        if (len > 0) {
            // Process bytes sequentially to mutate bits inside vdp_framebuffer
            // parse_vdp_protocol_state_machine(rx_byte);
        }
    }
}

Use code with caution.

### 4. Mandatory sdkconfig Optimization Rules

Configure these variables via idf.py menuconfig to optimize runtime execution speeds: 

### 4.1 Compiler Configurations

* CONFIG_COMPILER_OPTIMIZATION_PERF=y
Sets optimization profile to -O2 for maximum processing speeds instead of minimum binary footprint (-Os).
* CONFIG_ESP_SYSTEM_HW_STACK_GUARD=n
Disables hardware stack checking mechanics once code paths are verified stable. Saves clock cycles during intense context changes.

### 4.2 LwIP TCP/IP Tuning

* CONFIG_LWIP_TCP_SND_BUF=49152
Allocates space matching two complete frame definitions (2 × 24 KB). Prevents LwIP output pipelines from blocking when TCP windows fill up.
* CONFIG_LWIP_TCP_WND=49152
Matches window sizing limits to match memory queue constraints.
* CONFIG_LWIP_IRAM_OPTIMIZATION=y
Forces crucial networking logic out of Flash Memory caches into Instruction SRAM.
* CONFIG_LWIP_ICACHE_OPTIMIZATION=y
Maintains code cache persistence for networking processing pipelines.

### 4.3 FreeRTOS Kernel Options

* CONFIG_FREERTOS_TICK_RATE_HZ=1000
Keeps tick frequency constrained to 1kHz maximum. Prevents context execution losses generated by excessive operating system heartbeat tracking loops.

### 5. Parallel GPIO Transport Migration Roadmap

When transitioning to the tested 8-bit parallel GPIO transport architecture to bypass the limitations of serial baud rates, implement the following modifications:

1. **Preserve Core Allocation Topology**: Leave Core 0 handling network stack operations exclusively.
2. **Avoid CPU-Bound Interrupt Polling**: Do not handle parallel strobe pins using software interrupt handlers (`gpio_isr_handler_add`). Standard interrupt entry and exit code sequences will experience jitter under fast external retro-bus cycles.
3. **Deploy P4 Parallel IO Peripheral Engine**: Use the ESP32-P4's hardware Parallel IO slave controller.
4. **GDMA Stream Sinking**: Configure the Parallel IO engine to feed data directly into internal SRAM buffers utilizing the chip's central **GDMA (General DMA)** matrix. This removes the CPU entirely from the raw data ingestion phase, freeing up Core 1 exclusively for protocol execution and pixel updates.
