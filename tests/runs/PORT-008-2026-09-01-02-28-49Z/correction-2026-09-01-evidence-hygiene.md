# Evidence-hygiene correction — machine-local tool path removed

Recorded: 2026-09-01T13:14:05-04:00

The original linked-clock transcript named the absolute machine-local path to
AgonDev's `ez80-none-elf-objdump`. That path is local filesystem topology, not
part of the linked-code proof, and must not enter tracked project records.

The tracked transcript replaces only the absolute path with the tool's role and
name. The original transcript remains in the ignored machine-local evidence
archive at SHA-256
`19a71b0f1ce67eba1ff8c509facb5f7c4550b348b9a0179882c65c44be0bca99`.
The MOS binary and ELF hashes, disassembly, interpretation, run outcome, and
claim boundary are unchanged.

The exact analyzer bytes that produced `analysis.json` are also preserved in
this run directory. The maintained task-local analyzer now carries a visible
F014 warning, so the historical copy prevents a later repair from changing the
meaning of this failed-run record. Undeclared acquisition scratch files were
removed because the completed manifest does not cite them as evidence.
