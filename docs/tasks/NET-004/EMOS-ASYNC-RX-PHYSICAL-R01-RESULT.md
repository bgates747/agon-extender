# Async UART1 receive correction — first isolated physical result

The corrected EMOS build passed one finite exact-byte echo test through the P4
and Pi: all 176 records and four connection lifecycles completed, with no
recorded first error. Extender restored and independently verified the incoming
working ROM and released reservation 79. This qualifies the isolated case;
MechAgon's overlapping renderer/network workload remains a separate trial.

## Identity and result

| Item | Observed result |
|---|---|
| Candidate EMOS source | `954e3c54cd9a1b03191d1d2f04f03ae7dc295109` |
| Candidate full-ROM SHA-256 | `8de66c3ac52a4f4c90ffaac30f7de740c7aa71218f4753c2f3950d6fb9a5a222` |
| Candidate build | `agon-emos-eirene-r05-b2026-11-07-09-58-06Z` |
| Appliance | `netasync-r01-b2026-11-07-09-46-17Z`, 17,809 bytes, SHA `7ad4c8915a6f0a2ed721f5ab8ac080ca526d92ce3b30a1febc74567fb037fa1e` |
| Workload | Four sessions, 44 records each; lengths 0, 1, 2, 17, 63, 64, 65, 75, 79, 127, 128; four deterministic bit patterns |
| Data path | eZ80 application → EMOS-owned UART1 → P4 NM/TCP worker → Pi echo, and the same path back |
| Exact payload verification | Pi and eZ80 each passed 176 records; 9,936 payload bytes per direction, excluding framing |
| Connection retirement | Four opens/closes passed; every session ended detached, first error 0; final release 0 |
| Application state | Entry mode restored, actual CLI returned, callback and route restored; native SD witness agrees |
| Evidence preservation | 65,536 bytes from application RAM saved before any subsequent LOAD; SHA `885a5fda012e2efd5a0dd3910fc123d6ac1604664a1ded4666eae445c80b87a0` |
| Final restoration | Full 131,072-byte incoming EMOS `a25f1612…` independently compared; P4/native VDP/startup/listener unchanged |
| Clean release | Generation 79, `2026-11-07T10:36:14.079814+00:00`; all actors stopped, SD mounted |

The candidate adds a scoped foreground RX STOP hold, a post-RX ownership check,
and the generic bounded UART0 CTS retry with an atomic ownership observation.
The application still owns the unchanged generic sender core. Raw ROM use is
130,497 bytes, leaving 575; this is 356 bytes above the failed provisional ROM,
with two additional resident state bytes. It is an experimental selection, not
production promotion.

## Validation and limits

1. Exact candidate and rollback ROMs were staged/read back before installation;
   each newly installed ROM was independently read back in full. Fresh raw mode,
   callback, route, whole startup/listener, actual CLI, neutral input, offline
   listener/worker and free serial ports passed at final handback.
2. The eZ80 appliance wrote its result to SD only after positive connection
   retirement. The Pi retained the complete ordered byte matrix. The host
   controller joined both serial readers and the echo peer before collection.
3. The native elapsed witness was 288 nominal MOS counts at 120 counts/second.
   Host dispatch/terminal observation was 12.996 seconds and peer lifetime
   13.528 seconds; their boundaries include different setup/delivery work.
   These are provenance, not comparable speed or CPU measurements.
4. No reset, replay, sensor, renderer, PRT ownership, forced CTS stall or active
   UART0 workload was added. The test does not establish concurrent-carrier
   safety, long-run reliability, an electrical STOP-tail bound or useful CPU
   savings. It does not establish the cause or cure of the receiver overrun in
   [the original failed consumer trial](EMOS-ASYNC-PHYSICAL-R01-RESULT.md).
5. The earlier non-atomic combined ROM `d43150…` was withdrawn before any
   installation. Its source/build evidence remains separate from this result.

Private request, 89-input freeze, complete host/peer/native/SD/RAM records,
installation/readback, restoration and actual release receipts remain in the
owner's retained physical evidence. The [investigation plan](EMOS-ASYNC-RX-R01.md)
owns the subsequent consumer and headroom gates.
