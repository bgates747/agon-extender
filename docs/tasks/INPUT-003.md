# INPUT-003 — Direct F310 USB input on P4-PC

The Author wants the Logitech F310 plugged into a P4-PC onboard USB socket to
drive the existing mode-20 Agon controller viewer. First establish whether the
P4 can enumerate the controller through its onboard hub; then decode its input
and feed the existing P4-to-EMOS controller service. Keep browser keyboard
access, mainboard firmware, normal startup and the existing LAN input path.

## State and authorization

On 2026-10-27 the Author reports a powered bench, Legacy display route, MOS
prompt, working remote keyboard, and F310 hotplugged into the upper-right USB
socket after mainboard/P4 admission. The Author authorizes task preparation,
commit/push, then the largest useful unattended implementation and bench tranche
before requiring attention. The initial task/plan must be published before
implementation or bench diagnostics. Machine-local identities, reservations and
receipts belong in `HARDWARE.local.md` and ignored task evidence.

State: Author control review found a latched USB report fault while exercising
D-pad up-left. Viewer Escape and MOS keyboard remain responsive; restarting the
viewer does not recover USB input. Correct the report decoder and retain bounded
rejected-report diagnostics before the next review. Resting-state/cleanup checks
remain historical passes, not a complete control pass.

This is experimental work, not production acceptance. No physical rewiring,
replacement keyboard/controller, user button exercise, or firmware production
promotion is assumed. Stop for the Author when those actions become necessary,
or when the verified viewer is ready for interactive control review.

## Scope and ownership

1. The P4 USB host enumerates the F310 through the P4-PC onboard hub. Capture
   device speed, VID/PID, interfaces/endpoints and enumeration errors before
   attributing a failure to controller decoding.
2. A bounded P4-owned USB client decodes the identified F310 protocol and
   publishes both sticks, two independent analog triggers, D-pad and buttons.
   XInput is the preferred F310 setting; DirectInput may omit analog triggers.
   Do not silently change the Author's rear switch or compensate in software
   for the front Mode button swapping left stick and D-pad.
3. The P4 controller service retains coherent latest state and ordered button
   transitions. USB callbacks must not write UART or draw. EMOS continues to
   own ordinary VDU routing, admission and the existing physical UART1 gateway;
   the eZ80 viewer uses its existing resident service with no new global MOS API.
4. One source owns the controller stream. Preserve LAN compatibility and reject
   conflicting admission explicitly; never blend USB and LAN states or silently
   take over an active source. Record the chosen local admission/loss policy
   before implementing it. Unplug/error/expiry must invalidate held input.
5. Reuse the installed viewer, including app-owned conditional mode-20 switch,
   at least one second of settling, Escape and entry-mode restoration. Preserve
   mainboard VDP, EMOS, SD user files and `/autoexec.txt`. No checksum is added
   to E/VDP–EMOS traffic.
6. Retain keyboard acquisition separately from controller acquisition. USB hub
   support and simultaneous class drivers do not themselves qualify simultaneous
   physical keyboard/controller input; that remains a later bounded check.

## Bounded research précis

1. Official Agon references: `../../agon-docs/docs/mos/API.md` (`RST 18h`, counted
   output), `docs/mos/Keyboard.md` (sysvars/nonblocking input), and
   `docs/vdp/Screen-Modes.md` (VDU22, mode20 and double-buffer cleanup). No Agon
   ABI or viewer change is planned. Consult official source only if those
   contracts become insufficient; keep reference checkouts read-only.
2. Existing controller authorities: [controller operation](../controller-input.md),
   [EMOS carrier](../protocols/controller-emos.md),
   [LAN protocol](../protocols/controller-lan.md), and
   `vdp/video/extender/input/controller/{receiver,runtime,appliance}.hpp`.
   The existing viewer is under `tests/fixtures/controller/`; the P4 runtime
   currently feeds it from a Linux sender. No controller USB driver exists.
3. `vdp/video/extender/input/p4_usb_host.hpp` accepts one boot keyboard only.
   Non-keyboard interfaces are deliberately ignored. Consequently an absence
   of viewer input alone does not diagnose enumeration failure.
