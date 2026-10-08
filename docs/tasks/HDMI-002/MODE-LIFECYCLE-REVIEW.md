# HDMI mode transitions — offline lifecycle review

Two indefinite waits are reproduced in the actual HDMI sink: cancelling a
submitted direct swap does not release its caller, and borrowing panel storage
waits forever after a contained scanout fault. The proposed correction releases
those callers without surrendering DMA ownership and rebuilds faulted scanout
at a joined mode boundary, including an unchanged carrier. Host checks pass;
target compilation and its build-selection checks pass. These defects are established in controlled
tests, **not established as the cause of the recorded mode96-to97 failure**.
During this tranche the bench was assigned to another project; no hardware
was accessed. The later EMOS/Pingo handover does not deploy this P4 image.

## Bounded authority and call path

1. Official [mode and swap documentation](../../../../../agon-docs/docs/vdp/Screen-Modes.md),
   agon-docs commit `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`, specifies
   requested-mode failure followed by current-mode and then mode1 fallback.
   The read-only official VDP v2.16.0, commit
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`, implementation in
   [vdu_mode](../../../../../agon-vdp/video/vdu.h) supplies that order.
   EMOS still owns routing the ordinary VDU request to P4.
2. P4 [changeResolution](../../../vdp/video/agon_screen.h) detaches the former
   service before retiring borrowed panel memory on a carrier change. Its
   [service](../../../vdp/video/extender/display/stock_p4_service.cpp) cancels
   direct swaps, joins drawing/output, then drains the former controller.
   Same-carrier direct candidates also join the former service before borrowing.
   Ordinary independently allocated candidates retain prepare-before-commit.
3. The [HDMI sink](../../../vdp/video/extender/display/hdmi_output.cpp) owns panel
   buffers, acknowledgement metadata and the persistent core1 submission task.
   The [mode transaction](../../../vdp/video/extender/display/mode_transaction.hpp)
   prepares fallible resources before committing the new controller/service.
4. Pinned ESP-IDF5.5.5 commit `b774170ff46c393eeb5e495ea37936038d3f4f4f`
   [DPI driver](https://github.com/espressif/esp-idf/blob/b774170ff46c393eeb5e495ea37936038d3f4f4f/components/esp_lcd/dsi/esp_lcd_panel_dpi.c)
   and the existing isolated rolling derivative own physical DMA lifecycle.
   The [vendored Olimex bridge](../../../vdp/components/esp_lcd_lt8912b/UPSTREAM.json)
   retains commit `04032d68e5c727870f9d40beb9e37b7ab3a66916`; its construction
   and deletion wrap the DPI driver. Neither upstream component was modified.

## Findings and changes

| ID | Old behavior | Candidate behavior | Evidence limit |
|---|---|---|---|
| L-F01 | A direct swap in Submitted state waits only for Complete/Failed; detach sets cancellation but a stopped scanout cannot supply the IRQ | Cancellation or contained fault marks an already-submitted request failed under the callback lock; the caller returns false | Reproduced with actual sink and worker, controlled frame completions |
| L-F02 | panelStorage uses an uncancellable wait for pending ownership; a contained abort leaves it blocked | Waiters return false on the rolling runtime's contained-abort counter; storage borrowing returns empty | Reproduced with pending buffer and injected runtime fault |
| L-F03 | needsMode considers only readiness and carrier dimensions, so a stopped same-size panel is retained | A contained scanout fault also requires normal joined panel recreation | Host exercises same-carrier recovery; physical recovery remains pending |
| L-F04 | Startup cleanup and repeated carrier reconstruction lacked actual-sink host failure injection | New tests force acquisition/init failures, verify cleanup, retry and repeat carrier changes | Fake SDK boundary verifies caller ownership; it does not prove SDK internals or electrical reset |

The original mode96-to97 attempt did not open its next measurement window;
network/input stayed alive and cold-start mode97 subsequently passed. Its saved
evidence does not establish where the parser/service stopped or that the panel
had already faulted. Do not equate that observation with these controlled
reproductions. Likewise this remedy does not explain the earlier blue screen;
the preceding [refill investigation](OFFLINE480-REVIEW.md) remains separate.

## Ownership invariants retained

1. A Requested swap still belongs to the submission worker. Cancellation does
   not acknowledge it while that worker might be accessing panel memory. The
   waiter joins the worker's transition to Submitted, Complete or Failed.
2. Once Submitted is published under the callback lock, the worker performs no
   further accesses for that request. A cancelled caller may then return false,
   but pending buffer ownership stays intact. Only actual DMA acknowledgement
   or joined panel deletion resets that ownership; no timed reuse is introduced.
3. The mode owner joins both renderers and retires borrowed pointers before the
   core1 worker deletes/recreates a faulted panel. The existing requested/old/
   default fallback remains in charge if initialization fails. No autonomous
   restart, new retry loop, clock change, color change or extra buffer is added.
4. A first diagnostic reason of underrun is not treated as proof that DMA has
   stopped. Recovery checks the runtime's contained-abort count. Existing callback
   cancellation and healthy physical-frame acknowledgement retain their roles.

## Host validation

The [lifecycle runner](../../../tests/display/hdmi_lifecycle_test.py) compiles
the maintained complete HdmiOutput translation unit and executes its actual
persistent submission worker. SDK calls and the renderer-facing surface are
substitutes; geometry, ownership and output implementation are maintained code.
The host resource ledger checks acquire/release balance, not hardware memory
capacity. Address/undefined-behavior sanitizers pass.

| Check | Result |
|---|---|
| Retained r09 source, cancellation and faulted borrow | Both hangs reproduced; a deliberately supplied frame releases each old waiter |
| Corrected cancellation, with no further frame completion | Caller returns false; pending DMA ownership remains set |
| Cancellation while driver call is deliberately held | Caller remains blocked until worker finishes; then returns false |
| Cancellation while worker awaits prior native submission | No new driver submission; caller returns false; prior ownership retained |
| Healthy swap and fault after submission | Healthy swap waits for real modeled acknowledgement; fault returns false without buffer reuse |
| Startup failures | Power, I2C, all three register-bank handles, DSI, panel creation, buffer lookup, reset, callback registration, init and task creation clean up and allow retry |
| Low-memory panel fallback and missing startup callback | One-buffer retry works; exhausted retry and absent callback clean up |
| Repeated carriers and failed reconstruction | Ten 684→848 round trips; nine injected restart failures release resources and allow former-carrier reconstruction |
| Existing actual drawing/output-service suite | Pass: frame ordering, independent clock, joined detach and candidate worker-creation failure |
| Existing actual strip-runtime suite | ASAN/UBSAN pass: queue, deadline, generation, fault ordering and active-copy teardown |
| Build-selection checks | All12 pass |
| Physical mode switch, scanout recovery and Nurples | Pending HDMI02-O04; no physical tests performed |

Artifact-registry validation passes. The repository-wide version-record
validator still stops at the previously
recorded frozen light2-harness-r02 connectivity hash mismatch. Both that profile
and its connectivity file match Git HEAD and were untouched here; this is not a
passing global validation claim or a reason to rewrite frozen hardware evidence.

Host runtime durations include compilation and scheduling; they are not P4
performance figures. JSON records include UTC start/end, duration and relevant
source/test hashes. Retained before-source, logs and build inputs are under the
ignored `agents/hdmi002/mode-lifecycle` silo.

## Remaining limits

Host tests cannot establish physical DMA completion after bus failure, SDK IRQ
join timing, cache coherency, monitor relocking, PSRAM performance or complete
VDU/parser fallback behavior. Existing driver teardown deliberately fails rather
than freeing live DMA buffers if its one-second copy join expires; that policy
was not weakened. Applications already stuck waiting for a stopped physical
vblank are not promised automatic recovery by this change. New240-line modes,
rendering optimizations and production promotion remain outside this tranche.

Experimental build `rgb-001-r10-b2026-10-07-22-56-28Z` compiled successfully
in 510.72 seconds. Source-snapshot validation passed; all 20 manifest artifacts
were independently rehashed. Factory SHA-256:
`ef7e7bdae861119bcdc2fcda947631450f0890b6cefc8d4c23e2b6d8ead7498c`. It includes
the earlier r09 refill remedy plus these lifetime changes; both require physical
validation. Exact r06 rollback and r09 artifacts remain retained. No installed
state record or production selection has changed.
