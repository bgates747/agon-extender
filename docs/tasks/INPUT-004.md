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
6. The Author subsequently reports that rewiring the direct USB adapter through
   the Extender harness breadboard produces a working keyboard. This is an
   Author observation, not a captured enumeration/typing qualification. F310
   hotplug does not work with the installed FS-only peripheral selection;
   restoring concurrent P4 USB acquisition remains unfinished.
7. On 2026-10-30 the Author requires a resident-logic audit alongside controller
   restoration: put as much controller logic as practical in the Agon
   application because eZ80 flash is scarce. The [bounded audit](INPUT-004/EMOS-CONTROLLER-AUDIT.md)
   records actual resident costs and relocation candidates. Target zero EMOS
   growth for P4 USB coexistence; do not couple that restoration to an
   unmeasured EMOS/API rewrite.

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
6. Before restoring the F310 alongside the direct-header keyboard, classify
   each controller duty as P4 acquisition, minimum EMOS transport, or Agon
   application logic. Audit existing duties too. Keep calibration, deadzones,
   mappings, repeats, gameplay decisions and presentation in application code.
   Preserve EMOS routing/UART ownership; moving logic does not admit direct
   application UART/GPIO access. Measure linked ROM changes before proposing
   any resident alteration, and account for existing consumer compatibility.

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
| I4-03 | Open | All four audited keyboards fail initial SETUP/XCS_XACT with FS root, PRE selected and MPS8. The register diagnostic confirms actual channel PRE=1 and the intended SETUP configuration. Actual wire behavior and cause remain unresolved. The separate CHERRY/F310 transient remains Author-deprioritized under I4-06. |
| I4-04 | Partially established | Initial SETUP failure followed the keyboard from parent hub1/port1 to hub1/port3. Linux subsequently identifies the Author-transferred specimen as `04d9:a088`, a Holtek vendor ID with no manufacturer/product strings. Retail brand/model and physical socket label remain unrecorded. |
| I4-05 | Model comparisons complete | All four keyboards enumerate on Linux at 1.5 Mbit/s with compatible boot-keyboard interfaces, but fail initial SETUP in captured P4 trials. Exact descriptors and each failing comparison are retained. Further model swapping is not the current diagnostic lead. |
| I4-06 | Author direction | Deprioritize the recovered controller transient and resume captured keyboard model comparisons on the unchanged firmware. Do not let speculative transient diagnostics delay the next attachment trial. |
| I4-07 | Established for captured sample | Actual channel/host settings agree with explicit pinned SDK assignments. No register toggle or timing remedy is justified by this capture. Keyboard enumeration and typing still fail. |
| I4-08 | Open source contract | Establish the integrated HS-UTMI frame-clock/HFIR contract in FS-only host mode and the exact FC06 bit2 preamble polarity from primary P4/PHY documentation. A count of60000 or an ambiguous field label does not establish a defect. |
| I4-09 | Minimal reproduction established | The pinned USB-only image reproduces CHECK_SHORT_DEV_DESC failure while F310 enumerates at full speed. No keyboard HID admission. Minimal evidence does not identify the failed SETUP/DATA/STATUS stage or a vendor defect. The subsequent official candidate assessment is recorded under I4-10. |
| I4-10 | Initial-descriptor compatibility assessment complete | Official USB host1.6.0 admits IDF5.5.5 but its public FSLS option requires an absent HAL capability. No targeted initial-descriptor correction was identified, so that speculative comparison was deferred. I4-15 separately selects the complete component for the established dual-root dependency. Exact source/newer-SDK findings remain in [the assessment](INPUT-004/USB-COMPATIBILITY.md). |
| I4-11 | Deferred by Author | Author prefers Olimex as the first vendor contact because P4-PC adds the hub/connector path, then defers vendor contact entirely in favor of the direct full-speed header experiment. The Espressif-addressed draft and frozen review archive remain unsubmitted historical preparation; do not submit them or silently relabel the frozen archive. |
| I4-12 | Author-selected experiment; wiring researched | Try a keyboard through the P4-PC's exposed full-speed USB signals, bypassing the onboard hub. Author reports a successful directly wired keyboard on the P4-DevKit; this is a useful control, not P4-PC qualification. Rev C EXT1 maps +5V=2, GND=3, GPIO26/D-=4, GPIO27/D+=6; pin1 is +3.3V and pin5 is ESP_EN. Firmware controller selection and simultaneous use of onboard F310 remain implementation/qualification gates. No physical rewiring, build or flash was performed during wiring research. |
| I4-14 | Rejected incomplete implementation | The initial dual-PHY/map3 backport omitted IDF5.5.5's single-root hub limitation. The physical candidate admitted only the keyboard and crashed in HTTP readiness; exact keyboard-only P4 rollback is verified. No EMOS/mainboard VDP/startup change. |
| I4-13 | Author constraint; application extraction implemented offline | Minimize resident controller logic and prefer Agon application ownership. Restore concurrent USB acquisition on P4 without EMOS growth. The initial candidates/baseline remain in [the audit](INPUT-004/EMOS-CONTROLLER-AUDIT.md). The application extraction and matched reduced EMOS are implemented under [INPUT-005](INPUT-005.md), but have not been installed on this bench. |
| I4-15 | Selected offline correction | Replace only the USB host component with archive-pinned Espressif USB1.6.0, retaining SDK/PHY/HAL, silicon guards, HID and display. Keep the HS reset/EP0 task-log accommodations with complete source/linkage verification. Provide HTTP stack headroom and stop readiness checks on the first crash. Fresh Author foreground confirmation precedes physical installation; no coexistence pass is claimed. |

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
6. Root and installed HID keyboard acquisition source match. Public HID 1.2.1
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
6. Log interpretation gotcha: HID 1.2.1's `No HID device at USB port 2` prints
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

