# 01 — Power foundation

**Superseded draft; hardware work on hold as of 2026-09-07.** Retained for
review only. The Author rejected R32–R41 additions solely for intermediate
powered tests. This document is not an executable construction/test procedure.

Status: draft fresh-build checkpoint. No new result is recorded here.

For a fresh assembly, install common ground, the two separate positive rails,
C1–C6, and their intended IC supply/socket connections using
[function view 01](../signal-views/generated/01_schematic_power-domains.kicad_sch).
Leave U1–U4 out of the sockets during this initial powered rail test. An empty
socket has no CMOS input requiring bias. Do not join the two positive rails.

Check unpowered continuity first. At each authorized powered state, measure
the source rail and every assigned socket VCC contact: U1/U2 position 20,
U3/U4 position 14, referenced to common ground. Check P4-only, Agon-only and
both-powered settled states using the rail table in the
[step-02 worksheet](tests/02-startup-and-fail-safe-bias-network.md#rail-readings-first).
Record the actual absent-IC population. The DMM is the useful instrument here;
a digital sniffer cannot establish rail voltage or analog back-power limits.

Return to both boards off before populating ICs. Complete step 02's input and
enable preparation before powering populated U1–U4.

## Existing assembly

The [2026-09-04 observations](tests/01-power-domains-results-2026-09-04.md)
used installed ICs and are preserved as preliminary historical observations.
They are not a run of this new fresh-build procedure. The present breadboard
continues directly into step 02 while unpowered; repeat rail measurements
after completing its input-bias preparation. This plan does not instruct the
Author to dismantle the current board to reproduce an empty-socket test.
