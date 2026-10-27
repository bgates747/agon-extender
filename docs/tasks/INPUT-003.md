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
2. [ ] Establish enumeration result. If already-connected state is invisible,
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
5. [ ] Build the exact experimental P4 composition. Before flashing preserve a
   current full-flash backup and startup identity, verify application offset,
   use a selective application write, independently read back the result and
   verify unaffected flash regions. Preserve normal boot and mainboard images.
6. [ ] Reestablish real keyboard/CLI/service readiness and obtain fresh USB
   descriptor/report evidence. Verify the installed viewer/assets, use an
   explicitly invoked finite diagnostic if needed, and restore Legacy/CLI.
   Do not call a copied fixture ready while input or firmware is still pending.
7. [ ] Stop with the viewer ready for the Author, or with a precise observed
   hardware/operator dependency. Report what was identified, installed and
   observed; retain exact build and rollback receipts. Human control feel,
   complete button/axis exercise and physical coexistence require Author review.

## Decision register

| ID | State | Decision and consequence |
|---|---|---|
| I3-01 | Implementation direction authorized | Reuse the existing viewer and EMOS carrier; add P4-local USB acquisition first. EMOS/mainboard firmware remain unchanged unless evidence proves a separate change necessary. |
| I3-02 | Initial evidence | Existing P4r14 restart logs reach HID-client rejection of non-HID device address2, without enumeration errors. Confirm VID/PID/configuration using the new dedicated client before claiming native acquisition. |
| I3-03 | Experimental implementation | A recognized USB pad with its first valid report reserves local input while attached. It cannot steal an active LAN source; a LAN close/expiry releases that source. LAN admission conflicts while USB owns/reserves input. Unplug/error invalidates USB only. A new EMOS caller may explicitly rearm queue overflow/worker expiry; physical USB faults require reconnect. No production decision/acceptance is inferred. |
| I3-04 | Deferred | Simultaneous physical keyboard/controller and an EXT1 breakout/hub are follow-up scopes after native F310 acquisition is proven or onboard hardware blocks progress. |

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
