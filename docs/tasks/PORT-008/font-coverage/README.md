# Ordinary font command coverage — 2026-09-13

The Author sequences faithful VDP command coverage after the bounded video
delivery increment. PORT-008 owns ordinary command/reply integration and
PORT-003 owns the retained renderer. This slice checks existing font behavior;
it does not change font algorithms, add upstream features or resume the held
QUAL-003 graphics timing run. All work stays local pending human review.

## Bounded plan

1. [x] P008-F01: Read the official font/buffer/VDU contracts and retained source.
   Bind the exact reference and the already installed P4 candidate. Define
   visible independent expectations before sending commands.
2. [x] P008-F02: Generate a finite ordinary MOS EXEC script with complete VDU
   commands, each shorter than MOS's 256-byte line buffer. Exercise known
   monochrome glyphs, selection, safe width adjustment, deletion/recreation
   without deleting data, and a system-font copy. Keep mode selection in
   startup/CLI. Restore system font and retain a usable CLI.
3. [x] P008-F03: Run that exact script headlessly through the canonical stock
   emulator wrapper. Check pixels against the independently defined glyphs;
   preserve command bytes, runtime identity and captures. No timing claim.
4. [x] P008-F04: Transfer the same script into the host's existing SD workspace,
   invoke it through EMOS's ordinary CLI in ExCom, and compare browser pixels.
   Verify native keyboard, Legacy/SD and unchanged startup recovery afterward.
   Stop on an unexpected admission change or physical takeover.
5. [x] P008-F05: Record exact scope, failures and unsupported assumptions; leave
   any required port correction as a separately bounded, evidenced change.
   Keep human visual acceptance and commit/publication gates explicit.

## Reference précis

The read-only official VDP is v2.16.0 at
c7ac293d2aa81ddfa693390549bcd909069c8fc3. Official MOS is v3.0.2; the local
documentation checkout is f9806bd3cbff6ed5d1c08bef1d51fed11764b86b.
Canonical documentation paths relative to agon-docs are:

1. docs/vdp/Font-API.md: VDU 23,0,149 operations 0/1/2/4/5; fixed-width,
   byte-aligned rows, most significant bit at the left; 256 glyphs; system
   font ID65535. Font deletion preserves the underlying buffer. Operation3
   remains reserved and is not implemented as a new feature here.
2. docs/vdp/Buffered-Commands-API.md: buffer creation3 creates a zero-filled
   single writable block; adjust5 sets known glyph rows in it. No output-stream
   redirection is needed or permitted in this test.
3. docs/vdp/VDU-Commands.md and System-Commands.md: physical graphics coordinates,
   cursor selection, redefined system characters and system-font restoration.
4. Retained vdu_fonts.h, agon_fonts.h, context/fonts.h and context/graphics.h
   own dispatch, buffer lifetime, cursor-specific selection and glyph drawing.
   Official MOS src/mos.c mos_EXEC reads lines into a 256-byte allocation;
   mos_cmdVDU sends ordinary byte/word values. No direct UART or private reply
   handler is used by this case.

The disposition authority remains docs/tasks/SETUP-004/VDU-inventory.md.
docs/qualification/README.md explicitly warns that its generated mode matrix
has not been promoted. This case adds bounded evidence, not a qualified mode
or general compatibility claim. Use existing console firmware/build identity;
the generated command script is a source-hashed exploratory input, not a new
released utility or a silently incremented artifact lineage.

Initial scope uses one single-buffer mode (320×240, mode8). All tested glyphs
fit the screen; no both-edge sprite clipping, narrow-scroll fix, arbitrary
font-property mutation or deleted-active-font lifetime stress is included.
Use project-owned synthetic glyphs, not a third-party font asset. Physical
access/addresses and rollback stay in the ignored bench record.


## Generated case and stock result

The source-hashed command script is 1,285 bytes / 59 complete lines, SHA256
7248c8d1351bf225445e5c1c6990f47bf473f1c9310fba1938d1b8afcff092dc.
make_case.py generates it and its explicit MSB-left glyph rows; check_pixels.py
checks every pixel and a two-pixel halo around nine tiles. The four-pixel case
also requires the rest of its eight-pixel cell to stay blank. Deliberately blank
output and a narrow-font overrun are both rejected by the checker.

The canonical stock profile passes all nine tiles with zero mismatches and
shows the completion text and ordinary MOS prompt. It runs with dummy SDL
video/audio through the generated wrapper; all input hashes remain unchanged.
The local native harness defines time in SDL presents, not VDP frames; no
performance statement follows from this capture. Preserve its source/runtime
manifest and image under ignored agents/video-throughput/font-stock01.

One documentation discrepancy is now explicit: Font-API.md says MSB-left,
whereas the base VDU23 character-redefinition paragraph says LSB-left. The
retained redefineCharacter copies the bytes unchanged, and this stock capture
confirms the MSB-left oracle for these glyphs. Do not reverse the port's bytes
or edit the read-only upstream documentation based on the contradictory prose.

Ordinary read-pixel commands join prior drawing before changing/deleting font
storage; their returned sysvars are not asserted by this visible-only case.
All input is emitted by MOS, with no direct transport or output redirection.
The existing test SD workspace receives the exact same script by staged write,
independent readback, activation and active readback. Root startup is unchanged.
Physical output/recovery results follow below; Author review remains pending.

## Physical result and scope closure

The same script passes all nine tiles on P4 with zero mismatches. Each tile
checks a12×12 region including its halo:1,296 logical pixels in total. The
captured native output and P4 EVF1 bytes independently match the explicit oracle.
The P4 completion text and ordinary prompt are visible in its decoded capture.
The current image is the opt-in DSP-cleanup/poll1/TCP32768 draft
uart-excom-console-r17-b2026-09-13-13-07-24Z, factory SHA256
5bddd14bc5611c99c6b1e90b18fc0f2ed7167298a499199c6248dd8b1fbb489c.
The font renderer/parser was not changed for this case.

Keyboard commands return to Legacy, select mode3, start sdserve, independently
read back unchanged startup and script, and exit to the CLI. No reset/flash or
accepted production-file change occurs. The observer is closed. Private runs,
admission journals and exact foreground live under agents/font-coverage and
HARDWARE.local.md; the stock native capture uses the existing task-local harness.

P008-F01–F05 are machine-complete. This supports the tested visible behavior in
mode8 only. It does not cover variable width fonts (upstream reserved), all
metadata fields, baseline-adjust flags, font readback, deleting an active font,
other depths or malformed commands. No fixture performance claim or broad
qualified/released status follows. Human visual review and explicit commit /
publication approval remain pending; all changes stay local.

Reproduction from the Extender root:

```text
.venv/bin/python docs/tasks/PORT-008/font-coverage/make_case.py agents/font-coverage/new-case
.venv/bin/python docs/tasks/PORT-008/font-coverage/check_pixels.py agents/font-coverage/new-case/oracle.json <capture.png-or-evf> --output <result.json>
```

Select mode8 in the isolated emulator startup or EMOS CLI, then EXEC the generated
fonts.txt. Emulator setup/launch follows canonical guidance; physical SD/input
uses the existing admission and journalled clients. A later run must bind its
own exact runtime and input hashes. Preserve original evidence instead of
overwriting the accepted observations with a rerun.
