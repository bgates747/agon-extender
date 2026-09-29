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
machine-local reset endpoint without tracking it. Its four flash inputs and
manifest are staged on the Pi with exact matching hashes; the rollback was
rechecked. The finite ignored runner, fast-transfer deployment flow, startup
restoration path and spoken terminal hooks are prepared and statically checked.
Mocked success and injected mid-run failure paths both restore the exact original
startup bytes and retain the expected terminal verdict.

On the authorized run, preflight passed against EMOS v0.1.23, ready/neutral
input, the Legacy CLI, fast listener and exact P4 USB identity. An initial
explicit flash-header override changed two bootloader regions (the mode byte and
image digest); the mandatory pre-boot comparison detected it. The P4 remained
in its loader while the operator rewrote only the bootloader with `keep`
parameters. All four reviewed regions then matched exactly before boot. Serial
identified source `e7b35fd5`, build ID `build001-e7b35fd5-console-prelcd`, ELF
prefix `887af158d`, ESP-IDF v5.5.5, USB keyboard readiness, wired DHCP and HTTP
readiness with no panic or restart. After one ordinary Agon reset, staged
WebDAV returned HTTP 200 on port 8081 and fresh EMOS admission became
ready/neutral. The finite detached equivalence suite was then launched; its
terminal result and Author visual review remain pending.

Preliminary suite invocations stopped before startup mutation on ordinary
runner setup omissions: the fixture directory was absent, directory creation
was assigned to services that could not complete it in the current state, and
the automatic and foreground SD responders were initially distinguished only
by an insufficient boolean readiness check. The corrected runner assigns
directory creation to the EMOS CLI, requires a new SD-service boot identity
before opening the fast client, closes its listener session on every exit path
and preserves only the concise corrective result rather than treating these
attempts as candidate failures.

The corrected finite run09 passed the automated functional sequence. It
verified HTTP and staged-WebDAV availability, entered ExCom, reset back through
a fresh Legacy admission, used fast foreground transfers to launch the mode-0
bars and mode-20 grid from startup-selected modes, captured both browser
framebuffers, exited each fixture and restored the original startup. The driver
completed in 82.21 seconds; its spoken success hook brought total detached job
duration to 105.29 seconds. Final input was ready/neutral and an independent
post-run readback matched the original 38 bytes at SHA-256
`7b500d81030020f893aee64338889efd21630f7db9a893d0919d1084a69bb3a5`.
The bars capture shows the expected black-red-green-blue-cyan-magenta-yellow-
white order and asymmetric edge markers. The grid capture shows A1 through H6
in order with all asymmetric corner markers.

The first human staging startup incorrectly retained `EMOS EXCOM`, so its web
pass could not simultaneously exercise the Legacy connector. After the route
was removed, the Author confirmed that the physical Legacy mode-0 output looked
correct. The Author's direct fullscreen web capture also matches the fixture.
Its upper-right yellow marker is a solid 27-by-27 component (729 of 729 pixels),
disposing a later apparent one-pixel indentation as a viewing-presentation
artifact rather than retained framebuffer evidence. The corrected Legacy-only
mode-20 run was then separately staged without `EMOS EXCOM`; the Author
confirmed its physical display was correct. The original 38-byte startup was
restored and independently read back before a fresh reset. The deliberately
deferred manual Nurples test then passed its application-owned low-resolution
splash-to-mode20 transition, complete graphics, gameplay/restart behavior and
clean Escape return in Legacy. Its observed half speed is the selected test
binary's documented two-vblank/approximately-30-Hz behavior.

The identical executable failed its late mode20 transition in ExCom and retained
the same 320-by-240 geometry seen during the LCD experiment. Escape and an
explicit return to Legacy recovered normal admitted input. This proves that LCD
code is not necessary for the failure, but it does not yet distinguish inherited
hybrid-r61 behavior from a native-build regression. B01-HR10 therefore remains
open pending one exact hybrid-r61 control and native-candidate restoration.

B01-HR11 [ ] Subject to Author authorization, flash retained hybrid image
`uart-excom-console-r61-b2026-09-28-03-12-48Z` at factory SHA-256
`f794a8bba96f9afbfc1dae6eaa4554eb676880d76ffe74bda97bbebc7e160fea`,
repeat the same ExCom `/test/nurples/nurples.bin` late-switch observation, then
restore and independently verify native candidate
`build001-e7b35fd5-console-prelcd`. Do not repair the late-mode20 defect in
BUILD-001; use the control only to decide build equivalence and preserve the
failure for its owning post-audit work.
