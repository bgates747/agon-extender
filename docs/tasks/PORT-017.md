# PORT-017 — Mainboard SD read/write access through Extender

## State

Created 2026-09-12 at the Author's direction. **Highest priority, before all
other Extender implementation and before Rally optimization.** Work belongs on
this project's active `main` branch, not an isolated Rally worktree. This task
is self-contained; returning agents need not visit Rally to discover its scope.
The Author released implementation on 2026-09-12 after freezing prior work.
Current checkpoint, 2026-09-13 UTC: EMOS v0.1.14, console r12 and sdserve
v0.1.0 are installed. The Author confirms the flash/visual startup; the physical
service is online. Ten unattended physical transfer/readback cycles pass through
131731 bytes, including error/retry/recovery checks. Exact candidate/raw-FAT
and fault-injection evidence is recorded in `PORT-017/PROGRESS.md` and the
linked run. No dependent Rally/Golem work has started.

The Author has confirmed the fresh native-keyboard check, and physical
interrupted-file recovery passes with all 45368 acknowledged bytes retained.
P17-02 and P17-04 are complete within the evidence's declared scope. P17-05
local documentation/whole-card delivery is being finalized. No further reset,
firmware flash or card handover is needed for this acceptance.

The project TODO owns task ordering. The phases below own this task's detailed
progress; Rally RALLY-20 consumes its acceptance result rather than maintaining
a second independent SD-service implementation checklist.

## Scope and priority boundary

Provide host-initiated reading and writing of files on the **Agon mainboard SD**
through the already connected Extender. The developer must be able to upload a
game binary and retrieve files without moving the SD card. Preserve the working
Extender USB keyboard throughout normal service operation.

Only prerequisites necessary for this capability may precede its acceptance:
identity and recovery backups, interface research, protocol design, bootstrap,
required component changes and focused qualification. Defer EDP performance,
graphics timing, Rally optimization, unrelated cleanup and feature development.
Golem development is explicitly out of scope.

This is not PORT-007: that future task concerns the P4's own microSD slot.
No direct P4 access to the mainboard SD bus, extra Wi-Fi module, parallel-link
bring-up, browser keyboard restoration or custom onboard VDP is a prerequisite.

## Architecture and existing wiring

The existing logical path is:

    Developer host -> network -> P4 -> existing UART1 link -> eZ80 -> MOS -> SD

The Author confirms the boards are currently wired for this path. That confirms
available connectivity, not yet-qualified bulk transfer performance or integrity.
Read ignored HARDWARE.local.md for actual wiring, identities and connection
commands before touching hardware. Do not copy private bench details here.

P4 owns the network endpoint and Extender transport. EMOS owns UART1, receive
dispatch, console routing and the keyboard path. An eZ80 foreground service
performs MOS/FatFS operations. No filesystem work in a keyboard callback/ISR,
direct UART takeover, competing receiver, or simultaneous filesystem ownership.
Return results through the same owned interface.

Existing EMOS hooks are **not qualified as a bulk file channel**. QTG/8C timing
replies have source/mode restrictions and do not establish arbitrary Legacy-mode
file transport. Define the wire protocol and component contracts first, then
extend supported interfaces as required. The mainboard keyboard circuit is
damaged, so disabling Extender input is not an acceptable normal operating mode.

## Implementation gate and ordered phases

1. [x] **P17-01 — Freeze the protocol before implementing it.** Inspect existing
   transport and EMOS APIs; record capability/firmware identities and budgets.
   Specify sender/receiver, framing, version negotiation, message dispatch,
   transfer/session/request IDs, explicit offsets, chunk limits, flow control,
   keyboard priority, backpressure, checksums, acknowledgements, error codes,
   timeouts, duplicate/retry handling and cancellation. Define exactly when an
   ACK means received, written, closed or independently verified. Establish
   ROM/RAM fit and foreground execution. Freeze the contract locally first.
   Initial wire freeze: 51917e6. Compile and host boundary proof is recorded in
   `PORT-017/PROGRESS.md`; this completes the contract/resource gate only.
2. [x] **P17-02 — Resolve bootstrap and recovery.** Identify how the initial
   eZ80 service gets installed and invoked; do not assume an SD loader exists.
   Preserve good game/startup/firmware copies. Prefer supported RAM/service APIs;
   put maintained EMOS changes in agon-emos with its own linked task. Establish
   any needed EMOS flash authorization before deployment. Cooperative return,
   reconnect and transfer cancellation are required. A hung eZ80 cannot service
   files; the old reset circuit is electrically unresolved and must not be
   actuated until qualified. Exhaust supported alternatives before requesting
   one bundled physical intervention. No reset or firmware-flash loops.
