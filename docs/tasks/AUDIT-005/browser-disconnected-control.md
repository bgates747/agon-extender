# Browser-disconnected counted-point control

Procedure: **uart-path-capture-r02**. W7 of [AUDIT-005](../AUDIT-005.md).
The Author accepted the connected-run findings, requested this formal contract
and its commit, and preapproved execution on 2026-09-10. No unresolved user
choice blocks preparation. This is one exploratory control, not qualification.

## Question and fixed comparison

Does removing browser video demand materially reduce P4-induced UART stalls
for the same counted-point workload? The reference is the completed connected
run `AUDIT-005-2026-09-10-19-44-52Z`, whose
[waveform and CSV findings](uart-cts-findings.md) are frozen with this contract.
Its send wire span is 4.456 s, including 3.407 s of inter-byte idle with P4
withholding CTS permission; final query/reply takes 0.625 s.

1. Keep the exact r03 executable and its `RUN . trace count points` invocation,
   mode 0 on both displays, 512 counted writes of 64 bytes and 32,768-byte
   payload. Keep EMOS v0.1.12 and P4 console r07 at the build IDs and hashes in
   [the original procedure](uart-cts-capture.md#fixed-inputs-and-purpose).
2. Keep the existing USB keyboard connected, all keys released, r03 wiring,
   four analyzer probes and common ground. Keep Ethernet connected. The
   operator resets only Agon after the acquisition-ready cue; the P4 stays up.
3. Acquire the same 24 MHz, 720,000,000 samples using the tested raw-first,
   post-acquisition SR packing path, with the same decoder and boundaries.
4. Change only browser video demand: close every Extender browser tab/window
   on every device, including background tabs. Do not merely switch tabs or
   minimize the browser. Do not open any new agent or operator video client.
5. Wait at least five seconds after closing the final client before arming.
   Keep the tabs closed through acquisition and Agon's return to Legacy. The
   P4's existing HTTP/video service and Ethernet remain enabled; no firmware
   build or service configuration changes are authorized for this control.

The host records the browser condition as **operator-confirmed disconnected**,
not independently measured server client count. The installed firmware has no
selected external client-count evidence channel; opening P4 serial to inspect
logs can reset it and is excluded. The five-second settlement interval is
procedural margin, not proof that every internal operation has drained.

## Fixed-fixture metadata exception

The unchanged application writes the compiled annotation
`# browser=one_visible_connected_client_operator_required;entries_include_caller_cost`.
For this control that is the original fixture expectation, not a live browser
observation. Preserve the CSV byte-for-byte. The host condition record explicitly
overrides only that browser annotation and links the CSV, capture run ID and
procedure r02. Reject a purported browser-disconnected comparison without this
record. Do not relabel the reference run or change either executable to adjust
that annotation.

## Agent preparation and execution boundary

1. Commit the connected result, accepted findings and this W7 contract before
   executing the control. Standing preapproval covers r02 and registry r63.
2. Add the disconnected condition to the host/Pi capture metadata and operator
   prompt; retain the existing acquisition algorithm, raw sample packing,
   sample extent, marker/payload/reply validation and bounded completion.
   Preserve the r01 definition and original capture bundle.
3. Verify the four existing SD results, benchmark binary and startup against
   the returned media/deployment records. The card already has the correct
   startup, so no content change or repeat emulator workload review is needed.
   Record a new media handover manifest and safely unmount it.
4. Resolve the analyzer with a read-only scan, verify no other capture is
   active, stage and hash-check the new helper/condition record. Existing
   successful acquisition checks remain valid because acquisition mechanics
   do not change. Do not run extra calibration captures without new evidence
   of a problem.
5. Prepare a distinct browser-off launcher and notification-only emulator cue.
   The host records operator confirmation and completion of the five-second
   settlement before starting acquisition. No screenshot is required.
6. Stop after collecting and analyzing this one control. No silent retries,
   parameter sweeps, P4 reset, new instrumentation, firmware optimization or
   core reassignment follows from this authorization.

## Operator run sheet

1. Insert the prepared SD in Agon; keep both boards powered and all wiring
   seated. Close all Extender video tabs/windows, including on other devices.
2. Run the supplied browser-off launcher. Press Enter only after closing those
   tabs. The host waits five seconds, then arms the analyzer.
3. At **Reset Agon now**, press and release Agon's reset button once within
   five seconds. Leave keys released and the browser tabs closed.
4. Acquisition ends after 30 seconds of samples, then packs/verifies/retrieves
   evidence. It does not wait for browser output or a serial PASS. Keep waiting
   for the final result and MOS prompt on mainboard VGA before removing SD.
5. Return the SD. ExCom drawing is intentionally not visible while clients
   are closed; saved pixel replies and the CSV validate the workload. The
   normal Legacy return displays the final summary on mainboard VGA.
6. If the host stops before its reset cue, do not reset Agon. If it stops after
   the cue, let the fixture finish and return the CSV even if acquisition fails.
   If any browser reconnects during the run, disclose that condition; preserve
   the result but do not classify it as the disconnected control.

## Validation, comparison and stopping rule

Require the original acquisition, exact-payload, marker, reply, framing and
independent-decoder checks; require one valid counted-point CSV with unchanged
build/hash, clock arithmetic, pixel and successful Legacy return. Preserve
ordinary MOS timeout flags separately from eventual measured completion.
Validate Agon RTS during the final-reply wait as well as between reply bytes.

The comparison reports connected versus disconnected absolute values, deltas
and ratios for:

1. Agon send/tail/total clock intervals and corresponding wire intervals.
2. Payload byte time, idle with CTS high, idle with CTS low and longest gaps.
3. Final query/reply latency and reverse flow-control withholding.

Compare each run's software and wire boundaries at the clock's resolution.
Use the original connected capture, not the earlier full-suite median, for
this condition comparison. One run per condition is exploratory evidence,
not a noise estimate or universal performance claim. No arbitrary small
percentage difference will be called a proven improvement.

A large reduction in CTS-high idle with clients closed would implicate the
browser-video service path as a material contributor, but would not isolate
snapshot composition, scheduling, locking, encoding or Ethernet transmission.
Little change would leave the P4 parser/render path and remaining contention
as candidates; it would not prove browser service has zero cost. A mixed or
invalid result remains unresolved. In every case, record the observed result
and recommend one next bounded investigation or repair for Author review;
implementation of that repair is outside W7.
