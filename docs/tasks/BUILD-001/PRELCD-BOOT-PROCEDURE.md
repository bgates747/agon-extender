# BUILD-001 pre-LCD native boot procedure

State: authorized by the Author's 2026-09-28 direction to flash the prepared
pre-LCD build and determine whether it boots. This is a boot canary, not
functional equivalence, audit-baseline acceptance or production promotion.

## Exact candidate and rollback

| Role | Identity | Application SHA-256 |
|---|---|---|
| Native pre-LCD candidate | `build001-595286dd-console-prelcd`; branch `codex/build001-prelcd`; source `595286dd9ed05d0ff228d8ecba195c116197367f`; r61 product base `6c6bea3beb2f8abc89c5b1f40a0e7dd0890a084d` | `891c990d7ed147bc16a7efab537983645b5843e8b4eeb0b967235c910e361719` |
| Production rollback | `uart-excom-console-r55-b2026-09-25-02-18-28Z`; production v0.1.0 bundle `extender-installation-r02` | `a2d41a29ee9f5b42a10df9c3d724202b1db5ab561f3c3fc29f134f4f15fe54cb` |

The candidate uses ESP-IDF commit
`b774170ff46c393eeb5e495ea37936038d3f4f4f` and contains no selected LCD
source, LCD definition or ST7701 dependency. Its retained local manifest is
`agents/build001/prelcd-worktree/agents/build001/native-prelcd-01/manifest.json`.
Generated flash arguments select DIO, 80 MHz and 16 MiB with these exact inputs:

| Offset | Artifact | SHA-256 |
|---:|---|---|
| `0x2000` | `bootloader/bootloader.bin` | `e6b2b028ce0a854c81ca9d17750ceb9619ea8928445351cdce3925a64a0b74c8` |
| `0x8000` | `partition_table/partition-table.bin` | `e29396a4f5ecc129c0e275d2df19d69adb5ee33389e3d5659e9a50932ac6864a` |
| `0xf000` | `ota_data_initial.bin` | `7d2c7ac4888bfd75cd5f56e8d61f69595121183afc81556c876732fd3782c62f` |
| `0x20000` | `agon_extender.bin` | `891c990d7ed147bc16a7efab537983645b5843e8b4eeb0b967235c910e361719` |

## Boot-only execution

B01-PB01 [ ] Reverify the expected revision-v1.3 P4 stable USB identity,
candidate manifest and all local/remote staged hashes. Reverify the selected
production rollback archive before mutation.

B01-PB02 [ ] Confirm the current EMOS v0.1.23 development baseline has admitted
Extender input and a recoverable Legacy CLI. At that prompt clear the Legacy
screen with `VDU 12`. Do not modify EMOS, startup or SD files.

B01-PB03 [ ] Flash only the P4 using the candidate's generated arguments. Keep
the P4 in the loader until every written region independently compares with its
input, then hard-reset it once.

B01-PB04 [ ] Capture bounded serial startup. Passing this canary requires exact
application identity `595286dd`, completion beyond application initialization,
no panic/assert/reset loop, and restoration of the HTTP status endpoint. Do not
start an LCD, ExCom, fixture, browser-viewer or game test in this run.

B01-PB05 [ ] On boot failure, stop immediately and restore/independently verify
the selected production P4 image. Issue one ordinary Agon reset only if needed
to restore fresh EMOS admission. Invoke the established Legacy failure cue and
leave a concise failure identity visible.

B01-PB06 [ ] On boot success, leave the candidate installed and report the
bounded result for Author review. A later exact procedure and authorization are
still required for functional equivalence.
