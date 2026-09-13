# Ordinary sprite composition coverage — 2026-09-13

This PORT-008 slice follows the font, bitmap, context and palette cases. It
checks the retained sprite API and the P4 output binding through ordinary MOS
EXEC/VDU commands. It does not redesign VDP sprites, enable Golem, resume the
held QUAL-003 timing tranche or publish experimental source. The Author's
visual/commit review gates remain open; routine observations stay headless.

## Bounded plan

1. [x] P008-S01: Read the official sprite section of Bitmaps-API.md and inspect
   retained sprite dispatch, frame/background lifetime and scanline composition.
   Define literal synthetic expectations and separate software/framebuffer
   behavior from hardware/output decoration.
2. [x] P008-S02: Generate finite ordinary scripts for software sprites in
   mode8, hardware sprites in mode8, and hardware sprites over mode11's indexed
   framebuffer. Cover frame operations, visibility, movement/restoration,
   overlap, painting and mixed layer order with small owned resources. Select
   modes outside scripts and keep every MOS command below256 bytes.
3. [x] P008-S03: Execute exact scripts with canonical headless stock profiles.
   Compare literal output pixels/halos; retain stock deviations explicitly.
   Do not mistake framebuffer readback for hardware-sprite composition.
4. [x] P008-S04: Transfer exact passing/reference-bound inputs via sdserve,
   invoke sequentially through EMOS ExCom on the unchanged installed P4, and
   compare EVF output. Restore sprites/flags/palette, Legacy/SD and unchanged
   startup with neutral released keyboard admission afterward.
5. [x] P008-S05: Record evidence and unsupported cases. Diagnose any actual
   port discrepancy before changing its binding, leaving upstream rendering
   behavior intact. Do not call finite pixel checks general qualification.

## Source précis

References remain official VDP2.16.0
c7ac293d2aa81ddfa693390549bcd909069c8fc3, MOS3.0.2
8336409351ee5314e02801a7b72a4f1bb5282519 and agon-docs
f9806bd3cbff6ed5d1c08bef1d51fed11764b86b. They are read-only. The official
docs/vdp/Bitmaps-API.md owns both bitmap and sprite commands; there is no
separate Sprites-API.md in this checkout. Also relevant are VDU-Commands.md,
Screen-Modes.md and the VDP variable/feature flag documentation.

1. Sprites are sequential from ID0, with an active count. Bitmaps use arbitrary
   16-bit buffer IDs or aliases64000+byte ID. Sprite frames may differ in size;
   next/previous wrap, while an out-of-range explicit frame is ignored.
2. Software sprites save/restore background in single-buffer modes, refreshing
   after other drawing or explicit command15. Their double-buffer behavior is
   deliberately excluded. Hardware sprites are composed during output, retain
   all64 colours over indexed modes, and need the test flag variable2 set to1.
3. Hardware sprites accept RGBA8888/2222; mask input is outside this hardware
   slice. Higher IDs overlay lower IDs within a layer, and the hardware layer
   appears above software sprites irrespective of ID. RGBA2222 hardware XOR is
   supported in2.16.0; other hardware painting modes/8888 XOR use ordinary set.
4. Sprite coordinates are physical pixels, independent of graphics origin and
   viewport. Explicit refresh plus read-pixel joins are allowed for sequencing
   software operations. Read-pixel results are not evidence of hardware pixels:
   only the native/P4 presented output captures prove those overlays.
5. vdp/video/vdu_sprites.h and sprites.h own dispatch and resource references.
   Retained vdp-gl displaycontroller.cpp owns software hide/show/background;
   vgapalettedcontroller.cpp::rawDrawSpriteScanline/drawSpriteScanLine own
   hardware alpha/XOR/order. The original all-the-plots baseline is
   ac2dd5986daf496c43ae8e7fe41836274aec54a0, bound by PORT-003's R1 record.
6. P4 StockBoundController::drain calls the retained primitive and showSprites
   bodies. StockScanlineController retains the original scanline decoration
   under native-state guards. Use this active path when diagnosing output;
   the superseded custom compositor still exists but is not selected.

Use small, synthetic project-owned bitmaps. Join visible software drawing
before replacing/clearing frames, and retain bitmap storage until after final
capture and explicit sprite shutdown. Do not test deleting active bitmap data,
simultaneous clipping at both screen edges, maximal sprite counts, malformed
commands, mode7 or scanout overload in this slice. Those have distinct failure
and timing boundaries. These are source-hashed exploratory command cases, not
a new firmware lineage or released fixture. Exact bench identities, access,
rollback and startup remain in HARDWARE.local.md. No attention cue is needed.

