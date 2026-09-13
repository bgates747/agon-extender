# BENCH-001 native v2 integration closeout — 2026-09-13

This bounded continuation addresses the still-open B01-09 native integration
check. Physical driving/practice evidence remains accepted within its recorded
scope; the Author's 3,600.066-second learning programme is exhausted. These
are fixed qualification/debugging runs, not more driving practice. Do not tune
the controller or change gameplay to obtain a passing native run. Keep all
work silent/headless and local pending Author review; no hardware operation,
commit, push or new attention cue is needed for this step.

## Plan

1. [x] B01-H01: Read current failed native evidence, delivered binary/controller
   identities, resident transport contract and profile implementation. Identify
   any stale test configuration before altering code.
2. [x] B01-H02: Make the headless harness record and use an explicit freshness
   bound, defaulting to the current physical controller's 300 ms bound. Preserve
   the earlier200ms failure and350ms diagnostic as separate historical runs.
   Prepare a fresh frozen40-second profile with the exact delivered two-tick
   Rally binary, EMOS16, current portable P4 peer and current host controller.
3. [x] B01-H03: Run that profile through its generated entry point. Require
   fresh coherent manual-race telemetry, released controls, no grass/contact
   observations and at least one completed lap. Record cadence, latency,
   steering step, sample/lap counts and actual input/runtime identities.
4. [x] B01-H04: If it fails, localize the failure using retained wire/frame
   observations and source; implement only an evidenced harness/transport
   correction in its owner. Do not increase freshness limits, lower demands,
   fabricate interrupts or tune away a controller failure. A separately
   specified, datasheet-supported native-model correction requires its own
   reusable-tool task and independent register/interrupt checks before use.
   A documented native-model limit stays a limit if no faithful fix applies.
5. [x] B01-H05: Audit B01-09 against this new native evidence and the existing
   physical deployment/driving/recovery records. Update the owning task and
   delivery/limits documents accurately. Broader RALLY-22/Extender work and
   human validation/publication gates remain separate and open.

## Focused findings before implementation

1. Old native v2 profile01 stops on a200ms observation gap; profile02 uses
   an explicit350ms diagnostic and fails with36grass samples in30seconds.
   Those profiles use a prior controller and step3 (verified in raw payload
   byte78), not the final hardware-tested step2 combination.
2. Current `scripts/rally_drive.py::run` defaults to300ms observation age and
   progress bound, with200ms active HTTP requests. `Sample.decode` has a200ms
   standalone default, but run supplies its explicit bound. The headless
   harness still hardcodes350ms and describes physical use as200ms. That is
   stale harness configuration/metadata, not evidence of current performance.
3. Current Rally135899-byte binary SHA256
   `20fde9ace4aa56298c5648985a6f3fa0eccdd6c50d527c62045c393c421e37c1`
   matches the recorded steering candidate. Controller SHA256 is
   `314c9ff02df9a197013993f18cb242cacf351d8bde5af32a5f96c1e40e1d0f82`.
   EMOS16 bench image130071bytes remains
   `1da8330462eed54317e5889cf3f09cb1abaca8b478f7d92b88a3a1d74c9fc70c`.
4. `scripts/qualify_rally_headless.py` runs real eZ80 Rally/EMOS, with a portable
   P4 receiver/keyboard peer compiled from maintained headers. Its local Unix
   byte socket has no physical baud clock or ESP-IDF scheduling. The existing
   runtime lacks TX-empty interrupt demand: UART packets drain under VBlank/RX
   work. This known boundary must remain explicit; a native pass cannot prove
   physical UART interrupt timing. At this initial stage no emulator mutation
   was proposed; the measured failure below justified the explicit amendment.
