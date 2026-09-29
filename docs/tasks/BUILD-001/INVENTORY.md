# BUILD-001 B01-02 — Current build inventory and profile disposition

Status: inventory and profile dispositions accepted by the Author on
2026-09-28. Captured: 2026-09-28. No hardware was changed.

Sequencing amendment: the combined ExCom+LCD control below remains frozen
evidence of the first BUILD-001 attempt, but it is no longer the equivalence or
AUDIT-010 baseline. The replacement baseline is the retained working pre-LCD
r61 closure at Extender commit
`6c6bea3beb2f8abc89c5b1f40a0e7dd0890a084d`, paired with EMOS v0.1.23 source
`21a9ba27f1f346473d767c2c3053ee18e8911335`. B01-04e and B01-05e own its native
reproduction and new inventory evidence.

## Bound identities

| Actor or artifact | Identity |
|---|---|
| Extender source used for the clean control | `bd9d4fa98ca92daac5d60ab32cf0e810ff7e7fe1`; clean export |
| EMOS source observed, not built | `8f29bf811e4b989117e437a8e10afe2adbc77be7`; pre-existing untracked `scripts/application_peer.py` preserved |
| MOS builder observed, not built | `90034c2348761c42bab4217ce5b0f906922dc0e4`; clean |
| Selected production | `v0.1.0`, `extender-installation-r02`; unchanged |
| PlatformIO Core | 6.1.19 |
| pioarduino platform | 55.03.311 / reported package 55.3.311 |
| ESP-IDF framework | 5.5.5 / package 3.50505.0 |
| Arduino-ESP32 framework | 3.3.11; libraries `5.5.5+sha.b774170ff46` |
| RISC-V compiler package | 14.2.0+20260121 |
| CMake / Ninja / SCons | 4.0.3 / 1.13.1 / 4.8.1 |

The clean control is build ID
`uart-excom-console-r72-b2026-09-28-22-46-33Z`, status `draft`, with the LCD
opt-in applied only to its exported clean tree. The ignored local evidence is
retained under `agents/build001/baseline-console-lcd/`; tracked documents do not
record its absolute machine path.

## Control outputs

| Output | Bytes | SHA-256 |
|---|---:|---|
| Application binary | 1,646,592 | `e2b92f5e67b2e6f545d6c46b776a633459fc2616ad20faaab476df7aba69c31b` |
| ELF | 31,437,268 | `307c2ad7e1b3aeac94f6b48abbc2f05c581d9531c200b54c06979077fc62e496` |
| Factory image | 1,777,664 | `4c9f1a0979503b556e92afd0c9d544b702a630f10fda52db71781eeb29b0a7ff` |
| Bootloader | 24,256 | `0b1b6132f21901b5f90cb8d245d4e09407052abc47dcc7f47e0bdb41e8eca261` |
| Partition table | 3,072 | `e29396a4f5ecc129c0e275d2df19d69adb5ee33389e3d5659e9a50932ac6864a` |
| Managed dependency lock | 9,651 | `4195fd96f06ef18ca2255b5756e7409c644cf20d2ade7f53fa7c20ac0ed597aa` |
| Linker map | 13,568,961 | `1f3dd6d6dc1a0d24673eb16d4d1e6bda7ce56e7b5351962d7763daeaf9360913` |
| Generated CMake compilation database | 23,400,057 | `c517a955f8247d99ffcb1c7b89730a3b4a3293277af1cabbbeb54773c1f60e89` |

PlatformIO reported 67,920 of its nominal 512,000 RAM bytes and 1,645,712 of
7,340,032 application-flash bytes. Those numbers are retained as tool outputs,
not a complete P4 internal/PSRAM resource measurement.

The effective application configuration hash is
`e820457d174e04f6683ddb50c1120f9785cbe6cb0b7c40ca288d92773af76235`;
the bootloader configuration hash is
`099b7594fb62b518b4876567eaad1e3f16a1845f9527cd7fec2e511e6a14a512`.
Both select pre-v3 silicon bounds 100 through 199. The application selects the
custom `partitions.csv`, Arduino autostart on core 1 and a 1,000-Hz FreeRTOS tick.

## Actual graph finding

The console selection declares 24 project translation units, 11 vendored
vdp-gl translation units and five embedded browser assets. The final verbose
SCons link directly names 56 non-framework object tokens, including these
selected units, generated asset objects and Arduino library objects.

This control retained PlatformIO's verbose command log rather than claiming the
PORT-008 fail-closed provenance recorder: that recorder is deliberately bound
to `p4-port008-nonrelease-qualification` and refuses `p4-console`. The log and
fresh clean output are sufficient to demonstrate the graph split and establish
comparison hashes, but are not promoted as cryptographically complete
actual-action evidence.

The generated `compile_commands.json` contains 1,872 entries whose outputs use
the `.obj` suffix. The final link instead consumes SCons `.o` objects. The
database contains only 24 entries rooted in the exported project's `video/` or
`vendor/` paths, fewer than the 35 declared project-plus-vendored units, and it
does not describe the linked object paths. It is therefore not authoritative
for current actual-action analysis. The native design must make CMake own both
compilation and the final link, then validate the database against the ELF map.

