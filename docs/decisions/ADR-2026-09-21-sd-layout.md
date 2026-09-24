# SD separation of support files, evidence and transactions

- Status: Accepted
- Completeness: Complete
- Date: 2026-09-21
- Related task: REMOTE-005

The Author selected `/extender` for durable bootstrap/support/recovery files,
`/agents/extender` for agent evidence and historical backups, and `/tmp` for
reserved transfer transaction storage. The Extender allocation beneath `/tmp`
is `/tmp/extender`. Root, `/mos`, `/bin` and proposed `/emos` are not dumping
grounds for those files. MOS startup remains `/autoexec.txt`.

The [SD layout policy](../sd-layout.md) is the operational authority. Existing
protocol migration remains implementation work in REMOTE-005; acceptance of the
layout does not claim that the current listener supports it. Historical records
retain old paths with a relocation manifest, preserving provenance.
