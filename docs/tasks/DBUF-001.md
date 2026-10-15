# DBUF-001 — Double-buffered tile scrollers

Investigate how an application can scroll tile-based backgrounds efficiently
with two drawing buffers, particularly when hardware sprites can be composited
without damaging either background. Keep this game-renderer experiment separate
from rendering qualification and its diagnostic-pattern redesign. Full redraw
is excluded by the Author; no renderer or bench experiment starts with this task
registration.

## State, scope and ownership

1. Status: Deferred; discussion retained on 2026-10-14 at Author request.
2. Extender provisionally hosts the investigation because no current game project
   owns it. The Author intends a future game-engine suite containing proven,
   fast renderers for several game types; this experiment may transfer there.
3. The future application owns camera/tile/sprite bookkeeping. EMOS owns VDU
   routing and transport admission. The selected VDP/EDP owns drawing, buffer
   swaps and sprite composition. Physical scanout/publication semantics must be
   researched for the chosen renderer before implementation.
4. Scope: incremental tile scrolling with double buffering, correctness, visible
   smoothness/flicker and complete update cost. This is not a new general engine,
   a firmware optimization project or a replacement qualification suite.
5. Current authorization covers retaining/planning the task. Implementation,
   fixtures, emulator changes, hardware use and transfer to another project
   require explicit promotion and the applicable operation protocols.

## Retained discussion and constraints

1. Initial intended tile size is 16×16, reflecting the Author's Nurples workload.
2. The back buffer normally contains its own older scene, approximately two
   frames old under alternating steady swaps. The application must track each
   buffer's camera/world origin rather than assume the back buffer is the most
   recently displayed image.
3. The application scrolls that buffer from its own retained origin to the new
   camera position and draws newly exposed strips. At steady motion, that is
   normally two frames of displacement per turn: roughly twice the exposed-strip
   work of a comparable single-buffer incremental scroller such as Nurples.
   Actual tile draws depend on tile-boundary crossings, diagonal overlap and
   displacement; this is an expectation to measure, not a proven performance
   ratio. Each buffer needs its own dirty/animated-tile state.
4. The Author explicitly rejected full-screen redraw as a practical approach.
   Do not implement or require it as a runtime baseline. Correctness can use a
   host-side reference/oracle outside measurement if needed.
5. Extra exposed-strip work may be an unavoidable and acceptable price if double
   buffering eliminates objectionable flicker. Measure that tradeoff directly;
   do not assume fewer draws means a cheaper complete frame.
6. Software sprites ordinarily require saved backgrounds or damaged-area repairs
   in each buffer; their prior positions/footprints and tile animation complicate
   incremental restoration.
7. Hardware sprites are the preferred combination to investigate: the output
   compositor adds the current sprites without writing them into tile-background
   buffers. That avoids sprite-background saves/restores and leaves each buffer
   to track scrolling and tile changes. Qualify actual compositor ordering and
   sprite publication: this discussion does not assert identical physical
   scanout behavior on stock VGA, P4 HDMI and browser output.
8. Earlier suggestions included a separate cached background copied into the
   back buffer. This is an unselected alternative, not an agreed requirement or
   permission to add full-frame copying. The Author's chosen starting direction
   is per-buffer incremental scrolling, preferably with hardware sprites.

## Bounded future work

1. Before coding, read the official MOS/VDP contracts, freeze source/firmware/API
   identities, and prepare a short research précis covering scroll, swap, sprite
   lifetime and presentation semantics. Keep upstream references read-only.
2. Specify per-buffer camera position, dirty tiles and animation state, plus the
   lifetime of independent hardware-sprite state. Define initialization of both
   backgrounds and recovery when a displacement exceeds the retained region.
3. Prototype fixed-map horizontal and vertical scrolling, then diagonal motion,
   camera reversals, tile-boundary crossings, animated tiles and moving sprites.
   Include slow visual inspection, pause and stepping where supported.
4. Compare whole-update costs: buffer scroll, exposed tile draws, animated/dirty
   tile repair, any software-sprite cleanup, sprite publication and swap/wait.
   Record tile draws/update and updates/s; separate application/renderer/output
   scopes and identify non-comparable buffering or pacing contracts.
5. Establish visual correctness and flicker/smoothness acceptance with the Author
   before claiming the renderer reusable. No full redraw, unrelated transport
   experiment or maximum-speed-only visual demonstration belongs in this scope.
6. Record transferable findings and implementation ownership for the future
   game-engine suite. Promote reusable Extender services separately only when
   explicitly accepted and qualified.

## Decisions and gates

| ID | Disposition | Decision |
|---|---|---|
| D01 | Accepted scope | Separate experiment from qualification-suite redesign |
| D02 | Accepted constraint | Exclude full-screen redraw as a practical renderer |
| D03 | Selected investigation | Per-buffer incremental scrolling and exposed-strip repair |
| D04 | Selected investigation | Hardware sprites avoid tile-buffer sprite-background repair |
| D05 | Deferred | Choose initial target, APIs, fixture, timings and measurable acceptance limits when promoted |
| D06 | Deferred | Future game-engine-suite ownership and migration |

These are bounded experiment choices, not changes to normative Extender
architecture or claims of implemented performance. No new architecture decision
record or production release is implied.
