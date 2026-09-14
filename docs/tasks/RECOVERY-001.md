# RECOVERY-001 — Restore the known-good EMOS through P4 ZDI

## Executive summary

**Recovery accepted:** the Author confirms Rally works on the restored Agon.
The full known-good EMOS ROM and original P4 firmware were restored and
verified; CLI, SD read/write and hardware voice passed. Normal harness,
sniffers, P4/ZDI recovery leads and Pi reset remain connected and available
until further notice. The maintained recovery capability must remain usable.
The cause of the failed normal flash update is still open; no E07 or new
performance experiment starts from this acceptance.

## Contract and evidence

Follow [the enduring protocol](../mos-recovery.md). The selected 128 KiB ROM
backup SHA-256 is `1cd65eac21780a8a7c82e14209737c38796e24f32300524e58a93e5c44e096d8`.
Its first 130071 bytes exactly match working
`agon-emos-v0.1.16-b2026-09-13-07-31-36Z`, SHA-256
`1da8330462eed54317e5889cf3f09cb1abaca8b478f7d92b88a3a1d74c9fc70c`;
remaining bytes are FF. This was read from the running Agon before E05.
Private run artifacts belong under `agents/mos-recovery/`, device identities
remain in `HARDWARE.local.md`. Onboard VDP is not changed.

## Execution

1. [x] Identify the actual pre-test ROM and verify its relationship to working EMOS.
2. [x] Prepare maintained programmer and manifest-bound payload tools; preserve upstream ZDI/flash logic and historical tombstones. Add explicit host arming, bounded waits and full pre/post ROM capture. Build and review before deployment.
3. [x] Preserve/verify P4 baseline, deploy programmer and verify target ZDI identity without flash mutation. Stop for wiring assistance on mismatch.
4. [x] Capture and retain current ROM, arm the selected recovery, verify RAM and full flash readback. No automatic retry.
5. [x] Restore P4 firmware and verify it; arrange safe release of programming connections and target reboot. Check fresh keyboard/SD admission and unchanged startup when available.
6. [x] Record precise outcome and remaining human checks; spoken emulator notification and pause.

A document or command submission is not execution evidence. Mark individual
outcomes honestly if a physical step blocks completion. Changes remain local;
no experimental push. Check scope and update this record at each boundary.

## Preparation checkpoint — 2026-09-14

Maintained `p4-mos-recovery` builds successfully with the pinned project P4
toolchain. Three host tests pass: payload hash/size refusal, complete ordered
dump/CRC verification, and byte-identical retained ZDI/initialization source.
Factory components compare exactly at their manifest offsets. The dedicated
source uses explicit USB Serial/JTAG commands, 256-byte ZDI bursts with idle
yields, a pre-erase full-ROM dump, and independent post-write byte comparison.
Host arming requires a valid dump; an already-correct ROM is not erased.
No original code tombstone or EMOS product source was changed.

Artifacts and a guarded P4 backup/deployment/restoration script are staged
under the private run01 directory on the Pi. No serial port opened, no flash
or reset yet. Await confirmation that the normal Agon–P4 harness is isolated,
with only the three ZDI programming connections between those boards, before
deployment. Programmer readiness does not establish wiring or hardware success.

The Author subsequently confirmed all normal wiring remains attached and
directed that it stay attached. Reviewed r03 endpoints, the separate keyboard
UART pair and pinned Arduino startup: there is no overlap with ZDI46/47.
The programmer now explicitly releases all normal harness endpoints as inputs
without pulls before ZDI initialization. Rebuild and restage this refinement;
the obsolete blanket isolation step is superseded. Proceed within the already
authorized recovery scope; no additional physical wiring request is needed.

## Physical results — 2026-09-14

**Recovery passed through flash verification and actual MOS services.** The
maintained P4 programmer ran with all existing wiring attached. Three ZDI
identity reads passed. A full failed-ROM dump was retained before any erase;
the eZ80 PC was 000038. There was one authorized restore, no erase retry.

| Check | Result |
|---|---|
| Failed ROM | 126758 bytes differ from known-good; 99812 bytes are FF, including reset entry |
| Failed-ROM SHA-256 | `de4b55a4cc7a68ba1eb12aa12a4e3ba88d893ddb64a06fe338715c9dd801097a` |
| Restored ROM | All 131072 bytes exactly match pre-E05 ROM; CRC32 `81b2b6a4` |
| Verification | Programmer RAM CRCs, flash CRC and byte comparison; independent USB-host and workstation full-dump comparisons |
| Original P4 | Actual affected 2 MiB preserved, restored, independently flash verified; original r17 13:07:24 identity and USB/Ethernet startup observed |
| Agon restart | One Pi reset after restoring P4; fresh native keyboard admission |
| CLI and SD | Keyboard-issued EXEC ran MOS COPY; copied startup matches; 257-byte SD write/read passes |
| Startup | Root autoexec and prior backup byte-for-byte unchanged |
| Onboard VDP | Unchanged during recovery |
| Wiring | Normal harness and ZDI leads remain attached; no jumper change |

The first HTTP probe after P4 restore preceded usable network service; it did
not issue a target reset. The established USB boot observation then confirmed
original P4 identity, native keyboard and DHCP before the single target reset.
This is a readiness observation, not an extra MOS programming attempt.

The damaged ROM proves the earlier normal update did not leave valid firmware.
It does not yet establish why that update failed. Preserve the dump and review
the normal FLASH path before authorizing another MOS update or E07. Human
visual/input acceptance is still pending. Private full evidence is retained in
`agents/mos-recovery/run01/` and `agents/mos-recovery/remote-evidence/`.

Hardware notification executed through the accepted British voice player. New
SD service incarnation and stage6 audio_commands=pass receipt verified; returned
to Legacy MOS prompt. Human hearing/visual/input confirmation remains pending.
Source/procedure changes remain local and uncommitted for review; no push.

## Human acceptance — 2026-09-14

The Author confirmed “rally works” and explicitly retained all recovery, Pi5
reset, sniffer and normal data wiring for future use. RECOVERY-001 is accepted
and removed from the unfinished TODO. This supersedes earlier pending human
visual/input statements; it does not resolve the cause of the normal FLASH
failure. No new firmware deployment or commit/push was requested in this update.
