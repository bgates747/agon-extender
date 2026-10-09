# PORT-008 — Native payload ROM-fit results

## Finding

The complete private native EMOS image now fits: **309 ROM bytes remain**.
Excluding the uncalled C receive correctness reference recovers **574 bytes**
without removing a supported command or changing the forward path. The maintained
reference source still compiles/runs in an explicit test composition. This
completes the [bounded ROM-fit contract](NATIVE-ROM-FIT.md), not live ExExt
integration or physical qualification.

## Full-link accounting

Worst remaining capacity first; flash capacity is 131072 bytes. Percentage
change is `(after − before) / before × 100`. Native “before” is the retained
refused full-link map, not an installable firmware image. Ordinary “before” is
the retained ordinary image. All figures use unchanged AUDIT-008 accounting.

| Composition | Before ROM bytes | After ROM bytes | ROM change | Free bytes after | Static RAM bytes |
|---|---:|---:|---:|---:|---:|
| Private native payload | 131337, refused | 130763 | −574 (−0.437%) | 309 | 4063 |
| Ordinary EMOS | 130752 | 130178 | −574 (−0.439%) | 894 | 4058 |

Only the ordinary engine object's ROM cost changes: 1972 → 1398 bytes. Its RAM
cost remains zero. Native C guard/assembly still cost 210/146 bytes; static RAM,
2048-byte stack reserve and linker limits are unchanged. The explicit C-reference
test composition uses 130752 ROM bytes /320 free and 4058 static RAM bytes,
matching the previous ordinary composition's size. The preceding private image
without native leaves remains retained at 130981 bytes; it is a different
composition and is not the native before/after baseline above.

## Implementation and checks

`EMOS_PARALLEL_RECEIVE_REFERENCE=1` selects the maintained reference declaration
and function. Ordinary and native profiles do not select it. A host compilation
test checks absent, zero and one selections; existing forward execution tests
still use the ordinary selection. The reference remains private, with no MOS
API or hardware caller.

The initial successful native link exposed a required checker boundary: the
whole-image Port C inventory rejected the new assembly writer. The private
profile now replaces only that checker with a native checker that calls every
ordinary check, admits the three exact Port C write sites, checks the sole raw
leaf caller, rejects a live caller of the unbound guard and checks the short
atomic Port D helper. Ordinary profiles explicitly reject native symbols.
This is a scoped owner inventory extension, not a bypass of link checks.

| Validation | Result | Limit |
|---|---|---|
| Three complete firmware wrappers | Pass, including UART baud, parallel, keyboard and console checks | Compile/link only |
| Forward/binding/selection host suite | 10 tests pass | Modeled registers |
| Paired reverse C/C++ reference | 48 cases pass | Modeled wires |
| Paired boot/runtime adapters | 718 cases pass under ASan/UBSan | Modeled SDK/GPIO boundaries |
| Native C guard/assembly in full ROM image | 124 cases pass | Actual eZ80 instructions, modeled ports |
| Same native tests in separate RAM image | 124 cases pass | Test-only image, never firmware |
| C reference in explicit full test image | 38 cases pass | Actual eZ80 instructions/callback model |
| Native full-image startup/runtime regression | 26 cases pass | Actual linked coordinator/ISR cleanup, modeled ports |
| Actual-ELF composition/negative controls | 7 cases pass | Ordinary/native selection; corrupted DI, data-port write and raw-leaf CALL refused |

Sanitizer execution required a tracer-free local run; the successful run retains
sanitizers. No physical bench operation, full-system Fab display test, UART
throughput or GPIO electrical claim was made. READY is tested once per byte
for fault detection; the assembly loop does not wait for a per-byte handshake.

## Build identities and duration

All images retain the authorized draft EMOS source identity v0.1.24; timestamps
identify distinct builds and do not imply production promotion. Builder source
is mos-agondev `90034c2348761c42bab4217ce5b0f906922dc0e4`; AgonDev Clang is 15.0.7,
compiler source `c76386c0083e6a6236ff774275227e2389f85538`. Maintained EMOS base is
`1208083`, with exact development source hashes in the result index.

| Profile | Build timestamp (UTC) | Preparation seconds | Complete build/check seconds |
|---|---|---:|---:|
| `mos-agondev.mk` | 2026-10-09-15-12-18Z | 0.266 | 25.505 |
| `parallel-native-candidate.mk` | 2026-10-09-15-12-44Z | 0.270 | 27.761 |
| `parallel-reference-test.mk` | 2026-10-09-15-13-12Z | 0.282 | 26.378 |

These are host wall-clock durations including checks, not eZ80 performance
measurements or advance estimates for physical transfer tests. Each image,
ELF/map, compiler/link provenance, ledger and test log is retained locally under
`agents/port008-native-rom-fit/verified`. The preceding owner-refusal log is
retained separately as an informative guard finding. Portable hashes and test
durations are in [the result index](NATIVE-ROM-FIT-RESULT.json).

## Remaining boundary

F02c2/F02c3 still require complete packet drain, bounded phase deadlines,
coordinator-owned live payload calls and matched post-block UART status. The
309-byte remainder is a capacity measurement, not a promise that those additions
fit. Physical first/last byte, short VALID capture, contention, recovery and
throughput remain F03 gates. Installed firmware and production selection were
not changed. This new implementation awaits Author review before commit; the
preceding payload checkpoint and this work contract were committed and pushed.
