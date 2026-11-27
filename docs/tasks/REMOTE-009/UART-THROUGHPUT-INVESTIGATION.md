# REMOTE-009 — Investigate slow bulk UART in both directions

Find out what prevents the P4 and EMOS from moving bulk data over UART at
roughly the rate of the ordinary EMOS ↔ mainboard VDP path. Start with the
earliest working code and trace when each check, wait and acknowledgment
entered the loop. Return a measured explanation and the smallest repair that
addresses it for all consumers. Extender owns this investigation.

## Starting evidence

The recent direct upload moved 1,089,200 bytes in 285.684 seconds
(3,813 B/s). The November 2 direct upload moved 1.1 MB at 3,881 B/s. On
November 2 the P4-owned worker moved a comparable upload in 43.240 seconds
(about 25.4 kB/s). The later sequential reader brought a staged 1.1 MB
download to 43.573 seconds (about 25.2 kB/s). These file timings provide
historical controls. Compare UART wire time separately from SD-card and
host work. At 1 Mbaud with 8N1, the theoretical byte ceiling is 100,000 B/s.
Establish the actual baud on each path before comparing rates.

- [Original direct fast baseline](BASELINE-R01.md)
- [P4-staged comparison](STAGED-RESULTS.md)
- [Sequential download comparison](DOWNLOAD-RESULTS.md)
- [Accepted separation of host HTTP from the mainboard transfer](../../decisions/ADR-2026-11-02-staged-fast-file-transfers.md)

## Work and review

- REMOTE-009-009 [ ] **Start with the earlier code.** Use Git history to find the earliest working P4/EMOS UART file path and its matching host client, listener and resident firmware. Pin the exact revisions and available receipts. Compare that source with the November 2 introduction of the P4 worker (`ce3183ad`), the sequential-reader adoption (`8aa3245d`) and the current deployed and direct paths. Trace both directions. For each CRC or digest, verification read, reply, delay, sync, file reopen or seek, buffer copy and scheduler wait, record where it runs, when it appeared, how often it runs and what it was intended to protect. Keep checks that were already present in the earliest baseline distinguishable from later additions. If no runnable artifact survives, use its source and retained evidence and label the resulting limits.

- REMOTE-009-010 [ ] **Account for the time.** Trace the Pi HTTP client, P4 worker, UART send/receive and flow control, EMOS service and eZ80 filesystem calls. Use the ordinary EMOS-to-mainboard-VDP stream as the forward reference. Establish a matched VDP-to-EMOS producer for the reverse direction or report that reference as unavailable. Use identical byte counts, comparable framing and actual baud, with fixed and large payloads. Compare the ordinary stream, a P4 ↔ EMOS transport-only stream, and matched SD-file transfers. Show elapsed time and useful B/s separately for HTTP, UART active time and gaps, and SD reads/writes/syncs where observable. Begin with retained evidence and offline checks. If those leave a material gap, present a bounded physical A/B for review before booking or changing the bench. Change one check or wait at a time so the evidence can attribute any gain.

- REMOTE-009-011 [ ] **Recommend the shared fix.** Report which costs the evidence supports, how much each contributes, and which checks and waits can be removed or moved to transfer boundaries. Prefer the earliest working fast path wherever it satisfies the current contract. The Pi exchanges bulk data with P4, P4 and EMOS own the admitted UART transfer, and the eZ80 foreground utility owns mainboard file I/O. Use ordinary flow control and existing error reporting. Keep filesystem errors, clear terminal status and uncertain-write recovery. Do not add checksums, verification rereads or per-record host acknowledgment. If local UART replies themselves account for a material gap, show the smallest safe change to remove that barrier in both directions and identify the components that need it. Report the expected and still-unverified throughput against the matched VDP reference. Stop for Smith's review of the findings and repair before implementation.
