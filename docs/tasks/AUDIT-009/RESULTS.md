# AUDIT-009 — Documentation audit checkpoint

## Outcome

The approved unattended passes establish a [current handbook](../../README.md)
for humans and agents. Routine operation no longer starts with dated task
amendments: use [Using Extender](../../using-extender.md), then the maintained
SD, keyboard, reset/recovery and protocol guides. The same rule now governs
future documentation changes. Historical evidence remains separate; no frozen
experiment is silently reclassified as a current deployment recipe.

**The full audit remains open.** Four bounded passes prioritize external-agent
operation, current contracts and applicability within the Author's separate
one-hour allowances. Inventory and link
coverage are not body-review coverage. No code, firmware, hardware, SD contents,
network endpoint or emulator state changed. Changes are committed locally;
publication was not part of this execution contract.

## A09-03 — user-workflow coverage

**This is A09-03, the original workflow-mapping item, not A09-N03, the later
remediation-plan review.** The table below makes the existing evidence visible;
it adds no new test results. The seven workflows and all nine requested fields are explicitly mapped below.
A09-03 is complete as a documentation map, including identified gaps; this does
not mean every workflow has passed execution testing or every guide is complete.

“Desk review” means reading instructions, following their links and comparing
selected claims with source or retained receipts. Local CLI help checks did not
contact the P4. Neither establishes a fresh Mac, emulator or hardware pass.
Batch identifiers and the two reader perspectives are in
[CHECKS.md](CHECKS.md), under “Desk walkthroughs and journey map.”

| Required workflow and review points | Recorded work and current authority | Evidence and remaining limit |
|---|---|---|
| **Discover capabilities and start safely:** supported/planned features; installed/repository builds; bench ownership; Linux/Mac differences; local endpoint discovery | [Using Extender](../../using-extender.md) and [handbook](../../README.md) distinguish available services from plans and require the operator's local installed-state/access record. | B01/B03/B08 and Discover/start walkthrough. Desk navigation covered; no fresh Mac execution or verification of the live installation. Host portability follows source/retained use, not a new cross-platform test. |
| **Transfer files:** EMOSlet invocation/placement; Legacy/input prerequisites; checked/fast pairing; stage/activate; sessions/resume; backup cleanup; held-open files; SD layout | [SD guide](../../mainboard-sd.md), [wire contract](../../protocols/mainboard-sd.md) and [SD layout](../../sd-layout.md) own these instructions. `/emos/sdserve.bin`, prior input admission, journal uncertainty and application-memory limits were reconciled. | B02/B04/B06/B07; Transfer and Uncertain request/stop walkthroughs. Source and `sdcard.py` help checked; no new transfer, cleanup, interruption or resume test. Earlier physical receipts keep their original scope. |
| **Control and observe remotely:** USB/browser/agent ownership; pacing; locale/locks; capture/release/fullscreen; reset ownership; screen-text limits; video connection | [Keyboard guide](../../remote-keyboard.md), [reset guide](../../bench-reset.md), [screen-text guide](../../screen-text.md) and [video contract](../../protocols/browser-video.md) separate these services and their owners. | B02/B03/B08 and later B41 screen-text review; Observe/control walkthrough. Local keyboard/screen-text help checked. Browser/physical takeover, host-specific key behavior and timing were not newly exercised. Delivery counters are not proof of application execution. |
| **Run another project's software:** deployment paths; load/run versus utilities; RAM preservation; Legacy/ExCom; supported APIs and command deferrals | [Using Extender](../../using-extender.md), [SD layout](../../sd-layout.md), [console contract](../../protocols/excom-console.md) and [bug register](../../firmware-bugs.md) provide the operating boundaries. | B04/B06/B08 and Run another project walkthrough. Mapping and selected contracts covered; no fresh application run, exhaustive API review or universal compatibility claim. |
| **Build, update and recover:** ownership; wrappers/guards; identities; firmware selection; emulator profiles; flash approval; rollback; recovery readiness | [Build guide](../../building.md) and [MOS recovery](../../mos-recovery.md) distinguish compilation, identified deployment, reset and recovery. | B04/B08 and Build/recover walkthrough; B42/B43 later build-input review. No fresh compile, flash, rollback or recovery. Deployed-overlay reconstruction remains A09-F009. The walkthrough does **not** document an explicit emulator-profile setup/check sequence; that mapping remains incomplete. |
| **Interpret tests/performance:** mainboard/Extender; capture interference; browser/render/pacing costs; sample scope; units; historical regressions; bug disposition | [Timing guide](../../testing/game-timing.md), [capture protocol](../../qualification/capture-failure-protocol.md) and [bug register](../../firmware-bugs.md) separate measurements and diagnostic controls. | B03/B05 and combined Interpret tests/future hardware walkthrough. Selected claims and distinctions covered; no new benchmark, comprehensive historical regression review or revalidation of every bug entry. |
| **Understand hardware and future work:** DevKit/P4-PC; wiring/as-built; USB; SD ownership; HDMI/MIPI/VGA; plans versus capabilities | [Architecture](../../architecture.md), [P4-PC references](../../hardware/esp32-p4-pc/README.md) and handbook expose current versus planned scope; local bench records own actual assembly state. | B05 and combined Interpret tests/future hardware walkthrough. Scoped documentation review only; no physical inspection, new electrical qualification or new local-video capability proof. |

