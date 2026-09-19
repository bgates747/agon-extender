# ADR-0021 — RLE2 as the browser-video default

- Status: Accepted
- Completeness: Complete
- Date: 2026-09-19
- Related task: QUAL-003 / P01h

## Decision

The Author directs that browser video output request RLE2 compression by default
going forward. This promotes the installed client's `?rle2=1` selection into
project policy. Preserve negotiated raw compatibility and explicit diagnostic
codec overrides; they are not the normal browser default.

RLE2 encodes complete supported frames, not inter-frame differences. This decision
neither selects SRLE2/szip nor changes frame pacing, framebuffer semantics, or
unsupported-format fallback. Do not silently revert the default during upstream
integration or client replacement. Verify the default connection negotiates RLE2
when changing the browser client or deploying replacement firmware.

## Evidence and scope

The live client was inspected and requests `/video?rle2=1`. Retained matching
client source and latency evidence are in BENCH-005. P01h owns codec qualification;
this policy acceptance does not close its remaining correctness/coverage gates.
No new firmware or benchmark is implied by this documentation-only freeze.

Canonical wire/pacing authority: [browser video](../protocols/browser-video.md).
