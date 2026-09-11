# Original stock backend — R3 first hardware review

Status: **candidate deployed; qualitative improvement reported, residual
performance issues open**. R2 is accepted in `57a0d86`. This is a P4-only deployment; EMOS,
the repaired game and the Agon/mainboard VDP firmware remain unchanged.

## Deployment contract

1. Select the original VGA2/4/8/16/64 controllers and shared base/rendering
   units in the ordinary `p4-console` build. Explicitly forbid the old generic
   controller, planes, compositor and frame service. Enable the same runtime
   binding in both the application component and selected vendor units.
2. Use `uart-excom-console-r10` and registry r69 under the Author's standing
   identity approval. Retain the exact r09 image and known r07 rollback.
   Build a complete image from committed, clean inputs after local checks;
   verify identity, native renderer selection, flash layout and image hashes.
3. Verify the bench's stable USB identity, stage with matching hashes, write
   and independently verify flash, and collect one bounded startup record.
   Opening serial resets P4; close it afterward. Both boards stay powered
   with the existing harness seated. No mainboard VDP or EMOS flash.
4. Retain the existing startup: mode 3, Extender keyboard selection and the
   Nurples directory. The Author resets Agon with the prepared SD, opens the
   browser, selects ExCom, loads and runs repaired Nurples, declining joystick.
5. Ask the Author about sustained scrolling, repeated fire, hangs and Escape
   return. Compare the feel against the preceding severe hangs. A subjective
   result is useful first evidence; it does not establish measured speed or
   timing parity. Full R3 graphics, lifecycle and cadence qualification remains
   open. Do not automatically run the held callback benchmark.

## Build boundary

The ordinary hybrid build needs `video/` as a fallback include root for the selected vendor headers
and a C-compatible forced-header boundary around the task-only C++ Xtensa
rejection stubs. These are compiler bindings, not upstream algorithm changes.
A global include exposed a real header-name collision with libsodium's
`version.h`; the target uses GCC `-idirafter video`, so SDK component headers win
before the Extender namespace fallback. A pre-build environment clone is
inappropriate here because PlatformIO adds SDK include paths later. The source-selection hook accepts explicitly named files in `dispdrivers/`
as well as the reviewed root; it still excludes all unselected driver files.
Keep the prior R2 source/body verification and passing runtime evidence scoped
to that proof. Deployment selection receives its own build evidence here.

## Results

The complete draft image passes compilation/link and byte/selection checks:
all five native depth scroll implementations, clock/drawing/output tasks and
none of the old generic backend symbols are linked. Factory component offsets
and required QIO/80 MHz SDK configuration match. The existing source-selection
test and an exact nested-depth allowlist/rejected-subtree check pass; original
body/scanline verification still passes. The clean candidate build from `f0dc271` and physical startup now pass;
The Author reports marked gameplay improvement, with residual jerkiness and
noticeable slowdown as more sprites appear. Full qualification remains open. Local and
remote deployment details belong in ignored bench records; tracked evidence
will retain only the build identity, source checkpoint and integrity/results.


Candidate `uart-excom-console-r10-b2026-09-11-03-37-54Z` was written and
independently verified in `PORT-003-2026-09-11-03-39-04Z`. Native USB enumerated
the attached keyboard, Ethernet and HTTP started, and no startup fault was
observed in the bounded log. The serial port is closed. The unchanged EMOS
v0.1.12 and repaired game are recorded in [deployment.json](deployment.json);
[image-checks.json](image-checks.json) binds exact candidate/layout/selection.
The timing HTTP endpoint's availability is only a service-startup check; it
does not validate restored-backend frame cadence or gameplay progress.

No SD writes, automatic fixture, EMOS/mainboard flash or gameplay run occurred
during preparation. The Author now owns the manual playtest. Keep physical
60 Hz cadence, original-depth graphics coverage and sustained load checks open.


### Author qualitative Nurples observation

On the deployed r10 candidate, the Author reports: “marked improvement,” but
the game remains jerky and bogs down noticeably when more sprites enter the
mix. This is an operator observation, not a timed comparison. It supports
retaining the restoration as progress; it does not identify which changed
backend component caused the improvement or which component now limits speed.

Sprite count correlates with the observed slowdown. Native sprite work,
drawing/output exclusion, browser presentation and eZ80/UART progress have
not been separated by this playtest. No additional code, instrumentation,
flash, serial capture or benchmark was performed in response. Complete
elimination of the prior long hangs and Escape/return remain unconfirmed.
