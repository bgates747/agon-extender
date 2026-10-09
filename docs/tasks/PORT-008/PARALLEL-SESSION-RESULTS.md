# PORT-008 — Private session lifecycle results

**The bounded session step passes.** EMOS and P4 now have a paired private
prepare/challenge/commit lifecycle and session-aware block admission wrappers.
Host and linked eZ80 checks and both full target builds pass. The EMOS candidate
uses **130,212 ROM bytes**, leaving **860 free**. No live UART parser, physical
boot fence or parallel payload is enabled; no hardware or SD operation occurred.
Author review precedes the next integration step.

## Ownership and behavior

R01 — Reuse the existing fixed 16-byte control carrier, console CRC and
prepare/challenge/commit idiom. Version 2 prepare/commit use a distinct capability
tag; the version-1 console rejects these bodies. P4 issues a nonzero challenge;
EMOS trusts it only after matching transaction and commit replies. The
[session contract](PARALLEL-SESSION.md) records exact fields and prerequisites.
The capability requested during setup is not a formal mode commitment. Block
admission still requires committed ExExt, exact direction/length, strictly next
sequence and matching acknowledgement under the existing admission rules.

R02 — Both owner wrappers require their existing release sequencer to have
reached UART-ready state. EMOS additionally queries its actual serializer
reservation under the existing IRQ lock: no interrupt-disabled caller, private
send in progress, parked UART, pending stop/fault or unowned serializer can
advance it. A caller cannot supply a Boolean claiming reservation. No extra
transmitter, parser, task, UART rate or application entry point is introduced.

R03 — The same small 11-byte lifecycle is mirrored exactly in EMOS and P4.
Cancellation clears capability and block sequence, retaining the previous nonce
only to reject its reuse. Session-aware admission refuses those retained bytes
while inactive. The owner also asks its existing handover sequencer to recover;
it does not acknowledge pad release, prematurely drop the serializer, restore
UART or publish successful payload completion. Explicit cancel is available
for future timeout/reset/mode-exit handling; those events are not yet bound.

## ROM and RAM

Baseline is the tested UARTFLOW extraction, not production. The unchanged
AUDIT-008 accounting tool processed this candidate's full wrapper-linked image.
Percentage change is `(candidate − baseline) / baseline × 100`.

| Measure | UARTFLOW baseline | Session candidate | Difference |
|---|---:|---:|---:|
| ROM used, bytes | 129,464 | 130,212 | +748 (+0.58%) |
| ROM free below 131,072, bytes | 1,608 | 860 | −748 |
| Static RAM, bytes | 4,058 | 4,058 | 0 |
| Private session object, bytes per owner | Not instantiated | 11 | No live object yet |

The session functions reuse the single console CRC in EMOS's existing console
source unit. The reservation query reuses the existing IRQ lock. No linker/image
guard was relaxed. Future live coordinator state will consume RAM and its
binding will consume further ROM; 860 bytes is current headroom, not an estimate
that all remaining work fits. No timing or throughput claim follows from size.

## Validation

| Check | Result | Scope |
|---|---|---|
| Paired maintained session owners | 1,149 checks pass, ASan/UBSan | Full prepare/commit, both directions and boundary lengths, every-field corruption, old-version rejection, stale/replayed replies, owner/reservation refusal, cancellation at all five lifecycle states |
| Linked eZ80 session owners | 1,334 checks pass | Host/target agreement, actual reservation query, foreground/IRQ gates, bounded return, IX/SP/IFF preservation, immutable inputs, buffer guards, no port I/O |
| Existing linked UART reservation | 22 checks pass | Ordinary/private send exclusion, park/restore/status reservation and failure behavior |
| Existing linked UART parking | 289 checks pass | Actual UART register transitions, parser/serializer/IRQ boundaries and cleanup |
| Existing paired block admission | 18,097 checks pass | All lengths/directions, descriptor/ACK validity, replay/exhaustion and mode gates |
| Existing paired release/handover | 5,208 checks pass | Both directions, delayed adapters, reset/cancel at every step, failed release, absent peers and queued input |
| Actual native P4 UART parking | 196 checks pass | SDK boundaries, shift-register/RX/core fences, release/restore order and failures |
| Keyboard ordinary/telemetry, console, console session, owner-core and mode lifecycle | Pass | Existing input, console ownership and mode behavior retained |
| Prepared-source/build-profile checks | Six tests pass | Actual selected EMOS snapshot and generated source ownership |
| Complete maintained EMOS wrapper | Pass | Compile/link, UART divisor, parallel, keyboard, console, ABI and VDU guards |
| Complete P4-PC native wrapper | Pass | Existing `p4-console` browser profile, pinned dependencies and maintained validator |
| P4 unchanged-source recheck | Pass | Frozen source closure, incremental native rebuild and repeated maintained validation |

Linked tests execute actual complete-image EMOS instructions with modeled
registers; they are not a whole-system Fab run or electrical qualification.
ASan/UBSan were enabled; leak scanning was disabled because LeakSanitizer cannot
inspect processes under the sandbox tracer. There are no retained heap objects
in the session core. Test timings in logs describe host checks, not target speed.

## Evidence and reproduction

[The result manifest](PARALLEL-SESSION-RESULT.json) identifies exact component,
source, test and log hashes. Complete local evidence, the pinned builder clone,
prepared sources, ROM ledger, P4 source archive and CPU vectors are retained in
ignored `agents/port008-session/`. These are development checks, not a production
selection or permission to flash. The hardware-tested UARTFLOW image remains
installed unchanged.

From the Extender root:

```sh
ASAN_OPTIONS=detect_leaks=0 SESSION_VECTORS=agents/port008-session/vectors.txt \
  .venv/bin/python tests/parallel_session_test.py
ASAN_OPTIONS=detect_leaks=0 .venv/bin/python tests/parallel_admission_test.py
ASAN_OPTIONS=detect_leaks=0 .venv/bin/python tests/parallel_handover_test.py
```

Build EMOS through its maintained `firmware-check` wrapper using the selected
builder/toolchain configuration. Generate `nm.txt` with that toolchain's
`ez80-none-elf-nm -an` beside the same `MOS.bin`, then run:

```sh
cargo run --offline --release --manifest-path ../agon-emos/tests/uart_put_cpu/Cargo.toml \
  --bin parallel_session -- IMAGE_DIRECTORY agents/port008-session/vectors.txt
```

Set `MOS_AGONDEV_ROOT` and `MOS_AGONDEV_WORKTREE` to that build's actual
prepared snapshot for `test_emos_port.py`; its defaults may name a stock-MOS
snapshot. The unchanged accounting tool requires pyelftools; this run retained
0.33 in a task-local dependency directory rather than changing another project's
environment. P4 uses the existing host-native tool selection and retained pinned
dependency lock. No product-source workaround was needed for build preparation.

## Remaining integration

The existing c2b/c3 work still owns live session/parser binding, fresh identity
origins, stale-wire quarantine, complete queue/event/shift-register draining,
peer quiescence, per-phase deadlines, post-block status, and mandatory reciprocal
physical release at boot. A RAM reset alone cannot prove old UART replies gone.
The native payload adapter and physical first/last-byte/contention proof also
remain open. Session capability is not release evidence or payload success.
Changes remain uncommitted for Author review; unrelated EMOS application-peer
work is preserved.
