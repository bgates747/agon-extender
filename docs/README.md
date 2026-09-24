# Extender handbook

Start here for current operation and contracts. This handbook is being
consolidated under [AUDIT-009](tasks/AUDIT-009.md); its remaining coverage gaps
are explicit. It must not require comparing old task amendments to determine
current behavior. Dated evidence supports claims but is not a second manual.

## Use an existing installation

| Need | Current guide |
|---|---|
| First use, prerequisites, host setup and another project's workflow | [Using Extender](using-extender.md) |
| Mainboard SD files; checked/fast transfers; sessions and recovery | [Mainboard SD](mainboard-sd.md) |
| Physical/browser/agent input, ownership and platform limits | [Keyboard input](remote-keyboard.md) |
| Normal Agon reset and browser reset button | [Bench reset](bench-reset.md) |
| Recover an Agon that cannot boot MOS | [MOS recovery](mos-recovery.md) |
| Where files belong on SD | [SD layout](sd-layout.md) |

Remote input requires prior EMOS admission. The SD listener is foreground,
requires Legacy mode and runs as `/emos/sdserve.bin`. P4-local SD and physical
HDMI output are not current installed capabilities. Consult the operating guides
for precise limits rather than assuming support from a research or example file.

## Develop against the current interfaces

| Need | Current authority |
|---|---|
| Component builds and deployed-versus-base source limits | [Building](building.md) |
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
A base build is not yet proven equivalent to the deployed P4 overlay combination.

## Test and qualify

| Need | Authority |
|---|---|
| Current versus historical procedure applicability | [Procedure index](procedures/README.md) |
| Current fixture constraints and accepted input exceptions | [Bench constraints](qualification/bench-constraints.md) |
| Capture failures and uninstrumented controls | [Capture protocol](qualification/capture-failure-protocol.md) |
| Timing scopes, PRT units and package reuse boundary | [Game timing](testing/game-timing.md) |
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
