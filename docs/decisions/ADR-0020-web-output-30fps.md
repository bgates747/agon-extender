# ADR-0020 — 30 fps web output at512×384

- Status: Accepted
- Completeness: Complete
- Date: 2026-09-16
- Related task: QUAL-003, RESEARCH-003

## Decision and rationale

The Author selects30fps as the current supported512×384 web-output rate and
requires fixtures not to send faster. Normal fixture design must pace requests,
composition admission and sends to that ceiling, without catch-up bursts or
wasted60Hz composition. Native rendering/game timing remain independent.

The standalone P4 experiment met30fps without drops in its bounded controls,
but combined full-frame output reached only47.02–47.29fps at a60Hz target.
These results motivate a conservative output contract; they do not certify
all VDP workloads or browser presentation. Higher-rate output now belongs only
to separately approved stress work. The previous60fps output requirement is
deferred, not a normal acceptance gate. One-byte-per-pixel/256-colour capability
remains a future goal. Protocol encodings are unchanged by this cadence decision.

## Qualification boundary

QUAL-003 owns application of this contract to active fixtures and production
qualification. Historical evidence and frozen input identities are preserved.
This decision does not claim a production firmware limiter has been implemented.
