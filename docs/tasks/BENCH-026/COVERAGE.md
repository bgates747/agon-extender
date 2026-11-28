# Olimex procedure and caller coverage

The commissioned runner is only one of several paths into the bench. This
inventory expands the actual sparse checkout, follows its documented fallback
and component dependencies, and records separately commissioned callers
found in recent packets. It identifies paths that can hide a full transfer
behind a name such as “verify,” “handback,” or “recover.” See the
[transfer ledgers](../BENCH-026.md) for payload costs and dispositions.

## Evidence boundary

- Live sparse checkout at inspection: `4fc1ac7c91379f975b170d6b713c64bc3673e902`.
  Published correction: `9a57534ea207422a714b44d8bf3931932cb5c985`, the audit
  branch's source parent. Their only differences were the observer, the guide's
  formatting-mismatch continuation paragraph, and its regression test.
  Transfer implementation and firmware pins were the same.
- `git ls-tree -r --name-only 4fc1ac7c -- <sparse-paths>` expands to **45 files**.
  All 45 appear below. The second table follows linked maintained files and
  fallback commands. The third table audits available recent independent
  packets and identifies where an older receipt or operator revision governs.
- A source entry can establish possible I/O. A manifest and matching
  start/terminal or payload receipt establish what its specific run actually
  attempted. No live agent or device was probed. Machine-local paths and
  identifiers stay in their retained receipts. Historical snapshots outside
  the selected paths and recent task families were not individually replayed
  or certified. The scheduler does not maintain a registry of every
  job-local launcher, so unseen operator scripts remain an explicit gap.

## Expanded sparse checkout

