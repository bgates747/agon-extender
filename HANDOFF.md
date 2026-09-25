# Returning developer / external-agent orientation

Documentation checkpoint: 2026-09-24 UTC. Begin with [README](README.md) and
[using an existing installation](docs/using-extender.md). Read the canonical
workspace instructions named in the local `AGENTS.md`, when present, before
work. That ignored file is supplied by the maintained workspace, not a public
clone prerequisite. [TODO](TODO.md) owns
unfinished work; this handoff is not a competing task queue.

## Current recorded position

1. EMOS v0.1.19 removes the cancelled external `.emo` loading machinery while
   retaining resident input, display and gateway services. Prefixed utilities
   load from `/emos`. [Implementation and physical deployment](docs/tasks/AUDIT-008/HARDWARE.md)
   record exact identities, ROM readback and the bounded checks; broader human
   gameplay acceptance is not implied.
2. The listener is an EMOSlet at `/emos/sdserve.bin`, invoked as
   `EMOS sdserve [--fast] /`. Both listener and host upload must opt into fast
   mode. [Current SD instructions](docs/mainboard-sd.md) supersede old `/mos`
   installation and bare `sdserve` examples. The ordinary application fallback
   remains separate.
3. P4 physical USB, browser capture and host keyboard automation exist.
   [Keyboard ownership](docs/remote-keyboard.md) applies in Legacy and ExCom.
   Remote typing requires Extender input to be admitted already; do not ask an
   agent to enable its own disabled path through that path.
4. Accepted browser policy is full-frame RLE2, not inter-frame differencing.
   The retained reset-button build instead requests raw `/video`; its codec
   support remains present but unrequested by the ordinary page.
   [Composition review](docs/tasks/RELEASE-001/R01-03.md) records this discrepancy
   and removed explicit credit spacing. Performance impact is unmeasured; no
   correction is deployed.
5. Remote reset uses the separate Pi bridge described in the
   [reset guide](docs/bench-reset.md). It is neither a P4 reset nor a power cycle.
6. [AUDIT-009](docs/tasks/AUDIT-009.md) is reconciling documentation. Its inventory
   distinguishes reviewed procedures from unreviewed historical material. Do not
   infer full-documentation acceptance from this orientation update.

## Before bench work

Consult ignored `HARDWARE.local.md` and the latest applicable deployment receipt
for installed artifacts, owner and endpoints. Do not infer the live state from
this handoff or checkout HEAD. Read [bench constraints](docs/qualification/bench-constraints.md)
and [SD placement](docs/sd-layout.md) before fixture execution or deployment.
Observe current authorization and other agents' bench ownership.

Earlier handoff snapshots remain in Git history. Their installed-build claims,
uncommitted-work lists and startup descriptions were dated observations, not
current instructions. No firmware or hardware was changed for this documentation
checkpoint.
