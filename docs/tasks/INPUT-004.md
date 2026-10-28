# INPUT-004 — P4-PC onboard USB keyboard support

Make a physical USB keyboard work through a P4-PC onboard USB-A socket while
preserving the working directly attached F310, browser recovery input and EMOS
routing. The earlier speed workaround is installed, but a low-speed keyboard
failed its first descriptor transfer. Establish the remaining cause from pinned
source and physical evidence, implement the smallest justified correction, and
qualify actual typing/LEDs/reconnect plus keyboard/controller coexistence.

## State and authorization

1. On2026-10-28 the Author requests this research/implementation task, a commit
   and push of all current dirt before proceeding, then work toward an onboard
   keyboard. Publish this plan before implementation or live diagnostics.
2. This is an implementation goal, not authorization for physical rewiring or
   speculative wholesale SDK/USB-stack replacement. Continue useful offline
   work while keyboard identity/attachment and current bench state are unknown.
3. Use `HARDWARE.local.md` for current installed bytes, wiring, access, prior
   captures and bench reservations. Coordinate with the current owner before
   taking ports/input. Preserve any running Author flight; do not infer CLI
   readiness from P4 input status or a historical handback.
4. Preserve normal startup, EMOS and mainboard VDP. Never modify autoexec for
   this task. Use matched P4 source/configuration and a fresh identified build,
   verified backup/readback and rollback for any justified P4 application update.
5. The earlier unexplained P4 restart remains a distinct unresolved incident
   in INPUT-003; do not diagnose it from chronology or close it after a keyboard
   pass. Preserve reset reasons/backtraces if another event occurs.

## Scope and ownership

1. P4 USB host owns the onboard hub, enumeration, keyboard HID acquisition and
   keyboard/controller scheduling. Keyboard reports feed the existing P4 input
   owner; EMOS continues to own admission, UART1 routing and MOS-visible input.
2. Keep one active physical keyboard. Test modifiers, navigation, key releases,
   lock LEDs, held-key unplug and reconnect without stuck or invented keys.
   Preserve browser/agent input policy and access for recovery.
3. Retain F310 native USB acquisition and the unchanged CI2/CIS2 controller
   carrier. No CRC/substitute checksum is added to E/VDP–EMOS traffic. Do not
   change mainboard firmware, guest application bindings or controller mapping
   to compensate for a USB-host enumeration problem.
4. Prefer onboard sockets. The GPIO-header FS-controller route is a contingency
   only if onboard evidence demonstrates a remaining blocker and the Author
   selects that hardware change. Do not silently switch the USB peripheral map.
5. Keep upstream Agon/SDK/reference repositories read-only. Own any backport in
   project build/source inputs, with exact source hashes, bounded patches,
   provenance, rationale and removal conditions beside unusual code.

## Bounded research précis / known evidence

1. Prior investigation: [BOARD-001](BOARD-001.md), B001-08 and physical USB
   diagnosis sections. Original HS-hub/LS-keyboard capture explicitly rejected
   the device for missing transaction translation. After FS/LS-only selection,
   the pinned HCD detects FS-host/LS-device then returns generic transfer error
   at CHECK_SHORT_DEV_DESC. HID keyboard admission was never reached. Generic
   transfer error does not identify bad descriptors, power, DMA or timing.