### Required-field accounting

Each table covers all nine requested fields. “Not applicable” means the workflow
has no such operation; it is not an unperformed test disguised as a pass.
Operational commands and version requirements remain owned by the linked guides,
not by this audit snapshot.

#### Discover capabilities and start safely

| Required field(s) | Mapping / boundary |
|---|---|
| Entry point | [Using Extender](../../using-extender.md), then the handbook's job-specific guide. |
| Host tool; Agon command | Browser/document reader; no Agon command is required for discovery. An operator or prepared startup must admit Extender input before remote typing. |
| Processor/service owners; transport | Operator owns access/readiness decisions; EMOS owns mode and input admission; P4 owns network services. Reading local documentation uses no board transport; later remote use needs the owner-provided LAN endpoint. |
| Required firmware/build; SD location | Obtain installed receipts from the owner/local bench record, not checkout HEAD. No SD file is required merely to discover capabilities; prepared startup is `/autoexec.txt` when used. |
| Output/evidence; stop/recovery | Known owner, installed combination and observed program/service state. Stop when admission, authorization or running application is unknown; no speculative typing/reset. No new installation or Mac check was performed. |

#### Transfer files

| Required field(s) | Mapping / boundary |
|---|---|
| Entry point | [Mainboard SD guide](../../mainboard-sd.md), [wire contract](../../protocols/mainboard-sd.md), [layout](../../sd-layout.md). |
| Host tool; Agon command | Host Python `scripts/sdcard.py`; at a verified admitted prompt, `EMOS LEGACY`, then `EMOS sdserve [--fast] /`. Host upload and listener fast options must agree. Exact list/get/put/activate/recover/resume/exit syntax belongs to the guide. |
| Processor/service owners; transport | Host client journals requests over HTTP to P4; P4 bridges its SD service over the EMOS-owned UART link; foreground eZ80 EMOSlet performs mainboard filesystem operations. No background game/file service or command-execution API is implied. |
| Required firmware/build; SD location | Current recorded pairing is linked from the guide/AUDIT-008 hardware receipt: EMOS v0.1.19, matching P4 gateway and EMOSlet. `/emos/sdserve.bin`; application fallback `/extender/sdserve.bin`; chosen root bounds access. Sibling transaction-file exception, backups and `/agents/extender` placement follow the layout policy. |
| Output/evidence; stop/recovery | Listing/download, journal and bounded activation/verification result. Fast success omits whole-file reread verification. Keep uncertain requests, use journal recovery/resume; do not overwrite held-open files. Escape or idle host exit returns to the caller, possibly continuing EXEC. No new transfer or failure test performed. |

#### Control and observe remotely

