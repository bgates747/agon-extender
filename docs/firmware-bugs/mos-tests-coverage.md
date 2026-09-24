# MOS test-suite cross-reference — 2026-09-20

## Executive summary

The independent `mos-tests` project directly covers FWBUG-008 and FWBUG-009.
Its retained physical EMOS results demonstrate both failures. Those results
upgrade the earlier source-only register entries. The standalone stock-hardware
cohort excluded these calls; do not imply stock physical reproduction from the
emulator or EMOS results. No tests, builds or hardware operations were performed
for this cross-reference; the MOS test repository was inspected read-only.

Repository: `bgates747/mos-tests`, clean at
`411266b5ab1ed42b6d91c13a13dea5a6c468c8f2`, suite v0.0.0-alpha.
[Human scope](https://github.com/bgates747/mos-tests/blob/411266b5ab1ed42b6d91c13a13dea5a6c468c8f2/humans/README.md),
[catalogue](https://github.com/bgates747/mos-tests/blob/411266b5ab1ed42b6d91c13a13dea5a6c468c8f2/humans/dev/catalogue/api.json),
[qualification narrative](https://github.com/bgates747/mos-tests/blob/411266b5ab1ed42b6d91c13a13dea5a6c468c8f2/humans/reports/qualification/narrative.html).

## Direct matches

| Bug | Existing test | Retained outcome and limit |
|---|---|---|
| FWBUG-008 | `sd_writeblocks.rst08.001`, selector `0x73`, two seeds; sector2 should become512 bytes of `0x6B`. Independent card readback; C `SD_writeBlocks.c.001` is the distinct write control. | Physical Light2 EMOS v0.1.17 returned success but sector2 remained zero, both seeds. Narrative records read-dispatch source/binary confirmation and successful C write control. Stock MOS under Fab1.2.4/1.2.5 instead returns error2 with no intended sector write. Stock Console8/Light2 standalone selections did not exercise this API. |
| FWBUG-009 | `ffs_setlabel.rst08.001`, selector `0xA4`, two seeds; set `APITEST`, check return and label. | Physical EMOS and stock emulator reports fail with `A=0x17` (23), consistent with the wrapper fallthrough. Stock physical cohort excludes it. Return failure is established; inspect per-run side-effect evidence rather than claiming label success from a headline result alone. |

Source: [fixture setup/assertions](https://github.com/bgates747/mos-tests/blob/411266b5ab1ed42b6d91c13a13dea5a6c468c8f2/humans/dev/api-conformance/src/main.cpp),
[independent sector/label checks](https://github.com/bgates747/mos-tests/blob/411266b5ab1ed42b6d91c13a13dea5a6c468c8f2/agents/emulator/api_conformance.py),
[physical EMOS detailed report](https://github.com/bgates747/mos-tests/blob/411266b5ab1ed42b6d91c13a13dea5a6c468c8f2/humans/reports/qualification/emos-verbose.html),
[stock Fab1.2.5 detailed report](https://github.com/bgates747/mos-tests/blob/411266b5ab1ed42b6d91c13a13dea5a6c468c8f2/humans/reports/qualification/fab-125-verbose.html).

## Remaining registered bugs

| IDs | Coverage found in this MOS suite |
|---|---|
| FWBUG-001/002/003 | No targeted Copper cleanup, sprite-scanout stress or transformed-bitmap numeric reproducer found. General MOS output calls do not reproduce these graphics defects. |
| FWBUG-004/005/006 | No targeted unavailable-audio framing, virtual-key-query `&99`, or VDP updater consumption tests found. `mos_setkbvector` registration/clear coverage is not keyboard query/reply coverage; the emulator report explicitly leaves callback event delivery unqualified. |
| FWBUG-007/012 | No targeted primitive-completion, buffer-swap notification or queued bitmap/path destruction lifetime tests found. |
| FWBUG-010/011 | No targeted undersized/oversized VDP reply injection found. UART API tests use UART1 stimuli and are not tests of the MOS UART0 VDP packet parser. |

The coverage classification follows inspected catalogue, fixture, harness and
reports, not the existence of an API name alone. No duplicate replacement tests
should be designed for008/009 without first reusing these cases.

## Other report failures are not automatically new firmware bugs

The suite also records calling-contract/register discrepancies and functional
questions, including `mos_extractnumber` and `ffs_getlabel`. Its narrative
explicitly leaves firmware-versus-documentation-versus-test interpretation open
in several cases. These are retained leads, not silently promoted to confirmed
bug IDs by this coverage review. Its earlier write-timeout false-success finding
is distinct from the raw-write dispatch defect; it must not be merged into008.

## Author disposition — 2026-09-20

FWBUG-008 and FWBUG-009 are independently discovered and verified findings:
Extender's source audit identified the defects separately from the existing
mos-tests tests and retained runtime evidence. This is not a claim of two
independent physical test implementations or new bench verification.

The Author assigns their eventual fixes to mos-tests, deferred until tokens
are available. If either demonstrably blocks current Extender work, consider
a scoped EMOS-first correction and notify mos-tests of the patch and reusable
regression evidence. No present Extender blocker has been established. Ordinary
FatFS SD writes use a different path from FWBUG-008. No firmware patch, upstream
checkout edit or cross-project notification was performed by this update.