## Stage design

The generator emits setup/update/cleanup scripts with a separate literal oracle
for each. Setup shows all declared sprites; update changes frames, positions,
visibility, storage references and layer selections. Cleanup resets sprites
while retaining the expected underlying background. Capturing all three stages
distinguishes successful restoration from a sprite that never drew at all.
Software cases use19 sprites/17 tiles; hardware cases use21 sprites/19 tiles,
including explicit software↔hardware conversion over the indexed framebuffer.
All sprite images are at most4×3 pixels, with generous separation between tiles.

The first software native pass succeeds in all three stages. Before physical
execution, case02 strengthens the viewport/origin check: setup now retains the
deliberately unrelated tiny graphics viewport and offset origin through capture.
Only the update script restores them before its ordinary background drawing.
Restoring them before the setup capture could let a later ECHO redraw sprites
under normal settings, weakening that assertion. The passing initial case and
its exact native evidence remain separate; case02 receives fresh references.

Native phase profiles reconstruct each stage by running the same prior scripts
in order. Physical runs capture setup, then update, then cleanup in one session.
Read-pixel joins sequence software rendering before mutation. The native
independent setup capture and physical stage observations prove sprites were
visible before restoration, without introducing a timer binary or emulator
keyboard injection extension. No performance claim is attached to these stages.

## Native hardware/software conversion failure

Case02's hardware mode11 setup passes its literal pixels. Its update and
cleanup profiles terminate with SIGSEGV before their scheduled captures. A
failure-only native signal trace (separate from reference runs) shows null
access in VGA2Controller::rawDrawBitmap_Native, called by hideSprites after a
refresh. The emulator wrapper and stock VDP library remain unchanged.

Retained setSprites allocates saved backgrounds for software sprites and frees
them for hardware sprites. The ordinary command20 changes the hardware flag
only. An in-place hardware→software conversion therefore has no background
allocation; showSprites records nonzero saved dimensions, and a later hide
tries to restore from null storage. This is an inherited lifecycle defect,
not evidence of a P4 transport failure. The original failing input and trace
are retained and have not been sent to physical hardware.

The next bounded diagnostic isolates this conversion with one sprite, then
checks the ordinary API workaround: deactivate the sprite set, change its
kind, and reactivate the set so retained setSprites owns background allocation.
Apply the same deactivation/rebinding boundary in both conversion directions.
Do not modify upstream sprite algorithms or quietly relabel direct active
conversion as qualified. Successful guarded conversion is a narrower explicitly
named lifecycle contract; the unsupported direct path remains recorded.

The one-sprite reduction confirms the distinction. Direct conversion followed
by refresh crashes the stock native process; adding only deactivate/change-kind/
reactivate succeeds and produces the expected quantised software pixel. Direct
input SHA256 is c16c0a8a40f8c9dbbcb9678aebc865e3a480985997592eefbd5d3e7252008325;
guarded input is be9def9531c6353efd2c256858b453e6f7cf1c7d213b4e379d659c8296e1654f.
Both inputs and the informative failures remain under agents/sprite-coverage,
with canonical native runtime manifests under agents/video-throughput.

Case03 preserves every requested visual state, while naming both conversion
tiles as deactivate/rebind operations and using the proven sequence. Existing
software input bytes remain unchanged from case02; hardware setup/cleanup also
stay identical, while update adds the explicit allocation boundary. No port or
stock source has changed. The full final cases now receive their stock checks
before physical execution. Direct active conversion remains unqualified.

All three final mode11 hardware stages pass the independent oracle, including
full-colour output over a two-colour framebuffer and both guarded conversions.
The remaining mode8 variants receive the same three-stage check. No modified
native library is used for those reference runs; the signal-trace preload is
confined to the separate failure-only diagnostic invocation.

All nine final native captures pass: 165 tile-state comparisons and 10,806
logical pixels including halos across setup/update/cleanup in the three
variants. Setup retains the displaced graphics origin and tiny viewport,
confirming those do not control the sprite output under test. Checks reject a
missing sprite layer and a stale pre-update image. Inputs and captures retain
their exact identities in agents/sprite-coverage/input-summary03.json and the
canonical native manifests under agents/video-throughput/sprite-*-stock03.
Physical sequential observations and final recovery are next.

A first physical orchestration attempt selected ExCom before the parent SD
transfer had finished. Its pixel check rejected the retained previous P4 image;
it is not a renderer result. The transfer completed normally, and explicit
Legacy/ExCom/mode selection restored the route. The local runner now requires
the completed transfer-and-service-exit receipt before sending keyboard input.
The retry uses distinct evidence names. No reset, firmware or startup change
was needed for this setup correction.