4. [Olimex Rev C authority](../hardware/esp32-p4-pc/README.md) pins manufacturer
   commit `04032d68e5c727870f9d40beb9e37b7ab3a66916`. Onboard USB-A sockets
   share the HS controller through an FE1.1s hub; the separate FS PHY is exposed
   on EXT1. This tranche tries onboard sockets first and does not rewire EXT1.
5. [Espressif host documentation](https://docs.espressif.com/projects/esp-usb/en/latest/esp32p4/usb_host.html)
   describes concurrent clients and the missing transaction-translator support
   for FS/LS devices behind an HS hub. The existing source-bound FS/LS-only
   backport is already selected in the installed experimental P4 composition.
   Inspect its pinned IDF 5.5.5 implementation rather than upgrading the SDK.
   Historical keyboard capture reached LS detection but failed the initial
   short device-descriptor transfer even after selecting FS/LS-only operation.
6. Confirm F310 report layout from primary implementation/reference material
   and actual device descriptors/reports. Linux XInput F310 identity is
   `046d:c21d`; DirectInput identity is `046d:c216`. Do not infer either current
   rear-switch position or USB device speed from the Linux evdev axis width.
7. The installed P4 includes reviewed HDMI/controller changes absent from a
   generic console build. Start from the exact installed source composition,
   preserve its options, freeze changed sources and retain exact rollback bytes.
   New executable bytes receive a distinct build timestamp. Record provenance
   and source integration rather than substituting arbitrary repository HEAD.

## Work plan and gates

1. [x] Publish this task and TODO entry. Reserve the available bench, inspect
   fresh status and passively collect P4 USB diagnostics without resetting.
2. [x] Establish enumeration result. If already-connected state is invisible,
   prepare a descriptor/connection diagnostic and use only the bounded reset
   or hub reinitialization justified by the observed host state. Read reset,
   installation and serial procedures before their respective operations.
3. [x] Record the expected F310 transport/interface/report contract and a bounded
   local source policy. Implement portable decoding and lifecycle/source-conflict
   checks, plus P4 USB ownership and status diagnostics. Keep driver operations
   off the UART owner and avoid per-report log floods.
4. [x] Exercise malformed reports, stick/trigger endpoints, D-pad/buttons,
   transition order, stale/unplug/error neutralization and source exclusion in
   meaningful offline checks. Run existing controller pipeline checks.
5. [x] Build the exact experimental P4 composition. Before flashing preserve a
   current full-flash backup and startup identity, verify application offset,
   use a selective application write, independently read back the result and
   verify unaffected flash regions. Preserve normal boot and mainboard images.
6. [x] Reestablish real keyboard/CLI/service readiness and obtain fresh USB
   descriptor/report evidence. Verify the installed viewer/assets, use an
   explicitly invoked finite diagnostic if needed, and restore Legacy/CLI.
   Do not call a copied fixture ready while input or firmware is still pending.
7. [x] Stop with the viewer ready for the Author, or with a precise observed
   hardware/operator dependency. Report what was identified, installed and
   observed; retain exact build and rollback receipts. Human control feel,
   complete button/axis exercise and physical coexistence require Author review.

## Decision register

| ID | State | Decision and consequence |
|---|---|---|
| I3-01 | Implementation direction authorized | Reuse the existing viewer and EMOS carrier; add P4-local USB acquisition first. EMOS/mainboard firmware remain unchanged unless evidence proves a separate change necessary. |
| I3-02 | Observed | F310046d:c21d enumerates at full speed through the onboard hub: address2/interface0, IN81,32-byte maximum packet, interval4ms. The decoder accepts a real20-byte XInput resting-state report and the Agon viewer displays it. |
| I3-03 | Experimental implementation | A recognized USB pad with its first valid report reserves local input while attached. It cannot steal an active LAN source; a LAN close/expiry releases that source. LAN admission conflicts while USB owns/reserves input. Unplug/error invalidates USB only. A new EMOS caller may explicitly rearm queue overflow/worker expiry; physical USB faults require reconnect. No production decision/acceptance is inferred. |
| I3-04 | Deferred | Simultaneous physical keyboard/controller and an EXT1 breakout/hub are follow-up scopes after native F310 acquisition is proven or onboard hardware blocks progress. |
| I3-05 | Open | Decouple cold-boot native USB startup from Ethernet/HTTP initialization before claiming standalone/offline operation. Current hardware proof includes the network startup; no physical network-loss check was performed. |

## Validation and closeout

Keep preparation, native compilation, USB enumeration, report decoding,
P4/EMOS transport and visible viewer behavior as separate evidence scopes.
Record start/end/duration and exact inputs for bounded hardware operations;
do not infer end-to-end latency from packet or polling counters. Update current
input/build guidance when behavior becomes usable, while preserving historical
evidence. Production promotion/version approval follows explicit tested Author
acceptance and the canonical qualification requirements.

## Initial implementation evidence — 2026-10-27

1. Passive capture and existing-build restart identify P4r14 exactly and log
   `hid-host: No HID device at USB port 2`. The device identity is not yet
   available through the boot-keyboard-only acquisition path. Normal startup
   was read back unchanged before resetting; a fresh Agon input epoch followed.
2. The portable F310 decoder follows the XInput wire facts in Linux
   [v6.12 xpad.c](https://github.com/torvalds/linux/blob/v6.12/drivers/input/joystick/xpad.c),
   `xpad360_process_packet`: little-endian signed sticks, complemented Y axes,
   trigger bytes4/5 and independent buttons. New code implements those protocol
   facts without importing the Linux driver. All65,536 signed values are checked
   for X/Y orientation/endpoints, alongside descriptors, buttons and source loss.
3. The first offline controller pass is42/42, including the actual P4/EMOS/viewer
   software pipeline. These tests do not establish USB hardware operation.
4. Source commit `eb8b9ab4` corrects explicit rearm to evaluate expiry at the
   current monotonic time, including when the new caller is the first observer
   after a USB worker stall. The updated42-case controller run passes. The exact
   installed-source composition is committed separately as `1ee4d7a3` on
   `codex/input003-usb-f310`, retaining the installed display options.
5. An application-only install must compare the incoming bootloader with the
   prior verified device readback, not the newly linked factory bootloader:
   earlier application-only updates retained older boot bytes. The initial
   pre-write guard stopped without a flash write; the actual immutable prefix
   matches the retained installed readback. The original P4/Agon CLI was restored
   and startup was verified unchanged. Reuse of that full backup requires a
   fresh whole-device verification before any write.
6. Native USB reception and actual Agon viewer delivery now pass. The old
   viewer incorrectly reported mode cleanup failure even though a later fresh
   CLI query confirmed mode0/640×480/16colours. Official read-only VDPv2.16.0
   source (`c7ac293d2aa81ddfa693390549bcd909069c8fc3`, clean tag) explains the
   race: `video/vdu_fonts.h` sends unsolicited mode information on font changes.
   The viewer's post-selection query must disregard earlier mode20 replies and
   wait within its existing deadline for the selected entry mode. This is a
   viewer-only correction; the shared scroll fixture and firmware stay unchanged.

## Installed result — 2026-10-27

The F310 drives the existing viewer through the P4/EMOS service without an Oryx
controller sender. A finite instrumented check observes the actual viewer
identity, `Agon received controller input`, resting sticks128/−129 on both
sides, triggers0/0 and no held buttons. Escape prints `Controller viewer closed.`
and a separate fresh CLI query confirms mode0/640×480/16colours. This proves
resting-state delivery and cleanup, not physical exercise of every control.

| Component / check | Exact result |
|---|---|
| P4 build | `indexed-hdmi-r14-b2026-10-27-22-05-29Z`, clean source`1ee4d7a3d6314b662c78e685d300dab326164418` |
| P4 application |1777312bytes, SHA-256`d6c6f5e7d2126d611f23e7df5586b7d6d038977677f4e7204885e2760a22a0d0` |
| Firmware write | Application only at0x20000; independent full16MiB readback matches application and preserves all bytes outside written sectors[0x20000,0x1d2000) |
| Incoming/current full flash | Before`ca6e75f748fb2a84039f135d76d93ffcbf484da8d209bc58d1f328a68cd9cc17`; after`a895790d55c7c70846a8d99f0ca18e4902722cfc6a5328ffdf39b0897cd40f68` |
| Build composition | Board/display configuration, dependency lock, normalized SDK and compiler-source/definition selections match the prior installed P4; the unnecessary320-scaler build option was excluded before any write |
| Viewer build | `controller-viewer-r03-b2026-10-27-22-23-38Z`, clean source`c9191a6bb8a6a2ea0cce982a2440d633b0cbe7a8` |
| Viewer bytes |28860bytes, SHA-256`4e7e0da37fe37d2fe04ea2342737173507090873244227b2286c88322aca2d51`; independent SD readback matches |
| Source exclusion | A real LAN OPEN receives409 while USB owns input; same USB session remains valid |
| Controller software checks |42pass, including the existing P4/EMOS/viewer pipeline and USB decoder/source lifecycle |
| Live viewer check |19.686host-monotonic seconds including invocation, rendering, Escape and cleanup; printer mirror enabled during observation, no latency/FPS claim |
| Preserved components | EMOSv27 and mainboard VDP not flashed; normal99-byte startup read back unchanged; no processor-link checksum added |

The old viewer and its preceding retained backup are independently archived
under `/agents/extender/fixtures/input003`, with `relocations.json` on the card.
Protected transaction backups were archived as verified files and removed only
through the canonical target recovery-cleanup operation. Current support remains
`/extender/controller/ctrlview.bin`.

The terminal state is a verified Legacy CLI, mode0, corrected viewer freshly
loaded at0x040000 but stopped, admitted neutral remote keyboard, valid USB
source, SD listener offline/idle and printer mirror off. Host serial/client
workers have ended. The explicit review invocation is `RUN &040000`.

## Remaining Author review / qualification

1. [ ] Exercise both sticks through their ranges, both independent analog
   triggers, four D-pad directions and all eleven buttons. Judge the viewer
   visually; use R to clear counts and Escape to return to the entry mode.
2. [ ] Qualify physical unplug/reconnect and USB fault recovery, retained
   transitions under load, source conflicts in both directions and keyboard
   coexistence. Current unplug/error coverage is portable software testing.
3. [ ] Resolve I3-05 before standalone/offline cold-boot claims; preserve the
   current bounded network-startup requirement in operating instructions.
4. [ ] Perform the applicable canonical firmware qualification and obtain tested
   Author acceptance/version authority before production promotion. Selected
   production and release tags remain unchanged.

## D-pad review failure — 2026-10-27

1. The Author reports that sticks/buttons worked until D-pad up-left caused
   `Waiting for controller`. Escape works, MOS accepts browser keyboard, and
   restarting the viewer still waits. Fresh P4 status has USB report fault3,
  1472 accepted reports, receiver Source5/inactive and no queued transitions.
   This identifies a USB decoder rejection followed by a permanent acquisition
   stop; it is not a viewer hang, UART loss or queue overflow.
2. Installed code does not retain the rejected bytes. A valid up-left report
   passes the decoder. Whether the actual report had opposite contacts or bad
   length/header therefore remains unresolved; do not claim either as observed.
3. The Linux v6.12 `xpad360_process_packet` reference resolves opposite D-pad
   contacts to neutral on that axis. The local decoder instead rejects them as
   malformed. Match the reference axis semantics before packing the existing
   controller mask; do not weaken LAN or EMOS framing/held-mask contracts.
4. [ ] Cover all sixteen D-pad wire combinations and meaningful transitions,
   including up-left and simultaneous opposite contacts with other buttons.
5. [ ] Retain bounded anomaly bytes/counts on P4 for HTTP inspection; avoid
   per-report logging and processor-link protocol changes. Preserve existing
   transfer-error recovery policy until a framing fault is actually observed.
6. [ ] Build and selectively install an identified correction from the exact
   installed P4 composition, with verified backup/readback and unchanged EMOS,
   mainboard VDP, viewer and startup. Restore responsive CLI, load viewer, stop
   for Author control review. Retain the unresolved raw-report qualification.
