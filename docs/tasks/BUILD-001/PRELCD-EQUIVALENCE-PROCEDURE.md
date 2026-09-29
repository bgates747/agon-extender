# BUILD-001 pre-LCD functional-equivalence procedure

State: accepted by the Author on 2026-09-28; execution authorized within the
exact scope and stopping conditions below.
This procedure qualifies the native pre-LCD build boundary only. It neither
enables LCD output nor promotes production firmware.

## Exact candidate and rollback

| Role | Identity | Application SHA-256 |
|---|---|---|
| Native candidate | `build001-d17cae79-console-prelcd`; source `d17cae7968a7640d37a9ced36a681f063ef78913` | `861cb25c9c96e6b3e845cf5268ce922378649f4594e9f231ae9a85a1256ba8df` |
| Hardware-tested predecessor | `build001-eadc2925-wired-prelcd`; source `eadc2925e436754f5b7e0beddf088b01ded504ba` | `7fea756ec20eb28dd0d2ef5238fa02115b99d6fc813923fe56d05b02daf57e3b` |
| Production rollback | `uart-excom-console-r55-b2026-09-25-02-18-28Z`; production v0.1.0 bundle `extender-installation-r02` | `a2d41a29ee9f5b42a10df9c3d724202b1db5ab561f3c3fc29f134f4f15fe54cb` |

The candidate differs from the boot-tested predecessor only in native build
infrastructure for the recovery profile; its console product inputs retain the
same wired-network correction. The operator must nevertheless treat the d17
bytes as a new immutable candidate and independently compare every written
flash region before boot. The machine-local bench record supplies private
endpoints and commands.

| Offset | Candidate artifact | SHA-256 |
|---:|---|---|
| `0x2000` | `bootloader/bootloader.bin` | `da2cbcab6f4b4efed454e91c1800eb82db39fb44715e124d6f12b352c66f9cd7` |
| `0x8000` | `partition_table/partition-table.bin` | `e29396a4f5ecc129c0e275d2df19d69adb5ee33389e3d5659e9a50932ac6864a` |
| `0xf000` | `ota_data_initial.bin` | `7d2c7ac4888bfd75cd5f56e8d61f69595121183afc81556c876732fd3782c62f` |
| `0x20000` | `agon_extender.bin` | `861cb25c9c96e6b3e845cf5268ce922378649f4594e9f231ae9a85a1256ba8df` |

## Preconditions and stopping conditions

B01-PE01 [x] The Author accepts this exact procedure and authorizes the P4 flash,
ordinary Agon resets, temporary startup/fixture deployment, read-only service
checks and final rollback described below.

B01-PE02 [ ] The operator verifies the expected P4 identity, current EMOS
v0.1.23 development identity, foreground EMOSlet, admitted Extender keyboard,
recoverable Legacy CLI and current bench constraints. Any conflict stops the
run before mutation.

B01-PE03 [ ] The operator verifies the candidate manifest and every candidate
flash artifact, plus the immutable production rollback archive and its exact
flash bytes. Missing or mismatched bytes stop the run.

B01-PE04 [ ] The operator records start time, identities and initial state in
ignored evidence. A flash comparison failure, boot loop, panic, unexplained
reset, loss of both admitted input and noninteractive recovery, or filesystem
corruption indication stops candidate testing and invokes rollback.

## Automated pass

B01-PE05 [ ] At a verified Legacy prompt, the runner clears the mainboard screen
with `VDU 12`. The operator flashes only the P4 candidate, independently
compares all generated regions while the P4 remains in its loader, then boots
once and records the exact serial identity. EMOS and eZ80 flash remain
unchanged.

B01-PE06 [ ] The runner verifies stable ordinary Legacy output, ExCom
activation/return, admitted Extender keyboard press/release behavior, the SD
service and the HTTP status endpoint. It records browser-disconnected and
browser-connected checks separately and makes no performance claim from this
functional smoke.

B01-PE07 [ ] With mode selected only by `/autoexec.txt`, the runner executes the
mode0 asymmetric color/edge fixture. The Author later confirms correct colors,
orientation and all four source edges on Legacy output; one bounded browser
capture must agree with the source image. LCD is absent from this comparison.
The maintained build produces an 812-byte `bars.bin` with SHA-256
`ce783bcb3a517b4be48e6522d186d3409af04cf0bfb182531ed7334b0beed47f`.

B01-PE08 [ ] With `/autoexec.txt` selecting mode20 before launch, the runner
executes the static grid fixture without allowing the fixture to switch modes.
Expected Legacy and browser geometry is the complete A1-through-H6 grid in
order with all asymmetric edge markers at the native 512-by-384 extent. There
is no letterbox or pillarbox requirement on these non-LCD outputs.
The maintained build produces a 1,691-byte `grid.bin` with SHA-256
`a44d9e4ba6f23c603158130ac3d47039e411047bb34435fb52458968e7492e8d`.

B01-PE09 [ ] Each automated case prints concise progress on Legacy output where
practical and durably records start, end and duration. The runner invokes the
accepted spoken cue on terminal success or detected failure. A failure identity
is recorded durably before the cue; after alert-player output, the failure hook
reprints that identity as the final visible Legacy result. The agent does not
poll merely to wait for completion.

The maintained `scripts/bench_job.py` terminal-hook contract supplies the
detached duration/result record and selects exactly one argv-only success or
failure notification after the test driver exits. The reviewed run-specific
driver and ignored hook file must still bind those generic hooks to the accepted
Legacy voice cue and prove that its failure path restores the recorded error as
the last visible text.

## Manual application pass and closeout

B01-PE10 [ ] Only after all automated cases terminate, the Author manually runs
Nurples and any other selected asset-heavy application that changes video mode
after loading VDP buffers. Record mode-switch success, Legacy/ExCom rendering,
keyboard/Escape behavior and browser availability separately. These known
late-switch cases remain outside BUILD-001 repair scope and are not granted an
automated-fixture exception.

B01-PE11 [ ] Run the accepted ordinary boot smoke and recovery check. On a full
pass, leave the final Legacy result visible and invoke the spoken completion
cue. On failure, use the failure cue only if the admitted recovery path can then
restore the durable failure identity as the final visible text.

B01-PE12 [ ] After evidence capture, restore the selected production P4 firmware
unless the Author explicitly directs the candidate to remain for continued
review. Independently verify restored bytes and identity. Restoration is
rollback, not promotion of either build.

## Acceptance boundary

B01-PE13 [ ] The Author reviews the Legacy observations and any requested browser
captures. Host checks and unattended machine results may establish their named
facts, but they cannot self-accept visual equivalence or BUILD-001 cutover.
