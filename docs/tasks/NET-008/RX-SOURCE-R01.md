# NET-008 receive-service source review

The retained145 type3 events establish FIFO overruns, not their first cause.
The identified appliance has no independent receive-service control. Correct
its receive-service hazards and qualify them before blaming the modem.

1. Exact IDF source b774170ff46c393eeb5e495ea37936038d3f4f4f:
   components/esp_driver_uart/src/uart.c defaults RX threshold120; its ring-full
   branch disables RX-full/timeout interrupts until the consumer frees space.
   FIFO overflow resets the FIFO and emits UART_FIFO_OVF. Ring pressure and
   delayed ISR servicing can therefore both end as event3. Old records lack
   high-water/read-gap measurements, so causal attribution is unresolved.
2. Original appliance reads/verifies in CLI/main priority1 while TX runs priority5.
   exact() also prints USB progress directly while consuming input. IDF USB write
   takes a semaphore and may block on its ring. Stop doing USB formatting in the
   active receive loop. Prioritize RX over producer, give the FIFO earlier service,
   and keep UART ISR/buffers in internal memory through the supported IRAM option.
   No larger ring is used to hide a finite-duration processing deficit.
3. A controlled internal UART loopback uses supported uart_set_loop_back. Its
   contract explicitly routes TX into the RX module; it exercises serializer,
   actual FIFO, IDF ISR/ring, verification and concurrent producer. Keep both
   connected GPIOs inputs and do not call uart_set_pin in this mode, so it sends
   no test bytes to the modem. It does not qualify external pads/wiring or RF.
4. Prepare baseline, priority-only, no-USB-only, early/IRAM-IRQ-only and combined
   control profiles for bounded source-cause comparison; these preserve packet
   bytes and wire rate. Baseline is a controlled reconstruction, not a claim of
   bit-identical old firmware. A passing loopback alone does not identify the
   old external-stream cause. Preserve that uncertainty and compare diagnostics.
5. Record RX-ring/event-queue high-water, read-call gap, FIFO/ring/frame errors,
   queue saturation and task/profile settings. Read-gap includes blocking wait
   and is NOT an ISR-latency measurement. No counters may be reset to repair a
   failed workload. Any ignored UART errors must still invalidate the result.

This is source evidence and a corrective candidate, not hardware qualification.
Actual peripheral controls and corrected modem transfers require fresh scheduler
custody; current6502 lease169 is untouched. No mainboard MOS/VDP API changed.

Receiver acceptance also requires at least95% nominal8N1 wire utilization,
using actual transmitted frames and producer-to-drained TX duration. This guards
against qualifying a receiver with a producer too slow to load the UART.
