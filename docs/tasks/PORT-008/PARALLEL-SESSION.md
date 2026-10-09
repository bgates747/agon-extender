# PORT-008 — Private parallel session exchange

The next bounded c2b increment supplies the missing trusted session lifecycle
for the existing admission gates. It uses the console challenge/commit idiom
and CRC, and requires completed release recovery plus EMOS serializer ownership.
It is not connected to live startup, UART parsing, GPIO or ExExt activation.

## Research and ownership

Official `agon-docs/docs/vdp/System-Commands.md` at
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b` reserves VDU 23,0 for VDP commands.
Official VDP v2.16.0 at `c7ac293d2aa81ddfa693390549bcd909069c8fc3`
and [the existing console protocol](../../protocols/excom-console.md) bound F7
and the fixed body length. Both reference trees remain read-only. Reuse the
maintained `console_session.hpp` prepare/challenge/commit design, not a new
transport framework. EMOS implementation belongs in `agon-emos`; P4 in Extender.

## Private candidate records

All records retain the [admission carrier](PARALLEL-ADMISSION.md): 16-byte bodies,
`EX`, version 2, CRC-16 over bytes 0–13. V1 console behavior remains unchanged.

| Offset | Session prepare/commit meaning |
|---|---|
| 3 | Prepare 1 / reply 81h; commit 3 / reply 83h (offer remains 2 / 82h) |
| 4–7 | Nonzero EMOS transaction identity, fixed throughout this exchange |
| 8–11 | Zero on prepare; fresh nonzero P4-issued challenge otherwise |
| 12 | Capability tag 3: the agreed eight-bit ExExt block contract |
| 13 | Zero; reserved/nonzero values cannot establish capability |

EMOS sends prepare only after its completed recovery sequencer reaches UART
and the existing serializer is reserved. P4 handles session records only at its
UART recovery state, on the sole console owner. P4 generates the challenge;
no received offer grants itself a session. P4 stages prepare, then confirms the
exact transaction/challenge on commit. EMOS trusts the session only after the
matching commit reply. Sequence starts at zero so the first block is one.
The capability tag describes a private agreed contract, not current mode
commitment: only the existing EMOS mode coordinator may commit ExExt later.

The common candidate lifecycle is mirrored byte-for-byte between owners. On
cancellation, timeout, reset or mode exit its active flag and sequence are
invalidated. The previous nonce is retained during non-reset cancellation to
refuse its reuse; it cannot admit a block while inactive. An explicit fresh
prepare may replace an idle old session. P4 refuses a zero/repeated challenge.
These identities are replay guards, not authentication. The future boot/parser
adapter must quarantine stale UART bytes and supply fresh transaction/nonce
identities; local RAM reset alone cannot prove that old wire replies vanished.

## Verification and remaining gate

S01 [x] — Implement owner wrappers plus the small shared session lifecycle,
retaining existing admission and serializer code. No new live parser or boot call.

S02 [x] — Exercise full paired prepare/commit and both-direction admission;
wrong mode, not-yet-released/parked owner, absent reservation, corrupted fields,
old versions, duplicate commit, stale reply, cancellation and sequence reset.
Failure must not overwrite a reply buffer or publish an active EMOS session.

S03 [x] — Execute emitted host vectors through wrapper-linked EMOS instructions;
verify returns/state/buffer boundaries, register/interrupt preservation and no
GPIO access. Compile P4-PC and full EMOS; reuse AUDIT-008 ROM accounting.

S04 [x] — Record exact evidence and stop for review. Session expiration, complete
wire parsing/draining, shared-pad boot fencing, per-phase deadlines and native
payload binding remain open. No hardware deployment follows from these checks.


## Implementation checkpoint

The shared 11-byte lifecycle is mirrored exactly between P4 and EMOS. Existing
handover/admission leaves remain reusable; new session-aware wrappers require
active capability before passing their six session/sequence bytes to those
leaves. EMOS checks its actual serializer reservation under its existing IRQ
lock, including interrupt-enabled foreground context, UART ownership and pending
fault/stop. P4 checks the same UART-recovered sequencer before session requests.
No pointer, callback, parser, timer or live boot binding is added.

Cancellation is an explicit owner primitive: it invalidates capability/sequence
and asks the existing handover sequencer to release. It does not drop the
serializer, acknowledge pad release, restore UART or publish payload success.
The future coordinator must invoke this primitive on deadline/reset/mode exit;
those events are not yet connected to ordinary firmware startup/operation.
The full EMOS build currently uses 130,212 ROM bytes (+748), leaving 860 free;
static RAM remains 4,058 because no live session object is instantiated yet.

[Results and reproduction](PARALLEL-SESSION-RESULTS.md) bound this checkpoint.