| Required field(s) | Mapping / boundary |
|---|---|
| Entry point | [Keyboard](../../remote-keyboard.md), [video](../../protocols/browser-video.md), [screen text](../../screen-text.md), [reset](../../bench-reset.md). |
| Host tool; Agon command | Browser Connect/Capture; `scripts/keyboard.py` and `scripts/screen_text.py`; optional browser Reset Agon control. Prior `EMOS KEYINPUT extender` admission is an operator/startup prerequisite, not something a disabled remote path can type for itself. |
| Processor/service owners; transport | P4 arbitrates USB/browser/agent input and sends stock-compatible packets over UART to EMOS. Host HTTP/keyboard WebSocket and video WebSocket are distinct. P4 supplies ExCom pixels/text; Legacy VGA is not mirrored. Reset uses a separate host-to-Pi HTTP bridge and physical actuator, not P4 UART or ZDI programming. |
| Required firmware/build; SD location | Match installed browser/input firmware to its owner receipt; reset additionally requires the configured Pi bridge. No SD executable is required for ordinary admitted input/video. Startup may select input in `/autoexec.txt`; host journals stay host-local. |
| Output/evidence; stop/recovery | Input status acknowledges delivery stages, not MOS execution. Pixel-derived screen text is not MOS RAM or proof of a Legacy prompt. Release capture/held keys and retain uncertain agent state; physical keys override remote ownership. Observe guide limits for locales, locks, fullscreen Escape and takeover. No new platform/input/reset test performed. |

#### Run another project's software

| Required field(s) | Mapping / boundary |
|---|---|
| Entry point | [Using Extender](../../using-extender.md), [SD layout](../../sd-layout.md), [console contract](../../protocols/excom-console.md), application's own instructions and [known bugs](../../firmware-bugs.md). |
| Host tool; Agon command | Transfer client if needed, then physical/browser/agent keyboard at a verified prompt. Ordinary applications use their documented LOAD/RUN or installed CLI invocation; EMOSlets use `EMOS <utility>`. `EMOS LEGACY` / `EMOS EXCOM` select display route under the console contract. No universal application command is prescribed. |
| Processor/service owners; transport | eZ80 executes the application; EMOS owns ordinary VDU routing. Mainboard VDP handles Legacy output; P4 EDP handles ExCom. Remote input/file transport follows the preceding workflows; application-specific extra devices are not inferred. |
| Required firmware/build; SD location | Match application requirements against the installed EMOS/EDP receipts and supported subset. Keep game/project files in their project directories, utilities under their documented dispatch location. EMOSlet versus ordinary LOAD has different application-memory preservation limits. |
| Output/evidence; stop/recovery | Observe application-specific output/exit and final prompt; universal compatibility is not claimed. Stop on unexpected behavior, retain exact build/mode and consult the bug register. Unknown application state is not permission to inject CLI commands or reset. No application was run for this mapping. |

#### Build, update and recover

| Required field(s) | Mapping / boundary |
|---|---|
| Entry point | [Build guide](../../building.md), [version policy](../../versions/README.md), applicable deployment receipt and [MOS recovery](../../mos-recovery.md). |
| Host tool; Agon command | P4 wrapper/identified builder and EMOS Makefile/build tooling are linked in the guide. Compilation has no Agon command. Flashing requires the reviewed payload/procedure and authorization; `FLASH` submission alone is not success. Emulator setup is owned by canonical `agon-dev-env` instructions; see the explicit public-guide gap below. |
| Processor/service owners; transport | Host tools build images. Authorized P4 deployment uses its documented programmer; eZ80 ROM update uses the chosen MOS update/recovery procedure. P4 ZDI recovery is distinct from the Pi reset actuator. Emulator host execution uses a profile-local launcher, not physical bench transport. |
| Required firmware/build; SD location | Record exact source/toolchain/build identity and known recovery payload. Base `p4-console` is not proven equivalent to all deployed overlays (A09-F009). Maintained install/recovery SD files belong under `/extender`, evidence/backups under `/agents/extender`; emulator SD mapping is profile-owned, not the physical card. |
| Output/evidence; stop/recovery | Identified images/manifests, independent flash/readback and separate boot/input/service receipts where required. Preserve rollback and pre-erase ROM evidence; stop on mismatch or missing completion. No build, emulator launch, flash or recovery performed. |

