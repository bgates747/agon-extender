# PORT-015 — Bring up a directly connected USB keyboard

## State and scope

- Status: W2 bounded native USB acquisition passes on PERIBOARD-409: key
  transitions, held-key cleanup and reconnection observed. The unplug diagnostic
  is explained by the pinned upstream cleanup path (review linked below).
  W1 power/current particulars remain open. W3 ordinary-CLI integration is
  drafted; host/headless checks and Author-supplied graphical screenshot
  review pass. Source freeze and physical deployment/proof remain pending.
  Artifact status remains candidate; this is not full keyboard qualification.
- Started: 2026-09-09.
- Finished: --

The Author brought forward direct P4 USB keyboard input because the Agon
mainboard keyboard interface remains inoperative. First useful milestone:
USB keyboard → P4 processed keyboard → existing r03 UART1 → resident EMOS
keyboard handling → ordinary CLI on mainboard VGA. Browser input repairs
remain tracked in REMOTE-001 and follow this increment. Browser video is not
the display dependency for this proof.

Use one ordinary wired USB HID boot-protocol keyboard initially. P4 owns USB
enumeration, reports, key transitions, repeat and device removal; EMOS owns
source selection, UART1 and canonical key/sysvar/API effects. Reuse PORT-005's
processed input/stock serializer and PORT-008's 1152000/8N1 RTS/CTS transport.
Implement the existing `EMOS KEYINPUT extender` name. Preserve layout/source
separation and autoexec-only startup persistence. Do not add an application
UART bypass, proprietary keymap packet or implicit browser/USB input mixing.

## Decision register

| ID | Decision | State |
|---|---|---|
| PORT-015-D001 | Bring forward native P4 USB keyboard acquisition; first prove ordinary EMOS CLI on mainboard VGA using the existing UART contract. | Accepted by Author, 2026-09-09; SETUP-005 K009 and ADR-0014. |
| PORT-015-D002 | Use one wired boot-protocol keyboard and the existing `extender` input selector for the first increment. | Accepted direction; W3 draft implemented, physical CLI proof pending. |
| PORT-015-D003 | Author's USB-A male cable terminates in a reversed four-pin male header; a female-to-female USB-A adapter accepts the keyboard plug. | Author corrected the initial socket description and reported passing continuity/short/voltage checks; corrected data pair subsequently enumerates the keyboard. W1 particulars remain open. |

## Bounded reference

1. Olimex ESP32-P4-DevKit Rev D1 schematic and PCB at vendor commit
   `4b453612bd72e2b83b49cb1156de93f655b8aec4`, in
   `HARDWARE/ESP32-P4-DevKit-Rev.D1/` of
   <https://github.com/OLIMEX/ESP32-P4-DevKit>. The unmodified local vendor
   copies and board identity are indexed through HARDWARE.local.md.
2. ESP-IDF 5.5.5 USB host documentation and the matching
   `examples/peripherals/usb/host/hid` example. Use managed
   `espressif/usb_host_hid` **1.2.1**, vendor source
   `e3c35b840b9fc9969b981011c9ff782c01168433`. Its 1.1.0/1.2.1 releases fix
   concurrent-close and disconnect-cleanup defects present in older examples'
   driver range. This IDF version supplies the USB library itself.
   <https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-reference/peripherals/usb_host.html>
   <https://components.espressif.com/components/espressif/usb_host_hid/versions/1.2.1>
3. Before changing MOS/VDP behavior, refresh the relevant official
   Keyboard/API/System-Commands documentation and AUDIT-004's bounded packet
   and MOS traces. Official MOS v3.0.2 and VDP v2.16.0 remain read-only.
   Current complete processed events and serializer live under PORT-005;
   browser socket ownership/heartbeat policy is not a USB device lifetime.

## W2 implementation and checks

The standalone `p4-usb-keyboard` target selects one native acquisition
translation unit and uses `usb-keyboard-probe-r01` (candidate, registry r45,
standing Author preapproval). `scripts/prepare_usb_keyboard.py` produces an
identified local bundle without flashing or writing SD media. Its target lock
is `vdp/pio/p4-usb-keyboard-dependencies.lock`; ordinary EDP's
`vdp/dependencies.lock` remains unchanged. The resolver initially selected
unrelated updates for three Arduino dependencies, so the target explicitly
retains their existing versions. The builder rejects any changed existing
dependency version/hash. No vendored implementation is patched.

P4's HID task claims one boot-keyboard interface and copies eight-byte input
reports into a bounded queue. The application owner configures boot protocol,
decodes transitions and prints them on USB Serial/JTAG. Reports reserve queue
space for connection/removal notices. Lost/invalid reports clear held state;
older queued reports cannot rearm input, which requires a fresh neutral report.
P4 reports unmapped physical usage IDs rather than inventing stock key values.
The shared US subset preserves the existing browser mapping and held-key
release identity. No browser lease behavior changes here.