5. Official read-only MOS docs `docs/mos/API.md` define UART1 vector0x1A and
   separate RX/TX interrupt-enable bits. EMOS retains UART ownership and
   copied snapshots; this work does not add application interrupt handlers.
   Reference MOSv3.0.2/VDPv2.16.0 and agon-docs
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b` remain unchanged.
6. The EMOS-owned `scripts/review_boot.py::make_profile` generates the required
   hash-checked profile entry point and pins firmware/map, native runtime,
   peer/helper code, assets and raw FAT seed. Only working.img is mutable.
   Use a fresh profile rather than overwriting frozen historical evidence.
   Private paths/runtime provenance live under ignored agents/bench-001 and
   the existing profile manifests; no physical bench access is required.

## Current-candidate failure and measured model gap

The fixed40-second current-candidate run completes276 observations with45grass
samples, two contacts and two unclean laps. Its300ms checks do not fail:
reported receipt age has median23ms/max40ms, while observed source-frame gaps
have median3. The prior failure was therefore not merely stale test settings.
Preserve the new failure alongside the earlier profiles.

A separate10-second stationary trace makes no keyboard/controller request and
is explicitly labelled observation-only. Its61 complete CRC-valid packets take
median134.260ms from first to last host-received byte (128.786–136.941ms).
Packet arrivals are a median165.932ms apart and source frames advance by3.
This measures host-socket assembly, not absolute end-to-end latency, but proves
that a recent receipt timestamp can describe a snapshot already delayed by
over128ms during transmission alone.

Read-only eZ80F92/F93 specification PS015317-0120, pp105–107 and113–115,
defines transmit-empty demand from IER bit1 plus empty holding/FIFO state;
writing THR clears the source, and IIR is a read-only priority/status register.
The isolated native model never raises UART1 TX demand and its old IIR stub
incorrectly clears IER bit1 when read. EMOS uses bounded16-byte TX work under
its real UART/VBlank owners; without TX interrupts the model waits for later
VBlank/RX opportunities. This is an evidenced emulator limitation.

The follow-up is therefore assigned to reusable `mos-agondev` task TEST-002:
an opt-in UART1 TX interrupt/IIR correction in the maintained runtime generator,
independent register/byte-clock tests, preserved default runtime, then the exact
same Rally/controller case again. This explicitly amends the initial no-model-
change scope based on measured evidence. Do not patch a generated runtime,
alter the guest firmware/controller, synthesize key responses or relax the
300ms gate. Old failures stay visible; corrected native evidence still cannot
prove physical baud or ESP-IDF behavior. Human emulator/commit review remains.

## Results and closeout

The explicit TEST-002 runtime implements UART1 RX/TX demand and read-only IIR
priority/status. Its generator leaves the default adapted source byte-identical
to the reviewed baseline. All 138 generic unit tests pass, including five
compiled actual-Rust UART cases, source-drift/default-output checks and the
existing socket backpressure test. No UART0, guest, controller, byte clock,
FIFO capacity, VDP or physical firmware change was made.

The stationary 10-second trace now has 175 CRC-valid packets, median 2.180 ms
host assembly (1.578–3.336 ms), median 55.145 ms arrivals and source-frame step 1.
The earlier 134.260 ms assembly/step-3 result remains a failed-model diagnostic.
These are host-observed transport intervals, not physical baud or production FPS.

Two fixed 40-second drives then pass with the same delivered Rally/EMOS and
controller, 200% grip, step 2, corner reserve 0.58 and the unchanged 300 ms
freshness bound. The first records 659 road observations, four clean laps and
13 passes. The final case adds actual guest release and application-exit checks:

| Final native case | Result |
| --- | --- |
| Controlled interval | 40.066 s |
| Complete packets / controlled observations | 664 / 660 |
| Manual-mode road observations | 660 |
| Kerb / grass / contact entries | 0 / 0 / 0 |
| Clean laps / passes | 4 / 12 |
| Distance / maximum absolute lateral position | 24,197.4 / 41.996 world units |
| Last controlled frame / released-key guest frame | 661 / 663 |
| Exit | Ordinary Escape; telemetry stopped; both keyboard journals inactive with no pending request |

The guest's later frame reports held keys zero. After exit, the peer reports
ready, physically neutral, held zero and pending zero. Raw rows all decode as
fresh coherent manual racing without demo/autosteer. There is no unlimited-CPU
option. The source/controller and delivered image hashes above are unchanged.

The final generated profile passes its post-run hash/inventory check. That
check first rejected three Python-generated import caches, which were removed
without altering any frozen input. Future runs should set
`PYTHONDONTWRITEBYTECODE=1` when invoking the generated profile wrapper. The
cache-removal record is retained; inventory checking was not weakened.

The retained-evidence audit also verifies all 18 physical programme raw-stream
and controller hashes, result/lap counts and recorded exit evidence; the
learning allowance remains exhausted at 3,600.066 seconds. It rechecks the
post-practice ROM, startup and both Rally binary readbacks, the recorded marker
staged/active readback, and service journal with no pending transaction. This
does not relabel historical native failures or perform another hardware test.
Later PORT-008 records and HARDWARE.local.md own the current physical state.

B01-09 and H01–H05 are machine-complete within these limits. Final human
validation, commit/publication approval, full RALLY-22 review and the wider
Extender port queue remain open. No bench access, practice, alert or Git action
was performed for this continuation.

## Reproduction and evidence

1. Generic owner: `mos-agondev/scripts/prepare_uart_peer.py`, explicit
   `--uart1-tx-interrupts`; usage and bounds are in that project's
   `docs/uart-peer-emulator.md` and TEST-002. Reference Fab commit
   `fbb7d7ca887a06966ca8a62ed22272409a5ab640` remains read-only.
2. Runtime executable SHA256
   `875e73f4f452c7005e41a9e230b0d961289d58841dffd8d8a6c3a1ee64725911`;
   runtime manifest SHA256
   `446caa45878bf2eca812f73dd7f08669ca0cb78bbdd80750d61b5ecb384b874a`.
   Hashes identify this host build, not a portable binary expectation.
3. Final local profile:
   `.emulator/bench001-v2-txirq-drive-02/profile`. Change into that directory;
   `./fab-agon-emulator --check` verifies without launching. Preserve this
   evidence and prepare a fresh profile for another run. The EMOS-owned
   `scripts/review_boot.py::make_profile` generates the mandatory wrapper.
4. Ignored `agents/bench-001/headless-closeout/` retains exact preparation,
   source/input hashes, failed and passing runtime comparisons, generic test
   log, assembly timings, bytecode-inventory note and read-only `audit.py` /
   `audit.json`. Raw native UART/JSONL streams, journals and frozen inputs remain
   under their individual profiles. `PRACTICE.md` owns physical results.
