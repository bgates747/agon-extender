# PORT-003 Phase F contracts

The Author accepted these contracts with the complete Phase F plan on
2026-08-27. They govern implementation until an explicit reviewed amendment.

## Actors and ownership

1. The retained VDP parser and P4 display controller own official command
   interpretation, logical framebuffer state, frame progression, and final
   presentation composition.
2. The PORT-003 snapshot publisher owns immutable RGB888 snapshot storage,
   generation metadata, fixed-capacity publication, leases, and display-side
   drop accounting.
3. The PORT-006 network service owns the P4 Ethernet device, DHCP lease, HTTP
   server, WebSocket connection and credit state, opaque send execution, and
   network-side failure reporting.
4. Browser JavaScript validates `EVF1`, presents final pixels, and grants at
   most one next-frame credit after accepting the preceding frame.
5. No Pi, external web server, browser, or network worker owns VDP time or
   mutable logical storage.

## Immutable snapshot pool

1. Provision three fixed-capacity PSRAM slots, each able to hold packed RGB888
   for the largest retained 1024-by-768 mode. Assert pixel size and overflow
   bounds at build and runtime boundaries.
2. A slot is exactly one of free, producer-owned, latest-published, or leased.
   State transitions are bounded and tuple-unique; no unbounded allocation or
   queue exists.
3. The frame owner may acquire a free slot without waiting, compose one complete
   presentation at a quiescent frame boundary, then atomically publish it as
   latest. A previous unleased latest slot returns to free.
4. If no free slot exists, the producer records a presentation drop and does
   no composition. Logical VDP progress continues.
5. The network owner may lease only a complete published slot. The slot remains
   immutable until synchronous/asynchronous send completion or disconnect
   cleanup releases it. Consumers never receive a logical-plane pointer.
6. Snapshot production uses a conservative first-bench cadence independent of
   the 60/70/75 Hz logical clock. The exact cap is configuration metadata and a
   measured beta parameter, not an application-visible VDP behavior.

## EVF1 and browser credit

1. One binary WebSocket message contains the 32-byte `EVF1` little-endian
   header followed by one complete packed RGB888 surface.
2. Version 1 requires known magic/version/header length/pixel format/flags,
   nonzero dimensions, `stride >= width * 3`, exact payload arithmetic, zero
   reserved field, and no trailing or truncated bytes.
3. Width and height cover every retained mode through 1024 by 768. Neither the
   server nor browser assumes 320 by 240.
4. The first tranche accepts one video WebSocket client and one outstanding
   frame credit. A second video client receives a clear bounded refusal; this
   is not a permanent product-client-count decision.
5. The browser grants the next credit only after validating and handing the
   previous complete frame to its presentation loop. A pending credit selects
   the newest later snapshot; intermediate generations may be dropped and
   counted.
6. Malformed browser requests or frame data terminate or reject only that
   connection. They do not alter VDP state.

## Browser interface

1. Preserve the accepted legacy dark shell, pixelated 4:3 canvas, compact
   controls, status line, and statistics grid.
2. Preserve a local browser-generated RGB888 test pattern so browser parser and
   presenter behavior can be distinguished from P4/network behavior.
3. Replace `Physical-scanout mirror` and other stale physical-output claims
   with current EDP browser-video language.
4. Show connection state, sequence, dimensions, stride, logical period,
   received frames, and observed sequence gaps. Diagnostics are not VDP wire
   traffic.

## Boot and failure behavior

1. The P4 may boot, initialize the retained display, acquire DHCP, and serve a
   black/startup presentation with no Agon attached and no browser connected.
2. Ethernet, DHCP, HTTP, asset, snapshot-pool, or browser failure is reported
   over USB serial and leaves retained logical VDP execution available.
3. The first P4-only Phase F run does not claim VDU ingress. PORT-008 binds the
   disconnected Arduino `Stream` ingress to the current parallel wiring.
4. Agon/EMOS boots in Legacy. Only explicit operator action through EMOS may
   activate the qualification-only forward route after P4/browser readiness.

## Explicit deferrals

Compression, dirty rectangles, codecs, audio, multiple video clients, TLS,
authentication, internet exposure, friendly discovery, persisted network
configuration, Wi-Fi, OTA, management, parallel ingress, return UART, runtime
mode-transition qualification, and production throughput are outside Phase F.