W2 does not initialize the Agon UART, send keyboard packets, switch display or
input source, or modify EMOS. Typematic, LEDs, selected layouts and the complete
stock key set remain W3 work. Diagnostic USB acquisition cannot establish that
`EMOS KEYINPUT extender` works. P4 now runs the acquisition candidate; installed
EMOS remains unchanged.

Verification commands:

```text
.venv/bin/python tests/usb_boot_keyboard_test.py
.venv/bin/python tests/browser_keyboard_test.py
.venv/bin/python tests/usb_source_selection_test.py
.venv/bin/python scripts/prepare_usb_keyboard.py --output <new-local-bundle-directory>
```

Decoder tests exercise exact report transitions, modifier-only reports,
retained releases after modifier changes, duplicate/reordered slots, rollover,
lost-report neutral recovery, unmapped keys and removal. Existing browser
mapping/ownership tests pass unchanged. Selection-hook checks cover target
manifest/lock switching and protection of hand-maintained files. A successful
compile is separate from a source-stable identified bundle and physical proof.
The identified draft `usb-keyboard-probe-r01-b2026-09-09-19-55-40Z` passed
source-stability, exact embedded identities, output hashes and dependency
closure checks. The deployable candidate is built from the source checkpoint
and gets its own timestamp. The artifact registry validates. The full version
validator still fails the pre-existing, unchanged r02 profile/connectivity
hash mismatch; repairing that held historical design is outside this increment.
The [USB acquisition test sheet](../../hardware/designs/light2-harness-r03/tests/usb-keyboard-probe-r01.md)
owns the wiring confirmation and operator observations.

## Proposed connector mapping

This table uses the Author's cable-header numbering, not USB receptacle contact
numbering. The cable has a male USB-A plug with a female-to-female USB-A adapter
accepting the keyboard's plug. Check the complete cable/adapter assembly.
Legacy `KCLK`/`KDAT` labels identify positions only: these wires carry
actual USB D+/D− here, not PS/2 clock/data.

| Cable header pin | Reported conductor | P4 DevKit connection |
|---:|---|---|
| 1 | GND | EXT2 pin 18, GND |
| 2 | KCLK / USB D+ position | EXT2 pin 19, `USB_DP`, silkscreen `USB-P` |
| 3 | KDAT / USB D− position | EXT2 pin 20, `USB_DN`, silkscreen `USB-N` |
| 4 | +5 V / VBUS | EXT2 pin 1, `+5V` |

`USB-P` is the positive USB data signal, not a power source. The dedicated
host signals reach chip DP/DM pins 50/49. The existing USB-C Serial/JTAG path
uses different pins and stays available for programming. EXT2.1 is the board's
5 V rail, not a separately switched/current-limited host VBUS output. The
keyboard's load and available bench supply budget must be checked before use;
do not infer a qualified host power circuit from a net named `+5V`.

Keep the D+/D− connection short and together. Do not reuse the Agon Port C
pull-ups or series resistors for USB. The new connection is not part of the
previously qualified r03 pinwalk/UART evidence; record its as-built state and
eventual fixture identity beside the hardware design before powered testing.

## Work

1. [ ] **W1 — Verify the physical connection.** With boards powered down and
   ribbons seated, the operator checks socket-to-header continuity and absence
   of shorts, then connects the four mapped conductors. Record cable orientation
   and keyboard identity/current rating. Verify supply polarity/voltage at the
   socket before attaching the keyboard. The USB acquisition candidate is now
   installed and enumeration has been observed. Prepare the controlled
   wiring/test record and suitable VBUS protection/power scope before deployment.
2. [x] **W2 — Prove P4 USB acquisition.** Integrate the supported HID host
   component with a bounded event source; first observe enumeration and exact
   press/release/modifier reports. Keep USB work outside HTTP handling and
   deliver events through the P4 process owner. Verify removal clears held
   state. Freeze the identified candidate before bench deployment; preserve
   existing UART pins and avoid sending unsolicited input to EMOS.
3. [ ] **W3 — Prove the ordinary EMOS CLI.** Implement and test explicit
   `extender` source admission and source-return cleanup, reusing stock packet
   handling. Handle key transitions, layout, repeat and removal; define the
   supported keyboard set before claiming parity. Autoexec performs setup and
   returns to the normal CLI on mainboard VGA. Test typing/editing, modifiers,
   held/released keys and unplug/replug without relying on browser focus or
   video. Record result and remaining compatibility limits beside the design.

BC-001 remains active for installation/recovery: the keyboard under test cannot
be assumed working to launch or repair its own test. Native USB input does not
clear the mainboard fault or qualify ExCom, hubs, mice, arbitrary report formats,
multiple keyboards, or the browser transport. Firmware/version selection uses
the existing standing Author preapproval and normal clean candidate gates.

