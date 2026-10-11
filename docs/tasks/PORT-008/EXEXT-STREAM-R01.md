# PORT-008 — First ordinary ExExt stream

## Executive summary

The Author authorizes an eight-hour unattended goal on 2026-10-11, from
10:25:14 to 18:25:14 UTC. Extend the working bidirectional parallel transport
into an experimental ExExt mode for unchanged applications: EMOS routes normal
VDU bytes to the P4 parser; P4 returns actual VDP packets and keyboard events
through the same eight-bit pipe. Preserve Legacy and UART-only ExCom. Reuse
the established transport, renderer, MOS dispatch and packet handlers. Success
requires installed-byte verification, functional tests and deterministic Nurples
evidence; a compile or an echo alone is insufficient.

Current [bounded results](EXEXT-STREAM-R01-RESULTS.md) distinguish physical
passes, host checks, measured scopes and untested limits.

## Scope and boundaries

1. EMOS exclusively owns mode commitment, bus admission, eZ80 GPIO and transport
   scheduling. P4 EDP owns its counterpart, retained VDP parser and reply queue.
   Applications keep their normal RST/MOS interfaces and need no linked helper.
2. Existing eight data lines and READY/CLOCK/VALID wiring remain unchanged.
   Native P4-PC builds retain mandatory boot-owned 3.3 V LDO4. No rewiring,
   analyzer attachment, raw application GPIO access or upstream reference edits.
3. Batch ordinary output; do not perform a complete block negotiation for each
   printed character. Return servicing must progress when an application only
   reads a previously obtained keyboard-map/sysvar pointer or waits for a reply.
   Preserve packet order and stock callback context. Do not introduce an
   unbounded wait, nested transport owner or silent UART payload fallback.
4. Keep existing UART control framing where it is sufficient; document any
   necessary stream capability or scheduling extension before coding it. UART
   may carry handover control between blocks; ExExt VDU and VDP/keyboard payload
   use parallel. Legacy and ExCom never silently gain parallel traffic.
5. No renderer changes, new display modes, audio implementation, file-service
   migration, general EDU API or unrelated cleanup. Diagnostics remain host
   tools/MOSlets where feasible. ROM reclamation may remove redundant private
   diagnostics from the experimental composition; do not relax the ROM limit.
6. Preserve exact working UART P4/EMOS rollback and original startup. Do not
   back up firmware redundantly. Respect another agent's active bench run and
   coordinate handback before hardware changes. Installed mainboard VDP may
   belong to that run; record its identity rather than assuming stock.
7. If Author input becomes necessary, stop all work at the question and await
   the answer. At the deadline, stop experimentation and leave a verified usable
   bench. Report unmet goals candidly. Production promotion needs later Author
   acceptance and an agreed version; experimental success does not select it.

## Frozen work sequence

EX01 [x] — Review the current mode dispatcher, P4 Stream/owner, eZ80 IRQ and
packet paths, ROM budget and retained fixtures. Record a bounded implementation
design including idle input, split commands/uploads and synchronous replies.
Reconcile the parent task's stale physical-failure summary against DI05's pass.

EX02 [x] — Implement the EMOS-owned ordinary ExExt adapter and P4 parser/reply
bindings using maintained component sources. Keep actual packet publication
through existing stock/EMOS effects and callbacks. Add focused real-source tests
for batching, split streams, direction ownership, idle servicing and failures.

EX03 [x] — Build complete EMOS and P4-PC images through maintained wrappers;
run their required link/ROM/configuration checks and affected host/linked-eZ80
tests. Record exact identities and hashes. Freeze each hardware candidate first.

EX04 [ ] — After bench handback, install and independently verify the paired
candidate. Preserve original startup and ordinary application files. Demonstrate
CLI entry/exit, text, small/bulk VDU, actual reply/sysvar effects and keyboard
press/release with no application output. Test split commands and buffer uploads.

