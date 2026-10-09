# Returning developer / external-agent orientation

Documentation checkpoint: 2026-09-25 UTC. Begin with [README](README.md) and
[using an existing installation](docs/using-extender.md). Read the tracked `AGENTS.md` and the canonical workspace instructions it
references before work. Machine-specific bench configuration remains ignored. [TODO](TODO.md) owns
unfinished work; this handoff is not a competing task queue.

## 2026-10-09 active development checkpoint

PORT-008 LC02 software integration is complete after the Author resumed the
network-change pause. [Current checkpoint](docs/tasks/PORT-008/LIVE-COORDINATOR-LC02-STATUS.md)
and [results](docs/tasks/PORT-008/LIVE-COORDINATOR-LC02-RESULTS.md) record complete
ordinary/private EMOS/P4 build passes and bounded host/linked-eZ80 verification.
Private EMOS has 599 ROM bytes free. No activation caller, ExExt mode/API or SD
transport was added; **do not flash this as a qualified live transport**.
Stop for Author review before a separate private hardware fixture.
No bench/network-device operation, commit or push occurred. Preserve all current
Extender/EMOS dirt and unrelated EMOS application_peer.py. Refresh ignored bench
connectivity before later hardware work. The older overview below is dated
orientation, not current bench state.

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
4. The [current local bundle](production/README.md) selects accepted P4 r55,
   EMOS v0.1.19 and sdserve v0.2.0 with pinned host tools. Browser output requests
   full-frame RLE2/packed compression, not inter-frame differencing. Clean builds
   include the selected composition and validate both bootloader/application
   silicon settings. The earlier r01 package is non-deployable historical evidence.
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