## Physical preparation, 2026-09-09

The Author reports completed wiring, continuity/short/supply-voltage checks
passed, boards hot/connected, SD in Agon and no keyboard attached. Candidate
`usb-keyboard-probe-r01-b2026-09-09-19-58-58Z`, from clean `bee69b2`, passed
flash verification and native-host startup in PORT-015-2026-09-09-20-26-30Z.
The design-adjacent deployment record preserves the outcome and log hashes.
No Agon/SD change or Agon reset occurred. Native USB key acquisition, operator
keyboard identity/current rating and power-budget record remain open; W1/W2
are not yet claimed complete. The emulator screenshot is the earlier browser
attention cue and is not USB evidence.

The Author subsequently identified the USB data leads on the other exposed
USB controller. This image uses dedicated USB-P/USB-N at EXT2.19/20; the other
pair is GPIO27/26 at EXT2.16/17. Correct the two data connections with boards
powered down, then repeat acquisition. The two no-input attempts are ordinary
setup failures; their capture bundles and detailed narratives were discarded
under the bench retention policy. Keyboard is Perixx PERIBOARD-409, with
Author-reported USB HID/PS/2 support and lights at connection. Caps Lock LED
updates are intentionally absent in this acquisition fixture. No firmware
change is indicated by the wrong-controller observation.


## Corrected USB wiring: acquisition and reconnection observations

The Author corrected the data pair and completed the keyboard exercises.
PORT-015-2026-09-09-20-50-31Z records correct letters, Shift identity retention,
numeral, Enter/Backspace, no extra DOWN during the held-key exercise, and
synthesized releases when unplugged with Shift+A held. The Author clarified
that no reconnect was performed in that first recording.
PORT-015-2026-09-09-20-53-16Z records three connections and two removals, with
one valid a DOWN/UP pair after each connection and no intervening application
restart. Evidence is beside the r03 design under those run IDs.

Functional acquisition/cleanup/reconnection passed these observations. W2's
no-fault gate remains open: each removal logged USB HOST EP command error
ESP_ERR_INVALID_STATE. Investigate its source and disposition before full
qualification; do not classify this informative diagnostic as operator error.
Both recordings are stopped and saved. EMOS/SD and firmware are unchanged.
Future operator instructions should avoid requiring two keys held while
manipulating a connector; the completed held-key removal need not be repeated
without a diagnostic reason. W1 power/current particulars remain outstanding.


### USB capture wiring correction — 2026-09-09

The Author clarified that Agon was powered during these USB captures, but the Agon harness was not connected to the P4 right-side header (the same side as the USB connections). This supersedes the earlier assumption of a fully seated Agon/P4 harness for these runs. Native USB observations remain valid for this reported wiring state; simultaneous operation with the full Agon harness attached was not tested. The relation, if any, to the unplug diagnostic remains unestablished. No reconnection or hardware operation is implied by this correction. Applies to PORT-015-2026-09-09-20-50-31Z and PORT-015-2026-09-09-20-53-16Z; dated corrections are recorded alongside both captures.


USB repeat PORT-015-2026-09-09-20-59-38Z: all requested keys and matching
releases passed, including a after replug (two connections, sixteen reports,
fourteen key events). The same endpoint invalid-state diagnostic occurred at
unplug; W2 no-fault disposition remains pending. The repeat was requested with
the full Agon harness connected; the operator confirmed power and completion,
but did not separately confirm header seating. See the design-adjacent run
record for that evidence limit. Capture stopped and saved; keyboard remains
connected, with no EMOS/SD or firmware change.


## Unplug diagnostic disposition — 2026-09-09

The [pinned-source review](../../hardware/designs/light2-harness-r03/tests/usb-keyboard-unplug-review.md)
resolves the four unplug-only invalid-state log lines as expected upstream
endpoint-clear behavior. It supersedes the pending no-fault disposition above.
W2 bounded acquisition passes; original partial run outcomes remain historical,
and registry r45/artifact candidate status stay unchanged. No executable or
library change is warranted; a comment beside our disconnect callback records
the dependency behavior and removal condition. W1 power/current particulars
remain open. The following W3 work supersedes the prior next-step statement.

## W3 — Native USB to ordinary MOS CLI draft

The Author authorized W3 after the W2 review. Standing version preapproval
covers `agon-emos-v0.1.10`, `usb-cli-probe-r01` and registry r46, initially
draft. No physical EMOS/P4 image, SD contents or hardware state changes are
implied by these local builds. The
[ordinary CLI test sheet](../../hardware/designs/light2-harness-r03/tests/usb-cli-probe-r01.md)
owns the manual procedure and eventual physical result.

