# P4 UART flow candidate deployment passed

Candidate `uart-flow-probe-r01-b2026-09-08-05-51-31Z` from clean Extender
`3869264` was written and independently verified on
the identified P4 revision v1.3. The [deployment record](deployment.yaml)
pins the factory image and scope. The [boot excerpt](boot.txt) confirms the
candidate identity, four UART pins, 115200/8N1 and empty WAIT with CTS HIGH.

The Author authorized this deployment. Both boards remained powered and
ribbons seated. EMOS installation and the physical pause/resume/blocked-timeout
exchange remain pending under the [test sheet](../uart-flow.md).
