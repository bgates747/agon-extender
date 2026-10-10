# PORT-008 — Private native qualification caller

## Scope and authorization

Author authorized continuation on 2026-10-09 after committing/pushing the LC02
software checkpoint. Work one bounded increment at a time. This increment
prepares the missing qualification callers and checks complete firmware; pause
before physical installation and execution. It does not enable formal ExExt,
ordinary parallel VDU routing, SD transport or a public raw-pin API.

LC03-A [x] — Prepare a private, explicitly selected two-way qualification pair.
EMOS must own reservation, capability negotiation, exact block admission, native
coordination, status and release. The diagnostic MOSlet owns patterns, checks
and reporting, not GPIO, UART registers, interrupt vectors or resident function
addresses. Reuse API 51h's existing Legacy/MOSlet/busy admission and bounded
`ext.uartdiag` adapter; a private operation is absent from ordinary firmware.
P4 supplies bounded storage and consumes only matched successful receipts on
its existing UART owner. Keep diagnostics out of resident code wherever
possible. No autonomous P4 transfer request or production selection change.

LC03-A1 [x] — Add the smallest private EMOS service needed to perform one
bounded block on behalf of the MOSlet. Validate direction, nonzero length at
most4096, complete MOSlet buffer bounds and caller policy before mutation.
Generate fresh control identity in EMOS and retain the negotiated state there.
Refused acquisition changes no pins; uncertain admitted work fences/invalidate
and stops the diagnostic. Do not retry a possibly delivered block.

LC03-A2 [x] — Add a private P4 qualification storage/receipt adapter with
4096-byte capacity and deterministic patterns. Before acknowledging an offer,
P4 prepares TX bytes or poisons RX storage; P4 checks RX only after successful
receipt. Log descriptor, direction, length, integrity and duration via USB
serial after UART return. No byte-by-byte logging or payload callback overhead.

LC03-A3 [x] — Build a MOSlet for lengths1,2,255,256,4096 in both directions,
repeated with different patterns. Check every reverse byte and both guard
regions; retain durable results under `/agents/extender/results`. Select any
video mode in autoexec only. The MOSlet must stop on failure, return a nonzero
status and distinguish provisional data from a completed block. Report host
and MOS clock units/limits honestly; throughput awaits actual hardware.

LC03-A4 [x] — Exercise actual service/pattern/receipt code with existing paired
coordinator and linked instruction fixtures where possible. Include refused
direction/bounds, busy ownership, wrong/stale receipt and data corruption.
Build complete ordinary/native/probe EMOS compositions with unchanged ROM and
GPIO/baud guards and profile-specific activation-caller inventory. If the
private probe exceeds131072 ROM bytes, retain the refused map and stop before
another extraction. Compile the selected full P4 probe and verify source and
artifact closure. Update parent/component docs and pause with readiness limits.

LC03-B [ ] — Subsequent separately reviewed hardware tranche: refresh bench
ownership/topology, freeze exact installable identities and restoration files,
install/verify the private pair and MOSlet, prove boot release before payload,
then run the small two-way cases and verify UART keyboard recovery. First/last
byte alignment, VALID pulse capture and electrical output release remain
unproved until then. F03 reset/fault recovery and throughput may require further
bounded cases; a clean block suite alone does not close F03.

## Research and fixed dependencies

Reuse [LC02 results](LIVE-COORDINATOR-LC02-RESULTS.md),
[block control](BLOCK-CONTROL.md), [native payload](NATIVE-PAYLOAD.md),
[handover](HANDOVER.md) and the current diagnostic MOSlet gateway. Official
agon-docs baseline remains `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`;
[GPIO](../../../../../agon-docs/docs/GPIO.md) and
[MOS API](../../../../../agon-docs/docs/mos/API.md) supply stock boundaries.
Official MOS v3.0.2 / VDP v2.16.0 references remain read-only. No official
API, architecture or wiring change is selected. Pinned ESP-IDF5.5.5 remains
the native driver authority. Private EMOS starts at130473 ROM bytes /599 free;
ordinary128739 /2333 free. Diagnostic-only orchestration must not conceal ROM
pressure by changing the linker limit or bypassing EMOS ownership.

The test extension is a fixed private composition, not a supported facility for
ordinary applications. Its build/link checks must distinguish it from the
unactivated native composition. Deployment must not infer permission from an
unversioned compile image. Machine-specific bench state stays in ignored local
records. No installed firmware or SD file changes during LC03-A.

LC03-A completed off-bench on 2026-10-09. [Results and limits](LIVE-QUALIFICATION-RESULTS.md)
record full builds, 20 modeled two-way blocks and negative cases. Private EMOS
fits with 88 ROM bytes free; ordinary and unactivated native sizes are unchanged.
The P4 compile image has no installable identity. Pause before LC03-B physical
preparation/installation; software success does not establish electrical proof.

