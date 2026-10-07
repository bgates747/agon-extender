# BOARD-001 — Board-selectable P4 builds and compile-time pin profiles

## Executive summary

The Author requests one maintained VDP codebase with selectable Olimex
P4-DevKit and P4-PC boards. The Pi build wrapper will validate tracked board
configuration, generate compile-time constants and SDK overrides, and record
the exact selected mapping in build evidence. The pre-flash build tranche is
complete. The Author arranged the bench to suit the original drawing and
withdrew the reversed-PC proposal. The restored drawing matches the unchanged
PC firmware configuration and prepared builds; no remapping is needed.

## Scope and authorization

1. Implement board selection independently of the software/source profile in
   `scripts/build_p4.py`. Preserve the existing DevKit default and GPIO tuple.
2. Prepare a P4-PC Rev C direct harness mapping using consecutive EXT1 contacts,
   retaining the Agon Port C ordering and shared UART/parallel lane roles.
3. Build the ordinary browser VDP on Pi ARM64 for both boards with the pinned
   ESP-IDF 5.5.5 and Arduino-ESP32 3.3.11. Preserve production v0.1.0, existing
   dirty work, historical harness definitions and original factory rollback.
4. Do not flash, reset, capture serial, change wiring, run physical network tests,
   modify EMOS or promote/commit/publish this candidate. The Author reports
   having installed the selected production image and obtained working web
   access on P4-PC; that report is bounded boot/web evidence, not GPIO or USB
   qualification. Read `HARDWARE.local.md` before subsequent bench work.
5. HDMI integration, a Pico-D4 SPI link, a new UART/parallel ownership contract,
   historical diagnostic migration and electrical qualification are outside this
   tranche. EMOS continues to authorize and coordinate transport selection.
6. Current Author instruction: restore the original diagram and mapping after
   the Author arranged the bench to suit it. Firmware code, board JSON, tests
   and existing build outputs remain unchanged.

## Research and dependencies

1. Official [Agon GPIO documentation](../../../../agon-docs/docs/GPIO.md) and
   [VDP UART overview](../../../../agon-docs/docs/VDP.md) establish the hardware
   variant boundary and retained VDU byte-stream contract. No API change is
   required; upstream sources remain read-only.
2. `hardware/designs/light2-harness-r03/README.md` records direct PC0–PC7 lanes,
   UART RX/TX/CTS/RTS on D0/D1/D2/D3, and eight 15 kΩ Agon-side pull-ups.
   The Author now requests omission of the series resistors. Its historical
   drawing is retained; this task does not certify a revised physical assembly.
3. Olimex P4-PC Rev C schematic, manual and factory USB example in the
   read-only manufacturer checkout are indexed by
   [the reference record](../hardware/esp32-p4-pc/README.md). GPIO20/32 sensing
   options must remain disconnected. USB HS uses the onboard hub, reset GPIO21;
   GPIO26/27 and the user LED GPIO2 are excluded from the proposed transport.
4. [Building](../building.md), `vdp/build/p4-profiles.json` and
   [BUILD-001](BUILD-001.md) own the native source graph and toolchain pin.
   Board configuration must not duplicate that graph or select another display
   family. The ordinary profile has browser output, without HDMI scanout.

## Decisions and implementation choices

| ID | State | Choice and consequence |
|---|---|---|
| B001-D01 | Author requested | One source tree; board configuration supplies compile-time GPIO values. |
| B001-D02 | Implementation choice | `--board` selects a tracked, revisioned JSON profile independently of `--profile`; omission retains DevKit. Reject unknown or unsupported combinations. |
| B001-D03 | Original mapping retained by Author | P4-PC uses five consecutive odd-side EXT1 contacts and six even-side contacts; no buffer-enable pins. The Author arranged the bench to suit the original drawing and withdrew the reversed-PC proposal. The unchanged firmware profile matches the restored mapping; electrical qualification remains pending. |
| B001-D04 | Implementation choice | Historical recovery and buffered parallel qualification profiles remain DevKit-only until separately reviewed. Configuring parallel lane constants does not implement a new product parallel transport. |
| B001-D05 | Required boundary | ARM tools may be selected explicitly through host-local paths; do not silently run migrated x86 tools or change pinned dependencies. |

## Subtasks

### B001-01 [x] Reconcile source and hardware contracts