2. Official Espressif guidance: [USB host / FS-LS only](https://docs.espressif.com/projects/esp-usb/en/latest/esp32p4/usb_host.html#full-low-speed-only-host).
   The onboard HS-capable controller can run full/low speed without changing
   wiring. Pinned ESP-IDF5.5.5/b774170ff46c393eeb5e495ea37936038d3f4f4f lacks the
   public fsls_only field; maintained `vdp/native/usb_fsls_only.cmake` generates
   a hash-checked HCD derivative enabling it before root resets. This option is
   already in the installed matched native-controller composition.
3. Working F310 is full-speed; the failing keyboard was low-speed. The F310
   validates the onboard full-speed path, not LS preamble/control-stage behavior.
   Review HCD low-speed-via-FS-hub handling, HAL channel configuration, DMA/cache
   ownership/alignment, stage scheduling and the existing IDF-12986 delay before
   changing code. Retain alternatives as hypotheses until discriminated.
4. Secondary implementation lead, not a diagnosis: [EspUsbHost P4 notes](https://github.com/tanakamasayuki/EspUsbHost#esp32-p4-notes)
   describes cleaning cached IN buffers before USB DMA and reports keyboard
   operation on P4 with limits. Pin an exact revision, inspect actual code,
   compare against our SDK/component versions and verify applicability. Do not
   import its stack/API wholesale or treat a README as proof of our defect.
5. Maintained native acquisition: `vdp/video/extender/input/p4_usb_host.hpp`;
   controller USB client under `vdp/video/extender/input/controller/`. Build
   authority is `scripts/build_p4.py`, `docs/building.md` and the exact installed
   P4 source composition recorded locally. Source HEAD/selected production is
   not a substitute for currently installed experimental bytes.
6. Agon contracts: consult `../../agon-docs/docs/mos/Keyboard.md` and relevant
   keyboard/VDP reply documentation before changing MOS-visible behavior.
   `docs/remote-keyboard.md` owns current P4 source/admission behavior. Consult
   read-only official source only when material; record selected reference
   revisions if a new upstream research baseline is established.

## Work plan and gates

1. [ ] Publish task/TODO and all reviewed existing dirt as requested. Preserve
   private ignored files and immutable evidence; do not stage generated private
   firmware, secrets or another project's emulator implementation.
2. [ ] Pin current code/build/reference inputs and collect a source-level USB
   failure-path précis. Compare upstream fixes and the cache-coherency lead;
   identify expected signatures and smallest discriminating checks. Independent
   offline research may run in parallel, with only one bench owner.
3. [ ] Establish current bench owner, actual foreground/CLI, keyboard identity,
   connection and socket. Collect bounded existing-build enumeration evidence
   before changing firmware. Compare one alternative keyboard if available;
   keep each physical state stable and ask the Author for needed physical work.
4. [ ] Implement an evidence-supported remedy or diagnostic extension in a
   project-owned matched composition. Add meaningful offline checks for the
   affected low-level contract; run relevant existing input/controller checks.
   Do not claim target/device success from host tests.
5. [ ] Build a clean identified candidate preserving installed hardware/display/
   dependency settings. Before deployment freshly preserve/verify rollback and
   startup state, selectively write P4 app only, independently read it back and
   verify flash outside written sectors unchanged. Read installation/reset/
   test-execution/serial procedures before their operations.
6. [ ] Verify enumeration and actual EMOS CLI typing, modifiers, navigation,
   releases, LEDs, unplug/reconnect and held-key loss. Qualify simultaneous F310
   state/edges with keyboard use and browser recovery. Bounded explicit tests
   record component identities, start/end/durations, failures and terminal state;
   preserve startup, entry-mode restoration and >=1s monitor settling.
7. [ ] Leave input and a visible responsive CLI ready for Author typing review,
   with all unnecessary clients/captures closed. If a physical dependency is
   missing, finish independent preparation and ask only for that missing action.
8. [ ] After Author acceptance, update durable keyboard/build/operating guides
   and complete applicable canonical qualification/production promotion with
   the agreed version. Preserve the accepted bytes, rollback and limitations;
   do not infer a new production version or qualify other keyboards by analogy.

## Decision register

| ID | State | Decision / consequence |
|---|---|---|
| I4-01 | Author direction | Pursue onboard USB keyboard first; GPIO wiring remains a separately selected contingency. |
| I4-02 | Existing implementation | Retain installed FS/LS-only host and existing HID keyboard/controller clients unless source/evidence requires a bounded change. |
| I4-03 | Open | Remaining failure mechanism: distinguish LS-via-FS-hub signaling/stage timing, DMA/cache ownership, device quirks and other host errors. |
| I4-04 | Open | Exact keyboard/port/attachment and current bench foreground must be established before device tests. |

## Evidence and stop boundaries

Keep source findings, offline checks, target compilation, installed-byte proof,
USB enumeration and actual typing separate. No mainboard/EMOS change, emulator
change, physical rewiring, broad suite or production selection follows merely
from this task. If the current source cannot reveal the failure, prepare a bounded
instrumented candidate rather than repeatedly power-cycling or guessing delays.
Stop at an explicit Author boundary; never replay uncertain input/transfers.