#### Interpret tests and performance

| Required field(s) | Mapping / boundary |
|---|---|
| Entry point | [Timing guide](../../testing/game-timing.md), [capture controls](../../qualification/capture-failure-protocol.md), retained result and [bug register](../../firmware-bugs.md). |
| Host tool; Agon command | Reading retained results needs no tool beyond a document reader and no Agon command. Fresh timing uses the named builders/runner and fixture-specific startup only under its own contract; it is not selected by this map. |
| Processor/service owners; transport | eZ80 game work/pacing and ESP renderer timestamps have distinct owners/clocks; network presentation is another measurement. Diagnostic UART replies/serial collection and browser Ethernet are not interchangeable timing scopes. |
| Required firmware/build; SD location | Each retained run names its diagnostic mainboard/P4 and client identities. Fresh runs must refresh historical fixture paths to current SD policy; records belong under `/agents/extender`. Reading results has no firmware or SD prerequisite. |
| Output/evidence; stop/recovery | Scoped tables, units, clock limits, error/probe counts and capture-interference controls. Never reinterpret missing data as zero cost or failed capture as a renderer defect without its control. Recovery/restoration belongs to the selected test contract. No timing or bug reproduction performed. |

#### Understand hardware and future work

| Required field(s) | Mapping / boundary |
|---|---|
| Entry point | [Architecture](../../architecture.md), [P4-PC reference library](../../hardware/esp32-p4-pc/README.md), handbook and owning task. |
| Host tool; Agon command | Document/schematic reader; no Agon command or hardware tool is needed for this research workflow. |
| Processor/service owners; transport | Owner's local bench record identifies the assembled DevKit. EMOS owns mainboard SD mediation; future P4-local storage is a separate service. USB acquisition is P4-owned. Proposed HDMI/MIPI/VGA paths remain subject to their own integration; vendor examples are not Extender output implementations. |
| Required firmware/build; SD location | No firmware/SD prerequisite for reading references. Actual operation requires a profile-specific receipt; DevKit evidence is not P4-PC qualification. Mainboard application storage and planned P4 card storage are not interchangeable. |
| Output/evidence; stop/recovery | Provenance-bound documentation and an explicit supported/planned distinction. Stop before assuming construction or electrical compatibility; wiring/power/testing require their own review. No physical inspection or new video capability proof. |

### Mapped gaps and retained limits

1. **A09-F009 resolved for the current DevKit combination:**
   [R01-08](../RELEASE-001/R01-08.md) records clean reconstruction, physical
   acceptance and the current bundle. Broader compatibility remains unqualified.
2. **A09-F060 — emulator setup documentation:** the build guide depends on a
   configured Fab profile but does not supply a self-contained external-user
   setup/verification path. Canonical `agon-dev-env` instructions cover generated
   profile-local launchers, pinned MOS, SD mappings and host libraries, but this
   pass neither provisions a profile nor validates macOS setup. Existing A09-04/08
   own documentation reconciliation; any coupled profile/tool change retains its
   explicit human validation gate. Do not turn this into an improvised launch recipe.
3. **Installation-local input is intentional:** endpoint, ownership, current
   wiring and flashed-build identity must come from the operator/private record.
   Their absence from public Git is not an incomplete public configuration dump.
4. **Mapping is complete; qualification is not:** the runtime limits in each row
   remain with their existing owner tasks. This follow-up only read current guides
   and completed traceability; it did not reproduce historical acceptance.

## What changed

