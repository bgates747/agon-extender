# NET-004 control transmit diagnostic

Retain the cause of the first failed UART1 control transmission before EMOS
recovery changes its pins and state. Source and finite compiler work are selected;
hardware installation and one reproduction require a fresh stopped handoff.
No production behavior, feature removal or uncertain replay is selected.

## Scope and evidence

MechAgon selected this owner work on2026-11-05 under Smith's delegated RENDER
assistance. Extender owns EMOS/P4 transport; MechAgon owns its consumer/host
controller and remains the sole hardware operator until an explicit handoff.
Publish this plan before code. Existing N04-007 coexistence work remains open.

The actual first-error snapshot records SUBMIT132 after600 raw clock units,
accepted0, fault_requested1, key_faulted0, serializer reserved/transitioning1.
The NP control request remains unacknowledged. In the matched source,
send_reserved requests a fault after transmit failure; wait_reply alone does
not. Sustained CTS/FIFO readiness blockage is a hypothesis, not an established
production defect. Neither late RFC25 BUSY31 nor the first successful FRAME
establishes a renderer deadlock. Retain the informative original runs.

## Work and stopping points

N04-011.01 Publish this task and the consumer/owner boundaries before code. [x]

N04-011.02 Add an explicitly selected diagnostic composition that retains the
first failure: prefix/body, remaining bytes, last already-read LSR/Port C sample,
return reason and deadline/progress. Snapshot before fail() recovery; no extra
acknowledging UART reads, per-byte UART logging, checksum, replay or bypass. [x]

N04-011.03 Fit the complete matched ROM within131072 bytes, including stored
data and identity. Current matched image uses131068 bytes. Prefer eliminating
duplicated code/using existing storage; retain every feature and admission,
deadline, callback, bootstrap and error guard. If fit needs a feature tradeoff,
stop and present concrete options to the driver before making it. [x]

N04-011.04 Reuse mandatory startup, baud, parallel-upload, keyboard, console,
RFC25 and actual paired endpoint checks. Add focused diagnostic assertions for
first-fault retention, blocked CTS, nonempty FIFO, error and deadline cases.
Use normal Pi FIFO for one finite single-compiler build/check tranche. [x]

N04-011.05 Publish exact source, binary, map, trace layout and host-build evidence.
Bind consumers to the new actual KBvector/map. The public-only native198 remains
distinct from native199's private resident-memory snapshot; do not run the latter
against changed addresses without an explicit rebuilt binding. [x]

N04-011.06 After separate stopped hardware handoff, select one finite reproduction
with existing bounded P4 USB failure capture. Preserve both endpoints, stop at
the first failure, and follow normal recovery without replay. No target action
is released by the current source/build selection. [ ]

N04-011.07 Choose a production correction only from actual attributed evidence;
then reuse four-case echo and the separately selected matched coexistence case.
Restore normal CLI/mode/callback/startup/input and provide a stopped handback. [ ]

## Build limits and provenance

Use the maintained EMOS native branch and repository firmware-check wrapper,
retaining all selected linked validators and NETP/RFC25 composition. Keep the
P4 image unchanged unless source/evidence justifies a selected owner change;
existing USB-only fault records are the initial P4 evidence channel. No emulator,
benchmark, firmware flash or production promotion belongs to this build tranche.
Use a fresh identified build/output; do not overwrite retained images/maps.
Single compiler, ordinary bounded host checks, whole build/check watchdog600s;
join all owned children and release the actual FIFO token before handback.
Source/edit/mail work may proceed while queued; no compilation before checkout.
Private endpoints, paths and current hardware tokens remain in ignored records.

## Checked source/build checkpoint — 2026-11-05

Plans were published first in Extender5639a7ed and EMOS9263a08. Maintained EMOS
implementation71552879cb7e60f656ecbbc5c964ddd0e40fa416 produces both clean
identified builds with the matched netp/RFC25/controller/upload feature set.

| Composition | Identified build | Used ROM bytes | Free ROM bytes | Complete ROM SHA256 |
|---|---|---:|---:|---|
| Matched, diagnostics off | agon-emos-eirene-r04-b2026-11-06-03-24-36Z |130929|143|7d16f3b7447dfa5649b0088dc7e8fa59e6e4eff58448e5f0940fd1fbc88efea7|
| Matched, diagnostic selected | agon-emos-eirene-r04-b2026-11-06-03-24-49Z |131050|22|8270ecd709138fe5ae617a91d5d365eeede0738025d5043fc790541b19b8f281|

The prior matched image used131068 bytes/4 free. Sharing the existing deadline
and initializer saves139 bytes in the ordinary composition; the selected
diagnostic adds121 ROM bytes and19 BSS bytes. No feature or transport guard was
removed. All six existing mandatory validators and the new exact native-byte
trace/layout check pass in both clean builds. Actual C deadline/reply sanitizer
checks cover wrap,600-boundary,fuse,progress,ready and fault behavior. Linked
assertions establish first-failure freeze/commit order and existing status-read
inventory; native instruction execution and hardware behavior remain untested.
Compiler200 was released after both13.18-second build/check jobs and all owned
children joined; its actual successor was immediately notified.

Both maps retain sysvars0xBC322 and KBvector0xBC38E. The selected diagnostic
exports mutable sample scratch at0xBD098 (3 bytes) and first-fault record at
0xBD09B (16 bytes); the ordinary composition contains neither. The EMOS task
INTEG-022 records the exact private layout. Generated artifacts/maps/manifests
remain owner-retained outside Git; this is no installed or production selection.

**Invocation dependency:** ordinary reset clears diagnostic BSS. The existing
public-only consumer does not persist this private record. Before spending the
single selected reproduction, the consumer owner must select an exact-map
first-error copy into application storage and durable results, or demonstrate
another concrete pre-reset capture path. The old507-byte private snapshot must
not be run against a changed map. This is an evidence gap, not a request for a
new human approval or permission to repeat a failed run. Extender retains the
actual stopped operator handoff while this dependency is reconciled; no target
flash, reset or test has occurred in this preparation tranche.
