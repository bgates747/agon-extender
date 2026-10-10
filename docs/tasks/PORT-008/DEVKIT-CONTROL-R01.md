# PORT-008 — Repeat the proved DevKit receiver on P4-PC

## Executive summary

Author requests the actual successful DevKit firmware with only its pin mappings
changed. Reproduce the retained PRX-06 receiver, not a new implementation of its
mechanism. Original receiver and canary sources match the historical fixture
hashes. Current SDK is the same v5.5.5 lineage, but native ARM build/toolchain
provenance is recorded separately; no byte-identical original image claim.

DC01 [x] — Extract legacy commit `4626fcc41a0da5811a4374175fe803957ec5ab4f`;
verify original receiver/canary/sender hashes against the retained run manifest.
Change P4 receiver READY/VALID/data GPIO constants only, and mechanically prove
reversing that mapping yields the original source exactly. Build the standalone
USB-command receiver with original CMake/defaults; freeze compiler/config/image
identities. It contains no HDMI, networking, Extender keyboard or modern EMOS
handshake. Preserve current full-HDMI snapshot image for exact restoration.

DC02 [x] — Historical sender ownership exception approved; staging/readback complete.
The old eZ80 sender controls GPIO directly, conflicting with the current
EMOS-ownership rule. Author approved this one historical sender exception; do not substitute a covert
application bypass or claim the current native gateway can talk to the old
USB-only receiver. If approved, retain the exact original sender assembly and
canary, adapting only unattended launch/menu and mode selection outside the
fixture. Record that this is an isolated historical experiment, not a supported
Extender API. Stage/read back fixture and temporary startup through the current
listener before removing input support. Restore exact original startup afterward.

DC03 [x] — Verify identified P4 and original receiver build, flash/read back
its complete partition composition. Execute the original bounded 22-record
sweep (seven delay profiles, three repeats plus the analyzer record) only if
DC02 is resolved. Retain P4 whole-record pattern/sequence/CRC results and a
complete capture using the existing current probe map. Stop on failure without
uncertain replay. A forward-only success says nothing about reverse parallel.

DC04 [x] — Restore/read back the exact current full-HDMI P4 image, original
startup and input readiness; retrieve Agon evidence, leave listener stopped.
Report DevKit versus P4-PC results and changed variables. No EMOS ROM/mainboard
VDP change, wiring modification, new diagnostics or production promotion.

## Reuse and limits

[Original evidence and pinned research](FORWARD-PROTOTYPE-REUSE.md) identify
`src/prx_receiver.c` and `common/p4_canary.*` from the retained PRX-06 run.
Receiver SHA256 before remapping is
`0e0f76c0b252ebba0f61ebd74390ec086e95a163b1ba32c4c57e294a1a0969c5`.
Current board mapping comes from `vdp/build/boards/p4-pc.json`. GPIO contracts
were checked in the official read-only `agon-docs/docs/GPIO.md`; no new API.
The [snapshot run](DATA-SNAPSHOT-R01.md) and Author-reported harness difference
remain independent evidence. This experiment changes hardware/harness, pin map,
firmware composition and build environment relative to the historic DevKit run;
it cannot alone identify which difference causes a failure.

## Prepared result

Receiver build `prx06-p4pc-control-r01-b2026-10-10-04-38-26Z` compiles and
passes configuration, image integrity and pin-only source checks. Application
231872 bytes, SHA256
`2911baa324857b0eb9a483213d127a3532b2701c5893ed53c5545f03339e1cbe`.
Original USB console, less-than-v3 silicon selection and16MiB flash configuration
are retained. Native IDF build took71.56 host seconds. Original CMake/defaults
and canary remain byte-identical. Native compiler/config/segment identities are
retained separately; the original PlatformIO build environment was not reproduced
byte-for-byte. This is a source-faithful remap, not the original flash image.

Agon launcher compiled with unchanged original sender assembly and sweep function.
It removes interactive confirmation and in-program mode switching, and restores/
readback-verifies original startup before any original GPIO function runs.
This executable is prepared only; its direct GPIO execution is now authorized for this one historical
comparison. Fixture and temporary startup deployed/read back through the current UART listener; standalone receiver installation is next.

Ignored local preparation: `agents/port008-live-qualification/devkit-control-r01`,
including exact extracted sources, pin-only patch, manifest/hash verification,
compiler/SDK records, receiver and sender binaries. Exact current snapshot firmware is retained for restoration. No other source repair attempted.

