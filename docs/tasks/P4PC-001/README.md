# Olimex P4-PC task bucket

The Author has ordered the board; documentation and planning are established.
No P4-PC hardware or firmware validation has occurred.

The itemized plan is [P4PC-001](../P4PC-001.md). This directory holds purchasing,
future wiring tables and qualification evidence, not a second task queue.

1. [Purchase and accessories](PURCHASING.md).
2. [Prior adapter/board research](../RESEARCH-004/RESULTS.md).

Important inherited finding: the inspected PC Rev B uses GPIO9–13 for audio,
conflicting with some current DevKit harness assignments. EXT1 and UEXT expose
a different GPIO set. Treat the prior research as a starting point; verify the
actual delivered revision before wiring. Preserve the working DevKit setup.
