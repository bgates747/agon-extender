# Mainboard SD transfers through P4

The production runner stages new inputs once and collects the declared reports.
It also reads the entire installed foreground listener and startup batch each
time it starts that listener. A FLASH install or restore adds another whole-file
read of the FLASH utility. These reads occur even when the job touches none of
the three files. Reuse verified companion identities and keep the ordinary
UART upload and report path.

## Route and measured cost

Bulk SD data travels Pi5 ↔ P4 over HTTP and P4 ↔ eZ80 over the Extender
hardware UART. P4 spools bytes on its own card; EMOS's foreground listener
performs I/O on the Agon card. Agon FLASH's eZ80 → mainboard VDP firmware
stream and the ESP32 USB programmer are separate links. FLASH's SD input CRC
is computed on the Agon and reported as text. [P4 worker](../../../vdp/video/extender/storage/fast/engine.hpp#L113) ·
[SD guide](../../mainboard-sd.md) · [FLASH observer](../../../scripts/olimex_vdp_ota.py#L209)

The UART worker carries at most 212 file bytes per WRITE and 216 per READ and
waits for the local reply. The staged client requires the expected final
record count (4 + ceil(bytes/212) PUT, 2 + ceil(bytes/216) GET) and rejects
evidence of a PARLIO carrier. Empty files use control records only. The Pi
submits one staged job per file and polls P4 via HTTP every 250 ms. Polls,
carrier-admission HELLO, final status, and journal writes carry no bulk file
bytes. The older direct client uses one host HTTP request and durable journal
advance per UART record. Pending HTTP 202/503 adds a 40 ms wait. This accounts
for the slow behavior when custom callers use direct file I/O. Retain local
ACKs, boot/job binding, final counts and no replay of uncertain transfers.
Keep ordinary UART checksums disabled. [Staged client](../../../scripts/sdcard_staged.py#L88) ·
[Direct polling](../../../scripts/sdcard.py#L74)

Matched November 27 comparison, same installed stack and card. Times are Pi
elapsed seconds. The P4's inner interval includes SD work, so these are
not wire-only measurements. Worst staged time first.

| Bytes | Direction | Staged, s | Direct, s | Speedup |
| ---: | --- | ---: | ---: | ---: |
| 1,100,000 | GET | 49.277 | 276.953 | 5.62× |
| 1,100,000 | PUT | 44.998 | 281.132 | 6.25× |
| 65,537 | PUT | 3.918 | 17.402 | 4.44× |
| 65,537 | GET | 3.475 | 16.410 | 4.72× |

See [retained comparison](../REMOTE-009/UART-THROUGHPUT-INVESTIGATION.md) and
`agents/remote009/uart-rerun-r01/{direct,staged}-{65537,1100000}-{put,get}.timing.json`.
Individual values below are `host_elapsed_s` from staged terminal journals
(`last.result` after release), before surrounding listener startup and teardown.
The runner watchdog is 60 s + ceil(bytes/8,000) per PUT and 300 s per staged
GET, with a separate aggregate phase bound. These are stop bounds, not expected
durations. The multiple receipt files for one transfer ID describe one transfer.

## Commissioned transfer ledger

| Caller and operation | Direction, size and frequency | Justification and disposition |
| --- | --- | --- |
| `stage()` / `stage_uart()`, fixture executable, input asset or optional fixture script | Pi → Agon SD, one activated PUT per unique manifest path (0–32 MiB per file), normally one stage per job. The 8,182-byte production smoke PUT took 2.373 s. | Keep uploads for missing required inputs. The host pin, fresh-path STAT and terminal byte/carrier checks identify the intended transfer. A reverse read can only be justified where the transfer itself is the test. Named arms have distinct directories, so even identical file hashes get multiple PUTs when the manifest names distinct destinations. An admitted shared read-only asset path may avoid this, subject to fixture isolation. Otherwise use an approved PC-staged card for large duplicate sets. |
| `stage()`, ordinary VDP/VDPlet candidate | Pi → Agon SD, one raw app per job, maximum 1,310,720 B. The 1,118,288-byte VDPL-054 baseline PUT took 49.622 s. | Keep if the candidate is absent. The pinned source and UART receipt identify upload; FLASH on-card CRC verifies the resulting file before write. Retained local `stage-file-*.bin` comes from the Pi input rather than a reread from SD. |
| `stage()`, standard VDPlet restore or prior-standard rollback | A STAT success body of five bytes (type and length), zero firmware payload PUTs/GETs when the matching initial verified receipt exists. | Keep. Reuse the qualified copy and compare FLASH's on-card CRC. Missing/bad metadata stops the run. |
| `stage()`, FLASH restore absent from the standard/rollback pin map | Pi → Agon SD, one additional raw app up to the same slot capacity per job. | Justified for an explicit different restore identity. Commission repeated restores onto a durable versioned card path. State why the existing recovery files do not apply rather than blindly re-uploading a known standard. |
| `provision()`, initial deployment of a standard or rollback | PUT then GET once for each new Agon SD copy, compared byte for byte on the Pi. Two physical PUTs in 90.581 s, two corresponding GETs in 92.768 s. Each direction carried 2,234,432 bytes for both releases combined. | Keep initial verification and publish receipt. Already receipted images receive metadata checks only. The explicit interrupted-initial-deployment flag applies only to one unrecorded image. A new transfer after recorded verification requires a documented cause. |
| `uart_listener()`, `/autoexec.txt` | Agon SD → Pi, entire 45 bytes per listener startup; 0.319–0.474 s in retained runs. | An exact small startup check can be justified before a reset or after a card change. STAT alone cannot detect a same-sized change. Reuse the proof across otherwise unchanged phases. |
| `uart_listener()`, `/emos/sdserve.bin` | Agon SD → Pi, entire 26,127 bytes per listener startup; 1.371–1.374 s in retained runs. | This proves exact content beyond HELLO. Reuse an initial verified companion receipt with STAT, HELLO/liveness and explicit invalidation on tool/card changes or suspected corruption. Retain the one-time content proof. |
| `check_updater()` in `olimex_vdp_ota.replace()`, `/mos/flash.bin` | Agon SD → Pi, entire 15,624 bytes before **each** FLASH install and restore, including a recovery restore. VDPL-054 GETs took 0.849/0.852 s. It starts `uart_listener()`, so its two companion GETs also run. | A version banner alone does not authenticate its bytes. Verify the updater once for a particular commissioned card, bind its recorded receipt and check metadata plus the expected banner, prompt and CRC. Repeat only with cause. Offboard evidence already pins the updater and skips the listener. |
| `invoke()` / `collect_results()`, fixture report | Agon SD → Pi, one staged GET per declared report, staged spool bound 32 MiB. Named reports are required nonempty. Smoke result was 20 B in 0.577 s. | Keep the bytes required for analysis. Use a bounded metric report when it is the whole oracle. For intentionally large raw captures, collect once, use explicit deferred report retrieval, or admit approved PC retrieval. A separate USB transcript is not an SD GET. |
| `emos_install_inputs()` / `stage()`, ROMs and post-write SAVE/EXIT orchestration | Pi → Agon SD, 2 × 131,072 B per EMOS-changing job plus two small text batches. The batches launch SAVE and start the listener after it returns. | The candidate must reach FLASH. The standard EMOS restore still has no reusable SD pin in this runner. Commission a retained restore copy in the same way as VDPlet if that route is operationally suitable. Keep the ordering in the short batch. |
| `firmware(...,"emos")`, SAVE then `sd-rom-readback` | Agon SD → Pi, 131,072 B per installed-ROM read, 262,144 B per pair, with a new listener and its 26,172 companion bytes each time. FLASH writes first, then fresh input admits SAVE. | This verifies the physical ROM including padding. An input file CRC cannot prove it. Prefer a bounded digest computed over installed ROM on the Agon and returned as metadata if the address, exact size and code executing the check are qualified. Until then reserve full bytes for independent exact qualification or a documented diagnosis. |
| Post-P4 programming or adapter `Bench.cli()` | P4 firmware upload/read uses USB. The following CLI probe starts an SD listener and sends both companion files once on the P4↔Agon UART. Other callers of this method incur the same 26,172 B. | Use a fresh nonce MOS witness for CLI readiness. When SD readiness also matters, HELLO and STAT are appropriate on an admitted listener. Offboard branch already uses the nonce with zero file bytes. |
| Offboard stage and `--defer-results` | Offboard stage consumes pinned host records and performs zero automatic P4 SD transfers, including installed updater verification. It keeps SD reports for physical collection. Online stage with `--defer-results` moves its normal inputs, then leaves result files on SD after RUN. | Keep when appropriate for a large packet or carrier failure. A PC's initial comparison of a physically inserted SD card is not a serial transfer. Preserve original result/token bindings for later import and validation. |
| `verify_mos()`, `handback()`, `preload`, `enter-cwd`, status, STAT, MKDIR, LIST and staged EXIT | Zero SD-file contents. `preload` asks the eZ80 to LOAD directly from local SD into local RAM. Commands, small responses and serial observations still travel. | Keep the checks for prompt, directory, idle state and closed ports. Never use marker-only success where a separate result needs validation. |
| Ordinary `recover()` | No default report replay or extra SD dump. Performs normal restore transfers only for a proved outstanding changed component. | Keep restoration and preserve first failure evidence. Accept original stage and prior completed transfers as recorded. No automatic PUT/GET after a failed transfer. |

The companion reads total **26,172 bytes per listener**, and the updater check
totals **41,796 bytes**. One ordinary VDPlet arm (stage, install, collect,
restore) therefore returns **135,936 bytes** of unchanged tools and startup
before any test report. In the production-only smoke, these four GETs cost
**52,344 bytes and 3.497 s** by their receipts, compared with an 8,182-byte PUT
and 20-byte result. The stopped VDPL-054 baseline's stage, install and
recovery restore yielded **109,764 ancillary bytes in 7.088 s** across eight
GETs. Its failed RUN never reached collection. Evidence from
`agents/remote009/staged-uart-cutover-r01/operations`,
`vdpl054-olimex-v014/evidence/baseline`, and
`agents/vdplet-014-olimex-promotion/card-cache-r01/provision`.

Source: [stage and EMOS file generation](../../../scripts/olimex_bench.py#L435) ·
[listener and CLI helpers](../../../scripts/olimex_bench.py#L364) ·
[report collection](../../../scripts/olimex_bench.py#L850) ·
[EMOS write verification](../../../scripts/olimex_bench.py#L619) ·
[recovery](../../../scripts/olimex_bench.py#L942) ·
[provisioning](../../../scripts/olimex_vdp_cache.py#L20) · [SD receipts](../../../production/olimex-sd-firmware.json)

## Other callable routes and fallbacks

| Entry points reviewed | Payload and disposition |
| --- | --- |
| Direct `sdcard.py get`, `put --fast`, checked `put`, and `copy` | GET reads one complete file in 216-byte fragments. Fast PUT sends one copy in 212-byte fragments. Checked PUT GETs the entire staged `.p17part` and, if activated, the complete final file; it also uses transport checksums. COPY is Pi-buffered GET + PUT even for two paths on the same card; checked COPY adds both rereads. Restrict direct to metadata or explicitly commissioned compatibility/diagnosis. A verified card-local COPY would avoid both payload directions. |
| Direct `resume`, `recover inspect/restore/abandon/cleanup`, activate/cancel, move/remove | A resumed READ returns at most one 216-byte pending fragment. Other operations send metadata and control descriptors. Restoring the backup renames it locally on SD; cleanup can read its local contents without sending them to the Pi. GET a backup or partial only when the actual bytes are needed for archival or diagnosis. |
| Staged `resume`, `status`, `discard` | Resume can finish downloading an existing P4 spool over HTTP. It does not launch a second Agon UART READ. Completed delivered results are reused. Status/discard send control only. |
| Runner schema 1, schema 2, schema 3 explicit parallel | Current commissioned CLI refuses all three historical routes before hardware access. Schema 1's direct UART stage GETs any pre-existing payload, archives an old result by GET, PUTs missing files, then GETs staged inputs in full. Schema 2 stages by PARLIO but uses direct UART for collection and installed ROM retrieval. Historical schema-3 PARLIO stages/collects by PARLIO but remaining CLI and non-UART EMOS verification branches can use direct UART. Do not re-enable as an automatic fallback. |
| FSIM `utilities/f060-owner/olimex_full_flight.py`, `olimex_stock_startup.py`, `olimex_full_flight_recovery.py` | The first two GET `/mos/flash.bin` through the direct `Bench.listener` before staging. That wrapper also GETs the preserved files. Programmer paths call `Bench.cli()` after paired restart. Recovery STATs and GETs any original `summary.txt` and `state.bin` through the direct client. Preserve their genuine report payloads and migrate future authorized uses to staged UART. Apply common companion receipt and CLI-witness rules instead of special-case rereads. |
| Nurples current `docs/tasks/EARTH-001/pose/run-suite-r02.py` with `olimex-suite-r02.json` | Wrapper checks unchanged production, calls the pinned shared runner and resets once per arm. Its reset uses control and fresh boot/keyboard metadata, zero files. Nine named executables total 1,224,853 B of PUTs in one stage; nine distinct fixture reports GET once each (POSE.BIN or POSECOST.BIN). Validator consumes its existing report and USB transcript locally. The common listener opens once for stage and once per collection, implying 261,720 B of repeated companion GETs, assuming all arms complete. The reports are the measured data, so keep them and remove the repeated tool downloads. |
| Nurples Earth partial-stage adapters `retry.py` and `stage-last-three.py`; retained Sprite `scroll01/bench/standard` and `pair08` | Job-local artifacts show already-approved UART retries of only missing/failed assets and historical paired candidate and restore PUTs. Sprite's mode-20 B1 failed on the extra restore PUT before FLASH. Prefer current reusable SD restore, retain the already completed files and avoid re-running all staging to correct a single failed operation. |
| VDPlet `tools/fsim_bench_runner.py`, `vdpl020_bench_runner.py`; Sprite `scroll01/bench/standard/batch.py` | FSIM's historical wrapper sends each required executable, config, or asset via the P4 worker expecting PARLIO and uses UART only for capability and directory metadata. VDPL-020 legacy callback requests two real result files; its retained evidence checker only reads local files. Sprite's batch selects UART and delegates stage, install, draw, restore, handback to the shared runner once per manifest, then scores the local result and capture. Neither analysis step adds a wire GET. |
| BENCH-025 branch `96deebe7`, `olimex_reports.py` | Archives an original result once, uses STAT for freshness and initial exact-path deletion, and may GET the report again only after an interrupted delete intent when a same-size file remains. That conditional reread verifies ownership before deletion. The candidate's physical route requires PARLIO. Its PC import performs no serial transfer. Not today's commissioned runner. |
| `flash_firmware_commit.py` exact-commit development helper | EMOS path does a direct fast PUT of candidate, whole staged candidate GET, verification-batch PUT and GET, then full installed 131,072-byte ROM GET. Remove the staged-candidate reread in favor of FLASH input CRC and stop reverse-reading deterministic small batches when metadata suffices. Keep correct proof of installed ROM separately. Its P4 branch uses P4 programmer USB. |
| `qualification/run.py`, `lifecycle.py` and wrappers | SD smoke intentionally round-trips a 106-byte commit/hash payload to test the carrier itself. The raw-SD fixture, launch script, mode-query/restore and cleanup batches all use direct PUT + full GET; result files GET once. Cleanup uses full GET to detect a surviving file; STAT can answer this. Startup GETs are small. Exact qualification can SAVE and GET 131,072 bytes of already installed ROM, and a `.p17bak` may be archived before deleting it. Replace routine re-verification with metadata or real fixture oracles; preserve actual backup/test payloads whose bytes matter. |
| `qualification/render_load.py`, `render_modes.py`; historical `qualify_sdcard.py`, `qualify_sd_keyboard.py`, `qualify_keyboard.py`, `run_hello_demo.py` | Retained routines PUT/GET resident programs/assets and command batches, GET raw performance/failure reports and backups, or use checked direct transfers explicitly to test transaction integrity. Some write or use startup to launch, which is outside current commissioned operation. Technical evidence only until separately commissioned. The separate `qualification/performance.py` physical entry points raise immediately, so there is no live payload on that route. |
| `p4sd.py`, P4-local storage, development automatic WebDAV and application transfers | P4-local port 8080 transfers between Pi/P4 via HTTP, with no Agon UART hop. Automatic port 8081 and application SEND/RECEIVE are development paired profiles that do move files between P4 and Agon. They do not provide a commissioned UART fallback. |

References: [direct file API](../../../scripts/sdcard.py#L127) ·
[staged resume](../../../scripts/sdcard_staged.py#L152) ·
[exact-commit helper](../../../scripts/flash_firmware_commit.py#L184) ·
[qualification lifecycle](../../../qualification/lifecycle.py#L123) ·
[qualification SD smoke and raw execution](../../../qualification/run.py#L314) ·
[tool entry-point index](../../../scripts/README.md) ·
[P4-local HTTP](../../../scripts/p4sd.py)

## Review decisions

1. Record tool provisioning receipts for the foreground listener, FLASH utility
   and card identity. Reuse those receipts across a known unchanged interval.
   Define invalidation on card/tool write, replacement, contradictory metadata,
   wrong banner/CRC or credible corruption evidence. Use STATUS, HELLO, the
   five-byte STAT and MOS nonce for capability/liveness. These values still
   cannot establish the contents of an unauthenticated same-sized file.
2. Adopt reusable EMOS restore staging separately from replacing installed-ROM
   verification. Validate exact address/length and trust boundary of any on-Agon
   ROM digest before making it routine. Preserve the recovery procedure when
   the candidate cannot boot.
3. For repeated arms, account for duplicate bytes by file hash. A pinned
   shared read-only asset bound to the current card is useful only when fixture
   semantics permit it. Use approved offboard staging/extraction for deliberate
   large workloads. GET an original report once if the host needs the bytes.
   Retain full checks where transfer fidelity is the experiment or exact
   archive/diagnosis evidence is explicitly needed.
4. Align the general tool index, ordinary SD guide, and historical qualifications.
   Their older development and checked/direct recipes must not read as today's
   normal transfer procedure. The commissioned guide and carrier receipts govern
   current work.