| File | Entry point or authority | Serial or file effect |
|---|---|---|
| `.codex/config.toml` | Tool-review policy | Host authorization rules only. |
| `.gitignore` | Local checkout selection hygiene | No I/O. |
| `AGENTS.md` | Routes operators to commissioned guide and local evidence | No I/O. |
| `docs/bench-reset.md` | Reset, admission and post-reset CLI procedure | USB RTS or Pi GPIO reset; a caller may separately start listener and fetch a witness; do not infer firmware transfer. |
| `docs/mos-recovery.md` | FLASH MOS for usable MOS; commissioned external WROOM/ZDI for nonbooting MOS | Full 128 KiB ROM recovery and proof. Historic P4 ZDI explicitly excluded. |
| `docs/mos-recovery/LICENSE.agon-recovery.txt` | Recovery diagram license | No I/O. |
| `docs/mos-recovery/PROVENANCE.md` | Recovery wiring provenance | No I/O. |
| `docs/mos-recovery/console8_zdi.png` | WROOM reference diagram | No I/O. |
| `docs/mos-recovery/zdi.png` | ZDI pinout diagram | No I/O. |
| `docs/olimex-firmware-standard.json` | Exact app, listener, P4 and EMOS identities | Local pins only; which bytes the runner may send is selected elsewhere. |
| `docs/operations/olimex-bench/AUTHORING.md` | Build, manifests, stage/run, offboard, deferred collection | Defines UART fixtures, raw FLASH candidate, SD CRC and separate USB verification. Offboard proof replaces file staging only. |
| `docs/operations/olimex-bench/README.md` | Checkout through check-in, required restore and recovery | Canonical active UART-only and mainboard FLASH-only limits. Mainboard whole-app USB readback remains specified. |
| `docs/operations/olimex-bench/example/Makefile` | Build sample fixture | Local compilation. |
| `docs/operations/olimex-bench/example/job.example.json` | Sample fixture manifest | Describes guest upload and one report download; no transfer on preflight. |
| `docs/operations/olimex-bench/example/src/main.c` | Sample guest | Writes its report to local Agon SD and emits a command-correlated completion line; the runner moves the report. |
| `docs/operations/olimex-bench/sparse-paths.txt` | Checkout list | No I/O to bench. |
| `docs/procedures/bench-completion.md` | Supervisor evidence, failure notice and detached Pi service | Child argv determines payload; supervisor and chat wake-up move no serial file. Requires independent changed-byte proof without prescribing a carrier itself. |
| `docs/procedures/test-appliances.md` | Preparation, explicit invocation, mode settling and restoration | Workflow limits; fixture-specific input/result identities come from the manifest. |
| `docs/procedures/test-execution.md` | Preparation, invocation, collection authority | No transfer by itself. Owner commands may stage or collect only when authorized. |
| `docs/qualification/bench-constraints.md` | Limits on input, completion and production/test separation | Treat its historical UART capture cases as controls, not permission to run a transfer. |
| `docs/qualification/capture-failure-protocol.md` | Preserve traces; reruns require bounded disposition | USB serial evidence may be captured locally; no automatic artifact transfer. |
| `docs/sd-layout.md` | Card ownership and versioned recovery paths | Path organization, not a transfer. |
| `docs/serial-monitor.md` | Passive serial capture and observable MOS/boot limits | USB UART text/log data to Pi; capture written locally. No SD or flash read. |
| `production/README.md` | Release, archive and qualification links | Owner releases contain artifacts already retained on host. Rechecking them is local. |
| `production/bundles/olimex-parlio-v0.3.0/bundle.yaml` | Immutable P4, EMOS, listener and host tool provenance | Historical carrier qualification and exact pins; policy and current software checkout determine actual carrier. |
| `production/companions/olimex-mainboard-vdplet-v0.1.3-alpha.yaml` | Rollback app identity | Existing rollback reuses retained bytes. |
| `production/companions/olimex-mainboard-vdplet-v0.1.4-alpha.yaml` | Current VDPlet image, package and smoke evidence | Current app proof and release pin; no transfer by itself. |
| `production/current.yaml` | Current production selection | Local selector. |
| `production/olimex-bench-firmware.md` | Owner install/restore/recovery SD maintenance | New versioned SD image gets one PUT/full byte-compare GET; published prior receipt avoids repeats and metadata suffices in routine checks. |
| `production/olimex-sd-firmware.json` | Current-card initial verification references | No device I/O. Can reuse only for the recorded card and exact file. |
| `scripts/bench_process.py` | Execute, join, verify and classify child | Receipt files and host process group; no serial I/O of its own. |
| `scripts/keyboard.py` | P4 HTTP keyboard RPC | Keyboard command data and admission metadata. The downstream keyboard route does not carry a file. |
| `scripts/olimex_bench.py` | Root physical phase CLI | Stage, collect, optional preserved-file GETs, EMOS SAVE+GET and firmware dispatch. Offboard and defer variants have separate behavior. |
| `scripts/olimex_cli.py` | Passive MOS observer | Receives serial command echoes, prompt and result/diagnostic text. Writes a local raw trace. |
| `scripts/olimex_flash.py` | Classic ESP32 programming helper and ROM class dispatch | Legacy mainboard writer, read/write regions and selector gate. Standard CLI blocks the old writer; ordinary verification imports its ROM entry helper. |
| `scripts/olimex_operator_ready.py` | Read-only checkout/source-chat check | Local files and app-server metadata. No bench file or serial I/O. |
| `scripts/olimex_p4_app.py` | P4 app install/restore and paired reboot | P4 USB programmer write/reads; reboot through serial control and separate boot observation. |
| `scripts/olimex_vdp_cache.py` | Initial standard-image provisioning and exceptional unrecorded deployment continuation | P4-staged UART PUT/GET only for unrecorded newly deployed standard images. Matching existing verification uses metadata. |
| `scripts/olimex_vdp_ota.py` | Ordinary FLASH VDP and independent proof | Updater SD GET plus passive serial CRC capture; Agon writes over onboard UART and Pi reads partition, selector and app over mainboard USB. |
| `scripts/p4_boot_guard.py` | Parse the P4 boot prefix | No serial port or file transfer itself; caller captures. |
| `scripts/passive_serial.py` | Open and close a Linux port with joined line controls | Passive byte capture by caller; no erase, reset toggle, upload, or download of its own. |
| `scripts/reset_agon.py` | SSH/GPIO reset plus optional P4 HTTP admission poll | Control, no serial file; some callers subsequently use a listener for witness. |
| `scripts/reset_agon_usb.py` | USB adapter identity; RTS hold/pulse/release | Control and optional HTTP admission poll; intentionally sends no serial payload. |
| `scripts/sdcard.py` | Direct P4 HTTP-to-EMOS record client | Can move complete SD files, including legacy checked compatibility. In normal staged path supplies metadata, checksum-free listener checks and EXIT. The retained direct listener uses it for preserved-file GETs and any payloads selected by the caller. |
| `scripts/sdcard_staged.py` | Whole-file HTTP request to P4 spool; P4 exchanges records with EMOS | Normal bulk UART carrier with operation/job evidence. Parallel and direct compatibility routes are not fallbacks for a commissioned UART phase. |