Audit every GPIO touched by the ordinary console: boot fencing, UART setup and
TX cancellation, Ethernet, USB hub and SD. Separate direct-harness pins from
obsolete buffer controls. Record conflicts, optional sensing and board-specific
services; preserve DevKit behavior and the dated failed HDMI evidence.

### B001-02 [x] Define board profiles and validation

Create one tracked profile per board with identity/revision, transport lanes,
header positions, reserved connections, Ethernet/SD/USB settings and SDK
overrides. Reject duplicate/nonexistent/reserved transport GPIOs, unsafe values,
unsupported board/software pairs and inconsistent lane/header assignments.

### B001-03 [x] Extend the native builder

Add board selection, generate one constant header and effective SDK input,
record profile/header hashes and board identity in build manifests, and validate
actual compile inputs. Preserve fresh-output and dirty identified-build guards.
Allow explicit ARM tool and Python-environment paths with executable preflight.

### B001-04 [x] Use board constants in shared firmware

Replace ordinary product pin literals, including its early fence and TX abort
path. Retain UART roles and EMOS admission. Apply shared Ethernet/SD constants;
enable/reset the P4-PC USB hub without claiming keyboard qualification. The
Author selects the four onboard USB-A ports for keyboard attachment and accepts
one active keyboard at a time; do not add concurrent-keyboard composition.
Keep historical standalone fixtures scoped to their original board.

### B001-05 [x] Verify configuration and compile both variants

Run targeted negative configuration tests, generated C++ checks, native graph
checks and fresh ARM builds. Inspect app and bootloader silicon bounds, compiled
profile provenance, board-specific USB settings and actual packaged offsets.
Retain image hashes and precise limits; a compile pass is not a bench pass.

### B001-06 [x] Prepare the pre-flash review and documentation

Update the maintained build guide and dated log. Present the candidate image,
mapping, hashes, checks and unperformed hardware gates. Stop before flash and
leave current board state unchanged by this agent. Subsequent wiring review,
identity verification, flash authorization, UART/USB/SD
tests and Author acceptance remain separate gates.

## Additional requested drawing [x]

The Author requested a new drawing based on the preserved legacy SVG, showing
both complete headers, omitting sniffer circles and series resistors, and
connecting every pull resistor to the appropriate rail. The
[wiring review draft](../../hardware/designs/light2-p4pc-harness-draft/README.md)
derives signal endpoints directly from the PC board JSON again. The Author
withdrew the ascending-PC alternative after arranging the bench to suit the
original drawing. It shows eight 15 kΩ data
pull-ups, inherited 10 kΩ READY_N/VALID_N pull-ups and a 10 kΩ CLOCK pull-down.
All positive pulls use Agon pin 34; Agon pin 33 and PC EXT1-3 provide common
ground. The drawing is unversioned pending review and makes no as-built claim.

### B001-07 [x] Firmware remapping withdrawn — no code change

