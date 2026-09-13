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

## Provisional headless result and commissioning handover

The compiled EMOS and eZ80 service now pass actual FatFS/raw-image transfers at
0, 1, 212, 213, 65537 and 131731 bytes through the maintained P4 queue and host
HTTP client. Each stage and activated file was read back and compared. One WRITE
response was deliberately dropped; the application replayed it successfully.
The full run took 347.14 seconds; its 131731-byte cycle took 229.98 seconds,
including upload, Agon verification, host stage readback, activation verification
and host target readback. These are emulator pipeline times, not physical UART
throughput. The ignored long CPU flag was ineffective; this run was CPU-limited.

After the first-upload orphan recovery clarification, a fresh short raw-FAT run
passes recovery of a pre-existing valid journal/partial file without any target
or backup. A further focused run checks real target STAT and LIST alongside
write/read/activation and lost-response recovery. No changes to the official
reference runtime or official MOS/VDP checkouts were needed.

Latest EMOS host suite: 87 tests pass. Nine Extender wire/queue/client tests
pass, plus the retained console-session tests and target network-adapter fault
checks for both six-route and eight-route configurations. The final P4 compile
passes after the partial-envelope fault fix. The current eZ80 application is
18939 bytes. Provisional firmware/application hashes and source snapshots are
preserved in ignored `agents/port-017/review-ready`; raw headless evidence is
under `.emulator/port017`. These dirty exploratory inputs are not deployable
candidate identities or qualified evidence.

`BOOTSTRAP.md` defines the proposed single initial card handover, payload paths,
normal startup, host commands, rollback boundary and remaining approval gates.
The service cannot install its own initial EMOS gateway over an old gateway
that does not exist. No hardware has changed. Firmware, tests, tooling and
emulator-coupled documentation remain uncommitted pending the Author's
commissioning/commit disposition. Physical qualification and ten uninterrupted
cycles remain open; no dependent Rally/Golem work has started.

## Candidate freeze and returned card — 2026-09-13 UTC

The Author returned the card and directed preparation after the concrete
identity/commit proposal. The candidate freeze proceeds for EMOS v0.1.14,
console r12, sdserve v0.1.0 and mainboard-sd-qualification r01; physical and
human acceptance remain pending. The service gets an identified build wrapper.
The card was backed up before changes. Guarded IFTHERE/EXEC installation consumes
its trigger before FLASH, so the following boot starts the service without a
second card trip. Historical EMDONE and accepted Rally files stay intact.

Fresh EMOS host suite: 89 tests pass. Extender wire/queue/client checks pass.
Writable paths now reserve the eight-byte sibling suffix; invalid current-session
transfers use BAD_REQUEST, preserving STALE for unaccepted sessions. These
clarifications were frozen in 3c350df before implementation. Exact identified
builds and headless smoke follow the freeze.

The complete registry validator currently stops at a pre-existing hash mismatch
in hardware/designs/light2-harness-r02/profile.yaml for connectivity.yaml
(expected 560ab589..., actual c68e4d4f...). Neither input is changed by PORT-017.
The artifact-registry validation itself passes independently. Do not silently
rewrite that hardware integrity record to make this service gate green.

## Commissioning media ready — 2026-09-13 UTC

Candidate inputs: Extender 69da46a; EMOS 71f362a. Both candidate builds
record clean source. Complete EMOS wrapper qualification/link/runtime checks
pass; all 89 EMOS host tests and 10 Extender wire/queue/client tests pass.

1. `agon-emos-v0.1.14-b2026-09-13-01-07-47Z`: 130919 bytes; SHA-256 `eea1a479516df733688803f775d65c41a7c48a546927c7f07c0a489f8cd09808`.
2. `sdserve-v0.1.0-b2026-09-13-01-07-48Z`: 18974 bytes; SHA-256 `8903bb934f26af914f31d92a92508bc5095d09f4c2fa027c7b05155a9544a317`.
3. `uart-excom-console-r12-b2026-09-13-01-07-48Z`: 1570272 bytes; SHA-256 `ff1e0da79a844eed4a2a4c7bce3d346750610409f8a4d161129c3b599b26c7e0`.

The exact EMOS/application images pass a fresh headless raw-FAT smoke: empty
and 213-byte uploads, full stage/target readback, orphan recovery, STAT/LIST,
EXIT and one deliberately lost WRITE reply. Larger-file evidence remains the
earlier provisional run, not a claim that this exact candidate ran those sizes.

P4 was physically flashed and independently verified. Boot capture contains
the exact r12 build, USB HOST READY, USB KEYBOARD READY, Ethernet link and HTTP
startup without the checked fault markers. The HTTP SD status endpoint reports
protocol 1, offline as expected before the Agon service starts. This does not
yet validate the mainboard data path or keyboard coexistence during transfers.

The AGON card was backed up, staged and hash-verified, then safely unmounted.
Its guarded one-shot installer uses ESDNEW.BIN -> ESDDONE.BIN; historical
EMDONE.BIN is untouched and EMV0113.BIN preserves rollback. Autoexec then enables
Extender keyboard and starts /extender/sdserve.bin rooted at /extender/sdtest.
Accepted Rally binary/oval/Fuji data hashes remain unchanged. Onboard VDP was
not opened, reset or flashed by this goal and remains the previously restored
stock 2.16.0 by historical evidence; physical current boot verification awaits
the Author's return of the card. No reset-breakout action.

P17-03 implementation is complete with host and raw-FAT evidence. P17-02
commissioning/recovery and P17-04/P17-05 physical qualification/delivery remain
open. The labelled stock emulator is an attention cue only; the Author returns
the card, resets Agon and allows installation to finish. If FLASH asks for a
reset instead of restarting automatically, one further reset is sufficient;
the consumed trigger prevents reflash. Machine-local manifests, source hashes,
backups and captures are retained under agents/port-017 and .emulator/port017.

The Author subsequently reported a good flash and visually confirmed the
backend observations. Physical HELLO/STAT/LIST now pass. A 1024-byte arbitrary
binary upload, Agon verification, full host stage readback, activation and full
target readback pass in 3.262 seconds. No keyboard-during-transfer acceptance
is inferred from this installation observation. The Author has returned to
the couch; summon only when a concrete physical observation is needed.

Freeze the physical ten-cycle controller and its headless controller smoke
before running it. Independent errors stop with durable state retained; the
runner never automatically resets or reflashes.

## Ten physical cycles pass

All ten physical transfer/readback cycles passed without further card movement
or reset, through 131731 bytes, including previous-version verification and
one durable host-response-loss retry. Selected evidence is under
`evidence/PORT-017-2026-09-13-01-21-04Z/`. The final 131731-byte cycle took 360.381 seconds;
this includes multiple complete readbacks and verification, not just upload.
The exact-candidate raw-FAT disk-full test also passes (26624-byte partial file,
FR_DENIED, old target preserved, explicit recovery). Keyboard observer smoke
passes actual mapped Escape and typed `RUN . /` on the headless eZ80.

The next assistance cue is only for the physical native-keyboard test during
traffic and direct CLI restart with whole-card scope. No new firmware or card
movement is required. Ten-cycle success is not yet full task acceptance.
