# P4 browser-video qualification procedure

Status: Candidate — execution requires separate PORT-003 item 15 authorization

Identity: `p4-browser-video-qualification-r01`

Firmware identity: `extender-vdp-v0.1.0`, status `candidate`, variant
`olimex-p4-devkit`

Registry revision: `r12`

## Purpose and claim boundary

Qualify the first bootable retained-VDP P4 target as a P4-owned Ethernet and
browser-video service. This procedure proves target boot, exact identity,
ordinary DHCP, direct embedded assets, local browser self-test, immutable EVF1
startup-frame delivery, browser disconnect/reconnect, bounded snapshot/network
behavior, heap stability, and USB diagnostics.

The Agon remains physically disconnected. This procedure sends no VDU command
to the P4 and does not qualify parallel ingress, return UART, EMOS routing,
sysvars, operating modes, audio, input, storage, updater, internet exposure, or
assembled-system electrical behavior.

## Approval and controlled inputs

The Author approved these candidate controls on 2026-08-27:

1. firmware identity `extender-vdp-v0.1.0`;
2. procedure artifact `p4-browser-video-qualification` and revision `r01`;
3. artifact-registry revision `r12`.

Before this procedure may run, the Author must separately approve:

1. the exact committed candidate and generated build identity; and
2. PORT-003 checklist item 15, which authorizes P4 flash mutation and this
   P4-only run.

The approved procedure must control:

1. `extender-vdp-v0.1.0`, status `candidate`, variant `olimex-p4-devkit`;
2. `olimex-p4-devkit-profile-r03`;
3. `p4-ota-partition-layout-r01`;
4. the P4-only physical boundary recorded below;
5. pioarduino `55.03.311`, Arduino-ESP32 `3.3.11`, ESP-IDF `5.5.5`, and the
   project-local PlatformIO package closure;
6. this exact approved procedure revision; and
7. the full clean candidate commit recorded by the run manifest.

Read ignored `HARDWARE.local.md` immediately before any bench action. Resolve
the machine-local Pi, stable P4 USB identity, staging paths, and observed DHCP
lease from that authority without copying them into this document.

## Candidate freeze and identified build

1. Require committed `vdp/pio/p4-browser-vdp-identity.json` to select
   `extender-vdp-v0.1.0` with status `candidate`; require artifact-registry
   revision `r12` and this exact candidate procedure revision.
2. Regenerate Phase F provenance, dependency, implementation-manifest, host,
   browser, build-selection, and closure artifacts. Commit all candidate
   inputs and generated evidence, push them, and confirm a clean worktree.
3. Assign UTC build ID
   `extender-vdp-v0.1.0-bYYYY-MM-DD-HH-MM-SSZ`. Do not reuse the timestamp of
   the current unversioned predeployment image.
4. Clean and build `p4-browser-vdp` with that exact
   `AGON_EXTENDER_BUILD_ID`. Do not run PlatformIO `compiledb` afterward.
5. Run `validate-phase-f-build.py` with all three exact expected identity
   arguments. Require 23 selected application units, five embedded assets,
   C++17 at the actual application-component boundary, every required symbol
   and diagnostic string, no rejected identity marker, and every declared
   exclusion.
6. Record hashes and sizes for the factory and application images, bootloader,
   partition table, OTA data, SDK configuration, ELF, map, and generated
   closure records in a build manifest. Name staged binaries with the full
   build ID; an unqualified `firmware.bin` filename is not deployment
   authority.
7. Confirm the final source commit remains clean and unchanged after the
   identified build. Any source, configuration, procedure, profile, or fixture
   change invalidates the build and requires a new commit and build ID.

## Required P4-only bench state

1. The Olimex ESP32-P4-DevKit Rev D1 is USB-connected to the dedicated bench
   Pi and connected to trusted private-LAN Ethernet.
2. The Agon is physically disconnected from every Extender harness endpoint.
3. The existing Light 2 breadboard may remain attached because this target
   does not select or configure its transport GPIOs. Stop if read-only review
   finds an Ethernet-pin conflict, external signal source, rail conflict, or
   any departure from the documented disconnected-Agon boundary.
4. The logic analyzer may remain attached only as passive controlled loading;
   no analyzer timing claim is made. Verify the loose-prone probe identified in
   `HARDWARE.local.md` before mutation.
5. The unresolved Pi-controlled Agon-reset breakout must not be connected,
   energized through a signal lead, or actuated. This procedure resets only
   the P4 through its verified USB programming interface.

## Read-only preflight and deployment

Complete all read-only checks before erase or write:

