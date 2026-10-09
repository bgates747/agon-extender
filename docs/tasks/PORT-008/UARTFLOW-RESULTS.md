# UARTFLOW MOSlet extraction — bench-free results

Subsequent authorized [hardware qualification](UARTFLOW-HARDWARE-RESULTS.md)
passed. The report below preserves the preceding bench-free checkpoint.

UARTFLOW now runs as `/emos/uartflow.bin`, preserving `EMOS UARTFLOW` through
the existing launcher. Net ROM recovery is **1,327 bytes**, including the new
resident service: **1,608 bytes remain free**. Builds, host tests and linked
eZ80 tests pass. This is a development candidate, not deployed or promoted.
The first extraction is complete; physical timing and full-system utility
loading require later qualification. Other diagnostics remain unchanged.

## Accounting

The baseline is the preceding UART-reservation candidate, not production.
The unchanged AUDIT-008 accounting tool processed the final linked ELF/map.
Percentage change is `(candidate − baseline) / baseline × 100`.

| Measure | Reservation baseline | UARTFLOW MOSlet candidate | Change |
|---|---:|---:|---:|
| EMOS ROM used, bytes | 130,791 | 129,464 | −1,327 (−1.01%) |
| EMOS ROM free, bytes | 281 | 1,608 | +1,327 |
| Static RAM, bytes | 4,067 | 4,058 | −9 (−0.22%) |
| UARTFLOW SD utility, bytes | Not separate | 9,326 | Adds disk utility |

Utility code/data/BSS end at `0xB24F4`, leaving 23,308 bytes before the
`0xB8000` slot limit for heap/stack. This is address-space headroom, not measured
worst-case stack usage. The MOS header and slot size were checked. The resident
`_emos_uart_flow` algorithm symbol is absent; the admitted service is present.
Exact image identity and hashes are in [the result manifest](UARTFLOW-RESULT.json).
Local build/provenance/logs are retained under `agents/port008-uartflow/`.

## Ownership and compatibility

R1-01 — The EMOS-owned utility contains the prior FLOW/FLOWACK sequence, MOS
clock deadlines, stalled-clock bound and reporting. Its API adapter uses the
existing 66-byte gateway and RST binding. No raw UART/GPIO or callback is added
to the utility. The stock blocking receive API cannot support silence tests.

R1-02 — Resident `ext.uartdiag` v1 admits only an active foreground MOSlet in
Legacy with enabled interrupts. It validates two-byte buffers, arguments and
ownership, then performs bounded UART acquire/RX/TX/RTS/release operations.
Existing keyboard/parallel ownership guards remain authoritative. Exit cleanup
closes the diagnostic lease even when the utility does not explicitly close it.
The retained `emos_uart_flow.c` filename now owns this thin service, not the
test algorithm. UARTTEST, VDPPOLL and `edu.text-probe` remain resident.

R1-03 — Running the command now needs the utility file and matching development
EMOS. Missing files use ordinary load errors; older EMOS rejects the new service.
The generic acquisition failure message now covers an unavailable service or
busy UART. The dedicated P4 flow-control peer is still required; ordinary EDP
console firmware is not a substitute. Input must already be usable from the
mainboard keyboard before the diagnostic can acquire UART1.

## Validation

| Check | Result | What it establishes |
|---|---|---|
| Full maintained EMOS firmware wrapper | Pass | Target compile/link and required ABI, UART divisor, VDU and parallel guards |
| Clean MOSlet target build | Pass | 9,326-byte executable at `0xB0000` |
| Original 15 flow scenarios, actual utility algorithm and resident service | Pass | Pause/reply/quiet/deadline/error behavior and cleanup with scripted UART peer |
| Added host service and real utility-envelope checks | Pass | Buffer bounds, op/argument validation, owner refusal, failed acquisition, cleanup, old-firmware refusal |
| Linked eZ80 diagnostic gateway | 285 cases pass | Actual gateway, UART leaves, all TX byte values, RX/error/RTS, caller/mode/IRQ gates, actual exit cleanup; IX/SP/IFF preserved |
| Linked eZ80 reservation regression | 22 cases pass | Existing reserve/send/park/restore/release semantics retained |
| Utility, keyboard (ordinary/telemetry), console, SD link, admission, mode transaction, poll/text guards and port regressions | Pass | Affected existing contracts remain covered |

The host C harnesses use address/undefined-behavior sanitizers. The linked CPU
tests execute the built EMOS instructions against modeled UART registers. They
do not model a physical serial peer or prove electrical timing. Linked exit
testing found an unmasked cleanup path during implementation; cleanup now uses
the existing IRQ lock and the final linked run passes.

No whole-system Fab launch, real utility loading from SD, physical peer timing,
P4 rebuild, flashing, reset or production update was performed. Per-operation
gateway overhead changes the diagnostic's polling cadence; the old host results
do not prove identical physical timing. Final paired qualification must include
the P4's own blocked-return timeout/cancellation evidence. Prior parallel
admission/reservation work and unrelated EMOS application-peer work are preserved.

See [the work contract](../PORT-008.md) and EMOS's maintained
[UARTFLOW guide](../../../../agon-emos/projects/uartflow/README.md).
