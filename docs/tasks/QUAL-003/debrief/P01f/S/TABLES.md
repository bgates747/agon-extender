# P01f S results

**Priority19 around each two-row call failed qualification.** The first treatment completed all deterministic states and native refresh records, but the final pixel query returned FR_TIMEOUT15. Its timings worsened. The unchanged harness stopped immediately; the second treatment and final control were not run. Do not interpret the failed run as a qualified benchmark or deploy this intervention.

| Scope | Same-image control | Priority19 treatment (failed) | Treatment vs control |
|---|---:|---:|---:|
| Native refresh completions/s | 60.046 | 39.971 | -33.4% |
| Refresh spacing p95 ms | 21.345 | 53.909 | +152.6% |
| Refresh spacing maximum ms | 33.726 | 75.590 | +124.1% |
| Full-frame compose mean wall ms | 6.725 | 28.897 | +329.7% |
| Full-frame send mean wall ms | 17.790 | 17.267 | -2.9% |
| Sends/marker-window second | 26.771 | 21.560 | -19.5% |

Positive time differences are worse; negative rate differences are worse. These are descriptive counters from a failed diagnostic run, not a parity claim. Mainboard historical reference remains59.927 refresh/s and17.063ms p95; baseline chunk B output-off was60.053/s and17.052ms. Neither was rerun in S.

## What passed and failed

1. Control passed the ordinary strict NP04 analyzer,2400 states, terminal pixel query, native completion trace, output accounting, expected priority2 selector and browser checks. It met the frozen58–62/s and >=20ms p95 admission bounds.
2. Treatment NP04 retains count2400/error15. A separate read of its unchanged raw state records matches the expected SHA256 f43eaa27074aaf6916eded49e5f97bb7eb64a79fd0ccc060f1923a9eb3ea3948. The ordinary benchmark analyzer correctly rejected it; no patched copy or relaxed analyzer was used.
3. Both native traces contain2400 ordered completions, maximum pending1; output accounting has zero pending/invalid/failure counts. Post-window NPPRIO records confirm selectors2 and19 respectively. Neither has an assertion/panic in retained serial evidence. This is not an instruction-level trace proving every priority transition.
4. Both browser observations have no page errors, capture overflow or sequence gaps. Whole180second captures include non-gameplay setup/terminal output; they are not game-only throughput. Game-window send counters are tabulated separately.
5. Both512x384 framebuffers were allocated internally; available largest blocks differ. Same image does not imply identical allocation/task state across warm runs.
6. Unchanged fixture code executes its final pixel-query fence before stop marker/dump. Therefore the extra post-window NPPRIO line cannot have caused that earlier timeout. Native first-to-last refresh times are39.955s control and60.466s treatment, so the slowdown is inside completed work, not merely a20second wait added after it.

## Interpretation and next avenue

**This particular intervention is rejected for adoption.** Raising snapshot priority before acquisition can also make its current mutex holder inherit19; lowering it per row invokes scheduling again. The intervention adds priority API/check costs on every row pair. Those are plausible sources of adverse scheduling, not demonstrated causes. Clean browser decoding and a nearly unchanged per-send mean do not prove all network/response service deadlines were met.

P01e still contains valid evidence of a lock holder displaced by TCP/IP; this experiment does not erase that observation. It shows that replacing the observed relationship with repeated priority boosts is not a validated fix. Because the first treatment failed, there is no replicated causal estimate and no justification for a new priority/affinity guess here. Proceed to authorized chunk A: map mutex ownership, inheritance, task handoffs and the original FabGL interrupt/row lifecycle before choosing another intervention. Do not broaden into rewriting rendering or disabling interrupts.

## Durations and evidence

Control marker window 39.968082s; failed treatment marker window 60.483611s. Each wired browser observer requested180s. Control reset-to-collection was 202.88569037600246s. Treatment collector did not emit its successful duration record because the fixture was rejected; do not fabricate one.

Raw NP04 files, sanitized NPTRACE/NPOUT/NPPRIO records, independently decoded diagnostic summaries, browser summaries and hashes are retained in evidence/. Full private source/build/flash/capture/observer logs remain under agents/p01fs/. Build/provenance, exact parent delta and deployment are adjacent. Restoration and notification receipts will document the bench closeout.
