# REMOTE-005 — Opt-in fast listener tasklet

## Executive summary

Author-authorized ad hoc implementation, frozen 2026-09-24 UTC. Add `--fast`
to the existing foreground sdserve MOSlet and `put --fast` to the host client.
Skip the four whole-file verification passes on an activated upload (Agon stage
and target CRC rereads; host stage and target downloads). Normal mode stays the
default. Physical follow-through is now complete: see the measured comparison below.
Both repositories were clean before this contract; there was no dirt to commit.

Original frozen scope: Linux builds, host tests and isolated emulator tests only. Another agent owns
the bench: no physical SD access, network device requests, resets or flashing.
No P4 or resident EMOS behavior change, transport bypass or new listener binary.
Implementation is not an authorization to deploy. Contract is committed before
coding; emulator-coupled implementation awaits Author review before its commit.

## Exact contract and ownership

F01 [x] Freeze this tasklet and the selected boundaries before implementation.
The eZ80 listener owns fast mode for its entire foreground invocation. CLI accepts
`sdserve --fast [absolute-root]` (also root before switch), retaining the normal
root default and existing invocation without options.

F02 [x] Listener skips `checked_digest` only in FINISH and ACTIVATE. FINISH still
requires all declared bytes, syncs and closes successfully; ACTIVATE still stages
and renames, preserving the prior target as backup. Rename/recovery metadata,
replay caching, root/path/size bounds, write counts/errors, packet CRC and sequence
checks remain. Recovery remains checked. Internal 'verified' state must be named
'finished' so fast mode never claims verification it did not perform.

F03 [x] Advertise fast mode in HELLO feature bit 0x10; retain v1 packet layout,
existing operation numbers, 212-byte write payloads and required low feature bits.
The host checks the current listener mode before BEGIN. `put --fast` requires a
fast listener; an ordinary put requires an ordinary listener. Old listeners keep
working with ordinary puts. The updated host does not print verified/SHA readback
claims for fast uploads. Expected length/CRC in FINISH is transfer identity in
fast mode, not a measured digest. Host session journaling/retries remain durable.

F04 [x] Validate normal and fast paths against the actual C engine using the
existing Linux filesystem adapter. Cover empty/boundary/binary uploads, activation,
backup, byte equality checked externally by tests, loss/replay, corruption behavior,
mode mismatch, short writes, write/sync/close failures, and scope/self-overwrite
checks. Count bytes/requests to prove omitted work without promising bench speed.
Build the listener as a MOSlet within 32 KiB, preserving the prior build.

F05 [x] Run an isolated real-eZ80 emulator smoke where feasible, including CLI
option parsing and transfer through the existing emulated UART peer. Use raw FAT
media if filesystem-create/sync behavior is exercised; directory-backed Fab has
known limitations. Record exact inputs, results and remaining hardware gates.
Update the maintained service/client contract and task status; pause for review.

## Research and rationale

Official MOS 3.0.2 documentation for ffs_fwrite, ffs_fclose and ffs_fsync was read
before implementation: [API](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md).
Use those same public operations. The prior
[YMODEM comparison](FEATURE-COMPARE.md) remains relevant: retain framed block
integrity/retry idioms; this change does not replace the protocol or invent a
second file engine. Current service.c and sdcard.py show the four redundant
whole-file passes; eliminating those is the narrow first optimization.

Fast mode can accept incorrect file contents that normal readback would reject.
It retains checked filesystem operation outcomes and recovery artifacts, but is
not verified transfer or power-atomic replacement. Packet CRC is retained because
P4 shares that wire contract; removing it would require a separately scoped
transport change. No general safety checks, memory bounds or routing ownership
are removed merely to save instructions.

## Local results — 2026-09-24 UTC

Local implementation completed before the separately authorized deployment below. Draft
`sdserve-v0.2.0`, fixture `sdserve-fast-probe-r01`, registry r105 use the Author's
standing identity approval. Resident EMOS and P4 source are unchanged. The
emulator uses the already built draft EMOS v0.1.19 utility dispatcher.

| Check | Normal | Fast |
| --- | --- | --- |
| Actual C engine, UBSan host suite | 16 pass | 16 pass |
| Host + actual C engine, activated 4096-byte file: filesystem bytes read | 16404 | 20 |
| Same upload: host READ requests | 38 | 0 |
| Wrong declared file CRC | Rejected | Accepted intentionally |
| Corruption after FINISH | Activation rejects | Accepted intentionally |
| Compiled MOSlet, real eZ80/FatFS smoke | Pass | Pass |

