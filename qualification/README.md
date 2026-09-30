# Firmware qualification authority

This directory is the sole maintained executable authority for accepting an
Extender P4 or EMOS firmware revision. Historical task fixtures and scripts are
evidence and research inputs, not acceptance suites. Compatibility launchers
under `scripts/` may delegate here but contain no qualification logic.

## Acceptance policy

An installed Extender/EMOS combination is eligible for Author acceptance only
when the flash tool has produced verified receipts for both exact installed
components and one invocation of `qualification/run.py` records all of the
following against those receipts:

1. every `acceptance_required` case in `manifests/hardware.json` whose
   `applies_to` includes the flashed component passes on the installed boards;
2. the runner restores ordinary startup and admitted neutral keyboard state;
3. the durable summary identifies the flashed artifact and exact source commit,
   case results, elapsed times, and notification outcome; and
4. the Author completes any separately declared manual cases, including loaded-
   asset mode switches, before accepting a revision whose changes intersect
   those cases.

Offline source regression remains a separate development gate in `offline.py`;
it is not rerun by installed-firmware qualification and cannot substitute for
it. Build, emulator, browser-simulation, flash-write, boot-identity, and
human observations remain distinct evidence. No zero-hardware run may report
firmware qualification success. A flash receipt proves installation; it does
not substitute for installed-hardware qualification.

## Layout

| Path | Authority |
|---|---|
| `run.py` | Installed-firmware acceptance runner |
| `offline.py` | Separate pinned-source development regression runner |
| `notify.py` | Terminal spoken cue and durable visible verdict |
| `manifests/offline.json` | Complete maintained host/browser/build inventory |
| `manifests/hardware.json` | Applicable mandatory physical cases and drivers |
| `config.example.json` | Tracked schema for the ignored bench configuration |
| `tests/` | Structural tests for this qualification authority |

The full default run currently requires 17 independently reported checks across
two physical cases. The P4 case exercises actual browser assets and reset bridge,
Agon reset/readmission, Legacy and ExCom routing, keyboard input, display status,
text capture, three fresh decoded WebSocket video frames, an exact mainboard-SD
round trip, independently verified cleanup, and final startup recovery. The EMOS
case builds its receipt-bound fixture, stages it with restoration safeguards,
exercises real raw-sector write/read/restore with independent CRC oracles, and
restores the original startup file. A missing receipt or check fails closed.

QUAL-003 and QUAL-004 remain provenance for broad graphics and exact paired-
pixel testing. Their private adapters, diagnostic mainboard firmware, and
historical payloads are not silently executed as routine acceptance tests.
Reusable cases must be promoted here with current setup, cleanup, and exact
oracles before they become mandatory.

## Invocation

```sh
.venv/bin/python qualification/run.py \
  --flash-receipt /absolute/path/to/p4-flash-receipt.json \
  --flash-receipt /absolute/path/to/emos-flash-receipt.json
```

The default run requires one verified receipt for each component. `--case` is
reserved for targeted diagnostics and cannot establish full acceptance. The
runner owns its documented board resets, temporary
qualification SD file, cleanup, and terminal notification. It never flashes.
