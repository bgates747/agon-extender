# BENCH-017 — Mainboard VDP text observation for robot operators

Robots must be able to read the mainboard display after typing commands, so
they can recognize errors and returned prompts instead of waiting blindly for
a later command that never executed. Provide a maintained on-demand host reader
for text already visible on the mainboard display, preserving the loaded
application. The existing Legacy character-query prototype is research input;
its manual LOAD/RUN workflow is not the required product interface.

## Assignment and state

Smith requested this task on 2026-11-09 after failed-run cleanup.
**Preferred design recorded 2026-11-19 for Smith’s review. Implementation and qualification are pending.** This request
does not start a build, firmware change, deployment or physical test.

Smith subsequently clarified the required user experience: robots request the
current mainboard text on demand, without any additional per-read preparation.
No prior mirroring, application instrumentation, helper staging, manual helper
invocation or preparation before the command being observed is acceptable.
Installation of the finished platform capability is distinct from preparing
each read. This clarification replaces the initial CLI-helper recommendation;
it does not claim the required capability already exists.

This task takes ownership of BENCH-006's deferred Legacy S04. Existing ExCom
readback remains unchanged. QUAL-006 owns structured execution/lifecycle reporting;
this task supplies visible-text observation without requiring a complete
control-plane implementation before delivering a useful CLI reader.

## Incident and required outcome

AppleLadder printed its banner, returned nonzero at RUN, and MOS displayed an
EXEC error and normal Legacy prompt. EXEC skipped the trailing listener command.
The host waited for that listener until its2400s deadline. The Author's photo
exposed the early return. Exclusive inspection then confirmed a missing required
output directory before any reset or LOAD. MOS's generic SD-card error reflected
an application return code; it did not establish defective media.

The host must obtain fresh mainboard output with its route, geometry, capture
time and recognition limits. An unavailable/unreadable screen is inconclusive,
never a fabricated prompt or workload pass. Private incident evidence remains
in ignored bench records; the dated development log records the corrective note.

## Existing work and bounded research

| Capability | Reuse | Limit |
| --- | --- | --- |
| P4 `/screen/text` and `scripts/screen_text.py` | Maintained ExCom sampling and host presentation | Reads P4 pixels, not Legacy output or MOS RAM |
| BENCH-005 `textread` | Public `VDU 23,0,&83,x;y;` algorithm and historical Legacy error-text capture | Ordinary LOAD/RUN replaces application memory; not a maintained remote observer |
| Native VDP character query | Recognizes currently drawn characters | Matches pixels against current font/colour; not a retained transcript or authoritative backing store |
| Printer mirror | Future output through mainboard USB serial | Cannot recover text already printed; instrumentation/reader ownership remains separate |

The prototype received1200 replies per route without timeouts. Its cursor
metadata was cached. Source inspection of the selected VDPlet release confirms
the edge restriction below. A normal bottom-row prompt must not be declared
absent merely because the reader cannot observe that row.

### Selected native source findings

The VDPlet owner supplied source facts for the selected dc43 release/source
`60e5b4ebafa3e1c8bb740e45260d78cdb6125e30`; Extender independently inspected the
retained `video/context/fonts.h`. Local file identities and the source reply
are retained in the ignored task research record. This is source evidence,
not a new firmware build, hardware test or supported host reader.

1. Ordinary graphics-mode text has no logical cell grid exposed by the existing
   query. `Context::getScreenChar` recognizes canvas pixels using the current
   font/background, after plot completion. Teletext has separate 40-by-25 cell
   storage; that does not establish ordinary graphics-mode text backing.
2. The current bounds test rejects equality at `canvasW-fontWidth` or
   `canvasH-fontHeight`. It therefore rejects the last complete column and row
   of a tiled screen. The graphics-coordinate query uses the same recognizer
   and does not avoid this defect. A reliable prompt reader needs an explicit
   remedy; shifting, clearing or scrolling the display is not that remedy.
3. Variable-width fonts are refused; changed fonts/background, duplicate glyphs,
   bitmap glyphs and overlaid graphics limit recognition. Zero is not a
   discriminated no-match result. Queries use the current drawing context and
   canvas, with no atomic whole-screen snapshot; visible and drawing buffers
   need explicit treatment.
4. Public `83` queries require no preparatory mirror activation in the VDP,
   but replies share the application's untagged return stream and result state.
   Callbacks can alter or suppress the reply. EMOS host integration must own
   arbitration and preserve application query/callback semantics; merely sending
   query bytes from another processor is not an implemented host reader.
5. VDPlet resource `READ_BYTES` reads registered resource buffers, not arbitrary
   framebuffer pixels or logical screen text. It is not an existing shortcut
   to mainboard text access.

The character recognizer above is a historical comparison. For checking the
colour at a single graphics position, stock VDP separately documents the
`&84` screen-pixel query to MOS. Bulk pixel retrieval is outside this task.

Read these references before implementation:

1. [Current text service](../screen-text.md),
   [Legacy observation and safe serial capture](../serial-monitor.md),
   [prototype results](BENCH-005/RESULTS.md),
   [prototype source](BENCH-005/textread/src/main.c), and
   [original Legacy requirements](BENCH-006.md).