The Author retained the original wiring after arranging the bench to suit it.
The reversed-PC proposal and its deferred firmware work are superseded. The
[restored mapping table](../../hardware/designs/light2-p4pc-harness-draft/README.md#original-mapping--restored)
uses D0–D7 GPIOs 17,18,19,20,32,33,36,46 and
READY_N/CLOCK/VALID_N 15/14/16, matching the unchanged board profile and earlier
build evidence. No remapping or rebuild was performed or is needed for this
orientation request. Physical qualification remains a separate gate.

## Acceptance and remaining gates

1. This goal tranche is complete when B001-01–06 have reviewable outputs and
   both ordinary board variants compile with matching selected source graphs.
2. Full task closeout requires later physical mapping review, explicit flash
   authorization, passing relevant bench checks and Author acceptance. Production
   promotion/version agreement follows only that acceptance, under normal rules.

## Evidence and state

The authorized pre-flash goal tranche is complete. All six preparation subtasks
are implemented and checked; the full task remains open for hardware review,
qualification and Author acceptance. No hardware action was performed.
The following table describes the completed builds. The restored wiring
proposal matches the P4-PC column again; no binaries or provenance were changed.

| Check | DevKit | P4-PC |
|---|---|---|
| Native ARM build / action validation | PASS | PASS |
| Selected application sources | 33 | 33, identical source set |
| Compile actions | 1,842 | 1,844, hub support enabled |
| UART TX / RX / RTS / CTS GPIOs | 12 / 22 / 11 / 23 | 18 / 17 / 20 / 19 |
| Startup transport fence | 14 GPIOs | 11 GPIOs; hub reset excluded |
| Compiled USB hub support | Disabled, existing direct host | Enabled; four onboard ports, one active keyboard |
| App and bootloader binary silicon bounds | 1.0–1.99 | 1.0–1.99 |
| Merged-image exact segment check | PASS | PASS |
| Physical test | Not performed | Not performed |

Sixteen targeted host checks pass, covering invalid pin/configuration rejection,
emitted C++ role oracles and the retained native source/profile contracts. Board
validation inspects compiler dependency records and compiled SDK headers,
not just include directories or requested SDK settings.

Local evidence under `agents/board001/`:

1. `pc-build-network/` and `devkit-build/`: ELF, map, app/bootloader/partition/OTA
   segments, factory image, board/header/configuration manifests, validation,
   binary image-info and image checks.
2. `host-checks.log`, `host-checks.json`, `comparison.json`: test scope/duration
   and actual source-set equality. `source-snapshot/` retains the current source
   and build inputs with hashes; it is development evidence, not production.
3. PC factory candidate SHA-256:
   `af1d7f79b731419518ea441fe896a41bad615806651764468875d8501633909e`.
   DevKit factory candidate SHA-256:
   `cb487cc055b027d9eb55072a4be2c0f7fb94017e791159fa83c6fe5be01f6da9`.
   Both are unversioned dirty-tree development builds, not qualified release
   identities. Preserve these exact bytes; later candidate changes need new
   build evidence. Reviewed committed inputs are required for qualification.
4. `factory-preservation.json`: original full factory rollback hash unchanged;
   no device readback or flash occurred in this task.
5. `version-check.log`: full version validation finds a pre-existing r02
   connectivity/profile integrity mismatch. Both files are unchanged from HEAD;
   do not rewrite frozen evidence to make this check pass. Artifact-registry
   validation itself passes.

Build gotcha: default migrated native-tools binaries are x86-64; use the explicit
host-native overrides recorded in `HARDWARE.local.md`. The first sandboxed build
could not reach the component registry; network-enabled retry passed, and its
ordinary setup failure directory was discarded. Machine-specific paths and
device identity remain ignored local records.

The pre-flash review must still settle physical plug orientation, GPIO20/32
sensing disconnection and as-built pull/power connections. Later authorization
must select an exact candidate and verify device identity before replacement.
The Author clarified that source code is the firmware backup; do not create a
new device-firmware backup for routine flashing unless separately requested.
UART admission, keyboard enumeration/reconnect on each of the
four USB-A ports, local SD and browser service need bounded physical checks.

## Author-reported P4-PC smoke result — 2026-10-04

After receiving the direct command for the prepared P4-PC image, the Author
reports that the P4-PC accepts keyboard input from the web client, sends video
over Ethernet to the web client, and runs Nurples at an observed 16–17 fps.
This is a passing Author-observed smoke result for those paths, following the
Author-run flash of the prepared image; no agent flash/readback or boot capture
was performed. The command selected the PC factory image recorded above,
SHA-256 `af1d7f79b731419518ea441fe896a41bad615806651764468875d8501633909e`.

| Observation | Author result | Scope |
|---|---|---|
| Web-client keyboard input | PASS | Browser input; onboard USB keyboard not tested by this report |
| P4 Ethernet video to web client | PASS | Browser video; HDMI not tested by this report |
| Nurples frame rate | 16–17 fps | Author observation; timing method and comparable baseline not recorded |

These observations support the selected PC pin mapping and browser path in
the reported setup. They do not independently authenticate all GPIO lanes,
resistor wiring or installed bytes. Onboard USB ports, SD and the canonical
qualification/production gates remain open. No production selection, commit
or publication changes follow from this smoke report.

## Physical USB keyboard diagnosis — 2026-10-04

The Author reports EMOS in Legacy mode with `keyinput extender`: web-client
keys work and Nurples runs on the mainboard VDP at an apparently normal 60 Hz.
The keyboard attached to the P4-PC's lower-right USB-A socket (component side
up) does not produce EMOS input, has no observed plug-in light response, and
Caps Lock does not toggle its LED. Keyboard model and negotiated USB speed
remain unrecorded. Caps Lock is host-controlled; LED behavior alone does not
establish absence of port power.

