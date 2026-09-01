# Post-run correction — READY_N was not isolated

Recorded: 2026-09-01T11:39:24-04:00

After the run, the Author clarified that the actual `READY_N` signal conductor
remained connected to P4 GPIO20 through the existing pull-up throughout this
and the preceding PORT-008 attempts. Only logic-analyzer probes were moved for
the two-point CLOCK observation. The intended
`port-008-ready-isolated-fixture-r01` electrical state was therefore never
established.

This correction supersedes every statement in the contemporaneous diagnostic
summary and manifest claiming that `READY_N` was disconnected or isolated. It
does not change the captured samples: D4 sampled no source-side CLOCK
transition and D5 sampled no post-trigger destination-side CLOCK transition.
Because the defining isolation precondition was absent, however, the run cannot
exercise or select any branch of the READY-isolated discriminator. Its outcome
remains `invalid`, now for an unestablished temporary fixture rather than for
brief lows on a supposedly isolated net.

The raw capture, original diagnostic summary, and original analysis remain
preserved as contemporaneous evidence. They must be interpreted through this
correction.
