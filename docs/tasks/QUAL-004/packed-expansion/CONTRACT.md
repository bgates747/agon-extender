# Packed expansion — bounded physical comparison

## Executive summary

Author authorized BM02 execution. Reuse existing suite 34×34 packed assets at
1/2/4 bits per pixel. Compare two mainboard captures and two distinct stable P4
snapshots with each other and an independently computed full-screen oracle.
No renderer fixes, new bit depths, transforms or performance claims. BM03 stays
parked. Standing identity approval covers packed-expansion-probe-r01, registry r96.

BM02-P01 [x] Review official buffer command72 documentation at agon-docs
f9806bd3cbff6ed5d1c08bef1d51fed11764b86b and existing suite assets/generator.
Retain original packed bytes; 1/4bpp use inline mapping, 2bpp buffer mapping.
Width34 alignment discards row padding; zero index is transparent. Expansion
must be explicitly converted into an RGBA2222 bitmap before drawing.

BM02-P02 [x] Freeze generator, inputs, identities and oracle. Display each
34×34 result at64,64 on white against a black512×384 mode20 screen. The oracle
uses the original geometric index formula and documented mapping, not renderer
code. Input generation independently decodes the retained packed data to verify
that formula. No fixture mode switches. Reuse the existing immutable q4draw
player and mainboard diagnostic, leaving P4/EMOS unchanged.

BM02-P03 [x] Preserve actual mainboard flash and incoming startup, verify board
identity and input readiness, then stage/readback fixtures. Autoexec alone selects
mode20 on both endpoints and starts the established SD service. Host uses admitted
keyboard CLI to invoke each independent case after a fresh reset. Firmware and
startup restoration are mandatory, even after failure.

BM02-P04 [x] Capture PACK1/PACK2/PACK4 twice on mainboard, then stable distinct
P4 generations. Compare all196608pixels per case without masks/tolerance and
require the oracle on each endpoint. Retain hashes, raw evidence and acquisition
start/end/duration separately from preparation; this is not a speed benchmark.
Follow the [capture failure protocol](../../../qualification/capture-failure-protocol.md):
mark failures, recover readiness, continue independent cases, then execute
uninstrumented controls for marked cases. Do not repair inputs to erase failures.

BM02-P05 [x] Restore exact overwritten mainboard sectors/startup; independently
verify. Close observers/SD service, release input, prove CLI responsiveness and
leave the incoming player loaded but not running. Publish bounded results and
update BM02. No push or emulator notification requested.

The wider workspace contains unrelated work. Candidate inputs are committed
separately; record that workspace condition rather than claim a clean product
build. No new firmware binary is built. Existing immutable diagnostic provenance
and actual deployed/restored hashes accompany the run.

## Fixture correction before valid paired run

r01 mainboard images passed, but later P4 cases reused accumulated source/map
buffer blocks: command0 appends; resetting Agon does not reset P4. PACK2 retained
the PACK1 image (576 differences), PACK4 had1024 differences. This is an invalid
isolation condition, not evidence of renderer disagreement. Local raw evidence
is retained; no capture crash occurred. r02/registry r97 explicitly clears each
source/map buffer before upload, as the original suite did. Same packed bytes,
mapping, output coordinates and oracle. Repeat both endpoints under r02.
Existing completion drain precedes clearing and there are no sprite references.

Completed under r02. [Results](RESULTS.md). Initial invalid run IDs: mainboard
QUAL-004-2026-09-21-02-26-42Z; Extender QUAL-004-2026-09-21-02-31-29Z.
