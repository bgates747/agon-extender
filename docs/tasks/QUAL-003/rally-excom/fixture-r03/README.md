# RXPROBE r03 — current buffered road section

The first two probes passed. This probe uses the current non-Golem game's exact
section_protocol.hpp startup array and25-byte section::draw call. Its source hash
and current AgonArcade commit are in provenance.json. It does not compile or use
the abandoned Golem implementation. The present accepted renderer still uses
stock VDP buffered matrices to expand each eZ80-computed road section.

One painted section spans y160..224 with centre160 at the top and120 at bottom.
These legal parameters produce negative projected left endpoints. Probe39pixels
on road rows180/200/220 plus a red HUD control, for each of two drawing pages.
All road samples have sentinel999 expectations: assess the paired CSVs, not just
the fixture's local mismatch count. Total80samples per path. Mode136/startup and
fresh-file rules remain identical to r01. No firmware change or timing claim.

Hypothesis: stock video/types.h convertFloatToValue casts negative floating
results directly to uint16_t/uint32_t. C++ does not define this out-of-range
conversion. Xtensa versus RISC-V code generation may differ. This is an inherited
portability boundary, not evidence that rendering primitives differ. Establish
physical disagreement and compiler/source evidence before proposing a minimal
port-specific compatibility adaptation; do not change official stock sources.
