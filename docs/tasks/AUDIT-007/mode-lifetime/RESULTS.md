# Mode-startup crash investigation — 2026-09-20

## Executive summary

The retained COP16_SETUP scene followed by mainboard startup reproduced a P4
load-access panic on the installed key-query candidate. Exact-ELF decoding
locates the fault in `VGAPalettedController::deletePalette`, inside the
all-palettes loop. Host AddressSanitizer independently demonstrates an erased
unordered-map iterator being advanced in both the unchanged official method
and EDP's copy. This is an inherited defect, not evidence that the P4 worker
shutdown design caused this crash. No firmware correction was applied because
the frozen contract excludes upstream bug fixes. Original startup was restored,
ExCom MOS prompt verified by text readback, and keyboard ready/neutral with zero
pending or held events. No firmware was flashed.

## Evidence and interpretation

[Receipt](receipt.json), [captured panic](panic.txt), and
[host extraction/reproducer](check_palette_iterator.py) preserve the bounded
finding. Full serial, host sanitizer output, command journals, saved startup and
restoration receipts remain in ignored `agents/mode-lifetime/`; they include
machine-local details. Installed ELF SHA matches the panic's displayed prefix.

The scene matches the frozen QUAL-004 scene hash. During subsequent startup the
P4 allocated 640x480 storage before the fault, rather than reaching the intended
mode9 reselection. This refines the earlier shorthand “mode9 to mode9”: startup
contains routing/reset work before its explicit mode9 command. The panic stack
contains `VGAPalettedController::setResolution` and `VGABaseController::setResolution`.
Only the fault PC and decoded addresses are asserted; arbitrary stack words
must not be treated as a fully unwound call chain.

`deletePalette(65535)` iterates `m_signalMaps` and calls `deletePalette(it->first)`.
The nested call erases that map entry. The outer iterator is then invalid, but
its loop advances it. Mode selection invokes this cleanup. The official Copper
API requires mode changes to discard custom palettes; safe iteration would
preserve that contract. Both upstream and EDP host extractions report
heap-use-after-free. The host mock isolates container lifetime, not graphics,
concurrency or physical output. Original historical restarts lacked panic logs;
this reproduction supplies a matching plausible explanation, not retroactive
proof of each historical failure.

## Restoration and remaining work

Serial opening initially coincided with a separate P4 reboot, before test traffic.
That setup event is not counted as reproducing the Copper defect. One scene
replay produced the informative panic; no blind repeated failure campaign ran.
An ordinary mainboard reset after the P4 reboot restored admission and allowed
restoration of the exact incoming 64-byte startup through the SD service.
SD service exited, prompt/ECHO and neutral ready keyboard were independently
verified; serial capture was terminated. No browser video observer was opened.
The startup backup retains the temporary task startup for recovery traceability.

M03/M04 remain open: permission to correct the inherited iterator defect is a
material exception to the frozen no-upstream-fixes boundary. Proposed correction
would advance/save the next iterator before deleting the current custom palette,
retaining palette0 and all other stock semantics. No patch, build or deployment
has been made. Post-fix repetition and page-front/page-swap controls remain
unexecuted. The Author reported app safety notices; the agent received no tool
rejection or reason identifying their trigger. Bench work stopped after restoration.