1. EMOS's resident `EMOS KEYINPUT extender` branch uses existing UART1
   ownership, isolated framing/IRQ effects and held-state cleanup. Mainboard
   remains selected on failed admission. A matching stock General Poll commits
   the requested source; it proves ordered progress, not peer identity.
   Pair the native-USB P4 image with `extender`, and the browser image with
   `browser`. Direct browser/extender cross-selection returns BUSY without
   tearing down the current receiver; select mainboard between those sources
   until a combined P4 provider selector exists.
2. The `p4-usb-cli` composition retains the maintained VDP processed-input
   queue, callback/event path and stock serializer. Native HID callbacks only
   copy reports/interface events. One P4 process owner maps reports, advances
   repeat, queues keys and transmits serialized packets. No browser server,
   local echo, ordinary VDU redirection, per-key poll, module or parallel
   transfer is added. The W2 standalone acquisition executable stays frozen.
3. The native mapping covers UK/US ordinary printable keys, modifiers, Caps
   Lock state, Enter, Escape, Tab, Backspace and navigation/F-key packet
   identities. Stock Backspace uses keycode 127 (raw ASCII 8); arrows use
   8/21/10/11. Existing browser sample mapping is unchanged. Keypad, other
   layouts, LED output, full settings/query forwarding and VDP-local control
   parity remain unfinished. A 500 ms initial delay and 100 ms repeat period
   provide bounded typematic, with no catch-up burst after stalls. Held key
   identity is retained through modifier changes; full stock repeat semantics
   across changing modifiers are not claimed.
4. Accepted events retain order. The pending queue reserves held-key release
   capacity; overflow/lost reports clear state and require physical neutral
   before new input. Admission drains accepted old events/releases before its
   reply and never replays keys held across admission. USB removal releases
   held keys and permits reconnect. A blocked UART TX cancels stale bytes after
   five seconds and requires fresh locale/poll admission; silence alone is
   not a source-exit signal. Malformed/partial commands or UART receive faults
   stop this bounded composition until a P4 reset, with a short serial reason.
5. EMOS sends retained locale during admission. A live native `SET KEYBOARD`
   also waits for an ordered stock poll; unsupported layouts withhold readiness
   and fail boundedly, retaining the prior EMOS layout and latching its owned
   receiver fault. This is a declared candidate limit, not full locale parity.
6. Autoexec selects mode 3, runs the ordinary SD/CLOCK smoke, sets keyboard
   layout 1 and selects extender input, then leaves the ordinary MOS prompt.
   There is no SD typing app or five-minute deadline. Mainboard VDP continues
   VGA output/cursor and the accepted VBlank clock. EMOS's browser-only text
   diagnostic gateway remains unavailable to this native input composition.

The official keyboard and system-command docs were refreshed first at the
AUDIT-004 baseline; retained `video/agon_ps2.h`, `vdu_stream_processor.h` and
`vdu_sys.h` provide the material key/control and serializer details. EMOS owns
its implementation under INTEG-009; Extender owns the pairing and P4 code.
Machine-local paths, exact draft bundles and review commands are recorded in
`agents/usb-keyboard/REVIEW.md` and the bounded USB précis.

Software checks pass native mapping/repeat/neutral recovery, pinned virtual
keys, retained callback/packet serialization, and the P4 owner with faked
UART/USB boundaries: CTS pause/overflow, five-second cancellation/readmission,
unplug/replug, unsupported locale and malformed/partial/UART errors. EMOS
receiver checks and the linked image's baud, IRQ, callback/keymap and public
UART ownership guards pass. A real EMOS headless peer review consumes 258
native-mapped, retained-serialized packets, edits ordinary CLI input, prints
shifted text, queries extender and returns to a usable mainboard prompt. The
absent-peer case also returns to that prompt. These are software checks;
USB/UART electrical timing, physical CLI behavior and Author graphical review
remain separate gates. Broader browser/full-keyboard work stays open.


### Author-supplied graphical review

The Author supplied the EMOS v0.1.10 draft screenshot. It visibly confirms
SD/CLOCK PASS, extender admission, corrected `USB cli`, shifted `Shift 1!`,
case-insensitive source query, `USB CLI REVIEW COMPLETE`, and mainboard source
return with the ordinary MOS prompt. Visual result passes; this screenshot
does not establish physical USB/UART timing. Source freeze/deployment remain
pending. Future emulator windows must distinguish visual validation (screenshot
requested) from notification-only cues (no screenshot needed).


Author accepted the graphical result and authorized P4 flashing plus guarded
EMOS SD preparation. Freeze the reviewed implementation as candidates under
registry r47 (standing version preapproval). Physical CLI proof remains pending;
installed images and exact new builds are recorded with deployment evidence.
