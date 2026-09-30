# Extender handbook

Start here for current operation and contracts. The [handbook closeout](tasks/AUDIT-009/CLOSEOUT.md)
records checked workflows and remaining limits; the broader [AUDIT-009](tasks/AUDIT-009.md)
historical review is incomplete. It must not require comparing old task amendments to determine
current behavior. Dated evidence supports claims but is not a second manual.

Production **v0.1.0** is the accepted local combination. The [current approved local installation](../production/README.md) selects exact
firmware, EMOSlet and host-tool archives with hashes and installation guidance.

## Use an existing installation

| Need | Current guide |
|---|---|
| First use, prerequisites, host setup and another project's workflow | [Using Extender](using-extender.md) |
| P4-local SD file/directory management candidate | [P4 SD HTTP guide](p4-sd.md), candidate only; not in selected production |
| Mainboard SD: foreground checked/fast, candidate automatic WebDAV and application transfers | [Mainboard SD](mainboard-sd.md) |
| Physical/browser/agent input, ownership and platform limits | [Keyboard input](remote-keyboard.md) |
| Read visible ExCom text without taking video ownership | [Screen text](screen-text.md) |
| Normal Agon reset and browser reset button | [Bench reset](bench-reset.md) |
| Recover an Agon that cannot boot MOS | [MOS recovery](mos-recovery.md) |
| Where files belong on SD | [SD layout](sd-layout.md) |

Remote input requires prior EMOS admission. The production SD listener is foreground,
requires Legacy mode and runs as `/emos/sdserve.bin`. Newer paired development
firmware additionally supports automatic staged mainboard WebDAV on port 8081
at an idle CLI in Legacy/negotiated ExCom, and application-initiated card transfers.
These passed bounded hardware checks but are not in selected production; the
[mainboard SD guide](mainboard-sd.md) supplies current usage and limits. P4-local SD HTTP access passed bounded r57 candidate checks but is outside the
selected production bundle. Neither this page nor the selected bundle identifies
the firmware currently on an occupied bench. Physical HDMI output remains unqualified. Consult the operating guides
for precise limits rather than assuming support from a research or example file.

## Develop against the current interfaces

| Need | Current authority |
|---|---|
| Discover host clients versus retained development helpers | [Host tool index](../scripts/README.md) |
| Common P4 service boundaries for other projects | [Shared services](shared-p4-services.md), development interface and consumer obligations |
| Linux emulator setup and review boundaries | [Emulator setup](emulator-setup.md) |
| Component builds and hardware-equivalence limits | [Building](building.md) |
| Installation bundles and selection status | [Production entry point](../production/README.md), [installation guide](installing.md) |
| Processor ownership and accepted architecture | [Architecture](architecture.md), [repository ownership](../OWNERSHIP.md) |
| EMOS resident gateway and prefixed utilities | [EMOS documentation](https://github.com/bgates747/agon-emos/blob/main/docs/README.md) |
| ExCom control / display-preserving switching | [Console protocol](protocols/excom-console.md) |
| SD wire protocol | [SD protocol](protocols/mainboard-sd.md) |
| Browser frame encodings and pacing boundary | [Video protocol](protocols/browser-video.md) |
| Firmware/build identity rules | [Version policy](versions/README.md) |
| Known faults and reproduction references | [Firmware bug register](firmware-bugs.md) |

The architecture includes accepted design beyond implemented coverage. Current
operation is bounded by the guides and recorded qualifications; an accepted
architecture is not a claim that every mode/peripheral has been implemented.
The selected r55 DevKit composition has a clean build and bounded physical
acceptance; use the production manifests rather than historical overlay recipes.
Other boards and complete peripheral compatibility remain unqualified.

## Test and qualify

| Need | Authority |
|---|---|
| Current versus historical procedure applicability | [Procedure index](procedures/README.md) |
| Current fixture constraints and accepted input exceptions | [Bench constraints](qualification/bench-constraints.md) |
| Capture failures and uninstrumented controls | [Capture protocol](qualification/capture-failure-protocol.md) |
| Timing scopes, PRT units and package reuse boundary | [Game timing](testing/game-timing.md) |
| Firmware acceptance: offline and installed-hardware suite | [Qualification suite](../qualification/README.md) |
| Qualification operation and retained runs | [Qualification procedure](testing/regression-suite.md) |
| Compatibility evidence / generated-matrix status | [Qualification index](qualification/README.md) |

Bench access, endpoints and installed-build receipts remain machine-local.
A procedure's existence does not authorize its execution or qualify a rebuilt
candidate. Historical runner scripts require review before reuse.

## Evidence and future work

[TODO](../TODO.md) is the unfinished-work index. [Task records](tasks/README.md),
[decision records](decisions/README.md), dated development logs and qualification
receipts hold history and rationale. [P4-PC references](hardware/esp32-p4-pc/README.md)
are a pinned documentation library for the planned board, not evidence of its
arrival or successful integration. Routine users should not need these archives
to reconstruct the instructions in this handbook.
