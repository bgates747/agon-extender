# Ordinary Copper palette coverage — 2026-09-13

This bounded PORT-008 increment follows sprite coverage. It checks retained
scanline palette selection through ordinary MOS EXEC/VDU input, without
changing the renderer, firmware, accepted Rally installation or startup.
Observations remain headless and local; Author visual and publication review
remain open. The paired QUAL-003 timing tranche and Golem remain out of scope.

## Bounded plan

1. [x] P008-K01: Read the official Copper contract, palette/list lifetime and
   active P4 row binding. Define independent row-colour expectations and a
   finite cleanup procedure before writing the input generator.
2. [x] P008-K02: Generate setup/edit/replace/reset/cleanup scripts in indexed
   modes9,10,11. Cover primary versus secondary palettes, copy/automatic
   creation, wrapped entry indices, active deletion/recreation, first-block
   list input, owned-buffer release, shorter replacement/tail extension and
   software versus hardware sprite colours. Choose modes outside each script.
3. [x] P008-K03: Capture each stage with canonical stock headless profiles and
   check literal pixels including row boundaries and untouched halos. Preserve
   informative stock deviations explicitly; never repair inherited rendering
   merely to make these checks pass. Reject an intentionally wrong image.
4. [x] P008-K04: Only after completed SD transfer/readback/service-exit and
   passing native checks, execute the same stages sequentially on physical P4
   through EMOS ExCom. Capture independent EVF output and check literal pixels.
5. [x] P008-K05: Reset the Copper list, individually delete owned palettes,
   reset sprites/flags, restore palette and Legacy; verify unchanged startup,
   exact SD inputs, service exit and released keyboard admission. Record
   identities, evidence, results and limits without committing or publishing.

## Source précis and expected contract

