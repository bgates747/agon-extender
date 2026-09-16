# P01f W results

## Executive summary

**Snapshot-wide priority19 also failed and is rejected as a performance remedy.**
The ordinary control passed. The first treatment recorded2400 matching game
states and native completions, but failed its terminal pixel query15 and slowed
to36.671refresh/s,58.299ms p95. Controller stopped; remaining treatment/control
not run. No repeated causal estimate, performance pass or product adoption.

Eliminating per-row priority transitions did not make the boost viable. Enqueue
spacing also worsened, while time from enqueue to completion rose much less.
Next investigation should address the parser/graphics/snapshot ownership and
pre-enqueue delay, with an explicit ownership-handoff proposal before code.
Do not sweep further priority numbers or leap to assembly/interrupt masking.
No next experiment is started by this report.

## Same-image comparison

Percentage = (treatment − control) / control. Positive time changes are worse;
negative rate changes are worse. Treatment values are **failed-run diagnostics**,
not qualified benchmark results.

| Scope | Control | Snapshot-wide treatment (failed) | Difference |
|---|---:|---:|---:|
| Native refresh completions/s | 60.052 | 36.671 | -38.9% |
| Refresh spacing p95 ms | 29.019 | 58.299 | +100.9% |
| Refresh spacing p99 ms | 33.363 | 70.500 | +111.3% |
| Refresh spacing maximum ms | 37.661 | 86.909 | +130.8% |
| Enqueue spacing p95 ms | 28.680 | 56.977 | +98.7% |
| Enqueue-to-completion p95 ms | 4.075 | 5.487 | +34.7% |
| Snapshot mean wall ms | 10.969 | 17.884 | +63.0% |
| Socket send mean wall ms | 17.769 | 17.421 | -2.0% |
| Game-window sends/s | 27.751 | 25.741 | -7.2% |

Historical mainboard reference:59.927 native refreshes/s,17.063ms p95 spacing.
It was not rerun here. Neither60 native completions/s nor27.75 socket sends/s
measures physical browser/display presentation at60Hz. Snapshot/send scopes
include preemption and waits and may overlap; they are not exclusive CPU costs.
This run uses the unchanged software-sprite fixture; no new Rally, hardware-sprite
or Golem results.

## What the failure establishes

1. The same-image unboosted control reproduces the expected near60 average with
   irregular streamed cadence. It passes the ordinary strict NP04 analyzer,
   state hash, native trace, output accounting and browser/header checks.
2. The treatment's original NP04 has count2400/error15. A separate raw-record
   decode matches the same state hash; the ordinary analyzer rejected it as
   intended. No patched raw file, changed fence timeout or relaxed gate was used.
3. Both native traces contain2400 ordered completions and maximum pending1.
   Both output reports have zero unfinished/invalid/failed operations and exact
   full512×384 payload accounting. NPPRIO selector reports2/19. The linked scope
   is once per admitted snapshot, not inside the row loop. An event trace of
   every runtime priority transition was deliberately not added.
4. Native first-to-last completion duration is39.951s control versus65.834s
   treatment; marker windows39.963s/65.848s. Thus deterioration occurs during
   completed game work, not merely a terminal timeout added afterward.
5. Enqueue p95 expands28.680→56.977ms while enqueue-to-completion p95 changes
   4.075→5.487ms. This points toward submission/parser/ownership delay as an
   important avenue. Percentiles cannot be subtracted to apportion one stall;
   no contemporaneous passive UART trace establishes arrival timing in W.
6. Treatment snapshot wall mean is lower than S's failed per-row intervention
   (17.884 versus28.897ms), yet completed-refresh cadence is worse. Those are
   different ordered runs/images, not a controlled comparison proving the cost
   of yields. Snapshot overhead alone is an inadequate explanation of all results.
7. Both game framebuffers are internal512×384. Largest available blocks differ:
   225280control/172032treatment. Warm P4 order and heap/task state remain
   confounds; same image does not eliminate them. Stopping on first failure
   prevents the intended reversed/repeated comparison.
8. The next structural question is whether ordinary parser work can progress
   without depending on a snapshot-owned native mutex, while retaining stock
   command order, synchronous readback/flush, sprite lifetimes and mode teardown.
   A single graphics owner or cooperative snapshot handoff needs a concrete
   command/ownership design, not merely moving two tasks onto one core. Earlier
   same-core candidates remain rejected. No such redesign is implemented here.

## Browser and evidence limits

Both180second wired observers report no page errors, overflow or sequence gaps;
EVF geometry and lengths pass. End screenshots are blank white in the headless
capture, as in earlier B controls, although retained EVF payloads contain image
data. Therefore screenshots do not establish visible rendering. The existing
offline WebGL readback check is run separately after timed collection, using the
captured payloads and exact saved presenter assets; its result is recorded below.
It cannot certify every intermediate frame or physical monitor presentation.

Raw NP04 files, sanitized native/output records, independent summaries, browser
metadata, allocation excerpts and hashes are in evidence/. Private build, runner,
full serial, flash and browser bundles remain under agents/p01fw/. Full-run
collection duration is in each duration.json; both observers request180seconds.
The controller now saves duration/trace before strict NP04 rejection, so an
informative failure does not lose its collection-time record.
