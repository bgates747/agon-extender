# Evidence-hygiene correction — analyzer bytes preserved

Recorded: 2026-09-01T13:14:05-04:00

The exact analyzer bytes that produced `analysis.json` are now preserved in
this run directory at the hash recorded by the manifest. The maintained
task-local analyzer now carries a visible F014 warning, so this historical copy
prevents a later repair from changing the meaning of the failed-run record.

No captured sample, analysis output, observation, timestamp, artifact identity,
outcome, or claim boundary changed. Undeclared acquisition scratch files were
removed because the completed manifest does not cite them as evidence.
