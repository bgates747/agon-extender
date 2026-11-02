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
6. [ ] R09-06 After Author releases bench: preserve exact incoming pair,
   deploy identified candidate, compare matched >1MiB files against old fast
   client, verify actual bytes outside timing and normal CLI/startup behavior.
   Author acceptance/version/qualification gates precede promotion.

## State

Recorded before implementation. R09-01–05 complete offline:
[results](REMOTE-009/OFFLINE-RESULTS.md), 51 checks and native P4 compile/action
validation pass. Staged puts explicitly require activation; the existing RPC
client retains stage-only transactions and their live session. R09-06 is now
authorized after Author release from the6502 emulator; preserve fresh incoming
state before deployment. No staged speed, matched deployment or production
promotion is claimed yet.

Physical preparation update: [original fast baseline](REMOTE-009/BASELINE-R01.md)
passes exact1.1MB upload/download. Identified matched r27 candidate is built,
reviewed and uninstalled. P4 SD initialization times out across fresh boots;
Author physical card access is required before continuing R09-06. No new-path
hardware speedup or promotion is claimed.
