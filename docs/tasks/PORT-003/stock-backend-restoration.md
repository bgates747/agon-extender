# PORT-003 — Restore the stock video backend

Status: **accepted; R1 authorized**, 2026-09-10. The Author accepted the repair
with the first-pass rule below and directed a contract freeze followed by R1.
Existing version preapproval applies. R2/R3 remain subsequent work boundaries.

## Governing first-pass rule

**No upstream bug fixes in the first pass. If upstream code compiles on the
selected target, use it unchanged.** Suspected or confirmed upstream bugs are
recorded as observations and deferred; they do not authorize cleanup, hardening,
behavior changes or improved algorithms. This overrides the original W7
recommendation to remedy edge defects during restoration. Make only changes
actually required for compilation or the P4 processor/output binding. Preserve
every otherwise compilable upstream body, including its quirks. A failing
comparison is evidence to report, not permission to repair upstream.

Authority: [AUDIT-006 comparison and findings](../AUDIT-006/video-backend-audit.md),
accepted AUDIT-006-D001 and ADR-0013/ADR-0015. This is a repair within PORT-003,
not another port/audit task or a new generic-renderer project.

## Result and first increment

EDP should run the original five stock depth-controller implementations and
their efficient native-row operations, with only evidenced P4 processor and
video-output bindings changed. Its display clock and output must progress
independently of drawing-queue emptiness. The working UART console, official
VDU/context/text/Teletext, USB keyboard and browser RGB222 protocol remain the
surrounding interfaces.

**The first coding increment is a bounded original-class binding proof.**
Select and compile the existing VGA2/4/8/16/64 portable implementations against
a P4 lifecycle/output boundary; preserve stock native formats, row tables and
method bodies. Identify actual compiler/peripheral dependencies as they arise
and record each necessary change. Do not flash this proof or silently fall
back to renamed copies of the current generic controller. Its reviewable
result is the source diff, exact reuse ledger, successful target compilation
and native-row comparison evidence—not another speculative design essay.

If a concrete class cannot be selected without materially broad changes,
record the precise blocking dependency and smallest verbatim extraction option.
That is the decision point; a compilation failure is not authorization to
invent a replacement algorithm. Follow-on integration below is bounded to
what this proof establishes.

## Inputs and ownership

1. Retain official VDP v2.16.0 at `c7ac293d2aa81ddfa693390549bcd909069c8fc3`
   and selected vdp-gl at `ac2dd5986daf496c43ae8e7fe41836274aec54a0`.
   Keep official reference checkouts read-only. Use project-owned source and
   attributed patches; keep licenses and source-span provenance.
2. Baseline EDP source is `047ffe8`; installed diagnostic and rollback bindings
   remain in AUDIT-006's deployment/evidence records. Do not relabel or erase
   the semi-working checkpoint or the F001 reproduction.
3. EDP's parser retains EMOS-authorized UART session/routing and processed USB
   input. This repair concerns the video backend; no EMOS rewrite, new GPIO
   route, parallel transport, browser keyboard, game instrumentation, public
   callback ABI or mainboard firmware experiment is included.
4. EDP's drawing worker owns queued native drawing/software-sprite work.
   Retained synchronous flush and double-buffer callers are additional
   drawing owners and must obey the same exclusion contract.
5. EDP's output clock advances independently of those drawing owners. Its
   output reader resolves visible native rows and retained palette/overlay
   state, produces stock-derived final rows into owned snapshot storage, and
   publishes only completed snapshots. Network/browser code receives leases
   on that output storage, never ownership of native drawing memory.

## Work and completion boundaries

1. [ ] **R1 — Bind the original concrete family.** Keep the stock classes,
   native depth accessors, row-paint selection, copy/fill/scroll/bitmap bodies,
   palette tables and common renderer. Separate classic I2S/GPIO/DMA/ISR setup
   from portable operations. Preserve width/height quanta, row aliases and
   drawing/visible table identity. A contiguous allocation may back the rows;
   do not impose `base + y*stride` as their logical order after scrolling.

   Justify target allocation/cache/alignment choices using actual P4 SDK and
   compiler evidence. In particular, evaluate stock VGA8 word accesses over
   three-byte groups and VGA64 `x ^ 2` access. Preserve bytes when changing an
   access instruction is necessary. Restore exact portable utility bodies
   instead of retaining gratuitous renaming/re-expression. No dummy physical
   registers or no-op ISR/FPU substitutions may stand in for target support.

   R1 completes with five-depth target build closure, precise retained/changed
   symbols, and host comparison of native rows and affected render operations
   against original upstream bodies. It establishes feasibility, not runnable
   hardware or complete performance parity. Review R1 before expanding a
   surprising binding change.
