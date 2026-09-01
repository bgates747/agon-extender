# Evidence-hygiene correction — machine-local device paths removed

Recorded: 2026-09-01T13:14:05-04:00

The original sanitized preflight transcript still named the machine-local
serial device path and analyzer USB bus address used by the bench host. Those
values are operational topology, not evidence required to interpret this run,
and must not enter tracked project records.

The tracked transcript replaces only those paths with established statements
that the stable bench aliases matched. The original transcript remains in the
ignored machine-local evidence archive at SHA-256
`ae875816cb82805a87beb629ebe45c8a4684a0d3c4a91f6bd41ec9a5a2e9b9db`.
No run observation, timestamp, hardware identity, artifact identity, outcome,
or claim boundary changed.

The exact analyzer bytes that produced `analysis.json` are also preserved in
this run directory. The maintained task-local analyzer now carries a visible
F014 warning, so the historical copy prevents a later repair from changing the
meaning of this failed-run record.
