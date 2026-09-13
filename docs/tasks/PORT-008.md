# PORT-008 — Implement and qualify the compatibility transport

## Current priority — stock UART alignment, 2026-09-13

The Author authorized [the granular UART plan](PORT-008/uart-alignment/PLAN.md)
without an additional plan-review stop: restore stock-compatible forward and
return transport, prove pure-data rates/correctness, then introduce rendering.
Use compiling stock code; make only necessary platform adaptations. No unrelated
improvements or bug fixes. Legacy scripts/results are research with obsolete
wiring/protocol assumptions, not drop-in current contracts. Commit granularly,
keep experimental code unpushed, and preserve working bench recovery.
This sequence supersedes ordinary command expansion until the Author reviews it.

The bounded implementation and measurements are now at a review checkpoint.
[UART findings](PORT-008/uart-alignment/FINDINGS.md) retain exact pure-data
matrices, verified channel mapping, independent wire decoding, failure/recovery
evidence and [paired graphics tables](PORT-008/uart-alignment/results/graphics-comparison.md).
The production patch changes only the two UART adapter files: stock bulk-read
and timeout behavior, FIFO refill, and reply-before-next-command ordering.
No renderer, EMOS, wiring, game or emulator changed. The first graphics run
timed out on the mainboard; an unchanged retry completed all 624 intervals.
Neither that retry nor the eight unchanged pixel differences establish general
qualification. U13 records completed firmware/startup restoration, SD/CLI checks and neutral
keyboard admission; the bench is ready for Author review.

Remaining throughput work belongs at the EMOS sender/receiver boundary:
65,535 forward bytes spent 1,530.514 ms idle with continuous P4 permission;
almost all reverse idle overlapped Agon RTS stopping P4. Reuse AUDIT-005's
stock-code analysis, preserve resident ownership/deadlines and existing EMOS
work, and freeze a separate contract before changing that path. This finding
does not authorize an unplanned stock VDP rewrite. Experimental local commits
remain unpushed pending Author review.

## Unattended ordinary command expansion — 2026-09-13

Following the Author's video-speed-first sequence, PORT-003's bounded delivery
increment is machine-complete, with review gates still open. The next finite
coverage case is [font command coverage](PORT-008/font-coverage/README.md):
ordinary MOS EXEC/VDU input, independent synthetic glyph expectations, stock
headless reference, then ExCom output and Legacy/SD recovery. No publication or
general qualification is implied; the paired QUAL-003 timing tranche stays held.

After the font case passes its machine checks, the next slice is
[bitmap and affine coverage](PORT-008/bitmap-coverage/README.md), using the same
ordinary EXEC/VDU route and independent pixel expectations. The installed P4
candidate and accepted production/startup remain unchanged.

The completed bitmap slice is followed by
[graphics-context coverage](PORT-008/context-coverage/README.md): all eight
ordinary context operations, saved drawing state and global resource boundaries,
with independent pixels and the same stock/P4 comparison and recovery gates.

After those checks pass, [palette/depth coverage](PORT-008/palette-coverage/README.md)
compares ordinary pixels and palette mutation across single-buffer modes8–11.
The indexed-versus-direct-colour distinction is explicit in its pixel oracles.

The next bounded slice is [sprite composition](PORT-008/sprite-coverage/README.md):
software sprite state/backgrounds and hardware sprite output, including full
colour over an indexed framebuffer. This preserves the retained algorithms and
compares actual presented pixels before any broader compatibility claim.

After the staged sprite checks, [Copper palette coverage](PORT-008/copper-coverage/README.md)
checks indexed row selection, palette/list changes and sprite output colours.
The finite stage plan precedes implementation and preserves the stock renderer.

## Generalized EDP callbacks — 2026-09-10

The Author selected generalized callbacks as a production EDP capability in
[ADR-0017](../decisions/ADR-0017-generalized-edp-callbacks.md), enabling useful
feedback about EDP work and state. QUAL-003 tracks the initial design discussion
and render-completion benchmark use case. Preserve EMOS-owned transport and
application mediation when the contract is implemented and qualified. The
callback model remains under discussion. Rendering completion remains distinct
from output-sink presentation; the existing stock VDU queue contract still applies.

## State

- Status: The Author accepts the first ordinary ExCom hardware console as a
  major milestone: native USB input, retained EDP browser output and UART-only
  EMOS routing. P4 logs confirm entry, Legacy return and re-entry without the
  prior activation crash; N002 is closed for that defect. Browser latency and
  wider VDP fidelity remain follow-up work. Resident keyboard reception and
  native USB Legacy CLI/gameplay were already accepted. Browser input remains
  deprecated; the r02 circuit, parallel work and full qualification stay held.
- Started: 2026-08-29 19:12 EDT
- Finished: --

## Accepted bounded increment — ordinary ExCom console

Selected by the Author on 2026-09-09 after PORT-015 completion. This section
supersedes the keyboard-only scheduling below. The existing r02/parallel hold
remains; the accepted operating-mode, activation and EMOS ownership contracts
remain binding. PORT-003 owns retained VDP rendering; this task owns the paired
transport/EMOS integration boundary. The Author's standing preapproval covers
EMOS v0.1.11, uart-excom-console-r01 and draft registry r48.

1. Define the smallest paired EMOS/P4 composition that can enter actual ExCom.
   Inspect the existing mode coordinator and activation/readiness path before
   changing it; identify stale parallel assumptions and any unresolved contract
   needed for this slice. Reuse the accepted UART1 receiver/serializer and USB
   acquisition alongside the retained VDP parser, rendering and browser output.
   Do not substitute diagnostic key echo or a second text interpreter for VDP.
2. Implement case-insensitive `EMOS EXCOM` / `EMOS LEGACY` through EMOS's mode
   coordinator and ordinary VDU dispatch. Preserve the selected USB keyboard
   source and layout. Follow the accepted mainboard mode notification/cursor
   policy and keep its VBlank clock. A missing/unready EDP must leave a usable
   Legacy console; do not publish a committed mode before its prerequisites.
   Keyboard events and ordinary VDP replies share UART1 without interleaving.
3. Prove normal prompt output and editing on EDP, an ordinary command such as
   `echo ExCom`, and return to the mainboard MOS prompt with USB input intact.
   Repeat the transition and test absent-peer entry failure. Use emulator review
   before guarded hardware deployment, then Author-observed browser/mainboard
   results. Browser input, parallel transfer, full VDP feature parity and the
   deferred USB schematic are not prerequisites for this bounded proof.

Before implementation, record the concrete coordinator/composition findings
and any decision that genuinely blocks these accepted behaviors. This is the
first console increment toward Exclusive Compatible, not evidence that all
VDP commands, queries, graphics, audio or other retained services already match
stock. Expand the EDP port through subsequent discrete command/behavior tests.

### Preimplementation coordinator/composition inspection — 2026-09-09

These historical findings bounded item 1 before implementation. The Author
subsequently accepted `PORT-008-D005`; the draft implementation below resolves
the missing console adapter and wire grammar within that idle-CLI boundary.

1. EMOS already owns a transactional mode coordinator and a single committed
   VDU backend selector. Its production adapter is conditional on the held
   parallel qualification composition. The compatible-UART backend is not
   implemented: ordinary RST 10h/RST 18h output cannot yet reach EDP through it.
2. The accepted P4 USB CLI composition admits only complete keyboard-layout
   and General Poll commands. It uses the retained VDP keyboard handler and
   serializer, but does not expose ordinary VDU or browser video. Extend that
   composition boundary using the retained VDUStreamProcessor and renderer;
   do not treat the existing diagnostic text gateway as an ExCom console.
3. EMOS's UART1 receiver currently assembles keyboard, keyboard-settings and
   admission-poll replies. An ordinary console also needs display replies
   such as cursor position and mode information. Preserve separate UART0 and
   UART1 assembly, and apply replies only from their selected authority while
   reusing stock MOS state-update behavior. Keep native USB admission intact
   across display changes and do not reset keyboard ownership on every poll.
4. A General Poll echo proves neither mode activation nor peer capability.
   Q001–Q004 still require a bounded framed, versioned, transaction-specific,
   integrity-checked prepare/commit/recovery exchange before EMOS publishes an
   EDP route. Keyboard service in Legacy is the accepted separate exception;
   it does not authorize ordinary VDU there. No activation opcode or new wire
   grammar has been selected by this inspection.
5. MODE-001 and ADR-0014 decision 36 retain a restart-mediated route-change
   baseline. The later console decisions preserve keyboard selection and
   specify a fresh destination prompt, but do not explicitly settle the
   restart carrier. D005 asks for the smallest explicit resolution rather
   than silently implementing a different lifecycle.

The bounded source précis is in the ignored local record
`agents/precis/excom-console.md`. Official references remain clean at MOS
v3.0.2 (`8336409351ee5314e02801a7b72a4f1bb5282519`) and VDP v2.16.0
(`c7ac293d2aa81ddfa693390549bcd909069c8fc3`).

### Reviewed console implementation and software checks — 2026-09-09

1. Added the resident EMOS compatible-UART adapter to its existing mode
   coordinator and ordinary byte/stream dispatcher. Case-insensitive EXCOM and
   LEGACY commands preserve keyboard selection/layout. EMOS stages EDP mode
   and cursor replies until route publication and preserves UART0 packet
   scratch while invoking the retained stock state handlers. No application
   owns the transport or mode commit.
2. Added a separate P4 `p4-console` composition: native USB acquisition and
   packet serialization share the retained VDU parser, renderer and browser
   video. Preactivation accepts only the bounded control exchange and the
   established keyboard layout/poll exception. Active control is recognized
   by the retained parser at command boundaries. The draft
   [wire contract](../protocols/excom-console.md) records the framed,
   CRC-checked, transaction/challenge-bound prepare/commit/leave exchange.
3. Built EMOS `agon-emos-v0.1.11-b2026-09-10-00-50-45Z` and P4
   `uart-excom-console-r01-b2026-09-10-00-31-17Z`, both draft. EMOS's full
   qualification wrapper, 76 product tests, stock regressions, runtime checks
   and all profile-owned linked guards pass. P4 compilation and maintained
   session integrity/replay/expiry/abort tests pass. The EMOS host adapter test
   covers staging, stock scratch preservation, stale replies and bounded
   failed-entry/leave behavior.
4. The real-EMOS headless peer passes two ExCom/Legacy cycles with ordinary
   command text and retained input, plus withheld activation followed by usable
   Legacy input. Its second renderer is native stock VDP with the maintained
   P4 session and USB key mapper. This proves neither ESP-IDF execution nor
   browser video, electrical RTS/CTS, USB acquisition or full VDP parity.
   The Author supplied the expected final mainboard screenshot and authorized
   freezing and continued preparation; local manifests, logs and images live
   under the ignored `agents/excom/` and `.emulator/excom/` records.
5. The [draft hardware sheet](../../hardware/designs/light2-harness-r03/tests/uart-excom-console-r01.md)
   defines the next bounded bench check after Author emulator acceptance and
   candidate freeze. Installed EMOS v0.1.10/P4 USB CLI and physical SD contents
   have not changed. No flash or hardware evidence is claimed here.

Implementation details worth retaining: the P4 console uses IDF hardware RTS
with its RX ring; the earlier bounded USB-only parser used manual RTS. That
new composition requires physical qualification. EMOS's shared UART lease
survives keyboard-source release while ExCom needs display replies. Its fixed
parallel profile includes the new resident units only to remain linkable; held
parallel work is not resumed. A retained parallel cleanup lease cannot be
hidden by selecting the console adapter.

### Author visual acceptance and source freeze — 2026-09-09

The supplied final emulator screenshot shows `Legacy mode`, successful ordinary
command output, `Keyboard input: extender`, and the restored MOS prompt with
cursor. The Author authorized freezing this checkpoint and continuing candidate
preparation. EMOS implementation checkpoint: `8e63cc4`. This accepts the mainboard visual gate; N001 and physical P4
text/cursor/transport checks remain open. The Author retains the SD for other
testing. Prepare locally without SD writes, serial opens, flashes or resets;
coordinate the actual paired deployment after that testing finishes.

### Candidate preparation

The reviewed source is frozen in Extender `3761076` and EMOS `8e63cc4`.
The Author's standing version preapproval and explicit freeze-and-continue
instruction authorize candidate status for EMOS v0.1.11 and
uart-excom-console-r01, recorded in registry r49. Only lifecycle/build identity
changes; console behavior and procedure remain as reviewed. Build from clean
committed inputs and prepare the installer/rollback and P4 package locally.
The Author is using the installed pair and SD; actual staging/flashing and
physical observations remain pending. N001 is not accepted as a P4 exception.

Candidate preparation completed from clean Extender `17ece3d` and EMOS
`78bec86`: `uart-excom-console-r01-b2026-09-10-01-22-40Z` and
`agon-emos-v0.1.11-b2026-09-10-01-22-40Z`. The EMOS qualification wrapper,
linked guards, runtime/boot checks and P4 build pass. The candidate EMOS also
passes the existing paired and withheld-activation control/stream/prompt
checks; native reference pixels remain outside those assertions. The guarded
installer, repeatable startup payload, P4 deployment package and verified
v0.1.10/USB CLI rollback images are prepared locally. Full manifests and the
handoff remain in ignored `agents/excom/`. No SD, Pi staging, serial, flash,
reset or power operation accompanied this preparation. Continue with paired
deployment when the Author returns the bench and SD.

### Candidate deployment started — 2026-09-09

The Author returned the SD and both powered boards and authorized proceeding.
P4 deployment `PORT-008-2026-09-10-01-36-43Z` passes independent flash
verification, exact candidate startup and PERIBOARD-409 enumeration. Evidence
is beside r03 in `tests/PORT-008-2026-09-10-01-36-43Z/`.
The guarded EMOS v0.1.11 installer is staged and the SD safely unmounted;
v0.1.10 and the earlier rollback images are preserved. Await the Author's Agon
flash result and SD return before restoring the non-flashing startup. No Agon
reset or installation was performed by the agent; paired ExCom/Legacy console
behavior and N001's physical display check remain pending.

The Author subsequently reported successful EMOS installation. The returned
SD's consumed candidate and rollback hashes verify. Preparation
`PORT-008-2026-09-10-01-41-43Z` restores matching boot smoke and the procedure's
non-flashing autoexec; the card is safely unmounted. P4 remains running, with
no new serial/reset/flash operation. The paired ordinary-console observations
are now ready for the Author; physical ExCom PASS remains pending.

### First hardware attempt and video-only rollback — 2026-09-09

The Author confirms ordinary Legacy USB input passes. EMOS EXCOM fails with
`display switch failed; current route retained` / `EMOS backend unavailable`
and returns to the mainboard prompt. Browser video appeared disconnected and
showed deprecated keyboard release controls. The original P4 HTTP assets
confirm the controls and instrumented JavaScript were still being served.
The design-adjacent `uart-excom-console-r01-observation.md` records this
informative failure without claiming a common root cause.

At the Author's request, restore video-only web assets from `a53dffd`, remove
shared keyboard/timing endpoints and snapshot instrumentation, and retire the
old browser-input composition. Retain F003/F012 network correctness fixes with
the earlier five-second socket waits. Standing preapproval supplies
uart-excom-console-r02 and registry r50; EMOS v0.1.11, the USB input code and
the ExCom activation implementation remain unchanged. The r02 sheet first
checks the restored video connection, then repeats the console test.

N002: The initial physical attempts failed; the accepted r03 result below
closes this activation defect. The r02 capture below identifies
the activation crash; the earlier emulator peer did not execute ESP-IDF or the
actual P4 display-mode transition. N001 reference rendering remains separate.

r02 from clean source `840c052` built as
`uart-excom-console-r02-b2026-09-10-01-58-58Z` and passed deployment/readback
and native USB startup in `PORT-008-2026-09-10-02-00-11Z`. A physical browser
observer verified the restored assets and advancing video (Presented 3→78
over 15.008 seconds, without disconnect/error), then closed its connection.
The existing SD startup was verified and safely unmounted without changes.
The bounded capture completed and retained all three subsequent failures.

#### N002 — ExCom preparation skips retained context initialization (closed)