Author explicitly approved the historical sender exception in chat. It applies
only to this bounded reproduction and does not change the normative product
architecture or create a supported bypass. No resident EMOS modification.

## Execution checkpoint — paused for card return

The standalone receiver was flashed and all three segments read back correctly.
No USB arm command or parallel payload was issued. The unattended launcher
returned15 before GPIO access: its startup readback used text mode, which converts
CR/LF and invalidates a byte-exact comparison. MOS displays15 as “Volume timeout”;
that message alone did not establish a card fault. The launcher is rebuilt with
binary file access; original sender assembly/sweep and P4 receiver are unchanged.
The corrected launcher is not yet deployed.

Exact full-HDMI rollback was subsequently flashed and all four segments verified.
Input readiness is not yet recovered. The agent reset Agon while the earlier
card-reseat request remained pending; Author had removed the card. This was an
agent sequencing error, not transport evidence. No further bench operation is
permitted until Author returns the card and resumes this comparison.

Author mounted the card on Lenovo and requested startup syntax inspection.
Read-only inspection confirms the original38-byte startup exactly, SHA256
`7b500d81030020f893aee64338889efd21630f7db9a893d0919d1084a69bb3a5`:
`SET KEYBOARD 1`, then `EMOS KEYINPUT extender`. Both are implemented commands;
there is no BOM, stray text or remaining test launch. The earlier temporary
`VDU 22 3`, `LOAD /extender/install/prx06pc.bin`, `RUN` also use implemented MOS
commands. No nonexistent command was found. The separately reported syntax
error is not reproduced or explained by the current file. Card contents were
left unchanged. Original superseded launcher remains in the install directory;
normal startup does not execute it. DC03/DC04 remain incomplete; no historical
transfer verdict or performance claim is available.

## Author photo — startup error identified

The subsequent mainboard photo shows `KEYINPUT FAIL: receiver readiness timeout`,
`Keyboard input: mainboard`, `Error executing autoexec.txt at line 2`, then
`Volume timeout`. This resolves the reported “syntax error”: EMOS recognizes the
second startup command but cannot admit the P4 keyboard service. No nonexistent
command or startup syntax defect is shown. `Volume timeout` here is the generic
MOS text for FR_TIMEOUT returned by EMOS KEYINPUT, distinct from the launcher's
earlier explicit return15. It does not itself demonstrate an SD-volume failure.
P4 input recovery remains pending; no reset, flash or card write was performed
in response to the photo.

## Corrected Author report — post-flash keyboard regression

Author clarifies that keyboard input worked BEFORE the agent's firmware flash,
not afterward. The post-flash photo shows EMOS KEYINPUT receiver-readiness timeout
and fallback to mainboard input. Treat this as an unresolved post-flash/restoration
regression. The agent's claim that current keyboard operation was confirmed or
that the failure was transient was a misreading and is withdrawn. Exact full-HDMI
flash readback passed, but successful input restoration has NOT been established.
No additional bench operation follows from this correction.

## Completed historical comparison and verified restoration

Original PRX-06 receiver with GPIO-only P4-PC remap failed its first1024-byte
record at the slowest24-NOP profile. First byte41, lastF4 (expected74), stored
CRC F3F4/calculatedBA67 instead of6474. Remaining21records were not armed.
Original sender assembly/sweep unchanged; only unattended launch adapted.
Analyzer acquisition passed:45seconds at24MHz,1,080,000,000samples; exactly1024
qualified falling clocks with READYlow, zero mismatches on observed source
D2/D4/D5/D6/D7. D0/D1/D3 were not observed; probes are on Agon header, not P4.
Full hash-verified logic.sr and USB verdict retained in ignored local evidence.
Failure without modern coordinator or full EDP means those are not its sole
necessary cause. Harness, hardware, SDK/toolchain and receiver memory/cache/DMA
attribution remain unresolved. No usable throughput or reverse-transfer claim.

After Author confirmed card in Agon, keyboard admission and actual remote-command
checks recovered. Final exact full-HDMI snapshot restored/all four segments
verified; P4 HTTP availability awaited before final Agon recovery reset.
Original38-byte startup independently read back,52remote packets accepted,
input ready/neutral, held0/pending0, listener exited. No active bench operation.
EMOS/mainboardVDP/wiring unchanged. No repair or production change. Earlier
unverified-restoration and current-keyboard-status statements above are history.
Evidence: agents/port008-live-qualification/devkit-control-r01/handback.json,
run-result.json, analyzer-summary.json, installation and restoration receipts.