| Subject | Result |
|---|---|
| Entry points | Compact root README/HANDOFF, one handbook index, shared operating and build guides; local agent instructions point to the same authorities |
| SD transfers | Current `/emos/sdserve.bin`, prior keyboard admission, checked/fast pairing, journals, foreground return and open-file limits; corrected exact FINISH/ACTIVATE/readback claims |
| EMOS | Current resident ABI replaces cancelled loader prose at its stable path; current utility/SD documentation and integration summaries reconciled |
| Browser/control | Current input arbitration and platform limits, one video wire authority including retained codec extensions, distinct video and keyboard ownership |
| Reset/recovery | Supported Pi reset separated from ROM recovery; maintained recovery requires verified durable pre-erase dump and full post-write comparison |
| Architecture/hardware | Working service boundaries separated from future requirements; held r02 isolation not applied to active direct r03; Legacy SD admission reconciled |
| Procedure/example reuse | Current applicability indexes; old fixed-path and application-listener helpers require owner refresh; relative-output fixture instructions corrected |
| Evidence/status | Old instructions removed from current manuals; frozen procedure reuse limits and later task dispositions explicit; no blanket new acceptance |
| Task summaries | Current capability and main porting summaries reconciled; accepted framing/query repairs and recovered ROM no longer hidden behind obsolete planning/recovery instructions |
| Tool and decision discovery | All 48 Extender and 17 EMOS root scripts indexed by role; decision metadata indexed separately from implementation/qualification |
| Historical fixture boundaries | Old provider-media staging, physical qualification and keyboard/text fixture prerequisites distinguished from current combined console/EMOSlet use |
| Screen readback | Recurring instructions promoted from BENCH-006 to one source-checked guide, including shared-result and timeout/error limits |
| Deferred studies / build decisions | Test pacing and delta rollback summaries reconciled; Pi browser reset separated from deferred direct-P4 reset; current build parameters and unimplemented updater boundary explicit |

## Coverage

Inventory excludes the audit's own bookkeeping documents. It includes newly
promoted guides, relevant help producers and a few explicitly identified local
operational records. Vendor/archival classification is not verification of all
its contents. Every record has a disposition in [INVENTORY.csv](INVENTORY.csv).

| Review state | Extender | EMOS | Total |
|---|---:|---:|---:|
| Current body reviewed within recorded scope | 96 | 18 | 114 |
| Partially reviewed / selected claims only | 114 | 32 | 146 |
| Historical metadata classified, body not reviewed | 118 | 22 | 140 |
| Vendor/reference provenance role only | 44 | 0 | 44 |
| Pending body review | 625 | 39 | 664 |
| **Inventory total** | **997** | **111** | **1108** |

Forty-seven bounded batches and two documentation-only reader walkthroughs are
recorded in [CHECKS.md](CHECKS.md). Reviewed means the document's stated contract
was inspected against the sources/evidence listed there; it is not a fresh
hardware or independent fresh-machine acceptance.

## Checks and limits

1. Local SD/keyboard/screen-text/recovery CLI help succeeds. Examples were
   inspected against parser/source; no endpoint contacted and no build executed.
2. Qualification generator reproduces all 17 tracked outputs using the
   documented virtual environment. Its superseded mode candidate remains
   superseded. Canonical dependency-graph validation passes for its own reviewed
   baseline, not the installed P4 overlay chain.
3. Relative Markdown destination/anchor scan finds no new broken links in
   revised current guidance. Three predecessor-hardware targets and fourteen
   migration-handoff targets remain historical defects, explicitly inventoried.
   Existing ignored-file targets in revised tracked guides were also checked;
   the public handoff no longer links to an untracked AGENTS file.
4. Whitespace and newly added private-path/address checks pass. The aggregate
   version validator still rejects the unchanged held r02 connectivity hash;
   documentation work did not rewrite it or manufacture new acceptance.
5. External HTTP destinations, all Markdown syntaxes, every historical body,
   fresh public-clone reproduction and macOS execution were not requalified.
   Details and scan totals are in CHECKS; this is not an exhaustive link proof.

## Remaining consequential issues

