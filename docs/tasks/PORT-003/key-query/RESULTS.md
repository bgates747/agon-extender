# Virtual-key query results — 2026-09-20

Candidate `key-query-probe-r01-b2026-09-20-02-08-44Z` is installed on P4.
Author accepted the bounded automated coverage and requested checkpoint commit. Contract freeze: commit 54261935.

## Implemented scope

P4 tracks consumed input transitions in its existing processed keyboard FIFO.
The retained stock &99 handler queries that state and appends a synthetic event;
upstream character conversion and retained callback/reply serialization then
produce the ordinary keyboard reply to EMOS. Query key-up preserves the stock
preceding-keycode behavior. Queue overflow explicitly faults; transport cleanup
clears tracked state. Ordinary physical/browser event semantics are unchanged.

The image derives from the installed browser-capture-r03 composition; the source
changes are confined to three keyboard/console files in `build.json`. Browser UI,
codec and storage composition are preserved. No EMOS or mainboard VDP flash.
The installed rollback prefix was retained before writing, and the new flash
was independently verified. One ordinary Agon reset restored input admission.

## Evidence

| Check | Result |
| --- | --- |
| Adapter tests using actual upstream converter, all 256 modifier masks × keys 0..248 | Pass; ASan/UBSan |
| FIFO ordering, capacity, invalid key, reset, retained query keycode | Pass |
| Existing processed serializer, USB CLI and remote keyboard tests | Pass |
| P4 build, flash readback and USB host startup | Pass |
| eZ80 fixture through EMOS | 269/269 rows pass |
| Reply event counter | Every delta exactly 1; 260 consecutive held-Shift queries cover wrap |
| Held `a`, held Shift, modifiers and released keys | Pass |
| SD write, retrieval and startup preservation | Pass; autoexec byte-identical |
| Final state | ExCom MOS prompt; keyboard admitted, neutral, no pending events; SD service exited |

`result.csv` is the unmodified Agon receipt. Duration: 1,522 MOS ticks, nominally
12.683 seconds at 120 Hz, including host cue coordination. This is not a latency
benchmark or a calibrated wall-clock measurement. `deployment.json` records
fixture/result hashes and verification; `build.json` records image hashes.
Machine-local raw flash/rollback, CLI journals and startup readbacks remain in
the ignored key-query evidence directory. The inherited deployment launcher used
a REMOTE-001 record prefix; the work and evidence here belong to PORT-003.

## Limits and review

Hardware input was supplied by the admitted host-to-P4 keyboard path, then P4
UART to EMOS; it was not eZ80 memory injection. This run does not establish physical
USB replug behavior, browser-game responsiveness, malformed-stream recovery, or
hardware overflow recovery. Host tests cover queue exhaustion and reset state.
Keys 249..255 remain outside current EMOS ingress and are consumed without
injection; this bounded repair does not extend that ABI. The broader UC02/UC03
inventory remains open.

The global version validator still reports the pre-existing frozen wiring r02
connectivity hash mismatch, reproduced in HEAD. No wiring files were changed
for this repair; artifact registry validation is checked separately.
