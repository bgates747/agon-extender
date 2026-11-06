# Experimental parallel application message contract

The application explicitly selects `ext.netp` through the existing MOS0x51
gateway. All NM command/reply bytes cross the parallel pipe; UART1 carries only
keyboard and bounded carrier coordination. This contract is agreed with MechAgon
under Smith's ABI delegation on2026-11-05. It specifies development work, not an
installed or hardware-qualified service. [NET-004](../tasks/NET-004.md) owns the
remaining implementation and qualification work.

## Ownership and calls

The foreground ADL/MBASE0 application calls with interrupts enabled, static
storage and no competing gateway call. EMOS validates complete caller spans,
owns shared-pin parking/restore and preserves the committed Legacy display route.
P4's console owner owns parallel transfer and bounded copies; its network worker
alone owns the socket. No NM application interrupt callback is installed.

The ordinary66-byte gateway descriptor selects provider `ext`, service `netp`.
All integers below are little endian. The first input byte selects the operation.
The NM envelope remains14..142 bytes, with at most128 opaque application bytes.

| Operation | Input after operation byte | Output | Lifetime |
|---|---|---|---|
| OPEN=0 | none | eight bytes: `NP`, version1, parallel capability1, uint32 local session | Explicit capability; missing service refuses, no fallback |
| TAKE=1 | uint32 local session | One complete NM reply | Empty differs from fault; undersized output reports required size without consuming |
| SUBMIT=2 | uint32 local session, one complete NM command | none | BUSY accepts nothing; caller source borrowed only through synchronous bounded return |
| RELEASE=3 | uint32 local session | none | Success requires peer/local carrier quiescence and no live app reference; refusal retains ownership |

Result0 is local success,31 BUSY/not yet ready,35 unavailable,130 undersized,
131 empty and132 terminal carrier fault. Invalid requests use the existing
gateway's invalid-parameter result. `outputLength` reports the reply/required
size on TAKE. No partial result is published. Each successful OPEN returns a
nonzero, nonreused boot-local token; exhaustion refuses rather than wraps.

One accepted command remains pending until its matching result is consumed.
P4 retains a selected reply through physical completion. Offering a buffer to
DMA does not consume it. A failed/uncertain physical transfer faults the session;
it never enables automatic retransmission. Application session/query fields and
32-bit nonwrapping query allocation retain their existing NM meaning. Local
acceptance, socket delivery and remote game-turn execution are separate facts.

## Physical ordering

EMOS and P4 negotiate one bounded direction/count/transaction before a transfer.
Those control bytes contain no NM header or application payload. The eZ80 clocks
the complete parallel record; no per-byte acknowledgements or checksums are added.
The existing shared-pin owner restores UART1 after actual pad release. P4 cannot
emit a parallel reply through its ordinary UART reply drain. Legacy UART0 remains
the mainboard graphics route throughout.

Initially MechAgon prioritizes intent and serializes a parallel epoch after
RFC25 source release, physical UART0 TEMT and required VDPlet DONE. This does not claim concurrent
rendering/network transfer or bounded IRQ latency. EMOS/P4 implementations must
preserve unrelated UART0 ISR state and measure service gaps before such claims.
RELEASE is foreground polling, not a cancellation/replay service. A failed
release must not be reported as clean disable.


## C application caller

The experimental `include/agon/net_parallel.h` implements this foreground ABI.
Keep a zero-initialized `agon_netp_client` in application RAM (223 bytes on native
eZ80), and supply separate whole-record input/output buffers up to142 bytes.
`agon_netp_open`, `agon_netp_submit`, `agon_netp_take` and `agon_netp_release`
return the gateway result. SUBMIT accepts a complete NM record with the admitted
32-bit token and an increasing query. TAKE supplies actual/required length;
undersized output retains the record. A positive RELEASE clears local ownership;
BUSY/fault retains it. The include does not install or restore a callback.

This explicit EMOS composition excludes the prior resident UART NM endpoint;
`ext.net` returns unavailable. There is no automatic carrier fallback. The
separate historical UART SDK/installed firmware remain identified by their own
records. A checked header does not establish an installed matching service or
an RFC25-enabled callback map; use the eventual matched component manifest.


## Matched UART0 admission

The optional matched EMOS profile routes public25h through EMOS admission to the
reviewed RFC25 FIFO sender; historical experimental42h/43h are unavailable in
that profile. HL/BC/DE supply source/count/callback, all24 bits. Foreground
ADL/MBASE0/EI and complete ordinary application RAM spans are required. A returns
0 accepted,19 invalid,31 busy,32 unsafe caller or35 unavailable route; flags are
unspecified, and BC/DE/HL/index/alternate registers and MB are preserved. A refusal
changes no TX source/descriptor/IER and generates no callback.

The primary-register callback is a source-release signal only; preserve indexes
and alternate registers if it uses them. No MOS call, wait or reentrant submit
belongs there. EMOS retires the FIFO tail through a bounded foreground IER/TEMT
read before another physical epoch. A logical netp session remains open across
ordinary Legacy UART0 batches. Caller serialization still includes required
receiver DONE. These checked source contracts do not establish a physical pass.
