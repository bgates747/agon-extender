# REMOTE-009 — Remove HTTP turnaround from mainboard file transfers

The current host client serializes every 212-byte upload through HTTP, fsyncs
host state twice per record and waits 40 ms after a pending response. Move that
loop to a P4 worker, using P4 SD staging between network and mainboard traffic.
No new resident EMOS code is needed. Hardware qualification is prohibited while
the Author's bench is occupied; do not disturb Wolf3DOrig's active transfer.

## Scope and decisions

1. Author authorized task documentation then implementation on 2026-11-02.
   Extender owns the P4 worker, private spool and Python client. Existing EMOS
   owns UART1 admission/routing; foreground sdserve owns mainboard file I/O.
2. D01 accepted: P4 stages uploads before transmitting to EMOS and stages
   downloads before serving HTTP. HTTP backpressure stays outside the eZ80
   transfer loop. Complete staging is the initial implementation; concurrent
   prefix draining is unnecessary for this improvement.
3. D02 implementation choice: reuse installed ext.sdlink/major2 records.
   Local UART replies remain per record. This removes HTTP turnaround but is
   **not continuous UART streaming or a single payload admission**. Do not
   claim the Jukebox rate; a bulk carrier needs separate receiver/backpressure
   work. Record this remaining cost explicitly.
4. Use checksum-free major2 only: no CRC, substitute checksum or full-file
   verification download. Keep exact counts, filesystem errors, staged
   activation/backups, and explicit uncertain-result recovery.
5. One P4 job owns the queue and local media. Conflicting work reports busy;
   failed staging is retained and transport reset aborts. Whole-file jobs never
   replay automatically after uncertain admission; existing identical-record
   retries within a live UART session remain. Host state is durable at job boundaries.
6. Initial offline work left installed tools/production/hardware unchanged.
   Author releases the bench on 2026-11-02 for R09-06: monitored matched P4
   deployment and transfer comparison, reset after current startup inspection.
   Preserve incoming firmware/startup/listener/wiring and normal CLI; no autoexec
   edits or unrelated tests. Prior occupied-bench restrictions are historical.

## Research baseline

1. Official MOS API.md (agon-docs f9806bd3cbff6ed5d1c08bef1d51fed11764b86b),
   ffs_fread/ffs_fwrite: use maintained sdserve exact
   read/write counts and filesystem-result handling. No new MOS ABI/wiring.
2. Jukebox pre-skin Classic v0.11.0-beta,
   9edfba629a2a2934f4bc66ee415d73fe2f32b75f: play.inc reads through ffs_fread
   at 60 chunks/s; vdu.inc sends header/payload with RST.LIL18. No HTTP wait
   in that loop, and its receiving VDP does not write a file.
3. [Current carrier](../protocols/mainboard-sd.md), sd_service.hpp,
   sd_target.hpp and local/media.hpp own framing, replay and physical-card
   exclusion. Existing staged WebDAV is checked-mode, with CRCs and whole-file
   comparisons; it is unsuitable for this checksum-free path.

## Work and validation

1. [x] R09-01 Implement host-testable P4 transfer engine: major2 negotiation,
   exclusive queue ownership, bounded SD buffers, byte/phase counters and
   terminal success only after confirmed completion.
2. [x] R09-02 Implement P4 SD staging/background execution and HTTP admission,
   status, bulk download and explicit completed-job release. Block competing
   RPC and abort on transport/session loss; preserve failed stages.
3. [x] R09-03 Add explicit staged host client with durable per-job state and
   observation-only resume; no re-submission of uncertain operations.
4. [x] R09-04 Exercise real engine/client with empty/arbitrary binary/>64KiB
   files, both directions, duplicate/conflicting admission, short I/O, missing
   or full media, protocol/sequence errors and reset. Compile native sources.
5. [x] R09-05 Document candidate requirements/invocation, separate staging,
   mainboard and HTTP timings, and remaining per-record UART overhead.
6. [x] R09-06 After Author releases bench: preserve exact incoming pair,
   deploy identified candidate, compare matched >1MiB files against old fast
   client, verify actual bytes outside timing and normal CLI/startup behavior.
   Author acceptance/version/qualification gates precede promotion.
7. [x] R09-07 Attribute the slow P4-owned record loop observed in the first
   mounted-card run. Preserve its complete measured result before changing
   the candidate. Compare a worker-priority-only correction with the same
   small/large byte proofs; keep UART/framing/listener/renderer unchanged.
   Record whether the hypothesis is supported rather than declaring scheduling
   causal from priority inspection alone. The worker must remain blocked while
   waiting, preserve USB/video service, and leave normal CLI/input intact.
   Predeclared control gate: compare the65,537B pairs first. Repeat1.1MB only
   if either direction's control call is at least10% shorter than its first-run
   counterpart. Otherwise retain the negative/unchanged result without another
   ten-minute large repeat. This selects further work, never a preferred timing
   sample; all measured cases remain evidence and no reset/replay is implied.