Source links: [sparse list](../../operations/olimex-bench/sparse-paths.txt),
[operator](../../operations/olimex-bench/README.md),
[authoring](../../operations/olimex-bench/AUTHORING.md),
[runner](../../../scripts/olimex_bench.py),
[host process evidence](../../procedures/bench-completion.md).

## Linked and alternate entry points outside the sparse selection

| Procedure, file or helper | Boundary and finding |
|---|---|
| [Procedure index](../../procedures/README.md), [Extender handbook](../../README.md), [host tool index](../../../scripts/README.md) | Direct current operators to the sparse commissioning guide. Current host index still calls `sdcard_staged.py` development and cites the original parallel trial. Installed transport capability, release archive and allowed bench policy are separate. |
| [Mainboard SD operating guide](../../mainboard-sd.md), [foreground protocol](../../protocols/mainboard-sd.md), [staged protocol](../../protocols/mainboard-sd-staged.md), [host/tool pins](../../mainboard-sd-tools.json) | Guide opens with checksum-free production PARLIO and shows a `--require-parallel` PUT and GET. A later section gives the current `--require-uart` path. The commissioned procedure supersedes the opening recipe for live work. Mark the old examples historical or require the present authorization at point of use. |
| [P4 local SD guide](../../p4-sd.md), [p4sd.py](../../../scripts/p4sd.py), [staged WebDAV design](../../protocols/staged-webdav.md) | P4's own card HTTP on port 8080 does not cross an Agon UART. Candidate WebDAV on port 8081 and application-initiated service would move Agon-card content on the paired P4/eZ80 link; neither is a routine successor or fallback for the foreground bench runner. |
| [Installation](../../installing.md), [rollback](../../procedures/rollback.md), [verify_installation.py](../../../scripts/verify_installation.py), [package_installation.py](../../../scripts/package_installation.py) | Installation guide's retained DevKit spends USB bandwidth on factory write/verification and optionally reads EMOS through SAVE; package verification is local. Rollback says to preserve mutable data and reuse pre-existing owner binaries; RB-02 still tells operators to read back the staged EMOS image before FLASH. The current runner skips that pre-write full SD comparison for schema 3, then retrieves changed ROM after FLASH. Resolve this documentation collision rather than adding an extra GET to current jobs. |
| [Olimex firmware references](../../procedures/olimex-firmware.md) | Delegates current Olimex write/restore identity to the bench guide and owner selection. The Alexe/Console8 release example is a different path. |
| [Qualification package](../../../qualification/README.md), [qualification/lifecycle.py](../../../qualification/lifecycle.py), [qualification/run.py](../../../qualification/run.py), [qualification/render_load.py](../../../qualification/render_load.py), [qualification/render_modes.py](../../../qualification/render_modes.py), [qualification/performance.py](../../../qualification/performance.py) | Independently maintained qualification tools, outside the standard runner. The lifecycle uses direct fast uploads followed by GETs in stage-new-file, repeatedly reads startup, fetches ROM proof and stages small command files. Render load measures paired upload/readback where selected, while render modes can write startup. These are separate commissioning surfaces. A current Olimex package must reconcile obsolete direct mirror reads, startup mutations, and restore handling before use. |
| [Render load](../../testing/render-load.md), [resident rendering](../../testing/resident-render-suite.md), [game timing](../../testing/game-timing.md) | Some retained rendering experiments use local-card deferred report collection. Retained resident/render modes recipes refer to temporary autoexec behavior that current appliance rules do not permit. Retained game-timing runner has an old EXEC/listener setup and is explicitly reuse-blocked. No route is implied by the presence of captured results. |
| [Current keyboard guide](../../remote-keyboard.md), [flash_firmware_commit.py](../../../scripts/flash_firmware_commit.py), [p4_flash_remote.py](../../../scripts/p4_flash_remote.py) | Keyboard guide links an alternate maintained commit installer outside current phases. EMOS variant uses direct serial SD: upload the staged ROM, download all staged bytes again, PUT and reread a small verification batch, then GET 131,072 bytes from the installed ROM SAVE. P4 variant uses SCP from workstation to Pi, then **backs up 16,777,216 flash bytes by default** over P4 USB before programming a factory image. Keep whole-device backup only for an explicitly justified overwrite/recovery, not an app-only checkout. The app-only standard runner preserves other partitions. |
| [MOS recovery](../../mos-recovery.md), [prepare_mos_recovery.py](../../../scripts/prepare_mos_recovery.py), [mos_recovery_console.py](../../../scripts/mos_recovery_console.py) | Current separately commissioned fallback is WROOM; exact programmer build and readout must be identified per incident. These named helpers target the older P4 recovery console and generate/parse its pinned payload and hex before/after dumps. Their presence and the old host-tool-index label confer no current P4 qualification. Never silently use them on the WROOM. |
| [Reset bridge](../../../scripts/reset_bridge.py), [serial_monitor.py](../../../scripts/serial_monitor.py), [screen_text.py](../../../scripts/screen_text.py) | Browser reset routes to fixed GPIO or USB modem-control argv. Serial monitor captures bounded logs over USB. Screen-text HTTP reads P4-derived text instead of serial file content. Existing docs mention a separate listener/read/EXIT witness for some resets; standard `verify-mos` does not start it, so account for each selected caller separately. |
| [bench_firmware_check.py](../../../scripts/bench_firmware_check.py), [bench_job.py](../../../scripts/bench_job.py), [hardware_validation.py](../../../scripts/hardware_validation.py), [run_hardware_regression.py](../../../scripts/run_hardware_regression.py), [run_regression_suite.py](../../../scripts/run_regression_suite.py), [run_scroll_suite.py](../../../scripts/run_scroll_suite.py), [collect_render_qualification.py](../../../scripts/collect_render_qualification.py) | Inventory comparison, host supervision or offline/review entry points. A user-selected subprocess/adapter can move data; its argv must be audited. Scrolling generator's live adapter is not itself commissioned by this procedure. Report copies made from an already copied card root are host-local. |
| [qualify_sdcard.py](../../../scripts/qualify_sdcard.py), [qualify_sd_keyboard.py](../../../scripts/qualify_sd_keyboard.py), [qualify_keyboard.py](../../../scripts/qualify_keyboard.py), `prepare_sd_headless.py`, `qualify_sd_headless.py` | Retained qualification surface. Intentional PUT/GET and `.p17part`/`.p17bak` reads exercise exact transfer, rollback, activation and input interlocks. Older listener LOAD/RUN fixture and checked checksum modes are unsuitable for routine current operation. Headless pair is a model, not a physical UART measurement. |
| `capture_general_poll.py`, `capture_uart_flow.py`, `capture_uart_roundtrip.py`, `capture_visible_text.py`, `capture_keyboard.py`, `prepare_uart_forward.py`, `prepare_uart_roundtrip.py`, `prepare_uart_flow.py`, `prepare_general_poll.py`, `prepare_visible_text.py`, `prepare_usb_cli.py`, `prepare_usb_keyboard.py`, `native_bootstrap.py`, `modem_bw.py`, `modem_rx_control.py`, `modem_sniffer.py`, `net009_pi_uart.py` | Retained controlled diagnostics or preparation. Capture tools may receive bounded logs/records; these filenames do not license an image transfer. The modem and network fixtures have their own test transports. Treat old fixed pin/output locations and listener/bootstrap behavior as historical unless their owner commissions an exact current packet. See the [host tool index](../../../scripts/README.md). |
| `agon-vdplet/tools/notify_bench_completion.py`, `agon-dev-env/scripts/pi_chat.py`, `agon-dev-env/scripts/codex_rpc.py` | Actual long-phase service wrapper and socket wake-up. Launches selected worker, saves its returned status, then sends a message over the existing host socket. No additional device command or serial file in the wrapper. |
| `agon-flash` v1.9 updater, production P4 storage worker `vdp/video/extender/storage/fast/`, pinned EMOS listener and mainboard receiver | Physical dependencies, not separate Pi launchers. P4's HTTP spool is not a serial hop. The normal eZ80 FLASH-to-VDP send is the actual firmware write payload. Ordinary CRC comparison covers the SD file already present, not the independent installed bytes. |
| `docs/procedures/{p4-canary-r02,p4-canary-r03,frame-service-qualification-r01,frame-service-qualification-r02,frame-service-qualification-r03,browser-video-qualification-r01,port-008-forward-qualification-r01,mainboard-sd-qualification-r01}.md` | Historical or candidate recipes in the [procedure index](../../procedures/README.md). Full reads/writes on a particular historical build are recorded evidence, not an instruction to run the operation today. |

