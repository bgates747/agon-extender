# AUDIT-009 — Current-handbook closeout

## Outcome

The current-handbook review is complete within its recorded documentation/source
scope. Start at the [handbook](../../README.md), not an old task recipe. This is
not a claim that the entire historical inventory is reviewed or that a fresh
machine, firmware build or device has passed testing. Broader A09-04/05/06/08
coverage remains open; no automatic archival-review campaign is selected.

## What readers can use

| Job | Current authority | Important boundary |
|---|---|---|
| Identify and use an installation | [Using Extender](../../using-extender.md) | Operator's current bench record identifies installed firmware and access; repository selection alone does not |
| Choose approved firmware/tools | [Production](../../../production/README.md), [installation](../../installing.md) | v0.1.0 selects r55/EMOS v0.1.19/sdserve v0.2.0; local archives supplied by owner, not a public download |
| Transfer mainboard files | [Mainboard SD](../../mainboard-sd.md) | Foreground EMOSlet in Legacy; paired fast flags skip whole-file verification; retain uncertain-request journal |
| Transfer P4-local files | [P4 SD](../../p4-sd.md) | r57 candidate evidence, outside selected production; separate card/API, no guest-image lease protection |
| Type or read screen text | [Keyboard](../../remote-keyboard.md), [screen text](../../screen-text.md) | Prior EMOS input admission; output/input ownership separate; text sampling sees only P4 pixels |
| Reset or recover ROM | [Reset](../../bench-reset.md), [recovery](../../mos-recovery.md) | Different operations; private commissioned configuration and independent boot/readback checks |
| Build or review in an emulator | [Building](../../building.md), [emulator setup](../../emulator-setup.md) | Clean identified builds; Linux profile recipe has payload/runtime prerequisites; no fresh-host or hardware equivalence implied |
| Reuse P4 services elsewhere | [Shared services](../../shared-p4-services.md) | Consumer-owned runtime/adapters; all TRS-80-specific code stays in that project |
| Interpret results | [Video contract](../../protocols/browser-video.md), [qualification](../../qualification/README.md) | Browser presentation, renderer work and game pacing differ; obsolete three-mode matrix is not current authority |

## Corrections from this final pass

1. Root README no longer claims the maintained build cannot reconstruct accepted
   r55 or classifies implemented P4-local SD solely as future work.
2. Handbook/P4 SD wording distinguishes historical candidate acceptance from
   today's installed peer firmware. No new acceptance or promotion is implied.
3. Package verifier documents Python 3.11/PyYAML requirements; recovery identifies
   Linux udev/PySerial requirements; reset documents the maintained command and
   prerequisite SSH/noninteractive sudo/tool configuration.
4. Mainboard SD timeout wording now separates per-RPC retry deadlines from the
   fixed status timeout and full-transfer duration. Host whole-file buffering and
   lack of whole-file resume are explicit.
5. Host-client bootstrap and P4-card discovery no longer require finding build
   instructions or confusing the two SD services.

## Remaining gaps and owners

| Gap | Owner / disposition |
|---|---|
| Selected browser has no explicit 30-fps ceiling despite accepted policy | QUAL-003 / BENCH-005, F008; documented implementation-policy discrepancy, no rate changed |
| Old timing, SD and input-example runners need current startup, EMOSlet and evidence paths | BENCH-007 B07-R01; REMOTE-005 R05-10; PORT-003 P03-EX01; REMOTE-002 R02-EX01; DEMO-001 D01-EX01. Do not run old recipes unchanged |
| Held hardware digest and historical broken references | HW-002/version and archive owners, F024/F012/F016; no fabricated hashes or guessed replacement evidence |
| Four-mode conformance, parallel activation and broader electrical qualification | SETUP-005, REMED-001, QUAL-001/002 and PORT-008; existing UART acceptance does not close them |
| Browser platform/takeover/gameplay coverage, fresh-host setup and complete emulator portability | Owning input/build/profile workflows retain their validation gates; no new cross-platform pass claimed |
| Historical records not body-reviewed | Inventory retains partial/pending labels. Revisit when a current workflow depends on them, not merely because they exist |

These are dispositions, not new implementation authorization or a second task
queue. The [main audit task](../AUDIT-009.md) and [TODO](../../../TODO.md) own work.

## Evidence and limits

B68 in [CHECKS](CHECKS.md) records exact local checks and inspected subjects.
CLI help/source checks and local link resolution passed. The selected bundle
record matches the SHA-256 in `production/current.yaml`; maintained browser
`app.js` matches the recorded r55 bytes. These are file/contract checks, not a
fresh installed-image observation, archive reproduction or network test.

No network endpoint, firmware, source implementation, emulator profile, SD card,
reset or bench state was changed. Frozen installation archives and historical
measurements remain untouched. External URLs were not fetched; platform behavior,
all historical bodies and every runtime error path were not requalified.
