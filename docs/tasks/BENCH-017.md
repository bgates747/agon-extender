# BENCH-017 — Mainboard VDP text observation for robot operators

Robots must be able to read the mainboard display after typing commands, so
they can recognize errors and returned prompts instead of waiting blindly for
a later command that never executed. Turn the existing Legacy character-query
prototype into a maintained, bounded reader that preserves the loaded application.

## Assignment and state

Smith requested this task on 2026-11-09 after failed-run cleanup.
**Task recorded; implementation and qualification not started.** This request
does not start a build, firmware change, deployment or physical test.

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

The prototype received1200 replies per route without timeouts. Its selected
upstream implementation excluded the rightmost column and bottom row, and its
cursor metadata was cached. Recheck these limits against the exact current
VDPlet release. A normal bottom-row prompt must not be declared absent merely
because the reader cannot observe that row.

Read these references before implementation:

1. [Current text service](../screen-text.md),
   [Legacy observation and safe serial capture](../serial-monitor.md),
   [prototype results](BENCH-005/RESULTS.md#text-readback),
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

## Requirements and ownership

1. **Observe the correct display.** The host identifies mainboard VDP/Legacy
   explicitly. Determine whether the selected native VDP has a usable text
   buffer/read API; otherwise call the result character-query readback. P4
   ExCom text must never substitute for mainboard output.
2. **Preserve state.** A CLI capture preserves application bytes and MOS
   load/entry metadata, route, mode, font, viewport, cursor and existing text.
   Do not clear, scroll or switch modes to simplify recognition. Account for
   the capture command's echo. Detect overlap before using disposable MOSlet
   space; do not assume every application leaves it free.
3. **Respect foreground ownership.** EMOS owns routing, transports and admission.
   A CLI-only helper is unavailable while another application runs. The host
   must not type capture commands into an unknown foreground. Specify active-app
   observation separately; no reset, replay, raw UART/GPIO bypass or private
   memory scraping is a fallback for an unavailable reader.
4. **Bound and qualify captures.** Return rows, dimensions, region, start/end
   times, cursor provenance, unknown-cell/timeout counts and component/build
   identity. Disclose non-atomic sampling and font/colour/graphics/edge limits.
   Bound each query and the whole capture; support a useful bounded region
   rather than always paying for a full-screen sweep.
5. **Make it usable by robots.** Provide a maintained host command and importable
   interface over the existing admitted transport. Correlate output with the
   actual issued command; old prompts and command echo are not completion.
   Preserve raw text and classification. A returned error/prompt must stop an
   inappropriate listener-only wait without launching a successor or claiming
   the application passed.
6. **Deliver evidence safely.** If a helper saves to SD, use new declared paths
   and the maintained foreground service; capture before printing its own report.
   Distinguish capture/storage errors from application errors. No startup changes.
7. **Keep the implementation small.** Prefer public queries and a disposable
   CLI MOSlet where sufficient. Measure host latency, RAM/ROM/helper size, VDP
   traffic and interference before proposing resident additions. No E/VDP↔EMOS
   CRC or substitute checksum. Component owners implement any necessary supported
   firmware change; filing this task does not authorize one.

## Work plan

1. [ ] B17-01: Inspect exact selected contracts and reusable source; record a
   compact précis and resolve the decision register before coding.
2. [ ] B17-02: Specify minimal CLI capture, host result, busy/unavailable behavior,
   command correlation, time bounds and evidence paths. Freeze qualification inputs.
3. [ ] B17-03: Implement in maintained owning source trees. Replace the old
   prototype's application-clobbering LOAD/RUN deployment with a supported route.
4. [ ] B17-04: Verify parsing, bounded timeouts, partial/unknown coverage and
   stale-result rejection with meaningful host controls.
5. [ ] B17-05: Under a fresh authorized lease, qualify successful command output,
   returned application error/aborted EXEC, bottom-row prompt, scrolling/wrapping,
   unknown glyphs, busy application and missing VDP reply. Verify loaded bytes,
   MOS load metadata and display-state preservation; restore responsive CLI.
6. [ ] B17-06: Demonstrate prompt/error reporting without waiting for the full
   application deadline. Record capture duration and instrumentation limits;
   polling is not guest progress and text capture is not an optical pass.
7. [ ] B17-07: After acceptance, promote the command/API and instructions outside
   this task silo, update scheduler references and apply production/version rules
   if an accepted firmware or bundle changes.

## Decision register

| ID | Recommendation / alternatives | State and effect |
| --- | --- | --- |
| B17-D01 — First supported context | Prefer a CLI-safe disposable MOSlet using public native queries, preserving the loaded application. Compare an existing native buffer API if the selected release provides one. Resident machinery costs ROM/RAM and requires a supported execution-context contract. | Open; resolve from source facts, then present one concrete recommendation to Smith. Determines owner, transport and overlap handling. |
| B17-D02 — Running-app observation | Keep CLI readback distinct from future-output mirroring or resident observation. Reuse a supported channel where sufficient; avoid making a general control-plane rewrite a prerequisite. | Open after D01; determines busy behavior and first implementation scope. |

## Completion

A robot can obtain fresh mainboard text for qualified error/prompt cases through
a documented bounded route, or explicitly report why it cannot. Capture preserves
the loaded application and declared display state. The scheduler distinguishes
returned command failure from missing completion without automatic reset/replay.
Documentation names supported contexts and limits. A written task or historical
prototype alone does not meet these implementation criteria.