## Operators and job-local scripts

The current/recent discovery window was November 25–27, 2026 local time.
Starts, job packets and wrappers were inspected in the named bench/packet
subtrees for VDPlet, Sprites, Nurples and FSIM. Locate these host-retained
paths from the named repository root. Source HEADs at inspection were VDPlet
`20951bc`, Sprites `b8b0e16`, Nurples `46c61c5` and FSIM `41ec83d`.
Evidence generated under those repositories can pin a different exact
source or checkout. Extender's earlier provisioning and recovery receipts
were retained as route-specific evidence. No phases were replayed.

| Entry inspected | Binding and effect |
|---|---|
| VDPlet `build/vdpl054-olimex-v014/phase-packet.json` and `baseline.json` / `candidate.json` | Exact phase argv calls the standard runner. Preserve the failed baseline observer receipt and the separate restore receipt. Run UART capture and named `SCANLINE.TXT` collection serve different proofs. `build_pair.py` and `native_guard.py` prepare or inspect local builds. |
| VDPlet `build/releases/v0.1.4-alpha/default-promotion/phase-packet.json`; Extender `agents/vdplet-014-olimex-promotion/handback.py`; VDPlet `tools/vdpl020_bench_runner.py` | Standard staged UART and FLASH for install and any rollback. Promotion handback binds the existing exact candidate receipt and saved report files. Hashing and judging those files is host-only. Handback proves MOS and idle state without recopying either app or report. |
| VDPlet `build/vdpl059-olimex01/oryx-sd-stage-r01/manifest.json` and verification; `earth-offboard-r01` evidence | Verified physical SD staging. No staged PUT or GET from the Pi in that path. Both FLASH writes and USB selected-app verification still apply. The mounted host card is a separate later collection route. |
| VDPlet `tools/notify_bench_completion.py`, `tools/verify_vdf_bench_bundle.py`, `tools/fsim_bench_runner.py` | Notify only launches the explicit worker; bundle verification is local. FSIM job orchestration depends on the invocation and can use an explicitly selected transfer backend. FLY-08 selects its own helper below. |
| Sprites `build/vdpl062/packed21/bench/{prepare.py,launch.sh,batch.sh}` and `packed22/bench/{prepare.py,launch.sh,batch.sh}` | Prepare emits pinned arm files; launch uses the Pi service. Batch calls `docs/tasks/VDPL-062/olimex_batch.py`. Separate arm jobs can each own install and restore. Count firmware and USB proofs per arm, not per service. |
| Sprites `docs/tasks/VDPL-062/olimex_batch.py` | Hashes readiness and inputs; calls canonical CLI for each physical phase and checks captured reports locally. Offboard and deferred flags propagate to the runner. No direct payload call inside the wrapper. |
| Sprites `build/vdpl062/scroll01/bench/standard/{batch.py,launch.sh,launch-r02.sh,continue-r02.sh,continue-reverse-stock.sh,continue-pair-r02-stock.sh,launch-reverse-stock.sh,launch-pair-r02-stock.sh}` | Standard arm launch and continuation family. Older `batch.py` prepares UART jobs and invokes runner phases. Preserve actual per-phase receipts. `scroll01/bench/uart-batch.py` and other ad hoc scripts remain historical inputs. |
| Sprites `build/vdpl062/pair08-r02/bench/continue-verified.sh`; `docs/tasks/VDPL-062/olimex_candidate_continue.py` | Binds an already FLASH-written candidate, admits its verification, then named run, restore/rollback and handback. Uses original stage evidence. Verify calls the full USB table/selector/app reader below; a failed read does not itself require another FLASH write. |
| Sprites `docs/tasks/VDPL-062/olimex_restore_verify.py` | Recovery of an already completed FLASH restore. Binds previous write, stage, original operation and inventory; gets 4,096-byte table, 8,192-byte selector and exact app extent over mainboard USB. “Verify” here is a full transfer. |
| Sprites `docs/tasks/VDPL-062/olimex_stage_handback.py` | Binds failed stage and held custody, verifies inventory, runs new MOS and idle handback. No firmware input or full-proof reread. |
| Nurples `.build/earth-pose-r03/bench-uart-01/r03-production.json` and its stage/smoke supervisor records; `.build/earth-pose-r02/bench-uart-01/r02-production.json` | Stage and smoke for R03 both invoked shared `olimex_bench.py`; terminal logs each exited 0. No second job-local acquisition path in those phase argv. Transfer quantities come from the manifests and stage/result receipts. |
| Extender `agents/earth-001/pose-uart/{pose_uart.py,golem_matched.py,native_uart.py,cost_uart.py}` | Earlier separately scoped Nurples adapters. Pose directly PUTs fixture inputs and GETs reports using the direct client inside a custom Bench integration. Golem and native wrap that route. Cost directly downloads its report for decoding. This family demonstrates the limits of a policy check in the standard CLI alone. |
| Nurples `.build/earth-jit-256/auto-pair/{set01-pair.py,vdplet-reverse.py,stock-pair.py,stock-reverse.py}` | Earlier exploratory code directly calls the Bench listener API for updater checks, staging and report preservation; some select an ordinary or job-local OTA phase. Exact old packet governs; these are historical comparators, not current fallbacks. |
| FSIM `utilities/f060-owner/build/p083-full-flight08/{OPERATOR.md,prepare-and-alert.sh,job.json}`; `utilities/f060-owner/watched_flight.py` | Queued at inspection. Extra blank-slot guard reads **196,608 bytes (0x30000)** of mainboard USB store and 4,096 bytes of table before INSTALL, then restarts and witnesses MOS. This transfer is additional to normal candidate and restore application proofs. It prevents overwriting an already occupied slot. A qualified digest of the exact erased range could supply the same gate. |
| FSIM `utilities/f060-owner/{olimex_stock_startup.py,olimex_full_flight.py,olimex_full_flight_recovery.py,check_c8_flash.py}` | Historical OLX-06/FLY-07 packet. Stock worker reads table, selector, app extents and **1,441,792 bytes (0x160000)** of store; cleanup can reread it after a selected erase. Full-flight delegates to this worker, stages the fixture and collects reports. Recovery fetches stopped-run reports and invokes only the commissioned programmer steps. The wide store proof belonged to that store-writing contract. |
| Extender `agents/vdplet-014-olimex-promotion/card-cache-r01`, `agents/bench-023`, `agents/olimex-stock-recovery` | Current one-time SD byte receipts, USB trial and bounded recovery records. The latter two explain failure risk and earlier read extents. The older recipes cannot substitute for the current FLASH-only rule. |