The read-byte comparison counts four whole-file passes plus 20-byte metadata in
normal mode. Fast removes 16384 of 16404 bytes (99.88% of verification reads),
not 99.88% of total transfer time. Both modes retain the upload and its request
overhead. Seven host-client tests pass, including both mode mismatches rejected
before BEGIN and empty/boundary uploads. C tests also cover backups/recovery,
short writes and filesystem failures, replay and packet corruption, root bounds
and self-overwrite rejection. MOSlet is 19243 bytes, leaving 13525 of its 32768
byte image allocation (runtime stack/heap requirements remain unchanged).

The two raw-FAT smoke runs invoke `EMOS sdserve [--fast] /extender/sdtest` from
isolated autoexec files, transfer 0 and 213 bytes, recover an orphan, deliberately
lose one WRITE response, compare resulting bytes and exit the service cleanly.
The fast smoke's external READ comparison is a test oracle, not part of fast
upload. Emulator durations include startup/testing and are not baud or physical
throughput measurements. [Portable exact inputs/results](fast-transfer-results.json).

Reproduction: run the EMOS `tests/test_sdserve.py` suite and Extender
`tests/test_sdcard_client.py` with unittest discovery. Build a separate MOSlet
copy using `RAM_START=0xB0000 RAM_SIZE=0x8000`; prepare profiles with
`scripts/prepare_sd_headless.py --quick --moslet` and additionally `--fast` for
the second profile, supplying pinned firmware/runtime/application inputs. Launch
each profile through its generated `./fab-agon-emulator` wrapper. Machine-local
profiles and logs remain under `.emulator/remote005-{normal,fast}-smoke`; the
isolated source/build is `.emulator/remote005-fast-build`.

The original local-only scope ended here; subsequent deployment authorization
and results follow below. Transaction
placement and interactive-session follow-ups remain in their existing tasks.

## Authorized hardware follow-through — 2026-09-24 UTC

Author released the bench and explicitly requested deployment/testing. This
supersedes the local-only execution boundary above for this follow-through.
Use the exact locally tested draft MOSlet via the existing admitted listener,
retain the installed listener and startup, and install under `/mos/sdserve.bin`.
No EMOS/P4 firmware update or `/emos` migration is needed for this task.

H01 [x] Preserve prior listener/startup, deploy with normal verified transfer,
then verify installed bytes and backup after CLI rename.

H02 [x] Compare matched normal/fast uploads on the same physical card. Time only
host upload-through-activation; keep independent post-test downloads and backup
checks outside that interval. Include empty/boundary payloads, repeated binary
uploads, mode mismatch, self-write refusal, return/reentry and unchanged startup.
Record actual bytes/rates and limitations, without extrapolating game throughput.

H03 [x] Leave the new listener accessible for ordinary use, record exact bench
state and results. Preserve firmware, startup and unrelated user files.

## Physical results — 2026-09-24 UTC

Deployed `sdserve-v0.2.0-b2026-09-24-02-21-03Z` at `/mos/sdserve.bin`;
installed bytes and retained old listener were read back exactly. The preserved
original is `/agents/extender/backups/sdserve-pre-fast-20260924.bin`. EMOS, P4,
onboard VDP and `/autoexec.txt` were unchanged; no reset was required. Build
remains an identified draft from uncommitted source, not a general release.

| Timed activated upload | Normal | Fast | Reduction from normal |
| --- | ---: | ---: | ---: |
| 8192 bytes, mean of two invocations | 16.410 s | 3.283 s | 80.0% |
| Same payload, effective rate | 499 B/s | 2496 B/s | 5.00× throughput |

Clock: host monotonic wall time. Includes HELLO, upload, finish and activation,
client journal writes, plus each mode's configured verification. Independent
post-test downloads, backup checks, startup checks and service restart are
excluded. Two repeats are a bounded comparison, not a throughput distribution;
random binary contents differ between invocations to prove backup retention.
The 8192-byte case is reported first as the largest tested transfer. Empty and
213-byte boundary uploads also pass in both modes. All eight transfers were
independently compared byte-for-byte; retained previous versions matched.
Mode mismatch and self-write were refused; four normal/fast invocations exited
and reentered successfully. Final fresh invocation is `sdserve --fast /`, ready
for host `put --fast`; normal mode remains the executable's default.

[Exact physical results and inputs](fast-transfer-hardware-results.json).
The measured speedup is for this transfer path and sample size, not for games,
raw UART bandwidth or SD media speed. Host-injected keyboard setup worked;
no new human/native-keyboard acceptance is claimed. Local evidence and scripts
are retained under `agents/fast-transfer-hardware`.

Author accepted the completed work and authorized commit/push on 2026-09-24 UTC.
