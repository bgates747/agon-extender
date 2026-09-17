# Execution notes

## Executive summary

Physical JPEG corpus checks completed:39 case/quality combinations, RGB channel
order verified with64 solid8x8 colour blocks. Native browser decoding succeeded;
JPEG remains lossy. Streaming qualification follows before any verdict.

1. Initial JPEG RPC series stopped on HTTP400 after noise. The first harness
   did not preserve its error body, so its cause is unclassified. A direct repeat
   of the next case passed. The resumed harness preserves errors and permits
   one retry only for explicit incomplete-body rejection; completed cases were
   not silently discarded. Subsequent checks passed, including four malformed
   requests followed by a healthy JPEG. This is not a device reset observation.
2. Corpus rows measure one warmup plus three encoded samples; browser readback
   runs separately. Resumed completion duration covers resumed segment only;
   initial segment and preparation are not included. Future duration estimates
   must not mistake it for total elapsed runtime.
3. JPEG quality90 selected for matched game trials: middle requested quality,
   no chroma subsampling, all64 primary patch levels within6 units per channel.
   Quality80/95 remain recorded for space/fidelity assessment. No FPS conclusion
   from the standalone hardware encode time alone.
4. First JPEG sprite reference inspected visually: correct colours and geometry,
   edge errors limited in this sparse reference. Real Nurples screenshots and
   dense/noisy references remain necessary; this is not Author visual acceptance.

5. First game attempt invalidated by host module shadowing: adding the private
   helper directory to sys.path allowed Playwright screenshot setup to import
   its old queue.py instead of standard-library queue. Its obsolete SD state
   rejected connection before any upload/test invocation; no old fixture was
   deployed. Preload standard queue/concurrent.futures.thread before helper
   path insertion. Discard this trial from measurements; preserve host traceback.

6. Replay SAVE names must be unique: official MOS mos_SAVE uses FA_CREATE_NEW.
   Reusing first-attempt trace names aborted the second batch before SD return.
   Corrected controller gives phase/attempt-specific batch, EXEC, trace and
   telemetry paths, all inspected together. No firmware correction for this
   setup error. Only the final complete uniquely named series counts.