Author authorized flashing the qualification pair on 2026-10-09. LC03-B now
prepares an identified, source-frozen `port-008-probe-r01` P4 browser composition
and the exact LC03-A EMOS/MOSlet bytes. The explicit build exception admits
only this private probe lineage/composition, never release identities or an
ordinary native image. Retain the known-good HDMI/ordinary EMOS restoration
files; no new prior-firmware backup is required under the standing Author waiver.
Installation/readback and real payload qualification remain separate results.

The [installation and boot recovery](LIVE-QUALIFICATION-INSTALL.md) now verifies
P4 r04 and the exact LC03-A EMOS/MOSlet bytes. The first attempt exposed a P4 GPIO
input-enable defect and an inaccurate SDK mock; both are corrected. Required
physical boot release passes, complete EMOS ROM matches, original startup is
restored and input is ready/neutral with the listener offline. LC03-B remains
incomplete: no actual parallel payload has run. Pause before the existing
20-case two-way suite; first/last-byte alignment, release and F03 recovery remain
unproved. No timed UART fallback or production selection change was introduced.

Author authorized the existing tests at light reasoning, requiring a stop on
issues. The first block-run preflight stopped before fixture invocation:
opening the USB collector was followed by a fresh P4 boot, keyboard readiness
false and a stalled release phase. No parallel block, CLI command, SD mutation,
flash or deliberate reset occurred. Collector closed; no retry or repair.
[Retained preflight receipt](LIVE-QUALIFICATION-BLOCK-R01.json) records the
22.02 host-second attempt. Pause for Author direction before recovery/testing.

Author resumed the bounded test. The [first physical block attempt](LIVE-QUALIFICATION-BLOCK-R02.md)
failed:1byte Agon→P4 returned35 after604 nominal120Hz ticks, guards intact,
no completed P4 receipt;19remaining cases did not run. Raw USB capture avoided
the earlier capture-associated reset. Input recovered through a separate Agon
reset for CSV retrieval only; no replay/flash, startup unchanged, bench idle.
Earlier readiness/no-payload statements describe their checkpoints. Actual
payload emission and the precise failure phase remain unproved. LC03-B/F03
stay open; pause for review before phase instrumentation or another block.

## LC03-B one-hour repair authorization — 2026-10-10 UTC

Author authorized a one-hour goal to fix the first physical-block failure,
including bounded instrumentation, firmware installation and repeated controlled
qualification attempts. Preserve each informative failure and never replay an
uncertain block automatically. EMOS retains pin/transport ownership; production
and mainboard VDP remain unchanged. Time boundary:00:25–01:25UTC.

LC03-B1 [x] — Isolate the failed phase using parallel read-only source review and
bounded P4 USB observations. Reuse the one-byte first case; preserve prior logs.
LC03-B2 [ ] — Correct the demonstrated defect with focused host/linked checks,
compile identified paired changes within existing guards, install and verify.
LC03-B3 [ ] — Run the existing20-case two-way suite where phase progress permits,
compare both endpoint receipts, verify input return and unchanged startup. Record
remaining timing/electrical/fault limits without claiming full F03 acceptance.

### Repair findings and retained limits

The identified r06 physical attempt reached the native block, then failed the
P4 handover while native completion was still pending. EMOS's normal C=0,V=1
block-release levels arrived before the P4 callback proof. C=0,V=1 alone must
neither complete nor cancel this bounded native phase: the P4 retains its fence
until exact native completion or its existing deadline. No timed UART fallback.

P4 RX now relies on the pinned driver's hardware level-delimiter EOF and exact
nonzero byte count, including unit/buffer/delimiter identity and sentinel bounds.
P4 TX uses a fresh hardware pulse counter for exactly two VALID edges, plus
initial/final high, exact TX completion and a frozen final count. GPIO ANYEDGE
callbacks that sample the current pad cannot prove a short pulse reliably.
These corrections are private qualification work, not production promotion.

The older proved forward prototype used fixed-length EOF and repeated inactive
clock pulses; it does not prove the current stopped-clock/VALID-inactive EOF
boundary. The r07 physical result reached native RX but timed out without an
EOF callback. The reviewed EMOS tail is now applied and installed: sixteen
inactive clocks after data-pin release/VALID deassertion. Full ROM readback and
124 linked native instruction cases pass. Sixteen pulses are an empirical
bounded diagnostic, not a documented hardware minimum; physical payload proof
with this image remains separate.

Boot preflight exposed a second race: the P4's two-second handshake rewind
reused READY polarity while EMOS was awaiting an earlier acknowledgement. The
private r08 correction holds the already released phase across peer delay,
retaining genuine fault fencing and forbidding timed UART fallback. Four new
actual-adapter regressions reproduce the old defect and pass with the change.
The [bounded repair result](LIVE-QUALIFICATION-BLOCK-R03.md) owns the physical
attempts and final installation/handback evidence for this authorized hour.

