# INPUT-004 — P4-PC onboard USB keyboard support

Make a physical USB keyboard work through a P4-PC onboard USB-A socket while
preserving the working directly attached F310, browser recovery input and EMOS
routing. The earlier speed workaround is installed, but a low-speed keyboard
failed its first descriptor transfer. Establish the remaining cause from pinned
source and physical evidence, implement the smallest justified correction, and
qualify actual typing/LEDs/reconnect plus keyboard/controller coexistence.

## State and authorization

1. On 2026-10-28 the Author requests this research/implementation task, a commit
   and push of all current dirt before proceeding, then work toward an onboard
   keyboard. Publish this plan before implementation or live diagnostics.
   The Author subsequently confirms a powered/free bench, attaches the keyboard
   and authorizes the first physical tranche. After a hotplug-related scanout
   abort, the P4 error-logging candidate is installed and verified. One controlled
   Author replug passes with no restart or scanout fault. The Author confirms
   physical typing still produces no characters; the last captured enumeration
   attempt failed before HID acquisition. A subsequent captured CHERRY
   comparison also fails initial SETUP; shared low-speed handling remains open.
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
   wiring. Pinned ESP-IDF 5.5.5/b774170ff46c393eeb5e495ea37936038d3f4f4f lacks the
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

1. [x] Publish task/TODO and all reviewed existing dirt as requested. Preserve
   private ignored files and immutable evidence; do not stage generated private
   firmware, secrets or another project's emulator implementation.
2. [x] Pin current code/build/reference inputs and collect a source-level USB
   failure-path précis. Compare upstream fixes and the cache-coherency lead;
   identify expected signatures and smallest discriminating checks. Independent
   offline research may run in parallel, with only one bench owner.
3. [ ] Establish current bench owner, actual foreground/CLI, keyboard identity,
   connection and socket. Collect bounded existing-build enumeration evidence
   before changing firmware. Compare one alternative keyboard if available;
   keep each physical state stable and ask the Author for needed physical work.
4. [x] Implement an evidence-supported remedy or diagnostic extension in a
   project-owned matched composition. Add meaningful offline checks for the
   affected low-level contract; run relevant existing input/controller checks.
   Do not claim target/device success from host tests.
5. [x] Build a clean identified candidate preserving installed hardware/display/
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
| I4-03 | Open | Original and CHERRY keyboards both fail initial SETUP/XCS_XACT with FS root, PRE selected and MPS8. The Author confirms only the keyboard cable was plugged during CHERRY capture. F310 disappearance/reacquisition was not an intentional controller unplug. Actual wire behavior and the shared USB event's cause remain unresolved. |
| I4-04 | Partially established | Initial SETUP failure followed the keyboard from parent hub1/port1 to hub1/port3. Linux subsequently identifies the Author-transferred specimen as `04d9:a088`, a Holtek vendor ID with no manufacturer/product strings. Retail brand/model and physical socket label remain unrecorded. |
| I4-05 | Linux inventory complete | The Author supplied all four keyboards in turn. All enumerate at 1.5 Mbit/s and expose compatible boot-keyboard interfaces. Exact descriptors/speed evidence are retained; captured P4 comparisons remain the next physical gate. |

## Evidence and stop boundaries

Keep source findings, offline checks, target compilation, installed-byte proof,
USB enumeration and actual typing separate. No mainboard/EMOS change, emulator
change, physical rewiring, broad suite or production selection follows merely
from this task. If the current source cannot reveal the failure, prepare a bounded
instrumented candidate rather than repeatedly power-cycling or guessing delays.
Stop at an explicit Author boundary; never replay uncertain input/transfers.

## Source research results — 2026-10-28

1. Plan/current dirt were committed and pushed as`01a2e17b` before source work
   or live diagnostics. Three bounded independent reviews covered LS transfers,
   DMA/cache ownership and the existing HID keyboard client. Their ignored notes
   are under `agents/input004`; conclusions relied on here are recorded below.
2. Pinned SDK`hcd_dwc.c:1739–1745` already enables LS-via-FS-hub preambles;
   `:388–404` already delays1000us between successful LS control stages for
   internal Espressif issue IDF-12986. Current upstream retains these mechanisms.
   Adding them again or blindly increasing reset/stage delays is unsupported.