EX05 [ ] — Reuse focused existing fixtures and deterministic Nurples, Rally
and Aginvadors runs in Legacy, ExCom and ExExt where applicable. Include the
Apple IIe emulator from `../agon-6502`, specifically Choplifter and Lode Runner:
these exercise framebuffer uploads rather than only drawing commands/sprites.
Use the owning projects' current builds and retained deterministic workloads;
do not adopt their unrelated pending optimizations. Record application
work/pacing and rendering/transport scopes separately, plus input/reply behavior
and the exact mode/resolution. Never infer playability solely from presented
FPS or a deterministic run without input, or promise a transport speedup for
CPU-bound emulation. Preserve the external projects' dirty work and ownership.

EX06 [ ] — Exercise bounded mode-transition and reset/recovery controls. After
an uncertain transfer, fence and recover rather than replay automatically. If
the experimental mode is not usable, restore the exact working UART pair.

EX07 [ ] — Refresh current operating/build/protocol docs, parent task, dated
log, handoff and ignored bench receipts. Commit/push logical checkpoints in
component-owner repositories, leaving other agents' dirt alone. Record remaining
limits, final readiness, durations and the Author's morning review procedure.

## References and research baseline

1. [Current direction-isolation proof](DIRECTION-ISOLATION-R01.md): fixed supply,
   independent directions and genuine 1/255/4096 echo on full-HDMI data-r20.
2. [Live coordinator](LIVE-COORDINATOR.md), [native payload](NATIVE-PAYLOAD.md),
   [parallel control](PARALLEL-CONTROL.md), [eight-bit decision](../../decisions/ADR-0026-four-lane-exext-transport.md).
3. [Architecture](../../architecture.md), [ExCom control](../../protocols/excom-console.md),
   [keyboard contract](../../remote-keyboard.md), [game timing](../../testing/game-timing.md).
4. Official Agon documentation: `agon-docs/docs/mos/API.md` RST output, VDP flags
   and sysvars; `docs/mos/Keyboard.md` cached-map and callback methods;
   `docs/vdp/System-Commands.md` serial packet contract. Official references
   remain read-only: MOS tag `v3.0.2`, VDP tag `v2.16.0`; exact commits are
   recorded with the implementation review.

Private endpoints, tool locations, installed receipts and bench coordination
belong in ignored local records. Evidence/run identities remain immutable.

## Implementation review — first bounded adapter

