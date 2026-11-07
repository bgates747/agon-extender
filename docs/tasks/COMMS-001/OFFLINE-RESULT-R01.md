# Accuracy foundation — offline result r01

The accuracy protocol, deterministic oracle, bounded retry engine, durable host
journal and real Pi peer command line pass their source checks. A separate eZ80
compile/link probe includes the orchestration code. This is substantial reusable
implementation, but not a deployed mixed-carrier or overnight appliance.

| Check | Result | Boundary |
|---|---|---|
| Host C++ ASan/UBSan | PASS | All wire bits, spans, controls, safe retirement and orchestration models |
| Independent C++/Python records | 96 exact matches | Six patterns × four carrier pairs × four lengths; host execution |
| Python source/socket/CLI checks | 15 PASS | Real fragmented TCP, CRC/pattern/case refusal, truncation/extra bytes, deadlines, journal failures, actual peer readiness/close |
| Bounded repeat policy | PASS | Recovery retains first error; fifth failure ends case; UART/ownership/log failures stop dispatch |
| eZ80 core/engine link | PASS, 8,381 bytes | Stopped compilation probe only, not executed on Agon |
| Physical mixed-carrier/SD run | Not performed | Real EMOS/P4/MOS SD adapter is still required |

1. Source `eced8513f60401f38600acf4d0734e3aa5ae1d67` and
   [structured record](OFFLINE-RESULT-R01.json) retain input/output hashes.
   Identified native probe:
   `comms-accuracy-core-r01-b2026-11-07-03-58-28Z`, SHA256
   `d5f0c93b034f90133262ff2dfe99ec167b2e601f4b9890bca2f78d22560c6c4d`.
   Generated binary/source work and logs are retained locally, not committed.
2. The real peer accepts one trusted case attempt, checks every record and
   clean TCP close, then exits. Its NACK is a network diagnostic for a future
   UART-control adapter; it cannot prove physical UART delivery or pin retirement.
3. The engine checks each frame and the verified-prefix/complete-stream CRC.
   It retains first error and attempts even after recovery. Unknown ownership
   produces no further adapter calls, including log/MOS/control/cleanup calls;
   the prior intent remains incomplete for independent diagnosis.
4. Journals use exclusive creation, complete-write checks and host fsync;
   truncated tails, pending intents and failed writes are not repaired/replayed.
   A complete journal is not necessarily a passing case: retain its outcome.
   Agon's actual SD write/close/commit path remains unimplemented.
5. Shared serial check tranche took6.317 seconds on the Pi, including the separate
   performance checks. This is build/check duration, not carrier performance.
   All owned children joined and compiler285 was released; no emulator, device,
   firmware, startup, reservation takeover or sensor operation occurred.
6. Earlier compilation caught a strict host integer-width warning in the
   independent benchmark timer expression; it was corrected without weakening
   warnings. Retained prior source/check records remain separate.

## Remaining integration boundary

The live adapter must positively admit each carrier leg, restore UART1 before
failure reports, validate controls and bind real parser/VDU and MOS SD semantics.
The existing NM compositions do not supply that mixed-leg service. The reviewed
fixed GPIO filter has no suppression counter/event API; actual rejected-pulse
correlation remains unavailable, rather than a measured zero. These facts do
not invalidate portable checks or qualify the missing hardware behaviour.

Wolf retains actual bench custody for Smith's review. No new target work was
performed or inferred from its restored-idle held state.
