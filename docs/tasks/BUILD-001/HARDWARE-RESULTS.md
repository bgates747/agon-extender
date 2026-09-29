# BUILD-001 hardware-equivalence results

## B01-HR01 — 2026-09-28 native-console attempt

State: failed safely; candidate testing stopped and selected production P4
firmware restored.

| Field | Result |
|---|---|
| Candidate | `build001-bd733100-console-lcd`, source `bd7331005e69d298c724559c534f3fe19c9be6e6` |
| Candidate application | 1,801,168 bytes; SHA-256 `a2ebff97a91c006afa9a6bb57a5343740d2687e1d910f1dcb5bf96cb03fa56dc` |
| P4 | Expected ESP32-P4 USB identity; chip revision v1.3 |
| Flash result | Bootloader, partition table, initial OTA data and application written from the generated native flash arguments. Each region passed an independent pre-boot digest comparison. |
| Exact boot identity | Project `agon_extender`; application version `bd733100`; ELF prefix `68d1f3a15`; ESP-IDF v5.5.5. |
| Terminal failure | Repeatable assertion before application initialization completed: `sdio_mempool_create sdio_drv.c:258 (buf_mp_g)`. The P4 entered a software-reset loop and never brought up HTTP, keyboard, video or LCD services. |
| Candidate tests not run | Legacy/ExCom transport, LCD, browser, SD, mode0 fixture, mode20 grid and manual games. These results are disposed for this attempt, not failed functional comparisons. |
| Rollback | Selected production `uart-excom-console-r55-b2026-09-25-02-18-28Z` restored from `extender-installation-r02`; all four flash regions independently matched their recorded bytes before boot. |
| Recovered state | One ordinary Agon reset established a fresh ready/neutral Extender keyboard admission. The accepted Legacy spoken failure cue was invoked, then `BUILD-001 FAIL: P4 BOOT LOOP` was printed so the alert player could not overwrite it. |

The first independent candidate verification found that initial OTA data had
changed after the candidate booted. Because that partition is mutable at boot,
the operator rewrote only the generated initial OTA sector without booting,
verified it while the P4 remained in the loader, and then reset the P4. That
produced explicit successful comparisons for all four generated regions; it did
not change or conceal the subsequent boot assertion.

## Procedure conformance finding

B01-HR02 [x] The run did not establish B01-H02 as written before flashing. The
frozen procedure names EMOS v0.1.19, while the current machine-local bench record
identifies EMOS v0.1.23. The operator verified admitted input and a recoverable
CLI but failed to reconcile the EMOS identity conflict. This is a procedural
failure and prevents calling the overall hardware procedure conforming.

The P4 assertion occurs during ESP-IDF startup before EMOS transport, video,
keyboard or network services initialize. The EMOS-version discrepancy therefore
does not explain or waive the observed candidate boot failure. Before retrying
hardware, BUILD-001 must identify and repair the native-build startup defect,
repeat host validation, and replace or amend the reviewed procedure so its
precondition names the intentionally selected EMOS version.

## Disposition

B01-HR03 [x] Stop this candidate run at the boot-loop gate. Do not proceed to
fixtures or manual games and do not count any functional-equivalence item as
tested.

B01-HR04 [x] Superseded as the immediate next action by the Author's pre-LCD
baseline amendment. Preserve the combined candidate's ELF, map, configuration,
dependency lock and assertion evidence; do not repair that LCD-inclusive
candidate before the audit. If the native pre-LCD build reproduces the same
assertion, diagnose it there as a BUILD-001 migration defect.

B01-HR05 [x] Prepare a new hardware procedure for the immutable pre-LCD native
candidate with EMOS v0.1.23, exact replacement identity and unchanged rollback
boundary before another flash authorization request.

## B01-HR06 — pre-LCD boot result

B01-HR06 [x] Candidate `build001-595286dd-console-prelcd` reproduced the exact
same startup failure without any selected LCD source, definition or dependency.
Serial identified the expected clean pre-LCD application and then repeatedly
asserted at `sdio_mempool_create sdio_drv.c:258 (buf_mp_g)`. This rules out the
LCD implementation as a necessary cause of the boot loop. The defect belongs to
BUILD-001's native ESP-IDF dependency/configuration/initialization boundary and
must be diagnosed there before another candidate is prepared.

B01-HR07 [x] Compare the native and working hybrid r61 `esp_hosted`, remote-Wi-Fi
and SDIO component selection, linker retention, initialization registration and
Kconfig closure. Explain why native whole-archive linkage reaches
`sdio_mempool_create` without its required pool, then implement the smallest
build-boundary correction with host evidence. Do not alter product behavior or
reintroduce LCD while resolving this migration defect.

The native linker correctly honored ESP-Hosted 2.12.12's `WHOLE_ARCHIVE`
property and therefore retained its constructor. That constructor started the
unused remote-Wi-Fi SDIO transport before `app_main` and requested a DMA-capable
mempool which could not be allocated from early internal RAM. The working
hybrid link omitted the otherwise-unreferenced constructor; Extender uses the
P4's wired Ethernet and did not provide remote Wi-Fi as product behavior.
Commit `eadc2925e436754f5b7e0beddf088b01ded504ba` explicitly disables
`ESP_WIFI_REMOTE_ENABLED` and `ESP_HOSTED_ENABLED` in the maintained P4
configuration. Host validation passed, the Hosted constructor and failing SDIO
allocator disappeared from the link map, and the application shrank from
1,721,632 to 1,491,072 bytes.

B01-HR08 [x] Flash and independently compare corrected candidate
`build001-eadc2925-wired-prelcd`, then run a bounded boot and HTTP canary. All
four regions matched before boot. Serial identified app `eadc2925`, ELF prefix
`a90568060`, ESP-IDF v5.5.5, USB keyboard readiness, Ethernet DHCP address
`192.168.0.16`, and `HTTP browser service ready`, with no assertion or reboot.
Two HTTP checks returned `200 OK`; a second reset reproduced the clean boot.
The corrected candidate remains installed. This passes the migration boot
defect only; broader B01-06 functional equivalence remains open.

## B01-HR09 — first functional-equivalence attempt

B01-HR09 [x] Candidate `build001-d17cae79-console-prelcd` passed independent
flash-region comparisons, booted without panic or reset, identified the expected
source and ESP-IDF v5.5.5, initialized USB keyboard and wired Ethernet, returned
HTTP 200, and passed Legacy-to-ExCom-to-Legacy text transport. The operator then
found TCP port 8081 refused an `OPTIONS` connection. Testing stopped before SD
or visual fixtures.

The retained r61 manifest proves `staged_webdav: true`; the native profile had
selected the service sources but left `AGON_EXTENDER_STAGED_WEBDAV` at its
source-safe default of zero. This is a BUILD-001 configuration-equivalence
defect, not a runtime WebDAV failure. The operator restored production r55 from
the verified rollback image, independently read back all 1,617,920 bytes at the
same SHA-256, confirmed its exact serial identity and HTTP 200, restored fresh
ready/neutral keyboard admission with one ordinary Agon reset, invoked the
spoken failure cue, and left `BUILD-001 FAIL: STAGED WEBDAV OMITTED` visible.
Production selection and SD contents were unchanged.

B01-HR10 [ ] Flash and qualify corrected candidate
`build001-e7b35fd5-console-prelcd` only after the Author accepts the amended
exact-candidate procedure. Host evidence proves the selected compile actions
carry `AGON_EXTENDER_STAGED_WEBDAV=1` and the isolated embedded page carries the
machine-local reset endpoint without tracking it.
