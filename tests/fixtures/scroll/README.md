# Pattern scrolling fixture

Builds one finite eZ80 program containing eight one-pixel, mainboard-vblank-paced
individually callable cases: full and partial up/down/left/right. Revision r03
checks the invoking display's current mode, switches only if needed, waits for
settling and restores the entry mode/CLI. It leaves the display route unchanged.
The builder never launches hardware. Mode, width, height, margin, palette, steps and output path
are parameters; the same executable reads `scroll.cfg`. Default320×240 geometry
uses256×240 vertical and320×176 horizontal partial regions.

```sh
.venv/bin/python tests/fixtures/scroll/build.py \
  --output agents/scroll001/fixture-local \
  --toolchain-bin "$AGONDEV_BIN" \
  --result /agents/extender/results/scroll-local.csv
```

The directory `package` contains `scroll.bin`, eight palette-quantized patterns,
configuration, eight individual launchers and an explicit `run.txt` batch. Deployment destination is
`/extender/scroll-r01`; create `/agents/extender/results` separately. The result
must be new: the fixture refuses overwrite. The builder requires Pillow and
host-native AgonDev, plus installed librsvg/Cairo. Use another fresh output for
each build. Generated outputs stay ignored.

1. Read the [test appliance lifecycle](../../../docs/procedures/test-appliances.md)
   and current bench/execution protocol before deployment. Do not modify
   autoexec. For interactive preselection, supply `VDU 22 n`, wait at least one
   whole second after the switch, then provide the explicit test invocation.
   The appliance restores the mode present after that interactive preselection;
   it cannot remember the mode that preceded the Author's VDU command.
2. Prepare matched diagnostic mainboard/P4 images and a fresh CLI handoff.
   The fixture's private QTG capability probe refuses an old/ordinary image.
3. After readiness is confirmed, the operator selects Legacy or display-preserving
   ExCom through EMOS. Invoke one case with, for example,
   `EXEC /extender/scroll-r01/full-up.txt`, or all eight with
   `EXEC /extender/scroll-r01/run.txt`. Batch dispatch calls the exact same
   `run_case` function as an individual invocation and stops at the first failure.
   The program has no implicit run-all default: missing/invalid selection prints
   usage and executes no case.
4. Each case's mode/direction label is part of its moving pattern. Full-screen
   extent1 moves every pixel; partial extent2 moves only the graphics viewport.
   A clipped PLOT restores the one-pixel wrapped strip from the resident image.
   Bitmap loading, SD writes, diagnostic replies and announcements are outside
   the measured case. Never use a pixel read or foreground flush as a fence.
5. The fixture restores its entry mode and leaves a conspicuous completion,
   failure or cancellation cue on the invoking output. The Pi coordinator owns
   whole-suite cues on both displays and restores its earlier pre-suite route.
   Escape cancels updates and attempts the normal diagnostic drain. Cleanup
   failure prevents a PASS result. Physical behavior remains untested.

Manual command form, once installation/startup readiness is established:

```text
CD /extender/scroll-r01
LOAD scroll.bin
RUN &040000 full-up
```

Select `full-up`, `full-down`, `full-left`, `full-right`, `partial-up`,
`partial-down`, `partial-left`, `partial-right`, or `all`. Add an optional
24-character alphanumeric/dash/underscore run label, for example
`RUN &040000 full-up retry2`, to retain a repeat without overwriting results.
The configured result base acquires a route (`mb`/`ext`), selection and optional
label suffix. Individual results and batch results therefore do not collide.

CSV metrics retain the established QTG measurements1–8. New9/10are scroll
execution sum/calls and maximum/boundary crossings;11/12are bitmap sum/calls
and maximum/crossings. Metric2is all primitive execution;4is final software
sprite housekeeping. Their sum is total measured rendering work. Scroll and
bitmap are subsets of2and must not be added again. Metric1is a wall window
including pacing; its count column is the final normal-worker drain inµs.
Metric8is256timer-pair overhead controls, not a render sample.

All renderer values are local monotonic ESPµs, measured at normal operation
boundaries. They exclude vblank/queue/native-lock waits but include preemption
and diagnostic overhead. They are not exclusive CPU or scanout time. The
eZ80/MOS clock advances by2per mainboard vblank (nominal120units/s at60Hz).
`missed_slots` describes application submission pacing, not proved renderer
completion per frame. `SUITE,start,end,duration` retains whole fixture MOS ticks,
including loading/retrieval/write work. The PASS line requires the selected case
or all eight batch cases,
expected scroll/bitmap counts and no reported measurement-boundary crossings.
Run `--instrument 0` controls separately with the identical program and geometry.

The appliance waits160MOS ticks after an actual mode change: nominal1.33s at60Hz
or1.14s at70Hz, outside measured work. Stopped-clock waits have finite instruction
budgets. Double-buffered entry modes are gated until a supported visible-CLI
cleanup exists; one final swap does not make later typing visible.

The [Pi coordinator](../../../docs/testing/scroll-suite-runner.md) provides a
16-job stopped plan and receipt-driven sequencing. Host simulation and native
eZ80 compilation pass; its live adapter and the new lifecycle remain physically
unqualified. The earlier deployed r02 package is unchanged by offline builds.
No new installed-firmware, timing, visual or performance acceptance is claimed.
