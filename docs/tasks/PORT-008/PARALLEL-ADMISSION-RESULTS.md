# PORT-008 — Parallel admission gate results

## Executive summary

F02c2b1's private admission gates pass host and linked-eZ80 checks. Both gates
start the real handover sequencer only for an ExExt descriptor with the expected
session and next sequence; EMOS additionally requires P4's exact acknowledgement.
They are not connected to live UART parsers or startup. F02c2b remains open.
The accepted reset policy is now recorded as P08-F-D03 and in ADR-0026.

The EMOS image grows by **416 bytes**, leaving **521 bytes** below the 128 KiB
image limit. The remaining coordinator/native implementation must reconcile
this budget before deployment. No linker limit or ownership guard was relaxed.
No hardware, network device, SD, reset or deployment operation occurred.

## Implementation

1. The private candidate reuses the current 16-byte F7/FF control carrier with
   version 2. Both repositories retain byte-identical checksum/wire headers.
   The CRC implementation is unchanged (also checked in linked code after
   resolving seven relocated helper calls), extracted into a shared include; the
   EMOS gate lives with existing console code to avoid a second ROM copy.
2. Each coordinator supplies its trusted four-byte session and last consumed
   two-byte sequence. A received offer cannot establish a session. Both gates
   reject wrong mode, non-UART/recovery phase, zero/mismatched session, malformed
   direction/length, CRC errors, duplicate/skipped/zero sequence and wraparound.
   Success consumes exactly one sequence; rejection changes no state/output.
3. EMOS compares P4's acknowledgement against every offered descriptor field,
   including its reply opcode and separate CRC. P4 constructs that exact reply
   only after successful admission. Neither ACK nor admission means UART is
   quiet, pads are released, or the payload has completed.
4. The existing compatible console ignores version 2. No current Legacy/ExCom
   parser, GPIO binding, UART parking caller or startup behavior changed.
   Existing console and mode lifecycle tests pass after the CRC extraction.

## Verification

| Check | Result | Meaning / limit |
|---|---|---|
| New paired admission checks | 18,097 pass, ASan/UBSan | Both real gates; every length 1–4096 in both directions, modes, mutations, replay, rollover and actual paired return to UART |
| Linked eZ80 gate | 18,474 pass | Wrapper-linked instructions with IRQ enabled/disabled, ABI, IX/SP/IFF, bounds, immutable envelopes, no GPIO/UART accesses |
| Existing paired handover | 5,208 pass | Unequal delays, reset/cancel sweeps, absent peer and retained key order; modeled peripheral completions |
| Existing linked UART parking | 289 pass | Actual linked park/unpark and IRQ/ownership checks |
| Existing EMOS parallel | Nine tests pass | Engine and ownership regression |
| Existing paired reverse core | 48 pass | Simulated wire regression; no electrical timing claim |
| Compatible console | Two P4 tests, one EMOS test pass | Integrity/session behavior, scripted UART and ISR effects; mirrored headers |
| Mode lifecycle | One test pass | Retained initialization order and negative control |
| EMOS provenance/profile | Six tests pass | Prepared-source identity and product-owned build closure |
| P4 profiles | Eleven tests pass | Source/profile ownership |
| EMOS full wrapper | Pass | Required UART/Port C/keyboard/console/ABI/VDU checks; image 130,551 bytes |
| Native P4 build | Pass; exact source snapshot and maintained validator pass | P4-PC browser profile; no activation or deployment |

These are development tests, not a full-system Fab boot or a complete ExExt
runtime. The linked gate compares against host vectors whose expected accept/
reject outcomes are asserted independently by the paired test. Tests intentionally
provide trusted session state; they do not prove the still-unimplemented session
exchange or physical boot release. No throughput number is inferred.

| ROM measure | Previous parking checkpoint | Admission candidate | Difference |
|---|---:|---:|---:|
| EMOS image bytes | 130,135 | 130,551 | +416 (+0.320%, previous image baseline) |
| Free bytes below 131,072 | 937 | 521 | −416 |

## Reproduce

From the Extender root, with sibling EMOS present:

```sh
ADMISSION_VECTORS=/tmp/parallel-admission-vectors.txt \
  .venv/bin/python tests/parallel_admission_test.py
```

Build EMOS through its `firmware-check` wrapper with the isolated prepared
builder and retained toolchain, then supply that build's `MOS.bin` and `nm.txt`:

```sh
cargo run --offline --release \
  --manifest-path ../agon-emos/tests/uart_put_cpu/Cargo.toml \
  --bin parallel_admission -- IMAGE_DIRECTORY /tmp/parallel-admission-vectors.txt
```

Host checks require sanitizer support. Their `-Wno-endif-labels` accommodates
stock ZDS `#endif UART_H`; no upstream cleanup was made for this test.
Local build logs, linked vectors and source snapshots are under ignored
`agents/port008-admission`. The [machine-readable record](PARALLEL-ADMISSION-RESULT.json) hashes the source,
checks and artifacts without publishing private build configuration.

## Next boundary

Complete c2b's **fresh capability/session exchange, serializer reservation before
request/ACK, queue/event/shift-register drain, bounded phase deadlines and actual
startup release fences**. Normal cancellation/reset must invalidate the trusted
session. Mandatory peer release may leave Extender unavailable with old/absent
P4 firmware; the mainboard remains usable. No timed UART fallback is allowed.
Then bind native payload/peripheral adapters under c3. With only 521 ROM bytes
free, measure/reuse or replace reference machinery as part of that work rather
than simply adding another coordinator beside it. Physical proof remains F03
after the Author releases the bench. This increment is not bench-ready.