| Finding | What remains | Existing owner |
|---|---|---|
| F009 | Base P4 builder does not reproduce the deployed snapshot/overlay combination; a clean public rebuild is not established | RELEASE-001 / PORT-003 build owner; preservation complete, reconstruction pending |
| F008 | Accepted 30-fps normal contract and authorized 60-Hz retained experiments need final configuration/policy reconciliation | QUAL-003 / BENCH-005 |
| F019 | Retained timing runner selects mode in EXEC and uses the ordinary listener fallback; refresh procedure before reuse | BENCH-007 |
| F020 | Frozen SD qualification r01 predates current EMOSlet/reset operation; refresh before another qualification | REMOTE-005 / SD qualification owner |
| F035 | Fixed-path examples and old qualifier/service handovers need code/procedure refresh before reuse | PORT-003, REMOTE-002, DEMO-001 |
| F024 | Held r02 hardware connectivity digest mismatch predates audit | HW-002 / hardware-version owner |
| F040 | Draft-status definition conflicts with physically tested artifacts still recorded as draft; no silent promotion | Version-policy owner / A09-05 |
| F046 | Historical EMOS keyboard fixtures need current placement/readiness review before reuse | INTEG-009 |
| F051 | Historical storage-probe receipt paths need current placement review before a new physical run | AUDIO-001 / REMED-003 |
| F012, F016 | Historical cross-references need provenance repair; current handbook does not depend on them | Hardware archive / EMOS migration record owners |

[FINDINGS.md](FINDINGS.md) records all 52 findings and their dispositions.
Assigning an owner or exposing a gap does not authorize a fix or bench run.

## Exact continuation

