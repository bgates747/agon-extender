# PORT-008 — EMOS ROM recovery review

The Author selected **diagnostics as MOSlets wherever feasible**, superseding
this review's initial diagnostic-firmware recommendation. UARTFLOW is the first
candidate: its 1,731-byte resident object contains the test sequence, timing and
messages. UARTTEST and VDPPOLL contribute another 1,093 function bytes before
private strings/CLI overhead. Extraction is feasible in principle, but needs a
small resident interface for the existing nonblocking UART/RTS operations.
Its cost must be deducted before claiming savings. Preserve the text-probe
service and resident transport ownership. Replace the older parallel machinery
as the new native implementation becomes ready, rather than linking both forever.

This is a review and proposal, not permission to remove those commands.
No product source, build configuration, firmware or bench state changed.

## Measurement and growth

Reused the unchanged [previous purge accounting tool](../AUDIT-008/account.py)
against F02c2b2's ELF/map. [Current ledger](rom-review/BASELINE.json),
[objects](rom-review/OBJECTS.csv), [functions](rom-review/FUNCTIONS.csv) and
[review source hashes](rom-review/REVIEW-SOURCES.json) retain the evidence.
Its ROM/ELF/map reconciliation passes; current ROM is **130,791 bytes**, with
**281 free**, 4,067 static RAM bytes and 70 bytes of linker fill.

| Largest growth since the completed purge, ranked by added ROM | Then | Now | Added bytes |
|---|---:|---:|---:|
| Automatic SD admission (`emos_admission.o`) | 0 | 3,038 | 3,038 |
| Parallel engine, including new reverse reference | 1,398 | 1,972 | 574 |
| Resident SD transport | 685 | 1,257 | 572 |
| Keyboard C owner | 2,760 | 3,267 | 507 |
| New handover state machine | 0 | 430 | 430 |
| Console, including new admission gate | 1,928 | 2,344 | 416 |
| UART driver | 1,092 | 1,317 | 225 |

The whole image grew **6,017 bytes (4.82%)** from the post-purge 124,774-byte
baseline. These are different development/toolchain epochs, so the
[complete object comparison](rom-review/GROWTH.csv) attributes growth but does
not prove an optimization's net saving. The previous 6,282-byte purge is already
incorporated. Its removed provider registry/loader cannot be removed a second
time. The two diagnostic objects remain exactly the same size as after that purge.

## Ranked opportunities

Ranking favors useful recovery with limited new machinery, not gross size alone.
Costs overlap where stated; none is a measured before/after removal result.

| Rank | Candidate | Current linked cost | Caller/dependency finding | Recommendation |
|---|---|---:|---|---|
| 1 | UARTFLOW diagnostic | 1,731 ROM: 1,044 code + 687 constants; 10 RAM | Only product entry is the explicit `emos_cmd` branch. Uses private nonblocking UART/RTS operations and clock deadlines. Existing telemetry profile already omits this object. | Move sequence, waits and reporting to `/emos/uartflow.bin`; reuse resident UART leaves through a minimal admitted interface. Deduct that new interface and cleanup cost from gross recovery. |
| 2 | UARTTEST and VDPPOLL | 519 + 574 = 1,093 function bytes; private strings and CLI overhead additional | Only explicit CLI calls; share a 3,217-byte object with `edu.text-probe`. Clock helper, text validation/exchange and gateway must remain. | Move frontends to MOSlets using the same diagnostic interface. Preserve service code in the shared object; removing its entire 3,217 bytes is invalid. |
| 3 | Existing parallel reference/binding implementation | 1,972 engine + 1,268 binding + 393 assembly = 3,633 gross; included write/read bodies are 715/574 | Forward engine is called by the current binding; reverse reference has tests but no native product caller. UART open/reservation already use the shared binding guard. | Replace required internals during F02c3; retain a reference test composition. Savings equal removed code minus native replacement, not 3,633 bytes. No immediate deletion credit. |
| 4 | Fake adapter, rich CLI/status and CALL parsing | Inside 3,362-byte `emos_cmd`, shared helpers/constants elsewhere | Inlined branches prevent reliable per-command attribution from symbol sizes. Fake mode exercises coordinator tests; CALL still dispatches resident services. | Consider only after the first two candidates; requires a bounded compile experiment and explicit behavior disposition. |

