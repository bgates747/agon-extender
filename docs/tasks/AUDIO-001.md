# AUDIO-001 — Agon SD-to-parallel stereo streaming feasibility

## Executive summary

**AF01 complete: worth pursuing, but measured SD rates plus historical parallel
performance do not yet meet uncompressed 44.1 kHz/16-bit stereo.** Current SD
reads reached 189–199 KiB/s; the target is 172.27 KiB/s before transmission.
The next step is a sustained integrated parallel benchmark, then combined
read/send measurement—not a claim that stereo playback works.

See the [results and evidence](AUDIO-001/RESULTS.md). Six storage profiles passed
their bounded checks. No firmware flashed; startup preserved. AF02–AF05 remain
pending. Hardware voice notification closes this feasibility run.

## Scope and authority

Created at the Author's request on 2026-09-18. The Author authorized AF01 execution as a goal on September 18, with a one-hour
wall-clock budget, exclusive bench access, and small controlled tests including
custom P4 and EMOS firmware if needed. Start: 23:15:34 UTC; deadline: 00:15:34 UTC
September 19. Prefer retained evidence and minimal tests; reserve time to restore
and notify. Hardware voice at any stopping point; emulator voice fallback if
Agon is unrecoverable. This supersedes the earlier documentation-only boundary. Do not automatically begin
implementation after research. Golem is excluded. P4-PC delivery is not a
prerequisite; its stereo codec is a future physical sink.

EMOS continues to own transport and VDU routing. Split video/audio routing is a
proposal requiring a defined contract, not permission for application code to
bypass EMOS. Preserve ordinary Legacy behavior and working recovery paths.

## Itemized work plan

1. [x] AF01 — Feasibility study. Inspect Jukebox/AGM code and prior measurements;
   inventory existing forward-parallel code in Extender, EMOS and legacy work.
   Pin revisions and distinguish implemented, compiled, tested and abandoned
   paths. Reconcile the current local wiring record with older HW-001 holds;
   record the Author's report without treating it as a measured electrical pass.
   Establish actual SD-to-SRAM read rates, copying costs, memory headroom and
   parallel handshake limits from existing evidence. Identify unknowns requiring
   measurements. Assess a network PCM sink and browser playback requirements.
2. [ ] AF02 — Define a bounded integration/test contract from AF01 findings.
   Specify EMOS-controlled mainboard-video/Extender-audio routing, payload format,
   admission/backpressure, acknowledgements, shared-pin ownership, buffering,
   clocking, underrun/overflow behavior, stop and recovery. Determine whether a
   narrow raw-PCM experiment can use existing mechanisms or needs new commands.
   Record unresolved decisions before implementation; do not invent allocations.
3. [ ] AF03 — Following acceptance of the integration contract, implement only
   required EMOS/EDP/fixture changes with retained rollback identities. Reuse
   PORT-004 audio sink ownership and existing parallel transport work rather
   than duplicating production subsystems.
4. [ ] AF04 — Run staged tests: SD-to-SRAM alone; known SRAM payload over parallel
   with byte correctness; combined real chunk loop; network sink; continuous
   playback with mainboard video; then representative AGM video load if feasible.
   Measure stages separately and end-to-end; no inferred throughput from baud or
   strobe settings. Use deterministic payloads and integrity checks.
5. [ ] AF05 — Report sustainable rates, timing distributions, buffer occupancy,
   underruns/overflows, correctness and listening results. Identify the limiting
   stage and the next decision. Leave durable results; apply the current notification authorization.

## Feasibility inputs and budgets

Author states Jukebox already buffers one second ahead; AGM could buffer five
seconds including video. Inspect actual allocation/refill logic before proposing
changes. Buffering is not the missing idea: sustainable read-and-send rate is.

Stereo PCM payload = 44,100 samples/s × 2 channels × 2 bytes = 176,400 bytes/s.
One second is 176,400 bytes; five seconds of audio alone is 882,000 bytes, before
video, code and other allocations. Do not assume five seconds of this higher-rate
format fits the existing Agon SRAM layout. Encoded video adds to storage/memory
load; the study must identify which video bytes cross which transport in the
split-output design. Format signedness/interleaving/endianness remain to specify.

If read and send are sequential, their elapsed times plus other processing must
fit within the buffered media duration on average. Do not assume DMA overlap or
an eZ80 interrupt mechanism creates concurrent SD and transmit throughput.
Networking must deliver audio from P4 to a host/browser with a paced playback
clock; network receipt alone is not proof of uninterrupted audible playback.

## Dependencies and evidence

- [PORT-004](PORT-004.md): existing PCM scheduler/network sink task remains the
  owner of general audio implementation. This task owns the cross-project
  feasibility and end-to-end stereo experiment, not a replacement audio port.
- [HW-001](HW-001.md): historical parallel hardware design and holds; verify
  current state against HARDWARE.local.md before any bench activity.
- [P4PC-001](P4PC-001.md): future board bring-up and physical stereo output.
- Inspect agonjukebox/AGM and agon-extender-legacy as read-only evidence initially;
  identify exact paths/revisions in the study. Follow current ownership rules.

[Evidence bucket](AUDIO-001/README.md). Keep machine-specific addresses and device
identities in ignored local records. The authoritative project queue is TODO.md.

## AF01 execution sequence

1. [x] F01 — Inspect source/revisions and retained SD/parallel evidence; identify
   present routing and memory constraints.
2. [x] F02 — Run a bounded current SD benchmark if a safe reusable fixture is
   available. Do not build the complete audio integration to answer feasibility.
3. [x] F03 — Calculate serial-stage budgets and document architectural gaps,
   evidence limits, and a recommended next experiment.
4. [x] F04 — Restore any changed state, verify access, and hardware voice notify.

AF01 stopped after approximately 15 minutes, within the one-hour limit. Hardware
voice execution receipt verified; startup unchanged, service exited to MOS.
See [notification receipt](AUDIO-001/notification.json). No end-to-end stereo test
or firmware flash performed. AF02 awaits its integration contract.