Read-only references: official VDP v2.16.0
`c7ac293d2aa81ddfa693390549bcd909069c8fc3`, MOS v3.0.2
`8336409351ee5314e02801a7b72a4f1bb5282519`, agon-docs
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`. The exact official documentation
is `docs/vdp/Copper-API.md`, with `VDP-Variables.md`, `Bitmaps-API.md` and
`Buffered-Commands-API.md` for feature flags, sprites and list storage.

1. Copper variable0x0310 enables commands23,0,0xC4,0–4. Indexed modes use
   palette0 for drawing/quantisation; secondary palettes affect output rows.
   Sixty-four-colour output and per-VSYNC animation are outside this case.
2. New palettes copy palette0. Editing a missing ID creates it; entry indices
   wrap at the palette size. Changing palette0 later does not rewrite copies.
   Deleting an active secondary palette redirects its list entries to palette0;
   recreating that ID does not automatically relink those already bound entries.
3. A list contains little-endian16-bit row-count/palette-ID pairs. Only the
   first buffer block is consumed; the output owns its copied list afterward.
   Missing palette IDs use palette0 in the retained source. Extra rows/entries
   beyond the screen are ignored; the final selected palette covers any tail.
   Replacement can shorten the linked list; reset restores palette0 everywhere.
4. Software sprite pixels are framebuffer indices and follow Copper. Hardware
   sprite pixels retain their full-colour output, including across a palette
   boundary. This case retains sprite kind until explicit final shutdown.
5. `vdp/video/vdu_sys.h::vdu_sys_copper` owns dispatch;
   `vdp/video/agon_screen.h` owns the depth-dependent binding. Retained
   `vdp/vendor/vdp-gl/src/dispdrivers/vgapalettedcontroller.cpp` owns palette
   and list operations and `getSignalsForScanline`. Its all-the-plots baseline
   is `ac2dd5986daf496c43ae8e7fe41836274aec54a0` (PORT-003 R1 provenance).
   `stock_runtime_controller.hpp::prepareRow` rebinds the saved list cursor
   after palette/list revision changes under the native guard; ordinary rows
   keep the stock sequential lookup. `stock_scanline.cpp` owns retained row
   expansion and hardware-sprite decoration. These are the selected P4 paths.

This is a static visible-state case, not a concurrent mutation stress test,
scanout/performance measurement, all-modes test or complete API qualification.
Use only a few owned IDs. Delete palettes individually: retained delete-all
iterates a map while recursively erasing its elements, so its iterator lifetime
needs separate investigation before physical use. This inspection is not a
reproduced delete-all failure. Empty/malformed lists, exhaustion, mode changes
with active Copper, hardware sprite clipping and callbacks are excluded.

Exact private bench identities, recovery access and root startup are owned by
HARDWARE.local.md. Generated inputs, oracles, captures and journals live in the
ignored agents/copper-coverage and agents/video-throughput buckets. Every new
run uses fresh names and binds actual input/runtime hashes. No new firmware
identity or broadly qualified fixture is implied by these exploratory inputs.

## Stage design

Six independent tiles include two 180-row strips and small masked bitmaps and
sprites. One strip is drawn before Copper starts; the other is first drawn
after primary-palette mutation. Each row boundary and each tile's two-pixel
halo is checked. Hardware pixels are cyan; software pixels use primary index1.
Unused primary entries are black, keeping white sprite quantisation unambiguous
when primary white becomes light grey. The copied palette remains white.

Setup selects primary/red/green/blue/copied-white/missing-ID bands, with a
short first block whose final primary band extends to the bottom. A second
block would turn the tail blue if wrongly concatenated, or the entire strip
blue if wrongly selected alone. Edit changes primary to light grey, red to
magenta and blue to green; deletes/recreates the active green palette, proving
its old rows stay redirected to primary. Replace explicitly recreates the
copied palette and installs a shorter four-node list: cyan/light-grey/magenta,
with the fourth entry beyond the screen. Reset returns every framebuffer row
to primary; cleanup removes the sprites and clears the test drawing.

The first native case 02 passed the selected states, but its overlong first
list could not distinguish ignoring versus concatenating extra buffer blocks.
Final case 03 strengthens that assertion before physical use. The independent
ideal output remains identical; new exact-input native captures are required.
Case 01 was an unexecuted generator draft. These refinements concern test
coverage, not observed port failures. All earlier identities stay separate.

All 15 final case 03 native stages pass 90 independent tile-state comparisons,
49,260 logical pixels including halos. No stock-parity exception is needed.
Negative images reject a missing hardware sprite (16 pixels), stale setup
colours (1,345 pixels), and incorrectly concatenated second-block tail (80
pixels). These are pixel checker discrimination checks, not additional renderer
runs. Native manifests bind exact inputs and unchanged stock runtime; physical
sequential execution and recovery remain the next gates.

## Physical result and scope closure

Case 03 passes all 15 physical stages on the unchanged P4 candidate: setup,
edit, replace, reset and cleanup in modes 11, 10, 9. The final EVF snapshot of
each stage passes the same independent ideal oracle as stock native. There
are 90 tile-state comparisons and 49,260 checked logical pixels, including
halos. No parity exception, renderer correction, firmware build or flash was
required. P008-K01–K05 are machine-complete for this finite contract. Human
visual/commit/publication review and wider command qualification remain open.

The 15 five-second windows received 4,512 snapshots, all 320×240, with zero
sequence gaps, overflow or browser errors within each window. Those counts
describe static receive observations, not Copper animation cadence, game
framerate or scanout performance. Only the declared captured states received
pixel assertions; do not imply all 4,512 payloads were retained or checked.

An additional first-snapshot check deliberately remains separate. Every new
connection initially receives retained older pixels; for all 14 transitions
within this case, the first snapshot exactly matches the preceding stage's
oracle instead of the new one. The final snapshots all match the new stage.
This is consistent with the documented on-demand producer and retained latest
snapshot: `presentation_snapshot_pool.cpp::tryBegin`, `tryAcquireLatest` and
`releaseLease` do not continuously compose while the browser is absent.
The new consumer can lease an existing latest generation before requesting
new composition. These first-frame failures and previous-state comparisons
remain preserved; they are not silently counted as current-stage passes or
diagnosed as failed Copper execution. This case does not qualify reconnect
freshness or quantify how many intermediate frames retain the previous state.

Exact evidence is under ignored `agents/copper-coverage`:

1. `depth*-case03` contains input/oracle pairs; `input-summary03.json` and
   `source-identities03.json` bind exact input, generator, checker and source
   identities. Earlier case versions remain distinct.
2. `native-summary03.json` references stock captures; corresponding canonical
   runtime manifests live under `agents/video-throughput/copper-*-stock03`.
3. `physical-summary03.json`, `physical-evidence-index03.json` and
   `p4-depth*-*-case03` retain successful final EVF/PNG/pixel checks and receive
   records. `observer-summary03.json` retains actual layouts/counts.
4. `first-frame-summary03.json`, `first-frame-previous-state03.json` and each
   capture's `first-pixels.json` preserve the reconnect distinction above.
5. `negative03` retains absent-sprite, stale-state and wrong-tail rejections.
   `transfer03`/`recovery03` bind completed SD readbacks and service exit.

| Depth | Setup bytes / SHA256 | Edit bytes / SHA256 |
| --- | --- | --- |
| 2 | 1542 / ec40cc9f177bedd0af85202119cc57354d86be01db0ffa8f2f3c69d7a8601211 | 282 / c2134961c0897404688fbb338d8299f2b759f447cf45d4f8c7747d1519bb006b |
| 4 | 1582 / 67e2a7e197904c671d41d6a4381999ff21d15ff52655c656e9304fb0431dc653 | 282 / 8f2666655f3aa18d09cb52f4a1f2c4d05db24fd18cef0d13f26f1caba59ba779 |
| 16 | 1829 / 6a9cee61090b72a7585a99c2e11e078cfac0b30f9f799fcdccc8a4c908c627a0 | 283 / ef55e9f3b154212f4115f0738b910901db5d758fa9453bbcb79943ad565ddf39 |

Replace is 225 bytes, SHA256
`c9addead9c6d03ad51a62d5bf6a1a89208635bdd49285f1c55f1c9d0d2803dac`;
reset 193 bytes, `9837b6dd809b146ae51db028f182b9502e186921c6931aa4d8844c4d2c1809d5`;
cleanup 260 bytes, `53edca3cf422123cdc99babf8555116d4e9e4d31f2fabea1f071bbb5912b1a6b`.
These three inputs are identical across depths. Final generator SHA256 is
`5589fbb1a228cda862afe6088651c301f2636a20ac6ef463bda9d4cc6ce7f9f3`.

Final cleanup resets Copper/sprites, deletes owned resources individually,
clears flags and restores the normal palette. Ordinary EMOS returns to Legacy
and mode 3; sdserve reads back unchanged startup and all 15 inputs, then exits
with no pending request. Final keyboard status matches the owned canceled
session and boot, ready/neutral/released. No game or observer remains active.
Private access, exact installed candidate and terminal state remain in
HARDWARE.local.md. EMOS, stock onboardVDP, accepted production Rally, startup
and wiring are unchanged. No reset, attention cue, commit or push occurred.

Reproduce from the Extender root:

```text
.venv/bin/python docs/tasks/PORT-008/copper-coverage/make_case.py agents/copper-coverage/new-case --depth 2
.venv/bin/python docs/tasks/PORT-008/bitmap-coverage/check_pixels.py agents/copper-coverage/new-case/setup-oracle.json <setup.png-or-evf> --output <result.json>
```

Use depth 4/mode 10 or depth 16/mode 9 for the other variants. Select the mode
externally, then EXEC/capture setup, edit, replace, reset and cleanup in order.
Use exact corresponding stage oracles and fresh isolated profiles/journals.
Do not use the first reconnect snapshot as proof of current drawing. Owned
list/palette lifetime, not malformed input, asynchronous stress or callback
timing, is the tested boundary; exclusions in the source précis remain open.