2. [ ] **R2 — Restore independent execution and packed row output.** Reuse
   the stock worker's drain/suspend behavior with its optional timeout disabled,
   and coalesce drawing notifications as stock does. Frame time advances from
   output timing, not from completed drains. Preserve immediate flush, FIFO
   payload ownership, explicit swap notification and official callbacks.

   Use the original per-depth packed row expansion and palette/Copper cursor,
   followed by the stock sprite/text-cursor/mouse decorator. Normalize the
   signal byte/lane representation at the output boundary, producing the
   existing final RGB222 EVF1 image without an RGB888 intermediate. Retain
   immutable network leases and complete-or-error send semantics. Output
   demand, a slow browser or no free snapshot slot may skip an output copy;
   they must not stop the display clock or native drawing.

   Restore stock execution relationships where applicable; record actual
   P4 core/priority choices against SDK Ethernet, USB and timer tasks. Do not
   assume a core assignment alone fixes latency. Do not replay a complete
   draw/snapshot pass for each missed tick, introduce another primitive/time
   quota, or move bulk frame work into the timer callback.

   Before enabling an independent CPU output reader, prove valid target access
   to changing row pointers and pixel memory, plane swaps, palette/sprite
   mutation/destruction and mode teardown. Separate atomics do not prove
   entry exclusion. Explicitly resolve F007 with the smallest synchronization
   and lifetime binding that preserves stock progress. A whole-frame drawing
   suspension would reintroduce the coupling and is not the default solution.
   Join native-memory readers and drawing owners before freeing source state;
   already leased output snapshots keep their separate lifetime.
3. [ ] **R3 — Qualify the integrated replacement.** Run the boundary checks
   below and build the selected ordinary console with existing identity and
   deployment rules. Prepare a reviewed candidate and rollback before any
   flash. Use the existing deterministic graphics/UART evidence machinery and
   Nurples playtest to compare results, with source/build/run identities kept
   distinct. Do not automatically launch the held full QUAL-003 callback suite.

## Verification that can detect the actual departures

1. **Native bytes:** for all five depths compare raw packed rows against stock
   accessors, including patterns crossing packed groups. Keep framebuffer
   bytes, one-byte-per-pixel native sprite backgrounds, and public opaque
   RGBA2222 capture separate. A second generic bitstream implementation is not
   an independent oracle. Check single/double-buffer drawing and visible rows.
2. **Operations:** clear/nonzero fill; every paint mode; aligned and unaligned
   horizontal/vertical scroll; both overlap directions; narrow viewport
   preservation; glyph, shape/flood/path; ordinary and transformed bitmaps;
   a bitmap much larger than an inclusive one-row viewport. Test stock width
   quanta and edges, rather than expanding dimensions for convenience.
3. **Composition:** normalize stock signal rows and compare final pixels for
   all depths, primary/secondary palette changes, Copper zero/boundary/last
   spans, alpha/XOR, overlapping hardware/software sprites, cursor order and
   native save/restore. Readback must remain drawing-plane/palette-0 behavior,
   not a browser snapshot substituted for the stock response.
4. **Inherited defects:** retain upstream behavior unchanged. Keep the audit's
   narrow `swapRows`, both-edge hardware-sprite clipping and palette iteration
   suspicions as deferred observations. No first-pass fixes or additional
   hardening are authorized. Record any encountered failure separately from a
   porting difference; compilation or comparison work must not silently amend
   the upstream reference to obtain a pass.
5. **Concurrency/progress:** force suspend/start interleaving; exercise nested
   suspension, immediate flush, double-buffer swap, queue payload lifetime,
   ongoing drawing with output progress, missed notifications, and mode
   stop/reconfigure while an output frame is being prepared or leased. Check
   bounded memory ownership, no retired-row/overlay access and no synchronous
   network wait on the drawing path. Preserve the actual stock API semantics;
   queue empty is not a general presentation/completion fence.
6. **Hardware:** after local gates, use ordinary console entry/return, keyboard
   and existing graphics tests plus sustained repaired Nurples. Keep evidence
   of draw progress, output progress and finite-work completion distinct.
   Passing a screenshot or 48 finite rows cannot by itself close F001. Do not
   assert improved gameplay/frame rate before measuring or Author observation.

## Decision and stopping rules

AUDIT-006-D002 accepts original-class reuse with narrow P4 base/output
binding. Verbatim extraction is the fallback for a demonstrated source-unit
dependency; a clean-sheet generic renderer is not the fallback. R1 resolves
concrete compile/access dependencies before a wider production diff.

Implementation stops for a concrete review if it would require changed public
VDU semantics, removal of a supported depth, additional EMOS/mainboard firmware,
unjustified full-method rewrites, or a concurrency compromise. Routine SDK
binding choices within this contract do not require repeated approval. Record
findings and proposed alternatives before asking the Author to decide.

Keep active PORT-003 contracts/provenance and ADR-0015 aligned with the accepted
binding. Historical phase evidence stays scoped to its original implementation.
AUDIT-006's source audit and dispositions are accepted, with F009 deferred
unchanged under the first-pass rule. Implementation completion and physical
qualification remain separately recorded here.