The remaining-current-summary batch and first ten build decisions have been
reviewed within the recorded scope. The next ten documents are now divided into
[A09-N01–N04 in the main task](../AUDIT-009.md#next-phase), which owns the
actionable checklist and completion boundaries. A09-N01–N04 are complete within
their recorded scopes. Select a further bounded review with the Author before
starting another tranche; this continuation note grants no new scope.

Long histories remain partial until actually reviewed. Routine use already
starts at the current handbook; archive completion is not a new operational
prerequisite. No new bench or deferred implementation is selected.

## Second-pass local verification

No source, tool, firmware, SD, network endpoint or emulator changed. EMOS had
no new edits during this pass. Hardware-object validation passes for 41 objects;
all 39 P4-PC original/derivative hashes match provenance. Numeric-runner help
was checked without compiling or running regressions. The current local link
scan covers 712 Markdown files and 2465 links, retaining only the three known
historical hardware missing targets. No new changed-document failure appeared.
The earlier known version-record failure remains unresolved; no frozen digest
was rewritten. Documentation source checks are not fresh hardware acceptance.

The second tranche reached its checkpoint in about 17 minutes, below the
one-hour budget. Local commits separate architecture reconciliation, procedure/
example consolidation, and evidence/status closeout. No push was requested.

## Third-pass local verification

The next tranche completed the ten-task capability batch plus decision/tool
navigation, policy wording, fixture applicability and main porting summaries.
All 48 Extender and 17 EMOS root scripts are indexed; most helper bodies remain
only partially reviewed. No helper, emulator, build, endpoint or bench operation
was executed. Script descriptions were parsed without importing their modules.

The local scan covers 713 Extender Markdown files / 2577 inline relative links
and 76 EMOS files / 283 links. Only the same three historical hardware targets
and fourteen historical migration targets are missing; no revised-current-guide
failure appeared. Whitespace, new private-path/address additions, script index
coverage and task-detail links were checked locally. This is not an exhaustive
Markdown parser, external URL check or fresh-machine operation test.

Local commits preserve the documentation changes in both repositories; no push
was performed. The full audit remains open, with explicit coverage rather than
an implied acceptance of unread historical bodies.

This third tranche reached its checkpoint in approximately 22 minutes, within
the one-hour ceiling. Its recorded next batch is documentation review only.

## Fourth-pass local verification

The ten named task summaries were reviewed, followed by the first ten build
ADRs and their configuration inputs. Screen-text instructions now have a maintained
role-named guide; the task retains evidence and its local check. Networking ROM
headroom and the storage-study range were reconciled with existing measured data.
No research claim was promoted to hardware proof or a new implementation decision.

The relative-link scan covers 714 Markdown files and 2607 inline relative links,
with only the same three historical missing targets and no new changed-document
failure. All 55 Extender TODO targets and 17 sibling EMOS targets exist. New
private-path/address checks and whitespace checks pass. `screen_text.py --help`
was executed locally; no endpoint, build, firmware, SD or emulator operation.
EMOS received no changes in this pass. Changes are committed locally, not pushed.

This fourth tranche reached its bounded checkpoint in approximately 9 minutes,
within the one-hour limit. The next review batch is recorded above.

## A09-N01 result

Reviewed and reconciled ADR-0011/0012/0013 only, plus supporting current guide
navigation. Corrected stale input ownership and unresolved-version wording;
clarified the boundary between accepted design, selected source, dependency
provenance and deployed qualification. ESP32Time 2.0.6 and CRC 1.0.4 were already
selected; no code, dependency or architecture change was needed.

Batch B44 and findings A09-F053–F055 retain evidence and limits. Coverage now
stands at 108 reviewed, 146 partial, 140 metadata-only, 44 provenance-only and
670 pending records (1108 total). Full audit remains open. No bench or fresh
build/qualification performed. A09-N02–N04 await further instruction.

## A09-N02 result

Reconciled the full ADR-0015 display contract against maintained source and
retained qualification scope. Corrected obsolete generic-controller and
single-worker descriptions; documented separate timer, drawing, output and
consumer ownership. Native drawing storage remains distinct from RGB222
presentation snapshots. Consumer-demand composition and elapsed-tick accounting
do not establish 60 delivered frames/s or absence of streaming interference.

B45 and A09-F056–F057 record evidence. Coverage is now 109 reviewed / 145 partial,
with 140 metadata-only, 44 provenance-only and 670 pending (1108 total).
No architecture decision, firmware, code or physical state changed. N03–N04
remain unstarted. Earlier completed work was pushed before this tranche.

## A09-N03 result

Reconciled both remediation plans with later accepted UART/input/ExCom work,
without declaring whole-system conformance. Old global freezes no longer read
as a stop on accepted operation. F010 ownership and F016 task-status bookkeeping
are recorded resolved. Network short-write and server-lifetime corrections are
implemented and host-tested; physical resilience gates remain open. F018,
parallel activation, full electrical qualification and matrix replacement are
not closed by this documentation pass.

B46 and A09-F058/F059 record scope and evidence. Historical execution and
P001–P044 provenance records remain intact. Coverage is 111 reviewed / 145 partial,
140 metadata-only, 44 provenance-only and 668 pending (1108 total). No code,
architecture decision, generated model or bench state changed. N04 is unstarted.

## A09-N04 result

Current instructions now distinguish accepted source infrastructure, superseded
driver proposals and still-unqualified electrical claims.

| Document | Correction | Coverage / remaining limit |
|---|---|---|
| SETUP-004 | Replaced generic-controller and application-only keyboard guidance with accepted native framebuffer, P4 input and EMOS routing ownership; separated audio/storage plans and hardware revisions. | Partial: current instructions and selected dispositions reviewed. Long historical driver records, generated surveys and every source claim were not revalidated. |
| PORT-001 | Points routine dependency work to the promoted guide; original proof selection and review gates are completed history. | Body reviewed; no graph regeneration or new build. |
| PORT-002 | Removed obsolete review pause and qualified original absence-of-vendoring claims against current source-baseline records. | Body reviewed; declared profiles remain distinct from live firmware selection. |
| QUAL-002 | Distinguished the held r02 complete circuit from bounded r03 UART use, and inactive Legacy from EMOS-admitted services. Removed obsolete instruction to resume a suspended proposal. | Body reviewed; full electrical qualification remains on hold. No hardware inspection or tests. |

B47 and A09-F061–F063 record scope and corrections. Coverage is now 114 reviewed,
146 partial, 140 metadata-only, 44 provenance-only and 664 pending (1108 total).
All four N01–N04 steps are complete; the overall audit remains open. No code,
architecture decision, generated model, firmware or physical state changed.
