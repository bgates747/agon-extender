# BENCH-005 — Injected keyboard and visible-response latency

## Executive summary

Measure the reported difference between responsive Aginvadors controls and delayed
ExCom console typing using a bespoke application. Author authorizes execution,
exclusive bench use and a hardware voice alert at completion. Goal task.
No optimization is presumed; establish which measurements the installed firmware
can support before attributing delay to input, graphics or networking.

## Frozen execution contract

1. [x] K01 — Inspect input, acknowledgement and capture paths. Freeze this contract
   before implementation; retain identities and host-monotonic timing definitions.
2. [x] K02 — Build a bounded app with character and keymap variants, idle and
   continuously updating screen variants, a sequence-coded visible response,
   explicit exit and timeout. Keep firmware and production games unchanged where
   possible. App never changes mode; select mode 8 in temporary autoexec setup.
3. [x] K03 — Measure repeated injected taps under matching conditions. Distinguish
   HTTP admission, event drain, actual application receipt and captured/displayed
   image. Existing resident telemetry is Legacy-only: do not call its availability
   a paired ExCom acknowledgement. Use it for a bounded Legacy control if viable;
   otherwise explicitly mark that measurement unavailable. No fake app receipt
   inferred from the keyboard queue. ExCom visible-response tests are primary.
4. [x] K04 — Compare idle/busy and character/keymap distributions (ms, sample count,
   median, p95, worst), plus console control where practical. Preserve raw samples,
   errors and diagnostic limits. Browser capture/presentation is not physical
   monitor latency; software injection bypasses USB keyboard polling. Polling and
   observation overhead must be stated. Do not use CLOCKS_PER_SEC=100 to convert
   MOS time; host monotonic clock is the latency authority.
5. [x] K05 — Restore startup, release injected keys and web observer, return Legacy
   prompt, document actionable findings and send hardware voice notification.

## Boundaries

No Golem. No production app changes. Use /test/bench005. Temporary autoexec is
backed up/read back/restored. Hardware pin/firmware changes require a documented
need and bounded rollback; initial test uses installed firmware. Freeze any
necessary follow-on instrumentation amendment before changing firmware. Missing
observability is a result to report, not permission to mislabel measurements.

## Sources

Official local Agon docs MOS API and VDP commands; agondev input wrappers and MOS
interrupt implementation; existing BENCH-001 telemetry contract; installed web
client decoder and scripts/keyboard.py. Record concrete APIs in results/source.

## K01 findings / instrumentation refinement

Installed web client explicitly limits frame credits to 30/s at all resolutions.
Preserve this setting for the comparison. Browser-origin keyboard requests are
intentionally rejected; use the authorized host injection helper and bracket a
host/browser monotonic-clock alignment, retaining its uncertainty. This avoids
weakening the input boundary. First rejected request supplied no accepted sample.

Application character-state polling is not MOS getkey; test actual blocking
`getch()` separately (idle only). Its blocked call needs host Escape for exit;
the raw-tick safety cap only applies while the foreground loop runs. Host trial
and injection-session deadlines bound this test. Legacy telemetry payloads must
satisfy the existing v2 envelope constants even though the contents are synthetic.

## Self-assigned diagnostic control (within latency scope)

After the installed 30 fps client trials, temporarily remove only the client-side
credit delay in a headless observer for one matched idle-character group. This is
host-only instrumentation, not a deployed UI or firmware change. It tests whether
the identified output cap materially contributes to visible delay; retain the
30 fps baseline as the user's actual experience. No 60 fps performance claim
without measured delivery. Restore by closing the observer.

## Author extension — text readback

6. [x] K06 — Provide and validate a read-only MOS-screen capture utility on Legacy
   and ExCom using stock VDU 23,0,&83 queries. Save text on the Agon's SD for host
   retrieval. Preserve display contents during capture, include cursor/dimensions,
   mark unknown glyphs/timeouts. This is font/pixel recognition, not an authoritative
   character-cell backing store; no claim of graphics or changed-font coverage.
   Loading the helper itself leaves CLI text on screen; retain this limitation.

Legacy telemetry admission returned 27 (provider not found in the inspected EMOS
status enumeration); this installed configuration does not supply the requested
service. Fixture r02 returned 2, producing the Author-observed "Internal error".
R03 records admission status to SD before returning. Do not infer SD failure or
latency from this rejected control. Paired app-ack timing needs an instrumentation
follow-up; this bounded run records it as unavailable rather than flashing a new
EMOS purely to force a result.

K03 completed its explicitly permitted unavailable-control branch: Legacy telemetry
provider absent, no paired receipt claim. K06 passed interior text on both routes;
stock edge exclusion and cached cursor documented. See [results](BENCH-005/RESULTS.md).

Hardware voice fresh execution receipt verified; startup restored byte-for-byte,
observer closed, Legacy MOS prompt. First bounded investigation is complete, with
paired app-receipt timing explicitly unavailable and retained as follow-up.

## Browser pacing continuation

Author authorized [W01–W02](BENCH-005/web-pacing/PLAN.md): deploy a 60 fps request
ceiling with existing RLE2 and credit flow, then hardware notify for review.
Escalating push/worker options are planned but not authorized for implementation.

W07a [packed-output audit](BENCH-005/packed-output/RESULTS.md) identifies the
installed 512×384 RLE2 size ceiling; mode0 falls back to raw. Native packing
proposal remains unimplemented pending Author review.

## Author-authorized composed packing continuation

[W08 contract](BENCH-005/composed-packing/PLAN.md) supersedes the unimplemented
native-plane proposal: compose everything first, losslessly pack final colours,
and benchmark all supported non-50-Hz modes. Goal execution authorized, hardware
notification at review readiness.

W08 implementation and the 54-mode hardware screen are complete; bounded longer
confirmation and closeout are recorded in the linked contract. See
[packing results](BENCH-005/composed-packing/RESULTS.md) and
[findings](BENCH-005/composed-packing/FINDINGS.md). Human review remains pending;
this does not close BENCH-005's unrelated latency or pacing questions.

W09 [six-bit continuation](BENCH-005/composed-packing/sixbit/PLAN.md) is authorized:
preserve W08, pack full 64-colour composed output, benchmark Nurples only and
hardware notify for interactive review.
