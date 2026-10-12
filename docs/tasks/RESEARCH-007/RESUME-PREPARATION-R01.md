# Indexed/PPA comparison — offline resumption preparation

## Outcome

Both complete P4-PC targets compile/link and pass actual-source/component validation.
They share committed source `26660db54ca0ff0621cc7822b985092933a636e5`, identical SDK configuration
and dependency lock. Both exclude parallel boot/probe/data/ExExt selections.
The exact pre-parallel r11 rollback and new CLI-only fixture package are verified.
**No bench operation or new performance measurement occurred.** Fsim retains the bench.
The [resumption plan](RESUME-R01.md) controls the remaining physical work.

## Prepared firmware

| Role | Build | Application bytes | Application SHA-256 |
|---|---|---:|---|
| baseline | `rgb-001-r12-b2026-10-12-10-15-57Z` | 1737616 | `abf8bb9b013b9a2f65e6790230e9a4ff5b6f48936fda000ad192a1ddcd35a284` |
| candidate | `indexed-hdmi-r05-b2026-10-12-10-15-57Z` | 1743472 | `636bcfc6c7f6424d72ce6c3ed17cfc46d682619c534d79f101aea2cf3b6fc40c` |
| rollback | `rgb-001-r11-b2026-10-08-01-22-20Z` | 1726944 | `5f1b42a161ec9df13701db3038e06019a27b2880cf608cdcf8eea109670ca13a` |

The RGB888 control is newly compiled same-source experimental firmware, not an
already accepted replacement for r11. Candidate r05 differs from the earlier
r04 selection by excluding parallel startup handling. Neither image is installed
or production-selected. Both use360MHz CPU,200MHz PSRAM,80MHz flash, automatic
native HDMI carriers, rolling overlays,320 scaling and normal render probes.
EMOS remains the installed pre-parallel build; no new EMOS build is needed.

## Completed offline checks

| Check | Result / scope |
|---|---|
| Complete target builds | Both compile/link and actual-source/component validation pass |
| Parallel exclusion | Every compile action checked; native payload/coordinator sources not compiled; startup/coordinator symbols absent from both ELFs |
| Candidate target preprocessing | Actual P4 console flags/includes omit startup/coordinator classes and ExExt request handling |
| Source/config parity | Same committed source closure, SDK config and dependency lock; intended renderer/CLUT selections differ |
| Controller goldens | Indexed and RGB888 pass shared drawing/clipping/alpha/scroll/copy/overlay/swap checks |
| Build-selection checks |14 pass |
| Conversion-analysis units |2 pass; PPA whole-image time stays distinct from CPU per-row expansion |
| UART owner/session checks |2 +2 pass |
| Comparison guards |6 synthetic cases pass: mixed bytes, changed state, incomplete/faulted records, open windows and unfenced-game distinction |
| Frozen fixture/control hashes | Four finite executables and five resident control/data files pass |
| CLI package |24 generated files verified; startup setup only, four finite RUN commands per separate suite, no mode switch in test batches |
| Flash archive | Three four-segment sets verified against source manifests and archived readback; no merged NVS-overwriting span |
| Global version-record validator | Existing unrelated light2-harness-r02 connectivity hash mismatch remains; no electrical record changed |

## Ready package and limits

The local index is `agents/research007/resume-r01/INDEX.md`; generated package
and `plan.json` are under its `package` directory. The maintained offline
[preparer and comparator](comparison/README.md) document their inputs and use.
Generated files use unique campaign `r07-20261012-uart`, separate baseline/
candidate result paths and correlation tags. Actual deployment must preserve
and restore current startup/run.cfg bytes and independently verify SD readbacks.
Do not reuse the earlier autoexec/reset launchers.

The firmware archive SHA-256 is `8ae720471547e20136b69b961ee8c4888a0d30ea869f34f79d04ff0c4da18aae`; package plan SHA-256
is `53ede202ecb8cebbd9cb443423493572a535cc6258e5811bb9061e836c2a2c9f`. Exact segment/source records stay with
the local package. Private reset endpoints are retained only in ignored artifacts.
These are local experimental builds, not redistributable production packages.

Fresh Author handover, actual installed EMOS/mainboard identity, real CLI/listener
admission, independent flash/fixture verification and subsequent hardware execution
remain required. No new speedup, visual correctness, input-latency or acceptance
claim follows from these offline checks. Production selection remains unchanged.
