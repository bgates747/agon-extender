# Agon SD layout

The Author reserves the card root for files that require it and existing user
content. Extender agents must not accumulate payloads, results or startup backups
there. This policy governs new work; historical fixtures require a path review
before reuse. No user application directories were relocated.

| SD path | Owner and purpose |
|---|---|
| `/autoexec.txt` | MOS startup; stays at root |
| `/extender` | Maintained Extender support files and fixtures |
| `/extender/install` | Installer/bootstrap scripts and payloads; consumed historical payloads in `archive` |
| `/extender/recovery` | Documented recovery firmware; select by verified identity, never merely by filename |
| `/agents/extender/results` | Agent measurement records and run-control evidence |
| `/agents/extender/fixtures` | Archived agent fixtures |
| `/agents/extender/backups/startup` | Historical startup copies |
| `/agents/extender/backups/firmware` | Historical firmware, including failed candidates; not automatically usable rollback |
| `/tmp/extender` | Reserved transfer transaction storage; see implementation limitation below |
| `/mos`, `/bin` | Established executable locations; no backup/evidence dumping |
| `/emos` | Foreground EMOS-prefixed MOSlets; AUDIT-008 v0.1.19 launcher is locally tested only; no physical migration authorized |

## Transaction implementation limitation

The accepted destination for transfer staging, metadata and recovery backups is
`/tmp/extender`. The current listener still implements target-adjacent `.p17part`,
`.p17meta` and `.p17bak` files. Do not relocate an outstanding transaction by hand,
pretend the directory is already supported, or automatically purge it on boot.
REMOTE-005 owns migration: unique transaction names, durable destination mapping,
recovery, legacy sibling detection and self-write protection must remain correct.
Until then, existing transfers may create their required siblings; after resolving
and closing a transaction, archive retained evidence under `/agents/extender`.
Do not disguise this compatibility exception as permission for new root clutter.

## Relocation and reuse

On 2026-09-21, 158 identified Extender root files (5444163 bytes) were moved without
content changes. Every destination was hash-verified; startup was unchanged.
The [relocation manifest](storage/sd-relocation-2026-09-21.json) records exact old
and new paths, sizes and SHA-256. A copy is on SD at
`/agents/extender/relocation-2026-09-21.json`.

Historical evidence retains its original paths and identities. Use the manifest
to locate those files now. Historical installer batches are archived evidence,
not ready-to-run installers. Do not execute them from their new location without
reviewing their commands and firmware identity.

Before reusing any fixture or deployment script, its owning agent must inspect
absolute SD paths, relative outputs and working directory. Update/rebuild active
producers to use this layout before running them; never silently alter frozen
binaries/evidence. In particular, Nurples diagnostics hard-code `/NPRES.BIN`,
`/NPPROG.BIN` and `/NPRUN.ID`, and old installation scripts use root flash triggers.
Those historical workflows are retired from routine invocation until refreshed.

Unknown files and application assets remain untouched. Host-created Spotlight
and trash directories are outside this cleanup. No blanket deletion of `.BIN`
files or backups is permitted by this policy.
