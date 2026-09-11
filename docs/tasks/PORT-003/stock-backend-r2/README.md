# Original stock backend — R2 review

R2 implementation is **accepted for R3 deployment**, following the R1/contract freeze
in `f94c2e4`. The Author accepted PORT-003-R2-D001 with reservation: browser
row preparation may wait for one drawing primitive, but stock's reliable
60 Hz cadence remains the reference. **The clock never takes the native-state
lock, prepares pixels, or waits for a browser.**

The current `stock-backend-binding-r03` proof has 70 passing runtime checks,
42 passing original scanline checks, and 180 passing native-row comparisons.
The same two inherited VGA2 narrow-scroll discrepancies remain unchanged.
Twenty translation units compile/link for P4; the ordinary console translation
unit also compiles and joins that original display closure. These are
relocatable objects, not a bootable image or physical timing evidence.

R3 owns selection in the ordinary deployment build, candidate/rollback
preparation, and physical qualification. The installed hardware was untouched.
No gameplay improvement or exact target-clock cadence is claimed here.

## Implementation and ownership

1. `stock_runtime_controller.hpp` binds the original five VGA2/4/8/16/64
   classes to the P4 execution gate. The original primitive implementations,
   packed native rows, row-pointer scrolling, palette, sprite, readback and
   explicit swap bodies remain. The worker drains until empty or suspended,
   with the optional timeout disabled. There is no drawing quota.
2. `stock_scanline.cpp` retains the five original packed scanline expansion
   bodies **byte-for-byte**, including Copper and the stock
   `decorateScanLinePixels` call. The [span ledger](scanline-spans.json)
   identifies upstream and accepted R1 source bytes. Output normalization is
   solely `signalRow[x ^ 2] & 63`, into the existing RGB222 representation.
   There is no RGB888 intermediate.
3. `stock_native_access.*` supplies recursive native exclusion for one
   primitive, one row preparation, or a finite metadata/storage mutation.
   A separate foreground-entry mutex serializes synchronous flushes and
   queue submission. One state mutex/condition variable makes worker admission
   and suspension indivisible. Nested suspension counts retain stock's
   persistent background-disable state without holding a thread-owned mutex
   across API calls. Neither foreground nor native mutex belongs to the clock.
4. `stock_p4_service.*` owns the independent timer, drawing task and output
   task. A late timer callback advances the frame counter by elapsed periods
   once and coalesces task notifications; it does not replay old rendering
   passes. The counter outlives replaceable depth objects. Maximum callback
   lateness and skipped-delivery accounting are available for target checks.
5. `PresentationSnapshotPool` retains immutable network leases and its
   existing single-outstanding-consumer contract. The new direct RGB222
   producer uses three one-byte-per-pixel allocations, 2.25 MiB at the existing
   maximum 1024×768 size. Network demand admits output copies; backpressure or
   unavailable storage never gates the clock or the native drawing worker.
6. `agon_screen.h` conditionally binds the existing screen interface to the
   native controller and a stable service/snapshot owner. Mode change detaches
   and joins native readers/workers before replacing Canvas or native rows.
   Snapshot leases survive this replacement. The original modeline/mode table,
   nominal period, official VDU fallback, palette operations and mouse endpoint
   remain. `video.ino` receives the same stable snapshot pool through an
   output-owner helper. The ordinary deployment selection has not changed.

## Concrete integration decision