## Physical result and scope closure

Case03 passes all nine physical stages: setup/update/cleanup for software
sprites in mode8, hardware sprites in mode8, and hardware sprites in mode11.
All 165 tile-state comparisons and 10,806 logical pixels including halos match
the independent expectations on stock native and P4. This confirms the tested
visibility, frame operations, size changes, movement/restoration, XOR handling,
overlap order, viewport/origin independence, full-colour hardware output over
an indexed framebuffer, and explicitly guarded kind changes. No renderer or
firmware change was required. Direct active conversion is still the recorded
stock crash path; its guarded replacement is not evidence that it works.

The nine five-second physical observations retain 2,700 static snapshots, all
320×240, with no sequence gaps within each window. These are visible-state
observations, not sprite-throughput, animation-cadence or scanout measurements.
The exact successful run is agents/sprite-coverage/physical-summary03-review02.json;
each p4-*-case03-review02 directory retains EVF bytes, decoded PNG, observer
record and pixel assertions. The original stock crashes and the minimal
direct/guarded conversion inputs remain preserved. The ordinary setup-order
failure retains a brief correction and admission/SD journals; its superseded
image bundle was discarded under the bench evidence-retention rule.

| Variant | Setup bytes / SHA256 | Update bytes / SHA256 |
| --- | --- | --- |
| Software mode8 | 4354 / 5b63b238dadd8b59c33b9847447f8502f6b795b85399dd80a375c040e98742d8 | 924 / 9f9805a986f49ac6bccfb23d7c6c2ef5d1c664094715ba204248cdf35c33a867 |
| Hardware mode8 | 4641 / fd82aabfbe9cf81f4384518eb7cc81e8260f9b3f40aa0579686c27fc98765d89 | 1112 / ac9dd1a67a0a1d90134fb3832e179fd485b312ff3a8f5df06bb69a1d5805d488 |
| Hardware mode11 | 4639 / 42f27b0ebe1268dfc9e3028ab2ee829633cc66a6dfd16cb78bf13aa77bdb2f1d | 1111 / ffbcd08489f88d5f100b1877b47d6973376aeaf45e38a95f6e8d6bef8b293d0b |

All three cleanup scripts are identical335-byte inputs, SHA256
a84fab434c3316b05ecc809c35d4605ccde46cc6be83cc1b990b5b7cc0591e5d.
The final generator SHA256 is
eaa53d797acd815a224abb059f73631c99b61612427e9916fc083dee1d789535.
Native and input summary manifests retain the exact image/source/runtime
identities; earlier case versions remain separately identified.

Final cleanup resets sprites and test flags, preserving the expected
background. Ordinary EMOS returns to Legacy, selects mode3, starts sdserve,
and independently reads back unchanged startup plus all nine scripts. The
service exits with no pending request. A final read-only keyboard check matches
the same owned canceled session and boot, ready/neutral/released. No game or
observer remains active. P4 is still the previously installed optional
DSP-cleanup/poll1/TCP32768 r17 candidate; exact identity and private foreground
state remain in HARDWARE.local.md. EMOS, stock onboardVDP, accepted production,
root startup and wiring are unchanged. No flash, reset, attention cue, commit
or publication occurred.

P008-S01–S05 are machine-complete for the stated contract. Remaining limits
include direct active kind conversion, active bitmap deletion, larger frame
replacement needing a larger software background allocation, both-edge screen
clipping, maximal counts/scanout load, double-buffer software sprites, mode7,
mouse/text-cursor interactions and arbitrary palette/depth combinations. Human
visual review and explicit commit/publication approval remain open. These
selected states do not qualify the full sprite or command suite.

Reproduction from the Extender root:

```text
.venv/bin/python docs/tasks/PORT-008/sprite-coverage/make_case.py agents/sprite-coverage/new-case --hardware --mode 11
.venv/bin/python docs/tasks/PORT-008/bitmap-coverage/check_pixels.py agents/sprite-coverage/new-case/setup-oracle.json <setup.png-or-evf> --output <result.json>
```

Use mode8 with or without --hardware, or mode11 with --hardware. Select the
mode externally; EXEC setup.txt, capture, EXEC update.txt, capture, then EXEC
cleanup.txt and capture. Match each image to its stage oracle. Native isolated
profiles may reconstruct a stage by executing its predecessors in order. Use
canonical wrappers and existing journalled SD/keyboard clients, and bind fresh
runtime/input identities. Preserve the historical evidence when repeating it.