Removing only UARTFLOW's object would arithmetically put free space at
**2,012 bytes**. Removing the two standalone probe bodies as well would make
that **3,105 bytes** before other link/CLI/string changes and the resident
MOSlet-access interface. These are gross budget
scenarios, not built candidate sizes or promises that the remaining coordinator
will fit. The full UARTFLOW + probe-object total of 4,948 bytes is **not** an
available saving: much of the probe object implements the retained service.

## MOSlet feasibility and resident boundary

UARTFLOW needs `uart1_try_get`, `uart1_try_put`, RTS ownership and bounded waits.
Those are EMOS-private mechanisms. The official MOS UART API includes blocking
receive; it does not provide this diagnostic's complete private interface.
See the official `agon-docs/docs/mos/API.md`, UART entries 0x15–0x18.
A faithful MOSlet extraction needs a narrow resident interface. Direct hardware
access from the utility would bypass EMOS ownership and is not proposed. The
existing leaves already implement these operations; do not copy UART drivers,
invent another loader, or move the whole test state machine behind a new API.

1. The MOSlet owns the diagnostic sequence, expected strings, timing/deadline
   calculations, pass/fail messages and its working buffers. Existing `/emos`
   dispatch preserves `EMOS UARTFLOW` spelling once the built-in is removed.
2. EMOS owns admitted UART acquisition/configuration, nonblocking RX/TX, RTS
   changes and release. Reuse `open_UART1`, `uart1_try_get`, `uart1_try_put`,
   `uart1_claim_rts`, `uart1_receive_ready` and `close_UART1` behind a small
   interface. Admission starts at an idle Legacy CLI and then permits the
   admitted foreground MOSlet's calls; it must not demand Core/idle state on
   every call after the utility is running. Refuse an active Extender keyboard,
   console or parallel owner. No automatic keyboard takeover.
3. The existing resident gateway is the first interface to assess. It currently
   admits MOSlet buffers only for `ext.sdlink`, so diagnostic admission must be
   explicit, narrowly bounded to the utility region, with no saved caller
   pointers or callback into unloaded utility code. Keep the normal entry/exit
   cleanup responsible for releasing a diagnostic lease on utility return.
4. Measure dispatch, range validation, ownership and cleanup overhead before
   claiming net ROM recovery. The same interface should serve all three
   diagnostics. If it consumes the saving, report that result rather than
   silently falling back to diagnostic firmware or direct register access.

The existing [`bench-telemetry.mk`](../../../../agon-emos/port/bench-telemetry.mk)
proves the UARTFLOW object can be excluded independently; it is a dependency
check, not the selected user-facing solution. Current `edu.text-probe` rejects
MOSlet callers and is not a ready-made substitute for raw diagnostic access.

## Preserve and avoid

1. Keep keyboard reception, ordinary VDU routing, console, SD services and idle
   admission resident. The 3,038-byte automatic-admission object supports the
   recently requested listener-free workflow; size alone does not make it waste.
2. Keep `edu.text-probe`: its gateway, validation and active-keyboard fallback
   are retained contracts. The fixed VDPTEXT CLI function is only 29 bytes and
   shares its exchange; removing that wrapper is not a meaningful first target.
3. Fixed-parallel qualification and ordinary telemetry are already excluded.
   Their removal offers no new ordinary-ROM saving. Keep current image limits,
   ABI vectors, UART guards, reset safety and mandatory release policy.
4. Do not globally enable linker garbage collection to make figures smaller.
   This profile links whole C objects and has assembly/API roots and linked
   guards requiring explicit review. Removing a caller alone does not remove
   its externally visible code. Compiler C size optimization is already `-Oz`
   (FatFS deliberately `-Os`); a general stock-MOS/compiler overhaul is outside
   this transport review.

## Recommended next bounded change — pending approval

First specify and cost the shared resident diagnostic boundary, then extract
UARTFLOW as a normal `/emos` MOSlet using the existing launcher/build conventions.
Reuse its real-source harness, replacing only transport access with that boundary.
Check busy/refused admission, MOSlet request/buffer limits, partial/error/timeout
results and cleanup after normal/failed return. Exercise missing utility and
unsupported-firmware behavior, preserve loaded application RAM, and measure the
complete linked image with the unchanged accounting tool. Run the full firmware
wrapper and keyboard/console/SD regressions. Update ownership guards to recognize
the admitted diagnostic service without permitting general UART/GPIO bypass.
No bench required for this first implementation check.

Then decide whether the measured headroom justifies doing the two probe
frontends immediately. Native parallel replacement remains part of F02c3,
with the existing source/linked tests retained as behavioral references.
