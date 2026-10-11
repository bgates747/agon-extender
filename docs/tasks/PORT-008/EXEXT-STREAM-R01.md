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
