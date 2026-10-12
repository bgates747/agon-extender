# ADR-0027 — Linear byte storage with PPA HDMI expansion

- Status: Accepted
- Completeness: Complete
- Date: 2026-10-11
- Related task: RESEARCH-007

## Decision

The Author authorizes a bounded full-firmware experiment using linear one-byte
physical RGB222 logical pixels and PPA CLUT expansion for P4-PC HDMI. Preserve
stock-visible behaviour while adapting the VGA-specific byte-lane layout to
P4 expectations. Keep the existing directRGB888 build available as a control
and rollback; neither experimental selection changes approved production.

The P4 output task copies visible rows into private linear L8 storage and uses
the benchmarked public PPA BLEND operation outside native drawing exclusion.
The CLUT maps physical RGB222 bytes, including ignored sync-bit aliases, to
RGB888; it does not introduce a programmable256-colour application mode.
HDMI backgrounds are independently buffered. Existing rolling composition owns
immutable sprite snapshots and never borrows mutable logical pixels in an ISR.

## Rationale and limits

VGA byte-lane ordering suits original scanout hardware but imposes unnecessary
reordering before linear PPA input. Source compatibility alone does not justify
that cost. Common rasterizers and observable application contracts remain the
reuse boundary; hardware-specific pixel access and memory movement may differ.

Standalone expansion measurements support investigation, not gameplay speed
claims. Concurrent DMA/PPA operation, packed-depth fallback,320 scaling, memory
lifetimes and Nurples performance require integrated validation under the linked
task. Qualification and production acceptance remain separate from this decision.