3. `CHECK_SHORT_DEV_DESC` covers SETUP, DATA and STATUS. Its generic status 1
   collapses HCD ERROR_XFER / HAL XCS_XACT (three failed transactions); it does
   not disclose which stage or why the device transaction failed. Stage data
   is cleared during ISR buffer parsing, so it must be retained before that
   destructive point, then published later from task context.
4. Pinned `cache_sync_data_buffer`, lines310–319, already cleans ALL control
   buffers before DMA and invalidates them after completion. Thus the recorded
   initial descriptor error is not explained by missing pre-IN cleaning.
   A separate omission exists for non-control IN enqueue. Official
   [Espressif USB 1.6.0](https://components.espressif.com/components/espressif/usb/versions/1.6.0/changelog?language=en),
   repository commit`630f1c4e61f71d62bb57ff1b840931da24c3329f`, corrects the
   [HCD helper](https://github.com/espressif/esp-usb/blob/630f1c4e61f71d62bb57ff1b840931da24c3329f/host/usb/src/hcd_dwc.c)
   to clean all enqueue directions while preserving post-IN/control invalidation.
   This is a bounded input-path correctness backport, not a keyboard-cause claim.
5. EspUsbHost v2.8.0 pin`d6f34638bf917e337b56322a8a4b289a834e1709` supports that
   non-control-IN mechanism. Its allocator-zeroing assertion does not match our
   SDK: transfer data uses aligned internal DMA heap allocation without zeroing;
   the separate URB structure is calloc'ed. No new alignment defect is proven.
6. Root and installed HID keyboard acquisition source match. Public HID1.2.1
   APIs report only successfully enumerated devices, not early EP0 failures.
   Existing controller client already logs every enumerated device identity.
   A tentative stale-active-handle concern was retracted after the pinned HID
   close callback was inspected. Do not patch unconfirmed lifecycle guesses.
7. Small candidate scope: retain LS EP0 stage/HAL error/frame in a private pipe
   record under the existing HCD ISR lock, copy/clear it for the matching dequeued
   URB under the same lock, and emit one diagnostic line only after task-context
   unlock. No logging, allocation or added waits in the ISR, no report contents,
   successful-transfer logs, retries, delay changes or peripheral rerouting.
   The independent official cache correction must remain separately identified
   in the generated derivative and tests; neither change proves device success.
8. Initial read-only P4 service snapshot shows healthy attached F310, admitted
   neutral remote keyboard and no pending SD operation. Fsim confirms no active
   or queued exclusive bench work. Actual Author foreground and physical
   keyboard identity/connection remain unknown. One bounded passive P4 capture
   uses the maintained opener; no keys, reset, flash or mainboard operation.

## Prepared diagnostic / independent cache backport

1. The complete generated HCD remains pinned to upstream SHA-256
   `33fea9059ee546d1c773fc5e86ed0c294e600e645c4c14e0788ce879f596280b`
   and derivative SHA-256
   `2fb477b78bafbd16d292103c2438fc8abba1bdc10cefbd254e62e1426b50492b`.
   The validator rejects any unrelated generated-byte change; original SDK
   bytes remain unchanged. Only PC FS/LS builds select this derivative.
2. A failed LS control URB records its stage, HAL error and frame under the
   existing ISR HCD lock. Matching task dequeue copies identity/port fields,
   clears retained ownership, unlocks, then logs one line. No live HCD pointer
   is dereferenced after unlock, and no successful transfer/key data is logged.
   The one-slot-per-pipe record can lose an earlier diagnostic if multiple
   failures precede dequeue; it does not alter transfer/recovery behavior.
3. The independent official one-condition IN preclean correction is included
   in the same identified candidate. Control-transfer synchronization is
   unchanged, but extra work on other active IN pipes may affect scheduling;
   therefore an eventual device pass would not by itself attribute causality
   to either change. Do not describe this combined candidate as an unchanged
   timing control or reconstruct a missing original failure from its result.
4. Meaningful host checks compile the actual generated ISR snapshot/dequeue
   code against lock/queue spies and the original/generated cache helpers
   against a synchronization spy. They cover matched/older URB ownership,
   repeated reuse, gates, post-unlock logging and 16 cache ownership combinations.
   ASan/UBSan check the cache helper; leak scanning is disabled only because
   the managed runner's ptrace prevents it, and that harness allocates no heap.
5. An independent source review found no blocking lifetime/locking issue for
   compilation. This was source preparation; the first physical tranche below
   records subsequent installation and actual device evidence. No EMOS,
   mainboard or startup change is selected.
6. The 50 selected host checks pass in 6.75 monotonic host seconds. The matched
   source commit is`8c90c869`, based on the installed`cabbea34`; its source
   difference is restricted to this USB derivative, validator and tests.
7. Experimental build`indexed-hdmi-r14-b2026-10-28-19-32-01Z` passes native
   compilation and declared/compiled/archived/linked validation in 406.24 host
   monotonic seconds. Its application is 1,778,048 bytes, SHA-256
   `bb903f05123b0642772cc5b8774ebbc65ccf746dbb392a5629142eeaef6195aa`.
   Independent comparison verifies the source archives and unchanged board,
   display, dependencies, SDK configuration and generated application inputs
   after exact path/build-identity normalization. Five focused checks also pass
   from the matched checkout. The first physical tranche below records later
   installation. Actual keyboard typing checks remain pending.
8. The new application is 416 bytes larger than the prior image. At the existing
   application offset 0x20000 its 4 KiB write-sector range is [0x20000,0x1d3000),
   one sector larger than the prior image's range. Refresh selective-write,
   whole-flash backup/readback and outside-sector comparisons accordingly;
   do not reuse the earlier installation helper's hardcoded limits.

### Reading the first device failure

The pinned HCD's control-stage values are 0=SETUP, 1=DATA and 2=STATUS
(`components/usb/hcd_dwc.c`, `_buffer_exec_cont`). HAL error values are
0=three consecutive transaction errors, 1=buffer unavailable, 2=packet babble
and 3=STALL (`components/hal/include/hal/usb_dwc_hal.h`). Buffer-unavailable
still follows the stock fatal path and may abort before task-context publication.

| Observation | What it establishes | Next bounded investigation |
|---|---|---|
| SETUP transaction failure | The first eight-byte request did not complete. | LS signaling/preamble, device response and host scheduling; do not blame HID parsing. |
| DATA transaction failure | SETUP completed; descriptor reception failed. | Direction/PID, response length and stage transition, retaining existing cache proof. |
| STATUS transaction failure | Descriptor DATA completed; final acknowledgement failed. | Opposite direction/PID and stage transition; do not call this a missing descriptor. |
| STALL | The device rejected that control transaction. | Exact request/identity and any device-specific contract. |
| Keyboard enumerates | This device reached HID acquisition in this composition. | Actual typing/release/LED/reconnect and controller coexistence; no causal attribution from success alone. |

Capture attachment time and complete enumeration context, not just one error
line. A generic transaction error still does not distinguish no response from
other wire-level failures. Compare the existing image before installing the
candidate when physical state permits; do not manufacture a baseline by
restarting a running Author application.

## First physical tranche — 2026-10-28

The P4 now reports the precise failing stage, but the attached keyboard still
cannot enumerate. The failure precedes descriptor data and HID keyboard setup.
The installed diagnostic preserves working native F310 acquisition, admitted
host input, actual MOS CLI access and unchanged load-only startup. This is a
retained informative failure, not keyboard acceptance or production promotion.

| Observation | Existing P4 image | Diagnostic P4 image |
|---|---|---|
| Keyboard first descriptor request | Generic status1; stage unavailable | Initial SETUP, HAL XCS_XACT / three consecutive transaction errors |
| Requested low-speed path | LS-via-FS warning | Root FS, PRE selected, EP0/address0, MPS8, frame172 |
| Onboard hub | Full-speed, VID:PID 1a40:0101 | Same hub identity/speed |
| Native F310 | Valid first report, fault0 | Valid first report, fault0 |
| Actual MOS CLI and fast2 listener read/EXIT | Verified | Verified after fresh admission |
| Startup |108 bytes; unchanged, load-only | Same exact bytes; no RUN/EXEC |

1. Existing startup was independently downloaded before resets; the diagnostic
   installation used a fresh whole-device backup and whole-device verification.
   Only application sectors [0x20000,0x1d3000) were written. Independent 16 MiB
   readback matches the application exactly and every byte outside those sectors
   matches the incoming image. Actual bootloader, partitions, NVS and OTA were
   retained. No EMOS/mainboard firmware or SD file was written.
2. Incoming whole-flash SHA-256 is
   `dd878e47395f967341aeee403ba60681df7a602ca77a0bfdc81e490d9b3db4a0`;
   after-write SHA-256 is
   `75c185767b3260cde7094da1a8c4cc811d2f64679faa68acba1619164940999e`.
   The exact expanded rollback sectors are retained locally. Restoring only
   the shorter old application does not restore the extra tail sector.
3. Exact new console identity, USB host, F310 and display readiness preceded
   Agon reset release. Fresh admission was followed by observed CLI commands,
   two checksum-free fast2 startup reads/EXITs and verified quiet printer mirror.
   Final CLI input is neutral; listener is offline/idle, card stays mounted,
   all captures/clients/reset holds are closed and no guest application ran.
4. Installation took 530.19 host monotonic seconds. Backup read 231.1 s, application
   write 14.0 s and independent full readback 236.2 s are separate esptool-reported
   elapsed times; their rates vary with the host/link. A retained 154.3 s read
   underestimated this run. Keep that uncertainty in future advance estimates.
5. The HCD configuration confirms PRE selection and MPS8, not actual wire
   signaling. Initial SETUP failure precedes the existing 1000 us interstage
   workaround. Pinned source also enables UTMI parallel low-speed operation and
   keepalive. Neither a missing HID mapping nor an increased interstage delay
   is supported by this failure. The independent non-control-IN cache backport
   did not make this keyboard enumerate; do not infer broader cache qualification.
6. Log interpretation gotcha: HID1.2.1's `No HID device at USB port 2` prints
   `dev_addr`, not the downstream socket number. Here it describes the vendor
   F310 interface. The enumeration failure's `[1:1]` is parent hub address 1,
   port 1, as defined in pinned `components/usb/enum.c`; do not confuse them.
7. Official [USB guidance](https://docs.espressif.com/projects/esp-usb/en/latest/esp32p4/usb_host.html#full-low-speed-only-host)
   describes FS/LS-only operation as avoiding the HS-hub split limitation.
   [Espressif issue15683](https://github.com/espressif/esp-idf/issues/15683)
   contains P4 reports with the same generic LS descriptor error, including
   unsuccessful 500 ms reset/power delay trials. Those reports do not establish
   our exact mechanism; their nested HS-hub explanations cannot be assigned to
   this confirmed FS root. No source-supported additional remedy was found.
8. Next physical discriminator: the Author exchanges the existing keyboard and
   F310 sockets; the agent captures both devices on the unchanged diagnostic
   image. If the failure follows the keyboard while F310 works in either socket,
   the port-specific explanation weakens. F310 is FS and still does not qualify
   LS signaling. Then compare a known FS boot keyboard if available. No GPIO
   rewiring or speculative clock/delay/MC-EC patch is selected.

Machine-local evidence is indexed by `HARDWARE.local.md`, including baseline and
new boot captures, preflight/CLI receipts, exact flash/rollback bytes, source
comparison notes and the first-tranche duration receipt.

## Socket exchange failure and bounded correction — 2026-10-28

The Author reinserted the keyboard first after exchanging sockets and reported
a blank blue P4 display. Preserved HTTP evidence shows the same P4 incarnation
and live services/F310, with a latched HDMI scanout sequence fault. This is an
informative failure, separate from the keyboard's unsuccessful USB enumeration.

1. Retain initial service/counter snapshots and passive serial capture before
   recovery. `STRIP_FAULT_SEQUENCE=8`, detail 14 means 14 completed strip callbacks
   where the 848x480 frame needs 15; `430244=28682*15+14` corroborates it. The
   driver disables scanout DMA; it does not paint an error page or reboot P4.
   Refill 5392 us/copy 5389 us include delayed completion callbacks and do not prove
   that DMA execution itself took that long. Do not infer causality from replug
   chronology or convert the USB/JTAG console bytes using a UART baud rate.
2. The standing first Agon reset yields fresh input but does not clear the
   HDMI latch. P4 initialization followed by Agon reset restores scanout on the
   unchanged image. A new bounded boot capture shows the keyboard still fails
   SETUP/XCS_XACT, now parenthub1/port3; F310 is valid. The failure follows the
   keyboard across sockets. No firmware was changed for this comparison.
3. Source shows the USB ISR and rolling display IRQs are installed on core1.
   The existing 1000 us HCD critical-section delay is a risk on successful LS
   control stages but is not executed for this failed first SETUP. Pinned
   `components/usb/usbh.c:ep0_pipe_callback` additionally uses synchronous
   `ESP_EARLY_LOGE` from ISR for EP0 ERROR/STALL. It selects ROM USB/JTAG output.
   This blocking I/O is a concrete deadline exposure; its duration and causal
   contribution to this failure have not been measured.
4. Prepare a minimal project-owned, original/derivative-hash-pinned `usbh.c`
   backport under the existing explicit PC FSLS selection. Replace ISR error
   prints with two internal pending-action bits, and print retained ERROR/STALL
   visibility from `usbh_process` after releasing the existing lock and before
   any device free. Preserve original transfer actions, callbacks, wakeups,
   allocation, clocks, timing delays, CPU affinity and peripheral mapping.
   Existing pending actions may coalesce; record that reporting limit.
5. Meaningful host checks compile actual generated callback/action processing,
   test ISR and task events, all error kinds, unchanged original action bits,
   batch coalescing, no ISR/locked logging and log-before-free lifetime. Extend
   build validation and artifact records to prove the generated USBH unit is
   the only selected/archived/linked unit. SDK checkouts remain untouched.
6. Build and stage only a clean matched candidate, preserving current display/
   controller/dependency choices and verified rollback. After deployment, record
   actual CLI/input/scanout handback. The Author's controlled replug is the
   acceptance gate for this correction; host checks and cold boot are not a
   hotplug pass. Do not claim it repairs keyboard enumeration or merely raise
   the HDMI deadline guard to conceal missed callbacks.
7. Implemented/pushed the correction as `88293037`, with clean matched source
   `f00c5a0560b172d885af64a458eafac1ca763dce`. Built and independently validated
   `indexed-hdmi-r14-b2026-10-28-20-24-08Z`; application 1,778,112 bytes, SHA-256
   `b87f26792ee25737b47153e07dc76718c438d9cdc61111a5f3cb05246db43547`.
   All 31 focused host checks pass. Independent composition review confirms
   that the installed display, controller and dependency selections are retained.
8. Installed only application sectors [0x20000,0x1d3000). The retained incoming
   whole-device backup was freshly verified against the actual P4 before reuse.
   Independent full 16 MiB readback matches the application and every byte
   outside those sectors is unchanged. Incoming whole-image SHA-256 is
   `75c185767b3260cde7094da1a8c4cc811d2f64679faa68acba1619164940999e`;
   after-write SHA-256 is
   `5f924aa780531de0c70f2bd8da33b70703b6c13c5e0f33874ddea7e2cc90131c`.
   Exact expanded rollback sectors and installation receipts are retained locally.
9. Exact new P4 console/USB/F310/display readiness preceded Agon release. Fresh
   input admission, actual Legacy MOS CLI, unchanged load-only startup and two
   fast2 read/EXIT exchanges with quiet printer mirror all pass. Final scanout
   advances with zero faults; F310 is valid/fault0, input neutral and the listener
   offline/idle. EMOS, mainboard VDP and SD files remain unchanged. No guest
   application or full suite ran. All serial readers and reset holds are closed.
10. Native build took 603.25 host monotonic seconds; installation took 221.95 s,
    including a separately reported 166.1 s full readback. These are elapsed host
    times, not calibrated device timings. Reusing a freshly verified backup
    avoided another full-flash read. Retained receipts support future estimates.
11. The keyboard still fails initial SETUP on hub1/port3. This candidate addresses
    the identified ISR logging exposure, not a proven hotplug cause or keyboard
    remedy. The next gate is the Author unplugging both devices and reconnecting
    keyboard first, then F310, retaining their current sockets. Keep P4 serial
    readers closed during this physical comparison. Hotplug acceptance, actual
    keyboard operation and production promotion remain pending.

## Controlled replug result — 2026-10-28

The Author unplugged both devices and reconnected the keyboard first, then F310,
in their current sockets. The Author observed no P4 reset and left both attached.
Read-only service snapshots confirm that this replug did not reproduce the HDMI
abort. This is one passing physical comparison, not a general hotplug guarantee
or proof that ISR logging caused the earlier abort.

1. P4 incarnation and mainboard input epoch are unchanged from the candidate
   handback. Two snapshots show scanout advancing from frame143839 to143960,
   with faults, sequence errors, overbudget and underruns all zero. No reset,
   firmware write, input injection, mode change or guest invocation occurred.
2. F310 reacquired as USB address3, valid/fault0, nine reports and no malformed
   packets. This confirms acquisition after the completed replug; a simultaneous
   physical typing/controller exercise has not yet been performed.
3. P4 serial readers stayed closed through the physical comparison. A later
   bounded six-second passive capture contains normal display/network metrics;
   it did not retain the earlier enumeration event. The existing HTTP keyboard
   status describes EMOS admission/neutral state, not USB keyboard attachment.
   Therefore current physical keyboard acquisition cannot be inferred from its
   ready flag or the absence of an error in that delayed capture. The last
   directly captured keyboard attempt failed initial SETUP. Request an actual
   physical typing observation before claiming any new keyboard result.
   The Author subsequently types on the physical keyboard and confirms that
   no characters appear; the end-to-end input check fails.
4. All serial readers are closed. Input remains admitted/neutral and SD service
   offline/idle; both devices remain attached. No change to EMOS, mainboard VDP,
   startup or SD contents. Evidence remains in the machine-local bench index.

## Multi-keyboard Linux audit — 2026-10-28

1. The Author supplies a Logitech keyboard on the Linux workstation and
   authorizes read-only queries. The Author will next attach the keyboard from
   P4 and has two more different models available for the same audit.
2. [Keyboard comparison](INPUT-004/KEYBOARD-AUDIT.md) records the first result:
   Logitech K120 `046d:c31c`, actual low speed 1.5 Mbit/s, two HID interfaces,
   standard 8-byte boot keyboard on interface 0 and separate media/system
   controls on interface 1. Linux enumeration succeeds. Physical typing and
   P4 operation have not been tested for this specimen.
3. Preserve binary descriptors and actual negotiated speed for each attachment,
   rather than inferring speed from USB specification or product strings. Read
   input capabilities without collecting user keystrokes. No driver detach,
   reset, protocol/LED change, event grab or firmware operation is needed for
   the host descriptor audit. Keep the P4 bench untouched during these queries.
4. The Author moves the original P4 keyboard to the Linux workstation. It
   enumerates as `04d9:a088`, low speed 1.5 Mbit/s, revision `0x0113`, with a
   standard boot keyboard on interface 0 and separate system/media/mouse HID
   on interface 1. No manufacturer/product strings establish a retail model.
   Binary descriptor/driver/capability evidence is retained. Both audited
   devices match the current ordinary-keyboard decoder; neither is full speed.
   Two additional keyboard models remain for the Author to attach in turn.
5. The third keyboard identifies as CHERRY `046a:0011` (G83 / RS 6000 USB-ID
   database label), revision `0x0111`, again low speed 1.5 Mbit/s. It has one
   ordinary boot-keyboard interface, an 8-byte report and three lock LEDs, with
   no extra HID interfaces. Linux enumeration succeeds. Its simpler composition
   is useful for comparison but is not an established SETUP-failure remedy.
   One final keyboard remains for Linux audit; no P4 access occurred.
6. The fourth keyboard identifies as IBM NetVista `04b3:3025`, with LITE-ON
   manufacturer string, revision `0x0109`, low speed 1.5 Mbit/s. One standard
   boot-keyboard interface uses 8-byte input and three lock LEDs; interrupt
   interval is declared 24 ms. Linux enumeration succeeds. All four inventories
   are complete, with no full-speed specimen found and no P4 access during
   audit. Recommend CHERRY first and IBM second for captured P4 comparison,
   ranking interface simplicity then shorter declared polling interval. This
   does not predict a SETUP remedy or establish measured latency. Coordinate
   the Author's next physical attachment with an active bounded capture before
   drawing any new P4 enumeration/typing conclusion.

## Captured CHERRY P4 comparison — 2026-10-28

The Author connects the CHERRY after the P4 passive reader reports ready.
CHERRY fails at the same first SETUP stage as the original keyboard. HDMI and
P4 remain live. The connection window also contains a controller disconnect/
reacquisition. The Author confirms that only the keyboard cable was plugged;
the shared USB event's mechanism remains unresolved.

1. Preserved before/after service snapshots and a bounded passive capture on
   the unchanged installed candidate. Same P4 incarnation and mainboard input
   epoch; HDMI frames advance with faults/sequence/overbudget/underruns zero.
   No reset, flash, keys, guest invocation, startup/SD write or agent retry.
2. Twenty-two diagnostic records show address0/EP0, rootFULL, PRE1, MPS8,
   stage0/SETUP, HAL XCS_XACT. ENUM reports `[4:3] CHECK_SHORT_DEV_DESC FAILED`
   and port disabled/reset attempts1. These are logged control attempts, not
   evidence of 22 Author plug cycles. HID keyboard acquisition is never reached;
   there is no reason to request a typing trial on this failed enumeration.
3. The capture shows F310 input transfer code2, disconnect/invalidation, then
   valid enumeration/acquisition at address5 with its first report. Before the
   attachment F310 was address3. Final controller state is valid/fault0. The
   failed keyboard's parent hub is address4, previously address1; these address
   numbers are not physical socket labels, and no immediately preceding hub
   snapshot pins when that hub address changed. Do not infer a whole-P4 reset or
   identify the physical reason for that bus event from logs alone.
4. The agent requests capture stop after the Author reports connection; the
   maintained reader closes with exit0. Captured bytes and hashes, acquisition
   lines, status snapshots and wall-clock collection bounds are retained in the
   local bench record. The configured 300 s limit bounds collection only and
   does not authorize recovery or replay.
5. Establish whether the Author also touched F310, a USB hub or other cable
   while connecting CHERRY (resolved below). Then choose the next experiment:
   a further model control or actual failed-SETUP register/wire inspection. Two
   distinct standard keyboards failing before HID strengthens a common P4
   low-speed-path hypothesis; it does not prove a universal incompatibility,
   a particular host register defect or an electrical fault.
6. The Author clarifies that only the keyboard cable was plugged. Preserve that
   observation with the capture: the controller disappearance/reacquisition is
   an additional symptom of this keyboard-only attachment, not an operator
   controller replug. It does not establish a physical hub reset or power fault.

### Shared USB event follow-up

1. Against pinned ESP-IDF 5.5.5 `b774170ff46c393eeb5e495ea37936038d3f4f4f`,
   `components/usb/hub.c:root_port_handle_events` handles root disconnection,
   root error and overcurrent through the same device-removal branch. Current
   retained logs cannot distinguish which root event, if any, occurred.
2. `components/usb/ext_port.c:handle_disable` and
   `components/usb/hub.c:hub_port_reset` scope ordinary downstream failure/
   reset handling to the selected parent hub/port. That inspected child-failure
   path does not itself request a reset or removal of the sibling F310.
3. Project `vdp/video/extender/input/controller/usb_host.hpp:event` sets
   `gone_` on the matching USB host DEV_GONE event; `run` then calls `remove`,
   producing the observed DISCONNECTED line. Its generic input-failure code2
   does not itself set `gone_` or reset the hub. Code2 is a project diagnostic
   category for any non-completed input transfer, not the underlying USB
   transfer status. The latter was not retained and must not be inferred.
4. F310 reacquisition is logged before the first captured LS SETUP failure.
   Investigate the shared host/hub lifecycle rather than assigning that prior
   controller loss to the later keyboard-error cleanup. Event/log ordering
   still does not prove a physical mechanism.
5. The next bounded diagnostic should retain the exact root event, hub/device
   removal identity, downstream connection/enable/power status and actual
   controller transfer status, alongside the planned failed-SETUP hardware
   register snapshot. Publish outside ISR/locks; preserve existing timing,
   transfer actions and display guard. Do not select speculative power, clock,
   reset-delay or IRQ-affinity changes from this evidence. No new build,
   installation, reset or physical retry was performed for this source review.