## Accepted profile classification

“Migrate” means BUILD-001 must represent the profile before retiring the hybrid
path. “Freeze” means retain its source manifest and historical evidence but do
not create a native executable profile. “Tombstone” means preserve an explicit
rejection record but no buildable native target.

| Profile | Proposed class | Reason |
|---|---|---|
| `p4-console` | Migrate — product development | Sole documented maintained P4 product target; first reproduce the retained pre-LCD r61 closure. LCD becomes a later LCD-001 integration delta. |
| `p4-mos-recovery` | Migrate — recovery | Current documented external MOS recovery programmer; operational capability must survive build cutover. |
| `p4-port008-nonrelease-qualification` | Migrate — active diagnostic | PORT-008 retains unfinished qualification work and this profile owns actual-action provenance controls that inform the native graph validator. It remains non-release. |
| `p4-canary` | Freeze; convert common settings, not executable target | Earlier bring-up target and accidental default. Native profiles still inherit its board/configuration facts through common profile data. |
| `p4-uart-forward` | Freeze | Bounded PORT-009 diagnostic with retained builder/evidence; no current product role. |
| `p4-uart-roundtrip` | Freeze | Bounded PORT-010 diagnostic with retained builder/evidence; no current product role. |
| `p4-uart-flow` | Freeze | Bounded PORT-011 diagnostic with retained builder/evidence; no current product role. |
| `p4-display-renderer` | Freeze | Phase-B stepping-stone compile diagnostic superseded by the integrated console. |
| `p4-frame-service` | Freeze | Phase-C stepping-stone compile diagnostic superseded by the integrated console. |
| `p4-presentation` | Freeze | Phase-D stepping-stone compile diagnostic superseded by the integrated console. |
| `p4-official-display` | Freeze | Phase-E stepping-stone compile diagnostic superseded by the integrated console. |
| `p4-network-service` | Freeze | First-tranche compile diagnostic superseded by the integrated console. |
| `p4-browser-vdp` | Freeze | Predeployment Phase-F target superseded by the integrated console. |
| `p4-general-poll` | Freeze | One-shot PORT-013 diagnostic with retained builder/evidence; no product activation role. |
| `p4-visible-text` | Freeze | PORT-014 diagnostic with retained builder/evidence; no product activation role. |
| `p4-keyboard` | Freeze | Controlled PORT-005 diagnostic superseded by integrated console input. |
| `p4-usb-keyboard` | Freeze | Acquisition-only PORT-015 diagnostic superseded by integrated console input. |
| `p4-browser-typing` | Freeze | REMOTE-001 focused diagnostic superseded by integrated console browser input. |
| `p4-usb-cli` | Freeze | PORT-015 stepping target superseded by `p4-console`, which inherits its behavior. |
| `p4-forward-vdp` | Tombstone | Explicitly rejected and superseded; current hook already refuses it. |
| `p4-zdi-probe` | Tombstone | Explicitly retired; current hook already refuses it. |
| `p4-zdi-mos-recovery` | Tombstone | Explicitly retired; current hook already refuses it. |

The Author accepted this classification on 2026-09-28. The frozen diagnostic
manifests and builders remain useful historical oracles,
but maintaining twenty native profiles would preserve the accidental phase
structure that BUILD-001 is intended to remove. If a frozen diagnostic becomes
necessary later, its owner can define a current native profile from the retained
manifest under a bounded task.

## Current consumers

The maintained product path is consumed by `scripts/prepare_console.py`,
`scripts/vdp-pio.sh`, `scripts/package_installation.py`, browser-bundle tests,
performance builders, current building/shared-service documentation and the
production packager. The recovery path is consumed by `docs/mos-recovery.md`.
Dedicated preparation scripts still name the UART, polling, text and keyboard
diagnostics proposed for freezing. Current documentation and generated
dependency records also name phase targets; those references must be classified
as history, current procedure or generated model during B01-07 rather than
blindly rewritten.

## Host controls

| Control | Result |
|---|---|
| Clean identified `p4-console` plus LCD build | Pass |
| Browser bundle: embedded bytes, negotiation and 48 codec vectors | Pass |
| Console mode-lifecycle host test | Pass: 1 test |
| DSP matrix lifetime host test | Pass: original leak reproduced and correction control passed |
| Detached HTTP consumer against actual ESP-IDF headers/toolchain | Pass |
| Broad `unittest` discovery attempt | Not a valid suite runner: 32 discovered tests passed and two executable scripts were imported incorrectly |
| Direct USB source-selection control | Fail: its fake PlatformIO environment lacks the now-required `BoardConfig()` method |

The USB failure predates native implementation and is a stale host-test harness,
not evidence of product source failure. B01-04 must either update that harness
as part of profile retirement/cutover or replace it with native manifest
validation; it must not silently count the control as passing.
