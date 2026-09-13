# PORT-017 implementation record

## Contract and resource gate — 2026-09-13 UTC

Initial contract frozen in 51917e6 before service implementation. EMOS component
task INTEG-013 was registered separately in agon-emos 5824cfb. Work stays on both
repositories' current main branches. No physical board reset, serial open,
firmware flash, or removable-media write has occurred during implementation.

1. EMOS baseline reproduced at 130344 bytes. A private `ext.sdlink` gateway now
   compiles with the required ROM, UART divisor, keyboard, console, parallel,
   ABI and VDU link guards. Latest exploratory image: 130954 bytes, 118 spare;
   Core static RAM ends at BDAAA, below BF800 stack boundary. This includes a
   deliberately long UNVERSIONED identity. No new deployment version is assigned.
2. Existing bytewise 24-bit field assembly emitted expensive code. An explicit
   compiler builtin memcpy of three bytes generates native ADL loads on eZ80;
   the host path retains bytewise decoding. No supported feature was removed.
   A normal memcpy was insufficient under the freestanding compiler flags.
3. The maintained P4 console composition compiles with the queue and network
   endpoint: 53100 bytes reported static RAM and 1438192 flash. Minor subsequent
   timeout refinements require another build. HTTP never writes UART; the
   existing console owner sends whole packets after pending keyboard traffic.
4. Five portable wire/queue tests pass, including all payload sizes, arbitrary
   byte starts, every single-bit corruption of a full record, duplicates,
   conflicting identities, expiry and timer wrap. EMOS has 85 passing host
   tests after foreground filesystem tests were added. Those filesystem tests
   execute real service code with a POSIX fault adapter, not real FAT media.
5. The foreground application builds at 18933 bytes. It uses public MOS/FatFS
   APIs and the owned gateway. No video-mode change or ISR filesystem work.
   Default scope is `/extender/sdtest`; an explicit absolute root is supported.
   Preserve its canonical filename `sdserve.bin`, which the service rejects as
   a writable target. Stages/journals/backups are also reserved write targets.

P17-01 is complete. P17-02 through P17-05 remain open. Compiles and host tests
are not evidence of physical UART, filesystem integrity or keyboard operation.
All maintained firmware and emulator-coupled changes remain provisional and
uncommitted until the applicable Author validation/commit gate. No qualification
or release status is claimed for these exploratory builds.

## Findings to retain

1. `mos_fclose` reports remaining handles, not a FatFS result. The application
   uses checked `ffs_fclose`, `ffs_fsync`, byte counts and `ffs_ferror` instead.
2. Ordinary Fab directory-backed SD has the independently reproduced create-new
   and sync defects in REMED-003. Storage qualification uses a raw FAT image;
   host filesystem mocks alone cannot establish those contracts.
3. The existing UART-peer runtime models ordered bytes and host CTS backpressure,
   not physical baud, FIFO overflow, RTS timing or P4 scheduling. Its help text
   spells the unlimited CPU flag incorrectly; `-u` is accepted, whereas the
   displayed `--unlimited-cpu` is ignored. Preserve actual timing configuration
   in evidence and do not infer physical throughput from that runtime.
4. Partial SD envelopes trigger owned transport fault handling; late bytes must
   not become keyboard/console input. Oversized complete packets are drained by
   declared length. Shared keyboard-send failure now requests the existing fault
   path rather than silently continuing after a partially transmitted packet.
5. The journal is deliberately immutable during staging. Some ambiguous damaged
   or orphaned metadata states require explicit inspection; automatic recovery
   never deletes the only known target or guesses that a rename succeeded.

Machine-specific build logs, provisional bundles and raw captures are in the
ignored project build/profile trees. Final acceptance will preserve selected
evidence and exact committed candidate provenance in the tracked task silo.
