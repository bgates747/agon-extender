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
