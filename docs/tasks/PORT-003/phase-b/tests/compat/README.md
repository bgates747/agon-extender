# Phase B host compatibility boundary

These headers provide only the compile/runtime surface required to execute the
retained synchronous Canvas/common-renderer closure on a POSIX host. They are
test infrastructure, not replacements for ESP-IDF or FreeRTOS firmware APIs.

The queue implementation is a bounded byte-copy FIFO because upstream creates
one primitive queue during controller configuration even when Phase B selects
immediate execution. Task notifications and semaphores are inert: no Phase B
fixture starts a task, ISR, timer, or background executor. Heap-capability calls
delegate to the host allocator. Matrix support implements only the 3x3
operations used by retained bitmap transforms.

Any newly required platform API must be reviewed here before it is stubbed. A
need for broad subsystem emulation is a PORT-003 Phase B stop condition.