| Path / observation | Result | Measurement boundary |
|---|---|---|
| Earlier P4 browser video / Nurples | Author observed 16–17 fps | P4-rendered browser output; method unrecorded |
| Legacy mainboard VDP / Nurples, web input | Author observed apparently normal 60 Hz | Mainboard display; not comparable to P4 browser frame throughput |
| Legacy physical keyboard input from PC USB-A | FAIL by Author | Lower-right socket; no keyboard input or Caps Lock LED response |

Read-only HTTP checks returned 200 for the homepage and `/keyboard/status`,
with `ready=true`, `physical_neutral=true`. These fields establish admission
readiness/current key state, not successful USB keyboard enumeration. Local
evidence: `agents/board001/usb-diagnosis/2026-10-04-22-41-01Z/`.

The pinned ESP-IDF 5.5.5
[USB Host limitations](https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-reference/peripherals/usb_host.html#features-limitations)
explicitly exclude full/low-speed devices behind a hub attached to a high-speed
host. The same limitation appears in the pinned checkout's
`docs/en/api-reference/peripherals/usb_host.rst`. The PC build enables hub
support and uses default high-speed host selection, with GPIO21 reset matching
Olimex's factory USB-storage test. That storage example is not proof that a
USB keyboard works behind the high-speed hub. The known stack limitation is
a strong candidate cause; actual keyboard speed, hub enumeration and port
power have not been established by serial evidence.

The newer official
[USB host documentation](https://docs.espressif.com/projects/esp-usb/en/latest/esp32p4/usb_host.html#full-low-speed-only-host)
describes `fsls_only` at host installation to run the high-speed peripheral
at full/low speed and avoid this limitation. The pinned 5.5.5 API does not
expose that field. Newer documentation requires supporting IDF HAL code; a
component-only update is not assumed sufficient. Do not select the unrelated
full-speed peripheral, which is wired differently, or modify upstream references.

### B001-08 [ ] Resolve PC hub keyboard compatibility

1. Determine a bounded PC-only full/low-speed host remedy compatible with the
   v1.3 silicon and pinned build dependencies, or a reviewed dependency change.
   Preserve DevKit direct-host behavior, original pin assignments and EMOS
   routing. Keep the earlier PC build/evidence unchanged.
2. Obtain keyboard enumeration/speed and hub state evidence through an admitted
   diagnostic path. Automatic approval review initially rejected direct passive
   serial capture due to reset risk. The Author subsequently explicitly
   authorized P4-PC diagnostics and accepted an incidental P4-PC reset, while
   prohibiting flashing and Agon resets. Passive capture now succeeds using
   the reset-avoiding raw-termios approach, without command writes or deliberate
   modem-line transitions. This authorization does not admit deliberate resets.
   Earlier read-only HTTP/source evidence remains preserved.
3. Any new executable candidate needs new build evidence and separate flash
   selection. No new device-firmware backup is required unless requested.
   Test one stable keyboard state at a time and wait for Author observation;
   include bounded acquisition/input/LED/reconnect checks before broader ports.

## Factory USB test comparison — 2026-10-04

The Author recalls factory keyboard tests passing without a typing test.
Read-only inspection of the authoritative Olimex checkout at
`04032d68e5c727870f9d40beb9e37b7ab3a66916` and retained original factory
image found a distinction between host initialization and device testing:

1. `SOFTWARE/ESP-IDF/p4_production_test/main/main.c:205` runs the USB test.
   It prints `USB Host init` / DONE after host/MSC initialization, before
   waiting for a device. It then runs a separately labelled USB FLASH TEST.
2. `components/usb_flash_test/src/usb_flash_test.c:178` installs the host and
   mass-storage class driver. The run function at line 227 waits for an MSC
   device, mounts FATFS, writes/reads a test file and compares its contents.
   No HID keyboard registration is called by the active main/display/USB-test
   components. Vendored LVGL USB-HID examples are not the active test program.
3. The saved factory image contains those same host/storage status labels.
   Its only readable keyboard-name string found is `lv_keyboard`; that is
   not evidence of a physical keyboard acquisition test. Strings do not
   establish an exact source-to-binary reproduction, so retain that limit.

| Setup detail | Factory active USB test | Current P4-PC VDP |
|---|---|---|
| Hub reset | GPIO21, active low, 20 ms + 200 ms recovery | Same |
| Host selection | Default high-speed (`peripheral_map=0`) | Same |
| Installed device class | Mass storage (MSC) | Boot keyboard (HID) |
| Host event-task priority | 20 | 6 |
| Class background-task priority | 10 | 5 |
| Device acceptance | File write/read verification | Keyboard reports after enumeration |

The factory setup is a useful reset/power/host reference, but its host-init
DONE or storage PASS does not validate FS/LS keyboard operation behind an HS
hub. No keyboard-specific full-speed workaround was found in the active
factory test source. Task priority differences are recorded, not established
as causes. The reported physical failure and the pinned-IDF hub limitation
remain unresolved. Source hashes and factory string checks are retained in
`agents/board001/usb-diagnosis/factory-reference.json`; original factory
rollback hash remains unchanged. No serial access, reset, flash or firmware
source modification occurred during this comparison.

## Authorized serial diagnosis — confirmed USB speed mismatch

On 2026-10-04 the Author explicitly authorized P4-PC serial diagnostics,
accepting an incidental P4-PC reset while prohibiting flashing and Agon resets.
Raw-termios captures suppress HUPCL and perform no serial writes or modem-line
transitions. The first 30-second capture returned normal runtime telemetry;
HTTP boot identity remained unchanged.

During the next capture, staged for one keyboard reconnect to the same socket,
the P4 USB host logged at device uptime 1,859,055 ms:

```text
HUB: Connected device is LS, transaction translator (TT) is not supported
EXT_PORT: [1:4] Port disabled, reset attempts=1
HUB: Device tree node (parent_port=4): not found
```

The first two lines confirm that the current host detects a low-speed device
on hub 1 / downstream port 4, then rejects it for lack of transaction-translation
support. This matches the Author's lower-right keyboard socket. It establishes
the host-stack speed/topology failure for that connection, rather than a
guess based on Caps Lock LEDs or web-input success. No typing/LED report
acquisition pass follows, and installed-image byte identity remains based on
the Author-run flash/selected artifact rather than agent flash readback.

Evidence: `agents/board001/usb-diagnosis/2026-10-04-22-54-29Z/` and
`agents/board001/usb-diagnosis/2026-10-04-22-55-46Z/`. No deliberate reset,
firmware write, flash backup or Agon operation was performed.

### Full/low-speed initialization experiment — authorized build, stop before flash

The Author now authorizes preparing and building this experiment, then stopping
with a Pi shell command for the Author to flash. The agent must not flash,
reset or change live device state as part of this step.

Keep the P4-PC's same high-speed-capable host controller and onboard hub
wiring, but constrain that controller to full/low-speed operation before its
first root-port reset. This lets the hub connect at full speed and avoids the
unsupported high-speed transaction-translation path for the low-speed keyboard.
Use a PC-only bounded backport using the pinned SDK's existing
`usb_dwc_ll_hcfg_set_fsls_supp_only()` helper in
`components/hal/esp32p4/include/hal/usb_dwc_ll.h:447`. Its HCFG field setter
exists in 5.5.5 even though the public `usb_host_config_t` does not expose the
newer `fsls_only` option. Espressif's current HAL
[`usb_dwc_hal_port_toggle_reset()`](https://github.com/espressif/esp-idf/blob/master/components/esp_hal_usb/usb_dwc_hal.c)
sets this field immediately before asserting reset on an HS-capable controller.
The local recipe follows that ordering in IDF 5.5.5's HCD, before every root-port
reset. Negotiation and keyboard function still need physical testing.

Preserve DevKit operation and the unchanged upstream SDK checkout. Any local
remedy must live in project-owned build/source inputs with an explicit removal
condition, board-specific selection and compiled provenance. Do not switch to
the separately wired full-speed USB peripheral or guess at hub reset delays:
the captured error identifies a controller-speed/stack limitation.

Implementation: `scripts/build_p4.py --usb-fsls-only` accepts only
`p4-console --board p4-pc`; it applies
`vdp/native/usb_fsls_only.cmake` to a hash-checked SDK HCD input in generated
build output. The recipe never edits upstream source. The build manifest
records the flag and recipe/derivative hashes; the validator checks compiled
HCD selection, bounded diff, USB archive inclusion and the application
diagnostic definition. Normal DevKit operation and board JSON stay unchanged.
The P4-PC USB startup log announces the selected FS/LS restriction; that log
does not by itself establish negotiated speed. The hub upstream link is limited
to 12 Mbit/s, sufficient for the requested single keyboard. Remove the recipe
when a reviewed/qualified SDK supplies the public install setting.

The Author confirms one reconnect to the same socket during the staged
capture. The complete 180-second capture retained 10,428 serial bytes; HTTP
boot identity was unchanged before and after. The low-speed/TT rejection
and port-disable lines are retained with an extracted diagnosis and log hash.
No P4 reset was observed, and no Agon access, firmware flash or source change
occurred. A different ordinary full/low-speed keyboard is likely to meet the
same documented host/hub limitation; the next recommended investigation is
the PC-only full/low-speed host initialization rather than another keyboard.

### Full-speed experiment build result — 2026-10-04

The authorized compile-only experiment completed on Pi ARM64. It retains the
experimental `UNVERSIONED-DO-NOT-DEPLOY` identity with the Author explicitly
selecting this informal experiment. The agent stopped before flashing.

| Check | Result |
|---|---|
| Host build/board checks and backport guards | 18 passed |
| Native PC build and validator | PASS; 1,844 compile actions, 33 selected application sources |
| Compiled USB driver | Generated HCD derivative selected, archived and linked into the ELF |
| Machine-code check | HCFG.FSLSSupp write precedes HPRT reset assertion, guarded by HS PHY capability |
| Prior PC configuration comparison | Identical board/header hashes, SDK configuration, dependency lock, IDF commit and reset-URL selection |
| SDK reference | Unchanged, clean checkout |
| Image header | ESP32-P4, revisions 1.0–1.99, 16 MiB DIO/80 MHz; checksum/hash valid |
| Factory image | 1,727,680 bytes; SHA-256 `b3c4923a2ecf82c51cbcb36af137c9599c46506dd7f7c2e3de71703836b631c2` |
| ELF | SHA-256 `622062ae010c8b0f76b3f4e5f7f023a02d47af152e3c00b54623a0e21e7154b0` |
| Physical USB keyboard, LEDs and reconnect | Pending Author flash and test; no hardware claim |

Exact artifacts, source snapshots, manifest, validation and compiled USB
disassembly are retained under ignored `agents/board001/pc-usb-fsls-network-build/`.
No device access, firmware backup, flash, reset, Agon operation, production
promotion, commit or push occurred in this build step. The shell command given
to the Author selects this offset-zero factory image and the stable PC endpoint
from `HARDWARE.local.md`. Keep the prior PC build and informative serial failure.

### Full-speed keyboard tests fail; enumeration blocker narrowed — 2026-10-04

The Author reports physical keyboard failure after several power cycles of
both boards, hot-plugging, and booting P4-PC with the keyboard attached.
Browser input works in Legacy and ExCom; ExCom typing latency feels very good.
These are Author-run tests of the prepared experiment, not agent flash/readback
verification. The preceding build receipt remains unchanged.

Under the standing passive diagnostic authorization, the agent captured one
Author-confirmed keyboard reconnect to the same USB-A socket. At device uptime
452,505–452,507 ms:

```text
HCD DWC: Low-speed, extra delay will be applied in ISR
USBH: Dev 0 EP 0 Error
ENUM: Bad transfer status 1: CHECK_SHORT_DEV_DESC
ENUM: [1:4] CHECK_SHORT_DEV_DESC FAILED
EXT_PORT: [1:4] Port disabled, reset attempts=1
```

| Stage | Previous default-HS test | Current full-speed experiment |
|---|---|---|
| Low-speed device detected | Yes | Yes |
| Host/hub upstream speed | High speed; explicit TT rejection | Full speed; warning only occurs for FS host / LS device |
| Blocker | Unsupported transaction translation | Initial device-descriptor control transfer fails |
| HID keyboard admission | Not reached | Not reached |
| Browser input | Working | Author confirms Legacy and ExCom |

Pinned `components/usb/hcd_dwc.c:1742` emits the warning only when
`port_speed == USB_SPEED_FULL && pipe_config->dev_speed == USB_SPEED_LOW`.
This confirms that the full-speed restriction took effect. Transfer status 1
is `USB_TRANSFER_STATUS_ERROR` in
`components/usb/include/usb/usb_types_stack.h:102`. It is generic; missing
response/CRC trouble are possible meanings, not established causes. Invalid
descriptor contents, keyboard VID/PID, exact bus-error type, power fault or
silicon defect have not been established. The LS-via-FS-hub code retains the
SDK's one-millisecond control-stage workaround (`hcd_dwc.c:398–400`, internal
IDF-12986); this capture alone does not justify changing it.

Next recommendation: one alternative wired keyboard on the same socket and
current image, with passive enumeration evidence, before another firmware
change. This is now a useful hardware control because the broad high-speed
transaction-translation rejection has been bypassed. Preserve each test state
until Author observation.

The console code already removed its unconditional one-millisecond owner-loop
sleep during the earlier
[owner scheduling comparison](PORT-008/uart-alignment/E07P-owner.md).
That could contribute to typing responsiveness; no comparable measured typing
latency or attribution to P4-PC hardware exists.

Evidence: ignored `agents/board001/usb-diagnosis/2026-10-04-23-32-24Z/`.
The 180-second capture retained 9,669 bytes, with unchanged HTTP boot token
before/after. No P4 reset was observed. The agent made no firmware changes,
builds, flash writes, deliberate resets, Agon accesses or input injections.

### Author-requested mainboard SD roundtrip — 2026-10-04

PASS: Pi uploaded3,072 bytes to a unique absent test path beneath
`/agents/extender/results` on Agon SD via the existing automatic mainboard
WebDAV service, then fetched it back. Exact bytes/SHA256 match; PUT201,
9.368s; GET200,3.021s. These host monotonic request durations include
HTTP, P4-card staging and EMOS-authorized UART/file work. They do not
measure raw SD throughput. Local evidence: ignored
`agents/board001/sd-roundtrip/2026-10-04-23-52-34Z/`. The test file remains
on the Agon card. No existing target replacement, firmware change, reset,
mode switch or input injection occurred. This bounded smoke does not close
SD peripheral qualification or production acceptance.

### Pi-controlled Agon reset smoke — 2026-10-04

PASS by Author: the Author ran the direct Pi GPIO17 100 ms reset command
through the existing transistor circuit and reports normal operation after
restart. Read-only host inspection confirmed gpiochip0/pinctrl-rp1 and
libgpiod2.2.1 before the command was provided. The agent did not actuate the
reset. This is one functional reset/restart observation, not electrical
qualification or oscilloscope timing verification. P4 restart was not reported.

### Recovery wiring deferred by Author — 2026-10-04

The Author defers adding the two ZDI recovery leads until ready to rewire.
Proposed PC connections remain unimplemented: EXT1-19/GPIO47 to Agon ZDI1-4
TCK; EXT1-20/GPIO48 to ZDI1-6 TDI, using existing common ground. The retained
DevKit recovery firmware still selects GPIO46/47; GPIO46 is PC harness D7,
so a PC-specific programmer adaptation is required before recovery use. No
rewiring, firmware changes or recovery invocation occurred. Remaining bench
review items are physical USB keyboard compatibility, a direct P4-local SD
roundtrip, as-built sensing-link/pull/ground inspection and later parallel-lane
qualification when its product implementation is ready. Current web-input/video,
Agon SD roundtrip and Pi reset smokes pass within their recorded scope.

### P4-PC local SD roundtrip — 2026-10-04 local time

PASS: Pi sent a 3,072-byte binary through the maintained P4-local HTTP client
to a unique absent file under `/agents/extender/results`, then fetched it back.
Exact bytes and SHA256 matched:
`12adc9dff80688800f2f591f0da6ab2f8109d61d910697801f57669ec0d719d3`.
Upload20.691ms; download22.190ms, measured by Pi monotonic clock around the
client calls. These include HTTP/P4 SDMMC/FatFS work and client processing;
download includes local-file installation/sync. They are one small-file smoke,
not raw SD throughput or a sustained performance benchmark. P4 reported
mounted:true, mount_error:ESP_OK and format_enabled:false. Agon/EMOS did not
participate. No existing file replacement, reset, format or firmware change.
The small file remains on the P4 card. Evidence retained under ignored
`agents/board001/p4-sd-roundtrip/2026-10-05-00-07-46Z/` (UTC run timestamp).
The direct P4-local SD smoke item passes; broader SD qualification remains.