3. [x] **P17-03 — Implement bidirectional file operations.** Provide bounded
   host commands for capability/status, directory listing, chunked read, staged
   write, verification and activation, with cleanup/cancel behavior. Preserve
   an old runnable file until the candidate verifies. Do not call FAT rename
   power-failure atomic: document recoverable states and activation journal or
   selection scheme. Never overwrite a file being executed or held open.
4. [x] **P17-04 — Qualify on emulator and physical hardware.** Verify exact
   reads and writes of empty files, arbitrary binary bytes, chunk boundaries,
   and files larger than 64 KiB, including a roughly 132 KiB game binary.
   Read back and compare against the host bytes/digest. Exercise dropped ACKs,
   retransmission, duplicate/stale requests, corruption, disconnect, disk-full,
   write/close failures and interrupted activation. Keyboard remains usable;
   no phantom/stuck keys or silent truncation. Use raw-image FAT tests where
   necessary: REMED-003 identifies directory-backed emulator write/sync defects.
   Physical success is required; emulator-only success cannot close this gate.
5. [ ] **P17-05 — Deliver the reusable capability locally.** Demonstrate ten
   unattended write/read/verify cycles, including recoverable failures, without
   card movement or operator resets. Record throughput and recovery bounds,
   exact component versions, commands, evidence and any hard-hang limitation.
   Provide a local quick-start and preserved rollback. Promote accepted service
   interfaces/tools into maintained role-named locations. Commit relevant work
   and evidence without including unrelated dirty QUAL-003 changes. Only then
   release dependent graphics/performance work, subject to Author direction.

## Task précis: Radiotux reconnaissance

Public repositories checked 2026-09-12: Radiotux/Agon-Software and Agon-Tools.
Agon-Tools contains only LICENSE. Agon-Software main is
`e265db1de57c49142420324945c666049dc1ec53`; the existing local reference clone
already matches it. No separate public network SD-share/server was found.

- `get/README.TXT`, `get/src/get.c`, `get/agon_server.py`: GET v2.2 uses an
  ESP-AT Wi-Fi modem at 115200. A PC server sends 32 KiB chunks; the Agon buffers
  reception before MOS SD writes. Useful receive/write scheduling example.
  It is an interactive download client, not a remote filesystem service.
  Implicit server offsets advance before delivery confirmation, write/close
  results are unchecked, and there is no end-to-end digest/readback contract.
- `zget/src/zget.c` and supporting docs: Zimodem download variant. Its receiver
  skips leading bytes <=32 and has unbounded synchronization waits. Do not
  trust its 'bit-perfect' description for arbitrary binary transfer.
- `minicom/src/xmodem.c` and `ymodem.c`: bidirectional file/CRC/ACK examples.
  Static concerns include duplicate-block handling, unchecked writes, YMODEM
  ACK before storage/sequence validation and final-block length handling.
- All these tools assume direct UART ownership. They cannot be dropped into
  the EMOS-owned keyboard transport unchanged. These are static findings, not
  executed interoperability tests. GET declares GPL-3.0; check each file's
  licence before importing implementation.

Reference: https://github.com/Radiotux/Agon-Software

## Dependencies, ownership and constraints

Read OWNERSHIP.md, AGENTS.md, docs/versions/README.md,
docs/qualification/bench-constraints.md and HARDWARE.local.md. EMOS implementation
belongs to agon-emos; generic MOS build tooling belongs to mos-agondev. Upstream
AgonPlatform MOS/VDP/docs checkouts remain read-only. Use official MOS API.md
and Star-Commands.md for filesystem and launch contracts, plus EMOS src/uart.c,
src/emos_console.c and INTEG-009/012 for input and dispatch ownership.

PORT-008 and PORT-006 are existing transport/network foundations, not blanket
prerequisites requiring their unrelated work to finish. Preserve their working
behavior. QUAL-003/INTEG-012 provide diagnostic examples, not a proven data
channel. QUAL-003's unresolved first physical timing failure remains preserved.

Later P4/onboard VDP experimental flashing was authorized for the unattended
bench mission, but this task should not require changing onboard VDP. Keep the
normal product stock-VDP compatible. New firmware identities follow project
version policy. Headless emulator tests only; a GUI summons is reserved for
unavoidable human physical intervention. Existing emulator validation and
explicit commit-approval requirements still apply. No delegation or automatic
push. The initial task-registration update changes documentation only.
