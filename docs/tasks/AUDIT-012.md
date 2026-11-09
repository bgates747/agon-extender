# AUDIT-012 — Current candidate compatibility with pinned firmware

Audit Extender's current test and production candidates against Smith's pinned
firmware defaults before treating an older artifact as a normal deployment.
Keep inherent firmware-development/version-comparison cases explicit and return
Olimex to its current standard after those cases. This is a source/artifact
compatibility audit; hardware permissions do not expand.

## Authority and freeze boundary

Smith's 2026-11-08 notification directs all recently active agents to use:

1. VDPlet v0.1.2-alpha release firmware with verified SHA256SUMS for testing and
   deployments on Alexe, Olimex and Console8; it includes UART RX recovery.
2. Eirene MOS 3.1.0_uart0_rc_3 for Alexe/Console8 tests: release ZIP member
   `mos-rc3.bin`, 100,879 bytes, SHA-256
   `d7a51147f3381cd68d56f3fbe4605434a897dfae1b049269afeba09ec2b7eb50`.
3. On Olimex, the scheduling agent maintains that VDPlet and latest approved
   EMOS incorporating current Eirene enhancements as defaults. Scheduling
   requests explicitly identify and justify required exceptions.
4. Write this audit task, freeze it with a commit and push, then perform the
   audit immediately. Existing test/deployment/hardware permissions still apply.

The initial commit must contain this task and its authoritative TODO entry
before any audit findings are produced. Existing preparation and retained
firmware evidence predating this instruction are inputs, not results fabricated
for this audit. Keep unrelated pending controller/scheduler work intact.

## Scope and evidence rules

1. Extender owns auditing its current production selections/release candidates,
   maintained firmware/tool selectors, active test/deployment candidates and
   operator paths named by its authoritative TODO/current handoff. Do not take
   over other projects' source. Consult component owners for concrete facts.
2. Inventory every unfinished authoritative TODO item. Distinguish an actual
   current artifact from a plan, parked historical experiment or work with no
   firmware dependency; an unfinished task does not make all its archived
   binaries current candidates. Record exact source/manifest pointers for
   artifact-bearing groups and do not silently omit unresolved candidates.
3. Match platform, actual firmware/API/feature requirements and release assets.
   Separate bare RC3's result/lifetime semantics from guarded EMOS. Do not assume
   unchanged public ABI means every optional VDPlet feature is enabled, or API
   table presence proves exhaustive behavioral parity.
4. Preserve accepted production bundles, tags and frozen test inputs. An audit
   does not promote firmware, rebuild a candidate, alter an emulator, migrate
   production, run tests or install anything. If a candidate needs adaptation,
   record the owning task and bounded next action, not a new implicit run.
5. A source-compatible claim is not a physical pass. Use explicit dispositions:
   exact standard match; source-compatible with execution unqualified;
   inherent firmware/version exception; incompatible/needs adaptation;
   unresolved artifact/contract; or no current candidate/not applicable.
6. Do not create a new recurring approval bureaucracy. Apply existing manifest,
   scope, lease, freshness and cleanup rules. Missing evidence stays visible
   and assigned to its technical owner; no automatic fallback to older firmware.

## Work and completion

1. [x] Freeze this task/TODO entry in a pushed commit before audit execution.
2. [x] Inventory current selectors, release candidates and all unfinished TODO
   items, recording precise currentness and artifact/source references.
3. [x] Assess firmware/API/feature compatibility and justified exceptions;
   identify exact gaps and ownership without inventing unperformed tests.
4. [x] Record source/artifact findings in a tabular report and machine-readable
   inventory, including checksum identities and evidence limitations.
5. [x] Update affected maintained selection/operating guidance where this audit
   exposes an active contradiction; retain production/historical identities.
6. [x] Notify the Olimex scheduling agent of the relevant default, exception,
   restore and pending first-job implications. Report the result to Smith.

Completion means this bounded current-candidate audit and necessary protocol
corrections are delivered. It does not mean all candidates pass, every deferred
compatibility issue is implemented, or another project has finished its audit.

## Result

The [source/artifact report](AUDIT-012/RESULTS.md) and
[machine inventory](AUDIT-012/inventory.json) cover99 unfinished TODO entries
and19 candidate groups, including explicit incompatible/unqualified cases.
Task freeze commits a1686bf5 and0fa52f26 were pushed before audit analysis.
The current-standard policy and companion guidance are updated; no build,
emulator run, firmware write or physical observation occurred in this audit.
