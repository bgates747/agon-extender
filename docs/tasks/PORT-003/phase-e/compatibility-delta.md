# PORT-003 Phase E compatibility delta

## Retained observable behavior

The official Agon VDP `v2.16.0` mode table, mode IDs, modelines, dimensions,
color depths, scaling, rectangular-pixel flags, buffering choices, Teletext
path, Canvas ownership, fallback order, context reset, callbacks, cursor
restoration, and eight-byte mode-information packet remain authoritative.
The exact official `VDUStreamProcessor::vdu_mode()` and
`sendModeInformation()` bodies pass independent lifecycle fixtures without a
production rewrite.

## Required P4 adaptation

`vdp/video/agon_screen.h` is the sole patched official file. The patch replaces
the classic VGA concrete-controller factory and downcasts, physical frame clock,
and physical mouse-positioner binding with the project-owned P4 controller,
transactional mode facade, logical frame service, and display-only cursor
adapter. It narrows the aggregate FabGL include to retained Canvas declarations.
ADR-0015 authorizes this binding patch; the managed-import verifier records and
checks it as `vendored-patched` against official tag `v2.16.0`.

The P4 facade interprets modelines only for logical width, height, and cadence.
It does not reproduce classic VGA GPIO, I2S, DMA, signal tables, or VSYNC ISR
mechanics. One stable P4 controller is transactionally reconfigured, and the
P4 frame service—not an output sink—advances official logical frame time.

## Explicitly unchanged or excluded

No application-visible VDU command, mode number, response packet, context
contract, callback contract, or Teletext behavior is deliberately extended or
improved. Classic VGA/CVBS/Scene/PS2 physical drivers, audio, network, storage,
updater, transport, and output sinks are absent from the Phase E target closure.

Phase E does not qualify physical timing, pixels on a device, EMOS parity,
EDU/VDU routing, sysvar updates, assembled-system behavior, or hardware. PORT-008
owns the first physical command/response vertical slice; Phase F owns the
durable output-consumer contract and physical sink handoff.