1. Verify the disposable Pi host, stable board USB identity, unique resolved
   serial endpoint, ESP32-P4 revision, flash tool, and current board presence.
2. Confirm and record the disconnected-Agon state, passive analyzer state, and
   no active source on the harness.
3. Stage only the identified factory image and build manifest in a new
   run-specific Pi directory. Compare local and remote SHA-256 values.
4. Derive and record the current build's flash arguments. Require bootloader
   `0x2000`, partition table `0x8000`, OTA data `0xf000`, and application
   `0x20000`; reject inherited legacy offsets or flash overrides.
5. Assign run ID `PORT-003-YYYY-MM-DD-HH-MM-SSZ` at the instant execution
   begins and create `tests/runs/<RUN-ID>/` from the run-manifest template.
6. Erase P4 flash, write the exact factory image at `0x0`, and run an
   independent flash verification. No backup of the previous image is
   required.
7. Capture initial USB Serial/JTAG output with reconnect-aware handling for
   USB re-enumeration. Preserve raw ROM and application segments rather than
   joining them deceptively across an unavoidable descriptor gap.

## Required runtime checks

1. **Identity and platform.** Require exact source identity, build ID, and
   `candidate` status in startup diagnostics. Require ESP32-P4 revision 1.3,
   QIO at 80 MHz, 16 MiB flash, 360 MHz CPU, and no assertion, panic, Guru
   Meditation, watchdog reset, or reset loop.
2. **Retained boot.** Require retained VDP setup, mode initialization, process
   task creation, snapshot-pool enablement, and continuing ten-second
   diagnostic records. General Poll may remain waiting on the deliberately
   disconnected `Stream`; that is the required Phase F state.
3. **DHCP and server.** Require Ethernet start, link connection, a DHCP lease,
   and `HTTP browser service ready` over USB diagnostics. Record the observed
   lease in bench-sensitive evidence; do not require a compiled address.
4. **Direct assets.** From the development host, run
   `check-p4-browser-runtime.py` against the observed lease. Require all five
   HTTP assets to match their committed bytes exactly, one valid complete EVF1
   frame, no unsolicited second frame without credit, a clean disconnect, and
   a valid frame from a fresh connection.
5. **Browser self-test.** Open the P4-served `/?demo` page in a real WebGL2
   browser. Require the local RGB888 test pattern, a 320-by-240 surface, and
   increasing received/presented statistics with no frame error. Preserve a
   screenshot and browser/version record.
6. **Startup framebuffer.** Stop demo mode, select `Connect`, and require the
   P4-composed retained startup framebuffer to appear. Record sequence,
   dimensions, stride, logical period, and a screenshot. The browser must not
   synthesize this image.
7. **Disconnect/reconnect.** Close or reload the live page, wait through at
   least two ten-second diagnostic intervals, then reconnect. Require a fresh
   complete frame, a corresponding accepted/disconnected client record, and
   no retained lease after disconnect.
8. **Bounded counters.** Preserve at least six consecutive ten-second records
   spanning no-client, connected, disconnected, and reconnected states.
   Snapshot, provider, credit, send, failure, and drop counters must be
   monotonic and 32-bit bounded. Any nonzero `no_slot`, transition, send, or
   protocol count must have a matching controlled event or failure record;
   after disconnect, no held-client pressure may continue increasing.
9. **Memory stability.** Use the first completed connect/disconnect cycle as
   warm-up. Across at least five additional cycles, require snapshot
   allocation failures and composition failures to remain zero, PSRAM-backed
   snapshot storage to remain enabled, no monotonic free-heap decline, and
   final free 8-bit and PSRAM heap each no more than 65,536 bytes below its
   post-warm-up value. Preserve all raw heap records.
10. **Continued service.** After all cycles, require new snapshot publications,
    a new browser frame, responsive static assets, and continued periodic USB
    diagnostics. A network/client failure must not stop retained display
    execution.

## Outcome and evidence

Pass only if every required check succeeds without a deviation that weakens
the claim. Preserve failed, partial, aborted, and invalid runs. A failed
threshold may motivate a reviewed r02 procedure or a source correction; it may
not be silently relaxed during the run.

The run record must include exact identities, clean commit, tools, generic
bench aliases, disconnected-Agon confirmation, flash verification, build and
evidence hashes, raw serial capture, live-check JSON, browser screenshot,
browser version, parsed diagnostic timeline, and every deviation. Keep unique
device paths, private network topology, and other machine-local data in the
ignored bench record or explicitly bench-sensitive remote evidence.
