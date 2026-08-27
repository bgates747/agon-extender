# Legacy browser presentation assessment

## Frozen source

- Repository: `agon-extender-legacy`
- Commit: `f33b9dd` (`Add hardware-qualified VDP web presentation`)
- Browser files: `web/presentation/`
- Firmware evidence: `src/modules/vdp/vdp_web.c` and `vdp/common/`

Commit and repository-relative paths are the durable provenance.

## Reuse

1. Dark centered layout, pixelated 4:3 canvas, controls/status arrangement,
   and statistics grid as the accepted visual reference.
2. WebGL2 nearest-neighbor RGB888 texture presentation, subject to current
   browser tests and explicit failure reporting.
3. Strict explicit little-endian `EVF1` header encoding/parsing rather than C
   struct serialization.
4. Complete-frame, presentation-ready RGB888 semantics, sequence metadata,
   and browser-side sequence-gap accounting.
5. Local browser-generated test pattern as a diagnostic separation between
   browser presentation and P4/network delivery.

## Replace or extend

1. Replace `Physical-scanout mirror` and the legacy assumption that browser
   output is secondary to MIPI/HDMI. Browser video is now the sole foreseeable
   output path.
2. Remove the server's hard-coded 320-by-240 validation. Current retained modes
   reach 1024 by 768.
3. Replace the one-request/one-frame browser behavior with bounded repeated
   client credit and latest-snapshot delivery.
4. Replace the unsynchronized global borrowed surface with the Phase F
   immutable fixed-capacity snapshot/lease contract.
5. Separate generic Ethernet/HTTP ownership into PORT-006 and pixel/frame
   semantics into PORT-003.
6. Replace the hard-coded logged IP address with observed DHCP link and lease
   diagnostics.
7. Tighten validation of reserved fields, known flags, arithmetic overflow,
   disconnect cleanup, and connection count.

## Do not import

1. The legacy physical MIPI/HDMI authority model.
2. Any experimental fixed-frame Agon/EDP transport protocol.
3. Fixed physical-scanout timing claims, fixed dimensions, or one-frame-only
   behavior.
4. A mutable surface pointer whose lifetime is not protected through send
   completion.

The legacy result is valuable implementation evidence, not current system
authority. Phase F validates every selected byte and behavior against the
current retained VDP and accepted architecture.
