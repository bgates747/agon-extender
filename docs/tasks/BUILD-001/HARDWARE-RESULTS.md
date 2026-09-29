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

B01-HR04 [ ] Diagnose the native-only startup assertion from the retained ELF,
map, configuration, dependency lock and hybrid control. Any source or
configuration repair requires targeted host checks and a new immutable candidate
identity.

B01-HR05 [ ] Prepare a corrected hardware procedure or accepted amendment with
the actual EMOS dependency, exact replacement candidate and unchanged rollback
boundary before another flash authorization request.
