# Measurement candidate ready for operator typing

The clean r03 candidate was written and independently verified. Its startup
reported the exact build, expected UART pins/baud and HTTP readiness. EMOS and
the SD sample were unchanged; matching SD hashes were verified and the card
safely unmounted. Full private deployment and serial records remain in the
ignored local timing record.

The separately timestamped `p4-video-check.json` records a short headless
browser connection after deployment. Six actual P4 frames were received and
submitted, and the P4 diagnostic export succeeded. No browser keyboard session
was taken and no Agon UART round trip was exercised. The browser connection
was closed before operator handoff. `p4-video-analysis.json` preserves the
same-clock analysis: five snapshot compositions (median 118.217 ms), six video
sends (median 91.201 ms), and six browser receive-to-submit intervals (median
7.6 ms). These are limited video observations, not total typing latency or a
measurement of the cause of the earlier disconnects. Neither ring overflowed.
P4 recorder self-cost was 320 us total, 21 us maximum; these counters omit
other instrumentation effects.

Cadence clarification: the configured 200000-us snapshot minimum is evaluated
against the logical frame service's accumulated boundary clock. It is not a
wall-clock guarantee of exactly five browser frames per second: pending frame
ticks can be serviced later. Use actual composition/send/browser timestamps
to measure delivery cadence. The 16667-us EVF field likewise represents the
logical period. The measurement build preserves both policies.

Runtime `timing=off` disables P4 recording but still executes hooks and their
clock/locking checks. It is an overhead comparison within the instrumented
build, not a complete recreation of the uninstrumented firmware.

Next: the Author inserts SD/resets Agon, opens the bench browser address with
`?timing=on`, captures keyboard, types separated characters and normal edits,
observes idle/disconnect/recovery, then downloads records on the same page.
Reload only after saving. The agent analyzes those records before proposing
any repair. The original latency and disconnection issues remain unresolved.
