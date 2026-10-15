# Pattern scrolling fixture

Builds one finite eZ80 program containing eight one-pixel, mainboard-vblank-paced
cases: full and partial up/down/left/right. It does not change video modes or
launch hardware. Mode, width, height, margin, palette, steps and output path
are parameters; the same executable reads `scroll.cfg`. Default320×240 geometry
uses256×240 vertical and320×176 horizontal partial regions.

```sh
.venv/bin/python tests/fixtures/scroll/build.py \
  --output agents/scroll001/fixture-local \
  --toolchain-bin "$AGONDEV_BIN" \
  --result /agents/extender/results/scroll-local.csv
```

The directory `package` contains `scroll.bin`, eight palette-quantized patterns,
configuration and an explicit `run.txt`. Deployment destination is
`/extender/scroll-r01`; create `/agents/extender/results` separately. The result
must be new: the fixture refuses overwrite. The builder requires Pillow and
host-native AgonDev, plus installed librsvg/Cairo. Use another fresh output for
each build. Generated outputs stay ignored.

1. Read the current test/startup/bench protocol before deployment. Select mode
   in autoexec; startup ends in Legacy and never launches the fixture.
2. Prepare matched diagnostic mainboard/P4 images and a fresh CLI handoff.
   The fixture's private QTG capability probe refuses an old/ordinary image.
3. The operator selects Legacy or display-preserving ExCom through EMOS, then
   explicitly invokes `EXEC /extender/scroll-r01/run.txt`.
4. Each case's mode/direction label is part of its moving pattern. Full-screen
   extent1 moves every pixel; partial extent2 moves only the graphics viewport.
   A clipped PLOT restores the one-pixel wrapped strip from the resident image.
   Bitmap loading, SD writes, diagnostic replies and announcements are outside
   the measured case. Never use a pixel read or foreground flush as a fence.
5. The fixture leaves a conspicuous completion/failure cue on the current output.
   It asks EMOS for the other route with display retained, repeats the cue there
   and finishes in Legacy. Physical notification behavior remains untested.

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
including loading/retrieval/write work. The PASS line requires all eight cases,
expected scroll/bitmap counts and no reported measurement-boundary crossings.
Run `--instrument 0` controls separately with the identical program and geometry.

Status: offline draft. No installed-firmware, physical timing, wrap, visual,
notification or performance acceptance is claimed.