1. Official reference identities: MOS `v3.0.2`,
   `8336409351ee5314e02801a7b72a4f1bb5282519`; VDP `v2.16.0`,
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`. Their existing keyboard
   map API permits an application to cache a pointer and subsequently call no
   MOS API. A foreground-call-only return pump therefore cannot provide input.
2. Retain the proven version-2 exact-length offer, physical coordinator and
   completion exchange. Add an explicitly negotiated ordinary-stream binding
   and a bounded queue-status query. Control envelopes remain UART-only;
   ordinary VDU, VDP replies and keyboard packets use exact parallel blocks.
   EMOS batches byte output and services residual output/returns on VBlank.
   This first binding establishes correctness; negotiated block overhead must
   be measured rather than assumed to outperform UART for every workload.
3. The existing synchronous coordinator needs UART reply interrupts. The
   VBlank bridge will save the complete interrupted register state, set a
   non-reentrancy guard, temporarily admit interrupts during bounded transport
   service, then mask interrupts before publishing complete returned packets
   through the existing keyboard/VDP parser. Nested VBlank ticks may advance
   the normal clock but must skip transport service while that guard is held.
   Foreground writers hold the same guard. No parser or callback runs in a
   fabricated foreground interrupt context; returned packet effects run under
   the real VBlank handler. Test this bridge in the linked eZ80 harness.
4. P4 retains one parser/transport task. Its ordinary parallel receive ring is
   separate from the UART control recognizer and its packet output queue.
   A bounded I/O-only progress hook services handover/control while a retained
   VDP command waits for the rest of a split parameter/upload. The hook never
   reenters the VDP parser. Complete validated blocks alone enter the input
   ring or retire bytes from the output queue; failed blocks are not replayed.
5. Keep the console lease identity independent of the parallel session and
   block descriptor. Start the stream only after normal console preparation
   and initial query synchronization; drain it before LEAVE. The experimental
   build profile alone enables the adapter. Legacy and ExCom retain their
   existing parser, writer and keyboard paths.
6. On 2026-10-11 the Author explicitly broadened EX05 beyond Nurples and
   reaffirmed that fsim owns the bench until its noticeboard handback. Its
   deadline alone does not prove that an active run or service has ended.

## First implementation checkpoint — 2026-10-11

1. EX01/EX02 complete for the first bounded binding; physical operation and
   sustained performance remain EX04–EX06. The current physical root cause is
   resolved by boot-owned P4-PC GPIO-bank power, retained without alteration.
2. Actual P4 queue tests pass17 cases, broader parallel host discovery passes16
   suites, including82 ordinary/111 diagnostic paired native coordinator cases.
   Actual EMOS stream batching/idle keyboard/stop-drain/fault-owner tests pass;
   console tests pass both ordinary and stream builds, including independent
   lease identity and ExExt sysvar publication. Modeled peers are not hardware.
3. Linked eZ80 execution of the actual VBlank/register-save/ExExt/parser/callback
   paths passes ordinary and injected nested IRQ cases. Only physical transport
   service and the general keyboard-tick prelude are modeled. Primary/alternate
   registers, IX/IY, SP, IFF and genuine callback delivery are checked.
4. First complete P4-PC full-HDMI build passes. Revised STOP drain/close logic
   is building separately. Complete experimental EMOS passes all profile-owned
   UART/native/pad/keyboard/console/ROM checks:130335bytes,737free. Preserve this
   image independently; later builds receive new identities and fresh receipts.
5. STOP with pending returned bytes acknowledges their count and retains the
   stream, allowing reverse drain and actual-ISR publication before retrying.
   Empty STOP alone closes it. Transport sessions renew at a proved idle UART
   boundary before16-bit block numbers wrap; no uncertain payload is replayed.
6. The explicit experimental EMOS profile replaces the obsolete indefinite
   forward-epoch implementation, rather than relaxing the128KiB ROM guard.
   No diagnostics enter normal firmware. IRQ-disabled ordinary output refuses
   the parallel route; its application-compatibility impact remains to measure.

## First physical integration checkpoint — 2026-10-11

1. Complete P4-PC full-HDMI `port-008-stream-r02-b2026-10-11-10-59-20Z`
   passes its build checks and independent verification of all four installed
   flash segments. Application SHA256:
   `7eb66d7a5d446aabe47781f08898e3356bf98800a14c80c4ee3de95c44889d19`.
2. Complete EMOS `agon-emos-v0.1.24-b2026-10-11-11-06-08Z`, source
   `451bf616195f4cdbd3b09f80fc896fcddaba9c4a`, is130335bytes/737free.
   Image SHA256 `1321853bc8667e8b5562da34b856feb04ce7751895824ec087d8a3139c757c58`;
   all131072 installed ROM bytes match the image plus erased padding, SHA256
   `fb3ebcb4dfedfa628b7dfab52e682e2a30d8d8aad28f964a97ffc516ea0bfbe2`.
   The automatic post-flash startup did not regain readiness; one subsequent
   normal Agon reset recovered it. This is a retained startup failure, not a
   demonstrated fix. Original startup restored and verified byte for byte.
3. Ordinary ExCom entry, CLI typing and EMOS STATUS pass on the installed pair.
   Returning to Legacy also completes. First ExExt entry negotiates capability
   and two OFFER/COMPLETE exchanges, then loses remote readiness before the
   next CLI test. No ordinary ExExt or gameplay pass claimed. One normal Agon
   reset restores Legacy/input. Do not replay the uncertain stream.
4. Retain the first failure through normal USB-only error reporting: the native
   coordinator already knows its refusal stage, but only the private probe
   printed it; console recovery otherwise discards its original fault reason.
   Reporting once after failure has no successful per-byte instrumentation.
   Rebuild and repeat only the bounded CLI check before larger workloads.
5. Mainboard VDP remains the preceding consumer's qualified custom build, not
   stock2.16.0. No claim of stock-renderer comparison from this bench. Hardware
   reservation released during offline review/build; reacquisition required.
   Ignored evidence: `agents/exext-stream-r01/bench-r01`, including immutable
   initial installation failure, post-reset ROM verification and CLI receipts.

## EX04 corrective boundary — idle SD admission

The normal first-error log in full-HDMI stream-r03 reports `invalid ExExt
control carrier` immediately after the first two completed blocks. Source
review identifies an independent producer: `emos_admission_idle()` accepted
any non-Legacy mode after an ExCom capability grant. It could inject F6 SD
control through ordinary UART sending while ExExt permits F7 coordination only.
This is a transport-owner integration defect, not evidence of new D7 corruption.

1. Restrict automatic SD admission explicitly to Legacy/ExCom before processing
   pending replies, decisions or CLOSE. Reset its stale grant without sending
   another record in unsupported modes. File-service migration remains excluded.
2. While ExExt owns the route, refuse the ordinary private UART sender. Only
   the already-reserved parallel coordinator can use the dedicated control
   sender. Keep Legacy/ExCom behavior and the boot/transition handshake intact.
3. Add actual-source regression coverage for prior ExCom grants and pending SD
   states entering ExExt, and for ordinary-send rejection versus admitted
   coordinator-control sending. Build/verify the revised EMOS separately, then
   repeat the short physical CLI check before proceeding to fixtures.

## EX04 input-publication correction — 2026-10-11

1. EMOS-r04 installs and all128KiB read back exactly. ExCom CLI succeeds.
   ExExt now stays admitted without the stray SD control carrier, but its
   returned block can contain key down/up together. Publishing every packet
   under one VBlank hides the down state from stock MOS editor/getkey; slow
   typing still loses characters. This is a semantic scheduling defect, not
   evidence of a corrupt parallel byte or repaired interactive compatibility.
2. Stock MOS3.0.2 `mos_editor.c::getKey` and `mos_api.asm::mos_api_getkey`
   wait on `keycount` and require `keydown`. Its `vdp_protocol_KEY` replaces
   those globals for every down/up packet. Preserve those handlers/callbacks;
   EMOS must retain unpublished return bytes and admit at most one keyboard
   event per real VBlank, allowing foreground execution before the next event.
   Non-key replies may drain until that boundary. Never overwrite retained
   bytes with a new return block. Mode exit must drain through the same ISR.
3. Add actual-source combined down/up and interleaved-reply tests, plus linked
   real-eZ80 ISR/context checks over successive VBlanks. Build/check ROM and
   freeze the new identified image before physical installation. Repeat exact
   CLI text and mode exit, then continue EX04/EX05. Do not call earlier ready
   flags proof of received CLI text. Reset/release-handshake behavior remains
   a distinct EX06 concern; no extra bench/wiring/renderer scope is added.

The publication correction builds as
`agon-emos-v0.1.24-b2026-10-11-11-53-09Z`, source
`0c32deea8b593adfe7c7907bfbc19832923d4fdf`,130424bytes/648free,
image SHA256 `ca2a15a2b05c5b92850ad350c1d72348db6943c0a58a876891b7b8da29ce1ced`.
All mandatory complete-firmware/link checks pass. Linked real VBlank execution
passes combined down/up on successive ticks, both with and without a nested
IRQ; callbacks and primary/alternate/IX/IY/SP/IFF are preserved. The modeled
physical service does not establish electrical or gameplay performance.

## EX04 installed publication correction and fixture preparation

1. EMOS-r05 full128KiB ROM readback matches the identified image plus erased
   padding. Automatic post-FLASH startup again needed one normal Agon reset.
   Original38-byte startup was restored and verified; P4 stream-r03 and the
   preceding consumer's custom mainboard VDP remain unchanged.
2. Exact `EMOS STATUS` text passes in both ExCom and ExExt; ExExt reports
   Exclusive Extended / VDU route2. A later uppercase `EMOS LEGACY` loses G
   (`EMOS LEACY` in sampled text). Lowercase mode exit and listener entry work.
   This is an unresolved input-load limit, not a complete interactive pass.
   The first fixture preparation stopped before card mutations when listener
   readiness failed. Keep this failure alongside the successful status receipt.
3. Rebuild existing unmarked Aginvadors/Rally timing derivatives from the
   owners' current sources. Aginvadors source7321a0f; binary SHA256
   `cad392b4a04eb495d6cd7d5b2d5928a35e9c131ede10bcce9edf7cce5ff19338`.
   Rally source498e4c3; exact source/file hashes remain in its retained build
   manifest. Optional shared timing helpers require `maybe_unused` annotations
   for these warning-as-error builds; no timed behavior changes. Nurples uses
   retained SCAN-r02 fixtures. No game-owner source edits or deployment yet.

## EX06 reset-request correction boundary

Ordinary Agon reset can preserve the same CLOCK-low/VALID-high levels as live
UART. EMOS then mistakes old READY-high for a fresh released-peer indication,
drives VALID-low, and leaves P4's new recovery waiting for VALID-high. The
earlier physical-leaf model retried fences on deadlines; those retries concealed
the missing initial request. This explains why an extra reset or paired reset
can recover without repairing the protocol.

1. EMOS must release its data pads, hold CLOCK-high/VALID-low as an explicit
   reset request, and wait for P4 READY-low before starting the established
   CLOCK-low/VALID-high release/acknowledgement sequence. P4's existing live
   adapter observes the invalid live levels, releases its pads and asserts
   READY-low in recovery; no new peer wire opcode is needed. An old low from
   an unfinished block grants no UART: the subsequent high/low/high release
   sequence and actual adapter proofs remain mandatory.
2. Execute actual startup/pad/core code with an already-live peer and unequal
   polling. Retain negative coverage demonstrating the old stale-ready race.
   No timed UART fallback, peer-output assumption or repeated FLASH. Build and
   freeze an independently identified EMOS image before installation; repeat
   Agon-only resets and exact CLI input after installed ROM verification.
3. In parallel with this preparation, use established paired-reset recovery
   only to run the already-planned focused reply/upload controls on r05. Keep
   those results distinct from reset correctness and uppercase-input coverage.

### EX06 stronger reset proof before deployment

The first C1/V0-to-low proposal passes live-UART reset but fails when EMOS
resets during another recovery phase. It is superseded before deployment.
Retained earlier research in LIVE-QUALIFICATION-BLOCK-R04 had already rejected
a related single-level announcement; its counterexample is explicitly covered.

1. EMOS now requests C1/V0 while data pads are released, waits READY-high,
   holds C1/V1 until READY-low, then enters the existing C0/V1 recovery.
   An old high can advance only to the held CLOCK-high request, never to UART.
2. P4's boot adapter, after actual pad release, acknowledges C1/V0 high and
   C1/V1 low in every recovery phase. CLOCK-low resumes the established release
   cycle. P4 invalidates its released-pad proof before asking its owner to
   attach UART outputs, rather than waiting until LIVE. Native block ownership
   remains separate; the boot adapter never handles an active payload phase.
3. Actual EMOS foreground startup plus both physical pad/core adapters pass754
   ASan/UBSan cases, including every recovery phase with delayed P4 polling and
   no automatic retry. Old startup reproduces the live-ready race; the weaker
   one-level remedy fails all-phase coverage. These are software checks, not
   physical reset qualification. Complete paired builds and bench checks follow.
4. No SCAN timing result is claimed from the preliminary r05 invocation: console
   entry reset the P4 display to mode0, a CLI path lost one character, and LOAD
   failed. The provisional runner incorrectly proceeded to RUN; recovery and
   restoration completed. Future preparation selects route before mode in
   startup, checks each CLI preparation command and invokes only a verified
   loaded fixture. Original startup/configs are restored for offline work.

### EX06 paired build checkpoint

The stronger held-prefix pair is frozen before physical validation:
EMOS source653961b, build `agon-emos-v0.1.24-b2026-10-11-12-31-04Z`,
130513bytes/559free, SHA256
`5a0bb3dd95bdf670b3b0b3b281ab90b665bb665e41c4e169deac787cdca2ddfd`;
P4 source2b75db68, build `port-008-stream-r04-b2026-10-11-12-24-35Z`,
app SHA256 `af88216b9df6433c6b320f9146c2130af08355f03e6fff1aa82e63d767ab3c8c`.
Complete firmware/link checks and both linked nested/non-nested keyboard ISR
cases pass. The exact boot-leaf inventory now admits two connect fences (after
prefix and on failure), plus the existing start fence; no unrelated caller is
admitted. P4 has normal HDMI/services and no private probe/data-check firmware.
Successful per-block version2 USB printing is removed; first-fault reporting
remains. These identities are experimental and do not change production.

### EX06 first installed reset result

All four P4 flash segments and complete128KiB EMOS ROM independently verify.
Automatic post-FLASH startup reaches the listener on the first attempt; no extra
reset or repeat FLASH is needed. Original startup is restored/readback checked.
Three subsequent Agon-only reset pulses each return stable admitted/neutral P4
input. This closes the observed warm-reset reproduction for this pair, not every
reset-during-payload or power-loss case. Mainboard fsim VDP remains unchanged.

### EX04 tiny-query and partial-return correction

1. T01 produces120valid ordered rows, no abort/saturation/packet fault. Its
   pixel-query completion median is67.0ms (402% of one60Hz cycle), with only
   12.57application updates/s. P4 HDMI remains60.07scanouts/s: these scopes differ.
2. T03 does not run: `run` arrives as `un`. The runner initially mistakes the
   prior case's completion text for success, but missing durable T03 evidence
   rejects it. Require fresh completion/invocation evidence and inspect CLI
   errors before accepting any result. Startup and both configs are restored.
3. An actual-EMOS-owner negative with the real parser-boundary reservation
   condition reproduces a deadlock when a packet crosses the256-byte return
   cut. EMOS now retains incomplete packets outside the UART control parser,
   publishing only whole packets under the real ISR.512bytes of RAM accommodate
   a257-byte packet and next256-byte fetch. STOP can fetch the incomplete tail.
   All4096 offset/length/STOP cases pass; complete builds and hardware follow.
4. P4 removes its one-millisecond sleep between admitted native block phases.
   Existing deadlines, cleanup/recovery pacing, sole owner and IRQ/task
   preemption stay intact. This follows the continuously serviced ordinary
   parser loop. Compare tiny-query and input behavior before broader games;
   do not infer improvement from the source edit.


### EX04 installed focused comparison and EX06 teardown boundary

1. Full-HDMI stream-r05 (source7710a90e, app SHA256
   `4d5fbbf73679c69806da1e9ceea8292ab9e0a1c6780b5ffaaf16c9d34b41fe7d`)
   and EMOS-r07 (source47803b0, image SHA256
   `3c2565bbbe53ac7502aeff8fba93f4518c3351d2bbc4574a8e579804322b7d22`)
   independently verify. EMOS remains130849bytes/223free; no ROM limit waiver.
2. T01/T03 each save120valid ordered records with no fault/abort. T01 tiny-query
   completion median50.04ms versus67.0ms previously:25.3% less latency,
  16.63updates/s versus12.57. T03 median50.06ms and16.44updates/s. These
   fenced replies include transport and scheduling; they are not game FPS.
3. The next idle-input fixture never launches: after startup route/mode changes,
   P4 crashes in ESP-IDF `shared_intr_isr` while reading DW-GDMA status register
  0x50081030. Preserve the captured physical failure; no idle-input pass follows.
   One normal Agon reset after P4's reboot restores stable input. Original
   startup is restored and the bench released for offline work.
4. Pinned ESP-IDF5.5.5 commitb774170ff46c393eeb5e495ea37936038d3f4f4f
   `components/esp_hw_support/dma/dw_gdma.c::channel_destroy` unregisters
   the channel/group before freeing its shared interrupt. Last group release
   gates the register bus clock. The shared dispatcher can therefore read that
   now inaccessible status register during this interval. This exact source
   order plus the fault address supports a teardown-race explanation; hardware
   repeat controls are required before declaring the remedy proven.
5. Within EX06 mode-transition preservation, derive only this pinned SDK unit,
   joining/freeing its interrupt before dropping the group/clock reference.
   Keep the upstream checkout untouched, hash-check the input and record the
   generated source. Reuse the existing isolated DPI-derivative build mechanism.
   Add a source-derived negative/positive lifetime test, rebuild the normal
   full-HDMI candidate, verify installed bytes, repeat route/mode transitions,
   then resume the cached-map and game tests. No renderer/pixel/mode change,
   added diagnostics in EMOS or parallel electrical workaround is authorized.
6. Track the driver finding as [FWBUG-015](../../firmware-bugs.md); EX06 remains
   its implementation owner. Consumer Apple IIe test derivatives reuse the
   existing finite Choplifter/Lode Runner workloads; only startup-owned mode
   selection and durable Lode reporting differ. Owner/production code is intact.

### EX04 next bounded physical correction

Full-HDMI stream-r06 (isolated SDK teardown fix) independently verifies and
completes the cached-input test: six correct callbacks and cached-map changes
while the application only reads cached memory for five seconds. However,
Agon-only reset into ExExt fails admission twice, and recovered T07 sprite setup
faults at native completion before any result. T08/T09 remain unrun. Preserve
the separate limits; paired recovery is not a warm-reset pass. Extend existing
USB failure reporting with failed-leaf direction/length/callback facts, rebuild
the normal candidate, then isolate the failed transfer. Keep native success
paths, ownership, deadlines and production selection unchanged.

### EX04 pinned PARLIO RX descriptor correction boundary

Stream-r07 repeats T07 once after independent installation verification. Its
first failed leaf is forward RX, requested591bytes, done1, received576bytes,
callback-fault0: exactly the aligned body without its15-byte tail descriptor.
Pinned IDF5.5.5 `parlio_rx_default_desc_done_callback` handles one node per
GDMA DONE interrupt, although multiple node completions can coalesce before
the ISR. Normal EOF then reports that incomplete software total and merges
the unvisited tail. Do not accept the short count or infer lost wire bytes.

Derive only this hash-pinned SDK source for the explicit ExExt composition.
For finite RX, drain completed CPU-owned descriptors in order, bounded by the
mounted node count and transaction length; retain the existing node callback,
cache synchronization, tail merge and EOF checks. Preserve infinite RX behavior.
Execute source-derived negative/positive controls for591=576+15 and coalesced
4096-byte transfers, noncoalesced progress, short EOF, stale/duplicate interrupt
and DMA-owned nodes. Keep the SDK checkout unchanged. Record the derivative
in the build manifest; then repeat existing focused fixtures and games. This
is within EX04 split/bulk correctness and EX06 failure recovery; no new task,
wire timing, renderer change or optimistic byte-count substitution.


### EX05 poll snapshot ordering correction

Stream-r08 installs/verifies independently and T07 completes120valid records,
no abort or packet fault, confirming the formerly missing tail boundary works
in this bounded physical case. Fenced whole-update completion median67ms and
9.96updates/s remain slow. P4 currently handles POLL before its retained parser
consumes freshly retired forward bytes, so it can acknowledge an empty return
queue before generating the query reply. Within EX05, defer that complete
POLL envelope while queued forward bytes remain, matching STOP's existing
backpressure shape. An upload waiting for more bytes can acknowledge when the
ring is empty through the non-reentrant I/O-only hook. Test actual queue owner
negative/positive ordering, rebuild/verify normal full-HDMI firmware, compare
T01/T03 and retain game timing scopes. No wire format, renderer or EMOS change.

## EX05 memory boundary — frozen 2026-10-11 14:25 UTC

1. Stream-r09 repeats T01/T03 with no useful latency improvement (about50ms
   median), and its fresh T09 stops loading image3/350. Actual SDK errors report
   failure allocating GDMA link-list items, followed by native-arm failure for
   a3456byte forward block. No result is saved. HDMI stays healthy.
2. Revert the ineffective poll-deferral experiment. In explicit ExExt only,
   place the transient cache-aligned payload in PSRAM using the pinned driver's
   existing external-memory DMA and cache synchronization support. Keep SDK
   descriptors/control internal and retain all pad/callback lifetime guards.
   Earlier native qualification profiles retain their measured allocation.
3. Run actual native-leaf failure/lifetime controls for both allocations; build
   full HDMI firmware, verify all installed segments and repeat the same T09.
   A compile/heap hypothesis is not a game pass. If allocation still fails,
   retain the first error and review the internal DMA reserve before widening
   scope. Restore original startup/configs and release the bench offline.

## EX05 retained driver resources — frozen 2026-10-11 14:49 UTC

Stream-r10 moves payloads to PSRAM but T09 still fails internal GDMA descriptor
allocation (requested339bytes), before a saved result. The matched ExCom T09
passes120rows at60updates/s. Within EX05, keep the explicit ExExt native owner,
its cache-aligned4096byte PSRAM payload and disabled PARLIO RX/TX driver resources
across successful blocks. Create each direction on first admitted use, before
game assets exhaust internal DMA memory. Retain existing one-shot lifetimes for
other qualification compositions. Reattach only the admitted direction's GPIO
matrix after actual UART parking, disable/fence before return, and destroy all
resources on faults/reset cancellation before retiring the callback owner.

Test actual repeated variable-sized RX/TX blocks, retained callbacks, failed
creation/disable/fencing/cancel, and matched coordinator completion. SDK5.5.5
public create/enable/disable APIs remain authoritative; any GPIO reattachment
mirrors its exact processor-specific routing and is documented beside code.
Build/verify normal full-HDMI firmware, repeat frozen T09 first, then finite
games. No renderer, wire format, deadline, ownership or UART fallback change.


## EX05 retained payload isolation — frozen 2026-10-11 15:30 UTC

The retained-unit stream-r12 removes the observed allocation failure but its
T09 saves no result and does not answer CLI recovery. HDMI remains healthy;
this is neither a payload-integrity pass nor an application pass. Paired reset
also fails admission. Independently verified stream-r10 restores input and the
Legacy listener; original startup/config restoration is readback checked.

Keep the retained native owner and disabled driver units, but allocate their
one4096byte aligned payload in internal DMA-capable RAM at first admission,
before assets load. This isolates the newly introduced cached PSRAM payload
from resource retention, reusing the qualified internal-memory path. Do not
claim cache corruption or alter the SDK cache operations without evidence.
Run the actual native/coordinator failure-lifetime tests and real-target compile;
freeze/build normal HDMI firmware. Verify all segments, then run T01/T03 before
T09, comparing saved replies/data rather than accepting DMA byte counts alone.
Continue independent game controls and restore startup/configs after each run.
Warm-reset admission remains a separate unresolved gate.