2. Official `agon-docs/docs/vdp/System-Commands.md`, query `&83`, and MOS
   `API.md`, `Executables.md`, `Modules.md`: response flags, timeouts, loader
   metadata, MOSlet address space and application overlap. Consult official
   `agon-vdp/video/context/fonts.h` for glyph/edge implementation detail.
3. [Lifecycle ownership](QUAL-006.md), [SD service](../mainboard-sd.md),
   [SD placement](../sd-layout.md), [bench constraints](../qualification/bench-constraints.md)
   and [standard firmware reuse](../procedures/olimex-firmware.md).

Read-only research baseline inspected while recording the task:

| Reference | Revision |
| --- | --- |
| Agon documentation | `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b` |
| Official MOS | v3.0.2, `8336409351ee5314e02801a7b72a4f1bb5282519` |
| Official VDP | v2.16.0, `c7ac293d2aa81ddfa693390549bcd909069c8fc3` |

These are research references, not deployment selections. Bind actual approved
firmware/provenance from the current selector and inventory before testing;
inspect selected VDPlet source through its owner. Keep reference checkouts read-only.

## Preferred design for review

**VDPlet owns the visible-text buffer on the mainboard ESP32.** Update it when
the renderer places a glyph, using its character code, actual position and font
metrics. An overwrite replaces the old character at that location. A viewport
scroll moves the affected text, a clear removes it, and a buffer swap exposes
the text belonging to the newly displayed page. A font change preserves the
positions of earlier glyphs. A mode or resolution change follows what the
renderer actually clears or preserves. Mark areas whose text is obscured by
graphics or whose layout cannot be represented as unknown. Distinguish an
unknown area from a known blank. Initial scope is ordinary MOS and application
text on the mainboard display.

| Caller | Preferred interface | Ownership |
| --- | --- | --- |
| Pi runner | Enable, disable or request one coherent snapshot through the mainboard USB serial programmer connection while VDPlet is running. | VDPlet serves the request. Extender owns the host command, importable client and serial-port coordination. Opening the connection must preserve reset lines and the running application. |
| eZ80 application | Send VDU requests through EMOS to enable, disable or retrieve the same snapshot in bounded chunks. | EMOS owns ordinary VDU routing. VDPlet and EMOS owners must evaluate the existing keyboard-map reply mechanism for chunk delivery and demonstrate preservation of real keyboard state, pending replies and callbacks before selecting it. |

**Bench default.** Enable tracking at VDP startup so the first Pi request can
read an error printed before any client connected. Give the bench/host and the
application independent enable flags. Tracking continues while either requests
it. If both turn it off, resume with unknown coverage wherever contents cannot
be established again. Measure costs before selecting a general release default.

**Snapshot semantics.** One request identifies one displayed page at one point
in time. Bind all chunks to that snapshot. Include its identity, geometry,
coverage and capture time so the runner can record what was visible and when.
An old prompt alone cannot prove that a new command returned. A read must
preserve the loaded application, MOS load metadata, display and input state.

## Decision register

| ID | Direction | Status |
| --- | --- | --- |
| B17-D01 — Host experience | One on-demand read of existing text, including while an unmodified application runs. | Author requirement. |
| B17-D02 — Ownership and access | VDPlet maintains one renderer-backed model. The Pi and eZ80 have independent controls and can read it. Bench tracking starts at boot. | Preferred model for review. USB framing alongside diagnostic output, VDU command allocation, reply carrier and resource budget remain open. |

## Work plan

- B17-01 [ ] VDPlet owner identifies render, viewport and page operations in the selected mainboard source. Specify supported text modes, invalidation rules and storage cost at the largest supported geometry.
- B17-02 [ ] Extender and VDPlet owners specify USB commands, port ownership, response framing, snapshot lifetime, busy/unavailable responses and time bounds. Specify the eZ80 VDU requests and compare reply carriers with the EMOS owner. Review the interface before assigning opcodes.
- B17-03 [ ] After design approval, implement the buffer and both interfaces in their owning projects. Measure RAM, firmware size, render-time overhead with tracking enabled and disabled, and snapshot latency during output.
- B17-04 [ ] Verify overwrite (`ABC` becomes `AXC` after replacing the middle character), wrap, scroll, clear, bottom-right cell, mixed font sizes, resolution changes, graphics over text, and display-page swaps. Read one snapshot in chunks while new text is drawn. Exercise both enable flags and a tracking gap.
- B17-05 [ ] On an authorized bench run, use an unmodified application that prints an error and returns to MOS before the Pi reader connects. Require the first request to capture the error and bottom-row prompt without mirroring, helper, keyboard input, reset or replay. Check application memory and input state, host reads during execution, and an eZ80 read with real keyboard activity.
- B17-06 [ ] Demonstrate runner correlation of a returned error with the issued command. Preserve raw text, unknown coverage and failures in the evidence. Report an unavailable VDP as unavailable.
- B17-07 [ ] After qualification and acceptance, publish the supported runner command, application API, measured limits and agreed defaults in the maintained guides.

## Completion

An operator can request the text already visible on the mainboard in one host
call. An application can independently control tracking and retrieve a coherent
snapshot. Both readers preserve the foreground application's state, and the
operator can distinguish an observed blank from unobserved or obscured text.
