# Numeric conversions during upstream imports

## Executive summary

Run `.venv/bin/python scripts/check_numeric_port.py` before accepting a VDP
import. It rejects unreviewed changes to the bounded numeric baseline and runs
sanitized regressions. Passing it does not approve an import: new conversion
sites, actual target selection and physical behavior still require review.
This procedure is `numeric-upstream-import-r01`, owned by the existing
[upstream integration workflow](../dependencies/UPSTREAM-WATCH.md).

## Approved adaptations

Upstream references are Agon VDP v2.16.0
`c7ac293d2aa81ddfa693390549bcd909069c8fc3` and its retained vdp-gl lineage
`ac2dd5986daf496c43ae8e7fe41836274aec54a0`. Paths below are repository-relative.

| Finding | Upstream operation and retained location | Required P4 semantics | Regression |
|---|---|---|---|
| N01 | Numeric encoding in `video/types.h`; buffered transform consumer in `vdp/video/vdu_buffered.h` | `encodeFixed` validates, truncates through signed integer, then encodes unsigned bits; invalid result preserves destination | `tests/fixed_conversion_test.cpp`; pinned consumer fingerprint; RX06 physical road regression |
| N02 | `bufferAffineTransform`, same buffered header | Validate logical X/Y before implicit int16 conversion and `Context::scale`; keep truncation-before-scale | `tests/numeric_parser_test.py` |
| N03 | `bufferTransformBitmap`, same header | Validate each forward corner before int32 cast/allocation/publication | Parser test |
| N04 | `drawBitmapWithTransform`, `vdp/vendor/vdp-gl/src/displaycontroller.cpp` | Reject invalid forward corners without drawing; release owned matrices exactly once | `tests/numeric_renderer_test.py` |
| N05 | Three `genericRawDrawTransformedBitmap_*` templates in `displaycontroller.h` | Positive source bounds reject NaN before casts/pointer calculation | Renderer test |
| N06 | `createBitmapFromBuffer`, `vdp/video/vdu_sprites.h` | Validate existing double byte count before uint32 cast; retain entry-time clearing of old bitmap | Parser test |

The helpers live in `vdp/video/extender/port/{fixed,numeric}_conversion.hpp`.
Keep the adaptations P4-only and preserve stock valid-input rounding, ordering,
ownership and replies. Remove an adaptation only after the selected official
upstream implementation supplies equivalent defined behavior, its regression
passes, and the removal is explicitly reviewed. A compiler producing plausible
pixels from undefined casts is not an equivalent implementation.

## Import procedure

1. Run the numeric check against the old reviewed tree and retain its result.
   Establish official tagged source/dependency identities through the dependency
   workflow; never edit the official reference checkouts.
2. Compare old/new source graphs and reconcile every changed protected function,
   helper, test, caller, selected translation unit and build flag. The fingerprint
   file is a bounded review receipt, not a second source-selection graph.
3. Enumerate conversions afresh across the actual compiled closure, including
   implicit conversions and newly enabled backends. Use target compiler warnings
   and typed conversion evidence, not just grep. Retain exact compile commands,
   macros, optimization flags, selected source hashes and classifications. The
   [RX07 audit](../tasks/QUAL-003/rally-excom/rx07/README.md) and its replay script
   document the previous method and its limits; refresh it for the new release.
4. Check floating-point assumptions in actual target commands. `-ffast-math`,
   `-ffinite-math-only` or equivalent assumptions can invalidate NaN rejection;
   do not carry such changes through on the strength of host tests. Reconcile
   selection against `generated/code-graph.yaml` and the actual build manifest.
   Known old-graph/console-selection drift must not be silently relabelled fixed.
5. Classify each new site with its valid domain, truncation/rounding, overflow,
   ownership, framing and invalid-input behavior. Enumerate unapproved issues
   for disposition; do not broaden the port into upstream bug fixing. N07/N08
   and dormant findings remain outside the approved N01–N06 scope.
6. After review, update the numeric review JSON with new hashes, upstream
   identities and a durable review reference. There is deliberately no automatic
   rebaseline switch. A hash refresh without the preceding review is invalid.
   Run the check again, inspect changed tests and build the actual P4 candidate.
7. Run matched defined-input tests on stock and P4, and rejection cases on P4
   only. Undefined stock conversions are not an oracle. Retain fixture identities,
   raw results and durations. Repeat applicable current-game smoke checks and
   obtain human acceptance under the existing task gates before publication.

## Running and interpreting the check

```sh
.venv/bin/python scripts/check_numeric_port.py \
  --output agents/numeric-import-check.json
.venv/bin/python -m unittest discover -s tests -p 'numeric_import_gate_test.py' -v
```

Requires a C++17 host compiler named `c++` with address/undefined/float-cast-
overflow sanitizers and the project Python environment. The runner uses that
same Python for subprocess tests, temporary build storage, no firmware tools,
no network and no automatic modification of review hashes. A nonzero exit is
failure; do not substitute a prior report. Output records test completion and
wall duration, not rendering performance.

The parser/renderer harnesses extract actual selected bodies but stub surrounding
services. The fixed test exercises the helper; its caller is additionally pinned
for review. These are regression checks, not exhaustive future-site discovery or
proof of target macro selection. Existing `readFloatArguments` positive-infinity
sentinel behavior and inherited integer geometry overflow remain unchanged.

Current implementation and hardware evidence:
[RX09 results](../tasks/QUAL-003/rally-excom/rx09/results/README.md).
Manual gameplay review of that numeric candidate remains a separate open gate.