8. [ ] R09-08 Author review and production closeout: obtain acceptance and an
   agreed version, finish required canonical release qualification and package
   the exact tested component/tools through the production protocol. The
   bounded file result does not authorize broader unrelated qualification or
   imply that the canonical release suite has run.

## State

R09-01–07 are complete.56 offline checks, matched native builds and the bounded
Legacy file comparison pass. [Final measured results](REMOTE-009/STAGED-RESULTS.md)
record1.1MB upload43.24s/download243.20s,6.554x/2.087x the original client.
Empty/257/65537/1100000B pairs and missing-source/CLI handback pass in both
physical variants. Raising the blocked file worker from priority1 to4 resolves
a major scheduling cost; no renderer, UART, resident EMOS or listener change.
Exact incoming full16MiB P4 is restored and verified, startup/listener/CLI pass,
and serial/reset resources are released. The candidate remains uninstalled;
Author acceptance, versioning and canonical production gates remain open.

Physical preparation update: [original fast baseline](REMOTE-009/BASELINE-R01.md)
passes exact1.1MB upload/download. Identified matched r27 candidate is built,
reviewed and uninstalled. P4 SD initialization times out across fresh boots;
Author power cycled both devices and authorized continuation. Fresh P4 status
still times out before filesystem access. Manufacturer-source review identifies
an omitted active-low GPIO45 card power switch; the local driver enabled LDO4
but never enabled the card supply. Correct this prerequisite before repeating
the staged-transfer qualification. No new-path speedup or promotion is claimed.

## P4-PC card power correction — R09-06 prerequisite

1. [x] Compare board schematic/PCB and manufacturer SD test at OLIMEX/ESP32-P4-PC
   `04032d68e5c727870f9d40beb9e37b7ab3a66916`. Rev C GPIO45 is `SD1_PWR_EN`;
   FET1 switches card VDD_SD independently of the shared GPIO-bank LDO4.
   `SOFTWARE/ESP-IDF/p4_production_test/sdkconfig` selects GPIO45, active low,
   100ms stabilization. Its `components/sd_card_test/src/sd_card_test.c` enables
   that switch before mounting. Other SD pins match the existing profile.
2. [x] Express the switch in the PC board profile, validate its fixed mapping,
   and enable it before the first mount. Preserve fixed3.3V LDO4, no automatic
   retries, no unmount/power-cycle/format. DevKit skips the PC switch.
3. [x] Build a fresh identified matched candidate and verify its installed bytes;
   retain the earlier uninstalled r27 unchanged. The new23:11:45Z build passes
   full16MiB readback with unchanged bytes outside written application sectors.
   [Physical evidence](REMOTE-009/CARD-POWER-R01.md) records persistent mount
   timeout and correct unavailable-media rejection with clean UART/CLI handback.
   Exact incoming full16MiB P4 is restored and verified afterward; normal CLI,
   unchanged startup/listener and released serial/reset resources pass.
4. [x] Establish physical P4-PC card presence/seating and successful mount.
   Author found the card jarred loose, reseated it and rebooted. Fresh original
   r25 mounts successfully with ESP_OK; ordinary Legacy startup/listener read
   and EXIT pass. Physical seating explains the observed timeout; the source
   power-enable omission was not proven causal and original r25 mounts without
   that correction. No new flash or staged job was invoked in this preflight.
5. [x] After Golem yields and the Author returns the bench, deploy the retained
   matched candidate and run the successful staged-file cases/comparison.
   This prerequisite changes P4 software only; EMOS, native VDP, listener,
   startup, physical wiring and unknown user files remain unchanged.

## Mounted-card performance attribution

Author explicitly gives Extender the bench after Golem yields. Candidate r27
is installed with exact whole-flash verification before the write and independent
readback afterward. Card mount and actual CLI pass. First mounted-card cases
verify empty,257B and65537B files, but65537B takes about20.1s in either direction.
The recorded P4 worker phase takes18.7–18.8s; bulk HTTP takes less than0.2s.
The1.1MB cases must complete before this run is treated as the comparison.

Bounded scheduling hypothesis: `storage/fast/http.cpp` starts `sd-fast` at
priority1, while `video.ino` starts the continuously serviced `processLoop`
UART owner at priority3 on core0. The existing rolling drawing task is priority5;
this matched build's rolling output is priority6 on core1 (confirmed compiled
definitions). A blocked worker at priority4 is
the proposed single-variable control. Existing1000Hz FreeRTOS ticks rule out
a10ms tick assumption. Worker timing also includes local-file I/O, so the current
timer does not independently attribute CPU wait, UART wire or eZ80 filesystem
time. No per-record logging or new integrity work is proposed.

Outcome: priority4 passes the predeclared short-file gate and full1.1MB
confirmation. Compared with priority1, upload301.930→43.240s and download
308.909→243.200s. Every byte pair and error handback passes. Final source67dfc55b
and appfb8283f7 are frozen; incoming P4 full006397a5 and EMOS84da2c5a remain the
handback authority. Remaining download costs are not independently attributed
by these combined worker timers. [Portable evidence](REMOTE-009/STAGED-EVIDENCE.json)
records both variants, the gate and final restoration; no production/tag change.


