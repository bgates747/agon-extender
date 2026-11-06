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

N04-011.01 Publish this task and the consumer/owner boundaries before code. [ ]

N04-011.02 Add an explicitly selected diagnostic composition that retains the
first failure: prefix/body, remaining bytes, last already-read LSR/Port C sample,
return reason and deadline/progress. Snapshot before fail() recovery; no extra
acknowledging UART reads, per-byte UART logging, checksum, replay or bypass. [ ]

N04-011.03 Fit the complete matched ROM within131072 bytes, including stored
data and identity. Current matched image uses131068 bytes. Prefer eliminating
duplicated code/using existing storage; retain every feature and admission,
deadline, callback, bootstrap and error guard. If fit needs a feature tradeoff,
stop and present concrete options to the driver before making it. [ ]

N04-011.04 Reuse mandatory startup, baud, parallel-upload, keyboard, console,
RFC25 and actual paired endpoint checks. Add focused diagnostic assertions for
first-fault retention, blocked CTS, nonempty FIFO, error and deadline cases.
Use normal Pi FIFO for one finite single-compiler build/check tranche. [ ]

N04-011.05 Publish exact source, binary, map, trace layout and host-build evidence.
Bind consumers to the new actual KBvector/map. The public-only native198 remains
distinct from native199's private resident-memory snapshot; do not run the latter
against changed addresses without an explicit rebuilt binding. [ ]

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