### Author reports electrostatic discharges at USB shields

1. The Author reports building up static and receiving several shocks on
   touching USB connector shields during connections/disconnections. The Author
   subsequently confirms shocks during earlier tests but none felt during the
   captured CHERRY connection. Absence of a felt shock does not exclude ESD;
   there is no direct ESD observation correlated with that captured failure.
   Treat ESD as a plausible confounder for the shared USB interruption, not a
   proven explanation for persistent initial-SETUP failures or damaged hardware.
2. Verified the clean read-only Olimex Rev C reference at
   `04032d68e5c727870f9d40beb9e37b7ab3a66916`. In
   [the board design](https://github.com/OLIMEX/ESP32-P4-PC/blob/04032d68e5c727870f9d40beb9e37b7ab3a66916/HARDWARE/ESP32-P4-PC-Rev.C/ESP32-P4-PC_Rev_C.kicad_pcb),
   footprints `USB_HOST1-2` and `USB_HOST3-4` each assign all four mechanical
   shield pads, number0, directly to net1/GND. This establishes design intent
   for circuit-ground bonding, not measured continuity or a verified earth
   reference for the installed bench. A grounded shield alone is not an ESD
   immunity qualification.
3. [Phidgets' manufacturer guidance](https://www.phidgets.com/docs/Improving_Phidgets_Hardware_Reliability#Static_Discharge)
   describes ESD disrupting USB communications and triggering detach/reattach.
   [TI's USB ESD application note](https://www.ti.com/lit/pdf/slva796), section4.2,
   explains why discharge routing/layout matter in addition to ground naming.
   These support the general mechanism; they do not diagnose this P4 board.
4. The CHERRY discharge-observation question is resolved above. For a future
   controlled comparison, reduce charge with proper
   ESD handling and retain any felt-discharge observation alongside root/hub
   diagnostics. Do not deliberately inject sparks, infer a protective-earth
   connection or perform a grounding/wiring change as part of this research.
   No bench operation, continuity measurement or electrical change occurred.
5. The Author considers the recovered controller disruption a potentially rare
   transient and requests the next captured keyboard connection. Preserve the
   evidence and hypotheses, but resume model comparisons rather than preparing
   a new transient-diagnostic firmware tranche. Next intended specimen is IBM
   NetVista; retain the installed candidate and ordinary passive capture path.

## Captured IBM NetVista P4 comparison — 2026-10-28

1. Under the Author's direction to continue model comparisons, started a fresh
   bounded passive reader on the unchanged P4 candidate and signalled ready.
   The Author connects the intended IBM keyboard and reports a large shock
   from the USB hub during this attachment. The electrical event was not
   instrumented; retain the observation without diagnosing its cause.
2. One captured LS control failure is address0/EP0, rootFULL/PRE1/MPS8,
   SETUP stage0/HAL XCS_XACT, followed by hub4/port3 short-descriptor failure
   and port disable. No HID acquisition or IBM VID/PID is reached on P4.
   The Author-selected specimen's identity is established by its preceding
   Linux audit, not by a successful P4 descriptor transfer.
3. P4 incarnation and mainboard input epoch remain unchanged. HDMI frames
   advance with zero faults/sequence errors/overbudget/underruns. F310 remains
   valid/fault0 with unchanged USB address5 and carrier session; no controller
   disconnect/reacquisition appears in this capture. Actual controller movement
   was not exercised. The shock did not reproduce the earlier logged bus loss.
4. Capture stops cleanly with exit0 after the Author reports connection. Retain
   before/after snapshots, raw log/hash, wall-clock collection bounds and the
   felt-shock observation. No reset, flash, input injection, guest invocation,
   startup/SD change or agent connection retry. Three different keyboards now
   fail initial SETUP; Logitech K120 remains for the next captured comparison.
   Preserve the Author's priority to test models rather than pursue the
   recovered controller transient.

## Captured Logitech K120 P4 comparison — 2026-10-28

1. The Author requests the monitor, then connects the intended K120 after
   capture ready. One LS control attempt fails initial SETUP/XCS_XACT, rootFULL,
   PRE1, MPS8, hub4/port3. No device VID/PID or HID keyboard admission is reached.
   Specimen identity comes from the Author-selected preceding Linux audit.
2. P4 incarnation and mainboard input epoch are unchanged. F310 remains
   valid/fault0 at address5 with the same carrier session and no captured
   disconnect. HDMI frames advance with zero faults/sequence errors/overbudget/
   underruns. Actual typing/controller movement was not requested on this
   failed enumeration. No shock was reported for this particular trial.
3. The passive reader closes with exit0. Preserve before/after snapshots, raw
   log/hash and host wall-clock bounds. No reset, flash, keys, application,
   startup/SD change or agent connection retry. All four keyboard model controls
   are complete and fail the same pre-HID stage. Continue with failed-SETUP
   hardware-register evidence rather than further unbounded model swaps;
   keep the recovered controller transient deprioritized as the Author directed.

## Failed-SETUP register diagnostic tranche — authorized 2026-10-28

The Author directs proceeding after all four keyboards fail the same stage.
The P4 will retain actual USB channel/host configuration and interrupt status
for the failed low-speed control transaction, rather than infer hardware state
from cached endpoint parameters. This is a diagnostic candidate, not a proposed
timing or signaling remedy. The recovered controller transient remains outside
this tranche.

1. Review pinned HCD/HAL/LL read semantics. Raw channel interrupt status must
   be copied before the HAL decoder clears it; inspect actual channel/host
   configuration through the pinned HAL handles. Select only safe scalar reads
   that answer the SETUP/PRE/clock/configuration question. No register writes,
   resets, retries, delay changes, allocation, logging or new locks in the ISR.
2. Gate predecode reads to active low-speed-via-hub control traffic. Retain only
   a failed transfer's detached snapshot in the existing per-pipe record, copy
   and consume it for the matching URB at task dequeue, then format after unlock.
   Record that reads add bounded ISR work and are sequential, not atomic wire
   observations. Do not turn a decoded transaction error into proof of absent
   ACK or electrical corruption.
3. Extend generated-code lifecycle checks with distinct hardware sentinels,
   destructive decoder simulation and later register mutation, proving capture
   order, gating, ownership and post-unlock publication. Preserve original USB
   actions and the complete derivative/source identity checks. Independently
   review the generated patch before an identified build.
4. Commit/publish the reviewed source and selectively apply only this tranche
   to a clean child of the installed matched composition. Build with unchanged
   display/controller/board/SDK/dependency inputs; independently compare complete
   source archives, configuration, generated units and actual link selection.
5. Refresh the app-only installer against exact new bytes and the current full
   backup, preflight actual CLI/unchanged startup, preserve expanded rollback
   sectors and independently verify the whole P4 readback. Keep EMOS/mainboard
   VDP/startup/SD contents unchanged. Verify new console, scanout, F310, input
   admission and actual CLI before announcing a staged capture test.
6. A keyboard left attached may produce a diagnostic during the verified P4
   initialization capture. Preserve that evidence without replaying hotplug or
   invoking a guest. Decode its registers only against the pinned definitions;
   otherwise stage a bounded capture and coordinate the next physical replug.
   No new transient-campaign work or production promotion is implied.

Prepared source: eight raw registers (`HCINT`, `HCCHAR`, `HCTSIZ`, `HCFG`,
`GUSBCFG`, `HFIR`, `HPRT`, UTMI `FC06`) plus frame before decoding, gated to LS
control. The generated HCD SHA-256 is
`c5eb6da09c15c16324e15aba65e97a596207019aa8fc20625991ae231d81dae7`.
Independent source review passes. All 32 focused host checks pass in 1.17 host
monotonic seconds; the new generated-handler harness covers 21 ISR/dequeue
cases including destructive decoder mutation and poisoned post-unlock state.
The private record grows from 8 to 44 bytes on 32-bit P4; nine MMIO reads and
larger local copies have unmeasured execution cost. Target compile/installation
and hardware interpretation remain separate gates.


Matched preparation: root source `996a80c0` and installed-composition child
`632d35c0` are committed and published. The child directly follows installed
`f00c5a05`; its four-file patch exactly matches the reviewed root delta while
preserving the matched validator's existing display options. Nine focused
matched-source tests pass, with no other build-input or selection changes.
The identified build is `indexed-hdmi-r14-b2026-10-28-22-35-11Z`; compilation and
final artifact/composition validation remain pending at this preparation gate.
A fresh actual CLI/unchanged startup preflight passes, with the listener exited
and temporary printer mirroring disabled. No hardware installation follows from
source-test success alone.


## Register diagnostic installed and initial SETUP captured — 2026-10-28

The P4 diagnostic is installed and the original keyboard failure is reproduced
with actual hardware registers retained. No keyboard remedy is established.
The low-speed/PRE selection is present in hardware, matching the driver's
software fields; the captured error still cannot distinguish absent response
from malformed signaling.

1. Build `indexed-hdmi-r14-b2026-10-28-22-35-11Z`, matched source `632d35c0`,
   passes native compilation/validation in 455.12 host monotonic seconds. The
   application is 1,778,560 bytes, SHA-256
   `ecf69e4b0276b91108d08d50e32315fc2ae93bc33d5ca6b2129b335c18566549`,
   448 bytes larger than installed `f00c5a05`. Independent review verifies all
   23 retained artifacts, both complete 5,524-file source inventories, unchanged
   selections and the intended USB compile/archive/ELF linkage.
2. All 1,853 compile actions match after exact path normalization except IDF's
   `esp_app_desc.c` generic `PROJECT_VER` metadata (`88293037` to `996a80c0`).
   That field follows the containing broad-root Git identity; the build manifest
   identifies actual matched source `632d35c0` and the Extender header embeds
   the exact build ID above. Do not infer source provenance from `PROJECT_VER`.
   The rebuilt bootloader differs only in compile timestamp/image integrity
   fields and is not flashed; actual incoming bootloader bytes are preserved.
3. Fresh actual CLI/startup preflight passes. The saved full incoming P4 image
   matches the device before reuse as rollback. App-only write at `0x20000`,
   independent app verification and complete 16 MiB readback pass; every byte
   outside written sectors `[0x20000,0x1d3000)` is unchanged. The outgoing full
   readback SHA-256 is
   `ffb16a6833e9e8028cbd1a4f15bd35d59c640ed6ca07e6e99cddc36f2caa171a`.
   Installation takes 212.51 host monotonic seconds, excluding the separate
   post-installation command check. Exact rollback bytes remain retained.
4. The new P4 startup/USB host, attached F310 and HDMI initialization pass before
   Agon reset is released. Actual Legacy CLI commands and a read-only fast2
   startup download then pass, with listener EXIT and printer mirroring OFF
   independently verified in 7.35 host monotonic seconds. Startup remains the
   same 108 bytes; EMOS, mainboard VDP and SD files are unchanged. No guest or
   test application is invoked. All serial readers and reset holds are closed.
5. The attached Author-selected K120 fails once at hub port3 during ordinary
   P4 initialization. Initial SETUP/stage0, address0/EP0, MPS8 and HAL XCS_XACT
   match the preceding model comparisons. No physical replug is required.
   The raw 7,273-byte boot capture SHA-256 is
   `a97fee1ce3b20b4a224f432907a22f048b8909bd8dd912e28043e655e10c93c0`.
6. Final read-only status shows advancing HDMI frames and zero fault/sequence/
   overbudget/underrun counts. F310 native USB remains valid/fault0; actual
   controller movement is not exercised. Extender input is admitted and neutral;
   SD listener is offline/idle. These checks establish bounded installation and
   command readiness, not keyboard typing or broader hotplug qualification.

| Retained register | Raw value | Supported interpretation |
|---|---|---|
| HCINT | `0x00001002` | Channel halted plus excessive transaction error; no unique cause |
| HCCHAR | `0x00020008` | Address0/EP0, OUT/control, MPS8, actual low-speed/PRE bit1 |
| HCTSIZ | `0x000002ff` | Descriptor-DMA scheduling255, three-descriptor encoding, PID field0 |
| HCFG | `0x06800204` | FS/LS-only and descriptor DMA enabled |
| GUSBCFG | `0x2000140d` | Host mode, HS UTMI selection, 16-bit interface, timeout calibration5 |
| HFIR | `0x0000ea60` | Raw frame-interval count60000; not itself a duration measurement |
| HPRT | `0x00021405` | Enabled/powered full-speed root hub link, no active overcurrent bit |
| UTMI.FC06 | `0x00000049` | LS parallel/keepalive enabled, preamble-related bit2 clear; polarity unresolved |

The frame sample is373 and HS PHY type3. Register reads are sequential samples
at interrupt service, not USB wire observations. Neither PRE selection nor an
absent captured ACK bit proves what the downstream keyboard received or sent.
Do not toggle the ambiguously documented UTMI preamble bit, change clocks or
increase delays solely from these register values. Further source/clock/PRE
interpretation is offline; no additional hardware change is queued.

Machine-local build, composition, independent-review, installer and CLI receipts,
raw capture and decoded register JSON remain under `agents/input004` and are
indexed by the current local bench record. This remains an experimental
diagnostic installation; production selection and acceptance status are unchanged.


### Primary-reference boundary for I4-08

The inspected [Espressif ESP32-P4 Technical Reference Manual](https://documentation.espressif.com/esp32-p4_technical_reference_manual_en.pdf#page=3169)
is Pre-release v0.7, with creation metadata dated 2026-08-20; retained PDF SHA-256
`622fe9625d19cf00bd7aa49e65f0b5dd6ef2197f83cb7a88b4405078d6a957d4`.
Section52.5, printed/PDF page3169, withholds comprehensive USB OTG register
specifications under the IP provider's NDA and directs individual register
questions to Espressif Technical Support. The inspected manual and bounded
primary-source searches do not resolve the integrated HS-UTMI HFIR clock contract
or FC06 bit2 polarity. This is a limit of the located evidence, not proof that
no vendor document can answer either question.

Extender must obtain the precise vendor/IP contract or independent discriminating
evidence before selecting a clock/preamble change. No support message, speculative
register toggle or additional hardware operation follows from this result. The
retained public PDF/text and the bounded source-research notes are under the
ignored task evidence directory. Actual keyboard enumeration remains the next
functional gate after an evidence-supported remedy.


## Minimal native USB baseline — authorized 2026-10-28

The Author approves a USB-only P4 comparison, leaving the keyboard and F310
attached. Extender will temporarily install a pinned Espressif HID-host example
adapted only for board bring-up, explicit serial invocation, bounded evidence
and the required FS/LS-only root-reset backport, then restore the exact verified
Extender application. Success supplies a working baseline for integration
comparisons; repeated initial SETUP failure supplies a compact reproducer, not
proof of a vendor defect.

1. Initial checkout is clean; no pending dirt requires a safety commit. Publish
   this scope before the diagnostic build/install. The native fixture is
   `input004-usb-minimal-r01`, with a fresh identified UTC build and exact source
   archive/hash/commit. It remains outside production and ordinary P4 profiles.
2. Pin ESP-IDF5.5.5/b774170f and HID 1.2.1 to the installed retained component
   bytes. Preserve board hub reset, selected HS peripheral, hub support, USB
   configuration, core1 USB installation/IRQ ownership, silicon revision bounds,
   app offset and partition table. Remove Extender display/network/controller/
   Agon transport services. Do not call direct Agon registers or bypass EMOS.
3. Use only the required FS/LS root-reset derivative; retain its exact original
   source hash and generated hash. The installed cache/diagnostic/USBH logging
   derivatives are intentionally absent. Judge descriptor enumeration and HID
   admission first; stock non-control IN cache behavior may independently affect
   later reports. Preserve this difference in the comparison record.
4. P4 startup remains inert until the Pi explicitly sends serial START. Create
   event ownership before USB starts, print exact build/start/end identities and
   counts, and bound acquisition to20 seconds or admitted keyboard plus5 clean
   seconds. A serial STOP may end the acquisition after the host observes a
   definitive SDK enumeration failure. An app timeout is inconclusive by itself.
   Do not use GPIO0 as a guessed quit button or start/retry work after reset.
5. Finish source/configuration/compiled-linkage review and identify the actual
   application bytes before flashing. Freshly prove actual MOS CLI and unchanged
   setup-only startup. Keep verified full rollback and exact sector bytes; hold
   Agon reset across minimal P4 installation, invocation and restoration.
6. Use app-only writes at0x20000 with independent app/full readback comparisons.
   Leave bootloader, partitions, NVS/OTA, EMOS, mainboard VDP, startup and SD
   contents unchanged. No operator replug, Agon application or rendering test is
   part of this experiment. Capture serial evidence and record host/target clocks
   separately; a duration estimate does not authorize resets or replay.
7. Restore `indexed-hdmi-r14-b2026-10-28-22-35-11Z`, application SHA-256
   `ecf69e4b0276b91108d08d50e32315fc2ae93bc33d5ca6b2129b335c18566549`,
   independently verify application/full readback and new P4 startup before
   releasing Agon. Then prove fresh admission, actual MOS CLI, unchanged startup,
   listener exit and mirror-OFF. Any uncertain write remains journaled with Agon
   held for explicit root reconciliation; never blindly retry or release.
8. Record enumeration, actual typing/report exercise and restoration separately.
   No automatic vendor message, speculative register change, SDK upgrade,
   additional hardware change or production promotion follows from the result.


Minimal-build preparation notes: USB Serial/JTAG's VFS console requires an
explicit `vfs` component in the fixture's main dependency list. Native compilation
then succeeds. The final configuration checker records three bounded differences:
FreeRTOS's task-function wrapper disappears with removed coredump/debug support;
no coredump component is selected; the experimental external-port reset-count
symbol disappears but pinned `ext_port.c` falls back to the same value1. Other
selected effective USB/core/cache/clock/silicon/console settings must agree.
These differences are retained comparison limits, not complete configuration
equality. HID 1.2.1 is independently verified against the vendor package aggregate
`74b9c84cd2921a5e987f504c1713ca7819f7e8be80565e5253e9e9c7e07ab881`;
the installed component is byte-identical, including its upstream disconnect
cleanup. No local HID patch is introduced or removed by this baseline.


## Minimal USB-only result — 2026-10-28

The keyboard's first descriptor request also fails in the USB-only P4 image.
F310 enumerates successfully at full speed on that image. The failure is thus
reproduced without Extender display, network, controller client or EMOS transport
services, yielding a compact baseline for vendor-stack comparisons. It does not
prove a silicon/SDK defect or determine the wire-level cause.

1. Final build `input004-usb-minimal-r01-b2026-10-29-00-05-23Z` uses committed
   source `4610e9672bdb420e554cef1326a6fea756426ede`. Its application is 289,184
   bytes, SHA-256
   `0e0d896847907dd43ce5231adeb83591730bdbdee09b912ea952a18b33907a3b`.
   Native build/validation passes in 179.53 host monotonic seconds. Independent
   review verifies actual compile/object/archive/link-map/ELF agreement, all
   manifest artifacts, pristine HID/USBH, the sole FSLS root-reset derivative
   and the documented effective-configuration exceptions.
2. Fresh actual MOS CLI/startup preflight passes in 8.86 host monotonic seconds.
   The incoming whole P4 flash matches its retained rollback image before reuse.
   Minimal app write/independent verification and full 16 MiB readback pass before
   START. Agon remains held throughout the native image and planned restoration.
   No mainboard/EMOS/startup/SD change, physical replug or Agon test invocation.
3. Exact inert ready/build/source receipts precede one explicit serial START.
   P4 confirms host IRQ allocation on core 1. The observer records F310
   `046d:c21d` enumerated at full speed. The ordinary SDK emits
   `Bad transfer status 1: CHECK_SHORT_DEV_DESC`, then request failure and hub-port
   disable. No keyboard device identity/HID admission or keyboard report follows.
4. After five observed seconds following the definite SDK failure, the host
   sends one STOP. The app emits one HOST_STOPPED terminal receipt with elapsed
   6,027,266 microseconds and keyboard_admitted=false; the host retains five
   additional clean seconds. This is controlled collection completion, not a
   keyboard pass, deadline expiration or measured enumeration latency. The
   `esp_timer` clock's physical calibration is not measured.
5. Raw serial capture is 5,180 bytes, SHA-256
   `92ac6466a4daa58bb8706df45a13a5b2a605a8ba951922a9e3a5546a1c37be9e`.
   Independent review confirms the raw capture/result counts and hash. Minimal
   HCD instrumentation deliberately has no stage/HAL/register snapshot, so this
   result cannot be labeled a newly proven SETUP0/XCS_XACT failure. The earlier
   full-application snapshot alone proves that earlier sample's stage.

| Observation | Installed Extender diagnostic baseline | Minimal USB-only image |
|---|---|---|
| Keyboard request | CHECK_SHORT_DEV_DESC fails | CHECK_SHORT_DEV_DESC fails |
| Exact failing USB stage | Captured SETUP0/XCS_XACT | Not captured |
| Keyboard HID admission | Absent | Absent |
| F310 | Native USB valid/fault0 | Full-speed enumeration; no XInput client |
| USB installation/IRQ core | 1 | 1 |
| ESP-IDF / HID | 5.5.5/b774170f; pristine HID 1.2.1 | Same pins |
| Extender display/network/EMOS services | Present | Absent |
| HCD / USBH derivatives | FSLS, cache/diagnostics, task logging | Sole FSLS root-reset backport |

The warning about no HID device at USB address2 concerns F310's vendor interface;
it is not evidence of another socket failure. Further offline work should assess
one official USB-host candidate's actual support for P4 revisions 100–199 and the
pinned IDF/PHY interfaces. Do not relax revision checks, change unknown registers
or automatically deploy another stack. Preserve this baseline and current
production selection. Exact restoration and final CLI handback are recorded
separately after verification.


### Exact restoration and completed handback

Run `INPUT-004-2026-10-29-00-11-58Z` completes its hardware transaction in 423.50
host monotonic seconds, including both flash installations/readbacks, native
acquisition and restored startup/admission. This is separate from compilation,
preflight and the subsequent 7.40-second actual CLI check. Fixture/full readback
retrieval takes 167.6 seconds; restored full readback takes 181.2 seconds. These are
host USB-flash transport durations, not P4 rendering or device-input performance.

After the controlled negative result, the host restores the exact incoming
sectors `[0x20000,0x1d3000)`, including the original app tail. Independent app
verification and full 16 MiB readback prove byte-for-byte equality to the incoming
image, SHA-256
`ffb16a6833e9e8028cbd1a4f15bd35d59c640ed6ca07e6e99cddc36f2caa171a`.
The exact original Extender app/build is active again; the minimal image is no
longer installed. P4 startup, HDMI/F310 readiness and then Agon admission pass
before actual Legacy MOS commands are checked. Unchanged 108-byte startup,
listener EXIT, printer mirror OFF and neutral input are verified. Final HDMI
frames advance with zero faults; F310 status remains valid/fault0 without an
operator movement exercise. All readers and reset holds are closed/released.
No mainboard firmware, EMOS, startup or SD write occurred. Both devices remain
attached, and no further hardware operation is queued. Retained machine-local
completion/readback/CLI evidence is indexed by the current bench record.

## Official USB candidate assessment — 2026-10-28

The Author directs commit/push of any dirt and continuation of the proposed
compatibility check. The checkout was already clean and published. Three bounded
independent source reviews assess the official USB host 1.6.0 package, actual
pre-v3 SDK support and the initial-control path. The [assessment](INPUT-004/USB-COMPATIBILITY.md)
records exact pins, feature limits, function comparisons and primary references.

1. USB 1.6.0 declares IDF >=5.5.3 and officially supports overriding the bundled
   IDF 5.x USB component. It still compiles against the selected SDK PHY/HAL.
   Its public FSLS option explicitly refuses the pinned SDK's absent configured
   HAL API. Do not fake the feature macro, suppress that refusal or widen the
   board's revision bounds.
2. The selected initial-request descriptor, PRE, execution, completion and
   EP0 callback functions remain byte-identical. The existing CTRL synchronization
   and completed-stage delay were already present. Broader scheduling/lifecycle
   changes can affect behavior, but no reviewed source change identifies a fix
   for the captured first request. A speculative native variant was not built.
3. The examined newer released SDKs retain explicit pre-v3 support, but the
   bounded HAL checks identify no released configured-HAL pair. Their detailed
   retrieval limits are retained. Current development HAL's FSLS restriction
   uses the same reset ordering already backported; no SDK migration is selected.
4. Retain the official package, exact-commit HCD/CMake cross-check, component
   inventory/digest and independent review under the ignored task evidence.
   Prepare [the report draft](INPUT-004/USB-REPRODUCER-DRAFT.md) from the existing
   minimal capture/source. No vendor contact or public attachment occurs.
5. This tranche performs offline research/documentation only: no bench access,
   new native build, flash, reset, input, SD/startup change or production promotion.
   Exact previously verified installed firmware and the negative baseline remain
   unchanged. I4-11 holds the next diagnostic choice and concrete prerequisites.

The internal source/evidence review archive contains the exact 11 tested source
files, 32 pristine HID files, original raw capture/result, current report drafts
and an inventory. Only two partition-filename strings are normalized in a
separately labeled SDK configuration export; the original configuration hash is
recorded. Archive metadata has no local owner/path identity. This is not a
standalone build or installer, and contains no firmware binary. The retained
50-member archive is 88,277 bytes, SHA-256
`78784a494c486004728c6bd87145a5d1bc09301e1c7014c22c74e5a74a7b9d85`.
Its internal location/packaging receipt remains in the ignored task evidence.
No external distribution is implied by preparing it.

## Author selects direct full-speed USB header experiment

The Author defers vendor contact and selects Discord's proposed direct keyboard
connection. A plain USB-A socket breakout can expose VBUS, D-, D+ and ground;
the P4 contains the full-speed PHY, so no external USB controller or level shifter
is required for this route. Breakout protection circuitry varies by product.

Read-only comparison of the manufacturer Rev C schematic and PCB at
`04032d68e5c727870f9d40beb9e37b7ab3a66916` independently verifies EXT1 pads2/3/4/6
as +5V/GND/GPIO26-D-/GPIO27-D+. Pad1 is square. This is the separate full-speed
controller, not a parallel connection to the hub's existing data pair.
[Manufacturer schematic](https://github.com/OLIMEX/ESP32-P4-PC/blob/04032d68e5c727870f9d40beb9e37b7ab3a66916/HARDWARE/ESP32-P4-PC-Rev.C/ESP32-P4-PC_Rev_C.pdf).
Espressif's [USB hardware guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32p4/schematic-checklist-esp32p4.html#usb)
confirms default FS D-/D+=GPIO26/27 and recommends22/33ohm series resistors near
the chip and connector-side USB ESD protection. No added pull-up/level shifter
is part of this host connection. Select the correct controller in a separately
identified firmware implementation before claiming input operation. Current
firmware, bench state, startup and SD remain unchanged by this research.

## Direct FS keyboard-only execution authorized

The Author reports the P4-PC wired and powered and directs a test. The controller
is deliberately disconnected to avoid interference. The DevKit breadboard was
used only as a wire-colour reference; do not infer a P4-PC power-rail connection
from that discussion. Green/white/red/black are D+/D-/VBUS/ground. This later
completed-wiring report supersedes the earlier unresolved contact counting for
the purpose of the authorized test; it is not an agent continuity measurement.

1. Preserve the exact installed matched display/transport composition. Prepare
   the explicit experimental `--usb-direct-fs` selection for P4-PC/p4-console,
   using the same IDF5.5.5 and HID1.2.1. Record source/build identities before
   installation; do not select root HEAD's different display implementation.
2. Pinned SDK `usb_host.h` specifies BIT1 (=2) for peripheral1. Its
   `soc/esp32p4/usb_dwc_periph.c` maps that FS controller to GPIO26/27.
   `usb_host.c` currently initializes one PHY, so do not select mask3 as a
   guessed way to retain both controllers. This trial does not service the HS
   hub/F310. Skip onboard-hub reset for this explicit selection.
3. Exclude `--usb-fsls-only`: it selects the HS workaround/diagnostics, not this
   separate FS peripheral. Leave SDK/HAL/PHY bytes and the board's physical
   mapping unchanged. Actual compiler definitions, preprocessed USB selection,
   linked source, partitions and pre-v3 bounds must match the recorded variant.
4. Fresh read-only CLI/startup preflight precedes app-only installation. Preserve
   verified incoming full-flash/sector rollback, assert Agon reset while P4 is
   replaced, independently verify app/full readback and P4 initialization, then
   release Agon and prove fresh input admission/actual CLI. No EMOS, mainboard
   VDP, startup or SD write. No automatic replay on uncertain effects.
5. Capture keyboard enumeration/HID admission separately from physical typing.
   On success leave the reviewed variant ready for Author typing; it remains
   experimental until bounded physical input tests and acceptance. If P4 startup
   or ordinary CLI fails, retain the diagnostic result and restore the exact
   verified original P4 application before ordinary handback. A healthy P4 with
   no detected keyboard may retain the direct variant during the still-active
   physical connection investigation; identify that state explicitly. This is no simultaneous-controller
   qualification, broader suite or production promotion.

### Direct FS trial result — 2026-10-28

The direct-FS driver starts normally, but keyboard connection/HID admission has
not been observed. No descriptor failure is logged either. This differs from the
earlier onboard-hub trial and does not establish an electrical or SDK cause.

1. Root source `c7919440` and exact matched P4 source
   `fd212503e34eb19761d59bc919f68bdda02b3954` are published. The latter changes
   only four controller-selection/build files relative to the installed source;
   all selected display/transport/board/configuration/dependency inputs match.
2. Build `indexed-hdmi-r14-b2026-10-29-02-35-19Z` passes native validation in
   613.82 host monotonic seconds. Application1,777,312bytes, SHA-256
   `cdef666761a767e2675c8f2b2b397d0cc3836961cef783555219b8cff0360e61`.
   Root verifies source archives, actual dependencies/compile flags and
   preprocessed host mask2 with hub reset absent. SDK HCD/USBH remain pristine.
   Embedded build/profile identity and manifest/archive source identity are
   separate, as in the baseline; no full matched source hash is claimed embedded.
3. Incoming whole flash freshly matches the retained rollback. App-only write,
   independent app verification and complete16MiB readback pass; bytes outside
   written app sectors remain unchanged. P4 initialization/direct-port banner/
   display pass before Agon release. No mainboard/EMOS/startup/SD writes.
4. Fresh admission and actual Legacy MOS CLI pass; startup remains the same
   108bytes, listener exits and printer mirroring is disabled. Controller is
   physically absent throughout, as requested. Physical typing was not tested.
5. Initial boot and an additional bounded15second passive capture show no
   keyboard connection/HID-ready indication or enumeration-error line. All
   readers and reset holds are closed. Keep the healthy direct variant for the
   active connection investigation; the original image/sector rollback remains
   retained. Obtain red-to-black VBUS voltage at the USB connection before
   attributing this result to signal wiring or driver behavior. Detailed
   machine-specific receipts remain under ignored task evidence.

## Keyboard/controller coexistence selected — 2026-10-30

The Author directs restoration of controller operation alongside the working
direct-header keyboard. [The bounded continuation](INPUT-004/COEXISTENCE-R01.md)
records the exact upstream dual-host patch, matched P4 composition, preservation
requirements and validation/deployment gates. This is P4 acquisition work;
EMOS/mainboard VDP/startup remain unchanged. The INPUT-005 application/EMOS
extraction stays a separately matched offline result until its own deployment
is selected. No existing simultaneous-device pass is claimed.
