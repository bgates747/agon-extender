# W10 — Repeat the paired suite with stock drawing drain

**Authorized 2026-09-10.** The Author accepted the W9 findings and directed
the suggested next step: the existing full paired suite with browser video
connected, followed by the planned personal Nurples playtest after reviewing
the measurements. This increment prepares and collects that suite; no new
firmware, executable or timing instrumentation is required.

## Fixed inputs and scope

1. Keep P4 `uart-excom-console-r08-b2026-09-10-21-23-43Z`, verified in
   deployment `PORT-003-2026-09-10-21-31-49Z`. Keep EMOS
   `agon-emos-v0.1.12-b2026-09-10-03-50-35Z` and mainboard VDP 2.16.0.
   The [deployment receipt](evidence/stock-drain-local/deployment.json)
   identifies the P4 image and manifest. Do not reopen P4 serial or reset it
   for this run; the operator resets only Agon after reconnecting video.
2. Reuse `uart-path-benchmark-r03-b2026-09-10-18-21-38Z` unchanged. Restore
   its original full-suite autoexec, whose final command is `RUN`, using the
   existing deployment script. Preserve all six prior results and back up
   replaced files. Autoexec selects mode 0 on both displays and Extender
   keyboard input before the application starts. The fixture never selects
   video mode. The accepted full-suite emulator review still covers these
   exact workload and startup bytes; no new visual review is required.
3. Run the [existing cases and timing boundaries](paired-benchmark-plan.md):
   four entries × two payloads × two routes × three repetitions, 48 rows.
   Keep one connected browser video client visible throughout. The operator
   leaves keys released until the final result and Legacy prompt. Native USB
   keyboard stays selected in both modes. No sniffer or host capture script
   is needed for this saved-clock comparison.
4. The old executable, manifest and CSV declare P4 r07. Preserve those
   original records; bind this run to the verified r08 deployment in a
   separate condition record, explicitly overriding that compiled P4
   annotation. Browser-connected annotations apply again. Record the browser
   condition as required during preparation and confirm it with the operator
   during collection; do not claim a measured server client count.

## Collection and comparison

1. After the final summary and MOS prompt, the operator checks native USB
   typing outside measurement and returns the SD. The preceding W9 keyboard
   observation remains unconfirmed; this new check proves responsiveness
   after W10, not retroactively after W9. No routine screenshot is required.
2. Identify the one new CSV from the preserved six-result inventory; retain
   it byte-for-byte. Verify unchanged executable/startup, the r08 deployment
   binding, all 48 distinct cases, pixel values, statuses, clock arithmetic
   and successful Legacy return. Preserve an incomplete or failed record
   rather than silently retrying. Record browser disconnects or unexpected
   interaction as deviations affecting the comparison.
3. Report per-case Legacy/ExCom send, tail and total clock medians and ranges,
   and compare with the [original 48-row baseline](hardware-baseline.md).
   Keep setup-query and completion-query first timeouts separate from eventual
   success. In particular, W9 still observed a late setup reply even though
   measured point completion improved. Do not average that issue away.
4. Relate the counted-point result to W9 cautiously: this suite has a connected
   browser and coarse 16.67 ms clock resolution, while W9's wire measurement
   had browser video disconnected. Results include caller/UART/receiver waits;
   they do not measure pure EMOS CPU cost or browser presentation latency.
5. Stop after collection and present the result. If it supports the improvement,
   the next handoff is the Author's ordinary Nurples playtest, with the current
   game and no diagnostic controller or game modifications. Core-affinity and
   further optimizations remain deferred as previously directed.

Private media paths, backups and preparation receipts live in the local bench
record. This is a reuse of the existing fixture and method with the selected
r08 image; no new artifact identity or status promotion is introduced.

## Prepared handover

The original full-suite startup was restored with the established deployment
script. Only the final autoexec command changes from the preceding trace;
the executable, manifest, boot smoke and six existing CSVs keep their hashes.
The SD is safely unmounted. [Preparation](evidence/stock-drain-full-suite/preparation.json)
binds the selected firmware and preserved result inventory. No hardware run,
browser observation, firmware operation or P4 serial session was started.
The operator can insert the SD, connect one visible browser video client,
reset Agon once, and return the SD after the full result and keyboard check.

## Collected result and regression

After clarifying an earlier premature card return, the Author completed the
run. The sole new CSV passes all 48 cases and Legacy return; the Author
confirms responsive Legacy keyboard use, then reports substantial ExCom
Nurples hangs. [Findings](stock-drain-suite-findings.md) retain per-case
comparisons, remaining ordinary-query timeouts and the separate gameplay
regression. W10 measurements await review; no next repair or run was started.
