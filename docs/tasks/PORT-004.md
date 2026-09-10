# PORT-004 — Implement the P4 PCM scheduler and network audio sink

## State

- Status: Deferred by the Author on 2026-09-10 until the Author chooses to begin audio implementation
- Started: --
- Finished: --

## Intent

Implement the accepted Work 1.e audio boundary: retain the official VDP audio
runtime and vdp-gl synthesis/mixer semantics while replacing the fused
classic-ESP32 physical output backend with an Extender-owned PCM scheduler and
sink service. The guaranteed Rev 1 sink delivers EDP-generated audio over the
network for browser consumption.

## Authority and inputs

- [`tomm/userspace-vdp-gl`](https://github.com/tomm/userspace-vdp-gl), a
  userspace-oriented VDP-GL/FabGL fork. Before designing or implementing the
  P4 audio seam, inspect its `src/devdrivers/soundgen.h` and
  `src/devdrivers/soundgen.cpp` alongside the corresponding files in the
  selected tagged official VDP-GL source. Treat it as prior art, not upstream
  authority: identify reusable separation of waveform generation, channel
  mixing, sample pulling, and host/SDL output from classic-ESP32 DAC,
  sigma-delta, DMA, timer, and ISR machinery. The repository was first
  inspected at commit `2c12e77a0d00f8989c884525479ee6d37340751a`; refresh and
  pin the selected revision when PORT-004 starts.
- [SETUP-004 Work 1.e](SETUP-004.md#work-1e-execution-record) and its generated
  audio inventory.
- [ADR-0013](../decisions/ADR-0013-vdp-survey-integration-boundaries.md),
  especially decisions 22–25.
- [Current architecture](../architecture.md).
- [PORT-001 dependency graph](PORT-001.md) and
  [PORT-002 source-selection work](PORT-002.md).

## Required outcomes

1. Preserve the official audio parser, `PACKET_AUDIO` acknowledgements,
   channel state, envelopes, samples, playback timing, audio-control task, VDU
   7 behavior, and command success/failure semantics through narrow integration
   changes.
2. Preserve vdp-gl waveform generation, channel attachment and lifetime,
   sample-rate propagation, channel and global volume behavior, and signed
   eight-bit PCM mixing.
3. Expose the retained mixer through a bounded PCM pull/sink seam without
   retaining classic-ESP32 DAC, sigma-delta, I2S0-register, legacy-DMA,
   fixed-pin, ISR/timer, VGA/CVBS-selection, or target SDL output paths in the
   P4 build.
4. Advance logical playback from a stable selected sample clock independently
   of sink latency, backpressure, connection state, or availability. A slow or
   disconnected client must not block VDU processing, delay logical note
   completion, or alter channel status.
5. Define bounded buffering and explicit drop/resynchronization behavior for
   sinks that cannot keep pace. Keep transport failure separate from logical
   synthesis and command state.
6. Implement and qualify the initial network/browser audio sink, including PCM
   framing or encoding, buffering, browser compatibility, latency, jitter,
   clock drift, reconnect behavior, and concurrent video traffic.
7. Qualify command/status fidelity and logical timing separately from delivered
   audio fidelity and end-to-end browser latency. Record the Rev 1 exception
   that stock analog-output location and exact analog characteristics are not
   guaranteed.

## Dependencies and gates

- Complete and record the mandatory `userspace-vdp-gl` comparison above before
  freezing PORT-004's detailed implementation design. Do not independently
  recreate a waveform/mixer extraction already demonstrated there unless the
  official VDP compatibility contract requires a documented divergence.
- Complete SETUP-004 before implementation so network and remaining source
  boundaries are settled.
- Work 1.g determines the retained network/transfer substrate and must be
  reflected in the detailed implementation design.
- PORT-002 must represent the old physical output paths as vendored but
  excluded while retaining the selected mixer closure.
- `SETUP-005-D005` independently governs optional forwarding to the onboard VDP
  for local playback; PORT-004 must not assume that route.
- QUAL-001 must identify the audio command, acknowledgement, logical-timing,
  sink-delivery, and accepted analog-output-exception obligations before the
  detailed implementation contract is frozen.
- PORT-008 is required before an Agon-fed physical run can qualify official
  audio commands or response packets. PORT-004's host-side synthesis work need
  not wait for that transport.
- Define detailed scheduler, buffering, transport, browser, and qualification
  phases with the Author before coding.

## Accepted REMED-002 finding

[REMED-002](REMED-002.md) assigns PORT-004 the retained-audio portion of
`INTEGRITY-AUDIT-F004`; the detailed evidence and provenance remain in
[`AUDIT-2026-09-01-001`](../decisions/AUDIT-2026-09-01-001-open-task-and-implementation-integrity.md).

1. [ ] Define the complete official audio-command grammar and the behavior of
   every supported, deferred, and rejected subcommand before making the P4
   parser physically reachable.
2. [ ] Ensure a deferred audio implementation still consumes or safely rejects
   every command-dependent argument before top-level VDU parsing resumes.
3. [ ] Add deterministic framing tests with a valid command immediately after
   each variable-length, unsupported, malformed, and truncated audio command.

PORT-003 owns the safe retained-parser binding. PORT-008 and SETUP-005 own the
transport-reachability and mode-policy portions. This finding does not select
an audio sink or authorize implementation.

## Deferred Wolf3D/audio framing follow-up — 2026-09-10

The Author explicitly defers repair of the audio-command parser until taking
on audio implementation. This is a scheduling decision, not acceptance of the
current parser behavior as compatible. Do not start a separate interim repair
or Wolf3D investigation without renewed direction.

The quick source audit found that
`vdp/video/extender/audio/unavailable_audio_adapter.hpp:19` defines an empty
`VDUStreamProcessor::vdu_sys_audio()`. The retained dispatch in
`vdp/video/vdu_sys.h` calls it for `VDU 23,0,&85`; the P4 handler consumes no
channel, subcommand or payload and sends no audio status. Remaining bytes can
therefore become top-level VDU controls or text. The deployed paired-graphics
manifest records the same adapter SHA-256 as the inspected source:
`d610a6cc457bd917054da4f281cd63fa910c3f2a4ed57baec669b137afeb3e3e`.

Wolf3D source inspected at commit `1a5af2c` sends channel-enable commands at
startup and sample-selection/play commands during gameplay (`src/asm/wolf3d.asm`
and `src/asm/vdu_sound.asm`). Its ordinary graphics operations have retained
EDP handlers. The exact tested game binary has not been pinned. The framing
defect is confirmed by code inspection; its responsibility for all observed
Wolf3D symptoms has not been established by a repair/retest.

1. [ ] When audio implementation resumes, resolve the existing framing and
   acknowledgement obligations above, including a regression test for Wolf3D's
   command sequences followed by ordinary text/graphics commands.
2. [ ] Retest the same identified Wolf3D binary on mainboard VDP and EDP;
   check text placement, gameplay and clean return to EMOS. Close
   [QUAL-003-I003](QUAL-003.md) only when evidence supports doing so.

Official contract: Agon documentation `docs/vdp/Enhanced-Audio-API.md`,
command framing and status replies; retained stock-shaped implementation in
`vdp/video/vdu_audio.h`. No audio sink choice, code change or hardware operation
accompanies this deferral.
