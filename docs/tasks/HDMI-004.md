# HDMI-004 — Interactive mode preview

Build a labelled, menu-driven visual fixture for Author review of every currently
selectable P4 graphical mode. Stage on the Author-confirmed mainboard card;
leave execution to the Author. No firmware changes or automatic tests.

## Scope and state

Candidate built and deployed to the identified Extender card; Author visual review pending. The Author approved the geometry/palette pattern and
requested larger labels, then explicitly requested an interactive mode menu.
This request authorizes this fixture's mode selection through ordinary
EMOS-routed VDU commands, an exception to the usual startup-only fixture rule.
Ordinary autoexec must remain unchanged. EMOS continues to own routing.

## Instructions and gates

1. Enumerate modern graphical modes from maintained P4 source, including
   experimental 96–99; distinguish selectable modes from visually qualified ones.
2. Stream the approved raster through bounded mainboard RAM using MOS file APIs
   and public VDP RGBA2222 buffered-bitmap commands. Preserve native palette mapping.
3. Show mode number, dimensions and colour count. Present a numeric menu; Enter
   selects, a key returns to the menu, Escape exits to Legacy mode 0.
4. Provide an independent recovery command if a preview cannot be seen. Include
   double-buffer swaps and a teletext entry with an explicitly separate pattern.
5. Build and inspect generated streams; hash all deployed files. Confirm the
   actual card identity with the Author if it differs from the previous card.
6. Copy only the new fixture directory under /extender, verify hashes and
   unchanged startup, and leave the fixture stopped. Author reports visual results.

## Research contracts

Official references: ../../../../agon-docs/docs/mos/API.md (mos_fopen/fread/fclose,
mos_oscli and mos_getkey); ../../../../agon-docs/docs/vdp/Screen-Modes.md;
../../../../agon-docs/docs/vdp/Buffered-Commands-API.md (write/consolidate/clear);
../../../../agon-docs/docs/vdp/Bitmaps-API.md (RGBA2222 and bitmap selection/plot).
Maintained enumeration: vdp/video/agon_screen.h changeMode. HDMI carrier cropping
and timing are under review: listing a mode does not assert correct display.

## Validation

Offline compile and stream validation precede deployment. Hardware visual
acceptance is pending Author execution; no visual results are inferred from build.

## r01 preparation result

The MOS executable assembles successfully. Offline validation checks all 58
entries, each streamed block length (maximum 4096 bytes), opaque RGBA2222 pixels,
bitmap dimensions, double-buffer swap tails and package hashes. Total package
size is 13,367,009 bytes. No hardware execution or visual acceptance yet.

Maintained source and launch instructions: tests/fixtures/mode-preview/.
Generated source-raster inputs and package remain in the ignored visual-review
working directory. Standard modes receive the approved 4:3 interior; 96–99
receive the wide image. No SD files or startup have been modified. Deployment
must wait for confirmation because the mounted card differs from the previous
mainboard card; machine-local identities remain in the bench record.

The Author identified the Extender card by its contents. All 59 payload hashes
verified after copying to /extender/mode-preview; ordinary startup remained
byte-identical. Writes synced and the selected card safely unmounted. The C8
card was untouched. No fixture execution or hardware visual pass claimed.

## Application route correction

Initial Author invocation failed with “display switch failed; current route
retained”. The fixture used CLI-only default EMOS EXCOM/LEGACY requests inside
an application. EMOS src/emos.c emos_request_mode rejects that caller unless
--keep-display is explicit. Both requests now use that supported application
contract. Corrected executable uploaded through the checked listener and staged
SHA verified; package manifest updated and read back. Listener EXIT acknowledged;
CLI ExCom established, executable loaded and invoked. P4 screen-text readback
confirms the complete 58-entry menu at its Mode prompt. No mode selected by agent,
no reset or firmware changes. Author visual review pending.

## r02 — Explicit per-mode palette rasters

Author confirmed the menu works and requested offline palette quantization for
all drawing content. Build r02 uses the mode defaults in agon_palette.h, including
black/red/yellow/white in four-colour modes. Every pixel, including text edges,
background and the 64 source swatches, is matched to the nearest supported RGB
colour; no dithering. Equal-distance ties choose the first palette entry.

Native P4 HSV matching was inspected and rejected for offline artwork because
it introduces coloured fringes on neutral antialiasing. Uploading exact palette
RGB values avoids that remapping ambiguity. The build asserts palette membership
for every output pixel. The r01 files remain retained separately. The new full
package requires physical-card deployment; do not interrupt Author preview or
start a bulk UART transfer without coordinating collection. Cards remain mounted
unless the Author explicitly requests unmounting.

### r02 remote deployment

Author explicitly requested agent deployment instead of physical-card handling.
The listener's measured first raw 307,889-byte upload took 89.2 seconds, motivating
lossless TurboVega bitmap uploads through public buffered command 65. Exact
maintained compression.h codec is compiled for the host with allocation adapters;
every compressed bitmap is decoded and compared before packaging. Public contract:
../../../../agon-docs/docs/vdp/Buffered-Commands-API.md command 65; implementation:
vdp/video/vdu_buffered.h bufferDecompress and vdp/video/compression.h.
The 13,362,208-byte payload became 2,166,297 bytes (83.8% reduction).

The initial second raw file was cancelled after resolving its in-flight response;
no uncertain write was replayed. First completed raw file was retained until
replacement by the packed version. New directory /extender/mode-preview-r02
preserves r01. Fast listener upload checks FINISH size/CRC and target size;
executable and manifest additionally receive independent full readback. Do not
claim full raster SHA readback for this fast transfer. Ordinary startup must
remain byte-identical; no firmware change, reset or unmount is part of deployment.

### r02 deployed; Author review pending

All 60 package files activated under /extender/mode-preview-r02 through the fast
foreground listener. Packed deployment took 707.7 seconds, including executable
and manifest full readbacks; raw trial/build/preparation time is additional.
All transfer FINISH size/CRC checks and target size checks passed. Startup exact
38-byte readback remained unchanged. Listener EXIT acknowledged. CLI ExCom and
LOAD completion observed; RUN now shows the r02 menu awaiting the Author.
No mode selected by the agent. Actual palette-pattern HDMI review remains open.
The C8 card, firmware and reset lines were untouched; no unmount performed.

## Mode96 return-to-menu fault — 2026-10-14

Author reports mode96 looks spectacular. Alt-Tab returned input to the fixture's
any-key path and produced a solid blue display; one mainboard reset did not
recover the display. Live read-only P4 status afterward reports mode0, one rolling
fault, one over-budget refill, one underrun, first_fault2, first_error1940us and
max refill1940us. Input and HTTP remain responsive. This is an informative P4
scanout failure, not evidence of an eZ80/OS crash. Exact triggering input/timing
and causal scope remain unproven. Diagnostics retained under ignored visual-review
mode96-fault. No agent reset, input injection or firmware change during capture.
Fixture currently returns to mode0 on any character; modifier/navigation handling
and explicit return key should be corrected independently of the P4 fault.

### Escape-only correction deployed

Author requested that only Escape return from a preview. The executable now loops
on mos_getkey until ASCII27, ignoring Tab, Enter and other characters. Menu and
teletext guidance updated. Executable, teletext file and compact manifest activated
and independently read back through the fast listener; startup unchanged and EXIT
acknowledged. P4 reset was subsequently requested and performed to clear the
retained scanout fault; one Agon reset restored fresh input admission. The scanout
cause remains separate and unresolved; input filtering does not claim its repair.
