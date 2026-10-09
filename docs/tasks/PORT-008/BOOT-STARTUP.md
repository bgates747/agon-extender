# PORT-008 — Candidate startup release binding

The Author approved wiring the tested release leaves into candidate startup,
with bounded waits and usable mainboard MOS if P4 cannot acknowledge. Work is
off-bench only. The ordinary UART-only composition remains selectable and all
ROM/image guards remain mandatory. No ExExt payload, deployment or promotion.

T01 [x] — EMOS owns a private startup coordinator. Its init_UART1 hook fences
shared pads before any UART1 open; its post-mainboard-startup hook performs
bounded release polling with interrupts enabled. Reuse the existing keyboard
deadline and transport claim/release. open_UART1 and UART restoration leaves
must refuse pin enable without the coordinator's grant. An ordinary source
profile supplies inert startup hooks; an explicit non-release candidate profile
selects the real coordinator. No new CLI diagnostic belongs in firmware.

T02 [x] — Measure complete guarded EMOS builds first. Entry ROM headroom is
354 bytes. If the candidate does not fit, preserve exact failure/accounting,
keep ordinary composition buildable and stop before further extraction or P4
integration. Do not relax the limit or hide candidate behavior in generic tools.

T03 [x] — If EMOS fits, bind P4's existing console owner to boot release under
an explicit private build selection. Do not bind shared UART outputs in setup.
Install the driver on the existing ISR/owner core, poll held controls, and restore
UART pins only when the adapter grants permission. Timeout/failure repeats
physical release, never timed UART fallback; keep ordinary startup selectable.

T04 [x] — Exercise actual startup/gates with modeled GPIO and linked EMOS
instructions: successful exchange, missing/old peer, moving/stalled clock,
partial restore/failure, wrong core and attempted early open. Preserve Legacy
mainboard input and existing console/keyboard ownership. Compile both selected
compositions, retain source/artifact identities, update parent/owner records
and pause. Bench reset/electrical tests remain separately gated.

## Research and limits

Reuse the official GPIO and F92 reset baseline in
[BOOT-RELEASE.md](BOOT-RELEASE.md), the exact handover levels in
[HANDOVER.md](HANDOVER.md), and the maintained UART/keyboard owners. The
keyboard opens UART inside its IRQ lock, so blocking handshake waits cannot
live inside open_UART1: they must run at the admitted foreground startup hook.
The mainboard clock is available after stock VDP startup, before autoexec.
Its existing deadline allows 600 units (nominally 5 s at 120 units/s) and a
262,144-iteration stalled-clock fuse; neither grants ownership on expiration.

The shared session/control candidate stays disabled for payload. This increment
does not complete runtime reset coordination, session freshness/stale-byte
quarantine, native block/status binding or physical one-board-reset qualification.
Those remain under the parent c2b/c3 gate. A boot release is not successful data
delivery. The coordinator must close its own startup-only transport lease after
recovery; ordinary keyboard admission still belongs to existing EMOS commands.

## Result

Implementation and focused checks are recorded in [BOOT-STARTUP-RESULTS.md](BOOT-STARTUP-RESULTS.md). Candidate ROM fits with 123 bytes free. Both full P4 compositions and frozen unchanged-source rechecks pass; no bench use or automatic commit.