`PORT-008-2026-09-10-02-01-27Z` records three matching P4 load-access panics
following PREPARE/COMMIT. Exact ELF decoding reaches `vdu_resetViewports()` →
`cursorHome()` → `getFont()->width` (null pointer + 2). Local PREPARE invoked
raw `changeMode(0)` and replaced Canvas without the retained mode routine's
context/font reset. This also restarted the native USB provider, so Legacy
output retention could not preserve working USB keyboard admission.

Correct PREPARE to invoke retained `vdu_mode(0)` through its owning processor,
including drain, fallback, context reset, mouse/cursor setup and mode reply.
EMOS ignores that early mode packet while Legacy is selected; its existing
post-COMMIT query barrier still governs publication. The control wire format,
EMOS v0.1.11, native USB source selection and video-only browser are unchanged.
Standing preapproval covers `uart-excom-console-r03` and registry r51.

Host regression executes actual control + retained mode bodies at controlled
seams, requires context reset before ACK, exercises repeat/leave and invalid
control, and rejects N002's old raw call as a negative control. Physical
entry, editing, Legacy return and USB continuity must still pass before N002
can close. A P4-only flash is sufficient; do not reflash EMOS for this fix.
Peer-restart recovery beyond this crash correction remains unqualified.

Clean source `0f10013` produced candidate
`uart-excom-console-r03-b2026-09-10-02-21-03Z`. Deployment/readback and native
USB startup pass under `PORT-008-2026-09-10-02-22-12Z`; video-only Presented
advanced 3→78 over 15.012 seconds in a bounded physical-browser check. EMOS and
SD are unchanged. A P4 log is armed for the Author's entry/return retry; those
physical results were pending at deployment; acceptance is recorded below.

#### N001 — Native reference glyph omission (open)

The native VDP library used by the isolated review intermittently omits glyphs
in the ExCom image. The complete byte stream reaches it. A timed replay with
EMOS and the UART socket removed reproduces the omission; the native VDP's own
VDP echo (variable 0110h, used only in that isolated diagnostic) confirms it
consumed the full text. Disabling its cursor did not resolve the replay.
Periodic scanout and CTS-respecting input are present; artificial byte delays
are not used to make the paired review appear to pass.

Reference library SHA-256:
`cfd0aad2108e074af207f5bc6f1b73976097851405bc7c3f8949c7a165df2cb3`.
The local reproduction, byte trace, echo and images are retained under
`agents/excom/`. The failure is isolated from EMOS but not yet attributed to a
specific native-backend or retained-VDP source defect. No upstream or reference
checkout was modified. Automated review PASS explicitly means control,
byte-stream and prompt assertions; it does not assert pixel equality.

The Author's mainboard visual review can assess normal boot, switch notices,
Legacy return and preserved input. EDP text completeness and cursor behavior
remain explicit physical checks in the new P4 composition. If the P4 reproduces
this symptom, repair it before accepting the bounded console milestone; do not
promote missing glyphs to a compatibility exception. Remove this review
limitation only with identified/repaired reference behavior and a repeated
visual check.

The whole-project identity validator also exposed a pre-existing held-r02
connectivity hash mismatch: both the recorded hash and mismatching connectivity
bytes are unchanged from HEAD. Artifact, template and P4 source-identity checks
pass separately. Do not silently rehash the frozen design; reconcile it under
HW-001's existing hardware review hold.

## Established keyboard transport scope


Established keyboard scope: carry stock keyboard packets and relevant keyboard
configuration/query traffic between EMOS and P4 over the existing r03 UART1
link at 1152000/8N1 RTS/CTS. PORT-015 owns native USB acquisition, PORT-005
owns P4 event semantics, REMOTE-001 retains deferred browser sessions, and
agon-emos [INTEG-009](../../../agon-emos/docs/tasks/INTEG-009.md)
owns persistent EMOS reception and
canonical keyboard handling. Preserve stock wire bytes and MOS APIs, sysvars,
virtual keymap and callback semantics; do not introduce a custom UART keyboard
protocol or raw sysvar/keymap transfer.

The completed PORT-010 through PORT-014 diagnostics establish bounded UART,
General Poll and rendering evidence. Those bounded fixtures release UART when
finished; their text gateway closes it after each call. Those diagnostics alone
did not prove a persistent unsolicited-key receiver. The subsequent keyboard
checks below establish that bounded receiver proof using the actual retained
P4/EMOS components; wider source/session qualification remains open.

The historical r02/parallel destination and its evidence/tooling remain below
for their original scope. They do not gate this UART-only increment. The ExCom console section now controls scheduling; no held construction,
parallel recapture or direct VDP link is resumed.

## Authority and inputs

- Current keyboard authority: SETUP-005 K009/K010, PORT-015, PORT-005,
  agon-emos INTEG-009 and the r03 hardware/test record. AUDIT-004 P013/P014 and
  A003–A005 supply stock semantics. REMOTE-001 retains the deferred browser
  contract. The r02 references below are held context.

- AUDIT-001 requirements `C01` through `C06` and wiring findings `W01` through
  `W05`.
