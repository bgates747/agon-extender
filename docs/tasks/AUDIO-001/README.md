# AUDIO-001 evidence bucket

[Task contract](../AUDIO-001.md) · [Feasibility results](RESULTS.md) ·
[Raw hardware measurements](results.csv) · [Fixture source](sdbench/src/main.c)

AF01 completed September 18, 2026. Storage-only hardware test passed; sustained
parallel stereo remains unproven. No firmware flashed. See results for measured
rates, historical comparisons, limitations and the proposed next experiment.

Build with `make -C docs/tasks/AUDIO-001/sdbench`. Generated binaries/objects are
ignored; the deployed binary identity is in `deployment.json`. Machine-specific
control logs remain ignored under `agents/audio001/`.
