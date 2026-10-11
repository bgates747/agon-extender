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

EX01 [ ] — Review the current mode dispatcher, P4 Stream/owner, eZ80 IRQ and
packet paths, ROM budget and retained fixtures. Record a bounded implementation
design including idle input, split commands/uploads and synchronous replies.
Reconcile the parent task's stale physical-failure summary against DI05's pass.

EX02 [ ] — Implement the EMOS-owned ordinary ExExt adapter and P4 parser/reply
bindings using maintained component sources. Keep actual packet publication
through existing stock/EMOS effects and callbacks. Add focused real-source tests
for batching, split streams, direction ownership, idle servicing and failures.

EX03 [ ] — Build complete EMOS and P4-PC images through maintained wrappers;
run their required link/ROM/configuration checks and affected host/linked-eZ80
tests. Record exact identities and hashes. Freeze each hardware candidate first.

EX04 [ ] — After bench handback, install and independently verify the paired
candidate. Preserve original startup and ordinary application files. Demonstrate
CLI entry/exit, text, small/bulk VDU, actual reply/sysvar effects and keyboard
press/release with no application output. Test split commands and buffer uploads.

EX05 [ ] — Reuse focused existing fixtures and deterministic Nurples runs in
Legacy, ExCom and ExExt where applicable. Record application work/pacing and
rendering/transport scopes separately, plus input/reply behavior. Never infer
playability solely from presented FPS or a deterministic run without input.

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
