# PORT-003 Phase A compatibility delta

Phase A is a compile/link contract canary. It establishes no rendered-pixel,
timing, frame, output, or hardware compatibility claim.

## Retained unchanged

- Official Agon VDP `v2.16.0` source bytes and upstream directory names.
- vdp-gl `all-the-plots` declarations and implementations for `Canvas`,
  `BitmappedDisplayController`, and `GenericBitmappedDisplayController`.
- Upstream integer, `RGB888`, `NativePixelFormat`, ownership, factory-base, and
  abstract-controller type contracts exercised by static assertions.
- The upstream common primitive executor in the resulting ELF. A guarded
  link-evidence probe retains it but never invokes a drawing operation.

## Replaced or adapted for the canary

- The concrete classic VGA controller is replaced by
  `P4DisplayControllerContractCanary`. It implements the abstract surface but
  deliberately aborts on every drawing, readback, bitmap, scroll, glyph, and
  buffer-swap entry point.
- The small `fabutils.cpp` closure required by the common controller is carried
  in project-owned `fabutils_port.cpp` with exact vdp-gl tag, commit, and source
  spans. The broad upstream translation unit remains vendored but excluded.
- Xtensa coprocessor save/restore names are compile-only no-ops on RISC-V.
  Runtime transformed-bitmap policy remains a later qualification concern.
- The absent classic ESP32 FRC timer header is a parse-only fail-fast shim. No
  P4 timer emulation is claimed or selected.

## Explicitly absent

- Classic VGA, VGA text, CVBS, Scene, physical PS/2, sound output, network,
  file-browser/storage, and official `video.ino` translation units.
- Framebuffer allocation, drawing, palette, Copper, sprites, readback results,
  frame cadence, queues, swaps, completion, and output consumers.
- EDU/VDU routing, MOS integration, operating-mode policy, deployment, and
  target qualification.

The canonical dependency graph records the three project-owned Phase A build
units separately from immutable upstream file selections. This prevents the
diagnostic boundary from being misread as a production source profile.
