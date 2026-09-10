# AUDIT-005 W2 — EMOS differences and stock-code reuse

Recorded 2026-09-10. W1 was accepted and W2 authorized by the Author.
This is a source and saved-image review, with unranked findings for
[AUDIT-005](../AUDIT-005.md). W3 owns the recommendation and disposition.

## Result and evidence boundary

The ordinary ExCom transmit path reimplements the stock CTS/readiness/write
operation through several C routines. The matching deployed ELF confirms
additional calls, deadline arithmetic and interrupt-state operations even on
a successful first attempt. This is definite additional work and a stock-code
reuse opportunity. Its contribution to observed gameplay lag is **unmeasured**.

Reception already reuses the stock keyboard/map and display-effect routines.
Separate UART framing, source ownership and accepted recovery behavior explain
much of the remaining code. Replacing all of it with the stock UART0 receiver,
or calling the guarded public UART1 writer directly, would lose requirements.

Source labels M, D, E and P and their exact commits are the
[W1 selections](baseline-and-path-map.md#selected-sources). In particular, E is
`82929c4b3e64c370d1102f46f61e8b600d57d665`, P is
`52479f0ae9653e293031a1eed1b65f0cec9695cd`, and stock M is v3.0.2 at
`8336409351ee5314e02801a7b72a4f1bb5282519`. Relevant official
[output/callback API documentation][d-api] and [packet documentation][d-packets]
were consulted before the implementation comparison. The existing
[resident receiver contract][e-contract] explains the additional ownership,
error and callback constraints; its later native-USB addendum applies.
Instruction comparisons use [M serial][m-serial] and [M RST handlers][m-vectors]
against [E serial][e-serial] and [E RST handlers][e-vectors]. Receive details
also use [E C/IRQ bridges][e-bridge] and [E keymap implementation][e-map].

No firmware was built, instrumented, executed as an audit test or changed.
No SD or physical bench operation was performed. Source control-flow deductions
below are not reproductions on hardware. A notification emulator is solely an
attention cue. Existing tests were read for coverage, not rerun or expanded.

## Forward output: operation accounting

Here, a **call** is one ordinary byte call or one counted stream call; an
**attempt** is one poll of the UART before accepting a byte. A blocked byte can
require many attempts. The counted path enters the outer bridge once per
block; the delimiter path enters the byte bridge for every emitted byte.

| EMOS operation and source | Purpose and frequency | Stock equivalent, execution cost and reuse constraint |
| --- | --- | --- |
| `EMOS_vdu_PUTCH` / `EMOS_vdu_WRITE` backend selection, [E serial][e-serial] | Select the committed route once per call. Foreground. | Stock calls UART0 directly. This small routing addition is required by EMOS ownership; Legacy still reaches the stock UART0 loop. The deferred parallel branch is not executed in ExCom. |
| `EMOS_vdu_console_PUTCH` bridge | Save BC/DE/HL/IX/IY/A and marshal a three-byte C argument slot, once per byte call. | Stock PUTCH has no corresponding full C bridge. The current bridge protects the caller, including C `putch`'s preloaded HL return value. The saving cannot simply be deleted while its C callee can clobber those registers. |
| `EMOS_vdu_console_WRITE` bridge | Save caller state and marshal pointer/length once per counted block; form pointer/count/E postconditions on return. | Stock walks the caller's buffer in assembly. The block is already amortized at this outer boundary; it is incorrect to charge this whole bridge to every byte of counted output. Failure and flags are discussed below. |
| `emos_console_write_byte` → `emos_console_write_stream`, [E console][e-console] | Convert a byte to a one-byte stream; check lease, committed route and staging once per call. | No stock display lease exists. Lease/route validity is necessary; the extra byte-to-stream C call is an implementation choice. There is no copy of the full outgoing block or new per-byte wire envelope here. |
| Entry to `emos_keyboard_send`, [E keyboard][e-keyboard] | Briefly mask interrupts, check IFF/ownership/fault/preparation/reentrancy, set `transitioning`, restore IFF, initialize deadline once per call. | Stock PUTCH tests serial enable/flow flags but has no resident shared-owner coordinator. EMOS must serialize output with source/configuration transactions. The existing entry also rejects callers whose interrupts were already disabled. |
| Counted loop → `transmit` | C indexing, byte load and call once per byte, preserving order. | Stock counted output has an assembly pointer/count loop. No eZ80 software TX queue is added: both routes synchronously admit bytes to the UART. Neither waits for rendering completion. |
| `deadline_step` before `uart1_keyboard_put` | Read MOS clock, accumulate elapsed ticks, update last clock and reset/decrement a 32-bit fallback budget **every attempt**, before discovering whether CTS/THRE are ready. | Stock initializes a native-width TX wait counter per byte and decrements it only while THRE is unavailable. EMOS adds a clock deadline and a stopped-clock escape. Their placement charges bookkeeping to successful traffic as well as waiting. The current deadline covers the whole call, not just idle time. |
| `uart1_keyboard_put` ownership/fault/error checks, [E UART][e-uart] | Mask interrupts, check owner/fault, read LSR, preserve RX error consequences, check PC3 CTS and THRE, write one byte, restore IFF; **every attempt**. | Stock `UART1_wait_CTS` plus `UART1_serial_TX` already perform the core GPIO/LSR/THR operation in assembly. They lack the resident driver's error handoff and atomic ownership checks. Stock polling code must not swallow an RX error shared with the ISR. |
| `transmit` result loop | Retry BLOCKED/EMPTY; stop on deadline, fault, error or unavailable owner. Foreground. | Stock PUTCH retries TX timeout indefinitely and its CTS wait is unbounded. EMOS's bounded return and failure reporting are additional semantics. Interrupts are enabled between EMOS's short UART critical sections; the entire wait/block is **not** under DI. |
| UART open/close, source/layout selection and console PREPARE/COMMIT/LEAVE | Pin/vector ownership, retained settings, peer admission and staged display publication, per transition/configuration request. | `uart1_keyboard_open` already calls the stock-derived `open_UART1`. Preserve the AgonDev 32-bit baud-intermediate correction, explicit PC2 RTS and receive interrupts. Transition CRC, nonce checks and initial queries are not performed for each ordinary output byte. |

UART0 and UART1 are not interchangeable register substitutions throughout:
stock UART0 tests the inverted CTS bit in MSR; stock UART1 tests active-low
PC3 through GPIO. Their THR/LSR bases are `0xC0`/`0xD0` respectively. Under
r03, PC0 TX goes to P4 GPIO22 RX, PC1 RX receives P4 GPIO12 TX, PC2 RTS drives
P4 GPIO23 CTS, and PC3 CTS receives P4 GPIO11 RTS. CTS is the P4 receiver's
backpressure signal; eZ80 PC2 controls traffic in the opposite direction.

The reusable stock candidate is the private implementation of
`UART1_wait_CTS` / `UART1_serial_TX` and the stock counted loop, **with the
resident requirements accounted for**. EMOS's public UART1 PUTCH/TX/RX/open/
close entry points intentionally reject attempts to steal the resident UART.
They must remain guarded; no application bypass is implied by this audit.

## What the existing ELF establishes

The W1-verified candidate `agon-emos-v0.1.12-b2026-09-10-03-50-35Z` has ELF
SHA256 `bff6e870f38bb6c1d09dd59411599ac1486918b99967e69f12ce244d6ffe7781`.
Read-only `ez80-none-elf-nm -n` and
`ez80-none-elf-objdump -d --disassemble=<symbol>` on that ELF show:

| Routine | Retained direct calls on a healthy, first-attempt write with unchanged clock |
| --- | --- |
| `_transmit` at `0x681E` | `__frameset0` at call site `0x681E`; `_deadline_step` at `0x682F`; `_uart1_keyboard_put` at `0x683B`. |
| `_deadline_step` at `0x6746` | `__frameset` at `0x674A`; `_emos_keyboard_clock` at `0x674E`; `__ladd` at `0x678D`; `__lcmpzero` at `0x679A`. The last two implement the 32-bit fallback-budget decrement/test when the clock has not advanced. |
| `_uart1_keyboard_put` at `0x127D6` | `__frameset` at `0x127DA`; `_emos_keyboard_lock` at `0x127E3`; `_emos_keyboard_unlock` at `0x12833`. The error-only `_uart1_keyboard_stop` call is excluded. The THR write is at `0x12817`. |

These are **ten executed direct CALL sites inside those three routines** on
that stated branch, excluding the call into `transmit` from the send loop and
instructions within the called helpers. Three are frame-setup calls; two are
32-bit arithmetic/test helpers. This is a static branch accounting, not an
instruction-cycle total, benchmark, or ten calls added relative to a measured
stock binary. A retry repeats the deadline and UART routines but does not
reenter `transmit`'s own prologue. On a clock advance, the budget-reset branch
replaces the two arithmetic helpers.

The outer byte/stream C calls also remain in the ELF. Thus neither inlining
nor dead-code elimination removes the identified work in the deployed build.
The ignored `agents/audit-005/w2-static-listings.json` retains the six bounded
function listings and resolved call targets. This objdump displays relative
branch destinations above 64 KiB with truncated upper address bits; that is
not evidence of a firmware jump into the wrong bank. The table uses full
absolute CALL encodings and symbols. No timing conclusion relies on its
formatted relative-branch labels.

## Receive, publication and interrupt accounting

| EMOS operation | Purpose / frequency / interrupt effect | Stock reuse and constraints |
| --- | --- | --- |
| UART0 `_uart0_handler`, [E IRQ][e-irq] | Extra IX/IY and alternate-register save/restore on every UART0 IRQ, even for packets later ignored. Interrupts remain masked in the handler. | Stock's primary-register saves and one-byte receive/parser call remain. Six extra PUSHes and six matching POPs plus register-bank exchanges protect the current C/compiler-helper path; deleting them independently is unsafe. |
| UART0 `vdp_protocol`, [E protocol][e-protocol] | Retained assembly framing; check committed route at packet completion, allowing independently selected keyboard/settings while filtering unowned display effects. | Stock framing is already reused. Preserve the existing oversized-body discard-length fix. Display ownership filtering has no stock dual-receiver equivalent. |
| UART1 IRQ entry and `uart1_keyboard_irq` | Full C-compatible register saving, PC2 RTS stop, at most 16 received bytes per batch, LSR/error checks and parser calls; masked until IRQ return. | Stock supplies UART read and IRQ idioms but not this resident UART1 VDP receiver. Preserve finite batches, error latching and RTS release/stop behavior. The ISR does not block waiting to transmit. |
| `emos_keyboard_byte` private framer | State dispatch per incoming byte; header timestamp per packet; length validation, up to 16 payload bytes stored and length-counted discard for oversized bodies. | This repeats the stock framing algorithm in C, but **a second state/payload is necessary** while UART0 and UART1 can each hold an incomplete packet. Stock's global parser cannot simply consume both streams. Exact keyboard/settings lengths and partial-frame expiry add requirements. |
| `dispatch` / source gate / `publish` | Completed-packet dispatch; select one keyboard source; call shared effects and track callback-edited held virtual keys. Runs in IRQ context. | `emos_keyboard_payload` is a pointer-based adaptation of stock callback/publication order; `keyboard_handler`, its table, map and reset handling remain shared. C does not replace the MOS line editor or duplicate its text buffer. |
| Private `held[32]`, modifier and zero-code state | Update per published key packet; enumerate releases on source exit/fault/admission boundary. | Stock's 16-byte public map is not an equivalent virtual-key inventory: entries may alias or have no mapped bit. This private state retains keys needed for callback-visible synthetic releases, including virtual code zero. It is not a redundant second public keymap. |
| Keyboard effect bridge and settings | Protect IX/IY around the assembly callback; preserve DE payload edits and callback-before-sysvars order, per key. Settings copy five bytes per settings packet. | Stock callback/map effects and the five-byte LDIR are reused. Preserve the accepted post-callback lookup bounds check as well as wire validation; a callback may edit the packet. |
| `emos_console_packet` / `effect`, [E console][e-console] | Validate display opcode/length/owner per complete reply. Copy stock scratch to a 16-byte local save, copy the reply in, invoke stock effect, restore all 16 bytes under IRQ exclusion. | Stock cursor/mode/pixel/etc. publication handlers are reused instead of rewritten. Copying `32 + payload length` bytes protects even an incomplete UART0 packet. This is **per display reply**, not per outgoing pixel or VDU byte. Transition replies are staged before publication. |
| Mainboard VBlank / `emos_keyboard_tick` | Stock clock increment retained; added bridge saves and housekeeping every tick. Fault/partial-frame/source-stop cleanup can invoke synthetic callbacks with IRQs masked. | Stock clock service is reused. Partial receive packets expire after 30 clock units (nominally 250 ms); idle alone does not expire. Cleanup is occasional; the state checks/bridge are recurring. No eZ80 wait for browser presentation is added here. |

The saved-register burden and reply copies are real work, but their frequencies
differ from the forward byte path. A game holding Space need not generate a
keyboard packet for each shot. Source alone does not establish the actual
UART0/1 IRQ load, reply mix, cleanup frequency or time spent with interrupts
masked during the reported game session.

## Failure and compatibility differences

1. **A new whole-call deadline.** `deadline_start` runs once in
   `emos_keyboard_send`; accepting a byte does not restart it. With a normally
   serviced 60 Hz mainboard clock, 600 clock units are nominally five seconds.
   A separate 262,144-attempt fallback prevents a frozen-clock infinite loop.
   The latter resets when the clock changes, not when UART progress occurs.
   The elapsed limit can therefore expire during a progressing long stream.
   Stock PUTCH's inner TX timeout is retried indefinitely; it is not an
   equivalent overall limit. Short CTS stalls can affect either route without
   producing any timeout log.
2. **Ordinary partial-write recovery is incomplete in the reviewed source.**
   If `transmit` times out after an accepted prefix, `emos_keyboard_send`
   clears `transitioning` and returns TIMEOUT. That path sets no
   `fault_requested`; `emos_console_write_stream` only passes the result
   back. The console lease and backend remain selected. A later call can
   write once CTS is ready again. A UART line error has a different path
   which does request fault cleanup. The older `emos_keyboard_text` and
   layout transactions explicitly request a fault on partial failure; that
   protection is not inherited by ordinary console output.
3. **The public output boundary cannot resume the missing suffix.** The
   counted ExCom bridge advances HL by the entire requested low-16-bit count,
   clears BC and preserves E on success **or failure**, returning A/status
   and carry. The delimiter loop ignores each byte writer's carry and keeps
   advancing until its delimiter. C `putch` retains its preloaded character
   return. This can lose outgoing bytes and leave a subsequent command
   following an incomplete VDU command. Actual EDP behavior depends on its
   parser's continuation/timeout state; this audit does not claim that this
   sequence occurred during Nurples. Stock's unbounded public PUTCH normally
   prevents this particular enabled-UART timeout-return case.
4. **Caller interrupt state matters.** `emos_keyboard_send` immediately
   returns BUSY when IFF was clear, including from a keyboard ISR callback.
   This obeys the resident contract's prohibition on blocking ISR TX and
   avoids waiting for IRQ-owned progress. Stock PUTCH has no corresponding
   entry rejection. The official RST output documentation does not state an
   interrupt-enabled precondition. This is a compatibility difference to
   disposition, not permission to enable interrupts inside arbitrary callers
   or to promise stock blocking calls are safe in every ISR.
5. **Preservation is specific, not blanket flag equivalence.** The byte
   bridge preserves its caller registers/A and supplies carry status. The
   counted bridge retains documented pointer/count/E handling and stock's
   actual success A=0 rather than the documented last-byte result. However,
   stock counted output ends with `OR C`, clearing carry; successful ExCom
   counted output explicitly sets carry. The official RST 18 documentation
   does not promise flags. Existing statements that all stock register/carry
   behavior is preserved are therefore too broad. The ADL/MBASE pointer setup
   and the documented 16-bit BC count remain the reference; no new 24-bit
   count contract is inferred from BCU.

The [console host harness][e-console-test] mocks `emos_keyboard_send` as successful, while its
failure cases cover admission/reply/recovery rather than a real ordinary
stream stopped mid-write. The [keyboard harness][e-keyboard-test] exercises the older text and
layout fault paths, but does not call `emos_keyboard_send`. Existing linked
guards verify bridge shape; they do not reproduce the cross-layer partial
write above. These are read-only coverage observations, not new failed tests.

## P4 backpressure boundary

The [P4 console][p-console] uses a 4,096-byte driver RX buffer and a hardware
RTS threshold of 64. [ConsoleStream][p-stream] reads via one-byte driver calls;
its outgoing reply ring and UART TX completion checks are separate. The
core-0 priority-3 `processLoop` owns USB pumping, command parsing and reply
service. Active parsing is limited to 64 `processNext` calls per outer pass,
with a trailing `delay(1)`; a parser invocation may itself consume/wait for a
multi-byte command. A reply backlog of 4,096 bytes also gates parsing.

[P4 frame service][p-frame] runs a separate task at the configured
`configMAX_PRIORITIES - 2` priority, without a pinned core in its creation
call. [Display frame work][p-display] executes a bounded primitive batch,
draws sprites and composes requested snapshots before clearing its executing
flag. A caller of `suspendBackgroundPrimitiveExecution` yields until that flag
clears. These are concrete scheduling/wait boundaries where EDP processing
may delay receive service. They do not prove that CTS stopped the eZ80 in the
reported run. Browser frame delay alone also does not establish eZ80 delay.

## Unranked findings for W3

| Stable ID | Classification and affected behavior | Stock reuse candidate / constraints | Proposed owning work and missing evidence |
| --- | --- | --- | --- |
| **AUDIT-005-F001** | Definite reimplementation of the stock CTS/THRE/THR operation, with saved-ELF proof of additional byte-attempt bookkeeping. | Stock UART1 assembly and counted loop; retain resident ownership, RX error handoff, output ordering, bounded-failure semantics and ABI. Required behavior does not imply the current C layering is necessary. | PORT-008 coordinating EMOS transport. Need actual no-backpressure throughput/CPU time before assigning a slowdown or speedup factor. |
| **AUDIT-005-F002** | Source-confirmed ordinary timeout path permits continued output after losing a suffix; resulting EDP misframing is conditional and untested. | Stock blocking behavior explains the semantic difference; neither indefinite blocking nor the older diagnostic fault policy is an automatic approved replacement. | PORT-008 coordinating EMOS console/recovery. Need disposition of partial-output behavior and a focused cross-layer failure check in any later repair. |
| **AUDIT-005-F003** | Source-confirmed caller-IFF rejection and counted carry difference; existing preservation language overstates equivalence. | Stock RST/PUTCH conventions; protect callbacks and the interrupted C frame, preserve documented ABI, distinguish undocumented flags from contractual behavior. | PORT-008 coordinating EMOS compatibility. Actual application dependence on these differences is unknown; no evidence connects them to the reported lag. |
| **AUDIT-005-F004** | Necessary receive/ownership adaptations plus existing successful stock-effect reuse; extra IRQ saves, framing and reply copies have known frequencies but unmeasured cost. | Retained stock parser/effects/map/clock; independent UART state, callback edits, bounds fixes and held-key cleanup must survive any consolidation. | PORT-008 coordinating EMOS receiver. Need IRQ/reply/cleanup frequency and masked duration only if W3 selects this as a material cost to investigate. |
| **AUDIT-005-F005** | P4 parser/reply/render/snapshot boundaries can generate backpressure; contribution remains unmeasured. | Retained parser/controller behavior is outside the MOS transmit replacement. A smaller EMOS path cannot eliminate downstream waits by itself. | PORT-003 with PORT-008 for UART correlation. Need CTS/receive-service/render timing separated from browser presentation before assigning core or throughput blame. |

These IDs are discovery order, not priority. W2 supplies no patch, scheduling
change or new test program. W3 remains the next review item, subject to the
Author's instruction.

[d-api]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md
[d-packets]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/System-Commands.md
[m-serial]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/serial.asm
[m-vectors]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/vectors16.asm
[e-vectors]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src_startup/vectors16.asm
[e-serial]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src/serial.asm
[e-console]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src/emos_console.c
[e-keyboard]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src/emos_keyboard.c
[e-uart]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src/uart.c
[e-irq]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src/interrupts.asm
[e-protocol]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src/vdp_protocol.asm
[e-bridge]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src/emos_keyboard_io.asm
[e-map]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src/keyboard.asm
[e-console-test]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/tests/emos_console_harness.c
[e-keyboard-test]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/tests/emos_keyboard_harness.c
[e-contract]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/docs/tasks/INTEG-009/keyboard-contract.md
[p-console]: https://github.com/bgates747/agon-extender/blob/52479f0ae9653e293031a1eed1b65f0cec9695cd/vdp/video/extender/transport/console_hardware.inc
[p-stream]: https://github.com/bgates747/agon-extender/blob/52479f0ae9653e293031a1eed1b65f0cec9695cd/vdp/video/extender/transport/console_stream.hpp
[p-frame]: https://github.com/bgates747/agon-extender/blob/52479f0ae9653e293031a1eed1b65f0cec9695cd/vdp/video/extender/display/p4_frame_service.cpp
[p-display]: https://github.com/bgates747/agon-extender/blob/52479f0ae9653e293031a1eed1b65f0cec9695cd/vdp/video/extender/display/p4_display_controller.cpp
