# BENCH-005 — Injected keyboard and visible-response latency

## Executive summary

Measure the reported difference between responsive Aginvadors controls and delayed
ExCom console typing using a bespoke application. Author authorizes execution,
exclusive bench use and a hardware voice alert at completion. Goal task.
No optimization is presumed; establish which measurements the installed firmware
can support before attributing delay to input, graphics or networking.

## Frozen execution contract

1. [ ] K01 — Inspect input, acknowledgement and capture paths. Freeze this contract
   before implementation; retain identities and host-monotonic timing definitions.
2. [ ] K02 — Build a bounded app with character and keymap variants, idle and
   continuously updating screen variants, a sequence-coded visible response,
   explicit exit and timeout. Keep firmware and production games unchanged where
   possible. App never changes mode; select mode 8 in temporary autoexec setup.
3. [ ] K03 — Measure repeated injected taps under matching conditions. Distinguish
   HTTP admission, event drain, actual application receipt and captured/displayed
   image. Existing resident telemetry is Legacy-only: do not call its availability
   a paired ExCom acknowledgement. Use it for a bounded Legacy control if viable;
   otherwise explicitly mark that measurement unavailable. No fake app receipt
   inferred from the keyboard queue. ExCom visible-response tests are primary.
4. [ ] K04 — Compare idle/busy and character/keymap distributions (ms, sample count,
   median, p95, worst), plus console control where practical. Preserve raw samples,
   errors and diagnostic limits. Browser capture/presentation is not physical
   monitor latency; software injection bypasses USB keyboard polling. Polling and
   observation overhead must be stated. Do not use CLOCKS_PER_SEC=100 to convert
   MOS time; host monotonic clock is the latency authority.
5. [ ] K05 — Restore startup, release injected keys and web observer, return Legacy
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
