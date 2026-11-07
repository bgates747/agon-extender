# Accuracy appliance — first implementation tranche r01

Implement and qualify the reusable accuracy engine and real Pi TCP peer without
touching an occupied bench. Smith authorises the largest independent tranche
on both communications tasks on November 6, following design publication.
This tranche does not claim the still-unimplemented mixed-leg firmware adapter.

1. Freeze an explicit, bounded fixture record and deterministic pattern oracle.
   Implement portable C++ and independent Python encoders/decoders. Verify
   metadata/payload CRC, identity, lengths, reserved fields and attempt limits.
2. Implement the positive-retirement/UART-report/repeat state machine. Five
   failed attempts total; duplicate or stale controls cannot trigger another
   attempt. Unknown ownership, failed logging or broken control halts dispatch.
3. Implement an exclusive append-only journal and a real bounded Pi peer with
   NM-compatible four-byte length-prefixed TCP records. Its error response is
   a request for P4's UART control adapter, not proof it travelled over UART.
4. Qualify independent byte/CRC implementations, arbitrary TCP fragmentation,
   wrong/corrupt/truncated/duplicate/stale records, journal truncation/write
   failure, cancellation and the five-attempt boundary. No same-process fake
   result can stand in for real socket and cross-language tests.
5. Compile a stopped eZ80 core self-check executable to prove actual target
   syntax/types/link fit. It is not a ready appliance and is not deployed/run.
6. Audit fixed GPIO filtering and existing VDU/transport owners. Retain precise
   unsupported capabilities. Add no resident hook or numeric gateway operation
   until its owned admission/lifetime contract is concretely bound.
7. Build/check through normal Pi compiler FIFO: one compiler/child at a time,
   expected under5minutes/512MiB,15minute tranche horizon,180s compiler and60s
   check bounds,80C stop/512MiB available floor and joined-owned cleanup. No
   emulator, bench, service install, reset, flash or live network peer selected.
   Loopback sockets are host checks only, not a device qualification.

## Fixture record r01

The TCP wrapper is uint32LE complete-record length. The record is 40 header
bytes, zero to84 payload bytes, then uint32LE CRC-32/ISO-HDLC covering the
entire header and payload. Maximum complete record is128 bytes, matching the
existing NM opaque application bound. This is a new fixture payload protocol,
not an existing resident API or change to ordinary VDP packets.

| Byte offset | Width | Field |
|---|---:|---|
| 0 | 4 | ASCII CA01 |
| 4 | 1 | Kind: DATA1, ACK2, NACK3, RETRY4 |
| 5 | 1 | Selected outbound carrier: UART1=1, parallel=2 |
| 6 | 1 | Selected return carrier, same values |
| 7 | 1 | Pattern0..5: zero,ones,alternating,walking,ramp,seeded |
| 8 | 4 | Nonzero run |
| 12 | 4 | Nonzero case |
| 16 | 4 | Nonzero record sequence, no wrapping reuse |
| 20 | 4 | Pattern seed |
| 24 | 4 | Total logical bytes, at most16MiB |
| 28 | 4 | Byte offset into logical block |
| 32 | 1 | Attempt1..5 |
| 33 | 1 | Data direction: outbound0, return1 |
| 34 | 2 | Payload byte count0..84 |
| 36 | 1 | Status: OK0,CRC1,PATTERN2,SEQUENCE3,TIMEOUT4,OWNER5 |
| 37 | 1 | Flags: bit0 positive owner-retirement witness; others0 |
| 38 | 2 | Reserved zero |

DATA and ACK carry actual data, require OK status and an in-range logical span.
NACK carries exactly two uint32LE values: expected and observed CRC. It requires
a nonzero status. RETRY carries no payload, OK status and a positive retirement
witness. All kinds have independently checked CRC and nonzero identities.
Do not trust a bad-CRC header to identify which case failed; use the already
admitted outstanding context. NACK/RETRY physical delivery must be UART1
regardless of the selected data-return carrier in the case metadata. The Pi
peer cannot assert physical owner retirement, so its NACK leaves that flag off.

No test can automatically resume after reset, loss of the UART control path or
unknown owner state. The prepared peer refuses unsupported kinds and exits on
its original finite operation/whole bounds; later adapters own deliberate
recovery/repeat decisions.
