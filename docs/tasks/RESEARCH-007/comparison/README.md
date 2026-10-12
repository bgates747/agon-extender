# Offline comparison preparation

These tools prepare or analyse local files only. They have no serial, network,
reset, deployment or test-invocation code. The owning
[resumption plan](../RESUME-R01.md) controls physical execution after handover.

## Prepare

Run `prepare.py --help` for required inputs. Supply the checkout root, the retained
finite-fixture plan, the same-source ordinary-UART RGB888 and indexed build
folders, the exact r11 rollback folder, a fresh output folder and a unique
`r07-...` campaign name. The ignored local index records the concrete command.
The helper requires successful target validation and unchanged committed source
for both comparison variants, excludes all parallel selections, checks frozen
SCAN binary hashes and verifies archived flash bytes. It creates:

1. `plan.json`: variant/config/fixture hashes, result paths, clock assumptions,
   required resident hashes and firmware segment identities.
2. `startup-mode20.txt` and `startup-mode136.txt`: keyboard setup and mode only.
   These are the only generated files eligible to become root autoexec. Preserve
   and restore the actual startup bytes around future hardware use.
3. Separate `baseline` and `candidate` configurations and explicit CLI suites.
   Their `sd_path` mappings in the plan identify deployment destinations; each
   finite config replaces the indicated active run.cfg only after preserving it.
4. Per-mode hardware-sprite plans and separate hardware/chart CLI batches.
   Create the named result/plan directories before uploading. Resident binaries
   and data are not copied into this package; verify them against the plan.
5. A verified firmware archive containing only the four specified flash segments
   per variant and rollback, with their retained source/build records. This is
   an experimental local package, not a selected production release.

The suite is invoked by `EXEC` at a positively established MOS prompt, using the
selected variant's `suite20.txt` SD path from the plan. A reset alone never
launches a fixture. Hardware case54 requires the agent's window-relative Space;
colour charts require an explicit Escape after their measurement and visual
review. Neither control is silently appended to the finite suite.

Historical integration helpers remain evidence only. In particular, do not use
`finite_suite.py stage`, `controls.py hardware/chart`, or the old live
`qualification/render_load.py` / `static_conversion.py` launch paths: they
install test autoexec files. Their pure codecs/analysis remain reusable.

## Compare

`compare.py` consumes `plan.json` and two local collection directories. Each
contains `t03.bin`, `t07.bin`, `t08.bin`, `t09.bin`, `windows.json` and `run.json`.
The collection's `run.json` must record `installed_build_id` and
`application_sha256` from independent installation verification. It must also
retain the broader invocation/startup/input evidence required by the protocol;
these two fields alone do not prove that the collector observed the fixture.

The helper reuses SCAN decoding and window analysis, validates counts/build/tag/
faults/closed windows, and rejects different per-update state trajectories. It
writes a new JSON comparison with lower-cost reductions and higher-rate increases
labelled explicitly. Zero baselines yield null percentages. It preserves manager
friendly60Hz budget percentages and separate application/publication/DMA scopes.
It does not compare the unfenced Nurples interval as renderer completion and
cannot grant visual or human-input acceptance.

Run `test_compare.py` for synthetic guards against mixed installed bytes,
trajectory differences, open windows, faulted/truncated records and misleading
unfenced completion comparisons. These tests make no physical timing claim.