The [restoration contract](../stock-backend-restoration.md#r2-decision-register)
owns PORT-003-R2-D001. Acceptance applies to browser row preparation, **not** to
the clock. A long primitive can delay a browser row; its maximum target delay
has not been measured. Output priority supplies a scheduling opportunity
between primitives, but a host mutex test does not establish target fairness
or parity with hardware VGA scanout.

| Native state or operation | Binding and preserved behavior |
|---|---|
| Row bytes, row-table scrolling, plane swap | Common `execPrimitive` entry guard; original bodies retained. Output resolves current visible rows inside its row guard. |
| Immediate flush and double-buffer callers | Foreground entry plus suspension joins the active worker before synchronous dequeue; original FIFO and task notification remain. |
| Dynamic path/matrix pool | Each original `LightMemoryPool::alloc/free` operation is guarded. The retry/yield loop stays outside, so drawing can free queued payloads. No allocator algorithm change. |
| Palette tables and Copper list | Finite mutation guard and revision counter. A row reader rebinds a saved Copper cursor after list/palette retirement; ordinary sequential traversal is original. |
| Sprite frames and bitmaps | Guarded common sprite methods, official sprite publication/retirement, and original bitmap destruction. Stock user-detachment/reset preconditions remain. |
| Buffered bitmap bytes | Finite `BufferStream` writes, adjust write spans, reverse/copy writes and buffer-user retirement share exclusion. Inline UART operands are consumed before the guard. New, unpublished allocation fills need no reader exclusion. |
| Text and mouse cursor | Guarded bitmap/frame changes, visibility, position, cursor-map retirement and pointer replacement. Row decoration order remains stock. |
| Mode/controller lifetime | Stop requests, worker suspension and both task joins precede native destruction. Clock callbacks stop referencing task handles before deletion, with an ESP timer-task barrier. |

No guard surrounds an entire parser command that can wait for UART bytes,
an entire frame, or an entire queue drain. Native normalizing/network code
operates on copied output memory after the row guard is released. Existing
upstream ownership assumptions and deferred defects are not silently repaired.
The [binding verifier](runtime/verify_binding.py) compares original tokens
beneath only named guards and conditional P4 interface changes, and separately
checks the five exact scanline byte spans.

## Processor and SDK boundary

| Owner | P4 execution binding |
|---|---|
| Retained parser | Existing core 0, priority 3. |
| Native drawing | Core 0, priority 5, 8192-byte stack; stock worker relationship retained. |
| CPU row output | Core 1, priority 6, 8192-byte stack. Native access is shared only for a primitive/row/mutation. |
| Clock | Pinned IDF `ESP_TIMER_TASK`, configured priority 22/core 0. Callback accounts monotonic time and notifies tasks only. |
| USB library / HID | Existing unpinned priorities 6 / 5 (`p4_usb_host.hpp`). |
| Wired network | Existing unpinned priority 3 (`wired_network_service.cpp`). |

The pinned SDK maps `std::recursive_mutex` to a FreeRTOS recursive semaphore
with priority inheritance. `pthread_self()` would assert for native FreeRTOS
tasks lacking a pthread registration; the binding does not use C++ thread IDs
to infer ownership. `esp_timer_delete()` is deferred, so deletion alone is not
a callback join: a subsequent callback on the serialized ESP timer task
establishes the required boundary before task handles/state are retired.

Original native allocation retains its pool/row packing and alignment. The
runtime uses byte-addressable P4 PSRAM instead of the classic VGA controller's
internal-memory capability. Output snapshots also use PSRAM; USB, networking,
SDK objects and task stacks retain their own allocation policy. Actual mode
capacity, cache behavior, core scheduling and cadence remain target gates.

## Evidence and reproduction

Run from the repository root:

```sh
.venv/bin/python -B docs/tasks/PORT-003/stock-backend-r2/runtime/run_runtime.py
```

The [runtime manifest](runtime/results.json) records exact source/dependency
hashes, compiler identities, current build and run. [Runtime checks](runtime/runtime-tests.txt),
[native regressions](runtime/native-regression.txt), and
[scanline regressions](runtime/scanline-regression.txt) retain the observations.
The runner compiles the real service/controller code with a bounded host
FreeRTOS/timer substrate, then with the installed RISC-V compiler and P4 SDK.
The host model provides deterministic scheduling barriers; it does not model
FreeRTOS priority/affinity or physical timing accuracy.

Coverage includes worker start/suspend interleavings, nested suspension,
output within an unfinished drain, synchronous FIFO order, explicit swap
notification/plane identity, copied/recycled dynamic payloads, palette-cursor
retirement, sprite retirement during a row, active output and drawing during
teardown, lease survival, task-allocation failure/retry, and clock progress
while drawing or output holds native state. The clock test also forces late
observations and counter wrap. Native and composition regressions use the
unchanged R1/r02 test programs against the current runtime binding.

The target display link leaves no unresolved FabGL/DSP renderer or classic
VGA peripheral dependency. The console integration leaves no dependency on the
old `P4DisplayController`, compositor or coupled frame service. USB, network,
Arduino and SDK imports remain deliberately unresolved in this nonbootable
proof. Compiler flags come from the installed SCons database; the console
component database verifies the additional installed USB include paths. Both
input hashes are recorded. No PlatformIO/CMake generator or installer runs.

Full commands, source snapshots, compiler logs and objects are retained in
ignored `agents/stock-backend-r2/` directories. Standing version preapproval
covers fixture r03 and registry r68. The original r02 [manifest](results.json)
and [42-check record](scanline-tests.txt) remain historical quiescent evidence;
its frozen runner describes that source state, whereas the runtime runner
above is the current reproduction entry point.

[Additional validation](runtime/additional-validation.json) records the
independent existing snapshot-pool test passing with AddressSanitizer and
UndefinedBehaviorSanitizer. Its old controller companion still calls the
previously removed `executeFrameWork(8)` budget API and does not compile; it
is not claimed as a passing regression or changed as part of this restoration.
The inherited two-colour scroll failures, PAL8 packed word accesses,
both-edge sprite clipping and delete-all palette observation remain deferred
under the no-upstream-fixes instruction.

The artifact registry, templates and VDP source identities validate. The full
version validator still stops at the pre-existing held r02 hardware connectivity
hash mismatch; those hardware inputs are identical to `f94c2e4`.
