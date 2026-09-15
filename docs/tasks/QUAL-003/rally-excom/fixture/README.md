# RXPROBE r01 — first Rally pixel reproduction

This is a correctness probe, not a frame-rate measurement or the full game.
It reproduces current Rally's VDU24/MOVE viewport activation, protected24-row
HUD, horizontal graphics-viewport scroll, negative-left clipped one-row span,
and sixteen alternating buffer updates.64pixel queries compare retained HUD,
blue sky, white span edge and untouched road against fixed stock-palette values.
Pixel replies fence queued drawing. Dark red/blue are170, not255.

Build with `make -C docs/tasks/QUAL-003/rally-excom/fixture`.
Before loading, startup must select mode136 and disable logical scaling is done
by the fixture. Run `RUN . LEGACY.CSV` or `RUN . EXCOM.CSV`; files must not exist.
Fixture rejects a mode whose base is not8; the launcher must independently
ensure136 rather than8. It never changes mode or routes. Results are closed
between probes and include begin records and terminal pass/failure count.
Missing terminal is incomplete. The final screen shows only aggregate counts.

Paired launch procedure: preserve root autoexec and installed firmware. Stage
fixture under a fresh /extender test directory. Select EMOS Legacy in startup,
VDU22 136, load/run with LEGACY.CSV; then select ExCom, VDU22 136 and run the
identical binary with EXCOM.CSV. Use existing SD service to retrieve both results,
restore startup, and compare matching probe/frame coordinates. No browser is
needed for this first test. Retain all failures; do not silently repair or rerun.
A disagreement requires stock-reference checks before attributing a port defect.

Official contracts: agon-docs/docs/vdp/{VDU-Commands,System-Commands}.md;
stock agon-vdp v2.16.0 video/{agon_palette.h,vdu_sys.h,context/graphics.h}.
Stock sendScreenPixel calls waitPlotCompletion before reading drawing memory.
This test does not yet exercise Rally's buffered span tables, affine traffic,
bitmap strip repairs, full phase flow or output performance. Those follow if
these most basic protected-page operations pass.
