# REMOTE-005 — Opt-in fast listener tasklet

## Executive summary

Author-authorized ad hoc implementation, frozen 2026-09-24 UTC. Add `--fast`
to the existing foreground sdserve MOSlet and `put --fast` to the host client.
Skip the four whole-file verification passes on an activated upload (Agon stage
and target CRC rereads; host stage and target downloads). Normal mode stays the
default. This reduces transfer work; physical throughput gains are unmeasured.
Both repositories were clean before this contract; there was no dirt to commit.

Linux builds, host tests and isolated emulator tests only. Another agent owns
the bench: no physical SD access, network device requests, resets or flashing.
No P4 or resident EMOS behavior change, transport bypass or new listener binary.
Implementation is not an authorization to deploy. Contract is committed before
coding; emulator-coupled implementation awaits Author review before its commit.

## Exact contract and ownership

F01 [x] Freeze this tasklet and the selected boundaries before implementation.
The eZ80 listener owns fast mode for its entire foreground invocation. CLI accepts
`sdserve --fast [absolute-root]` (also root before switch), retaining the normal
root default and existing invocation without options.

F02 [ ] Listener skips `checked_digest` only in FINISH and ACTIVATE. FINISH still
requires all declared bytes, syncs and closes successfully; ACTIVATE still stages
and renames, preserving the prior target as backup. Rename/recovery metadata,
replay caching, root/path/size bounds, write counts/errors, packet CRC and sequence
checks remain. Recovery remains checked. Internal 'verified' state must be named
'finished' so fast mode never claims verification it did not perform.

F03 [ ] Advertise fast mode in HELLO feature bit 0x10; retain v1 packet layout,
existing operation numbers, 212-byte write payloads and required low feature bits.
The host checks the current listener mode before BEGIN. `put --fast` requires a
fast listener; an ordinary put requires an ordinary listener. Old listeners keep
working with ordinary puts. The updated host does not print verified/SHA readback
claims for fast uploads. Expected length/CRC in FINISH is transfer identity in
fast mode, not a measured digest. Host session journaling/retries remain durable.

F04 [ ] Validate normal and fast paths against the actual C engine using the
existing Linux filesystem adapter. Cover empty/boundary/binary uploads, activation,
backup, byte equality checked externally by tests, loss/replay, corruption behavior,
mode mismatch, short writes, write/sync/close failures, and scope/self-overwrite
checks. Count bytes/requests to prove omitted work without promising bench speed.
Build the listener as a MOSlet within 32 KiB, preserving the prior build.

F05 [ ] Run an isolated real-eZ80 emulator smoke where feasible, including CLI
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
