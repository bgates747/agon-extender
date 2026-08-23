# PORT-004 — Implement the P4 PCM scheduler and network audio sink

## State

- Status: Not started — registered from SETUP-004 Work 1.e
- Started: --
- Finished: --

## Intent

Implement the accepted Work 1.e audio boundary: retain the official VDP audio
runtime and vdp-gl synthesis/mixer semantics while replacing the fused
classic-ESP32 physical output backend with an Extender-owned PCM scheduler and
sink service. The guaranteed Rev 1 sink delivers EDP-generated audio over the
network for browser consumption.

## Authority and inputs

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