## Discrepancies and leverage points

1. **Different policy at different entry points.** The standard CLI calls
   `require_commissioned_policy` after manifest binding. The general
   `preflight()` and direct `Bench` methods can still exercise older schema
   and PARLIO behavior from custom adapters. Some active wrappers add their
   own gate, including Sprite's `olimex_batch.py`. Historical wrappers remain
   executable. The CLI's tests cannot certify those paths.
2. **The older operating and tool guides are easy to mistake for current
   instructions.** They lead with PARLIO, older EMOS rereads or an alternate
   commit installer. Clarify these points where operators choose a tool, and
   distinguish owner factory recovery from ordinary application programming.
3. **A “read-only” phase may reopen the unreliable USB programmer and transfer
   the complete app or store.** Changing the receipt format to a compact
   device proof affects standard restore/candidate verification, promotion,
   Sprite continuations and FSIM guards. Distinguish the pinned source hash,
   a device-reported digest and a path to retained actual read bytes.
4. **A no-file-service packet may still have two USB readbacks.** Offboard
   staging and deferred collection remove the stated Agon SD transfers.
   Ordinary FLASH and its post-write USB verification remain. Standalone
   `verify-mos` supplies keyboard control and passive serial evidence, rather
   than installed image proof or check-in.
5. **Full backups have a narrower justification than full verification.**
   Protect unknown bytes that a proposed write would erase. Routine app-only
   programming keeps unrelated regions and has exact retained restore inputs.
   Require a scoped evidence reason before using a factory/wide-backup route.
