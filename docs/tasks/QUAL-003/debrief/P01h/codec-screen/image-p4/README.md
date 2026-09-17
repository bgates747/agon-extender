# RGB888 JPEG and indexed PNG on P4

## Executive summary

Author authorizes physical P4 experiments, first hardware JPEG from RGB888,
then indexed PNG, compared with RLE2. RGB565 is excluded. Keep the same renderer,
network path and workload; preserve exact baseline and restore before hardware
voice notification. No mainboard firmware changes, Golem or production promotion.

## Frozen execution contract

1. [x] I01 — Preserve incoming bench state and clear old mainboard cue. Inspect
   official P4 JPEG API and official PNG implementation, identify exact source
   dependencies and reusable indexed-PNG candidates. Record bounded research.
2. [x] I02 — Prepare isolated candidate and reproducible changes inside this
   task. JPEG accepts expanded RGB888 (driver byte order verified), reusable for
   future RGB888 sources. Benchmark quality 80/90/95 and 4:4:4 without colour
   subsampling first. Reject malformed dimensions and avoid per-frame allocation.
3. [ ] I03 — Compile, independently verify deployment and exercise hardware JPEG
   on retained corpus. Decode in browser, measure visual error and conversion,
   encoding, bytes and delivery separately. Compare selected settings with RLE2
   on matched deterministic Nurples and static scenes, three interleaved trials.
4. [ ] I04 — Add indexed PNG using reviewed existing encoder, levels1/3 where
   available, exact64-colour palette. Prove decoded pixels exact, reject bad input,
   measure the same scopes and repeat matched selected-setting comparisons.
5. [ ] I05 — Assess evidence, preserve anomalous runs, state practical verdict and
   limits in executive summary and tables. Restore original P4/startup, leave
   keyboard neutral at Legacy prompt, send hardware British voice and verify
   fresh receipt. Commit discrete work, no push or promotion.

## Controls and stopping rules

Use the card in the Agon only; host MOS-suite card is excluded. Test fixtures
remain under /test, modes selected by startup only. Same512x384 source, browser,
30Hz web cap, scheduling and renderer across codecs. Lossy JPEG is judged by
explicit error metrics plus retained decoded images, not byte equality. Palette
conversion before compression must be exact. Browser reception is not proof of
unique completed hardware frames. No changed scheduler, affinity or priority.

New discoveries may refine bounded implementation details, recorded as
agent-assigned. Unexpected resets/corruption stop the affected series; investigate
boundedly, preserve evidence, restore before review if unresolved. No need to
expand into firmware recovery or scheduler work. Three prior matched game trials
per codec took roughly43 seconds each, excluding setup, retrieval and restoration;
this is an estimate, not a collection timeout.

Author's latest colour decision: RGB222 expands exactly to RGB888 levels
0,85,170,255. RGB565 introduces unequal channel rounding and is out of scope.
Official PNG API presence does not establish indexed encoding or performance;
inspect source before selecting. Existing PNG Linux/browser work is reused.

I01/I02: mainboard cue cleared through admitted CLI; actual startup preserved.
Official JPEG and PNG source review is in RESEARCH.md. Candidate compiles with
IDF5.5.5 and preallocated image scratch; both codecs are compiled into the same
image, but JPEG testing precedes PNG. PNGenc retains its embedded memory
configuration. Source preparation and browser ImageBitmap path are task-owned.

Setup correction: initial build exhausted HTTP URI slots after adding two
diagnostic endpoints. Server stopped before codec calls. Increase capacity by
two; no graphics/scheduling change. Rebuild and independently verify before
continuing. Initial boot/firmware evidence retained privately, not timing data.