## Author-approved installed fast-transfer handoff

After the earlier exact restoration, the Author requests Golem use the new fast
transfers, authorizes pinning and explicitly approves installing the pinned P4
image and leaving it installed for Golem. The
[exact firmware/client pin](REMOTE-009/FAST-TRANSFER-PIN.json) is committed;
retained local binaries match its sizes and hashes. Fresh pre-reset CLI reads
verify unchanged startup and listener. Whole incoming flash verification precedes
the application-only write; independent full16MiB readback verifies appfb8283f7
and unchanged bytes outside its sectors. Clean boot, actual Legacy CLI, mounted
P4 card and one exact257B staged upload/download pass. The listener exits,
staged job is idle, input/controller are ready and all USB/reset owners release.
No larger suite or PCM test is invoked. Golem receives the installedr27 baseline;
originalr25 remains rollback, rather than the requested end state. EMOS, native
mainboard VDP, startup and wiring stay unchanged. This bounded deployment is not
production selection or complete canonical qualification. Local evidence and
custody are indexed in the machine-local bench record.


## R09-DL01 — Self-assigned download throughput improvement

The Author directs Extender to work on download speed while other agents prepare
and explicitly permits reserving its own finite test slots (2026-11-03). Track
this as a self-assigned implementation/verification tranche. Consumer leases
remain exclusive; BBC BASIC and the separately authorized6502 work receive
coordinated slots when ready. Source work does not occupy the bench.

1. [x] Review the exact accepted listener READ path and P4 worker call sequence,
   relevant official MOS file APIs and existing tests. Pin matched inputs and
   bound a short research précis before implementation. Attribute filesystem,
   packet/scheduling and final HTTP costs separately; no per-byte logging.
2. [x] Select the smallest measured/removable remedy, preferring reuse of the
   foreground listener's existing file APIs and state. Keep resident EMOS
   unchanged if the foreground utility can own it. Do not add checksums or a
   new bulk wire protocol merely to optimize this path.
3. [x] Implement in component-owner sources on pinned isolated inputs; test
   file-handle lifetime, sequential/random offsets, EOF/errors, writes/renames,
   session changes and EXIT as appropriate. Preserve the accepted listener and
   deployed P4r27; stage a separately identified utility/candidate when needed.
4. [x] Reserve/assert a finite own bench slot through the central scheduler after
   independent preparation and current consumer coordination. Compare matched
   baseline/candidate file cases with exact host byte proof outside timing,
   separate stage/worker/HTTP/end-to-end units and ordinary CLI cleanup. Gate
   another1.1MB comparison on a useful short-file result; no full suite, PCM,
   startup change or uncertain replay. Existing measured baseline243.20s for
   1.1MB is contextual, not a fresh controlled baseline on a different file.
5. [x] Preserve raw passing/informative failing evidence, restore accepted
   components/normal CLI/input/idle resources, release promptly to next ready
   agent, report achieved speed and remaining costs, and update this record.
   Production promotion/version selection remains a separate acceptance gate.

Initial source observation: `projects/sdserve/src/service.c` READ opens, seeks,
reads and closes the source on every<=216B request. A retained sequential file
handle is a hypothesis worth checking; source review must bound invalidation,
filesystem ownership and cleanup before changing behavior. P4 worker timers
combine local-file I/O, UART and eZ80 service work, so current counters alone
cannot prove this is the whole download bottleneck.


[Bounded download research and candidate contract](REMOTE-009/DOWNLOAD-R01.md)
pins the accepted listener and P4 session behavior before implementation.

The isolated EMOS-owned fast reader passes61 instrumented engine checks (three
skips: two independent-checkout codec lookups and the checked-only absence of a
persistent handle) and seven application-helper checks. Direct comparison of
the owner codec to Extender's codec passes. For a1000-byte/five-request read,
actual fast filesystem calls fall from five opens/sizes/seeks/closes to one
open, one size, zero seeks and one close; all five reads and original wire
records remain. Fast CRC invocation count remains zero. This establishes the
removed call cost, not a physical throughput improvement. The6502 consumer owns
the bench; candidate build and host preparation continue without target access.

The finite physical tranche now passes and releases central custody. Matched
65537B host elapsed falls13.728→3.029s;1.1MB falls250.920→43.573s (5.759×,
82.63percent less elapsed). All four downloads match exact source bytes; record
counts stay identical. The accepted listener/startup and all firmware remain
unchanged, temporary aliases are removed, and actual CLI/input/idle resources
pass. [Download results](REMOTE-009/DOWNLOAD-RESULTS.md) and
[exact evidence](REMOTE-009/DOWNLOAD-EVIDENCE.json) retain scope and identities.
Author acceptance, naming/promotion and any broader qualification remain open;
the installed fast-transfer pin still selects its original listener.
