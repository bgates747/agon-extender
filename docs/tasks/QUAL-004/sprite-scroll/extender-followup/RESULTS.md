# Extender sprite/scroll checks — passed within scope

## Executive summary

Extender completed all four checkpoints with stable captures and clean Escape/
CLI recovery. OVERLAP, EDGES and HIDDEN match retained mainboard images exactly:
589824pixels, zero differences. HIDDEN independently matches the complete
background oracle. INITIAL is stable and visually consistent with the Author's
stock observation; no mainboard captured reference exists for that checkpoint.

| Case | Extender result | Mainboard comparison |
|---|---|---|
| INITIAL | Distinct stable frame generations; both sprites present; image visually reviewed | Stock human visual control only; no exact pixel claim |
| OVERLAP | Stable; expected overlap/frame history | Zero differences /196608pixels |
| EDGES | Stable; expected clipped sprites | Zero differences /196608pixels |
| HIDDEN | Stable; zero independent background-oracle mismatches | Zero differences /196608pixels |

[Machine results](evidence/results.json), [duration](evidence/duration.json),
[verified SD inputs](evidence/staged.json). Per-case evidence includes four
compressed wire frames, decoded pixels and PNGs; paired cases include difference
images and comparison records. Last two snapshots must have distinct sequence
numbers and identical complete pixels. No tolerance, masks, crop or scaling.

## Procedure and limits

Existing sprite-scroll-probe-r01/player were unchanged and verified on SD.
Startup selected mode20 on mainboard and Extender; each case began at fresh Agon
startup, with sprites hidden/drained before the next mode setup. Ordinary VDU
routing remained through EMOS. No firmware was built or flashed. Installed P4
candidate remains key-query-probe-r01-b2026-09-20-02-08-44Z, with existing verified
deployment provenance; no fresh physical flash readback was performed here.
Mainboard stock v2.16.0 and EMOS unchanged.

Every case completed Escape and subsequent CLI/SD-service admission. No capture
failure, restart or input-admission change occurred. Therefore no capture-free
EDP failure-control run was needed. This establishes static accumulated-history
checkpoints, not live animation smoothness, throughput or all API coverage.
The earlier mainboard INITIAL diagnostic panic remains open and deferred.

Three new paired scenes bring cumulative retained coverage to74 scenes /
13820928pixels. INITIAL is not included in that total. Original load-only
mainboard review startup restored; fixture loaded but not run, input available,
SD service and video observers closed. See final receipt.