- [SETUP-004 Work 1.c](SETUP-004.md#work-1c-execution-record) and its accepted
  low-level peripheral disposition.
- [`light2-harness-r01`](../../hardware/designs/light2-harness-r01/README.md)
  and `light2-extender-solderless-assembly-r01` as predecessor evidence only.
- [`light2-harness-r02`](../../hardware/designs/light2-harness-r02/README.md)
  and `light2-extender-solderless-assembly-r02` for the frozen common-UART and
  forward-parallel target.
- [`la03-p4-probe-fixture-r01`](../../hardware/fixtures/la03-p4-probe-fixture-r01/README.md).
- Official VDP v2.16.0 Stream/parser/packet behavior and official MOS startup
  General Poll behavior.
- [HW-001](HW-001.md), which owns the selected common V1 four-signal UART and
  one-way forward-parallel electrical core. The r02 connectivity model,
  maintained human schematic, and separate wiring order guide construction;
  signal views remain tracing/debugging references. Hardware work is on hold;
  the resistor-addition proposal was rejected under HW-001-Q011;
  stage-specific as-built records and qualification remain to be completed.
- [ADR-0016](../decisions/ADR-0016-v1-transport-electrical-core.md), which
  accepts the four-chip transport topology without closing HW-001's remaining
  design and qualification gates.
- [ADR-0014](../decisions/ADR-0014-edu-operating-modes-and-service-architecture.md),
  [SETUP-005](SETUP-005.md), and the durable QUAL-001 matrix when established.
- [Versioning and qualified-run policy](../versions/README.md).
- PORT-003 Gate F run `PORT-003-2026-08-28-15-28-59Z`, which qualifies
  `extender-vdp-v0.1.1` only as a P4-retained-parser/display/browser target and
  makes no transport or Agon-integration claim.

## Resident EMOS integration

INTEG-009 extends resident EMOS with normal compile-time linking and explicit
ownership boundaries. The Author rejected the proposed module loader and
runtime relocation; MOS-001 is cancelled in favor of resident EMOS extensions.
P4/browser work retains its existing ownership and stock UART contract.

## Current keyboard tranche

INTEG-009 Work 1 has an [accepted command/receiver contract](../../../agon-emos/docs/tasks/INTEG-009/keyboard-contract.md)
and Work 2 is accepted and frozen in EMOS commit `2e5eb23`. Its matched General Poll barrier requires P4 to serialize
previously queued keyboard frames before the reply; neither a new keyboard
wire envelope nor per-key ACK is proposed. Existing polling-only RTS helpers
are kept separate from the new owned interrupt receiver. The Author approved
EMOS v0.1.8 and registry r35; the accepted source checkpoint retains its
reviewed draft build. INTEG-009 Work 3 passed Author emulator review with the
separate `keyboard-api-probe-r01` SD exerciser; the Author authorized its
source freeze and bounded Work 4 cleanup/recovery tests. The Author approved
`keyboard-api-probe-r02` and registry r37 for that emulator fixture. All nineteen
paired and graphical stages pass; the Author confirmed the displayed recovery
result and authorized freezing this bounded checkpoint. It reuses the reviewed EMOS
v0.1.8 image unchanged; a generic isolated Fab UART1 peer exercises the real
resident interrupt/parser and public MOS keyboard APIs. This does not qualify
browser input or authorize a P4 change, physical flash or UART1 bench run.

The Author subsequently authorized PORT-005's bounded P4 controlled-key sender
and the ordinary SD observer, approving uart-keyboard-probe-r01 and registry
r38. The implementation now shares the retained acquisition/callback/serializer
path for twelve unsolicited key events after locale/General Poll admission.
Host ordering/orchestration, paired EMOS CLI/timeout and Author-supplied
graphical checks pass; candidates are frozen. The Author confirmed EMOS
installation. The paired hardware capture now passes exact stock keyboard
packets, framing, character-start CTS permission and full acquisition; the
Author confirmed Agon API checks and MOS return on all three runs. The [r03 keyboard
sheet](../../hardware/designs/light2-harness-r03/tests/keyboard-sender.md)
defines the paired scope. Browser focus/network integration followed that
controlled proof; it is now deferred under SETUP-005 K010. The
[bounded result](../../hardware/designs/light2-harness-r03/tests/PORT-005-2026-09-09-03-26-09Z/README.md)
retains the evidence; wider session, load and query-routing work remains open.

The subsequent native USB CLI/gameplay acceptance is recorded in
[PORT-015](PORT-015.md#gameplay-acceptance-and-immediate-scope--2026-09-09).
The [W3 continuation](../../hardware/designs/light2-harness-r03/tests/PORT-015-2026-09-09-23-25-54Z/README.md)
also passes ordinary editing/repeat, USB reconnect, mainboard source exclusion
and Agon-only reset readmission. The remaining qualification work uses
mainboard/extender selection; browser
focus, lease and network cleanup remain deferred with REMOTE-001.

1. [ ] Apply SETUP-005 K001–K003 and K009/K010, PORT-015 and the retained
   stock reference to the remaining transport qualification.
   Use r03 PC0/TX→P4 RX22, PC1/RX←P4 TX12, PC2/RTS→P4 CTS23 and
   PC3/CTS←P4 RTS11. Existing hardware/evidence identities are unchanged.
2. [ ] Provide P4's normal keyboard packet sender on the UART stream, sharing
   complete frames with applicable stock replies without byte interleaving.
   Key packets must not require an EMOS poll or diagnostic ACK for each event.
3. [ ] Integrate agon-emos INTEG-009's persistent owned receive path, source
   selection and stock handler effects; preserve the independent UART0/onboard
   display and clock while the bounded test runs.
4. [ ] Qualify exact key-down/up, modifiers, virtual-key map, key counter,
   callbacks and relevant settings/query effects, plus USB removal,
   source-change/reset cleanup and backpressure. Browser focus/disconnect
   cases remain deferred. Keep stock versus project-specific recovery
   behavior explicit and retain normal boot/SD/clock regression checks.
5. [ ] Record paired evidence beside r03's design tests and link bounded
   keyboard obligations in QUAL-001. A test does not qualify all of PORT-008.

These instructions supersede parallel-first/r02-only prerequisites for this
slice. Firmware identities, test details and any later physical operations
remain separate review/deployment steps.

## Historical full transport scope (held)

The following required outcomes and earlier work retain their original scope;
parallel-specific gates are not requirements for the current keyboard tranche.

## Required outcomes

1. Receive the selected forward parallel transport on the accepted P4 pins and
   deliver its application payload to the retained VDU Stream boundary in exact
   order without adding application-visible framing or semantics.
2. Return official VDP protocol packets to the eZ80 over UART1 at the accepted
   1,152,000-baud target with exact packet bytes and bounded buffering,
   backpressure, timeout, and recovery behavior.
3. Define and qualify any physical-link framing or integrity mechanism needed
   below the application byte stream as a separately versioned transport
   contract; do not confuse it with VDU or EDU command syntax.
4. Resolve and qualify shared PC0/PC1 parallel/UART ownership, transceiver
   enables, released-idle behavior, break-before-make, resets, failures, and
   coexistence with every retained P4 pin function.
5. Determine the required flow-control contract from official behavior and the
   common-UART/parallel architecture. If the candidate harness cannot satisfy it, stop
   for a separately approved harness revision before changing wiring.
6. Supply the selected eZ80/MOS-side command routing and MOS-owned response
   parsing path. Extender must not write MOS sysvars or completion flags
   directly.
7. Run the unmodified official General Poll semantics end to end before adding
   any Extender-specific discovery or capability operation.
8. Qualify representative retained VDU streams and every required VDP response
   class against exact bytes, parser state, completion flags, sysvar effects,
   timing, malformed input, reset, and recovery requirements selected by the
   compatibility matrix.
9. Keep diagnostics off the protocol return stream and preserve legacy mode's
   requirement that Extender be logically and electrically absent.

## Decision register

| Decision | Question | Recommendation | State | Downstream effect |
|---|---|---|---|---|
| `PORT-008-D001` | How can EDP hear the explicit EMOS activation request when r02 currently disables every Agon-to-P4 path in Legacy and uncommitted state? | Former proposal: assert only the common-UART Agon-to-P4 enable as a receive-only listener and use a dedicated no-CTS EMOS bootstrap sender. | Rejected by the Author, 2026-09-01 | Do not implement or reconcile the listener exception. The all-controls-released Legacy rule and corrective action remain binding; production activation requires an intended-circuit solution. |
| `PORT-008-D002` | Which current-circuit work can execute intended production code without promoting an r01 workaround? | Implement new epoch-preconditioned production forward-parallel objects and invoke them through a separately identified fixed-backend qualification composition; add no r01 behavior to the product and make no activation, UART, return, or r02 electrical claim. | Accepted by the Author, 2026-09-01 | Resolves `REMED-002-D003` in favor of replacement rather than repair/promotion of the prototype adapters. Production data-plane implementation and host tests may be separately authorized; physical and artifact gates remain. |
| `PORT-008-D003` | How should circuit construction, candidate-code tests, and eventual release proof be sequenced? | Validate r02 in its existing signal-view order; use applicable production-candidate components and scoped test callers, allow simplified electrical diagnostics, authenticate each tested candidate, and verify eventual release consumption later. | Accepted by the Author, 2026-09-05 | Supersedes D002's r01-first scheduling and the requirement to complete a release pair before stage validation. Retains production-component reuse, EMOS ownership, exact evidence, and applicable physical/mode gates. |
| `PORT-008-D004` | How should intermediate assemblies support powered measurements and logic capture? | Separate tracing-oriented signal views from a cumulative `wiring-order/` plan. Include every powered-input and shared-bank prerequisite, use permanent circuit parts only, and keep test sheets/results under that plan. | Accepted by the Author, 2026-09-05 | Refines D003's sequencing assumption. The later R32–R41 proposal was rejected; no circuit change or physical execution is approved by this process decision. Hardware execution is on hold as of 2026-09-07. |
| `PORT-008-D005` | Does the first ordinary ExCom console switch at the idle MOS prompt without restarting, or retain the older restart-mediated route-change baseline? | Allow EMOS-owned Legacy↔ExCom switching at the idle CLI, preserving keyboard source/layout and presenting a fresh destination screen; make no application display-state preservation or migration claim. | Accepted by the Author, 2026-09-09 | Supersedes the restart prerequisite for this bounded idle-console increment; retain all activation, parser, timeout and rollback requirements. |

D005's alternative is to retain restart-mediated switching. That requires
settling SETUP-005 F018 first: the restarting processor, target-mode carrier,
autoexec behavior and failure path. The recommendation avoids introducing that
carrier for an idle-console proof, but requires a bounded parser/queue boundary
and explicit recovery in EMOS and EDP. It does not authorize switching in the
middle of an application's output or state-preserving mode migration. The
paired UART activation and selected-authority reply handling identified above
are prerequisites under either choice.

The rejected alternative and source trace remain in the task-local
[activation bootstrap design](PORT-008/activation/README.md). The accepted
current-circuit boundary, exact hardware/code matrix, permissible tests, and
stop gates are in the
[production-equivalence audit](PORT-008/production-equivalence/README.md).
D003 retains that component factoring but replaces its current-circuit
schedule with the durable staged process. It does not adopt the rejected D001
activation exception or resolve HW-001-Q010.

The historical r02 activation carrier remains deferred with `HW-001-Q010`.
The next ExCom console increment must resolve the following questions for its
current r03 UART composition; that does not resume r02 construction or adopt
the rejected D001 listener. These questions still do not block the separately
bounded production forward-parallel data-plane work selected by D002:

1. `PORT-008-Q001` — activation grammar, version, integrity, transaction
   identity/replay behavior, deadlines, retries, bounded decoding, and the
   exact sender behavior required by the selected request carrier;
2. `PORT-008-Q002` — request, P4 readiness response, EMOS confirmation,
   transport-epoch, and EMOS-only formal-mode commit ordering;
3. `PORT-008-Q003` — bounded response staging and fail-back for General Poll
   as the first post-commit ordinary-VDU canary under current authority; and
4. `PORT-008-Q004` — coordinated shutdown, P4 reset, eZ80-only reset, stale
   epoch rejection, parser invalidation, and clean retry.

## Work

### Suspended work — staged r02 circuit validation

The Author placed this hardware-dependent checklist on hold on 2026-09-07.
The retained draft sequence does not authorize construction or test preparation.
Resume only after the Author has reviewed the communication requirements and
explicitly resumed the hardware work.

1. [ ] **S1 — Select and document the next installed subset.** Coordinate
   with HW-001 and QUAL-002 after the hold is lifted. Use the connection
   ledger to describe the actual subset; the earlier sequence is superseded
   and the R32–R41 proposal was rejected. Full wiring remains incomplete.
   Consume the
   [September 4 power-domain observations](../../hardware/designs/light2-harness-r02/wiring-order/tests/01-power-domains-results-2026-09-04.md)
   as preliminary evidence only; obtain the current as-built state before
   selecting another physical step. Record cumulative wiring, remaining
   omissions, safe states, and measurement scope.
2. [ ] **S2 — Select the smallest applicable firmware composition.** Name
   the P4 and EMOS candidate components that the selected stage can execute,
   their test caller and preconditions, and any missing implementation. Use a
   simplified diagnostic only with its electrical purpose and later candidate-
   code test explicitly recorded. Keep unrelated services inactive.
   Use the [method inventory](../../hardware/designs/light2-harness-r02/wiring-order/test-methods.md)
   to prepare only the next caller: passive bias first, isolated enable-bank
   diagnostics next, then EMOS-owned lane/UART callers. Existing parallel
   components do not supply an already-built UART or per-lane fixture.
3. [ ] **S3 — Prepare stage evidence and review.** Apply Work 2.e's candidate
   record requirement to code used by the stage; define bounded observations,
   appropriate host/target checks, and the applicable procedure and identities.
   Evaluate known defects only against the paths and evidence method selected.
   Do not resume the entire interrupted validator repair sequence by default.
4. [ ] **S4 — Integrate accepted stage results.** After separately authorized
   execution, keep human circuit sheets/results in the
   [r02 design test directory](../../hardware/designs/light2-harness-r02/wiring-order/tests/README.md)
   and link their electrical disposition to QUAL-002 and transport findings here.
   Expand from UART subsets through READY and the parallel lanes in the wiring
   order, then
   to the retained parser and General Poll when their prerequisites exist.
   Retain failed or partial results without claiming a complete operating mode.

### Historical/contained prototype tranche — Exclusive Extended response vertical slice

The imperative text in this tranche is retained as historical design and run
provenance. It does not authorize another r01 implementation, flash, fixture
change, or powered retry; the later corrective-action and activation stop gates
control all further execution.

Before freezing the complete multi-mode D003 contract, build a narrowly scoped
Exclusive Extended learning prototype. This is code-led architecture evidence,
not a production compatibility implementation or permission to infer the
remaining modes from one successful path. Accepted PORT-003 Gate F supplies
the retained official facade, parser integration, and browser-visible output
needed by the canary. The prototype must preserve that qualified source
boundary while replacing only the deliberately disconnected ingress binding.

1. Begin with a forward-only learning stage in the actual retained VDP port.
   Use a fixed-backend development EMOS build so ordinary official command
   bytes reach EDP/P4 firmware through
   the eight-bit parallel direction, then visibly execute a representative set
   of simple display commands. Use the existing controlled-power predecessor
   circuit only under its strict power discipline, keep the UART-return driver
   disabled, and treat the direct GPIO20/open-drain READY_N path as predecessor
   test wiring only. Qualify no either-order-power, powered-off, isolated-
   release, or production-circuit claim.
   The installed 220-ohm series values are accepted only as the experimental
   wiring state for this run; production selection remains deferred.
   The accepted visible fixture uses only official VDP commands: select a
   conventional bitmap mode, clear it, set text color, print a recognizable
   banner, reposition the text cursor, print a second string, set graphics
   color, draw lines and a filled rectangle, then change and visibly use one
   palette entry. Freeze exact bytes and expected pixels from official
   documentation before bench execution.
   The fixture originates in an ordinary eZ80 application through the normal
   MOS/VDU call surface. A fixed-purpose EMOS development build owns routing
   those unchanged bytes onto the parallel transport; the application neither
   manipulates transport GPIO nor uses a new application protocol.
   Agon and EMOS still boot in Legacy mode. After EDP/P4 has acquired its DHCP
   lease and the operator has confirmed the P4-served browser endpoint, the
   operator explicitly requests Exclusive Extended through the existing EMOS
   mode-command framework. A qualification-only forward adapter prepares and
   commits the route under that controlled authorization. With reverse UART
   disabled it cannot prove the eventual EDP handshake or a fully qualified
   runtime transition; it must report that limitation and cannot enable itself
   automatically at boot.
2. Stop for Author review of the forward-only command, display, and physical-
   transfer evidence before enabling any P4-to-eZ80 product traffic.
3. Make EDP/P4 firmware emit an exact official VDP response packet over the
   accepted UART1 return direction; use General Poll as the first canary and do
   not invent a disposable command or response protocol.
4. Route UART1 bytes into one bounded experimental parser owned by EMOS on the
   eZ80. EMOS alone may update canonical MOS sysvars and completion flags; EDP,
   applications, and resident services must not write those assets directly.
5. Exercise enough real code and controlled bench traffic to expose parser
   boundaries, packet ordering, buffering, pacing, timeout, reset, and failure
   assumptions. Record observations without generalizing beyond exercised
   bytes and signals.
6. Keep the onboard VDP outside the prototype's audio/video output and EDP
   response path. Peripheral-input integration, concurrent UART0 packets,
   Exclusive Compatible, Dual, the general EDU result domain, runtime mode
   transitions, and broad legacy-software qualification remain out of scope.
7. Stop for Author review of the bidirectional prototype and its findings. Feed accepted
   evidence back into REMED-001 Work 2.e and SETUP-005-D003 before designing
   the complete response architecture.

**Prototype gate:** before implementation or bench operation, present the
exact fixed-backend EMOS/EDP source boundary, initial visible command set,
later official packet canary, existing Exclusive Extended wiring profile,
minimum fixture, strict controlled-power safety checks, disabled-return proof,
and stop conditions for Author approval. This bounded gate does not require
the complete PORT-008.1 production transport contract or settle its Review
Gate 1.

This tranche may perform the minimum official-source review needed to preserve
wire contracts and memory safety. It must not turn into a survey-only planning
exercise before the first bounded implementation, nor may experimental code be
promoted into the product architecture merely because it runs.

### Historical prototype execution record — rejected/superseded

The dated entries in this section preserve the predecessor investigation and
candidate lineage. They do not describe a current build, selectable profile,
procedure, or qualification authority; the Immediate Work 2 chain below owns
the replacement status.

#### 2026-08-29 — P4 forward boundary checkpoint

1. **Authorization and stopping boundary.** The Author previously approved the
   prototype plan and authorized implementation, then directed work to resume
   on the preserved `light2-extender-solderless-assembly-r01` while the new r02
   board is constructed separately. This checkpoint stops after compile-valid
   P4 ingress. It makes no EMOS, fixture, deployment, electrical, or visible-
   output claim.
2. **Official application contract.** Official Agon documentation states that
   VDP input is an unframed byte stream and that `RST 10h` and `RST 18h` send
   raw binary VDU bytes. The retained `VDUStreamProcessor` still owns command
   parsing. The new adapter supplies only its existing Arduino `Stream` input;
   it does not add an application command, envelope, length, padding byte, or
   parser.
3. **Physical record boundary.** ESP-IDF 5.5.5's
   `parlio_rx_level_delimiter_config_t` explicitly defines
   `eof_data_len = 0` as receive completion when the enable signal becomes
   inactive. The r01 receiver therefore uses active-low `VALID_N` deassertion
   to terminate a variable-length physical record. This removes the suspected
   need for a below-stream length prefix. Physical record boundaries disappear
   at the Stream queue and do not change VDU byte semantics.
4. **Selected r01 binding.** `ForwardParallelStream` uses the authoritative r01
   mapping D0--D7 = P4 GPIO 22, 12, 23, 11, 32, 10, 33, 9; external CLOCK =
   GPIO14 sampled on its falling edge; active-low VALID = GPIO13; and active-
   low open-drain READY = GPIO20. It retains the predecessor's ESP-IDF PARLIO
   idiom but not its canary, fixed-size record, or application framing.
5. **Backpressure and failure behavior.** One receiver task arms a 4096-byte
   DMA record only when the 8192-byte FreeRTOS stream buffer has room for the
   complete maximum record. GPIO20 asserts READY only after DMA is armed and
   releases it immediately after completion. Any receive error, zero/oversize
   completion, READY release failure, or impossible short enqueue stops the
   receiver with READY released instead of exposing a truncated VDU stream.
6. **Return exclusion.** Every retained VDP write into this Stream is discarded
   and counted. `setVDPProtocolDuplex` remains an explicit no-op. The new build
   selects no UART output source and makes no P4-to-eZ80 claim.
7. **Build boundary.** New PlatformIO environment `p4-forward-vdp` inherits the
   accepted `p4-browser-vdp` closure, replaces only
   `disconnected_stream.cpp` with `forward_parallel_stream.cpp`, and defines
   `AGON_EXTENDER_PORT008_FORWARD`. Its machine-readable source selection
   retains the same official header-defined implementation and vdp-gl closure.
8. **Compile evidence.** `scripts/vdp-pio.sh run -e p4-forward-vdp` completed
   successfully in 56.25 seconds after correcting two compile-visible API
   details: C++17 requires ESP-IDF structure designators in declaration order,
   and `gpio_num_t` requires `GPIO_NUM_NC` rather than integer `-1`. The first
   attempt also rebuilt PlatformIO's private environment because it retained
   Python 3.12 while the project invoked Python 3.14. The final image used
   47,224 bytes of reported RAM and 1,247,354 bytes of flash.
9. **Fail-closed identity.** No firmware revision or build identity was
   assigned without Author approval. The linked image contains
   `UNVERSIONED-DO-NOT-DEPLOY`; it must not be staged, flashed, or cited as a
   candidate artifact.
10. **Next implementation boundary.** A fixed-purpose development EMOS adapter
    must route unchanged ordinary VDU bytes through the r01 sender and must
    arrange the official General Poll request needed to release the retained
    VDP startup wait while reverse writes remain disabled. BC-001 requires the
    accepted 106-byte visible fixture and mode invocation to run from root
    `/autoexec.txt`. Those changes, artifact identities, a committed physical
    procedure, and bench authorization remain pending.

#### 2026-08-30 — EMOS forward adapter and fixture checkpoint

1. **Immutable source identities.** P4 ingress remains frozen at
   `agon-extender` commit `c03656c`. The eZ80 sender, mode adapter, VDU routing,
   fixture generator, deterministic checks, and approved emulator evidence are
   frozen in `agon-emos` commit `08fec48`. Reusable product-profile,
   configured-source runtime-audit, named-worktree, and graphical-launcher
   support is frozen in `mos-agondev` commit `5079d4c`.
2. **Ordinary application surface.** `RST 10h`, `RST 18h`, and C `putch` retain
   raw ordinary VDU bytes. Standard bounded `RST 18h` maps one application
   block to one physical record without an application envelope; delimiter
   mode and single-character calls use one-byte records. Legacy continues to
   use the onboard VDP's UART0 path.
3. **Fixed-purpose physical sender.** The profile-selected EMOS adapter uses
   the preserved r01 Port C data bus and Port D READY/CLOCK/VALID signals. It
   snapshots and restores affected GPIO registers and interrupt-enable state,
   admits and completes each record through bounded active-low READY waits,
   writes data before each falling clock edge, rejects empty, reentrant, and
   over-4096-byte records, and contains no reverse-UART call.
4. **Mode authority and startup release.** Only an EMOS-owned Exclusive
   Extended request may prepare this adapter. Preparation acquires the GPIOs
   and sends exact official General Poll request bytes `23, 0, 0x80, 1`; route
   commitment follows successful physical completion. Failed preparation
   restores the GPIO snapshot and leaves the public mode in Legacy. Exclusive
   Compatible and Dual are unavailable through this physical adapter.
5. **Cold-boot fixture.** `agon-emos/projects/port008-forward/fixture.json`
   freezes the accepted 106-byte ordinary VDU command at SHA-256
   `b5d2757ebf1bdaf0132b8a2a6683e749aa57aeb265ad23a25368451860f65595`.
   Its generated 118-byte `P8VDU.BIN` includes a 12-byte `RST.LIL 18h` wrapper
   and measured SHA-256
   `3befe47e271f0351222ce1748a40bea5b8650f99f55069e1183f73d19f6e754a`.
   The eventual SD-card procedure uses `/emos.bin`, `/P8VDU.BIN`, and an
   `/autoexec.txt` containing `EMOS MODE EXTENDED` followed by `P8VDU.BIN`.
6. **Build and deterministic evidence.** The fixed-purpose EMOS image measured
   113,935 bytes at SHA-256
   `1675baf089ecd1420b59a546e5316519ec7b20e7000a3fe3f2c4493604984f9b`.
   These measurements are not deployable identities. Source tests and linked
   disassembly verify the GPIO mapping, register preservation, General Poll,
   record bound, data/clock ordering, forward-only boundary, and fixture. The
   no-macro ordinary profile also builds with the physical adapter unavailable.
7. **Non-physical qualification.** All 50 `agon-emos` tests and the complete
   configured `mos-agondev` gate passed, including translation, compilation,
   restricted runtime closure, linking, headless boot, stock shell parity, VDP
   regressions, and target ABI/FatFS contracts. The Author then approved the
   graphical emulator gate after observing provider discovery; Legacy to fake
   Dual and back to Legacy; keyboard entry; root and `/bin` directory access;
   `help echo`; `time`; `credits`; `mem`; and a responsive prompt.
8. **Bounded claim.** This checkpoint proves source integration and emulator
   compatibility only. It does not prove r01 electrical transfer, visible P4
   browser output from the fixture, General Poll response identity, canonical
   MOS response/sysvar effects, reverse UART, either-order power behavior, or
   any r02/V1 circuit property. One `RST 18h` block above 4096 bytes is
   currently rejected rather than split.
9. **Next gate.** Assign reviewed deployable EMOS, P4, fixture, procedure, and
   run identities; freeze the exact controlled-power r01 procedure; stage media
   only from those commits; and obtain separate bench authorization before the
   forward-only visible-command run. Stop for Author review of that physical
   evidence before enabling P4-to-eZ80 traffic.

#### 2026-08-31 — Forward qualification candidate preparation

1. **Approved identities.** The Author approved `extender-vdp-v0.2.0`,
   `agon-emos-v0.1.0`, `agon-transport-fixture-r01`,
   `port-008-forward-qualification-r01`, and baseline
   `port-008-forward-r01`. Independent UTC build IDs remain unassigned until
   clean committed builds begin; the run ID remains unassigned until the Agon
   cold boot that starts the physical run.
2. **EMOS freeze.** The exact source identity and fail-closed ordinary-build
   behavior are frozen in `agon-emos` commit `59c3102`. The Author graphically
   approved that emulator-coupled change; all 51 repository tests passed under
   the selected worktree. The fixed-purpose `port008-forward` profile remains
   a qualification-only EMOS configuration.
3. **P4 candidate input.** `p4-forward-vdp-identity.json` assigns the approved
   source identity to the existing forward-ingress environment. A task-local
   validator reuses the complete PORT-003 Phase-F closure and changes only its
   ingress assertions: `ForwardParallelStream`, the exact r01 startup
   diagnostic, discard-only return, and absence of `DisconnectedStream`.
4. **Staging and oracle tooling.** The task-local stager reuses the proven
   clean-worktree, identity, and factory-segment checks while emitting the
   narrower PORT-008 claim. The frame-capture tool reuses the established EVF1
   parser, saves the raw RGB888 payload, and requires the frozen 230,400-byte
   SHA-256 oracle without recording the private endpoint.
5. **Keyboardless installation.** Official unmodified `agon-flash` v1.9 already
   provides `-f`; no custom flash-utility build is required. The temporary
   two-line autoexec renames `/emos.bin` before invoking `flash ... -f`, so the
   utility's automatic reset reaches a failing rename rather than flashing a
   second time. This one-shot media arrangement, not the flash utility, is the
   BC-001 bench workaround.
6. **Physical gate remains closed.** The candidate baseline and procedure
   freeze the controlled r01 wiring, two distinct SD-card states, exact hashes,
   P4-first boot order, stop conditions, and bounded claim. No mounted card,
   firmware, wiring, power state, reset, or harness traffic may be changed
   until clean build manifests and read-only preflight are presented and the
   Author separately authorizes those physical actions.

#### 2026-08-31 — Original EMOS hardware-failure capture

1. **Failure preserved.** After restoring stock VDP v2.14.1 Dressing Gown on the onboard
   ESP32, the physical Agon again displayed the VDP banner without a MOS banner
   or flashing cursor. The normal Extender harness was disconnected. An
   external P4 used only GPIO46-to-ZDI-TCK, GPIO47-to-ZDI-TDI, and common
   ground, leaving both boards' power rails separate.
2. **Bounded observer.** A temporary `p4-zdi-probe` environment ports the
   proven `agon-recovery` ZDI operations to P4 GPIO and the USB Serial/JTAG
   console. It contains no target flash, reset, RAM-write, resume, product
   transport, or production command surface. Failed USB console input required
   an identity-gated delayed one-shot capture; all three product reads had to
   be `0007` and the eZ80 had to be running before the halt.
3. **Captured execution.** Run `PORT-008-2026-08-31-21-55-19Z` halted at
   `PC=0x0009EA`. Candidate map, code bytes, and stack place execution in
   `_wait_timer0`, called by `_wait_ESP32` during MOS startup. `gp=0` confirms
   that the official General Poll response had not completed.
4. **Timer finding.** Timer 0 control/data were `0x84`/`0x0000`. The sampled
   timeout had expired and was about to return, so the visible failure is not
   a Timer 0 deadlock; EMOS was repeatedly timing out while waiting for `gp`.
5. **UART finding.** `serialFlags=0x03`, `LCR=0x03`, `MCR=0x02`, `LSR=0x60`,
   and `MSR=0x10` show enabled 8N1 UART0 with hardware flow control, accepted
   CTS, an empty transmitter, and no received byte. This does not establish
   whether the request reached stock VDP or whether the missing response is an
   electrical, VDP-side, baud/configuration, or receive-path defect.
6. **Coherent discriminator.** Rebooting the P4 after the first halt changed
   the ZDI context, and a strict supplement refused to touch UART state at the
   changed PC. After a manual target reset, run
   `PORT-008-2026-08-31-22-27-18Z` reproduced the stopped execution state and
   read UART0 divisor `0x000B` inside the same halt epoch, restoring LCR and
   AF/MB before continuing.
7. **Identity correction.** The candidate YAML contained a mistyped,
   nonexistent long `agon-emos` object name. It now records the actual clean
   source commit `59c31026e1229395d9a9ba44f71cda7b8e78b9f3`; all existing
   short `59c3102` references already named that commit unambiguously.
8. **Root cause.** At 18.432 MHz, 1,152,000 baud requires divisor 1. In the
   AgonDev build, the inherited `16 * baudRate` expression was evaluated at
   native 24-bit width before assignment to `UINT32`; the wrapped product
   makes the subsequent division return 11 exactly. This is a source
   portability defect exposed by AgonDev, not intended stock MOS behavior.
   `agon-emos` QUAL-001 owns the narrow widening correction, deterministic
   linked regression, emulator acceptance, and replacement physical candidate.
9. **Corrective emulator gate.** The widened UART0/UART1 source passed all
   machine checks and the Author's graphical emulator review. The normal MOS
   prompt appeared, EMOS reported its expected identity and three providers,
   service calls completed, and Legacy to Dual to Legacy transitions worked.
   The correction is still uncommitted and no replacement hardware candidate
   has been identified, built from clean source, or authorized for deployment.
10. **Recovery candidate prepared.** The failed installed EMOS cannot run the
    SD-card flash utility. A temporary P4-to-ZDI recovery image therefore embeds
    the exact corrected 114,069-byte EMOS image and upstream `agon-recovery`
    flash agent. Deterministic payload regeneration, isolated source closure,
    image validation, live P4 USB-identity preflight, and remote staging pass.
    Its factory-image SHA-256 is
    `741135661f1f3ce46ddf0f7593c6144195f9e56b7d1e44d8ef69bbc8e0d0d7e6`.
11. **Physical correction passed.** Run
    `PORT-008-2026-08-31-23-11-18Z` used that one-shot image to program and
    read back the exact corrected EMOS payload. The Author then cold-booted
    physical VDP v2.14.1/MOS 3.0.2 and graphically confirmed provider
    discovery, both service calls, fake Dual, final Legacy generation 2, and
    return to the prompt. The onboard ESP32 was then directly flashed from the
    clean official VDP v2.16.0 tag and its writes verified by esptool. After an
    Agon reset, the same keyboardless fixture passed unchanged against VDP
    v2.16.0. This closes the dirty-source boot-blocker diagnostic against the
    task's official VDP baseline; it does not qualify or release the
    unversioned EMOS build.

#### 2026-08-31 — Corrected candidate refreeze

1. The UART-width correction, its physical diagnosis, and the product-owned
   linked-image guard are frozen in `agon-emos` commit `0e24b06` and
   `mos-agondev` commit `29cd336`. The Author approved and pushed both commits.
2. The forward-r01 candidate now selects those corrected authorities while
   retaining `agon-emos-v0.1.0`, the fixed-purpose `port008-forward` profile,
   and the unchanged fixture and frame-oracle bytes. The failed dirty-source
   recovery image remains diagnostic evidence and is not a candidate input.
3. The next controlled boundary is a clean identified P4 build, clean
   identified fixed-purpose EMOS build, deterministic fixture regeneration,
   and read-only deployment preflight. No flash, SD-card write, reset, power,
   or harness operation is authorized by this refreeze.

#### 2026-09-01 UTC — Identified candidate build and read-only preflight

1. **Clean authorities.** The candidate input was committed and pushed as
   `agon-extender` commit `acf9ded5c7936fe61c6377f367ac8c96c3984b78`.
   Clean `agon-emos` commit
   `0e24b06abdb322fdb4e681a21242ccfebfc8ea65` and clean `mos-agondev`
   commit `29cd336f472164156de330cf77c69a4eda450527` supplied the fixed-purpose
   EMOS source and AgonDev build system. The prepared MOS tree contains 126
   tracked files and records the exact clean EMOS source commit.
2. **P4 candidate.** Clean build
   `extender-vdp-v0.2.0-b2026-09-01-00-20-07Z` passed the task-local linked
   closure validator: 24 selected translation units, five assets, 18 required
   symbols, C++17, and all exclusions. Its application image is 1,248,288
   bytes at SHA-256
   `a243e7b2fada7f1f166fa6e7be3a2aa718d606688f1046c88af02f8aaff05ee0`;
   its complete factory image is 1,379,360 bytes at SHA-256
   `bdb9553e87ff73f2d8f5f3cdbe45192618b8c493fe75460eb35bbbe1af225dad`.
   Factory-segment equality and embedded source/build/status identity passed.
3. **EMOS candidate and fixture.** Clean fixed-purpose build
   `agon-emos-v0.1.0-b2026-09-01-00-20-07Z` passed provenance, final-image
   identity, UART-divisor, linked sender-order, General Poll, and exact fixture
   gates. Its 114,082-byte binary has SHA-256
   `8c356f95cb901edcf675e8add5567316a324e5c43559f3034c54218f3998f231`.
   Regenerated `P8VDU.BIN` remains 118 bytes at SHA-256
   `3befe47e271f0351222ce1748a40bea5b8650f99f55069e1183f73d19f6e754a`,
   containing the frozen 106-byte VDU payload unchanged.
4. **Software qualification.** All 54 `agon-emos` tests and all 106
   `mos-agondev` tests passed. The ignored build-ID-specific packages contain
   adjacent manifests, hashes, P4 closure/exclusion evidence, EMOS ELF/HEX/map
   outputs, and the exact fixture. All three controlled repositories remained
   clean after generation and validation.
5. **Read-only bench preflight.** The dedicated Pi was reachable; the stable
   P4 USB identity resolved to one serial endpoint; the logic analyzer,
   Espressif flash tool, Python, and established remote staging root were
   present. No removable SD medium was inserted: both visible reader endpoints
   reported zero-byte empty devices. The procedure therefore stopped before
   selecting a card, reading card files, staging media, or taking any physical
   action.
6. **Closed physical boundary.** No firmware was copied or flashed; no SD-card
   file was read or written; and no reset, power, wiring, probe, or harness
   traffic operation occurred. The next gate requires the Author to identify
   the exact inserted Agon card, followed by the powered-off r01 assembly and
   probe inspection and separate authorization of physical mutation.

#### 2026-09-01 UTC — Exact SD-card read-only preflight

1. **Unambiguous medium.** After the Author inserted the intended card, exactly
   one nonempty removable medium was visible: a 29.7 GB FAT volume labeled
   `AGON`. The other reader endpoint remained empty. This satisfies the
   procedure's Author-identification and no-guessing requirement for this
   mounted-card epoch.
2. **Boot-file state.** Root `/!boot.obey` and `/autoexec.obey` are absent.
   Existing `/autoexec.txt` is a 205-byte CRLF EMOS smoke fixture at SHA-256
   `e6ba3cdc87bb22461d7de131c95a44b680b33304821e9091adfb5066fda597e0`.
   It must be copied into the eventual run-specific recoverable backup before
   any authorized replacement.
3. **Official flasher.** `/mos/flash.bin` is 15,624 bytes at SHA-256
   `480b476703b798cf8d93294cac42d77cad93f7747003b061520b86685c75eb57`.
   A fresh download of the
   [official v1.9 release asset](https://github.com/AgonPlatform/agon-flash/releases/tag/v1.9)
   matched it byte for byte.
4. **Candidate-name check.** Root `/emos.bin` and `/P8VDU.BIN` are absent.
   Root `/emos-installed.bin` is the known prior 114,069-byte unversioned
   diagnostic EMOS at SHA-256
   `bf7633f9853e812d806a6528450d268db68541b12df0dcb47b4f68b15a130478`.
   It is related evidence rather than an unknown collision, but it still
   occupies the one-shot rename destination and must be preserved or relocated
   before Stage A can be staged.
5. **Stop boundary.** This check only read card metadata and file bytes. It did
   not copy, rename, replace, delete, unmount, or otherwise modify the card.
   Media backup and collision resolution belong to the separately authorized
   staging action; powered-off r01 wiring and probe inspection remains the
   other prerequisite to deployment.

#### 2026-09-01 UTC — Stage A media staging

1. **Authorization and revalidation.** The Author explicitly authorized writing
   the identified card and undertook to verify the physical connections. Before
   mutation, the host revalidated the unique mounted medium, existing
   autoexec, diagnostic EMOS, official flasher, empty candidate names, and
   identified candidate hash.
2. **Recoverable backup.** The existing autoexec and 114,069-byte diagnostic
   EMOS were copied and hash-verified under ignored task-local media-stage
   timestamp `2026-09-01-00-47-33Z`. The same files remain recoverable on the
   card as `/autoexec.pre-port008-20260901-004733.txt` and
   `/emos-installed-unversioned-bf7633f9.bin`; neither was overwritten or
   deleted.
3. **Exact Stage A state.** Root `/emos.bin` is the 114,082-byte identified
   candidate at SHA-256
   `8c356f95cb901edcf675e8add5567316a324e5c43559f3034c54218f3998f231`.
   Root `/autoexec.txt` is the exact 69-byte CRLF installation script at
   SHA-256
   `9109e37f557efc53302e53e62b28ca64ee0e6984aa6e387d69997f49fa86130e`:

   ```text
   rename emos.bin emos-installed.bin
   flash mos emos-installed.bin -f
   ```

4. **Verification and stop.** Temporary card-side copies were hash-checked
   before their final renames; all final and preserved files were checked
   again after a filesystem sync. The card was then safely unmounted. No
   firmware was flashed and no board, harness, reset, probe, or power state was
   changed. No physical run ID has been assigned.

#### 2026-09-01 UTC — Stage A physical installation

1. **Author-observed result.** The Author installed the staged card and reports
   that official `agon-flash` completed the EMOS update, reset the Agon
   automatically, and reached the expected autoexec error on the following
   boot.
2. **One-shot guard.** This observation is consistent with the first autoexec
   line having renamed `/emos.bin` to `/emos-installed.bin` before flashing.
   On the automatic second boot, the same rename cannot find `/emos.bin`, so
   MOS stops before the flash command and does not program the image again.
3. **Qualification boundary.** The installed candidate replaces the previous
   unversioned 114,069-byte diagnostic image because only the clean identified
   114,082-byte fixed-purpose build is eligible for this run. The observation
   does not yet replace the required host-side verification that
   `/emos-installed.bin` has the candidate hash and `/emos.bin` is absent.
   Stage B remains unstaged, no forward-transfer run ID has been assigned, and
   no forward-path claim is made.

#### 2026-09-01 UTC — Stage B media staging

1. **Post-install verification.** With the card returned to the host,
   `/emos.bin` was absent and `/emos-installed.bin` was exactly 114,082 bytes at
   candidate SHA-256
   `8c356f95cb901edcf675e8add5567316a324e5c43559f3034c54218f3998f231`.
   The 69-byte Stage A autoexec also retained its exact hash. This completes
   the host-side Stage A verification deferred above.
2. **Recoverable transition.** The post-install EMOS and Stage A autoexec were
   copied into the ignored timestamped media backup and verified. The Stage A
   autoexec also remains on-card as
   `/autoexec.stage-a-port008-20260901.txt` rather than being overwritten.
3. **Exact Stage B state.** Root `/P8VDU.BIN` is the frozen 118-byte fixture at
   SHA-256
   `3befe47e271f0351222ce1748a40bea5b8650f99f55069e1183f73d19f6e754a`.
   Root `/autoexec.txt` is the exact 31-byte CRLF fixture invocation at
   SHA-256
   `69d5b80f46513cf15041dff2bbf19c2993726bf5754db96bf8ac7f71a673c18d`:

   ```text
   EMOS MODE EXTENDED
   P8VDU.BIN
   ```

4. **Verification and stop.** Both Stage B files were copied through temporary
   card-side names, hash-checked before final rename, checked again after
   filesystem sync, and safely unmounted. No board was booted, no transport
   traffic occurred, and no physical run ID was assigned. The Author's r01
   wiring and probe confirmation remains the next gate.

#### 2026-09-01 UTC — P4 deployment and startup preflight

1. **Exact deployment.** After the Author reported the P4 ready to flash, the
   Pi resolved the expected stable USB identity and ESP32-P4 revision 1.3. It
   erased flash, wrote the exact 1,379,360-byte
   `extender-vdp-v0.2.0-b2026-09-01-00-20-07Z` factory image at offset zero,
   verified the write-time hash, and independently passed `verify_flash`. The
   factory-image SHA-256 remained
   `bdb9553e87ff73f2d8f5f3cdbe45192618b8c493fe75460eb35bbbe1af225dad`.
2. **Controlled startup capture.** A normal USB-UART reset with the stable
   serial endpoint held open preserved the ESP-ROM prefix and complete
   application startup. The capture reports P4 revision 1.3, QIO at 80 MHz,
   16 MiB flash, 360 MHz CPU, source `extender-vdp-v0.2.0`, the exact build ID,
   candidate status, and the selected r01 forward pin map. The successful
   receiver-start return follows hardware configuration and `READY_N` release
   in `ForwardParallelStream::begin()`; electrical idle remains an analyzer
   observation for the run rather than a claim from this software log.
3. **Network preflight.** The P4 obtained the router-reserved DHCP address and
   reported `HTTP browser service ready`; a Pi-side plain-HTTP request returned
   status 200 with the expected no-store HTML response. The Author then opened
   the live web page and confirmed that it was up. The captures contain no
   panic, assertion, failed transport setup, restart loop, or unexpected reset
   marker.
4. **Evidence and stop.** Raw flash, verify, reset-control, ROM, and startup
   logs are retained in the ignored build-specific `p4-deployment` directory
   and on the Pi staging host. No Agon cold boot or forward traffic occurred,
   and no run ID was assigned. Physical r01 harness and LA-03 probe
   verification remains the final gate before run start.

#### 2026-09-01 UTC — First forward-run failure and root cause

1. **Controlled start and observed failure.** After the Author confirmed the
   complete r01 harness and LA-03 probe attachment, run
   `PORT-008-2026-09-01-01-29-06Z` began with the P4 browser endpoint live.
   The Author cold-booted the Agon. MOS reported an error executing
   `/autoexec.txt` line 1 followed by `Internal error`. Line 1 was
   `EMOS MODE EXTENDED`; EMOS therefore did not commit the route and
   `P8VDU.BIN` did not execute. The run is failed, and no frame or visible VDU
   claim is available.
2. **Preserved electrical evidence.** The 8 MHz, 4,000,000-sample capture
   contains one bounded 135.900 ms active-low `VALID_N` window, `READY_N` low
   throughout 500 ms, and no sampled `CLOCK` edge. The no-edge observation
   does not rule out pulses shorter than the 125 ns sample interval. It also
   records `FWD_OE_N` and `REV_OE_N` simultaneously low for 1,086,412 samples,
   or 135.8015 ms. That violates r01 ownership independently of the software
   timeout; this run does not assign its physical cause.
3. **Confirmed EMOS defect.** In ADL mode, linked instructions
   `LD (_port008_length), BC` at `0x00173C` and
   `LD BC, (_port008_length)` at `0x001792` transfer 24 bits. The exact
   candidate reserves `_port008_length` at `0x0BC2FA` with `DS 2`, while
   `_port008_idle_low` begins at `0x0BC2FC`. Saving the four-byte General Poll
   length therefore writes zero-valued `BCU` over the saved inactive-VALID
   control byte. The release-wait loop reasserts `VALID_N`; P4 does not finish
   and release `READY_N`; and EMOS reaches completion timeout 2. The command
   surface exposes that value as FatFS `FR_INT_ERR`, which MOS renders as
   `Internal error`. This mechanism accounts for the screen result and sampled
   transaction duration.
4. **Why non-physical qualification missed it.** Fab has no model of this
   external Port C/Port D-to-P4 path, and runtime qualification exercised the
   fake adapter rather than `EMOS MODE EXTENDED` through the fixed-purpose
   adapter. The physical-profile linked check verified constants, General Poll
   bytes, control-flow ordering, and GPIO-write ordering, but not BSS symbol
   spans against 24-bit load/store operands. Its synthetic disassembly test
   omitted the length store and reload.
5. **Independent P4 gap.** The r01 authority assigns P4 GPIO15 to `FWD_OE_N`
   and GPIO21 to `REV_OE_N`, requires both high at reset/fault, and forbids both
   low. `ForwardParallelStream` configures data, `CLOCK`, `VALID_N`, and
   `READY_N`, but not GPIO15 or GPIO21. The source omission and the captured
   overlap are facts; whether that omission, wiring, probe attachment, or
   another electrical interaction produced the observed levels remains open.
6. **Observer deviation.** HTTP returned 200 before the run observer opened
   the USB Serial/JTAG endpoint; opening it produced a fresh P4 ROM/application
   boot. The receiver and HTTP service returned before the captured
   transaction. Any rerun must follow the existing procedure literally:
   deliberately open and retain serial through P4 startup, then wait for
   receiver and HTTP readiness before authorizing the Agon boot. Do not attach
   the observer late.
7. **Durable evidence.** The run directory contains the raw Sigrok archive, a
   task-specific deterministic forward-only analysis, sanitized P4 log,
   preflight and analyzer logs, manifest, and full diagnostic summary. Raw
   sensitive console evidence remains on the bench host and is represented by
   hash only in the tracked manifest.
8. **Closed retry boundary.** No candidate source was changed and no retry was
   attempted. A new run requires an EMOS width correction with linked
   symbol-span regression, an actor-explicit P4 direction-enable lifecycle and
   deterministic checks, new build IDs from clean committed inputs, renewed
   harness/probe confirmation, and separate Author authorization.

#### 2026-09-01 UTC — Experimental corrective retry and second failure

1. **Authorized experimental correction.** The Author approved a bounded
   hardware review before new semantic identities were assigned. The EMOS
   sender now reserves all three ADL bytes used by `LD (nn),BC`, rejects a
   nonzero upper byte, and has a linked symbol-span regression. The P4 now owns
   GPIO15 `FWD_OE_N` and GPIO21 `REV_OE_N`, preloads and releases both high,
   and selects forward only after releasing reverse. Both products remained
   visibly `UNVERSIONED-DO-NOT-DEPLOY`.
2. **Corrective startup.** The exact P4 factory image at SHA-256
   `37f1dd65d76666d0fa46a05defb47544a93dc31bd9d31ef0283cf692bde2c967`
   passed chip identification, erase, write verification, independent flash
   verification, controlled reset, revision/clock/flash checks, corrected
   direction diagnostics, DHCP, and HTTP 200. The exact first corrective EMOS
   image at SHA-256
   `7984048405e327e7e3fc6e1dc227d697b0bc7a032bcbeff631b4ecead48275c1`
   passed its complete build gates and was installed by the official one-shot
   keyboardless process.
3. **Second physical result.** Run `PORT-008-2026-09-01-02-10-50Z` again
   stopped at `EMOS MODE EXTENDED`; MOS printed the line-1 error and
   `Internal error`. The 8 MHz capture now sampled three falling clock edges
   during the initial 0.375 us `VALID_N` assertion. `READY_N` remained low, so
   the P4 receive did not complete and EMOS reached its completion timeout.
   The long first-run direction overlap did not recur; one isolated 125 ns
   reverse-enable-low sample remains a failed observation without an assigned
   physical cause.
4. **Second EMOS defect.** The proven legacy PRX-06 sender asserts `VALID_N`
   with `CLOCK` high before its byte loop, writes each byte while the clock is
   high, emits one falling sample edge, and raises the clock after every byte.
   The EMOS loop instead placed adjacent clock-high and clock-low Port D writes
   after each data write. That created sub-125 ns observed high phases and did
   not preserve the qualified PARLIO cadence. The existing validator checked
   only data-before-two-control-writes ordering and could not distinguish the
   malformed loop.
5. **Cadence correction prepared.** EMOS now mirrors the proven PRX-06 loop and
   leaves `VALID_N` inactive with `CLOCK` high. Source and synthetic tests
   require the pre-loop assertion and per-byte falling/rising phases; the
   linked-image verifier confirms the emitted instruction shape. The complete
   firmware build, UART linked check, PORT-008 linked check, and all 55 EMOS
   tests pass. The 114,085-byte unversioned image has SHA-256
   `8f659845c24a9b328f6791a7ac75a2b820df254bc601517d1b2741ed7999987b`.
   It was subsequently installed and failed the third physical attempt below.

#### 2026-09-01 UTC — Third failure and Legacy-startup safety audit

The containment record is
[`CA-2026-09-01-001`](../decisions/CA-2026-09-01-001-port008-preactivation-ready.md).

1. **Cadence-corrected attempt.** Run `PORT-008-2026-09-01-02-28-49Z`
   used the unversioned 114,085-byte EMOS image containing both the ADL storage
   correction and the PRX-06 cadence correction. P4 HTTP returned 200 before
   the Author cold-booted the Agon. MOS again stopped at
   `EMOS MODE EXTENDED` with an autoexec line-1 error and `Internal error`;
   the route did not commit and `P8VDU.BIN` did not execute.
2. **Electrical result.** The 8 MHz, 500 ms capture sampled no `CLOCK` edge,
   two incomplete `VALID_N` low spans of 0.375 us and 0.125 us, and
   continuously asserted `READY_N`. `FWD_OE_N` remained low and `REV_OE_N`
   remained high, so no direction-enable overlap occurred. The run does not
   assign the missing-clock cause among eZ80 state, r01 wiring/conditioning,
   P4 observation, probe attachment, or another physical interaction.
   Exact linked-image disassembly independently proves that the flashed
   114,085-byte EMOS artifact forces PD5 high/low state bytes, configures PD5
   as an output, writes high/low in the admission loop, and writes one
   falling/rising pair per byte. It does not prove the eZ80 pad or downstream
   conductor changed level. The next useful discriminator is therefore a
   same-attempt observation at the eZ80 PD5 source and P4 GPIO14 destination,
   not another speculative sender rewrite.
3. **Legacy EMOS route audit.** EMOS does not acquire the prototype GPIO during
   ordinary boot. Stock VDP synchronization, display-state reads, MOS banner,
   SD mount, and sysvar initialization precede `emos_init()`. That function
   selects Legacy, onboard VDP route zero, and inactive EDU. Only the explicit
   autoexec command calls `emos_port008_prepare()`. Failure invokes recovery,
   restores the saved Port C/Port D registers, and leaves the committed VDU
   backend on the onboard UART route.
4. **P4 pre-activation defect.** The P4 receiver starts independently and
   asserts open-drain `READY_N` as soon as PARLIO is armed. The third capture
   proves that state existed before the explicit EMOS request. Reverse
   P4-to-Agon output remained disabled, so this is not evidence of VDU-route
   hijacking or direction contention; it nevertheless violates the normative
   Legacy requirement that Extender be electrically indistinguishable from
   absence.
5. **Browser observation boundary.** The browser page was open but Connect had
   not been pressed. Connect owns only WebSocket establishment and frame
   credit; it does not start P4 parallel ingress and cannot explain the
   line-1 mode failure. A future visible-output run must nevertheless connect
   the browser before Agon cold boot so an emitted frame can be observed.
6. **Unapproved correction gate.** No replacement activation protocol is
   selected by this diagnosis. Before another firmware change or physical
   retry, the Author must review a bounded actor-explicit activation design
   that keeps every P4-to-Agon signal released in Legacy, permits only a
   deliberate EMOS request before commit, and fails back to Legacy. The
   missing physical `CLOCK` cause remains a separate required diagnosis. The
   later proposed D001 Dormant-listen row intentionally conflicts with this
   original literal net set. That sentence recorded the decision condition at
   diagnosis time; the Author subsequently rejected D001, and `HW-001-Q010`
   now owns the intended-circuit request-path requirement.
7. **Prepared physical discriminator.** The subsequently authorized
   [READY-isolated two-point CLOCK diagnostic](PORT-008/forward-r01/proposed-clock-discriminator.md)
   changes no firmware or SD content. It observes eZ80 PD5 and P4 GPIO14 in
   one attempt while the disconnected sender-side `READY_N` remains pulled
   high, forcing EMOS to time out and recover without sending a record or
   committing the route. The attempted run did not actually establish that
   temporary electrical state; its corrected disposition is recorded below.

#### 2026-09-01 UTC — READY-isolated two-point CLOCK diagnostic

1. **Authorized execution.** The Author approved procedure
   `port-008-clock-discriminator-r01`, temporary fixture
   `port-008-ready-isolated-fixture-r01`, and probe map
   `la03-clock-discriminator-r01`. The existing firmware and SD-card content
   remained unchanged. A post-run Author correction established that only the
   probes moved: the actual `READY_N` conductor remained connected to P4
   GPIO20 throughout, so the authorized temporary fixture was not realized.
2. **Trigger correction.** A read-only analyzer check proved that stopping
   `sigrok-cli` before a D4 edge preserves no archive. Because absent D4 is a
   required discriminator outcome, the Author approved a D6 rising power-on
   trigger with 240,000,000 samples at 24 MHz and 10 percent pretrigger.
3. **Screen result.** Run `PORT-008-2026-09-01-15-01-14Z` stopped on autoexec
   line 1 with `Error accessing SD card`. The fixed adapter's READY-admission
   timeout returns value 1 through MOS's FatFS result domain, where value 1 is
   rendered as `FR_DISK_ERR`; this is the expected transport timeout, not
   evidence of an SD read failure. The route did not commit and `P8VDU.BIN`
   did not execute.
4. **CLOCK result.** Source probe D4 at Agon header pin 14 / eZ80 PD5 remained
   low for all 240,000,000 samples. Destination probe D5 at P4 GPIO14 had no
   post-trigger edge, and D4/D5 matched for every post-trigger sample. No P4-
   only observation failure can explain this attempt's missing source clock.
5. **Validity limit.** D6 contained three post-trigger low spans totaling 14
   samples—0.083 us, 0.417 us, and 0.083 us. D3 contained two brief low spans,
   including the same 0.417 us interval, without a bounded record. Those lows
   were observed on the still-connected live net, not an isolated sender-side
   node. The defining electrical precondition was absent, so the run is
   invalid for this discriminator regardless of those levels.
6. **Bounded disposition.** Preserve only the direct sampled observation that
   D4 never went high and D5 had no post-trigger edge. Do not infer the sender
   branch that would have executed under isolated READY, and do not change the
   P4 receiver or eZ80 sender on this evidence alone. The separate
   pre-activation READY defect remains contained by `CA-2026-09-01-001`; no
   corrective firmware or wiring is authorized by this diagnostic.

#### 2026-09-01 — Activation design-only pass

1. The accepted r02 truth table releases both Agon-to-P4 forward enables, the
   P4-to-Agon UART-return enable, and `READY_N` while Legacy is committed or a
   transaction is uncommitted. The accepted pull-discovery rule nevertheless
   requires EDP to receive an explicit EMOS request before driving a response.
   No request can cross the accepted no-path row; proactive READY merely
   reverses ownership and remains prohibited.
2. `PORT-008-D001` proposed at this pass the minimum firmware-capable
   correction: for
   controlled beta only, P4 asserts the common-UART Agon-to-P4 enable as a
   bounded input-only activation listener while UART return, parallel forward,
   and READY remain released. P4 initializes the UART receive side and decoder
   before asserting that enable and releases it before teardown. Because the
   disabled UART-return bank also disconnects P4 RTS from `PC3/CTS1`, the first
   request requires a bounded dedicated EMOS sender that does not wait on CTS.
   Enabling U1 adds no incremental PC0/PC2 input load, but exposes those levels
   to P4 and actively sinks one Agon-domain control, changing the corrective-
   action condition and accepted truth-table/quiescence wording. It therefore
   requires Author review plus corrective-action and architecture/hardware
   reconciliation and does not close `HW-001-Q007` or qualify strict V1 Legacy
   absence.
3. Keeping the no-path row instead requires a new hardware arm/request path.
   A complete parallel listener would expose more pins and cannot return
   identity/capability data without another epoch; network, browser, timed, and
   operator-side arming violate EMOS pull-discovery ownership.
4. The task-local activation record preserves the constrained state envelope,
   deterministic host/source oracles, later physical-evidence boundary, and
   four downstream questions covering control grammar, EMOS-only commit
   ordering, post-commit General Poll failure handling, and reset/shutdown.
   They were unselected at the conclusion of this pass; the Author disposition
   below supersedes its recommendation.
5. The former recommendation would have moved decision-bearing activation work
   to the current common-UART/r02 topology. Because it changed accepted truth-
   table interpretation and test behavior, acceptance would have required new
   artifact identities and same-turn CA/ADR/architecture/HW-001 reconciliation.
   Existing r01 adapters and failures remain predecessor evidence or bounded
   diagnostic inputs only. The missing physical r01 CLOCK cause remains a
   separate required diagnosis or explicit withdrawal gate before PORT-008 can
   close; this pass did not authorize that physical work. No source, protocol
   version, hardware profile, fixture, procedure, build, deployment, or powered
   state changed. Files outside that historical pass's then-authorized scope
   remained untouched; this is not a current audit exclusion.

#### 2026-09-01 — Author disposition and production-equivalence audit

1. The Author rejected D001. EDP/P4 firmware will not assert a receive-only
   common-UART forward enable in Legacy, and EMOS will not gain a dedicated
   no-CTS bootstrap sender for that workaround. Accepted Legacy and corrective-
   action conditions remain unchanged. An intended-circuit solution must make
   an EMOS-originated request observable without turning the beta exception
   into production behavior.
2. The Author accepted D002's development boundary. R01 and r02 share the exact
   forward data, CLOCK, VALID, READY endpoint pins and logical polarities. In a
   stable active-parallel epoch, the intended GPIO15-low, GPIO17-low,
   GPIO21-released tuple also functions on r01 because GPIO17 is unconnected
   and GPIO15 enables the r01 D0/D1 forward buffer. Production sender, PARLIO,
   Stream, parser, display, and browser components can therefore execute
   unchanged on r01 from that epoch boundary inward.
3. R01 cannot execute the intended full-duplex UART state safely: the r02
   GPIO15-low/GPIO21-low UART tuple would enable opposing r01 PC1 drivers.
   Activation, UART return, RTS/CTS, General Poll confirmation, MOS response
   state, mode transitions, break-before-make electrical behavior, reset,
   power, isolation, and r02 timing must not be claimed from r01.
4. The fixed-backend qualification caller/profile may supply only the active-
   epoch precondition. It must be separately identified and excluded from
   release; it may add no application command, wire grammar, r01 product
   branch, discard-success production output, or supported EMOS bypass.
5. At disposition time, no complete P4 or EMOS PORT-008 adapter was promoted.
   The selected code
   boundary separates P4 epoch-control, bounded transactional PARLIO ingress,
   composite duplex Stream, UART return, and activation roles; EMOS receives a
   new epoch-preconditioned record engine below its existing semantic
   dispatcher. The detailed task-local audit owns the object boundary, exact
   test matrix, evidence gates, and must-wait list.
6. The audit also records an inherited RST 18 return-value discrepancy:
   official documentation says bounded mode returns the last byte, while
   official MOS and current EMOS return zero after success. The production
   factoring must not silently change de-facto behavior; no upstream correction
   or broad regression work is selected now.
7. No source, protocol, hardware artifact, fixture, procedure, build,
   deployment, or physical state changed. Files outside that disposition-time
   evidence set were not used as authority or modified. This is a historical
   scope statement, not a current audit exclusion.

### Work 2 execution chain — production forward components and evidence

The Author authorized the component replacement on 2026-09-01. D003 now
integrates its remaining work with the staged r02 queue above. Completed
implementation stays available; open work is selected by the next stage's
requirements rather than by restarting the historical r01 sequence.

1. [x] **2.a — Freeze the executable boundary.** Use the task-local
   production-equivalence audit as the design input. Keep the active parallel
   epoch as an explicit precondition; exclude activation, UART return delivery,
   response/sysvar integration, physical deployment, and intended-circuit
   electrical qualification.
2. [x] **2.b — Implement the production P4 data plane.** EDP/P4 code must
   separate shared-pad/control ownership, transactional PARLIO ingress,
   flattened byte queueing, the retained parser-facing Stream, and an
   out-of-band output-fault latch. Host fakes exercise the same maintained
   classes; production code contains no r01 or test-success conditional.
3. [x] **2.c — Implement the production EMOS data plane.** EMOS/eZ80 code must
   separate local parallel-epoch pin ownership from the record hot loop, split
   arbitrary bounded RST 18 streams below the physical-record limit without a
   wire envelope, bound READY waits, preserve raw byte and ABI behavior, and
   avoid whole-record interrupt exclusion. EMOS task `INTEG-002` owns the
   repository-local implementation.
4. [x] **2.d — Build the non-release fixed-backend composition.** A
   qualification-only P4 top level and EMOS profile may procedurally assert the
   externally prepared peer/active-epoch precondition; EMOS does not detect or
   validate that condition. They must call the production entry points, emit no
   activation or precommit General Poll, add no supported application bypass,
   and remain excluded from release manifests.
5. [ ] **2.e — Authenticate the candidate components used by the stage.**
   Record committed source/configuration and generated inputs, actual target
   compiler commands and relevant flags/defines, object/archive-member and
   image digests, and evidence that the selected link consumes the claimed
   components. Review that bounded record under the staged process. Retain
   tested target objects for later comparison; host-native tests establish
   behavior only. Complete release-pair fingerprints and a production P4
   release consumer are not prerequisites for this stage record. The existing
   comparator remains provisional and cannot certify affected records while
   its defects remain open.
6. [ ] **2.f — Validate the selected component boundary and hand off.** Run
   relevant P4 host, EMOS source/link, and target compile/link checks, evidence-
   method checks, and a bounded review for the selected stage. Preserve the
   human emulator gate whenever an EMOS/emulator change requires it. Require
   actual retained-parser fault injection when parser behavior is claimed;
   lower-level Stream tests do not substitute for it. Record physical and
   identity prerequisites without executing a physical operation here.
7. [ ] **2.g — Verify eventual release consumption.** When production
   compositions exist, compare their consumed candidate objects and linked
   contracts with the recorded stage inputs. Reuse evidence only within its
   tested scope; changed objects or integration require impact review and
   relevant repeat tests. The release-pair comparator's repair, fingerprint,
   and capture work belongs to this gate if that method is selected. This
   deferred gate does not block S1--S4 or candidate evidence under 2.e.

**Immediate Work 2 stop gate:** Stop before any flash, SD mutation, wiring or
probe change, reset, power operation, or decision-bearing physical run. Also
stop before selecting production activation grammar/carrier, enabling UART
return on r01, or representing captured P4 output as delivered MOS traffic.

#### 2026-09-01 software-only execution status

This dated execution record and its interruption handoff preserve the earlier
Work 2.e definition. D003 and the current checklist above supersede their
repair order and release-pair prerequisites for new stage work. Their failed
or invalid capture dispositions remain unchanged.

1. Work 2.b is implemented. The maintained P4 boundary now consists of
   `P4EpochHardware`, transactional `P4ParlioIngress`, `P4ParallelDataPlane`,
   an allocation-free flattened SPSC queue, `ExtenderVdpStream`, and a shared
   first-fault/cancellation channel. The ESP32-P4 target adapter owns the exact
   data, CLOCK, VALID, READY, forward-bank, return-bank, and shared-UART pads.
   It removes the GPIO12/GPIO11 UART output owners before asserting either
   parallel-forward enable, arms PARLIO before READY, uses release/acquire
   callback publication, bounds task waits, and unwinds direction before
   receiver teardown. None of these maintained objects contains an r01 or
   test-success branch.
2. The non-release P4 half of Work 2.d also exists. Environment
   `p4-port008-nonrelease-qualification` links those production objects into
   the real retained `VDUStreamProcessor`, display, frame, snapshot, network,
   and browser closure. Its fixed caller supplies only a live parallel epoch;
   its output binding visibly captures accepted bytes, latches every output
   failure, owns no UART, and is explicitly forbidden by the ordinary browser
   and forward source manifests. This is a compile/link composition, not an
   approved artifact or physical-run identity.
3. The sanitizer host suite passes 25 cases and the complete task-local Python
   discovery passes 46 tests. Coverage includes every byte value, physical-
   record flattening, maximum-record reservation, overlong-record rejection,
   partial-start cleanup/retry, active-record timeout versus indefinite idle,
   cancellation/record-admission arbitration, one-byte advertised-read
   preservation, stale-epoch rejection, output-fault cancellation, owner
   cleanup-before-revocation, false-live boot rejection, and concurrent SPSC
   publication. The ESP32-P4 composition builds and links with
   the four intended transport objects and excludes the prototype and
   disconnected Stream objects. The target build is API/source-closure
   evidence only; real GPIO, stopped-CLOCK, stuck-VALID, timing, and peripheral
   reset behavior still require a separately authorized target-runtime run.
4. Work 2.c is implemented in EMOS under `INTEG-002`. The production epoch
   owner, raw 4096-byte-chunking record engine, target GPIO helpers, bounded
   elapsed-time and stalled-clock waits, interrupt-safe lifecycle, and private
   semantic-route lease are integrated with the ordinary RST 10, bounded and
   delimiter RST 18, and C-runtime dispatcher paths. Backend zero retains the
   onboard UART path; backend two reaches only the common production parallel
   route. `open_UART1()` now reserves the same lifecycle lock before its first
   flag, Port C, or UART mutation and releases it only after publishing UART1
   active, so a UART transition and a parallel epoch cannot both win.
5. Work 2.e remains open. The retained schema-v1 checker reports only
   preliminary compile-output/final-symbol similarity and always sets
   `equivalence_proved: false`. The new product gate and EMOS/P4 actual-step
   recorders now implement the clean Git/source/tool, producer, final-link,
   contribution, symbol, disassembly, role, identity, and cross-composition
   boundary. Unversioned EMOS role-pair records and partial P4 diagnostics now
   exist, but all predate retained gate/policy corrections and are invalid.
   The gate's full allocated-section EMOS relocation projection and exact
   composition-dependent coordinator dependency rule are retained work in
   progress. Two JSON boolean-as-integer checks and the generic recorder's
   literal reserved-placeholder collision remain open. The comparison remains
   ineligible until clean rehearsal freezes every command fingerprint and
   fresh records use approved identities. A production
   P4 release consumer still does not exist, so P4 qualification/release
   equivalence cannot yet be claimed.
6. Work 2.f remains open. Lower-level output-fault tests do not replace the
   required real retained-parser General Poll and Mode Information failure
   injection at every emitted byte. No flash, SD mutation, emulator behavior
   run, deployment identity, wiring/probe change, reset, power operation, or
   physical transfer occurred in this pass.
7. A fresh v10 isolated clean-scope snapshot contains 146 files and reports
   prepared-source identity
   `0e24b06abdb322fdb4e681a21242ccfebfc8ea65+tracked-dirty`. The complete EMOS
   host suite passes 64 tests. The ordinary image is 116,520 bytes at SHA-256
   `a4c2d3f87286dd32e7b2e3a7b30786ae4156208e2440ba096c733f76256d09a4`;
   its ELF SHA-256 is
   `8315db0fd2f519a16d35d4b668d74ed9b6d52e65cee0c1ca947acf9b64f88373`
   and its map SHA-256 is
   `75a5a45de6099c1e12596752000defde76e5b46efb30705988792f5218179357`.
   The non-release fixed image is 116,966 bytes at SHA-256
   `4f0c0db7d419c6a0f17fe9d07dd3bd2107fb110371fa0a44b444c1e3417d2e66`;
   its ELF SHA-256 is
   `7186c10373f6f642eedc0949fb443cd5dd7b6eedeed43a44b86f877c78bb382d`
   and its map SHA-256 is
   `539375306a4f830ec300131e033b556df519fd0cee9819bff63364f4ffbcc341`.
   All five common production objects are byte-identical across the profiles.
   The linked gates establish exact ordinary-entry-to-dispatcher and
   dispatcher-to-production-route call edges, exact fixed-coordinator-to-
   wrapper and wrapper-to-common-route call edges, predecessor exclusion,
   UART1 guard presence, normal-profile exclusion of fixed-only symbols, and
   the fixed profile's non-release identity. The linked bridge check also fixes
   the bounded RST 18 argument and success/failure epilogue instruction shape;
   extracted production-code host tests cover coordinator commit, recovery-
   failure retention/retry, and public error mapping. These gates do not
   establish clean source/tool authority, authenticated final-link object
   provenance, release identity, runtime route selection, target execution,
   activation or response behavior, emulator behavior, or electrical behavior.
8. An adversarial build exposed and corrected a local EMOS wrapper defect: an
   explicitly selected `MOS_WORKTREE` was not forwarded to the generic
   firmware targets. Regression coverage now requires every EMOS build and
   qualification wrapper to pass the selected worktree. This is project build
   tooling, not an official MOS defect.
9. An incremental P4 configure/build can leave `firmware.map` containing a
   CMake compiler-probe link when the application ELF is already current. The
   bounded target-closure validator fails closed on that file. The recorded
   software result was regenerated by a clean application relink and then
   revalidated; build success alone is not map or object-provenance evidence.
10. The production factoring and adversarial reconciliation exposed the
    additional local EMOS defects `PORT008-PROV-P009` through `P016`: three
    lifecycle-publication races, verifier claim overstatement, the UART1/
    parallel Port C serialization gap, an initially profile-optional UART1
    guard, discarded adapter-recovery failure, and leakage of private parallel
    statuses into the public command-error domain. All were introduced by
    project production/integration work rather than official MOS. P012's final
    verifier checks and P015/P016's transaction/error-domain corrections pass
    in the v10 suite and linked builds. The integrity audit owns their exact
    provenance and evidence boundaries.
11. The final P4 adversarial pass exposed the additional project-created
    `PORT008-PROV-P017` through `P021`. The first target wait treated a quiet
    epoch as a failed record; the Stream could turn an advertised byte into
    synthetic `0xFF` after a concurrent fault; fault publication and record
    admission lacked one total order; the non-release owner could revoke its
    lease after failed cleanup; and retained process-task creation failure
    continued into boot/network publication. None has an upstream
    implementation counterpart. The corrected boundary keeps one armed
    advertised transaction through idle, preserves exactly one advertised
    read, uses a nonblocking sequentially consistent admission edge with
    quarantine/post-commit checks, retries cleanup before revocation, and
    returns before false-live publication. Host/source/compile evidence passes;
    target-runtime and retained-parser execution remain open.
12. The Work 2.e audit exposed `PORT008-PROV-P022`: EMOS forwarded its selected
    prepared tree, but the generic `mos-agondev` root preflight authenticated
    the default stock source/tree pair before compiling that different EMOS
    tree. This project build-orchestration defect has no official-MOS
    counterpart. Generic `mos-agondev` commit `7e00798` binds the caller's
    maintained source and prepared tree, rejects assembly-output symlink
    redirection before object recipes, and derives profile provider authority
    from linked target objects. EMOS forwards both inputs. A fresh identified
    target build remains required; the correction does not promote v10.
13. The same audit exposed `PORT008-PROV-P023`: the non-release P4 PlatformIO
    environment supplied its qualification role through global build flags,
    so the three production translation units carried a qualification-only
    command input. This was introduced by project qualification integration;
    official VDP has no counterpart. The role is now defined only in two
    qualification-only translation units, source selection rejects global
    reintroduction, and a fresh target capture remains required.
14. The audit also exposed `PORT008-PROV-P024`: ordinary and fixed EMOS
    profiles supplied different identity/role definitions component-wide even
    though only `src/emos.c` consumes them. This project profile defect has no
    official-MOS counterpart. Generic `mos-agondev` now scopes those flags to
    the selected source and both EMOS profiles select only `src/emos.c`; fresh
    ordinary/fixed records must prove equality of the five common production
    units.
15. The audit then exposed `PORT008-PROV-P025`: the project P4 identity
    injector supplied source identity, build ID, and lifecycle status through
    component-wide definitions although only the boot sketch consumes them.
    Qualification and release build IDs differ by construction, so exact
    common-unit command equality would otherwise be impossible. Official VDP
    has no Extender identity layer. Work 2.e must scope varying identity bytes
    to the boot owner and prove that the captured/linked identity matches the
    approved build record; the comparison gate must not waive the difference.
16. The fixed EMOS profile exposed `PORT008-PROV-P026`: it substituted the
    qualification label for the EMOS firmware source/build identity and had no
    independently revisioned composition input. This was created by project
    profile integration; official MOS has neither layer. The profiles now
    share the `agon-emos` source identity and lifecycle lineage while every
    produced ordinary or fixed image requires its own immutable build ID. The
    fixed image additionally carries the separately revisioned
    `port-008-forward-qualification` identity. Those inputs are scoped to
    `src/emos.c`, and the procedure identity is reported as non-release.
    Approved successor identities and fresh target records are still required.
17. `PORT008-PROV-P027` records the corresponding P4 composition-identity
    omission. The fixed P4 caller originally had no independently revisioned
    `port-008-forward-qualification` input. Official VDP has no such
    composition. The boot identity owner now alone consumes and reports that
    qualification identity; ordinary environments reject it and common
    production units remain neutral. Author approval and fresh target evidence
    remain open.
18. `PORT008-PROV-P028` records a local EMOS wrapper defect: the wrapper used
    `AGONDEV_TOOLCHAIN` for linked-image inspection but failed to pass the
    selected root to recursive generic producer targets. Official MOS has no
    AgonDev wrapper. Firmware, fixed, and qualification targets now forward the
    exact absolute root and a focused regression covers all three. This does
    not authenticate a pre-correction build.
19. `PORT008-PROV-P029` groups false-authentication paths caught before the
    new generic recorder's retained baseline: Make-pattern source scoping,
    non-unique session association, incomplete producer-record binding, nested
    response indirection, and incomplete driver-selected assembler authority.
    All arose in new `mos-agondev` evidence infrastructure rather than official
    MOS. Generic commits `7e00798` and `64bbf34` correct them; the early
    rehearsal is invalid and was not retained.
20. `PORT008-PROV-P030` groups pre-baseline P4 recorder defects: rendered shell
    text was initially treated as actual argv, the child environment/runtime
    roots and SCons response grammar were incomplete, generated identity/input
    paths were underprotected, and the backend selected by Espressif's
    intentional assembler/inspection dispatchers was not authenticated. These
    were local evidence-tool defects, not upstream compiler defects. Direct
    execution, exact round trips, rooted runtime/input inventories, anchored
    header writes, and explicit dispatcher/backend identities now fail closed;
    a clean real PlatformIO capture remains required.
21. `PORT008-PROV-P031` groups pre-baseline defects in the product gate's
    command, role, lineage, root/symlink, session, identity, and linked-
    instruction comparisons plus early closure overstatement. A longer build
    ID could initially satisfy the source-identity substring check. Official
    MOS/VDP provide no
    counterpart. The corrected gate revalidates raw records and requires exact
    policy-owned commands, distinct sessions/builds, matching controlled
    lineage, exact objects, direct nonzero contribution, independently
    terminated identities, owned symbols, and normalized linked instructions.
    Duplicate registry IDs and digit-shaped but impossible UTC build timestamps
    also fail before eligibility. Its command fingerprints intentionally
    remain null until clean rehearsal, so current validation is ineligible
    rather than permissive.
22. The first clean PlatformIO rehearsal exposed `PORT008-PROV-P032`: the
    project-owned P4 capture hook tried to identify itself through Python's
    `__file__` global, but PlatformIO/SCons executes an extra script with
    `exec()` and supplies no such global. Official VDP has no actual-step
    recorder or corresponding hook. The capture therefore stopped before an
    evidence directory was created. The hook now resolves the exact committed
    `pio/capture_p4_actual_steps.py` boundary from SCons' authoritative
    `PROJECT_DIR`, and a host regression executes the active-install path with
    `__file__` deliberately absent. A new committed clean capture is still
    required; the stopped invocation authenticates nothing.
23. The first EMOS gate replay exposed `PORT008-PROV-P033`: the generic
    recorder substituted an enclosing `BUILD_TOOL` root when an exact nested
    `BUILD` root was followed by a quote in Clang's `-###` output. The gate's
    longest-root delimiter grammar therefore rederived different bytes and
    rejected the record. Official MOS has no recorder or driver-selection
    probe. Generic `mos-agondev` commit `6d4008c` now applies one global
    longest-candidate pass with the gate's conservative right-boundary set and
    adversarial prefix/delimiter coverage. Both otherwise successful EMOS
    captures remain invalid for fingerprint freeze and must be repeated with
    the corrected recorder.
24. `PORT008-PROV-P034` was a local P4 evidence-tool defect: the TEMPFILE
    callable and authenticated PlatformIO/SCons `piomaxlen` response contract
    did not match the real producer. The retained correction exercises a real
    forced long command. Official VDP has no corresponding recorder.
25. `PORT008-PROV-P035` was a local P4 recorder defect: the spawn wrapper could
    delegate an ambiguous or unclassifiable possible target action. The
    retained correction fails closed. Official VDP has no recorder counterpart.
26. `PORT008-PROV-P036` was a local P4 gate defect: claimed source, output,
    ELF, and map fields were not rebound to exact expanded-argv operands. The
    retained correction performs that binding; official VDP has no such gate.
27. `PORT008-PROV-P037` was a local gate path-classification defect: rooted
    directories could be treated as files and malformed or missing rooted
    tokens were underclassified. The retained correction rejects those forms.
28. `PORT008-PROV-P038` was a local gate identity defect: rooted spellings
    could stand in for canonical file identity and hardlink aliases could
    create duplicate ambiguity. The retained correction uses canonical
    resolved identity and rejects aliases.
29. `PORT008-PROV-P039` groups local gate containment defects involving
    relative roots, absolute suffix escape, unsafe policy suffixes, descendant
    symlinks, and root-leaf retargeting. The retained correction rejects them.
30. `PORT008-PROV-P040` was a local generic-evidence semantic-hash defect:
    zds2gas input was hashed as raw bytes rather than its UTF-8 universal-
    newline text contract. The retained correction hashes that semantic text.
31. `PORT008-PROV-P041` is a local Python/JSON exact-type defect. Broad integer
    checks are corrected, but boolean values can still satisfy the P4
    `ascii_occurrences` and Python-runtime `version_info` integer comparisons.
    Those two residual paths remain open and no evidence may be accepted.
32. `PORT008-PROV-P042` was a local EMOS comparator defect: linked
    disassembly treated valid `r_imm24` rebasing as drift and did not cover the
    full allocated object contribution. The retained work-in-progress
    correction verifies and canonicalizes relocations across allocated
    sections; its host suite passed 62 tests, but it is not a final baseline.
33. `PORT008-PROV-P043` was a local policy defect: the comparator had no
    policy-owned dependency delta for the composition-dependent EMOS
    coordinator. The retained policy permits exactly qualification-only
    `${PREPARED}/src/emos_parallel.h` and no release-only dependency.
34. `PORT008-PROV-P044` is a local normalization-collision defect. The retained
    P4 validator rejects literal reserved placeholders in raw argv, but the
    generic `mos-agondev` recorder can still collapse literal `${ROOT}` and a
    substituted real root to the same normalized value. That recorder path
    remains open. Official MOS and VDP have no normalization counterpart.

#### Work 2.e interruption handoff

**Current use:** Historical continuation context for the provisional comparator,
not the current task queue. D003 supersedes its ordered repair-and-recapture
sequence for stage validation; consult S1--S4 and Work 2.e/2.g above.

**Checkpoint disposition, 2026-09-05:** The Author authorized preserving this
work in a commit and push as the GPT-5.6 Sol to GPT-6 Astra handoff. The
uncommitted-state descriptions below record the interruption state; the
checkpoint retains those corrections as provisional source, not as an accepted
baseline. Astra subsequently ran the complete task-local host suite: all 155
tests passed. Work 2.e remains incomplete, earlier captures remain ineligible,
and no release-equivalence or physical claim follows. The dated development
log records the checkpoint scope, the existing hardware version-validation
failure, and the sequencing recommendation that remains subject to review.

This handoff records the 2026-09-02 Author stop boundary and was reconciled
against the task-local
[production-object gate](PORT-008/production-equivalence/object-equivalence/README.md),
REMED-002, the integrity audit, and the development log on 2026-09-05. The
defect descriptions and general eligibility blockers remain in those
authorities; this section records only the worktree state and continuation
context a fresh agent cannot reconstruct safely from their prose alone.

1. **Where the pass stopped.** The Author halted the pass after the focused
   host tests had passed while the independent adversarial review was still
   incomplete and before cleanup, commit, command-fingerprint rehearsal, or
   fresh capture. The
   validator, test, and policy work completed across the interruption was
   subsequently approved for retention as work in progress, not accepted as a
   final baseline. No Work 2.f, deployment, emulator, target-runtime, reset,
   power, wiring, or other physical operation occurred.
2. **Earlier retained P4 recorder cluster.** The uncommitted P4 cluster is
   `vdp/pio/capture_p4_actual_steps.py`, its focused test file, and its
   task-local README. It authenticates the exact loaded PlatformIO 6.1.19 /
   SCons 4.8.1 `piomaxlen` response-file contract, exercises an actual forced
   long command, and refuses to delegate ambiguous possible target actions.
   The associated P4 gate changes bind claimed source/output/ELF/map paths to
   the actual expanded argv and strengthen rooted-path identity and
   containment. These changes address P034--P039; they have not produced a
   complete P4 capture.
3. **Comparator/policy cluster active at the stop.** The uncommitted
   `validate-production-object-provenance.py`, its focused test file, and
   `production-object-policy.json` replace the old EMOS selected-symbol
   linked-disassembly comparison with a full allocated-section projection.
   The gate verifies every non-relocation linked byte, accepts only proved
   `r_imm24` relocation rebasing, resolves section targets from exact map
   contributions and named targets from a unique final symbol, and
   canonicalizes only verified relocation spans. The policy also owns the
   coordinator's exact dependency delta: qualification alone adds
   `${PREPARED}/src/emos_parallel.h`. The change was made because the pinned
   eZ80 objdump renders relocated absolute operands; the former comparison
   reported ordinary link-layout rebasing as drift and did not cover the full
   allocated contribution.
4. **Last diagnostic checkpoint.** A direct, read-only diagnostic against the
   invalid unversioned EMOS release/qualification pair produced identical
   canonical linked projections for all five equality units:

   | Equality unit | Canonical projection SHA-256 | Allocated sections: bytes / relocations |
   |---|---|---|
   | `emos-parallel-owner` | `00f80362556606f40e5d62111549011bac0a8fb5804db380e3425f5fe4bc3068` | `.bss`: 40 / 0; `.rodata`: 12 / 4; `.text`: 1256 / 131 |
   | `emos-parallel-engine` | `a36e01854c45443ead6e1f4e4433782edda591d11e01ddb57271c81bca104ac9` | `.text`: 1398 / 55 |
   | `emos-uart-owner` | `793031e8f2da9129005e974e5d12ca0c256a78d9d99743d2afb25fd300c43ef4` | `.text`: 462 / 22 |
   | `emos-parallel-io` | `77511e089fc1d78d806318641ea4a000d6a226a87632e1663acb9006fb3ecca5` | `.STARTUP`: 393 / 7 |
   | `emos-vdu-serial-bridge` | `ed254558a4ee265a2b8b97179ddd5011bd3b7569a0344d561951d5c0dc1b0ef7` | `.STARTUP`: 364 / 19 |

   This was a debugging observation, not a gate report or evidence claim. Both
   captures predate the retained authority/policy state, use unapproved
   identities, and remain ineligible. The ignored local Work 2.e evidence root
   for run `PORT-008-2026-09-02-03-31-14Z` preserves the raw diagnostic
   context; do not edit, move, commit, or promote it.
5. **Last test checkpoint.** Before interruption, all 43 focused P4-recorder
   tests passed. After the P042/P043 changes, all 62 focused production-gate
   tests passed, including correct rebasing; wrong relocation and
   non-relocation bytes; unsupported, overlapping, and out-of-range
   relocations; ambiguous map/symbol resolution; unaligned section parsing;
   and the exact dependency delta. No complete task-local suite, product build,
   or new capture was run after the final retained edits, so the focused
   results must not be generalized.
6. **Environment gotcha.** The strengthened root checks allow only an
   explicitly permitted root leaf to be a symlink, not descendant symlinks.
   A fresh EMOS rehearsal therefore needs a newly provisioned
   `venv --copies` Python environment. The diagnostic copied environment is
   local setup material only. The production-object gate README owns the
   durable capture rule.
7. **Investigate and finish before rehearsal.**

   1. Review the complete retained Work 2.e diff independently, with particular
      attention to the real pinned objdump section/relocation grammar, exact
      map-contribution resolution, relocation expression/addend bounds,
      allocated no-content sections, and rejection of any unverified byte
      normalization. Existing tests demonstrate selected cases but do not
      substitute for this review.
   2. Close P041 by applying exact-integer validation to P4
      `final_elf_strings[].ascii_occurrences` and every element of captured
      Python `version_info`, then add direct Boolean-collision regressions.
   3. Close the remaining generic-recorder half of P044 in
      `mos-agondev`'s
      `projects/mos-port/tools/record_target_step.py`. The recorder must
      reject or encode literal reserved placeholders before root substitution
      so a literal `${ROOT}` cannot collide with an actual root. Retain a
      regression proving the two inputs remain distinguishable. The clean
      generic repository was at commit `6d4008c` at handoff; recheck its state
      rather than assuming it is unchanged.
   4. Rerun both focused suites and the complete task-local host discovery,
      review the resulting diff and documented claim boundaries, and commit
      all controlled gate/recorder/policy inputs before any new capture.
   5. Provision the copied EMOS Python environment, perform a new unversioned
      two-role command-fingerprint rehearsal, review every candidate command,
      commit the frozen EMOS fingerprints, and then recapture both roles
      because the policy digest will have changed. Do not reuse the existing
      rehearsal directories.
   6. Keep P4 qualification rehearsal separate. P4 cannot complete a
      release/qualification pair or freeze a release policy until a real
      production P4 release consumer exists; the browser composition is not a
      surrogate. Approved successor firmware and qualification-composition
      identities remain an Author gate for eligible final captures, but not
      for explicit unversioned mechanical rehearsals.
8. **Review provenance.** The interrupted auxiliary adversarial reviews did
   not leave an accepted patch or completed review result. P041 and P044 are
   the recorded actionable findings from that boundary. A fresh agent must
   verify the retained code directly and must not infer review completion from
   the 43- or 62-test checkpoints.

### PORT-008.1 — Freeze transport and wiring contracts

1. Extract the exact official Stream, UART, packet, timeout, flow-control, and
   General Poll contracts from the pinned VDP/MOS sources and documentation.
2. Reconcile those contracts with `light2-harness-r02`, using r01 PARLIO and
   115,200-baud results only as predecessor evidence, plus the selected P4
   peripherals and QUAL-001 rows.
3. Produce a pin-conflict, ownership-state, flow-control, buffering, and
   failure-state analysis without changing hardware.
4. Identify whether the candidate wiring is sufficient. Any required wire,
   component, enable-logic, or pin change is a proposed new harness revision and
   an Author stop gate.

**Review Gate 1:** Author approves the transport contract, physical ownership
model, test phases, and either the existing harness sufficiency finding or a
separate hardware-revision proposal before production implementation beyond
the bounded prototype tranche.

### PORT-008.2 — Implement the P4 transport boundary

1. Add the project-owned parallel receiver and Stream-compatible adapter behind
   the retained VDU parser boundary.
2. Add the project-owned UART1 packet-output adapter and selected pacing/flow
   control without changing official packet generation.
3. Keep P4 pin assignments visible, centralized, and traceable to the approved
   harness profile.
4. Add deterministic host tests for byte ordering, boundaries, buffering,
   timeout, error, recovery, packet transparency, and ownership state.
5. Update source selection, dependency graphs, compatibility matrix rows, and
   provenance-rich inline comments for every unavoidable hardware substitution.
6. Authenticate each stage's selected candidate objects under Work 2.e.
   Preserve their exact build and link records; compare eventual release
   consumption under Work 2.g. A diagnostic that does not use a product
   component makes no claim about that component.

### PORT-008.3 — Implement the eZ80/MOS integration boundary

1. Outside the bounded prototype tranche, implement the selected command
   backend and UART1 response-parser route only after `SETUP-005-D001` through
   `D003` authorize the relevant mode behavior.
2. Reuse MOS's canonical packet/sysvar ownership wherever selected; do not
   create a competing sysvar writer.
3. Preserve stock UART0/onboard-VDP input handling and legacy fallback according
   to the accepted mode design.
4. Provide bounded eZ80 fixtures for exact transport and parser behavior before
   attempting broad application tests.

### PORT-008.4 — Qualify physical transport

Develop the circuit evidence incrementally under S1--S4; the complete
transport requirements below are the destination, not prerequisites for power,
bias, or individual-path measurements. Qualify each selected subset only after
its relevant safety, construction, and procedure review.

1. Freeze versioned firmware, MOS/eZ80 fixture, harness, analyzer fixture,
   procedure, build, and run identities before each decision-bearing run.
2. Requalify all eight forward data lines and control signals on the clean
   project, including integrity, backpressure, sustained transfer, reset, and
   recovery.
3. Qualify UART1 return at 1,152,000 baud and the accepted flow-control behavior.
4. Measure shared-net ownership and prove no contention through every selected
   transition and failure state.
5. Preserve raw analyzer/serial evidence and bound every claim to signals
   actually observed or independently validated.

### PORT-008.5 — Qualify official compatibility traffic

1. Run the official General Poll startup synchronization as the first
   end-to-end Agon/MOS/Extender canary.
2. Expand only through compatibility-matrix-selected command/response classes;
   do not invent disposable application protocols to stand in for them.
3. Verify exact MOS-owned packet, completion-flag, and sysvar effects.
4. Exercise selected fragmented, back-to-back, stalled, malformed, overrun,
   reset, and recovery cases according to the accepted strict/non-strict mode
   policy.

**Review Gate 2:** Author reviews qualified transport and General Poll evidence
before this task can gate integrated compatibility claims.

## Dependencies and sequencing gates

- Active bench constraint BC-001 requires every eZ80 text fixture to be
  cold-boot executable through the Agon SD card's root `/autoexec.txt`, with no
  interactive keyboard prerequisite. Record the exact invocation and a
  non-keyboard evidence path before each affected run.
- QUAL-001 supplies accepted compatibility obligations before corresponding
  compatibility claims. Its incomplete mode matrix does not prevent bounded
  mode-neutral circuit/component evidence in PORT-008 or QUAL-002.
- PORT-003 Gate F provides the qualified retained VDU/parser/mode lifecycle and
  browser-output target. It does not qualify physical ingress, General Poll,
  EMOS routing, or any Agon integration; PORT-008 must establish those claims
  through its own approved stage and integration gates. Power, bias, and
  isolated transport checks need no browser or retained-parser dependency
  unless their selected observation method uses those services.
- `SETUP-005-D001` and `D002` historically authorized only the bounded
  Exclusive Extended prototype above. `PORT-008-D002` now supersedes its
  implementation disposition with new production data-plane objects and a
  non-release fixed-backend qualification composition. SETUP-005-D003 remains
  open and gates production response parsing, generalized MOS sysvar
  integration, Exclusive Compatible, Dual's separate EDU result domain, and
  broad compatibility qualification. Prototype findings remain visibly
  provisional until the Author accepts their D003 disposition.
- QUAL-002 owns staged power/bias/electrical checks before a complete transport
  exists. Only active-transfer tests require the relevant controlled transport
  candidate; full power/reset and mode claims retain their integration gates.
- PORT-008 Gate 2 is required before PORT-003 Gate G or later tasks claim
  end-to-end Agon compatibility through Extender.
- Read `HARDWARE.local.md` before any physical operation. No bench action is
  authorized by this task plan; each candidate procedure and physical run
  requires the established review and deployment gates.

## Stock-UART hardware boundary

The Author clarified during
[`AUDIT-2026-08-23-001`](../decisions/AUDIT-2026-08-23-001-operating-mode-semantics.md)
that `light2-harness-r01` is not a candidate implementation of Exclusive
Compatible mode's stock-UART transport. It was designed for the predecessor's enhanced
parallel-forward/reverse-UART architecture and must not be incrementally tested
or relabeled into stock physical or firmware conformance.

HW-001 owns the authoritative r02 common UART/parallel candidate. D003 develops
its UART circuit subsets before parallel completion, using the applicable
candidate drivers and bounded diagnostics. A UART lane or enable test does not
claim Exclusive Compatible mode or resolve its lifecycle/response contract.
Those claims require the relevant firmware design and integration evidence.
No stock-UART bench test against r01 is authorized by this process; powered r02
tests retain their stage-specific procedure gates.

The final task split remains under SETUP-005. Historically, this boundary did
not change PORT-008's then-approved Exclusive Extended split-link prototype; it
prevented that work and its harness from being mistaken for the newly
identified stock-UART profile. D002 now supersedes the prototype's
implementation disposition: retain it as evidence and implement the production
forward data plane behind the accepted fixed-backend qualification boundary.

## Explicit exclusions

- No reverse high-speed parallel bus.
- No new VDU/EDU discovery packet merely for testing.
- No adoption of the predecessor's fixed eight-byte UART experiment as product
  protocol.
- No direct P4 writes to MOS memory or sysvars.
- No Console8 pin assignment; that requires a separate harness task.
- No printer, terminal, ZDI, serial updater, or other accepted maintenance
  carve-out implementation.

## Completion criteria

1. Both review gates are approved.
2. The selected Light 2 transport and any required revised harness are
   versioned and qualified at target speed.
3. The official General Poll passes end to end with exact MOS-visible effects.
4. Required command/response classes have deterministic host evidence and
   controlled physical evidence or an accepted blocker/deferral in QUAL-001.
5. Shared-net ownership, flow control, resets, error recovery, and coexistence
   have no unexplained qualification gap.
6. Source selection, dependencies, compatibility matrix, procedures, artifacts,
   runs, and development log agree.
7. Every accepted PORT-008 action from REMED-002 has passed its task-local
   validation or has an explicit Author-accepted deferral that prevents its
   prototype evidence from supporting a product claim.

## Accepted REMED-002 findings and retained risk

The Author accepted the PORT-008 dispositions in
[REMED-002](REMED-002.md). Detailed evidence and provenance remain in
[`AUDIT-2026-09-01-001`](../decisions/AUDIT-2026-09-01-001-open-task-and-implementation-integrity.md),
and the pre-activation physical hold remains owned by
[`CA-2026-09-01-001`](../decisions/CA-2026-09-01-001-port008-preactivation-ready.md).
The original intake did not authorize a firmware change, flash, powered
transfer, protocol decision, or promotion of the fixed-purpose adapters. The
later accepted D002 boundary authorizes only the software replacement work
   recorded above; it does not authorize a flash, powered transfer, protocol
   decision, or promotion of either predecessor or the source-frozen but
   unidentified replacement.

1. [ ] **F004 reachability split:** With PORT-003, PORT-004, and SETUP-005,
   ensure that every audio or updater command reachable through physical
   ingress consumes or safely rejects its complete grammar before the retained
   parser resumes.
2. [ ] **F005:** Replace the infinite external-clock completion wait with a
   bounded timeout/abort contract that releases READY and all direction outputs
   after stopped CLOCK, stuck VALID, timeout, reset, or cancellation.
3. [ ] **F007 consumer:** Stage forward builds only through PORT-003's corrected
   cryptographic build-to-source authority and add an A/B rejection fixture;
   do not maintain a weaker PORT-008 provenance path.
4. [x] **F008 consumer:** HW-001 reconciled the maintained r02 schematic
   digest, generated complete/focused views, and version record on 2026-09-01.
   This closes only the frozen-input identity defect; r02 remains unqualified
   and every construction, activation, return, and physical gate stays open.
   The later connectivity/profile discrepancy recorded on 2026-09-05 is
   tracked under HW-001 S3 and prevents a present clean frozen-input claim.
5. [ ] **F013:** Make receiver startup transactional: represent started state
   explicitly, unwind every partially allocated/configured resource in reverse
   order, restore released outputs, and prove deterministic retry after each
   injected failure.
6. [ ] **F014:** Make every analyzer return nonzero for invalid or insufficient
   evidence, validate each procedure precondition and claimed timing/data
   property, and freeze the exact accepted script hash with the run.
7. [ ] **F015:** Reconcile the baseline, candidate, procedure, and linked EMOS
   build source identities under the versioning policy before another package
   or run is named.
8. [ ] **R001:** Establish the ESP-IDF callback-to-task ordering guarantee or
   use explicit lock-free synchronization for published receive state before
   claiming portability.
9. [ ] Preserve `PORT008-PROV-P001`'s permanent EMOS divisor correction and
   require its clean build identity and qualification evidence.
10. [ ] Preserve the durable width, sender-cadence, fail-safe direction, and
    activation invariants from `PORT008-PROV-P002` through `P005` without
    promoting the exact prototype adapters. Keep `P006` as closed historical
    diagnostic provenance. Record `P007`'s upstream RST 18 documentation/source
    mismatch without changing current de-facto behavior unless the accepted
    Extender-specific trigger is met.
11. [x] Record `PORT008-PROV-P008` through `P016` as local EMOS integration or
    evidence-tool defects, retain their focused regressions, and do not treat
    their pre-freeze build results or later source commit as target-object
    provenance or release evidence.
12. [x] Record `PORT008-PROV-P017` through `P021` as local P4 target,
    data-plane, Stream, qualification-owner, or guarded boot-integration
    defects; retain their focused regressions without treating host/source/
    compile checks as target-runtime qualification.
13. [x] Record `PORT008-PROV-P022` as a local generic-build orchestration
    defect, retain selected-source/tree and assembly-output-path regressions,
    and require fresh post-correction evidence rather than promoting v10.
14. [x] Record `PORT008-PROV-P023` and `P024` as local P4 qualification-profile
    and EMOS/generic-build profile defects, confine role flags to
    qualification-only or role-owning sources, and require fresh captured
    commands and objects rather than relying on unused-definition assumptions.
15. [x] Correct `PORT008-PROV-P025` by scoping P4 source/build/status identity
    bytes to the boot identity owner, binding the captured values to the
    approved build record, and retaining exact common-unit command comparison.
16. [x] Correct `PORT008-PROV-P026` by sharing the EMOS source identity and
    lifecycle lineage while requiring a distinct immutable build ID for each
    produced image, separating the non-release qualification-composition
    revision, scoping those values to `src/emos.c`, and retaining fresh
    identified-build and record gates.
17. [x] Record and correct `PORT008-PROV-P027`/`P028` in the P4 composition
    identity and EMOS recursive toolchain boundaries; retain Author identity
    and fresh-capture gates.
18. [x] Record `PORT008-PROV-P029` through `P031` as local pre-baseline
    recorder/gate defects, retain adversarial regressions, invalidate every
    early rehearsal, and keep null command fingerprints fail-closed until a
    clean rehearsal supplies reviewable candidates.
19. [x] Record and correct `PORT008-PROV-P032` as a local P4 recorder-
    installation defect, retain a no-`__file__` active-install regression, and
    reject the stopped invocation as evidence.
20. [x] Record and correct `PORT008-PROV-P033` as a local generic-recorder
    root-normalization defect, retain longest-root/delimiter/prefix regressions,
    and require both EMOS roles to be recaptured.
21. [x] Record `PORT008-PROV-P034` through `P040` as local recorder/gate
    defects and retain their fail-closed corrections and regressions.
22. [x] Record `PORT008-PROV-P041` through `P044`; retain the P042/P043
    work-in-progress corrections, and keep P041's two exact-type paths and
    P044's generic-recorder collision explicitly open.
23. [ ] Close the pre-activation corrective action only after the Author
    accepts an EMOS-requested activation design, deterministic checks prove
    fail-closed Legacy and transition behavior, and General Poll completes
    without an unexplained CLOCK or READY gap. Because D001 is rejected, a
    separately authorized run must prove all four P4/U4 controls and P4 UART
    TX/RTS return drivers released before the request; no Dormant-listen
    exception is available.

Every existing capture or build claim materially dependent on F007, F014, or
F015 must receive an explicit retained, rerun, superseded, or withdrawn
disposition before it is reused.


### Repository validation note — 2026-09-08 keyboard Work 3

The new keyboard fixture registry entry and templates validate. The full
version-record validator stops at the already committed r02 profile's
`connectivity.yaml` integrity mismatch (expected `560ab589...`, actual
`c68e4d4f...`). Both files match HEAD and were untouched by keyboard work.
Reconcile that held-design record before resuming r02 qualification; it is
not evidence against the r03 UART keyboard fixture.

The Author accepted the graphical result and explicitly authorized freezing this bounded sender/observer checkpoint, then preparing the paired hardware test. Reviewed builds retain their original draft status; candidate packaging and physical qualification follow separately.

## Focused browser typing increment — 2026-09-09

The Author authorized implementation and preapproved versioning. REMOTE-001's
bounded r01 record now owns the browser-session/test scope. P4 maps US physical
key events into the retained serializer; EMOS v0.1.9 receives keyboard packets
while its resident text gateway sends the SD program's echo. UART1 remains
1152000/8N1 on r03; ordinary VDU/ExCom routing and parallel work are unchanged.
Registry r40 and browser-keyboard-probe-r01 are draft, with human review and
physical typing pending. Earlier documentation-only freeze statements describe
the previous gate and no longer prohibit this authorized increment.

## Graphical typing review accepted — 2026-09-09

The Author supplied the review screenshot showing `aB3?`, newline `z`,
BROWSER TYPING PASS (8 edited characters), mainboard input and the MOS prompt.
This accepts the bounded graphical result, not physical browser typing.
Standing version preapproval advances registry r41 and the unchanged EMOS
v0.1.9/browser-keyboard-probe-r01 implementation to candidate for clean builds.
The reviewed draft builds and their results retain their original identities.
At that checkpoint, guarded Agon installation and paired P4/browser
qualification were next; subsequent observations follow below. Current input
priority is native USB as recorded in this task's State and Intent.

## First physical browser typing feedback — 2026-09-09

The Author confirms visible typed characters, Enter and Backspace on hardware,
with noticeable latency and apparent focus/capture loss while typing. P4
connection loss is a suggested cause, not an established finding. REMOTE-001
I001/I002 were assigned the bounded measurement and diagnosis; their findings
are retained in that deferred task. No full hardware
qualification or candidate-status change is made. Escape/MOS return and the
result byte are unconfirmed for this physical session. The operator observation
is retained beside the r03 deployment, separately from its earlier run record.

### r03 first working hardware observation — 2026-09-09

The Author reports ExCom now working, with significant browser display latency.
The existing capture `PORT-008-2026-09-10-02-22-54Z` records PREPARE/COMMIT,
LEAVE, and another PREPARE/COMMIT, without a panic or P4 restart in the
retrieved interval. This first report supported corrected activation. The Author subsequently
accepted the functional milestone; the completed capture and precise evidence
limits are recorded below.

The browser provider sends complete RGB888 frames: 640×480×3 = 921,600 bytes.
Snapshot production has a deliberate 200,000 µs minimum interval (5 Hz), and
the runtime counters agree with approximately five publications per second.
That cadence alone introduces up to roughly 200 ms waiting before transfer,
with encoding/transfer/browser presentation adding delay. At 5 fps the raw
pixel payload is 36.864 Mbit/s per fully receiving client. No latency intervals
or Ethernet throughput were measured here; do not attribute all observed delay
to bandwidth. Browser output optimization remains subsequent bounded work.

### First ordinary ExCom console accepted — 2026-09-09

The Author explicitly accepts this as a major success and authorizes the
progress commit. `PORT-008-2026-09-10-02-22-54Z` preserves the successful
P4 capture beside the r03 design tests. It records entry, one Legacy return
and re-entry, with one startup and no recorded panic/console fault. The
working-console observation and log close N002's activation crash. Do not
infer a second completed return or individually unreported editing checks.

This freezes the first ordinary UART-only ExCom console with native USB input
and retained EDP browser output. EMOS v0.1.11 and console r03 remain candidates;
no lifecycle status/version change accompanies functional acceptance. The log
was stopped and retrieved without resetting either board. Significant browser
latency is acknowledged: the current complete RGB888 frame path is capped at
5 Hz. Subsequent increments should improve browser presentation and expand
retained VDP fidelity. N001, broad transport qualification and held parallel
work are not closed by this milestone.

### Nurples gameplay included in the accepted milestone

The Author subsequently clarified that they played Nurples rendered by EDP
on the P4, with native USB input. Apart from the five-fps browser presentation,
the graphics looked great by their visual assessment. The accepted milestone
therefore includes real-game graphics/input beyond ordinary CLI output. The
design-adjacent run record includes this additional operator observation; no
exact game-binary identity, frame comparison or complete VDP parity is inferred.
