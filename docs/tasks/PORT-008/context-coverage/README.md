# Ordinary graphics-context coverage — 2026-09-13

This bounded PORT-008 increment follows the font and bitmap checks. It exercises
the retained VDP context API through ordinary MOS EXEC/VDU commands, first on
stock native VDP and then the already installed P4 candidate. It introduces no
renderer algorithm, firmware flash, public interface, or Golem dependency.
The held QUAL-003 timing work remains held. Human visual, commit and publication
review remain open; the Author has forbidden publishing experimental changes.

## Bounded plan

1. [x] P008-C01: Read official Context-Management-API.md, the relevant base VDU
   and screen-mode contracts, and retained context dispatch/activation/reset
   source. Bind unchanged stock references and existing physical admission.
2. [x] P008-C02: Generate a finite synthetic pixel case covering all eight
   context operations, saved painting/origin/viewport/cursor state, independent
   named stacks, and global bitmap/palette storage. Use single-buffer mode8,
   selected outside the script. Keep commands within MOS's 256-byte line limit.
3. [x] P008-C03: Run the exact input through the canonical headless stock
   wrapper. Check explicit expected pixels and untouched halos, preserving any
   stock/documentation discrepancy instead of rewriting an oracle to hide it.
4. [x] P008-C04: Transfer and read back the exact input with sdserve, invoke
   through ordinary EMOS in ExCom, compare pixels, and recover Legacy/SD with
   unchanged startup and neutral released keyboard admission. No reset unless
   required by a separately diagnosed failure.
5. [x] P008-C05: Record scope, exact evidence and remaining limitations. Any
   actual port defect receives a bounded diagnosis before implementation.
   Do not promote finite visible checks to general command qualification.

## Source précis and boundaries

Read-only stock VDP v2.16.0 is c7ac293d2aa81ddfa693390549bcd909069c8fc3;
MOS v3.0.2 is 8336409351ee5314e02801a7b72a4f1bb5282519. Both reference trees
are clean. Official documentation remains f9806bd3cbff6ed5d1c08bef1d51fed11764b86b.
Relevant paths relative to agon-docs are docs/vdp/Context-Management-API.md,
VDU-Commands.md, Screen-Modes.md and Bitmaps-API.md. Retained implementation
boundaries are vdp/video/vdu_context.h, context/graphics.h, context/viewport.h
and context.h in this project. SETUP-004/VDU-inventory.md remains the command
disposition authority; its supported entries do not imply exhaustive testing.

1. VDU23,0,200 operations0–7 select/delete/reset/save/restore/save-copy/
   restore-all/clear-stack. Context IDs are bytes. Selecting a nonexistent ID
   clones the complete current stack; deleting the active ID has no effect.
2. Save-copy selects a copy of another stack's top context while retaining the
   current stack ID. A subsequent restore returns to the caller's saved state.
   With a nonexistent source ID it still saves the current state.
3. Painting, origin, viewport and cursor state belong to contexts. Buffers,
   bitmap definitions, mode and palette are global. In mode8 palette changes
   affect subsequent painting only; they do not recolour existing screen pixels.
4. Reset bit0 restores graphics painting/options. Reset bit1 also restores
   logical coordinates. The latter must be explicitly returned to physical
   coordinates if subsequent test commands use pixels; do not mistake the
   documented coordinate reset for a broken origin/viewport implementation.
5. Read-pixel commands join earlier drawing before storage retirement. This
   visible case does not assert their returned MOS sysvars or query latency.
   The inherited resetGraphicsPainting implementation also assigns text colour
   indices; this case does not claim independence of every reset flag field.

Use generated project-owned pixels and the preceding bitmap checker's strict
capture decoder/oracle format. Select mode8 outside the script, reserve ordinary
bottom text rows for MOS output, delete only explicitly owned inactive contexts
and buffers, and finish with a usable prompt. Exact installed firmware, private
network locations, rollback and foreground state remain in HARDWARE.local.md.
No emulator attention cue is required while the Author sleeps.

## Stock result

The 295-line generated script SHA256 is
08244e65712db5b4a83e81f3959c3f573d5253287f42c3011d79b716fa2f5c1a.
All 18 explicit pixel tiles and their two-pixel halos match stock native output.
This includes retained XOR mode, relative graphics cursor, viewport clipping,
named-stack cloning with saved history, save-copy preserving its caller's stack
ID, nonexistent-source save-copy, restore-all/clear-stack, inactive/active
deletion, selective resets, and local bitmap selection with shared data edits.
The palette case explicitly confirms that mode8 retains already drawn red
pixels while later selection uses the globally changed blue palette entry.

No discrepancy or renderer change was required. The preceding bitmap checker
is reused in its independent-oracle mode, without a stock-reference exception.
Source/input hashes and native runtime/capture evidence are retained under
agents/context-coverage/case01 and agents/video-throughput/context-stock01.
The capture ends with the completion text and a usable MOS prompt. Physical
comparison and recovery remain pending; a native pass does not establish them.

## Physical result and scope closure

P4 independently passes all 18 tiles and 1,296 logical pixels including halos.
The exact 5,528-byte input passed staged/active SD readback before execution.
The native reference PNG SHA256 is
df9f25ea253851c14681b7a50615552cf1b5ee5c375e493ec379c5730c11d4c0.
The five-second browser observation retains 294 snapshots, all 320×240, with
no sequence gaps. Static snapshot receipt is not a gameplay/scanout measurement.
The same optional DSP-cleanup/poll1/TCP32768 P4 candidate remains installed;
its identity and admission are recorded privately, with no firmware change.

Ordinary EMOS commands return to Legacy and start sdserve. Unchanged startup
and exact input readback pass, then the service exits with no pending request.
The keyboard session is canceled, ready and neutral under the same boot. The
native emulator/browser observers are closed. No reset, root-startup edit,
accepted production-file change or publication occurs.

P008-C01–C05 are machine-complete. The result covers these mode8 graphics
settings and global-resource boundaries only. It does not establish every text
font/cursor reset field, all-coordinate combinations, context-mode transitions,
malformed commands, query return values or timing. Human visual/commit review
and wider command qualification remain open.

Reproduce with this generator and the existing bitmap checker in its default
independent-oracle mode:

```text
.venv/bin/python docs/tasks/PORT-008/context-coverage/make_case.py agents/context-coverage/new-case
.venv/bin/python docs/tasks/PORT-008/bitmap-coverage/check_pixels.py agents/context-coverage/new-case/oracle.json <capture.png-or-evf> --output <result.json>
```

Select mode8 outside the script and EXEC contexts.txt. Bind fresh input/runtime
hashes for any rerun; preserve the original case and capture evidence.