F03 must retain two SDK fault limits found during review: pinned PARLIO unit
deletion can partially destroy resources before returning an error, making a
blind retry unsafe; its TX arming path also contains an unbounded hardware-ready
spin before the application polling deadline starts. Nominal passing blocks and
mock SDK failure injection do not qualify those real driver-failure paths. The
new PCNT adapter permanently retains a partially failed unit deletion until P4
reset; existing PARLIO deletion needs equivalent follow-up before full F03
acceptance. Do not claim full fault recovery from the ordinary block suite.

## LC03-B second authorized repair hour

Author approved continuation on2026-10-09 local time,01:26:35UTC October10,
for a further hour ending02:26:35UTC. Reuse LC03-B1/B2/B3 and the existing
twenty-case fixture; retain the first hour as frozen failure evidence. Focus
on PARLIO receive-completion proof, preferring the previously proved forward
receiver configuration. No synthetic completion or weakened byte/record/cleanup
proof. Independently compile and test changes, install identified bytes, stop
on each informative failure, recover separately without replay, and compare
all endpoint receipts if the first block passes. Preserve original startup,
mainboard VDP and production. No additional prior-firmware backup is needed.

### LC03-B second-hour RX remedy contract

P4 RX reuses the earlier physically proved fixed byte-count PARLIO EOF, with
active-low VALID still qualifying the eight data inputs. Two independent P4
PCNT units must prove exactly N falling CLOCK edges while VALID is low and
exactly two VALID edges from initial high to final high. DMA callback identity,
exact length, fresh admission, cleanup, and matched UART completion remain
mandatory. P4 freezes/re-reads CLOCK first while the VALID counter remains live,
then freezes/re-reads VALID, closing the between-counter acceptance gap. Both
native directions enforce the existing 2,000 ms capture limit. No synthetic EOF,
GPIO-interrupt pulse proof, relaxed record length, mainboard VDP change, or
production promotion is authorized by this experimental remedy. Reuse the
existing twenty-case paired fixture; stop on failure and restore input/startup.

The r09 fixed-count candidate still receives no first-byte DMA callback. Pinned
P4 LL documentation requires two AHB/core clock cycles for asynchronous FIFO
reset synchronization; the passing predecessor clocked inactive periods before
payload. A bounded sixteen-clock **forward-only** inactive preamble is admitted
as the next diagnostic, with Port C still released and VALID high. Reverse must
not receive this preamble because P4 TX does not use VALID to gate shifting.
Retain the existing sixteen-clock tail and exact payload count. The proposed
reset explanation and sixteen-clock choice remain unproved until bench results.
Private failure logs may include hardware counter snapshots; these snapshots
never substitute for successful frozen counter proofs.

## Second-hour physical checkpoint

[Fixed-count RX results](LIVE-QUALIFICATION-BLOCK-R04.md) supersede the earlier
first-byte timeout for the installedr10/forward-preamble pair. Two independent
fresh-session invocations pass1and2bytes, then reject255bytes despite an exact
DMA callback: PCNT reports256qualifiedclocks and4or10VALIDedges. Seventeen
later cases, including reverse, remain unrun; LC03-B stays incomplete. Separate
recovery restores original startup and neutral ready input after each failure.
A reproduced warm-reset ambiguity requires a stronger fresh-transition protocol.
The attempted paired correction failed a further reset-at-ACK regression and
was preserved, then removed from maintained source. Its ROM must not be deployed. The record retains
exact identities, source checks and the next hardware proof boundary.

## Author-requested full-EDP data-only control — 2026-10-10 UTC

The Author requested the most modern working EDP/EMOS base, full video output,
and a very abbreviated transfer/readback comparison without special diagnostics.
The comparison composition selects HDMI, retained USB/browser/services and the
native EMOS-owned block coordinator. It excludes private phase logging and PCNT
units entirely. Its fixed-count real DMA callback plus inactive VALID permits
retirement; the test MOSlet writes a deterministic block, reads it back and
compares every byte and guards. The small P4 endpoint only retains/echoes data.
This explicitly weaker observation is a controlled experiment, not replacement
qualification for exact edge proof, fault recovery, ExExt, or public SD routing.
The strict counter-based composition and frozen failure evidence remain intact.

DC01 [x] — Freeze/build full HDMI comparison with diagnostic probe flag absent,
verify selected source/configuration and installed bytes. Reuse latest installed
EMOS native service without redundant flashing if its exact ROM is verified;
it has no phase/edge instrumentation. Mainboard VDP/production unchanged.

DC02 [x] — Run at most three forward/reverse echo pairs (1,255,4096 bytes),
compare every returned byte, preserve CSV, stop on first failure without replay.
Stage/retrieve over existing UART listener separately; never count that traffic
as parallel proof. Preserve/restore startup exactly and verify input recovery.
Then report whether the prior diagnostic composition affected the outcome.

[Data-only control result](DATA-ONLY-CONTROL-R01.md): one-byte echo passes;255-byte
completion succeeds both ways but readback differs at third byte.4096unrun.
The bounded comparison is complete; full transport qualification remains open.
